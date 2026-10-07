#!/usr/bin/env python3
"""Read completed scratch probes, including T-low guard, into auditable compact evidence.

This is an exploratory mechanism reading, not a gate: holdout/referees are absent and no fitted
point is selected. Raw matrices and source requests/census are gzipped beside the summaries.
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
SCRATCH = Path('/Users/new/vitrea-w49/b-grounding-scratch')
MAIN = Path('/Users/new/Developer/GitHub/designer')
sys.path.insert(0, str(CAL / 'results/2026-10-03-w44-g1-refit/cuts'))
import readings as R
cut = json.loads((CAL / 'results/2026-10-07-w49a-g1-landing/cuts/cut-025-dark-w49a-landing.json').read_text())
current = {(c['scale'],c['scene']):c for c in cut['T1']['cells'] if c['scheme']=='dark' and c['tier']=='webgpu'}
auth = {(c['scale'],c['scene']):c for c in json.loads((HERE/'attribution.json').read_text())['authorised']}
probes={p['label']:p for path in sorted(HERE.glob('probes*.json')) for p in json.loads(path.read_text())['points']}
result=[]
for path in sorted((SCRATCH/'renders').glob('*/*/matrix.json')):
    label=path.parent.parent.name; scale=int(path.parent.name[0]); point=probes[label]
    request=json.loads((path.parent/'request.json').read_text())
    rows=json.loads(path.read_text())['cells']
    assert sorted(r['key']['sceneId'] for r in rows)==request['scenes']
    assert all(r['key']['web']['engineVersion']=='151.0.7922.34' for r in rows)
    assert json.loads((path.parent/'census.json').read_text())['passes']
    measured=[]
    for row in rows:
        scene=row['key']['sceneId']; c=current[scale,scene]
        assert c['partition']=='gate'
        value=row['material']['interiorStdDevWeb']['value']
        n,old,now=c['native'],c['reference'],c['candidate']
        raw_growth=(abs(value-n)-abs(now-n))/c['B']
        bands=None
        if c['stratum']=='T':
            profile=c['profile']
            native=np.asarray(Image.open(MAIN/'apps/reference-apple/fixtures'/profile/f'{scene}.png').convert('RGB'))
            webpath=path.parent/'web-captures'/profile/scene/f'{scene}__webgpu.png'
            web=np.asarray(Image.open(webpath).convert('RGB'))
            bands=R.read(profile,scene,native,web)
            low=c['bands']['low']; g=(abs(bands['web']['low']-low['native'])-abs(low['candidate']-low['native']))/c['B']
        else:
            g=raw_growth
        a=auth.get((scale,scene)); ref=a['reference'] if a else old
        measured.append(dict(scene=scene,scale=scale,stratum=c['stratum'],native=n,current=now,probe=value,
            B=c['B'],growthCurrentInB=g,rawGrowthCurrentInB=raw_growth,
            historicalReference=ref,historicalGeneration=a['referenceGeneration'] if a else 'd0219cd684bf',
            growthHistoricalInB=(abs(value-n)-abs(ref-n))/c['B'],listed=a is not None,
            bands=bands,meanNative=row['material']['interiorMeanNative']['value'],
            meanWeb=row['material']['interiorMeanWeb']['value']))
    record=dict(label=label,scale=scale,rows=len(measured),matrixSha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        cells=measured,newGrowthBeyondB=[x['scene'] for x in measured if x['growthCurrentInB']>1],
        listedRepaired=[x['scene'] for x in measured if x['listed'] and x['growthHistoricalInB']<=1])
    result.append(record)
    target=HERE/'readings'/label/f'{scale}x';target.mkdir(parents=True,exist_ok=True)
    (target/'matrix.json.gz').write_bytes(gzip.compress(path.read_bytes(),mtime=0))
    for name in ('request.json','census.json'): shutil.copyfile(path.parent/name,target/name)
    print(label,scale,'rows',len(measured),'protected growth>B',record['newGrowthBeyondB'],'listed repaired',record['listedRepaired'])
(HERE/'probe-readings.json').write_text(json.dumps(result,indent=2)+'\n')
