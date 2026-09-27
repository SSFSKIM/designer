"""Synthetic behavior of W41's fixed-strip spatial read, never native pixels."""
import unittest
import numpy as np
import spatial


class SpatialTests(unittest.TestCase):
    def rows(self):
        y=np.r_[np.linspace(-.35,.35,17),np.linspace(-.35,.35,17)]
        x=np.r_[128+18*y[:17],128-18*y[17:]]
        return np.repeat(x[:,None],3,axis=1),np.full((34,3),128.),y

    def test_signed_term_separates_reflected_equal_input_rows(self):
        x,mean,y=self.rows();tone=lambda c:c*.5+20
        local=spatial.predict('S1',[.6],x,mean,y,tone,True)
        signed=spatial.predict('S2',[.6,8.],x,mean,y,tone,True)
        np.testing.assert_allclose(local[:17],local[17:][::-1])
        self.assertGreater(abs(signed[0,0]-signed[-1,0]),5)

    def test_inactive_term_has_no_directional_parameter(self):
        x,mean,y=self.rows();tone=lambda c:c
        with self.assertRaises(ValueError):spatial.predict('S2',[.6,8.],x,mean,y,tone,False)
        np.testing.assert_array_equal(spatial.predict('S2',[.6],x,mean,y,tone,False),spatial.predict('S1',[.6],x,mean,y,tone,False))

    def test_fitting_recovers_independent_blend_and_position(self):
        x,mean,y=self.rows();tone=lambda c:c*.5+20
        target=(.6*x+.4*mean)*.5+20+8*y[:,None]
        result=spatial.fit('S2',x,mean,y,target,np.ones(len(x))/len(x),tone,True)
        for objective in ('leastSquares','minimax'):
            self.assertIsNotNone(result[objective])
            self.assertLess(result[objective]['maximumCodes'],1e-6)
            np.testing.assert_allclose(result[objective]['coefficients'],[.6,8],atol=1e-6)
        self.assertEqual(len(result['starts']),16)

if __name__=='__main__':unittest.main()
