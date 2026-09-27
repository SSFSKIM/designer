"""Certified-rejected endpoints cannot pull the remaining endpoint's objective."""
import unittest
import survivor_scope_runner as runner


class ScopeTests(unittest.TestCase):
    def test_m1_retains_only_light_inactive_m2_retains_both(self):
        light = dict(endpoint=1, role='calibration', cell='light')
        dark = dict(endpoint=3, role='calibration', cell='dark')
        self.assertEqual(runner.observations_for('M1', [dark, light]), [light])
        self.assertEqual(runner.observations_for('M2', [dark, light]), [dark, light])
        self.assertIs(runner.observations_for('M1', [dark, light])[0], light)

    def test_other_roles_poses_and_certified_m0_model_refused(self):
        for family in ('M1', 'M2'):
            for observation in (dict(endpoint=1, role='validation'),
                                dict(endpoint=0, role='calibration')):
                with self.assertRaises(PermissionError):
                    runner.observations_for(family, [observation])
        with self.assertRaises(ValueError):
            runner.observations_for('M0', [dict(endpoint=1, role='calibration')])


if __name__ == '__main__':
    unittest.main()
