"""Small refusal and numerical checks for the offline knowledge-evidence script."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('w52_attribute', HERE / 'attribute.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AttributionChecks(unittest.TestCase):
    def test_hash_authentication_refuses_changed_input_before_decode(self):
        with tempfile.TemporaryDirectory(dir=HERE) as name:
            path = Path(name) / 'payload.json'
            path.write_bytes(b'{"value":1}')
            pin = {'path': str(path), 'sha256': MODULE.sha(path.read_bytes())}
            self.assertEqual(MODULE.load(pin, 'test'), {'value': 1})
            path.write_bytes(b'{"value":2}')
            with self.assertRaisesRegex(ValueError, 'input changed'):
                MODULE.load(pin, 'test')

    def test_population_refuses_duplicate_or_missing_key(self):
        rows = [{'renderer': 'webgpu',
                 'profile': f'apple-macos-27.0-{scale}x-dark-standard-glass{position}',
                 'scene': f'impulse__{shape}__rest', 'readings': {MODULE.STAT: {}}}
                for scale in (1, 2) for position in (.25, .5) for shape in MODULE.SHAPES]
        self.assertEqual(len(MODULE.selected_rows({'cells': rows})), 16)
        with self.assertRaises(AssertionError):
            MODULE.selected_rows({'cells': rows[:-1]})
        with self.assertRaises(AssertionError):
            MODULE.selected_rows({'cells': rows + [rows[0]]})

    def test_constant_linear_delta_preserves_unquantized_full_coverage_variance(self):
        values = np.array([.02, .05, .07, .11, .4])
        self.assertAlmostEqual(float(np.std(values)), float(np.std(values - .015)), places=15)
        spatial_gain = np.array([.4, .6, 1, 1, 1])
        self.assertGreater(abs(float(np.std(values)) -
                               float(np.std(values - .015 * spatial_gain))), 1e-4)

    def test_quantization_can_move_stddev_despite_constant_linear_delta(self):
        encoded = np.array([33, 34, 35, 90], dtype=float) / 255
        linear = MODULE.decode(encoded)
        predicted = np.round(MODULE.encode(linear - .002) * 255) / 255
        self.assertGreater(abs(float(np.std(MODULE.decode(predicted))) - float(np.std(linear))),
                           1e-5)

    def test_small_native_channel_difference_does_not_reach_chroma_threshold(self):
        image = np.array([[[41, 42, 41], [69, 68, 69]]], dtype=float) / 255
        background = np.zeros_like(image)
        delta = np.linalg.norm(MODULE.chroma(image) - MODULE.chroma(background), axis=-1)
        self.assertTrue(np.all(delta < .03))
        self.assertTrue(np.all(delta > 0))


if __name__ == '__main__':
    unittest.main()
