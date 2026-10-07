#!/usr/bin/env python3.12
"""Boundary tests for prospective membership and the no-native-launch default."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


class BedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('w49b_declare_test', HERE / 'declare.py')
        cls.D = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.D)
        cls.docs = cls.D.build()

    def test_fit_passes_cannot_expose_any_blind_cell(self):
        P = self.D.reuse.pass_spec()
        plan = self.docs['sitting-native.json']
        sources = self.D.source_docs(plan, self.docs)
        seen = set()
        for p in plan['passes']:
            if p['role'] != 'native-calibration':
                continue
            for run in range(1, p['runs'] + 1):
                doc = P.derive_from(plan, sources, p['name'], run)
                self.assertFalse(doc['split']['holdout'])
                seen.update(P.capture_ids(doc))
        blind = set(self.docs['scenes-native.json']['split']['holdout'])
        self.assertTrue(blind)
        self.assertTrue(seen.isdisjoint(blind))

    def test_every_scene_is_assigned_once_and_every_background_has_repeated_no_glass_control(self):
        doc = self.docs['scenes-native.json']
        roles = [sid for ids in doc['split'].values() for sid in ids]
        self.assertEqual(len(roles), len(set(roles)))
        self.assertEqual(set(roles), {s['id'] for s in doc['scenes']})
        for state in ('rest', 'inactive'):
            controls = {s['background'] for s in doc['scenes'] if s['state'] == state
                        and doc['components'][s['component']]['kind'] == 'none'}
            self.assertEqual(controls, set(doc['backgrounds']))

    def test_holdout_crosses_unseen_spans_pitches_and_photo_instead_of_duplicate_fit_cells(self):
        units = self.docs['manifest.json']['units']
        self.assertTrue(all(u['split'] == 'holdout' for u in units if u['span'] in (112, 144, 224)))
        for pitch in (12, 24, 48):
            rows = [u for u in units if u.get('pitch') == pitch]
            self.assertTrue(rows)
            self.assertTrue(all(u['split'] == 'holdout' for u in rows))
        self.assertTrue(any(u['family'] == 'blind-photo' and u['split'] == 'holdout' for u in units))
        self.assertTrue(any(u['span'] == 192 and u['split'] == 'calibration' for u in units))

    def test_matching_canvas_crop_preserves_impulse_and_checker_input_phase(self):
        small = self.docs['manifest.json']['bridge']['smallCanvas']
        large = self.docs['scenes-transfer.json']['canvas']
        dx = (large['width'] - small['width']) / 2
        dy = (large['height'] - small['height']) / 2
        self.assertEqual((dx, dy), (128, 128))
        self.assertEqual(dx % 64, 0)
        self.assertEqual(dy % 64, 0)

    def test_closing_bridges_run_after_a_cut_and_every_opening_cell_has_reference(self):
        P = self.D.reuse.pass_spec()
        plan = self.docs['sitting-native.json']
        sources = self.D.source_docs(plan, self.docs)
        P.validate_plan(plan, sources)
        tail = [p for p in plan['passes'] if p.get('runAfterCut')]
        self.assertEqual(plan['passes'][-len(tail):], tail)
        self.assertEqual({(p['scale'], p['pose']) for p in tail},
                         {(1, 'active'), (1, 'receded'), (2, 'active'), (2, 'receded')})
        for p in plan['passes']:
            if p['role'].startswith('bridge-') and p['kind'] == 'capture':
                self.assertEqual(set(p['bridge']['cells']),
                                 {f'{k}/{sid}' for k, ids in p['profiles'].items() for sid in ids})
        bad = copy.deepcopy(plan)
        next(p for p in bad['passes'] if p['name'].startswith('open-'))['bridge']['cells'].clear()
        with self.assertRaises(ValueError):
            P.validate_plan(bad, sources)

    def test_manifest_validator_rejects_wrong_backing_size_and_unassigned_scene(self):
        doc = copy.deepcopy(self.docs['scenes-native.json'])
        doc['split']['calibration'].pop()
        with self.assertRaises(ValueError):
            self.D.validate_scenes(doc)
        doc = copy.deepcopy(self.docs['scenes-native.json'])
        doc['components']['rrect-s224']['size'] = [900, 224]
        with self.assertRaises(ValueError):
            self.D.validate_scenes(doc)

    def test_default_capture_refuses_before_native_or_sitting_side_effects(self):
        with tempfile.TemporaryDirectory() as root:
            env = {'PATH': '/usr/bin:/bin:/opt/homebrew/bin', 'VITREA_SITTING_DIR': root}
            proc = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'sitting.py'),
                                   'capture', 'native-cal-2x-active'],
                                  env=env, capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('X5', proc.stderr)
            self.assertFalse(list(Path(root).iterdir()))

    def test_every_bridge_has_nonempty_region_statistics_on_its_real_reference(self):
        qualified = self.D.bridge_qualification(self.docs['sitting-native.json'])
        self.assertEqual(len(qualified), 20)
        self.assertTrue(all(row['statistics'] > 0 for row in qualified))

    def test_export_rejects_misfiled_blind_admission_and_never_selects_blind_passes(self):
        import release
        plan = self.docs['sitting-native.json']
        sources = self.D.source_docs(plan, self.docs)
        selected = release.calibration_passes(plan, sources)
        self.assertFalse(any(p['role'] in release.BLIND_ROLES for p in selected))
        p = next(p for p in selected if p['role'] == 'native-calibration')
        admission = dict(admitted=True, run=1, role='native-blind',
                         **{'pass': 'native-blind-2x-active'}, frames={})
        with self.assertRaises(ValueError):
            release.validate_run(admission, p, 1, plan, sources)
        bad = copy.deepcopy(plan)
        blind = next(p for p in bad['passes'] if p['role'] == 'native-blind')
        blind['role'] = 'native-calibration'
        with self.assertRaises(ValueError):
            release.calibration_passes(bad, sources)

    def test_impulse_is_centred_at_every_span_and_all_main_shapes_have_halo_clearance(self):
        doc = self.docs['scenes-native.json']
        S = self.D.reuse.driver()
        for span in self.D.SPANS:
            c = doc['components'][f'rrect-s{span}']
            x, y = S.frame_of(c, doc['canvas'])
            self.assertEqual((x + c['size'][0]/2, y + c['size'][1]/2), (256, 256))
            self.assertGreaterEqual(min(x, y, 576-x-c['size'][0], 456-y-c['size'][1]), 60)

    def test_dry_plan_uses_declared_dimensions_and_never_executes(self):
        P = self.D.reuse.pass_spec()
        plan = self.docs['sitting-native.json']
        sources = self.D.source_docs(plan, self.docs)
        S = self.D.reuse.driver()
        dry = S.dry_plan(plan, sources)
        self.assertIs(dry['executed'], False)
        for p in plan['passes']:
            if p['role'] == 'native-calibration':
                doc = P.derive_from(plan, sources, p['name'])
                self.assertEqual(doc['canvas'], {'width': 576, 'height': 456})
                self.assertEqual(len(P.cells(doc)), len(p['profiles'][next(iter(p['profiles']))]))
        self.assertEqual(dry['totals']['captures'], P.plan_counts(plan, sources)['totals']['captures'])


if __name__ == '__main__':
    unittest.main()
