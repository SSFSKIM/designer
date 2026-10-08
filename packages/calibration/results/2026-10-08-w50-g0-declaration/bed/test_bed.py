"""W50 bed contracts; run with python -I -B test_bed.py. No native process is launched."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class BedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = load('w50_build_test', HERE / 'build.py')

    def test_actual_plan_stores_1600_frames_in_40_launches(self):
        scenes, manifest, plan = self.b.build()
        p = self.b.pass_spec()
        counts = p.plan_counts(plan, {'w50': scenes, 'canonical': self.b.canonical()})
        self.assertEqual(counts['totals']['captures'], 1600)
        self.assertEqual(counts['totals']['captureLaunches'], 40)
        self.assertEqual(len(manifest['cells']), 448)
        self.assertEqual(len(manifest['references']), 128)
        main = [q for q in counts['passes'] if q['role'] == 'low-end']
        self.assertEqual([q['cellsPerRun'] for q in main], [[76, 60, 60]] * 8)

    def test_blind_dependencies_never_enter_exposed_roles(self):
        _, m, _ = self.b.build()
        cells = {c['id']: c for c in m['cells']}
        for c in cells.values():
            if c['span'] == 224 or c['background'] == 'checker-low' or c.get('level') in (7, 20):
                self.assertEqual(c['role'], 'blind')
        for ref in m['references']:
            roles = {c['role'] for c in cells.values() if c['reference'] == ref['id']}
            self.assertEqual(set(ref['roles']), roles)
            if ref['background'] in ('grey-007', 'grey-020', 'checker-low'):
                self.assertEqual(ref['roles'], ['blind'])

    def test_sentinels_bracket_actual_harness_sorted_order(self):
        scenes, _, plan = self.b.build()
        p = self.b.pass_spec()
        for q in plan['passes']:
            if q['role'] != 'low-end':
                continue
            for run in (1, 2, 3):
                doc = p.derive_from(plan, {'w50': scenes}, q['name'], run)
                ids = p.capture_ids(doc)
                self.assertTrue(all(i.startswith('00-open-') for i in ids[:2]))
                self.assertTrue(all(i.startswith('zz-close-') for i in ids[-2:]))

    def test_bridges_bind_committed_original_canvas_frames(self):
        scenes, _, plan = self.b.build()
        for p in plan['passes']:
            if p['source'] != 'canonical':
                continue
            self.assertEqual(self.b.canonical()['canvas'], {'width': 320, 'height': 200})
            self.assertEqual(len(p['bridge']['cells']), 2)
            for row in p['bridge']['cells'].values():
                raw = self.b.committed(row['reference']['path'])
                self.assertEqual(self.b.sha(raw), row['reference']['sha256'])
        self.assertTrue(all(p['runAfterCut'] for p in plan['passes'][-8:]))

    def test_geometry_fits_canvas_with_nonempty_deep_and_center_support(self):
        scenes, m, _ = self.b.build()
        self.assertEqual(scenes['canvas'], {'width': 512, 'height': 384})
        self.assertEqual(scenes['components']['span-224']['size'], [392, 224])
        for c in scenes['components'].values():
            if c['kind'] == 'none':
                continue
            w, h = c['size']
            self.assertGreaterEqual((512-w)/2, 60)
            self.assertGreaterEqual((384-h)/2, 60)
            self.assertGreater(min(w, h) - 16, 8)

if __name__ == '__main__':
    unittest.main()
