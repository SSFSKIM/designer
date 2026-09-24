"""Catch signed cancellation, selected-state bars and hidden pre-rim conditioning."""
import unittest
import numpy as np
from edge import bar, forward, recover, whole_pixel, decode

class Arithmetic(unittest.TestCase):
    def test_absolute_before_average_and_all_runs(self):
        images=[np.array([[0.,2.,0.],[2.,0.,0.]]),np.array([[2.,0.,0.],[0.,2.,0.]])]
        np.testing.assert_array_equal(bar(images),[2,2,0])
        np.testing.assert_array_equal(bar([images[0],images[0],images[1]]),[2,2,0])

    def test_shadow_conditioning_not_deep_or_final_level(self):
        out=forward(np.array([[.2,.2,.2]]),np.array([-.5]),1,a=.1,g=.4,width=2,
                    shadow_alpha=.2,shadow_depth=.5,shadow_reach=4)
        k=1-.1*(1-.5/4)**2
        self.assertAlmostEqual(out['level'][0],.2*k)
        self.assertAlmostEqual(out['linear'][0,0],.2*k+(1-.5/2)**2*(.1+.4*.2*k))

    def test_forward_refuses_translucent_or_partial_coverage_inputs(self):
        # The runtime encodes before coverage premultiplication. This helper
        # models only the opaque, fully covered branch used by the frozen cut.
        for options in [dict(alpha=.5), dict(coverage=.5),
                        dict(alpha=np.array([1., .5])), dict(coverage=np.array([1., .5]))]:
            with self.subTest(options=options):
                with self.assertRaisesRegex(ValueError, 'opaque full-coverage'):
                    forward(np.ones((2,3)),np.full(2,-.5),1,shadow_alpha=0,**options)

    def test_opaque_full_coverage_still_encodes_white_as_255(self):
        out=forward(np.ones((1,3)),np.array([-.5]),1,shadow_alpha=0,alpha=1,coverage=1)
        np.testing.assert_array_equal(out['linear'],np.ones((1,3)))
        np.testing.assert_allclose(out['encoded'],np.full((1,3),255),rtol=0,atol=1e-12)

    def test_recovery_discriminates_baseline_from_coefficient_change(self):
        b=np.repeat(np.array([.03,.12,.3,.55])[:,None],3,axis=1);d=np.full(4,-.5)
        options=dict(width=2,shadow_alpha=.1,shadow_depth=.35,shadow_reach=6)
        out=forward(b,d,1,a=.07,g=.23,**options)
        np.testing.assert_allclose(recover(b,d,1,out['linear'],**options),[.07,.23],atol=1e-10)
        shifted=forward(b+.03,d,1,a=.07,g=.23,**options)
        np.testing.assert_allclose(recover(b+.03,d,1,shifted['linear'],**options),[.07,.23],atol=1e-10)
        self.assertGreater(np.max(abs((out['linear']-b)-(shifted['linear']-(b+.03)))),.001)
        changed=forward(b,d,1,a=.1,g=.23,**options)
        np.testing.assert_allclose(recover(b,d,1,changed['linear'],**options),[.1,.23],atol=1e-10)

if __name__=='__main__':unittest.main()
