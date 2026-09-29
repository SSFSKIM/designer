"""Synthetic reporting tests: measured errors, rails and controls stay distinct."""
import unittest
import numpy as np
import scoring
from replay import m


class ScoringTests(unittest.TestCase):
    def test_repeat_failure_retained_when_median_passes(self):
        p = np.full((4, 3), 128.)
        runs = np.full((7, 4, 3), 128.)
        runs[5, :, 2] = [130, 126, 130, 126]
        result = scoring.summarize([dict(cell='synthetic', endpoint='light-inactive',
            scale=1, member=0, part='straight', side='top', shell=0, bin=12,
            score=m.score_bin(p, runs), shadowControl=False)])
        self.assertFalse(result['survives'])
        self.assertEqual(result['worstMeasured']['repeat'], 5)
        self.assertEqual(result['worstMeasured']['codes'], 2.)

    def test_deficient_bins_excluded_not_failed_or_counted_as_measured(self):
        p = np.full((2, 3), 128.)
        runs = np.full((7, 2, 3), 170.)
        result = scoring.summarize([dict(cell='small', endpoint='light-inactive',
            scale=1, member=0, part='arc', side=None, shell=0, bin=1,
            score=m.score_bin(p, runs), shadowControl=False)])
        self.assertEqual(result['populationDeficientBins'], 1)
        self.assertEqual(result['admittedBins'], 0)
        self.assertEqual(result['bindingFailedBins'], 0)
        self.assertIsNone(result['worstMeasured'])

    def test_satisfied_censor_does_not_become_measured_accuracy(self):
        p = np.full((4, 3), 251.)
        runs = np.full((7, 4, 3), 255.)
        row = dict(cell='white', endpoint='dark-active', scale=2,
                   member=0, part='straight', side='top', shell=0, bin=12,
                   score=m.score_bin(p, runs), shadowControl=True)
        result = scoring.summarize([row])
        self.assertTrue(result['survives'])
        self.assertIsNone(result['worstMeasured'])
        self.assertEqual(result['statusComparisons']['censored-bound-satisfied'], 24)
        self.assertEqual(result['shadowControlBins'], 1)
        row['score'] = m.score_bin(np.full((4, 3), 249.), runs)
        result = scoring.summarize([row])
        self.assertFalse(result['survives'])
        self.assertEqual(result['railFailedBins'], 1)


if __name__ == '__main__':
    unittest.main()
