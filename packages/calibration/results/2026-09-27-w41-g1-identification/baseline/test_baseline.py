import json
from pathlib import Path
import tempfile
import unittest
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

    def test_x6_refusal_does_not_launch_backend(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'baseline'
            target.mkdir()
            record = baseline.load(baseline.HERE / 'preparation.json')
            (target / 'preparation.json').write_text(json.dumps(record))
            refused = {'verdict': {'passes': False}}
            with patch.object(baseline, 'HERE', target), \
                 patch.object(baseline, 'CAPTURES', target / 'captures'), \
                 patch.object(baseline.x6, 'observe', return_value=refused), \
                 patch.object(baseline.subprocess, 'run', wraps=baseline.subprocess.run) as run:
                with self.assertRaises(PermissionError): baseline.capture()
                self.assertFalse(any(call.args[0][0] == 'pnpm' for call in run.call_args_list))


if __name__ == '__main__': unittest.main()
