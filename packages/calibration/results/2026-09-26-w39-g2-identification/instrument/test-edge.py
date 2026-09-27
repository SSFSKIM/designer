"""The signed basis must distinguish paired normals; its support and integration matter."""
import unittest
import numpy as np
import edge_law

class EdgeTests(unittest.TestCase):
    def test_area_integration_recovers_two_scale_straight_ramp(self):
        r=edge_law.radial(np.array([-.5,-.25,-.75]),np.array([-1.,-1.,-1.]),np.array([1,2,2]),1.4,1,8)
        # Analytic means: 1-(.5,.25,.75)/1.4. All samples are inside the ramp.
        np.testing.assert_allclose(r[:,0],1-np.array([.5,.25,.75])/1.4,atol=1e-14)
        self.assertAlmostEqual(r[0,0],np.mean(r[1:,0]),places=14)
    def test_signed_normal_and_h4_deep_identity(self):
        d=np.array([-.5,-.5,-6.,-12.]);ny=np.array([-1.,1.,-1.,-1.]);scales=np.ones(4)
        r=edge_law.radial(d,ny,scales,1.4,2,8)
        self.assertGreater(r[0,1],0);self.assertEqual(r[1,1],0)
        b=np.tile([.4,.5,.6],(4,1));back=np.tile([.2,.3,.4],(4,1))
        extra=edge_law.h4(b,back,r,np.array([.1,.2]))
        np.testing.assert_array_equal(extra[2:],np.zeros((2,3)))
    def test_width_two_duplicates_first_shoulder_hat(self):
        d=-np.linspace(.1,11,100);n=np.linspace(-1,1,100)
        r=edge_law.radial(d,n,np.ones(100),2,3,8)
        np.testing.assert_allclose(r[:,0],r[:,5],atol=1e-14)
        np.testing.assert_allclose(r[:,1],r[:,8],atol=1e-14)

if __name__=='__main__':unittest.main()
