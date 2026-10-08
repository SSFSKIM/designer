"""Synthetic DL5h regression tests; no native or captured evidence is opened."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('repeat_core', Path(__file__).with_name('core.py'))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)


def stat(value, bar=.5, units='encoded-luma-codes'):
    return dict(value=value, units=units, support='deep8', repeat=dict(bar=bar),
                provenance={'source': 'synthetic-own-native-repeats'})


class RepeatTests(unittest.TestCase):
    def test_native_bar_not_landing_budget(self):
        result = C.compare_statistics({'level':stat(100)}, {'level':stat(100.04)})
        self.assertEqual(result['level']['limit'], .05)
        self.assertEqual(result['level']['first'], 100)
        with self.assertRaises(C.InstrumentFault):
            C.compare_statistics({'level':stat(100)}, {'level':stat(100.075)})

    def test_channels_never_cancel_and_cuts_never_pool(self):
        first = {'deep':stat([10.,10.,10.], [.5]*3, 'encoded-RGB-codes'),
                 'center':stat([10.,10.,10.], [.5]*3, 'encoded-RGB-codes')}
        second = {'deep':stat([10.06,9.94,10.], [.5]*3, 'encoded-RGB-codes'),
                  'center':stat([10.,10.,10.], [.5]*3, 'encoded-RGB-codes')}
        with self.assertRaises(C.InstrumentFault): C.compare_statistics(first, second)

    def test_missing_optional_and_owner_statistics_cannot_vacuously_admit(self):
        for first, second in [({}, {}), ({'T1':stat(None, None)}, {'T1':stat(None,None)}),
                              ({'owner':stat(1,None)}, {'owner':stat(1,None)})]:
            with self.assertRaises(C.IdentityRequired): C.compare_statistics(first, second)

    def test_t1_fine_and_low_each_have_own_linear_bar(self):
        first = {name:stat(.01, .002, 'linear-luma') for name in ('T1-fine','T1-low')}
        second = {name:stat(.01, .002, 'linear-luma') for name in first}
        second['T1-fine']['value'] = .0103
        with self.assertRaises(C.InstrumentFault): C.compare_statistics(first, second)
        del second['T1-fine']
        with self.assertRaises(C.InstrumentFault): C.compare_statistics(first, second)

    def test_nonfinite_and_budget_substitution_refused(self):
        for value in (float('nan'), float('inf')):
            with self.assertRaises(C.InstrumentFault):
                C.compare_statistics({'x':stat(1)}, {'x':stat(value)})
        with self.assertRaises(C.InstrumentFault):
            C.compare_statistics({'x':stat(1)}, {'x':stat(1,5)})

    def test_fault_retains_all_cuts_and_missing_budget_never_fabricates_difference(self):
        with self.assertRaises(C.InstrumentFault) as caught:
            C.compare_statistics({'a':stat(0),'b':stat(0)}, {'a':stat(.2),'b':stat(.3)})
        self.assertEqual(caught.exception.differences['a']['difference'],.2)
        self.assertEqual(caught.exception.differences['b']['difference'],.3)
        with self.assertRaises(C.IdentityRequired) as missing:
            C.compare_statistics({'T1':stat(None,None)}, {'T1':stat(None,None)})
        self.assertEqual(missing.exception.differences['T1']['status'],'STRICT_IDENTITY_REQUIRED')
        self.assertNotIn('difference',missing.exception.differences['T1'])

    def test_fixed_budget_derivation_requires_own_positive_scalar(self):
        derived = C.bar_from_fixed_budget(1, {'referenceKey':['p','webgpu','s','T1']})
        self.assertEqual(derived['bar'], .5)
        self.assertEqual(derived['B'], 1)
        self.assertIn('max(code', derived['formula'])
        for value in (None, 0, -1, True, float('nan'), [1,1,1]):
            with self.assertRaises(C.IdentityRequired):
                C.bar_from_fixed_budget(value, {'referenceKey':['p','webgpu','s','T1']})


if __name__ == '__main__': unittest.main()
