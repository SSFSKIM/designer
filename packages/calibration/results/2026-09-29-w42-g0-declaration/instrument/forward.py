"""W42 G0 instrument: the forward models of the declared families (charter Design, "The law" and "The rival
families"; memo E §1's algebra, with `~/vitrea-w42/grounding/refit/lt.py` (SHA-256 7a0a36dc…) the reference).

One engine renders every family. A family is a set of discrete choices (`Family`) plus a parameter dict; LT,
the primary family, is the engine at its defaults:

  capture   S = F * B on the footprint R_fp: the shape's box plus the declared margin (active 0.35 s if
            s > 64, else 16 pt; receded one device px), with F memo C's Gaussian floor of 0.4 f device px
            (f = 2 device px per backdrop texel, 4 on rrect-lg), applied before the knee;
  narrow    C = G(sigma_n) * S, sigma_n = k_n * 5 pt * o(s, d, pose), o the dump's exact law;
  wide      W = G(k_w * 8 pt) * S on R_fp, clamp-to-edge when active and normalised when receded;
  composite light N = C + lam * max(0, W - C), dark N = C - lam * max(0, C - W); M = 0.5 N + 0.5 W;
  output    y = T(255 M), per channel.

All averaging is in ENCODED values (0..1). Widths are in CSS px (points) unless a rejected null's `units`
says otherwise. Everything is evaluated on the device-pixel grid of the footprint crop; the narrow term's
depth-graded width is realised by linear interpolation in sigma between blurs whose spacing
`NARROW_STEP` bounds (proof 1 measures the interpolation error against a dense reference).

Every family maps a constant backdrop to itself before T: each blur and each footprint normalisation
preserves a constant, the hinge reads max(0, 0) = 0, the bleed and the tails are convex mixtures of
blurs, and R1's composite of T(C) = T(W) = T(g) returns T(g). That is clause 7's invariance, and
`uniform_invariance()` checks it on every family.
"""
import itertools
from dataclasses import dataclass, replace

import numpy as np
from scipy import ndimage

import geometry as G
from tone import srgb_to_lin, lin_to_srgb, memo_c_T

ENDPOINTS = ('light-rest', 'light-inactive', 'dark-rest', 'dark-inactive')
RN, RW = 5.0, 8.0          # the declared radii (memo D): BlurRadius 5, BlurFill radius 8
WN = 0.5                   # Normal = NSGlassTintAmount = 0.5 on the bed, fixed (memo D §0)
TRUNCATE = 4.0
# Narrow-term interpolation: blur levels are spaced so that consecutive sigmas differ by at most
# NARROW_STEP[0] device px + NARROW_STEP[1] * sigma. Proof 1 states the error this costs.
NARROW_STEP = (0.20, 0.04)
# The deep mask. In the ACTIVE pose Apple refracts inside a band reaching BAND_IN pt inward from the edge and
# BAND_OUT pt beyond it (memo D §3: inner refraction height min(s/4, 20), outer reach 16-19.2+; the bed
# stream's finding and the parent's ruling on it). LT models no refraction, so every active region sits
# outside the band plus the narrow kernel's support: d_in = BAND_IN + 2 sigma_n,ref with sigma_n,ref the
# declared narrow width at the centre under k = 2.1 (8.4 t pt). The receded pose has no refraction and keeps
# memo C's 8 pt. A cell may still pass its own d_in (a reader proving itself on a synthetic render).
BAND_IN, BAND_OUT = 20.0, 19.2
RECEDED_D_IN = 8.0
# The active mask's kernel support. Every active reader and family fitter uses kernel='n' (the revised ruling 3):
# refraction is taken to act AFTER the blur (vitrea's own order), so a pixel beyond the band is the law's own value
# whatever the kernel's reach, and d_in = 20 + 2 sigma_n,ref = 20 + 16.8 t pt. kernel='w' (2 sigma_w,ref = 2 x 2.1
# x 8 = 33.6 pt beyond the band, 53.6 pt, rrect-ml and rrect-lg only) is the FALLBACK mask of the rival order,
# refraction BEFORE the blur, taken only after the parent reads a BEFORE call (refraction_order.py; tolerances.json
# "refraction_order_test", v3). Ruling 3 as first given put every family fitter at 'w'; its outputs are kept as
# that fallback's record. The receded pose, with no band, carries W fully at RECEDED_D_IN.
KERNEL_REF = {'n': lambda s: 2.1 * RN * 0.8 * G.size_t(s), 'w': lambda s: 2.1 * RW}


def band_d_in(s, kernel='n'):
    return BAND_IN + 2 * KERNEL_REF[kernel](s)


# The active bleed layer's declared inputs (memo D §3, w42-dumps.txt lines 128, 135 and 144-146), by scheme. Active
# only and s > 64: its blur radius is 0 at s <= 64 and its opacity 0 when receded.
BLEED_MATRIX = {'light': (0.9, 1.0, 1.2), 'dark': (0.125, 0.5, 1.0)}   # inputBleedColorMatrix black, white, saturation
BLEED_SPAN = {sch: m[1] - m[0] for sch, m in BLEED_MATRIX.items()}      # white - black
BLEED_OPACITY = {'light': 0.5, 'dark': 0.8}      # x t (inputBleedOpacity)
BLEED_DARKEN = {'light': 1.0, 'dark': 0.0}       # inputBleedDarkenBlend: a darken blend in light, normal in dark
BLEED_REACH = 0.35                               # x s: inputBleedAmount = inputBleedHeight = inputBleedBlurRadius
BLEED_DISTANCES = (1.0, 0.0)                     # inputBleedDistance0, inputBleedDistance1
# The fix wave's engine label: proof rows produced after the review of b151aff4 (the W-shape support fix, the
# dump-literal bleed) carry it, so that a row of a family whose model changed is never read at the old engine.
ENGINE = 'fix-b151aff4'


def endpoint(scheme, pose):
    return f'{scheme}-{pose}'


def opacity_law(d, s, active):
    """BlurOpacity by SDF depth d (pt, negative inside), memo D §3: active 0.8t at the centre (d = -s/2),
    0.4t at 1 pt inside the edge, 0.5 at the edge, 1 beyond; receded 0.4 + 0.4t inside, 1 at and beyond."""
    t = G.size_t(s)
    if active:
        return np.interp(d, [-s / 2, -1.0, 0.0, 1e-6], [0.8 * t, 0.4 * t, 0.5, 1.0])
    return np.where(d < 0, 0.4 + 0.4 * t, 1.0)


@dataclass(frozen=True)
class Family:
    """The discrete choices that define a family. Defaults are LT."""
    name: str = 'LT'
    narrow: str = 'var'          # 'var' (radius scale, LT) | 'free' (sigma_n(span) ordinates) | 'mix' (null)
    units: str = 'pt'            # 'pt' | 'texel' | 'dev' (the last two are rejected nulls)
    support: str = 'box'         # W's support: 'box' (R_fp) | 'canvas' | 'shape' (rounded shape + margin mu)
    edge: str = 'auto'           # 'auto' (clamp active, norm receded) | 'clamp' | 'norm' | 'swap'
    wkind: str = 'gauss'         # 'gauss' | 'tails' (two Gaussians: sigma2, a)
    fills: int = 1               # 2 = K2 (the knee against Wk of width sk, the normal mix toward W)
    order: str = 'after'         # 'after' (LT) | 'before' (R1: T on C and W, then the fill) | 'blurlast' (R2)
    space_c: str = 'enc'         # the narrow term's averaging space: 'enc' | 'lin' (C-linear)
    knee: str = 'channel'        # 'channel' (per-channel max/min) | 'luma' (the whole colour selected by luma)
    bleed: str = 'none'          # 'none' | 'shared' (radius k_w * 0.35 s) | 'own' (radius k_b * 0.35 s)
    bleed_form: str = 'normal'   # 'normal' (the stated variant: Normal mix, whole shape, matrix affine absorbed by
    #                              native T) | 'literal' (the dump's inputs: darken / normal, matrix, band; see
    #                              compose and bleed_ramp)
    bleed_at: str = 'pre'        # the literal form's place: 'pre' (inside T's argument) | 'post' (after T)
    floor: str = 'gauss'         # 'gauss' (memo C's 0.8-dev floor) | 'box' (literal decimation, a null)
    free_params: tuple = ('k', 'lam')

    def with_(self, **kw):
        return replace(self, **kw)


_TOKENS = itertools.count()


class Cell:
    """One cell: backdrop, shape, scale, endpoint, the footprint crop and the deep evaluation mask."""

    def __init__(self, cid, background, component, scale, scheme, pose, d_in=None, rgb=False, T=None, kernel='n'):
        self.id, self.scale, self.scheme, self.pose = cid, scale, scheme, pose
        # A token never reused in the process: the shared blur store is keyed by it. Keying by id(self), as the
        # first byte-bounded store did, let a new cell that reused a freed cell's id read that cell's blurs
        # when a window, width and mode coincided exactly.
        self.token = next(_TOKENS)
        self.ep = endpoint(scheme, pose)
        self.active = pose == 'rest'
        self.bg_spec = G.BACKGROUNDS[background] if isinstance(background, str) else background
        self.comp_spec = G.COMPONENTS[component] if isinstance(component, str) else component
        self.comp_name = component if isinstance(component, str) else component.get('name', 'shape')
        B8 = G.render_background(self.bg_spec, scale).astype(np.float64)
        self.rgb = rgb
        self.B = (B8 if rgb else G.luma(B8)) / 255.0
        self.d = G.sdf(self.comp_spec, scale)
        self.span = G.span(self.comp_spec)
        self.t = G.size_t(self.span)
        self.f = G.backdrop_texel_dev(self.comp_spec)
        self.T = T if T is not None else memo_c_T(self.ep, self.span)
        inside = self.d <= 0
        ys, xs = np.nonzero(inside)
        self.box_px = (ys.min(), ys.max() + 1, xs.min(), xs.max() + 1)
        if d_in is None:
            d_in = band_d_in(self.span, kernel) if self.active else RECEDED_D_IN
        self.d_in = d_in
        self.mask = self.d <= -d_in
        self.y = None            # observed image (codes), set by synth() or a loader
        self._crops = {}
        self._cache = {}

    # ---- footprints
    def margin_pt(self):
        if self.active:
            return 0.35 * self.span if self.span > 64 else 16.0
        return 1.0 / self.scale

    def crop(self, support, mu=None):
        """(y0, y1, x0, x1) of the computation window for a support."""
        key = (support, None if mu is None else round(mu, 4))
        if key not in self._crops:
            H, W = self.d.shape
            if support == 'canvas':
                win = (0, H, 0, W)
            else:
                m = self.margin_pt() if support == 'box' else max(mu, 0.0)
                mp = int(round(m * self.scale))
                if support == 'shape':
                    mp = int(np.ceil(m * self.scale)) + 1
                y0, y1, x0, x1 = self.box_px
                win = (max(0, y0 - mp), min(H, y1 + mp), max(0, x0 - mp), min(W, x1 + mp))
            self._crops[key] = win
        return self._crops[key]

    def mask_in(self, win):
        y0, y1, x0, x1 = win
        return self.mask[y0:y1, x0:x1]

    # ---- the floored capture on a window
    def S(self, win, floor='gauss'):
        key = ('S', win, floor)
        if key not in self._cache:
            y0, y1, x0, x1 = win
            B = self.B[y0:y1, x0:x1]
            if floor == 'gauss':
                S = _blur(B, 0.4 * self.f, 'clamp')
            else:  # the literal decimation null: f x f block average anchored at the window, bilinear back up
                S = _box_decimate(B, self.f)
            self._cache[key] = S
        return self._cache[key]

    def unit_dev(self, units):
        return {'pt': self.scale, 'texel': float(self.f), 'dev': 1.0}[units]

    def blur(self, src_key, X, sig_dev, mode, weight=None, wkey=None):
        """Cached Gaussian of a window image. mode 'clamp' | 'norm' (normalised zero padding, or normalised over
        `weight`, a support mask on the window). `wkey` names the weight in the store's key by its content (the
        forward engine's rounded-shape support passes it); without it the key holds id(weight), which is safe
        only while the caller keeps that array alive for the cell's life (read_local caches its weights so)."""
        wk = None if weight is None else (wkey if wkey is not None else ('id', id(weight)))
        key = (self.token, src_key, round(float(sig_dev), 4), mode, wk)
        hit = _BLURS.get(key)
        if hit is not None:
            _BLURS.move_to_end(key)
            return hit
        out = _blur(X, sig_dev, mode, weight)
        _remember(key, out)
        return out


# One least-recently-used store for every cell's blurs, bounded in BYTES per process. A per-cell count bound
# (the first version: 160 blurs a cell) let a fit over 50-90 cells at 2x hold 12-20 GB per worker, and the
# machine's memory pressure stopped proof 2's last runs; the bound below keeps a worker near 1-2 GB whatever
# the number of cells, and changes no value, only what is recomputed.
from collections import OrderedDict  # noqa: E402

BLUR_CACHE_BYTES = 0.8e9
_BLURS = OrderedDict()
_BLUR_BYTES = [0]


def _remember(key, arr):
    _BLURS[key] = arr
    _BLUR_BYTES[0] += arr.nbytes
    while _BLUR_BYTES[0] > BLUR_CACHE_BYTES and len(_BLURS) > 1:
        _, old = _BLURS.popitem(last=False)
        _BLUR_BYTES[0] -= old.nbytes


FAST_FROM_DEV = 12.0      # blurs at or above this width run decimated (see _blur_decimated); 0 disables


def _blur(X, sig, mode, weight=None):
    if sig < 1e-3:
        return X
    if X.ndim == 3:
        return np.stack([_blur(X[..., c], sig, mode, weight) for c in range(X.shape[2])], -1)
    if FAST_FROM_DEV and sig >= FAST_FROM_DEV:
        return _blur_decimated(X, sig, mode, weight)
    if mode == 'clamp':
        return ndimage.gaussian_filter(X, sig, mode='nearest', truncate=TRUNCATE)
    wt = np.ones_like(X) if weight is None else weight
    num = ndimage.gaussian_filter(X * wt, sig, mode='constant', truncate=TRUNCATE)
    den = ndimage.gaussian_filter(wt, sig, mode='constant', truncate=TRUNCATE)
    return np.where(den > 1e-9, num / np.maximum(den, 1e-12), X)


def _blur_decimated(X, sig, mode, weight=None):
    """A wide Gaussian computed on a q-times decimated grid (q = 2 below 48 device px, 4 above) and brought back
    bilinearly. The window is first padded at FULL resolution by the kernel's reach (edge replication for
    clamp, zeros for the normalised mode), so the edge semantics are exactly the direct filter's; the
    decimated Gaussian's width is reduced by the variance the block average ((q^2 - 1) / 12) and the bilinear
    return (q^2 / 6) add. Proof 1 part D states its error against the direct filter."""
    q = 2 if sig < 48 else 4
    sd = np.sqrt(sig ** 2 - (q * q - 1) / 12.0 - q * q / 6.0) / q
    P = int(np.ceil(TRUNCATE * sig / q + 2)) * q
    H, W = X.shape

    def dec_up(Z, pad_mode):
        Zp = np.pad(Z, P, mode=pad_mode)
        Hp, Wp = Zp.shape
        ny, nx = -(-Hp // q), -(-Wp // q)
        Zp = np.pad(Zp, ((0, ny * q - Hp), (0, nx * q - Wp)), mode='edge')
        Yd = ndimage.gaussian_filter(Zp.reshape(ny, q, nx, q).mean(axis=(1, 3)), sd, mode='nearest',
                                     truncate=TRUNCATE)
        yy = (np.arange(P, P + H) + 0.5) / q - 0.5
        xx = (np.arange(P, P + W) + 0.5) / q - 0.5
        return ndimage.map_coordinates(Yd, np.meshgrid(yy, xx, indexing='ij'), order=1, mode='nearest')
    if mode == 'clamp':
        return dec_up(X, 'edge')
    wt = np.ones_like(X) if weight is None else weight
    num, den = dec_up(X * wt, 'constant'), dec_up(wt, 'constant')
    return np.where(den > 1e-9, num / np.maximum(den, 1e-12), X)


def _box_decimate(B, f):
    H, W = B.shape[:2]
    ny, nx = -(-H // f), -(-W // f)
    pad = ((0, ny * f - H), (0, nx * f - W)) + (((0, 0),) if B.ndim == 3 else ())
    Bp = np.pad(B, pad, mode='edge')
    if B.ndim == 3:
        St = Bp.reshape(ny, f, nx, f, B.shape[2]).mean(axis=(1, 3))
        return np.stack([_upsample(St[..., c], f, H, W) for c in range(B.shape[2])], -1)
    return _upsample(Bp.reshape(ny, f, nx, f).mean(axis=(1, 3)), f, H, W)


def _upsample(St, f, H, W):
    yy = (np.arange(H) + 0.5) / f - 0.5
    xx = (np.arange(W) + 0.5) / f - 0.5
    return ndimage.map_coordinates(St, np.meshgrid(yy, xx, indexing='ij'), order=1, mode='nearest')


# ---------------------------------------------------------------- the maps C, W (and Wk, Bl) of a family

def _edge_mode(cell, fam):
    if fam.edge == 'swap':
        return 'norm' if cell.active else 'clamp'
    if fam.edge != 'auto':
        return fam.edge
    return 'clamp' if cell.active else 'norm'


def sigma_n_pt(cell, fam, p, d):
    """The narrow width in the family's units at depth d (array), before conversion to device px."""
    if fam.narrow == 'free':
        return np.full_like(d, free_sigma(p, cell.pose, cell.span))
    o = opacity_law(d, cell.span, cell.active)
    return p['k_n'] * RN * o


FREE_SPANS = (64.0, 80.0, 96.0, 128.0, 160.0)   # t = 0 (every s <= 64), 1/6, 1/3, 2/3, 1


def free_sigma(p, pose, s):
    """The free sigma_n(span) law: one ordinate per declared span stratum and pose (pt), linear in s between
    them, the t = 0 ordinate for every s <= 64 and the t = 1 ordinate above 160 (the declared clamp)."""
    ys = [p[f'sn_{pose}_{int(v)}'] for v in FREE_SPANS]
    return float(np.interp(min(max(s, 64.0), 160.0), FREE_SPANS, ys))


def narrow_map(cell, fam, p, X, src_key, win, mode, at):
    """C on the pixels `at` (boolean window mask) from source X on the window."""
    u = cell.unit_dev(fam.units)
    dwin = cell.d[win[0]:win[1], win[2]:win[3]]
    if fam.narrow == 'mix':
        o = opacity_law(dwin[at], cell.span, cell.active)
        o = o[:, None] if X.ndim == 3 else o
        Gx = cell.blur(src_key, X, p['k_n'] * RN * u, mode)[at]
        return (1 - o) * X[at] + o * Gx
    sig = sigma_n_pt(cell, fam, p, dwin[at]) * u
    lo, hi = float(sig.min()), float(sig.max())
    if hi - lo < 1e-4:
        return cell.blur(src_key, X, lo, mode)[at]
    levels = [lo]
    while levels[-1] < hi - 1e-9:
        levels.append(min(hi, levels[-1] + NARROW_STEP[0] + NARROW_STEP[1] * levels[-1]))
    levels = np.array(levels)
    stack = np.stack([cell.blur(src_key, X, v, mode)[at] for v in levels])
    idx = np.clip(np.searchsorted(levels, sig) - 1, 0, len(levels) - 2)
    fr = (sig - levels[idx]) / (levels[idx + 1] - levels[idx])
    ar = np.arange(sig.size)
    a, b = stack[idx, ar], stack[idx + 1, ar]
    if X.ndim == 3:
        fr = fr[:, None]
    return a + fr * (b - a)


def maps(cell, fam, p):
    """The blurred terms on the deep mask, for a family and its width parameters. Returns a dict with
    C, W (and Wk for K2, Bl for the bleed), each an (n,) or (n, 3) array over cell.mask pixels, plus the
    window images needed by R2."""
    mode = _edge_mode(cell, fam)
    u = cell.unit_dev(fam.units)
    k_w = p.get('k_w', p.get('k'))
    # C (and the bleed) are taken on R_fp, the box plus the declared margin; W-canvas moves W and C to the canvas
    # (its declared form). W-shape moves ONLY W: its window and normalising weight are the rounded shape grown by
    # mu, and its narrow term stays on R_fp as LT's does and as read_local's readers take it. (Until the review of
    # b151aff4 the shape window replaced R_fp for C too, which moved C by up to 4.6 encoded codes on receded
    # p16 cells at mu = 4.)
    win = cell.crop('canvas') if fam.support == 'canvas' else cell.crop('box')
    S = cell.S(win, fam.floor)
    at = cell.mask_in(win)
    out = {}
    # the narrow term (in its space)
    if fam.order == 'blurlast':
        out['S'] = S[at]
    elif fam.space_c == 'lin':
        Sl = srgb_to_lin(255 * S)
        out['C'] = lin_to_srgb(narrow_map(cell, fam, p, Sl, ('Sl', win, fam.floor), win, mode, at)) / 255
    else:
        out['C'] = narrow_map(cell, fam, p, S, ('S', win, fam.floor), win, mode, at)
    # the wide term on its support
    wwin, Sw, atw, weight, wkey, wmode = win, S, at, None, None, mode
    if fam.support == 'shape':
        mu = round(float(p['mu']), 4)
        wwin = cell.crop('shape', mu)
        Sw = cell.S(wwin, fam.floor)
        atw = cell.mask_in(wwin)
        weight = (cell.d[wwin[0]:wwin[1], wwin[2]:wwin[3]] <= mu).astype(float)
        wkey, wmode = ('shape', mu), 'norm'
    wsrc = ('S', wwin, fam.floor)
    sw = k_w * RW * u
    W = cell.blur(wsrc, Sw, sw, wmode, weight, wkey)[atw]
    if fam.wkind == 'tails':
        W2 = cell.blur(wsrc, Sw, p['s2'] * cell.scale, wmode, weight, wkey)[atw]
        W = (1 - p['a']) * W + p['a'] * W2
    out['W'] = W
    if fam.fills == 2:
        out['Wk'] = cell.blur(wsrc, Sw, p['sk'] * cell.scale, wmode, weight, wkey)[atw]
    if fam.bleed != 'none' and cell.active and cell.span > 64:
        kb = p['k_b'] if fam.bleed == 'own' else k_w
        out['Bl'] = cell.blur(('S', win, fam.floor), S, kb * BLEED_REACH * cell.span * u, mode)[at]
    if fam.order == 'blurlast':
        out['_win'] = (win, S, at, mode)
    return out


def bleed_weight(cell):
    """The Normal variant's structural weight (bleed_form 'normal', the form before the review of b151aff4). Its
    assumptions, stated: the bleed is a Normal mix at the declared opacity ob in BOTH schemes (the dump's darken
    blend in light is not taken); it sits inside T's argument (pre-T); it covers the whole shape at one weight (the
    dump's amount, height and distances are not taken); its colour matrix's affine part is absorbed by native T
    read on uniform greys, which is exact only because the weight is the same everywhere on the shape, and its
    saturation is not taken. Then (1 - ob) M + ob (black + (white - black) Bl) is, up to an affine map of the
    whole output that native T absorbs, (1 - beta) M + beta Bl with beta below."""
    ob = BLEED_OPACITY[cell.scheme] * cell.t
    dl = BLEED_SPAN[cell.scheme]
    return ob * dl / (1 - ob + ob * dl)


# ---------------------------------------------------------------- the dump-literal bleed (the declared form)
#
# The declared form since the review of b151aff4 takes every bleed input the dump records, each with its reading:
#   radius     inputBleedBlurRadius 0.35 s, scaled by the family's k (k_w, or k_b when its own) as every radius is;
#              the source is the floored capture on R_fp, as C's;
#   colour     inputBleedColorMatrix: Q = black + (white - black) sat(Bl) on ENCODED values, sat a Rec.709
#              luma-preserving saturation (1.2 light, 1 dark; greys are unmoved), as memo D reads the face matrix;
#   blend      inputBleedDarkenBlend b: X' = (1 - w) X + w [b min(X, Q) + (1 - b) Q], per channel: a darken blend in
#              light (b = 1) and a Normal blend in dark (b = 0);
#   weight     w = ob r(d), ob = inputBleedOpacity (0.5 t light, 0.8 t dark);
#   band       inputBleedHeight h = 0.35 s is read as the depth over which the bleed acts, and inputBleedDistance0 /
#              inputBleedDistance1 (1, 0) as the ramp's ends in units of h measured inward from the edge: r = 1 at the
#              edge (depth 0 h), falling linearly to 0 at depth 1 h. inputBleedAmount equals the height in every dump,
#              so the reading takes it as the same extent and models no displacement of the bleed's source;
#   place      a discrete choice: inside T's argument (X = M, 'pre') or after T (X = T(M) / 255, 'post'; memo E's key
#              order, Face before Bleed, is only a pointer).
# Native T is measured on family A (charter clause 6), so the family is rendered through the face that makes its
# own uniform response reproduce native T at the deep median (face_T): for a uniform backdrop g the bleed moves
# the output by a depth-graded amount (the dark matrix does not map g to g), and the deep median of that is what
# family A reads. A family with a depth-graded uniform response therefore keeps clause 7's deep-MEDIAN invariance
# by construction while its per-pixel uniform response departs from T(g) inside the band (reported by
# uniform_invariance). The light darken leaves a uniform backdrop unmoved before T (Q(g) = 0.9 + 0.1 g >= g).

def bleed_ramp(cell, d):
    """The literal band r(d) on SDF depths d (pt, negative inside)."""
    h = BLEED_REACH * cell.span
    return np.interp(-np.asarray(d) / h, [BLEED_DISTANCES[1], BLEED_DISTANCES[0]], [1.0, 0.0])


def bleed_colour(cell, Bl):
    black, white, sat = BLEED_MATRIX[cell.scheme]
    if Bl.ndim == 2 and sat != 1.0:
        L = (Bl @ G.W709)[:, None]
        Bl = L + sat * (Bl - L)
    return black + (white - black) * Bl


def bleed_blend(cell, X, Q, w):
    b = BLEED_DARKEN[cell.scheme]
    if X.ndim == 2 and np.ndim(w) == 1:
        w = w[:, None]
    return X + w * (b * np.minimum(X, Q) + (1 - b) * Q - X)


def bleed_w(cell):
    """w = ob r(d) on the deep mask (cached on the cell)."""
    if 'bleed_w' not in cell._cache:
        cell._cache['bleed_w'] = BLEED_OPACITY[cell.scheme] * cell.t * bleed_ramp(cell, cell.d[cell.mask])
    return cell._cache['bleed_w']


class FaceT:
    """The face a literal-bleed family renders through: native T with the family's own uniform response at the
    deep median (w_med = median of w over the mask) divided out, so that family A's deep median reads native T.
    pre: y = T_f(255 X'), T_f(c) = T(255 U^-1(c / 255)), U(g) = the literal blend of g at w_med.
    post: y = 255 X', X = T_f(255 M) / 255, T_f(c) solves 255 blend(T_f(c) / 255, Q(c / 255), w_med) = T(c)."""

    def __init__(self, cell, T, at):
        self.T, self.at, self.cell = T, at, cell
        self.w = float(np.median(bleed_w(cell)))
        self.trust_below = getattr(T, 'trust_below', None)
        black, white, _ = BLEED_MATRIX[cell.scheme]
        self.q = lambda g: black + (white - black) * g
        self.b = BLEED_DARKEN[cell.scheme]
        if at == 'pre':
            g = np.linspace(-0.5, 1.5, 4001)
            U = g + self.w * (self.b * np.minimum(g, self.q(g)) + (1 - self.b) * self.q(g) - g)
            self.g, self.U = g, U

    def __call__(self, c):
        c = np.asarray(c, float)
        if self.at == 'pre':
            return self.T(255 * np.interp(c / 255, self.U, self.g))
        y = self.T(c) / 255
        Q, w = self.q(c / 255), self.w
        normal = (y - w * Q) / (1 - w)
        if self.b == 0:
            return 255 * normal
        return 255 * np.where(y <= Q, y, normal)


def face_T(cell, fam, T):
    key = ('faceT', fam.bleed_at, id(T))
    if key not in cell._cache:
        cell._cache[key] = (FaceT(cell, T, fam.bleed_at), T)     # T kept alive with its id
    return cell._cache[key][0]


def _hinge(C, W, sg, lam, knee):
    if knee == 'luma' and C.ndim == 2:
        gap = sg * ((W - C) @ G.W709)
        return C + lam * (gap > 0)[:, None] * (W - C)
    return C + sg * lam * np.maximum(0, sg * (W - C))


def compose(cell, fam, mp, lam, T=None):
    """Output codes on the deep mask from the maps and lam."""
    T = T or cell.T
    sg = 1 if cell.scheme == 'light' else -1
    W = mp['W']
    Wk = mp.get('Wk', W)
    if fam.order == 'before':
        TC, TW, TWk = T(255 * mp['C']), T(255 * W), T(255 * Wk)
        return (1 - WN) * _hinge(TC, TWk, sg, lam, fam.knee) + WN * TW
    if fam.order == 'blurlast':
        win, S, at, mode = mp['_win']
        raise NotImplementedError('R2 needs the full window; use render_window')
    N = _hinge(mp['C'], Wk, sg, lam, fam.knee)
    M = (1 - WN) * N + WN * W
    if 'Bl' in mp and fam.bleed_form == 'literal':
        Tf = face_T(cell, fam, T)
        Q, w = bleed_colour(cell, mp['Bl']), bleed_w(cell)
        if fam.bleed_at == 'pre':
            return Tf(255 * bleed_blend(cell, M, Q, w))
        return 255 * bleed_blend(cell, Tf(255 * M) / 255, Q, w)
    if 'Bl' in mp:
        b = bleed_weight(cell)
        M = (1 - b) * M + b * mp['Bl']
    return T(255 * M)


def render(cell, fam, p, T=None):
    """Predicted output codes on cell.mask (n,) or (n, 3)."""
    if fam.order == 'blurlast':
        return _render_blurlast(cell, fam, p, T)
    return compose(cell, fam, maps(cell, fam, p), p['lam'], T)


def _render_blurlast(cell, fam, p, T=None):
    """R2 (a rejected null): the fill composites onto the sharp capture and the narrow blur comes last."""
    T = T or cell.T
    sg = 1 if cell.scheme == 'light' else -1
    mode = _edge_mode(cell, fam)
    u = cell.unit_dev(fam.units)
    win = cell.crop('box')
    S = cell.S(win, fam.floor)
    Wf = cell.blur(('S', win, fam.floor), S, p.get('k_w', p.get('k')) * RW * u, mode)
    N = S + sg * p['lam'] * np.maximum(0, sg * (Wf - S))
    M = (1 - WN) * N + WN * Wf
    at = cell.mask_in(win)
    Mn = narrow_map(cell, fam.with_(order='after'), p, M, ('M', win, round(p['lam'], 6),
                                                          round(p.get('k_w', p.get('k')), 6)), win, mode, at)
    return T(255 * Mn)


def expand(fam, p):
    """Fill the implied parameters: LT's one k governs both radii unless the family frees them."""
    q = dict(p)
    if 'k' in q:
        q.setdefault('k_n', q['k'])
        q.setdefault('k_w', q['k'])
    return q


def synth(cell, fam, p, seed=0, noise=0.5, T=None):
    """A synthetic capture: the family rendered through T, plus uniform +-noise, rounded to codes (memo C/E's
    quantisation), written into a canvas image that is NaN outside the deep mask."""
    y = render(cell, fam, expand(fam, p), T)
    rng = np.random.default_rng(seed)
    yq = np.clip(np.round(y + rng.uniform(-noise, noise, y.shape)), 0, 255)
    shape = cell.d.shape + ((3,) if cell.rgb else ())
    img = np.full(shape, np.nan)
    img[cell.mask] = yq
    cell.y = img
    return img


def uniform_invariance(families, levels=(0, 32, 64, 128, 160, 208, 255), eps=1e-9):
    """Clause 7 by construction: every family maps a constant backdrop to T(level) (before rounding). Returns
    (name, worst per-pixel |y - T(g)|, worst |deep median - T(g)|): clause 7's metric is the deep median, and the
    dump-literal bleed, whose uniform response is graded in depth inside its band, is invariant only there."""
    rows = []
    for name, (fam, p) in families.items():
        worst, worst_med = 0.0, 0.0
        for ep in ENDPOINTS:
            sch, pose = ep.split('-')
            for comp in ('capsule-button', 'rrect-md', 'rrect-lg'):
                if fam.bleed != 'none' and pose != 'rest':
                    continue
                for g in levels:
                    c = Cell(f'g{g}', {'kind': 'solid', 'srgb': [g, g, g]}, comp, 1, sch, pose)
                    y = render(c, fam, expand(fam, p))
                    t = float(c.T(np.array([float(g)]))[0])
                    worst = max(worst, float(np.abs(y - t).max()))
                    worst_med = max(worst_med, abs(float(np.median(y)) - t))
        rows.append((name, worst, worst_med))
    return rows
