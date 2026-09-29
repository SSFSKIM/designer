"""W42 G0 instrument: the local model regression the step, patch, depth and lam readers share.

Each of those readers reads a structure at its own scale (the grounding's reading discipline): it takes the
pixels of one declared population, inverts the output transfer to the M domain, and regresses M on basis
maps of the KNOWN backdrop, as memo C's model reader did (`probe/reader.py fit`, SHA-256 a5d6b1cb...):

    M = a0 + a1 C + a2 s h + a3 W,   h = max(0, s (W - C)),  s = +1 light / -1 dark
    lam = a2 / a1,  w = a3 / (a1 + a3),  gain = a1 + a3

with C a narrow blur and W a wide blur of the backdrop, each built with the forward engine's own operators
(the footprint crop, the 0.8-device-px capture floor, clamp or normalised edges, the rounded-shape support),
so a reader and a forward model can never disagree about what an operator is. Fixing lam, or lam and w,
turns the same regression into the constrained reads the readers expose ("given or free").

Two readings of the output:
- 'native': invert the cell's T (native T per endpoint; memo C's table in the synthetic proofs), weight each
  pixel by T's slope so the residual is in output codes, and drop pixels where T is not trusted;
- 'linear': vitrea's known-kernel control. vitrea's body is affine in LINEAR light and then encoded (memo B
  §1), so M is the decoded linear value (x 255), the affine is absorbed by a0 and the gain, and each pixel is
  weighted by the encode's slope (memo C's `fit_vit` weighting). The basis maps are then blurred in linear
  light and without the capture floor, which vitrea does not have.
Widths are searched on a declared grid and refined by a bounded Nelder-Mead from the grid's best point
(LOCAL, deterministic). A width's resolution is its profile interval: the range over which the weighted rms
stays within +0.10 code of its minimum.
"""
import numpy as np
from scipy import optimize

import forward as F
import geometry as G
from tone import srgb_to_lin

FREE_KEYS = [f'sn_{{pose}}_{int(v)}' for v in F.FREE_SPANS]


def luma_img(y):
    return G.luma(y) if y.ndim == 3 else y


def observed(cell, pix, reading):
    """(M, weight, ok) on the canvas mask `pix` (flattened in np.nonzero order)."""
    y = luma_img(cell.y)[pix]
    ok = np.isfinite(y)
    y0 = np.where(ok, y, 0.0)
    if reading == 'native':
        M = cell.T.inv(y0)
        wt = cell.T.slope(M)
    else:
        M = srgb_to_lin(y0) * 255
        wt = 1 / np.maximum(1e-3, (srgb_to_lin(np.clip(y0 + 0.5, 0, 255))
                                    - srgb_to_lin(np.clip(y0 - 0.5, 0, 255))) * 255)
    return M, wt, ok


def model_ok(cell, reading, ok, C, W):
    """Restrict to pixels where T is measured, decided by the MODEL and not by the observed code. memo C's
    table does not measure dark T above an input of 128-140 at spans >= 96 (tone.TRUST); keeping the pixels
    whose observed code inverts below that limit would keep the knee-side pixels whose noise fell low and
    drop the rest, a censoring that biases lam and the widths. Instead a pixel is kept when its model value
    is below the limit for every lam in [0, 1]: M <= 0.5 (C + W) in dark, M <= max(C, W) in light."""
    lim = getattr(cell.T, 'trust_below', None)
    if reading != 'native' or lim is None:
        return ok
    bound = 0.5 * (C + W) if cell.scheme == 'dark' else np.maximum(C, W)
    return ok & (bound < lim)


class Basis:
    """Basis maps for one cell on the canvas mask `pix`, in the reading's space. Values are x 255 (encoded
    codes, or linear light x 255)."""

    def __init__(self, cell, pix, reading='native'):
        self.cell, self.pix, self.reading = cell, pix, reading
        self.space = 'enc' if reading == 'native' else 'lin'
        self.floor = reading == 'native'
        self.sg = 1 if cell.scheme == 'light' else -1
        # the narrow term's edge mode on R_fp: LT's declared modes in the native reading (it matters only
        # within a blur width of R_fp's edge, where the receded margin of one device px puts the depth
        # reader's shallowest patch); vitrea's chain clamps at the canvas
        self.c_edge = ('clamp' if cell.active else 'norm') if reading == 'native' else 'clamp'
        self._c = {}

    def _src(self, win):
        c = self.cell
        if self.floor:
            X = c.S(win)
        else:
            X = c.B[win[0]:win[1], win[2]:win[3]]
        if X.ndim == 3:
            X = G.luma(X * 255) / 255
        if self.space == 'lin':
            X = srgb_to_lin(255 * X)
        return X, ('rl', win, self.floor, self.space)

    def _at(self, win):
        at = np.zeros((win[1] - win[0], win[3] - win[2]), bool)
        at[:] = self.pix[win[0]:win[1], win[2]:win[3]]
        assert at.sum() == self.pix.sum(), 'the read population must lie inside the computation window'
        return at

    def C(self, sn=None, kn=None):
        """The narrow term: a width flat in depth (sn, pt) or the declared o-law radius scale (kn)."""
        key = ('kn', round(float(kn), 5)) if kn is not None else ('sn', round(float(sn), 5))
        if key not in self._c:
            if len(self._c) > 24:
                self._c.pop(next(iter(self._c)))
            self._c[key] = self._C(sn, kn)
        return self._c[key]

    def _C(self, sn, kn):
        c = self.cell
        win = c.crop('box')
        X, key = self._src(win)
        at = self._at(win)
        if kn is not None:
            fam, p = F.Family(), {'k_n': kn}
        else:
            fam = F.Family(narrow='free')
            p = {k.format(pose=c.pose): sn for k in FREE_KEYS}
        return 255 * F.narrow_map(c, fam, p, X, key, win, self.c_edge, at)

    def W(self, sw, support='box', edge='clamp', mu=None, s2=None, a=0.0):
        """The wide term (pt) on a support: 'canvas' (clamp at the canvas), 'box' (R_fp, clamp or norm) or
        'shape' (the rounded shape grown by mu pt, normalised); optional second Gaussian (s2, weight a)."""
        c = self.cell
        win = c.crop(support, mu if support == 'shape' else None)
        X, key = self._src(win)
        at = self._at(win)
        weight, mode = None, edge
        if support == 'shape':
            wk = ('rl-shape-weight', win, round(mu, 4))
            if wk not in c._cache:
                c._cache[wk] = (c.d[win[0]:win[1], win[2]:win[3]] <= mu).astype(float)
            weight, mode = c._cache[wk], 'norm'
        Wv = c.blur(key, X, sw * c.scale, mode, weight)[at]
        if a:
            Wv = (1 - a) * Wv + a * c.blur(key, X, s2 * c.scale, mode, weight)[at]
        return 255 * Wv


def regress(parts, lam=None, w=None, predict=False):
    """Weighted least squares over the concatenated parts [(M, wt, ok, C, W, sg)] with shared coefficients.
    lam None: free (a0, a1, a2, a3); lam given, w None: (a0, a1, a3); both given: (a0, gain).
    predict=True adds 'pred': per part, the predicted M on that part's ok rows."""
    rows, ys, ws = [], [], []
    for M, wt, ok, C, W, sg in parts:
        h = np.maximum(0, sg * (W - C))[ok]
        C_, W_ = C[ok], W[ok]
        one = np.ones_like(C_)
        if lam is None:
            A = np.stack([one, C_, sg * h, W_], 1)
        elif w is None:
            A = np.stack([one, C_ + sg * lam * h, W_], 1)
        else:
            A = np.stack([one, (1 - w) * (C_ + sg * lam * h) + w * W_], 1)
        rows.append(A)
        ys.append(M[ok])
        ws.append(wt[ok])
    A, y, wt = np.concatenate(rows), np.concatenate(ys), np.concatenate(ws)
    cf, *_ = np.linalg.lstsq(A * wt[:, None], y * wt, rcond=None)
    r = (y - A @ cf) * wt
    out = dict(rms=float(np.sqrt(np.mean(r ** 2))), n=int(y.size))
    if predict:
        pr, i = [], 0
        for A_ in rows:
            pr.append(A_ @ cf)
        out['pred'] = pr
    if lam is None:
        a0, a1, a2, a3 = cf
        out.update(lam=float(a2 / a1) if a1 else np.nan, w=float(a3 / (a1 + a3)) if a1 + a3 else np.nan,
                   gain=float(a1 + a3), a0=float(a0))
    elif w is None:
        a0, a1, a3 = cf
        out.update(lam=float(lam), w=float(a3 / (a1 + a3)) if a1 + a3 else np.nan, gain=float(a1 + a3),
                   a0=float(a0))
    else:
        out.update(lam=float(lam), w=float(w), gain=float(cf[1]), a0=float(cf[0]))
    return out


def to_output(cell, M, reading):
    """Predicted output codes from M in the reading's domain."""
    from tone import lin_to_srgb
    return cell.T(M) if reading == 'native' else lin_to_srgb(M / 255.0)


def search(objective, grid, bounds):
    """Grid then bounded Nelder-Mead from the grid's best point; returns (x, value, grid table)."""
    tab = [(tuple(x), objective(np.array(x, float))) for x in grid]
    x0, v0 = min(tab, key=lambda r: r[1])
    lo, hi = np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds])
    f = lambda x: objective(np.clip(x, lo, hi)) + 1e3 * float(np.sum(np.abs(x - np.clip(x, lo, hi))))
    if len(x0) == 1:
        r = optimize.minimize_scalar(lambda v: f(np.array([v])), bracket=None,
                                     bounds=(max(lo[0], x0[0] * 0.7 - 0.05), min(hi[0], x0[0] * 1.3 + 0.05)),
                                     method='bounded', options=dict(xatol=2e-3))
        x, v = np.array([r.x]), r.fun
    else:
        simplex = [np.array(x0, float)]
        for i in range(len(x0)):
            e = np.array(x0, float)
            e[i] = e[i] * 1.08 + 0.05
            simplex.append(e)
        r = optimize.minimize(f, np.array(x0, float), method='Nelder-Mead',
                              options=dict(initial_simplex=np.array(simplex), xatol=2e-3, fatol=1e-5,
                                           maxiter=200))
        x, v = np.clip(r.x, lo, hi), r.fun
    if v0 < v:
        x, v = np.array(x0, float), v0
    return x, float(v), tab


def profile_interval(objective, x, i, tol=0.10, rel=(0.6, 1.6), n=33):
    """Range of parameter i over which objective stays within +tol of objective(x), others held."""
    base = objective(x)
    lo, hi = x[i] * rel[0] - 0.05, x[i] * rel[1] + 0.05
    ok = []
    for v in np.linspace(max(0.0, lo), hi, n):
        xx = np.array(x, float)
        xx[i] = v
        if objective(xx) <= base + tol:
            ok.append(float(v))
    return (min(ok), max(ok)) if ok else (np.nan, np.nan)
