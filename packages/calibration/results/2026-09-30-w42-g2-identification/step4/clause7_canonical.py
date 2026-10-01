#!/usr/bin/env python3.12
"""Clause 7 on the canonical uniform calibration/validation cells for candidate 2 (the set clause 10
was read on): the rendered deep median per channel against its own T with every spatial gate at its
identity, which is the runtime's `bodyToneTableCodesAt` at the solid's colour and the cell's span
(clause7-canonical-t2.ts; the law reads the table only when it is on, so the reference is computed).
Deep mask: the instrument's rule, active d <= -(20 + 16.8 t) pt, receded d <= -8 pt, on the
declared component's SDF (instrument/geometry.py). Untinted cells only: a tinted cell's reference
would need the author tint's composite, which the table does not carry. Dark active is the shipped
document in candidate 2, and its captures are byte-identical to the shipped tree (README).

    python3.12 -B clause7_canonical.py /tmp/w42-g2-step4/clause7-t2.json -> clause7-canonical.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(HERE.parents[1] / '2026-09-29-w42-g0-declaration/instrument'))
import geometry as G  # noqa: E402

T2 = json.loads(Path(sys.argv[1]).read_text())
spec = json.loads((REPO / 'apps/reference-apple/scenes.json').read_text())
strata = json.loads((HERE.parents[1] / '2026-09-29-w42-g0-declaration/gate/sheets/strata.json').read_text())
cells = [c for c in strata['strata']['uniform']['cells'] if c['tint'] is None]
rows = []
for c in cells:
    scheme = 'dark' if '-dark-' in c['profileKey'] else 'light'
    ep = f"{scheme}-{'rest' if c['pose'] == 'rest' else 'inactive'}"
    if ep == 'dark-rest':
        continue
    scale = 2 if '-2x-' in c['profileKey'] else 1
    scene = next(s for s in spec['scenes'] if s['id'] == c['sceneId'])
    comp = spec['components'][scene['component']]
    s = min(comp['size'])
    t = min(max((s - 64) / 96, 0), 1)
    d = G.sdf(comp, scale)
    mask = d <= (-(20 + 16.8 * t) if c['pose'] == 'rest' else -8)
    png = Path('/tmp/w42-g2-step4/canon/c2/captures') / c['profileKey'] / c['sceneId'] / f"{c['sceneId']}__webgpu.png"
    img = np.asarray(Image.open(png).convert('RGB'), float)
    deep = [float(np.median(img[..., k][mask])) for k in range(3)]
    ref = T2[f"{ep}|{scene['background']}|{s}"]
    rows.append(dict(cell=f"{c['profileKey']}/{c['sceneId']}", endpoint=ep, span=s, pixels=int(mask.sum()),
                     reference=ref, candidate=deep, worst=max(abs(a - b) for a, b in zip(deep, ref))))
value = dict(clause='7, canonical uniform cells, candidate 2', cells=len(rows),
             worst=max(r['worst'] for r in rows), passes=all(r['worst'] <= 1.0 and r['pixels'] > 0 for r in rows),
             rows=rows)
(HERE / 'clause7-canonical.json').write_text(json.dumps(value, indent=1) + '\n')
for r in rows:
    print(f"{r['cell']:90s} {r['pixels']:6d} ref {np.round(r['reference'], 2).tolist()} c2 {r['candidate']} worst {r['worst']:.2f}")
print('cells', len(rows), 'worst', round(value['worst'], 3), 'passes', value['passes'])
