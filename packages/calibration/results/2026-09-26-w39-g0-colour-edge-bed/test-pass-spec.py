#!/usr/bin/env python3
"""Pass membership guards against dropped controls, extra references and wrong-scale phases."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pass_spec', HERE / 'pass-spec.py')
passes = importlib.util.module_from_spec(spec); spec.loader.exec_module(passes)


class PassSpecTests(unittest.TestCase):
    def test_capture_counts_and_reference_schedule(self):
        plan = passes.plan()
        self.assertEqual(plan['counts'], dict(normal=5768, run1ColourReferences=504,
            sentinels=48, preflight=40, baseTotal=6360, conditionalBothAxes=784,
            conditionalOneAxis=448, totalBothAxes=7144))
        for p in plan['passes']:
            self.assertEqual([r['count'] for r in p['runs']], [332, 206, 206, 206, 206, 206, 206])
            self.assertEqual([r['conditionalCount'] for r in p['runs']], [28] * 7)
            self.assertEqual(len(p['sentinel']['cells']), 4)
            for r in p['runs']:
                self.assertEqual(len(r['cells']), len(set(r['cells'])))

    def test_each_axis_branch_keeps_only_its_device_scale(self):
        for scale in (1, 2):
            for axes, count in [((), 0), (('x',), 8), (('y',), 8), (('x', 'y'), 14)]:
                doc = passes.derive('active', scale, run=2, reachable_axes=axes)
                phase = [s for s in doc['scenes'] if s['$class'] == 'phase']
                self.assertEqual(len(phase), count)
                self.assertTrue(all(s['$scale'] == scale for s in phase))
                self.assertTrue(all(s['$phaseAxis'] in (*axes, 'zero') for s in phase))
                self.assertTrue(all(s['state'] == 'rest' for s in doc['scenes']))

    def test_preflight_end_pairs_follow_full_geometry_run(self):
        for p in passes.plan()['preflight']:
            self.assertEqual(len(p['cells']), 18)
            self.assertEqual(len(p['endRepeatCells']), 2)
            self.assertTrue(all('-zero' in c for c in p['endRepeatCells']))
            self.assertTrue(all('-light-' in c for c in p['cells']))
            self.assertEqual(p['count'], 20)

    def test_refuses_undeclared_axes_and_passes(self):
        for args in [('active', 3, 1, ()), ('rest', 1, 1, ()), ('active', 1, 8, ()), ('active', 1, 1, ('z',))]:
            with self.assertRaises(ValueError):
                passes.derive(*args)


if __name__ == '__main__':
    unittest.main(verbosity=2)
