"""One declared baseline start for diagnosing the synthetic minimax failure.

Not a changed production budget, native fit, or substitute for the full proof.
"""
import json
from unittest.mock import patch
import numpy as np
import instrument as m
import stroke_fit as f
sh=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.))
xy=np.array([[80,19],[80,64],[140,41],[19,41],[138,31],[138,52],[21,31],[21,52]])
planted=np.array([1,.4,.3,.5,.2,.15,-.2,.7,12,.65,15,.8,8,.6,16])
obs=[]
for endpoint in range(4):
    for level in [64,128,180]:
        g=m.samples(sh,xy,1);b=np.full((*g['d'].shape,3),level,float)
        o=dict(endpoint=endpoint,g=g,backdrop=b,shadow=b,binids=np.arange(len(xy)),target=None)
        o['target']=f.predict(planted,o,'M0');obs.append(o)
class NoAdditionalStarts:
    def uniform(self,low,high,size):return np.empty((0,size[1]))
with patch.object(f.np.random,'default_rng',return_value=NoAdditionalStarts()):
    result=f.fit_local(obs,'M0')
print(json.dumps(result,indent=2,allow_nan=False))
