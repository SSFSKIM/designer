"""W42 G2 step 2, part 2: one declared family fitted on one endpoint's calibration cells and transferred to its
validation cells (clause 6; reading-plan.md items 5, 7 and 8).

    python3.12 -B fit_family.py FAMILY ENDPOINT [--kernel n|w] [--scales 2,1] [--tag TAG]

The fit is the instrument's: least squares (`fitting.Problem`, here per channel through native T), outer
parameters from `proof_common.starts_for`, lam inner; then minimax on the region statistics against Apple's
(censored statistics one-sided). Family A's calibration cells are scored, never optimised on (every family maps a
constant backdrop to T(level)). Output: fits/<tag>/<family>__<endpoint>.json (committed, compact) and the full
per-statistic table in the scratch directory (by SHA-256).
"""
import argparse
import gzip
import hashlib
import json
import time

import numpy as np
from scipy import optimize

import common as C

F, FA, Fi, PC = C.F, C.PC.FA, C.Fi, C.PC

GREY = ('B', "B'", 'C', 'D')


def family_of(name):
    return FA.FAMILIES[name][0]


def build(name, ep, kernel, scales):
    cal, val = [], []
    for sc in scales:
        cal += C.cells(ep, sc, ('calibration',), letters=('A',) + GREY, kernel=kernel)
        val += C.cells(ep, sc, ('validation',), letters=('A',) + GREY, kernel=kernel)
    return cal, val


def minimax(prob, x0, lams0, maxfev):
    """proof_common.minimax_refine's search (Nelder-Mead over the outer parameters and every endpoint's lam from
    the least-squares point, bounded by clipping) against Apple's region statistics, per channel, censored
    statistics as their rail deficit."""
    eps = prob.eps
    n = len(prob.keys)
    lo = np.array([prob.bounds[k[1][0]][0] for k in prob.keys] + [Fi.LAM_BOUNDS[0]] * len(eps))
    hi = np.array([prob.bounds[k[1][0]][1] for k in prob.keys] + [Fi.LAM_BOUNDS[1]] * len(eps))

    def preds_at(z):
        z = np.clip(z, lo, hi)
        x, lams = z[:n], dict(zip(eps, z[n:]))
        return prob.predictions(x, lams)

    def f(z):
        worst = 0.0
        for c, pr in zip(prob.cells, preds_at(z)):
            t = C.minimax_objective_terms(c, pr)
            if t:
                worst = max(worst, max(t))
        return worst
    z0 = np.concatenate([x0, [lams0[e] for e in eps]])
    step = np.maximum(0.02 * np.abs(z0), 0.02)
    simplex = [z0] + [z0 + np.eye(len(z0))[i] * step[i] for i in range(len(z0))]
    f0 = f(z0)
    r = optimize.minimize(f, z0, method='Nelder-Mead',
                          options=dict(maxfev=maxfev, xatol=1e-4, fatol=1e-3, initial_simplex=simplex))
    z = np.clip(r.x, lo, hi)
    if r.fun > f0:
        z = z0
    return z[:n], dict(zip(eps, z[n:])), float(min(r.fun, f0)), float(f0), int(r.nfev)


def stat_table(cells, preds):
    out = {}
    for c, pr in zip(cells, preds):
        out[c.id] = [(k, nv, round(float(pv), 4), round(float(err), 4), bound, st)
                     for k, nv, pv, err, bound, st, _ in C.score_cell(c, pr)]
    return out


def run(name, ep, kernel='n', scales=(2, 1), tag='main', level='k@endpoint', maxfev_mm=None, units=None):
    t0 = time.time()
    fam = family_of(name)
    if units:
        fam = fam.with_(units=units)
    cal, val = build(name, ep, kernel, scales)
    fitcells = [c for c in cal if c.letter != 'A']
    layout = PC.layout_for(name, ep, level)
    bounds = PC.bounds_for(name)
    prob = C.ProblemRGB(fitcells, fam, layout, bounds)
    starts = PC.starts_for(name, ep, len(prob.keys))
    res = prob.fit(starts)
    t_ls = time.time() - t0
    mm_x, mm_lams, mm_s, mm_s0, nfev = minimax(prob, res['xvec'], res['lam'],
                                               maxfev_mm or (120 if len(prob.keys) <= 2 else 200))
    t_mm = time.time() - t0 - t_ls
    points = {'ls': (res['xvec'], res['lam']), 'minimax': (mm_x, mm_lams)}
    report = dict(schema='w42-g2-step2-fit-1', family=name, endpoint=ep, kernel=kernel, scales=list(scales),
                  layout=[list(l) for l in layout], units=fam.units, count=FA.FAMILIES[name][2],
                  cells=dict(fit=len(fitcells), calibration=len(cal), validation=len(val),
                             excludedEmpty=prob.excluded),
                  seconds=dict(ls=round(t_ls), minimax=round(t_mm)))
    full = {}
    for key, (x, lams) in points.items():
        params = {k: float(v) for k, v in zip([f'{kk[0][0]}@{kk[0][1]}' for kk in prob.keys], x)}
        pc = {c.id: dict(prob.params_for(x, c), lam=lams[c.ep]) for c in cal + val}
        pred_cal = [C.render_rgb(c, fam, pc[c.id]) if fam.order != 'blurlast' else
                    _render_blurlast(c, fam, pc[c.id]) for c in cal]
        pred_val = [C.render_rgb(c, fam, pc[c.id]) if fam.order != 'blurlast' else
                    _render_blurlast(c, fam, pc[c.id]) for c in val]
        s_cal, s_val = C.summarize(cal, pred_cal), C.summarize(val, pred_val)
        report[key] = dict(params=params, lam={k: float(v) for k, v in lams.items()},
                           calibration={k: v for k, v in s_cal.items() if k != 'failed'},
                           validation={k: v for k, v in s_val.items() if k != 'failed'},
                           failedCalibration=s_cal['failed'][:40], failedValidation=s_val['failed'][:40],
                           failures=s_cal['failures'] + s_val['failures'],
                           survives=(s_cal['failures'] + s_val['failures']) == 0)
        full[key] = dict(calibration=stat_table(cal, pred_cal), validation=stat_table(val, pred_val))
    report['ls']['lsPooledFitCells'] = res['pooled']
    report['minimax']['objective'] = dict(start=mm_s0, end=mm_s, nfev=nfev)
    report['survives'] = report['ls']['survives'] or report['minimax']['survives']
    raw = json.dumps(dict(report=report, statistics=full), sort_keys=True, default=float).encode()
    scratch = C.SCRATCH / 'fits' / tag / f'{name}__{ep}__{kernel}.json.gz'
    scratch.parent.mkdir(parents=True, exist_ok=True)
    scratch.write_bytes(gzip.compress(raw, mtime=0))
    report['statisticsTable'] = dict(path=str(scratch), sha256=hashlib.sha256(raw).hexdigest())
    out = C.HERE / 'fits' / tag / f'{name}__{ep}__{kernel}.json'
    C.save(out, report)
    return report


def _render_blurlast(c, fam, p):
    pr = np.stack([F.render(c, fam, F.expand(fam, p), T=Tc) for Tc in c.Tc], -1)
    return np.stack([pr[:, i, i] for i in range(3)], -1) if pr.ndim == 3 else pr


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('family')
    ap.add_argument('endpoint')
    ap.add_argument('--kernel', default='n')
    ap.add_argument('--scales', default='2,1')
    ap.add_argument('--tag', default='main')
    ap.add_argument('--units', default=None)
    a = ap.parse_args()
    r = run(a.family, a.endpoint, a.kernel, tuple(int(s) for s in a.scales.split(',')), a.tag, units=a.units)
    for key in ('ls', 'minimax'):
        v = r[key]
        print(f"{a.family} {a.endpoint} {key}: {v['params']} lam {v['lam']} failures {v['failures']} "
              f"worst cal {v['calibration']['worstMeasured']:.2f} @ {v['calibration']['worstAt']} "
              f"val {v['validation']['worstMeasured']:.2f} pooled cal {v['calibration']['pooledRms']:.3f}")
    print('seconds', r['seconds'], 'survives', r['survives'])
