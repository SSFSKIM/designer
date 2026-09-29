"""The narrowed transfer cannot read native evidence before all selections freeze."""
import json
import hashlib
import numpy as np
from pathlib import Path
from types import SimpleNamespace
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

    def test_m1_requires_all_original32_before_validation_or_any_native_read(self):
        with tempfile.TemporaryDirectory(dir=complete.runner.PRIMARY, prefix='synthetic-complete-') as root:
            root = Path(root); partition = root/'partition'; partition.mkdir(); output = root/'output'
            for geometry in ('device', 'curvature'):
                for index in range(16):
                    if geometry == 'curvature' and index == 15:
                        continue
                    (partition/f'{geometry}-M1-start-{index:02d}.json').write_text(
                        json.dumps(result('M1', geometry, index)))
            with patch.object(sys, 'argv', ['complete', '--family', 'M1', '--partition',
                                           str(partition), '--out', str(output)]), \
                    patch.object(complete.scope, 'verify_authority', return_value={'synthetic': True}), \
                    patch.object(complete.r, 'Preparation', side_effect=AssertionError('native forbidden')), \
                    patch.object(complete.runner, 'load_inactive', side_effect=AssertionError('native forbidden')):
                with self.assertRaisesRegex(ValueError, 'complete unique original16start'):
                    complete.main()
            self.assertFalse(output.exists())

    def test_m1_freezes_only_its32_selections_before_native(self):
        with tempfile.TemporaryDirectory(dir=complete.runner.PRIMARY, prefix='synthetic-complete-') as root:
            root = Path(root); partition = root/'partition'; partition.mkdir(); output = root/'output'
            for geometry in ('device', 'curvature'):
                for index in range(16):
                    (partition/f'{geometry}-M1-start-{index:02d}.json').write_text(
                        json.dumps(result('M1', geometry, index)))
            # M2 need not finish, and even a completed M2 result is outside this freeze.
            (partition/'device-M2-start-00.json').write_text(json.dumps(result('M2', 'device', 0)))
            def before_native(*args):
                pinned = json.loads((output/'frozen-optimizer-inputs.json').read_text())
                self.assertEqual(len(pinned), 32)
                self.assertTrue(all('M1' in Path(path).name for path in pinned))
                self.assertEqual(len(list(output.glob('*-optimizer.json'))), 2)
                selected = json.loads((output/'frozen-selected-predictions.json').read_text())
                self.assertEqual(set(selected), {'device-M1', 'curvature-M1'})
                self.assertEqual(selected['device-M1']['leastSquares']['startIndex'], 0)
                self.assertEqual(json.loads((output/'selected-family-scope.json').read_text())
                    ['interpretedEndpoints'], ['light-inactive'])
                self.assertFalse((output/'device-M2-optimizer.json').exists())
                raise RuntimeError('synthetic stops before native')
            with patch.object(sys, 'argv', ['complete', '--family', 'M1', '--partition',
                                           str(partition), '--out', str(output)]), \
                    patch.object(complete.scope, 'verify_authority', return_value={'synthetic': True}), \
                    patch.object(complete.r, 'Preparation', return_value=object()), \
                    patch.object(complete, 'load_light_inactive', side_effect=before_native):
                with self.assertRaisesRegex(RuntimeError, 'synthetic stops before native'):
                    complete.main()

    def test_all_unconverged_m1_freezes_same_forward_fallback_and_original_identity(self):
        with tempfile.TemporaryDirectory(dir=complete.runner.PRIMARY, prefix='synthetic-complete-') as root:
            root = Path(root); partition = root/'partition'; partition.mkdir(); output = root/'output'
            for geometry in ('device', 'curvature'):
                for index in range(16):
                    item = result('M1', geometry, index)
                    for objective in ('leastSquares', 'minimax'):
                        row = item['starts'][0][objective]
                        row['converged'] = False
                        row['weightedSquaredError'] = float((index-7)**2+1)
                        row['maximumCodes'] = float(16-index)
                        row['coefficients'][7] = 40 + index/1000
                    (partition/f'{geometry}-M1-start-{index:02d}.json').write_text(json.dumps(item))
            def before_native(*args):
                frozen = json.loads((output/'frozen-selected-predictions.json').read_text())
                for name in ('device-M1', 'curvature-M1'):
                    for objective, index in (('leastSquares', 7), ('minimax', 15)):
                        prediction = frozen[name][objective]
                        optimizer = json.loads((output/(name+'-optimizer.json')).read_text())
                        selected, status = complete.execute.select_prediction(optimizer, objective)
                        self.assertEqual(prediction['startIndex'], index)
                        self.assertEqual(prediction['coefficients'], selected['coefficients'])
                        self.assertEqual(prediction['coefficients'][7], 40 + index/1000)
                        self.assertEqual(prediction['status'], status)
                        self.assertIn('unconverged', prediction['status'])
                self.assertEqual(len(json.loads((output/'frozen-optimizer-inputs.json').read_text())), 32)
                raise RuntimeError('controlled native boundary')
            with patch.object(sys, 'argv', ['complete', '--family', 'M1', '--partition',
                                           str(partition), '--out', str(output)]), \
                    patch.object(complete.scope, 'verify_authority', return_value={'synthetic': True}), \
                    patch.object(complete.r, 'Preparation', return_value=object()), \
                    patch.object(complete, 'load_light_inactive', side_effect=before_native):
                with self.assertRaisesRegex(RuntimeError, 'controlled native boundary'):
                    complete.main()

    def test_light_inactive_reader_filters_public_metadata_before_payload_read(self):
        cells = {'light-inactive': 'apple-macos-27.0-1x-light-standard-glass0.5/li__inactive',
                 'dark-inactive': 'apple-macos-27.0-1x-dark-standard-glass0.5/di__inactive',
                 'light-active': 'apple-macos-27.0-1x-light-standard-glass0.5/la__rest'}
        profiles = [dict(key='apple-macos-27.0-1x-'+scheme+'-standard-glass0.5',
                         colorScheme=scheme) for scheme in ('light', 'dark')]
        scenes = {cell.split('/')[1]: dict(state='inactive' if 'inactive' in name else 'rest',
                                          background='g128') for name, cell in cells.items()}
        wave = SimpleNamespace(spec={'profiles': profiles}, scenes=scenes,
                               component=lambda sid: sid)
        read = []
        reader = SimpleNamespace(allowed=set(scenes), entries={(cell, 'crop'): {'admitted': True}
            for cell in cells.values()}, read=lambda cell, kind: read.append(cell) or b'synthetic')
        archive = SimpleNamespace(unbundle=lambda raw: ([dict(admitted=True, protocol='normal',
            state='s')]*7, {'s': b'synthetic'}), unpack=lambda raw: dict(scheme='light', pose='inactive'))
        native = SimpleNamespace(wave=SimpleNamespace(native_only=lambda component: False),
                                 archive=archive)
        preparation = SimpleNamespace(prepare=lambda cell, role, payloads, states, background:
            dict(cell=cell, endpoint=1, role=role, stateMembership=states))
        with patch.object(complete.r, 'guarded_reader', return_value=(native, wave, reader)):
            observations = complete.load_light_inactive(preparation, 'validation')
        self.assertEqual(read, [cells['light-inactive']])
        self.assertEqual([v['cell'] for v in observations], read)

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
        unfrozen = complete.separation_availability({'M1-device'}, 'light-inactive',
                                                     'leastSquares', unfrozen=('M2',))
        self.assertIn('M2 UNAVAILABLE/unfrozen', next(v for v in unfrozen
            if v['models'] == ['M1-device', 'M2-curvature'])['status'])


if __name__ == '__main__':
    unittest.main()
