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


def manifest(doc, pose, scale, label):
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
    return dict(hardware=dict(osBuild='26A428'), captureProtocol=dict(runLabel=label), profiles=profiles)


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


class Order(unittest.TestCase):
    def setUp(self):
        self.S = load()

    def test_declared_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.S.check_order(root, 'preflight-2x')
            with self.assertRaisesRegex(ValueError, 'earlier'):
                self.S.check_order(root, 'active-1x')
            for name in ('preflight-1x', 'preflight-2x'):
                (root / name / 'run-1').mkdir(parents=True)
            self.S.check_order(root, 'active-1x')
            with self.assertRaisesRegex(ValueError, 'earlier'):
                self.S.check_order(root, 'active-2x')
            (root / 'active-2x' / 'QUARANTINE-run-1-1').mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, 'later'):
                self.S.check_order(root, 'active-1x')
            with self.assertRaisesRegex(ValueError, 'earlier'):
                self.S.check_order(root, 'active-2x-sentinel')


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
