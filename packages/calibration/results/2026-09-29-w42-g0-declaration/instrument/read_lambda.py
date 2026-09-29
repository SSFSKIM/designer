"""W42 G0 instrument: memo E's per-cell lam reader and hinge-gap reader, for U1 (charter Design, "The instrument";
memo E §3a, §3c; the references are `~/vitrea-w42/grounding/refit/lam_iv.py` and `lam_gap.py`, hashed in
HASHES).

U1 is the receded one-sided weight drifting with pitch inside one shape (memo E: lam 0.68 at pitch 64 against
0.92-0.94 at pitch 16 on the W34 capsule). Two readers localise it:

- the PER-CELL lam reader: with the endpoint's scale(s) held at a pooled fit and w = 0.5, lam alone is read
  per cell by the forward engine through T, on a grid then refined, with its INTERVAL, the lam range over
  which the cell's rms stays within +INTERVAL_TOL code of its minimum (a wide interval means the cell does
  not identify lam), and the rms at the dump's 0.9 beside it;
- the HINGE-GAP reader: on the knee side (W > C light, W < C dark), lam is read per bin of the hinge gap
  |W - C| (encoded 0..1, GAP_BINS) at the same held scales. A lam that falls with the gap would read as a
  compressive hinge; one that is flat within a cell but differs between cells points at W's reference
  (its reach or support), which is where memo E put the drift.

Both run in the native reading through the engine (LT's maps). The LINEAR reading, for vitrea's known-kernel
control, uses read_local's regression instead: C and W are the code's own widths blurred in linear light, the
affine and the share are free, and lam is profiled per cell and per gap bin with the cell's other
coefficients held; vitrea draws no knee, so it must read lam = 0.
"""
import numpy as np

import forward as F
import read_local as L
from fitting import golden

HASHES = {'lam_iv.py': 'ec9761ba1307efd997b189b6ed687a1581c00e1a13a4d079a9999832b72fc1e6',
          'lam_gap.py': 'a9326f09fceccf9e1592ee214a59d409dca7a15a1336d03d315cba31ace50b6d'}
LAM_GRID = np.round(np.arange(-0.5, 1.61, 0.02), 3)
INTERVAL_TOL = 0.10
GAP_BINS = (0.0, 0.05, 0.1, 0.2, 0.3, 0.45, 1.0)
MIN_BIN_PX = 200


TRUST_LAMS = (0.0, 1.2)


def _obs(cell, mp=None):
    """Observed codes on the deep mask and the pixels the readers may use. Where T is not measured above an
    input (memo C's dark trust limits at spans >= 96), the pixel set is decided by the MODEL, not by the
    observed code: a pixel is kept only if its predicted M stays below the limit for every lam in TRUST_LAMS
    (M is monotone in lam). Selecting on the observed code would keep the knee-side pixels whose noise
    happened to fall low and drop the rest, a censoring that biases lam (X21's one-sided bound, in reader
    form); the first proof-1 run showed it, reading 1.6 at the bound on dark cells whose truth was 0.9."""
    y = cell.y[cell.mask]
    ok = np.isfinite(y)
    lim = getattr(cell.T, 'trust_below', None)
    if lim is not None:
        if mp is None:
            ok &= cell.T.trusted(np.where(ok, y, 0.0))
        else:
            sg = 1 if cell.scheme == 'light' else -1
            C, W = mp['C'], mp['W']
            for lam in TRUST_LAMS:
                M = 255 * ((1 - F.WN) * (C + sg * lam * np.maximum(0, sg * (W - C))) + F.WN * W)
                ok &= M < lim
    return y, ok


def per_cell(cell, fam, p):
    """lam alone on one cell at held outer parameters p (e.g. {'k': ...} or {'k_n', 'k_w', ...})."""
    q = F.expand(fam, dict(p))
    mp = F.maps(cell, fam, q)
    y, ok = _obs(cell, mp)
    if ok.sum() < MIN_BIN_PX:
        return dict(lam=None, lo=None, hi=None, rms=None, rms09=None, at_bound=False, n=int(ok.sum()),
                    note='no trusted pixels: T is not measured over this cell\'s levels')

    def rms(lam):
        return float(np.sqrt(np.mean((F.compose(cell, fam, mp, lam) - y)[ok] ** 2)))

    r = np.array([rms(v) for v in LAM_GRID])
    i = int(np.argmin(r))
    lo, hi = LAM_GRID[max(0, i - 1)], LAM_GRID[min(len(LAM_GRID) - 1, i + 1)]
    lam = golden(rms, lo, hi, tol=1e-4)
    best = rms(lam)
    okv = LAM_GRID[r <= best + INTERVAL_TOL]
    return dict(lam=float(lam), lo=float(okv.min()), hi=float(okv.max()), rms=best, rms09=rms(0.9),
                at_bound=bool(i in (0, len(LAM_GRID) - 1)), n=int(ok.sum()))


def hinge_gap(cell, fam, p, bins=GAP_BINS):
    """lam per bin of the knee-side hinge gap at held outer parameters p."""
    q = F.expand(fam, dict(p))
    mp = F.maps(cell, fam, q)
    y, ok = _obs(cell, mp)
    C, W = mp['C'], mp['W']
    sg = 1 if cell.scheme == 'light' else -1
    gap = sg * (W - C)
    out = []
    for a, b in zip(bins[:-1], bins[1:]):
        m = ok & (gap > a) & (gap <= b)
        if m.sum() < MIN_BIN_PX:
            out.append(dict(bin=(a, b), lam=None, n=int(m.sum())))
            continue

        def rms(lam, m=m):
            N = C[m] + sg * lam * gap[m]
            M = (1 - F.WN) * N + F.WN * W[m]
            return float(np.sqrt(np.mean((cell.T(255 * M) - y[m]) ** 2)))

        r = np.array([rms(v) for v in LAM_GRID])
        i = int(np.argmin(r))
        lam = golden(rms, LAM_GRID[max(0, i - 1)], LAM_GRID[min(len(LAM_GRID) - 1, i + 1)], tol=1e-4)
        okv = LAM_GRID[r <= rms(lam) + INTERVAL_TOL]
        out.append(dict(bin=(a, b), lam=float(lam), lo=float(okv.min()), hi=float(okv.max()), n=int(m.sum())))
    return out


# ---------------------------------------------------------------- the linear reading (vitrea's control)

def _linear_parts(cell, sn, sw, support='canvas', edge='clamp'):
    pix = cell.mask
    key = ('_rlam', id(pix), round(sn, 4), round(sw, 4), support, edge)
    if key not in cell._cache:
        b = L.Basis(cell, pix, 'linear')
        M, wt, ok = L.observed(cell, pix, 'linear')
        cell._cache[key] = (M, wt, ok, b.C(sn=sn), b.W(sw, support, edge), b.sg)
    return cell._cache[key]


def per_cell_linear(cell, sn, sw, support='canvas', edge='clamp'):
    """lam profiled on one cell in the linear reading, a0, gain and w re-fitted at each lam."""
    part = _linear_parts(cell, sn, sw, support, edge)
    rms = lambda lam: L.regress([part], lam=lam)['rms']
    r = np.array([rms(v) for v in LAM_GRID])
    i = int(np.argmin(r))
    lam = golden(rms, LAM_GRID[max(0, i - 1)], LAM_GRID[min(len(LAM_GRID) - 1, i + 1)], tol=1e-4)
    best = rms(lam)
    okv = LAM_GRID[r <= best + INTERVAL_TOL]
    free = L.regress([part])
    return dict(lam=float(lam), lo=float(okv.min()), hi=float(okv.max()), rms=best, rms0=rms(0.0),
                lam_free=free['lam'], w_free=free['w'], rms_free=free['rms'], n=int(part[2].sum()))


def hinge_gap_linear(cell, sn, sw, support='canvas', edge='clamp', bins=GAP_BINS):
    """lam per knee-side gap bin in the linear reading, the cell's a0, gain and w held at its lam = 0 read."""
    M, wt, ok, C, W, sg = _linear_parts(cell, sn, sw, support, edge)
    base = L.regress([(M, wt, ok, C, W, sg)], lam=0.0)
    a0, g, w = base['a0'], base['gain'], base['w']
    gap = sg * (W - C) / 255.0
    out = []
    for a, b in zip(bins[:-1], bins[1:]):
        m = ok & (gap > a) & (gap <= b)
        if m.sum() < MIN_BIN_PX:
            out.append(dict(bin=(a, b), lam=None, n=int(m.sum())))
            continue

        def rms(lam, m=m):
            pred = a0 + g * ((1 - w) * (C[m] + sg * lam * 255 * gap[m]) + w * W[m])
            return float(np.sqrt(np.mean(((pred - M[m]) * wt[m]) ** 2)))

        r = np.array([rms(v) for v in LAM_GRID])
        i = int(np.argmin(r))
        lam = golden(rms, LAM_GRID[max(0, i - 1)], LAM_GRID[min(len(LAM_GRID) - 1, i + 1)], tol=1e-4)
        okv = LAM_GRID[r <= rms(lam) + INTERVAL_TOL]
        out.append(dict(bin=(a, b), lam=float(lam), lo=float(okv.min()), hi=float(okv.max()), n=int(m.sum())))
    return out


def encoded_control(cell, sn, sw, support='canvas', edge='clamp'):
    """The known-space control: vitrea's LINEAR captures read with ENCODED basis maps and the output codes as
    M (an affine T in encoded values): memo C's reading manufactured lam 1.4-1.5 this way."""
    pix = cell.mask
    b = L.Basis(cell, pix, 'linear')
    b.space, b.floor = 'enc', False
    y = L.luma_img(cell.y)[pix]
    ok = np.isfinite(y)
    part = (y, np.ones_like(y), ok, b.C(sn=sn), b.W(sw, support, edge), b.sg)
    return L.regress([part])
