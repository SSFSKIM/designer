import copy
import unittest
from observe import verdict


class GateTests(unittest.TestCase):
    def setUp(self):
        self.good = {'settings': {k: {'exitCode': 0, 'stdout': v} for k, v in
            [('reduceTransparency', '0'), ('increaseContrast', '0'),
             ('NSGlassTintAmount', '0.5')]}, 'foreignProcesses': [],
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
