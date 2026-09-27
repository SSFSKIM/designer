"""Catch shadow normal-offset approximation, missing span law and receded paint."""
import unittest
import numpy as np
import instrument as m
import shadow
class ShadowTests(unittest.TestCase):
    def test_receded_exact_zero(self):
        sh=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.))
        q=np.array([[19.5,42],[80,19.5],[80,64.5]])
        for scheme in ('light','dark'):
            np.testing.assert_array_equal(shadow.at(q,sh,1,shadow.materials()[scheme+'-inactive'],.3),0)
    def test_translation_uses_supplied_path_not_normal_extrapolation(self):
        sh=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.))
        mat=shadow.materials()['light-active'];q=np.array([[140.5,42.]])
        actual=shadow.at(q,sh,1,mat,.3)
        # At right apex the unshifted normal has ny=0. The real downward offset
        # moves the sampled point away from the circular centre, unlike d-offset*ny.
        naive=shadow.from_distance(np.array([.5]),44,mat,.3)
        self.assertGreater(abs(float(actual[0]-naive[0])),1e-5)
    def test_scale_covariance_and_far_finiteness(self):
        sh=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.))
        q=np.array([[80,19.5],[80,64.5],[140.5,42],[80,42],[-10000,0]])
        for mat in shadow.materials().values():
            if mat is shadow.materials().get('default'):continue
            a=shadow.at(q,sh,1,mat,.3);b=shadow.at(q*2,sh,2,mat,.3)
            np.testing.assert_allclose(a,b,rtol=0,atol=1e-15)
            self.assertTrue(np.all(np.isfinite(a)))
if __name__=='__main__':unittest.main()
