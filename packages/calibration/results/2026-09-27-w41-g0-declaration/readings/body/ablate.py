import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,numpy as np
R=Path('/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-26-w39-g2-identification');sys.path[:0]=[str(R/'instrument'),str(R/'body-correction')]
import body
from solver import solve_h3
from scipy.optimize import least_squares
out=Path.home()/'vitrea-w41/grounding/body';data=json.loads((out/'readings.json').read_text());fits=json.loads((out/'h3.json').read_text())
result=[]
for f in fits:
 rows=[r for r in data['rows'] if r['scheme']==f['scheme'] and r['pose']==f['pose'] and not r['sid'].startswith(('red-','green-'))]
 x=np.array([r['input'] for r in rows])/255;y=np.array([r['median'] for r in rows]);neutral=np.array(f['neutral'])/255
 fit=solve_h3(x,neutral,y)
 allrows=[r for r in data['rows'] if r['scheme']==f['scheme'] and r['pose']==f['pose']];xx=np.array([r['input'] for r in allrows])/255;pred=body.h3(xx,neutral,fit['coefficients'])*255
 scores=[dict(cell=r['cell'],sid=r['sid'],pred=p.tolist(),native=r['median'],residual=(p-r['median']).tolist()) for r,p in zip(allrows,pred)]
 # CSS optimistic constant affine encoded matrix (more flexible than saturate + rgba).
 A=np.column_stack([x,np.ones(len(x))]);coef=np.linalg.lstsq(A,y,rcond=None)[0];css=A@coef-y
 # Genuine two-layer encoded neutral model slope+intercept; chromatic saturate factor, constant neutral alpha.
 # y = a*x + b*encoded_luma(x) + c ; identical c in channels.
 W=np.array([.2126,.7152,.0722]);design=np.stack([x,np.repeat((x@W)[:,None],3,axis=1),np.ones_like(x)],-1).reshape(-1,3)
 cscoef=np.linalg.lstsq(design,y.ravel(),rcond=None)[0];csp=(design@cscoef).reshape(-1,3)-y
 print(f['scheme'],f['pose'],'no-bridge H3',fit['upperCodes'],'CSS affine max',abs(css).max(),'CSS isotropic max',abs(csp).max(),flush=True)
 for z in scores:
  if ('red-colour' in z['sid'] or 'green-colour' in z['sid']) and '1x' in z['cell']:print(z,flush=True)
 result.append(dict(scheme=f['scheme'],pose=f['pose'],fit=fit,scores=scores,cssAffineMax=float(abs(css).max()),cssIsotropicMax=float(abs(csp).max())))
(out/'ablations.json').write_text(json.dumps(result))
