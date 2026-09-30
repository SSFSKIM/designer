"""W42 G0 instrument: memo B's impulse reader, generalised to any square set drawn in the backdrop (charter
Design, "The instrument": the impulse reader; memo B §1 and §2a; `~/vitrea-w42/grounding/kernel/
impulse_fit.py`, SHA-256 6fd89384…).

The declared statistic. The backdrop's foreground squares (the canonical impulse lattice, the bed's single
patches) are labelled from the raster itself, so the model knows the exact square geometry at the capture's
pixel grid. On a window of deep-interior pixels (at least `margin` pt inside the shape, within R pt of a
square's centre) the observation is fitted by

    y = y0 + b (K * B)(x),   K = Gaussian(sigma)  or  (1 - k) Gaussian(s1) + k Gaussian(s2)

with (K * B) evaluated exactly for axis-aligned squares (erf products), a common sub-pixel shift (dx, dy)
and an affine output. It returns the single width, the two-Gaussian widths and the wide share k, each fit's
rms and max, in CSS px.

The output is affine in codes (memo B's, Tkind 'output'), or first inverted through the known T ('native')
or into linear light ('srgb', vitrea). memo B's own limits carry: a component whose impulse peak is below
about one code is invisible, which at 2x hides any width above about 10 CSS px, so the share is a reading
only where the wide component's peak is resolved; and under a one-sided knee the tails on the knee side are
flattened toward W, so on Apple the single width is the narrow term's CORE, not a mixture.
"""
import numpy as np
from scipy import ndimage, optimize
from scipy.special import erf

import geometry as G
import read_model as RM
from tone import srgb_to_lin


def squares(cell):
    """[(y0, y1, x0, x1)] device-px extents of the foreground squares, and their centres (pt)."""
    spec = cell.bg_spec
    B = cell.B if cell.B.ndim == 2 else G.luma(cell.B * 255) / 255
    fg = float(np.array(spec['foreground'], float) @ G.W709) / 255
    bgv = float(np.array(spec['background'], float) @ G.W709) / 255
    is_fg = np.abs(B - fg) < np.abs(B - bgv)
    lab, n = ndimage.label(is_fg)
    sq = [(sl[0].start, sl[0].stop, sl[1].start, sl[1].stop) for sl in ndimage.find_objects(lab)]
    return sq, fg, bgv


def gauss_box(ys, xs, sq, sig):
    """Sum over squares of the Gaussian-blurred unit square at points (ys, xs), device px. Separable: each
    square's erf factors are evaluated once per distinct row and column, then multiplied per point."""
    k = np.sqrt(2) * sig
    uy, iy = np.unique(ys, return_inverse=True)
    ux, ix = np.unique(xs, return_inverse=True)
    r = 0.0
    for (y0, y1, x0, x1) in sq:
        fy = 0.5 * (erf((y1 - uy) / k) - erf((y0 - uy) / k))
        fx = 0.5 * (erf((x1 - ux) / k) - erf((x0 - ux) / k))
        r = r + fy[iy] * fx[ix]
    return r


def window(cell, sq, margin_pt, R_pt):
    s = cell.scale
    H, W = cell.d.shape
    yy, xx = np.mgrid[0:H, 0:W]
    near = np.zeros((H, W), bool)
    keep = []
    for (y0, y1, x0, x1) in sq:
        cy, cx = (y0 + y1) / 2, (x0 + x1) / 2
        disc = np.hypot(yy + 0.5 - cy, xx + 0.5 - cx) < R_pt * s
        near |= disc
        keep.append((y0, y1, x0, x1))
    y = RM.luma_y(cell)
    return (cell.d < -margin_pt) & near & np.isfinite(y)


def fit(cell, kind='gauss', margin_pt=16.0, R_pt=40.0, Tkind='output', p0=None):
    sq, fg, bgv = squares(cell)
    m = window(cell, sq, margin_pt, R_pt)
    if m.sum() < 50:
        return None
    lim = getattr(cell.T, 'trust_below', None)
    if Tkind == 'native' and lim is not None:
        # model-based trust at nominal widths (a 2-pt narrow and a 16-pt wide blur of the backdrop): a pixel
        # is kept when 255 max(C, W) is below T's limit, never by its observed code (censoring)
        B = cell.B if cell.B.ndim == 2 else G.luma(cell.B * 255) / 255
        bound = np.maximum(ndimage.gaussian_filter(B, 2 * cell.scale, mode='nearest'),
                           ndimage.gaussian_filter(B, 16 * cell.scale, mode='nearest'))
        m = m & (255 * bound < lim)
        if m.sum() < 50:
            return None
    ys, xs = np.nonzero(m)
    yc, xc = ys + 0.5, xs + 0.5
    yv = RM.luma_y(cell)[m]
    if Tkind == 'native':
        yv = cell.T.inv(yv)
    elif Tkind == 'srgb':
        yv = srgb_to_lin(yv) * 255
    # only squares whose blur can reach the window matter; keep those within R + 40 pt of it
    s = cell.scale
    sq = [q for q in sq if np.hypot(ys - (q[0] + q[1]) / 2, xs - (q[2] + q[3]) / 2).min() < (R_pt + 40) * s]
    sgn = 1 if fg > bgv else -1

    def design(p):
        if kind == 'gauss':
            u = gauss_box(yc - p[1], xc - p[2], sq, p[0])
        else:
            u = (1 - p[2]) * gauss_box(yc - p[3], xc - p[4], sq, p[0]) + p[2] * gauss_box(yc - p[3], xc - p[4], sq, p[1])
        return np.stack([np.ones_like(u), sgn * u], 1)

    def f(p):
        if kind == 'gauss' and p[0] <= 0.05:
            return 1e9
        if kind == 'mix' and (min(p[0], p[1]) <= 0.05 or not (0 <= p[2] <= 1) or p[1] < p[0]):
            return 1e9
        A = design(p)
        c, *_ = np.linalg.lstsq(A, yv, rcond=None)
        return float(np.mean((yv - A @ c) ** 2))
    if kind == 'gauss':
        starts = [p0 or [2.0 * s, 0.0, 0.0]]
        starts += [[st[0] * 3, 0.0, 0.0] for st in starts]
    else:
        g = p0 or [1.0 * s, 6.0 * s, 0.5, 0.0, 0.0]
        starts = [g, [g[0], g[1] * 2, 0.3, 0, 0], [g[0] * 2, g[1] * 3, 0.7, 0, 0]]
    best = None
    for st in starts:
        r = optimize.minimize(f, st, method='Nelder-Mead', options=dict(xatol=1e-4, fatol=1e-9, maxiter=3000))
        if best is None or r.fun < best.fun:
            best = r
    A = design(best.x)
    c, *_ = np.linalg.lstsq(A, yv, rcond=None)
    res = yv - A @ c
    if Tkind == 'native':
        res = res * cell.T.slope(yv)
    p = best.x
    out = dict(kind=kind, npx=int(m.sum()), n_squares=len(sq), y0=float(c[0]), b=float(c[1]),
               rms=float(np.sqrt(np.mean(res ** 2))), max=float(np.abs(res).max()))
    if kind == 'gauss':
        out.update(sigma=float(p[0] / s), shift=(float(p[1] / s), float(p[2] / s)))
    else:
        out.update(s1=float(p[0] / s), s2=float(p[1] / s), k=float(p[2]), shift=(float(p[3] / s), float(p[4] / s)))
    return out


def read(cell, margin_pt=16.0, R_pt=40.0, Tkind='output', mix=True):
    g = fit(cell, 'gauss', margin_pt, R_pt, Tkind)
    if g is None:
        return None
    out = dict(single=g)
    if mix:
        s = cell.scale
        out['mix'] = fit(cell, 'mix', margin_pt, R_pt, Tkind, p0=[g['sigma'] * s, max(6.0, 3 * g['sigma']) * s,
                                                                  0.5, 0.0, 0.0])
    return out
