#!/usr/bin/env python3.12
"""Synthetic checks of the identifying reader, not fitted-native assertions."""
import unittest
import numpy as np
import identification as M


class Identification(unittest.TestCase):
    def test_minimax_does_not_mean_cancel_and_uses_calibration_only(self):
        X = np.ones((4, 1))
        y = np.array([0., 0., 0., 8.])
        ls = M.fit(X, y, 'least-squares')
        mm = M.fit(X, y, 'minimax')
        self.assertAlmostEqual(ls[0], 2)
        self.assertAlmostEqual(mm[0], 4)
        self.assertAlmostEqual(np.max(np.abs(y-X@mm)), 4)

    def test_integrated_band_and_body_do_not_multiply_averages(self):
        component = {'kind':'capsule-circular','size':[120,44],
                     'suppliedPaths':[{'frameOrigin':[100,78],'elements':[]}]}
        result = M.coverage(np.array([[160,77],[160,78]]), component, 1, (0,.25))
        np.testing.assert_allclose(result['body'], [0,.75])
        np.testing.assert_allclose(result['band'], [.75,.25])
        # A half-alpha black stroke over D=128, B=180. The outside
        # band never overlaps the body, even within a partially covered pixel.
        predicted = 128 + result['body']*52 - result['band']*64
        np.testing.assert_allclose(predicted, [80,151])

    def test_channel_absolute_before_reduction_and_population(self):
        row = M.bin_residual(np.array([[4.,-4,0],[-4,4,0]]), np.zeros((2,3)),
                             np.zeros((2,3)), np.zeros(3))
        self.assertEqual(row['maeRGB'], [4,4,0])
        self.assertFalse(row['admissible'])
        self.assertEqual(row['status'], 'unmeasured: population below four')

    def test_forward_matches_declared_compositor_on_curved_partial_pixels(self):
        import forward as F
        component={'kind':'capsule-circular','size':[120,44],
                   'suppliedPaths':[{'frameOrigin':[100,78],'elements':[]}]}
        xy=np.array([[99,99],[100,89],[219,100],[107,84]])
        cov=M.coverage(xy,component,1,(.125,-.0625))
        r=dict(component=component,scale=1,xy=xy,D=np.tile([128.,192.,64.],(4,1)),
               body=dict(betaRGB=[180.,200.,120.],uncertaintyRGB=[.5,.5,.5]))
        for space in ['encoded','linear']:
            base=F.baseline(r,space,(.125,-.0625),cov=cov)[0]
            target=np.array([50.,70.,90.])/255
            if space=='linear':target=M.decode(target)
            coefs=[[-.4,.4*target[c]] for c in range(3)]
            got=np.floor(F.prediction(r,dict(space=space,name='body-forward-affine',power=2.),coefs,cov,base)+.5)
            field=lambda rgb:lambda x,y:np.tile(rgb,(len(x),1))
            expected=M.I.forward_circular(xy,component,1,field([128,192,64]),field([180,200,120]),
                lambda x,y,nx,ny:(np.full(len(x),.4),np.tile([50,70,90],(len(x),1))),
                translation=(.125,-.0625),space=space)
            np.testing.assert_array_equal(got,expected)

    def test_physical_alpha_identifies_one_shared_alpha_and_bounded_target(self):
        import alpha
        colour=np.array([[.1,.2,.3],[.4,.5,.6],[.7,.8,.9]])
        X=np.zeros((3,3,4));X[:,:,0]=-colour
        for c in range(3):X[:,c,c+1]=1
        y=(-.5*colour+np.array([.1,.2,.3])).ravel()
        for method in ['least-squares','minimax']:
            got=alpha.solve(X.reshape(-1,4),y,method)
            np.testing.assert_allclose(got,[.5,.1,.2,.3],atol=1e-5)
            self.assertTrue(np.all(got[1:]<=got[0]+1e-8))

    def test_reference_interval_uses_body_and_stroke_weights(self):
        import forward as F
        r=dict(D=np.full((3,3),128.))
        cov=dict(body=np.array([1.,0.,0.]),band=np.array([0.,1.,1.]))
        nominal=np.full((3,3),128.)
        spec=dict(space='encoded',name='body-forward-affine')
        physical=F.reference_uncertainty(r,spec,[[-.4,.2]]*3,cov,nominal)
        np.testing.assert_allclose(physical[:,0],[0,.3,.3],atol=1e-12)
        amplified=F.reference_uncertainty(r,spec,[[2.,0]]*3,cov,nominal)
        np.testing.assert_allclose(amplified[:,0],[0,1.5,1.5],atol=1e-12)


if __name__ == '__main__':
    unittest.main()
