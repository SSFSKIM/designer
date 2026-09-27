import copy
import unittest
from unittest.mock import patch
import observe
from observe import verdict


class GateTests(unittest.TestCase):
    def setUp(self):
        self.good = {'settings': {k: {'exitCode': 0, 'stdout': v} for k, v in
            [('reduceTransparency', '0'), ('increaseContrast', '0'),
             ('NSGlassTintAmount', '0.5')]}, 'foreignProcesses': [], 'processCensus': {'usable': True},
            'idle': {'exitCode': 0, 'stdout': '"HIDIdleTime" = 60000000000'}}

    def test_all_facts_required(self):
        self.assertTrue(verdict(self.good)['passes'])
        for key in self.good['settings']:
            row = copy.deepcopy(self.good)
            row['settings'][key]['exitCode'] = 1
            self.assertFalse(verdict(row)['passes'])
        for key, value in [('reduceTransparency', '1'), ('increaseContrast', '1'),
                           ('NSGlassTintAmount', '0.6')]:
            row = copy.deepcopy(self.good)
            row['settings'][key]['stdout'] = value
            self.assertFalse(verdict(row)['passes'])

    def test_failed_or_unusable_full_census_refuses_even_when_no_foreign_process_listed(self):
        for exit_code, stdout in [(1, ''), (0, ''), (0, 'not a ps row')]:
            with patch.object(observe.machine, 'read', side_effect=lambda *args: (
                    {'command': list(args), 'exitCode': exit_code, 'stdout': stdout, 'stderr': 'ps failed'}
                    if args[0] == 'ps' else {'exitCode': 0, 'stdout': '0'})):
                row = observe.observe()
            self.assertFalse(row['processCensus']['usable'])
            self.assertEqual(row['foreignProcesses'], [])
            self.assertIn('foreignProcessCountZero', row['verdict']['refusals'])

    def test_census_excludes_ancestors_but_refuses_foreign_browsers(self):
        with patch.object(observe.os, 'getpid', return_value=201), \
             patch.object(observe.machine, 'read', return_value={
                'command': ['ps'], 'exitCode': 0, 'stdout':
                '201 100 python observe.py\n100 1 Chromium parent\n300 1 Google Chrome\n',
                'stderr': ''}):
            census = observe.process_census()
        self.assertTrue(census['usable'])
        self.assertEqual(census['foreignProcesses'], [['300', '1', 'Google Chrome']])

    def test_foreign_or_recent_input_refuses(self):
        row = copy.deepcopy(self.good)
        row['foreignProcesses'] = [['123', '1', 'Google Chrome']]
        self.assertFalse(verdict(row)['passes'])
        row = copy.deepcopy(self.good)
        row['idle']['stdout'] = '"HIDIdleTime" = 59999999999'
        self.assertFalse(verdict(row)['passes'])
        row['idle']['stdout'] = 'no idle fact'
        self.assertFalse(verdict(row)['passes'])
        row['idle']['stdout'] = self.good['idle']['stdout']
        row['idle']['exitCode'] = 1
        self.assertFalse(verdict(row)['passes'])


if __name__ == '__main__': unittest.main()
