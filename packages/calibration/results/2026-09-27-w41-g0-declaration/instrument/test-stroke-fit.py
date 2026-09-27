"""Planted supplied-path stroke fit; catches an optimizer that reports its seed,
loses a pose, drops the bounded geometry map, or returns an unchecked epigraph."""
import json
import unittest
import numpy as np
import instrument as m
import stroke_fit as f
class StrokeFitTests(unittest.TestCase):
    def test_planted_joint_four_endpoint_fit(self):
        sh=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.))
        xy=np.array([[80,19],[80,64],[140,41],[19,41],[138,31],[138,52],[21,31],[21,52]])
        planted=np.array([1,.4,.3,.5,.2,.15,-.2,.7,12,.65,15,.8,8,.6,16])
        observations=[]
        for endpoint in range(4):
            for level in [64,128,180]:
                g=m.samples(sh,xy,1)
                b=np.full((*g['d'].shape,3),level,float)
                o=dict(endpoint=endpoint,g=g,backdrop=b,shadow=b,binids=np.arange(len(xy)),target=None)
                o['target']=f.predict(planted,o,'M0')
                observations.append(o)
        result=f.fit_local(observations,'M0')
        print(json.dumps(result,allow_nan=False))
        self.assertEqual(len(result['starts']),16)
        self.assertIsNotNone(result['leastSquares']);self.assertIsNotNone(result['minimax'])
        self.assertLess(result['leastSquares']['maximumCodes'],1e-5)
        self.assertLess(result['minimax']['maximumCodes'],1e-5)
        self.assertTrue(all(r[k]['parameterFeasible'] for r in result['starts'] for k in ['leastSquares','minimax']))
    def test_all_declared_parameterisations_cover_bounds(self):
        for family,dimension in [('M0',15),('M1',39),('M2',43)]:
            lo,hi,start=f.domain(family)
            self.assertEqual(len(start),dimension)
            for q in [lo,hi,start]:
                for endpoint in range(4):
                    width,beta,gamma,material=f.unpack(q,family,endpoint)
                    self.assertLessEqual(abs(gamma),1-beta+1e-12)
                    if family!='M0':self.assertTrue(np.all(np.diff(material[:8])>=0))
if __name__=='__main__':unittest.main()
