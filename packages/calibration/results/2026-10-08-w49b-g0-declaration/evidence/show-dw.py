"""Native/current/declared-rung comparisons; gain is display-only, never a gate."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
S=Path('/Users/new/vitrea-w49/b-g0-scratch');MAIN=Path('/Users/new/Developer/GitHub/designer')
cases={
 'd-controls':[(s,scene,'d-only-256') for s in (1,2) for scene in
  ('checkerboard-32__rrect-lg__rest','hc-text__rrect-lg__rest')],
 'w-controls':[(s,scene,'w-joint-d4-a09-t128') for s in (1,2) for scene in
  ('impulse__rrect-ml__inactive','impulse__rrect-lg__inactive','checkerboard-64__rrect-lg__inactive')],
}
for name,group in cases.items():
 rows=[];inputs=[]
 for scale,scene,label in group:
  profile=f'apple-macos-27.0-{scale}x-dark-standard-glass0.25'
  paths=[MAIN/'apps/reference-apple/fixtures'/profile/f'{scene}.png',
   MAIN/'packages/calibration/web-captures'/profile/scene/f'{scene}__webgpu.png',
   S/'renders'/label/f'{scale}x/web-captures'/profile/scene/f'{scene}__webgpu.png']
  images=[]
  for path in paths:
   inputs.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
   im=Image.open(path).convert('RGB')
   if scale==2:im=im.resize((320,200),Image.Resampling.BOX)
   images.append(np.asarray(im).astype(float))
  median=float(np.median(images[0][50:150,80:240]));gain=8 if scene.startswith('impulse') else 4
  images += [np.clip((im-median)*gain+128,0,255) for im in images[:3]]
  row=Image.new('RGB',(1920,228),(28,28,28))
  ImageDraw.Draw(row).text((3,3),f'{scale}x {scene} | native / W49a / {label} || same at gain{gain} about native median {median:g}',fill='white')
  for i,im in enumerate(images):row.paste(Image.fromarray(im.astype('uint8')),(i*320,28))
  rows.append(row)
 out=Image.new('RGB',(1920,228*len(rows)))
 for i,row in enumerate(rows):out.paste(row,(0,228*i))
 out.save(S/f'{name}.png');(S/f'{name}-inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
