# Independent W33 G1a reviewer artifact, offline, 2026-09-22 (§5.171).
# Preserved scratch script, not a standalone replay: paths/dependencies remain as reviewed.
import sys, os, json, pickle
from pathlib import Path
import numpy as np
from collections import defaultdict, Counter
root=Path('/Users/new/Developer/GitHub/designer/.claude/worktrees/w33-g1a-contour-model')
ev=root/'packages/calibration/results/2026-09-22-w33-g1a-contour-model'; out=Path('/tmp/w33-g1a-independent-review')
os.environ['VITREA_WEB_CAPTURES']='/Users/new/Developer/GitHub/designer/packages/calibration/web-captures'
sys.path.insert(0,str(ev)); import model as m
from PIL import Image
pop=json.loads((ev/'population.json').read_text())['rows']; records=[]
for row in pop:
 p,s=row['profile'],row['scene']; g=m.g0
 n=g.rgb(g.FIXTURES/p/(s+'.png')); w=g.rgb(g.CAPTURES/p/s/(s+'__webgpu.png'))
 a=np.asarray(Image.open(g.CAPTURES/p/s/(s+'__webgpu__alpha.png')).convert('RGBA'),dtype=float)[:,:,3]/255
 h,width=n.shape[:2]; rect,radius,_=g.geometry(s,width/320);d,sides=g.sdf_masks(width,h,rect,radius); nx,ny=m.normals(width,h,rect,radius)
 b=g.rgb(g.FIXTURES/'backgrounds'/f'{g.SCENE[s]["background"]}@{width/320:g}x.png'); gy,gx=np.gradient(b.mean(axis=2))
 ring=(d>=0)&(d<1)
 records.append(dict(**row,n=n[ring],w=w[ring],b=b[ring],a=a[ring],nx=nx[ring],ny=ny[ring],gx=gx[ring],gy=gy[ring],sides={k:v[ring] for k,v in sides.items()}))
with open(out/'records.pkl','wb') as f:pickle.dump(records,f)
groups=defaultdict(list)
for r in records:groups[tuple(r[k] for k in ('profile','pose','backdropClass','span','kind'))].append(r)
angleResults=[]
for key,rs in groups.items():
 nx,ny,n,w,b,gx,gy=[np.concatenate([r[k] for r in rs]) for k in ('nx','ny','n','w','b','gx','gy')]
 bins=np.floor(np.mod(np.arctan2(ny,nx),2*np.pi)/(2*np.pi/16)+.5).astype(int)%16
 ids=np.unique(bins); masks=[bins==i for i in ids]; weights=np.sqrt([x.sum() for x in masks]); y=np.array([(n-w)[mask].mean() for mask in masks])
 def fit(basis):
  X=np.array([basis[mask].mean(axis=0) for mask in masks]);coef=np.linalg.lstsq(X*weights[:,None],y*weights,rcond=None)[0];err=y-X@coef
  return dict(max=float(np.abs(err).max()),mae=float(np.average(abs(err),weights=weights**2)),coef=coef.tolist())
 best={}
 for phi in np.arange(0,180,2.5):
  v=nx*np.cos(phi*np.pi/180)+ny*np.sin(phi*np.pi/180);u=-nx*np.sin(phi*np.pi/180)+ny*np.cos(phi*np.pi/180)
  for k in (.5,1,2,4,8,16):
   for family,basis in [('rotated',np.column_stack((np.ones(len(nx)),abs(v)**k))),('twoaxis',np.column_stack((np.ones(len(nx)),abs(v)**k,abs(u)**k)))]:
    f=fit(basis);f.update(phi=float(phi),k=k)
    if family not in best or f['max']<best[family]['max']:best[family]=f
 q=abs(nx)**4
 for family,basis in [('gradient',np.column_stack((np.ones(len(nx)),q,gx,gy,nx*gx+ny*gy,abs(nx*gx+ny*gy)))),('colour-gradient',np.column_stack((np.ones(len(nx)),q,w.mean(axis=1),q*w.mean(axis=1),gx,gy,nx*gx+ny*gy,abs(nx*gx+ny*gy))))]:best[family]=fit(basis)
 opposite=max((abs(y[list(ids).index(i)]-y[list(ids).index((i+8)%16)])/2 for i in ids if (i+8)%16 in ids),default=0)
 angleResults.append(dict(key=key,oppositeBound=float(opposite),fits=best))
(out/'extended-angular.json').write_text(json.dumps(angleResults))
for family in ('rotated','twoaxis','gradient','colour-gradient'):
 print(family,{t:sum(r['fits'][family]['max']<=t for r in angleResults) for t in (1,3)},'worst',max(r['fits'][family]['max'] for r in angleResults))
print('even arbitrary law impossible at 1 / 3',*[sum(r['oppositeBound']>t for r in angleResults) for t in (1,3)])
for r in angleResults:
 if r['key'][:4]==('apple-macos-27.0-1x-dark-standard-glass0.5','rest','photo',96):print('dark/photo/md',r)
