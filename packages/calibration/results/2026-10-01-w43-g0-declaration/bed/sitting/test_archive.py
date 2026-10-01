#!/usr/bin/env python3.12
"""W43 archive tests (charter clause 5; G0 (d)): producer -> tree check -> deterministic pack ->
fetch by digest from a local copy -> replay with the raw root denied.

The run tree is SYNTHETIC: a small plan over stand_in.py's v8-shaped canonical document and W42's
own scenes file (an opening and a closing bridge pass recapturing W42's two sentinels, a dump
sentinel, a seven-run published bed pass over both schemes), real sitting admissions
(sitting.run_admission over frame_binding and capture_argv), solid-colour PNGs that are not
captures. In the bed pass one cell is unanimous, one carries two states, one is byte-identical to
the background raster every run composited over, and the dark scheme's first cell repeats the
light scheme's first frame, so frames are shared within a cell, across cells, across passes and
across kinds. Needs python3.12 with numpy/PIL and the zstd CLI.

Run: python3.12 -m unittest -v test_archive    (from this directory)"""
import copy
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


A = load('w43_archive_under_test', HERE / 'w43_archive.py')
S = A.sitting()
P = A.pass_spec()
SI = load('w43_stand_in_for_archive', HERE / 'stand_in.py')
L5, L25, D25 = SI.key(1, 'light', '0.5'), SI.key(1, 'light', '0.25'), SI.key(1, 'dark', '0.25')
SIZE = (320, 200)
GREY = (128, 128, 128)
BACKGROUND = 'backgrounds/grey-128@1x.png'
HARNESS_PROTOCOL = {  # what the harness records: literals, not read from sitting.py
    'normal': dict(initialSettleSeconds=1.75, resetInterstitialSeconds=6.0, resetCarriesGlass=False,
                   minIdleSeconds=60.0),
    'long': dict(initialSettleSeconds=8.0, orderSeed=4242, resetInterstitialSeconds=6.0, resetCarriesGlass=False,
                 minIdleSeconds=60.0),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def small_plan():
    """(plan, sources, declaration, picks): the synthetic sitting's declared membership."""
    canonical = SI.encode(SI.scenes_v8_stand_in())
    w42 = (SI.REPO / SI.W42_SCENES).read_bytes()
    cdoc = json.loads(canonical)
    rest = lambda k: [s for s in next(p for p in cdoc['profiles'] if p['key'] == k)['scenes']  # noqa: E731
                      if s.endswith('__rest')]
    light, dark = rest(L25)[:3], rest(D25)[:2]
    sentinels = sorted(f'{c}__rest' for c in SI.W42_SENTINELS)

    def bridge(name):
        return dict(name=name, kind='capture', role='bridge-w42-sentinel', glass=0.5, scale=1, pose='active',
                    source='w42', runs=2, protocol='long', profiles={L5: sentinels})

    plan = dict(schema=P.SCHEMA, sitting='g1a',
                sources=dict(canonical=dict(path=SI.CANONICAL, sha256=sha(canonical)),
                             w42=dict(path=SI.W42_SCENES, sha256=sha(w42))),
                passes=[bridge('open-w42-1x-light-active'),
                        dict(name='dump-0.25-1x-light-active', kind='dump', role='dump-sentinel', glass=0.25, scale=1,
                             pose='active', source='canonical', profile=L25, scenes=light),
                        dict(name='bed-0.25-1x-active', kind='capture', role='bed', glass=0.25, scale=1, pose='active',
                             source='canonical', runs=7, protocol='normal', publish=True,
                             profiles={L25: light, D25: dark}),
                        bridge('close-w42-1x-light-active')])
    sources = dict(canonical=cdoc, w42=json.loads(w42))
    P.validate_plan(plan, sources)
    declaration = dict(sitting='g1a', planSha256=sha(SI.encode(plan)),
                       sources=dict(canonical=sha(canonical), w42=sha(w42)))
    picks = dict(unanimous=f'{L25}/{light[0]}', twoState=f'{L25}/{light[1]}', asBackground=f'{L25}/{light[2]}',
                 sameAsLight=f'{D25}/{dark[0]}', sentinel=f'{L5}/{sentinels[0]}')
    return plan, sources, declaration, picks


PLAN, SOURCES, DECLARATION, PICKS = small_plan()


def colour(cell, run):
    if cell == PICKS['asBackground']:
        return GREY
    if cell == PICKS['sameAsLight']:
        cell = PICKS['unanimous']
    h = hashlib.sha256(cell.encode()).digest()
    rgb = [h[0], h[1], h[2] | 1]
    if cell == PICKS['twoState'] and run in (2, 5):    # a second, losing state
        rgb[0] = (rgb[0] + 1) % 256
    return tuple(rgb)


def manifest(doc, label, protocol):
    profiles = []
    for p in doc['profiles']:
        fixtures = [dict(sceneId=sid, file=f'{p["key"]}/{sid}.png', captureMethod='screencapturekit',
                         materialRendered=True, deterministic=True, width=SIZE[0], height=SIZE[1],
                         hidIdleSeconds=100.0, presentedActive=True, capturedAt='2026-10-01T00:00:00Z',
                         deltaFromBackground=3.0, orderIndex=i)
                    for i, sid in enumerate(p['scenes'])]
        profiles.append(dict(profileKey=p['key'], display=dict(requestedScale=1, actualBackingScale=1,
                                                               pixelSize=list(SIZE), colorSpace='kCGColorSpaceSRGB'),
                             fixtures=fixtures))
    return dict(hardware=dict(osBuild='26A428'), backgrounds={'grey-128@1x': BACKGROUND}, profiles=profiles,
                captureProtocol=dict(runLabel=label, **HARNESS_PROTOCOL[protocol]))


def write_run(root, name, n):
    p = P.pass_of(name, PLAN)
    doc = P.derive_from(PLAN, SOURCES, name, n)
    passdir = root / name
    run = passdir / f'run-{n}'
    run.mkdir(parents=True)
    spec = S.write_doc(passdir, f'scenes-run-{n}.json', doc)
    label = f'w43-{name}-{n}'
    m = manifest(doc, label, p['protocol'])
    for profile in m['profiles']:
        for f in profile['fixtures']:
            path = run / f['file']
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.new('RGB', SIZE, colour(f'{profile["profileKey"]}/{f["sceneId"]}', n)).save(path)
    (run / 'backgrounds').mkdir()
    Image.new('RGB', SIZE, GREY).save(run / BACKGROUND)
    raw = json.dumps(m).encode()
    (run / 'manifest.json').write_bytes(raw)
    argv = S.capture_argv(['open', '-W'], Path('/a.app'), spec, run, 1, label, p['protocol'], P.capture_ids(doc),
                          p['pose'])
    (run / 'launch.json').write_text(json.dumps(dict(argv=argv)) + '\n')
    admission = S.run_admission(p, n, argv, m, sha(raw), len(P.cells(doc)), DECLARATION,
                                S.frame_binding(run, m, doc, 1))
    (run / 'admission.json').write_text(json.dumps(admission) + '\n')
    for f, text in (('attest.read', f'phase=open\npass={name}\nrun={n}\n'), ('driver-idle.txt', 'idle-wait: idle=90\n'),
                    ('watchdog.txt', 'watch: front=dev.vitrea.reference-apple.w39 idle=95\n'),
                    ('producer-capture.out', f'capturing {len(P.cells(doc))} fixtures\n'),
                    ('producer-capture.err', ''), ('attest.open.json', '{}\n'), ('session-before.json', '{}\n')):
        (run / f).write_text(text)


def write_dump(root, name):
    p = P.pass_of(name, PLAN)
    run = root / name / 'run-1'
    (run / 'json').mkdir(parents=True)
    for sid in p['scenes']:
        (run / 'json' / f'{sid}.json').write_text(json.dumps(dict(scene=sid, synthetic=True)) + '\n')
    (run / 'check.json').write_text(json.dumps(dict(departures=[], synthetic=True)) + '\n')
    (run / 'timing.json').write_text('{}\n')
    (run / 'dump.out').write_text('== dump-layers ==\n')
    (run / 'admission.json').write_text(json.dumps(dict(
        schema='w43-dump-admission-1', admitted=True, dry=False, protocol='dump', run=1, scenes=len(p['scenes']),
        departures=0, glass=p['glass'], sitting=DECLARATION['sitting'], planSha256=DECLARATION['planSha256'],
        declaration=DECLARATION, **{'pass': name})) + '\n')


def sitting_tree(root):
    """The synthetic sitting under `root`: every declared run admitted, one quarantine kept, and logs."""
    root = Path(root)
    for p in P.pass_order(PLAN):
        if p['kind'] == 'dump':
            write_dump(root, p['name'])
        else:
            for n in range(1, p['runs'] + 1):
                write_run(root, p['name'], n)
    q = root / 'bed-0.25-1x-active' / 'QUARANTINE-run-3-1'
    (q / L25).mkdir(parents=True)
    (q / 'refusal.txt').write_text('ValueError: watchdog stopped the launch: HID input during the launch\n')
    (q / 'driver-idle.txt').write_text('idle-wait: idle=80\n')
    (q / 'watchdog.txt').write_text('watch: front=com.apple.universalcontrol idle=7.7\n')
    Image.new('RGB', SIZE, (9, 9, 9)).save(q / L25 / 'not-archived.png')
    (root / 'logs').mkdir()
    for f, text in (('orchestrator-status.txt', 'ALL PASSES DONE\n'), ('slider-writes.jsonl', '{"value": 0.25}\n'),
                    ('slider-as-found.json', '{}\n'), ('launcher-chain-1.json', '{"chain": []}\n')):
        (root / 'logs' / f).write_text(text)
    return root


def produce(raw, out, plan=PLAN, sources=SOURCES, declaration=DECLARATION):
    return A.produce(raw, out, plan=plan, sources=sources, declaration=declaration)


def record_of(out, cell):
    inv = json.loads((out / 'inventory.json').read_text())
    row = next(r for r in inv['cells'] if r['cell'] == cell)
    return row, json.loads(gzip.decompress((out / row['path']).read_bytes()))


class Archive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.raw = sitting_tree(cls.tmp / 'raw')
        cls.out = cls.tmp / 'archive'
        cls.inventory = produce(cls.raw, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_each_distinct_frame_is_stored_once(self):
        inv = self.inventory
        # 35 bed captures (7 runs x 5 cells), 8 bridge captures (2 passes x 2 runs x 2 cells), and
        # 11 runs' background rasters: 54 occurrences of 7 distinct byte strings.
        self.assertEqual((inv['frameOccurrences'], inv['distinctFrames']), (54, 7))
        stored = sorted(p.name for p in (self.out / 'frames').iterdir())
        self.assertEqual(stored, [f'{r["sha256"]}.png' for r in inv['frames']])
        self.assertEqual(len(stored), 7)
        for row in inv['frames']:
            self.assertEqual(hashlib.sha256((self.out / row['path']).read_bytes()).hexdigest(), row['sha256'])
        grey = next(r for r in inv['frames'] if r['kinds'] == ['background', 'capture'])
        _, rec = record_of(self.out, PICKS['asBackground'])
        self.assertEqual({m['frame'] for m in rec['runs']}, {grey['sha256']})
        self.assertTrue(all(set(r['backgrounds'].values()) == {grey['sha256']} for r in inv['runs']))

    def test_a_unanimous_cell_costs_one_frame(self):
        row, rec = record_of(self.out, PICKS['unanimous'])
        self.assertEqual((row['runs'], row['frames'], len(rec['statistics'])), (7, 1, 1))
        _, twin = record_of(self.out, PICKS['sameAsLight'])
        self.assertEqual({m['frame'] for m in twin['runs']}, {m['frame'] for m in rec['runs']})   # across cells
        row, rec = record_of(self.out, PICKS['twoState'])
        self.assertEqual((row['runs'], row['frames']), (7, 2))                                     # the losing state kept
        self.assertEqual(sorted(m['run'] for m in rec['runs'] if m['frame'] != rec['runs'][0]['frame']), [2, 5])
        row, rec = record_of(self.out, PICKS['sentinel'])
        self.assertEqual((row['runs'], row['frames']), (4, 1))                                     # across passes
        self.assertEqual(sorted({m['pass'] for m in rec['runs']}),
                         ['close-w42-1x-light-active', 'open-w42-1x-light-active'])
        self.assertEqual({m['protocol'] for m in rec['runs']}, {'long'})

    def test_membership_is_the_runs_own_record(self):
        _, rec = record_of(self.out, PICKS['twoState'])
        run4 = next(m for m in rec['runs'] if m['run'] == 4)
        png = self.raw / 'bed-0.25-1x-active' / 'run-4' / (PICKS['twoState'] + '.png')
        self.assertEqual(run4['frame'], hashlib.sha256(png.read_bytes()).hexdigest())
        manifest_raw = (self.raw / 'bed-0.25-1x-active' / 'run-4' / 'manifest.json').read_bytes()
        self.assertEqual(run4['manifestSha256'], hashlib.sha256(manifest_raw).hexdigest())
        self.assertNotIn('file', run4['attestation'])
        self.assertEqual(run4['attestation']['hidIdleSeconds'], 100.0)

    def test_inventory_names_the_plan_roles_and_sections(self):
        inv = self.inventory
        self.assertEqual((inv['sitting'], inv['planSha256']), ('g1a', DECLARATION['planSha256']))
        self.assertEqual(inv['sources'], DECLARATION['sources'])
        self.assertEqual((inv['declaredCells'], inv['archivedCells']), (7, 7))
        for row in inv['cells']:
            source = SOURCES['w42' if row['cell'].startswith(L5) else 'canonical']
            self.assertEqual(row['path'].split('/')[0], A.role_of(source, row['cell'].split('/', 1)[1]))
        paths = {r['path'] for r in inv['operational']}
        q = 'operational/bed-0.25-1x-active/QUARANTINE-run-3-1/'
        for want in (q + 'refusal.txt', q + 'driver-idle.txt', q + 'watchdog.txt',
                     'operational/bed-0.25-1x-active/run-1/driver-idle.txt',
                     'operational/bed-0.25-1x-active/run-1/watchdog.txt',
                     'operational/bed-0.25-1x-active/run-1/manifest.json',
                     'operational/bed-0.25-1x-active/scenes-run-1.json',
                     'operational/dump-0.25-1x-light-active/run-1/admission.json',
                     'operational/logs/slider-writes.jsonl', 'operational/logs/launcher-chain-1.json'):
            self.assertIn(want, paths)
        self.assertFalse(any(p.endswith('.png') for p in paths))
        self.assertFalse(any('/json/' in p or p.endswith('/check.json') for p in paths))
        self.assertEqual(sorted(r['path'].rsplit('/', 1)[1] for r in inv['dumps']),
                         sorted([f'{s}.json' for s in PLAN['passes'][1]['scenes']] + ['check.json']))
        self.assertEqual(len(inv['runs']), 11)

    def test_refusals(self):
        with self.assertRaisesRegex(ValueError, 'already exists'):
            produce(self.raw, self.out)
        with self.assertRaisesRegex(ValueError, 'outside every checkout'):
            produce(self.raw, A.REPO / 'archive-x')
        for name, damage, message in (
                ('incomplete', lambda t: (t / 'bed-0.25-1x-active' / 'run-7' / 'admission.json').unlink(),
                 'bed-0.25-1x-active run 7 is not admitted'),
                ('no-dump', lambda t: (t / 'dump-0.25-1x-light-active' / 'run-1' / 'admission.json').unlink(),
                 'every dump sentinel'),
                ('frame-moved', lambda t: Image.new('RGB', SIZE, (1, 1, 1)).save(
                    t / 'bed-0.25-1x-active' / 'run-3' / (PICKS['unanimous'] + '.png')),
                 'differ from the ones admission bound')):
            with self.subTest(name=name):
                tree = self.tmp / f'raw-{name}'
                shutil.copytree(self.raw, tree)
                damage(tree)
                with self.assertRaisesRegex(ValueError, message):
                    produce(tree, self.tmp / f'out-{name}')
                self.assertFalse((self.tmp / f'out-{name}').exists())

    def edited(self, name, where, change):
        tree = self.tmp / name
        shutil.copytree(self.raw, tree)
        path = tree / where / 'admission.json'
        a = json.loads(path.read_text())
        change(a)
        path.write_text(json.dumps(a) + '\n')
        return tree

    def test_an_admission_under_another_plan_or_a_rehearsal_refuses(self):
        for name, where, change, message in (
                ('other-plan', 'bed-0.25-1x-active/run-4', lambda a: a.update(planSha256='9' * 64), 'another declaration'),
                ('other-sitting', 'open-w42-1x-light-active/run-2', lambda a: a.update(sitting='g1b'),
                 'another declaration'),
                ('stale-dump', 'dump-0.25-1x-light-active/run-1', lambda a: a.update(planSha256='8' * 64),
                 'another declaration'),
                ('rehearsal', 'bed-0.25-1x-active/run-2', lambda a: a.update(predeclaration=True), 'predeclaration'),
                ('other-cells', 'bed-0.25-1x-active/run-5',
                 lambda a: a['frames'].pop(PICKS['unanimous']), 'not the cells the plan declares')):
            with self.subTest(name=name):
                tree = self.edited(name, where, change)
                with self.assertRaisesRegex(ValueError, message):
                    produce(tree, self.tmp / f'out-{name}')
                self.assertFalse((self.tmp / f'out-{name}').exists())

    def test_membership_that_is_not_the_plan_refuses(self):
        wider = copy.deepcopy(PLAN)
        canonical = SOURCES['canonical']
        extra = [s for s in next(p for p in canonical['profiles'] if p['key'] == D25)['scenes']
                 if s.endswith('__rest')][2]
        wider['passes'][2]['profiles'][D25].append(extra)          # declared, never captured
        with self.assertRaisesRegex(ValueError, 'not the cells the plan declares'):
            produce(self.raw, self.tmp / 'out-wider', plan=wider)
        narrower = copy.deepcopy(PLAN)
        narrower['passes'][2]['profiles'][D25].pop()               # captured, not declared
        with self.assertRaisesRegex(ValueError, 'not the cells the plan declares'):
            produce(self.raw, self.tmp / 'out-narrower', plan=narrower)
        self.assertFalse((self.tmp / 'out-wider').exists() or (self.tmp / 'out-narrower').exists())

    def test_tampering_is_refused(self):
        copy_ = self.tmp / 'tampered'
        shutil.copytree(self.out, copy_)
        (copy_ / 'stray.png').write_bytes(b'x')
        with self.assertRaisesRegex(ValueError, 'unlisted'):
            A.verify_tree(copy_)
        (copy_ / 'stray.png').unlink()
        inv = json.loads((copy_ / 'inventory.json').read_text())
        row = next(r for r in inv['cells'] if r['cell'] == PICKS['unanimous'])
        rec = json.loads(gzip.decompress((copy_ / row['path']).read_bytes()))
        key = next(iter(rec['statistics']))
        rec['statistics'][key]['mean'][0] += 1
        raw = gzip.compress(A.encode(rec), mtime=0)
        (copy_ / row['path']).write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'altered'):
            A.verify_tree(copy_)
        row['sha256'] = hashlib.sha256(raw).hexdigest()
        (copy_ / 'inventory.json').write_bytes(A.encode(inv))
        with self.assertRaisesRegex(ValueError, 'differ'):           # a consistent inventory still refuses
            A.replay(copy_)

    def test_orphan_missing_and_misnamed_frames_are_refused(self):
        def variant(name, change):
            tree = self.tmp / name
            shutil.copytree(self.out, tree)
            inv = json.loads((tree / 'inventory.json').read_text())
            change(tree, inv)
            (tree / 'inventory.json').write_bytes(A.encode(inv))
            return tree

        def orphan(tree, inv):
            buf = tree / 'frames' / 'tmp.png'
            Image.new('RGB', SIZE, (3, 4, 5)).save(buf)
            digest = hashlib.sha256(buf.read_bytes()).hexdigest()
            buf.rename(tree / 'frames' / f'{digest}.png')
            inv['frames'].append(dict(path=f'frames/{digest}.png', sha256=digest, bytes=1, kinds=['capture']))

        def missing(tree, inv):
            _, rec = record_of(self.out, PICKS['sentinel'])
            gone = rec['runs'][0]['frame']
            (tree / 'frames' / f'{gone}.png').unlink()
            inv['frames'] = [r for r in inv['frames'] if r['sha256'] != gone]

        def misnamed(tree, inv):
            row = inv['frames'][0]
            wrong = '0' * 64
            (tree / row['path']).rename(tree / f'frames/{wrong}.png')
            row['path'] = f'frames/{wrong}.png'

        with self.assertRaisesRegex(ValueError, 'orphans'):
            A.replay(variant('orphan', orphan))
        with self.assertRaisesRegex(ValueError, 'does not store'):
            A.replay(variant('missing', missing))
        with self.assertRaisesRegex(ValueError, 'under its own digest'):
            A.verify_tree(variant('misnamed', misnamed))


class Replay(unittest.TestCase):
    """Its own raw root, because the deny hook holds for the rest of the process."""

    def test_tree_pack_fetch_replay_with_the_raw_root_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            raw = sitting_tree(tmp / 'raw-replay')
            out = tmp / 'archive'
            produce(raw, out)
            A.verify_tree(out)
            first = A.pack(out, tmp / 'release-1')
            second = A.pack(out, tmp / 'release-2')
            self.assertEqual(first['sha256'], second['sha256'])
            self.assertEqual(first['asset'], f'w43-archive-g1a-{first["sha256"]}.tar.zst')
            self.assertEqual(first['tag'], 'w43-archive-g1a')
            self.assertLess(first['bytes'], A.LIMIT)
            commands = A.publish_commands(first)
            self.assertIn('--latest=false', commands[0])
            self.assertEqual(commands[0][3], 'w43-archive-g1a')
            root = A.fetch('g1a', first['asset'], first['sha256'], cache=tmp / 'cache', source=first['path'])
            a = {p.relative_to(root).as_posix(): A.file_sha(p) for p in root.rglob('*') if p.is_file()}
            b = {p.relative_to(out).as_posix(): A.file_sha(p) for p in out.rglob('*') if p.is_file()}
            self.assertEqual(a, b)
            with self.assertRaisesRegex(ValueError, 'digest mismatch'):
                A.fetch('g1a', A.asset_name('g1a', '0' * 64), '0' * 64, cache=tmp / 'cache2', source=first['path'])
            with self.assertRaisesRegex(ValueError, 'sitting and the expected digest'):
                A.fetch('g1b', first['asset'], first['sha256'], cache=tmp / 'cache3', source=first['path'])
            result = A.replay(root, deny_raw_root=raw)
            self.assertTrue(result['identical'])
            self.assertEqual((result['cells'], result['frames']), (7, 7))
            with self.assertRaises(PermissionError):
                (raw / 'logs' / 'orchestrator-status.txt').read_text()

            # The negative control: an analyse that reaches for the raw root inside replay is refused.
            def peeking(png):
                (raw / 'bed-0.25-1x-active' / 'run-1' / 'manifest.json').read_bytes()
                return A.default_analyse(png)

            with self.assertRaises(PermissionError):
                A.replay(root, analyse=peeking, deny_raw_root=raw)


if __name__ == '__main__':
    unittest.main(verbosity=2)
