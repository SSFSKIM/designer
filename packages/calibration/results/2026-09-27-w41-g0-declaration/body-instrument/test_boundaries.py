"""Adversarial synthetic boundary checks, including standalone exact duals."""
from fractions import Fraction as F
import unittest
import numpy as np
import body41 as b
from test_body import NEUTRAL, cloud, independent_certificate


class BoundaryProofs(unittest.TestCase):
    def test_gain_box_limits_are_certified_not_silently_relaxed(self):
        x = np.array([[70.,80.,90.], [90.,80.,70.]])
        offset, design = b.linear_design('E3',x,NEUTRAL)
        y = offset+design @ np.full(3,3.5)
        result = b.solve_linear('E3',x,NEUTRAL,y)
        self.assertGreater(result['lowerCodes'], 1)
        a, rhs, labels = b.constraints('E3',x,NEUTRAL,y,result['lowerCodes'])
        independent_certificate(result['lowerCertificate'],a,rhs)
        self.assertTrue(any(labels[i][0] == 'gain' for i in result['lowerCertificate']['indices']))

    def test_six_dimensional_farkas_and_changed_system_refusal(self):
        # q_i<=0, sum(q_i)>=1: seven equally weighted constraints prove empty.
        a = np.vstack([np.eye(6), -np.ones(6)])
        rhs = np.r_[np.zeros(6),-1.]
        weights = b._rational_weights(a)
        self.assertEqual(weights,[F(1,7)]*7)
        cert = {'indices':list(range(7)),'weights':list(map(str,weights))}
        independent_certificate(cert,a,rhs)
        self.assertTrue(b.verify_certificate(cert,a,rhs))
        self.assertFalse(b.verify_certificate(cert,a,np.r_[np.zeros(6),1.]))
        changed = a.copy(); changed[0,0] = np.nextafter(1.,2.)
        self.assertFalse(b.verify_certificate(cert,changed,rhs))

    def test_both_rails_remain_hard_at_large_epsilon(self):
        x = np.array([[192.,32.,32.]])
        y = np.array([[255.,0.,100.]])
        a0,b0,l0 = b.constraints('EH6',x,NEUTRAL,y,0)
        a1,b1,l1 = b.constraints('EH6',x,NEUTRAL,y,255)
        for label in ([0,0,'high-rail'], [0,1,'low-rail']):
            np.testing.assert_array_equal(a0[l0.index(label)],a1[l1.index(label)])
            self.assertEqual(b0[l0.index(label)],b1[l1.index(label)])
        predicted = np.array([[249.,6.,103.]])
        s = b.score(predicted,y)
        self.assertEqual(s['railFailures'],2)
        self.assertEqual(s['uncensoredFailures'],1)
        self.assertEqual(s['allChannelFailedCells'],1)
        self.assertFalse(s['heldoutCoverageEligible'][0])
        self.assertEqual(s['uncensoredErrorCodes'][0],[None,None,3.])

    def test_per_channel_bar_and_gain_boundary_recovery(self):
        x = cloud(); q = [0,1e-9,3]
        y = b.forward('E3',x,NEUTRAL,q)
        solved = b.solve_linear('E3',x,NEUTRAL,y)
        self.assertLess(solved['upperCodes'],1e-7)
        np.testing.assert_allclose(solved['coefficients'],q,atol=1e-7)
        neutral_x = np.array([[80.,80.,80.]])
        target = b.forward('E3',neutral_x,NEUTRAL,[1,1,1])+np.array([[2.,0.,0.]])
        self.assertEqual(b.survival_linear('E3',neutral_x,NEUTRAL,target,.5)['status'],
                         'certified-infeasible')
        self.assertEqual(b.survival_linear('E3',neutral_x,NEUTRAL,target,[[2.,.5,.5]])['status'],
                         'forward-feasible')

    def test_local_censor_feasibility_not_reconstructed_rgb(self):
        x = np.vstack([cloud(),[192,32,32]])
        target = b.forward('E3',x,NEUTRAL,[2,2,2]); target[-1,0] = 255
        result = b.fit_local('E3',x,NEUTRAL,target)
        for key in ('leastSquares','minimax'):
            self.assertIsNotNone(result[key])
            self.assertEqual(result[key]['railDeficitCodes'],0)
            self.assertLess(result[key]['maximumCodes'],1e-5)
            self.assertEqual(result[key]['rank'],3)
        self.assertTrue(result['budget']['hardRailConstrainedLS'])

    def test_all_censored_local_has_no_measured_rank_or_accuracy(self):
        x = [[255.,255.,255.]]
        neutral = [255.]*7
        result = b.fit_local('E3',x,neutral,[[255.,255.,255.]])
        self.assertEqual(result['leastSquares']['rank'],0)
        self.assertEqual(result['leastSquares']['score']['uncensoredChannels'],0)
        self.assertEqual(result['leastSquares']['score']['statuses'],
                         [['censored-bound-satisfied']*3])


if __name__ == '__main__':
    unittest.main(verbosity=2)
