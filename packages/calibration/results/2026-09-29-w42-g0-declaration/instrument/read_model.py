"""W42 G0 instrument: memo C's model reader, generalised to any declared cell (charter Design, "The instrument
(G0)": memo C's model reader; memo C §1; `~/vitrea-w42/grounding/probe/reader.py` `fit`/`grid` and
`fullfit.py`, SHA-256 a5d6b1cb… for reader.py).

The declared statistic. On one cell's deep mask the body is read as the two-scale one-sided algebra

    C = G(sn) * B',  W = K_w(sw) * B',  h = max(0, sg (W - C))   (sg = +1 light, -1 dark)
    M = (1 - w) C + sg (1 - w) lam h + w W,   y = T(255 M)

with B' the backdrop in the mixing space (encoded, or linear light), optionally pre-blurred by the capture's
0.8-device-px floor (0.4 f device px), and W on one of five supports:
- 'Rfp': LT's declared footprint and edge mode for both C and W (the shape's box plus the declared margin;
  clamp-to-edge when active, normalised when receded);
- 'canvas': C and W Gaussian on the whole canvas, clamp at its edge (memo C's 'gauss');
- 'shape' / 'box': W normalised over the rounded shape or its bounding box, C on the canvas (memo C's 'foot'
  and 'boxfoot');
- 'group': W the shape's mean.

It returns (sn, sw, lam, w, gain) in CSS px and the fit's rms in output codes, by two stages:
1. memo C's M-domain regression on a (sn, sw) grid: invert y through T (native T, on the pixels the MODEL
   places below T's trust limit, `model_trusted`; memo C selected by the observed code, which biases), or
   the sRGB-affine linear reading for vitrea), regress M = a0 + a1 C + a2 sg h + a3 W with slope weights so
   the residual is in output codes; w = a3 / (a1 + a3), lam = a2 / a1, gain = a1 + a3.
2. fullfit's continuous least squares in output codes over (sn, sw, lam, w) with T pinned, from the grid's
   best, each width's interval the range where the rms stays within +0.10 code of its minimum.

The regression reads lam and w without assuming either; the continuous fit then pins widths to the grid's
resolution and below. On a depth-graded active cell (t > 0) the single sn it returns is an effective width,
which is why clause 2's gate for this reader is on cells whose narrow width is flat in depth.
"""
import numpy as np
from scipy import ndimage, optimize

import geometry as G
from tone import srgb_to_lin, lin_to_srgb

KINDS = ('Rfp', 'canvas', 'shape', 'box', 'group')
SN = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0, 10.0]
SW = [4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 40]
TRUNC = 4.0
MIN_PX = 200


# ---------------------------------------------------------------- the reader's blurred maps

def _cache(cell):
    if not hasattr(cell, '_rm'):
        cell._rm = {}
    return cell._rm


def luma_y(cell):
    y = cell.y
    return G.luma(y) if y.ndim == 3 else y


def eval_mask(cell, trust=False):
    """Deep mask and finite observations. With trust=True, also memo C's selection by the OBSERVED code's
    inversion (kept for comparison only: it censors on the dependent variable, keeping a dark knee-side pixel
    only when its noise fell low, and biased lam to its bound on dark spans >= 96; fork B found it)."""
    y = luma_y(cell)
    m = cell.mask & np.isfinite(y)
    if trust and getattr(cell.T, 'trust_below', None) is not None:
        yy = np.where(np.isfinite(y), y, 0)
        m &= cell.T.trusted(yy)
    return m


def model_trusted(cell, C, W, space, Tkind):
    """Where T is measured, decided by the MODEL: a pixel is kept when its model input is below T's trust
    limit for EVERY lam in [0, 1] and w in [0, 1], i.e. 255 max(C, W) < limit (the knee and the normal mix
    keep M between C and W's larger value). Everything is kept when T has no limit or the reading is not
    through native T."""
    lim = getattr(cell.T, 'trust_below', None)
    if Tkind != 'native' or lim is None or space != 'enc':
        return np.ones(C.shape, bool)
    return 255 * np.maximum(C, W) < lim


def source(cell, space, floor):
    """The backdrop on the whole canvas in the mixing space, optionally floored (0.4 f device px, clamp)."""
    key = ('src', space, floor)
    c = _cache(cell)
    if key not in c:
        B = cell.B if cell.B.ndim == 2 else G.luma(cell.B * 255) / 255
        if floor:
            B = ndimage.gaussian_filter(B, 0.4 * cell.f, mode='nearest', truncate=TRUNC)
        c[key] = B if space == 'enc' else srgb_to_lin(255 * B)
    return c[key]


def _gauss(X, sig_dev, mode, weight=None):
    if sig_dev < 1e-3:
        return X.copy()
    if mode == 'clamp':
        return ndimage.gaussian_filter(X, sig_dev, mode='nearest', truncate=TRUNC)
    wt = np.ones_like(X) if weight is None else weight
    num = ndimage.gaussian_filter(X * wt, sig_dev, mode='constant', truncate=TRUNC)
    den = ndimage.gaussian_filter(wt, sig_dev, mode='constant', truncate=TRUNC)
    return np.where(den > 1e-9, num / np.maximum(den, 1e-12), X)


def blurred(cell, sig_pt, kind, space, floor, role):
    """A blur of the source (canvas-size image) for a support kind; role 'C' or 'W'."""
    key = ('b', round(float(sig_pt), 4), kind, space, floor, role)
    c = _cache(cell)
    if key in c:
        return c[key]
    X = source(cell, space, floor)
    sd = sig_pt * cell.scale
    H, W = X.shape
    out = np.full((H, W), np.nan)
    if kind == 'Rfp':
        y0, y1, x0, x1 = cell.crop('box')
        mode = 'clamp' if cell.active else 'norm'
        out[y0:y1, x0:x1] = _gauss(X[y0:y1, x0:x1], sd, mode)
    elif kind == 'canvas' or role == 'C':
        out = _gauss(X, sd, 'clamp')
    elif kind in ('shape', 'box'):
        y0, y1, x0, x1 = cell.box_px
        sup = (cell.d[y0:y1, x0:x1] <= 0).astype(float) if kind == 'shape' else np.ones((y1 - y0, x1 - x0))
        out[y0:y1, x0:x1] = _gauss(X[y0:y1, x0:x1], sd, 'norm', sup)
    elif kind == 'group':
        out = np.full((H, W), X[cell.d <= 0].mean())
    else:
        raise ValueError(kind)
    if len(c) > 120:
        for k in [k for k in c if k[0] == 'b'][:40]:
            del c[k]
    c[key] = out
    return out


def maps(cell, sn, sw, kind='Rfp', space='enc', floor=True, m=None):
    m = eval_mask(cell) if m is None else m
    C = blurred(cell, sn, kind, space, floor, 'C')[m]
    W = blurred(cell, sw, kind, space, floor, 'W')[m]
    return C, W


# ---------------------------------------------------------------- the M domain

def m_domain(cell, Tkind, m):
    """(Mo, wt): the observation inverted to the mixing domain and the slope weight that turns an M residual
    into output codes. native: y = T(255 M); srgb: y = enc(a + b M_lin) (Mo in linear light x 255);
    enc-affine: y = a + b 255 M (the encoded reading of an unknown affine output, the known-space control)."""
    y = luma_y(cell)[m]
    if Tkind == 'native':
        Mo = cell.T.inv(y)
        return Mo, cell.T.slope(Mo), y
    if Tkind == 'srgb':
        Mo = srgb_to_lin(y) * 255
        d = (srgb_to_lin(np.clip(y + 0.5, 0, 255)) - srgb_to_lin(np.clip(y - 0.5, 0, 255))) * 255
        return Mo, 1 / np.maximum(1e-3, d), y
    if Tkind == 'enc-affine':
        return y.copy(), np.ones_like(y), y
    raise ValueError(Tkind)


def regress(cell, sn, sw, kind='Rfp', space='enc', floor=True, Tkind='native', m=None):
    m = eval_mask(cell) if m is None else m
    C, W = maps(cell, sn, sw, kind, space, floor, m)
    Mo, wt, y = m_domain(cell, Tkind, m)
    keep = model_trusted(cell, C, W, space, Tkind)
    if keep.sum() < 50:
        return dict(sn=sn, sw=sw, a0=np.nan, a1=np.nan, a2=np.nan, a3=np.nan, gain=np.nan, w=np.nan, lam=np.nan,
                    rms=np.inf, n=int(keep.sum()))
    C, W, Mo, wt, y = C[keep], W[keep], Mo[keep], wt[keep], y[keep]
    sg = 1 if cell.scheme == 'light' else -1
    h = np.maximum(0, sg * (W - C))
    A = np.stack([np.ones_like(C) / 255, C, sg * h, W], 1) * 255
    cf, *_ = np.linalg.lstsq(A * wt[:, None], Mo * wt, rcond=None)
    a0, a1, a2, a3 = cf
    Mp = A @ cf
    if Tkind == 'native':
        r = cell.T(Mp) - y
    elif Tkind == 'srgb':
        r = lin_to_srgb(np.clip(Mp / 255, 0, 1)) - y
    else:
        r = Mp - y
    return dict(sn=sn, sw=sw, a0=a0, a1=a1, a2=a2, a3=a3, gain=a1 + a3,
                w=a3 / (a1 + a3) if a1 + a3 else np.nan, lam=a2 / a1 if a1 else np.nan,
                rms=float(np.sqrt(np.mean(r ** 2))), n=int(keep.sum()))


def grid(cell, sns=SN, sws=SW, **kw):
    tab, best = {}, None
    m = eval_mask(cell)
    for sw in sws:
        for sn in sns:
            if sn >= sw:
                continue
            r = regress(cell, sn, sw, m=m, **kw)
            tab[(sn, sw)] = r['rms']
            if best is None or r['rms'] < best['rms']:
                best = r
    return best, tab


def predict(cell, p, kind='Rfp', space='enc', floor=True, m=None):
    """M (0..1 in the mixing space) on the pixels m for p = (sn, sw, lam, w)."""
    sn, sw, lam, w = p
    C, W = maps(cell, sn, sw, kind, space, floor, m)
    sg = 1 if cell.scheme == 'light' else -1
    return (1 - w) * C + sg * (1 - w) * lam * np.maximum(0, sg * (W - C)) + w * W


def residual(cell, p, kind, space, floor, Tkind, m, keep=None):
    M = predict(cell, p, kind, space, floor, m)
    y = luma_y(cell)[m]
    if keep is not None:
        M, y = M[keep], y[keep]
    if Tkind == 'native':
        return cell.T(255 * M) - y
    if Tkind == 'srgb':  # affine in linear light projected out (memo C's fit_vit)
        Ml = M if space == 'lin' else srgb_to_lin(255 * M)
        X = np.stack([np.ones_like(Ml), Ml], 1)
        cf, *_ = np.linalg.lstsq(X, srgb_to_lin(y), rcond=None)
        return lin_to_srgb(np.clip(X @ cf, 0, 1)) - y
    X = np.stack([np.ones_like(M), 255 * M], 1)   # enc-affine
    cf, *_ = np.linalg.lstsq(X, y, rcond=None)
    return X @ cf - y


LO = {'sn': 0.0, 'sw': 3.0, 'lam': -0.5, 'w': 0.0}
HI = {'sn': 14.0, 'sw': 60.0, 'lam': 1.6, 'w': 1.0}
NAMES = ('sn', 'sw', 'lam', 'w')
MIN_GAP = 0.25


def fit(cell, x0, kind='Rfp', space='enc', floor=True, Tkind='native', fix=None, m=None):
    """Continuous least squares in output codes (fullfit.py); fix pins any of sn, sw, lam, w."""
    m = eval_mask(cell) if m is None else m
    fix = fix or {}
    free = [n for n in NAMES if n not in fix]
    # the model-trusted selection is fixed at the start point so the objective stays continuous
    d0 = dict(zip(NAMES, x0))
    d0.update(fix)
    keep = model_trusted(cell, *maps(cell, d0['sn'], d0['sw'], kind, space, floor, m), space, Tkind)

    # the wide width is searched as its excess over the narrow one (sw = sn + dsw, dsw >= MIN_GAP), so the
    # continuous fit cannot swap the two terms' roles: with lam ~ 0 the algebra is symmetric under
    # (C, W, w) -> (W, C, 1 - w), and an unordered search wandered to sn > sw on vitrea's captures
    both = 'sn' in free and 'sw' in free
    lo = {**LO, 'sw': MIN_GAP if both else LO['sw']}
    hi = {**HI, 'sw': HI['sw'] if not both else HI['sw']}

    def full(x):
        d = dict(fix)
        d.update(zip(free, x))
        if both:
            d['sw'] = d['sn'] + d['sw']
        return [d[n] for n in NAMES]
    x0d = dict(zip(NAMES, x0))
    if both:
        x0d['sw'] = max(x0d['sw'] - x0d['sn'], MIN_GAP)
    x0f = np.clip([x0d[n] for n in free], [lo[n] for n in free], [hi[n] for n in free])
    r = optimize.least_squares(lambda x: residual(cell, full(x), kind, space, floor, Tkind, m, keep), x0f,
                               bounds=([lo[n] for n in free], [hi[n] for n in free]),
                               diff_step=1e-3, x_scale='jac', max_nfev=300, xtol=1e-8, ftol=1e-10)
    p = full(r.x)
    return dict(zip(NAMES, p), rms=float(np.sqrt(np.mean(r.fun ** 2))), n=int(keep.sum()),
                kind=kind, space=space, floor=floor, Tkind=Tkind)


def profile_interval(cell, p, name, kind, space, floor, Tkind, tol=0.10, rel=0.5, n=25):
    """Range of one width over which the rms stays within +tol codes of the fit's, the rest refitted except
    the widths (lam and w free): the reader's resolution on that width."""
    m = eval_mask(cell)
    i = NAMES.index(name)
    v0 = p[i]
    keep = model_trusted(cell, *maps(cell, p[0], p[1], kind, space, floor, m), space, Tkind)
    base = np.sqrt(np.mean(residual(cell, p, kind, space, floor, Tkind, m, keep) ** 2))
    lo_v, hi_v = max(LO[name], v0 * (1 - rel)), v0 * (1 + rel) + (0.5 if v0 < 0.5 else 0)
    ok = []
    for v in np.linspace(lo_v, hi_v, n):
        q = list(p)
        q[i] = v
        other = 'sw' if name == 'sn' else 'sn'
        fx = {name: v, other: q[NAMES.index(other)]}
        f = fit(cell, q, kind, space, floor, Tkind, fix=fx, m=m)
        if f['rms'] <= base + tol:
            ok.append(v)
    return (min(ok), max(ok)) if ok else (np.nan, np.nan)


def read(cell, kind='Rfp', space='enc', floor=True, Tkind='native', sns=SN, sws=SW, intervals=False):
    """The declared statistic: grid regression, then the continuous fit from its best. A cell with fewer than
    MIN_PX readable pixels (T's trust limit removes a dark knee side at spans >= 96) returns None."""
    if eval_mask(cell).sum() < MIN_PX:
        return None
    g, _ = grid(cell, sns, sws, kind=kind, space=space, floor=floor, Tkind=Tkind)
    if not np.isfinite(g['rms']):
        return None
    lam0 = g['lam'] if np.isfinite(g['lam']) else 0.5
    w0 = g['w'] if np.isfinite(g['w']) else 0.5
    x0 = (g['sn'], g['sw'], float(np.clip(lam0, -0.4, 1.5)), float(np.clip(w0, 0.02, 0.98)))
    f = fit(cell, x0, kind, space, floor, Tkind)
    f['grid'] = {k: g[k] for k in ('sn', 'sw', 'lam', 'w', 'gain', 'rms')}
    if intervals:
        p = [f[n] for n in NAMES]
        f['sn_iv'] = profile_interval(cell, p, 'sn', kind, space, floor, Tkind)
        f['sw_iv'] = profile_interval(cell, p, 'sw', kind, space, floor, Tkind)
    return f
