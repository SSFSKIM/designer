"""W42 G0 instrument: memo B's edge-spread reader, generalised to any two-level checker (charter Design, "The
instrument": the ESF reader; memo B §1 and §2b; `~/vitrea-w42/grounding/kernel/esf.py`, SHA-256 582b7699…).

The declared statistic. Every checker edge inside the deep interior (all samples at least `margin` pt inside
the shape) is sampled along the mid-line of the cell row (for a vertical edge) or column (for a horizontal
edge) over +-half pt, half = min(8, pitch / 2). The profiles are oriented so that t > 0 is the brighter side
and averaged. The side the one-sided knee leaves LINEAR is the ramp side: the brighter side in the light
scheme (there C exceeds W and the hinge is off), the darker side in the dark scheme. A Gaussian width sigma
is fitted to the ramp side only, with an affine output (a + b u), against the exact 2-D model
u = G_sigma * B sampled on the same pixels, B the raw backdrop. Returns sigma (CSS px) and its interval
(the scan's range within +0.1 code of the minimum, memo B's), plus the edge count.

What it reads is the EFFECTIVE narrow width at the edges' depths: under LT the narrow blur composed with the
capture's floor, sqrt(sigma_n^2 + F^2) with F = 0.4 f device px, since Gaussians compose in quadrature.
Only the side the knee leaves linear carries it; the other side is flattened toward W, which is how memo B
first saw the knee (vitrea's two halves read alike). W itself varies slowly across the +-half window and
enters the affine fit as a small bias, which proof 1 measures.
"""
import numpy as np
from scipy import ndimage, optimize

import geometry as G
import read_model as RM
from tone import srgb_to_lin, lin_to_srgb

# sigma is IDENTIFIED on a cell when its +0.1-code interval spans at most this fraction of sigma (+-5 %):
# a ramp that half a cell cannot resolve (a receded width near the pitch) gives only a bound, as memo B found.
IDENT_REL = 0.10
SIG_DEV = [0.2, 0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0,
           14.0, 16.0, 20.0, 24.0]


def _transitions(v):
    return np.nonzero(v[1:] != v[:-1])[0] + 1


def edges(cell, margin_pt=14.0, half_pt=None):
    """Sample sets [(ys, xs)] (device px, oriented bright to t > 0) and the offsets t (device px)."""
    B = cell.B if cell.B.ndim == 2 else G.luma(cell.B * 255) / 255
    bright = B > 0.5 * (B.min() + B.max())
    pitch = cell.bg_spec['cell']
    half = min(8.0, pitch / 2.0) if half_pt is None else half_pt
    s = cell.scale
    t = np.arange(-int(round(half * s)), int(round(half * s)))
    H, W = B.shape
    y = RM.luma_y(cell)
    ok = (cell.d < -margin_pt) & np.isfinite(y)
    xe = _transitions(bright[H // 2, :])            # column index of the first pixel after each x edge
    ye = _transitions(bright[:, W // 2])
    xm = (xe[:-1] + xe[1:]) // 2                     # mid-cell columns and rows (full cells only)
    ym = (ye[:-1] + ye[1:]) // 2
    out = []
    for x in xe:
        for r in ym:
            xs = x + t
            if xs.min() < 0 or xs.max() >= W:
                continue
            ys = np.full_like(xs, r)
            if ok[ys, xs].all():
                out.append((ys, xs) if bright[r, xs[-1]] else (ys, xs[::-1]))
    for yy in ye:
        for c in xm:
            ys = yy + t
            if ys.min() < 0 or ys.max() >= H:
                continue
            xs = np.full_like(ys, c)
            if ok[ys, xs].all():
                out.append((ys, xs) if bright[ys[-1], c] else (ys[::-1], xs))
    return out, t, B


def profile(img, E):
    return np.mean([img[ys, xs] for ys, xs in E], 0)


def fit_side(yp, up, t, side, uw=None):
    sel = t >= 0 if side > 0 else t < 0
    A = np.stack([np.ones(sel.sum()), up[sel]] + ([] if uw is None else [uw[sel]]), 1)
    c, *_ = np.linalg.lstsq(A, yp[sel], rcond=None)
    r = yp[sel] - A @ c
    return c, float(np.sqrt(np.mean(r ** 2)))


def read(cell, margin_pt=14.0, half_pt=None, sigmas=SIG_DEV, side=None, Tkind='output', space='enc'):
    """sigma (CSS px) on the ramp side; side +1 fits the bright side, -1 the dark side (default: the side the
    scheme's knee leaves linear).

    Tkind 'output' is memo B's reader verbatim (affine in output codes, for a T nobody has measured);
    'native' inverts through cell.T first and 'srgb' reads linear light (vitrea), so a curved T cannot bend
    the ramp (memo C's dark T is strongly curved: the output reading misses dark rrect-ml by +30 % where
    the inverted one reads +3 %). A W term as a nuisance regressor was tried and rejected: over half a cell
    it is nearly collinear with the ramp and moved sigma by up to 70 %."""
    E, t, B = edges(cell, margin_pt, half_pt)
    if len(E) < 2:
        return None
    y = RM.luma_y(cell)
    if Tkind == 'native':
        # every sample is inverted: only the ramp side enters the fit, and selecting edges by the observed
        # code would censor on the dependent variable (a clamped knee-side sample inverts to the clamp)
        y = np.where(np.isfinite(y), cell.T.inv(np.nan_to_num(y)), np.nan)
    elif Tkind == 'srgb':
        y = srgb_to_lin(np.nan_to_num(y)) * 255
    yp = profile(y, E)
    ramp = side if side is not None else (1 if cell.scheme == 'light' else -1)
    uw = None
    src = B if space == 'enc' else srgb_to_lin(255 * B)

    def rms_at(sg):
        up = profile(ndimage.gaussian_filter(src, sg, mode='nearest', truncate=5), E)
        cf, r = fit_side(yp, up, t, ramp, uw)
        if Tkind == 'native':   # residual back in output codes through the local slope of T
            r = r * float(np.median(cell.T.slope(yp)))
        elif Tkind == 'srgb':   # and through the sRGB encode's local slope
            v = np.clip(yp / 255, 1e-4, 1)
            r = r * float(np.median((lin_to_srgb(v + 1e-4) - lin_to_srgb(v)) / (255e-4)))
        return cf, r
    rows = [(sg, rms_at(sg)[1]) for sg in sigmas]
    i = int(np.argmin([r[1] for r in rows]))
    lo, hi = sigmas[max(0, i - 1)], sigmas[min(len(sigmas) - 1, i + 1)]
    res = optimize.minimize_scalar(lambda v: rms_at(v)[1], bounds=(lo, hi), method='bounded',
                                   options=dict(xatol=1e-3))
    sg, (cf, rms) = float(res.x), rms_at(float(res.x))
    # the interval: a fine scan about the optimum, the range within +0.1 code of it (memo B's criterion)
    fine = np.unique(np.concatenate([np.linspace(0.5 * sg, 1.5 * sg, 41), sigmas]))
    ok = [v for v in fine if rms_at(v)[1] <= rms + 0.1]
    iv = (min(ok) / cell.scale, max(ok) / cell.scale)
    return dict(sigma=sg / cell.scale, sigma_dev=sg, rms=rms, iv=iv,
                identified=bool(iv[1] - iv[0] <= IDENT_REL * sg / cell.scale),
                n_edges=len(E), a=float(cf[0]), b=float(cf[1]), side=ramp,
                edge_depth_pt=[float(-cell.d[ys[len(ys) // 2], xs[len(xs) // 2]]) for ys, xs in E])
