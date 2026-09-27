"""A start clipped at a rail must not hide another converged basin."""
import unittest
import numpy as np
from pathlib import Path
import sys
sys.dont_write_bytecode = True
try:
    from multistart import fit_multistart
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'instrument'))
    import fitting
    def fit_multistart(forward, target, starts, bounds=None, monotone_start=None):
        return fitting.fit(forward, target, starts[0], bounds, monotone_start)['minimax']

class MultistartTests(unittest.TestCase):
    def test_an_unclipped_start_escapes_zero_gradient_plateau(self):
        result = fit_multistart(lambda q: np.clip(q, 0, 1), np.array([.4]),
                                [np.array([-1.]), np.array([.7])])
        self.assertLess(result['maximum'], 1e-8)
        self.assertTrue(result['converged'])

    def test_monotone_bounded_parameters_are_not_relaxed_for_a_better_fit(self):
        result = fit_multistart(lambda q: q, np.array([.7, .3]),
                                [np.array([.1, .9]), np.array([.3, .7])],
                                [(0, 1), (0, 1)], monotone_start=0)
        self.assertAlmostEqual(result['maximum'], .2, places=7)
        self.assertGreaterEqual(result['coefficients'][1], result['coefficients'][0] - 1e-10)

if __name__ == '__main__':
    unittest.main()
