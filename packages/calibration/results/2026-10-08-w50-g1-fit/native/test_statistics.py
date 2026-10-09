"""Synthetic-only tests of the declared cuts and established T1 formula."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent


def load():
    spec = importlib.util.spec_from_file_location('w50_native_statistics_test', HERE/'statistics.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StatisticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = load()

    def test_cuts_keep_channels_and_independent_center_at_both_scales(self):
        component = {'kind': 'rrect', 'size': [168, 96], 'radius': 20.4}
        canvas = {'width': 512, 'height': 384}
        for scale in (1, 2):
            shape = (384*scale, 512*scale, 3)
            rgb = np.broadcast_to(np.array([20, 21, 22], dtype=np.uint8), shape).copy()
            rgb[188*scale:196*scale, 252*scale:260*scale] = [25, 26, 27]
            bg = np.zeros(shape, dtype=np.uint8)
            masks = self.s.analytical_masks(component, canvas, scale, shape[:2])
            row = self.s.read_frame(rgb, bg, component, canvas, scale)
            self.assertEqual(row['supports']['deep8']['rgbMedianCodes'], [20, 21, 22])
            self.assertEqual(row['supports']['center8']['rgbMedianCodes'], [25, 26, 27])
            self.assertEqual(row['supports']['center8']['pixels'], 64*scale*scale)
            self.assertEqual(row['supports']['deep8']['maskPackedBitsSha256'],
                             hashlib.sha256(np.packbits(masks['deep8']).tobytes()).hexdigest())

    def test_dark_analytical_cut_does_not_disappear_with_the_detected_silhouette(self):
        canvas = {'width': 64, 'height': 64}
        component = {'kind': 'rrect', 'size': [48, 48], 'radius': 0}
        rgb = np.zeros((64, 64, 3), dtype=np.uint8)
        row = self.s.read_frame(rgb, rgb, component, canvas, 1, include_structured=True)
        self.assertEqual(row['supports']['deep8']['pixels'], 1024)
        self.assertEqual(row['supports']['deep8']['rgbMedianCodes'], [0, 0, 0])
        self.assertEqual(row['supports']['full-silhouette']['status'], 'UNMEASURED_EMPTY_SUPPORT')
        self.assertEqual(row['statistics']['T1-full-silhouette']['value'], None)

    def test_far24_uses_distance_from_every_dot_pixel_not_its_centroid(self):
        canvas = {'width': 96, 'height': 96}
        component = {'kind': 'rrect', 'size': [80, 80], 'radius': 0}
        for scale in (1, 2):
            bg = np.zeros((96*scale, 96*scale, 3), dtype=np.uint8)
            bg[48*scale:52*scale, 48*scale:52*scale] = 255
            masks = self.s.analytical_masks(component, canvas, scale, bg.shape[:2],
                                            background=bg, impulse=True)
            self.assertTrue(masks['deep8_far24'][48*scale, 24*scale])
            self.assertFalse(masks['deep8_far24'][48*scale, 25*scale])
            self.assertFalse(masks['deep8_far24'][48*scale, 75*scale-1])
            self.assertTrue(masks['deep8_far24'][48*scale, 76*scale-1])

    def test_empty_dot_set_is_exactly_deep8_including_the_recorded_support_hash(self):
        canvas = {'width': 96, 'height': 96}
        component = {'kind': 'rrect', 'size': [80, 80], 'radius': 0}
        for impulse in (False, True):
            rgb = np.full((96, 96, 3), [10, 20, 30], dtype=np.uint8)
            row = self.s.read_frame(rgb, np.zeros_like(rgb), component, canvas, 1,
                                    impulse=impulse, include_structured=True)
            self.assertEqual(row['supports']['deep8'], row['supports']['deep8_far24'])
            self.assertEqual(row['statistics']['deep8-far24-luma-mean']['value'], 18.596)
            self.assertEqual(row['statistics']['deep8-far24-luma-median']['value'], 18.596)

    def test_full_silhouette_t1_is_linear_population_sd_and_uses_the_native_mask(self):
        canvas = {'width': 32, 'height': 32}
        component = {'kind': 'rrect', 'size': [32, 32], 'radius': 0}
        rgb = np.zeros((32, 32, 3), dtype=np.uint8)
        rgb[:, 16:] = 255
        mask = np.ones((32, 32), dtype=bool)
        row = self.s.read_frame(rgb, np.zeros_like(rgb), component, canvas, 1,
                                include_structured=True, silhouette_mask=mask)
        t1 = row['statistics']['T1-full-silhouette']
        self.assertEqual(t1['value'], .5)
        self.assertEqual(row['supports']['full-silhouette']['linearLumaMean'], .5)
        detected = self.s.read_frame(rgb, np.zeros_like(rgb), component, canvas, 1,
                                     include_structured=True)
        self.assertEqual(detected['supports']['full-silhouette']['pixels'], 512)
        self.assertEqual(detected['statistics']['T1-full-silhouette']['value'], 0)

    def test_repeat_bars_keep_channel_spread_and_stop_above_one_code_without_extra_runs(self):
        readings = [np.array([20, 21, 22]), np.array([21, 21, 22]), np.array([20, 21, 22])]
        verdict = self.s.repeat_codes(readings)
        self.assertEqual(verdict['spreadCodes'], [1, 0, 0])
        self.assertEqual(verdict['barCodes'], [.5, .5, .5])
        self.assertTrue(verdict['passes'])
        readings[1][2] = 24
        verdict = self.s.repeat_codes(readings)
        self.assertEqual(verdict['spreadCodes'], [1, 0, 2])
        self.assertFalse(verdict['passes'])
        for bad in (readings[:2], readings + readings[:1], [[0, 0, 0], [0, 0, 0], [0, np.nan, 0]]):
            with self.assertRaises(ValueError):
                self.s.repeat_codes(bad)

    def test_t1_repeat_bar_uses_its_established_linear_step_not_a_code_sd(self):
        # All means in the linear segment: exactly 1/(255*12.92) per encoded code.
        step = 1/(255*12.92)
        verdict = self.s.repeat_t1([0, step, 0], [0, 0, 0])
        self.assertAlmostEqual(verdict['spreadCodes'], 1)
        self.assertAlmostEqual(verdict['barLinear'], .5*step)
        self.assertAlmostEqual(verdict['barCodes'], .5)
        self.assertTrue(verdict['passes'])
        self.assertFalse(self.s.repeat_t1([0, 2*step, 0], [0, 0, 0])['passes'])

    def test_t1_anchor_and_aggregation_are_order_independent_with_differing_runs(self):
        step = 2.4/1.055*((1.055*.2**(1/2.4)-.055+.055)/1.055)**1.4/255
        expected = self.s.repeat_t1([0, step*.6, step*.2], [.1, .3, .2])
        self.assertEqual(expected['anchorNativeMean'], .2)
        self.assertAlmostEqual(expected['codeStepLinear'], step)
        self.assertAlmostEqual(expected['spreadCodes'], .6)
        self.assertAlmostEqual(expected['barCodes'], .5)
        reversed_runs = self.s.repeat_t1([step*.2, step*.6, 0], [.2, .3, .1])
        self.assertEqual(expected, reversed_runs)

    def test_saved_native_mask_roundtrips_and_refuses_hash_or_population_changes(self):
        rgb = np.zeros((3, 3, 3), dtype=np.uint8)
        mask = np.eye(3, dtype=bool)
        support = self.s.read_support(rgb, mask, retain_mask=True)
        np.testing.assert_array_equal(self.s.decode_support(support), mask)
        for changed in (dict(support, pixels=4), dict(support, maskPackedBitsSha256='0'*64)):
            with self.assertRaises(ValueError):
                self.s.decode_support(changed)

    def test_bad_image_shape_range_and_empty_required_cut_refuse(self):
        canvas = {'width': 32, 'height': 32}
        component = {'kind': 'rrect', 'size': [16, 16], 'radius': 0}
        rgb = np.zeros((32, 32, 3), dtype=np.uint8)
        with self.assertRaisesRegex(ValueError, 'empty'):
            self.s.read_frame(rgb, rgb, component, canvas, 1)
        for bad in (np.zeros((32, 32, 4)), np.full((32, 32, 3), np.nan),
                    np.full((32, 32, 3), 256), np.zeros((31, 32, 3), dtype=np.uint8)):
            with self.assertRaises(ValueError):
                self.s.read_frame(bad, rgb, {'kind': 'rrect', 'size': [32, 32], 'radius': 0}, canvas, 1)


if __name__ == '__main__':
    unittest.main()
