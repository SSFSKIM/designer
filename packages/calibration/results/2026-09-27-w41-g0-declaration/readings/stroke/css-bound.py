from analyse import *
from scipy.optimize import linprog
knots=['neutral-40','neutral-56','neutral-72','neutral-88','neutral-104','neutral-128','neutral-150','g255']
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  rr=[filt(base,background=bg,scheme=scheme,pose=pose,scale=1,shell=0,part='straight',bin=12)[0] for bg in knots]
  x=np.array([r['backgroundRGB'][1] for r in rr]);y=np.array([r['native'][1] for r in rr]);X=np.stack([x,np.ones(len(x))],1)
  for name,offsetbound in [('black',(0,0)),('fixedcolour',(0,None)),('unconstrainedAffine',(None,None))]:
   A=np.vstack([np.c_[X,-np.ones(len(x))],np.c_[-X,-np.ones(len(x))]])
   if name=='fixedcolour':A=np.vstack([A,[255,1,0]]);Y=np.r_[y,-y,255]
   else:Y=np.r_[y,-y]
   fit=linprog([0,0,1],A_ub=A,b_ub=Y,bounds=[(0,1),offsetbound,(0,None)],method='highs')
   print(scheme,pose,name,fit.success,fit.x)
