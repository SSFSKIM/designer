"""Synthetic-only canonical metrics; expectations are independent pixel/kernel calculations."""
import copy
import importlib.util
from pathlib import Path
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent


def load():
    spec = importlib.util.spec_from_file_location('w50_reference_statistics_tests', HERE/'statistics.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def manual_gaussian(image):
    x = np.arange(-16, 17, dtype=float)
    kernel = np.exp(-x*x/32); kernel /= kernel.sum()
    # scipy reflect is the half-sample symmetric extension, numpy's symmetric pad.
    horizontal = np.apply_along_axis(lambda row: np.convolve(np.pad(row, (16, 16), mode='symmetric'),
                                                            kernel, mode='valid'), 1, image)
    return np.apply_along_axis(lambda column: np.convolve(np.pad(column, (16, 16), mode='symmetric'),
                                                         kernel, mode='valid'), 0, horizontal)


class StatisticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.s = load()

    def test_text_bands_use_fixed_device_sigma_unmasked_blur_and_eroded_native_support(self):
        for scale in (1, 2):
            rgb = np.zeros((64*scale, 64*scale, 3), dtype=np.uint8)
            rgb[8*scale:56*scale, 8*scale:56*scale] = 128
            read = self.s.canonical_read(rgb, np.zeros_like(rgb),
                {'kind': 'rrect', 'size': [48, 48], 'radius': 0}, {'width': 64, 'height': 64},
                scale, text=True)
            mask = np.zeros(rgb.shape[:2], dtype=bool)
            mask[12*scale:52*scale, 12*scale:52*scale] = True
            linear = np.zeros(rgb.shape[:2]); linear[8*scale:56*scale, 8*scale:56*scale] = ((128/255+.055)/1.055)**2.4
            low = manual_gaussian(linear)
            self.assertEqual(read['supports']['eroded4']['pixels'], 1600*scale*scale)
            self.assertAlmostEqual(read['statistics']['T1-low']['value'], float(low[mask].std()), places=14)
            self.assertAlmostEqual(read['statistics']['T1-fine']['value'], float((linear-low)[mask].std()), places=14)
            self.assertGreater(read['statistics']['T1-fine']['value'], 0)

    def test_web_statistics_use_the_published_native_mask_not_web_detection(self):
        native = np.zeros((64, 64, 3), dtype=np.uint8); native[8:56, 8:56] = 255
        web = np.zeros_like(native)
        read = self.s.canonical_read(native, np.zeros_like(native),
            {'kind': 'rrect', 'size': [48, 48], 'radius': 0}, {'width': 64, 'height': 64}, 1,
            web_rgb=web, text=True)
        self.assertEqual(read['web']['statistics']['T1-full-silhouette']['value'], 0)
        self.assertEqual(read['web']['supports']['full-silhouette']['pixels'], 2304)

    def test_empty_native_silhouette_remains_unmeasured_while_declared_path_keeps_channels(self):
        native = np.full((64, 64, 3), [20, 21, 22], dtype=np.uint8)
        read = self.s.canonical_read(native, np.zeros_like(native),
            {'kind': 'rrect', 'size': [48, 48], 'radius': 0}, {'width': 64, 'height': 64}, 1,
            text=True)
        self.assertIsNone(read['statistics']['T1-full-silhouette']['value'])
        self.assertIsNone(read['publishedInteriorMean'])
        self.assertEqual(read['statistics']['deep8-channel-median']['value'], [20, 21, 22])
        self.assertEqual(read['supports']['deep8']['pixels'], 1024)
        self.assertEqual(read['statistics']['T1-low']['status'], 'UNMEASURED_EMPTY_SUPPORT')

    def test_far24_empty_dots_equal_deep8_and_retains_encoded_not_linear_luma(self):
        native = np.full((96, 96, 3), [10, 20, 30], dtype=np.uint8)
        read = self.s.canonical_read(native, np.zeros_like(native),
            {'kind': 'rrect', 'size': [80, 80], 'radius': 0}, {'width': 96, 'height': 96}, 1,
            impulse=True)
        self.assertEqual(read['supports']['deep8'], read['supports']['deep8_far24'])
        self.assertAlmostEqual(read['statistics']['deep8-far24-luma-mean']['value'], 18.596)
        self.assertAlmostEqual(read['statistics']['deep8-far24-luma-median']['value'], 18.596)

    def test_seven_repeat_bars_use_published_mean_and_report_large_spread_without_noise_stop(self):
        step = 1/(255*12.92)
        bar = self.s.repeat_bar([0, 3*step, 0, 0, 0, 0, 0], units='linear-luma', published_mean=0)
        self.assertAlmostEqual(bar['code'], step)
        self.assertAlmostEqual(bar['bar'], 1.5*step)
        self.assertAlmostEqual(bar['B'], 3*step)
        self.assertAlmostEqual(bar['spreadCodes'], 3)
        self.assertNotIn('passes', bar)
        self.assertNotIn('stop', bar)
        same = self.s.repeat_bar([0]*7, units='linear-luma', published_mean=.2)
        expected = 2.4/1.055*.2**(1.4/2.4)/255
        self.assertAlmostEqual(same['code'], expected)
        self.assertAlmostEqual(same['B'], expected)
        codes = self.s.repeat_bar([[20, 20, 20], [20, 22, 26], *[[20, 20, 20]]*5],
                                 units='encoded-RGB-codes', published_mean=None)
        self.assertEqual(codes['bar'], [.5, 1., 3.])
        self.assertEqual(codes['B'], [1., 2., 6.])
        with self.assertRaises(ValueError): self.s.repeat_bar([0]*6, units='linear-luma', published_mean=0)
        with self.assertRaises(ValueError): self.s.repeat_bar([0]*7, units='linear-luma', published_mean=None)

    def test_known025_numeric_and_historical_fields_are_never_rebased_by_completion(self):
        known = {'profile': 'apple-macos-27.0-1x-dark-standard-glass0.25', 'renderer': 'webgpu',
            'scene': 'text__rrect-md__rest', 'statistic': 'T1-low', 'role': 'historical-prediction-check',
            'native': .12, 'current': .13, 'B': .001, 'fidelity': {'native': .4, 'current': .5, 'reference': .6},
            'historical': [{'value': .22, 'maxGrowthInB': 2.1}], 'status': 'MEASURED'}
        new = {'native': 100., 'current': 200., 'B': 50., 'fidelity': {'native': 30.}}
        before = copy.deepcopy(known)
        self.assertEqual(self.s.complete_t1_reference(known, new), before)
        self.assertEqual(known, before)


if __name__ == '__main__': unittest.main()
