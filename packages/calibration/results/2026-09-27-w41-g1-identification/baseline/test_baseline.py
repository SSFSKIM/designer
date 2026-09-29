import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
import baseline


class BaselineTests(unittest.TestCase):
    def test_srgb_solid_and_pixel_centred_gradient(self):
        solid = baseline.raster({'kind': 'solid', 'srgb': [32, 192, 32]}, 1, (4, 2))
        np.testing.assert_array_equal(solid, np.tile([32, 192, 32], (2, 4, 1)))
        horizontal = baseline.raster({'kind': 'linear-gradient', 'from': [0, 0, 0],
                                     'to': [240, 120, 0], 'angle': 0}, 1, (4, 2))
        self.assertEqual(horizontal[0].tolist(), [[30, 15, 0], [90, 45, 0],
                                                 [150, 75, 0], [210, 105, 0]])
        vertical = baseline.raster({'kind': 'linear-gradient', 'from': [0, 0, 0],
                                   'to': [200, 100, 0], 'angle': 90}, 2, (4, 2))
        self.assertEqual(vertical[:, 3].tolist(), [[25, 13, 0], [75, 38, 0],
                                                  [125, 63, 0], [175, 88, 0]])

    def test_only_admitted_calval_not_holdout_or_missing_phase(self):
        cells, excluded = baseline.scope()
        self.assertEqual(len(cells), 536)
        self.assertEqual(len(excluded), 8)
        wave = baseline.runner.boundary.default_wave()
        self.assertEqual({wave.roles[c.split('/', 1)[1]] for c in cells},
                         {'calibration', 'validation'})
        self.assertTrue(all('phase' in cell for cell in excluded))

    def test_projection_reads_deep_whole_exterior_and_interior(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / 'image.png'
            Image.new('RGB', (320, 280), (100, 120, 140)).save(image)
            cells, _ = baseline.scope()
            cell = next(c for c in cells if '-1x-light-' in c and 'factor-' in c)
            data = baseline.project(cell, image)
            self.assertEqual(data['members'][0]['deep']['medianRGB'], [100, 120, 140])
            bins = data['members'][0]['bins']
            self.assertEqual({b['shell'] for b in bins if b['part'] != 'boundary'},
                             set(range(-14, 4)))
            for b in bins:
                if b['pixels']:
                    self.assertEqual(b['meanRGB'], [100, 120, 140])
            self.assertEqual(data['composite'], 'complete opaque web frame; active shadow included')

    def test_transparent_projection_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / 'image.png'
            Image.new('RGBA', (320, 280), (100, 120, 140, 0)).save(image)
            cells, _ = baseline.scope()
            cell = next(c for c in cells if '-1x-light-' in c and 'factor-' in c)
            with self.assertRaises(ValueError): baseline.project(cell, image)

    def test_transfer_keeps_complete_composite_errors_in_all_seven_repeats(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / 'image.png'
            Image.new('RGB', (320, 280), (110, 110, 110)).save(image)
            cells, _ = baseline.scope()
            cell = next(c for c in cells if '-1x-light-' in c and 'factor-' in c)
            component, scale = baseline.component(cell)
            payload = {'rgb': np.full((280, 320, 3), 100, dtype=np.uint8),
                       'component': component, 'scale': scale}
            result = baseline.transfer_projection(cell, image, [payload] * 7)
            self.assertEqual(result['deep'][0]['median']['errorCodes'], [10, 10, 10])
            for field in ['exterior', 'interiorTransfer']:
                rows = [b for b in result[field] if b['pixels'] >= 4]
                self.assertTrue(rows)
                for b in rows:
                    self.assertEqual(len(b['score']['runs']), 7)
                    self.assertEqual(b['score']['median']['errorCodes'], [10, 10, 10])
            with self.assertRaises(ValueError):
                baseline.transfer_projection(cell, image, [payload] * 6)

    def test_gradient_projection_uses_pinned_strip_at_each_scale(self):
        with tempfile.TemporaryDirectory() as tmp:
            for scale in (1, 2):
                cell = next(c for c in baseline.scope()[0]
                            if f'-{scale}x-light-' in c and c.endswith('/v90-c-c44__rest'))
                definition = baseline.wave.spec['backgrounds'][
                    baseline.wave.scenes[cell.split('/', 1)[1]]['background']]
                rgb = baseline.raster(definition, scale, (320, 280))
                path = Path(tmp) / f'{scale}.png'
                Image.fromarray(rgb).save(path)
                result = baseline.project(cell, path)['strip']
                self.assertEqual(result['web'], result['reference'])
                self.assertEqual(len(result['web']), 32 * scale)
                self.assertEqual(result['pixelsPerRow'], 48 * scale)
                self.assertNotIn('bar', result)

    def test_preparation_rechecks_live_public_scene_and_split_metadata(self):
        record = baseline.load(baseline.HERE / 'preparation.json')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scenes, split = root / 'scenes.json', root / 'split.json'
            scenes.write_bytes(b'public scenes')
            split.write_bytes(b'public split')
            scratch = {**record, 'scenesSha256': baseline.sha(scenes),
                       'splitSha256': baseline.sha(split)}
            with patch.object(baseline.wave, 'scenes_path', scenes), \
                 patch.object(baseline.wave, 'split_path', split):
                baseline.verify_preparation(scratch)
                for path in (scenes, split):
                    path.write_bytes(b'changed public metadata')
                    with self.assertRaisesRegex(ValueError, 'scene|split'):
                        baseline.verify_preparation(scratch)
                    path.write_bytes(b'public scenes' if path == scenes else b'public split')

    def test_authority_rejects_changed_public_manifest_geometry_and_g1_code(self):
        # Each changed file could redirect a later projection without moving any PNG digest.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            here = root / 'baseline'
            here.mkdir()
            x6dir = root / 'x6'
            x6dir.mkdir()
            w39 = root / 'w39'
            w39.mkdir()
            scenes = root / 'scenes.json'
            split = root / 'split.json'
            record = {'backdrops': 'baseline/generated-backdrops'}
            inputs = [here / 'preparation.json', here / 'generated-backdrops/manifest.json',
                      w39 / 'supplied-paths.json', scenes, split,
                      here / 'baseline.py', x6dir / 'observe.py']
            for path in inputs:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('original')
            with patch.object(baseline, 'ROOT', root), patch.object(baseline, 'HERE', here), \
                 patch.object(baseline, 'W39', w39), \
                 patch.object(baseline.wave, 'scenes_path', scenes), \
                 patch.object(baseline.wave, 'split_path', split), \
                 patch.object(baseline.runner, 'committed') as committed:
                self.assertEqual(baseline.authority_path(), here / 'authority-v2.json')
                baseline.seal_authority(record)
                sealed_hash = baseline.sha(baseline.authority_path())
                def committed_input(repo, name):
                    if name == 'baseline/authority-v2.json' and baseline.sha(repo / name) != sealed_hash:
                        raise ValueError('uncommitted frozen input')
                    return baseline.sha(repo / name)
                committed.side_effect = committed_input
                baseline.verify_authority(record)
                for path in inputs:
                    path.write_text('changed')
                    with self.assertRaisesRegex(ValueError, 'authority'):
                        baseline.verify_authority(record)
                    path.write_text('original')
                with (here / 'authority-v2.json').open('a') as stream: stream.write(' ')
                with self.assertRaisesRegex(ValueError, 'authority'):
                    baseline.verify_authority(record)
                (here / 'authority-v2.json').unlink()
                with self.assertRaisesRegex(ValueError, 'authority'):
                    baseline.verify_authority(record)

    def test_frozen_projections_are_verified_before_native_transfer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            here = root / 'baseline'
            here.mkdir()
            cell = 'profile/scene'
            projection = here / 'projections/profile/scene.json'
            projection.parent.mkdir(parents=True)
            projection.write_text('{"cell": "profile/scene"}')
            png = root / 'scene__webgpu.png'
            png.write_bytes(b'frame')
            descriptor = root / 'cell__webgpu.json'
            descriptor.write_text('{}')
            report = root / 'report__webgpu.json'
            report.write_text('{}')
            record = {'cells': [cell]}
            (here / 'preparation.json').write_text(json.dumps(record))
            capture = {'png': str(png), 'pngSha256': baseline.sha(png),
                       'cellSha256': baseline.sha(descriptor),
                       'reportSha256': baseline.sha(report),
                       'projection': str(projection.relative_to(root)),
                       'projectionSha256': baseline.sha(projection)}
            (here / 'authority-v2.json').write_text('{"schema": 1}')
            frozen = {'preparationSha256': baseline.sha(here / 'preparation.json'),
                      'authoritySha256': baseline.sha(here / 'authority-v2.json'),
                      'captures': {cell: capture}}
            (here / 'frozen-baseline.json').write_text(json.dumps(frozen))
            frozen_hash = baseline.sha(here / 'frozen-baseline.json')
            def committed_freeze(repo, name):
                if baseline.sha(repo / name) != frozen_hash:
                    raise ValueError('uncommitted freeze')
                return frozen_hash
            with patch.object(baseline, 'ROOT', root), patch.object(baseline, 'HERE', here), \
                 patch.object(baseline.runner, 'committed', side_effect=committed_freeze):
                baseline.verify_frozen(record, frozen)
                projection.write_text('{"cell": "different"}')
                with self.assertRaisesRegex(ValueError, 'projection'):
                    baseline.verify_frozen(record, frozen)
                with patch.object(baseline, 'verify_preparation'), \
                     patch.object(baseline, 'verify_authority'), \
                     patch.object(baseline, 'load_module', side_effect=AssertionError('archive accessed')):
                    with self.assertRaisesRegex(ValueError, 'projection'):
                        baseline.transfer()
                projection.write_text('{"cell": "profile/scene"}')
                (here / 'authority-v2.json').write_text('{"schema": 2}')
                with self.assertRaisesRegex(ValueError, 'authority'):
                    baseline.verify_frozen(record, frozen)
                (here / 'authority-v2.json').write_text('{"schema": 1}')
                with (here / 'frozen-baseline.json').open('a') as stream: stream.write(' ')
                with self.assertRaisesRegex(ValueError, 'frozen baseline'):
                    baseline.verify_frozen(record, frozen)

    def test_authority_rechecked_before_backend_after_backend_and_after_projection(self):
        original = baseline.load(baseline.HERE / 'preparation.json')
        profile, sid = original['cells'][0].split('/', 1)
        record = {**original, 'cells': [profile + '/' + sid],
                  'profiles': {profile: original['profiles'][profile]}}
        for change_point in ('prelaunch', 'backend', 'projection', 'none'):
            with self.subTest(change_point=change_point), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                here = root / 'baseline'
                here.mkdir()
                (root / 'x6').mkdir()
                (here / 'preparation.json').write_text(json.dumps(record))
                (here / 'authority-v2.json').write_text('{"schema": 1}')
                captures = root / 'captures'
                changed = [False]
                calls = [0]
                def verify(_record):
                    calls[0] += 1
                    if changed[0]: raise ValueError('authority changed')
                    if change_point == 'prelaunch' and calls[0] == 2:
                        changed[0] = True
                        raise ValueError('authority changed')
                def backend(_command, **_kwargs):
                    if change_point == 'backend':
                        changed[0] = True
                    else:
                        directory = captures / profile / sid
                        directory.mkdir(parents=True)
                        (directory / 'cell__webgpu.json').write_text(json.dumps({
                            'sceneId': sid, 'renderer': 'webgpu', 'engine': 'chromium',
                            'colorSpace': 'srgb', 'pixelSize': list(baseline.runner.dimension(
                                baseline.wave, profile + '/' + sid)),
                            'deterministic': True, 'repeatNoise': 0}))
                        (directory / 'report__webgpu.json').write_text(json.dumps({
                            'fallback': None, 'problems': [],
                            'materialProfile': {'sha256': record['documents'][
                                record['profiles'][profile]['material']][:12]},
                            'recededProfile': {'sha256': record['documents'][
                                record['profiles'][profile]['receded']][:12]}}))
                        (directory / (sid + '__webgpu.png')).write_bytes(b'synthetic web')
                def project(_identity, _png):
                    if change_point == 'projection': changed[0] = True
                    return {'cell': profile + '/' + sid}
                with patch.object(baseline, 'ROOT', root), \
                     patch.object(baseline, 'HERE', here), \
                     patch.object(baseline, 'CAPTURES', captures), \
                     patch.object(baseline, 'verify_preparation'), \
                     patch.object(baseline, 'verify_authority', side_effect=verify), \
                     patch.object(baseline.x6, 'observe', return_value={'verdict': {'passes': True}}), \
                     patch.object(baseline.subprocess, 'run', side_effect=backend), \
                     patch.object(baseline, 'project', side_effect=project):
                    if change_point == 'none':
                        baseline.capture()
                    else:
                        with self.assertRaisesRegex(ValueError, 'authority changed'):
                            baseline.capture()
                if change_point == 'none':
                    frozen = json.loads((here / 'frozen-baseline.json').read_text())
                    self.assertEqual(frozen['authoritySha256'],
                                     baseline.sha(here / 'authority-v2.json'))
                else:
                    self.assertFalse((here / 'frozen-baseline.json').exists())

    def test_x6_refusal_does_not_launch_backend(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'baseline'
            target.mkdir()
            (target.parent / 'x6').mkdir()
            record = baseline.load(baseline.HERE / 'preparation.json')
            (target / 'preparation.json').write_text(json.dumps(record))
            (target / 'authority-v2.json').write_text('{"schema": 1}')
            refused = {'verdict': {'passes': False}}
            with patch.object(baseline, 'HERE', target), \
                 patch.object(baseline, 'CAPTURES', target / 'captures'), \
                 patch.object(baseline.x6, 'observe', return_value=refused), \
                 patch.object(baseline, 'verify_authority'), \
                 patch.object(baseline.subprocess, 'run', wraps=baseline.subprocess.run) as run:
                with self.assertRaises(PermissionError): baseline.capture()
                self.assertFalse(any(call.args[0][0] == 'pnpm' for call in run.call_args_list))
                self.assertFalse((target / 'captures').exists())
                self.assertEqual(len(list((target.parent / 'x6').glob('prelaunch-*.json'))), 1)
                # A fresh prelaunch gate may proceed; a prior refusal must not reserve the capture root.
                original_run = run._mock_wraps
                def launch_probe(command, **kwargs):
                    if command[0] == 'pnpm': raise RuntimeError('backend invoked')
                    return original_run(command, **kwargs)
                with patch.object(baseline.x6, 'observe', return_value={'verdict': {'passes': True}}), \
                     patch.object(baseline.subprocess, 'run', side_effect=launch_probe):
                    with self.assertRaisesRegex(RuntimeError, 'backend invoked'):
                        baseline.capture()
                self.assertEqual(len(list((target.parent / 'x6').glob('prelaunch-*.json'))), 2)


if __name__ == '__main__': unittest.main()
