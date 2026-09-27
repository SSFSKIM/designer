"""The narrowed transfer cannot read native evidence before all selections freeze."""
import json
import hashlib
import numpy as np
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import survivor_scope_complete as complete


def result(family, geometry, index):
    low, high, identity = complete.r.f.domain(family, geometry == 'curvature')
    starts = [identity, *np.random.default_rng(4100).uniform(low, high, (15, len(identity)))]
    objective = dict(converged=True, weightedSquaredError=1., maximumCodes=1.,
                     zeroFloorBracketCodes=None, coefficients=identity.tolist(),
                     railDeficitCodes=0., rank=1, singularValues=[1.])
    return dict(family=family, cssWidth=geometry == 'css', curvature=geometry == 'curvature',
                fittedEndpoints=['light-inactive'] if family == 'M1'
                    else ['light-inactive', 'dark-inactive'],
                starts=[dict(startIndex=index, initial=starts[index].tolist(),
                             leastSquares=objective, minimax=objective)])


class CompleteTests(unittest.TestCase):
    def test_four_remaining_models_are_frozen_before_any_native_reader(self):
        with tempfile.TemporaryDirectory(dir=complete.runner.PRIMARY, prefix='synthetic-complete-') as root:
            root = Path(root); output = root/'output'
            partitions = [root/f'partition-{i}' for i in range(3)] + [root/'scheduler-results']
            for partition in partitions:
                partition.mkdir()
            for family in ('M1', 'M2'):
                for geometry in ('device', 'curvature'):
                    for index in range(16):
                        (partitions[index % 4]/f'{geometry}-{family}-start-{index:02d}.json').write_text(
                            json.dumps(result(family, geometry, index)))
            def before_native(*args):
                pinned = json.loads((output/'frozen-optimizer-inputs.json').read_text())
                self.assertEqual(len(pinned), 64)
                self.assertTrue(all(hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
                                    for path, digest in pinned.items()))
                self.assertEqual(len(list(output.glob('*-optimizer.json'))), 4)
                raise RuntimeError('synthetic stops at the native boundary')
            with patch.object(sys, 'argv', ['complete', *[arg for partition in partitions
                    for arg in ('--partition', str(partition))], '--out', str(output)]), \
                    patch.object(complete.scope, 'verify_authority', return_value={'synthetic': True}), \
                    patch.object(complete.r, 'Preparation', return_value=object()), \
                    patch.object(complete.runner, 'load_inactive', side_effect=before_native):
                with self.assertRaisesRegex(RuntimeError, 'synthetic stops'):
                    complete.main()

    def test_broken_seal_refuses_native_load_and_output_creation(self):
        with tempfile.TemporaryDirectory(dir=complete.runner.PRIMARY, prefix='synthetic-complete-') as root:
            root = Path(root); partition = root/'partition'; partition.mkdir(); output = root/'output'
            for family in ('M1', 'M2'):
                for geometry in ('device', 'curvature'):
                    for index in range(16):
                        (partition/f'{geometry}-{family}-start-{index:02d}.json').write_text(
                            json.dumps(result(family, geometry, index)))
            with patch.object(sys, 'argv', ['complete', '--partition', str(partition),
                                           '--out', str(output)]), \
                    patch.object(complete.scope, 'verify_authority', return_value={'synthetic': True}), \
                    patch.object(complete.r, 'verify_seal', side_effect=ValueError('broken seal')), \
                    patch.object(complete.r, 'Preparation', side_effect=AssertionError('native forbidden')), \
                    patch.object(complete.runner, 'load_inactive', side_effect=AssertionError('native forbidden')):
                with self.assertRaisesRegex(ValueError, 'broken seal'):
                    complete.main()
            self.assertFalse(output.exists())

    def test_paired_m1_result_refused_before_reader_or_output_creation(self):
        with tempfile.TemporaryDirectory(dir=complete.runner.PRIMARY, prefix='synthetic-complete-') as root:
            root = Path(root); partition = root/'partition'; partition.mkdir(); output = root/'output'
            old = result('M1', 'device', 0)
            old['fittedEndpoints'] = ['light-inactive', 'dark-inactive']
            (partition/'device-M1-start-00.json').write_text(json.dumps(old))
            with patch.object(sys, 'argv', ['complete', '--partition', str(partition), '--out', str(output)]), \
                    patch.object(complete.scope, 'verify_authority', return_value={'synthetic': True}), \
                    patch.object(complete.runner, 'load_inactive', side_effect=AssertionError('native forbidden')):
                with self.assertRaisesRegex(ValueError, 'different endpoint scope'):
                    complete.main()
            self.assertFalse(output.exists())

    def test_duplicate_filename_index_and_incomplete_start_fail_before_native(self):
        with tempfile.TemporaryDirectory(dir=complete.runner.PRIMARY, prefix='synthetic-complete-') as root:
            root = Path(root); a = root/'a'; b = root/'b'; a.mkdir(); b.mkdir()
            path = a/'device-M1-start-00.json'
            path.write_text(json.dumps(result('M1', 'device', 0)))
            (b/path.name).write_text(path.read_text())
            with patch.object(sys, 'argv', ['complete', '--partition', str(a), '--partition', str(b),
                                           '--out', str(root/'out')]), \
                    patch.object(complete.scope, 'verify_authority', return_value={'synthetic': True}), \
                    patch.object(complete.runner, 'load_inactive', side_effect=AssertionError('native forbidden')):
                with self.assertRaisesRegex(ValueError, 'duplicate'):
                    complete.main()
            self.assertFalse((root/'out').exists())
            (b/path.name).unlink()
            with patch.object(sys, 'argv', ['complete', '--partition', str(a), '--out', str(root/'out')]), \
                    patch.object(complete.scope, 'verify_authority', return_value={'synthetic': True}), \
                    patch.object(complete.runner, 'load_inactive', side_effect=AssertionError('native forbidden')):
                with self.assertRaisesRegex(ValueError, 'complete unique original16start'):
                    complete.main()

    def test_misfiled_start_and_malformed_objective_fail_before_native(self):
        with tempfile.TemporaryDirectory(dir=complete.runner.PRIMARY, prefix='synthetic-complete-') as root:
            root = Path(root); partition = root/'partition'; partition.mkdir()
            path = partition/'device-M2-start-03.json'
            path.write_text(json.dumps(result('M2', 'device', 2)))
            def attempt():
                with patch.object(sys, 'argv', ['complete', '--partition', str(partition),
                                               '--out', str(root/'out')]), \
                        patch.object(complete.scope, 'verify_authority', return_value={'synthetic': True}), \
                        patch.object(complete.runner, 'load_inactive', side_effect=AssertionError('native forbidden')):
                    complete.main()
            with self.assertRaisesRegex(ValueError, 'start identity'):
                attempt()
            malformed = result('M2', 'device', 3)
            del malformed['starts'][0]['minimax']
            path.write_text(json.dumps(malformed))
            with self.assertRaisesRegex(ValueError, 'malformed'):
                attempt()
            self.assertFalse((root/'out').exists())

    def test_changed_seed_is_not_an_original_start(self):
        with tempfile.TemporaryDirectory(dir=complete.runner.PRIMARY, prefix='synthetic-complete-') as root:
            root = Path(root); partition = root/'partition'; partition.mkdir()
            changed = result('M1', 'device', 0)
            changed['starts'][0]['initial'][0] += .1
            (partition/'device-M1-start-00.json').write_text(json.dumps(changed))
            with patch.object(sys, 'argv', ['complete', '--partition', str(partition),
                                           '--out', str(root/'out')]), \
                    patch.object(complete.scope, 'verify_authority', return_value={'synthetic': True}), \
                    patch.object(complete.runner, 'load_inactive',
                                      side_effect=AssertionError('native forbidden')):
                with self.assertRaisesRegex(ValueError, 'original seeded start'):
                    complete.main()
            self.assertFalse((root/'out').exists())

    def test_resolution_uses_absolute_pixel_differences_and_uncensored_channels(self):
        import numpy as np
        row = dict(pixels=4, part='straight', side='top', shell=0, bin=3)
        part = dict(member=0, bins=[row], offset=0, interior=[dict(shell=-1, pixels=4,
            outsideSubpixels=0, zeroStrokeWitness=True)])
        runs = np.full((7, 4, 3), 100.)
        runs[:, :, 1] = 255  # A rail is never an uncensored separator.
        observation = dict(cell='synthetic', role='validation', endpoint=1, scale=2,
            binids=np.zeros(4, dtype=int), runs=runs, parts=[part])
        left = np.full((4, 3), 100.)
        right = left.copy()
        right[:, 0] = [104, 96, 104, 96]  # Signed mean zero, mean absolute four.
        right[:, 1] = 200
        right[:, 2] = 102
        rows = list(complete.separation_rows(observation, {'M1-device': left,
                                                             'M2-curvature': right}))
        self.assertEqual([v['channel'] for v in rows], ['R', 'B'])
        self.assertEqual(rows[0]['meanAbsoluteDifferenceCodes'], 4)
        self.assertEqual(rows[0]['resolutionBoundCodes'], 3)
        self.assertTrue(rows[0]['resolvedInstance'])
        self.assertFalse(rows[1]['resolvedInstance'])

    def test_interior_witnesses_are_support_only_and_missing_pairs_are_labeled(self):
        part = dict(member=0, interior=[dict(shell=-2, pixels=5, outsideSubpixels=0,
            zeroStrokeWitness=True, nativeRunMeanRGB=[[120, 120, 120]] * 7)])
        witness = complete.interior_support_rows([dict(cell='synthetic', role='calibration',
            endpoint=1, scale=1, parts=[part])])
        self.assertTrue(witness[0]['zeroStrokeWitness'])
        self.assertEqual(witness[0]['qualification'], 'support only; not inside-body accuracy')
        self.assertNotIn('nativeRunMeanRGB', witness[0])
        available = complete.separation_availability({'M1-device', 'M2-curvature'},
                                                       'light-inactive', 'leastSquares')
        self.assertEqual(next(v for v in available if v['models'] == ['M1-css', 'M2-curvature'])
                         ['status'], 'UNAVAILABLE: certified geometry; unfitted')
        self.assertEqual(next(v for v in available if v['models'] == ['M1-device', 'M2-curvature'])
                         ['status'], 'AVAILABLE: local model-instance predictions only')
        diagnostic = complete.separation_availability({'M1-device', 'M2-curvature'},
            'light-inactive', 'minimax', {'M1-device': 'unconverged forward diagnostic; no survival claim'})
        self.assertEqual(next(v for v in diagnostic if v['models'] == ['M1-device', 'M2-curvature'])
                         ['status'], 'AVAILABLE: unconverged forward diagnostic; no survival claim')


if __name__ == '__main__':
    unittest.main()
