#!/usr/bin/env python3.12
"""Complete only missing declared identities after the widened scratch refusal.

The first attempt reached two unmeasurable, undeclared accessibility probes.
Its partial rows and captures remain evidence. This continuation neither retries
those probes nor overwrites a measured identity; it fills the declared bed only.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
CAL=HERE.parent.parent
DEST=Path('/tmp/w33-g1b-fit/pre-fit')
spec=importlib.util.spec_from_file_location('w33_capture',HERE/'render-bed.py')
capture=importlib.util.module_from_spec(spec); spec.loader.exec_module(capture)
key=lambda c:(c['key']['profileKey'],c['key']['sceneId'],c['key']['web']['renderer'])
fingerprint=lambda c:hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
before={key(c):fingerprint(c) for c in json.loads((DEST/'matrix.json').read_text())['cells']}
declared=[r for r in json.loads((HERE/'declared-bed.json').read_text())['rows']
          if r['renderer']=='webgpu' and r['role']!='holdout']
missing=[r for r in declared if (r['profile'],r['scene'],r['renderer']) not in before]
(HERE/'prefit-completion-selection.json').write_text(json.dumps(missing,indent=1)+'\n')
for profile in dict.fromkeys(r['profile'] for r in missing):
    scheme='dark' if '-dark-' in profile else 'light'
    doc=CAL/'profiles'/f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json'
    rec=doc.with_name(doc.stem+'-receded.json')
    ids=sorted(r['scene'] for r in missing if r['profile']==profile)
    capture.x6(f'pre-fit-completion/{profile}/missing-declared-only')
    subprocess.run(['npx','tsx','cli/compare.ts','--profile',profile,
                    '--material-profile',str(doc),'--receded-profile',str(rec),
                    '--renderer','webgpu','--alpha','--write-partial','--out-matrix',str(DEST/'matrix.json'),
                    '--set','calibration,validation,probe','--scene',','.join(ids)],cwd=CAL,
                   env=dict(os.environ,VITREA_WEB_CAPTURES=str(DEST/'captures')),check=True)
after={key(c):fingerprint(c) for c in json.loads((DEST/'matrix.json').read_text())['cells']}
assert all(after[k]==v for k,v in before.items())
assert all((r['profile'],r['scene'],r['renderer']) in after for r in declared)
print('preserved',len(before),'rows; added',len(after)-len(before),'declared bed',len(declared))
with (HERE/'pre-fit-stops.txt').open('w') as f:
    subprocess.run([sys.executable,str(HERE/'read-round.py'),'pre-fit'],stdout=f,check=True)
with (HERE/'pre-fit-repro.txt').open('w') as f:
    subprocess.run([sys.executable,str(CAL/'results/2026-09-21-w32-g1-shadow-fit/repro.py'),
                    str(DEST/'declared-matrix.json')],stdout=f,check=True)
