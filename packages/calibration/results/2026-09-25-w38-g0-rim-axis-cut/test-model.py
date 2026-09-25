import unittest
from model import edge,np,params,SCALE

class ExistingLeafLaw(unittest.TestCase):
    def test_literal_held_top_both_scales(self):
        for scheme in ['light','dark']:
            old=params(scheme);new=params(scheme,'C1')
            for scale in [1,2]:
                d=-np.arange(.25,6,.5)/scale;b=edge.decode(np.array([132,173,11])/255)
                p=edge.forward(b,d,1,width=old['widths'][scale-1],a=old['a'],g=old['g'],lit=(np.sqrt(2)*.7071)**.85,along=.97)['encoded']
                q=edge.forward(b,d,1,width=new['widths'][scale-1],a=new['a'],g=new['g'],lit=np.sqrt(2)**.85,along=.97)['encoded']
                np.testing.assert_allclose(p,q,atol=1e-12,rtol=0)
        self.assertNotEqual(SCALE,2**(-.85/2))

    def test_shared_collapsed_and_clear(self):
        for tint in [0,.5,1]:
            collapsed=.038*(1-tint)+.52*tint
            for tone in [0,.5,1]:
                oldlit=(np.sqrt(2)*.7071)**.85;newlit=np.sqrt(2)**.85;a=.08
                old=oldlit*(a*(1-tone)+collapsed*tone)
                new=newlit*(SCALE*a*(1-tone)+collapsed*tone)
                self.assertAlmostEqual(new-old,(newlit-oldlit)*collapsed*tone,places=14)
                angles=np.linspace(0,2*np.pi,101)
                old=np.maximum(abs(-.7071*np.cos(angles)-.7071*np.sin(angles))*np.sqrt(2),1e-6)**0
                new=np.maximum(abs(-np.sin(angles))*np.sqrt(2),1e-6)**0
                np.testing.assert_array_equal(old,new) # actual clear/strong-border lobe
        self.assertAlmostEqual(.02432*newlit,.03265136326761601,places=14)
        self.assertAlmostEqual(.3328*newlit,.44680812892527166,places=14)

    def test_native_precomposition_not_encoded_offset(self):
        body=edge.decode(np.array([[32,32,32],[128,128,128],[180,100,50]])/255)
        d=np.array([-.3,-.7,-1.1]);a=.04;g=.24
        out=edge.forward(body,d,1,a=a,g=g,lit=1)
        got=edge.recover(body,d,1,out['linear'])
        np.testing.assert_allclose(got,[a,g],atol=1e-12,rtol=0)
        altered=edge.forward(body,d,1,a=a+.02,g=g-.04)
        np.testing.assert_allclose(edge.recover(body,d,1,altered['linear']),[a+.02,g-.04],atol=1e-12,rtol=0)
        moved=edge.forward(body*.8,d,1,a=a,g=g)
        # Fixed coefficients on changed baseline are NOT a constant encoded edge.
        self.assertGreater(np.max(abs((moved['encoded']-255*edge.encode(body*.8))-(out['encoded']-255*edge.encode(body)))),.1)
        with self.assertRaises(ValueError):edge.forward(body,d,1,a=a,g=g,coverage=.5)

if __name__=='__main__':unittest.main()
