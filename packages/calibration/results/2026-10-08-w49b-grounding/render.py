#!/usr/bin/env python3.12
"""Run the finite exploratory probes; census before every launch, scratch destinations only.

No process is killed, no lock is waited on, and no existing render is overwritten. A partial
matrix is retained as failed evidence and never treated as the requested experiment.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
SCRATCH = Path('/Users/new/vitrea-w49/b-grounding-scratch')
LOCK = Path('/tmp/w49-gpu.lock')
CUT = CAL / 'results/2026-10-07-w49a-g1-landing/cuts/cut-025-dark-w49a-landing.json'
PROBE_FILE = HERE / os.environ.get('W49B_PROBES', 'probes.json')
PROBES = json.loads(PROBE_FILE.read_text())
CELLS = [c for c in json.loads(CUT.read_text())['T1']['cells']
         if c['scheme'] == 'dark' and c['tier'] == 'webgpu' and c['partition'] == 'gate']
spec = importlib.util.spec_from_file_location('census', CAL / 'results/2026-10-02-w43-g3-refit/stage/census.py')
census = importlib.util.module_from_spec(spec)
spec.loader.exec_module(census)

for point in PROBES['points']:
    if len(sys.argv) > 1 and point['label'] not in sys.argv[1:]:
        continue
    for scale in point['scales']:
        label = point['label']
        out = SCRATCH / 'renders' / label / f'{scale}x'
        if out.exists():
            raise SystemExit(f'Refuse existing render {out}')
        out.mkdir(parents=True)
        scenes = sorted(c['scene'] for c in CELLS if c['scale'] == scale and c['pose'] == point['pose'])
        profile = f'apple-macos-27.0-{scale}x-dark-standard-glass0.25'
        argv = ['pnpm', 'run', '-s', 'compare', '--', '--profile', profile, '--renderer', 'webgpu',
                '--candidate-document', str(SCRATCH / 'candidates' / label / 'candidate.json'),
                '--set', 'calibration,validation,recorded,probe', '--scene', ','.join(scenes),
                '--alpha', '--write-partial', '--out-matrix', str(out / 'matrix.json')]
        LOCK.mkdir()  # a competing owner is a stop, not an invitation to kill it or wait in a poll
        try:
            observation = census.observe()
            (out / 'census.json').write_text(json.dumps(observation, indent=2) + '\n')
            if not observation['passes']:
                raise SystemExit(f'Census refuses {label}: {observation["refusals"]}')
            env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
            env['VITREA_WEB_CAPTURES'] = str(out / 'web-captures')
            (out / 'request.json').write_text(json.dumps(dict(argv=argv, scenes=scenes,
                probesSha256=hashlib.sha256(PROBE_FILE.read_bytes()).hexdigest()), indent=2)+'\n')
            print(f'{label} {scale}x: {len(scenes)} gate cells; census passed', flush=True)
            with (out / 'render.txt').open('w') as log:
                run = subprocess.run(argv, cwd=CAL, env=env, stdout=log, stderr=subprocess.STDOUT)
            if run.returncode:
                raise SystemExit(f'{label} {scale}x failed {run.returncode}; see {out}/render.txt')
            matrix = json.loads((out / 'matrix.json').read_text())
            rows = matrix['cells']
            got = sorted(row['key']['sceneId'] for row in rows)
            if got != scenes:
                raise SystemExit(f'Render membership differs: {got} != {scenes}')
            print(f'{label} {scale}x complete: membership exact', flush=True)
        finally:
            LOCK.rmdir()
