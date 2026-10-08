"""Pure projection tests preserve measured arrays, native masks and original reference fields."""
import copy
from pathlib import Path
import types
import unittest

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


P = source(HERE/'projection.py', 'w50_projection_tests')


class ProjectionTests(unittest.TestCase):
    def row(self, statistic='deep8-channel-median'):
        return {'profile': 'synthetic', 'renderer': 'webgpu', 'scene': 'cell', 'statistic': statistic,
                'role': 'calibration', 'support': 'Original support prose.', 'B': None,
                'native': None, 'current': None, 'historical': []}

    def reading(self, value, *, support='deep8', units='encoded-RGB-codes', native=None):
        witnesses = [{'run': run, 'maskShape': [64, 64], 'pixels': 10,
                      'maskPackedBitsSha256': str(run)*64} for run in (1, 2, 3)]
        return {'status': 'MEASURED', 'measurementStatus': 'MEASURED', 'value': value,
            'nativeValue': value if native is None else native, 'required': True,
            'support': support, 'units': units, 'nativeRepeat': {'barCodes': [.5]*3, 'passes': True},
            'nativeSupportWitnesses': witnesses,
            'nativeRuns': [{'run': n, 'sha256': str(n)*64} for n in (1, 2, 3)]}

    def provenance(self, digit='a'):
        return {'capture': {'path': '/synthetic/first.png', 'sha256': digit*64},
            'material': {'documentPair': {'activeSha256': 'b'*64, 'recededSha256': 'c'*64}},
            'reading': 'first'}

    def test_rgb_arrays_native_witnesses_and_reference_nulls_survive_projection(self):
        row = self.row(); before = copy.deepcopy(row)
        candidate = self.reading([11, 21, 31], native=[10, 20, 30])
        current = self.reading([12, 22, 32], native=[10, 20, 30])
        result = P.reading(candidate, current, self.provenance(), self.provenance('d'),
                           reported=False, eligible_empty=False)
        self.assertEqual((result['native'], result['current'], result['candidate']),
                         ([10, 20, 30], [12, 22, 32], [11, 21, 31]))
        self.assertEqual(result['nativeSupportWitnesses'], candidate['nativeSupportWitnesses'])
        self.assertEqual((result['code'], result['bar'], result['B']), ([1]*3, [.5]*3, [1]*3))
        self.assertEqual(row, before)
        native = result['evidence']['native']
        self.assertEqual(native['numericIdentity']['documentPair'], None)
        self.assertEqual(native['captureIdentity']['kind'], 'native-three-run-cohort')
        self.assertEqual(len(native['captureIdentity']['runs']), 3)
        self.assertEqual(result['evidence']['candidate']['numericIdentity']['captureSha256'], 'a'*64)

    def test_reported_rows_keep_null_budget_but_native_repeat_is_not_discarded(self):
        candidate = self.reading(.2, support='full-silhouette', units='linear-luma', native=.1)
        candidate.update(required=False, status='REPORTED', B=None)
        candidate['nativeRepeat'] = {'codeStepLinear': .01, 'barLinear': .005, 'barCodes': .5}
        current = dict(candidate, value=.15)
        result = P.reading(candidate, current, self.provenance(), self.provenance('d'),
                           reported=True, eligible_empty=False)
        self.assertIsNone(result['B']); self.assertTrue(result['reported'])
        self.assertEqual(result['nativeRepeat'], candidate['nativeRepeat'])
        self.assertEqual(result['measurementStatus'], 'MEASURED')

    def test_empty_optional_t1_requires_exact_eligibility_and_all_three_zero_witnesses(self):
        candidate = self.reading(None, support='full-silhouette', units='linear-luma')
        candidate.update(status='UNMEASURED_EMPTY_SUPPORT', measurementStatus='UNMEASURED_EMPTY_SUPPORT',
                         required=False, nativeRepeat=None, B=None)
        for item in candidate['nativeSupportWitnesses']: item['pixels'] = 0
        current = copy.deepcopy(candidate)
        result = P.reading(candidate, current, self.provenance(), self.provenance('d'),
                           reported=True, eligible_empty=True)
        self.assertIsNone(result['candidate']); self.assertIsNone(result['native'])
        self.assertEqual(result['measurementStatus'], 'UNMEASURED_EMPTY_SUPPORT')
        for change in ('ineligible', 'nonzero', 'two-runs'):
            with self.subTest(change=change):
                bad = copy.deepcopy(candidate)
                if change == 'nonzero': bad['nativeSupportWitnesses'][1]['pixels'] = 1
                elif change == 'two-runs': bad['nativeSupportWitnesses'].pop()
                with self.assertRaises(ValueError):
                    P.reading(bad, current, self.provenance(), self.provenance('d'),
                              reported=True, eligible_empty=change != 'ineligible')

    def test_support_or_native_source_mismatch_cannot_borrow_current_measurement(self):
        candidate = self.reading([1, 2, 3]); current = copy.deepcopy(candidate)
        for field, value in (('units', 'encoded-luma-codes'), ('support', 'center8'),
                             ('nativeValue', [4, 5, 6])):
            with self.subTest(field=field):
                changed = dict(current, **{field: value})
                with self.assertRaises(ValueError):
                    P.reading(candidate, changed, self.provenance(), self.provenance('d'),
                              reported=False, eligible_empty=False)

    def test_canonical_compound_and_fine_companion_preserve_one_original_inventory_key(self):
        row = self.row('low-end-path-level')
        self.assertEqual(P.statistic_names(row, {'family': 'impulse'}),
                         ['deep8-far24-luma-mean', 'deep8-far24-luma-median'])
        self.assertEqual(P.statistic_names(row, {'family': 'solid'}), ['deep8-channel-median'])
        self.assertEqual(row['statistic'], 'low-end-path-level')
        text = self.row('T1-low')
        self.assertEqual(P.statistic_names(text, {'family': 'texture'}), ['T1-low', 'T1-fine'])
        self.assertEqual(P.statistic_names(self.row('owner-contracts'), {}), [])
        with self.assertRaises(ValueError): P.statistic_names(row, {'family': 'texture'})

    def test_native_budget_is_not_a_transport_noise_or_an_rgb_channel_average(self):
        candidate = self.reading([10, 20, 30])
        candidate['nativeRepeat']['barCodes'] = [.5, .7, .9]
        result = P.reading(candidate, candidate, self.provenance(), self.provenance('d'),
                           reported=False, eligible_empty=False)
        self.assertEqual(result['bar'], [.5, .7, .9])
        self.assertEqual(result['B'], [1, 1.4, 1.8])
        scalar = self.reading(.2, units='linear-luma', support='full-silhouette')
        scalar['nativeRepeat'] = {'codeStepLinear': .004, 'barLinear': .003}
        result = P.reading(scalar, scalar, self.provenance(), self.provenance('d'),
                           reported=False, eligible_empty=False)
        self.assertEqual((result['code'], result['bar'], result['B']), (.004, .003, .006))


if __name__ == '__main__':
    unittest.main()
