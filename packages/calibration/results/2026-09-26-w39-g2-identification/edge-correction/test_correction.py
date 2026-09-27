"""Censoring is channel-local; missing samples cannot silently become passes."""
import sys
sys.dont_write_bytecode = True
import unittest
import numpy as np
try:
    from replay import classify
except ImportError:
    def classify(native, prediction, labels, bins, tau):
        # The original score(): absolute errors and geometry admission alone.
        result = []
        for i, b in enumerate(bins):
            mask = labels == i
            errors = abs(prediction[mask] - native[mask]).mean(0)
            result.append(dict(channelStatus=['measured'] * 3,
                               failedChannels=np.flatnonzero(errors > tau[i] + 1e-8).tolist()))
        return result

class CensorTests(unittest.TestCase):
    def score(self, native, prediction, pixels=4):
        return classify(np.tile(native, (pixels, 1)), np.tile(prediction, (pixels, 1)),
                        np.zeros(pixels, dtype=int), [dict(status='measured', pixels=pixels)],
                        np.ones((1, 3)))[0]

    def test_native_255_cannot_be_measured_zero_error_pass(self):
        result = self.score([255, 255, 255], [255, 255, 255])
        self.assertEqual(result['channelStatus'], ['UNMEASURED'] * 3)
        self.assertEqual(result['failedChannels'], [])

    def test_censored_r_does_not_erase_measured_g_failure(self):
        result = self.score([255, 100, 100], [255, 103, 100])
        self.assertEqual(result['channelStatus'], ['UNMEASURED', 'measured', 'measured'])
        self.assertEqual(result['failedChannels'], [1])

    def test_population_three_is_not_measured(self):
        self.assertEqual(self.score([100]*3, [100]*3, 3)['channelStatus'], ['UNMEASURED']*3)

    def test_censor_thresholds_are_inclusive(self):
        result = self.score([5, 250, 249], [8, 247, 247])
        self.assertEqual(result['channelStatus'], ['UNMEASURED', 'UNMEASURED', 'measured'])
        self.assertEqual(result['failedChannels'], [2])

if __name__ == '__main__':
    unittest.main()
