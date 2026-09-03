"""W12 G3 measurement library: the two probes (1x W9, 2x W12) read on one code path.

Everything here is analysis. No constant under `packages/` is touched and nothing is captured; the
only inputs are committed probe fixtures, committed backdrop rasters and the analytic checkerboard
plate (verified byte-equal to the committed rasters by `verify_plates`).

Lengths are CSS px unless a name says device px; a capture at scale s has s device px per CSS px.
Captures and plates are read as linear luminance (Rec.709 of sRGB-decoded channels), the space the
reference's own averaging was measured in (claims 5.31) and the space every W11 body fit used.

Run from the repository root with the analysis venv:
    /Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python packages/calibration/results/.../g3/g3_*.py
"""
import json
import os

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates, uniform_filter

ROOT = os.environ.get('VITREA_ROOT', '/Users/new/Developer/GitHub/designer')
PROBE1 = f'{ROOT}/packages/calibration/results/2026-09-02-w9-probe/apple-macos-26.5-1x-light-standard'
PROBE2 = f'{ROOT}/packages/calibration/results/2026-09-03-w12-lens/probe-2x/apple-macos-26.5-2x-light-standard'
BG2 = f'{ROOT}/packages/calibration/results/2026-09-03-w12-lens/probe-2x/backgrounds'
BG_FIX = f'{ROOT}/apps/reference-apple/fixtures/backgrounds'
BG1_SCRATCH = '/Users/new/.claude/jobs/5c70e47f/tmp/w9-probe-fixtures/backgrounds'
SNAP2X = '/Users/new/.claude/jobs/5c70e47f/tmp/w12'  # the five 2x probe run snapshots (scratch)
OUT = f'{ROOT}/packages/calibration/results/2026-09-03-w12-lens/g3'

CANVAS = (320, 200)
COMP = {  # w, h, radius in CSS px; centred on the canvas
    'rrect-sm': (64, 32, 8), 'capsule-button': (120, 44, 22), 'rrect-md': (160, 96, 20),
    'rrect-ml': (224, 128, 27), 'rrect-lg': (280, 160, 34),
}
SPAN = {'rrect-sm': 32, 'capsule-button': 44, 'rrect-md': 96, 'rrect-ml': 128, 'rrect-lg': 160}
COMPS = ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg']
FIT_COMPS = ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml']  # rrect-lg is the holdout
PITCH = {'checkerboard-4': 4, 'checkerboard-8': 8, 'checkerboard': 16, 'checkerboard-32': 32,
         'checkerboard-64': 64, 'checkerboard-lc16': 16}
PITCHES4 = ['checkerboard-8', 'checkerboard', 'checkerboard-32', 'checkerboard-64']  # 5.41's fit set
PITCHES5 = ['checkerboard-4'] + PITCHES4
LC16 = 'checkerboard-lc16'
SCALES = (1, 2)

# The reference's own parameters (claims 5.50 1): quarter-device-scale buffer, blur radius in buffer px.
BUFFER_SCALE = 0.25


def blur_radius_buffer_px(span):
    """Apple's `inputBlurRadius`, buffer px: max(4/3, (span + 8)/42) (claims 5.50 1)."""
    return max(4.0 / 3.0, (span + 8.0) / 42.0)


# ---------------------------------------------------------------- colour


def load_rgb(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float64) / 255.0


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def luma_lin(rgb):
    lin = srgb_to_lin(rgb)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


# ---------------------------------------------------------------- captures and plates


def probe_dir(scale):
    return {1: PROBE1, 2: PROBE2}[scale]


def probe_path(scene, scale):
    return f'{probe_dir(scale)}/{scene}.png'


def capture(scene, scale):
    """A probe cell as linear luminance; asserts the fixture's own pixel size matches the scale."""
    Y = luma_lin(load_rgb(probe_path(scene, scale)))
    assert Y.shape == (CANVAS[1] * scale, CANVAS[0] * scale), (scene, scale, Y.shape)
    return Y


def checker_plate(cell_css, scale, a=0.0, b=1.0):
    """Bottom-left anchored checkerboard (AppKit flipped y), linear luminance."""
    W, H = CANVAS[0] * scale, CANVAS[1] * scale
    c = cell_css * scale
    iy = np.floor((H - 1 - np.arange(H)) / c).astype(int)
    ix = np.floor(np.arange(W) / c).astype(int)
    par = (ix[None, :] + iy[:, None]) % 2
    return np.where(par == 0, a, b).astype(np.float64)


LC16_LEVELS = (0.21586050011389923, 0.7835377915261935)  # read from the committed lc16 rasters

_plate_cache = {}


def plate(backdrop, scale):
    """The backdrop as linear luminance at the given scale.

    Checkerboard families are generated analytically (`verify_plates` proves the generator equals the
    committed rasters at both scales); `photo` and the solids are read from the committed rasters.
    """
    key = (backdrop, scale)
    if key in _plate_cache:
        return _plate_cache[key]
    if backdrop == LC16:
        P = checker_plate(16, scale, *LC16_LEVELS)
    elif backdrop in PITCH:
        P = checker_plate(PITCH[backdrop], scale)
    else:
        path = f'{BG2}/{backdrop}@2x.png' if scale == 2 else f'{BG_FIX}/{backdrop}@1x.png'
        if not os.path.exists(path):
            path = f'{BG1_SCRATCH}/{backdrop}@{scale}x.png'
        P = luma_lin(load_rgb(path))
    _plate_cache[key] = P
    return P


def verify_plates():
    """Analytic checker plates against the committed rasters, both scales. Returns max |difference|."""
    out = {}
    for backdrop in list(PITCH) + [LC16]:
        for scale in SCALES:
            path = f'{BG2}/{backdrop}@2x.png' if scale == 2 else f'{BG1_SCRATCH}/{backdrop}@1x.png'
            if not os.path.exists(path):
                continue
            R = luma_lin(load_rgb(path))
            out[f'{backdrop}@{scale}x'] = float(np.abs(R - plate(backdrop, scale)).max())
    return out


# ---------------------------------------------------------------- geometry


def sdf_rrect(W, H, cx, cy, w, h, r):
    """Signed distance (negative inside) on pixel centres, device px."""
    ys, xs = np.mgrid[0:H, 0:W]
    px = np.abs(xs + 0.5 - cx) - (w / 2 - r)
    py = np.abs(ys + 0.5 - cy) - (h / 2 - r)
    return (np.sqrt(np.maximum(px, 0) ** 2 + np.maximum(py, 0) ** 2)
            + np.minimum(np.maximum(px, py), 0) - r)


_depth_cache = {}


def depth(comp, scale):
    """Depth u inside the silhouette, CSS px (positive inside, 0 on the contour)."""
    key = (comp, scale)
    if key not in _depth_cache:
        W, H = CANVAS[0] * scale, CANVAS[1] * scale
        w, h, r = COMP[comp]
        d = sdf_rrect(W, H, 160 * scale, 100 * scale, w * scale, h * scale, r * scale)
        _depth_cache[key] = -d / scale
    return _depth_cache[key]


def box_for(comp, scale):
    """5.41's inset interior box: inset min(max(radius, 12), h/2 − 8) CSS px. (x0, x1, y0, y1)."""
    w, h, r = COMP[comp]
    m = min(max(r, 12), h / 2 - 8)
    return (int(round((160 - w / 2 + m) * scale)), int(round((160 + w / 2 - m) * scale)),
            int(round((100 - h / 2 + m) * scale)), int(round((100 + h / 2 - m) * scale)))


def box_mask(comp, scale):
    x0, x1, y0, y1 = box_for(comp, scale)
    m = np.zeros((CANVAS[1] * scale, CANVAS[0] * scale), bool)
    m[y0:y1, x0:x1] = True
    return m


def band_mask(comp, scale, u0, u1):
    """Pixels with u0 ≤ u < u1 CSS px inside the silhouette (the depth bands of the depth reading)."""
    u = depth(comp, scale)
    return (u >= u0) & (u < u1)


# ---------------------------------------------------------------- linear fits


def lstsq_cols(y, cols):
    """y ≈ c0 + Σ ci·col_i; returns (coef, rms, r2)."""
    X = np.stack([np.ones_like(y)] + list(cols), 1)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    rms = float(np.sqrt(np.mean(res ** 2)))
    ss = float(np.sum((y - y.mean()) ** 2))
    return coef, rms, (1 - float(res @ res) / ss if ss > 0 else float('nan'))


_gcache = {}


def G(P, key, sigma_css, scale):
    """Gaussian of the plate, σ given in CSS px and applied in device px."""
    k = (key, scale, round(float(sigma_css), 4))
    if k not in _gcache:
        s = sigma_css * scale
        _gcache[k] = gaussian_filter(P, s, mode='nearest') if s > 1e-6 else P
    return _gcache[k]


SIG_SINGLE = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0]
SIG_SHARP = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0]
SIG_HEAVY = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 14.0, 16.0, 18.0, 20.0]


MIN_COL_ABS, MIN_COL_REL = 0.005, 0.05
"""A blurred plate whose surviving contrast under the mask is below max(0.005 linear luminance,
5% of the plate's own contrast there) carries no information about its own width: the amplitude that
multiplies it is unidentifiable and least squares answers with an arbitrarily large number. Every fit
below refuses such a column and records the largest σ that survives, so "σ is not identifiable beyond
X on this pitch" is said rather than fitted."""


def col_floor(P, mask):
    return max(MIN_COL_ABS, MIN_COL_REL * float(P[mask].std()))


def sigma_ceiling(P, key, mask, scale, sigmas=SIG_SINGLE):
    """The largest σ (CSS px) whose blurred plate still carries identifiable contrast under the mask."""
    floor = col_floor(P, mask)
    ok = [s for s in sigmas if G(P, key, s, scale)[mask].std() >= floor]
    return max(ok) if ok else 0.0


def fit_single(Y, P, mask, scale, key, sigmas=SIG_SINGLE):
    """Y ≈ a + t·G_σ(P) over the mask. Returns dict(sigma, a, t, rms, r2) at the best σ, and the curve."""
    y = Y[mask]
    floor = col_floor(P, mask)
    best, curve = None, []
    for s in sigmas:
        col = G(P, key, s, scale)[mask]
        if col.std() < floor:
            continue
        coef, rms, r2 = lstsq_cols(y, [col])
        rec = dict(sigma=s, a=float(coef[0]), t=float(coef[1]), rms=rms, r2=r2,
                   col_std=float(col.std()))
        curve.append(rec)
        if best is None or rms < best['rms']:
            best = rec
    if best is None:  # every width is annihilated: report the level alone
        best = dict(sigma=float('nan'), a=float(y.mean()), t=float('nan'),
                    rms=float(y.std()), r2=0.0, col_std=0.0)
    return best, curve


def _nnls_two(y, cs, ch):
    """y ≈ a + t_s·cs + t_h·ch with t_s, t_h ≥ 0 (a free): the amplitudes are transmissions."""
    from scipy.optimize import lsq_linear
    X = np.stack([np.ones_like(y), cs, ch], 1)
    r = lsq_linear(X, y, bounds=([-np.inf, 0, 0], [np.inf, np.inf, np.inf]))
    res = y - X @ r.x
    rms = float(np.sqrt(np.mean(res ** 2)))
    ss = float(np.sum((y - y.mean()) ** 2))
    return r.x, rms, (1 - float(res @ res) / ss if ss > 0 else float('nan'))


def _two_record(coef, rms, r2, ss, sh, n):
    t = float(coef[1] + coef[2])
    return dict(sigma_sharp=ss, sigma_heavy=sh, a=float(coef[0]), t_sharp=float(coef[1]),
                t_heavy=float(coef[2]), t=t,
                share=float(coef[2] / t) if abs(t) > 1e-9 else float('nan'),
                rms=rms, r2=r2, n=int(n))


def fit_two(Y, P, mask, scale, key, sig_sharp=SIG_SHARP, sig_heavy=SIG_HEAVY, min_gap=1.5):
    """Y ≈ a + t_s·G_σs(P) + t_h·G_σh(P), both σ on a grid, both amplitudes non-negative.

    share = t_h/(t_s + t_h) is the heavy component's share of the transmission — the quantity
    5.38 3 and 5.41 2 report.
    """
    return fit_two_joint([Y], [(key, P)], [mask], scale, sig_sharp, sig_heavy, min_gap)


def fit_two_joint(Ys, P_by_key, masks, scale, sig_sharp=SIG_SHARP, sig_heavy=SIG_HEAVY, min_gap=1.5):
    """The two-component fit pooled over several plates (5.38 3's 'joint over the pitches'):
    one (a, t_s, t_h) for the pooled samples, one (σs, σh) shared."""
    y = np.concatenate([Y[m] for Y, m in zip(Ys, masks)])
    P0 = np.concatenate([P[m] for (k, P), m in zip(P_by_key, masks)])
    floor = max(MIN_COL_ABS, MIN_COL_REL * float(P0.std()))
    cols = {}
    for s in sorted(set(sig_sharp) | set(sig_heavy)):
        c = np.concatenate([G(P, k, s, scale)[m] for (k, P), m in zip(P_by_key, masks)])
        if c.std() >= floor:
            cols[s] = c
    best = None
    for ss in sig_sharp:
        if ss not in cols:
            continue
        for sh in sig_heavy:
            if sh < ss + min_gap or sh not in cols:
                continue
            coef, rms, r2 = _nnls_two(y, cols[ss], cols[sh])
            if best is None or rms < best['rms']:
                best = _two_record(coef, rms, r2, ss, sh, len(y))
    if best is None:
        # No pair survives: the heavy width is annihilated at this pitch and contributes level only
        # (5.41 1). Fall back to the one component that is still identifiable and say so.
        single = None
        for s, c in cols.items():
            coef, rms, r2 = lstsq_cols(y, [c])
            if single is None or rms < single['rms']:
                single = dict(sigma_sharp=s, sigma_heavy=float('nan'), a=float(coef[0]),
                              t_sharp=float(coef[1]), t_heavy=float('nan'), t=float(coef[1]),
                              share=float('nan'), rms=rms, r2=r2, n=int(len(y)))
        best = single or dict(sigma_sharp=float('nan'), sigma_heavy=float('nan'), a=float(y.mean()),
                              t_sharp=float('nan'), t_heavy=float('nan'), t=float('nan'),
                              share=float('nan'), rms=float(y.std()), r2=0.0, n=int(len(y)))
        best['heavy_unresolved'] = True
    best['sigma_ceiling'] = max(cols) if cols else 0.0
    return best


# ---------------------------------------------------------------- the candidate forms


def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def structure_gpu(P, key, scale, sigma_b_css, sigma_h_css, k):
    """vitrea's GPU body: (1 − k)·G_σb + k·G_σh, both σ in CSS px."""
    return (1 - k) * G(P, key, sigma_b_css, scale) + k * G(P, key, sigma_h_css, scale)


def structure_css(P, key, scale, sigma_b_css, sigma_h_css, k):
    """vitrea's CSS body: one blur whose σ interpolates the two by the same weight."""
    return G(P, key, sigma_b_css * (1 - k) + sigma_h_css * k, scale)


# --- F2: the reference's quarter-device-scale buffer


def downsample(P, factor, filt='box'):
    if filt == 'box':
        H, W = P.shape
        return P.reshape(H // factor, factor, W // factor, factor).mean(axis=(1, 3))
    if filt == 'bilinear':
        H, W = P.shape
        yy = (np.arange(H // factor) + 0.5) * factor - 0.5
        xx = (np.arange(W // factor) + 0.5) * factor - 0.5
        return map_coordinates(P, np.meshgrid(yy, xx, indexing='ij'), order=1, mode='nearest')
    raise ValueError(filt)


def upsample(B, factor, shape):
    """Bilinear back to device resolution; buffer pixel j is centred on device (j + 0.5)·factor − 0.5."""
    H, W = shape
    yy = (np.arange(H) + 0.5) / factor - 0.5
    xx = (np.arange(W) + 0.5) / factor - 0.5
    return map_coordinates(B, np.meshgrid(yy, xx, indexing='ij'), order=1, mode='nearest')


_qcache = {}


def quarter_buffer(P, key, scale, sigma_buffer_px, filt='box'):
    """(U, B): the unblurred quarter-device-scale buffer and the blurred one, both back at device res.

    The buffer is 0.25 of the *device* scale (`CABackdropLayer.scale`, claims 5.50 1), so one buffer
    pixel is 4 device px = 4/scale CSS px at either scale, and a blur of σ buffer px is
    4·σ/scale CSS px.
    """
    ck = (key, scale, round(float(sigma_buffer_px), 4), filt)
    if ck in _qcache:
        return _qcache[ck]
    small = downsample(P, 4, filt)
    U = upsample(small, 4, P.shape)
    Bs = gaussian_filter(small, sigma_buffer_px, mode='nearest') if sigma_buffer_px > 1e-6 else small
    B = upsample(Bs, 4, P.shape)
    _qcache[ck] = (U, B)
    return _qcache[ck]


def ramp_weight(comp, scale, w_edge=0.5, end_frac=0.5, gamma=1.0):
    """Apple's blur opacity ramp in depth: w_edge at the contour rising to 1 at u = end_frac·span."""
    u = depth(comp, scale)
    end = max(end_frac * SPAN[comp], 1e-6)
    x = np.clip(u / end, 0, 1) ** gamma
    return w_edge + (1 - w_edge) * x


def structure_f2(P, key, comp, scale, c, w_edge=0.5, end_frac=0.5, gamma=1.0, filt='box'):
    """The quarter-buffer mechanism: (1 − w)·U + w·B with σ_buffer = c·r(span)."""
    r = blur_radius_buffer_px(SPAN[comp])
    U, B = quarter_buffer(P, key, scale, c * r, filt)
    w = ramp_weight(comp, scale, w_edge, end_frac, gamma)
    return (1 - w) * U + w * B


# ---------------------------------------------------------------- pooled evaluation


def pooled_rms(struct_of, comps, scales, pitches, masks=None):
    """RMS over the given cells with (a, t) free per (comp, scale) — the level laws as nuisance.

    `struct_of(comp, scale, backdrop)` returns the modelled structure on the full canvas.
    Returns (rms, n, per-cell dict).
    """
    sse = 0.0
    n = 0
    per = {}
    for scale in scales:
        for comp in comps:
            m = box_mask(comp, scale) if masks is None else masks[(comp, scale)]
            ys, xs = [], []
            for b in pitches:
                Y = capture(f'{b}__{comp}__rest', scale)
                ys.append(Y[m])
                xs.append(struct_of(comp, scale, b)[m])
            y = np.concatenate(ys)
            x = np.concatenate(xs)
            coef, rms, r2 = lstsq_cols(y, [x])
            sse += float(rms ** 2 * len(y))
            n += len(y)
            cell = dict(a=float(coef[0]), t=float(coef[1]), rms=rms, r2=r2, n=int(len(y)), per_pitch={})
            for b, yy, xx in zip(pitches, ys, xs):
                res = yy - (coef[0] + coef[1] * xx)
                cell['per_pitch'][b] = dict(rms=float(np.sqrt(np.mean(res ** 2))),
                                            std_ref=float(yy.std()),
                                            std_model=float((coef[0] + coef[1] * xx).std()),
                                            bias=float(res.mean()))
            per[f'{comp}@{scale}x'] = cell
    return float(np.sqrt(sse / n)), n, per


def to_jsonable(o):
    if isinstance(o, dict):
        return {k: to_jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return [to_jsonable(v) for v in o.tolist()]
    return o


def write_part(name, obj):
    os.makedirs(f'{OUT}/parts', exist_ok=True)
    with open(f'{OUT}/parts/{name}.json', 'w') as f:
        json.dump(to_jsonable(obj), f, indent=1, sort_keys=True)
    print(f'[wrote] {OUT}/parts/{name}.json')
