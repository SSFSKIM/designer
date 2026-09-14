"""Scientific and admission regressions; run with Python 3.12 (numpy/scipy)."""
import importlib.util
from pathlib import Path
import subprocess
import unittest
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('abscissa', HERE/'read.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ReadingTests(unittest.TestCase):
    def test_isotonic_pools_ties_and_violations_not_sorted_targets(self):
        fit = module.isotonic([0, 1, 1, 2], [0, 0.8, 0.2, 0.4])
        np.testing.assert_allclose(fit, [0, 1.4/3, 1.4/3, 1.4/3])

    def test_isotonic_preserves_input_order_and_monotone_data(self):
        np.testing.assert_allclose(module.isotonic([2, 0, 1], [0.7, 0.1, 0.4]), [0.7, 0.1, 0.4])

    def test_roundoff_does_not_split_mathematically_equal_abscissae(self):
        np.testing.assert_allclose(module.isotonic([0.5, 0.5+1e-14], [0, 1]), [0.5, 0.5])

    def test_reader_refuses_D_on_both_poses_before_any_image_IO(self):
        for scene in ['hc-text__rrect-sm__inactive', 'hc-text__rrect-sm__rest',
                      'checkerboard__rrect-ml__inactive', 'hc-text__rrect-sm__rest-tint-orange']:
            result = subprocess.run(['pnpm','--filter','@vitrea/calibration','--fail-if-no-match',
                'exec','tsx',str(HERE/'extract.ts'),'--check-scene',scene],
                cwd=HERE.parents[3], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('X10 refused checking cell', result.stdout+result.stderr)

if __name__ == '__main__':
    unittest.main()
