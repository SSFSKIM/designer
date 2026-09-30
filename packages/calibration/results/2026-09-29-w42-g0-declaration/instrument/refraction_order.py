"""W42 G0 instrument: the refraction-order test (the parent's revised ruling 3). Declared in tolerances.json
"refraction_order_test": the median form (17da5c7d), the tail form v2 (cb490956), and v3 (79152643), each before
its own proof ran.

The active pose refracts inside a 20-pt inner band and a 19.2-pt outer reach. The primary hypothesis is that
refraction acts AFTER the blur: the blurred body is displaced inside the band, and every pixel beyond it is the
law's own value, whatever the kernel's reach. The rival is refraction BEFORE the blur: the capture is displaced
first, so W at a pixel 20-54 pt deep integrates displaced content from the band and the law, which knows no
refraction, misfits there more the nearer the band is.

v3 (the review of b151aff4, finding I-1): the v2 statistic reads BEFORE on a wrong family with no lens at all, so
v3 measures SPECIFICITY beside sensitivity and makes the call conditional on the fitted family's residual.
  fit     the test family F (LT here) as the gated fit: both scales, families A-E, the narrow-support mask;
  voters  2x cells only (the 1x cells are fitted, never vote);
  S1      D_tail: per voting cell Delta_c = rms(NEAR) - rms(FAR) of the luma residual binned by depth ([d_in, 30),
          [30, 38), [38, 46), [46, 54), [54, inf) pt; NEAR the shallowest bin with >= 200 px, FAR the deepest, at
          least 16 pt deeper); D_tail = mean of the 3 largest over structured cells - the same over uniform cells;
          BEFORE > 0.30, AFTER < 0.15;
  S2      A_hat = A_ref beta, beta the pooled projection of the voting structured cells' luma residuals on the
          regressor R_c = F's render with the stand-in lens (A_ref = 8 pt) before every blur - F's render;
          BEFORE >= 8 pt, AFTER < 4 pt;
  legs    sensitivity: an LT truth with the stand-in lens before the blur, A in {0, 2, 4, 8, 16} pt;
          specificity: every declared rival as an AFTER truth, no lens;
  call    a statistic is admitted on a reading only when F's pooled rms there is below P*_S, the smallest pooled
          rms at which its specificity leg reads other than AFTER (see tolerances.json v3 for the whole rule).
The stand-in lens displaces the floored capture along the SDF normal by A (1 - |d| / h)^2, pointing inward,
inside the 20-pt inner band and outside the edge to the 19.2-pt outer reach; the lens's real form is declared
only by its inputs (memo D §3).

Usage: python3.12 refraction_order.py v3   (writes refraction_order.v3.json / .txt; the v2 record,
refraction_order.json / .txt, is left as it stands). `python3.12 refraction_order.py v2` re-runs v2.
"""
import copy
import json
import os
import sys
import time
from multiprocessing import Pool

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


def displaced_capture(cell, A, win, floor='gauss'):
    """The floored capture on `win` displaced along the SDF normal (the BEFORE order's input)."""
    S = cell.S(win, floor)
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


def with_lens(cell, A):
    """A copy of the cell whose capture is displaced by the stand-in lens on EVERY window a family reads (R_fp, the
    canvas, a rounded-shape window), with a fresh token so no cached blur is shared."""
    c2 = copy.copy(cell)
    c2._cache, c2._crops, c2._pops = {}, {}, None
    c2.token = next(F._TOKENS)

    def S(win, floor='gauss'):
        key = ('S', win, floor)
        if key not in c2._cache:
            c2._cache[key] = displaced_capture(cell, A, win, floor)
        return c2._cache[key]
    c2.S = S
    return c2


def render_before(cell, fam, p, A):
    """The family rendered on a displaced capture."""
    return F.render(with_lens(cell, A), fam, F.expand(fam, p))


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


def statistic(cells, resids, voters=None):
    """S1. v2 (the declared statistic since cb490956): D_tail, the mean of the 3 largest Delta_c over structured
    cells minus the same over uniform cells. v1 (the median form, 17da5c7d) is reported beside it. `voters`: the
    cells that vote (v3: the 2x cells; v2: every cell given)."""
    voters = set(c.id for c in cells) if voters is None else voters
    per = {c.id: delta_c(c, e) for c, e in zip(cells, resids) if c.id in voters}
    struct = sorted(v for c in cells if c.id in per and c.letter != 'A' and (v := per[c.id]) is not None)
    unif = sorted(v for c in cells if c.id in per and c.letter == 'A' and (v := per[c.id]) is not None)
    tail = lambda xs: float(np.mean(xs[-3:])) if xs else 0.0
    D_tail = tail(struct) - tail(unif)
    D_v1 = (float(np.median(struct)) if struct else float('nan')) - (float(np.median(unif)) if unif else 0.0)
    call = 'BEFORE' if D_tail > BEFORE_BAR else 'AFTER' if D_tail < AFTER_BAR else 'undecided'
    top = sorted(((v, cid) for cid, v in per.items() if v is not None and not cid.split('|')[1].startswith('a-')),
                 reverse=True)[:3]
    return dict(D=D_tail, D_v1=D_v1, n_struct=len(struct), n_unif=len(unif), call=call,
                carried=sum(v > BEFORE_BAR for v in struct), top_cells=top, per_cell=per)


LUMA = np.array([0.2126, 0.7152, 0.0722])
A_REF = 8.0
S2_BEFORE, S2_AFTER = 8.0, 4.0


def projection(cells, resids, fam, pfit, voters):
    """S2: A_hat = A_REF * beta, beta = sum <e, R> / sum <R, R> over the voting structured cells, R the render with
    the stand-in lens at A_REF before every blur less the render without it, both at F's fitted point."""
    num = den = 0.0
    per = []
    for c, e in zip(cells, resids):
        if c.id not in voters or c.letter == 'A':
            continue
        p = pfit(c)
        R = render_before(c, fam, p, A_REF) - F.render(c, fam, F.expand(fam, p))
        el = e if e.ndim == 1 else e @ LUMA
        Rl = R if R.ndim == 1 else R @ LUMA
        a, b = float(el @ Rl), float(Rl @ Rl)
        num, den = num + a, den + b
        per.append((c.id, a, b))
    A_hat = A_REF * num / den if den > 0 else 0.0
    call = 'BEFORE' if A_hat >= S2_BEFORE else 'AFTER' if A_hat < S2_AFTER else 'undecided'
    top = sorted(per, key=lambda r: -abs(r[1]))[:3]
    return dict(A_hat=A_hat, call=call, n=len(per), top_cells=[(cid, A_REF * a / den if den else 0.0)
                                                             for cid, a, _ in top])


def run(ep, order, A=None, seed=0):
    """v2: render the LT truth in one order on the 2x cells, fit LT at the narrow-support mask, the statistic."""
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


def run_v3(args):
    """v3, one leg row: the truth (an LT truth with the lens at A, or a declared rival with no lens) on both scales
    of families A-E, LT fitted as the gated fit, S1 over the 2x voters and S2."""
    ep, truth, A, seed = args
    t0 = time.time()
    cells = []
    for sc in (2, 1):
        cells += bed.cells(ep, sc, letters=('A', 'B', "B'", 'C', 'D', 'E'), kernel='n')
    tfam = FA.FAMILIES[truth][0]
    p = PC.truth(truth, ep)
    rng = np.random.default_rng(seed)
    for c in cells:
        y = render_before(c, tfam, p, A) if A else F.render(c, tfam, F.expand(tfam, p))
        yq = np.clip(np.round(y + rng.uniform(-0.5, 0.5, y.shape)), 0, 255)
        img = np.full(c.d.shape + ((3,) if c.rgb else ()), np.nan)
        img[c.mask] = yq
        c.y = img
    fam = F.Family()
    prob = Fi.Problem(cells, fam, FA.LAYOUTS['k@endpoint'], PC.bounds_for('LT'))
    res = prob.fit(PC.starts_for('LT', ep, 1))
    preds = prob.predictions(res['xvec'], res['lam'])
    resids = [c.y[c.mask] - pr for c, pr in zip(prob.cells, preds)]
    voters = {c.id for c in prob.cells if c.scale == 2}
    s1 = statistic(prob.cells, resids, voters)
    pfit = lambda c: {'k': res['x'][f'k@{ep}'], 'lam': res['lam'][ep]}
    s2 = projection(prob.cells, resids, fam, pfit, voters)
    return dict(ep=ep, truth=truth, A=A, leg='sensitivity' if truth == 'LT' else 'specificity', pooled=res['pooled'],
                max_cell=res['max_cell'], k=res['x'][f'k@{ep}'], lam=res['lam'][ep], n_cells=len(prob.cells),
                n_voters=len(voters), S1=dict((k, v) for k, v in s1.items() if k != 'per_cell'),
                S1_per_cell=s1['per_cell'], S2=s2, bed=bed.BED_COMMIT[:8], engine=F.ENGINE,
                seconds=time.time() - t0)


def not_after(r, stat):
    return r['S1']['D'] >= AFTER_BAR if stat == 'S1' else r['S2']['A_hat'] >= S2_AFTER


def validity(rows):
    """Per endpoint and statistic: P*_S, the resolution (smallest A reading BEFORE), power, and whether P*_S
    reaches 2.1 codes (memo E's LT pooled rms on Apple's cells, at its low end)."""
    out = {}
    for ep in sorted({r['ep'] for r in rows}):
        spec = [r for r in rows if r['ep'] == ep and r['leg'] == 'specificity']
        sens = sorted((r for r in rows if r['ep'] == ep and r['leg'] == 'sensitivity'), key=lambda r: r['A'] or 0)
        for stat in ('S1', 'S2'):
            bad = [r['pooled'] for r in spec if not_after(r, stat)]
            pstar = min(bad) if bad else max((r['pooled'] for r in spec), default=float('nan'))
            before = [r['A'] for r in sens if r['A'] and r[stat]['call'] == 'BEFORE']
            after0 = [r for r in sens if not r['A']]
            out[f'{ep}|{stat}'] = dict(
                P_star=pstar, P_star_from='the first non-AFTER specificity row' if bad else "the leg's range (none "
                'reads other than AFTER)', false_non_after=sorted((r['truth'], round(r['pooled'], 3)) for r in spec
                                                                   if not_after(r, stat)),
                resolution=min(before) if before else None, power=bool(before),
                after_reads_after=bool(after0) and after0[0][stat]['call'] == 'AFTER',
                admits_memo_E_LT=bool(before) and pstar > 2.1)
    return out


def write_v3(rows):
    rows = sorted(rows, key=lambda r: (r['ep'], r['leg'] != 'sensitivity', r['A'] or 0, r['truth']))
    val = validity(rows)
    json.dump(dict(rows=rows, validity=val), open('refraction_order.v3.json', 'w'), indent=1, default=float)
    L = ['W42 G0 refraction-order test v3 (tolerances.json refraction_order_test.v3_2026-09-30, declared in 79152643',
         'before this proof): LT fitted on both scales of families A-E at the narrow mask; 2x cells vote.',
         'S1 = D_tail (BEFORE > 0.30, AFTER < 0.15); S2 = A_hat, the lens projection (BEFORE >= 8 pt, AFTER < 4 pt).',
         'P = LT\'s pooled rms over the fitted cells. Sensitivity: an LT truth, the stand-in lens before the blur at A;',
         'specificity: each declared rival as an AFTER truth, no lens.', '']
    for r in rows:
        what = f"LT truth, lens A {r['A'] or 0:>4}" if r['leg'] == 'sensitivity' else f"rival {r['truth']}"
        L.append(f"  {r['ep']:10s} {r['leg']:11s} {what:34s} P {r['pooled']:6.3f}  S1 {r['S1']['D']:+6.3f} "
                 f"{r['S1']['call']:9s}  S2 {r['S2']['A_hat']:+7.2f} pt {r['S2']['call']:9s}  k {r['k']:.4f} "
                 f"lam {r['lam']:.3f}  S1 top {', '.join(f'{c.split(chr(124))[1]} {v:.2f}' for v, c in r['S1']['top_cells'])}")
    L += ['', 'VALIDITY (per endpoint and statistic): P*_S, the pooled rms below which the statistic is admitted;',
          "its resolution (the smallest lens reading BEFORE); whether it would admit LT at memo E's 2.1 codes."]
    for k, v in val.items():
        L.append(f"  {k:14s} P* {v['P_star']:.3f} ({v['P_star_from']}); resolution "
                 f"{v['resolution'] if v['resolution'] else 'none (no power at A <= 16)'}; AFTER truth reads AFTER: "
                 f"{v['after_reads_after']}; admits LT at 2.1 codes: {v['admits_memo_E_LT']}; false non-AFTER: "
                 f"{v['false_non_after']}")
    open('refraction_order.v3.txt', 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'v3'
    if which == 'v2':
        rows = []
        for ep in ('light-rest', 'dark-rest'):
            for order, A in [('after', None)] + [('before', a) for a in STRENGTHS]:
                r = run(ep, order, A)
                rows.append(r)
                print(f"{ep:11s} {order:6s} A {A} D_tail {r['D']:+.3f} call {r['call']} pooled {r['pooled']:.3f}",
                      flush=True)
                json.dump(rows, open('refraction_order.json', 'w'), indent=1, default=float)
        sys.exit(0)
    only = [e for e in os.environ.get('W42_EPS', '').split(',') if e] or ['light-rest', 'dark-rest']
    rivals = [n for n, v in FA.FAMILIES.items() if v[4].startswith('rival')]
    jobs = [(ep, 'LT', A, 0) for ep in only for A in (None,) + STRENGTHS]
    jobs += [(ep, n, None, 0) for ep in only for n in rivals]
    try:
        rows = json.load(open('refraction_order.v3.json'))['rows']
    except FileNotFoundError:
        rows = []
    done = {(r['ep'], r['truth'], r['A']) for r in rows if r.get('engine') == F.ENGINE}
    jobs = [j for j in jobs if (j[0], j[1], j[2]) not in done]
    with Pool(int(os.environ.get('W42_POOL', '2'))) as pool:
        for r in pool.imap_unordered(run_v3, jobs):
            rows.append(r)
            print(f"{r['ep']} {r['leg']} {r['truth']} A {r['A']}: P {r['pooled']:.3f} S1 {r['S1']['D']:+.3f} "
                  f"S2 {r['S2']['A_hat']:+.2f} ({r['seconds']:.0f}s)", flush=True)
            write_v3(rows)
    write_v3(rows)
