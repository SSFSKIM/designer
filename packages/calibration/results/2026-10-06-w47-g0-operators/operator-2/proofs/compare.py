#!/usr/bin/env python3.12
"""W47 G0(b): two repeated recorders on each tree, identity across trees, and live-path differences.

The before tree is operator1 plus only the unchanged fine recorder; after is the merged operators.
Read raw-raster SHA256, not PNG encoding equality. The PNG bytes are independently decoded and
hashed to prove each recorded digest names the archived raster. Op1 replay must equal its committed
post-op1 cases. No threshold or fitted point is chosen here.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--renders',type=Path,default=HERE);ap.add_argument('--check',action='store_true');args=ap.parse_args()
 root=args.renders
 runs={k:json.loads((root/k/'cases.json').read_text()) for k in ('before-1','before-2','after-1','after-2','op1-replay')}
 b,a=runs['before-1'],runs['after-1'];assert b.keys()==a.keys()
 assert runs['before-2'].keys()==b.keys() and runs['after-2'].keys()==a.keys()
 for first,second in [('before-1','before-2'),('after-1','after-2')]:
  assert all(runs[first][k]['sha256']==runs[second][k]['sha256'] for k in runs[first]),f'{first}: repeat differs'
 lines=[];identities=0;live=0;rows=[]
 for label,old in b.items():
  new=a[label];assert old['identity']==new['identity']
  assert old.get('patch')==new.get('patch') and old.get('scene')==new.get('scene')
  same=old['sha256']==new['sha256']
  if old['identity']:assert same,label;identities+=1
  else:assert not same,label;live+=1
  delta=None
  if not label.startswith('golden/'):
   pixels=[]
   for phase in ('before-1','after-1'):
    path=root/phase/'png'/f"{label.replace('/','__')}.png"
    image=np.asarray(Image.open(path).convert('RGBA'))
    assert hashlib.sha256(image.tobytes()).hexdigest()==runs[phase][label]['sha256']
    pixels.append(image.astype(np.int16))
   difference=np.abs(pixels[1]-pixels[0]);delta=dict(pixels=int(np.any(difference>0,axis=2).sum()),maximumCode=int(difference.max()))
  rows.append(dict(label=label,identity=old['identity'],before=old['sha256'],after=new['sha256'],difference=delta))
  lines.append(f"{'IDENTICAL' if same else 'LIVE     '} {label}: {delta}")
 prior=json.loads((HERE.parents[1]/'operator-1/after/cases.json').read_text())
 replay=runs['op1-replay'];assert prior.keys()==replay.keys()
 assert all(prior[k]['sha256']==replay[k]['sha256'] for k in prior),'op1 replay changed'
 out=dict(beforeTree='cf36cdd13',afterTree='8f55ea1ed',cases=len(b),identityCases=identities,liveCases=live,
  repeatCasesIdentical=dict(before=len(b),after=len(a)),op1ReplayCasesIdentical=len(prior),rows=rows)
 lines += [f'Identity across trees: {identities}/{identities}; live cases moved: {live}/{live}',
  f'Repeats: {len(b)}/{len(b)} before and {len(a)}/{len(a)} after',f'Op1 replay unchanged: {len(prior)}/{len(prior)}']
 for name,text in [('comparison.json',json.dumps(out,indent=2)+'\n'),('comparison.txt','\n'.join(lines)+'\n')]:
  p=HERE/name
  if args.check:assert p.read_text()==text
  else:
   with p.open('x') as f:f.write(text)
 print('\n'.join(lines[-3:]))
if __name__=='__main__':main()
