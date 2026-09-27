"""Regression: clipping must not turn a local plateau into a claimed minimum."""
import gzip
import json
from pathlib import Path
import sys
import unittest
import numpy as np

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / 'instrument'))
import body
import fitting
try:
    from solver import solve_h3, channel_constraints, farkas_valid
except ImportError:
    # Exercise the currently shipped behavior before its replacement exists.
    def solve_h3(x, neutral, target):
        fit = fitting.fit(lambda q: body.h3(x, neutral, q), target / 255,
                          [1, 0, 0, 1, 0, 0])['minimax']
        return dict(coefficients=fit['coefficients'], upperCodes=255 * fit['maximum'])


class CorrectionTests(unittest.TestCase):
    def test_clipped_dark_active_plateau_is_not_a_minimum(self):
        data = json.loads(gzip.decompress((HERE.parent /
            'body/identification-attempt-1.json.gz').read_bytes()))
        fit = next(f for f in data['fits'] if f['family'] == 'H3' and
                   f['endpoint'] == 'dark-active')
        rows = {r['cell']: r for r in data['rows']}
        cells = [rows[c] for c in fit['fitCells']]
        x = np.array([r['inputCodes'] for r in cells]) / 255
        target = np.array([r['members'][0]['medianRGB'] for r in cells])
        result = solve_h3(x, np.array(fit['neutralOrdinatesCodes']) / 255, target)
        self.assertLessEqual(result['upperCodes'], 20.138873)
        self.assertLess(result['upperCodes'] - result['lowerCodes'], 1.1e-5)
        self.assertTrue(farkas_valid(result['lowerCertificate']))

    def test_incompatible_identical_inputs_have_known_global_minimum(self):
        x = np.array([[.3, .3, .3], [.3, .3, .3]])
        # Row sums force identity neutral, so no coefficient can fix these targets.
        target = np.array([[70, 76.5, 76.5], [83, 76.5, 76.5]])
        result = solve_h3(x, body.KNOTS, target)
        self.assertAlmostEqual(result['upperCodes'], 6.5, places=6)
        self.assertTrue(farkas_valid(result['lowerCertificate']))

    def test_clipped_rails_do_not_constrain_preclip_values(self):
        z = np.array([[.1, .2, .3], [.4, .5, .6]])
        a, b, labels = channel_constraints(z, np.array([0., 255.]), 0.)
        self.assertEqual(labels, [(0, 'upper'), (1, 'lower')])
        self.assertEqual(a.shape, (2, 2))

    def test_free_negative_coefficients_and_clipping_are_admitted(self):
        rng = np.random.default_rng(19)
        x = rng.uniform(.05, .9, (24, 3))
        q = [2.1, -.5, -.3, 1.4, -.7, -.6]
        target = body.h3(x, body.KNOTS, q) * 255
        result = solve_h3(x, body.KNOTS, target)
        self.assertLess(result['upperCodes'], 1e-5)
        self.assertTrue(np.any(np.array(result['coefficients']) < 0))
        np.testing.assert_allclose(body.matrix(result['coefficients']).sum(1), 1)


if __name__ == '__main__':
    unittest.main()
