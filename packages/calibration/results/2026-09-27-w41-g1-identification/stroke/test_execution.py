"""Synthetic execution plumbing; never runs an optimizer or archive reader."""
import tempfile
from pathlib import Path
import unittest
import numpy as np
import execute
import diagnostics
import replay
import scoring


class ExecutionTests(unittest.TestCase):
    def observation(self):
        image = np.full((90, 170, 3), 128, dtype=np.uint8)
        component = dict(kind='capsule-circular', size=[120, 44], suppliedPaths=[
            dict(kind='capsule-circular', rect=[0, 0, 120, 44], frameOrigin=[20, 20])])
        payload = dict(component=component, scale=1, scheme='light', pose='inactive',
                       rgb=image, noGlass=image)
        return replay.Preparation().prepare('synthetic/g128__inactive', 'validation',
            [payload]*7, ['synthetic']*7, 'g128')

    def test_sensitivity_keeps_frozen_coefficients_and_all_admitted_bins(self):
        observation = self.observation()
        _, _, q = replay.f.domain('M0')
        q[10] = -30
        frozen = q.copy()
        rows = []
        result = execute.sensitivity([observation], q, 'M0', False, False, rows.append)
        np.testing.assert_array_equal(q, frozen)
        self.assertEqual(len(rows), sum(b['pixels'] >= 4
            for p in observation['parts'] for b in p['bins']))
        self.assertFalse(result['coefficientsChanged'])
        self.assertTrue(all(row['coefficientsFixed'] for row in rows))

    def test_zero_controls_and_outer_rows_not_removed_by_candidate_width(self):
        observation = self.observation()
        controls = scoring.inactive_zero_controls([observation])
        _, _, q = replay.f.domain('M0')
        q[0], q[10] = 2., -40.
        prediction = replay.compact_predict(q, observation, 'M0')
        rows = list(scoring.bin_rows(observation, prediction, controls))
        self.assertEqual(len(rows), 80)
        self.assertTrue(all(row['zeroInactiveControl'] is not None
            for row in rows if row['score']['pixels'] >= 4))
        self.assertTrue(any(row['score']['worstChannelFailure'] for row in rows))

    def test_boundary_reports_only_stroke_increment_without_accuracy_claim(self):
        observation = self.observation()
        _, _, q = replay.f.domain('M0')
        rows = []
        result = diagnostics.straddling([observation], q, 'M0', False, False, rows.append)
        self.assertGreater(len(rows), 0)
        self.assertFalse(result['usedForSurvival'])
        self.assertLess(result['maximumPixelStrokeIncrementCodes'], 1e-12)
        q[10] = -40
        rows = []
        result = diagnostics.straddling([observation], q, 'M0', False, False, rows.append)
        self.assertGreater(result['maximumPixelStrokeIncrementCodes'], 1.)
        self.assertTrue(all(row['status'] == 'DIAGNOSTIC' for row in rows))

    def test_additive_outputs_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'evidence.json'
            execute.json_write(path, {'first': True})
            with self.assertRaises(FileExistsError):
                execute.json_write(path, {'first': False})


if __name__ == '__main__':
    unittest.main()
