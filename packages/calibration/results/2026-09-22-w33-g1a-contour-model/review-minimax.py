# Independent W33 G1a reviewer artifact, offline, 2026-09-22 (§5.171).
# Preserved scratch script, not a standalone replay: paths/dependencies remain as reviewed.
import pickle,json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from collections import defaultdict,Counter
out=Path('/tmp/w33-g1a-independent-review'); records=pickle.loads((out/'records.pkl').read_bytes());groups=defaultdict(list)
for r in records:
 straight=np.logical_or.reduce([r['sides'][s] for s in ('top','bottom','left','right')])
 for part,mask in [('all',np.ones(len(straight),dtype=bool)),('straight',straight),('arcs',~straight)]:
  groups[tuple(r[k] for k in ('profile','pose','backdropClass','span','kind'))+(part,)].append((r['nx'][mask],r['ny'][mask],(r['n']-r['w'])[mask]))
rows=[]
for key,rs in groups.items():
 nx,ny,delta=[np.concatenate([r[i] for r in rs]) for i in range(3)]
 bins=np.floor(np.mod(np.arctan2(ny,nx),2*np.pi)/(2*np.pi/16)+.5).astype(int)%16; ids=np.unique(bins); masks=[bins==i for i in ids]; y=np.array([delta[mask].mean() for mask in masks]); fits=[]
 families=[('constant',np.ones((len(nx),1)))]
 for k in (.5,1,2,4,8):
  q=abs(nx)**k;families.extend([(f'even-{k:g}',q[:,None]),(f'isotropic-even-{k:g}',np.column_stack((np.ones(len(nx)),q)))])
 families.extend([('one-sided-diagonal',np.maximum(-(nx+ny)/np.sqrt(2),0)[:,None]),('shipped-diagonal-unit-exponent',abs(nx+ny)[:,None]),('signed-normal',np.column_stack((np.ones(len(nx)),nx,ny)))])
 for family,basis in families:
  X=np.array([basis[mask].mean(axis=0) for mask in masks]);z=np.ones((len(y),1));p=X.shape[1]
  fit=linprog(np.r_[np.zeros(p),1],A_ub=np.r_[np.c_[X,-z],np.c_[-X,-z]],b_ub=np.r_[y,-y],bounds=[(None,None)]*p+[(0,None)],method='highs')
  fits.append(dict(law=family,max=fit.fun,coefs=fit.x[:-1].tolist()))
 rows.append(dict(key=key,best=min(fits,key=lambda r:r['max']),fits=fits))
(out/'minimax.json').write_text(json.dumps(rows))
for part in ('all','straight','arcs'):
 rs=[r for r in rows if r['key'][-1]==part];print(part,{t:sum(r['best']['max']<=t+1e-8 for r in rs) for t in (1,3)})
 print('best range',min(r['best']['max'] for r in rs),max(r['best']['max'] for r in rs))
print('new full closures',[r for r in rows if r['key'][-1]=='all' and r['best']['max']<=1+1e-8])
