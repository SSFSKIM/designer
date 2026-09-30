"""Reference check: this engine's LT against memo E's lt.py (the charter's named reference) on the same cells.
lt.py is imported read-only from the grounding scratch; its cells are built on vitrea's web captures only so
that no native pixel is opened (the observed image is never read, only the geometry and the backdrop)."""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.expanduser('~/vitrea-w42/grounding/refit'))
sys.path.insert(0, os.path.expanduser('~/vitrea-w42/grounding/probe'))
import lt  # noqa: E402
import forward as F  # noqa: E402

CASES = [('light', 'rest', 2, 'checkerboard', 'rrect-md', 1.983, 1.983, 0.9),
         ('light', 'rest', 1, 'checkerboard-64', 'rrect-lg', 1.67, 2.04, 0.9),
         ('light', 'inactive', 2, 'checkerboard', 'capsule-button', 2.14, 1.98, 0.9),
         ('dark', 'rest', 2, 'checkerboard-64', 'rrect-md', 2.00, 2.12, 0.9),
         ('dark', 'inactive', 1, 'checkerboard-64', 'rrect-md', 2.12, 2.04, 0.7)]
rows = []
for sch, pose, s, bg, comp, kn, kw, lam in CASES:
    ref = lt.LTCell(sch, pose, s, bg, comp, src='webgpu', floor='gauss')
    mode = 'clamp' if pose == 'rest' else 'norm'
    yr = ref.predict(kn, kw, lam=lam, units='pt', mode=mode, reading='var')
    c = F.Cell(bg, bg, comp, s, sch, pose)
    yo = np.full(c.d.shape, np.nan)
    yo[c.mask] = F.render(c, F.Family(), {'k_n': kn, 'k_w': kw, 'lam': lam})
    m = ref.m & c.mask
    a = np.full(c.d.shape, np.nan); a[ref.m] = yr
    d = (yo - a)[m]
    rows.append(dict(cell=f'{sch}-{pose} {s}x {bg} {comp}', n=int(m.sum()), rms=float(np.sqrt(np.mean(d ** 2))),
                     max=float(np.abs(d).max()), mean=float(d.mean())))
    print(rows[-1], flush=True)
json.dump(rows, open('ref_check.json', 'w'), indent=1)
