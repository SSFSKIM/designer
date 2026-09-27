"""Declared LS and numerical minimax grid beside the certified support obstruction.

Four scheme/pose fits share both scales. Least squares has equal cell mass and
equal channel/bin mass within each cell, after censor exclusion; every member
shares its cell's mass. Validation never enters a solve or grid selection.
Minimax is the maximum channel/bin mean absolute error, absolute before spatial
reduction. An active-constraint SLSQP solve uses the exact clipped forward and
its piecewise analytic derivative. Its convergence is not a global certificate;
the separate support proof certifies the all-coefficient survival rejection.
"""
import argparse
import gzip
import hashlib
import json
import os
import platform
import scipy
from pathlib import Path
import sys
import time
import numpy as np
from scipy.optimize import minimize
import basis

W=np.array([.2126,.7152,.0722]);BOUND=4096
p=argparse.ArgumentParser();p.add_argument('cache');p.add_argument('output');p.add_argument('--endpoint',required=True);p.add_argument('--grid-limit',type=int,default=45)
a=p.parse_args();cache=Path(a.cache);output=Path(a.output);output.mkdir(exist_ok=False)
sealpath=cache/'seal.json'
if sealpath.exists():
 seal=json.loads(sealpath.read_text())
 for item in seal['files']:
  raw=(cache/item['file']).read_bytes()
  if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('cache seal mismatch')
else:
 if not str(cache).startswith('/private/tmp/w39-edge-synthetic-') and not str(cache).startswith('/tmp/w39-edge-synthetic-'):raise ValueError('native cache must be sealed')
manifest=json.loads((cache/'manifest.json').read_text())
scheme,pose=a.endpoint.split('-');pose='rest' if pose=='active' else 'inactive'
records=[r for r in manifest['records'] if r['scheme']==scheme and r['pose']==pose]
geo={k:dict(np.load(cache/(k+'.npz'))) for k in {r['geometry'] for r in records}}
for r in records:
 r['data']=dict(np.load(cache/(r['id']+'.npz')))
 r['bins']=manifest['geometries'][r['geometry']]['bins']
 r['binids']=geo[r['geometry']]['binids'];r['inside']=geo[r['geometry']]['inside']
 b=r['data']['deep']/255;y=b@W;z=b-y
 r['colour']=np.column_stack((np.ones(3),np.full(3,y),z,y*z))
 r['base']=np.where(r['inside'][:,None],b,r['data']['backdrop']/255)
 r['target']=r['data']['native']/255
 counts=np.bincount(r['binids'],minlength=len(r['bins']))
 r['counts']=counts;r['admitted']=counts>=4
 valid=(r['data']['native']>5)&(r['data']['native']<250)&r['admitted'][r['binids'],None]
 r['valid']=valid
 vc=np.stack([np.bincount(r['binids'],weights=valid[:,c],minlength=len(counts)) for c in range(3)],axis=1)
 r['validcounts']=vc;r['fitbins']=(vc>=4)&r['admitted'][:,None]
 valid &= r['fitbins'][r['binids']]
 membercount=sum(s['cell']==r['cell'] for s in records)
 weight=np.divide(valid,np.maximum(vc[r['binids']],1))
 weight/=max(1,int(r['fitbins'].sum()))*membercount
 r['weight']=weight
cal=[r for r in records if r['role']=='calibration'];ncell=len({r['cell'] for r in cal})
for r in cal:r['weight']/=ncell
fitkeys=[(i,int(b),int(c)) for i,r in enumerate(cal) for b,c in np.argwhere(r['fitbins'])]


def predict(r,q):
 return r['base']+(r['radial']@q.reshape(11,4))@r['colour'].T

def ls_value(q):
 loss=0.;grad=np.zeros((11,4))
 for r in cal:
  pre=predict(r,q);pred=np.clip(pre,0,1);error=pred-r['target']
  loss+=np.sum(r['weight']*error*error)*255**2
  derivative=2*255**2*r['weight']*error*((pre>0)&(pre<1))
  grad+=(r['radial'].T@derivative)@r['colour']
 return float(loss),grad.ravel()


def linear_start():
 h=np.zeros((44,44));g=np.zeros(44)
 for r in cal:
  rad=r['radial'];delta=r['target']-r['base']
  for c in range(3):
   weight=r['weight'][:,c];colour=r['colour'][c]
   h+=np.kron(rad.T@(rad*weight[:,None]),np.outer(colour,colour))
   g+=np.outer(rad.T@(weight*delta[:,c]),colour).ravel()
 q=np.linalg.lstsq(h,g,rcond=None)[0]
 eigen=np.linalg.eigvalsh(h)
 singular=np.sqrt(np.maximum(eigen,0))[::-1]
 rank=int(np.linalg.matrix_rank(h))
 return np.clip(q,-BOUND,BOUND),rank,singular.tolist()


class Minimax:
 def __init__(self):self.last=None;self.values=None;self.pre=[]
 def evaluate(self,q):
  if self.last is not None and np.array_equal(q,self.last):return self.values
  arrays=[];self.pre=[]
  for r in cal:
   pre=predict(r,q);self.pre.append(pre);err=abs(np.clip(pre,0,1)-r['target'])*255
   bins=np.stack([np.bincount(r['binids'],weights=err[:,c]*r['valid'][:,c],minlength=len(r['bins'])) for c in range(3)],axis=1)
   bins/=np.maximum(r['validcounts'],1)
   arrays.extend(bins[r['fitbins']].tolist())
  self.last=q.copy();self.values=np.asarray(arrays)
  return self.values
 def jacobian(self,q,ids):
  self.evaluate(q);out=[]
  for i in ids:
   ri,b,c=fitkeys[int(i)];r=cal[ri];mask=(r['binids']==b)&r['valid'][:,c]
   pre=self.pre[ri][mask,c];sign=np.sign(np.clip(pre,0,1)-r['target'][mask,c])*((pre>0)&(pre<1))
   grad=(r['radial'][mask]*sign[:,None]).mean(0)
   out.append((255*np.outer(grad,r['colour'][c])).ravel())
  return np.asarray(out)


def minimax(q):
 judge=Minimax();values=judge.evaluate(q);active=set(np.argsort(values)[-64:].tolist())
 start=np.r_[q,float(values.max())+1e-7];iterations=0;rounds=[];best=start.copy()
 for roundno in range(12):
  ids=np.array(sorted(active))
  constraints=dict(type='ineq',fun=lambda v:v[-1]-judge.evaluate(v[:-1])[ids],
      jac=lambda v:np.column_stack((-judge.jacobian(v[:-1],ids),np.ones(len(ids)))))
  result=minimize(lambda v:v[-1],start,jac=lambda v:np.r_[np.zeros(44),1.],method='SLSQP',
      bounds=[(-BOUND,BOUND)]*44+[(0,None)],constraints=[constraints],
      options=dict(ftol=1e-8,maxiter=200))
  iterations+=int(result.nit);values=judge.evaluate(result.x[:-1]);actual=float(values.max())
  if actual<best[-1]:best=np.r_[result.x[:-1],actual]
  violation=actual-result.x[-1]
  rounds.append(dict(round=roundno,active=len(ids),converged=bool(result.success),message=str(result.message),
      iterations=int(result.nit),epigraph=float(result.x[-1]),actualMaximum=actual,unseenViolation=float(violation)))
  if result.success and violation<=1e-6:
   return dict(coefficients=result.x[:-1].tolist(),maximumCodes=actual,converged=True,
       iterations=iterations,rounds=rounds,certificate='numerical stationary point; survival rejection separately certified by support')
  active.update(np.argsort(values)[-64:].tolist());start=np.r_[best[:-1],best[-1]+1e-7]
 return dict(coefficients=best[:-1].tolist(),maximumCodes=float(best[-1]),converged=False,iterations=iterations,rounds=rounds,
      certificate='bounded numerical search stopped; survival rejection separately certified by support')


def score(q,method):
 rows=[]
 for r in records:
  pred=np.clip(predict(r,q),0,1)*255;data=r['data'];labels=r['binids'];counts=r['counts']
  def reduced(native):
   error=abs(pred-native)
   return np.stack([np.bincount(labels,weights=error[:,c],minlength=len(counts)) for c in range(3)],axis=1)/np.maximum(counts[:,None],1)
  errors=reduced(data['native']);states=np.stack([reduced(state) for state in data['states']]);tau=np.maximum(1,data['bar'])
  signed=np.stack([np.bincount(labels,weights=(pred-data['native'])[:,c],minlength=len(counts)) for c in range(3)],axis=1)/np.maximum(counts[:,None],1)
  for i,b in enumerate(r['bins']):
   rows.append(dict(cell=r['cell'],scheme=r['scheme'],pose=r['pose'],scale=r['scale'],role=r['role'],method=method,
    **b,residualRGB=errors[i].tolist() if counts[i] else None,signedResidualRGB=signed[i].tolist() if counts[i] else None,
    toleranceRGB=tau[i].tolist(),failedChannels=np.flatnonzero(errors[i]>tau[i]+1e-8).tolist() if r['admitted'][i] else [],
    repeatResidualRGB=[states[j,i].tolist() for j in data['stateix']] if counts[i] else None))
 return rows

trials=[];bestls=None;bestmm=None;started=time.monotonic()
for width in [.8,1,1.2,1.4,1.6,1.8,2,2.2,2.4]:
 for exponent in [1,2,3,4,6]:
  if len(trials)>=a.grid_limit:continue
  t0=time.monotonic()
  bases={k:basis.radial(g['t'],g['ny'],width,exponent) for k,g in geo.items()}
  for r in records:r['radial']=bases[r['geometry']]
  q,rank,singular=linear_start()
  fit=minimize(ls_value,q,jac=True,method='L-BFGS-B',bounds=[(-BOUND,BOUND)]*44,
      options=dict(ftol=1e-14,gtol=1e-7,maxiter=1000,maxls=40))
  ls=dict(coefficients=fit.x.tolist(),weightedMeanSquaredCodes=float(fit.fun),converged=bool(fit.success),message=str(fit.message),iterations=int(fit.nit))
  mm=minimax(fit.x)
  trial=dict(widthCSS=width,exponent=exponent,rank=rank,columns=44,singularValues=singular,
      leastSquares=ls,minimax=mm,seconds=time.monotonic()-t0)
  trials.append(trial)
  if bestls is None or ls['weightedMeanSquaredCodes']<bestls['leastSquares']['weightedMeanSquaredCodes']:bestls=trial
  if bestmm is None or mm['maximumCodes']<bestmm['minimax']['maximumCodes']:bestmm=trial
  path=output/(f'trial-{len(trials):02}.json')
  with path.open('x') as f:json.dump(trial,f,indent=2,allow_nan=False)
  print(a.endpoint,len(trials),'shape',width,exponent,'LS',ls['weightedMeanSquaredCodes'],ls['converged'],
      'MM',mm['maximumCodes'],mm['converged'],'seconds',trial['seconds'],flush=True)
for method,best in [('leastSquares',bestls),('minimax',bestmm)]:
 bases={k:basis.radial(g['t'],g['ny'],best['widthCSS'],best['exponent']) for k,g in geo.items()}
 for r in records:r['radial']=bases[r['geometry']]
 rows=score(np.array(best[method]['coefficients']),method)
 with (output/(method+'-bins.json.gz')).open('xb') as f:f.write(gzip.compress(json.dumps(rows,allow_nan=False).encode(),mtime=0))
with (output/'summary.json').open('x') as f:json.dump(dict(endpoint=a.endpoint,inventorySha256=manifest['inventorySha256'],
    cacheManifestSha256=hashlib.sha256((cache/'manifest.json').read_bytes()).hexdigest(),
    runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
    cacheSealSha256=hashlib.sha256(sealpath.read_bytes()).hexdigest() if sealpath.exists() else None,
    runnerSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    fits=len(trials),fitCells=sorted({r['cell'] for r in cal}),sharedScales=[1,2],bestLeastSquares=bestls,bestMinimax=bestmm,
    seconds=time.monotonic()-started),f,indent=2,allow_nan=False)
