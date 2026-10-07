#!/usr/bin/env python3
"""Extract the existing level/deep/fine readings beside T1, without a new pixel exposure."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
CAL=HERE.parents[1]
cut_path=CAL/'results/2026-10-07-w49a-g1-landing/cuts/cut-025-dark-w49a-landing.json'
generation_path=CAL/'results/generations/b2d074d2df24-940384c06f73.json'
cut=json.loads(cut_path.read_text())
rows={(r['key']['profileKey'],r['key']['sceneId']):r for r in json.loads(generation_path.read_text())['cells']
      if r['key']['web']['renderer']=='webgpu'}
readings={r['cell']:r for r in cut['T1']['readings']}
cells=[]
for c in cut['T1']['cells']:
    if c['scheme']!='dark' or c['tier']!='webgpu': continue
    if not (c['stratum']=='P' or c['stratum']=='F' and c['pose']=='inactive' or
            c['scene'] in ('checkerboard-lc16__rrect-md__rest','checkerboard__rrect-md__rest','impulse__rrect-lg__inactive')):
        continue
    material=rows[c['profile'],c['scene']]['material']
    bands=readings.get(f'{c["profile"]} webgpu {c["scene"]}')
    cells.append(dict(profile=c['profile'],scene=c['scene'],stratum=c['stratum'],
        T1Native=c['native'],T1Current=c['candidate'],
        meanNative=material['interiorMeanNative']['value'],meanCurrent=material['interiorMeanWeb']['value'],
        readings=bands))
aggregates={k:v for k,v in cut['T1']['aggregatesAllRead'].items() if 'dark webgpu' in k
    and (k.startswith('P ') and k.endswith('both') or k.startswith('F ') and k.endswith('inactive'))}
(HERE/'decomposition.json').write_text(json.dumps(dict(
    sourceCutSha256=hashlib.sha256(cut_path.read_bytes()).hexdigest(),
    sourceGenerationSha256=hashlib.sha256(generation_path.read_bytes()).hexdigest(),
    definitions='T1: linear whole-silhouette SD. Deep: encoded SD, 8 CSS px inset. Fine/low: sigma4-device split, 4 CSS px eroded. These supports differ; their variances are not additive.',
    cells=cells,aggregates=aggregates),indent=2)+'\n')
print(f'Extracted {len(cells)} level/band rows and {len(aggregates)} named-miss aggregate readings.')
