import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,numpy as np
R=Path('/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-26-w39-g2-identification');sys.path.insert(0,str(R/'instrument'))
import body,fitting
out=Path.home()/'vitrea-w41/grounding/body';data=json.loads((out/'readings.json').read_text());mats=json.loads((R/'resolved-materials.json').read_text()) if (R/'resolved-materials.json').exists() else json.loads((R/'instrument/resolved-materials.json').read_text());all=[]
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  ep=scheme+'-'+('active' if pose=='rest' else 'inactive');m=mats[ep];rows=[r for r in data['rows'] if r['scheme']==scheme and r['pose']==pose and min(r['median'])>5 and max(r['median'])<250];x=np.array([r['input'] for r in rows])/255;y=np.array([r['median'] for r in rows])/255
  fit=fitting.fit(lambda q:body.h2(x,m,q=q),y,np.r_[m['bodyChromaRetention'],m['backdropToneResponseThin']],[(0,1)]*5,monotone_start=1)
  for fam,q in [('H2',None),('H2prime',fit['minimax']['coefficients'])]:
   pred=body.h2(x,m,q=q)*255;es=abs(pred-y*255);res=dict(endpoint=ep,family=fam,maximum=float(es.max()),success=True if q is None else fit['minimax']['converged'],scores=[dict(cell=r['cell'],sid=r['sid'],scale=r['scale'],pred=p.tolist(),native=r['median'],error=e.tolist()) for r,p,e in zip(rows,pred,es)]);all.append(res);print(ep,fam,res['maximum'],res['success'],flush=True)
(out/'h2-calibration.json').write_text(json.dumps(all))
