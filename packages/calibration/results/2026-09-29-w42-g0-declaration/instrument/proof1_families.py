"""W42 G0 proof 1, the family fitters (charter clause 2): on synthetic renders of every declared family through
native T (the memo C stand-in), quantised +-0.5, on the bed's geometries, the fitter recovers the known
parameters to the tolerances declared in tolerances.json before this proof ran.

Parts:
  A  every non-null family, per endpoint: render at its truth, fit the same family, compare;
  B  the three nested levels of k (and the pose-shared rival) on all four endpoints together: a global-k
     truth recovered at every level, and memo E's per-endpoint k read at every level;
  C  LT's survival resolution: how far k and lam must move before some region statistic moves by one code
     (lam re-fitted by least squares), i.e. the smallest change clause 6 can see on this bed;
  D  the engine's own numerical floor: the narrow interpolation against a dense reference, and clause 7's
     uniform invariance for every family.

Usage: python3.12 proof1_families.py [A|B|C|D ...]   (default: all). Writes proof1_families.json / .txt.
"""
import json
import sys
import time
from multiprocessing import Pool

import numpy as np

import bed
import families as FA
import fitting as Fi
import forward as F
import proof_common as PC

TOL = json.load(open('tolerances.json'))
EPS = F.ENDPOINTS
OUT = {}


def log(*a):
    print(*a, flush=True)


def part_a_one(args):
    name, ep = args
    fam = FA.FAMILIES[name][0]
    if name.startswith('LT+bleed') and ep.endswith('inactive'):
        return dict(family=name, ep=ep, skipped='the bleed is declared zero when receded (identical to LT)')
    if name == 'knee-luma':
        cells = PC.cells_for(name, ep)
    elif name == 'LT':
        cells = PC.cells_for(name, ep, scales=(2, 1))
    else:
        cells = PC.cells_for(name, ep)
    p = PC.truth(name, ep)
    t0 = time.time()
    PC.render_truth(cells, fam, p)
    lay = PC.layout_for(name, ep)
    prob = Fi.Problem(cells, fam, lay, PC.bounds_for(name))
    res = prob.fit(PC.starts_for(name, ep, len(prob.keys)))
    rec = {}
    for key, v in res['x'].items():
        pn = key.split('@')[0]
        tv = p.get(pn, p.get('k')) if pn in ('k', 'k_n', 'k_w') else p[pn]
        rec[pn] = dict(truth=tv, read=v, err=v - tv)
    rec['lam'] = dict(truth=p['lam'], read=res['lam'][ep], err=res['lam'][ep] - p['lam'])
    return dict(family=name, ep=ep, n_cells=len(prob.cells), excluded=prob.excluded, pooled=res['pooled'],
                max_cell=res['max_cell'], recovered=rec, seconds=time.time() - t0)


def tol_for(pn):
    t = TOL['proof1_family_recovery']
    if pn in ('k',):
        return t['k (every nesting level: global, per scheme, per endpoint)']['abs']
    if pn in ('k_n', 'k_w'):
        return t['k_n, k_w (LT-2k)']['abs']
    if pn == 'lam':
        return t['lam (per endpoint, every family)']['abs']
    if pn.startswith('sn_'):
        return t['sigma_n(span) ordinates (free Gaussian rival)']['abs_pt']
    return {'mu': t['mu (W on the rounded shape, margin)']['abs_pt'],
            'a': t['tails: a (weight of the second Gaussian)']['abs'],
            's2': t['tails: sigma2 (pt)']['abs_pt'], 'sk': t['K2: sk (the knee fill\'s width, pt)']['abs_pt'],
            'k_b': t['LT + bleed (own scale): k_b']['abs']}[pn]


def part_a(pool):
    jobs = [(n, ep) for n, (_, _, _, _, status) in FA.FAMILIES.items() if status != 'null' for ep in EPS]
    rows = pool.map(part_a_one, jobs, chunksize=1)
    floor = TOL['synthetic_render']['fit_reaches_floor_if_pooled_rms_at_most']
    for r in rows:
        if 'skipped' in r:
            continue
        ok = r['pooled'] <= floor
        for pn, v in r['recovered'].items():
            v['tol'] = tol_for(pn)
            v['ok'] = abs(v['err']) <= v['tol']
            ok &= v['ok']
        r['pass'] = bool(ok)
    OUT['A'] = rows


def nesting_cells(k_by_ep, lam_by_ep, fam=None, p_extra=None, scales=(2,)):
    cells = []
    for ep in EPS:
        cs = []
        for s in scales:
            cs += bed.cells(ep, s, letters=("B'", 'C', 'B'))
        p = {'k': k_by_ep[ep], 'lam': lam_by_ep[ep], **(p_extra or {})}
        PC.render_truth(cs, fam or F.Family(), p)
        cells += cs
    return cells


def fit_level(cells, level):
    """Fit LT at a nesting level. Scopes that do not couple endpoints decouple into independent groups (one per
    scheme, or one per endpoint), which is the same optimum at a fraction of the cost."""
    scope = FA.LAYOUTS[level][0][1]
    key = {'global': lambda ep: 'all', 'scheme': lambda ep: ep.split('-')[0], 'endpoint': lambda ep: ep}[scope]
    groups = {}
    for c in cells:
        groups.setdefault(key(c.ep), []).append(c)
    x, lams, per = {}, {}, {}
    for g, cs in groups.items():
        prob = Fi.Problem(cs, F.Family(), FA.LAYOUTS[level], PC.bounds_for('LT'))
        r = prob.fit(PC.starts_for('LT', 'light-rest', len(prob.keys)))
        x.update(r['x'])
        lams.update(r['lam'])
        per.update(r['per_cell'])
    rms_ep = {ep: float(np.sqrt(np.mean([v ** 2 for k, v in per.items() if k.startswith(ep + '|')]))) for ep in EPS}
    n_params = len(x) + len(lams)
    return dict(level=level, n_params=n_params, x=x, lam=lams, pooled=float(np.sqrt(np.mean([v ** 2 for v in per.values()]))),
                pooled_by_ep=rms_ep, max_cell=max(per.values()))


def part_b_one(args):
    truth_name, level = args
    cells = []
    for ep in EPS:
        cs = bed.cells(ep, 2, letters=("B'", 'C', 'B'))
        if truth_name == 'global':
            p = {'k': 2.05, 'lam': FA.TRUTH_LAM[ep]}
        elif truth_name == 'memoE':
            p = {'k': FA.TRUTH_K[ep], 'lam': FA.TRUTH_LAM[ep]}
        else:
            p = {'k_n': 1.75, 'k_w': 2.10, 'lam': FA.TRUTH_LAM[ep]}
        PC.render_truth(cs, F.Family(), p)
        cells += cs
    r = fit_level(cells, level)
    r['truth'] = truth_name
    return r


def part_b(pool):
    jobs = [(t, lv) for t in ('global', 'memoE', 'LT-2k') for lv in ('k@global', 'k@scheme', 'k@endpoint',
                                                                   'k2@endpoint')]
    OUT['B'] = pool.map(part_b_one, jobs, chunksize=1)


def part_c_one(ep):
    """Survival resolution of LT's k and lam on the whole 2x bed of one endpoint."""
    cells = PC.cells_for('LT', ep, scales=(2,))
    p = PC.truth('LT', ep)
    exact = PC.render_truth(cells, F.Family(), p)
    prob = Fi.Problem(cells, F.Family(), FA.LAYOUTS['k@endpoint'], PC.bounds_for('LT'))
    keep = {c.id for c in prob.cells}
    exact = [e for c, e in zip(cells, exact) if c.id in keep]
    cells = prob.cells
    st = PC.stats_list(cells, exact)

    def misfit_k(dk):
        x = np.array([p['k'] + dk])
        lams, _ = prob.inner(x)
        preds = []
        for c in cells:
            q = prob.params_for(x, c)
            q['lam'] = lams[ep]
            preds.append(F.render(c, F.Family(), q))
        return PC.survival_misfit(cells, preds, st)[0], lams[ep]

    def misfit_lam(dl):
        preds = [F.render(c, F.Family(), F.expand(F.Family(), dict(p, lam=p['lam'] + dl))) for c in cells]
        return PC.survival_misfit(cells, preds, st)[0]

    def solve(f, sign, hi):
        lo_, hi_ = 0.0, hi
        while f(sign * hi_) < 1.0 and hi_ < 8 * hi:
            hi_ *= 2
        for _ in range(12):
            mid = 0.5 * (lo_ + hi_)
            if f(sign * mid) < 1.0:
                lo_ = mid
            else:
                hi_ = mid
        return 0.5 * (lo_ + hi_)
    fk = lambda d: misfit_k(d)[0]
    out = dict(ep=ep, n_cells=len(cells))
    out['k_up'] = solve(fk, +1, 0.05)
    out['k_down'] = solve(fk, -1, 0.05)
    out['lam_up'] = solve(misfit_lam, +1, 0.05)
    out['lam_down'] = solve(misfit_lam, -1, 0.05)
    return out


def part_c(pool):
    OUT['C'] = pool.map(part_c_one, EPS, chunksize=1)


def part_e_one(job):
    """E: on the bed at its final pin (07b45391: the s = 32 receded rrect-sm rows added), (i) LT recovered on the
    receded endpoints with the new rows in; (ii) memo E's per-endpoint k read at the global and per-scheme
    levels, scored in REGION STATISTICS (the survival sense), not only pixel rms."""
    kind, arg = job
    if kind == 'lt':
        r = part_a_one(('LT', arg))
        r['bed'] = bed.BED_COMMIT[:8]
        return dict(kind='lt', **r)
    level = arg
    cells, exact = [], []
    for ep in EPS:
        cs = bed.cells(ep, 2, letters=("B'", 'C', 'B'))
        exact += PC.render_truth(cs, F.Family(), {'k': FA.TRUTH_K[ep], 'lam': FA.TRUTH_LAM[ep]})
        cells += cs
    r = fit_level(cells, level)
    st = PC.stats_list(cells, exact)
    preds = []
    for c in cells:
        key = {'k@global': 'k@all', 'k@scheme': f"k@{c.ep.split('-')[0]}", 'k@endpoint': f'k@{c.ep}'}[level]
        preds.append(F.render(c, F.Family(), F.expand(F.Family(), {'k': r['x'][key], 'lam': r['lam'][c.ep]})))
    s_all, where = PC.survival_misfit(cells, preds, st)
    per_ep = {}
    for ep in EPS:
        ix = [i for i, c in enumerate(cells) if c.ep == ep]
        per_ep[ep] = PC.survival_misfit([cells[i] for i in ix], [preds[i] for i in ix], [st[i] for i in ix])[0]
    return dict(kind='nesting-regions', level=level, x=r['x'], lam=r['lam'], pooled=r['pooled'], s_ls=s_all,
                where=where, s_ls_by_ep=per_ep, bed=bed.BED_COMMIT[:8])


def part_e(pool):
    jobs = [('lt', 'light-inactive'), ('lt', 'dark-inactive'), ('nest', 'k@global'), ('nest', 'k@scheme'),
            ('nest', 'k@endpoint')]
    OUT['E'] = pool.map(part_e_one, jobs, chunksize=1)


def part_d():
    rows = []
    for ep in ('light-rest', 'dark-rest'):
        for c in bed.cells(ep, 2) + bed.cells(ep, 1):
            if c.span <= 64:
                continue
            a = F.render(c, F.Family(), {'k_n': 2.0, 'k_w': 2.0, 'lam': 0.8})
            old = F.NARROW_STEP
            F.NARROW_STEP = (0.01, 0.002)
            c._cache = {}
            b = F.render(c, F.Family(), {'k_n': 2.0, 'k_w': 2.0, 'lam': 0.8})
            F.NARROW_STEP = old
            d = a - b
            rows.append(dict(ep=ep, cell=c.id, rms=float(np.sqrt(np.mean(d ** 2))), max=float(np.abs(d).max())))
    fams = {}
    for n, (fam, *_r) in FA.FAMILIES.items():
        p = PC.truth(n if n in FA.TRUTH_EXTRA or n == 'free-sn' else 'LT', 'light-rest')
        if n == 'free-sn':
            p.update(PC.truth('free-sn', 'light-inactive'))
        if n == 'LT-2k':
            p = dict(p, k=2.0)
        fams[n] = (fam, p)
    inv = F.uniform_invariance(fams, levels=(0, 64, 128, 192, 255))
    fast = []
    for ep in EPS:
        for c in bed.cells(ep, 2) + bed.cells(ep, 1):
            q = F.expand(F.Family(), {'k': 2.0, 'lam': 0.85})
            a = F.render(c, F.Family(), q)
            old = F.FAST_FROM_DEV
            F.FAST_FROM_DEV = 0
            c._cache = {}
            b = F.render(c, F.Family(), q)
            F.FAST_FROM_DEV = old
            d = np.abs(a - b)
            fast.append(dict(ep=ep, cell=c.id, rms=float(np.sqrt(np.mean(d ** 2))), max=float(d.max())))
    excl = {f'{s}x {ep}': bed.refraction_exclusions(ep, s) for ep in EPS for s in (2, 1)}
    OUT['D'] = dict(interpolation=dict(worst_rms=max(r['rms'] for r in rows), worst_max=max(r['max'] for r in rows),
                                       median_rms=float(np.median([r['rms'] for r in rows])), n=len(rows)),
                    uniform_invariance=inv,
                    decimated_wide_blur=dict(worst_max=max(r['max'] for r in fast), worst_rms=max(r['rms'] for r in fast),
                                             n=len(fast)),
                    refraction_exclusions=excl,
                    active_d_in={s: F.band_d_in(s) for s in (44, 64, 80, 96, 112, 128, 160)})


def write():
    json.dump(OUT, open('proof1_families.json', 'w'), indent=1, default=float)
    L = ['W42 G0 proof 1, family fitters (synthetic, memo C T stand-in, quantised +-0.5)', '']
    if 'A' in OUT:
        L.append('A  recovery per family and endpoint: param truth -> read (err; tol) ... pooled rms')
        for r in OUT['A']:
            if 'skipped' in r:
                L.append(f"  {r['family']:13s} {r['ep']:15s} skipped: {r['skipped']}")
                continue
            parts = [f"{pn} {v['truth']:.3f}->{v['read']:.3f} ({v['err']:+.4f}; {v['tol']})"
                     for pn, v in r['recovered'].items()]
            L.append(f"  {r['family']:13s} {r['ep']:15s} {'PASS' if r['pass'] else 'FAIL'} pooled {r['pooled']:.3f} "
                     f"max {r['max_cell']:.3f} n {r['n_cells']} | " + ' | '.join(parts))
    if 'B' in OUT:
        L += ['', 'B  k nesting (all four endpoints together): truth, level -> k read, pooled (per endpoint)']
        for r in OUT['B']:
            ks = ', '.join(f'{k} {v:.4f}' for k, v in r['x'].items())
            pe = ' '.join(f'{e[:1]}{e.split("-")[1][:1]} {v:.3f}' for e, v in r['pooled_by_ep'].items())
            L.append(f"  truth {r['truth']:7s} {r['level']:12s} params {r['n_params']:2d} pooled {r['pooled']:.3f} "
                     f"max {r['max_cell']:.3f} [{pe}] | {ks}")
    if 'C' in OUT:
        L += ['', 'C  LT survival resolution (the change that moves some region statistic by one code)']
        for r in OUT['C']:
            L.append(f"  {r['ep']:15s} k +{r['k_up']:.4f} / -{r['k_down']:.4f}   lam +{r['lam_up']:.4f} / "
                     f"-{r['lam_down']:.4f}   ({r['n_cells']} cells)")
    if 'D' in OUT:
        d = OUT['D']
        L += ['', f"D  narrow interpolation vs dense reference: worst rms {d['interpolation']['worst_rms']:.4f}, "
                  f"worst max {d['interpolation']['worst_max']:.4f}, median rms {d['interpolation']['median_rms']:.4f} "
                  f"over {d['interpolation']['n']} depth-graded cells",
              '   uniform invariance (max |y - T(g)| before rounding): ' +
              ', '.join(f'{n} {v:.1e}' for n, v in d['uniform_invariance'])]
        if 'decimated_wide_blur' in d:
            w = d['decimated_wide_blur']
            L.append(f"   decimated wide blur vs direct: worst max {w['worst_max']:.4f}, worst rms {w['worst_rms']:.4f} "
                     f"over {w['n']} cells (every pass)")
            L.append('   active deep mask d_in (pt) by span: ' + ', '.join(f'{k} {v:.1f}' for k, v in d['active_d_in'].items()))
            L.append('   refraction exclusions (active; the parent ruling):')
            for k, v in d['refraction_exclusions'].items():
                for cid, why in v.items():
                    L.append(f'     {k}: {cid}: {why}')
    if 'E' in OUT:
        L += ['', 'E  at the final bed pin (w42-g0-bed 07b45391, the s = 32 receded rrect-sm rows in)']
        for r in OUT['E']:
            if r['kind'] == 'lt':
                parts = [f"{pn} {v['truth']:.3f}->{v['read']:.4f} ({v['err']:+.4f})" for pn, v in r['recovered'].items()]
                L.append(f"  LT recovery {r['ep']:15s} pooled {r['pooled']:.3f} max {r['max_cell']:.3f} n {r['n_cells']} | "
                         + ' | '.join(parts))
            else:
                pe = ' '.join(f"{e}:{v:.2f}" for e, v in r['s_ls_by_ep'].items())
                ks = ', '.join(f'{k} {v:.4f}' for k, v in r['x'].items())
                L.append(f"  memo E's per-endpoint k read at {r['level']:11s}: pooled {r['pooled']:.3f}, region-statistic "
                         f"miss at the LS point {r['s_ls']:.2f} [{pe}] at {r['where']} | {ks}")
    open('proof1_families.txt', 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    parts = sys.argv[1:] or ['A', 'B', 'C', 'D']
    try:
        OUT.update(json.load(open('proof1_families.json')))
    except FileNotFoundError:
        pass
    with Pool(2) as pool:
        for part in parts:
            t = time.time()
            if part == 'D':
                part_d()
            else:
                {'A': part_a, 'B': part_b, 'C': part_c, 'E': part_e}[part](pool)
            log(f'part {part} done in {time.time() - t:.0f}s')
            write()
