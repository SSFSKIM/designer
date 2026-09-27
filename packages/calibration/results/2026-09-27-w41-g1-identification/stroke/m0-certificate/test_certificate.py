"""Synthetic checks: clip completeness, Jensen necessity, and exact proof refusal."""
import unittest
import json
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
import numpy as np
import certificate as c


class CertificateTests(unittest.TestCase):
    def test_all_physical_clip_cases_enter_relaxation(self):
        bs = [20, 40, 72, 104, 150, 200, 240]
        for coverage in [0., .25, 1.]:
            for t, k in [(0., -255.), (0., 255.), (1., 0.), (3., -100.), (.5, 100.)]:
                intrinsic = np.array(bs)*t+k
                targets = (1-coverage)*np.array(bs)+coverage*np.clip(intrinsic, 0, 255)
                rows = [dict(b=b, mean=str(F(float(y))), bound='1') for b,y in zip(bs,targets)]
                # Removing a clip region or a c=0 boundary loses this containment.
                fits = []
                for regime in c.regimes(len(bs)):
                    a,rhs,_ = c.constraints(rows, regime)
                    x = [F(coverage), F(coverage*t), F(coverage*k)]
                    fits.append(all(sum(v*w for v,w in zip(row,x)) <= r for row,r in zip(a,rhs)))
                self.assertTrue(any(fits), (coverage,t,k))

    def test_every_regime_certified_for_nonmonotone_targets(self):
        rows = [dict(b=b, mean=str(y), bound='1') for b,y in [(40,100),(80,10),(120,100)]]
        result = c.solve(rows)
        self.assertEqual(result['status'], 'CERTIFIED_INFEASIBLE_RELAXATION')
        self.assertEqual(len(result['regimes']), 10)
        for item in result['regimes']:
            a,rhs,_ = c.constraints(rows,item['regime'])
            self.assertTrue(c.verify(item['certificate'],a,rhs))
            bad = dict(item['certificate'], weights=['0']*len(item['certificate']['weights']))
            self.assertFalse(c.verify(bad,a,rhs))

    def test_feasible_cut_does_not_reject_family(self):
        rows = [dict(b=b,mean=str(b),bound='1') for b in [40,80,120]]
        self.assertEqual(c.solve(rows)['status'], 'NOT_REJECTED_BY_RELAXATION')

    def test_jensen_is_not_mae_survival(self):
        # Signed errors cancel but the sealed absolute-before-mean score fails.
        prediction=np.array([50.,50.,50.,50.]); native=np.array([40.,60.,40.,60.])
        self.assertEqual(abs(prediction.mean()-native.mean()),0)
        self.assertGreater(abs(prediction-native).mean(),1)


class SavedReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import run
        cls.r=run
        cls.proof=Path('/Users/new/vitrea-w41/pre-w41-proof')
        cls.m,cls.native,_=run.load(cls.proof)

    def tearDown(self):
        self.r.DATA=self.r.HERE

    def test_complete_saved_proof_needs_no_native_reader_or_lp(self):
        self.r.DATA=self.r.HERE/'white-extension'
        with patch.object(self.native,'guarded',side_effect=AssertionError('native reader')), \
             patch.object(c,'linprog',side_effect=AssertionError('LP during replay')):
            result=self.r.replay(self.proof,self.m,self.native)
        for endpoint in ('light-inactive','dark-inactive'):
            self.assertEqual(result['endpoints'][endpoint]['exactRegimes'],45)
            self.assertTrue(result['endpoints'][endpoint]['rejectedM0'])

    def test_initial_light_cut_remains_not_a_rejection(self):
        result=self.r.replay(self.proof,self.m,self.native)
        self.assertFalse(result['endpoints']['light-inactive']['rejectedM0'])
        self.assertEqual(result['endpoints']['light-inactive']['exactRegimes'],33)
        self.assertTrue(result['endpoints']['dark-inactive']['rejectedM0'])

    def test_wrong_neutral_reference_is_refused(self):
        records=json.loads((self.r.HERE/'manifest.json').read_text())['records']
        row=dict(records[0],b=records[0]['b']+1)
        with self.assertRaisesRegex(ValueError,'reference not uniform'):
            self.r.derive([row],self.m,self.native)

    def test_changed_payload_identity_is_refused(self):
        records=json.loads((self.r.HERE/'manifest.json').read_text())['records']
        row=dict(records[0],sha256='0'*64)
        with self.assertRaisesRegex(ValueError,'payload hash mismatch'):
            self.r.derive([row],self.m,self.native)

    def test_repeat_geometry_change_is_refused(self):
        import copy
        records=json.loads((self.r.HERE/'manifest.json').read_text())['records']
        unpack=self.native.archive.unpack
        calls=0
        def changed(raw):
            nonlocal calls
            p=unpack(raw); calls+=1
            if calls==2:
                p=copy.deepcopy(p)
                p['component']['suppliedPaths'][0]['frameOrigin'][0]+=.25
            return p
        with patch.object(self.native.archive,'unpack',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'geometry or endpoint differs'):
                self.r.derive(records[:1],self.m,self.native)


if __name__ == '__main__': unittest.main()

