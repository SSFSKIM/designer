"""Exercise the actual Gauss-Newton step from a deliberately nonoptimal start.

Only the runner's definitions are loaded, avoiding its CLI side effects. No
production function is mocked or replaced, and the clipped forward is the
same function the native run calls.
"""
import ast
from pathlib import Path
import numpy as np
from scipy.optimize import OptimizeResult
import basis
source=Path(__file__).with_name('fit-grid-gn.py')
tree=ast.parse(source.read_text())
functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in ('predict','ls_value','gauss_newton')]
rng=np.random.default_rng(3921);rows=[]
t=np.repeat(rng.uniform(.05,11.8,(180,1)),64,axis=1);ny=np.repeat(rng.uniform(-1,1,(180,1)),64,axis=1)
rad=basis.radial(t,ny,.8,1)
for amplitude in [.01,.4]:
 true=np.sin(np.arange(44)+1)*amplitude;rows=[];clips=0
 for i in range(12):
  b=rng.uniform(.15,.85,3);y=b@np.array([.2126,.7152,.0722]);z=b-y
  colour=np.column_stack((np.ones(3),np.full(3,y),z,y*z))
  raw=b+(rad@true.reshape(11,4))@colour.T;target=np.clip(raw,0,1);clips+=int((raw!=target).sum())
  rows.append(dict(base=np.broadcast_to(b,raw.shape),target=target,radial=rad,colour=colour,weight=np.full(raw.shape,1/(12*raw.size))))
 namespace=dict(np=np,OptimizeResult=OptimizeResult,BOUND=4096,cal=rows)
 exec(compile(ast.Module(body=functions,type_ignores=[]),str(source),'exec'),namespace)
 fit=namespace['gauss_newton'](np.zeros(44))
 print('amplitude',amplitude,'clipped outputs',clips,'iterations',fit.nit,'converged',fit.success,'MSEcodes',fit.fun,'coefficient error',max(abs(fit.x-true)))
 assert fit.success and fit.nit>0 and fit.fun<1e-14
 if amplitude==.4:assert clips>0
