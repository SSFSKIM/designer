#!/usr/bin/env python3.12
"""W42 archive tests (charter clause 5): producer -> tree check -> deterministic pack -> fetch by
digest from a local copy -> replay through bed/wave.py's Reader with the raw root denied.

The run tree is SYNTHETIC: real declaration (bed/scenes-w42-body.json, bed.json, pins.json),
real sitting admissions (sitting.run_admission over manifests shaped like the harness's, with
the per-fixture pixel statistics the harness records), solid-colour PNGs that are not captures.
One cell carries two states across its runs, so a losing state is present. Needs python3.12
with numpy/PIL and the zstd CLI.

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
# What the harness records per fixture that reads the pixels (Manifest.swift FixtureEntry).
PIXEL_STATISTICS = ('deltaFromBackground', 'chromaShift', 'repeatNoise', 'identicalToBackground',
                    'settleIterations', 'settleSeconds')
# The harness's own run summary (main.swift, `for c in caveats { print("CAVEAT: \(c)") }`), counted
# over every fixture, H included, with no scene id in it (the verification round's finding 2).
CAVEAT = ('CAVEAT: 1 of 23 fixtures are PIXEL-IDENTICAL to their own background raster: the component '
          'contributed no pixels whatsoever. These carry zero information about shape or material and exist '
          'only to exercise the diff pipeline end to end.')
STAGING = '.staging-6F1C2B0E-2D4A-4E4B-9B8F-0C1D2E3F4A5B'


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
    m['caveats'] = ['0 of 23 fixtures are PIXEL-IDENTICAL to their own background raster']
    log = [f'capturing {sum(len(q["fixtures"]) for q in m["profiles"])} fixtures via screencapturekit at 1.0x']
    for profile in m['profiles']:
        profile['caveats'] = ['a profile-scoped caveat']
        for i, f in enumerate(profile['fixtures']):
            level = colour(f['sceneId'], n)[0]
            f.update(deltaFromBackground=level / 3, chromaShift=-0.5, repeatNoise=0.25, identicalToBackground=False,
                     settleIterations=2, settleSeconds=1.5, orderIndex=i)
            path = run / f['file']
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.new('RGB', (320, 200), colour(f['sceneId'], n)).save(path)
            log.append(f'  [{i + 1}/{len(profile["fixtures"])}] {profile["profileKey"]}/{f["sceneId"]} NOISY({level / 7:.3f})')
    raw = json.dumps(m).encode()
    (run / 'manifest.json').write_bytes(raw)
    log += [f'manifest → {run}/manifest.json', CAVEAT]
    (run / 'producer-capture.out').write_text('\n'.join(log) + '\n')
    for name in ('attest.open.json', 'attest.close.json', 'session-before.json', 'driver-idle.log',
                 'producer-capture.err'):
        (run / name).write_text('{}\n' if name.endswith('.json') else f'{name} of {label}\n')
    (run / 'backgrounds').mkdir()
    Image.new('RGB', (320, 200), (1, 2, 3)).save(run / 'backgrounds' / 'grey-128@1x.png')
    argv = S.capture_argv(['open', '-W'], Path('/a.app'), Path('/s.json'), run, 1, label, protocol,
                          sorted(s['id'] for s in doc['scenes']), pose)
    (run / 'launch.json').write_text(json.dumps(dict(argv=argv)) + '\n')
    admission = S.run_admission(p, n, argv, m, hashlib.sha256(raw).hexdigest(),
                                sum(len(q['scenes']) for q in doc['profiles']), T.DECLARATION,
                                S.frame_binding(run, m, doc, 1))
    (run / 'admission.json').write_text(json.dumps(admission) + '\n')
    (root / p['name'] / f'scenes-run-{n}.json').write_text(json.dumps(doc) + '\n')


def write_dump(root, p):
    run = root / p['name'] / 'run-1'
    (run / 'json').mkdir(parents=True)
    for sid in P.dump_ids(p['key']):
        (run / 'json' / f'{sid}.json').write_text(json.dumps(dict(scene=sid, synthetic=True)) + '\n')
    (run / 'check.json').write_text(json.dumps(dict(departures=0, synthetic=True)) + '\n')
    (run / 'admission.json').write_text(json.dumps(dict(admitted=True, protocol='dump', run=1,
                                                         scenesSha256=T.DECLARATION['scenesSha256'],
                                                         splitSha256=T.DECLARATION['splitSha256'],
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
    # The harness's staging directory, left behind by an interrupted capture: its manifest carries
    # every fixture's pixel statistics, H's included (the verification round's finding 5).
    (q / STAGING).mkdir()
    shutil.copyfile(root / KEY / 'run-3' / 'manifest.json', q / STAGING / 'manifest.json')
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
        self.assertEqual(len(inv['holdoutOperational']), 31)   # manifest + two capture logs, 10 runs; the staged one
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

    def edited(self, name, edit):
        """A copy of the raw tree with one admission edited in place."""
        tree = self.tmp / name
        shutil.copytree(self.raw, tree)
        path = tree / edit[0] / 'admission.json'
        a = json.loads(path.read_text())
        edit[1](a)
        path.write_text(json.dumps(a) + '\n')
        return tree

    def test_b_m1_an_admission_under_another_declaration_refuses(self):
        for name, where, change, message in (
                ('stale-capture', f'{KEY}/run-4', lambda a: a.update(splitSha256='9' * 64), 'another declaration'),
                ('stale-dump', f'{PASSES[0]}/run-1', lambda a: a.update(scenesSha256='8' * 64), 'another declaration'),
                ('rehearsal', f'{KEY}/run-2', lambda a: a.update(predeclaration=True), 'predeclaration')):
            with self.subTest(name=name):
                tree = self.edited(name, (where, change))
                with self.assertRaisesRegex(ValueError, message):
                    A.produce(tree, self.tmp / f'out-{name}', wave=self.wave, passes=PASSES)
                self.assertFalse((self.tmp / f'out-{name}').exists())

    def test_b_m1_a_declared_cell_left_uncaptured_refuses(self):
        import copy as copy_
        wider = copy_.copy(self.wave)
        wider.bed = copy_.deepcopy(self.wave.bed)
        wider.bed['passes'][KEY]['cells'].append('h-p1-c24-rrect-112')   # declared, never captured at 1x
        with self.assertRaisesRegex(ValueError, r'1 declared cell\(s\) were never captured'):
            A.produce(self.raw, self.tmp / 'out-uncaptured', wave=wider, passes=PASSES)
        self.assertFalse((self.tmp / 'out-uncaptured').exists())

    def test_b2_a_frame_changed_after_admission_refuses(self):
        for cell in ('bp-p1-c4-rrect-md__rest', 'h-g232-rrect-md__rest'):     # an open frame and a held one
            with self.subTest(cell=cell):
                tree = self.tmp / f'raw-{cell}'
                shutil.copytree(self.raw, tree)
                png = tree / KEY / 'run-3' / 'apple-macos-27.0-1x-light-standard-glass0.5' / f'{cell}.png'
                Image.new('RGB', (320, 200), (1, 1, 1)).save(png)
                with self.assertRaisesRegex(ValueError, 'differ from the ones admission bound'):
                    A.produce(tree, self.tmp / f'out-{cell}', wave=self.wave, passes=PASSES)

    def test_b_m2_operational_copies_carry_no_holdout_pixel_statistic(self):
        inv = json.loads((self.out / 'inventory.json').read_text())
        held = {s for s, r in self.wave.roles.items() if r == 'holdout'}
        manifests = [r['path'] for r in inv['operational'] if r['path'].endswith('/manifest.json')]
        self.assertEqual(len(manifests), 11)              # 7 bed runs + 3 sentinel runs + the staged one
        seen_held = seen_open = 0
        for rel in manifests:
            public = json.loads((self.out / rel).read_text())
            self.assertNotIn('caveats', public)
            for profile in public['profiles']:
                self.assertNotIn('caveats', profile)
                for f in profile['fixtures']:
                    if f['sceneId'] in held:
                        seen_held += 1
                        self.assertLessEqual(set(f), set(A.H_ATTESTATION))
                        self.assertFalse(set(f) & set(PIXEL_STATISTICS))
                    else:
                        seen_open += 1
                        self.assertLessEqual(set(PIXEL_STATISTICS), set(f))   # calibration keeps them
        raw_held = sum(1 for path in list((self.raw / KEY).glob('run-*/manifest.json'))
                       + list((self.raw / KEY).glob(f'QUARANTINE-*/{STAGING}/manifest.json'))
                       for p in json.loads(path.read_text())['profiles'] for f in p['fixtures'] if f['sceneId'] in held)
        self.assertEqual(seen_held, raw_held)
        self.assertGreater(seen_held, 0)
        self.assertGreater(seen_open, 0)
        for rel in (r['path'] for r in inv['operational'] if r['path'].endswith('/producer-capture.out')):
            text = (self.out / rel).read_text()
            self.assertNotIn('PIXEL-IDENTICAL', text)                          # the run summary is withheld
            for line in text.splitlines():
                if any(f'/{sid}' in line for sid in held):
                    self.assertNotIn('NOISY', line)
                    self.assertIn('withheld', line)
        guarded = {r['path'] for r in inv['holdoutOperational']}
        self.assertTrue(all(p.startswith('holdout/operational/') for p in guarded))
        self.assertIn(f'holdout/operational/{KEY}/run-1/manifest.json', guarded)
        self.assertIn(f'holdout/operational/{KEY}/run-1/producer-capture.out', guarded)
        self.assertIn(f'holdout/operational/{KEY}/QUARANTINE-run-3-1/{STAGING}/manifest.json', guarded)
        self.assertIn(CAVEAT.encode(), (self.out / f'holdout/operational/{KEY}/run-1/producer-capture.out').read_bytes())

    def test_verification_round_the_real_caveat_line_does_not_survive_redaction(self):
        held = {s for s, r in self.wave.roles.items() if r == 'holdout'}
        log = ('capturing 23 fixtures via screencapturekit at 1.0x (interleaved)\n'
               '  [1/23] apple-macos-27.0-1x-light-standard-glass0.5/h-g232-rrect-md__rest byte-stable EMPTY(==background)\n'
               '  [2/23] apple-macos-27.0-1x-light-standard-glass0.5/a-g128-rrect-md-1x__rest byte-stable\n'
               'manifest → /raw/1x-light-active/run-1/manifest.json\n' + CAVEAT + '\n').encode()
        public = A.public_log(log, held).decode()
        self.assertNotIn('PIXEL-IDENTICAL', public)
        self.assertNotIn('1 of 23', public)
        self.assertNotIn('EMPTY', public)
        self.assertIn('a-g128-rrect-md-1x__rest byte-stable', public)            # calibration diagnostics stay
        self.assertIn('manifest →', public)

    def test_verification_round_a_staged_manifest_is_redacted_and_guarded(self):
        inv = json.loads((self.out / 'inventory.json').read_text())
        held = {s for s, r in self.wave.roles.items() if r == 'holdout'}
        rel = f'operational/{KEY}/QUARANTINE-run-3-1/{STAGING}/manifest.json'
        self.assertIn(rel, {r['path'] for r in inv['operational']})
        public = json.loads((self.out / rel).read_text())
        fixtures = [f for p in public['profiles'] for f in p['fixtures'] if f['sceneId'] in held]
        self.assertTrue(fixtures)
        self.assertFalse(any(set(f) & set(PIXEL_STATISTICS) for f in fixtures))

    def test_b_m2_the_whole_manifest_opens_only_inside_the_receipt(self):
        W = A.wave_module()
        rel = f'holdout/operational/{KEY}/run-1/manifest.json'
        with self.assertRaises(PermissionError):
            self.wave.reader(self.out).read_holdout_operational(rel)
        generation = A.file_sha(self.out / 'inventory.json')
        receipt = W.Receipt(self.tmp / 'scratch-receipt.jsonl', dict(
            scenes=self.wave.scenes_sha, split=self.wave.split_sha, generation=[generation],
            instrument='synthetic', closure='synthetic', candidate='synthetic'))
        with receipt.expose() as token:
            reader = self.wave.reader(self.out, ('holdout',), token)
            whole = reader.read_holdout_operational(rel)
        self.assertEqual(whole, (self.raw / KEY / 'run-1' / 'manifest.json').read_bytes())
        full = json.loads(whole)
        held = [f for p in full['profiles'] for f in p['fixtures'] if self.wave.roles[f['sceneId']] == 'holdout']
        self.assertTrue(all('deltaFromBackground' in f for f in held))
        with self.assertRaises(PermissionError):                               # the token is dead after it
            reader.read_holdout_operational(rel)

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
