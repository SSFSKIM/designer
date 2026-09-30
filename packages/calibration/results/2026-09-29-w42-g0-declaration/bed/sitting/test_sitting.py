#!/usr/bin/env python3.12
"""W42 sitting driver tests (charter clause 4). Nothing is captured and nothing is launched:
the machine recorder, session reader, harness and launcher are stubs; pass-spec.py, the bed
files and dumpcheck.py are the real ones. The dump-step tests feed memo D's own dump files
(~/vitrea-w42/grounding/dumps, hashed in the grounding's scratch-sha256.txt) relabelled with
W42 scene ids, and are skipped where that scratch is absent.

The pre-launch declaration check (B-M1) and the orchestrator run for real inside `Mirror`, a
throwaway Git checkout holding the bed, its tools and a declaration.json at their real relative
paths; the other tests hold the check's answer fixed (`DECLARATION`).

Run: python3.12 -m unittest -v test_sitting    (from this directory)"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
BED_DIR = HERE.parent
REPO = HERE.parents[5]
W34_MACHINE = REPO / 'packages/calibration/results/2026-09-23-w34-g0-contour-bed/machine-side-built.json'
MEMO_D = Path('/Users/new/vitrea-w42/grounding/dumps/runs')
PIN = dict(path=str(Path('/tmp/w42-test-side/VitreaReference.app').resolve()), binarySha256='b' * 64,
           cdhash='c' * 40, buildVersion='LC_BUILD_VERSION stub')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S = load('w42_sitting_under_test', HERE / 'sitting.py')
S._PIN = dict(PIN)
P = S.pass_spec()
SPEC, BED = P.load()
PINS = json.loads((BED_DIR / 'pins.json').read_text())
# What pinned_declaration answers for the pinned bed, held fixed outside the Mirror tests.
DECLARATION = dict(scenesSha256=PINS['scenes-w42-body.json'], splitSha256=PINS['bed.json'], head='test-head',
                   declarationSha256='d' * 64)


def machine(scale=2, **changes):
    m = json.loads(W34_MACHINE.read_text())
    m['foreignProcessCount'], m['foreignProcesses'] = 0, []
    m['side'].update(path=PIN['path'], binarySha256=PIN['binarySha256'], buildVersion=dict(stdout=PIN['buildVersion']))
    m['side']['signature']['stderr'] = f'CDHash={PIN["cdhash"]}\n'
    if scale == 1:
        m['display']['stdout'] = m['display']['stdout'].replace(
            'scaling:on <-- current mode', 'scaling:on').replace(
            'mode 69: res:2560x1440 hz:60 color_depth:4', 'mode 69: res:2560x1440 hz:60 color_depth:4 <-- current mode')
    for key, value in changes.items():
        if key == 'foreign':
            m['foreignProcessCount'] = value
        else:
            m['settings'][key]['stdout'] = value
    return m


HARNESS_PROTOCOL = {  # what the harness records: literals, not read from sitting.py
    'normal': dict(initialSettleSeconds=1.75, resetInterstitialSeconds=6.0, resetCarriesGlass=False,
                   minIdleSeconds=60.0),
    'long': dict(initialSettleSeconds=8.0, orderSeed=4242, resetInterstitialSeconds=6.0, resetCarriesGlass=False,
                 minIdleSeconds=60.0),
}


def manifest(doc, pose, scale, label, protocol='normal', idle=100.0, origin_shift=None):
    canvas = doc['canvas']
    scenes = {s['id']: s for s in doc['scenes']}
    size = [canvas['width'] * scale, canvas['height'] * scale]
    frame = [1120.0, 580.0, float(canvas['width']), float(canvas['height'])]
    profiles = []
    for p in doc['profiles']:
        fixtures = []
        for sid in p['scenes']:
            comp = doc['components'][scenes[sid]['component']]
            paths = [] if comp['kind'] == 'none' else [dict(
                kind=comp['kind'], frameOrigin=S.declared_origin(comp, canvas), rect=[0, 0, *comp['size']],
                opaque=False, elements=[])]
            if origin_shift and sid == origin_shift and paths:
                paths[0]['frameOrigin'] = [(canvas['width'] - comp['size'][0]) / 2,
                                           (canvas['height'] - comp['size'][1]) / 2]
            active = pose == 'active'
            fixtures.append(dict(sceneId=sid, file=f'{p["key"]}/{sid}.png', captureMethod='screencapturekit',
                                 materialRendered=True, deterministic=True, width=size[0], height=size[1],
                                 hidIdleSeconds=idle if sid == sorted(p['scenes'])[0] else 100.0,
                                 presentedActive=active, capturedAt='2026-10-01T00:00:00Z',
                                 presentation=dict(observedPose='active' if active else 'inactive',
                                                   isKeyWindow=active, appIsActive=active),
                                 windowFrame=dict(coordinateSpace='appkit-global-bottom-left', requested=list(frame),
                                                  actual=list(frame), backingScaleFactor=float(scale)),
                                 suppliedPaths=paths))
        profiles.append(dict(profileKey=p['key'], display=dict(requestedScale=scale, actualBackingScale=scale,
                                                               pixelSize=size, colorSpace='kCGColorSpaceSRGB'),
                             fixtures=fixtures))
    return dict(hardware=dict(osBuild='26A428'), profiles=profiles,
                captureProtocol=dict(runLabel=label, **HARNESS_PROTOCOL[protocol], hidIdleSecondsAtStart=100.0,
                                     hidIdleSecondsAtEnd=100.0))


STUB_LAUNCHER = r'''
import json, os, shutil, sys
from pathlib import Path
args = sys.argv[1:]
env = dict(a.split('=', 1) for i, a in enumerate(args) if i and args[i - 1] == '--env')
with open(os.environ['STUB_CALLS'], 'a') as f:
    f.write(json.dumps(args) + '\n')
mode = os.environ['STUB_MODE']
if 'dump-layers' in args:
    out = Path(args[args.index('--out') + 1]); out.mkdir(parents=True)
    ids = args[args.index('--scenes') + 1].split(',')
    source = json.loads(Path(os.environ['STUB_DUMPS']).read_text())
    for sid in ids:
        d = json.loads(Path(source[sid]).read_text())
        d['scene'] = sid
        if mode == 'depart' and sid == ids[0]:
            def walk(n):
                if isinstance(n, dict):
                    for flt in n.get('filters') or []:
                        if 'inputBlurRadius' in (flt.get('inputs') or {}):
                            flt['inputs']['inputBlurRadius'] = 6
                    for s in n.get('sublayers') or []: walk(s)
            walk(d['view']['layer'])
        (out / (sid + '.json')).write_text(json.dumps(d))
    sys.exit(0)
fixtures = Path(env['VITREA_FIXTURES'])
out, err = Path(args[args.index('--stdout') + 1]), Path(args[args.index('--stderr') + 1])
n = len(args[args.index('--scenes') + 1].split(','))
out.write_text(f'capturing {n} fixtures via screencapturekit\n')
if mode == 'block':
    # A capture that does not return: a stand-in native app, detached as LaunchServices would
    # start it, and this launcher waiting on it like `open -W`.
    import subprocess, time
    app = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(900)', os.environ['STUB_NATIVE']],
                           start_new_session=True)
    Path(os.environ['STUB_PIDS']).write_text(json.dumps(dict(launcher=os.getpid(), app=app.pid)))
    time.sleep(900)
    sys.exit(0)
if mode == 'tcc':
    err.write_text('error: ScreenCaptureKit is unavailable\n\nThis is the Screen Recording (TCC) gate.\n')
else:
    if os.environ.get('STUB_AUTO') == '1':
        # The manifest of exactly the document this run was given, shaped as the suite shapes it.
        sys.path.insert(0, os.environ['STUB_TEST_DIR'])
        import test_sitting as T
        doc = json.loads(Path(env['VITREA_SCENES']).read_text())
        label = args[args.index('--run-label') + 1]
        manifest = T.manifest(doc, 'receded' if '--inactive' in args else 'active', int(env['VITREA_SCALE']), label,
                              'long' if '--order-seed' in args else 'normal')
        edit = os.environ.get('STUB_EDIT_SCENES')
        if edit and not Path(edit + '.edited').exists():        # once, after the first capture
            T.one_byte_edit(Path(edit), 'grey-128')
            Path(edit + '.edited').write_text('')
    else:
        manifest = json.loads(Path(os.environ['STUB_MANIFEST']).read_text())
    (fixtures / 'manifest.json').write_text(json.dumps(manifest))
    if mode != 'no-png':
        from PIL import Image
        for p in manifest['profiles']:
            for f in p['fixtures']:
                path = fixtures / f['file']
                path.parent.mkdir(parents=True, exist_ok=True)
                size = (f['width'] // 2, f['height']) if mode == 'bad-png' else (f['width'], f['height'])
                Image.new('RGB', size, (len(f['sceneId']) % 256, 7, 9)).save(path)
    err.write_text('')
'''

STUB_SESSION = r'''
import json, os
print(json.dumps(dict(idleSeconds=float(os.environ.get('STUB_IDLE', '100')), screenLocked=False,
                      windowOwners=['Dock|20', 'Window Server|24'] + (['universalAccessAuthWarn|0']
                      if os.environ.get('STUB_PROMPT') else []))))
'''

STUB_HARNESS = r'''
import json, os, sys
with open(os.environ['STUB_CALLS'], 'a') as f:
    f.write(json.dumps(['harness'] + sys.argv[1:]) + '\n')
'''


class Stubs:
    def __init__(self, tmp, scale=2, **machine_changes):
        self.tmp = Path(tmp)
        (self.tmp / 'machine.json').write_text(json.dumps(machine(scale, **machine_changes)))
        for name, text in [('launcher.py', STUB_LAUNCHER), ('session.py', STUB_SESSION), ('harness.py', STUB_HARNESS),
                           ('recorder.py', f'import pathlib\nprint(pathlib.Path({str(self.tmp / "machine.json")!r}).read_text())\n')]:
            (self.tmp / name).write_text(text)
        self.root = self.tmp / 'root'
        self.calls = self.tmp / 'calls.jsonl'
        py = sys.executable
        self.env = dict(VITREA_SITTING_DIR=str(self.root), VITREA_APP=PIN['path'],
                        VITREA_RECORD_MACHINE=f'{py} {self.tmp / "recorder.py"}',
                        VITREA_SESSION_READER=f'{py} {self.tmp / "session.py"}',
                        VITREA_HARNESS=f'{py} {self.tmp / "harness.py"}',
                        VITREA_LAUNCHER=f'{py} {self.tmp / "launcher.py"}',
                        VITREA_IDLE_LIMIT='0', VITREA_IDLE_POLL='0', W42_ORCHESTRATED='1',
                        STUB_CALLS=str(self.calls), STUB_MODE='manifest', STUB_MANIFEST=str(self.tmp / 'manifest.json'),
                        STUB_DUMPS=str(self.tmp / 'dumps.json'))

    def admit_before(self, name):
        """Fake admissions for every pass ranked before `name` (the order gate reads only these)."""
        order = P.pass_order(BED)
        target = next(p for p in order if p['name'] == name)
        for p in order:
            if p['rank'] >= target['rank']:
                break
            for n in range(1, p['runs'] + 1):
                d = self.root / p['name'] / f'run-{n}'
                d.mkdir(parents=True, exist_ok=True)
                (d / 'admission.json').write_text(json.dumps(
                    {'admitted': True, 'pass': p['name'], 'run': n, 'protocol': S.protocol_of_pass(p),
                     'scenesSha256': DECLARATION['scenesSha256'], 'splitSha256': DECLARATION['splitSha256']}))

    def run(self, *argv, declaration=None, **extra):
        env = {**self.env, **extra}
        with mock.patch.dict(os.environ, env, clear=False):
            for k in ('DRY', 'STUB_PROMPT', 'W42_PREDECLARATION'):
                if k not in extra:
                    os.environ.pop(k, None)
            answer = dict(declaration or DECLARATION)
            if os.environ.get('W42_PREDECLARATION') == '1':
                answer['predeclaration'] = True
            with mock.patch.object(S, 'REPO', Path('/nonexistent-repo')), \
                    mock.patch.object(S, 'MAIN', Path('/nonexistent-main')), \
                    mock.patch.object(S, 'pinned_declaration', lambda predeclaration=False: dict(answer)):
                return S.main(list(argv))

    def calls_made(self):
        return [json.loads(l) for l in self.calls.read_text().splitlines()] if self.calls.exists() else []


class Plan(unittest.TestCase):
    def test_plan_executes_nothing_and_counts_the_bed(self):
        with mock.patch('subprocess.run', side_effect=AssertionError('launched')), \
                mock.patch('subprocess.check_output', side_effect=AssertionError('read')), \
                mock.patch('subprocess.Popen', side_effect=AssertionError('spawned')):
            value = S.dry_plan()
        t = value['totals']
        # The charter's v2.1 bed plus the s = 32 receded rows the parent ruled from the gate
        # rehearsal, then the cells ruled from the instrument stream's separation proof (depth 34,
        # corner and end, the dark 16 / 112 twins) and ruling 3's active guard rows, less the
        # active cells no active reader reads (b1): 2x 87 / 92 / 101 / 107, 1x 14 / 16 / 14 / 16.
        self.assertEqual((t['dumpLaunches'], t['dumpScenes'], t['captureLaunches']), (8, 447, 80))
        self.assertEqual((t['glass'], t['references'], t['sentinels'], t['captures']), (3129, 264, 48, 3441))
        names = [p['name'] for p in value['passes']]
        self.assertEqual(names[:8], [f'dump-{s}x-{c}-{p}' for s in (2, 1) for c in ('light', 'dark')
                                     for p in ('active', 'receded')])
        self.assertEqual(names[8:12], ['2x-light-active', '2x-light-receded', '2x-dark-active', '2x-dark-receded'])
        self.assertTrue(all(n.endswith('-sentinel') for n in names[12:16]))
        self.assertEqual([p['mode'] for p in value['passes']], ['68'] * 4 + ['69'] * 4 + ['68'] * 8 + ['69'] * 8)
        for p in value['passes']:
            for r in p['runs']:
                self.assertNotIn('--dry-run', r['argv'])

    def test_per_pass_counts_match_bed_json(self):
        for key, c in BED['counts'].items():
            docs = [P.derive(key, n) for n in range(1, 8)]
            self.assertEqual(len(docs[0]['scenes']), c['glass'] + c['references'], key)
            self.assertTrue(all(len(d['scenes']) == c['glass'] for d in docs[1:]), key)

    def test_references_only_in_run_one_and_roles_preserved(self):
        roles = {sid: r for r, ids in SPEC['split'].items() for sid in ids}
        for key in BED['passes']:
            one, two = P.derive(key, 1), P.derive(key, 2)
            self.assertTrue(any(s['id'].startswith('ref-') for s in one['scenes']))
            self.assertFalse(any(s['id'].startswith('ref-') for s in two['scenes']))
            for doc in (one, two, P.derive(key, 1, sentinel=True)):
                ids = {s['id'] for s in doc['scenes']}
                self.assertEqual(len(doc['profiles']), 1)
                listed = [s for r in P.SPLIT_ROLES for s in doc['split'][r]]
                self.assertEqual(sorted(listed), sorted(ids))
                for r in P.SPLIT_ROLES:
                    self.assertTrue(all(roles[s] == r for s in doc['split'][r]))
                self.assertTrue(set(doc['backgrounds']) == {s['background'] for s in doc['scenes']})

    def test_sentinel_argv_is_the_long_protocol(self):
        doc = P.derive('2x-dark-receded', 2, sentinel=True)
        argv = S.capture_argv(['open', '-W'], Path('/a.app'), Path('/s.json'), Path('/r'), 2, 'l', 'long',
                              [s['id'] for s in doc['scenes']], 'receded')
        self.assertEqual(S.launch_protocol(argv), 'long')
        self.assertIn('4242', argv)
        self.assertEqual(argv[-1], '--inactive')
        self.assertEqual(sorted(s['id'] for s in doc['scenes']),
                         sorted(f'{c}__inactive' for c in BED['sentinels']))


class Gates(unittest.TestCase):
    def test_every_failing_gate_is_named_in_one_refusal(self):
        m = machine(2, reduceTransparency='1', foreign=3)
        m['side']['binarySha256'] = 'd' * 64
        with mock.patch.object(S, '_PIN', dict(PIN)):
            with self.assertRaises(ValueError) as caught:
                S.validate_machine(m, 1)
        text = str(caught.exception)
        for fragment in ('policy/slider', 'display mode', 'side bundle identity', 'foreign capture'):
            self.assertIn(fragment, text)

    def test_idle_wait_is_bounded_logged_and_stops_on_a_prompt(self):
        reads = iter([dict(idleSeconds=10, screenLocked=False, windowOwners=[]),
                      dict(idleSeconds=80, screenLocked=False, windowOwners=[])])
        lines, clock = [], iter(range(100))
        got = S.wait_for_idle(lambda: next(reads), lines.append, need=75, limit=50, poll=0,
                              sleep=lambda s: None, clock=lambda: next(clock))
        self.assertEqual(got['idleSeconds'], 80)
        self.assertEqual(len(lines), 2)
        with self.assertRaises(ValueError):
            S.wait_for_idle(lambda: dict(idleSeconds=1, screenLocked=False, windowOwners=[]), lines.append,
                            limit=3, poll=0, sleep=lambda s: None, clock=iter(range(100)).__next__)
        with self.assertRaisesRegex(ValueError, 'prompt'):
            S.wait_for_idle(lambda: dict(idleSeconds=999, screenLocked=False,
                                         windowOwners=['universalAccessAuthWarn|0']), lines.append)

    def test_outputs_never_inside_a_checkout_or_documents(self):
        for bad in (REPO / 'x', Path.home() / 'Documents' / 'w42'):
            with self.assertRaises(ValueError):
                S.outside_repository(bad)
        S.outside_repository('/tmp/w42-ok')

    def test_dry_env_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            Stubs(tmp).run('capture', '1x-light-active', DRY='1')


def dumps_for(ids, tag):
    """memo D's dump of the same shape in the same endpoint, per W42 scene id."""
    base = {'capsule-button': 'capsule-button', 'rrect-md': 'rrect-md', 'rrect-lg': 'rrect-lg',
            'rrect-ml': 'rrect-ml', 'rrect-64': 'rrect-64', 'rrect-80': 'rrect-80'}
    comps = {s['id']: s['component'] for s in SPEC['scenes']}
    out = {}
    for sid in ids:
        shape = next(b for b in sorted(base, key=len, reverse=True) if comps[sid].startswith(b))
        out[sid] = str(MEMO_D / tag / 'json' / f'dark-solid__{shape}__rest.json')
    return out


@unittest.skipUnless(MEMO_D.is_dir(), "memo D's scratch dumps are absent on this machine")
class DumpStep(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.st = Stubs(self._tmp.name, scale=1)
        self.st.admit_before('dump-1x-light-active')
        ids = P.dump_ids('1x-light-active')
        (self.st.tmp / 'dumps.json').write_text(json.dumps(dumps_for(ids, '1x-light-active')))

    def tearDown(self):
        self._tmp.cleanup()

    def test_a_conforming_dump_is_admitted(self):
        self.st.run('dump', '1x-light-active')
        run = self.st.root / 'dump-1x-light-active' / 'run-1'
        a = json.loads((run / 'admission.json').read_text())
        self.assertEqual((a['protocol'], a['scenes'], a['departures']), ('dump', 14, 0))
        self.assertEqual((a['scenesSha256'], a['splitSha256']), (DECLARATION['scenesSha256'], DECLARATION['splitSha256']))
        report = json.loads((run / 'check.json').read_text())
        self.assertEqual(report['departures'], 0)
        argv = self.st.calls_made()[-1]
        self.assertIn('--require-key', argv)
        self.assertIn('VITREA_SCALE=1', argv)

    def test_a_dump_rehearsal_records_the_census_and_is_never_evidence(self):
        (self.st.tmp / 'machine.json').write_text(json.dumps(machine(1, foreign=2)))
        root = self.st.tmp / 'rehearsal-root'
        self.st.run('dump', '1x-light-active', '--rehearse', VITREA_SITTING_DIR=str(root))
        run = root / 'rehearsal-dump-1x-light-active' / 'run-1'
        self.assertFalse((run / 'admission.json').exists())
        record = json.loads((run / 'rehearsal.json').read_text())
        self.assertEqual((record['outcome'], record['departures'], record['scenes']), ('dumped-and-checked', 0, 14))
        self.assertEqual(record['foreignCensus']['open']['count'], 2)
        self.assertEqual(record['scenesSha256'], DECLARATION['scenesSha256'])
        timing = json.loads((run / 'timing.json').read_text())
        self.assertEqual((timing['scenes'], timing['timeoutSeconds']), (14, S.dump_timeout(14)))
        self.assertEqual((len(timing['loadAverageAtLaunch']), len(timing['loadAverageAtClose'])), (3, 3))
        with self.assertRaisesRegex(ValueError, 'foreign'):     # the evidence dump still enforces it
            self.st.run('dump', '1x-light-active')

    def test_a_departure_stops_the_sitting_before_any_capture(self):
        with self.assertRaisesRegex(ValueError, 'departure'):
            self.st.run('dump', '1x-light-active', STUB_MODE='depart')
        quarantined = list((self.st.root / 'dump-1x-light-active').glob('QUARANTINE-run-1-*'))
        self.assertEqual(len(quarantined), 1)
        self.assertIn('departure', (quarantined[0] / 'refusal.txt').read_text())
        with self.assertRaisesRegex(ValueError, 'earlier pass is not complete'):
            self.st.run('capture', '2x-light-active')
        self.assertFalse(any('capture' in c for c in self.st.calls_made()))


class Capture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.st = Stubs(self._tmp.name, scale=1)
        self.st.admit_before('1x-light-active')

    def tearDown(self):
        self._tmp.cleanup()

    def prime(self, run, sentinel=False, **kw):
        doc = P.derive('1x-light-active', run, sentinel)
        name = '1x-light-active' + ('-sentinel' if sentinel else '')
        m = manifest(doc, 'active', 1, f'w42-{name}-{run}', 'long' if sentinel else 'normal', **kw)
        (self.st.tmp / 'manifest.json').write_text(json.dumps(m))

    def test_run_one_carries_references_and_is_admitted(self):
        self.prime(1)
        self.st.run('capture', '1x-light-active', '1', '1')
        run = self.st.root / '1x-light-active' / 'run-1'
        a = json.loads((run / 'admission.json').read_text())
        self.assertEqual((a['protocol'], a['cells'], a['key']), ('normal', 23, '1x-light-active'))
        self.assertEqual((a['scenesSha256'], a['splitSha256']), (DECLARATION['scenesSha256'], DECLARATION['splitSha256']))
        held = [s for s in P.derive('1x-light-active', 1)['split']['holdout']]
        self.assertEqual(a['holdoutFrames']['count'], len(held))
        self.assertEqual(len(a['frames']) + len(held), 23)
        png = run / 'apple-macos-27.0-1x-light-standard-glass0.5' / 'a-g128-rrect-md-1x__rest.png'
        self.assertEqual(a['frames']['apple-macos-27.0-1x-light-standard-glass0.5/a-g128-rrect-md-1x__rest'],
                         hashlib.sha256(png.read_bytes()).hexdigest())
        self.assertFalse(any(k.split('/', 1)[1] in held for k in a['frames']))   # H frames only as one digest
        argv = [c for c in self.st.calls_made() if 'capture' in c][-1]
        ids = argv[argv.index('--scenes') + 1].split(',')
        self.assertEqual(sum(1 for s in ids if s.startswith('ref-')), 9)
        self.assertNotIn('--inactive', argv)
        self.assertTrue(any(c[:2] == ['harness', 'backgrounds'] for c in self.st.calls_made()))
        self.prime(2)
        self.st.run('capture', '1x-light-active', '2', '2')
        argv = [c for c in self.st.calls_made() if 'capture' in c][-1]
        self.assertFalse(any(s.startswith('ref-') for s in argv[argv.index('--scenes') + 1].split(',')))

    def test_an_admission_binds_png_bytes_that_exist_at_the_declared_size(self):
        for mode, message in (('no-png', 'fixture PNG missing'), ('bad-png', 'not an RGB\\(A\\) PNG of 320x200')):
            with self.subTest(mode=mode):
                self.prime(1)
                with self.assertRaisesRegex(ValueError, message):
                    self.st.run('capture', '1x-light-active', '1', '1', STUB_MODE=mode)
                self.assertFalse((self.st.root / '1x-light-active' / 'run-1').exists())
        self.assertEqual(len(list((self.st.root / '1x-light-active').glob('QUARANTINE-run-1-*'))), 2)

    def test_an_admission_under_another_declaration_does_not_count(self):
        self.prime(1)
        for path in self.st.root.glob('*/run-*/admission.json'):    # earlier passes, admitted under another bed
            a = json.loads(path.read_text())
            path.write_text(json.dumps(dict(a, splitSha256='f' * 64)))
        with self.assertRaisesRegex(ValueError, 'earlier pass is not complete'):
            self.st.run('capture', '1x-light-active', '1', '1')

    def test_per_capture_idle_quarantines_and_blocks_successors(self):
        self.prime(1, idle=30.0)
        with self.assertRaisesRegex(ValueError, 'per-capture HID idle'):
            self.st.run('capture', '1x-light-active', '1', '1')
        self.assertEqual(len(list((self.st.root / '1x-light-active').glob('QUARANTINE-run-1-*'))), 1)
        self.assertFalse((self.st.root / '1x-light-active' / 'run-1').exists())
        with self.assertRaisesRegex(ValueError, r'earlier run\(s\) \[1\]'):
            self.st.run('capture', '1x-light-active', '2', '2')

    def test_offset_origin_is_attested(self):
        self.prime(1, origin_shift='bp-p1-c4-capsule-button-odd__rest')
        with self.assertRaisesRegex(ValueError, 'supplied path attestation'):
            self.st.run('capture', '1x-light-active', '1', '1')

    def test_an_existing_run_is_never_overwritten(self):
        (self.st.root / '1x-light-active' / 'run-1').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.st.run('capture', '1x-light-active', '1', '1')

    def test_a_failed_gate_quarantines_before_launch(self):
        (self.st.tmp / 'machine.json').write_text(json.dumps(machine(1, NSGlassTintAmount='0.546', foreign=1)))
        self.prime(1)
        with self.assertRaisesRegex(ValueError, 'policy/slider.*foreign'):
            self.st.run('capture', '1x-light-active', '1', '1')
        self.assertFalse(any('capture' in c for c in self.st.calls_made()))
        q = next((self.st.root / '1x-light-active').glob('QUARANTINE-run-1-*'))
        self.assertTrue((q / 'attest.open.json').exists() and (q / 'session-before.json').exists())

    def test_idle_never_reached_refuses_without_launch(self):
        self.prime(1)
        with self.assertRaisesRegex(ValueError, 'HID idle never reached'):
            self.st.run('capture', '1x-light-active', '1', '1', STUB_IDLE='10')
        self.assertEqual(self.st.calls_made(), [])

    def test_a_later_pass_blocks_an_earlier_one(self):
        (self.st.root / '1x-dark-active' / 'run-1').mkdir(parents=True)
        self.prime(1)
        with self.assertRaisesRegex(ValueError, 'later pass has already started'):
            self.st.run('capture', '1x-light-active', '1', '1')

    def test_sentinel_waits_for_every_bed_pass_of_its_scale(self):
        self.prime(1, sentinel=True)
        with self.assertRaisesRegex(ValueError, 'earlier pass is not complete'):
            self.st.run('capture', '1x-light-active', '1', '1', '--sentinel')

    def test_rehearsal_expects_the_tcc_refusal(self):
        root = self.st.tmp / 'rehearsal-root'
        self.prime(1)
        self.st.run('capture', '1x-light-active', '--rehearse-refusal', VITREA_SITTING_DIR=str(root), STUB_MODE='tcc')
        verdict = json.loads((root / 'rehearsal-1x-light-active' / 'run-1' / 'rehearsal.json').read_text())
        self.assertEqual(verdict['outcome'], 'refused-tcc')
        with self.assertRaisesRegex(ValueError, 'published a capture'):
            self.st.run('capture', '1x-dark-active', '--rehearse-refusal', VITREA_SITTING_DIR=str(root))


HARNESS = Path('/Users/new/vitrea-w39/side/harness')


@unittest.skipUnless(HARNESS.exists(), 'the W39 side harness is absent on this machine')
class SideHarnessLoadsEveryDerivedDocument(unittest.TestCase):
    """The pinned side binary's non-GUI `backgrounds` command loads each derived document
    through SceneSpecFile.validate() (every scene in one split set, every split id a scene,
    every profile id declared) and renders its backgrounds. No window, no ScreenCaptureKit."""

    def test_every_pass_document_loads(self):
        import subprocess
        spec_doc, bed = P.load()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            docs = []
            for p in P.pass_order(bed):
                scale = P.endpoint(p['key'])[0]
                if p['kind'] == 'dump':
                    profile = next(x for x in spec_doc['profiles'] if x['key'] == bed['passes'][p['key']]['profile'])
                    docs.append((p['name'], scale, P.subset(spec_doc, P.dump_ids(p['key']), profile)))
                elif p['kind'] == 'bed':
                    docs += [(f'{p["name"]}-run-{n}', scale, P.derive(p['key'], n)) for n in (1, 2)]
                else:
                    docs.append((p['name'], scale, P.derive(p['key'], 1, sentinel=True)))
            for name, scale, doc in docs:
                path = tmp / f'{name}.json'
                path.write_text(json.dumps(doc))
                env = {**os.environ, 'VITREA_SCENES': str(path), 'VITREA_FIXTURES': str(tmp / name),
                       'VITREA_SCALE': str(scale)}
                out = subprocess.run([str(HARNESS), 'backgrounds'], env=env, capture_output=True, text=True)
                self.assertEqual(out.returncode, 0, name + ': ' + out.stderr[-400:])
                self.assertIn(f'{len(doc["backgrounds"])} backgrounds', out.stdout, name)
            self.assertEqual(len(docs), 32)


W39_DIR = REPO / 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed'
STALE_BED = '764217e1'   # the bed before fix b1: a real earlier bed.json and scenes file


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True).stdout


class Mirror:
    """A throwaway Git checkout holding the W42 bed, its tools and a declaration.json at their real
    relative paths, whose declaration names the bed and is committed and hashed, and whose W39
    bundle pin is the stub machine's: the pre-launch check, the driver and the orchestrator run for
    real against it. `replace` substitutes a file's bytes (the red half of a red/green proof)."""

    TOOLS = ('sitting.py', 'pass-spec.py', 'record-machine.py', 'run-sitting-w42.sh', 'sitting-orchestrate.sh',
             'collect-pass.py', 'w42_archive.py')

    def __init__(self, tmp, replace=None):
        self.repo = Path(tmp) / 'repo'
        files = [BED_DIR / n for n in ('wave.py', 'scenes-w42-body.json', 'bed.json', 'pins.json', 'twin-audit.json')]
        files += [HERE / n for n in self.TOOLS]
        files += [BED_DIR / 'dumps' / n for n in ('dumpcheck.py', 'dump-reference.json')]
        files += [W39_DIR / 'wave.py']
        for f in files:
            self.put(f.relative_to(REPO), f.read_bytes())
        self.put((W39_DIR / 'bundle-pin.json').relative_to(REPO), json.dumps(PIN).encode())
        for rel, raw in (replace or {}).items():
            self.put(rel, raw)
        self.bed = self.repo / BED_DIR.relative_to(REPO)
        self.sitting = self.bed / 'sitting'
        self.declare(PINS['scenes-w42-body.json'], PINS['bed.json'])
        git(self.repo, 'init', '-q')
        git(self.repo, 'config', 'user.email', 'test@example.invalid')
        git(self.repo, 'config', 'user.name', 'W42 mirror')
        self.commit('the mirror')

    def put(self, rel, raw):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        if path.suffix == '.sh':
            path.chmod(0o755)

    def declare(self, scenes, split, hashed=True):
        d = self.bed.parent
        raw = json.dumps(dict(schema='w42-declaration-1', items=[dict(id='split', declared=dict(
            scenesSha256=scenes, splitSha256=split))]), indent=1).encode()
        (d / 'declaration.json').write_bytes(raw)
        digest = d / 'declaration.sha256'
        if hashed:
            digest.write_text(hashlib.sha256(raw).hexdigest() + '  declaration.json\n')
        elif digest.exists():
            digest.unlink()

    def commit(self, message):
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-qm', message)

    def repin(self):
        pins = json.loads((self.bed / 'pins.json').read_text())
        for name in ('scenes-w42-body.json', 'bed.json'):
            pins[name] = hashlib.sha256((self.bed / name).read_bytes()).hexdigest()
        (self.bed / 'pins.json').write_text(json.dumps(pins, indent=2) + '\n')

    def sitting_py(self, *argv, env=None):
        return subprocess.run([sys.executable, str(self.sitting / 'sitting.py'), *argv], capture_output=True,
                              text=True, env={**os.environ, **(env or {})}, timeout=120)


def one_byte_edit(scenes, background='grey-064'):
    """A silent, loadable one-byte edit: the grey's first channel moves by one code (its last
    digit, 4 -> 5 or 8 -> 9)."""
    raw = bytearray(scenes.read_bytes())
    level = background.split('-')[1].lstrip('0')
    key = f'"{background}": {{'.encode()
    at = raw.index(level.encode(), raw.index(key) + len(key))
    last = at + len(level) - 1
    raw[last] = raw[last] + 1
    scenes.write_bytes(bytes(raw))
    json.loads(raw)


def stub_displayplacer(tmp, start='68'):
    """displayplacer over one screen with modes 68 and 69; every call is logged."""
    tmp = Path(tmp)
    state, calls = tmp / 'mode', tmp / 'dp-calls.txt'
    state.write_text(start)
    listing = json.loads(W34_MACHINE.read_text())['display']['stdout']
    (tmp / 'dp.py').write_text(f"""import sys
from pathlib import Path
state = Path({str(state)!r})
with open({str(calls)!r}, 'a') as f:
    f.write(' '.join(sys.argv[1:]) + '\\n')
listing = {listing!r}
if sys.argv[1] == 'list':
    m = state.read_text()
    text = listing.replace(' <-- current mode', '')
    line = [l for l in text.splitlines() if l.startswith(f'  mode {{m}}:')][0]
    print(text.replace(line, line + ' <-- current mode'))
else:
    state.write_text(sys.argv[1].split('mode:')[1])
""")
    (tmp / 'dp').write_text(f'#!/bin/bash\nexec {sys.executable} {tmp / "dp.py"} "$@"\n')
    (tmp / 'dp').chmod(0o755)
    return tmp / 'dp', state, calls


STUB_DRIVER = r"""#!/bin/bash
# A stand-in for run-sitting-w42.sh: logs its argv, then does what STUB_DRIVER_MODE says.
echo "$*" >> "$STUB_DRIVER_CALLS"
case "${STUB_DRIVER_MODE:-ok}" in
  swallow) cat > /dev/null ;;
  sleep) sleep 4 ;;
esac
exit 0
"""


class PinCheck(unittest.TestCase):
    """B-M1, red and green, in a Mirror: the bed a launch captures is the pinned, committed,
    hashed declaration, or nothing launches."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.m = Mirror(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, **env):
        out = self.m.sitting_py('pin-check', env={'W42_PREDECLARATION': '', **env})
        return out.returncode, out.stdout + out.stderr

    def test_the_declared_bed_passes(self):
        rc, text = self.check()
        self.assertEqual(rc, 0, text)
        record = json.loads(text)
        self.assertEqual((record['scenesSha256'], record['splitSha256']),
                         (PINS['scenes-w42-body.json'], PINS['bed.json']))
        self.assertNotIn('predeclaration', record)

    def test_a_scenes_file_edited_by_one_byte_refuses(self):
        one_byte_edit(self.m.bed / 'scenes-w42-body.json')
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('not its pins', text)                     # pins.json catches the edit
        self.m.repin()
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('differs from its committed copy at HEAD', text)   # re-pinned but uncommitted
        self.m.commit('an edited scenes file, re-pinned and committed')
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('declaration.json names scenes', text)    # committed, but not the declared one

    def test_a_stale_bed_json_refuses(self):
        stale = subprocess.run(['git', '-C', str(REPO), 'show',
                                f'{STALE_BED}:{(BED_DIR / "bed.json").relative_to(REPO)}'],
                               check=True, capture_output=True).stdout
        (self.m.bed / 'bed.json').write_bytes(stale)
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('not its pins', text)
        self.m.repin()
        self.m.commit('a stale bed.json, re-pinned and committed')
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('declaration.json names scenes', text)

    def test_an_unhashed_declaration_refuses(self):
        self.m.declare(PINS['scenes-w42-body.json'], PINS['bed.json'], hashed=False)
        self.m.commit('the declaration without its hash')
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('declaration.sha256', text)

    def test_predeclaration_records_the_declaration_and_launches_rehearsals_only(self):
        self.m.declare('0' * 64, '1' * 64)
        self.m.commit('a declaration naming another bed')
        rc, text = self.check(W42_PREDECLARATION='1')
        self.assertEqual(rc, 0, text)
        record = json.loads(text)
        self.assertTrue(record['predeclaration'])
        self.assertIn('declaration.json names scenes 000000000000', record['declarationProblems'][0])
        with tempfile.TemporaryDirectory() as tmp:
            st = Stubs(tmp)
            out = self.m.sitting_py('capture', '2x-light-active', env={**st.env, 'W42_PREDECLARATION': '1'})
            self.assertNotEqual(out.returncode, 0)
            self.assertIn('admits rehearsals only', out.stderr)
            self.assertFalse(st.root.exists())

    def test_the_driver_refuses_before_its_root_exists(self):
        (self.m.bed / 'bed.json').write_bytes((self.m.bed / 'bed.json').read_bytes() + b' ')
        with tempfile.TemporaryDirectory() as tmp:
            st = Stubs(tmp)
            out = self.m.sitting_py('dump', '2x-light-active', env=st.env)
            self.assertNotEqual(out.returncode, 0)
            self.assertIn('refused before any launch', out.stderr)
            self.assertFalse(st.root.exists())
            self.assertEqual(st.calls_made(), [])


class Orchestrator(unittest.TestCase):
    """sitting-orchestrate.sh in a Mirror with a stub displayplacer: the pin check first, the pass
    list on fd 3 with its status checked and its last pass asserted, STOP_AFTER=dumps, the
    rehearsals through the mode trap, the display restored and verified on every exit, and the
    detached launch."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def setup(self, replace=None, stub_driver=True, start_mode='68', **machine_changes):
        self.m = Mirror(self.tmp, replace)
        self.st = Stubs(self.tmp, scale=1, **machine_changes)
        self.dp, self.state, self.dp_calls = stub_displayplacer(self.tmp, start_mode)
        self.driver_calls = self.tmp / 'driver-calls.txt'
        if stub_driver:
            (self.m.sitting / 'run-sitting-w42.sh').write_text(STUB_DRIVER)
            self.m.commit('the stub driver')
        self.env = {**os.environ, **self.st.env, 'DISPLAYPLACER': str(self.dp), 'STUB_IDLE': '400',
                    'STUB_DRIVER_CALLS': str(self.driver_calls), 'W42_FOREGROUND': '1'}
        for k in ('DRY', 'W42_ORCHESTRATED', 'W42_PREDECLARATION', 'START_AT', 'STOP_AFTER', 'PASSES', 'REHEARSAL'):
            self.env.pop(k, None)

    def orchestrate(self, **env):
        return subprocess.run(['bash', str(self.m.sitting / 'sitting-orchestrate.sh')], env={**self.env, **env},
                              capture_output=True, text=True, timeout=180)

    def status(self):
        return (self.st.root / 'logs' / 'orchestrator-status.txt').read_text()

    def driven(self):
        return self.driver_calls.read_text().splitlines() if self.driver_calls.exists() else []

    def switches(self):
        return [l.split('mode:')[1] for l in self.dp_calls.read_text().splitlines() if 'mode:' in l]

    def test_stop_and_restore(self):
        self.setup(stub_driver=False, foreign=1)
        self.st.admit_before('dump-1x-light-active')
        out = self.orchestrate(START_AT='dump-1x-light-active')
        self.assertEqual(out.returncode, 3, out.stdout + out.stderr)
        self.assertEqual(self.state.read_text(), '68')
        status = self.status()
        self.assertIn('display -> mode 69', status)
        self.assertIn('STOP dump-1x-light-active', status)
        self.assertIn('restore: display mode 68 (verified)', status)
        self.assertNotIn('START dump-2x', status)
        q = list((self.st.root / 'dump-1x-light-active').glob('QUARANTINE-run-1-*'))
        self.assertEqual(len(q), 1)
        self.assertIn('foreign', (q[0] / 'refusal.txt').read_text())
        self.assertFalse(any('dump-layers' in c for c in self.st.calls_made()))

    def test_a_bed_that_is_not_the_declaration_launches_nothing(self):
        self.setup(start_mode='69')
        self.m.declare('0' * 64, PINS['bed.json'])
        self.m.commit('a declaration naming another scenes file')
        out = self.orchestrate()
        self.assertEqual(out.returncode, 5, out.stdout + out.stderr)
        self.assertIn('STOP: the bed is not the pinned declaration', self.status())
        self.assertIn('declaration.json names scenes', (self.st.root / 'logs' / 'pin-check.json').read_text())
        self.assertEqual(self.driven(), [])
        self.assertEqual(self.state.read_text(), '68')    # left at 69 by a crash: restored even so

    def test_a_child_reading_stdin_cannot_swallow_the_passes(self):
        self.setup()
        out = self.orchestrate(STOP_AFTER='dumps', STUB_DRIVER_MODE='swallow')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertEqual(len(self.driven()), 8)
        self.assertIn('DUMPS DONE', self.status())

    def test_a_failing_pass_order_stops_the_sitting(self):
        self.setup(replace={(HERE / 'pass-spec.py').relative_to(REPO): b'import sys\nsys.exit(3)\n'})
        out = self.orchestrate()
        self.assertEqual(out.returncode, 6, out.stdout + out.stderr)
        self.assertIn('pass-spec.py order failed', self.status())
        self.assertNotIn('ALL PASSES DONE', self.status())
        self.assertEqual(self.driven(), [])

    def test_stop_after_dumps_runs_the_dump_step_only(self):
        self.setup()
        out = self.orchestrate(STOP_AFTER='dumps')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        want = [f'dump {s}x-{c}-{p}' for s in (2, 1) for c in ('light', 'dark') for p in ('active', 'receded')]
        self.assertEqual(self.driven(), want)
        self.assertEqual(self.switches(), ['69', '68'])
        self.assertIn('DUMPS DONE: stopped after dump-1x-dark-receded', self.status())
        self.assertEqual(self.state.read_text(), '68')

    def test_rehearsals_run_through_the_mode_trap(self):
        self.setup()
        out = self.orchestrate(REHEARSAL='1', PASSES='1x-light-active dump-1x-dark-receded 2x-light-active')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertEqual(self.driven(), ['dump 1x-dark-receded --rehearse', 'capture 2x-light-active --rehearse-refusal',
                                         'capture 1x-light-active --rehearse-refusal'])
        self.assertEqual(self.switches(), ['69', '68', '69', '68'])
        self.assertIn('REHEARSALS DONE (1x-light-active)', self.status())
        for bad, message in ((dict(REHEARSAL='1'), 'needs PASSES'),
                             (dict(PASSES='2x-light-active'), 'rehearsals only'),
                             (dict(REHEARSAL='1', PASSES='2x-light-active-sentinel'), 'no rehearsal'),
                             (dict(STOP_AFTER='captures'), 'not a declared stop')):
            with self.subTest(bad=bad):
                self.assertEqual(self.orchestrate(**bad).returncode, 6)
                self.assertIn(message, self.status())

    def test_a_signal_mid_pass_restores_the_display(self):
        self.setup()
        env = {**self.env, 'STOP_AFTER': 'dumps', 'STUB_DRIVER_MODE': 'sleep', 'START_AT': 'dump-1x-light-active'}
        proc = subprocess.Popen(['bash', str(self.m.sitting / 'sitting-orchestrate.sh')], env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 60
        while not self.driven() and time.monotonic() < deadline:
            time.sleep(0.2)
        self.assertEqual(self.state.read_text(), '69')
        proc.send_signal(signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=60), 143)
        self.assertEqual(self.state.read_text(), '68')
        self.assertIn('restore: display mode 68 (verified)', self.status())

    def test_the_sitting_detaches_into_its_own_session(self):
        self.setup()
        env = {k: v for k, v in self.env.items() if k != 'W42_FOREGROUND'}
        out = subprocess.run(['bash', str(self.m.sitting / 'sitting-orchestrate.sh')],
                             env={**env, 'STOP_AFTER': 'dumps', 'STUB_DRIVER_MODE': 'sleep',
                                  'START_AT': 'dump-1x-dark-receded'},
                             capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn('detached as pid', out.stdout)
        pid = int((self.st.root / 'logs' / 'orchestrator.pid').read_text())
        deadline = time.monotonic() + 20
        while os.getsid(pid) == os.getsid(0) and time.monotonic() < deadline:
            time.sleep(0.1)
        self.assertNotEqual(os.getsid(pid), os.getsid(0))   # its own session: a torn-down caller cannot HUP it
        deadline = time.monotonic() + 90
        while 'restore:' not in (self.status() if (self.st.root / 'logs' / 'orchestrator-status.txt').exists()
                                 else '') and time.monotonic() < deadline:
            time.sleep(0.5)
        self.assertIn('DUMPS DONE', self.status())
        self.assertEqual(self.state.read_text(), '68')


def gone(pid, within=15):
    """True once `pid` no longer exists (a reaped process), within `within` seconds."""
    deadline = time.monotonic() + within
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.2)
    return False


class VerificationRound(unittest.TestCase):
    """The verification review of the fixes (53400aa5): per-run provenance (finding 1) and a
    cancellation that reaches the driver and its launch at once (finding 3), in a Mirror."""

    def test_a_scenes_file_edited_between_runs_refuses_the_next_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            m = Mirror(tmp)
            st = Stubs(tmp, scale=1)
            st.admit_before('1x-light-active')
            scenes = m.bed / 'scenes-w42-body.json'
            env = {**st.env, 'STUB_AUTO': '1', 'STUB_TEST_DIR': str(HERE), 'STUB_EDIT_SCENES': str(scenes)}
            out = m.sitting_py('capture', '1x-light-active', '1', '2', env=env)
            self.assertNotEqual(out.returncode, 0)
            base = st.root / '1x-light-active'
            admitted = json.loads((base / 'run-1' / 'admission.json').read_text())
            self.assertEqual(admitted['scenesSha256'], PINS['scenes-w42-body.json'])
            self.assertEqual(json.loads((base / 'scenes-run-1.json').read_text())['backgrounds']['grey-128']['srgb'],
                             [128, 128, 128])
            self.assertNotEqual(hashlib.sha256(scenes.read_bytes()).hexdigest(), PINS['scenes-w42-body.json'])
            q = list(base.glob('QUARANTINE-run-2-*'))
            self.assertEqual(len(q), 1)
            self.assertIn('no longer the one this driver validated', (q[0] / 'refusal.txt').read_text())
            self.assertEqual(len([c for c in st.calls_made() if 'capture' in c]), 1)   # run 2 never launched

    def test_a_signal_mid_capture_ends_the_driver_and_its_launch_and_restores_at_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            m = Mirror(tmp)
            st = Stubs(tmp, scale=1)
            st.admit_before('1x-light-active')
            dp, state, _ = stub_displayplacer(tmp)
            pids = tmp / 'pids.json'
            env = {**os.environ, **st.env, 'DISPLAYPLACER': str(dp), 'STUB_IDLE': '400', 'W42_FOREGROUND': '1',
                   'START_AT': '1x-light-active', 'STUB_MODE': 'block', 'STUB_PIDS': str(pids),
                   'STUB_NATIVE': PIN['path'] + '/Contents/MacOS/VitreaReference'}
            for k in ('W42_ORCHESTRATED', 'STOP_AFTER', 'PASSES', 'REHEARSAL', 'W42_PREDECLARATION'):
                env.pop(k, None)
            proc = subprocess.Popen(['bash', str(m.sitting / 'sitting-orchestrate.sh')], env=env,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = time.monotonic() + 90
            while not pids.exists() and time.monotonic() < deadline:
                time.sleep(0.2)
            launched = json.loads(pids.read_text())
            self.assertEqual(state.read_text(), '69')
            began = time.monotonic()
            proc.send_signal(signal.SIGTERM)
            self.assertEqual(proc.wait(timeout=60), 143)
            self.assertLess(time.monotonic() - began, 20)                    # not the pass's length
            status = (st.root / 'logs' / 'orchestrator-status.txt').read_text()
            self.assertEqual(state.read_text(), '68')
            self.assertIn('restore: display mode 68 (verified)', status)
            driver = int(re.search(r'job pid (\d+): \S*run-sitting-w42.sh capture', status)[1])
            for pid in (driver, launched['launcher'], launched['app']):
                self.assertTrue(gone(pid), f'pid {pid} survives the cancellation')
            q = list((st.root / '1x-light-active').glob('QUARANTINE-run-1-*'))
            self.assertEqual(len(q), 1)
            self.assertIn('Cancelled', (q[0] / 'refusal.txt').read_text())


class DriverUnderTheOrchestrator(unittest.TestCase):
    """b4: a launch outside the orchestrator is refused; b2: an admission binds its PNG bytes."""

    def test_a_launch_outside_the_orchestrator_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            st = Stubs(tmp)
            with self.assertRaises(SystemExit):
                st.run('capture', '2x-light-active', '--rehearse-refusal', W42_ORCHESTRATED='')
            self.assertEqual(st.calls_made(), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
