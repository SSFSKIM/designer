"""Synthetic breaks: wrong units/support, averaging before nonlinear colour,
wrong angular gauge, movable strip, censor erasure and signed cancellation."""
import json
import unittest
import numpy as np
import instrument as m

class InstrumentTests(unittest.TestCase):
    def test_stadium_device_support_at_both_scales(self):
        proof=[]
        for scale in (1,2):
            sh=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.))
            xy=np.array([[80*scale,20*scale-1],[80*scale,20*scale-2],[80*scale,20*scale]])
            g=m.samples(sh,xy,scale)
            c=m.coverage(g,1,0,0)
            np.testing.assert_array_equal(c.mean(1),[1,0,0])
            geo=m.readers.geometry((90*scale,170*scale),[sh],scale)
            yy,xx=np.nonzero(geo.outside & (np.floor(geo.d)==1) & geo.arc)
            arc=m.coverage(m.samples(sh,np.c_[xx,yy],scale),1,0,0).mean(1)
            self.assertGreater(float(arc.max()),0)
            proof.append(dict(scale=scale,straightCoverage=c.mean(1).tolist(),arcShell1Max=float(arc.max())))
        print('stadium',json.dumps(proof))

    def test_css_width_rival_reaches_second_straight_at_two_x(self):
        sh=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.))
        g=m.samples(sh,np.array([[160,38]]),2)
        self.assertEqual(float(m.coverage(g,1,0,0,css_width=False).mean()),0)
        self.assertEqual(float(m.coverage(g,1,0,0,css_width=True).mean()),1)

    def test_max_normal_normalisation_and_invalid_domain(self):
        theta=np.linspace(0,2*np.pi,100001)
        a=m.angular(np.cos(theta),np.sin(theta),.4,.3)
        self.assertLess(abs(float(a.max())-1),1e-8)
        self.assertGreaterEqual(float(a.min()),0)
        with self.assertRaises(ValueError):m.angular(np.array([0]),np.array([1]),.9,.2)

    def test_nonlinear_colour_before_area_average(self):
        sh=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.))
        g=m.samples(sh,np.array([[80,19]]),1)
        b=np.repeat((128+128*(g['q'][...,0]-80.5))[...,None],3,axis=-1)
        q=[0,0,0,0,0,0,22,127]
        pred=m.composite(g,b,b,1,0,0,'M1',q)
        np.testing.assert_allclose(pred,16,rtol=0,atol=1e-12)
        print('nonlinear-before-average',pred.tolist(),'wrong-after-average',0)

    def test_m2_neutral_identity_and_held_luma(self):
        b=np.array([[90,90,90],[32,192,32]],float)
        knots=[20,30,40,50,60,80,100,180]
        base=m.material(b,'M1',knots)
        corrected=m.material(b,'M2',knots+[5,.02],dark=True)
        np.testing.assert_allclose(corrected[0],base[0],atol=1e-10)
        np.testing.assert_allclose(m.body.decode(corrected/255)@m.body.W,m.body.decode(base/255)@m.body.W,atol=1e-12)
        self.assertTrue(np.all((corrected>=0)&(corrected<=255)))

    def test_strip_uses_fixed_rows_medians_and_reference(self):
        counts=[]
        for scale in (1,2):
            sh=m.readers.Shape('capsule-circular',(120.,44.),(100.,118.))
            yy,xx=np.mgrid[:280*scale,:320*scale]
            ref=np.repeat((128+.4*(yy+.5-140*scale)/scale)[...,None],3,axis=-1)
            rgb=ref*.4+100
            # One corrupt centre-column value must not change the declared row median.
            rgb[:,160*scale,:]+=20
            row=m.gradient_strip(np.repeat(rgb[None],7,axis=0),np.repeat(ref[None],7,axis=0),sh,scale)
            expected_y=(np.arange(124*scale,156*scale)+.5)/scale-140
            np.testing.assert_allclose(row['yCSS'],expected_y,atol=0)
            np.testing.assert_allclose(row['native'],.4*np.array(row['reference'])+100,atol=1e-12)
            self.assertEqual(row['pixelsPerRow'],48*scale)
            counts.append(dict(scale=scale,rows=len(row['yCSS']),pixelsPerRow=row['pixelsPerRow'],maximumError=float(np.max(abs(np.array(row['native'])-(.4*np.array(row['reference'])+100))))))
        print('strip',json.dumps(counts))

    def test_absolute_before_reduction_and_mixed_censor(self):
        pred=np.array([[10,99,99],[12,101,101]],float)
        target=np.array([[11,100,100],[11,100,100]],float)
        s=m.score_bin(pred,np.repeat(target[None],7,axis=0),minimum=2)
        np.testing.assert_array_equal(s['median']['errorCodes'],[1,1,1])
        p=np.tile([250,120,120],(4,1));t=np.tile([255,123,120],(4,1))
        s=m.score_bin(p,np.repeat(t[None],7,axis=0))
        self.assertEqual(s['median']['status'],['censored-bound-satisfied','measured','measured'])
        self.assertEqual(s['median']['failed'],[False,True,False])
        self.assertFalse(s['survives']); self.assertFalse(s['heldoutCoverage'])
        self.assertEqual(len(s['runs']),7)
        small=m.score_bin(p[:2],np.repeat(t[None,:2],7,axis=0))
        self.assertEqual(small['median']['status'],['UNMEASURED']*3)

if __name__=='__main__':unittest.main()
