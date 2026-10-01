"""W42 G2 step 2, part 4: the refraction-order test v3 on Apple's active cells (declaration `refractionOrder`,
`refractionOrderNoCall`; instrument/refraction_order.py and tolerances.json v3_2026-09-30, unchanged).

The test family F (the clause-6 survivor in the endpoint, or LT if none survives) is fitted as the gated fit: both
scales, families A-E, calibration AND validation (bed.cells' default roles, as run_v3 reads them), the narrow mask,
through the per-channel native T (E in RGB with the instrument's own per-channel output). P is its pooled rms over
the fitted cells. S1 = D_tail over the 2x voters; S2 = A_hat, the projection of the voters' luma residuals on F's
own response to the stand-in 8-pt lens before every blur. A statistic is admitted only when P < P* (light S1 0.549,
S2 2.285; dark S1 0.568, S2 1.086). Neither admitted, or both admitted and opposite: UNDECIDED, and Decision Log
5f's two fits decide whether the endpoint may land (analyze.py reads fits/<tag>/<F>__<ep>__{n,w}.json).

    python3.12 -B refraction_v3.py ENDPOINT [FAMILY]     -> refraction/<endpoint>.json
"""
import json
import sys
import time

import numpy as np

import common as C

F, FA, Fi, PC = C.F, C.PC.FA, C.Fi, C.PC
import refraction_order as RO  # noqa: E402

PSTAR = {'light-rest': {'S1': 0.549, 'S2': 2.285}, 'dark-rest': {'S1': 0.568, 'S2': 1.086}}


def projection_rgb(cells, resids, fam, pfit, voters):
    """RO.projection with the per-channel native T (the same regressor and pooling)."""
    num = den = 0.0
    per = []
    for c, e in zip(cells, resids):
        if c.id not in voters or c.letter == 'A':
            continue
        p = pfit(c)
        R = C.render_rgb(RO.with_lens(c, RO.A_REF), fam, p) - C.render_rgb(c, fam, p)
        el, Rl = e @ RO.LUMA, R @ RO.LUMA
        a, b = float(el @ Rl), float(Rl @ Rl)
        num, den = num + a, den + b
        per.append((c.id, a, b))
    A_hat = RO.A_REF * num / den if den > 0 else 0.0
    call = 'BEFORE' if A_hat >= RO.S2_BEFORE else 'AFTER' if A_hat < RO.S2_AFTER else 'undecided'
    top = sorted(per, key=lambda r: -abs(r[1]))[:3]
    return dict(A_hat=A_hat, call=call, n=len(per),
                top_cells=[(cid, RO.A_REF * a / den if den else 0.0) for cid, a, _ in top])


def run(ep, family='LT'):
    t0 = time.time()
    fam = FA.FAMILIES[family][0]
    cells = []
    for sc in (2, 1):
        cells += C.cells(ep, sc, ('calibration', 'validation'), letters=('A', 'B', "B'", 'C', 'D', 'E'),
                         kernel='n')
    prob = C.ProblemRGB(cells, fam, PC.layout_for(family, ep), PC.bounds_for(family))
    res = prob.fit(PC.starts_for(family, ep, len(prob.keys)))
    preds = prob.predictions(res['xvec'], res['lam'])
    resids = [c.y[c.mask].astype(float) - pr for c, pr in zip(prob.cells, preds)]
    voters = {c.id for c in prob.cells if c.scale == 2}
    s1 = RO.statistic(prob.cells, resids, voters)
    names = [f'{k[0][0]}@{k[0][1]}' for k in prob.keys]

    def pfit(c):
        q = {n.split('@')[0]: v for n, v in zip(names, res['xvec'])}
        q['lam'] = res['lam'][ep]
        return q
    s2 = projection_rgb(prob.cells, resids, fam, pfit, voters)
    P = res['pooled']
    admitted = {s: P < PSTAR[ep][s] for s in ('S1', 'S2')}
    calls = {'S1': s1['call'], 'S2': s2['call']}
    adm = [calls[s] for s in ('S1', 'S2') if admitted[s]]
    if not adm:
        verdict = 'UNDECIDED: neither statistic admitted'
    elif len(adm) == 2 and adm[0] != adm[1]:
        verdict = 'UNDECIDED: both admitted and opposite'
    else:
        verdict = adm[0] if adm[0] in ('AFTER', 'BEFORE') else 'UNDECIDED: the admitted statistic reads between its bars'
    grey = [c for c in prob.cells if c.letter != 'E']
    P_grey = float(np.sqrt(np.mean([res['per_cell'][f'{c.ep}|{c.id}'] ** 2 for c in grey])))
    out = dict(schema='w42-g2-step2-refraction-v3-1', endpoint=ep, family=family, fittedCells=len(prob.cells),
               voters=len(voters), params=res['x'], lam=res['lam'], P=P, maxCell=res['max_cell'],
               P_withoutE_descriptive=P_grey, Pstar=PSTAR[ep], admitted=admitted,
               S1={k: v for k, v in s1.items() if k != 'per_cell'}, S1_per_cell=s1['per_cell'], S2=s2,
               verdict=verdict, seconds=round(time.time() - t0),
               note='P over families A-E, calibration and validation, both scales, per channel (E in RGB through '
                    'the per-channel native T, the instrument\'s own output), as run_v3 declares it')
    C.save(C.HERE / 'refraction' / f'{ep}.json', out)
    print(json.dumps({k: v for k, v in out.items() if k not in ('S1_per_cell',)}, default=float, indent=1))
    return out


if __name__ == '__main__':
    run(*sys.argv[1:])
