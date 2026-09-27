"""Supplementary minimax certificates and negative controls, no native inputs."""
import json
from pathlib import Path
import numpy as np
import body, edge_law

rng=np.random.default_rng(3902);b=rng.uniform(.2,.7,(200,3));back=rng.uniform(.1,.6,(200,3))
d=-rng.uniform(.05,11.8,200);ny=rng.uniform(-1,1,200)
rad=edge_law.radial(d,ny,rng.choice([1,2],200),1.4,2)
x=edge_law.features(b,rad);true=np.sin(np.arange(44)+1)*.01
y=edge_law.forward(b,rad,true)
q,_,rank,sv=np.linalg.lstsq(x.reshape(-1,44),(y-b).ravel(),rcond=None)
r=edge_law.forward(b,rad,q)-y
extra=edge_law.h4(b,back,rad,[.08,-.04])
# A reflected straight pair forces equality for every even-only coefficient.
paired=edge_law.radial(np.array([-.5,-.5]),np.array([-1.,1.]),np.ones(2),1.4,2)
observations=.5+.2*paired[:,1]
floor=float(abs(np.diff(observations)[0])*255/2)
ms=json.loads((Path(__file__).parent/'resolved-materials.json').read_text())
colour=rng.uniform(40,150,(100,3))/255
neg=[]
for ep,m in ms.items():
 if ep=='default':continue
 true=np.r_[.8,np.array(m['backdropToneResponseThin'])*.97+.006]
 miss=float(abs(body.h2(colour,m)-body.h2(colour,m,q=true)).max()*255)
 assert miss>1
 neg.append(dict(endpoint=ep,wrongExactH2OnH2primeMaximumCodes=miss))
assert floor>1 and np.max(abs(extra))*255>1
print(json.dumps(dict(nativeReads=0,edge=dict(leastSquaresRSS=float(np.sum(r*r)),minimaxMaximum=float(abs(r).max()),
 coefficients=q.tolist(),rank=int(rank),singularValues=sv.tolist(),
 minimaxCertificate='A feasible prediction with maximum below 1e-14 attains the nonnegative objective lower bound to arithmetic precision; no regularisation.',
 wrongEvenFamilyMinimaxFloorCodes=floor),H4WrongZeroBoundaryMaximumCodes=float(abs(extra).max()*255),H2negatives=neg),indent=2))
