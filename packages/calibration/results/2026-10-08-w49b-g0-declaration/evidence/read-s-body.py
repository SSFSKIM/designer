"""Non-gating S diagnostic: mean on the already-defined W44 analytical deep cut (8 CSS px).
The adopted impulse silhouette can contain only sparse detected pixels. This reads the body's
path-defined deep region instead; it never substitutes this population into T1 acceptance.
"""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path('/Users/new/vitrea-w49/b-g0');S=Path('/Users/new/vitrea-w49/b-g0-scratch')
sys.path.insert(0,str(ROOT/'packages/calibration/results/2026-10-03-w44-g1-refit/cuts'))
import readings as R
MAIN=Path('/Users/new/Developer/GitHub/designer')
rows=[]
for scale in (1,2):
 profile=f'apple-macos-27.0-{scale}x-dark-standard-glass0.25'
 for scene in ('impulse__rrect-ml__inactive','impulse__rrect-lg__inactive'):
  native_path=MAIN/'apps/reference-apple/fixtures'/profile/f'{scene}.png'
  native=np.asarray(Image.open(native_path).convert('RGB'))
  g=R.cell_geometry(profile,scene,native);mask=g['deep']
  row=dict(scale=scale,scene=scene,pixels=int(mask.sum()),adoptedSilhouettePixels=int(g['silhouette'].sum()),readings={})
  paths={'native':native_path}
  for label in ('identity','s-0p5','s-0p25','s-0p125'):
   paths[label]=S/'renders'/label/f'{scale}x/web-captures'/profile/scene/f'{scene}__webgpu.png'
  for label,path in paths.items():
   image=np.asarray(Image.open(path).convert('RGB'));encoded=R.encoded_luma(image)[mask]
   row['readings'][label]=dict(encodedMean=float(encoded.mean()),encodedMedian=float(np.median(encoded)),
    linearMean=float(R.P.luminance(image)[mask].mean()),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
  rows.append(row)
out=S/'s-analytic-deep.json'
if out.exists():raise SystemExit('Refuse existing diagnostic')
out.write_text(json.dumps(dict(scope='NON-GATING path-defined W44 deep cut, not the adopted silhouette statistic',rows=rows),indent=2)+'\n')
for row in rows:print(row['scale'],row['scene'],{k:round(v['encodedMean'],3) for k,v in row['readings'].items()})
