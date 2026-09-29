"""W42 G0 instrument: the refraction-order test (the parent's revised ruling 3; declared in tolerances.json
"refraction_order_test", 17da5c7d, before this proof ran).

The active pose refracts inside a 20-pt inner band and a 19.2-pt outer reach. The primary hypothesis is that
refraction acts AFTER the blur: the blurred body is displaced inside the band, and every pixel beyond it is the
law's own value, whatever the kernel's reach. The rival is refraction BEFORE the blur: the capture is displaced
first, so W at a pixel 20-54 pt deep integrates displaced content from the band and the law, which knows no
refraction, misfits there more the nearer the band is.

The statistic (`statistic()`): fit the law on the active cells at the narrow-support mask, bin each cell's luma
residual by depth ([d_in, 30), [30, 38), [38, 46), [46, 54), [54, inf) pt), take Delta_c = rms(NEAR) - rms(FAR)
per cell (NEAR the shallowest bin with >= 200 px, FAR the deepest, at least 16 pt deeper), and D = the mean of
the 3 largest Delta_c over the structured cells minus the same over the uniform cells (the tail form, declared
in cb490956 after the median form of 17da5c7d proved powerless). BEFORE above 0.30 code, AFTER below 0.15,
undecided between.

The proof renders both orders. AFTER is the law's own render (the displacement after the blur never reaches a
pixel beyond the band). BEFORE displaces the floored capture along the SDF normal by A (1 - |d| / h)^2, pointing
inward, inside the inner band (h = 20 pt) and outside the edge to the outer reach (h = 19.2 pt), then renders the
law on the displaced capture. The lens's real form is declared only by its inputs (memo D §3); A sweeps
{2, 4, 8, 16} pt.

Usage: python3.12 refraction_order.py   (writes refraction_order.json / .txt)
"""
import copy
import json
import os

import numpy as np
from scipy import ndimage

import bed
import fitting as Fi
import forward as F
import families as FA
import proof_common as PC

BINS = (30.0, 38.0, 46.0, 54.0)
MIN_BIN_PX = 200
MIN_SEP_PT = 16.0
BEFORE_BAR, AFTER_BAR, CARRY = 0.30, 0.15, 3
STRENGTHS = (2.0, 4.0, 8.0, 16.0)


def displaced_capture(cell, A, win):
    """The floored capture on `win` displaced along the SDF normal (the BEFORE order's input)."""
    S = cell.S(win)
    y0, y1, x0, x1 = win
    d = cell.d[y0:y1, x0:x1]
    gy, gx = np.gradient(d)                          # pt per device px
    norm = np.hypot(gx, gy) + 1e-12
    nx, ny = gx / norm, gy / norm                    # outward normal
    delta = np.zeros_like(d)
    inner = (d < 0) & (d > -F.BAND_IN)
    outer = (d >= 0) & (d < F.BAND_OUT)
    delta[inner] = A * (1 + d[inner] / F.BAND_IN) ** 2
    delta[outer] = A * (1 - d[outer] / F.BAND_OUT) ** 2
    shift = delta * cell.scale                       # device px, pointing inward (against the normal)
    yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]].astype(float)
    coords = [yy - ny * shift, xx - nx * shift]
    if S.ndim == 3:
        return np.stack([ndimage.map_coordinates(S[..., c], coords, order=1, mode='nearest') for c in range(3)], -1)
    return ndimage.map_coordinates(S, coords, order=1, mode='nearest')


def render_before(cell, fam, p, A):
    """The law rendered on a displaced capture; a fresh copy of the cell so no cached blur is shared."""
    c2 = copy.copy(cell)
    c2._cache, c2._crops, c2._pops = {}, {}, None
    c2.token = next(F._TOKENS)
    win = c2.crop('box')
    c2._cache[('S', win, 'gauss')] = displaced_capture(cell, A, win)
    return F.render(c2, fam, F.expand(fam, p))


def depth_bins(cell):
    depth = -cell.d[cell.mask]
    edges = (cell.d_in,) + BINS + (np.inf,)
    return [(lo, hi, (depth >= lo) & (depth < hi)) for lo, hi in zip(edges[:-1], edges[1:])]


def delta_c(cell, resid):
    """rms(NEAR) - rms(FAR), or None when the cell has no NEAR/FAR pair."""
    r = resid if resid.ndim == 1 else resid @ np.array([0.2126, 0.7152, 0.0722])
    bins = [(lo, hi, m) for lo, hi, m in depth_bins(cell) if m.sum() >= MIN_BIN_PX]
    if len(bins) < 2:
        return None
    near, far = bins[0], bins[-1]
    if far[0] - near[0] < MIN_SEP_PT:
        return None
    rms = lambda m: float(np.sqrt(np.mean(r[m] ** 2)))
    return rms(near[2]) - rms(far[2])


def statistic(cells, resids):
    """v2 (the declared statistic since cb490956): D_tail, the mean of the 3 largest Delta_c over structured
    cells minus the same over uniform cells. v1 (the median form, 17da5c7d) is reported beside it."""
    per = {c.id: delta_c(c, e) for c, e in zip(cells, resids)}
    struct = sorted(v for c in cells if c.letter != 'A' and (v := per[c.id]) is not None)
    unif = sorted(v for c in cells if c.letter == 'A' and (v := per[c.id]) is not None)
    tail = lambda xs: float(np.mean(xs[-3:])) if xs else 0.0
    D_tail = tail(struct) - tail(unif)
    D_v1 = (float(np.median(struct)) if struct else float('nan')) - (float(np.median(unif)) if unif else 0.0)
    call = 'BEFORE' if D_tail > BEFORE_BAR else 'AFTER' if D_tail < AFTER_BAR else 'undecided'
    top = sorted(((v, cid) for cid, v in per.items() if v is not None and not cid.split('|')[1].startswith('a-')),
                 reverse=True)[:3]
    return dict(D=D_tail, D_v1=D_v1, n_struct=len(struct), n_unif=len(unif), call=call,
                carried=sum(v > BEFORE_BAR for v in struct), top_cells=top, per_cell=per)


def run(ep, order, A=None, seed=0):
    """Render the truth in one order, fit LT at the narrow-support mask, return the statistic."""
    cells = bed.cells(ep, 2, letters=('A', 'B', "B'", 'C', 'D', 'E'), kernel='n')
    fam = F.Family()
    p = PC.truth('LT', ep)
    rng = np.random.default_rng(seed)
    for i, c in enumerate(cells):
        y = render_before(c, fam, p, A) if order == 'before' else F.render(c, fam, F.expand(fam, p))
        yq = np.clip(np.round(y + rng.uniform(-0.5, 0.5, y.shape)), 0, 255)
        img = np.full(c.d.shape + ((3,) if c.rgb else ()), np.nan)
        img[c.mask] = yq
        c.y = img
    prob = Fi.Problem(cells, fam, FA.LAYOUTS['k@endpoint'], PC.bounds_for('LT'))
    res = prob.fit(PC.starts_for('LT', ep, 1))
    preds = prob.predictions(res['xvec'], res['lam'])
    resids = [c.y[c.mask] - pr for c, pr in zip(prob.cells, preds)]
    st = statistic(prob.cells, resids)
    st.update(ep=ep, order=order, A=A, k=res['x'], lam=res['lam'], pooled=res['pooled'], bed=bed.BED_COMMIT[:8])
    return st


if __name__ == '__main__':
    rows = []
    for ep in ('light-rest', 'dark-rest'):
        for order, A in [('after', None)] + [('before', a) for a in STRENGTHS]:
            r = run(ep, order, A)
            rows.append(r)
            print(f"{ep:11s} {order:6s} A {A} D_tail {r['D']:+.3f} (v1 {r['D_v1']:+.3f}; {r['n_struct']}/{r['n_unif']} "
                  f"cells; top {[(round(v, 2), c) for v, c in r['top_cells']]}) call {r['call']} pooled {r['pooled']:.3f} "
                  f"k {list(r['k'].values())[0]:.4f}", flush=True)
            json.dump(rows, open('refraction_order.json', 'w'), indent=1, default=float)
    L = ['W42 G0 refraction-order test (tolerances.json refraction_order_test, statistic_v2): synthetic renders of',
         'both orders. D_tail = mean of the 3 largest Delta_c (structured) - the same (uniform); BEFORE > 0.30,',
         'AFTER < 0.15. v1 = the first, median form (no power; refraction_order.v1.txt).']
    for r in rows:
        L.append(f"  {r['ep']:11s} {r['order']:6s} A {str(r['A']):5s} D_tail {r['D']:+.3f} (v1 {r['D_v1']:+.3f})  "
                 f"call {r['call']:9s} ({r['n_struct']} structured / {r['n_unif']} uniform cells vote) "
                 f"LT pooled {r['pooled']:.3f}; top {', '.join(f'{c.split(chr(124))[1]} {v:.2f}' for v, c in r['top_cells'])}")
    open('refraction_order.txt', 'w').write('\n'.join(L) + '\n')
