#!/usr/bin/env python3.12
"""The W39 archive producer and replay on synthetic runs, plus one real-reader cell (§5.184).

Synthetic: a small declaration with a calibration pair, a colour cell that
borrows the grey opaque, and a held-out colour; two normal runs (the colour
`none` references in run 1 only) and a sentinel run. The fake statistics are a
function of every frame the payload carries, so a dependency that failed to
arrive in the archive would change them and the replay would refuse.

Every run's `admission.json` is written by the sitting's own constructor
(`sitting.run_admission`) from the launch argv the sitting builds for the arm
(`sitting.protocol_argv`) and a manifest whose `captureProtocol` carries what the
harness records for it, so the producer is tested against the admission the
sitting actually writes, not a record shaped to suit the producer.
"""
import gzip
import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w39_archive  # noqa: E402


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


producer = module('w39_archive_producer', 'archive-producer.py')
sitting = module('w39_archive_test_sitting', 'sitting.py')
replayer = module('w39_replay_archive', 'replay-archive.py')
wave_mod = sys.modules['wave']
P1 = 'apple-macos-27.0-1x-light-standard-glass0.5'
P2 = 'apple-macos-27.0-2x-dark-standard-glass0.5'
CANVAS = {'width': 16, 'height': 12}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def harness_protocol(arm, label):
    """captureProtocol as the harness encodes it: Swift omits a nil optional (orderSeed)."""
    return {'runLabel': label, **{k: v for k, v in sitting.PROTOCOLS[arm].items() if v is not None}}


def write_run(root, profiles, pass_name, n, protocol=None):
    """manifest.json and the SITTING's admission.json for one captured run."""
    arm = sitting.protocol_of_pass(pass_name)
    label = f'w39-{pass_name}-{n}'
    (root / 'manifest.json').write_text(json.dumps(dict(
        captureProtocol=protocol if protocol is not None else harness_protocol(arm, label), profiles=profiles)))
    manifest = json.loads((root / 'manifest.json').read_text())
    argv = ['open', '-W', '--args', 'capture', '--run-label', label, *sitting.protocol_argv(arm)]
    admission = sitting.run_admission(pass_name, n, argv, manifest, sha(root / 'manifest.json'),
                                      sum(len(p['fixtures']) for p in profiles), (), None)
    (root / 'admission.json').write_text(json.dumps(admission) + '\n')
    return root


def fake_analyse(payload):
    out = {'nativeOnly': bool(payload.get('nativeOnly')), 'scale': payload['scale']}
    for name in ('rgb', 'noGlass', 'opaque', 'opaqueNoGlass'):
        if payload.get(name) is not None:
            a = np.asarray(payload[name])
            out[name] = dict(sum=int(a.astype(np.int64).sum()), sha=hashlib.sha256(a.tobytes()).hexdigest())
    out['origin'] = payload['component'].get('frameOrigin')
    return out


GLASS = {'kind': 'capsule-circular', 'size': [8, 4], 'position': [8, 6]}
SCENES = {
    'canvas': CANVAS,
    'backgrounds': {'g': {'kind': 'solid', 'srgb': [128] * 3}, 'c': {'kind': 'solid', 'srgb': [90, 70, 100]},
                    'h': {'kind': 'solid', 'srgb': [70, 90, 100]}},
    'components': {'glass': GLASS, 'opaque': {**GLASS, 'opaque': True, 'fillSRGB': [0, 0, 0]},
                   'empty': {'kind': 'none'}},
    'scenes': [{'id': i, 'background': b, 'component': c, 'state': 'rest'} for i, b, c in [
        ('g-glass', 'g', 'glass'), ('g-opaque', 'g', 'opaque'), ('g-ref', 'g', 'empty'),
        ('c-glass', 'c', 'glass'), ('c-ref', 'c', 'empty'),
        ('h-glass', 'h', 'glass'), ('h-ref', 'h', 'empty')]],
    'profiles': [{'key': P1, 'scenes': 'all'}, {'key': P2, 'scenes': 'all'}],
}
IDS = [s['id'] for s in SCENES['scenes']]
SCENES['split'] = {'probe': IDS, 'calibration': [], 'validation': [], 'holdout': [], 'recorded': []}
SPLIT = {'schema': 'w39-split-1', 'calibration': ['g-glass', 'g-opaque', 'g-ref', 'c-glass', 'c-ref'],
         'validation': [], 'holdout': ['h-glass', 'h-ref'],
         'dependencies': {'g-glass': {'noGlass': 'g-ref', 'opaque': 'g-opaque'},
                          'c-glass': {'noGlass': 'c-ref', 'opaque': 'g-opaque'},
                          'h-glass': {'noGlass': 'h-ref', 'opaque': 'g-opaque'}}}


def render(shape, scale, hw, inside, outside, quad=16):
    """Supersampled coverage render of a circular stadium, rounded to uint8."""
    import w39_readers as R
    h, w = hw
    x0, y0, x1, y1 = shape.rect(scale); r = min(shape.size) / 2 * scale
    u = (np.arange(quad) + .5) / quad
    y, x = np.mgrid[:h, :w].astype(float)
    cover = np.zeros(hw)
    for dy in u:
        for dx in u: cover += R.I.stadium(x + dx, y + dy, [x0, y0, x1, y1], r)[0] <= 0
    cover = (cover / (quad * quad))[..., None]
    return np.rint(cover * np.float64(inside) + (1 - cover) * np.float64(outside)).astype(np.uint8)


class Archive(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.decl = self.base / 'declaration'; self.decl.mkdir()
        (self.decl / 'scenes.json').write_text(json.dumps(SCENES))
        (self.decl / 'split.json').write_text(json.dumps(SPLIT))
        (self.decl / 'pins.json').write_text(json.dumps({'scenesSha256': sha(self.decl / 'scenes.json'),
                                                        'splitSha256': sha(self.decl / 'split.json')}))
        self.wave = wave_mod.Wave(self.decl / 'scenes.json', self.decl / 'split.json', self.decl / 'pins.json')
        self.raw = self.base / 'raw'
        # Run 2 repeats run 1 byte for byte except one state of the grey glass cell.
        run1 = self.capture('pass-a-run1', IDS, seed=1)
        run2 = self.capture('pass-a-run2', [i for i in IDS if i not in ('c-ref', 'h-ref')], seed=1,
                            vary='g-glass', n=2)
        sentinel = self.capture('pass-a-sentinel', ['c-glass', 'h-glass'], seed=1, sentinel=True)
        self.runs = [run1, run2, sentinel]

    def frame(self, sid, profile, seed, vary):
        scale = 1 if '-1x-' in profile else 2
        rng = np.random.default_rng(int(hashlib.sha256(f'{sid}/{profile}/{seed}'.encode()).hexdigest()[:8], 16))
        a = rng.integers(0, 256, (CANVAS['height'] * scale, CANVAS['width'] * scale, 3), dtype=np.uint8)
        if vary: a[0, 0, 0] ^= 1
        return a

    def capture(self, name, ids, seed, vary=None, sentinel=False, admitted=True, n=1, protocol=None):
        root = self.raw / name; profiles = []
        for profile in (P1, P2):
            fixtures = []
            for sid in ids:
                file = f'{profile}/{sid}.png'; (root / profile).mkdir(parents=True, exist_ok=True)
                # The same bytes in every run, so byte-stable repeats de-duplicate.
                Image.fromarray(self.frame(sid, profile, seed, vary == sid)).save(root / file)
                fixtures.append(dict(sceneId=sid, file=file, deterministic=True,
                                     suppliedPaths=[{'frameOrigin': [4, 4]}], frameOrigin=[4, 4],
                                     windowFrame={'requested': [0, 0, 16, 12], 'actual': [0, 0, 16, 12]}))
            profiles.append(dict(profileKey=profile, fixtures=fixtures))
        write_run(root, profiles, 'active-1x' + ('-sentinel' if sentinel else ''), n, protocol)
        if not admitted:
            (root / 'admission.json').write_text(json.dumps(dict(admitted=False, dry=True)))
        return root

    def produce(self, out='archive', runs=None):
        loaded = producer.load_runs(runs or self.runs)
        captured = {p + '/' + s for r in loaded for p, s in r['entries']}
        return w39_archive.produce(producer.groups_from(loaded, self.wave), self.wave, self.base / out,
                                   analyse=fake_analyse, captured=captured)

    def reader(self, out='archive'): return self.wave.reader(self.base / out)

    def test_complete_role_separated_archive_with_dependency_closure(self):
        result = self.produce()
        self.assertEqual(result['declaredCells'], 14); self.assertEqual(result['archivedCells'], 14)
        self.assertEqual(result['uncaptured'], [])
        roles = {e['path'].split('/')[0] for e in result['entries'] if e['cell'].endswith('/h-glass')}
        self.assertEqual(roles, {'holdout'})
        self.assertTrue(all(e['path'].startswith('calibration/') for e in result['entries']
                            if e['cell'].split('/')[1] in SPLIT['calibration']))
        text = (self.base / 'archive/inventory.json').read_text()
        self.assertNotIn('statistics":{', text); self.assertNotIn('sum', text)
        reader = self.reader()
        runs = w39_archive.recorded_statistics(reader, P1 + '/c-glass')
        self.assertEqual([r['protocol'] for r in runs], ['normal', 'normal', 'long'])
        # The colour reference exists in run 1 only; runs 2 and the sentinel carry run 1's bytes.
        crop_runs, states = w39_archive.unbundle(reader.read(P1 + '/c-glass', 'crop'))
        self.assertEqual(len(states), 1)
        payload = w39_archive.unpack(next(iter(states.values())))
        self.assertEqual([r['sources']['noGlass'] for r in crop_runs], [str(self.runs[0].resolve())] * 3)
        self.assertEqual([r['sources']['opaque'] for r in crop_runs], [str(r.resolve()) for r in self.runs[:2]]
                         + [str(self.runs[0].resolve())])
        self.assertEqual(payload['dependencies']['opaque']['sceneId'], 'g-opaque')
        # The borrowed control's OWN reference (grey), not the colour cell's, is carried,
        # hashed and sourced as a separate dependency (review P1-3).
        self.assertEqual(payload['dependencies']['opaqueNoGlass']['sceneId'], 'g-ref')
        g_ref = np.asarray(Image.open(self.runs[0] / f'{P1}/g-ref.png'))
        np.testing.assert_array_equal(payload['opaqueNoGlass'], g_ref)
        self.assertEqual([r['inputHashes']['opaqueNoGlass'] for r in crop_runs],
                         [sha(r / f'{P1}/g-ref.png') for r in self.runs[:2]] + [sha(self.runs[0] / f'{P1}/g-ref.png')])
        self.assertEqual([r['sources']['opaqueNoGlass'] for r in crop_runs],
                         [str(r.resolve()) for r in self.runs[:2]] + [str(self.runs[0].resolve())])
        self.assertNotEqual(crop_runs[0]['inputHashes']['opaqueNoGlass'], crop_runs[0]['inputHashes']['noGlass'])
        self.assertIn('opaqueNoGlass', crop_runs[0]['attestation'])
        np.testing.assert_array_equal(payload['noGlass'], np.asarray(Image.open(self.runs[0] / f'{P1}/c-ref.png')))
        self.assertEqual(payload['component']['frameOrigin'], [4, 4])
        self.assertIn('windowFrame', crop_runs[0]['attestation']['native'])
        # An opaque control carries its background's reference for its coverage.
        _, states = w39_archive.unbundle(reader.read(P1 + '/g-opaque', 'crop'))
        self.assertEqual(w39_archive.unpack(next(iter(states.values())))['dependencies']['noGlass']['sceneId'],
                         'g-ref')
        # A changed state is a second state, not a registration.
        _, states = w39_archive.unbundle(reader.read(P1 + '/g-glass', 'crop'))
        self.assertEqual(len(states), 2)

    def test_replay_from_archive_alone_with_raw_root_denied(self):
        self.produce()
        out = io.StringIO()
        with redirect_stdout(out):
            replayer.main([str(self.base / 'archive'), '--declaration', str(self.decl),
                           '--deny-raw-root', str(self.raw)], analyse=fake_analyse)
        report = json.loads(out.getvalue())
        self.assertTrue(report['identical'])
        self.assertEqual(report['cells'], 10)       # calibration only: holdout needs the receipt
        self.assertNotIn('h-glass', out.getvalue())
        with self.assertRaisesRegex(PermissionError, 'raw inputs forbidden'):
            open(self.runs[0] / 'manifest.json').close()

    def test_holdout_payload_is_behind_the_boundary(self):
        self.produce()
        reader = self.reader()
        for kind in ('crop', 'statistics'):
            with self.assertRaisesRegex(PermissionError, 'holdout'): reader.read(P1 + '/h-glass', kind)
        with self.assertRaisesRegex(PermissionError, 'holdout'):
            self.wave.reader(self.base / 'archive', roles=['holdout'])

    def test_replay_refuses_an_altered_archive_and_a_different_instrument(self):
        result = self.produce()
        entry = next(e for e in result['entries'] if e['cell'] == P1 + '/g-glass' and e['kind'] == 'statistics')
        stats = json.loads(gzip.decompress((self.base / 'archive' / entry['path']).read_bytes()))
        with self.assertRaisesRegex(ValueError, 'differ'):
            w39_archive.replay(self.reader(), P1 + '/g-glass',
                               analyse=lambda p: {**fake_analyse(p), 'changed': True})
        self.assertTrue(w39_archive.replay(self.reader(), P1 + '/g-glass', analyse=fake_analyse)['identical'])
        stats['statistics'][next(iter(stats['statistics']))]['rgb']['sum'] += 1
        (self.base / 'archive' / entry['path']).write_bytes(gzip.compress(w39_archive.encode(stats), mtime=0))
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            w39_archive.replay(self.reader(), P1 + '/g-glass', analyse=fake_analyse)

    def test_protocol_is_the_sittings_admission_checked_against_the_capture(self):
        loaded = producer.load_runs(self.runs)
        self.assertEqual([r['protocol'] for r in loaded], ['normal', 'normal', 'long'])
        self.assertEqual(json.loads((self.runs[2] / 'admission.json').read_text())['captureProtocol'],
                         {**sitting.PROTOCOLS['long']})
        self.assertEqual(sitting.PROTOCOLS['long']['initialSettleSeconds'], 8)
        self.assertEqual(sitting.PROTOCOLS['long']['orderSeed'], 3901)

        def refused(name, edit, pattern, sentinel=False):
            root = self.capture(name, IDS, seed=1, sentinel=sentinel)
            path = root / 'admission.json'; admission = json.loads(path.read_text())
            manifest = json.loads((root / 'manifest.json').read_text())
            edit(admission, manifest)
            path.write_text(json.dumps(admission)); (root / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, pattern): producer.load_runs([root])

        # A missing or unknown arm is refused, never inferred from the manifest.
        refused('no-arm', lambda a, m: a.pop('protocol'), 'no protocol arm')
        refused('odd-arm', lambda a, m: a.update(protocol='sentinel'), 'no protocol arm')
        # W34's long signature (settle 8, seed 3401) is not W39's long arm.
        refused('w34-seed', lambda a, m: m['captureProtocol'].update(orderSeed=3401), 'not the long arm',
                sentinel=True)
        refused('w34-unnamed', lambda a, m: (a.pop('protocol'), m['captureProtocol'].update(orderSeed=3401)),
                'no protocol arm', sentinel=True)
        # An admission whose arm disagrees with the capture that happened.
        refused('short-settle', lambda a, m: m['captureProtocol'].update(initialSettleSeconds=1.75),
                'not the long arm', sentinel=True)
        refused('relabelled', lambda a, m: a.update(protocol='long', captureProtocol=dict(sitting.PROTOCOLS['long'])),
                'not the long arm')
        refused('echo', lambda a, m: a['captureProtocol'].update(orderSeed=3901), 'admission captureProtocol')
        refused('not-sentinel', lambda a, m: (a.update(protocol='long', captureProtocol=dict(sitting.PROTOCOLS['long'])),
                                              m['captureProtocol'].update(initialSettleSeconds=8.0, orderSeed=3901)),
                'sentinel passes')
        refused('other-manifest', lambda a, m: a.update(manifestSha256='0' * 64), 'different manifest')
        # The sitting's constructor itself refuses a manifest that is not the launched arm.
        with self.assertRaisesRegex(ValueError, 'not the launched'):
            self.capture('sitting-refuses', IDS, seed=1, sentinel=True,
                         protocol=harness_protocol('normal', 'w39-active-1x-sentinel-1'))

    def test_carried_control_reference_may_not_outrank_its_dependent(self):
        # The closure adds a dependency the split never names; the rank guard still holds.
        # No grey glass here, so the split can hold the grey reference above the colour
        # cell that borrows the grey control.
        scenes = json.loads(json.dumps(SCENES))
        scenes['scenes'] = [x for x in scenes['scenes'] if x['id'] != 'g-glass']
        ids = [x['id'] for x in scenes['scenes']]; scenes['split']['probe'] = ids
        split = json.loads(json.dumps(SPLIT)); del split['dependencies']['g-glass']
        split['calibration'] = ['g-opaque', 'c-glass', 'c-ref']; split['validation'] = ['g-ref']
        decl = self.base / 'ranked'; decl.mkdir()
        (decl / 'scenes.json').write_text(json.dumps(scenes)); (decl / 'split.json').write_text(json.dumps(split))
        (decl / 'pins.json').write_text(json.dumps({'scenesSha256': sha(decl / 'scenes.json'),
                                                   'splitSha256': sha(decl / 'split.json')}))
        wave = wave_mod.Wave(decl / 'scenes.json', decl / 'split.json', decl / 'pins.json')
        groups = producer.groups_from(producer.load_runs([self.capture('ranked', ids, seed=1)]), wave)
        self.assertTrue(min(wave.cells).endswith('/c-glass'))   # the first group is the colour cell
        with self.assertRaisesRegex(PermissionError, 'ranks above its dependent: g-ref'): next(groups)

    def test_producer_refusals(self):
        self.produce()
        with self.assertRaisesRegex(ValueError, 'already exists'): self.produce()
        dry = self.capture('dry', IDS, seed=1, admitted=False)
        with self.assertRaisesRegex(ValueError, 'not an admitted'): self.produce('b', [dry])
        with self.assertRaisesRegex(ValueError, 'named twice'): self.produce('c', [self.runs[0], self.runs[0]])
        lonely = self.capture('lonely', ['c-glass'], seed=1)
        with self.assertRaisesRegex(ValueError, 'missing captured dependency'): self.produce('d', [lonely])
        small = self.capture('small', IDS, seed=1)
        Image.fromarray(np.zeros((3, 3, 3), np.uint8)).save(small / f'{P1}/g-ref.png')
        with self.assertRaisesRegex(ValueError, 'dimensions'): self.produce('e', [small])
        with self.assertRaisesRegex(ValueError, 'outside the repository'):
            producer.refuse_repository(wave_mod.ROOT / 'packages/calibration/results/x')
        producer.refuse_repository(self.base / 'fine')

    def test_release_asset_round_trip_feeds_the_guarded_reader(self):
        self.produce()
        release = module('w39_release_asset', 'release-asset.py')
        fetcher = module('w39_fetch_archive', 'fetch-archive.py')
        asset = release.pack(self.base / 'archive', self.base / 'release')
        root = fetcher.fetch('w39-archive', asset['asset'], asset['sha256'], cache=self.base / 'cache',
                             source=asset['path'], download=None)
        reader = self.wave.reader(root)
        self.assertEqual(reader.generation, sha(self.base / 'archive/inventory.json'))
        cells = sorted({r['cell'] for r in reader.report_inventory() if r['cell'].split('/', 1)[1] in reader.allowed})
        self.assertEqual(len(cells), 10)
        self.assertTrue(all(w39_archive.replay(reader, c, analyse=fake_analyse)['identical'] for c in cells))
        with self.assertRaisesRegex(PermissionError, 'holdout'): reader.read(P2 + '/h-glass', 'crop')

    def test_production_is_deterministic(self):
        a, b = self.produce('a'), self.produce('b')
        self.assertEqual([e['sha256'] for e in a['entries']], [e['sha256'] for e in b['entries']])


class SittingMainAdmission(unittest.TestCase):
    """Admissions written by the sitting's own `main` (stubbed machine and harness,
    test-sitting.py's full ordered sitting) are what the producer accepts, arm and all."""

    def test_main_admitted_normal_and_sentinel_runs_load_with_their_arms(self):
        T = module('w39_archive_test_sitting_driver', 'test-sitting.py')
        with tempfile.TemporaryDirectory() as tmp:
            S = T.load(); stubs = T.Stubs(tmp)
            T.full_sitting(S, stubs)
            roots = [stubs.root / 'active-1x/run-1', stubs.root / 'active-1x/run-7',
                     stubs.root / 'active-1x-sentinel/run-1', stubs.root / 'inactive-2x-sentinel/run-3']
            loaded = producer.load_runs(roots)
            self.assertEqual([r['protocol'] for r in loaded], ['normal', 'normal', 'long', 'long'])
            self.assertEqual([r['manifest']['captureProtocol'].get('orderSeed') for r in loaded],
                             [None, None, 3901, 3901])
            # The production module's arms are the ones main wrote under.
            self.assertEqual(S.PROTOCOLS, producer.sitting_protocols())
            # A main-written sentinel admission, its harness manifest spoiled to W34's seed.
            m = json.loads((roots[2] / 'manifest.json').read_text()); m['captureProtocol']['orderSeed'] = 3401
            (roots[2] / 'manifest.json').write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError, 'not the long arm'): producer.load_runs([roots[2]])


class RealReaderIntegration(unittest.TestCase):
    """The real `w39_readers.analyse`, archived and replayed."""

    def test_borrowed_grey_control_calibrates_on_its_own_reference_through_the_archive(self):
        # Review P1-3: a colour glass cell borrows a white-over-grey-128 opaque control.
        # Archived by the producer from sitting-admitted runs and replayed through the
        # real reader, the control's coverage must read alpha 0 on every exterior shell
        # and the same measured edge as the control's own native-only cell.
        import w39_readers as R
        canvas = {'width': 160, 'height': 100}
        glass = {'kind': 'capsule-circular', 'size': [120, 44], 'position': [80, 50]}
        scenes = {'canvas': canvas,
                  'backgrounds': {'g': {'kind': 'solid', 'srgb': [128] * 3},
                                  'c': {'kind': 'solid', 'srgb': [69, 61, 63]}},
                  'components': {'glass': glass, 'opaque': {**glass, 'opaque': True, 'fillSRGB': [255] * 3},
                                 'empty': {'kind': 'none'}},
                  'scenes': [{'id': i, 'background': b, 'component': c, 'state': 'rest'} for i, b, c in [
                      ('g-opaque', 'g', 'opaque'), ('g-ref', 'g', 'empty'),
                      ('c-glass', 'c', 'glass'), ('c-ref', 'c', 'empty')]],
                  'profiles': [{'key': P1, 'scenes': 'all'}, {'key': P2, 'scenes': 'all'}]}
        ids = [x['id'] for x in scenes['scenes']]
        scenes['split'] = {'probe': ids, 'calibration': [], 'validation': [], 'holdout': [], 'recorded': []}
        split = {'schema': 'w39-split-1', 'calibration': ids, 'validation': [], 'holdout': [],
                 'dependencies': {'c-glass': {'noGlass': 'c-ref', 'opaque': 'g-opaque'}}}
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); decl = base / 'declaration'; decl.mkdir()
            (decl / 'scenes.json').write_text(json.dumps(scenes)); (decl / 'split.json').write_text(json.dumps(split))
            (decl / 'pins.json').write_text(json.dumps({'scenesSha256': sha(decl / 'scenes.json'),
                                                       'splitSha256': sha(decl / 'split.json')}))
            wave = wave_mod.Wave(decl / 'scenes.json', decl / 'split.json', decl / 'pins.json')
            # The control's attested origin is a quarter pixel off the glass's: its own
            # geometry, not the glass's, is what its coverage must be read on.
            origins = {'c-glass': [20, 28], 'g-opaque': [20.25, 28]}
            colours = {'c-glass': ([120, 110, 115], [69, 61, 63]), 'g-opaque': ([255] * 3, [128] * 3),
                       'g-ref': (None, [128] * 3), 'c-ref': (None, [69, 61, 63])}
            root = base / 'raw' / 'run-1'; profiles = []
            for profile in (P1, P2):
                scale = 1 if '-1x-' in profile else 2
                fixtures = []
                for sid in ids:
                    (root / profile).mkdir(parents=True, exist_ok=True)
                    inside, outside = colours[sid]
                    entry = dict(sceneId=sid, file=f'{profile}/{sid}.png')
                    if inside is None: image = np.broadcast_to(np.uint8(outside), (100 * scale, 160 * scale, 3))
                    else:
                        path = dict(kind='capsule-circular', frameOrigin=origins[sid], rect=[0, 0, 120, 44],
                                    opaque=sid == 'g-opaque', elements=[])
                        entry['suppliedPaths'] = [path]
                        image = render(R.shapes_of({**glass, 'suppliedPaths': [path]})[0], scale,
                                       (100 * scale, 160 * scale), inside, outside)
                    Image.fromarray(np.ascontiguousarray(image)).save(root / entry['file'])
                    fixtures.append(entry)
                profiles.append(dict(profileKey=profile, fixtures=fixtures))
            write_run(root, profiles, 'active-1x', 1)
            loaded = producer.load_runs([root])
            w39_archive.produce(producer.groups_from(loaded, wave), wave, base / 'archive',
                                captured={p + '/' + x for r in loaded for p, x in r['entries']})
            reader = wave.reader(base / 'archive')
            for cell in sorted(wave.cells):
                self.assertTrue(w39_archive.replay(reader, cell)['identical'], cell)
            for profile in (P1, P2):
                scale = 1 if '-1x-' in profile else 2
                [run] = w39_archive.recorded_statistics(reader, profile + '/c-glass')
                [own] = w39_archive.recorded_statistics(reader, profile + '/g-opaque')
                self.assertEqual(run['protocol'], 'normal')
                cov, own = run['statistics']['members'][0]['coverage'], own['statistics']['members'][0]['coverage']
                self.assertEqual((cov['status'], cov['controlSceneId'], cov['controlReferenceSceneId']),
                                 ('measured', 'g-opaque', 'g-ref'))
                self.assertEqual((cov['backgroundRGB'], cov['fillRGB'], cov['frameOriginCss']),
                                 ([128.] * 3, [255.] * 3, [20.25, 28.]))
                self.assertEqual(own['backgroundSource'], cov['backgroundSource'])
                exterior = [b['alpha'] for b in cov['bins'] if b['part'] != 'boundary' and b['shell'] >= 0
                            and b['alpha'] is not None]
                self.assertEqual(len(exterior), len([b for b in cov['bins'] if b['part'] != 'boundary'
                                                     and b['shell'] >= 0 and b['pixels'] > 0]))
                self.assertTrue(exterior and all(a == 0 for a in exterior), (profile, exterior[:4]))
                self.assertEqual(cov['bins'], own['bins']); self.assertEqual(cov['edges'], own['edges'])
                self.assertEqual(cov['edges']['right']['pathEdge'], 140.25 * scale)
                # The discriminating witness: calibrated on the dependent's colour reference,
                # as before the fix, the grey exterior reads a nonzero alpha and every
                # measured edge moves.
                _, states = w39_archive.unbundle(reader.read(profile + '/c-glass', 'crop'))
                payload = w39_archive.unpack(next(iter(states.values())))
                wrong = R.opaque_coverage(payload['opaque'], payload['noGlass'], [255.] * 3)
                self.assertGreater(float(abs(wrong[:2, :2]).min()), .3)
                shape = R.shapes_of(payload['dependencies']['opaque']['component'])[0]
                for side in R.SIDES:
                    moved = R.coverage_profile(wrong, shape, scale, side)['measuredEdge']
                    self.assertGreater(abs(moved - cov['edges'][side]['measuredEdge']), 1, (profile, side))

    def test_w34_calibration_cell_round_trips_through_the_archive(self):
        import w39_readers
        cell = 'apple-macos-27.0-1x-light-standard-glass0.5/grey-255__circular-200__rest'
        payload = w39_readers.w34_payload(cell)
        self.assertEqual(payload['role'], 'calibration')
        direct = json.loads(w39_archive.encode(w39_readers.analyse(payload)))
        replayed = json.loads(w39_archive.encode(w39_readers.analyse(w39_archive.unpack(w39_archive.pack(payload)))))
        self.assertEqual(direct, replayed)
        self.assertEqual(direct['schema'], 'w39-readers/1')


if __name__ == '__main__': unittest.main(verbosity=2)
