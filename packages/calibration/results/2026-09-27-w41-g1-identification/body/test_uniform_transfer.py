"""Synthetic coverage tests: every glass member survives selection, not every control."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

spec = importlib.util.spec_from_file_location('uniform_transfer', Path(__file__).with_name('uniform-transfer.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Coverage(unittest.TestCase):
    def census(self, component, role='calibration', background='solid', admitted=True, existing=()):
        wave = SimpleNamespace(scenes={'s': {'background': 'b'}}, roles={'s': role},
            spec={'backgrounds': {'b': {'kind': background}}}, component=lambda sid: component)
        reader = SimpleNamespace(entries={('profile/s', 'crop'): {}} if admitted else {})
        return m.census_row(wave, reader, 'profile/s', existing)

    def test_small_solid_control_is_not_dropped(self):
        r = self.census({'kind': 'capsule-circular', 'size': [120, 44]})
        self.assertEqual(r['disposition'], 'covered: supplemental transfer')
        self.assertEqual(len(r['members']), 1)

    def test_column_keeps_each_glass_member(self):
        r = self.census({'kind': 'column', 'items': [
            {'kind': 'capsule-circular', 'size': [120, 44]},
            {'kind': 'rrect', 'size': [120, 44]},
            {'kind': 'rrect', 'size': [120, 44], 'opaque': True}]})
        self.assertEqual([v['disposition'] for v in r['members']],
            ['covered: supplemental transfer'] * 2 + ['excluded: opaque control, not glass'])

    def test_explicit_exclusions(self):
        shape = {'kind': 'rrect', 'size': [120, 44]}
        cases = [({'kind': 'none'}, {}, 'no-glass reference'),
                 (shape, {'role': 'holdout'}, 'holdout sealed'),
                 (shape, {'admitted': False}, 'no admitted crop'),
                 (shape, {'background': 'linear-gradient'}, 'structured background'),
                 ({**shape, 'opaque': True}, {}, 'opaque controls only')]
        for component, kwargs, reason in cases:
            with self.subTest(reason=reason):
                self.assertIn(reason, self.census(component, **kwargs)['disposition'])

    def test_existing_members_are_not_reread(self):
        r = self.census({'kind': 'rrect', 'size': [120, 44]}, existing={'profile/s'})
        self.assertEqual(r['disposition'], 'covered: original step2')

    def test_distinct_members_rails_and_all_repeats(self):
        def deep(value):
            return dict(medianRGB=value, runMediansRGB=[value] * 7, barRGB=[.5] * 3, pixels=[4] * 7)
        row = dict(cell='profile/s', role='calibration', scale=2, endpoint='light-active',
            inputCodes=[255, 128, 0], stateMembership=['state'] * 7,
            members=[deep([255, 128, 0]), deep([252, 120, 0])])
        candidate = dict(family='E3', method='globalMinimax', coefficients=[1, 1, 1],
            neutral=[40, 56, 72, 88, 104, 128, 150])
        metadata = dict(kind='rrect', size=[120, 44])
        scores = [m.score_member(candidate, row, i, metadata, 'covered: supplemental transfer') for i in [0, 1]]
        summary = m.summary_group(scores)
        self.assertEqual((summary['cells'], summary['members']), (1, 2))
        self.assertEqual((summary['failedCells'], summary['failedMembers']), (1, 1))
        self.assertEqual(summary['measuredFailedChannels'], 1)
        self.assertEqual(summary['repeatMeasuredFailedChannels'], 7)
        self.assertEqual(summary['railFailures'], 0)
        self.assertEqual(summary['statusCounts']['censored-bound-satisfied'], 4)
        self.assertEqual(summary['repeatStatusCounts']['censored-bound-satisfied'], 28)
        self.assertEqual(summary['worstMeasured']['member'], 1)


if __name__ == '__main__':
    unittest.main()
