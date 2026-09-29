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
# The active bleed's declared matrix (memo D §3): white - black of the bleed colour matrix, by scheme.
BLEED_SPAN = {'light': 1.0 - 0.9, 'dark': 0.5 - 0.125}
BLEED_OPACITY = {'light': 0.5, 'dark': 0.8}      # x t, active only, s > 64


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
    floor: str = 'gauss'         # 'gauss' (memo C's 0.8-dev floor) | 'box' (literal decimation, a null)
    free_params: tuple = ('k', 'lam')

    def with_(self, **kw):
        return replace(self, **kw)


class Cell:
    """One cell: backdrop, shape, scale, endpoint, the footprint crop and the deep evaluation mask."""

    def __init__(self, cid, background, component, scale, scheme, pose, d_in=None, rgb=False, T=None):
        self.id, self.scale, self.scheme, self.pose = cid, scale, scheme, pose
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
            d_in = max(12.0, 0.23 * self.span) if self.active else 8.0
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

    def blur(self, src_key, X, sig_dev, mode, weight=None):
        """Cached Gaussian of a window image. mode 'clamp' | 'norm' (normalised zero padding, or normalised over
        `weight`, a support mask on the window)."""
        key = (src_key, round(float(sig_dev), 4), mode, None if weight is None else id(weight))
        if key in self._cache:
            return self._cache[key]
        out = _blur(X, sig_dev, mode, weight)
        if len(self._cache) > 160:
            for k in list(self._cache)[:40]:
                if k[0] != 'S':
                    del self._cache[k]
        self._cache[key] = out
        return out


def _blur(X, sig, mode, weight=None):
    if sig < 1e-3:
        return X
    if X.ndim == 3:
        return np.stack([_blur(X[..., c], sig, mode, weight) for c in range(X.shape[2])], -1)
    if mode == 'clamp':
        return ndimage.gaussian_filter(X, sig, mode='nearest', truncate=TRUNCATE)
    wt = np.ones_like(X) if weight is None else weight
    num = ndimage.gaussian_filter(X * wt, sig, mode='constant', truncate=TRUNCATE)
    den = ndimage.gaussian_filter(wt, sig, mode='constant', truncate=TRUNCATE)
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
    win = cell.crop('box')
    if fam.support == 'canvas':
        win = cell.crop('canvas')
    elif fam.support == 'shape':
        win = cell.crop('shape', p['mu'])
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
    weight = None
    wmode = mode
    if fam.support == 'shape':
        key = ('shape-weight', win, round(p['mu'], 4))
        if key not in cell._cache:
            cell._cache[key] = (cell.d[win[0]:win[1], win[2]:win[3]] <= p['mu']).astype(float)
        weight = cell._cache[key]
        wmode = 'norm'
    sw = k_w * RW * u
    W = cell.blur(('S', win, fam.floor), S, sw, wmode, weight)[at]
    if fam.wkind == 'tails':
        W2 = cell.blur(('S', win, fam.floor), S, p['s2'] * cell.scale, wmode, weight)[at]
        W = (1 - p['a']) * W + p['a'] * W2
    out['W'] = W
    if fam.fills == 2:
        out['Wk'] = cell.blur(('S', win, fam.floor), S, p['sk'] * cell.scale, wmode, weight)[at]
    if fam.bleed != 'none' and cell.active and cell.span > 64:
        kb = p['k_b'] if fam.bleed == 'own' else k_w
        out['Bl'] = cell.blur(('S', win, fam.floor), S, kb * 0.35 * cell.span * u, mode)[at]
    if fam.order == 'blurlast':
        out['_win'] = (win, S, at, mode)
    return out


def bleed_weight(cell):
    """The bleed's structural weight after native T absorbs its matrix's affine part (see Family docs)."""
    ob = BLEED_OPACITY[cell.scheme] * cell.t
    dl = BLEED_SPAN[cell.scheme]
    return ob * dl / (1 - ob + ob * dl)


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
    """Clause 7 by construction: every family maps a constant backdrop to T(level) exactly (before rounding)."""
    rows = []
    for name, (fam, p) in families.items():
        worst = 0.0
        for ep in ENDPOINTS:
            sch, pose = ep.split('-')
            for comp in ('capsule-button', 'rrect-md', 'rrect-lg'):
                if fam.bleed != 'none' and pose != 'rest':
                    continue
                for g in levels:
                    c = Cell(f'g{g}', {'kind': 'solid', 'srgb': [g, g, g]}, comp, 1, sch, pose)
                    y = render(c, fam, expand(fam, p))
                    worst = max(worst, float(np.abs(y - c.T(np.full(y.shape, float(g)))).max()))
        rows.append((name, worst))
    return rows
