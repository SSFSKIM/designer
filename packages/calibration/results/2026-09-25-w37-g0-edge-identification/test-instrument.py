"""Executable breaks: non-unit composition, outside support and baseline absorption."""
import unittest
import numpy as np
import law

class Forward(unittest.TestCase):
    def setUp(self):
        self.shape=dict(width=2.,shoulder=6.,share=.15,exponent=2.)
        self.coeff=np.array([.02,.1,.3,.2,-.01])
    def test_encoded_hand_calculation(self):
        body=np.array([.1,.2,.3]); Y=.18596
        f=.85*.75**2+.15*(11/12)**2
        expected=body+f*(.02+.1*Y+(.3+.2*Y)*(body-Y))-.01*(11/12)**2*body
        out=law.forward(body,np.array([-.5]),np.array([1.]),self.shape,self.coeff,'encoded')
        np.testing.assert_allclose(out['encoded'][0],expected*255,atol=1e-11)
    def test_refuses_fractional_composition(self):
        for key in ['alpha','coverage']:
            for value in [.5,np.array([1.,.5])]:
                with self.assertRaises(ValueError):
                    law.forward(np.ones(3)*.2,np.array([-1.,-2.]),np.ones(2),self.shape,self.coeff,'linear',**{key:value})
    def test_compact_support_and_zero_coefficients(self):
        b=np.array([.1,.2,.3]);d=np.array([-7.,-6.,0.,1.])
        for space in ['encoded','linear']:
            out=law.forward(b,d,np.ones(4),self.shape,self.coeff,space)
            expected=b*255 if space=='encoded' else law.edge.encode(b)*255
            np.testing.assert_allclose(out['encoded'],np.tile(expected,(4,1)),atol=1e-11)
    def test_precomposition_interventions(self):
        rng=np.random.default_rng(37);b=rng.uniform(.08,.6,(80,3));d=rng.uniform(-5.9,-.1,80);ny=rng.uniform(-1,1,80)
        for space in ['encoded','linear']:
            x=law.features(b,d,ny,self.shape,space)
            target=law.forward(b,d,ny,self.shape,self.coeff,space)['unclipped']
            recovered=np.linalg.lstsq(x.reshape(-1,5),(target-b).ravel(),rcond=None)[0]
            np.testing.assert_allclose(recovered,self.coeff,atol=1e-12)
            shifted=b+.03
            moved=law.forward(shifted,d,ny,self.shape,self.coeff,space)['unclipped']-shifted
            self.assertGreater(float(np.max(abs(moved-(target-b)))),.0001)
            new=self.coeff+np.array([.001,.002,-.003,.004,.005])
            changed=law.forward(b,d,ny,self.shape,new,space)['unclipped']
            np.testing.assert_allclose(np.linalg.lstsq(x.reshape(-1,5),(changed-b).ravel(),rcond=None)[0],new,atol=1e-12)

if __name__=='__main__':unittest.main()
