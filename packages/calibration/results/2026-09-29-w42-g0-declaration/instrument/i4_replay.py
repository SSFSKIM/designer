"""W42 G0 instrument, the review of b151aff4, finding I-4: were outputs produced while the shared blur store was
keyed by id(cell) contaminated by a stale blur? Evidence, not argument: every cited proof-2 row (the rows
resolution.py selects, including the fallback table), every rejected-null row (proof2_nulls.json, and the 2x-only
first run the README cites) and the capture-floor check are re-evaluated at their RECORDED points, with no refit,
by the code and bed pin that produced them, the only change being the store's key: a never-reused token.

The replay roots are scratch extracts under /tmp/w42fix/i4-<commit>-<pin>/ (the instrument folder of the producing
commit by `git archive`, the canonical scenes.json of that commit, and the recorded pin's bed files beside it, their
SHA-256 written into bed.py's PINS). For the commits before 04163eec the key in forward.py is patched to a token;
a489cc02's code already carries it. A row's producing commit is the first commit whose JSON holds it; its pin is the
one it records (rows without a pin ran on 5ba68aeb, as proof2_separation.py states), its kernel the one it records
(none = the narrow support, before ruling 3).

Per row: the truth is re-rendered and re-quantised exactly as the proof did (same seeds), the fitted family is
evaluated at the recorded least-squares point (lam re-derived by the same golden search, and compared with the
recorded lam) and at the recorded minimax point, and ls_pooled, ls_max_cell, s_ls and s are compared with the record.

Usage:
  python3.12 i4_replay.py plan                         -> /tmp/w42fix/i4-jobs.json (the jobs, grouped by root, kernel)
  python3.12 i4_replay.py run ROOT KERNEL OUT          (run from anywhere; one process, W42_POOL workers)
  python3.12 i4_replay.py report                       -> i4_replay.json / i4_replay.txt beside this file
"""
import inspect
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REL = 'packages/calibration/results/2026-09-29-w42-g0-declaration/instrument'
SCRATCH = '/tmp/w42fix'
PRODUCERS = ['7efe4ce8', '9c1623b4', 'be700896', '04163eec', 'a489cc02']
CODE_OF = {'7efe4ce8': '7efe4ce8', '9c1623b4': '9c1623b4', 'be700896': 'be700896', '04163eec': 'a489cc02',
           'a489cc02': 'a489cc02'}


def _git_json(commit, name):
    out = subprocess.run(['git', '-C', HERE, 'show', f'{commit}:{REL}/{name}'], capture_output=True)
    return json.loads(out.stdout) if out.returncode == 0 else None


def _pair_key(r):
    return (r['truth'], r['fit'], r['ep'], r['whole'], r.get('bed', '5ba68aeb'), r.get('kernel'), round(r['s'], 9),
            round(r['ls_pooled'], 9))


def _null_key(r):
    return (r['fit'], r['ep'], round(r['pooled'], 9))


def _first(name, key):
    first = {}
    for c in PRODUCERS:
        d = _git_json(c, name)
        if d is None:
            continue
        rows = d['pairs'] if isinstance(d, dict) else d
        for r in rows:
            first.setdefault(key(r), c)
    return first


def _kernel(r):
    k = r.get('kernel')
    return 'w' if k == 'w' else 'n'


def plan():
    head = json.load(open(os.path.join(HERE, 'proof2_separation.json')))['pairs']
    # resolution.py's selection: the best row per (truth, fit, endpoint), active W-support rows apart
    order = {'5ba68aeb': 0, '07b45391': 1, '5d719b60': 2, '764217e1': 3}
    rank = lambda r: (order.get(r.get('bed', '5ba68aeb'), 9), bool(r.get('whole')))
    best, fallback = {}, {}
    for i, r in enumerate(head):
        key = (r['truth'], r['fit'], r['ep'])
        target = fallback if (r['ep'].endswith('rest') and r.get('kernel') == 'w') else best
        if key not in target or rank(r) > rank(head[target[key]]):
            target[key] = i
    sel = sorted(set(best.values()) | set(fallback.values()))
    first = _first('proof2_separation.json', _pair_key)
    jobs = []
    for i in sel:
        r = head[i]
        c = first[_pair_key(r)]
        jobs.append(dict(kind='pair', index=i, producer=c, root=f"{CODE_OF[c]}-{r.get('bed', '5ba68aeb')}",
                         kernel=_kernel(r), row=r))
    for name, kind in (('proof2_nulls.json', 'null'), ('proof2_nulls-2xonly.json', 'null2x')):
        first = _first(name, _null_key)
        for i, r in enumerate(json.load(open(os.path.join(HERE, name)))):
            c = first[_null_key(r)]
            jobs.append(dict(kind=kind, index=i, producer=c, root=f"{CODE_OF[c]}-{r['bed']}", kernel=_kernel(r),
                             row=r))
    for i, r in enumerate(json.load(open(os.path.join(HERE, 'proof2_floor_check.json')))):
        jobs.append(dict(kind='floor', index=i, producer='a489cc02', root=f"a489cc02-{r['bed']}", kernel='n', row=r))
    json.dump(jobs, open(f'{SCRATCH}/i4-jobs.json', 'w'), indent=1, default=float)
    from collections import Counter
    print(Counter((j['root'], j['kernel'], j['kind']) for j in jobs))


# ---------------------------------------------------------------- the replay (runs inside a root)

def _setup(root, kernel):
    os.environ['W42_KERNEL'] = kernel
    d = os.path.join(SCRATCH, f'i4-{root}', REL)
    os.chdir(d)
    sys.path.insert(0, d)


def _cells(bed, ep, scales, letters, kernel):
    kw = {'kernel': kernel} if 'kernel' in inspect.signature(bed.cells).parameters else {}
    out = []
    for s in scales:
        out += bed.cells(ep, s, letters=letters, **kw)
    return out


def _close(a, b):
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def replay(job):
    import numpy as np
    import bed
    import families as FA
    import fitting as Fi
    import forward as F
    import proof_common as PC
    t0 = time.time()
    r, kind, K = job['row'], job['kind'], job['kernel']
    ep = r['ep']
    out = dict(kind=kind, index=job['index'], producer=job['producer'], root=job['root'], kernel=K)
    if kind == 'pair':
        whole = r['whole']
        cells = _cells(bed, ep, (2, 1) if whole else (2,), r['letters'], K)
        tfam, ffam = FA.FAMILIES[r['truth']][0], FA.FAMILIES[r['fit']][0]
        exact = PC.render_truth(cells, tfam, PC.truth(r['truth'], ep))
        prob = Fi.Problem(cells, ffam, PC.layout_for(r['fit'], ep), PC.bounds_for(r['fit']))
        keep = {c.id for c in prob.cells}
        exact = [e for c, e in zip(cells, exact) if c.id in keep]
        cells = prob.cells
        tstats = PC.stats_list(cells, exact)
        names = [f'{k[0][0]}@{k[0][1]}' for k in prob.keys]
        xls = np.array([r['ls_x'][n] for n in names])
        lams, mses = prob.inner(xls)
        pooled, mx = float(np.sqrt(np.mean(mses))), float(np.sqrt(np.max(mses)))
        s_ls, where_ls = PC.survival_misfit(cells, prob.predictions(xls, r['ls_lam']), tstats)
        xmm = np.array([r['mm_x'][n] for n in names])
        s, where = PC.survival_misfit(cells, prob.predictions(xmm, r['mm_lam']), tstats)
        rec = dict(n_cells=r['n_cells'], ls_pooled=r['ls_pooled'], ls_max_cell=r['ls_max_cell'], s_ls=r['s_ls'],
                   s=r['s'], where=r['where'], lam=r['ls_lam'])
        got = dict(n_cells=len(cells), ls_pooled=pooled, ls_max_cell=mx, s_ls=s_ls, s=s, where=where, lam=lams)
        label = f"{r['truth']} -> {r['fit']} {ep}{' whole' if whole else ''} {r.get('bed', '5ba68aeb')} {K}"
    else:
        null = r.get('fit')
        if kind == 'floor':
            letters = ("B'",) if r['scope'].startswith('fine') else ('B', "B'", 'C', 'D')
            cells = [c for c in _cells(bed, ep, (2, 1), letters, K)
                     if not r['scope'].startswith('fine') or c.geometry.get('pitch', 99) <= 8]
            null, x = 'null-boxfloor', r['k']
        elif kind == 'null':
            cells = _cells(bed, ep, (2, 1), ('B', "B'", 'C', 'D'), K)
            x = r['x']
        else:   # the 2x-only first run: its cell set is not recorded; take the first that reproduces n_cells
            x, cells = r['x'], None
            for letters, scales in ((('B', "B'", 'C', 'D'), (2,)), (PC.LETTERS[null], (2,)),
                                    (PC.LETTERS[null], (2, 1))):
                cs = _cells(bed, ep, scales, letters, K)
                if len(cs) == r['n_cells']:
                    cells = cs
                    out['cell_set'] = f"{'/'.join(letters)} at {'+'.join(f'{s}x' for s in scales)}"
                    break
            if cells is None:
                out.update(label=f"{null} {ep} (2x only)", status='NOT REPLAYABLE',
                           note=f"no letter set reproduces the recorded {r['n_cells']} cells")
                return out
        PC.render_truth(cells, F.Family(), PC.truth('LT', ep))
        prob = Fi.Problem(cells, FA.FAMILIES[null][0], PC.layout_for(null, ep), PC.bounds_for(null))
        names = [f'{k[0][0]}@{k[0][1]}' for k in prob.keys]
        xv = np.array([x[n] for n in names])
        lams, mses = prob.inner(xv)
        rms = np.sqrt(np.array(mses))
        rec = dict(n_cells=r['n_cells'], pooled=r['pooled'], max_cell=r['max_cell'])
        got = dict(n_cells=len(prob.cells), pooled=float(np.sqrt(np.mean(mses))), max_cell=float(rms.max()))
        if 'lam' in r:
            rec['lam'], got['lam'] = r['lam'], lams
        if kind == 'floor':
            rec['worst'] = r['worst']
            got['worst'] = f'{ep}|' + prob.cells[int(np.argmax(rms))].id
        label = f"{null} {ep} {r.get('scope', '')} {r.get('bed')} {K}{' (2x only)' if kind == 'null2x' else ''}"
    diffs = {}
    for k, v in rec.items():
        g = got[k]
        if isinstance(v, dict):
            d = max(abs(v[e] - g[e]) for e in v)
            if d > 1e-9:
                diffs[k] = d
        elif isinstance(v, str):
            if v != g:
                diffs[k] = f'{v} != {g}'
        elif not _close(float(v), float(g)):
            diffs[k] = float(g) - float(v)
    out.update(label=label, recorded=rec, replayed=got, diffs=diffs,
               status='EXACT' if not diffs else 'DIFFERS', seconds=time.time() - t0)
    return out


def run(root, kernel, dest):
    _setup(root, kernel)
    from multiprocessing import Pool
    jobs = [j for j in json.load(open(f'{SCRATCH}/i4-jobs.json')) if j['root'] == root and j['kernel'] == kernel]
    only = os.environ.get('I4_ONLY')       # 'kind:index,...' (the no-cache control's rows)
    if only:
        want = {tuple(x.split(':')) for x in only.split(',')}
        jobs = [j for j in jobs if (j['kind'], str(j['index'])) in want]
    done = {}
    if os.path.exists(dest):
        done = {(o['kind'], o['index']): o for o in json.load(open(dest))}
    todo = [j for j in jobs if (j['kind'], j['index']) not in done]
    res = list(done.values())
    with Pool(int(os.environ.get('W42_POOL', '2'))) as pool:
        for o in pool.imap_unordered(_run_one, [(root, kernel, j) for j in todo]):
            res.append(o)
            print(f"{o['status']:8s} {o['label']} {o.get('diffs', '')} {o.get('seconds', 0):.0f}s", flush=True)
            json.dump(res, open(dest, 'w'), indent=1, default=float)


def _run_one(args):
    root, kernel, job = args
    if os.getcwd() != os.path.join(SCRATCH, f'i4-{root}', REL):
        _setup(root, kernel)
    if os.environ.get('I4_NOCACHE') == '1':
        # the control: no blur is ever reused, so every blur is computed at its own width (the store's key rounds
        # a width to 1e-4 device px, so a cached blur serves every width within 5e-5 of the one computed first)
        import forward as F
        F.BLUR_CACHE_BYTES = 0
    return replay(job)


# ---------------------------------------------------------------- the report

TOL_ROUNDING = 1e-3     # codes; see the classification below


def classify(o):
    """EXACT: every compared value within 1e-9 (relative). ROUNDING: every numeric difference at most 1e-3 code
    (1e-4 in lam), cell counts equal: the size of the store's own width rounding (a blur computed at one width
    serves every width within 5e-5 device px), which the no-cache control reproduces; a stale blur of another
    backdrop moves a region statistic by codes. Anything else is MOVED."""
    if o.get('status') == 'NOT REPLAYABLE':
        return 'NOT REPLAYABLE'
    if not o['diffs']:
        return 'EXACT'
    num = {k: v for k, v in o['diffs'].items() if isinstance(v, float)}
    if 'n_cells' in o['diffs']:
        return 'MOVED'
    lam_ok = abs(o['diffs'].get('lam', 0.0)) <= 1e-4
    if all(abs(v) <= TOL_ROUNDING for k, v in num.items() if k != 'lam') and lam_ok:
        return 'ROUNDING'
    return 'MOVED'


def report():
    import glob
    res = []
    for f in sorted(glob.glob(f'{SCRATCH}/i4-out/*-[nw].json')):
        if not os.path.basename(f).startswith('control-'):
            res += json.load(open(f))
    ctrl = {}
    for f in sorted(glob.glob(f'{SCRATCH}/i4-out/control-*.json')):
        for o in json.load(open(f)):
            ctrl[(o['kind'], o['index'])] = o
    jobs = json.load(open(f'{SCRATCH}/i4-jobs.json'))
    retried = {(j['kind'], j['index']) for j in jobs if j.get('retry_of')}
    rows = []
    for o in res:
        key = (o['kind'], o['index'])
        o['class'] = classify(o)
        if key in retried and o['root'].endswith('5ba68aeb') and 'n_cells' in o.get('diffs', {}):
            o['class'] = 'SUPERSEDED BY THE 07b45391 RETRY (the row carries no pin and ran on 07b45391)'
        if key in ctrl:
            c = ctrl[key]
            o['control_nocache'] = dict(replayed=c['replayed'],
                                        vs_recorded=c['diffs'], vs_replay={
                                            k: (c['replayed'][k] - o['replayed'][k]) for k in o['replayed']
                                            if isinstance(o['replayed'][k], float)})
        rows.append(o)
    rows.sort(key=lambda o: (o['kind'], o['producer'], o['index'], o['root']))
    readers = json.load(open(f'{SCRATCH}/i4-out/readers.json')) if os.path.exists(f'{SCRATCH}/i4-out/readers.json') else []
    json.dump(dict(rows=rows, readers=readers), open(os.path.join(HERE, 'i4_replay.json'), 'w'), indent=1,
              default=float)
    from collections import Counter
    L = ['W42 G0 instrument, finding I-4: outputs of the id(cell)-keyed blur store replayed with a never-reused token',
         '(i4_replay.py, i4_readers.py). Rows: re-evaluated at their RECORDED points, no refit, by the code and bed pin',
         'that produced them. Classes: EXACT (1e-9 relative); ROUNDING (<= 1e-3 code, lam <= 1e-4: the store\'s own',
         'width rounding, see the no-cache control); MOVED (anything else).', '']
    cnt = Counter((o['kind'], o['class']) for o in rows)
    L.append('summary: ' + '; '.join(f'{k[0]} {k[1]}: {v}' for k, v in sorted(cnt.items())))
    mx = {}
    for o in rows:
        for k, v in o.get('diffs', {}).items():
            if isinstance(v, float) and 'SUPERSEDED' not in o['class']:
                mx[k] = max(mx.get(k, 0.0), abs(v))
    L.append('largest |replayed - recorded| over rows not superseded: ' + ', '.join(f'{k} {v:.3g}' for k, v in mx.items()))
    L.append('')
    for o in rows:
        d = ', '.join(f'{k} {v:+.3g}' if isinstance(v, float) else f'{k} {v}' for k, v in o.get('diffs', {}).items())
        rec = o.get('recorded', {})
        main = ' '.join(f'{k} {rec[k]:.4f}' for k in ('ls_pooled', 's_ls', 's', 'pooled', 'max_cell') if k in rec)
        L.append(f"{o['class'][:14]:14s} {o['kind']:6s} {o['producer']} {o['label']}: {main}"
                 + (f' | diff {d}' if d else '')
                 + (f" | no-cache control vs replay: {', '.join(f'{k} {v:+.2g}' for k, v in o['control_nocache']['vs_replay'].items())}"
                    if 'control_nocache' in o else ''))
    if readers:
        L += ['', 'READERS: regenerated JSON against the committed JSON (numeric leaves; differ = beyond 1e-9 relative)']
        for r in readers:
            L.append(f"  {r['commit']} {r['file']:44s} {r['n']:6d} numbers, {r['differ']:4d} differ, max {r['max']:.3g}"
                     + (f" at {r['where']}" if r['where'] else '')
                     + (f"; structure {r['structure'][:3]}" if r['structure'] else '')
                     + (f"; other {r['other'][:3]}" if r['other'] else ''))
    open(os.path.join(HERE, 'i4_replay.txt'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L[:8]))


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'plan':
        plan()
    elif cmd == 'run':
        run(*sys.argv[2:5])
    elif cmd == 'report':
        report()
