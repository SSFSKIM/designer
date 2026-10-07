#!/usr/bin/env python3
"""Read completed scratch probes, including T-low guard, into auditable compact evidence.

This is an exploratory mechanism reading, not a gate: holdout/referees are absent and no fitted
point is selected. Matrices and request/census records are checked against the preserved copies.
Write probe-readings-corrected.json, never replace the original recorded probe-readings.json;
--check recomputes from the existing scratch matrices/pixels and compares without writing files.
The native/current/probe/historicalReference fields retain raw full-silhouette T1 values. The
historicalStatistic and historicalRegressionReference fields name the actual regression metric;
rawGrowthHistoricalInB separately preserves the full-silhouette historical calculation.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
SCRATCH = Path('/Users/new/vitrea-w49/b-grounding-scratch')
MAIN = Path('/Users/new/Developer/GitHub/designer')
sys.path.insert(0, str(CAL / 'results/2026-10-03-w44-g1-refit/cuts'))
import readings as R
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true',
                    help='Compare scratch recomputation to the corrected output without writing.')
args = parser.parse_args()
output = HERE / 'probe-readings-corrected.json'
cut = json.loads((CAL / 'results/2026-10-07-w49a-g1-landing/cuts/cut-025-dark-w49a-landing.json').read_text())
current = {(c['scale'],c['scene']):c for c in cut['T1']['cells'] if c['scheme']=='dark' and c['tier']=='webgpu'}
auth = {(c['scale'],c['scene']):c for c in json.loads((HERE/'attribution.json').read_text())['authorised']}
probes={p['label']:p for path in sorted(HERE.glob('probes*.json')) for p in json.loads(path.read_text())['points']}
result=[]
for path in sorted((SCRATCH/'renders').glob('*/*/matrix.json')):
    label=path.parent.parent.name; scale=int(path.parent.name[0]); point=probes[label]
    archived=HERE/'readings'/label/f'{scale}x'
    assert gzip.decompress((archived/'matrix.json.gz').read_bytes())==path.read_bytes()
    for name in ('request.json','census.json'):
        assert (archived/name).read_bytes()==(path.parent/name).read_bytes(),(label,scale,name)
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
        raw_historical=(abs(value-n)-abs(ref-n))/c['B']
        historical_ref=low['reference'] if c['stratum']=='T' else ref
        historical=((abs(bands['web']['low']-low['native'])-abs(historical_ref-low['native']))/c['B']
                    if c['stratum']=='T' else raw_historical)
        measured.append(dict(scene=scene,scale=scale,stratum=c['stratum'],native=n,current=now,probe=value,
            B=c['B'],growthCurrentInB=g,rawGrowthCurrentInB=raw_growth,
            historicalReference=ref,historicalGeneration=a['referenceGeneration'] if a else 'd0219cd684bf',
            historicalStatistic='T1-low' if c['stratum']=='T' else 'T1-full-silhouette',
            historicalRegressionReference=historical_ref,rawGrowthHistoricalInB=raw_historical,
            growthHistoricalInB=historical,listed=a is not None,
            bands=bands,meanNative=row['material']['interiorMeanNative']['value'],
            meanWeb=row['material']['interiorMeanWeb']['value']))
    record=dict(label=label,scale=scale,rows=len(measured),matrixSha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        cells=measured,newGrowthBeyondB=[x['scene'] for x in measured if x['growthCurrentInB']>1],
        listedRepaired=[x['scene'] for x in measured if x['listed'] and x['growthHistoricalInB']<=1])
    result.append(record)
    print(label,scale,'rows',len(measured),'protected growth>B',record['newGrowthBeyondB'],'listed repaired',record['listedRepaired'])
if args.check:
    assert json.loads(output.read_text())==result,'Corrected output differs from scratch recomputation'
    print('Scratch recomputation matches the corrected output: 14 scale-runs, 342 cells.')
else:
    output.write_text(json.dumps(result,indent=2)+'\n')
