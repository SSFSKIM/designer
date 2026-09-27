"""Step 2: seven neutral ordinates from calibration only, shared across scales."""
import argparse
import json
import sys
import numpy as np
import native

p=argparse.ArgumentParser();p.add_argument('archive');args=p.parse_args()
w,r=native.guarded(args.archive,('calibration',))
selected=sorted(c for c,k in r.entries if k=='crop' and c.split('/',1)[1] in r.allowed
    and c.split('/',1)[1].startswith('neutral-') and '-colour__' in c)
rows=[native.cell(r,c) for c in selected]
assert len(rows)==56
out=[]
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  knots=[]
  for code in [40,56,72,88,104,128,150]:
   rr=[x for x in rows if x['scheme']==scheme and x['pose']==pose
       and x['cell'].split('/',1)[1].startswith(f'neutral-{code}-colour__')]
   assert len(rr)==2 and {x['scale'] for x in rr}=={1,2}
   values=np.array([x['members'][0]['medianRGB'] for x in rr])
   ls=float(values.mean());mm=float((values.max()+values.min())/2)
   knots.append(dict(inputCode=code,leastSquaresCode=ls,minimaxCode=mm,
       bars=[x['members'][0]['barRGB'] for x in rr],cells=[x['cell'] for x in rr],
       leastSquaresResidualRGB=(ls-values).tolist(),minimaxResidualRGB=(mm-values).tolist()))
  out.append(dict(scheme=scheme,pose=pose,knots=knots,rank=7,columns=7,
     singularValues=[float(np.sqrt(6))]*7,
     extrapolation='End-segment encoded continuation and unit-cube clip at bridge inputs32/192; no validation extension.'))
print(json.dumps(dict(archive=str(r.root),inventorySha256=r.generation,rawRootDenied=str(native.Path.home()/'vitrea-w39'),
                     roles=['calibration'],rows=rows,curves=out),indent=2,allow_nan=False))
