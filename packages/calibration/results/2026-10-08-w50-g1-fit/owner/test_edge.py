import importlib.util
from pathlib import Path
import unittest
import numpy as np
P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('owner_edge', P / 'edge.py')
edge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edge)

class EdgeTests(unittest.TestCase):
    def test_reported_error_growth_is_not_an_absolute_gate(self):
        native = np.full((80, 120, 3), 30, dtype=float)
        current = native + 2
        candidate = native + 5
        result = edge.measure(native, current, candidate,
            {'kind': 'rrect', 'size': [80, 44], 'radius': 8}, 1, ('synthetic-profile', 'synthetic-scene'))
        self.assertEqual(result['state'], 'MEASURED')
        self.assertEqual(result['verdict'], 'reported')
        self.assertEqual(result['current'], 2)
        self.assertEqual(result['candidate'], 5)
        self.assertEqual(result['growth'], 3)
        self.assertGreater(result['bins'], 0)
    def test_named_bins_carry_supplied_cell_identity(self):
        native = np.full((80, 120, 3), 30, dtype=float)
        identity = ('apple-macos-27.0-1x-dark-standard-glass0.25', 'synthetic__rrect-sm__rest')
        result = edge.measure(native, native + 2, native + 20,
            {'kind': 'rrect', 'size': [80, 44], 'radius': 8}, 1, identity)
        self.assertTrue(result['namedMissBins'])
        for entry in result['namedMissBins']:
            self.assertEqual(entry['cell'], '/'.join(identity))
    def test_changed_source_or_missing_dependency_refuses(self):
        import hashlib
        text = 'def a():\n return missing()\n'
        with self.assertRaisesRegex(ValueError, 'dependency'):
            edge.bind(text, hashlib.sha256(text.encode()).hexdigest(), ['a'], {})
        with self.assertRaisesRegex(ValueError, 'hash'):
            edge.bind(text, '0'*64, ['a'], {})

if __name__ == '__main__': unittest.main()
