#!/usr/bin/env python3.12
"""W42 sitting driver tests (charter clause 4). Nothing is captured and nothing is launched:
the machine recorder, session reader, harness and launcher are stubs; pass-spec.py, the bed
files and dumpcheck.py are the real ones. The dump-step tests feed memo D's own dump files
(~/vitrea-w42/grounding/dumps, hashed in the grounding's scratch-sha256.txt) relabelled with
W42 scene ids, and are skipped where that scratch is absent.

Run: python3.12 -m unittest -v test_sitting    (from this directory)"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
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
if mode == 'tcc':
    err.write_text('error: ScreenCaptureKit is unavailable\n\nThis is the Screen Recording (TCC) gate.\n')
else:
    (fixtures / 'manifest.json').write_text(Path(os.environ['STUB_MANIFEST']).read_text())
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
                        VITREA_IDLE_LIMIT='0', VITREA_IDLE_POLL='0',
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
                    {'admitted': True, 'pass': p['name'], 'run': n, 'protocol': S.protocol_of_pass(p)}))

    def run(self, *argv, **extra):
        env = {**self.env, **extra}
        with mock.patch.dict(os.environ, env, clear=False):
            for k in ('DRY', 'STUB_PROMPT'):
                if k not in extra:
                    os.environ.pop(k, None)
            with mock.patch.object(S, 'REPO', Path('/nonexistent-repo')), \
                    mock.patch.object(S, 'MAIN', Path('/nonexistent-main')):
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
        # rehearsal (4 cells per 2x receded pass, 1 per 1x receded pass).
        self.assertEqual((t['dumpLaunches'], t['dumpScenes'], t['captureLaunches']), (8, 424, 80))
        self.assertEqual((t['glass'], t['references'], t['sentinels'], t['captures']), (2968, 260, 48, 3276))
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
        self.assertEqual((a['protocol'], a['scenes'], a['departures']), ('dump', 15, 0))
        report = json.loads((run / 'check.json').read_text())
        self.assertEqual(report['departures'], 0)
        argv = self.st.calls_made()[-1]
        self.assertIn('--require-key', argv)
        self.assertIn('VITREA_SCALE=1', argv)

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
        self.assertEqual((a['protocol'], a['cells'], a['key']), ('normal', 25, '1x-light-active'))
        argv = [c for c in self.st.calls_made() if 'capture' in c][-1]
        ids = argv[argv.index('--scenes') + 1].split(',')
        self.assertEqual(sum(1 for s in ids if s.startswith('ref-')), 10)
        self.assertNotIn('--inactive', argv)
        self.assertTrue(any(c[:2] == ['harness', 'backgrounds'] for c in self.st.calls_made()))
        self.prime(2)
        self.st.run('capture', '1x-light-active', '2', '2')
        argv = [c for c in self.st.calls_made() if 'capture' in c][-1]
        self.assertFalse(any(s.startswith('ref-') for s in argv[argv.index('--scenes') + 1].split(',')))

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


class Orchestrator(unittest.TestCase):
    """sitting-orchestrate.sh with a stub displayplacer: a refusal stops the sitting, a
    continuation starts where the operator names, and the display is restored to mode 68."""

    def test_stop_and_restore(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            st = Stubs(tmp, scale=1, foreign=1)
            state = st.tmp / 'mode'
            state.write_text('68')
            listing = json.loads(W34_MACHINE.read_text())['display']['stdout']
            (st.tmp / 'dp.py').write_text(f"""import sys
from pathlib import Path
state = Path({str(state)!r})
listing = {listing!r}
if sys.argv[1] == 'list':
    m = state.read_text()
    text = listing.replace(' <-- current mode', '')
    line = [l for l in text.splitlines() if l.startswith(f'  mode {{m}}:')][0]
    print(text.replace(line, line + ' <-- current mode'))
else:
    state.write_text(sys.argv[1].split('mode:')[1])
""")
            (st.tmp / 'dp').write_text(f'#!/bin/bash\nexec {sys.executable} {st.tmp / "dp.py"} "$@"\n')
            (st.tmp / 'dp').chmod(0o755)
            st.admit_before('dump-1x-light-active')
            env = {**os.environ, **st.env, 'DISPLAYPLACER': str(st.tmp / 'dp'), 'STUB_IDLE': '400',
                   'START_AT': 'dump-1x-light-active', 'VITREA_APP': PIN['path']}
            env.pop('DRY', None)
            # The subprocess reads the real pin; point the stub machine at it instead.
            m = machine(1, foreign=1)
            real = json.loads(S.W39_PIN.read_text())
            m['side'].update(binarySha256=real['binarySha256'], buildVersion=dict(stdout=real['buildVersion']))
            m['side']['signature']['stderr'] = f'CDHash={real["cdhash"]}\n'
            (st.tmp / 'machine.json').write_text(json.dumps(m))
            env['VITREA_APP'] = real['path']
            out = subprocess.run(['bash', str(HERE / 'sitting-orchestrate.sh')], env=env, capture_output=True,
                                 text=True, timeout=120)
            self.assertEqual(out.returncode, 3, out.stdout + out.stderr)
            self.assertEqual(state.read_text(), '68')
            status = (st.root / 'logs' / 'orchestrator-status.txt').read_text()
            self.assertIn('display -> mode 69', status)
            self.assertIn('STOP dump-1x-light-active', status)
            self.assertIn('restore: display mode 68', status)
            self.assertNotIn('dump-2x', status)
            q = list((st.root / 'dump-1x-light-active').glob('QUARANTINE-run-1-*'))
            self.assertEqual(len(q), 1)
            self.assertIn('foreign', (q[0] / 'refusal.txt').read_text())
            self.assertFalse(any('dump-layers' in c for c in st.calls_made()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
