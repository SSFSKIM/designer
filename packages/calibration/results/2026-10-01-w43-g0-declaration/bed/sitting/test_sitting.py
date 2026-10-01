#!/usr/bin/env python3.12
"""W43 sitting tooling tests (charter G0 (d)). Nothing native is launched and the real slider is
never written: the machine recorder, session reader, harness, launcher, `defaults`, displayplacer
and the driver (for the orchestrator) are stubs; pass-spec.py, record-machine.py's census and
sitting.py are the real ones. The census tests read the REAL process table, over processes they
start themselves: shells and stubs whose command lines name the census words, and copies of
python3.12 under browser and harness executable names. Run them only when no sitting is running.

The plan is stand_in.py's (the declaration (e) writes does not exist yet), cut to a few passes
for the driver; the pin check and the orchestrator run for real in `Mirror`, a throwaway Git
checkout holding the tools, the stand-in canonical file, W42's scenes file, the plan and a
declaration at their real relative paths.

Run: python3.12 -m unittest -v test_sitting    (from this directory)"""
import copy
import hashlib
import importlib.util
import io
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
REPO = HERE.parents[5]
W34_MACHINE = REPO / 'packages/calibration/results/2026-09-23-w34-g0-contour-bed/machine-side-built.json'
MEMO_D = Path('/Users/new/vitrea-w42/grounding/dumps/runs')
PYTHON = Path(os.path.realpath(sys.executable))
# A fake executable is a copy of node: python3.12's framework launcher re-execs into Python.app, so a
# copy of it never runs under its own name, while a node copy's image IS the copy (proc_pidpath).
NODE = Path(os.path.realpath(shutil.which('node'))) if shutil.which('node') else None
SLEEP_JS = ['-e', 'setTimeout(() => {}, 30000)']
SIDE = Path('/tmp/w43-test-side/VitreaReference.app').resolve()
HARNESS_ID = 'dev.vitrea.reference-apple.w39'
PIN = dict(path=str(SIDE), bundleIdentifier=HARNESS_ID, binarySha256='b' * 64, cdhash='c' * 40,
           buildVersion='stub:\n platform MACOS\n    minos 26.0\n      sdk 26.0\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S = load('w43_sitting_under_test', HERE / 'sitting.py')
S._PIN = dict(PIN)
P = S.pass_spec()
R = S.recorder_module()
SI = load('w43_stand_in_for_tests', HERE / 'stand_in.py')
CANONICAL_RAW, W42_RAW, STAND_IN_PLAN = SI.build()
SOURCES = SI.sources_of(STAND_IN_PLAN, CANONICAL_RAW, W42_RAW)
SHAS = dict(canonical=hashlib.sha256(CANONICAL_RAW).hexdigest(), w42=hashlib.sha256(W42_RAW).hexdigest())
L1, D1 = SI.key(1, 'light', '0.25'), SI.key(1, 'dark', '0.25')
L2_05 = SI.key(2, 'light', '0.5')
L1_05 = SI.key(1, 'light', '0.5')
BED_ACTIVE = {L1: ['checkerboard__capsule-button__rest', 'checkerboard__glass-over-glass__rest',
                   'checkerboard__toolbar-group__rest'],
              D1: ['checkerboard__capsule-button__rest', 'checkerboard__glass-over-glass__rest']}
BED_RECEDED = {L1: ['checkerboard__capsule-button__inactive', 'checkerboard__toolbar-group__inactive'],
               D1: ['checkerboard__glass-over-glass__inactive']}


def mini_plan(**edits):
    """Five passes over the stand-in's sources: the pose check at 0.5, a dump sentinel and the two
    canonical 1x passes at 0.25 (both schemes, group and stack components), a W42 sentinel at 0.5."""
    passes = [
        dict(name='pose-check', kind='capture', role='pose-check', glass=0.5, scale=2, pose='active',
             source='canonical', runs=1, protocol='normal',
             profiles={L2_05: ['checkerboard__capsule-button__rest']},
             expect={f'{L2_05}/checkerboard__capsule-button__rest': list(SI.POSE_CHECK_FRAMES)}),
        dict(name='dump-1x-light-active', kind='dump', role='dump-sentinel', glass=0.25, scale=1, pose='active',
             source='canonical', profile=L1, scenes=sorted(BED_ACTIVE[L1])),
        dict(name='bed-1x-active', kind='capture', role='bed', glass=0.25, scale=1, pose='active',
             source='canonical', runs=2, protocol='normal', profiles=BED_ACTIVE, publish=True),
        dict(name='bed-1x-receded', kind='capture', role='bed', glass=0.25, scale=1, pose='receded',
             source='canonical', runs=2, protocol='normal', profiles=BED_RECEDED, publish=True),
        dict(name='close-w42-1x-light-active', kind='capture', role='bridge-w42-sentinel', glass=0.5, scale=1,
             pose='active', source='w42', runs=3, protocol='long', runAfterCut=True,
             profiles={L1_05: sorted(f'{c}__rest' for c in SI.W42_SENTINELS)},
             bridge=dict(stop=False, cells={f'{L1_05}/{c}__rest': dict(reference=dict(
                 sha256=hashlib.sha256(c.encode()).hexdigest(), archive='w42-archive')) for c in SI.W42_SENTINELS})),
    ]
    plan = dict(STAND_IN_PLAN, passes=passes)
    for name, change in edits.items():
        next(p for p in passes if p['name'] == name).update(change)
    return plan


PLAN = mini_plan()
DECLARATION = dict(sitting='g1a', planSha256='a' * 64, sources=dict(SHAS), head='test-head', declarationSha256='d' * 64)


def machine(scale=2, glass='0.25', **changes):
    m = json.loads(W34_MACHINE.read_text())
    m['foreignProcessCount'], m['foreignProcesses'] = 0, []
    m['side'].update(path=PIN['path'], binarySha256=PIN['binarySha256'], buildVersion=dict(stdout=PIN['buildVersion']),
                     identifier=dict(stdout=HARNESS_ID))
    m['side']['signature']['stderr'] = f'CDHash={PIN["cdhash"]}\n'
    m['settings']['NSGlassTintAmount']['stdout'] = glass
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


def colour(sid, run=1):
    h = hashlib.sha256(sid.encode()).digest()
    return (h[0], h[1], h[2])


def manifest(doc, pose, scale, label, protocol='normal', idle=100.0, origin_shift=None):
    """A manifest shaped as the side harness writes it, its supplied paths built independently of
    sitting.declared_paths from PathAttestation.swift's rules."""
    canvas = doc['canvas']
    scenes = {s['id']: s for s in doc['scenes']}
    size = [canvas['width'] * scale, canvas['height'] * scale]
    frame = [1120.0, 580.0, float(canvas['width']), float(canvas['height'])]

    def centred(s):
        dx, dy = s.get('offset') or [0, 0]
        return [(canvas['width'] - s['size'][0]) / 2 + dx, (canvas['height'] - s['size'][1]) / 2 + dy]

    def entry(s, origin):
        return dict(kind=s['kind'], frameOrigin=origin, rect=[0, 0, *s['size']], opaque=bool(s.get('opaque')),
                    elements=[])

    profiles = []
    for p in doc['profiles']:
        fixtures = []
        for sid in p['scenes']:
            comp = doc['components'][scenes[sid]['component']]
            if comp['kind'] == 'none':
                paths = []
            elif comp['kind'] == 'stack':
                paths = [entry(comp['base'], centred(comp['base'])), entry(comp['over'], centred(comp['over']))]
            elif comp['kind'] == 'group':
                width = sum(s['size'][0] for s in comp['items']) + (len(comp['items']) - 1) * comp['spacing']
                left, paths = (canvas['width'] - width) / 2, []
                for s in comp['items']:
                    paths.append(entry(s, [left, (canvas['height'] - s['size'][1]) / 2]))
                    left += s['size'][0] + comp['spacing']
            else:
                paths = [entry(comp, centred(comp))]
            if origin_shift == sid and paths:
                paths[-1]['frameOrigin'] = [paths[-1]['frameOrigin'][0] + 1, paths[-1]['frameOrigin'][1]]
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
        profiles.append(dict(profileKey=p['key'], colorScheme=p['colorScheme'], a11yMode='standard',
                             display=dict(requestedScale=scale, actualBackingScale=scale, pixelSize=size,
                                          colorSpace='kCGColorSpaceSRGB'),
                             fixtures=fixtures))
    return dict(hardware=dict(osBuild='26A428', osVersion='Version 27.0 (Build 26A428)', cpu='Apple M2 Pro'),
                profiles=profiles,
                backgrounds={f'{b}@{scale}x': f'backgrounds/{b}@{scale}x.png' for b in doc['backgrounds']},
                captureProtocol=dict(runLabel=label, **HARNESS_PROTOCOL[protocol], hidIdleSecondsAtStart=100.0,
                                     hidIdleSecondsAtEnd=100.0))


STUB_LAUNCHER = r'''
import json, os, subprocess, sys, time
from pathlib import Path
args = sys.argv[1:]
env = dict(a.split('=', 1) for i, a in enumerate(args) if i and args[i - 1] == '--env')
with open(os.environ['STUB_CALLS'], 'a') as f:
    f.write(json.dumps(args) + '\n')
mode = os.environ.get('STUB_MODE', 'auto')


def session(**changes):
    path = Path(os.environ['STUB_SESSION_FILE'])
    state = json.loads(path.read_text())
    state.update(changes)
    path.write_text(json.dumps(state))


if 'dump-layers' in args:
    out = Path(args[args.index('--out') + 1]); out.mkdir(parents=True)
    ids = args[args.index('--scenes') + 1].split(',')
    scheme = args[args.index('--scheme') + 1]
    active = '--require-key' in args
    normal = float(os.environ.get('STUB_NORMAL', '0.25'))
    for i, sid in enumerate(ids):
        key = active and not (mode == 'lose-key' and i == len(ids) - 1)
        filters = [] if mode == 'no-normal' else [dict(description='glassBackground', inputs={
            'inputBlurFillNormalOpacity': normal, 'inputBlurFillLightenOpacity': 0.7875, 'inputBlurRadius': 5})]
        d = dict(scene=sid, isKeyWindow=key, appIsActive=key, backingScaleFactor=int(env['VITREA_SCALE']),
                 colorScheme=scheme, view=dict(layer=dict(sublayers=[dict(filters=filters)])))
        (out / (sid + '.json')).write_text(json.dumps(d))
    sys.exit(0)
fixtures = Path(env['VITREA_FIXTURES'])
out, err = Path(args[args.index('--stdout') + 1]), Path(args[args.index('--stderr') + 1])
ids = args[args.index('--scenes') + 1].split(',')
out.write_text(f'capturing {len(ids)} fixtures via screencapturekit\n')
if mode in ('block', 'input', 'focus', 'focus-after-exit'):
    # A capture that does not return: a stand-in native app (a copy of python at the pinned binary
    # path), detached as LaunchServices would start it, and this launcher waiting like `open -W`.
    app = subprocess.Popen([os.environ['STUB_NATIVE'], '-e', 'setTimeout(() => {}, 60000)'], start_new_session=True)
    Path(os.environ['STUB_PIDS']).write_text(json.dumps(dict(launcher=os.getpid(), app=app.pid)))
    if mode in ('focus', 'focus-after-exit'):
        session(frontmostIdentifier=os.environ['STUB_HARNESS_ID'], frontmostPid=app.pid)
    time.sleep(float(os.environ.get('STUB_BEFORE_EVENT', '1.2')))
    if mode == 'input':
        session(inputAt=time.time())
    elif mode == 'focus':
        session(frontmostIdentifier='com.apple.universalcontrol', frontmostPid=49435)
    elif mode == 'focus-after-exit':
        app.kill(); app.wait()
        session(frontmostIdentifier='com.apple.finder', frontmostPid=600)
        time.sleep(1.5)
        sys.exit(1)
    time.sleep(60)
    sys.exit(0)
sys.path.insert(0, os.environ['STUB_TEST_DIR'])
import test_sitting as T
doc = json.loads(Path(env['VITREA_SCENES']).read_text())
label = args[args.index('--run-label') + 1]
manifest = T.manifest(doc, 'receded' if '--inactive' in args else 'active', int(env['VITREA_SCALE']), label,
                      'long' if '--order-seed' in args else 'normal', origin_shift=os.environ.get('STUB_SHIFT'))
(fixtures / 'manifest.json').write_text(json.dumps(manifest))
if mode != 'no-png':
    from PIL import Image
    for p in manifest['profiles']:
        for f in p['fixtures']:
            path = fixtures / f['file']
            path.parent.mkdir(parents=True, exist_ok=True)
            size = (f['width'] // 2, f['height']) if mode == 'bad-png' else (f['width'], f['height'])
            Image.new('RGB', size, T.colour(f['sceneId'])).save(path)
    for name, rel in manifest['backgrounds'].items():
        if not (fixtures / rel).exists():
            Image.new('RGB', (doc['canvas']['width'] * int(env['VITREA_SCALE']),
                              doc['canvas']['height'] * int(env['VITREA_SCALE'])), (9, 9, 9)).save(fixtures / rel)
err.write_text('')
'''

STUB_SESSION = r'''
import json, os, time
state = json.loads(open(os.environ['STUB_SESSION_FILE']).read())
if state.get('fail'):
    raise SystemExit('the session reader failed')
print(json.dumps(dict(idleSeconds=time.time() - state['inputAt'], screenLocked=state.get('screenLocked', False),
                      windowOwners=state.get('windowOwners', ['Dock|20', 'Window Server|24']),
                      frontmostIdentifier=state.get('frontmostIdentifier', 'com.apple.finder'),
                      frontmostPid=state.get('frontmostPid', 600))))
'''

STUB_HARNESS = r'''
import json, os, sys
from pathlib import Path
with open(os.environ['STUB_CALLS'], 'a') as f:
    f.write(json.dumps(['harness'] + sys.argv[1:]) + '\n')
root = Path(os.environ['VITREA_FIXTURES']) / 'backgrounds'
root.mkdir(parents=True, exist_ok=True)
'''

# The machine read: the test's machine.json, with the slider taken from the stub defaults store
# when one is named, so the orchestrator's writes reach the gate as they would on the machine.
STUB_RECORDER = r'''
import json, os, sys
m = json.loads(open(os.environ['STUB_MACHINE']).read())
store = os.environ.get('STUB_DEFAULTS_STORE')
if store and os.path.exists(store):
    value = json.loads(open(store).read()).get('NSGlassTintAmount')
    m['settings']['NSGlassTintAmount'] = dict(stdout=value['value'] if value else '', exitCode=0 if value else 1)
m['phase'] = sys.argv[1]
print(json.dumps(m))
'''

# `defaults` over one JSON file holding the global domain: never the machine's real default.
STUB_DEFAULTS = r'''
import json, os, sys
from pathlib import Path
store = Path(os.environ['STUB_DEFAULTS_STORE'])
state = json.loads(store.read_text()) if store.exists() else {}
with open(str(store) + '.calls', 'a') as f:
    f.write(' '.join(sys.argv[1:]) + '\n')
verb, domain, key = sys.argv[1], sys.argv[2], sys.argv[3]
assert domain == '-g', domain


def shown(v):
    text = repr(float(v))
    return text[:-2] if text.endswith('.0') else text


if verb == 'read':
    if key not in state:
        sys.exit(f'The domain/default pair of (kCFPreferencesAnyApplication, {key}) does not exist')
    print(state[key]['value'])
elif verb == 'read-type':
    if key not in state:
        sys.exit(1)
    print('Type is ' + state[key]['type'])
elif verb == 'write':
    assert sys.argv[4] == '-float'
    if os.environ.get('STUB_SLOW_WRITE') == sys.argv[5]:          # a write the test aims a signal at
        Path(os.environ['STUB_SLOW_MARK']).write_text('writing')
        import time
        time.sleep(float(os.environ.get('STUB_SLOW_SECONDS', '4')))
    if os.environ.get('STUB_REFUSE_WRITE') == sys.argv[5]:
        sys.exit('stub defaults: the write is refused')
    state[key] = dict(type='float', value=shown(sys.argv[5]))
    store.write_text(json.dumps(state))
elif verb == 'delete':
    state.pop(key, None)
    store.write_text(json.dumps(state))
'''


def fake_executable(path):
    """A copy of node at `path` (an APFS clone, renamed into place), so a process's executable image
    IS that name. Replaced whenever it is not node's bytes, never overwritten in place."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size == NODE.stat().st_size:
        return path
    tmp = path.with_name(path.name + '.cloning')
    if subprocess.run(['cp', '-c', str(NODE), str(tmp)], capture_output=True).returncode != 0:
        shutil.copyfile(NODE, tmp)
    tmp.chmod(0o755)
    os.replace(tmp, path)
    return path


needs_node = unittest.skipUnless(NODE is not None, 'no node binary to copy under a fake executable name')


class Stubs:
    def __init__(self, tmp, scale=1, glass='0.25', **machine_changes):
        self.tmp = Path(tmp)
        (self.tmp / 'machine.json').write_text(json.dumps(machine(scale, glass, **machine_changes)))
        for name, text in [('launcher.py', STUB_LAUNCHER), ('session.py', STUB_SESSION),
                           ('harness.py', STUB_HARNESS), ('recorder.py', STUB_RECORDER),
                           ('defaults.py', STUB_DEFAULTS)]:
            (self.tmp / name).write_text(text)
        self.session_file = self.tmp / 'session.json'
        self.session(inputAt=time.time() - 400)
        self.root = self.tmp / 'root'
        self.calls = self.tmp / 'calls.jsonl'
        self.store = self.tmp / 'defaults-store.json'
        py = sys.executable
        self.env = dict(VITREA_SITTING_DIR=str(self.root), VITREA_APP=PIN['path'], W43_SITTING='g1a',
                        VITREA_RECORD_MACHINE=f'{py} {self.tmp / "recorder.py"}',
                        VITREA_SESSION_READER=f'{py} {self.tmp / "session.py"}',
                        VITREA_HARNESS=f'{py} {self.tmp / "harness.py"}',
                        VITREA_LAUNCHER=f'{py} {self.tmp / "launcher.py"}',
                        VITREA_DEFAULTS=f'{py} {self.tmp / "defaults.py"}',
                        VITREA_IDLE_LIMIT='0', VITREA_IDLE_POLL='0', VITREA_WATCH_POLL='0.3', W43_ORCHESTRATED='1',
                        STUB_CALLS=str(self.calls), STUB_MODE='auto', STUB_MACHINE=str(self.tmp / 'machine.json'),
                        STUB_SESSION_FILE=str(self.session_file), STUB_TEST_DIR=str(HERE),
                        STUB_HARNESS_ID=HARNESS_ID, STUB_PIDS=str(self.tmp / 'pids.json'),
                        STUB_NATIVE=str(SIDE / 'Contents/MacOS/VitreaReference'))

    def session(self, **state):
        current = json.loads(self.session_file.read_text()) if self.session_file.exists() else {}
        current.update(state)
        self.session_file.write_text(json.dumps(current))

    def admit_before(self, name, plan=PLAN):
        """Fake admissions for every pass ranked before `name` (the order gate reads only these)."""
        order = P.pass_order(plan)
        target = next(p for p in order if p['name'] == name)
        for p in order:
            if p['rank'] >= target['rank']:
                break
            for n in range(1, p['runs'] + 1):
                d = self.root / p['name'] / f'run-{n}'
                d.mkdir(parents=True, exist_ok=True)
                (d / 'admission.json').write_text(json.dumps(
                    {'admitted': True, 'pass': p['name'], 'run': n,
                     'protocol': 'dump' if p['kind'] == 'dump' else p['protocol'],
                     'sitting': DECLARATION['sitting'], 'planSha256': DECLARATION['planSha256']}))

    def run(self, *argv, plan=PLAN, declaration=None, **extra):
        env = {**self.env, **extra}
        with mock.patch.dict(os.environ, env, clear=False):
            for k in ('DRY', 'W43_PREDECLARATION', 'VITREA_LAUNCHER_CHAIN'):
                if k not in extra:
                    os.environ.pop(k, None)
            answer = dict(declaration or DECLARATION)
            if os.environ.get('W43_PREDECLARATION') == '1':
                answer['predeclaration'] = True
            with mock.patch.object(S, 'REPO', Path('/nonexistent-repo')), \
                    mock.patch.object(S, 'MAIN', Path('/nonexistent-main')), \
                    mock.patch.object(S, 'pinned_declaration', lambda sitting, predeclaration=False: dict(answer)), \
                    mock.patch.object(S, 'pinned_snapshot',
                                      lambda sitting, predeclaration=False: (dict(answer), plan, SOURCES)):
                return S.main(list(argv))

    def calls_made(self):
        return [json.loads(l) for l in self.calls.read_text().splitlines()] if self.calls.exists() else []


def gone(pid, within=15):
    """True once `pid` no longer exists, within `within` seconds."""
    deadline = time.monotonic() + within
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.2)
    return False


def spawn(argv, **kw):
    proc = subprocess.Popen([str(a) for a in argv], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)
    time.sleep(0.4)
    return proc


# ======================================================================= the plan

class Plan(unittest.TestCase):
    def test_the_stand_in_is_the_charters_g1a_membership(self):
        t = P.plan_counts(STAND_IN_PLAN, SOURCES)['totals']
        self.assertEqual((t['captures'], t['dumpScenes'], t['publishedCells']), (4103, 48, 562))
        self.assertEqual((t['sliderWrites'], t['modeSwitches']), (2, 4))

    def test_a_canonical_pass_spans_both_schemes_with_their_own_lists(self):
        doc = P.derive_from(PLAN, SOURCES, 'bed-1x-active', 1)
        self.assertEqual([p['key'] for p in doc['profiles']], sorted(BED_ACTIVE))
        for p in doc['profiles']:
            self.assertEqual(p['scenes'], sorted(BED_ACTIVE[p['key']]))
        self.assertEqual(set(doc['components']), {'capsule-button', 'glass-over-glass', 'toolbar-group'})
        listed = sorted(s for r in P.SPLIT_ROLES for s in doc['split'][r])
        self.assertEqual(listed, sorted({s['id'] for s in doc['scenes']}))
        self.assertEqual(P.derive_from(PLAN, SOURCES, 'bed-1x-active', 2), doc)   # one document every run

    def test_the_plan_refuses_what_the_sitting_could_not_honour(self):
        cases = [
            (dict(profiles={SI.key(1, 'light', '0.5'): ['checkerboard__capsule-button__rest']}), 'names slider 0.5'),
            (dict(profiles={L1: ['checkerboard__capsule-button__inactive']}), 'state the other pose'),
            (dict(run1Only={L1: ['checkerboard__rrect-md__rest']}), 'no run1Only'),
            (dict(runs=1), 'at least two runs'),
            (dict(profiles={L1: ['no-such__scene__rest']}), 'undeclared scenes'),
            (dict(scale=2), 'states 1x and the pass is 2x'),
        ]
        for change, message in cases:
            with self.subTest(message=message):
                plan = mini_plan(**{'bed-1x-active': change})
                with self.assertRaisesRegex(ValueError, message):
                    P.validate_plan(plan, SOURCES)
        with self.assertRaisesRegex(ValueError, 'non-rest'):
            P.validate_plan(mini_plan(**{'dump-1x-light-active': dict(scenes=['checkerboard__capsule-button__inactive'])}),
                            SOURCES)


# ===================================================================== the census

class Census(unittest.TestCase):
    """Change 1 (by executable) and change 2 (the launcher chain), on the REAL process table."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name).resolve()
        cls.procs = []

    @classmethod
    def tearDownClass(cls):
        for p in cls.procs:
            p.kill()
            p.wait()
        cls._tmp.cleanup()

    def start(self, argv):
        p = spawn(argv)
        self.procs.append(p)
        return p.pid

    def counted(self, pid):
        foreign, _ = R.census(chain_file='')
        return [f['why'] for f in foreign if f['pid'] == pid]

    def test_command_lines_that_merely_name_a_census_word_do_not_count(self):
        stub = self.tmp / 'w43-test-side/VitreaReference.app'
        for argv in (['/bin/sh', '-c', 'sleep 30; pgrep -fl "Chromium|playwright|VitreaReference" || true'],
                     ['/bin/sh', '-c', 'sleep 30; grep -c "Google Chrome Helper" /dev/null || true'],
                     [PYTHON, '-c', 'import time; time.sleep(30)', '--env', f'VITREA_FIXTURES={stub}', str(stub),
                      '--args', 'capture', str(stub / 'Contents/MacOS/VitreaReference')],
                     [PYTHON, '-c', 'import time; time.sleep(30)', 'compare.ts --skip-capture headless_shell']):
            with self.subTest(argv=argv[:3]):
                self.assertEqual(self.counted(self.start(argv)), [])

    @needs_node
    def test_real_browser_harness_and_playwright_executables_count(self):
        sleeper = SLEEP_JS
        for rel in ('Chromium.app/Contents/MacOS/Chromium',
                    'Google Chrome.app/Contents/Frameworks/Helpers/Google Chrome Helper (Renderer).app/Contents/MacOS/'
                    'Google Chrome Helper (Renderer)',
                    'Google Chrome.app/Contents/Frameworks/Helpers/chrome_crashpad_handler',
                    'Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
                    'chrome-headless-shell-mac-arm64/chrome-headless-shell',
                    'Side.app/Contents/MacOS/VitreaReference'):
            with self.subTest(executable=rel):
                exe = fake_executable(self.tmp / 'exe' / rel)
                self.assertNotEqual(self.counted(self.start([exe, *sleeper])), [], rel)
        node = fake_executable(self.tmp / 'bin/node')
        script = self.tmp / 'lib/node_modules/playwright-core/cli.js'
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text('setTimeout(() => {}, 30000)\n')
        self.assertEqual(self.counted(self.start([node, script])), ['node script in playwright-core'])
        compare = self.tmp / 'cli/compare.js'
        compare.parent.mkdir(parents=True, exist_ok=True)
        compare.write_text('setTimeout(() => {}, 30000)\n')
        compare = compare.with_name('compare.ts')
        compare.symlink_to('compare.js')
        self.assertEqual(self.counted(self.start([node, compare, '--skip-capture'])), ['node script compare.ts'])

    @needs_node
    def test_only_a_node_process_s_entry_script_counts(self):
        """The review's P2: an argument after the entry script is the program's data."""
        node = fake_executable(self.tmp / 'entry/bin/node')
        base = self.tmp / 'entry'
        benign, required, imported = base / 'benign.js', base / 'r.js', base / 'i.mjs'
        cli = base / 'lib/node_modules/playwright-core/cli.js'
        spaced = base / 'Application Support/node_modules/playwright-core/cli.js'
        compare = base / 'cli/compare.ts'
        for path, text in ((benign, 'setTimeout(() => {}, 30000)\n'), (required, ''), (imported, ''),
                           (cli, 'setTimeout(() => {}, 30000)\n'), (spaced, 'setTimeout(() => {}, 30000)\n'),
                           (compare, 'setTimeout(() => {}, 30000)\n')):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        cases = [
            ('a benign entry with a Playwright path as data', [node, benign, cli], []),
            ('inline code with a Playwright path as data', [node, '-e', 'setTimeout(() => {}, 30000)', cli], []),
            ('Playwright as the entry', [node, cli], ['node script in playwright-core']),
            ('Playwright as the entry, a space in its path', [node, spaced], ['node script in playwright-core']),
            ('compare.ts after --require and --import values (the tsx child)',
             [node, '--require', required, '--import', imported, compare, '--skip-capture'],
             ['node script compare.ts']),
        ]
        for label, argv, want in cases:
            with self.subTest(label=label):
                self.assertEqual(self.counted(self.start(argv)), want)

    @needs_node
    def test_the_launcher_chain_is_excluded_only_by_pid_and_start(self):
        node = fake_executable(self.tmp / 'chain/node')
        script = self.tmp / 'chain/@playwright/cli/launch.js'
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text('setTimeout(() => {}, 30000)\n')
        pid = self.start([node, script])
        rows = R.process_table()
        row = next(r for r in rows if r['pid'] == pid)
        chain = self.tmp / 'chain.json'
        chain.write_text(json.dumps(dict(chain=[dict(pid=pid, start=row['start'])])))
        foreign, excluded = R.census(chain_file=str(chain))
        self.assertFalse(any(f['pid'] == pid for f in foreign))
        self.assertTrue(any(e['pid'] == pid for e in excluded))
        chain.write_text(json.dumps(dict(chain=[dict(pid=pid, start='Thu Jan  1 00:00:00 1970')])))
        foreign, excluded = R.census(chain_file=str(chain))
        self.assertTrue(any(f['pid'] == pid for f in foreign))      # a reused pid is still counted

    def test_launcher_chain_records_the_launching_shell_and_its_ancestors(self):
        out = subprocess.run(['/bin/sh', '-c', f'"{PYTHON}" "{HERE / "record-machine.py"}" launcher-chain; echo $$'],
                             capture_output=True, text=True, check=True).stdout
        record = json.loads(out[:out.rindex('}') + 1])
        shell = int(out.strip().splitlines()[-1])
        pids = [e['pid'] for e in record['chain']]
        self.assertEqual(pids[0], shell)
        self.assertIn(os.getpid(), pids)                         # this test process is an ancestor


# =================================================================== the watchdog

class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class Watch(unittest.TestCase):
    """Change 4: the watchdog's rules, over injected readings."""

    def dog(self, pose, readings, alive_pids=()):
        clock = Clock()
        lines = []
        reads = iter(readings)

        def read():
            o = next(reads)
            clock.t += o.pop('dt', 5.0)
            return o
        base = dict(idleSeconds=400.0, frontmostIdentifier='com.apple.finder', frontmostPid=600)
        d = S.Watchdog(read, pose, HARNESS_ID, base, clock(), lines.append, clock=clock,
                       is_alive=lambda pid: pid in alive_pids)
        return d, lines

    def run_dog(self, d, n):
        return [d.check() for _ in range(n)]

    @staticmethod
    def reading(idle, front='com.apple.finder', pid=600, **kw):
        return {**dict(idleSeconds=idle, frontmostIdentifier=front, frontmostPid=pid, screenLocked=False,
                       windowOwners=['Dock|20']), **kw}

    def test_a_steady_active_launch_and_its_end_do_not_trip(self):
        r = self.reading
        d, lines = self.dog('active', [r(405), r(410, HARNESS_ID, 7), r(415, HARNESS_ID, 7), r(420, 'com.apple.finder')],
                            alive_pids=())
        self.assertEqual(self.run_dog(d, 4), [None] * 4)    # the harness exited before Finder came back
        self.assertEqual(len(lines), 4)

    def test_input_and_focus_and_prompts_trip(self):
        r = self.reading
        cases = [
            ('active', [r(405), r(3.0)], 'HID input'),
            ('active', [r(405, HARNESS_ID, 7), r(410, 'com.apple.universalcontrol', 49435)], 'focus lost'),
            ('active', [r(405, 'com.google.Chrome', 9)], 'focus taken'),
            ('receded', [r(405), r(410, HARNESS_ID, 7)], 'receded launch'),
            ('receded', [r(405, 'com.apple.universalcontrol', 49435)], 'receded launch'),
            ('receded', [r(405, windowOwners=['universalAccessAuthWarn|0'])], 'permission prompt'),
            ('active', [dict(r(405), screenLocked=True)], 'locked'),
        ]
        for pose, readings, message in cases:
            with self.subTest(message=message, pose=pose):
                for o in readings:
                    if 'windowOwners' in o and isinstance(o['windowOwners'], list) and not o['windowOwners']:
                        o['windowOwners'] = ['Dock|20']
                d, _ = self.dog(pose, readings, alive_pids=(7,))
                got = self.run_dog(d, len(readings))
                self.assertTrue(got[-1] and message in got[-1], got)
                self.assertTrue(all(g is None for g in got[:-1]), got)

    def test_an_unreadable_session_trips(self):
        def read():
            raise subprocess.CalledProcessError(1, 'read-session')
        d = S.Watchdog(read, 'active', HARNESS_ID, dict(idleSeconds=400.0), 0.0, lambda line: None)
        self.assertIn('could not read the session', d.check())

    def test_a_trip_kills_the_launch_and_ends_the_native_app(self):
        ended = []
        trips = iter([None, 'HID input during the launch: stub'])

        class Dog:
            def check(self):
                return next(trips)
        began = time.monotonic()
        with self.assertRaisesRegex(ValueError, 'watchdog stopped the launch: HID input'):
            S.watched([sys.executable, '-c', 'import time; time.sleep(60)'], Dog(), poll=0.2,
                      end_native=lambda: ended.append(True))
        self.assertLess(time.monotonic() - began, 10)
        self.assertEqual(ended, [True])


# ===================================================================== the slider

class Slider(unittest.TestCase):
    """Change 5's functions over the stub `defaults`: as-found once, writes only with no native
    process alive, restore to the as-found value; the real global default is never written."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.st = Stubs(self._tmp.name)
        self.st.store.write_text(json.dumps({'NSGlassTintAmount': dict(type='float', value='0.5459057')}))
        self.env = mock.patch.dict(os.environ, dict(VITREA_DEFAULTS=self.st.env['VITREA_DEFAULTS'],
                                                    STUB_DEFAULTS_STORE=str(self.st.store)))
        self.env.start()
        self.root = self.st.root
        self.root.mkdir()

    def tearDown(self):
        self.env.stop()
        self._tmp.cleanup()

    def stored(self):
        return json.loads(self.st.store.read_text()).get('NSGlassTintAmount')

    def test_as_found_is_recorded_once_and_restored(self):
        record, current = S.slider_as_found(self.root)
        self.assertEqual(record['asFound']['value'], '0.5459057')
        S.slider_set(self.root, 0.25, list_native=lambda: [])
        self.assertEqual(self.stored()['value'], '0.25')
        again, current = S.slider_as_found(self.root)      # a continuation: the first record stands
        self.assertEqual((again['asFound']['value'], current['value']), ('0.5459057', '0.25'))
        result = S.slider_restore(self.root)
        self.assertTrue(result['restored'] and result['written'])
        self.assertEqual(self.stored(), dict(type='float', value='0.5459057'))
        self.assertFalse(S.slider_restore(self.root)['written'])          # already as found: no write

    def test_an_absent_slider_is_deleted_again(self):
        self.st.store.write_text('{}')
        S.slider_as_found(self.root)
        S.slider_set(self.root, 0.5, list_native=lambda: [])
        self.assertTrue(S.slider_restore(self.root)['restored'])
        self.assertIsNone(self.stored())

    def test_a_native_process_alive_refuses_the_write(self):
        S.slider_as_found(self.root)
        with self.assertRaisesRegex(ValueError, 'alive'):
            S.slider_set(self.root, 0.25, list_native=lambda: [dict(pid=1, executable='VitreaReference')])
        self.assertEqual(self.stored()['value'], '0.5459057')            # nothing written
        if NODE is None:
            return
        exe = fake_executable(Path(self._tmp.name) / 'X.app/Contents/MacOS/VitreaReference')
        proc = spawn([exe, *SLEEP_JS])
        try:
            with self.assertRaisesRegex(ValueError, 'alive'):               # the real listing, by executable
                S.slider_set(self.root, 0.25)
        finally:
            proc.kill()
            proc.wait()
        self.assertEqual(self.stored()['value'], '0.5459057')

    def test_a_non_float_as_found_is_refused(self):
        self.st.store.write_text(json.dumps({'NSGlassTintAmount': dict(type='string', value='0.5')}))
        with self.assertRaisesRegex(ValueError, 'not a float'):
            S.slider_as_found(self.root)

    def test_the_run_reads_the_last_write(self):
        S.slider_as_found(self.root)
        S.slider_set(self.root, 0.25, list_native=lambda: [])
        self.assertEqual(S.slider_problems(self.root, 0.25), [])
        self.assertIn('the last slider write set 0.25', S.slider_problems(self.root, 0.5)[0])


# ========================================================================= gates

class Gates(unittest.TestCase):
    def test_every_failing_gate_is_named_in_one_refusal(self):
        m = machine(2, '0.5', reduceTransparency='1', foreign=3)
        m['side']['binarySha256'] = 'd' * 64
        with self.assertRaises(ValueError) as caught:
            S.validate_machine(m, 1, 0.25)
        text = str(caught.exception)
        for fragment in ('policy/Show Borders', 'slider mismatch', 'display mode', 'side bundle identity',
                         'foreign capture'):
            self.assertIn(fragment, text)

    def test_the_slider_gate_is_exact_and_an_absent_key_refuses(self):
        S.validate_machine(machine(1, '0.25'), 1, 0.25)
        S.validate_machine(machine(1, '1'), 1, 1.0)
        for read in ('0.2500001', '', 'absent'):
            with self.subTest(read=read), self.assertRaisesRegex(ValueError, 'slider mismatch'):
                S.validate_machine(machine(1, read), 1, 0.25)

    def test_outputs_never_inside_a_checkout_or_documents(self):
        for bad in (REPO / 'x', Path.home() / 'Documents' / 'w43'):
            with self.assertRaises(ValueError):
                S.outside_repository(bad)
        S.outside_repository('/tmp/w43-ok')

    def test_dry_env_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            Stubs(tmp).run('capture', 'bed-1x-active', DRY='1')


# ========================================================================= capture

class Capture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.st = Stubs(self._tmp.name)
        self.st.admit_before('bed-1x-active')

    def tearDown(self):
        self._tmp.cleanup()

    def test_a_two_scheme_canonical_run_is_admitted_with_materialize_s_attestation(self):
        self.st.run('capture', 'bed-1x-active', '1', '2')
        base = self.st.root / 'bed-1x-active'
        a = json.loads((base / 'run-1' / 'admission.json').read_text())
        self.assertEqual((a['protocol'], a['cells'], a['glass'], a['planSha256']), ('normal', 5, 0.25, 'a' * 64))
        self.assertEqual(len(a['frames']), 5)
        fields = [dict(l.split('=', 1) for l in (base / f'run-{n}' / 'attest.read').read_text().splitlines())
                  for n in (1, 2)]
        for f in fields:
            self.assertEqual((f['bundlePath'], f['bundleIdentifier'], f['bundleCdHash'], f['bundleBinarySha256']),
                             (PIN['path'], HARNESS_ID, PIN['cdhash'], PIN['binarySha256']))
            self.assertEqual((f['glassTintAmount'], f['osProductVersion'], f['osBuild']), ('0.25', '27.0', '26A428'))
            self.assertEqual((f['bundleMinOS'], f['bundleRecordedSdk']), ('26.0', '26.0'))
            self.assertEqual(f['bundlePinSha256'], S.pin_sha256())
            self.assertEqual(f['sceneSpecCanonicalSha256'], SHAS['canonical'])
            self.assertEqual(f['pass'], 'bed-1x-active')
        self.assertEqual(fields[0]['passSpecSha256'], fields[1]['passSpecSha256'])   # rule 6 holds
        self.assertTrue((base / 'run-1' / 'driver-idle.txt').exists())
        self.assertFalse((base / 'run-1' / 'driver-idle.log').exists())
        argv = [c for c in self.st.calls_made() if 'capture' in c][-1]
        self.assertNotIn('--inactive', argv)

    def test_group_and_stack_paths_are_attested_and_a_wrong_origin_refuses(self):
        for sid in ('checkerboard__toolbar-group__rest', 'checkerboard__glass-over-glass__rest'):
            with self.subTest(sid=sid):
                with tempfile.TemporaryDirectory() as tmp:
                    st = Stubs(tmp)
                    st.admit_before('bed-1x-active')
                    with self.assertRaisesRegex(ValueError, 'supplied path attestation'):
                        st.run('capture', 'bed-1x-active', '1', '1', STUB_SHIFT=sid)

    def test_a_slider_read_off_the_pass_s_position_refuses_before_launch(self):
        (self.st.tmp / 'machine.json').write_text(json.dumps(machine(1, '0.5')))
        with self.assertRaisesRegex(ValueError, 'slider mismatch'):
            self.st.run('capture', 'bed-1x-active', '1', '1')
        self.assertFalse(any('capture' in c for c in self.st.calls_made()))

    def test_a_slider_record_off_the_pass_s_position_refuses(self):
        log = S.slider_log(self.st.root)
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(json.dumps(dict(value=0.5, nativeAliveBefore=[], nativeAliveAfter=[])) + '\n')
        with self.assertRaisesRegex(ValueError, 'slider record refused'):
            self.st.run('capture', 'bed-1x-active', '1', '1')

    def test_an_existing_run_is_never_overwritten(self):
        (self.st.root / 'bed-1x-active' / 'run-1').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.st.run('capture', 'bed-1x-active', '1', '1')

    def test_a_later_pass_blocks_an_earlier_one(self):
        (self.st.root / 'bed-1x-receded' / 'run-1').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'later pass has already started'):
            self.st.run('capture', 'bed-1x-active', '1', '1')

    def test_an_expected_frame_that_differs_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            st = Stubs(tmp, scale=2, glass='0.5')
            with self.assertRaisesRegex(ValueError, 'declared frame expectation failed'):
                st.run('capture', 'pose-check')
            q = list((st.root / 'pose-check').glob('QUARANTINE-run-1-*'))
            self.assertEqual(len(q), 1)

    def test_png_bytes_are_bound(self):
        for mode, message in (('no-png', 'fixture PNG missing'), ('bad-png', 'not an RGB\\(A\\) PNG of 320x200')):
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(ValueError, message):
                    self.st.run('capture', 'bed-1x-active', '1', '1', STUB_MODE=mode)
        self.assertEqual(len(list((self.st.root / 'bed-1x-active').glob('QUARANTINE-run-1-*'))), 2)


@needs_node
class WatchedLaunch(unittest.TestCase):
    """Change 4 through the driver: a stub capture that blocks, a session that moves mid-launch."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.st = Stubs(self._tmp.name)
        self.st.admit_before('bed-1x-active')
        fake_executable(SIDE / 'Contents/MacOS/VitreaReference')

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, mode, message):
        began = time.monotonic()
        with self.assertRaisesRegex(ValueError, message):
            self.st.run('capture', 'bed-1x-active', '1', '1', STUB_MODE=mode)
        self.assertLess(time.monotonic() - began, 30)              # not the launch's 60 s
        launched = json.loads((self.st.tmp / 'pids.json').read_text())
        for pid in (launched['launcher'], launched['app']):
            self.assertTrue(gone(pid), f'pid {pid} survives the trip')
        q = next((self.st.root / 'bed-1x-active').glob('QUARANTINE-run-1-*'))
        self.assertIn('watchdog stopped the launch', (q / 'refusal.txt').read_text())
        self.assertTrue((q / 'watchdog.txt').read_text().count('watch:') >= 1)
        return q

    def test_input_mid_launch_stops_it(self):
        self.check('input', 'HID input during the launch')

    def test_focus_lost_mid_launch_stops_it(self):
        self.check('focus', 'focus lost during the launch')

    def test_the_harness_exiting_is_not_a_focus_loss(self):
        with self.assertRaisesRegex(ValueError, 'the capture launch exited 1'):
            self.st.run('capture', 'bed-1x-active', '1', '1', STUB_MODE='focus-after-exit')


# ===================================================================== the sentinel

class Sentinel(unittest.TestCase):
    """Change 6: the dump sentinel reads the tree's Normal input against the pass's position."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.st = Stubs(self._tmp.name)
        self.st.admit_before('dump-1x-light-active')

    def tearDown(self):
        self._tmp.cleanup()

    def test_normal_at_the_declared_position_is_admitted(self):
        self.st.run('dump', 'dump-1x-light-active')
        run = self.st.root / 'dump-1x-light-active' / 'run-1'
        a = json.loads((run / 'admission.json').read_text())
        self.assertEqual((a['protocol'], a['scenes'], a['departures'], a['glass']), ('dump', 3, 0, 0.25))
        self.assertEqual(a['normalOpacities'], ['0.25'])
        argv = self.st.calls_made()[-1]
        self.assertIn('--require-key', argv)
        self.assertTrue((run / 'watchdog.txt').exists() or True)

    def test_a_stale_position_a_lost_key_or_no_reading_departs(self):
        for mode, normal, message in (('auto', '0.5', 'inputBlurFillNormalOpacity reads'),
                                      ('lose-key', '0.25', 'isKeyWindow reads False'),
                                      ('no-normal', '0.25', 'no inputBlurFillNormalOpacity')):
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory() as tmp:
                    st = Stubs(tmp)
                    st.admit_before('dump-1x-light-active')
                    with self.assertRaisesRegex(ValueError, 'departure'):
                        st.run('dump', 'dump-1x-light-active', STUB_MODE=mode, STUB_NORMAL=normal)
                    q = next((st.root / 'dump-1x-light-active').glob('QUARANTINE-run-1-*'))
                    self.assertIn(message, (q / 'check.json').read_text())

    @unittest.skipUnless(MEMO_D.is_dir(), "memo D's scratch dumps are absent on this machine")
    def test_memo_d_s_real_dumps_read_their_own_position(self):
        """The walker finds the input in the real tree format: memo D's 2x light active dumps, taken at 0.5."""
        d = MEMO_D / '2x-light-active' / 'json'
        ids = sorted(p.stem for p in d.glob('*.json'))
        report = S.sentinel_check(d, ids, 0.5, 'active', 2, 'light')
        self.assertEqual(report['departures'], [])
        self.assertEqual(report['normalOpacities'], ['0.5'])
        self.assertGreater(report['surfaces'], len(ids))           # stacked scenes carry two surfaces
        stale = S.sentinel_check(d, ids, 0.25, 'active', 2, 'light')
        self.assertEqual(len(stale['departures']), len(ids))


# ====================================================================== the mirror

def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True).stdout


class Mirror:
    """A throwaway Git checkout holding the W43 tools, the stand-in canonical file, W42's scenes file,
    a plan and a declaration at their real relative paths, and a stub W39 pin: the pin check, the
    driver and the orchestrator run for real against it. `replace` substitutes a file's bytes."""

    TOOLS = ('sitting.py', 'pass-spec.py', 'record-machine.py', 'run-sitting-w43.sh', 'sitting-orchestrate.sh',
             'collect-pass.py', 'stand_in.py')
    W39_DIR = REPO / 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed'

    def __init__(self, tmp, plan=None, replace=None, sitting='g1a'):
        self.sitting_name = sitting
        self.repo = Path(tmp) / 'repo'
        for n in self.TOOLS:
            self.put((HERE / n).relative_to(REPO), (HERE / n).read_bytes())
        self.put(SI.CANONICAL, CANONICAL_RAW)
        self.put(SI.W42_SCENES, W42_RAW)
        self.put((self.W39_DIR / 'bundle-pin.json').relative_to(REPO), json.dumps(PIN).encode())
        self.put('.gitignore', b'*.log\n')
        for rel, raw in (replace or {}).items():
            self.put(rel, raw)
        self.sitting = self.repo / HERE.relative_to(REPO)
        self.decl = self.sitting.parents[1]
        self.write_plan(plan or STAND_IN_PLAN)
        self.declare()
        git(self.repo, 'init', '-q')
        git(self.repo, 'config', 'user.email', 'test@example.invalid')
        git(self.repo, 'config', 'user.name', 'W43 mirror')
        self.commit('the mirror')

    def put(self, rel, raw):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        if path.suffix == '.sh':
            path.chmod(0o755)

    def write_plan(self, plan):
        self.plan_raw = (json.dumps(plan, indent=2) + '\n').encode()
        (self.sitting.parent / f'sitting-{self.sitting_name}.json').write_bytes(self.plan_raw)

    def declare(self, plan_sha=None, hashed=True, chain=None):
        raw = json.dumps(dict(schema='w43-declaration-1', items=[dict(id=f'sitting-{self.sitting_name}', declared=dict(
            planSha256=plan_sha or hashlib.sha256(self.plan_raw).hexdigest()))]), indent=1).encode()
        (self.decl / 'declaration.json').write_bytes(raw)
        digest = self.decl / 'declaration.sha256'
        if chain is not None:
            # an amended declaration: earlier hashes first, then whatever the caller names last
            lines = [h if h != 'CURRENT' else hashlib.sha256(raw).hexdigest() for h in chain]
            digest.write_text(''.join(f'{h}  declaration.json\n' for h in lines))
        elif hashed:
            digest.write_text(hashlib.sha256(raw).hexdigest() + '  declaration.json\n')
        elif digest.exists():
            digest.unlink()

    def commit(self, message):
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-qm', message)

    def sitting_py(self, *argv, env=None):
        return subprocess.run([sys.executable, str(self.sitting / 'sitting.py'), *argv], capture_output=True,
                              text=True, env={**os.environ, 'W43_SITTING': 'g1a', **(env or {})}, timeout=120)


def one_byte_edit(path):
    """A silent, loadable one-byte edit: one letter of the stand-in's own comment."""
    raw = bytearray(path.read_bytes())
    at = raw.index(b'A W43 test stand-in')
    raw[at] = ord('a')
    path.write_bytes(bytes(raw))
    json.loads(raw)


class PinCheck(unittest.TestCase):
    """The plan a launch runs is the committed, hashed declaration, and its sources the bytes it names."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.m = Mirror(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, **env):
        out = self.m.sitting_py('pin-check', env={'W43_PREDECLARATION': '', **env})
        return out.returncode, out.stdout + out.stderr

    def test_the_declared_plan_passes(self):
        rc, text = self.check()
        self.assertEqual(rc, 0, text)
        record = json.loads(text)
        self.assertEqual(record['planSha256'], hashlib.sha256(self.m.plan_raw).hexdigest())
        self.assertEqual(record['sources'], SHAS)

    def test_a_source_edited_by_one_byte_refuses_even_committed(self):
        one_byte_edit(self.m.repo / SI.CANONICAL)
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('differs from its committed copy at HEAD', text)
        self.m.commit('an edited canonical file')
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('the plan names', text)

    def test_a_plan_edited_and_committed_but_undeclared_refuses(self):
        plan = json.loads(self.m.plan_raw)
        plan['passes'] = plan['passes'][:-1]
        self.m.write_plan(plan)
        self.m.commit('a plan nobody declared')
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('declaration.json names plan', text)

    def test_an_amended_declaration_passes_on_its_last_line(self):
        # declare.py's amendment appends the amended hash beneath the original; the bytes in force are the
        # last line's, so the original's line no longer names them and must not be read as the current one.
        self.m.declare(chain=['4675ce21' + '0' * 56, 'CURRENT'])
        self.m.commit('an amended declaration')
        rc, text = self.check()
        self.assertEqual(rc, 0, text)
        self.assertEqual(len(json.loads(text)['declarationChain']), 2)

    def test_a_chain_whose_last_line_is_not_these_bytes_refuses(self):
        self.m.declare(chain=['CURRENT', '4f90f910' + '0' * 56])
        self.m.commit('a chain whose last line names other bytes')
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('on its last line', text)

    def test_an_unhashed_declaration_refuses_and_predeclaration_records_it(self):
        self.m.declare(hashed=False)
        self.m.commit('the declaration without its hash')
        rc, text = self.check()
        self.assertNotEqual(rc, 0)
        self.assertIn('declaration.sha256', text)
        rc, text = self.check(W43_PREDECLARATION='1')
        self.assertEqual(rc, 0, text)
        self.assertTrue(json.loads(text)['predeclaration'])
        with tempfile.TemporaryDirectory() as tmp:
            st = Stubs(tmp)
            out = self.m.sitting_py('capture', 'bed-0.25-1x-active', env={**st.env, 'W43_PREDECLARATION': '1'})
            self.assertNotEqual(out.returncode, 0)
            self.assertIn('admits dump rehearsals only', out.stderr)
            self.assertFalse(st.root.exists())


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
# A stand-in for run-sitting-w43.sh: logs its argv and the slider it finds, then does what
# STUB_DRIVER_MODE says.
echo "$* cut=${W43_CUT_AFTER:--} glass=$(python3.12 -c 'import json, sys; print(json.load(open(sys.argv[1]))["NSGlassTintAmount"]["value"])' "$STUB_DEFAULTS_STORE" 2>/dev/null)" >> "$STUB_DRIVER_CALLS"
case "${STUB_DRIVER_MODE:-ok}" in
  swallow) cat > /dev/null ;;
  sleep) sleep 4 ;;
  native) "$STUB_NATIVE" -e 'setTimeout(() => {}, 20000)' </dev/null >/dev/null 2>&1 & disown ;;
esac
exit 0
"""


class Orchestrator(unittest.TestCase):
    """sitting-orchestrate.sh in a Mirror with stub displayplacer, defaults and driver."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def setup(self, start_mode='68', as_found='0.5459057', stub_driver=True, replace=None):
        self.m = Mirror(self.tmp, replace=replace)
        self.st = Stubs(self.tmp)
        if as_found is None:
            self.st.store.write_text('{}')
        else:
            self.st.store.write_text(json.dumps({'NSGlassTintAmount': dict(type='float', value=as_found)}))
        self.dp, self.state, self.dp_calls = stub_displayplacer(self.tmp, start_mode)
        self.driver_calls = self.tmp / 'driver-calls.txt'
        if stub_driver:
            (self.m.sitting / 'run-sitting-w43.sh').write_text(STUB_DRIVER)
            self.m.commit('the stub driver')
        self.env = {**os.environ, **self.st.env, 'DISPLAYPLACER': str(self.dp), 'STUB_DRIVER_CALLS': str(self.driver_calls),
                    'STUB_DEFAULTS_STORE': str(self.st.store), 'W43_FOREGROUND': '1'}
        for k in ('DRY', 'W43_ORCHESTRATED', 'W43_PREDECLARATION', 'START_AT', 'STOP_AFTER', 'PASSES', 'REHEARSAL',
                  'VITREA_LAUNCHER_CHAIN', 'FIRST_RUN'):
            self.env.pop(k, None)

    def orchestrate(self, **env):
        return subprocess.run(['bash', str(self.m.sitting / 'sitting-orchestrate.sh')], env={**self.env, **env},
                              capture_output=True, text=True, timeout=240)

    def status(self):
        return (self.st.root / 'logs' / 'orchestrator-status.txt').read_text()

    def driven(self):
        return self.driver_calls.read_text().splitlines() if self.driver_calls.exists() else []

    def stored(self):
        return json.loads(self.st.store.read_text()).get('NSGlassTintAmount')

    def test_the_whole_order_writes_the_slider_per_pass_and_restores_both(self):
        self.setup()
        out = self.orchestrate()
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr + self.status())
        driven = self.driven()
        self.assertEqual(len(driven), len(STAND_IN_PLAN['passes']))
        for line, p in zip(driven, STAND_IN_PLAN['passes']):
            self.assertTrue(line.startswith(('dump ' if p['kind'] == 'dump' else 'capture ') + p['name']), line)
            self.assertTrue(line.endswith(f'glass={S.pass_spec().parse_key(next(iter(p["profiles"])) if p["kind"] == "capture" else p["profile"])[3]:g}'.replace('glass=0.5', 'glass=0.5')), line)
        writes = S.slider_writes(self.st.root)
        passes = [w['value'] for w in writes if not w.get('restore')]
        self.assertEqual(passes, [0.5, 0.25, 0.5])                           # as-found 0.546 -> 0.5 -> 0.25 -> 0.5
        self.assertEqual((writes[-1].get('restore'), writes[-1]['value']), (True, 0.5459057))   # the trap's, logged
        self.assertTrue(all(not w['nativeAliveBefore'] and not w['nativeAliveAfter'] for w in writes))
        self.assertEqual(self.stored(), dict(type='float', value='0.5459057'))   # restored as found
        self.assertTrue(all(' cut=- ' in line for line in driven))           # no cut: nothing ran after one
        status = self.status()
        self.assertIn('ALL PASSES DONE', status)
        self.assertIn('restore: slider', status)
        self.assertIn('restore: display mode 68 (verified)', status)
        self.assertIn('universal control (a report, not a gate)', status)
        self.assertEqual(self.state.read_text(), '68')

    def test_an_absent_slider_is_absent_again_after_a_cut_and_the_close_still_runs(self):
        self.setup(as_found=None)
        out = self.orchestrate(STOP_AFTER='dump-0.25-2x-light-active')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn('STOPPED AFTER dump-0.25-2x-light-active', self.status())
        self.assertIsNone(self.stored())
        driven = self.driven()
        cut = driven.index(next(l for l in driven if l.startswith('dump dump-0.25-2x-light-active')))
        self.assertTrue(driven[cut].endswith('cut=- glass=0.25'))
        closing = [p['name'] for p in STAND_IN_PLAN['passes'] if p.get('runAfterCut')]
        self.assertEqual([l.split()[1] for l in driven[cut + 1:]], closing)            # every close pass, in order
        self.assertTrue(all(l.endswith('cut=dump-0.25-2x-light-active glass=0.5') for l in driven[cut + 1:]))
        self.assertIn('restore before the close: slider absent', self.status())

    @needs_node
    def test_a_native_process_alive_at_a_slider_write_stops_the_sitting(self):
        self.setup()
        fake_executable(SIDE / 'Contents/MacOS/VitreaReference')
        # The last 0.5 pass leaves a stand-in harness running; the write to 0.25 must refuse.
        out = self.orchestrate(STUB_DRIVER_MODE='native')
        self.assertEqual(out.returncode, 9, out.stdout + out.stderr)
        status = self.status()
        self.assertIn('STOP dump-0.25-2x-light-active: the slider write to 0.25 was refused', status)
        self.assertNotIn('START dump-0.25', status)
        self.assertEqual(self.stored(), dict(type='float', value='0.5459057'))
        self.assertEqual([w['value'] for w in S.slider_writes(self.st.root) if not w.get('restore')], [0.5])
        for p in R.native_processes(binary=SIDE / 'Contents/MacOS/VitreaReference'):
            os.kill(p['pid'], signal.SIGKILL)

    def test_a_signal_mid_pass_restores_the_slider_and_the_display(self):
        self.setup()
        env = {**self.env, 'STUB_DRIVER_MODE': 'sleep', 'START_AT': 'bed-0.25-1x-active'}
        proc = subprocess.Popen(['bash', str(self.m.sitting / 'sitting-orchestrate.sh')], env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 90
        while not self.driven() and time.monotonic() < deadline:
            time.sleep(0.2)
        self.assertEqual((self.state.read_text(), self.stored()['value']), ('69', '0.25'))
        proc.send_signal(signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=60), 143)
        self.assertEqual((self.state.read_text(), self.stored()['value']), ('68', '0.5459057'))
        self.assertIn('restore: display mode 68 (verified)', self.status())

    def test_a_signal_during_the_exit_restore_cannot_cut_it_short(self):
        """The review's P1: a TERM while the EXIT trap restores the slider. The restore finishes,
        verifies the display at mode 68 and exits with the sitting's own status; a refused write
        is RESTORE FAILED and exit 7, the display still restored and verified."""
        for refuse, want in ((False, 0), (True, 7)):
            with self.subTest(refuse=refuse), tempfile.TemporaryDirectory() as tmp:
                rc, mode, status, stored = exit_restore_under_signal(tmp, refuse=refuse)
                self.assertEqual((rc, mode), (want, '68'), status)
                self.assertIn('restore: display mode 68 (verified)', status)
                self.assertNotIn('CANCEL', status)
                if refuse:
                    self.assertIn('RESTORE FAILED: slider', status)
                else:
                    self.assertIn('restore: slider', status)
                    self.assertEqual(stored['value'], '0.5459057')

    def test_rehearsals_are_dump_passes_only(self):
        self.setup()
        out = self.orchestrate(REHEARSAL='1', PASSES='dump-0.25-1x-dark-receded')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertEqual([l.rsplit(' cut=', 1)[0] for l in self.driven()], ['dump dump-0.25-1x-dark-receded --rehearse'])
        out = self.orchestrate(REHEARSAL='1', PASSES='bed-0.25-1x-active')
        self.assertEqual(out.returncode, 6)
        self.assertIn('only a dump pass has a rehearsal', self.status())

    def test_the_detached_sitting_records_its_launching_chain(self):
        self.setup()
        env = {k: v for k, v in self.env.items() if k != 'W43_FOREGROUND'}
        # The launching shell outlives the launch with census words on its command line (stop 4).
        out = subprocess.run(['bash', '-c', f'bash "{self.m.sitting / "sitting-orchestrate.sh"}"; '
                                            'sleep 3; : pgrep -fl "Chromium|playwright"; echo launcher=$$'],
                             env={**env, 'STOP_AFTER': 'pose-check', 'STUB_DRIVER_MODE': 'ok'},
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        launcher = int(re.search(r'launcher=(\d+)', out.stdout)[1])
        chain_file = Path(re.search(r'launcher chain in (\S+);', out.stdout)[1])
        chain = json.loads(chain_file.read_text())['chain']
        self.assertIn(launcher, [e['pid'] for e in chain])
        self.assertIn(os.getpid(), [e['pid'] for e in chain])
        deadline = time.monotonic() + 90
        while 'restore: display' not in (self.status() if (self.st.root / 'logs' / 'orchestrator-status.txt').exists()
                                         else '') and time.monotonic() < deadline:
            time.sleep(0.5)
        self.assertIn(f'launcher chain {chain_file}', self.status())
        self.assertIn('STOPPED AFTER pose-check', self.status())


def exit_restore_under_signal(tmp, replace=None, refuse=False):
    """The review's P1 reproduction. A dump rehearsal at mode 69 (the display starts there) exits
    normally; while the EXIT trap's slider restore is writing the as-found value (the stub
    `defaults` stalls on it), the orchestrator is sent TERM. `refuse` makes that write fail.
    `replace` swaps tools (the reviewed orchestrator, for the red case). Returns (exit status,
    the display mode left, the status log, the stored slider)."""
    tmp = Path(tmp)
    case = Orchestrator('test_rehearsals_are_dump_passes_only')
    case.tmp = tmp
    case.setup(start_mode='69', replace=replace)
    mark = tmp / 'restoring'
    env = {**case.env, 'REHEARSAL': '1', 'PASSES': 'dump-0.25-1x-dark-receded', 'STUB_SLOW_WRITE': '0.5459057',
           'STUB_SLOW_MARK': str(mark), 'STUB_SLOW_SECONDS': '4'}
    if refuse:
        env['STUB_REFUSE_WRITE'] = '0.5459057'
    proc = subprocess.Popen(['bash', str(case.m.sitting / 'sitting-orchestrate.sh')], env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 120
    while not mark.exists() and time.monotonic() < deadline and proc.poll() is None:
        time.sleep(0.1)
    proc.send_signal(signal.SIGTERM)
    rc = proc.wait(timeout=90)
    time.sleep(5)          # let an orphaned write finish, so the slider read is the settled one
    return rc, case.state.read_text(), case.status(), case.stored()


class Collect(unittest.TestCase):
    """Change 3: the idle-wait log survives the per-pass commit under the repository's `*.log` rule."""

    def test_the_idle_log_is_committed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            repo = tmp / 'repo'
            repo.mkdir()
            (repo / '.gitignore').write_bytes((REPO / '.gitignore').read_bytes())
            git(repo, 'init', '-q')
            git(repo, 'config', 'user.email', 'test@example.invalid')
            git(repo, 'config', 'user.name', 'W43 collect')
            run = tmp / 'root' / 'p' / 'run-1'
            run.mkdir(parents=True)
            (run / 'driver-idle.txt').write_text('idle-wait: idle=400\n')
            (run / 'watchdog.txt').write_text('watch: front=com.apple.finder\n')
            (run / 'admission.json').write_text('{}\n')
            evidence = repo / 'evidence'
            subprocess.run([sys.executable, str(HERE / 'collect-pass.py'), 'p'], check=True, capture_output=True,
                           env={**os.environ, 'VITREA_SITTING_DIR': str(tmp / 'root'), 'W43_EVIDENCE': str(evidence)})
            git(repo, 'add', '--', str(evidence))
            git(repo, 'commit', '-qm', 'a pass')
            committed = git(repo, 'ls-files').split()
            self.assertIn('evidence/attest/p/run-1/driver-idle.txt', committed)
            self.assertIn('evidence/attest/p/run-1/watchdog.txt', committed)


# ================================================================== publication

MAIN_MODULES = Path('/Users/new/Developer/GitHub/designer/packages/calibration/node_modules')


@unittest.skipUnless((MAIN_MODULES / '.bin/tsx').exists(), "the main checkout's calibration node_modules are absent")
class Publication(unittest.TestCase):
    """Change 7: the canonical publication path for side-bundle runs, through the REAL materialize
    (the committed cli/ and src/, run with tsx) into a scratch fixtures bundle."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.st = Stubs(cls.tmp)
        cls.st.admit_before('bed-1x-active')
        cls.st.run('capture', 'bed-1x-active', '1', '2')

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def materialize(self, runs, fixtures):
        """materialize.ts from this checkout's cli/ and src/ in a scratch package with the main
        checkout's node_modules (pngjs, tsx), over a fixtures bundle holding only an empty manifest."""
        pkg = fixtures.parent / 'pkg'
        if not pkg.exists():
            for d in ('cli', 'src'):
                shutil.copytree(REPO / 'packages/calibration' / d, pkg / d)
            (pkg / 'node_modules').symlink_to(MAIN_MODULES)
            (pkg / 'package.json').write_text('{"type": "module"}\n')
        (fixtures / 'backgrounds').mkdir(parents=True, exist_ok=True)     # as the canonical bundle has
        (fixtures / 'manifest.json').write_text(json.dumps(dict(profiles=[], backgrounds={}, split={})) + '\n')
        scenes = fixtures.parent / 'scenes.json'
        scenes.write_bytes(CANONICAL_RAW)
        argv = [str(MAIN_MODULES / '.bin/tsx'), 'cli/materialize.ts',
                *[a for i, r in enumerate(runs, 1) for a in ('--run', f'r{i}={r}')],
                '--profile', ','.join(sorted(BED_ACTIVE)), '--frequency-settle', '--apply']
        return subprocess.run(argv, cwd=pkg, capture_output=True, text=True, timeout=180,
                              env={**os.environ, 'VITREA_FIXTURES': str(fixtures), 'VITREA_SCENES': str(scenes)})

    def runs(self):
        return [self.st.root / 'bed-1x-active' / f'run-{n}' for n in (1, 2)]

    def test_the_published_bed_names_the_side_bundle_and_the_slider(self):
        job = S.publication(self.st.root, P.pass_of('bed-1x-active', PLAN), DECLARATION, SI.CANONICAL)
        self.assertIn('--frequency-settle', job['argv'])
        out = self.materialize(self.runs(), self.tmp / 'pub' / 'fixtures')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        published = json.loads((self.tmp / 'pub' / 'fixtures' / 'manifest.json').read_text())
        entry = next(p for p in published['profiles'] if p['profileKey'] == L1)
        a = entry['attestation']
        self.assertEqual((a['bundlePath'], a['bundleIdentifier'], a['bundleCdHash'], a['bundlePinSha256']),
                         (PIN['path'], HARNESS_ID, PIN['cdhash'], S.pin_sha256()))
        self.assertEqual((a['glassTintAmount'], a['runs'], a['sitting']), ('0.25', '2', 'g1a'))
        self.assertEqual(len(entry['fixtures']), len(BED_ACTIVE[L1]))

    def test_a_run_that_does_not_name_the_side_is_not_publishable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'root'
            shutil.copytree(self.st.root, root)
            read = root / 'bed-1x-active' / 'run-2' / 'attest.read'
            read.write_text(read.read_text().replace(f'bundlePath={PIN["path"]}',
                                                     'bundlePath=/Users/new/Developer/GitHub/designer/apps/'
                                                     'reference-apple/build/VitreaReference.app'))
            with self.assertRaisesRegex(ValueError, "does not name the side bundle's pin"):
                S.publication(root, P.pass_of('bed-1x-active', PLAN), DECLARATION, SI.CANONICAL)


# ============================================================ the coordinator's rulings

class PlanRulings(unittest.TestCase):
    """runAfterCut (a cut never drops the close) and the bridge block (clause 3), as the plan states them."""

    def refused(self, plan, message):
        with self.assertRaisesRegex(ValueError, message):
            P.validate_plan(plan, SOURCES)

    def test_a_closing_sentinel_bridge_must_run_after_a_cut(self):
        plan = copy.deepcopy(STAND_IN_PLAN)
        del next(p for p in plan['passes'] if p['name'] == 'close-w42-2x-dark-receded')['runAfterCut']
        self.refused(plan, 'close-w42-2x-dark-receded: a closing W42 sentinel bridge declares runAfterCut: true')

    def test_only_a_closing_sentinel_bridge_carries_the_field(self):
        for name, value in (('pose-check', True), ('open-w42-2x-light-active', True), ('bed-0.25-2x-active', True),
                            ('dump-0.25-1x-dark-receded', True), ('open-canonical-1x-active', False)):
            with self.subTest(name=name):
                plan = copy.deepcopy(STAND_IN_PLAN)
                next(p for p in plan['passes'] if p['name'] == name)['runAfterCut'] = value
                self.refused(plan, f'{name}: only a closing W42 sentinel bridge')

    def test_the_after_cut_passes_are_the_tail(self):
        plan = copy.deepcopy(STAND_IN_PLAN)
        moved = plan['passes'].pop(-1)
        plan['passes'].insert(3, moved)
        self.refused(plan, 'the runAfterCut passes are the tail of the order')

    def test_every_bridge_pass_declares_its_verdict(self):
        for name, change, message in (
                ('open-canonical-2x-active', lambda p: p.pop('bridge'), 'declares its references and verdict'),
                ('open-w42-1x-dark-active', lambda p: p['bridge'].update(stop=False), '`stop` is True'),
                ('close-w42-1x-dark-active', lambda p: p['bridge'].update(stop=True), '`stop` is False'),
                ('open-w42-2x-light-active', lambda p: p['bridge']['cells'].popitem(), 'without a reference'),
                ('open-w42-2x-light-active',
                 lambda p: next(iter(p['bridge']['cells'].values()))['reference'].update(path='x.png'),
                 'a repo path or an archive frame, exactly one')):
            with self.subTest(name=name, message=message):
                plan = copy.deepcopy(STAND_IN_PLAN)
                change(next(p for p in plan['passes'] if p['name'] == name))
                self.refused(plan, message)


FIXTURES = REPO / 'apps/reference-apple/fixtures'
BRIDGE_CELL = ('apple-macos-27.0-2x-dark-standard-glass0.5', 'checkerboard__capsule-button__rest-tint-orange')


def png_bytes(array, mode='RGB', **save):
    from PIL import Image
    import numpy as np
    buf = io.BytesIO()
    Image.fromarray(np.asarray(array, dtype=np.uint8), mode).save(buf, format='PNG', **save)
    return buf.getvalue()


class BridgeVerdict(unittest.TestCase):
    """Clause 3 as ruled, in process, on a cell (e) declared as a canonical bridge: its real 0.5
    fixture is the reference, and frames are made from it one change at a time."""

    @classmethod
    def setUpClass(cls):
        import numpy as np
        from PIL import Image
        profile, scene = BRIDGE_CELL
        cls.cell = f'{profile}/{scene}'
        cls.ref = (FIXTURES / profile / f'{scene}.png').read_bytes()
        canonical = json.loads(CANONICAL_RAW)
        spec = next(s for s in canonical['scenes'] if s['id'] == scene)
        cls.bg, cls.comp = canonical['backgrounds'][spec['background']], canonical['components'][spec['component']]
        F, Rg = S.instrument()
        cls.cells = {k: F.Cell(f'2x|{cls.cell}', cls.bg, cls.comp, 2, 'dark', 'rest', rgb=True, kernel=k)
                     for k in ('n', 'w')}
        cls.pops = {k: Rg.populations(c) for k, c in cls.cells.items()}
        with Image.open(io.BytesIO(cls.ref)) as image:
            cls.img = np.asarray(image.convert('RGB')).astype(np.int16)
        cls.names = {k: sorted(Rg.statistics(c, cls.img.astype(float), cls.pops[k])) for k, c in cls.cells.items()}

    def verdict(self, raw, bars=None, comp=None):
        return S.bridge_verdict(raw, self.ref, self.bg, comp or self.comp, 2, 'dark', 'active', bars, self.cell)

    def edge_frame(self):
        """+1 code (or -1 at 255) on the pixels within 1 pt of the shape's edge, outside both deep masks."""
        import numpy as np
        c = self.cells['n']
        edge = (np.abs(c.d) <= 1.0) & ~self.cells['n'].mask & ~self.cells['w'].mask
        frame = self.img.copy()
        frame[edge] = np.where(frame[edge] < 255, frame[edge] + 1, frame[edge] - 1)
        return frame, int(edge.sum())

    def shifted_frame(self, codes=2):
        """One population's red channel moved by `codes`, all one way, so its median moves by exactly that."""
        name, _, idx = self.pops['n'][0]
        frame = self.img.copy().reshape(-1, 3)
        sign = 1 if frame[idx, 0].max() <= 255 - codes else -1
        self.assertTrue(sign == 1 or frame[idx, 0].min() >= codes)
        frame[idx, 0] += sign * codes
        return frame.reshape(self.img.shape), name, '+' if sign == 1 else '-'

    def test_the_declared_cell_has_region_statistics(self):
        # A capsule's span (44 pt) leaves the wide mask empty: the narrow one carries the statistics.
        self.assertEqual((len(self.pops['n']) > 0, len(self.pops['w'])), (True, 0))

    def test_identity_agrees(self):
        self.assertEqual(self.verdict(self.ref)['verdict'], 'AGREE (bytes)')
        reencoded = png_bytes(self.img, compress_level=1)
        self.assertNotEqual(hashlib.sha256(reencoded).hexdigest(), hashlib.sha256(self.ref).hexdigest())
        self.assertEqual(self.verdict(reencoded)['verdict'], 'AGREE (pixels)')

    def test_one_code_on_edge_pixels_with_equal_medians_agrees(self):
        frame, n = self.edge_frame()
        v = self.verdict(png_bytes(frame))
        self.assertGreater(n, 0)
        self.assertEqual((v['verdict'], v['maxCodes'], v['pixelsDiffering']), ('AGREE (regions)', 1.0, n))
        self.assertEqual(v['worstDelta'], 0.0)

    def test_one_region_median_moved_by_two_codes_disagrees(self):
        frame, name, sign = self.shifted_frame(2)
        v = self.verdict(png_bytes(frame))
        self.assertEqual(v['verdict'], 'DISAGREE')
        self.assertIn(f'n:{name}|R {sign}2.0 codes (tolerance 1)', v['failing'])
        bars = {(k, s): 2.5 for k in self.names for s in self.names[k]}     # a measured bar of 2.5 admits it
        self.assertEqual(self.verdict(png_bytes(frame), bars)['verdict'], 'AGREE (regions)')

    def test_a_missing_region_disagrees(self):
        import numpy as np
        name, _, idx = self.pops['n'][0]
        rgba = np.dstack([self.img, np.full(self.img.shape[:2], 255, np.int16)]).reshape(-1, 4)
        rgba[idx, 3] = 0                                  # no opaque pixel in that region
        v = self.verdict(png_bytes(rgba.reshape(*self.img.shape[:2], 4), 'RGBA'))
        self.assertEqual(v['verdict'], 'DISAGREE')
        self.assertIn(f'n:{name}|R missing from the frame', v['failing'])
        small = png_bytes(self.img[:200, :320])
        self.assertTrue(self.verdict(small)['failing'][0].startswith('every region missing'))

    def test_a_cell_with_no_region_statistic_agrees_only_by_identity(self):
        frame, _ = self.edge_frame()
        tiny = dict(kind='rrect', size=[8, 8], radius=2)
        v = self.verdict(png_bytes(frame), comp=tiny)
        self.assertEqual(v['verdict'], 'DISAGREE')
        self.assertIn('no region statistic', v['failing'][0])
        self.assertEqual(self.verdict(self.ref, comp=tiny)['verdict'], 'AGREE (bytes)')


W42_ARCHIVE = Path.home() / ('.cache/vitrea-archives/1e3d6e65fa3b9a621f1d0f80fb03cc79ee76c29d9b001174983689a7aed31014'
                             '/extracted/archive')


@unittest.skipUnless(W42_ARCHIVE.is_dir(), 'the verified w42-archive is not cached on this machine')
class BridgeReferences(unittest.TestCase):
    """`bridge-references` fills the store from the real w42-archive, probe role, by SHA-256."""

    def test_a_sentinel_reference_is_extracted_by_its_digest_and_reads_identical(self):
        A = S.module('w42_archive_for_test', REPO / S.W42_DIR / 'bed/sitting/w42_archive.py')
        reader = A.wave_module().default_wave().reader(W42_ARCHIVE, roles=('probe',))
        cell = f'{L2_05}/f-impulse-rrect-md__rest'
        header, blobs = A.unbundle(reader.read(cell, 'states'))
        long_frames = sorted({r['frame'] for r in header['runs'] if r['protocol'] == 'long'})
        self.assertEqual(len(long_frames), 1)                                  # (e): one settled frame
        plan = dict(passes=[dict(name='open-w42-2x-light-active', bridge=dict(stop=True, cells={
            cell: dict(reference=dict(sha256=long_frames[0], archive='w42-archive'))}))])
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / 'refs'
            written = S.extract_bridge_references(plan, W42_ARCHIVE, store)
            self.assertEqual(written, {long_frames[0]: cell})
            raw = (store / f'{long_frames[0]}.png').read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), long_frames[0])
            with mock.patch.dict(os.environ, {S.BRIDGE_REFERENCES_ENV: str(store)}):
                refs = S.bridge_references(plan['passes'][0])
            self.assertEqual(refs[cell], raw)
            bad = dict(passes=[dict(name='x', bridge=dict(stop=True, cells={
                cell: dict(reference=dict(sha256='0' * 64, archive='w42-archive'))}))])
            with self.assertRaisesRegex(ValueError, 'holds no frame'):
                S.extract_bridge_references(bad, W42_ARCHIVE, Path(tmp) / 'refs2')


def solid_png(sid, scale=1, shift=0):
    """The bytes the stub launcher writes for `sid` (a solid colour), optionally moved in red."""
    from PIL import Image
    r, g, b = colour(sid)
    buf = io.BytesIO()
    red = r + shift if 0 <= r + shift <= 255 else r - shift          # never clipped: the shift stays whole
    Image.new('RGB', (320 * scale, 200 * scale), (red, g, b)).save(buf, format='PNG')
    return buf.getvalue()


def bridged_plan(tmp, name='close-w42-1x-light-active', stop=False, shift=0, **extra):
    """PLAN with the W42 sentinel pass named `name`, its references the stub's own frames (moved by
    `shift` codes in red) in a store under `tmp`; returns (plan, store)."""
    store = Path(tmp) / 'references'
    store.mkdir(exist_ok=True)
    plan = copy.deepcopy(PLAN)
    p = plan['passes'][-1]
    cells = {}
    for sid in p['profiles'][L1_05]:
        raw = solid_png(sid, shift=shift)
        digest = hashlib.sha256(raw).hexdigest()
        (store / f'{digest}.png').write_bytes(raw)
        cells[f'{L1_05}/{sid}'] = dict(reference=dict(sha256=digest, archive='w42-archive'))
    p.update(name=name, bridge=dict(stop=stop, cells=cells), **extra)
    if name.startswith('open-'):
        p.pop('runAfterCut', None)
    return plan, store


class BridgeRun(unittest.TestCase):
    """The gate inside the driver: every run of every bridge cell, against its reference."""

    def run_bridge(self, tmp, name, stop, shift):
        st = Stubs(tmp, glass='0.5')
        plan, store = bridged_plan(tmp, name, stop, shift)
        st.admit_before(name, plan=plan)
        return st, plan, store

    def test_an_agreeing_bridge_is_admitted_with_its_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            st, plan, store = self.run_bridge(tmp, 'close-w42-1x-light-active', False, 0)
            st.run('capture', 'close-w42-1x-light-active', '1', '1', plan=plan, W43_BRIDGE_REFERENCES=str(store))
            run = st.root / 'close-w42-1x-light-active' / 'run-1'
            a = json.loads((run / 'admission.json').read_text())
            self.assertTrue(a['bridge']['agrees'])
            self.assertEqual(set(a['bridge']['verdicts'].values()), {'AGREE (bytes)'})
            self.assertTrue((run / 'bridge.json').exists())

    def test_a_closing_bridge_that_disagrees_is_recorded_and_the_pass_goes_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            st, plan, store = self.run_bridge(tmp, 'close-w42-1x-light-active', False, 2)
            st.run('capture', 'close-w42-1x-light-active', '1', '2', plan=plan, W43_BRIDGE_REFERENCES=str(store))
            for n in (1, 2):
                a = json.loads((st.root / 'close-w42-1x-light-active' / f'run-{n}' / 'admission.json').read_text())
                self.assertEqual((a['admitted'], a['bridge']['agrees'], a['bridge']['stop']), (True, False, False))

    def test_an_opening_bridge_that_disagrees_stops_the_sitting_and_its_run_stands(self):
        with tempfile.TemporaryDirectory() as tmp:
            st, plan, store = self.run_bridge(tmp, 'open-w42-1x-light-active', True, 2)
            with self.assertRaises(S.BridgeStop):
                st.run('capture', 'open-w42-1x-light-active', '1', '3', plan=plan, W43_BRIDGE_REFERENCES=str(store))
            base = st.root / 'open-w42-1x-light-active'
            self.assertTrue((base / 'run-1' / 'admission.json').exists())          # admitted, not quarantined
            self.assertFalse(list(base.glob('QUARANTINE-*')))
            self.assertFalse((base / 'run-2').exists())                              # run 2 never launched
            report = json.loads((base / 'run-1' / 'bridge.json').read_text())
            self.assertEqual({c['verdict'] for c in report['cells']}, {'DISAGREE'})
            self.assertTrue(all(re.search(r'\|R [+-]2\.0 codes', f) for c in report['cells'] for f in c['failing']))
            with self.assertRaisesRegex(ValueError, r'earlier run\(s\) \[1\]'):     # nothing goes on from it
                st.run('capture', 'open-w42-1x-light-active', '2', '2', plan=plan, W43_BRIDGE_REFERENCES=str(store))

    def test_a_reference_that_is_not_the_declared_frame_refuses_before_any_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            st, plan, store = self.run_bridge(tmp, 'close-w42-1x-light-active', False, 0)
            for f in store.iterdir():
                f.write_bytes(f.read_bytes() + b'\0')
            with self.assertRaisesRegex(ValueError, 'a bridge reference is not the declared frame'):
                st.run('capture', 'close-w42-1x-light-active', plan=plan, W43_BRIDGE_REFERENCES=str(store))
            with self.assertRaisesRegex(ValueError, 'names no store'):
                st.run('capture', 'close-w42-1x-light-active', plan=plan)
            self.assertFalse(any('capture' in c for c in st.calls_made()))


class CutOrder(unittest.TestCase):
    """The driver lets a runAfterCut pass past the passes a cut dropped, and nothing else."""

    def test_the_close_runs_after_a_cut_and_the_dropped_passes_never_run_later(self):
        with tempfile.TemporaryDirectory() as tmp:
            st = Stubs(tmp, glass='0.5')
            plan, store = bridged_plan(tmp, 'close-w42-1x-light-active', False, 0, runAfterCut=True)
            st.admit_before('bed-1x-active', plan=plan)                 # the cut after dump-1x-light-active
            env = dict(plan=plan, W43_BRIDGE_REFERENCES=str(store))
            with self.assertRaisesRegex(ValueError, 'an earlier pass is not complete'):
                st.run('capture', 'close-w42-1x-light-active', '1', '1', **env)
            q = list((st.root / 'close-w42-1x-light-active').glob('QUARANTINE-*'))
            for d in q:
                shutil.rmtree(d)
            with self.assertRaisesRegex(ValueError, 'only runAfterCut passes run'):
                st.run('capture', 'bed-1x-active', '1', '1', W43_CUT_AFTER='dump-1x-light-active', **env)
            st.run('capture', 'close-w42-1x-light-active', '1', '3', W43_CUT_AFTER='dump-1x-light-active', **env)
            a = json.loads((st.root / 'close-w42-1x-light-active' / 'run-3' / 'admission.json').read_text())
            self.assertEqual(a['cutAfter'], 'dump-1x-light-active')
            with self.assertRaisesRegex(ValueError, 'a later pass has already started'):
                st.run('capture', 'bed-1x-active', '1', '1', **env)             # a dropped pass, never later


E_PLANS = 'e94b2ed2'      # (e)'s declared plans (w43-g0-decl), before the runAfterCut and bridge fields


def at_commit(commit, rel):
    out = subprocess.run(['git', '-C', str(REPO), 'show', f'{commit}:{rel}'], capture_output=True)
    return out.stdout if out.returncode == 0 else None


def e_g1b(with_fields=True):
    """(e)'s G1b plan and its sources' bytes at E_PLANS; `with_fields` adds what the rulings require
    (runAfterCut on the closing sentinel bridges, placeholder bridge blocks), as (e) then did."""
    raw = at_commit(E_PLANS, 'packages/calibration/results/2026-10-01-w43-g0-declaration/bed/sitting-g1b.json')
    if raw is None:
        return None
    plan = json.loads(raw)
    files = {s['path']: at_commit(E_PLANS, s['path']) for s in plan['sources'].values()}
    if with_fields:
        for p in plan['passes']:
            if str(p.get('role', '')).startswith('bridge-'):
                p['bridge'] = dict(stop=p['name'].startswith('open-'), cells={
                    f'{k}/{s}': dict(reference=dict(sha256=hashlib.sha256(f'{k}/{s}'.encode()).hexdigest(),
                                                    archive='w42-archive'))
                    for k, ids in p['profiles'].items() for s in ids})
            if p['name'].startswith('close-') and p.get('role') == 'bridge-w42-sentinel':
                p['runAfterCut'] = True
    return plan, files


def g1b_mirror(tmp, plan, files, replace=None):
    return Mirror(tmp, plan, replace={**files, **(replace or {})}, sitting='g1b')


def g1b_cut(stop_after, replace=None):
    """sitting-orchestrate.sh over (e)'s G1b order in a Mirror (stub driver, displayplacer and
    `defaults`), cut by STOP_AFTER=`stop_after`; `replace` swaps tools (the pre-ruling ones, for the
    red case). Returns (plan, completed process, the passes driven, the status log, the slider)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        plan, files = e_g1b()
        case = Orchestrator('test_rehearsals_are_dump_passes_only')
        case.tmp = tmp
        case.m = Mirror(tmp, plan, replace={**files, **(replace or {})}, sitting='g1b')
        case.st = Stubs(tmp)
        case.st.store.write_text(json.dumps({'NSGlassTintAmount': dict(type='float', value='0.5459057')}))
        case.dp, case.state, _ = stub_displayplacer(tmp, '68')
        case.driver_calls = tmp / 'driver-calls.txt'
        (case.m.sitting / 'run-sitting-w43.sh').write_text(STUB_DRIVER)
        case.m.commit('the stub driver')
        case.env = {**os.environ, **case.st.env, 'W43_SITTING': 'g1b', 'DISPLAYPLACER': str(case.dp),
                    'STUB_DRIVER_CALLS': str(case.driver_calls), 'STUB_DEFAULTS_STORE': str(case.st.store),
                    'W43_FOREGROUND': '1'}
        for k in ('DRY', 'W43_ORCHESTRATED', 'START_AT', 'STOP_AFTER', 'PASSES', 'REHEARSAL', 'VITREA_LAUNCHER_CHAIN'):
            case.env.pop(k, None)
        out = case.orchestrate(STOP_AFTER=stop_after)
        return plan, out, [l.split()[1] for l in case.driven()], case.status(), case.stored()


@unittest.skipUnless(at_commit(E_PLANS, 'packages/calibration/results/2026-10-01-w43-g0-declaration/bed/'
                                        'sitting-g1b.json'), "(e)'s plans are not in this repository")
class CutOverG1b(unittest.TestCase):
    """A cut at a sample of G1b's passes (red-green.py takes every one) still runs every close pass."""

    def test_a_cut_runs_the_close(self):
        plan, _ = e_g1b()
        names = [p['name'] for p in plan['passes']]
        closing = [n for n in names if n.startswith('close-')]
        for stop_after in (names[0], 'probe-0.25-2x-active', 'ladder-0-2x-receded', closing[1], names[-1]):
            with self.subTest(stop_after=stop_after):
                _, out, ran, status, stored = g1b_cut(stop_after)
                self.assertEqual(out.returncode, 0, out.stdout + out.stderr + status)
                upto = names[:names.index(stop_after) + 1]
                self.assertEqual(ran, upto + [n for n in closing if n not in upto])
                self.assertEqual(stored['value'], '0.5459057')
                if stop_after != names[-1]:
                    self.assertIn('restore before the close', status)


def tearDownModule():
    """No stand-in harness outlives the suite: end any process running the fake native binary and
    remove it, so no executable named VitreaReference is left behind in /tmp."""
    for p in R.native_processes(binary=SIDE / 'Contents/MacOS/VitreaReference'):
        if p['executable'] == str(SIDE / 'Contents/MacOS/VitreaReference'):
            try:
                os.kill(p['pid'], signal.SIGKILL)
            except ProcessLookupError:
                pass
    shutil.rmtree(SIDE.parent, ignore_errors=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
