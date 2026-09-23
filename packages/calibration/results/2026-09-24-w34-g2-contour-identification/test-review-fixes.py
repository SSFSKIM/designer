#!/usr/bin/env python3.12
"""Regression cases for the three independent-review findings (§5.176)."""
import copy
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np
import identification as M
import forward as F
import fast


class ReviewFixes(unittest.TestCase):
    def test_affine_body_retains_integer_sample_centres_and_partial_integral(self):
        component={'kind':'capsule-circular','size':[120,44],
                   'suppliedPaths':[{'frameOrigin':[100,78],'elements':[]}]}
        y,x=np.mgrid[:200,:320]
        rgb=np.stack([100+40*(x/320-.5)+20*(y/200-.5)]*3,axis=2)
        d,*_=M.I.geometry(320,200,component,1)
        body=M.I.body_baseline(rgb,d,'linear-gradient')
        xy=np.array([[160,100],[160,77]])
        record=dict(cell='synthetic-affine',component=component,scale=1,xy=xy,
                    D=np.full((2,3),128.),body=body)
        cov=M.coverage(xy,component,1,(0,-.25))
        # Fully covered pixel (160,100) must reproduce its fitted sample,100.
        # The partial body lies in y=[77.75,78); its mean image index is77.375.
        expected=np.array([100.,.75*128+.25*(100+20*(77.375/200-.5))])
        for evaluator in [F.baseline,fast.baseline]:
            got=evaluator(record,'encoded',(0,-.25),cov=cov)[0]*255
            np.testing.assert_allclose(got[:,0],expected,atol=1e-10,rtol=0)
        np.testing.assert_allclose(cov['bodyX'],[0,0],atol=1e-14)
        np.testing.assert_allclose(cov['bodyY'],[0,.25*(77.375/200-.5)],atol=1e-14)
        shortcut=fast.coverage(xy,component,1,(0,-.25))
        for name in cov:np.testing.assert_allclose(shortcut[name],cov[name],atol=1e-14)

    def test_w33_gradient_uses_quartic_even_response(self):
        r=dict(nx=np.array([.5]),ny=np.array([np.sqrt(.75)]),gx=np.zeros(1),
               gy=np.zeros(1),D=np.full((1,3),128.),B=np.full((1,3),100.),d=np.array([.5]))
        spec=dict(name='gradient',stage='W33-first',space='encoded',w33Reference=True)
        X,_=M.design(r,spec,0)
        self.assertAlmostEqual(X[0,1],.5**4)

    def test_w33_two_axis_rotates_both_orthogonal_axes(self):
        r=dict(nx=np.array([1.,0.]),ny=np.array([0.,1.]),D=np.full((2,3),128.),
               B=np.full((2,3),100.),d=np.array([.5,.5]))
        spec=dict(name='isotropic-two-axis',stage='W33-first',space='encoded',
                  power=4.,angle=np.pi/4,w33Reference=True)
        X,_=M.design(r,spec,0)
        np.testing.assert_allclose(X,[[1,.25,.25],[1,.25,.25]],atol=1e-14)

    def test_reference_grid_recovers_a_rotated_two_axis_response(self):
        theta=np.arange(32)*2*np.pi/32
        x,y=np.cos(theta),np.sin(theta);phi=np.deg2rad(37.5)
        target=3+(x*np.cos(phi)+y*np.sin(phi))**4+2*(-x*np.sin(phi)+y*np.cos(phi))**4
        r=dict(nx=x,ny=y)
        powers,angles=M.parameter_grid(dict(name='isotropic-two-axis',w33Reference=True))
        errors=[]
        for k in powers:
            for angle in angles:
                X=M.angular_basis(r,'isotropic-two-axis',k,angle,reference=True)
                errors.append(float(np.max(abs(target-X@M.fit(X,target,'least-squares')))))
        self.assertLess(min(errors),1e-12)
        self.assertEqual(M.parameter_grid(dict(name='gradient',w33Reference=True))[0],[4.])

    def test_runner_keeps_bookkeeping_outside_the_frozen_document(self):
        path=Path(__file__).with_name('read-holdout.py')
        spec=importlib.util.spec_from_file_location('receipt_runner_test',path)
        runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
        fit=dict(profile='synthetic',pose='rest',spec=dict(stage='new-axes',exactBody=True),
                 coefficients=[[0.,0.]]*3)
        unmodelled=dict(profile='synthetic',pose='rest',spec=dict(stage='W33-first'))
        document=dict(inventories={},dependencies={},candidates=[
            dict(fit=unmodelled,selection='nonphysical',comparator='no-glass'),
            dict(fit=fit,selection='synthetic',comparator='no-glass')])
        original=copy.deepcopy(document)
        token=SimpleNamespace(configuration=dict(candidate=dict(document=document,sha256='synthetic')))
        saved={}
        # No receipt, reader or pixel is opened: exercise the real main loop
        # with an empty analytical population and intercept only its I/O seams.
        with patch.object(runner.fast,'activate'),patch.object(M,'extract',return_value=([],{})),\
             patch.object(M,'instrument_tables'),patch.object(runner,'capture'),\
             patch.object(M,'save',side_effect=lambda path,value:saved.setdefault(Path(path).name,value)),\
             patch.object(F,'verify'):
            runner.main(object(),token)
        self.assertEqual(document,original)
        self.assertEqual(token.configuration['candidate']['document'],original)
        self.assertEqual(saved['holdout-qualified-candidate-map.json'],{0:1})


if __name__=='__main__':unittest.main()
