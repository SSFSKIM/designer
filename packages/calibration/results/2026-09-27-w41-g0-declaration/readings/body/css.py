import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,numpy as np
from scipy.optimize import linprog
p=Path.home()/'vitrea-w41/grounding/body';data=json.loads((p/'readings.json').read_text());out=[]
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  rr=[r for r in data['gradients'] if r['scheme']==scheme and r['pose']==pose]
  x=np.concatenate([np.array(r['reference']).ravel() for r in rr]);y=np.concatenate([np.array(r['median']).ravel() for r in rr]);A=np.column_stack([x,np.ones(len(x))]);con=np.concatenate([np.column_stack([A,-np.ones(len(x))]),np.column_stack([-A,-np.ones(len(x))]),[[255,1,0]]]);rhs=np.r_[y,-y,255]
  r=linprog([0,0,1],A_ub=con,b_ub=rhs,bounds=[(0,1),(0,255),(0,None)],method='highs');assert r.success
  out.append(dict(scheme=scheme,pose=pose,maximum=r.x[-1],slope=r.x[0],intercept=r.x[1]));print(out[-1])
(p/'css-gradient-projection.json').write_text(json.dumps(out))
