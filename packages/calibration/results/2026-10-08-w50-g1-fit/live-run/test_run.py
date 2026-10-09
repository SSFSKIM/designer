"""run.py: the operator sequence end to end on livekit's synthetic world, and its stop policy.

The end-to-end cases drive the REAL dispatcher and all seven real roles through child.py's own
DRIVER source (run_inprocess), with batches.py's batches; only the initializer's numerical
work and the world's stand-in seams are synthetic. Every printed line must be an allowlisted
event. The policy cases script the driver's answers to prove what is and is not retried.
"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
FIT = HERE.parent


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value; spec.loader.exec_module(value); return value


T = module(HERE/'kit.py', 'w50_live_run_test_kit')
R = module(HERE/'run.py', 'w50_live_run_operator')
C = R.C
GATED = (T.K.P1, 'webgpu', 'cell-grey-004-s096__rest', 'deep8-channel-median')
ALLOWED = set(R.FIELDS) | {'schema'}


class Initializer:
    """fit/execution.py's assemble/bind_arguments shape over the world's synthetic cohort. Its
    initializer.json names the pre-fit evidence the world's root admits, as the real one does."""
    def __init__(self, world, prefit=None): self.world = world; self.calls = []; self.prefit = prefit
    def assemble(self, root):
        self.calls.append('assemble'); w = self.world
        made = w.put('synthetic/initializer.json', {'preFitEvidence': self.prefit or w.prefit})
        return {'cohort': T.candidate(w)['cohort'], 'initializer': made}
    def bind_arguments(self, root, cohort):
        self.calls.append('bind'); w = self.world
        return {'cohort': w.pin(w.repo/'numerical-cohort.json'), 'argumentManifest': w.pin(w.repo/'arguments.json'),
                'preFitEvidence': dict(w.prefit)}


def operator(case, world, lines, numerical=None, pnpm='pnpm', initializer=None):
    initializer = initializer or Initializer(world)
    if numerical is None: numerical = lambda cohort: world.repo/world.numerical['path']
    op = R.Operator(repo=world.repo, live=world.fit_dir/'live-execution', work=world.base/'outputs',
                    call=C.run_inprocess(world.D, initializer), numerical=numerical or None, pnpm=pnpm,
                    declarations=lambda: T.declarations(world), transport=lambda decl: T.transport(world, decl),
                    owner_records=lambda decl, candidate: world.intrinsic, out=lines.append)
    return op, initializer


def events(case, lines):
    out = [json.loads(line) for line in lines]
    for event in out:
        case.assertLessEqual(set(event), ALLOWED)
        case.assertEqual(event['schema'], 'w50-live-run-event-1')
    return out


class EndToEnd(unittest.TestCase):
    def sequence(self, world, lines, until=None):
        op, initializer = operator(self, world, lines)
        steps = [['initialize'], ['fit-batch'], ['run', 'fit'], ['fit-record'], ['gate-batch'], ['run', 'gate'],
                 ['exposure-batch'], ['run', 'exposure'], ['status']]
        codes = []
        for argv in steps:
            codes.append(R.main(['--work', str(world.base/'outputs'), *argv], op))
            if until and argv == until: break
        return op, initializer, codes

    def test_the_operator_sequence_reaches_one_exposure_verdict(self):
        world = T.K.EndToEnd(self); lines = []
        op, initializer, codes = self.sequence(world, lines)
        self.assertEqual(codes, [0]*9)
        self.assertEqual(initializer.calls, ['assemble', 'bind'])
        out = events(self, lines)
        self.assertEqual([e['code'] for e in out[:2]], ['INITIALIZER_RECORDED', 'CANDIDATE_WRITTEN'])
        verdicts = [(e['phase'], e['verdict']) for e in out if e['code'] == 'VERDICT']
        self.assertEqual(verdicts, [('fit', 'CAPTURED'), ('gate', 'PASS_EXPOSED_OWNER_PENDING'), ('exposure', 'PASS')])
        self.assertEqual([e['phase'] for e in out if e['code'] == 'PHASE_CREATED'], ['fit', 'gate', 'exposure'])
        self.assertTrue(all(e['event']['code'] == 'ATTEMPT_COMPLETE' for e in out if e['code'] == 'ATTEMPT'))
        status = [e for e in out if e['step'] == 'status']
        self.assertEqual({e['phase']: e['verdict'] for e in status},
                         {'fit': 'CAPTURED', 'gate': 'PASS_EXPOSED_OWNER_PENDING', 'exposure': 'PASS'})
        # The records are the dispatcher's own: one fit contract, the gate names the fit record.
        self.assertEqual(len(op.fit_contracts()), 1)
        gate = json.loads(op.slot('gate').read_text())
        self.assertEqual(gate['fitRecord'], T.B.D.pin(world.repo, op.record('fit-record.json')))
        # Re-running a finished phase resumes its slot and creates nothing.
        lines.clear()
        self.assertEqual(R.main(['run', 'gate'], op), 0)
        self.assertEqual([e['code'] for e in events(self, lines)], ['PHASE_RESUMED', 'VERDICT'])
        # A second candidate, fit batch or fit record is refused, never written.
        for argv in (['initialize'], ['recover-bind'], ['fit-batch'], ['fit-record']):
            lines.clear(); self.assertEqual(R.main(argv, op), 1)
            self.assertEqual(events(self, lines)[-1]['code'], 'EXISTS')

    def test_a_neither_gate_stops_everything_after_it(self):
        world = T.K.EndToEnd(self, offsets={'|'.join(GATED): 10}); lines = []
        op, _, codes = self.sequence(world, lines, until=['run', 'gate'])
        self.assertEqual(codes, [0]*6)
        out = events(self, lines)
        self.assertEqual([e['verdict'] for e in out if e['code'] == 'VERDICT'], ['CAPTURED', 'NEITHER'])
        for argv in (['exposure-batch'], ['run', 'exposure']):
            lines.clear(); self.assertEqual(R.main(argv, op), 1)
        self.assertEqual([e['code'] for e in events(self, lines)], ['NO_PHASE'])
        lines.clear(); R.main(['exposure-batch'], op)
        self.assertEqual(events(self, lines)[-1], {'schema': 'w50-live-run-event-1', 'step': 'exposure-batch',
                                                    'code': 'STOPPED_AFTER_GATE', 'phase': 'gate', 'verdict': 'NEITHER'})
        self.assertFalse(op.record('exposure-batch.json').exists())
        self.assertFalse(op.output('exposure').exists())
        self.assertFalse(op.slot('exposure').exists())


class Initialize(unittest.TestCase):
    """A failed numerical referee keeps the initializer's result; the rerun runs only the referee."""

    def test_a_failed_referee_resumes_from_the_recorded_initializer_result(self):
        world = T.K.EndToEnd(self); lines = []; attempts = []
        def numerical(cohort):
            attempts.append(cohort)
            if len(attempts) == 1: raise FileNotFoundError('pnpm')  # an unforeseen fault: code ERROR
            return world.repo/world.numerical['path']
        op, initializer = operator(self, world, lines, numerical=numerical)
        self.assertEqual(R.main(['initialize'], op), 1)
        out = events(self, lines)
        self.assertEqual([e['code'] for e in out], ['INITIALIZER_RECORDED', 'ERROR'])
        self.assertNotIn('Traceback', ''.join(lines)); self.assertNotIn('pnpm', ''.join(lines))
        self.assertIn('FileNotFoundError', Path(out[-1]['log']).read_text())
        self.assertTrue(op.record('initialized.json').is_file()); self.assertFalse(op.record('candidate.json').exists())
        lines.clear()
        self.assertEqual(R.main(['initialize'], op), 0)
        self.assertEqual([e['code'] for e in events(self, lines)], ['INITIALIZE_RESUMED', 'CANDIDATE_WRITTEN'])
        self.assertEqual(initializer.calls, ['assemble', 'bind'])
        self.assertEqual(attempts[0], attempts[1])
        recorded = json.loads(op.record('initialized.json').read_text())
        candidate = json.loads(op.record('candidate.json').read_text())
        self.assertEqual({k: candidate[k] for k in R.INITIALIZED}, {k: recorded[k] for k in R.INITIALIZED})
        # The run continues from the resumed candidate.
        lines.clear(); self.assertEqual(R.main(['fit-batch'], op), 0)

    def test_a_changed_initializer_output_refuses_the_resume(self):
        world = T.K.EndToEnd(self); lines = []
        def numerical(cohort): raise R.Stop(step='initialize', code='REFUSED')
        op, initializer = operator(self, world, lines, numerical=numerical)
        self.assertEqual(R.main(['initialize'], op), 1)
        (world.repo/'arguments.json').write_text('changed\n')
        lines.clear(); self.assertEqual(R.main(['initialize'], op), 1)
        self.assertEqual([e['code'] for e in events(self, lines)], ['REFUSED'])
        self.assertEqual(initializer.calls, ['assemble', 'bind'])

    def test_the_real_referee_call_stops_cleanly_and_logs_each_attempt_freshly(self):
        world = T.K.EndToEnd(self); lines = []
        tools = Path(world.base/'tools'); tools.mkdir()
        failing = tools/'failing-pnpm'; failing.write_text('#!/bin/sh\necho crashed\nexit 1\n'); failing.chmod(0o755)
        working = tools/'working-pnpm'
        working.write_text(f"#!/bin/sh\ncp '{world.repo/world.numerical['path']}' \"$7\"\n"); working.chmod(0o755)
        op, initializer = operator(self, world, lines, numerical=False, pnpm=str(tools/'absent-pnpm'))
        self.assertEqual(R.main(['initialize'], op), 1)
        out = events(self, lines)
        self.assertEqual([e['code'] for e in out], ['INITIALIZER_RECORDED', 'TOOL_MISSING'])
        self.assertIn('not on PATH', Path(out[-1]['log']).read_text())
        logs = [out[-1]['log']]
        op.pnpm = str(failing)
        for _ in range(2):
            lines.clear(); self.assertEqual(R.main(['initialize'], op), 1)
            out = events(self, lines)
            self.assertEqual([e['code'] for e in out], ['INITIALIZE_RESUMED', 'REFUSED'])
            self.assertIn('crashed', Path(out[-1]['log']).read_text()); logs.append(out[-1]['log'])
        self.assertEqual(len(set(logs)), 3)
        op.pnpm = str(working)
        lines.clear(); self.assertEqual(R.main(['initialize'], op), 0)
        self.assertEqual([e['code'] for e in events(self, lines)], ['INITIALIZE_RESUMED', 'CANDIDATE_WRITTEN'])
        self.assertEqual(initializer.calls, ['assemble', 'bind'])


class Provenance(unittest.TestCase):
    """Without a recovery record, a point is admitted only with this root's own pre-fit evidence."""

    def test_a_point_naming_another_pre_fit_evidence_is_refused_without_a_recovery(self):
        world = T.K.EndToEnd(self); lines = []
        other = world.put('synthetic/other-pre-fit-evidence.json', {'synthetic': 'another root'})
        op, initializer = operator(self, world, lines, initializer=Initializer(world, prefit=other))
        self.assertEqual(R.main(['initialize'], op), 0)
        lines.clear(); self.assertEqual(R.main(['fit-batch'], op), 1)
        self.assertEqual([e['code'] for e in events(self, lines)], ['REFUSED'])
        self.assertFalse(op.record('fit-batch.json').exists())

    def test_recover_bind_is_refused_on_a_root_without_the_declaration(self):
        world = T.K.EndToEnd(self); lines = []
        op, initializer = operator(self, world, lines)
        self.assertEqual(R.main(['recover-bind'], op), 1)
        self.assertEqual([e['code'] for e in events(self, lines)], ['REFUSED'])
        self.assertEqual(initializer.calls, [])
        self.assertFalse(op.record('recovered.json').exists())


class Errors(unittest.TestCase):
    def test_an_unforeseen_exception_prints_only_a_code_and_a_log_path(self):
        with tempfile.TemporaryDirectory() as name:
            base = Path(name).resolve(); lines = []
            root = base/'live/execution-root-2.json'; root.parent.mkdir(); root.write_text('{}\n')
            op = R.Operator(repo=base, live=FIT/'live-execution', root=root, records=base/'run', work=base/'work',
                            call=Scripted([]), out=lines.append)
            def boom(): raise RuntimeError('value 0.731 leaked')
            op.step_status = boom
            self.assertEqual(R.main(['status'], op), 1)
            out = events(self, lines)
            self.assertEqual([(e['step'], e['code']) for e in out], [('status', 'ERROR')])
            self.assertNotIn('0.731', ''.join(lines)); self.assertNotIn('Traceback', ''.join(lines))
            self.assertIn('RuntimeError: value 0.731 leaked', Path(out[0]['log']).read_text())
            self.assertTrue(Path(out[0]['log']).is_relative_to(base/'work/operator'))
            # A stop whose event is not allowlisted is an error too, never a traceback.
            lines.clear()
            def bad(): raise R.Stop(step='status', code='NOT_A_CODE')
            op.step_status = bad
            self.assertEqual(R.main(['status'], op), 1)
            self.assertEqual([e['code'] for e in events(self, lines)], ['ERROR'])


class Scripted:
    """A driver whose answers are scripted per op; 'advance' answers are consumed in order."""
    def __init__(self, advance, verdict='CAPTURED'):
        self.advance = list(advance); self.ops = []; self.verdict = verdict
    def __call__(self, op, **request):
        self.ops.append(op)
        if op == 'advance': return self.advance.pop(0)
        if op == 'verdict': return {'ok': True, 'verdict': self.verdict}
        if op == 'stop_stale': return {'ok': True, 'event': event('INSTRUMENT_FAULT', 1)}
        if op == 'create_phase': return {'ok': True, 'contract': request['contract_path']}
        raise AssertionError(op)


def event(code, attempt=None, phase='fit'):
    return {'schema': 'w50-live-public-event-1', 'code': code, 'phase': phase, **({'attempt': attempt} if attempt else {})}


def attempt(code, n=1): return {'ok': True, 'state': 'attempt', 'attempt': n, 'members': 3, 'event': event(code, n)}
def failure(message): return {'ok': False, 'error': 'ValueError', 'message': message, 'log': '/x/log'}
ANALYSIS = {'ok': True, 'state': 'analysis', 'event': event('ANALYSIS_COMPLETE')}


class Policy(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve(); self.lines = []

    def run_fit(self, answers, retries=1):
        """A sealed fit slot already exists, so run fit goes straight to its attempts."""
        root = self.base/'live/execution-root-2.json'; root.parent.mkdir(); root.write_text('{}\n')
        script = Scripted(answers)
        op = R.Operator(repo=self.base, live=FIT/'live-execution', root=root, records=self.base/'run',
                        work=self.base/'work', call=script, out=self.lines.append)
        T.B.write_once(op.record('fit-batch.json'), {'phase': 'fit'})
        slot = op.slot('fit'); slot.parent.mkdir(parents=True, exist_ok=True)
        slot.write_text(json.dumps({'batch': T.B.D.pin(self.base, op.record('fit-batch.json'))}))
        Path(str(slot)+'.sha256').write_text('sealed\n')
        code = R.main(['run', 'fit', '--retries', str(retries)], op)
        return code, script.ops, [e['code'] for e in events(self, self.lines)]

    def test_complete_attempts_then_one_analysis(self):
        code, ops, codes = self.run_fit([attempt('ATTEMPT_COMPLETE'), ANALYSIS])
        self.assertEqual((code, ops), (0, ['advance', 'advance', 'verdict']))
        self.assertEqual(codes, ['PHASE_RESUMED', 'ATTEMPT', 'ANALYSIS', 'VERDICT'])

    def test_an_instrument_fault_is_retried_only_within_the_budget(self):
        code, ops, codes = self.run_fit([attempt('INSTRUMENT_FAULT', 1), attempt('INSTRUMENT_FAULT', 2)], retries=1)
        self.assertEqual((code, ops), (1, ['advance', 'advance']))
        self.assertEqual(codes, ['PHASE_RESUMED', 'ATTEMPT', 'ATTEMPT', 'REFUSED'])

    def test_a_census_refusal_or_lost_lease_stops_for_the_operator(self):
        for stop in ('CENSUS_REFUSED', 'LEASE_LOST'):
            self.lines.clear()
            with self.subTest(stop=stop):
                (self.base/'live').exists() and __import__('shutil').rmtree(self.base/'live')
                (self.base/'run').exists() and __import__('shutil').rmtree(self.base/'run')
                code, ops, codes = self.run_fit([attempt(stop)], retries=5)
                self.assertEqual((code, ops), (1, ['advance']))
                self.assertEqual(codes[-1], 'REFUSED')

    def test_a_killed_attempt_is_preserved_once_then_planned_again(self):
        code, ops, codes = self.run_fit([failure('Prior attempt is not a preserved stop (see stop_stale_attempt)'),
                                         attempt('ATTEMPT_COMPLETE', 2), ANALYSIS])
        self.assertEqual((code, ops), (0, ['advance', 'stop_stale', 'advance', 'advance', 'verdict']))
        self.assertEqual(codes, ['PHASE_RESUMED', 'STALE_STOPPED', 'ATTEMPT', 'ANALYSIS', 'VERDICT'])

    def test_nothing_is_retried_past_a_marker(self):
        for message, final in (('Incomplete native subread cannot be replayed', 'NATIVE_INCOMPLETE'),
                               ('Analysis already started', 'ANALYSIS_STARTED')):
            self.lines.clear()
            with self.subTest(final=final):
                for name in ('live', 'run'):
                    if (self.base/name).exists(): __import__('shutil').rmtree(self.base/name)
                code, ops, codes = self.run_fit([failure(message)], retries=5)
                self.assertEqual((code, ops), (1, ['advance']))
                self.assertEqual(codes, ['PHASE_RESUMED', final])
                self.assertNotIn('/x/log', ''.join(self.lines).replace('"log": "/x/log"', ''))
                self.assertNotIn(message, ''.join(self.lines))

    def test_events_outside_the_allowlist_are_never_printed(self):
        root = self.base/'live/execution-root-2.json'; root.parent.mkdir(); root.write_text('{}\n')
        op = R.Operator(repo=self.base, live=FIT/'live-execution', root=root, records=self.base/'run',
                        work=self.base/'work', call=Scripted([]), out=self.lines.append)
        for bad in ({'step': 'run', 'code': 'VERDICT', 'value': 1.5},
                    {'step': 'run', 'code': 'VERDICT', 'verdict': 'WITHIN'},
                    {'step': 'run', 'code': 'ATTEMPT', 'event': {**event('ATTEMPT_COMPLETE'), 'native': [1, 2]}},
                    {'step': 'status', 'code': 'STATUS', 'status': {'schema': 'w50-live-public-status-1', 'cells': []}}):
            with self.subTest(bad=bad), self.assertRaises(ValueError): op.emit(**bad)
        self.assertEqual(self.lines, [])


class ChildProcess(unittest.TestCase):
    """child.Child runs DRIVER in a fresh isolated interpreter; its streams stay in the log."""

    def test_results_come_back_by_file_and_streams_stay_in_the_log(self):
        with tempfile.TemporaryDirectory() as name:
            base = Path(name).resolve()
            fake = base/'dispatch.py'
            fake.write_text("import sys\n"
                "def root_doc(root):\n    print('dispatcher noise'); print('stderr noise', file=sys.stderr); return {'repo': '/x'}\n"
                "def public_status(root, contract):\n    return {'schema': 'w50-live-public-status-1', 'flags': sys.flags.isolated}\n"
                "def create_phase(root, batch, output, fit_record=None):\n    raise ValueError('Logical phase slot already exists')\n")
            child = C.Child(sys.executable, fake, base/'initializer.py', base/'logs', base)
            status = child('status', root=str(base/'root.json'), contract='c')
            self.assertEqual((status['ok'], status['status']['flags']), (True, 1))
            log = Path(status['log']).read_text()
            self.assertIn('dispatcher noise', log); self.assertIn('stderr noise', log)
            failed = child('create_phase', root=str(base/'root.json'), batch='b', output='o')
            self.assertEqual((failed['ok'], failed['error']), (False, 'ValueError'))
            self.assertIn('Traceback', Path(failed['log']).read_text())
            self.assertNotEqual(status['log'], failed['log'])


if __name__ == '__main__':
    unittest.main()
