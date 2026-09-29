#!/usr/bin/env python3
"""Every M2 cell's per-wave and cumulative move, resolved by generation (§5.179).

W41 G2 (c9a §5.193): W36 G1's `m2-rebaseline.py`, ported onto W40's generation store. The
cumulative origin stays W31's pre-fit bed, now named as its (active, receded) pair and
resolved by `matrix_store.load_generation` rather than through the superseded index by
hand; the per-wave reference is whatever `chroma-cut.json` beside it names.

W42 G0 (charter clause 10): this script reads a cut, not rows, so it takes no --candidate;
a cut stamped `admission` passes the stamp on (the JSON carries it after `source`, and
stdout opens `# CANDIDATE`).

    python3.12 -B m2-rebaseline.py [--cut PATH] [--out PATH]
"""
import argparse
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import referee_source
parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--cut',type=Path,default=HERE/'chroma-cut.json')
parser.add_argument('--out',type=Path,default=HERE/'m2-rebaseline.json')
parser.add_argument('--claims',default='c9a §5.193')
args=parser.parse_args()
cut=json.loads(args.cut.read_text())
if 'admission' in cut:
    print('# CANDIDATE admission: the cut read rows at '+', '.join(
        f"{d['path']} sha256:{d['sha12']}" for d in cut['admission']['documents'])
          +' (declared scratch documents; not a shipped cut)')
pre={}
for scheme,sha,receded in [('light','d0c389d70456','2334c7b4c5e2'),('dark','880ab1e31450','5e71370ae6d5')]:
    for cell in referee_source.generation(sha,receded)[0]:
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
args.out.write_text(json.dumps(dict(claims=args.claims,**({'source':cut['source']} if 'source' in cut else {}),
    **({'admission':cut['admission']} if 'admission' in cut else {}),bound=.02,
    referenceGeneration=cut['referenceGeneration'],cells=rows),indent=2)+'\n')
for r in rows:
    print(r['profile'],r['scene'],f"{r['waveReference']:.9f} -> {r['value']:.9f}",
          f"per wave {r['perWave']*100:+.6f}% cumulative {r['cumulative']*100:+.6f}%",r['passStop'])
