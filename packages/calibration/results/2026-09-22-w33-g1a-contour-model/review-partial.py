# Independent W33 G1a reviewer artifact, offline, 2026-09-22 (§5.171).
# Preserved scratch script, not a standalone replay: paths/dependencies remain as reviewed.
import json,pickle
from pathlib import Path
from collections import defaultdict
import numpy as np
out=Path('/tmp/w33-g1a-independent-review');ev=Path('/Users/new/Developer/GitHub/designer/.claude/worktrees/w33-g1a-contour-model/packages/calibration/results/2026-09-22-w33-g1a-contour-model')
rs=pickle.loads((out/'records.pkl').read_bytes()); bounds=json.loads((ev.parent/'2026-09-22-w33-g0-rim-cut/tables.json').read_text())['bounds'];boundMap={tuple(r[k] for k in ('profile','pose','backdropClass','side')):r['bound'] for r in bounds}
N,W,B,A,NX=[np.concatenate([r[k] for r in rs]) for k in ('n','w','b','a','nx')]; D=N-W; groups={};beg=0; schemeGroups=defaultdict(list)
for r in rs:
 count=len(r['n']);r['index']=np.arange(beg,beg+count);beg+=count
 scheme=('dark' if '-dark-' in r['profile'] else 'light',r['pose']) if 'standard' in r['profile'] else ('accessibility',r['pose'])
 schemeGroups[scheme].extend(r['index']);cls=r['backdropClass'] if r['backdropClass'] in ('photo','light-solid','black-bearing') else 'dark-or-other-solid'
 for side,mask in r['sides'].items():groups.setdefault((r['profile'],r['pose'],cls,side),[]).extend(r['index'][mask])
keys=list(groups); gids=np.empty(len(N),int)
for i,k in enumerate(keys):gids[np.array(groups[k])]=i
counts=np.bincount(gids);bars=np.array([boundMap[k] for k in keys]);baseErrors=np.bincount(gids,weights=abs(D).mean(axis=1))/counts
assert np.all(baseErrors<=bars)
def cap(T):
 needed=np.maximum(np.max(np.where(T<B,(B-T)/np.maximum(B,1),0),axis=1),np.max(np.where(T>B,(T-B)/np.maximum(255-B,1),0),axis=1))
 a=np.maximum(A,np.ceil(needed*255-1e-10)/255);a=np.where(A<.5,np.minimum(127/255,a),a)
 p=T-(1-a[:,None])*B;source=np.floor(np.clip(p,0,255*a[:,None])/np.maximum(a[:,None],1e-12)+.5)
 return np.floor(source*a[:,None]+(1-a[:,None])*B+.5)
def score(P):
 err=abs(N-P).mean(axis=1);errs=np.bincount(gids,weights=err)/counts
 return err.mean(),errs
baseline=abs(N-W).mean();print('baseline',baseline,'pixels',len(N))
results=[]
# Existing falsified target + the cap, attenuated independently only by scheme/pose.
targets=json.loads((ev/'targets.json').read_text())['rows'];tm={(r['profile'],r['scene']):np.array(r['rgb']) for r in targets};candidate=np.concatenate([tm[(r['profile'],r['scene'])] for r in rs])
for name,k in [('candidate',None),('isotropic',None),('active-even-2',2),('active-even-4',4),('active-even-8',8)]:
 delta=np.zeros_like(N)
 for group,ids in schemeGroups.items():
  ix=np.array(ids)
  if group[0]=='accessibility':continue
  if name=='candidate':delta[ix]=candidate[ix]-W[ix];continue
  if name.startswith('active') and group[1]!='rest':continue
  q=np.ones(len(ix)) if name=='isotropic' else abs(NX[ix])**k
  for c in range(3):
   X=np.column_stack((q*W[ix,c],q));coef=np.linalg.lstsq(X,D[ix,c],rcond=None)[0];delta[ix,c]=X@coef
 bestP=W.copy();settings={}
 for group,ids in schemeGroups.items():
  if group[0]=='accessibility' or (name.startswith('active') and group[1]!='rest'):continue
  ix=np.array(ids);groupmask=np.array(['standard' in kk[0] and ('dark' if '-dark-' in kk[0] else 'light')==group[0] and kk[1]==group[1] for kk in keys])
  best=(abs(N[ix]-W[ix]).mean(),0,W[ix])
  for strength in np.linspace(0,1,201)[1:]:
   # Only this scheme/pose differs, so G0's per-profile ceilings remain independent.
   T=np.floor(np.clip(W+strength*delta,0,255)+.5);P=cap(T);mae,errs=score(P)
   if np.all(errs[groupmask]<=bars[groupmask]+1e-10):
    loss=abs(N[ix]-P[ix]).mean()
    if loss<best[0]:best=(loss,strength,P[ix])
  bestP[ix]=best[2];settings[str(group)]={'strength':best[1],'mae':best[0],'baseline':abs(N[ix]-W[ix]).mean()}
 mae,errs=score(bestP);result=dict(name=name,mae=mae,misses=int((errs>bars+1e-10).sum()),settings=settings)
 results.append(result);print(result,flush=True)
(out/'partial.json').write_text(json.dumps(results))
