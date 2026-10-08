#!/usr/bin/env python3
"""Synthetic target-chart tests; no native archive is an input to this suite."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

PATH = Path(__file__).with_name('uniform.py')
spec = importlib.util.spec_from_file_location('w50_uniform_fit', PATH)
U = importlib.util.module_from_spec(spec)
spec.loader.exec_module(U)


class UniformFitTests(unittest.TestCase):
    def test_bilinear_input_and_span_weights_hold_outer_rows(self):
        rows = np.array([[20, 28, 48, 60], [24, 32, 52, 64], [28, 36, 56, 68]])
        self.assertAlmostEqual(float(U.weights(4, 70) @ rows.ravel()), 26)
        self.assertAlmostEqual(float(U.weights(4, 32) @ rows.ravel()), 24)
        self.assertAlmostEqual(float(U.weights(4, 224) @ rows.ravel()), 32)
        with self.assertRaises(ValueError):
            U.weights(64, 44)

    def test_recovers_an_identified_chart_without_reading_hidden_rows(self):
        rows = np.array([[20, 28, 48, 60], [24, 32, 52, 64], [28, 36, 56, 68]])
        readings = []
        for span, row in zip((44, 96, 160), rows):
            for x, y in zip((0, 8, 28, 40), row):
                readings.append(dict(inputCode=x, span=span, value=float(y), role='calibration'))
        readings.append(dict(inputCode=4, span=128, value=30, role='validation'))
        result = U.fit(readings, joins=[dict(span=s, value=90) for s in (32, 44, 96, 128, 160, 224)])
        np.testing.assert_allclose(np.array(result['rows']) * 255, rows, atol=2e-5)
        self.assertLess(result['worstErrorCodes'], 2e-5)
        self.assertEqual(result['kind'], 'analytical-chart-target-fit-not-rendered-verdict')

    def test_conflicting_channel_targets_return_obstruction_not_false_exact_fit(self):
        readings = [dict(inputCode=0, span=44, value=v, role='calibration') for v in (20, 24)]
        result = U.fit(readings, joins=[dict(span=44, value=90)])
        self.assertAlmostEqual(result['worstErrorCodes'], 2, places=5)
        self.assertAlmostEqual(result['rows'][0][0] * 255, 22, places=4)

    def test_decreasing_native_targets_cannot_create_a_decreasing_chart(self):
        readings = [dict(inputCode=x, span=44, value=y, role='calibration')
                    for x, y in ((0, 32), (8, 20))]
        result = U.fit(readings, joins=[dict(span=44, value=90)])
        self.assertAlmostEqual(result['worstErrorCodes'], 6, places=5)
        self.assertTrue(np.all(np.diff(result['rows'], axis=1) >= -1e-9))

    def test_fixed_join_limits_actual_interpolated_span_not_just_row_anchors(self):
        readings = [dict(inputCode=40, span=s, value=40, role='calibration') for s in (44, 96, 160)]
        joins = [dict(span=s, value=50) for s in (44, 96, 160)] + [dict(span=128, value=34)]
        result = U.fit(readings, joins=joins)
        self.assertAlmostEqual(result['worstErrorCodes'], 6, places=4)
        self.assertLessEqual(float(U.weights(40, 128) @ (np.array(result['rows']).ravel() * 255)), 34 + 1e-7)

    def test_refuses_withheld_and_nonfinite_observations(self):
        for role in ('blind', 'historical-prediction-check', 'holdout', 'gate'):
            with self.assertRaises(ValueError):
                U.fit([dict(inputCode=0, span=44, value=20, role=role)], joins=[dict(span=44, value=90)])
        for field in ('inputCode', 'span', 'value'):
            row = dict(inputCode=0, span=44, value=20, role='calibration')
            row[field] = float('nan')
            with self.assertRaises(ValueError):
                U.fit([row], joins=[dict(span=44, value=90)])
        with self.assertRaises(ValueError):
            U.fit([], joins=[dict(span=44, value=90)])
        with self.assertRaises(ValueError):
            U.fit([dict(inputCode=0, span=44, value=20, role='calibration')], joins=[])

    def test_joint_initializer_shares_worst_bound_and_preserves_mean_multiplicity(self):
        endpoints = ('active.dark.0.25', 'receded.dark.0.25', 'active.dark.0.5', 'receded.dark.0.5')
        readings = [dict(endpoint=e, inputCode=0, span=44, value=v, role='calibration')
                    for e, values in zip(endpoints, ((20, 24), (10, 10, 10, 12), (5,), (5,)))
                    for v in values]
        joins = [dict(endpoint=e, span=44, value=90) for e in endpoints]
        result = U.fit_joint(readings, joins=joins)
        self.assertEqual(set(result['endpoints']), set(endpoints))
        self.assertEqual(result['observations'], 8)
        self.assertAlmostEqual(result['worstErrorCodes'], 2, places=5)
        self.assertAlmostEqual(result['meanAbsoluteErrorCodes'], .75, places=5)
        # The second endpoint's own minimax would choose11. Its shared-bound mean optimum is10.
        self.assertAlmostEqual(result['endpoints'][endpoints[1]][0][0] * 255, 10, places=4)
        self.assertEqual(result['kind'], 'joint-analytical-initializer-not-rendered-verdict')
        for bad in (readings[:-1], [{**readings[0], 'endpoint': 'other'}] + readings[1:]):
            with self.assertRaises(ValueError): U.fit_joint(bad, joins=joins)
        with self.assertRaises(ValueError): U.fit_joint(readings, joins=joins[:-1])

    def test_pure_score_keeps_each_channel_and_observation_and_never_claims_gate_pass(self):
        rows = {e: [[.1, .2, .3, .4]]*3 for e in U.ENDPOINTS}
        readings = [dict(endpoint=e, inputCode=0, span=44, role='calibration',
                         channel=c, statistic='central8-channel-median', value=v)
                    for e in U.ENDPOINTS for c,v in zip(('R','G','B'),(23.5,25.5,27.5))]
        score=U.score_joint(readings,rows)
        self.assertEqual(score['observations'],12)
        self.assertAlmostEqual(score['worstErrorCodes'],2)
        self.assertAlmostEqual(score['meanAbsoluteErrorCodes'],4/3)
        self.assertEqual([r['errorCodes'] for r in score['residuals'][:3]],[2,0,2])
        self.assertNotIn('passes',score)
        self.assertEqual(score['status'],'ANALYTICAL_SCORE_ONLY')

    def test_mean_error_breaks_worst_error_tie(self):
        readings = [dict(inputCode=0, span=44, value=v, role='calibration') for v in (20, 24)]
        readings += [dict(inputCode=0, span=160, value=30, role='validation') for _ in range(3)]
        result = U.fit(readings, joins=[dict(span=s, value=90) for s in (44, 96, 160)])
        self.assertAlmostEqual(result['rows'][2][0] * 255, 30, places=4)
        self.assertAlmostEqual(result['meanAbsoluteErrorCodes'], 0.8, places=5)


if __name__ == '__main__':
    unittest.main()
