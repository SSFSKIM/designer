#!/usr/bin/env python3
"""The W39 wave boundary, dependency rules and launcher, on synthetic probe cells (§5.184).

Derived from W34 G0's `test-wave.py`; the receipt tests carry over, the
dependency, placement, preflight and canonical-path tests are new.
"""
import copy
import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def load():
    spec = importlib.util.spec_from_file_location('w39_wave_under_test', HERE / 'wave.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


GLASS = {'kind': 'capsule-circular', 'size': [120, 44], 'position': [160, 140]}
SCENES = {
    'canvas': {'width': 320, 'height': 280},
    'backgrounds': {'g': {'kind': 'solid', 'srgb': [128] * 3}, 'c': {'kind': 'solid', 'srgb': [90, 70, 100]},
                    'h': {'kind': 'solid', 'srgb': [70, 90, 100]}},
    'components': {'glass': GLASS, 'opaque': {**GLASS, 'opaque': True, 'fillSRGB': [0, 0, 0]},
                   'top': {**GLASS, 'position': [160, 70]}, 'top-opaque': {**GLASS, 'position': [160, 70], 'opaque': True},
                   'column': {'kind': 'column', 'items': [{**GLASS, 'position': [160, 70]}, {**GLASS, 'position': [160, 210]}]},
                   'phase': {'kind': 'rrect', 'radius': 22, 'size': [120.25, 44], 'position': [160.125, 140]},
                   'empty': {'kind': 'none'}},
    'scenes': [
        {'id': 'cal', 'background': 'g', 'component': 'glass', 'state': 'rest'},
        {'id': 'cal-opaque', 'background': 'g', 'component': 'opaque', 'state': 'rest'},
        {'id': 'g-ref', 'background': 'g', 'component': 'empty', 'state': 'rest'},
        {'id': 'top', 'background': 'g', 'component': 'top', 'state': 'rest'},
        {'id': 'top-opaque', 'background': 'g', 'component': 'top-opaque', 'state': 'rest'},
        {'id': 'column', 'background': 'g', 'component': 'column', 'state': 'rest'},
        {'id': 'phase', 'background': 'g', 'component': 'phase', 'state': 'rest'},
        {'id': 'val', 'background': 'c', 'component': 'glass', 'state': 'rest'},
        {'id': 'c-ref', 'background': 'c', 'component': 'empty', 'state': 'rest'},
        {'id': 'held', 'background': 'h', 'component': 'glass', 'state': 'rest'},
        {'id': 'h-ref', 'background': 'h', 'component': 'empty', 'state': 'rest'}],
    'profiles': [{'key': 'profile', 'scenes': 'all'}],
}
IDS = [s['id'] for s in SCENES['scenes']]
SCENES['split'] = {'probe': IDS, 'calibration': [], 'validation': [], 'holdout': [], 'recorded': []}
SPLIT = {'schema': 'w39-split-1',
         'calibration': ['cal', 'cal-opaque', 'g-ref', 'top', 'top-opaque', 'column', 'phase'],
         'validation': ['val', 'c-ref'], 'holdout': ['held', 'h-ref'],
         'dependencies': {
             'cal': {'noGlass': 'g-ref', 'opaque': 'cal-opaque'},
             'top': {'noGlass': 'g-ref', 'opaque': 'top-opaque'},
             'column': {'noGlass': 'g-ref', 'opaque': 'cal-opaque'},
             'phase': {'noGlass': 'g-ref', 'opaque': 'cal-opaque'},
             # Colour cells borrow the grey centre opaque as path registration.
             'val': {'noGlass': 'c-ref', 'opaque': 'cal-opaque'},
             'held': {'noGlass': 'h-ref', 'opaque': 'cal-opaque'}}}


class WaveBoundary(unittest.TestCase):
    def setUp(self):
        self.mod = load()
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.scenes, self.split = copy.deepcopy(SCENES), copy.deepcopy(SPLIT)
        self.put('scenes.json', self.scenes); self.put('split.json', self.split)
        self.put('preflight.json', {'scenes': [{'id': 'preflight-x1'}]})
        self.pins = {'scenesSha256': sha(self.root / 'scenes.json'), 'splitSha256': sha(self.root / 'split.json'),
                     'preflightScenesSha256': sha(self.root / 'preflight.json')}
        self.put('pins.json', self.pins)
        entries = []
        for cell, role in [('cal', 'calibration'), ('val', 'validation'), ('held', 'holdout')]:
            for kind in ['crop', 'statistics']:
                path = f'{role}/{cell}.{kind}'
                self.put(path, {'secret': cell})
                entries.append({'cell': 'profile/' + cell, 'kind': kind, 'path': path,
                                'sha256': sha(self.root / path)})
        self.put('inventory.json', {'entries': entries, 'scenesSha256': self.pins['scenesSha256'],
                                    'splitSha256': self.pins['splitSha256']})

    def put(self, name, value):
        p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value)); return p

    def wave(self, preflight=True):
        return self.mod.Wave(self.root / 'scenes.json', self.root / 'split.json', self.root / 'pins.json',
                             self.root / 'preflight.json' if preflight else None)

    def respin(self, split=None, scenes=None):
        if split is not None: self.put('split.json', split)
        if scenes is not None: self.put('scenes.json', scenes)
        self.put('pins.json', {**self.pins, 'scenesSha256': sha(self.root / 'scenes.json'),
                               'splitSha256': sha(self.root / 'split.json')})

    def test_probe_role_never_bypasses_identification_holdout(self):
        wave = self.wave(); reader = wave.reader(self.root)
        self.assertEqual(json.loads(reader.read('profile/cal', 'statistics')), {'secret': 'cal'})
        for kind in ['crop', 'statistics']:
            # Missing files prove refusal precedes payload access.
            (self.root / f'holdout/held.{kind}').unlink()
            with self.assertRaisesRegex(PermissionError, 'holdout'): reader.read('profile/held', kind)
        with self.assertRaisesRegex(PermissionError, 'holdout'): wave.select(['holdout'])
        with self.assertRaisesRegex(PermissionError, 'holdout'): wave.launch_plan(['calibration', 'holdout'])
        with self.assertRaisesRegex(ValueError, 'unknown'): wave.select(['probe'])

    def test_launcher_defaults_to_calibration_and_validation_and_names_every_exclusion(self):
        included, excluded = self.wave().launch_plan()
        self.assertEqual(included, ['cal', 'val'])
        self.assertNotIn('held', included + list(excluded))
        self.assertEqual(set(excluded), {'cal-opaque', 'g-ref', 'c-ref', 'top', 'top-opaque', 'column', 'phase'})
        self.assertRegex(excluded['top'], r'^position \(160, 70\)')
        self.assertRegex(excluded['column'], '^column')
        self.assertRegex(excluded['phase'], '^fractional size')
        self.assertRegex(excluded['g-ref'], '^native-only')
        self.assertEqual(self.wave().launch_scenes(), included)

    def test_web_placement_mirrors_component_region(self):
        refusal = self.mod.web_placement_refusal
        canvas = {'width': 320, 'height': 280}
        self.assertIsNone(refusal({'kind': 'capsule-circular', 'size': [120, 44]}, canvas))
        self.assertIsNone(refusal({'kind': 'rrect', 'radius': 22, 'size': [120, 64], 'position': [160, 140]}, canvas))
        # Math.round((280 - 45) / 2) = 118 (half up); the centre lands at 140.5.
        self.assertIsNone(refusal({'kind': 'rrect', 'radius': 22, 'size': [121, 45], 'position': [160.5, 140.5]}, canvas))
        self.assertIsNotNone(refusal({'kind': 'rrect', 'radius': 22, 'size': [121, 45], 'position': [160, 140]}, canvas))
        self.assertIsNotNone(refusal({'kind': 'capsule', 'size': [120, 44], 'offset': [0, 0]}, canvas))

    def test_dependencies_fail_closed(self):
        cases = [
            ('dependencies must name exactly', lambda s: s['dependencies'].pop('cal')),
            ('dependencies must name exactly', lambda s: s['dependencies'].__setitem__(
                'g-ref', {'noGlass': 'g-ref', 'opaque': 'cal-opaque'})),
            ('noGlass, opaque', lambda s: s['dependencies']['cal'].pop('opaque')),
            ('unknown scene', lambda s: s['dependencies']['cal'].__setitem__('noGlass', 'phantom')),
            ('must be a none scene', lambda s: s['dependencies']['cal'].__setitem__('noGlass', 'cal-opaque')),
            ('opaque control', lambda s: s['dependencies']['cal'].__setitem__('opaque', 'g-ref')),
            ('share the glass cell background', lambda s: s['dependencies']['val'].__setitem__('noGlass', 'g-ref')),
            ('must declare dependencies', lambda s: s.pop('dependencies')),
            ('schema', lambda s: s.__setitem__('schema', 'w34')),
        ]
        for message, mutate in cases:
            split = copy.deepcopy(SPLIT); mutate(split); self.respin(split)
            with self.subTest(message), self.assertRaisesRegex(ValueError, message): self.wave()

    def test_role_rank_pair_and_borrow_rules(self):
        # A calibration cell may never carry a holdout pixel.
        split = copy.deepcopy(SPLIT)
        split['calibration'].remove('g-ref'); split['holdout'].append('g-ref'); self.respin(split)
        with self.assertRaisesRegex(PermissionError, 'ranks above'): self.wave()
        # A true pair (same background, same geometry) shares one role.
        split = copy.deepcopy(SPLIT)
        split['calibration'].remove('top-opaque'); split['validation'].append('top-opaque'); self.respin(split)
        with self.assertRaisesRegex(PermissionError, 'ranks above'): self.wave()
        split = copy.deepcopy(SPLIT)
        split['calibration'].remove('top'); split['validation'].append('top'); self.respin(split)
        with self.assertRaisesRegex(ValueError, 'pair must share one role'): self.wave()
        # A borrowed control is calibration only.
        scenes = copy.deepcopy(SCENES)
        scenes['scenes'].append({'id': 'val-opaque', 'background': 'g', 'component': 'opaque', 'state': 'rest'})
        scenes['split']['probe'].append('val-opaque')
        split = copy.deepcopy(SPLIT); split['validation'].append('val-opaque')
        split['dependencies']['val']['opaque'] = 'val-opaque'
        self.respin(split, scenes)
        with self.assertRaisesRegex(ValueError, 'borrowed opaque control must be calibration'): self.wave()

    def test_dependency_pose_and_profile_coverage(self):
        scenes = copy.deepcopy(SCENES); scenes['scenes'][1]['state'] = 'inactive'; self.respin(scenes=scenes)
        with self.assertRaisesRegex(ValueError, 'pose'): self.wave()
        scenes = copy.deepcopy(SCENES)
        scenes['profiles'] = [{'key': 'profile', 'scenes': 'all'},
                              {'key': 'other', 'scenes': ['cal', 'g-ref']}]
        self.respin(copy.deepcopy(SPLIT), scenes)
        with self.assertRaisesRegex(ValueError, 'absent from a profile'): self.wave()

    def test_membership_hashes_and_preflight_fail_closed(self):
        for replacement in [
                {**SPLIT, 'calibration': SPLIT['calibration'] + ['held']},
                {**SPLIT, 'validation': ['val']},
                {**SPLIT, 'validation': SPLIT['validation'] + ['phantom']}]:
            self.respin(replacement)
            with self.assertRaisesRegex(ValueError, 'membership'): self.wave()
        self.respin(copy.deepcopy(SPLIT))
        with (self.root / 'scenes.json').open('a') as f: f.write(' ')
        with self.assertRaisesRegex(ValueError, 'scenes hash'): self.wave()
        self.respin(scenes=copy.deepcopy(SCENES))
        with (self.root / 'preflight.json').open('a') as f: f.write(' ')
        with self.assertRaisesRegex(ValueError, 'preflight scenes hash'): self.wave()
        self.put('preflight.json', {'scenes': [{'id': 'cal'}]})
        self.put('pins.json', {**json.loads((self.root / 'pins.json').read_text()),
                               'preflightScenesSha256': sha(self.root / 'preflight.json')})
        with self.assertRaisesRegex(ValueError, 'never identification material'): self.wave()

    def test_canonical_outputs_refused(self):
        root = self.mod.ROOT
        for path in [root / 'apps/reference-apple/fixtures', root / 'apps/reference-apple/fixtures/x',
                     root / 'packages/calibration/results/matrix.json', root / 'packages/calibration/web-captures/a',
                     root / 'packages/calibration/results/superseded/x.json', root / 'packages/calibration', root]:
            with self.subTest(str(path)), self.assertRaisesRegex(ValueError, 'canonical'):
                self.mod.refuse_canonical(self.root / 'ok', path)
        self.mod.refuse_canonical(self.root / 'fixtures', self.root / 'matrix.json',
                                  root / 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/m.json')
        command, env = self.mod.compare_command(self.wave(), ['cal'], self.root / 'f', self.root / 'm.json',
                                                self.root / 'c')
        self.assertEqual(command[command.index('--set') + 1], 'probe')
        self.assertEqual(command[command.index('--scene') + 1], 'cal')
        self.assertIn('--fail-if-no-match', command)
        self.assertEqual(env['VITREA_SCENES'], str((self.root / 'scenes.json').resolve()))

    def test_reporting_exposes_only_inventory_not_payload(self):
        reader = self.wave().reader(self.root)
        for kind in ['crop', 'statistics']: (self.root / f'holdout/held.{kind}').write_text('INVALID JSON SECRET')
        report = reader.report_inventory()
        self.assertNotIn('SECRET', json.dumps(report))
        self.assertEqual(len(report), 6)
        bad = json.loads((self.root / 'inventory.json').read_text())
        bad['entries'][0]['path'] = 'holdout/held.crop'; self.put('inventory.json', bad)
        with self.assertRaisesRegex(ValueError, 'placement'): self.wave().reader(self.root)
        bad['scenesSha256'] = 'wrong generation'; self.put('inventory.json', bad)
        with self.assertRaisesRegex(ValueError, 'generation'): self.wave().reader(self.root)

    def test_receipt_refuses_another_inventory_and_spends_the_wave(self):
        wave = self.wave()
        other = json.loads((self.root / 'inventory.json').read_text()); other['note'] = 'another generation'
        self.put('other/inventory.json', other)
        config = {'scenes': wave.scenes_sha, 'split': wave.split_sha,
                  'generation': [sha(self.root / 'inventory.json')],
                  'instrument': 'i', 'closure': 'c', 'candidate': 'candidate'}
        log = self.root / 'receipt.jsonl'
        with self.mod.Receipt(log, config).expose() as token:
            reader = wave.reader(self.root, roles=['holdout'], authorization=token)
            self.assertEqual(json.loads(reader.read('profile/held', 'statistics')), {'secret': 'held'})
            with self.assertRaisesRegex(PermissionError, 'generation'):
                wave.reader(self.root / 'other', roles=['holdout'], authorization=token)
        with self.assertRaisesRegex(PermissionError, 'inactive'): reader.read('profile/held', 'statistics')
        with self.assertRaisesRegex(PermissionError, 'already spent'):
            with self.mod.Receipt(log, {**config, 'candidate': 'changed'}).expose(): pass
        self.assertEqual([json.loads(l)['event'] for l in log.read_text().splitlines()], ['begin', 'complete'])
        with self.assertRaisesRegex(ValueError, 'generation must freeze'):
            self.mod.Receipt(self.root / 'r2.jsonl', {**config, 'generation': ['short']})


class PinnedDeclaration(unittest.TestCase):
    """The committed W39 declaration itself passes every rule the synthetic cases exercise."""

    def test_default_wave_validates_and_plans(self):
        mod = load()
        wave = mod.default_wave()
        included, excluded = wave.launch_plan()
        self.assertEqual(len(wave.cells), sum(len(wave.scenes) if p['scenes'] == 'all' else len(p['scenes'])
                                              for p in wave.spec['profiles']))
        self.assertTrue(included)
        self.assertFalse(set(included) & set(wave.split['holdout']))
        self.assertTrue(all(wave.roles[s] in ('calibration', 'validation') for s in included + list(excluded)))
        for sid in included:
            self.assertIsNone(mod.web_placement_refusal(wave.component(sid), wave.spec['canvas']))
            self.assertFalse(mod.native_only(wave.component(sid)))
        self.assertTrue(wave.preflight_ids)
        with self.assertRaises(PermissionError): wave.launch_plan(['holdout'])
        out = io.StringIO()
        with redirect_stdout(out):
            mod.main(['plan', '--fixtures', '/tmp/w39-f', '--out-matrix', '/tmp/w39-m.json', '--captures', '/tmp/w39-c'])
        plan = json.loads(out.getvalue())
        self.assertEqual(plan['scenes'], included); self.assertEqual(plan['excluded'], excluded)
        with self.assertRaises(PermissionError):
            mod.main(['plan', '--roles', 'holdout', '--fixtures', '/tmp/f', '--out-matrix', '/tmp/m', '--captures', '/tmp/c'])
        with self.assertRaisesRegex(ValueError, 'canonical'):
            mod.main(['plan', '--fixtures', str(mod.ROOT / 'apps/reference-apple/fixtures'),
                      '--out-matrix', '/tmp/m', '--captures', '/tmp/c'])


if __name__ == '__main__': unittest.main(verbosity=2)
