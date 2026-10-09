"""DL5s re-executes the previous finalization fault matrix in a fresh synthetic namespace.
Scientific adapters and inputs are synthetic; the runner/claims/finalization are real.
"""
import contextlib
import copy
import errno
import io
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
module = types.ModuleType('analysis2_run_tests'); module.__file__ = str(HERE/'attempt2_run.py')
sys.modules[module.__name__] = module
exec(compile((HERE/'attempt2_run.py').read_bytes(), str(HERE/'attempt2_run.py'), 'exec'), module.__dict__)
R = module


class RunTests(unittest.TestCase):
    @contextlib.contextmanager
    def synthetic_run(self, cleanup_fault=False):
        """Real runner, analyzer, writer and quarantine; only scientific inputs are synthetic."""
        with tempfile.TemporaryDirectory() as tmp, contextlib.ExitStack() as stack:
            home = Path(tmp)
            for name in ('ROOT', 'CONTRACT', 'CONTRACT_PATH', 'AUTHORITY_PATH', 'UNION', 'MANIFEST', 'PREFLIGHT'):
                path = home/name.lower(); path.write_bytes(b'{}\n')
                stack.enter_context(patch.object(R.A, name, path))
            original_claim = Path(str(R.A.CONTRACT)+'.started.json')
            original_claim.write_bytes(R.W.encode({'numericalAdmission': {}}))
            for owner, name, path in ((R.A, 'NEW_MARKER', home/'marker'),
                    (R.A, 'OUTPUT', home/'output'), (R.A, 'OLD_OUTPUT', home/'old-output'),
                    (R.A, 'MARKER', home/'old-marker'), (R, 'LOGICAL', home/'logical'),
                    (R, 'TERMINAL', home/'terminal'), (R, 'COMPLETE', home/'complete'),
                    (R, 'PENDING', home/'pending'), (R, 'FAILED', home/'failed')):
                stack.enter_context(patch.object(owner, name, path, create=True))
            R.A.MARKER.write_bytes(b'{}\n')
            batch_path = home/'batch'; batch_path.write_bytes(b'{}\n')
            calls = {'measure': 0, 'judge': 0}
            union = {'members': []}
            store = types.SimpleNamespace(complete_union=lambda: union)
            data = ({}, {}, batch_path, {'cohort': []}, [], store)
            guard = types.SimpleNamespace(enforce=lambda *args: None)
            stack.enter_context(patch.object(R.A, 'verify_seal', return_value=(
                {}, {}, {}, {}, {}, {'closure': {'sources': []}}, guard)))

            @contextlib.contextmanager
            def lease():
                yield
                if cleanup_fault: raise OSError('Synthetic lease cleanup fault')

            def evaluate_measure(*args):
                calls['measure'] += 1
                return {}

            def evaluate_judge(*args):
                calls['judge'] += 1
                return {'status': 'PASS_EXPOSED_OWNER_PENDING'}

            components = {'measurement': types.SimpleNamespace(evaluate=evaluate_measure),
                          'judge': types.SimpleNamespace(evaluate=evaluate_judge)}
            admission = types.SimpleNamespace(validate_captures=lambda *args: {})
            live = types.SimpleNamespace(_LEASE={'token': 'synthetic'}, _gpu_lease=lease,
                _component=lambda view, name: (components[name], {}),
                admission_module=lambda view: admission, require_context=lambda ctx: None)
            core = {'C': types.SimpleNamespace(D=None, validate_report=lambda *args, **kw: None),
                    'L': types.SimpleNamespace(), 'Q': R.source(
                        HERE.parent/'live-execution/quarantine.py', 'analysis2_run_quarantine')}

            def activate(*args):
                context = {'executionRoot': str(R.A.ROOT), 'contract': str(R.A.CONTRACT),
                           'batchPath': str(batch_path), 'executionClaim': R.W.pin(R.A.NEW_MARKER)}
                sys.modules['w50_g1_dispatch'] = types.SimpleNamespace(admission_module=lambda view: admission)
                return context, {'captures': []}

            proof = {'status': 'CLEAN', 'synthetic': True}
            R.A.PREFLIGHT.write_bytes(R.W.encode(proof))
            plan = {'proof': proof, 'live': live, 'core': core, 'data': data, 'union': union,
                'manifest': {}, 'originalClaim': {'numericalAdmission': {}}, 'guard': guard,
                'sources': [], 'boundary': contextlib.nullcontext(),
                'roles': {name: (component, {}) for name, component in components.items()},
                'setupDispatcher': types.SimpleNamespace()}
            stack.enter_context(patch.object(R.P, 'prepare', return_value=plan))
            stack.enter_context(patch.object(R, '_PLAN', plan))
            stack.enter_context(patch.object(R.A, 'preservation', return_value={'failedAttempt': {
                'analysis': 2, 'attempt': 1, 'tombstone': 'synthetic-preserved-failure'}}))
            stack.enter_context(patch.object(R, 'modules', return_value=(live, core)))
            stack.enter_context(patch.object(R, 'admit', return_value=(data, union)))
            stack.enter_context(patch.object(R, 'activate', side_effect=activate))
            stack.enter_context(patch.object(R.R, 'Boundary', return_value=contextlib.nullcontext()))
            stack.enter_context(patch.object(R.R, 'install'))
            stack.enter_context(patch.object(R.W, 'compare', return_value={
                'status': 'MATCH', 'count': 634, 'exemptions': [], 'sha256': 'a'*64}))
            dispatcher = sys.modules.get('w50_g1_dispatch')
            try: yield calls
            finally:
                if dispatcher is None: sys.modules.pop('w50_g1_dispatch', None)
                else: sys.modules['w50_g1_dispatch'] = dispatcher

    def assert_failed_without_replay(self, calls):
        expected = {'status': 'NEITHER', 'measurementStatus': 'UNMEASURED', 'analysis': 2, 'attempt': 2}
        self.assertEqual(calls, {'measure': 1, 'judge': 1})
        self.assertEqual(R.W.parse(R.TERMINAL.read_bytes())['status'],
                         'PASS_EXPOSED_OWNER_PENDING')
        terminal_bytes = R.TERMINAL.read_bytes()
        result_bytes = (R.A.OUTPUT/'quarantine/result.json').read_bytes()
        for _ in range(3):
            self.assertEqual(R.status(), expected)
            self.assertEqual(R.run(), expected)
        for operation in ('status', 'run'):
            output = io.StringIO()
            with patch.object(sys, 'argv', ['analysis2-test', operation]), \
                 contextlib.redirect_stdout(output):
                self.assertEqual(R.main(), 1)
            self.assertEqual(R.W.parse(output.getvalue()), expected)
        self.assertEqual(calls, {'measure': 1, 'judge': 1})
        self.assertEqual(R.TERMINAL.read_bytes(), terminal_bytes)
        self.assertEqual((R.A.OUTPUT/'quarantine/result.json').read_bytes(), result_bytes)

    def test_terminal_file_and_directory_fsync_faults_cannot_revive_success(self):
        for kind in ('file', 'directory'):
            with self.subTest(kind=kind), self.synthetic_run() as calls:
                fsync = os.fsync
                faults = []
                def fail_finalization(fd):
                    info = os.fstat(fd)
                    target = R.TERMINAL if kind == 'file' else R.TERMINAL.parent
                    if R.TERMINAL.exists() and info.st_ino == target.stat().st_ino:
                        faults.append(kind)
                        raise OSError('Synthetic terminal fsync fault')
                    return fsync(fd)
                with patch.object(R.os, 'fsync', side_effect=fail_finalization):
                    self.assertEqual(R.run()['status'], 'NEITHER')
                self.assertTrue(faults)
                self.assert_failed_without_replay(calls)

    def test_completion_fsync_faults_leave_transaction_ineligible(self):
        for kind in ('file', 'staging-directory', 'commit-directory'):
            with self.subTest(kind=kind), self.synthetic_run() as calls:
                fsync, write_once = os.fsync, R.W.write_once
                staged, faults = [], []
                def stage_then_arm(path, value):
                    artifact = write_once(path, value)
                    if path == R.PENDING: staged.append(True)
                    return artifact
                def fail_completion(fd):
                    info = os.fstat(fd)
                    target = R.PENDING if kind == 'file' else R.PENDING.parent
                    written = bool(staged) if kind == 'commit-directory' else R.PENDING.exists()
                    if written and info.st_ino == target.stat().st_ino:
                        faults.append(kind)
                        raise OSError('Synthetic completion fsync fault')
                    return fsync(fd)
                with patch.object(R.W, 'write_once', side_effect=stage_then_arm), \
                     patch.object(R.os, 'fsync', side_effect=fail_completion):
                    self.assertEqual(R.run()['status'], 'NEITHER')
                self.assertTrue(faults)
                self.assertTrue(R.FAILED.is_dir())
                self.assertFalse(R.COMPLETE.exists())
                self.assert_failed_without_replay(calls)

    def test_completion_directory_and_failure_allocation_faults_cannot_publish_success(self):
        with self.synthetic_run() as calls:
            fsync, mkdir, write_once = os.fsync, Path.mkdir, R.W.write_once
            staged, faults = [], []
            def stage_then_arm(path, value):
                artifact = write_once(path, value)
                if path == R.PENDING: staged.append(True)
                return artifact
            def refuse_completion_flush(fd):
                if staged and os.fstat(fd).st_ino == R.COMPLETE.parent.stat().st_ino:
                    faults.append('completion-directory')
                    raise OSError(errno.ENOSPC, 'Synthetic completion directory fault')
                return fsync(fd)
            def refuse_failure_allocation(path, *args, **kwargs):
                if path == R.FAILED:
                    faults.append('failure-allocation')
                    raise OSError(errno.ENOSPC, 'Synthetic failure allocation fault')
                return mkdir(path, *args, **kwargs)
            result = None
            with patch.object(R.W, 'write_once', side_effect=stage_then_arm), \
                 patch.object(R.os, 'fsync', side_effect=refuse_completion_flush), \
                 patch.object(Path, 'mkdir', new=refuse_failure_allocation):
                try: result = R.run()
                except OSError: pass  # Inspect the surviving eligibility before asserting return.
            self.assertIn('completion-directory', faults)
            self.assertIn('failure-allocation', faults)
            self.assert_failed_without_replay(calls)
            self.assertEqual(result, R.unmeasured())
            self.assertFalse(R.COMPLETE.exists())
            self.assertFalse(R.FAILED.exists())

    def test_exclusive_link_is_last_io_and_authentication_operation(self):
        with self.synthetic_run() as calls:
            link, read = os.link, Path.read_bytes
            operations = {name: getattr(os, name) for name in ('fsync', 'open', 'close', 'stat', 'lstat')}
            committed, after_commit = [], []
            def commit(*args, **kwargs):
                value = link(*args, **kwargs)
                committed.append(True)
                return value
            def observe(name):
                def operation(*args, **kwargs):
                    if committed: after_commit.append(name)
                    return operations[name](*args, **kwargs)
                return operation
            def read_bytes(path):
                if committed: after_commit.append('read')
                return read(path)
            with contextlib.ExitStack() as patches:
                patches.enter_context(patch.object(R.os, 'link', side_effect=commit))
                patches.enter_context(patch.object(Path, 'read_bytes', new=read_bytes))
                for name in operations:
                    patches.enter_context(patch.object(R.os, name, side_effect=observe(name)))
                result = R.run()
            self.assertEqual(result['status'], 'PASS_EXPOSED_OWNER_PENDING')
            self.assertTrue(committed)
            self.assertEqual(after_commit, [])
            self.assertEqual(calls, {'measure': 1, 'judge': 1})
            self.assertEqual(R.status(), result)

    def test_crash_loss_of_eligibility_link_is_neither_and_never_replay(self):
        with self.synthetic_run() as calls:
            self.assertEqual(R.run()['status'], 'PASS_EXPOSED_OWNER_PENDING')
            pending_bytes = R.PENDING.read_bytes()
            R.COMPLETE.unlink()  # Model a crash losing only the unsynced synthetic eligibility link.
            self.assert_failed_without_replay(calls)
            self.assertEqual(R.PENDING.read_bytes(), pending_bytes)
            self.assertFalse(R.FAILED.exists())

    def test_transient_status_fault_revokes_eligibility_when_failure_allocation_is_unavailable(self):
        with self.synthetic_run() as calls:
            self.assertEqual(R.run()['status'], 'PASS_EXPOSED_OWNER_PENDING')
            pending_bytes = R.PENDING.read_bytes()
            sha, mkdir = R.W.sha, Path.mkdir
            faults = []
            def refuse_result_read(path):
                if path == R.A.OUTPUT/'quarantine/result.json':
                    faults.append('validation')
                    raise OSError(errno.EIO, 'Synthetic transient authentication fault')
                return sha(path)
            def refuse_failure_allocation(path, *args, **kwargs):
                if path == R.FAILED:
                    faults.append('failure-allocation')
                    raise OSError(errno.ENOSPC, 'Synthetic failure allocation fault')
                return mkdir(path, *args, **kwargs)
            with patch.object(R.W, 'sha', side_effect=refuse_result_read), \
                 patch.object(Path, 'mkdir', new=refuse_failure_allocation):
                self.assertEqual(R.status(), R.unmeasured())
            self.assertEqual(faults, ['validation', 'failure-allocation'])
            self.assert_failed_without_replay(calls)
            self.assertEqual(R.PENDING.read_bytes(), pending_bytes)
            self.assertFalse(R.COMPLETE.exists())
            self.assertFalse(R.FAILED.exists())

    def test_failed_completion_authentication_stays_failed_if_bytes_later_reappear(self):
        with self.synthetic_run() as calls:
            self.assertEqual(R.run()['status'], 'PASS_EXPOSED_OWNER_PENDING')
            completion_bytes = R.COMPLETE.read_bytes()
            R.COMPLETE.write_bytes(b'{}\n')  # Synthetic damage, not a scientific payload.
            self.assertEqual(R.status()['measurementStatus'], 'UNMEASURED')
            self.assertTrue(R.FAILED.is_dir())
            R.COMPLETE.write_bytes(completion_bytes)
            self.assert_failed_without_replay(calls)
            # Fault dominance is checked before parsing even a surviving success record.
            with patch.object(R.W, 'parse', side_effect=AssertionError('Failure must dominate')):
                self.assertEqual(R.run()['measurementStatus'], 'UNMEASURED')

    def test_quarantine_cleanup_fault_after_terminal_write_cannot_revive_success(self):
        with self.synthetic_run() as calls:
            _, core = R.modules()
            run_private = core['Q'].run_private
            def fail_after_quarantine(*args):
                run_private(*args)
                raise OSError('Synthetic quarantine cleanup fault')
            with patch.object(core['Q'], 'run_private', side_effect=fail_after_quarantine):
                self.assertEqual(R.run()['status'], 'NEITHER')
            self.assert_failed_without_replay(calls)

    def test_lease_cleanup_fault_after_terminal_write_cannot_revive_success(self):
        with self.synthetic_run(cleanup_fault=True) as calls:
            self.assertEqual(R.run()['status'], 'NEITHER')
            self.assert_failed_without_replay(calls)

    def test_success_bytes_without_independent_completion_are_unmeasured(self):
        with self.synthetic_run() as calls:
            live, core = R.modules()
            data, union = R.admit(None, None, None, None, live, core)
            R.analyze(live, core, data, union, {}, None)
            self.assert_failed_without_replay(calls)

    def test_successful_finalization_is_authenticated_and_never_reanalyzed(self):
        with self.synthetic_run() as calls:
            result = R.run()
            self.assertEqual(result['status'], 'PASS_EXPOSED_OWNER_PENDING')
            self.assertTrue(R.COMPLETE.is_file())
            self.assertFalse(R.FAILED.exists())
            for _ in range(3):
                self.assertEqual(R.status(), result)
                self.assertEqual(R.run(), result)
            self.assertEqual(calls, {'measure': 1, 'judge': 1})

    def test_marker_crash_and_output_claim_each_bar_second_and_third_invocation(self):
        for tombstone in ('marker', 'output', 'logical', 'terminal', 'pending', 'complete', 'failed'):
            with self.subTest(tombstone=tombstone), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp)
                with patch.object(R.A, 'NEW_MARKER', home/'marker'), \
                     patch.object(R.A, 'OUTPUT', home/'output'), \
                     patch.object(R, 'LOGICAL', home/'logical'), \
                     patch.object(R, 'TERMINAL', home/'terminal'), \
                     patch.object(R, 'PENDING', home/'pending'), \
                     patch.object(R, 'COMPLETE', home/'complete'), \
                     patch.object(R, 'FAILED', home/'failed'), \
                     patch.object(R.A, 'verify_seal', side_effect=AssertionError('No replay')):
                    path = home/tombstone
                    path.mkdir() if tombstone == 'output' else path.write_bytes(b'partial')
                    for _ in range(3):
                        self.assertEqual(R.run(), {'status': 'NEITHER', 'measurementStatus': 'UNMEASURED', 'analysis': 2, 'attempt': 2})

    def test_facade_keeps_actual_live_context_and_lease_guards(self):
        live, core = R.modules()
        context = {'stage': 'analysis'}
        member = {'id': 'm', 'scene': 's', 'lane': 'candidate',
                  'run': {'profile': 'p', 'renderer': 'webgpu', 'candidate': {'sha256': 'a'*64}}}
        record = {**member['run'], 'scene': 's', 'lane': 'candidate'}
        live._ACTIVE = {'context': context, 'snapshot': copy.deepcopy(context), 'hashes': [],
                        'members': [member], 'records': {'m': record}, 'payloads': []}
        facade = R.ReadOnlyDispatcher(live, None, context)
        with patch.object(core['C'].D, 'lease_owned', return_value=True):
            facade.require_context(context)
            self.assertEqual(facade.resolve_capture_run(context, record), member['run'])
            with self.assertRaises(ValueError): facade.require_context(dict(context))
            with self.assertRaises(ValueError): facade.resolve_capture_run(context, {**record, 'scene': 'other'})
            context['phase'] = 'exposure'
            with self.assertRaises(ValueError): facade.require_context(context)
            context.pop('phase')
        with patch.object(core['C'].D, 'lease_owned', return_value=False):
            with self.assertRaises(ValueError): facade.require_context(context)
        for method in ('execute_analysis', 'create_phase', 'require_render_admission',
                       'require_native_admission', 'require_owner_admission', 'qualification_native'):
            self.assertFalse(hasattr(facade, method))

    def test_run_requires_exact_preflight_and_refusal_is_permanent(self):
        with self.synthetic_run() as calls:
            R.A.PREFLIGHT.write_bytes(R.W.encode({'status': 'CLEAN', 'wrong': True}))
            self.assertEqual(R.run(), R.unmeasured())
            self.assertTrue(R.FAILED.is_dir())
            R.A.PREFLIGHT.write_bytes(R.W.encode({'status': 'CLEAN', 'synthetic': True}))
            self.assertEqual(R.run(), R.unmeasured())
            self.assertEqual(calls, {'measure': 0, 'judge': 0})
            self.assertFalse(R.A.NEW_MARKER.exists())

    def test_diagnostic_and_start_share_the_same_complete_prepare(self):
        with self.synthetic_run() as calls:
            proof = R.preflight()
            self.assertEqual(proof, R.W.parse(R.A.PREFLIGHT.read_bytes()))
            self.assertFalse(R.A.OUTPUT.exists())
            self.assertFalse(R.A.NEW_MARKER.exists())
            self.assertEqual(R.P.prepare.call_count, 1)
            self.assertEqual(R.run()['status'], 'PASS_EXPOSED_OWNER_PENDING')
            self.assertEqual(R.P.prepare.call_count, 2)
            marker = R.W.parse(R.A.NEW_MARKER.read_bytes())
            self.assertEqual(marker['attempt'], 2)
            self.assertEqual(marker['analysis'], 2)
            self.assertEqual(marker['auditCommit'], R.A.AUDIT_COMMIT)
            self.assertEqual(marker['rulingCommit'], R.A.RULING)
            self.assertEqual(marker['preflight'], R.W.pin(R.A.PREFLIGHT))
            self.assertEqual(marker['failedAttempt']['attempt'], 1)
            self.assertEqual(calls, {'measure': 1, 'judge': 1})

    def test_admission_fault_is_terminal_before_any_marker(self):
        with self.synthetic_run() as calls:
            with patch.object(R.P, 'prepare', side_effect=ValueError('synthetic admission fault')):
                self.assertEqual(R.run(), R.unmeasured())
            self.assertTrue(R.FAILED.is_dir())
            self.assertFalse(R.A.NEW_MARKER.exists())
            self.assertEqual(R.run(), R.unmeasured())
            self.assertEqual(calls, {'measure': 0, 'judge': 0})


if __name__ == '__main__': unittest.main()
