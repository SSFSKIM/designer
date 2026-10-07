"""Native/current/S0.5 contact sheet at the grounding's identical display gains, not a gate."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
S=Path('/Users/new/vitrea-w49/b-g0-scratch')
MAIN=Path('/Users/new/Developer/GitHub/designer')
rows=[];inputs=[]
for scale in (1,2):
 for scene in ('impulse__rrect-ml__inactive','impulse__rrect-lg__inactive'):
  profile=f'apple-macos-27.0-{scale}x-dark-standard-glass0.25'
  paths=[MAIN/'apps/reference-apple/fixtures'/profile/f'{scene}.png',
   MAIN/'packages/calibration/web-captures'/profile/scene/f'{scene}__webgpu.png',
   S/'renders/s-0p5'/f'{scale}x/web-captures'/profile/scene/f'{scene}__webgpu.png']
  images=[]
  for p in paths:
   inputs.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
   im=Image.open(p).convert('RGB')
   if scale==2:im=im.resize((320,200),Image.Resampling.BOX)
   images.append(np.asarray(im).astype(float))
  median=float(np.median(images[0][50:150,80:240]))
  images += [np.clip((im-median)*8+128,0,255) for im in images[:3]]
  row=Image.new('RGB',(1920,228),(28,28,28))
  ImageDraw.Draw(row).text((3,3),f'{scale}x {scene} | native / W49a / S0.5 || same at gain8 about native median {median:g}',fill='white')
  for i,im in enumerate(images):row.paste(Image.fromarray(im.astype('uint8')),(i*320,28))
  rows.append(row)
out=Image.new('RGB',(1920,228*len(rows)))
for i,row in enumerate(rows):out.paste(row,(0,228*i))
out.save(S/'s-first-impulses.png')
(S/'s-first-image-inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
