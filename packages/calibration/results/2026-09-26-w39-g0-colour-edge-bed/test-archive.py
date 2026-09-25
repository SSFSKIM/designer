#!/usr/bin/env python3.12
"""The W39 archive producer and replay on synthetic runs, plus one real-reader cell (§5.184).

Synthetic: a small declaration with a calibration pair, a colour cell that
borrows the grey opaque, and a held-out colour; two normal runs (the colour
`none` references in run 1 only) and a sentinel run. The fake statistics are a
function of every frame the payload carries, so a dependency that failed to
arrive in the archive would change them and the replay would refuse.
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
replayer = module('w39_replay_archive', 'replay-archive.py')
wave_mod = sys.modules['wave']
P1 = 'apple-macos-27.0-1x-light-standard-glass0.5'
P2 = 'apple-macos-27.0-2x-dark-standard-glass0.5'
CANVAS = {'width': 16, 'height': 12}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fake_analyse(payload):
    out = {'nativeOnly': bool(payload.get('nativeOnly')), 'scale': payload['scale']}
    for name in ('rgb', 'noGlass', 'opaque'):
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
                        vary='g-glass')
        sentinel = self.capture('pass-a-sentinel', ['c-glass', 'h-glass'], seed=1, protocol='long')
        self.runs = [run1, run2, sentinel]

    def frame(self, sid, profile, seed, vary):
        scale = 1 if '-1x-' in profile else 2
        rng = np.random.default_rng(int(hashlib.sha256(f'{sid}/{profile}/{seed}'.encode()).hexdigest()[:8], 16))
        a = rng.integers(0, 256, (CANVAS['height'] * scale, CANVAS['width'] * scale, 3), dtype=np.uint8)
        if vary: a[0, 0, 0] ^= 1
        return a

    def capture(self, name, ids, seed, vary=None, protocol='normal', admitted=True):
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
        (root / 'manifest.json').write_text(json.dumps(dict(profiles=profiles)))
        (root / 'admission.json').write_text(json.dumps(dict(admitted=admitted, dry=False, protocol=protocol,
                                                             run=name)))
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


class RealReaderIntegration(unittest.TestCase):
    """One W34 calibration cell through the real `w39_readers.analyse`, archived and replayed."""

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
