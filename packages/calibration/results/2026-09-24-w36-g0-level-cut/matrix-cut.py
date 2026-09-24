"""Freeze W36's non-holdout L1 baseline and structured stops from matrix fields.

The current W33 generation becomes the superseded generation at G1's split. The
snapshot below pins those numbers now; G1 must reproduce them from the named
superseded files rather than substituting a new pre-fit reference (§5.178).
"""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def read(p):return json.loads(p.read_text())
def save(name,value):
    with (HERE/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
scene=read(ROOT/'apps/reference-apple/scenes.json')
roles={s:r for r,ids in scene['split'].items() if isinstance(ids,list) for s in ids}
rows=[];probe=[]
for c in read(ROOT/'packages/calibration/results/matrix.json')['cells']:
    key=c['key'];profile=key['profileKey'];sid=key['sceneId'];role=roles.get(sid)
    # Role admission happens before any metric is inspected. No held-out reading.
    if role not in ['calibration','validation','probe']:continue
    if not (profile.startswith('apple-macos-27.0-') and '-standard-' in profile and
            c['tier']=='texture' and key['web']['renderer']=='webgpu'):continue
    m=c.get('material',{});value=lambda field:m.get(field,{}).get('value')
    n,w=value('interiorMeanNative'),value('interiorMeanWeb')
    row=dict(cell=profile+'/'+sid,profile=profile,scene=sid,role=role,
        capturePath=key['web']['capturePath'],nativeMean=n,webMean=w,
        absoluteError=None if n is None or w is None else abs(w-n),
        interiorStdDevWeb=value('interiorStdDevWeb'),chromaNative=value('chromaStructureRatioNative'),
        chromaWeb=value('chromaStructureRatioWeb'),
        tintDeltaLNative=value('tintDeltaLNative'),tintDeltaLWeb=value('tintDeltaLWeb'),
        perceptual={k:v['value'] for k,v in c.get('perceptual',{}).items() if isinstance(v,dict)},
        shape={k:v['value'] for k,v in c.get('shape',{}).items() if isinstance(v,dict)})
    (rows if role in ['calibration','validation'] else probe).append(row)
rows.sort(key=lambda r:r['cell']);probe.sort(key=lambda r:r['cell'])
base=dict(light=dict(active='6e509c7f76cc',receded='45acb6d916b9',
                    supersededFile='results/superseded/6e509c7f76cc.json'),
          dark=dict(active='eab099cc6698',receded='4e68f81869f6',
                    supersededFile='results/superseded/eab099cc6698.json'))
for row in rows:
    b=base['dark' if '-dark-' in row['profile'] else 'light']
    assert 'sha256:'+b['active'] in row['capturePath']
    assert 'sha256:'+b['receded'] in row['capturePath']
missing=[r['cell'] for r in rows if r['absoluteError'] is None]
misses=[dict(cell=r['cell'],absoluteError=r['absoluteError']) for r in rows if r['absoluteError'] is not None and r['absoluteError']>.055]
summary=dict(declaredPopulation=len(rows),measuredPopulation=len(rows)-len(missing),
    missing=missing,absoluteMisses=misses,absoluteBound=.055,growthBound=.005,
    baselineGeneration=base,baselineLocation='Working matrix at G0; named superseded files after G1 split',
    estimator='mean linear Rec.709 luminance over the native silhouette; material.interiorMean{Native,Web}',
    predicate='No shape conditioning exclusion. Missing material metrics are UNMEASURED, not passes.',
    existingMissTreatment='The absolute bound remains 0.055. Name both existing misses, never floor them; growth <=0.005 applies to them too. Adoption may report these misses, not claim every cell passes.',
    sets=['calibration','validation'],renderer='webgpu',tier='texture',probe='Diagnostic only',
    populationByProfile={p:sum(r['profile']==p for r in rows) for p in sorted({r['profile'] for r in rows})})
save('l1-baseline.json',rows);save('l1-declaration.json',summary)
save('probe-level-diagnostics.json',probe)
photo=[r for r in rows if r['scene'].startswith('photo__') and 'tint' not in r['scene'] and r['chromaNative'] is not None]
save('structured-baseline.json',[r for r in rows if r['scene'].split('__')[0] in ['photo','impulse','checkerboard','hc-text']])
print(json.dumps(summary,indent=2));print('M1 baseline')
import numpy as np
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
    rr=[r for r in photo if f'-{scheme}-' in r['profile'] and r['scene'].endswith('__'+pose)]
    print(scheme,pose,len(rr),float(np.median([r['chromaWeb']/r['chromaNative'] for r in rr])))
