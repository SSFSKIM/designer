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


if __name__ == '__main__':
    unittest.main()
