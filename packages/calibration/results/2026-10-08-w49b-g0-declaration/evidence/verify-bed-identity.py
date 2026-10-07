"""Identity controls only: compare all completed dark gate rasters with current canonical pixels."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
S=Path('/Users/new/vitrea-w49/b-g0-scratch')
D=Path('/Users/new/vitrea-w49/b-g0/packages/calibration/results/2026-10-08-w49b-g0-declaration')
refs=json.loads((D/'references.json').read_text())
checks=[]
for scale in (1,2):
 folder=S/'renders/identity'/f'{scale}x'
 if not (folder/'complete.json').exists():raise SystemExit('Incomplete identity run')
 for c in refs['cells']:
  if c['partition']!='gate' or c['scale']!=scale:continue
  rel=Path(c['profile'])/c['scene']/f'{c["scene"]}__webgpu.png'
  before=Path(c['currentCaptureTree'])/rel;after=folder/'web-captures'/rel
  a=np.asarray(Image.open(before).convert('RGBA'));b=np.asarray(Image.open(after).convert('RGBA'))
  if not np.array_equal(a,b):raise SystemExit(f'IDENTITY MISMATCH {scale} {c["scene"]}')
  checks.append(dict(profile=c['profile'],scene=c['scene'],rawSha256=hashlib.sha256(a.tobytes()).hexdigest()))
out=S/'dark-bed-identity.json'
if out.exists():raise SystemExit('Refuse existing proof')
out.write_text(json.dumps(dict(status='byte-identical',generation=refs['currentGeneration'],cells=checks),indent=2)+'\n')
print(len(checks),'dark gate cells byte-identical to W49a current at both scales')
