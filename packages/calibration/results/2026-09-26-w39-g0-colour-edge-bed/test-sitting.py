#!/usr/bin/env python3.12
"""W39 sitting driver tests (c9a §5.184). No capture: the machine, session, harness and
launcher are stubs; pass-spec.py, the scenes files and the committed supplied-path export
are the real ones. Run: python3.12 test-sitting.py"""
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
W34 = HERE.parent / '2026-09-23-w34-g0-contour-bed'
PATHS = json.loads((HERE / 'preflight-supplied-paths.json').read_text())['components']
BED_PATHS = json.loads((HERE / 'supplied-paths.json').read_text())['components']
PIN = dict(path=str(Path('/tmp/w39-test-side/VitreaReference.app').resolve()), binarySha256='b' * 64, cdhash='c' * 40,
           buildVersion='LC_BUILD_VERSION stub')


def load():
    spec = importlib.util.spec_from_file_location('w39_sitting_under_test', HERE / 'sitting.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._PIN = dict(PIN)
    return module


def machine(scale=2):
    """W34's recorded side-built machine read, re-pointed at the stub pin and mode."""
    m = json.loads((W34 / 'machine-side-built.json').read_text())
    m['foreignProcessCount'] = 0
    m['foreignProcesses'] = []
    m['side'].update(path=PIN['path'], binarySha256=PIN['binarySha256'],
                     buildVersion=dict(stdout=PIN['buildVersion']))
    m['side']['signature']['stderr'] = f'CDHash={PIN["cdhash"]}\n'
    if scale == 1:
        m['display']['stdout'] = m['display']['stdout'].replace(
            'scaling:on <-- current mode', 'scaling:on').replace(
            'mode 69: res:2560x1440 hz:60 color_depth:4',
            'mode 69: res:2560x1440 hz:60 color_depth:4 <-- current mode')
    return m


# What the harness writes in captureProtocol (Manifest.swift / main.swift), stated here as
# literals rather than read from sitting.py: a normal launch names no settle or seed, so
# the harness records its default 1.75 s and omits orderSeed; the long one is 8 s / 3901.
HARNESS_PROTOCOL = {
    'normal': dict(initialSettleSeconds=1.75, resetInterstitialSeconds=6.0, resetCarriesGlass=False,
                   minIdleSeconds=60.0),
    'long': dict(initialSettleSeconds=8.0, orderSeed=3901, resetInterstitialSeconds=6.0,
                 resetCarriesGlass=False, minIdleSeconds=60.0),
}


def manifest(doc, pose, scale, label, protocol='normal'):
    """A manifest the harness would publish for `doc`: every attestation holding."""
    canvas = doc['canvas']
    scenes = {s['id']: s for s in doc['scenes']}
    size = [canvas['width'] * scale, canvas['height'] * scale]
    frame = [1120.0, 580.0, float(canvas['width']), float(canvas['height'])]
    profiles = []
    for p in doc['profiles']:
        fixtures = []
        for sid in p['scenes']:
            component = scenes[sid]['component']
            paths = PATHS.get(component, BED_PATHS.get(component))
            fixtures.append(dict(sceneId=sid, file=f'{p["key"]}/{sid}.png', captureMethod='screencapturekit',
                materialRendered=True, deterministic=True, width=size[0], height=size[1],
                presentedActive=pose == 'active',
                presentation=dict(observedPose=pose, isKeyWindow=pose == 'active', appIsActive=pose == 'active'),
                windowFrame=dict(coordinateSpace='appkit-global-bottom-left', requested=list(frame),
                                 actual=list(frame), backingScaleFactor=float(scale)),
                suppliedPaths=copy.deepcopy(paths)))
        profiles.append(dict(profileKey=p['key'], display=dict(requestedScale=scale, actualBackingScale=scale,
                             pixelSize=size, colorSpace='kCGColorSpaceSRGB'), fixtures=fixtures))
    return dict(hardware=dict(osBuild='26A428'), profiles=profiles,
                captureProtocol=dict(runLabel=label, **HARNESS_PROTOCOL[protocol],
                                     hidIdleSecondsAtStart=100.0, hidIdleSecondsAtEnd=100.0))


STUB_LAUNCHER = r'''
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
env = dict(a.split('=', 1) for i, a in enumerate(args) if i and args[i - 1] == '--env')
out, err = Path(args[args.index('--stdout') + 1]), Path(args[args.index('--stderr') + 1])
Path(os.environ['STUB_ARGV']).write_text(json.dumps(args))
mode = os.environ['STUB_MODE']
fixtures = Path(env['VITREA_FIXTURES'])
n = len(args[args.index('--scenes') + 1].split(','))
if mode == 'hang':
    import time; time.sleep(30)
out.write_text(f'capturing {n} fixtures via screencapturekit at 2.0x (interleaved)\n')
if mode == 'tcc':
    err.write_text('error: ScreenCaptureKit is unavailable: TCC refused\n\nThis is the Screen Recording (TCC) gate. Liquid Glass ...\n')
elif mode == 'idle':
    err.write_text('error: the machine has been idle 17.9s, under the 60.0s this run requires\n')
elif mode == 'manifest':
    (fixtures / 'manifest.json').write_text(Path(os.environ['STUB_MANIFEST']).read_text())
    err.write_text('')
elif mode == 'prompt':
    err.write_text('error: ScreenCaptureKit is unavailable: TCC\n\nThis is the Screen Recording (TCC) gate.\n')
    Path(os.environ['STUB_PROMPT']).write_text('1')
'''

STUB_SESSION = r'''
import json, os
from pathlib import Path
owners = ['Dock|20', 'Window Server|24']
if Path(os.environ['STUB_PROMPT']).exists() and Path(os.environ['STUB_PROMPT']).read_text() == '1':
    owners.append('universalAccessAuthWarn|0')
print(json.dumps(dict(idleSeconds=float(os.environ.get('STUB_IDLE', '100')), screenLocked=False, windowOwners=owners)))
'''

STUB_HARNESS = r'''
import json, os, sys
from pathlib import Path
with Path(os.environ['STUB_CALLS']).open('a') as f:
    f.write(json.dumps(dict(command=sys.argv[1:], scenes=os.environ['VITREA_SCENES'],
                            fixtures=os.environ['VITREA_FIXTURES'])) + '\n')
'''


class Stubs:
    def __init__(self, tmp, scale=2):
        self.tmp = Path(tmp)
        (self.tmp / 'machine.json').write_text(json.dumps(machine(scale)))
        for name, text in [('launcher.py', STUB_LAUNCHER), ('session.py', STUB_SESSION),
                           ('harness.py', STUB_HARNESS),
                           ('recorder.py', f'import pathlib\nprint(pathlib.Path({str(self.tmp / "machine.json")!r}).read_text())\n')]:
            (self.tmp / name).write_text(text)
        self.root = self.tmp / 'root'
        py = sys.executable
        self.env = dict(VITREA_SITTING_DIR=str(self.root), VITREA_APP=PIN['path'],
                        VITREA_RECORD_MACHINE=f'{py} {self.tmp / "recorder.py"}',
                        VITREA_SESSION_READER=f'{py} {self.tmp / "session.py"}',
                        VITREA_HARNESS=f'{py} {self.tmp / "harness.py"}',
                        VITREA_LAUNCHER=f'{py} {self.tmp / "launcher.py"}',
                        VITREA_REHEARSAL_FIXTURES=str(self.tmp),
                        STUB_ARGV=str(self.tmp / 'argv.json'), STUB_CALLS=str(self.tmp / 'calls.jsonl'),
                        STUB_PROMPT=str(self.tmp / 'prompt'), STUB_MANIFEST=str(self.tmp / 'manifest.json'),
                        STUB_MODE='tcc')

    def scale(self, scale):
        (self.tmp / 'machine.json').write_text(json.dumps(machine(scale)))


def take(S, stubs, kind, scale, run, sentinel=False, axes=(), mutate=None, **env):
    """One real run through S.main with the stubs: the harness 'publishes' the manifest
    it would write for the run's own declaration and protocol (`mutate` may spoil it)."""
    name = S.pass_name(kind, scale, sentinel)
    doc = S.pass_doc(kind, scale, run, axes, sentinel)
    m = manifest(doc, 'active' if kind == 'preflight' else kind, scale, f'w39-{name}-{run}',
                 'long' if sentinel else 'normal')
    if mutate:
        mutate(m)
    stubs.scale(scale)
    Path(stubs.env['STUB_MANIFEST']).write_text(json.dumps(m))
    argv = [kind, str(scale), str(run), str(run)] + (['--sentinel'] if sentinel else [])
    with mock.patch.dict(os.environ, {**stubs.env, 'STUB_MODE': 'manifest', **env}):
        os.environ.pop('DRY', None)
        S.main(argv)
    return stubs.root / name / f'run-{run}'


def write_verdict(S, root, axes=('x',)):
    """A frozen preflight verdict bound to `root`'s four preflight manifests."""
    inputs = {f'{s}x': {f'run{r}ManifestSha256': hashlib.sha256(
        (root / f'preflight-{s}x/run-{r}/manifest.json').read_bytes()).hexdigest() for r in (1, 2)}
        for s in (1, 2)}
    verdict = dict(schema='w39-preflight-verdict-1', inputs=inputs, reachableAxes=list(axes),
                   admittedScenes=sorted(S.phase_scenes(axes)))
    (root / 'preflight-verdict.json').write_text(json.dumps(verdict))
    return verdict


def full_sitting(S, stubs, axes=('x',)):
    """The whole declared sitting, run by run, in order: both preflight scales, the
    verdict, the four bed passes and the four long sentinel passes."""
    for scale in (1, 2):
        for run in (1, 2):
            take(S, stubs, 'preflight', scale, run)
    write_verdict(S, stubs.root, axes)
    for sentinel in (False, True):
        for name in S.BED:
            kind, scale = name.split('-')[0], int(name[-2])
            for run in range(1, S.RUNS['sentinel' if sentinel else 'bed'] + 1):
                take(S, stubs, kind, scale, run, sentinel, axes)


class Machine(unittest.TestCase):
    def setUp(self):
        self.S = load()

    def test_every_gate_refuses_and_names_all_failures(self):
        for scale in (1, 2):
            good = machine(scale)
            self.S.validate_machine(good, scale)
            with self.assertRaisesRegex(ValueError, 'mode'):
                self.S.validate_machine(good, 3 - scale)
            for field, value in [('reduceTransparency', '1'), ('increaseContrast', '1'),
                                 ('NSGlassTintAmount', '0.7'), ('ButtonShapesEnabled', '1')]:
                bad = copy.deepcopy(good)
                bad['settings'][field]['stdout'] = value
                with self.assertRaisesRegex(ValueError, 'Show Borders'):
                    self.S.validate_machine(bad, scale)
            for source in ('os', 'display'):
                bad = copy.deepcopy(good)
                bad[source]['stdout'] = 'wrong'
                with self.assertRaises(ValueError):
                    self.S.validate_machine(bad, scale)
            for key, value in [('binarySha256', 'x'), ('buildVersion', dict(stdout='other'))]:
                bad = copy.deepcopy(good)
                bad['side'][key] = value
                with self.assertRaisesRegex(ValueError, 'identity'):
                    self.S.validate_machine(bad, scale)
            bad = copy.deepcopy(good)
            bad['foreignProcessCount'] = 1
            with self.assertRaisesRegex(ValueError, 'foreign'):
                self.S.validate_machine(bad, scale)
            bad['settings']['NSGlassTintAmount']['stdout'] = '0.6'
            with self.assertRaisesRegex(ValueError, 'Show Borders.*foreign'):
                self.S.validate_machine(bad, scale)
            with self.assertRaises(TypeError):     # no exclusivity exception exists
                self.S.validate_machine(bad, scale, require_exclusive=False)

    def test_build_version_compares_without_surrounding_whitespace(self):
        self.S._PIN = dict(PIN, buildVersion=PIN['buildVersion'] + '\n')
        self.S.validate_machine(machine(2), 2)
        bad = machine(2)
        bad['side']['buildVersion'] = dict(stdout=PIN['buildVersion'] + ' minos 27.0')
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.S.validate_machine(bad, 2)

    def test_the_recorded_rehearsal_machine_reads_match_the_real_pin(self):
        """The four G0 rehearsal opening reads, against the committed pin: the side
        identity must match; what refused them is the machine, named gate by gate."""
        reads = sorted((HERE / 'dry-attestations').rglob('attest.open.json'))
        if not reads:
            self.skipTest('no committed rehearsal attestations yet')
        self.S._PIN = json.loads((HERE / 'bundle-pin.json').read_text())
        for path in reads:
            m = json.loads(path.read_text())
            scale = 1 if '-1x' in str(path) else 2
            try:
                self.S.validate_machine(m, scale)
            except ValueError as error:
                self.assertNotIn('identity changed', str(error), path)

    def test_session_gates(self):
        ok = dict(idleSeconds=61, screenLocked=False, windowOwners=['Dock|20'])
        self.assertEqual(self.S.session_problems(ok), [])
        for bad in [dict(ok, idleSeconds=59), dict(ok, screenLocked=None), dict(ok, windowOwners=None),
                    dict(ok, windowOwners=['universalAccessAuthWarn|0'])]:
            self.assertTrue(self.S.session_problems(bad))


class Manifest(unittest.TestCase):
    def setUp(self):
        self.S = load()
        self.doc = self.S.pass_doc('preflight', 2, 1, (), False)
        self.label = 'w39-preflight-2x-1'
        self.good = manifest(self.doc, 'active', 2, self.label)

    def test_good_manifest_admits(self):
        self.S.validate_manifest(self.good, self.doc, 'active', 2, self.label)

    def fails(self, mutate, pattern):
        m = copy.deepcopy(self.good)
        mutate(m)
        with self.assertRaisesRegex(ValueError, pattern):
            self.S.validate_manifest(m, self.doc, 'active', 2, self.label)

    def test_each_attestation_refuses(self):
        f = lambda m: m['profiles'][0]['fixtures'][3]
        self.fails(lambda m: f(m).pop('windowFrame'), 'window frame')
        self.fails(lambda m: f(m)['windowFrame'].update(actual=[1120.5, 580.0, 320.0, 280.0]), 'window frame')
        self.fails(lambda m: f(m)['windowFrame'].update(backingScaleFactor=1.0), 'window frame')
        self.fails(lambda m: f(m)['suppliedPaths'][0].update(
            frameOrigin=[f(m)['suppliedPaths'][0]['frameOrigin'][0] + .25,
                         f(m)['suppliedPaths'][0]['frameOrigin'][1]]), 'supplied path')
        self.fails(lambda m: f(m)['suppliedPaths'][0].update(opaque=not f(m)['suppliedPaths'][0]['opaque']),
                   'supplied path')
        self.fails(lambda m: f(m).update(presentedActive=False), 'pose')
        self.fails(lambda m: f(m).update(deterministic=False), 'repeat')
        self.fails(lambda m: m['profiles'][0]['display'].update(colorSpace='kCGColorSpaceDisplayP3'), 'sRGB')
        self.fails(lambda m: m['profiles'][0]['display'].update(actualBackingScale=1), 'scale')
        self.fails(lambda m: m['profiles'][0]['fixtures'].pop(), 'membership')
        self.fails(lambda m: m['captureProtocol'].update(runLabel='other'), 'label')

    def test_end_repeat_is_the_zero_pair_and_run_one_carries_references(self):
        repeat = self.S.pass_doc('preflight', 1, 2, (), False)
        self.assertEqual(sorted(s['$geometry'] for s in repeat['scenes']), ['zero', 'zero'])
        self.assertEqual(len(self.doc['profiles'][0]['scenes']), 18)
        r1 = self.S.pass_doc('active', 2, 1, (), False)
        r2 = self.S.pass_doc('active', 2, 2, (), False)
        self.assertGreater(len(r1['scenes']), len(r2['scenes']))

    def test_inactive_manifest(self):
        doc = self.S.pass_doc('inactive', 1, 3, (), False)
        m = manifest(doc, 'inactive', 1, 'w39-inactive-1x-3')
        self.S.validate_manifest(m, doc, 'inactive', 1, 'w39-inactive-1x-3')
        m['profiles'][0]['fixtures'][0]['presentation']['isKeyWindow'] = True
        with self.assertRaisesRegex(ValueError, 'inactive'):
            self.S.validate_manifest(m, doc, 'inactive', 1, 'w39-inactive-1x-3')


def admit(S, root, name, n):
    """An admitted run of pass `name` on disk, its admission built by the production
    constructor from a launch of the pass's own protocol."""
    run = root / name / f'run-{n}'
    run.mkdir(parents=True)
    protocol = S.protocol_of_pass(name)
    argv = ['launcher', '--args', 'capture', *S.protocol_argv(protocol)]
    m = dict(captureProtocol=dict(runLabel=f'w39-{name}-{n}', **HARNESS_PROTOCOL[protocol]))
    (run / 'admission.json').write_text(json.dumps(S.run_admission(name, n, argv, m, 'f' * 64, 1, (), None)))


class Protocol(unittest.TestCase):
    def setUp(self):
        self.S = load()

    def test_the_two_protocols_are_the_declared_settings(self):
        self.assertEqual(self.S.PROTOCOLS['normal'], dict(HARNESS_PROTOCOL['normal'], orderSeed=None))
        self.assertEqual(self.S.PROTOCOLS['long'], HARNESS_PROTOCOL['long'])
        self.assertEqual(self.S.protocol_argv('normal'),
                         ['--reset-interstitial', '6', '--min-idle-seconds', '60'])
        self.assertEqual(self.S.protocol_argv('long'), ['--reset-interstitial', '6', '--min-idle-seconds',
                                                        '60', '--initial-settle', '8', '--order-seed', '3901'])

    def test_protocol_is_derived_from_the_launch_by_exact_match(self):
        launch = lambda *flags: ['open', '-W', '--args', 'capture', '--scenes', 'a', *flags]
        base = ['--reset-interstitial', '6', '--min-idle-seconds', '60']
        self.assertEqual(self.S.launch_protocol(launch(*base)), 'normal')
        self.assertEqual(self.S.launch_protocol(launch(*base, '--order-seed', '3901', '--initial-settle', '8')),
                         'long')
        for flags in [base + ['--initial-settle', '8'], base + ['--order-seed', '3901'],
                      base + ['--initial-settle', '8', '--order-seed', '3401'], base[:2],
                      base + ['--reset-glass'], base + ['--order-seed', '3901', '--order-seed', '3901']]:
            with self.assertRaises(ValueError, msg=flags):
                self.S.launch_protocol(launch(*flags))

    def test_admission_names_the_protocol_and_checks_the_manifest(self):
        argv = lambda p: ['--args', 'capture', *self.S.protocol_argv(p)]
        m = lambda p: dict(captureProtocol=dict(runLabel='l', **HARNESS_PROTOCOL[p]))
        a = self.S.run_admission('active-1x', 3, argv('normal'), m('normal'), 'e' * 64, 5, ('x',), 'v')
        self.assertEqual((a['protocol'], a['pass'], a['run'], a['admitted'], a['dry']),
                         ('normal', 'active-1x', 3, True, False))
        self.assertEqual(a['captureProtocol']['initialSettleSeconds'], 1.75)
        a = self.S.run_admission('inactive-2x-sentinel', 1, argv('long'), m('long'), 'e' * 64, 5, (), 'v')
        self.assertEqual((a['protocol'], a['captureProtocol']['orderSeed']), ('long', 3901))
        refusals = [
            ('active-1x-sentinel', argv('normal'), m('normal'), 'pass is long'),
            ('active-1x', argv('long'), m('long'), 'pass is normal'),
            # A normal run is the harness defaults, not merely "not long".
            ('active-1x', argv('normal'), dict(captureProtocol=dict(runLabel='l')), 'captureProtocol'),
            ('active-1x', argv('normal'), {}, 'captureProtocol'),
            ('active-1x', argv('normal'),
             dict(captureProtocol=dict(HARNESS_PROTOCOL['normal'], orderSeed=7)), 'captureProtocol'),
            ('active-1x', argv('normal'),
             dict(captureProtocol=dict(HARNESS_PROTOCOL['normal'], initialSettleSeconds=2.0)), 'captureProtocol'),
            ('active-1x-sentinel', argv('long'),
             dict(captureProtocol=dict(HARNESS_PROTOCOL['long'], orderSeed=3401)), 'captureProtocol'),
        ]
        for name, launch, manifest_, pattern in refusals:
            with self.subTest(name=name, pattern=pattern), self.assertRaisesRegex(ValueError, pattern):
                self.S.run_admission(name, 1, launch, manifest_, 'e' * 64, 5, (), None)


class Order(unittest.TestCase):
    def setUp(self):
        self.S = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def complete(self, *names):
        for name in names:
            for n in range(1, self.S.runs_of(name) + 1):
                admit(self.S, self.root, name, n)

    def refused(self, name, run, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            self.S.check_order(self.root, name, run)

    def test_declared_order_and_run_counts(self):
        self.assertEqual([self.S.runs_of(n) for n in self.S.PASSES], [2, 2] + [7] * 4 + [3] * 4)
        self.assertEqual(sorted(self.S.PASSES, key=self.S.rank), self.S.PASSES)
        self.assertEqual(len({self.S.rank(n) for n in self.S.PASSES}), 9)   # only preflight peers
        for scale in (1, 2):
            self.S.check_order(self.root, f'preflight-{scale}x', 1)

    def test_every_run_of_every_prior_pass_must_be_admitted(self):
        admit(self.S, self.root, 'preflight-1x', 1)
        admit(self.S, self.root, 'preflight-2x', 1)
        admit(self.S, self.root, 'preflight-2x', 2)
        self.refused('active-1x', 1, r"not admitted: \['preflight-1x run 2'\]")
        admit(self.S, self.root, 'preflight-1x', 2)
        self.S.check_order(self.root, 'active-1x', 1)
        for n in range(1, 7):
            admit(self.S, self.root, 'active-1x', n)
        self.refused('active-2x', 1, r"\['active-1x run 7'\]")
        self.refused('inactive-2x-sentinel', 1, 'active-1x run 7.*active-2x run 1')

    def test_a_quarantine_alone_does_not_satisfy_a_run(self):
        self.complete('preflight-1x', 'preflight-2x')
        for n in range(1, 7):
            admit(self.S, self.root, 'active-1x', n)
        (self.root / 'active-1x' / 'QUARANTINE-run-7-1').mkdir()
        (self.root / 'active-1x' / 'QUARANTINE-run-7-1' / 'refusal.txt').write_text('ValueError: x\n')
        self.refused('active-2x', 1, r"\['active-1x run 7'\]")
        # An admission that is not the pass's own protocol is not admitted either.
        admit(self.S, self.root, 'active-1x', 7)
        self.S.check_order(self.root, 'active-2x', 1)
        self.complete('active-2x', 'inactive-1x', 'inactive-2x', 'active-1x-sentinel')
        path = self.root / 'active-1x-sentinel' / 'run-3' / 'admission.json'
        path.write_text(json.dumps(dict(json.loads(path.read_text()), protocol='normal')))
        self.refused('active-2x-sentinel', 1, r"\['active-1x-sentinel run 3'\]")

    def test_skipped_and_interrupted_runs_block_their_successors(self):
        self.complete('preflight-1x', 'preflight-2x')
        admit(self.S, self.root, 'active-1x', 1)
        self.refused('active-1x', 3, r'earlier run\(s\) \[2\]')       # skipped
        (self.root / 'active-1x' / 'run-2').mkdir()                      # interrupted
        self.refused('active-1x', 3, r'\[2\]')
        (self.root / 'active-1x' / 'run-2').rename(self.root / 'active-1x' / 'QUARANTINE-run-2-1')
        self.refused('active-1x', 3, r'\[2\]')                           # quarantined
        self.S.check_order(self.root, 'active-1x', 2)                    # still completable
        admit(self.S, self.root, 'active-1x', 2)
        self.S.check_order(self.root, 'active-1x', 3)

    def test_sentinel_passes_follow_the_bed_order(self):
        self.complete('preflight-1x', 'preflight-2x', *self.S.BED)
        self.S.check_order(self.root, 'active-1x-sentinel', 1)
        self.refused('active-2x-sentinel', 1, r"\['active-1x-sentinel run 1', 'active-1x-sentinel run 2', "
                                              r"'active-1x-sentinel run 3'\]")
        admit(self.S, self.root, 'active-1x-sentinel', 1)
        admit(self.S, self.root, 'active-1x-sentinel', 2)
        self.refused('active-2x-sentinel', 1, r"\['active-1x-sentinel run 3'\]")
        admit(self.S, self.root, 'active-1x-sentinel', 3)
        self.S.check_order(self.root, 'active-2x-sentinel', 1)

    def test_a_started_later_pass_refuses_an_earlier_one(self):
        self.complete('preflight-1x', 'preflight-2x')
        (self.root / 'active-2x' / 'QUARANTINE-run-1-1').mkdir(parents=True)
        self.refused('active-1x', 1, 'later')
        self.refused('preflight-2x', 1, 'later')


class Driver(unittest.TestCase):
    """main() end to end with stubs."""

    def setUp(self):
        self.S = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.stubs = Stubs(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, argv, **env):
        with mock.patch.dict(os.environ, {**self.stubs.env, **env}, clear=False):
            os.environ.pop('DRY', None)
            self.S.main(argv)

    def test_refusal_rehearsal_is_a_real_launch_and_admits_only_tcc(self):
        self.run_main(['active', '2', '--rehearse-refusal'])
        run = self.stubs.root / 'rehearsal-active-2x' / 'run-1'
        verdict = json.loads((run / 'rehearsal.json').read_text())
        self.assertEqual(verdict['outcome'], 'refused-tcc')
        argv = json.loads(Path(self.stubs.env['STUB_ARGV']).read_text())
        self.assertNotIn('--dry-run', argv)
        self.assertIn('capture', argv)
        self.assertEqual(argv[argv.index('--min-idle-seconds') + 1], '60')
        run1 = self.S.pass_doc('active', 2, 1, (), False)
        self.assertEqual(argv[argv.index('--scenes') + 1].split(','),
                         sorted({s for p in run1['profiles'] for s in p['scenes']}))
        self.assertFalse((run / 'manifest.json').exists())

    def test_rehearsal_outcomes_other_than_tcc_quarantine(self):
        doc = self.S.pass_doc('active', 2, 1, (), False)
        Path(self.stubs.env['STUB_MANIFEST']).write_text(json.dumps(manifest(doc, 'active', 2, 'x')))
        for mode, word in [('manifest', 'published a capture'), ('idle', 'refused-other'),
                           ('prompt', 'prompt-pending')]:
            with self.subTest(mode=mode):
                Path(self.stubs.env['STUB_PROMPT']).unlink(missing_ok=True)
                root = self.stubs.tmp / f'root-{mode}'
                with self.assertRaisesRegex(ValueError, word):
                    self.run_main(['active', '2', '--rehearse-refusal'], STUB_MODE=mode,
                                  VITREA_SITTING_DIR=str(root))
                quarantined = list((root / 'rehearsal-active-2x').glob('QUARANTINE-run-1-*'))
                self.assertEqual(len(quarantined), 1)
                self.assertTrue((quarantined[0] / 'refusal.txt').exists())

    def test_rehearsal_timeout_is_prompt_pending(self):
        self.S.REHEARSAL_TIMEOUT = 2
        with mock.patch.object(self.S.subprocess, 'run', wraps=self.S.subprocess.run):
            with self.assertRaisesRegex(ValueError, 'prompt-pending'):
                self.run_main(['preflight', '2', '--rehearse-refusal'], STUB_MODE='hang')

    def test_opening_refusal_names_every_gate_and_keeps_the_reads(self):
        m = machine(2)
        m['foreignProcessCount'] = 13
        (self.stubs.tmp / 'machine.json').write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, 'mode.*foreign.*idle'):
            self.run_main(['active', '1', '--rehearse-refusal'], STUB_IDLE='5')
        q, = (self.stubs.root / 'rehearsal-active-1x').glob('QUARANTINE-run-1-*')
        self.assertTrue((q / 'attest.open.json').exists() and (q / 'session-before.json').exists())
        self.assertFalse(Path(self.stubs.env['STUB_ARGV']).exists())   # nothing launched

    def test_dry_and_implicit_root_refused(self):
        with mock.patch.dict(os.environ, {**self.stubs.env, 'DRY': '1'}):
            with self.assertRaises(SystemExit):
                self.S.main(['active', '2'])
        env = dict(self.stubs.env)
        env.pop('VITREA_SITTING_DIR')
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(SystemExit):
                self.S.main(['active', '2'])
        with self.assertRaisesRegex(ValueError, 'outside'):
            self.run_main(['preflight', '2'], VITREA_SITTING_DIR=str(HERE / 'scratch'))

    def test_rehearsals_and_evidence_never_share_a_root(self):
        (self.stubs.root / 'preflight-2x').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'rehearsals only'):
            self.run_main(['active', '2', '--rehearse-refusal'])

    def test_real_preflight_then_bed_needs_the_bound_verdict(self):
        for scale in (2, 1):
            (self.stubs.tmp / f's{scale}').mkdir()
            self.stubs = Stubs(self.stubs.tmp / f's{scale}', scale)
            self.stubs.root = Path(self.tmp.name) / 'shared-root'
            self.stubs.env['VITREA_SITTING_DIR'] = str(self.stubs.root)
            for run in (1, 2):
                doc = self.S.pass_doc('preflight', scale, run, (), False)
                Path(self.stubs.env['STUB_MANIFEST']).write_text(json.dumps(
                    manifest(doc, 'active', scale, f'w39-preflight-{scale}x-{run}')))
                self.run_main(['preflight', str(scale), str(run), str(run)], STUB_MODE='manifest')
        root = self.stubs.root
        self.assertTrue((root / 'preflight-2x/run-2/admission.json').exists())
        # No verdict: no bed pass.
        with self.assertRaisesRegex(ValueError, 'verdict'):
            self.run_main(['active', '1'], STUB_MODE='manifest')
        inputs = {f'{s}x': {f'run{r}ManifestSha256': hashlib.sha256(
            (root / f'preflight-{s}x/run-{r}/manifest.json').read_bytes()).hexdigest() for r in (1, 2)}
            for s in (1, 2)}
        verdict = dict(schema='w39-preflight-verdict-1', inputs=inputs, reachableAxes=['x'],
                       admittedScenes=sorted(self.S.phase_scenes(('x',))))
        self.assertEqual(len([s for s in verdict['admittedScenes'] if '__rest' in s and '-1x-' in s]), 8)
        bad = dict(verdict, admittedScenes=verdict['admittedScenes'][1:])
        (root / 'preflight-verdict.json').write_text(json.dumps(bad))
        with self.assertRaisesRegex(ValueError, 'disagree'):
            self.S.load_verdict(root, root / 'preflight-verdict.json')
        (root / 'preflight-verdict.json').write_text(json.dumps(verdict))
        axes, _ = self.S.load_verdict(root, root / 'preflight-verdict.json')
        self.assertEqual(axes, ('x',))
        doc = self.S.pass_doc('active', 1, 1, axes, False)
        self.assertTrue(any(s.get('$phaseAxis') == 'x' for s in doc['scenes']))
        self.assertFalse(any(s.get('$phaseAxis') == 'y' for s in doc['scenes']))
        (root / 'preflight-verdict.json').write_text(json.dumps(verdict) + ' ')
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.S.load_verdict(root, root / 'preflight-verdict.json')

    def test_interrupted_predecessor_blocks_until_the_operator_preserves_it(self):
        run1 = self.stubs.root / 'preflight-2x' / 'run-1'
        run1.mkdir(parents=True)
        (run1 / 'attest.open.json').write_text('{"partial": true}')
        with self.assertRaisesRegex(ValueError, r'run 2 refused: earlier run\(s\) \[1\]'):
            take(self.S, self.stubs, 'preflight', 2, 2)
        self.assertFalse((self.stubs.root / 'preflight-2x' / 'run-2').exists())
        # No hidden retry: the driver refuses the run and leaves the directory as it was.
        with self.assertRaisesRegex(ValueError, 'already exists'):
            take(self.S, self.stubs, 'preflight', 2, 1)
        self.assertEqual(sorted(p.name for p in run1.iterdir()), ['attest.open.json'])
        self.assertEqual([p.name for p in (self.stubs.root / 'preflight-2x').iterdir() if p.is_dir()],
                         ['run-1'])
        # The operator preserves it under a quarantine name, then continues deliberately.
        run1.rename(run1.with_name('QUARANTINE-run-1-interrupted'))
        take(self.S, self.stubs, 'preflight', 2, 1)
        self.assertEqual((run1.with_name('QUARANTINE-run-1-interrupted') / 'attest.open.json').read_text(),
                         '{"partial": true}')
        self.assertTrue(json.loads((run1 / 'admission.json').read_text())['admitted'])
        take(self.S, self.stubs, 'preflight', 2, 2)
        # An admitted run is kept, never retaken.
        with self.assertRaisesRegex(ValueError, 'already exists'):
            take(self.S, self.stubs, 'preflight', 2, 1)

    def test_quarantined_predecessor_blocks_and_is_retaken(self):
        # The harness recorded a settle the normal launch did not ask for.
        spoil = lambda m: m['captureProtocol'].update(initialSettleSeconds=8.0)
        with self.assertRaisesRegex(ValueError, 'captureProtocol'):
            take(self.S, self.stubs, 'preflight', 1, 1, mutate=spoil)
        passdir = self.stubs.root / 'preflight-1x'
        q, = passdir.glob('QUARANTINE-run-1-*')
        self.assertIn('captureProtocol', (q / 'refusal.txt').read_text())
        self.assertTrue((q / 'attest.open.json').exists() and (q / 'attest.close.json').exists())
        with self.assertRaisesRegex(ValueError, r'\[1\]'):
            take(self.S, self.stubs, 'preflight', 1, 2)
        take(self.S, self.stubs, 'preflight', 1, 1)
        take(self.S, self.stubs, 'preflight', 1, 2)
        self.assertEqual(len(list(passdir.glob('QUARANTINE-*'))), 1)

    def test_the_complete_sitting_admits_every_run_under_its_protocol(self):
        full_sitting(self.S, self.stubs)
        root = self.stubs.root
        for name in self.S.PASSES:
            passdir = root / name
            self.assertEqual(sorted(c.name for c in passdir.iterdir() if c.is_dir()),
                             sorted(f'run-{n}' for n in range(1, self.S.runs_of(name) + 1)))
            for n in range(1, self.S.runs_of(name) + 1):
                a = json.loads((passdir / f'run-{n}' / 'admission.json').read_text())
                protocol = 'long' if name.endswith('-sentinel') else 'normal'
                self.assertEqual((a['schema'], a['admitted'], a['dry'], a['pass'], a['run'], a['protocol']),
                                 ('w39-run-admission-1', True, False, name, n, protocol))
                self.assertEqual(a['manifestSha256'], hashlib.sha256(
                    (passdir / f'run-{n}' / 'manifest.json').read_bytes()).hexdigest())
                argv = json.loads((passdir / f'run-{n}' / 'launch.json').read_text())['argv']
                if protocol == 'long':
                    self.assertEqual(argv[argv.index('--initial-settle') + 1], '8')
                    self.assertEqual(argv[argv.index('--order-seed') + 1], '3901')
                else:
                    self.assertNotIn('--initial-settle', argv)
                    self.assertNotIn('--order-seed', argv)
        # Nothing follows the last sentinel, and nothing precedes it again.
        with self.assertRaisesRegex(ValueError, 'later'):
            take(self.S, self.stubs, 'inactive', 2, 1, axes=('x',))


if __name__ == '__main__':
    unittest.main(verbosity=2)
