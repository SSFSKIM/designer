#!/usr/bin/env python3
"""Verify grounding provenance, corrected comparisons and preservation of the original evidence.

By default this checks all 342 cells without scratch pixels or a running browser. T regression
uses T1-low for both current and historical growth; the raw historical metric stays separate.
--recompute also re-reads the existing scratch matrices/pixels and compares the complete output.
Neither mode renders or writes evidence.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
CAL=HERE.parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--recompute',action='store_true',
                    help='Check stored output against scratch pixels/matrices.')
args=parser.parse_args()
sha=lambda b: hashlib.sha256(b).hexdigest()
load=lambda p: json.loads(p.read_text())
cut_path=CAL/'results/2026-10-07-w49a-g1-landing/cuts/cut-025-dark-w49a-landing.json'
cut=load(cut_path)
base={(c['scale'],c['scene']):c for c in cut['T1']['cells'] if c['scheme']=='dark' and c['tier']=='webgpu'}
attribution=load(HERE/'attribution.json')
assert attribution['sourceCutSha256']==sha(cut_path.read_bytes())
assert len(attribution['authorised'])==15 and len(attribution['namedMissCells'])==27
authorised={(c['scale'],c['scene']):c for c in attribution['authorised']}
for slot,doc in load(HERE/'documents/index.json').items():
    assert sha((HERE/'documents'/f'{doc["sha256"][:12]}.json').read_bytes())==doc['sha256'],slot
for candidate in (HERE/'candidates').glob('*/candidate.json'):
    for slot,endpoint in load(candidate)['endpoints'].items():
        assert sha((candidate.parent/endpoint['path']).read_bytes())==endpoint['sha256'],(candidate,slot)
probes={sha(path.read_bytes()) for path in HERE.glob('probes*.json')}
original_path=HERE/'probe-readings.json'
assert sha(original_path.read_bytes())=='78dbd3a13e2d083d32181f4e2e9bb06a454d84f37a5cc4b9d9837d7f90f7eba8'
original={(r['label'],r['scale']):r for r in load(original_path)}
readings=load(HERE/'probe-readings-corrected.json')
assert len(readings)==14 and sum(r['rows'] for r in readings)==342
assert {(r['label'],r['scale']) for r in readings}==set(original)
checked=0
for reading in readings:
    folder=HERE/'readings'/reading['label']/f'{reading["scale"]}x'
    request=load(folder/'request.json')
    assert request['probesSha256'] in probes
    matrix=gzip.decompress((folder/'matrix.json.gz').read_bytes())
    assert sha(matrix)==reading['matrixSha256']
    rows={r['key']['sceneId']:r for r in json.loads(matrix)['cells']}
    assert sorted(rows)==request['scenes']==sorted(c['scene'] for c in reading['cells'])
    assert len(reading['cells'])==reading['rows']
    assert load(folder/'census.json')['passes']
    recorded=original[reading['label'],reading['scale']]
    assert {k:v for k,v in reading.items() if k!='cells'}=={k:v for k,v in recorded.items() if k!='cells'}
    original_cells={c['scene']:c for c in recorded['cells']}
    for c in reading['cells']:
        current=base[c['scale'],c['scene']]
        assert current['partition']=='gate' and c['scale']==reading['scale']
        assert c['stratum']==current['stratum'] and c['B']==current['B']
        assert c['current']==current['candidate'] and c['native']==current['native']
        row=rows[c['scene']]
        assert row['key']['web']['engineVersion']=='151.0.7922.34'
        assert c['probe']==row['material']['interiorStdDevWeb']['value']
        entry=authorised.get((c['scale'],c['scene']))
        assert c['listed']==(entry is not None)
        reference=entry['reference'] if entry else current['reference']
        generation=entry['referenceGeneration'] if entry else 'd0219cd684bf'
        assert c['historicalReference']==reference and c['historicalGeneration']==generation
        raw_current=(abs(c['probe']-c['native'])-abs(c['current']-c['native']))/c['B']
        raw_historical=(abs(c['probe']-c['native'])-abs(reference-c['native']))/c['B']
        assert abs(raw_current-c['rawGrowthCurrentInB'])<1e-12
        assert abs(raw_historical-c['rawGrowthHistoricalInB'])<1e-12
        if c['stratum']=='T':
            low=current['bands']['low'];n=low['native'];probe=c['bands']['web']['low']
            assert c['bands']['native']['low']==n
            growth=(abs(probe-n)-abs(low['candidate']-n))/c['B']
            historical=(abs(probe-n)-abs(low['reference']-n))/c['B']
            assert c['historicalStatistic']=='T1-low'
            assert c['historicalRegressionReference']==low['reference']
        else:
            growth=raw_current;historical=raw_historical
            assert c['historicalStatistic']=='T1-full-silhouette'
            assert c['historicalRegressionReference']==reference
        assert abs(growth-c['growthCurrentInB'])<1e-12
        assert abs(historical-c['growthHistoricalInB'])<1e-12,(reading['label'],c['scale'],c['scene'])
        # Only T historical growth is corrected: all other recorded values and conclusions stay exact.
        for name,value in original_cells[c['scene']].items():
            corrected=c['rawGrowthHistoricalInB'] if name=='growthHistoricalInB' and c['stratum']=='T' else c[name]
            assert corrected==value,(reading['label'],c['scale'],c['scene'],name)
        checked+=1
assert checked==342
witness=next(c for r in readings if r['label']=='thin-active' and r['scale']==1
             for c in r['cells'] if c['scene']=='hc-text-7__rrect-lg__rest')
assert abs(witness['growthHistoricalInB']-0.097119)<0.5e-6
assert abs(witness['rawGrowthHistoricalInB']-(-0.279561))<0.5e-6
assert witness['growthHistoricalInB']>0>witness['rawGrowthHistoricalInB']
if args.recompute:
    subprocess.run([sys.executable,'-I',str(HERE/'read-probes.py'),'--check'],check=True)
print('Verified: 15 authorisations, 27 named-miss cells, 10 candidate document sets, 14 scale-runs, '
      '342 gate cells; original evidence unchanged, T-low sign witness passes; no referee/holdout render.')
