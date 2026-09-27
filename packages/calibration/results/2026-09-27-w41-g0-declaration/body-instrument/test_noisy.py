"""Synthetic noisy observations: exact dual recovery, bounded honest exhaustion."""
import json
import unittest
from unittest.mock import patch
import numpy as np
import body41 as b
from test_body import NEUTRAL, independent_certificate

X = np.array([[70., 80., 90.]])
TARGET = np.array([[95., 102., 112.]])


class NoisyProofs(unittest.TestCase):
    def test_noisy_observation_recovers_tiny_bound_weight(self):
        # Dropping the coefficient-bound row loses exact cancellation even
        # though the floating dual calls the two observation rows sufficient.
        for family in ('E3', 'EH6'):
            with self.subTest(family=family):
                fit = b.solve_linear(family, X, NEUTRAL, TARGET)
                self.assertEqual(fit['status'], 'global minimax bracket')
                self.assertTrue(fit['converged'])
                self.assertGreater(fit['lowerCodes'], 1)
                self.assertLessEqual(fit['bracketWidthCodes'], 1e-5)
                a, rhs, _ = b.constraints(family, X, NEUTRAL, TARGET, fit['lowerCodes'])
                independent_certificate(fit['lowerCertificate'], a, rhs)
                verdict = b.survival_linear(family, X, NEUTRAL, TARGET, .5)
                self.assertEqual(verdict['status'], 'certified-infeasible')
                a, rhs, labels = b.constraints(family, X, NEUTRAL, TARGET, 1.)
                independent_certificate(verdict['certificate'], a, rhs)
                weights = dict(zip(verdict['certificate']['indices'],
                                   map(b.F, verdict['certificate']['weights'])))
                self.assertTrue(any(labels[i][0] == 'gain' and 0 < w < b.F('1e-12')
                                    for i, w in weights.items()))

    def test_recovery_exhaustion_is_explicit_not_a_negative(self):
        for family in ('E3', 'EH6'):
            with self.subTest(family=family), patch.object(b, 'MAX_DUAL_RECOVERY_ATTEMPTS', 0):
                for result in (b.solve_linear(family, X, NEUTRAL, TARGET),
                               b.survival_linear(family, X, NEUTRAL, TARGET, .5)):
                    self.assertEqual(result['status'], 'uncertified')
                    self.assertFalse(result['converged'])
                    self.assertIn('reason', result)
                    bracket = result['floatingBracket']
                    self.assertFalse(bracket['certified'])
                    self.assertIsNotNone(bracket['lower'])
                    self.assertIsNotNone(bracket['upper'])
                    self.assertLessEqual(bracket['lower'], bracket['upper'])
                    self.assertNotIn('certificate', result)

    def test_deterministic_100_noisy_cases(self):
        # Fifty independently perturbed clouds per family, from one through
        # eight cells. This catches exact-recovery stalls hidden by planted fits.
        rng = np.random.default_rng(4101)
        counts = {'cases': 0, 'stalls': 0, 'minimaxUncertified': 0,
                  'survivalUncertified': 0, 'certifiedMinimax': 0,
                  'certifiedInfeasible': 0, 'forwardFeasible': 0}
        for family in ('E3', 'EH6'):
            for index in range(50):
                x = rng.uniform(45, 145, (1 + index % 8, 3))
                q = rng.uniform(.4, 1.6, b.SIZES[family])
                target = np.clip(b.forward(family, x, NEUTRAL, q) +
                                 rng.normal(0, 2, x.shape), 6, 249)
                with self.subTest(family=family, index=index):
                    counts['cases'] += 1
                    try:
                        fit = b.solve_linear(family, x, NEUTRAL, target)
                        verdict = b.survival_linear(family, x, NEUTRAL, target, .5)
                    except RuntimeError:
                        counts['stalls'] += 1
                        raise
                    if fit['status'] == 'uncertified':
                        counts['minimaxUncertified'] += 1
                        self.assertFalse(fit['converged'])
                        self.assertFalse(fit['floatingBracket']['certified'])
                    else:
                        counts['certifiedMinimax'] += 1
                        self.assertLessEqual(fit['bracketWidthCodes'], 1e-5)
                        a, rhs, _ = b.constraints(family, x, NEUTRAL, target, fit['lowerCodes'])
                        independent_certificate(fit['lowerCertificate'], a, rhs)
                        prediction = b.forward(family, x, NEUTRAL, fit['coefficients'])
                        self.assertEqual(float(np.max(abs(prediction-target))), fit['upperCodes'])
                    if verdict['status'] == 'uncertified':
                        counts['survivalUncertified'] += 1
                        self.assertFalse(verdict['converged'])
                    elif verdict['status'] == 'certified-infeasible':
                        counts['certifiedInfeasible'] += 1
                        a, rhs, _ = b.constraints(family, x, NEUTRAL, target, 1.)
                        independent_certificate(verdict['certificate'], a, rhs)
                    else:
                        self.assertEqual(verdict['status'], 'forward-feasible')
                        counts['forwardFeasible'] += 1
                        self.assertLessEqual(np.max(abs(b.forward(
                            family, x, NEUTRAL, verdict['coefficients'])-target)), 1.)
        print('NOISY_SWEEP ' + json.dumps(counts, sort_keys=True), flush=True)
        self.assertEqual(counts['cases'], 100)
        self.assertEqual(counts['stalls'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
