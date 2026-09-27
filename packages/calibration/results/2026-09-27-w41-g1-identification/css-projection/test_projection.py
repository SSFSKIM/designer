"""Pure tests: reversing filters, dropping clamps or accepting invalid domains must fail."""
import unittest
import numpy as np
import projection as p


class Algebra(unittest.TestCase):
    def test_contrast_then_brightness_matches_affine_even_when_output_clips(self):
        for g,k in [(1,0),(.94,.35),(2,.1),(0,.6),(.3,1.2)]:
            route=p.affine_route(g,k)
            x=np.linspace(0,1,1001)
            np.testing.assert_allclose(p.affine_output(x,route),np.clip(g*x+k,0,1),atol=1e-14)

    def test_order_is_observable(self):
        route=p.affine_route(.75,.375)
        self.assertEqual(route,{'brightness':1.5,'contrast':.5})
        self.assertAlmostEqual(float(p.affine_output(np.array([0.]),route)[0]),.375)
        self.assertNotEqual(.375,float(np.clip(.5*np.clip(1.5*0,0,1)+.25,0,1)))

    def test_domain_rejected_not_repaired(self):
        for g,k in [(-1,1),(1,-.01),(0,0),(float('nan'),1),(1,float('inf'))]:
            with self.assertRaises(ValueError):p.affine_route(g,k)

    def test_minimum_white_plate_is_exact_before_saturation_clip(self):
        route=p.plate_route(.4,.7,.94)
        self.assertAlmostEqual(route['alpha'],.5)
        self.assertAlmostEqual(route['saturation'],1.88)
        x=np.array([.3,.4,.5]); l=float(x @ p.CSS_W)
        route=p.plate_route(l,.7,.94)
        np.testing.assert_allclose(p.plate_output(x,route),.7+.94*(x-l),atol=1e-14)

    def test_saturation_clip_is_retained_as_residual(self):
        x=np.array([0.,1.,0.]);l=float(x @ p.CSS_W)
        route=p.plate_route(l,.94,.94)
        actual=p.plate_output(x,route)
        ideal=np.clip(.94+.94*(x-l),0,1)
        self.assertGreater(actual[0]-ideal[0],.1)

    def test_plate_refuses_singular_or_invalid_domain(self):
        for args in [(.7,0.,.9),(.5,1.,.9),(.2,.6,-1),(-.1,.2,.9)]:
            with self.assertRaises(ValueError):p.plate_route(*args)

    def test_minimum_black_plate_carries_downward_shift(self):
        route=p.plate_route(1.,.94,.938)
        self.assertEqual(route['plate'],0)
        self.assertEqual(route['side'],'black')
        self.assertAlmostEqual(route['alpha'],.06)
        np.testing.assert_allclose(p.plate_output(np.array([1.,1.,1.]),route),[.94]*3)

    def test_equal_luma_has_no_plate_at_both_endpoints(self):
        for l in (0.,.5,1.):
            route=p.plate_route(l,l,.94)
            self.assertEqual(route['alpha'],0)
            self.assertEqual(route['side'],'none')
            self.assertEqual(route['saturation'],.94)

    def test_frozen_tuple_uses_encoded_luma_and_continues_end_segments(self):
        params={'neutral':[150,157,164,171,178,188,197],
                'coefficients':[.929205829365914,.9597570955316058,.9383102545096953]}
        l,f,g=p.e3_terms([0,0,0],params)
        self.assertEqual(l,0)
        self.assertAlmostEqual(f*255,132.5)
        self.assertEqual(g,params['coefficients'][0])
        l,f,g=p.e3_terms([128,128,128],params)
        self.assertAlmostEqual(f*255,188)
        self.assertAlmostEqual(l*255,128)


if __name__=='__main__':unittest.main()
