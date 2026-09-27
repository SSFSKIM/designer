"""Synthetic proof-obligation tests; no archive reader or native inputs."""
import copy
from fractions import Fraction
import unittest
import numpy as np
import replay_certificate as c


class CertificateTests(unittest.TestCase):
    def test_seven_code_pair_has_exact_lower_bound(self):
        out = c.exact_witness(np.full((7, 4), 21), np.full((7, 4), 14))
        self.assertTrue(out['allSevenAndMedianReject'])
        self.assertEqual(out['bar'], ['1/2', '1/2'])
        for row in out['states']:
            self.assertEqual(row['jensenExcess'], '5')
            self.assertEqual(row['necessaryWorstMAELowerBound'], '7/2')

    def test_equal_observation_does_not_reject(self):
        out = c.exact_witness(np.full((7, 4), 21), np.full((7, 4), 21))
        self.assertFalse(out['rejects'])

    def test_equal_means_do_not_erase_pixel_obstruction(self):
        left = np.tile([10, 20, 10, 20], (7, 1))
        right = np.tile([20, 10, 20, 10], (7, 1))
        row = c.exact_witness(left, right)['states'][0]
        self.assertEqual(row['absoluteMeanDifference'], '0')
        self.assertEqual(row['meanAbsolutePairedDifference'], '10')
        self.assertTrue(row['rejects'])

    def test_exact_repeat_bar_and_strict_inequality(self):
        left = np.full((7, 4), 20)
        left[-1] = 24
        right = np.full((7, 4), 22)
        out = c.exact_witness(left, right)
        self.assertEqual(out['bar'], ['5/2', '1/2'])
        self.assertFalse(out['rejects'])
        out = c.exact_witness(np.full((7, 4), 21), np.full((7, 4), 19))
        self.assertFalse(out['rejects'], 'exact equality at sum of bounds is not rejection')

    def test_censor_and_population_and_repeat_refuse(self):
        for shape, value in (((7, 4), 5), ((7, 4), 250), ((7, 3), 21), ((6, 4), 21)):
            with self.subTest(shape=shape, value=value), self.assertRaises(AssertionError):
                c.exact_witness(np.full(shape, value), np.full(shape, 14))

    @staticmethod
    def observation():
        return dict(component={'kind': 'capsule-circular', 'position': [160, 140]},
                    scale=1, bin={'pixels': 4, 'shell': 0}, xy=np.zeros((4, 2)),
                    channel=np.full((4, 256), 32.), shadow=np.zeros((4, 256)),
                    g=dict(radiusCSS=22, q=np.zeros((4, 256, 2)),
                           d=np.full((4, 256), .5), nx=np.zeros((4, 256)),
                           ny=np.full((4, 256), -1.), arc=np.zeros((4, 256), bool)))

    def test_geometry_reference_and_shadow_mutations_refuse(self):
        a = self.observation()
        c.assert_equal_inputs(a, copy.deepcopy(a))
        for key in ('xy', 'channel', 'shadow'):
            b = copy.deepcopy(a)
            b[key].flat[0] += 1
            with self.subTest(key=key), self.assertRaises(AssertionError):
                c.assert_equal_inputs(a, b)
        for key in ('q', 'd', 'nx', 'ny', 'arc'):
            b = copy.deepcopy(a)
            b['g'][key].flat[0] = not b['g'][key].flat[0] if key == 'arc' else 7
            with self.subTest(key=key), self.assertRaises(AssertionError):
                c.assert_equal_inputs(a, b)
        for key, value in (('component', {}), ('scale', 2), ('bin', {'pixels': 5})):
            b = copy.deepcopy(a)
            b[key] = value
            with self.subTest(key=key), self.assertRaises(AssertionError):
                c.assert_equal_inputs(a, b)
        b = copy.deepcopy(a)
        b['g']['radiusCSS'] = 32
        with self.assertRaises(AssertionError):
            c.assert_equal_inputs(a, b)

    def test_common_nonuniform_reference_not_silently_admitted(self):
        a = self.observation()
        a['channel'][0, 0] = 31
        with self.assertRaises(AssertionError):
            c.assert_equal_inputs(a, copy.deepcopy(a))

    def test_saved_unchanged_provenance_loader(self):
        m, shadow, archive, materials = c.load_law()
        self.assertEqual(m.ROOT, c.SOURCE)
        for scheme in ('light', 'dark'):
            self.assertEqual(shadow.occlusion(44, materials[scheme+'-inactive'], .2), 0)

    def test_both_external_pixel_roots_denied(self):
        c.deny_external_pixels()
        for root in ('vitrea-w39', '.cache/vitrea-archives'):
            with self.subTest(root=root), self.assertRaises(PermissionError):
                (c.Path.home()/root/'intentionally-not-opened').read_bytes()


if __name__ == '__main__':
    unittest.main()
