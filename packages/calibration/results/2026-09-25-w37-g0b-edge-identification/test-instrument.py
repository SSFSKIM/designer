"""Catch centre sampling, coupled tail signs, baseline absorption and missing sides."""
import unittest
import numpy as np
import law

class Instrument(unittest.TestCase):
    def test_integrated_ramp_grey128(self):
        shape={'width':1.4,'exponent':2}
        def line(scale, depths):
            r={'d':np.array(depths),'nx':np.zeros(len(depths)),'ny':np.ones(len(depths)),
               'arc':np.zeros(len(depths),bool),'span':44,'scale':scale}
            return law.radial(r,shape,'F1')[:,0]*37.6
        one=line(1,[-.5]);two=line(2,[-.75,-.25])
        np.testing.assert_allclose(one,[24.17142857142857],atol=1e-12)
        np.testing.assert_allclose(two,[17.45714285714286,30.885714285714286],atol=1e-12)
        self.assertLess(max(abs(two-[18,31])),1)
        self.assertLess(abs(one[0]-24),1)
        self.assertAlmostEqual(one[0],two.mean())

    def test_signed_tail_and_identity(self):
        r={'d':np.array([-5.75,-5.25,-.25,-13]),'nx':np.zeros(4),'ny':np.ones(4),
           'arc':np.zeros(4,bool),'span':44,'scale':2}
        for family in ['F1','F2','F3']:
            x=law.features(np.array([.5,.5,.5]),law.radial(r,{'width':1.4,'exponent':2},family),family)
            c=np.zeros(x.shape[-1]); stride=law.stride(family);c[3*stride]=-.02
            out=law.forward(np.array([.5,.5,.5]),x,c,r['d'])
            self.assertTrue(np.all(out[:2]<127.5))
            self.assertTrue(np.all(out[-1]==127.5))
            np.testing.assert_allclose(law.forward(np.array([.5]*3),x,c*0,r['d']),127.5,atol=1e-12)

    def test_synthetic_precomposition(self):
        rng=np.random.default_rng(731)
        for family in ['F1','F2','F3']:
            b=rng.uniform(.2,.7,(200,3));r=rng.uniform(0,.2,(200,7))
            x=law.features(b,r,family); c=rng.uniform(-.01,.01,x.shape[-1])
            y=x@c; recovered=np.linalg.lstsq(x.reshape(-1,len(c)),y.ravel(),rcond=None)[0]
            np.testing.assert_allclose(recovered,c,atol=1e-10)
            delta=law.features(b+.1,r,family)@c-y
            self.assertGreater(np.max(abs(delta)),1e-5)
            changed=c.copy();changed[1]+=.02
            recovered2=np.linalg.lstsq(x.reshape(-1,len(c)),(x@changed).ravel(),rcond=None)[0]
            np.testing.assert_allclose(recovered2,changed,atol=1e-10)
            for alpha,coverage in [(0.5,1),(1,.5)]:
                with self.assertRaises(ValueError):law.forward(b,x,c,np.zeros(200),alpha=alpha,coverage=coverage)

if __name__=='__main__':unittest.main()
