# Independent W33 G1a reviewer artifact, offline, 2026-09-22 (§5.171).
# Preserved scratch script, not a standalone replay: paths/dependencies remain as reviewed.
from pathlib import Path
import pickle,json,numpy as np
from scipy.optimize import least_squares
out=Path('/tmp/w33-g1a-independent-review');ev=Path('/Users/new/Developer/GitHub/designer/.claude/worktrees/w33-g1a-contour-model/packages/calibration/results/2026-09-22-w33-g1a-contour-model')
rs=pickle.loads((out/'records.pkl').read_bytes());ts=json.loads((ev/'targets.json').read_text())['rows'];targets={(r['profile'],r['scene']):np.array(r['rgb']) for r in ts}
def decode(x):return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
def encode(x):return np.where(x<=.0031308,12.92*x,1.055*np.maximum(x,0)**(1/2.4)-.055)
for scheme,pose,cls in [('light','rest','photo'),('light','inactive','black-bearing'),('dark','rest','dark-solid')]:
 rr=[r for r in rs if r['profile']==f'apple-macos-27.0-1x-{scheme}-standard-glass0.5' and r['pose']==pose and r['backdropClass']==cls]
 n,w,nx=[np.concatenate([r[k] for r in rr]) for k in ('n','w','nx')];pred=np.concatenate([targets[(r['profile'],r['scene'])] for r in rr]);print(scheme,pose,cls,'candidate',np.abs(n-pred).mean(axis=0))
 # A physical fixed tinted blend over the final composited web colour; opposite
 # angular endpoints share a single RGB source and interpolated alpha.
 for space in ('encoded','linear'):
  x,y=w/255,n/255
  if space=='linear':x,y=decode(x),decode(y)
  q=abs(nx)[:,None]**(2 if scheme=='dark' and pose=='rest' else 8)
  def predict(v):
   a=(1-q)*v[0]+q*v[1];return (1-a)*x+a*v[2:5]
  def fun(v):return (predict(v)-y).ravel()
  best=min((least_squares(fun,v,bounds=(0,1),max_nfev=200) for v in ([.3,.5,.2,.2,.2],[.5,.7,.6,.6,.6])),key=lambda f:f.cost)
  p=predict(best.x); p=255*(encode(p) if space=='linear' else p)
  print('fixed colour',space,'alpha0/alpha1/c',best.x,'MAE RGB',abs(n-p).mean(axis=0))
