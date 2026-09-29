"""W42 G0 proof 2 (charter clause 2, "the families that should be distinguishable are distinguished"): for each
declared pair, the fitted family's best reach of the truth family's region statistics on the bed.

For a truth family A and a fitted family B (tolerances.json, proof2_separation.rule): B is fitted to A's
quantised synthetic render by least squares, then refined by minimax on the region statistics of A's EXACT
render; s is the largest remaining |statistic difference|. DISTINGUISHED if s > 1.5 codes, UNRESOLVED if
s < 0.5, MARGINAL between. A pair not distinguished on the cells that should answer it is re-read on the
whole bed (2x families B-E and the 1x pass) before it is reported.

Pairs, per endpoint:
  rival -> LT      could LT mimic each rival (so a true rival would be missed)?
  LT -> rival      could each rival that does not contain LT mimic LT?
  U1 set           W-shape, W-tails, K2 and W-canvas against each other, receded endpoints (U1's candidates)
  nulls            LT -> each rejected null, pooled rms against memo E's bars (2.60 reading, 4.65 unit)

Usage: python3.12 proof2_separation.py [set ...] with set in {rivals, lt, u1, nulls}; writes
proof2_separation.json / .txt (merging with an earlier run's rows).
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

import bed
import families as FA
import fitting as Fi
import forward as F
import proof_common as PC

EPS = F.ENDPOINTS
RIVALS = [n for n, v in FA.FAMILIES.items() if v[4].startswith('rival')]
NESTED = {'LT-2k', 'W-tails', 'K2'}          # contain LT: LT is one of their parameter points
U1SET = ['W-shape', 'W-tails', 'K2', 'W-canvas']   # memo E §3b: R1 does not move the drift
NULLS = [n for n, v in FA.FAMILIES.items() if v[4] == 'null']
# The minimax refinement is run wherever the least-squares point could plausibly be pulled under the
# 1.5-code line; on the pairs where it ran it moved s by at most a few tenths (reported per pair).
MINIMAX_SKIP = 6.0


def applicable(name, ep):
    if name.startswith('LT+bleed') and ep.endswith('inactive'):
        return False
    return True


def run_pair(args):
    truth_name, fit_name, ep, whole = args
    t0 = time.time()
    letters = sorted(set(PC.LETTERS[truth_name]) | set(PC.LETTERS[fit_name]))
    if whole:
        letters = ['B', "B'", 'C', 'D', 'E']
    cells = []
    for s in ((2, 1) if whole else (2,)):
        cells += bed.cells(ep, s, letters=letters)
    tfam, ffam = FA.FAMILIES[truth_name][0], FA.FAMILIES[fit_name][0]
    exact = PC.render_truth(cells, tfam, PC.truth(truth_name, ep))
    prob = Fi.Problem(cells, ffam, PC.layout_for(fit_name, ep), PC.bounds_for(fit_name))
    keep = {c.id for c in prob.cells}
    exact = [e for c, e in zip(cells, exact) if c.id in keep]
    cells = prob.cells
    tstats = PC.stats_list(cells, exact)
    ls = prob.fit(PC.starts_for(fit_name, ep, len(prob.keys)))
    preds = prob.predictions(ls['xvec'], ls['lam'])
    s_ls, where_ls = PC.survival_misfit(cells, preds, tstats)
    out = dict(truth=truth_name, fit=fit_name, ep=ep, whole=whole, n_cells=len(cells), letters=letters,
               excluded=prob.excluded,
               ls_pooled=ls['pooled'], ls_max_cell=ls['max_cell'], ls_x=ls['x'], ls_lam=ls['lam'], s_ls=s_ls,
               where_ls=where_ls)
    if s_ls >= MINIMAX_SKIP:
        x, lams, s, where = ls['xvec'], ls['lam'], s_ls, where_ls
        out['minimax'] = f'not run: the LS point misses by {s_ls:.2f} >= {MINIMAX_SKIP}'
    else:
        x, lams, s, where = PC.minimax_refine(prob, ls['xvec'], ls['lam'], tstats, maxfev=60)
        out['minimax'] = 'Nelder-Mead from the LS point, 60 evaluations'
    out.update(s=s, where=where, mm_x={f'{k[0][0]}@{k[0][1]}': float(v) for k, v in zip(prob.keys, x)},
               mm_lam=lams, verdict=PC.verdict(s), seconds=time.time() - t0, bed=bed.BED_COMMIT[:8])
    # which cells carry the separation at the minimax point
    per = []
    for c, st in zip(cells, tstats):
        p = prob.params_for(x, c)
        p['lam'] = lams[c.ep]
        pred = F.render(c, ffam, p)
        sc, wh = PC.survival_misfit([c], [pred], [st])
        per.append((c.id, sc, wh))
    per.sort(key=lambda r: -r[1])
    out['top_cells'] = per[:5]
    return out


def run_null(args):
    """A null fitted to an LT truth on every structured family of BOTH scales: the unit nulls are only testable
    across scales (at 2x one point is two device px and, off rrect-lg, one texel, so a 2x-only bed reads
    'points' and 'device px' as the same law with k doubled)."""
    null, ep = args
    letters = ('B', "B'", 'C', 'D')
    cells = bed.cells(ep, 2, letters=letters) + bed.cells(ep, 1, letters=letters)
    PC.render_truth(cells, F.Family(), PC.truth('LT', ep))
    prob = Fi.Problem(cells, FA.FAMILIES[null][0], PC.layout_for(null, ep), PC.bounds_for(null))
    r = prob.fit(PC.starts_for(null, ep, 1))
    return dict(truth='LT', fit=null, ep=ep, n_cells=len(cells), pooled=r['pooled'], max_cell=r['max_cell'],
                x=r['x'], lam=r['lam'])


def jobs_for(which):
    J = []
    if 'rivals' in which:
        J += [(r, 'LT', ep, False) for r in RIVALS for ep in EPS if applicable(r, ep)]
    if 'lt' in which:
        for r in RIVALS:
            for ep in EPS:
                if not applicable(r, ep) or r in NESTED or (r == 'free-sn' and ep.endswith('inactive')):
                    continue
                J.append(('LT', r, ep, False))
    if 'u1' in which:
        J += [(a, b, ep, False) for ep in ('light-inactive', 'dark-inactive') for a in U1SET for b in U1SET
              if a != b and not (b in NESTED and a == 'LT')]
    return J


def write(rows, nulls):
    json.dump(dict(pairs=rows, nulls=nulls), open('proof2_separation.json', 'w'), indent=1, default=float)
    L = ['W42 G0 proof 2: separation on the bed (s = the fitted family\'s best max region-statistic miss, codes)',
         'truth -> fit      endpoint          s(minimax)  s(LS)  LS pooled  verdict        cells  where', '']
    for r in sorted(rows, key=lambda r: (r['truth'], r['fit'], r['ep'], r['whole'])):
        L.append(f"{r['truth']:>12s} -> {r['fit']:<13s} {r['ep']:15s} {r['s']:7.2f} {r['s_ls']:7.2f} "
                 f"{r['ls_pooled']:7.3f}  {r['verdict']:13s} {r['n_cells']:3d}{' whole' if r['whole'] else ''}  "
                 f"{r['where']}")
    if nulls:
        L += ['', 'rejected nulls fitted to LT truth: pooled rms (memo E bars: mixture >= 2.60, units/R2 >= 4.65)']
        for r in nulls:
            L.append(f"  {r['fit']:14s} {r['ep']:15s} pooled {r['pooled']:.2f} max cell {r['max_cell']:.2f} "
                     f"x {r['x']}")
    open('proof2_separation.txt', 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    which = sys.argv[1:] or ['rivals', 'lt', 'u1', 'nulls']
    try:
        prev = json.load(open('proof2_separation.json'))
        rows, nulls = prev['pairs'], prev['nulls']
    except FileNotFoundError:
        rows, nulls = [], []
    done = {(r['truth'], r['fit'], r['ep'], r['whole']) for r in rows}
    with Pool(int(os.environ.get('W42_POOL', '2'))) as pool:
        J = [j for j in jobs_for(which) if j not in done]
        for r in pool.imap_unordered(run_pair, J):
            rows.append(r)
            print(f"{r['truth']} -> {r['fit']} {r['ep']}: s {r['s']:.2f} ({r['verdict']}) {r['seconds']:.0f}s",
                  flush=True)
            write(rows, nulls)
        # re-read on the whole bed every pair not distinguished on its subset
        again = [(r['truth'], r['fit'], r['ep'], True) for r in rows if not r['whole'] and r['verdict'] != 'DISTINGUISHED'
                 and (r['truth'], r['fit'], r['ep'], True) not in done]
        for r in pool.imap_unordered(run_pair, again):
            rows.append(r)
            print(f"WHOLE {r['truth']} -> {r['fit']} {r['ep']}: s {r['s']:.2f} ({r['verdict']})", flush=True)
            write(rows, nulls)
        if 'nulls' in which:  # superseded by proof2_nulls.py, which runs them apart
            nulls = [n for n in nulls]
            for r in pool.imap_unordered(run_null, [(n, ep) for n in NULLS for ep in EPS]):
                nulls.append(r)
                print(f"null {r['fit']} {r['ep']}: pooled {r['pooled']:.2f}", flush=True)
                write(rows, nulls)
