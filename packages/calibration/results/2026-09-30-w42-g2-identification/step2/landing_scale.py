"""W42 G2, the improvement landing (Decision Log 7): candidate 2's chroma scale read by least squares at the landing
values (LT at the k@global least-squares point: one k for both radii in every endpoint, lam per endpoint), on family
E's calibration cells with the per-channel knee, as declaration item candidate2Chroma specifies the fit ("re-fitted
on the new bed's calibration colour cells with the law held at its identified parameters"). Not a render.

    python3.12 -B landing_scale.py     -> landing-scale.json
"""
import json

import numpy as np
from scipy import optimize

import common as C
import knee_chroma as KC

F = C.F
glob = json.loads((C.HERE / 'fits' / 'main' / 'LT@k@global__all__n.json').read_text())['ls']
k = glob['params']['k@all']
out = dict(schema='w42-g2-landing-scale-1', k=k, lam=glob['lam'], endpoints={})
for ep in ('light-rest', 'light-inactive', 'dark-inactive'):
    p = F.expand(F.Family(), dict(k=k, lam=glob['lam'][ep]))
    q = KC.g_coeffs(ep)
    cal = C.cells(ep, 2, ('calibration',), letters=('E',), rgb=True)
    val = C.cells(ep, 2, ('validation',), letters=('E',), rgb=True)
    ac = [KC.argument(c, F.Family(), p, 'channel') for c in cal]
    av = [KC.argument(c, F.Family(), p, 'channel') for c in val]
    ys = [c.y[c.mask].astype(float) for c in cal]
    f = lambda s: float(np.mean([np.mean((KC.output(c, a, s, q) - y) ** 2) for c, a, y in zip(cal, ac, ys)]))
    r = optimize.minimize_scalar(f, bounds=KC.S_BOUNDS, method='bounded', options=dict(xatol=1e-6))
    s = float(r.x)
    sc = C.summarize(cal, [KC.output(c, a, s, q) for c, a in zip(cal, ac)])
    sv = C.summarize(val, [KC.output(c, a, s, q) for c, a in zip(val, av)])
    out['endpoints'][ep] = dict(scale=s, lsRms=float(np.sqrt(r.fun)), gCoefficients=q,
                                calibration=dict(worst=sc['worstMeasured'], failures=sc['failures'],
                                                 pooled=sc['pooledRms']),
                                validation=dict(worst=sv['worstMeasured'], failures=sv['failures'],
                                                pooled=sv['pooledRms']))
    print(ep, round(s, 6), out['endpoints'][ep]['calibration'], out['endpoints'][ep]['validation'])
C.save(C.HERE / 'landing-scale.json', out)
