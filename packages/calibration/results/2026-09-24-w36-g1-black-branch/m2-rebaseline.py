#!/usr/bin/env python3
"""Every M2 cell's per-wave and cumulative move, resolved by generation (§5.179)."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
CAL=HERE.parent.parent
index=json.loads((CAL/'results/superseded/index.json').read_text())
cut=json.loads((HERE/'chroma-cut.json').read_text())
pre={}
for scheme,sha in [('light','d0c389d70456'),('dark','880ab1e31450')]:
    path=CAL/'results/superseded'/index['byDocumentSha256'][sha]
    for cell in json.loads(path.read_text())['cells']:
        if cell['key']['web']['renderer']!='webgpu': continue
        if f'sha256:{sha}' not in cell['key']['web']['capturePath']: continue
        value=(cell.get('material') or {}).get('interiorStdDevWeb')
        if value: pre[(cell['key']['profileKey'],cell['key']['sceneId'])]=value['value']
rows=[]
for cell in sorted(cut['cells'],key=lambda c:(c['profile'],c['scene'])):
    initial=pre[(cell['profile'],cell['scene'])]
    reference=cell['interiorStdDevWebReference']
    now=cell['interiorStdDevWeb']
    wave=(now-reference)/reference
    assert abs(wave-cell['structureDeltaFraction'])<1e-12
    rows.append(dict(profile=cell['profile'],scene=cell['scene'],w31PreFit=initial,
                     waveReference=reference,value=now,perWave=wave,cumulative=(now-initial)/initial,
                     passStop=abs(wave)<=.02))
assert len(rows)==26
(HERE/'m2-rebaseline.json').write_text(json.dumps(dict(claims='c9a §5.179',bound=.02,
    referenceGeneration=cut['referenceGeneration'],cells=rows),indent=2)+'\n')
for r in rows:
    print(r['profile'],r['scene'],f"{r['waveReference']:.9f} -> {r['value']:.9f}",
          f"per wave {r['perWave']*100:+.6f}% cumulative {r['cumulative']*100:+.6f}%",r['passStop'])
