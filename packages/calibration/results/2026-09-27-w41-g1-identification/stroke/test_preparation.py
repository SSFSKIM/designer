"""Synthetic only: exact reuse cannot change subpixel order, rails or membership."""
import unittest
import numpy as np
import replay

m, f = replay.m, replay.f


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.shape = m.readers.Shape('capsule-circular', (120., 44.), (20., 20.))
        self.xy = np.array([[80, 19], [80, 64], [140, 41], [19, 41],
                            [138, 31], [138, 52], [21, 31], [21, 52], [80, 18]])

    def test_reuse_matches_full_subpixel_composite_all_families_and_rivals(self):
        # Moving nonlinear material after pixel averaging breaks the gradient case.
        rng = np.random.default_rng(42)
        max_error = 0.
        for scale in (1, 2):
            g = m.samples(self.shape, self.xy * scale, scale)
            fall = rng.uniform(0, .6, g['d'].shape)
            for gradient in (False, True):
                image = np.full((170, 340, 3), [32., 192., 32.])
                if gradient:
                    image += np.arange(170)[:, None, None] * .1
                b = m.bilinear(image, g['q'])
                compact = replay.CompactComposite(g, b, fall)
                for endpoint in range(4):
                    amplitude = .12 if endpoint in (0, 2) else 0.
                    for family in ('M0', 'M1', 'M2'):
                        for css, curvature in ((False, False), (True, False), (False, True)):
                            lo, hi, _ = f.domain(family, curvature)
                            for _ in range(3):
                                q = rng.uniform(lo, hi)
                                width, beta, gamma, colour = f.unpack(q, family, endpoint)
                                dense = m.composite(g, b, b * (1-amplitude*fall[..., None]),
                                    width, beta, gamma, family, colour, dark=endpoint >= 2,
                                    css_width=css, rho=q[-1] if curvature else None)
                                actual = compact.predict(q, endpoint, amplitude, family, css, curvature)
                                max_error = max(max_error, float(np.max(abs(actual-dense))))
                                np.testing.assert_allclose(actual, dense, atol=2e-12, rtol=0)
        print('maximum compact/dense difference codes', max_error)

    def test_same_coverage_reuses_operator_without_freezing_material(self):
        g = m.samples(self.shape, self.xy, 1)
        b = np.full((*g['d'].shape, 3), 128.)
        compact = replay.CompactComposite(g, b, np.zeros(g['d'].shape))
        _, _, q = f.domain('M0')
        initial = compact.predict(q, 1, 0., 'M0')
        q[10] = -40
        changed = compact.predict(q, 1, 0., 'M0')
        self.assertGreater(np.max(abs(initial-changed)), 1)
        self.assertEqual(compact.operator_builds, 1)

    def test_interior_witness_zero_is_not_a_body_accuracy_test(self):
        xy = np.array([[80, 20], [80, 21], [80, 22]])
        g = m.samples(self.shape, xy, 1)
        for width in (0., 1., 2.):
            np.testing.assert_array_equal(m.coverage(g, width, .4, .2), 0.)

    def test_required_bins_keep_population_deficiency_and_full_outer_range(self):
        geo = m.readers.geometry((90, 170), [self.shape], 1)
        bins, labels, selected = replay.required_bins(geo, 0)
        self.assertEqual({b['shell'] for b in bins}, {0, 1, 2, 3})
        self.assertEqual(len(bins), 80)
        self.assertTrue(any(b['pixels'] == 0 for b in bins))
        self.assertTrue(all(bins[i]['pixels'] >= 4 for i in np.unique(labels[selected])))

    def test_scoring_cannot_cancel_pixel_errors_or_drop_repeat_failure(self):
        prediction = np.full((4, 3), 128.)
        runs = np.full((7, 4, 3), 128.)
        runs[0, :, 0] = [130, 126, 130, 126]
        row = m.score_bin(prediction, runs)
        self.assertFalse(row['survives'])
        self.assertEqual(row['runs'][0]['errorCodes'][0], 2.)
        self.assertEqual(row['median']['errorCodes'][0], 0.)

    def test_held_shadow_factorization_matches_sealed_supplied_path_predictor(self):
        for scale in (1, 2):
            g = m.samples(self.shape, self.xy * scale, scale)
            for name, material in replay.shadow.materials().items():
                fall = replay.held_falloff(g, self.shape, material)
                for luma in (0., .04, .3, .85, 1.):
                    amplitude = replay.shadow_amplitude(self.shape, material, luma)
                    expected = replay.shadow.at(g['q'], self.shape, scale, material, luma)
                    np.testing.assert_allclose(amplitude*fall, expected, rtol=0, atol=1e-16)

    def test_column_keeps_one_cell_mass_and_every_repeat_member(self):
        # Splitting the two members into independent observations would give
        # the column twice the mass of a single-member native cell.
        shapes = [dict(kind='capsule-circular', size=[120, 44]) for _ in range(2)]
        component = dict(kind='column', items=shapes, suppliedPaths=[
            dict(kind='capsule-circular', rect=[0, 0, 120, 44], frameOrigin=[20, y])
            for y in (20, 100)])
        image = np.full((170, 170, 3), 128, dtype=np.uint8)
        payload = dict(component=component, scale=1, scheme='light', pose='inactive',
                       rgb=image, noGlass=image)
        prepared = replay.Preparation().prepare('synthetic', 'calibration', [payload]*7,
                                                ['synthetic']*7, 'synthetic')
        self.assertEqual(len(prepared['parts']), 2)
        self.assertEqual(prepared['runs'].shape, (7, len(prepared['target']), 3))
        _, weights, groups = f.objective_layout([prepared])
        self.assertAlmostEqual(weights.sum(), 1.)
        self.assertTrue(all(w['zeroStrokeWitness'] for part in prepared['parts']
                            for w in part['interior']))
        _, _, q = f.domain('M0')
        np.testing.assert_allclose(replay.compact_predict(q, prepared, 'M0'), 128,
                                   rtol=0, atol=1e-12)
        changed = dict(payload, noGlass=image.copy())
        changed['noGlass'][0, 0, 0] = 127
        with self.assertRaisesRegex(ValueError, 'reference varies'):
            replay.Preparation().prepare('synthetic', 'calibration',
                [payload]*6+[changed], ['synthetic']*7, 'synthetic')

    def test_fit_adapter_rejects_validation_before_optimizer(self):
        with self.assertRaisesRegex(PermissionError, 'calibration'):
            replay.fit_observations([{'role': 'validation'}], 'M0')


if __name__ == '__main__':
    unittest.main()
