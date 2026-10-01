"""W42 G2 step 2, part 5: the k ladder (declaration `kNesting`): LT with one k for all four endpoints (k@global, 5
parameters) and one per scheme (k@scheme, 6), fitted jointly on every endpoint's calibration cells; k@endpoint is
fits/<tag>/LT__<ep>__n.json and k2@endpoint is LT-2k's. Same cells, mask, search and scoring as fit_family.py.

    python3.12 -B nesting.py LEVEL [TAG]     -> fits/<tag>/LT@<level>__all__n.json
"""
import gzip
import hashlib
import json
import sys
import time

import common as C
import fit_family as FF

F, FA, PC = C.F, C.PC.FA, C.PC


def run(level, tag='main'):
    t0 = time.time()
    fam = F.Family()
    cal, val = [], []
    for ep in C.EPS:
        a, b = FF.build('LT', ep, 'n', (2, 1))
        cal += a
        val += b
    fitcells = [c for c in cal if c.letter != 'A']
    prob = C.ProblemRGB(fitcells, fam, list(FA.LAYOUTS[level]), PC.bounds_for('LT'))
    res = prob.fit(PC.starts_for('LT', 'light-rest', len(prob.keys)))
    t_ls = time.time() - t0
    mm_x, mm_lams, mm_s, mm_s0, nfev = FF.minimax(prob, res['xvec'], res['lam'], 240)
    report = dict(schema='w42-g2-step2-fit-1', family='LT', level=level, endpoint='all', kernel='n',
                  cells=dict(fit=len(fitcells), calibration=len(cal), validation=len(val)),
                  seconds=dict(ls=round(t_ls), minimax=round(time.time() - t0 - t_ls)))
    full = {}
    for key, (x, lams) in (('ls', (res['xvec'], res['lam'])), ('minimax', (mm_x, mm_lams))):
        params = {k: float(v) for k, v in zip([f'{kk[0][0]}@{kk[0][1]}' for kk in prob.keys], x)}
        per_ep = {}
        tabs = {}
        for ep in C.EPS:
            ce = [c for c in cal if c.ep == ep]
            ve = [c for c in val if c.ep == ep]
            pc = [C.render_rgb(c, fam, dict(prob.params_for(x, c), lam=lams[ep])) for c in ce]
            pv = [C.render_rgb(c, fam, dict(prob.params_for(x, c), lam=lams[ep])) for c in ve]
            sc, sv = C.summarize(ce, pc), C.summarize(ve, pv)
            per_ep[ep] = dict(calibration={k: v for k, v in sc.items() if k != 'failed'},
                              validation={k: v for k, v in sv.items() if k != 'failed'},
                              failures=sc['failures'] + sv['failures'])
            tabs[ep] = dict(calibration=FF.stat_table(ce, pc), validation=FF.stat_table(ve, pv))
        report[key] = dict(params=params, lam={k: float(v) for k, v in lams.items()}, endpoints=per_ep)
        full[key] = tabs
    report['minimax']['objective'] = dict(start=mm_s0, end=mm_s, nfev=nfev)
    raw = json.dumps(dict(report=report, statistics=full), sort_keys=True, default=float).encode()
    scratch = C.SCRATCH / 'fits' / tag / f'LT@{level}__all__n.json.gz'
    scratch.parent.mkdir(parents=True, exist_ok=True)
    scratch.write_bytes(gzip.compress(raw, mtime=0))
    report['statisticsTable'] = dict(path=str(scratch), sha256=hashlib.sha256(raw).hexdigest())
    C.save(C.HERE / 'fits' / tag / f'LT@{level}__all__n.json', report)
    print(level, report['ls']['params'], report['ls']['lam'], report['minimax']['params'], report['seconds'])
    return report


if __name__ == '__main__':
    run(*sys.argv[1:])
