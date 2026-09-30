"""W42 G0 proof 2: the minimax refinement's convergence on the rows near the 1.5-code line whose search has three or
more dimensions (the review of b151aff4, I-8). The separation rows run 60 Nelder-Mead evaluations from the
least-squares point; here each named row's search continues from its RECORDED minimax point with a fresh simplex
(3 % steps, 120 evaluations), then restarts from the best point found (1 % steps, 60 evaluations): three times the separation run's budget. The truth and the
fitted family are rebuilt exactly as proof2_separation.run_pair builds them (same cells, pin, kernel, engine). A row
is converged within the budget when the continued search lowers s by less than 0.05 code; its verdict is re-read
at the lowest s found.

Usage: python3.12 proof2_minimax_check.py 'truth>fit>ep>whole' ...   (writes proof2_minimax_check.json / .txt)
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy import optimize

import bed
import families as FA
import fitting as Fi
import forward as F
import proof2_separation as P
import proof_common as PC
import regions as R


def search(prob, z0, tstats, step, maxfev):
    eps, n = prob.eps, len(prob.keys)
    lo = np.array([prob.bounds[k[1][0]][0] for k in prob.keys] + [Fi.LAM_BOUNDS[0]] * len(eps))
    hi = np.array([prob.bounds[k[1][0]][1] for k in prob.keys] + [Fi.LAM_BOUNDS[1]] * len(eps))
    pops = [R.populations(c) for c in prob.cells]

    def f(z):
        z = np.clip(z, lo, hi)
        x, lams = z[:n], dict(zip(eps, z[n:]))
        worst = 0.0
        for c, st, pp in zip(prob.cells, tstats, pops):
            p = prob.params_for(x, c)
            p['lam'] = lams[c.ep]
            sp = R.stats_from_masked(c, F.render(c, prob.fam, p), pp)
            worst = max([worst] + [abs(sp[k] - v) for k, v in st.items()])
        return worst
    st = np.maximum(step * np.abs(z0), step)
    simplex = [z0] + [z0 + np.eye(len(z0))[i] * st[i] for i in range(len(z0))]
    r = optimize.minimize(f, z0, method='Nelder-Mead',
                          options=dict(maxfev=maxfev, xatol=1e-5, fatol=1e-4, initial_simplex=simplex))
    return np.clip(r.x, lo, hi), float(f(r.x)), int(r.nfev), f(z0)


def check(key):
    truth, fit, ep, whole = key
    t0 = time.time()
    rows = json.load(open('proof2_separation.json'))['pairs']
    here = lambda r: (r.get('bed'), r.get('kernel')) == (bed.BED_COMMIT[:8], PC.KERNEL if ep.endswith('rest')
                                                          else 'receded (no band)') and P.engine_ok(r)
    cand = [r for r in rows if (r['truth'], r['fit'], r['ep'], bool(r['whole'])) == key]
    rec = ([r for r in cand if here(r)] or cand)[-1]
    cells = []
    for s in ((2, 1) if whole else (2,)):
        cells += bed.cells(ep, s, letters=rec['letters'], kernel=PC.KERNEL)
    tfam, ffam = FA.FAMILIES[truth][0], FA.FAMILIES[fit][0]
    exact = PC.render_truth(cells, tfam, PC.truth(truth, ep))
    prob = Fi.Problem(cells, ffam, PC.layout_for(fit, ep), PC.bounds_for(fit))
    keep = {c.id for c in prob.cells}
    exact = [e for c, e in zip(cells, exact) if c.id in keep]
    tstats = PC.stats_list(prob.cells, exact)
    z0 = np.array([rec['mm_x'][f'{k[0][0]}@{k[0][1]}'] for k in prob.keys] + [rec['mm_lam'][e] for e in prob.eps])
    z1, s1, n1, s_at_rec = search(prob, z0, tstats, 0.03, 120)
    z2, s2, n2, _ = search(prob, z1, tstats, 0.01, 60)
    best = min(s1, s2, s_at_rec)
    return dict(truth=truth, fit=fit, ep=ep, whole=whole, n_cells=len(prob.cells), dims=len(z0),
                s_recorded=rec['s'], s_at_recorded_point=s_at_rec, s_continued=s1, nfev_continued=n1,
                s_restart=s2, nfev_restart=n2, s_best=best, drop=rec['s'] - best, converged=rec['s'] - best < 0.05,
                verdict_recorded=rec['verdict'], verdict_best=PC.verdict(best), z_best=list(z2 if s2 <= s1 else z1),
                row_bed=rec.get('bed'), row_engine=rec.get('engine'), seconds=time.time() - t0)


if __name__ == '__main__':
    keys = []
    for a in sys.argv[1:]:
        t, f, e, w = a.split('>')
        keys.append((t, f, e, w == 'whole'))
    try:
        out = json.load(open('proof2_minimax_check.json'))
    except FileNotFoundError:
        out = []
    with Pool(int(os.environ.get('W42_POOL', '2'))) as pool:
        for r in pool.imap_unordered(check, keys):
            out = [o for o in out if (o['truth'], o['fit'], o['ep'], o['whole']) != (r['truth'], r['fit'], r['ep'], r['whole'])] + [r]
            print(f"{r['truth']} -> {r['fit']} {r['ep']}: recorded {r['s_recorded']:.3f}, best {r['s_best']:.3f} "
                  f"({'converged' if r['converged'] else 'MOVED'}; {r['verdict_best']}) {r['seconds']:.0f}s", flush=True)
            json.dump(out, open('proof2_minimax_check.json', 'w'), indent=1, default=float)
    L = ['W42 G0 proof 2: minimax convergence on the rows near the 1.5 line with >= 3 search dimensions (I-8).',
         'Continued from each recorded minimax point: 120 Nelder-Mead evaluations (3 % simplex), then 60 (1 %).']
    for r in out:
        L.append(f"  {r['truth']:>12s} -> {r['fit']:<14s} {r['ep']:15s}{' whole' if r['whole'] else '      '} dims {r['dims']} "
                 f"s recorded {r['s_recorded']:.3f} (re-evaluated {r['s_at_recorded_point']:.3f}) -> best {r['s_best']:.3f} "
                 f"{'converged' if r['converged'] else 'MOVED by %.3f' % r['drop']}; {r['verdict_recorded']} -> "
                 f"{r['verdict_best']}")
    open('proof2_minimax_check.txt', 'w').write('\n'.join(L) + '\n')
