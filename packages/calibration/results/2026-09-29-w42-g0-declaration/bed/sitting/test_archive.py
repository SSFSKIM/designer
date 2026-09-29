#!/usr/bin/env python3.12
"""W42 archive tests (charter clause 5): producer -> tree check -> deterministic pack -> fetch by
digest from a local copy -> replay through bed/wave.py's Reader with the raw root denied.

The run tree is SYNTHETIC: real declaration (bed/scenes-w42-body.json, bed.json, pins.json),
real sitting admissions (sitting.run_admission over manifests shaped like the harness's),
solid-colour PNGs that are not captures. One cell carries two states across its runs, so a
losing state is present. Needs python3.12 with numpy/PIL and the zstd CLI.

Run: python3.12 -m unittest -v test_archive    (from this directory)"""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from PIL import Image

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = load('w42_archive_under_test', HERE / 'w42_archive.py')
T = load('w42_test_sitting_for_archive', HERE / 'test_sitting.py')
S, P = T.S, T.P
KEY = '1x-light-active'
PASSES = ['dump-' + KEY, KEY, KEY + '-sentinel']


def colour(sid, run):
    h = hashlib.sha256(sid.encode()).digest()
    rgb = [h[0], h[1], h[2]]
    if sid.startswith('a-g128-rrect-md-1x') and run in (2, 5):   # a second, losing state
        rgb[0] = (rgb[0] + 1) % 256
    return tuple(rgb)


def write_run(root, p, n, pose='active'):
    doc = P.derive(p['key'], n, p['kind'] == 'sentinel')
    run = root / p['name'] / f'run-{n}'
    run.mkdir(parents=True)
    label = f'w42-{p["name"]}-{n}'
    protocol = S.protocol_of_pass(p)
    m = T.manifest(doc, pose, 1, label, protocol)
    for profile in m['profiles']:
        for f in profile['fixtures']:
            path = run / f['file']
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.new('RGB', (320, 200), colour(f['sceneId'], n)).save(path)
    raw = json.dumps(m).encode()
    (run / 'manifest.json').write_bytes(raw)
    for name in ('attest.open.json', 'attest.close.json', 'session-before.json', 'driver-idle.log',
                 'producer-capture.out', 'producer-capture.err'):
        (run / name).write_text('{}\n' if name.endswith('.json') else f'{name} of {label}\n')
    (run / 'backgrounds').mkdir()
    Image.new('RGB', (320, 200), (1, 2, 3)).save(run / 'backgrounds' / 'grey-128@1x.png')
    argv = S.capture_argv(['open', '-W'], Path('/a.app'), Path('/s.json'), run, 1, label, protocol,
                          sorted(s['id'] for s in doc['scenes']), pose)
    (run / 'launch.json').write_text(json.dumps(dict(argv=argv)) + '\n')
    admission = S.run_admission(p, n, argv, m, hashlib.sha256(raw).hexdigest(),
                                sum(len(q['scenes']) for q in doc['profiles']))
    (run / 'admission.json').write_text(json.dumps(admission) + '\n')
    (root / p['name'] / f'scenes-run-{n}.json').write_text(json.dumps(doc) + '\n')


def write_dump(root, p):
    run = root / p['name'] / 'run-1'
    (run / 'json').mkdir(parents=True)
    for sid in P.dump_ids(p['key']):
        (run / 'json' / f'{sid}.json').write_text(json.dumps(dict(scene=sid, synthetic=True)) + '\n')
    (run / 'check.json').write_text(json.dumps(dict(departures=0, synthetic=True)) + '\n')
    (run / 'admission.json').write_text(json.dumps(dict(admitted=True, protocol='dump', run=1,
                                                         **{'pass': p['name']})) + '\n')
    (run / 'dump.out').write_text('== dump-layers ==\n')


def sitting_tree(root):
    order = {p['name']: p for p in P.pass_order(P.load()[1])}
    write_dump(root, order[PASSES[0]])
    for name in PASSES[1:]:
        for n in range(1, order[name]['runs'] + 1):
            write_run(root, order[name], n)
    q = root / KEY / 'QUARANTINE-run-3-1'
    q.mkdir()
    (q / 'refusal.txt').write_text('ValueError: a quarantined attempt, kept\n')
    (root / 'logs').mkdir()
    (root / 'logs' / f'{KEY}-driver.txt').write_text('driver log\n')


class Archive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.raw = cls.tmp / 'raw'
        sitting_tree(cls.raw)
        cls.wave = A.wave_module().default_wave()
        cls.out = cls.tmp / 'archive'
        cls.inventory = A.produce(cls.raw, cls.out, wave=cls.wave, passes=PASSES)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_inventory_names_the_pinned_declaration_and_roles(self):
        inv = json.loads((self.out / 'inventory.json').read_text())
        self.assertEqual(inv['scenesSha256'], hashlib.sha256(self.wave.scenes_path.read_bytes()).hexdigest())
        self.assertEqual(inv['splitSha256'], hashlib.sha256(self.wave.split_path.read_bytes()).hexdigest())
        pins = json.loads((A.BED_DIR / 'pins.json').read_text())
        self.assertEqual(inv['splitSha256'], pins['bed.json'])
        self.assertEqual(inv['archivedCells'], 23)
        self.assertEqual(inv['uncaptured'], [])
        for row in inv['entries']:
            sid = row['cell'].split('/', 1)[1]
            self.assertEqual(row['path'].split('/')[0], self.wave.roles[sid])
        self.assertTrue(all(r['path'].startswith('operational/') for r in inv['operational']))
        self.assertTrue(all(r['path'].startswith('dumps/') for r in inv['dumps']))
        paths = {r['path'] for r in inv['operational']}
        self.assertIn(f'operational/{KEY}/QUARANTINE-run-3-1/refusal.txt', paths)
        self.assertIn(f'operational/logs/{KEY}-driver.txt', paths)
        self.assertIn(f'operational/{KEY}/run-1/manifest.json', paths)
        self.assertFalse(any(p.endswith('.png') for p in paths))
        self.assertEqual(len(inv['dumps']), 15)

    def test_reference_travels_inside_its_dependent_role(self):
        wave = self.wave
        cell = 'apple-macos-27.0-1x-light-standard-glass0.5/h-g232-rrect-md__rest'
        row = next(r for r in json.loads((self.out / 'inventory.json').read_text())['entries']
                   if r['cell'] == cell and r['kind'] == 'states')
        self.assertTrue(row['path'].startswith('holdout/'))
        header, blobs = A.unbundle((self.out / row['path']).read_bytes())
        self.assertEqual(len(header['runs']), 7)
        dep = header['runs'][6]['dependencies']['noGlass']
        self.assertEqual((dep['sourcePass'], dep['sourceRun']), (KEY, 1))
        self.assertIn(dep['frame'], blobs)
        self.assertEqual(wave.roles[dep['sceneId']], 'holdout')

    def test_sentinel_dependencies_come_from_the_bed_pass_run_one(self):
        cell = 'apple-macos-27.0-1x-light-standard-glass0.5/f-impulse-rrect-md__rest'
        row = next(r for r in json.loads((self.out / 'inventory.json').read_text())['entries']
                   if r['cell'] == cell and r['kind'] == 'states')
        header, _ = A.unbundle((self.out / row['path']).read_bytes())
        self.assertEqual(len(header['runs']), 10)
        longs = [r for r in header['runs'] if r['protocol'] == 'long']
        self.assertEqual(len(longs), 3)
        self.assertTrue(all((r['dependencies']['noGlass']['sourcePass'], r['dependencies']['noGlass']['sourceRun'])
                            == (KEY, 1) for r in longs))

    def test_losing_state_is_kept(self):
        cell = 'apple-macos-27.0-1x-light-standard-glass0.5/a-g128-rrect-md-1x__rest'
        row = next(r for r in json.loads((self.out / 'inventory.json').read_text())['entries']
                   if r['cell'] == cell and r['kind'] == 'states')
        header, blobs = A.unbundle((self.out / row['path']).read_bytes())
        self.assertEqual(len({r['frame'] for r in header['runs']}), 2)

    def test_frames_are_the_captured_png_bytes(self):
        cell = 'apple-macos-27.0-1x-light-standard-glass0.5/bp-p1-c4-rrect-md__rest'
        row = next(r for r in json.loads((self.out / 'inventory.json').read_text())['entries']
                   if r['cell'] == cell and r['kind'] == 'states')
        header, blobs = A.unbundle((self.out / row['path']).read_bytes())
        source = self.raw / KEY / 'run-4' / 'apple-macos-27.0-1x-light-standard-glass0.5' / 'bp-p1-c4-rrect-md__rest.png'
        self.assertEqual(header['runs'][3]['frame'], hashlib.sha256(source.read_bytes()).hexdigest())

    def test_refusals(self):
        with self.assertRaisesRegex(ValueError, 'already exists'):
            A.produce(self.raw, self.out, wave=self.wave, passes=PASSES)
        with self.assertRaisesRegex(ValueError, 'outside the repository'):
            A.produce(self.raw, A.REPO / 'archive-x', wave=self.wave, passes=PASSES)
        broken = self.tmp / 'raw-incomplete'
        shutil.copytree(self.raw, broken)
        (broken / KEY / 'run-7' / 'admission.json').unlink()
        with self.assertRaisesRegex(ValueError, 'run 7 is not admitted'):
            A.produce(broken, self.tmp / 'a2', wave=self.wave, passes=PASSES)
        nodump = self.tmp / 'raw-nodump'
        shutil.copytree(self.raw, nodump)
        (nodump / PASSES[0] / 'run-1' / 'admission.json').unlink()
        with self.assertRaisesRegex(ValueError, 'dump step'):
            A.produce(nodump, self.tmp / 'a3', wave=self.wave, passes=PASSES)

    def test_tree_pack_fetch_replay(self):
        A.verify_tree(self.out)
        first = A.pack(self.out, self.tmp / 'release-1')
        second = A.pack(self.out, self.tmp / 'release-2')
        self.assertEqual(first['sha256'], second['sha256'])
        self.assertEqual(first['asset'], f'w42-archive-{first["sha256"]}.tar.zst')
        self.assertLess(first['bytes'], A.LIMIT)
        commands = A.publish_commands(first)
        self.assertIn('--latest=false', commands[0])
        root = A.fetch(A.TAG, first['asset'], first['sha256'], cache=self.tmp / 'cache', source=first['path'])
        a = {p.relative_to(root).as_posix(): A.file_sha(p) for p in root.rglob('*') if p.is_file()}
        b = {p.relative_to(self.out).as_posix(): A.file_sha(p) for p in self.out.rglob('*') if p.is_file()}
        self.assertEqual(a, b)
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            A.fetch(A.TAG, A.asset_name('0' * 64), '0' * 64, cache=self.tmp / 'cache2', source=first['path'])
        result = A.replay(root, wave=self.wave, deny_raw_root=self.raw)
        self.assertTrue(result['identical'])
        holdout = sum(1 for r in json.loads((root / 'inventory.json').read_text())['entries']
                      if r['path'].startswith('holdout/')) // 2
        self.assertEqual(result['cells'], 23 - holdout)
        with self.assertRaises(PermissionError):
            (self.raw / 'logs' / f'{KEY}-driver.txt').read_text()
        with self.assertRaises(PermissionError):
            A.replay(root, wave=self.wave, roles=('holdout',))

    def test_tampering_is_refused(self):
        copy = self.tmp / 'tampered'
        shutil.copytree(self.out, copy)
        (copy / 'stray.png').write_bytes(b'x')
        with self.assertRaisesRegex(ValueError, 'unlisted'):
            A.verify_tree(copy)
        (copy / 'stray.png').unlink()
        inv = json.loads((copy / 'inventory.json').read_text())
        row = next(r for r in inv['entries'] if r['kind'] == 'statistics' and r['path'].startswith('calibration/'))
        stats = json.loads(gzip.decompress((copy / row['path']).read_bytes()))
        key = next(iter(stats['statistics']))
        stats['statistics'][key]['mean'][0] += 1
        raw = gzip.compress(A.encode(stats), mtime=0)
        (copy / row['path']).write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'altered'):
            A.verify_tree(copy)
        row['sha256'] = hashlib.sha256(raw).hexdigest()
        (copy / 'inventory.json').write_bytes(A.encode(inv))
        # A consistent inventory now names a different generation, and replay still refuses.
        with self.assertRaisesRegex(ValueError, 'differ'):
            A.replay(copy, wave=self.wave)


if __name__ == '__main__':
    unittest.main(verbosity=2)
