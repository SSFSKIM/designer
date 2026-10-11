"""W52-DL1: machine precision is separate from a scientific error allowance."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('w52_comparison', HERE / 'comparison.py')
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


class ComparisonTests(unittest.TestCase):
    def test_exposed_luma_boundary_is_numerically_equal(self):
        # W51's two failures were subtraction roundoff, not a measured extra code.
        for native, candidate in [(19.999999999999996, 21.0), (21.0, 19.999999999999996)]:
            value = abs(candidate - native)
            self.assertTrue(comparison.less_equal(value, 1.0, native, candidate))
            self.assertGreater(value, 1.0)

    def test_real_growth_does_not_hide_in_the_numerical_allowance(self):
        native, candidate = 20.0, 21.00000001
        self.assertFalse(comparison.less_equal(abs(candidate - native), 1.0, native, candidate))
        # Existing occupied-cap failure remains a failure without the separately ruled rebase.
        self.assertFalse(comparison.less_equal(0.0013798445629486346, 0.001318279930855289,
                                               0.003953386427888242))

    def test_epsilon_is_declared_from_units_and_source_operands_not_the_cell_budget(self):
        self.assertEqual(comparison.epsilon(1.0, 21.0), 64 * math.ulp(21.0))
        self.assertEqual(comparison.epsilon(0.0005, 0.003), 64 * math.ulp(1.0))
        self.assertLess(comparison.epsilon(255.0), 1e-8)
        self.assertLess(comparison.epsilon(1.0) / 0.0005, 1e-9)

    def test_only_the_numerical_boundary_is_inclusive(self):
        eps = comparison.epsilon(1.0)
        self.assertTrue(comparison.less_equal(1.0 + eps, 1.0))
        self.assertFalse(comparison.less_equal(1.0 + 2 * eps, 1.0))
        self.assertTrue(comparison.less_equal(-0.1, 0.0))

    def test_nonfinite_operands_never_get_tolerance_or_a_pass(self):
        for bad in [math.nan, math.inf, -math.inf]:
            for args in [(bad, 1.0), (1.0, bad), (1.0, 1.0, bad)]:
                with self.assertRaises(ValueError):
                    comparison.less_equal(*args)
        with self.assertRaises(ValueError):
            comparison.epsilon()


if __name__ == '__main__':
    unittest.main()
