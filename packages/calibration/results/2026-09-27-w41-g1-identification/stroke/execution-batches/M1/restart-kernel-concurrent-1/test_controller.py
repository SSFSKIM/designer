"""Synthetic suite for controller.py: real child processes, a fake root, a fake gate.

Children are a small stand-in runner that publishes the scheduler's claim, solver-start,
deferral, failure and result files for its task the way memo_runner_v3 does, and holds its
"fit" until the test releases it. The gate is a stand-in with the v4 gate's shape: it counts
every identity-valid live claim as a reservation and admits while effective concurrency is
within its cap, so the controller never decides concurrency itself. No scheduler root,
receipt, native reader or fit is touched.

Run: /tmp/w39-g2-wgpu/bin/python -B -X pycache_prefix=FRESH_EMPTY_DIR -m unittest -v test_controller
(from this directory).
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import controller as c  # noqa: E402

old = c.old
METRIC = old.policy.v3.MEMORY_METRIC_V4
SCHEDULER = c.STROKE / 'scheduler/scheduler.py'
SOURCES = {'synthetic-source': 'synthetic'}

RUNNER = r'''
import importlib.util, json, os, pathlib, sys, time
root, idx, script, scheduler = pathlib.Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
spec = importlib.util.spec_from_file_location('synthetic_scheduler', scheduler)
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
modes = json.loads(pathlib.Path(script).read_text())[str(idx)]
n = 1
while True:
    try:
        os.close(os.open(root / f'attempt-{idx}-{n}', os.O_CREAT | os.O_EXCL)); break
    except FileExistsError:
        n += 1
mode = modes[min(n, len(modes)) - 1]
name = f'curvature-M1-start-{idx:02d}.json'
def put(folder, body):
    s.immutable(root / folder / name, body)
decision = {'policyVersion': 4, 'admitted': False, 'resourceMode': 'normal',
            'memory': {'metric': sys.argv[5], 'availableBytes': 1}, 'reservedBytes': 2,
            'effectiveConcurrency': 4}
time.sleep(mode.get('beforeClaim', 0))
if mode['kind'] == 'cli_deferred':
    print('Traceback (most recent call last):')
    print('  File "memo_runner_v3.py", line 1, in <module>')
    print('verification_scheduler.Deferred: ' + json.dumps(decision), flush=True)
    sys.exit(1)
if mode['kind'] == 'crash':
    print('ValueError: synthetic crash before claim', flush=True)
    sys.exit(2)
claim = {'task': ['M1', 'curvature', idx], 'pid': os.getpid(),
         'processIdentity': s.process_identity(os.getpid())}
put('claims', claim)
if mode['kind'] == 'claimed_deferral':
    put('deferrals', {'kind': 'STROKE_NO_FIT_DEFERRAL', 'solverStarted': False})
    sys.exit(1)
time.sleep(mode.get('beforeStart', 0))
put('started', {'pid': os.getpid(), 'processIdentity': claim['processIdentity']})
deadline = time.monotonic() + 120
while not (root / f'release-{idx}').exists() and time.monotonic() < deadline:
    time.sleep(0.02)
put('results', {'validationRead': False, 'holdoutRead': False, 'policyVersion': 4,
                'memoizationOperationalSourceSha256': {'synthetic-source': 'synthetic'},
                'schedulerClaim': claim})
'''


def wait_for(condition, timeout=30, what='condition'):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(0.02)
    raise AssertionError('timed out waiting for ' + what)


class Gate:
    """Stand-in for the v4 gate: live identity-valid claims reserve; cap bounds admission."""

    def __init__(self, root, cap):
        self.root, self.cap, self.open, self.error = root, cap, True, None
        self.calls = []

    def live(self):
        tasks = []
        for path in sorted((self.root / 'claims').glob('*.json')):
            claim = json.loads(path.read_text())
            if old.s.process_identity(claim['pid']) == claim['processIdentity']:
                tasks.append(claim['task'][2])
        return tasks

    def __call__(self, launch):
        if self.error:
            raise self.error
        live = self.live()
        effective = len(live) + 1
        decision = {'resourceMode': 'normal', 'memory': {'availableBytes': 10, 'metric': METRIC},
                    'reservedBytes': len(live), 'effectiveConcurrency': effective,
                    'modeConcurrencyLimit': self.cap, 'freshestPressure': {'pressureLevel': 1}}
        admitted = self.open and effective <= self.cap
        self.calls.append({'task': launch['task'][2], 'live': live, 'effective': effective,
                           'admitted': admitted, 'at': time.monotonic()})
        if not admitted:
            refusal = old.s.Deferred('synthetic refusal')
            refusal.decision = decision
            raise refusal
        return decision


class Harness(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='m1-concurrent-test-'))
        self.root = self.tmp / 'root'
        for name in ('claims', 'started', 'deferrals', 'failures', 'results'):
            (self.root / name).mkdir(parents=True)
        self.out = self.tmp / 'out'
        self.out.mkdir()
        (self.tmp / 'runner.py').write_text(RUNNER)
        self.modes = {}
        self.children = []
        self.verified = []

    def tearDown(self):
        for idx in range(16):
            (self.root / f'release-{idx}').touch()
        for proc in self.children:
            proc.wait(timeout=60)

    def entry(self, idx):
        return {'task': ['M1', 'curvature', idx],
                'receipt': {'path': f'/synthetic/receipt-{idx}', 'sha256': f'r{idx}'},
                'argv': [sys.executable, '-B', '-X',
                         f'pycache_prefix={self.tmp}/prefix-{idx:02d}',
                         str(self.tmp / 'runner.py'), str(self.root), str(idx),
                         str(self.tmp / 'modes.json'), str(SCHEDULER), METRIC],
                'expectedResult': str(self.root / 'results' / f'curvature-M1-start-{idx:02d}.json')}

    def set_modes(self, **modes):
        self.modes.update({k.lstrip('t'): v for k, v in modes.items()})
        (self.tmp / 'modes.json').write_text(json.dumps(self.modes))

    def verify(self, entry):
        # The serial driver's verify, reduced to what a synthetic root can mean:
        # the current generation is unused and the result absent.
        self.verified.append(entry['task'][2])
        lifecycle = [self.root / d / old.claim_name(entry) for d in c.LIFECYCLE]
        if Path(entry['expectedResult']).exists() or any(p.exists() for p in lifecycle):
            raise ValueError('current generation already used')
        return {'task': entry['task'], 'resourceSourceSha256': SOURCES}

    def adopt(self, idx, *, identity=None):
        """A fit started by someone else, as the serial controller's child was."""
        self.set_modes(**{f't{idx}': [{'kind': 'fit'}]})
        entry = self.entry(idx)
        proc = subprocess.Popen(entry['argv'], stdout=subprocess.DEVNULL)
        self.children.append(proc)
        claim = self.root / 'claims' / f'curvature-M1-start-{idx:02d}.json'
        wait_for(lambda: (self.root / 'started' / claim.name).exists(), what='adopted start')
        live = old.s.process_identity(proc.pid)
        return c.Slot(entry, {'resourceSourceSha256': SOURCES}, proc.pid, ordinal=0,
                      identity=identity or live, claim_sha256=c.digest(claim)), proc

    def controller(self, pending, adopted=(), gate=None, identify=None, healthy=None):
        self.gate = gate or Gate(self.root, 3)
        self.journal = c.Journal(self.out / 'run.jsonl')
        self.ctl = c.Controller(root=self.root, out=self.out,
                                pending=[self.entry(i) for i in pending], adopted=list(adopted),
                                verify=self.verify, admit=self.gate,
                                identify=identify or old.s.process_identity,
                                healthy=healthy or (lambda: None), journal=self.journal,
                                admission_interval=0.3, poll_interval=0.02)
        self.error = None

        def body():
            try:
                self.ctl.run()
            except BaseException as error:  # noqa: B902 - reported to the test thread
                self.error = error
            finally:
                self.journal.close()
        self.thread = threading.Thread(target=body, daemon=True)
        self.thread.start()

    def join(self):
        self.thread.join(timeout=60)
        self.assertFalse(self.thread.is_alive(), 'controller did not end')

    def rows(self, kind=None):
        rows = [json.loads(line) for line in (self.out / 'run.jsonl').read_text().splitlines()]
        return [r for r in rows if kind is None or r['kind'] == kind]

    def started(self, idx):
        return (self.root / 'started' / f'curvature-M1-start-{idx:02d}.json').exists()

    def release(self, idx):
        (self.root / f'release-{idx}').touch()


class ConcurrentDispatch(Harness):
    def test_two_starts_admitted_concurrently_beside_the_adopted_fit(self):
        adopted, proc = self.adopt(8)
        self.set_modes(t9=[{'kind': 'fit'}], t10=[{'kind': 'fit'}], t11=[{'kind': 'fit'}])
        self.controller([9, 10, 11], adopted=[adopted])
        wait_for(lambda: self.started(9) and self.started(10), what='two live starts')
        # Cap 3 with the adopted fit reserved: the third new start is refused, not launched.
        wait_for(lambda: any(call['task'] == 11 and not call['admitted']
                             for call in self.gate.calls), what='refusal at the cap')
        admitted = [call for call in self.gate.calls if call['admitted']]
        self.assertEqual([(a['task'], a['live']) for a in admitted], [(9, [8]), (10, [8, 9])])
        refused = [call for call in self.gate.calls if not call['admitted']]
        self.assertTrue(all(r['task'] == 11 and r['effective'] == 4 and r['live'] == [8, 9, 10]
                            for r in refused))
        self.assertEqual([r['task'][2] for r in self.rows('launch')], [9, 10])
        self.assertEqual(self.rows('finish'), [])
        waits = self.rows('resource_wait')
        self.assertTrue(waits and all(w['effectiveConcurrency'] == 4 for w in waits))
        # Refusals are re-evaluated on the admission interval, not every poll.
        times = [r['at'] for r in refused]
        self.assertTrue(all(b - a >= 0.29 for a, b in zip(times, times[1:])))
        # The adopted fit ends: audited from files, no exit code; capacity frees at once.
        self.release(8)
        wait_for(lambda: self.started(11), what='queued start after capacity frees')
        finish = self.rows('finish')[0]
        self.assertEqual((finish['task'][2], finish['adopted'], finish['exitCode'],
                          finish['problem']), (8, True, None, None))
        self.assertEqual(finish['observedIdentity']['command'], '<defunct>')
        for idx in (9, 10, 11):
            self.release(idx)
        self.join()
        self.assertIsNone(self.error)
        finishes = self.rows('finish')
        self.assertEqual(sorted(f['task'][2] for f in finishes), [8, 9, 10, 11])
        self.assertTrue(all(f['problem'] is None for f in finishes))
        self.assertTrue(all(f['exitCode'] == 0 for f in finishes if not f['adopted']))
        self.assertEqual([r['task'][2] for r in self.rows('launch')], [9, 10, 11])
        end = self.rows()[-1]
        self.assertEqual((end['kind'], end['launched'], end['completed']), ('batch_end', 3, 4))
        # Each child runs in its own session: a signal to the controller's group misses fits.
        launches = self.rows('launch')
        self.assertTrue(all(Path(r['stdoutPath']).exists() for r in launches))

    def test_cap_one_holds_every_start_until_the_adopted_fit_ends(self):
        adopted, _ = self.adopt(8)
        self.set_modes(t9=[{'kind': 'fit'}])
        self.controller([9], adopted=[adopted], gate=Gate(self.root, 1))
        wait_for(lambda: len(self.rows('resource_wait')) >= 2, what='two refusals')
        self.assertEqual(self.rows('launch'), [])
        self.assertTrue(all(call['live'] == [8] for call in self.gate.calls))
        self.release(8)
        wait_for(lambda: self.started(9), what='start after adopted terminal')
        self.release(9)
        self.join()
        self.assertIsNone(self.error)
        rows = self.rows()
        kinds = [r['kind'] for r in rows]
        self.assertLess(kinds.index('finish'), kinds.index('launch'))

    def test_closed_gate_waits_then_admits_when_it_opens(self):
        self.set_modes(t9=[{'kind': 'fit'}])
        gate = Gate(self.root, 3)
        gate.open = False
        self.controller([9], gate=gate)
        wait_for(lambda: len(self.rows('resource_wait')) >= 2, what='refusals')
        self.assertEqual(self.rows('launch'), [])
        gate.open = True
        wait_for(lambda: self.started(9), what='start after gate opens')
        self.release(9)
        self.join()
        self.assertIsNone(self.error)
        self.assertEqual(self.rows()[-1]['kind'], 'batch_end')

    def test_handshake_blocks_admission_until_solver_start(self):
        # Start 9 is slow to claim and slower to reach its solver start; the gate would
        # admit 10 at any moment, so any preview during the handshake would show here.
        self.set_modes(t9=[{'kind': 'fit', 'beforeClaim': 0.6, 'beforeStart': 0.6}],
                       t10=[{'kind': 'fit'}])
        self.controller([9, 10])
        wait_for(lambda: self.started(10), what='second start')
        rows = self.rows()
        kinds = [(r['kind'], r.get('task', [None] * 3)[2]) for r in rows]
        self.assertLess(kinds.index(('solver_started', 9)), kinds.index(('launch', 10)))
        started_9 = next(r for r in rows if r['kind'] == 'solver_started')
        self.assertEqual(started_9['pid'], next(r for r in rows if r['kind'] == 'launch')['pid'])
        self.assertEqual([call['task'] for call in self.gate.calls], [9, 10])
        self.assertEqual(self.gate.calls[1]['live'], [9])
        self.release(9)
        self.release(10)
        self.join()
        self.assertIsNone(self.error)
        self.assertEqual([r['task'][2] for r in self.rows('launch')], [9, 10])


class Deferrals(Harness):
    def test_no_claim_cli_deferral_is_retried_as_a_new_attempt(self):
        self.set_modes(t9=[{'kind': 'cli_deferred'}, {'kind': 'fit'}])
        self.controller([9])
        wait_for(lambda: self.started(9), what='second attempt')
        self.release(9)
        self.join()
        self.assertIsNone(self.error)
        wait_row = self.rows('cli_resource_wait')[0]
        self.assertEqual((wait_row['attempt'], wait_row['exitCode'], wait_row['effectiveConcurrency']),
                         (1, 1, 4))
        launches = self.rows('launch')
        self.assertEqual([r['attempt'] for r in launches], [1, 2])
        self.assertNotEqual(launches[0]['stdoutPath'], launches[1]['stdoutPath'])
        self.assertIn('Deferred', Path(launches[0]['stdoutPath']).read_text())
        self.assertGreaterEqual(self.gate.calls[1]['at'] - self.gate.calls[0]['at'], 0.29)
        finish = self.rows('finish')
        self.assertEqual([(f['attempt'], f['problem']) for f in finish], [(2, None)])

    def test_claimed_deferral_halts_dispatch_and_drains_the_live_fit(self):
        adopted, proc = self.adopt(8)
        self.set_modes(t9=[{'kind': 'claimed_deferral'}], t10=[{'kind': 'fit'}])
        self.controller([9, 10], adopted=[adopted])
        wait_for(lambda: self.rows('halt'), what='halt')
        self.assertIn('claimed no-fit deferral', self.rows('halt')[0]['reason'])
        time.sleep(0.5)
        self.assertEqual([r['task'][2] for r in self.rows('launch')], [9])
        self.assertIsNone(proc.poll(), 'adopted fit must keep running')
        self.assertTrue(self.thread.is_alive(), 'halted controller still audits the live fit')
        self.release(8)
        self.join()
        self.assertIsInstance(self.error, RuntimeError)
        finishes = {f['task'][2]: f for f in self.rows('finish')}
        self.assertTrue(finishes[9]['deferralExists'])
        self.assertIsNone(finishes[8]['problem'])
        self.assertEqual(self.rows()[-1]['kind'], 'stop')
        self.assertEqual(self.rows()[-1]['queued'], [['M1', 'curvature', 10]])

    def test_crash_without_claim_is_not_retried(self):
        self.set_modes(t9=[{'kind': 'crash'}, {'kind': 'fit'}])
        self.controller([9])
        self.join()
        self.assertIsInstance(self.error, RuntimeError)
        self.assertEqual(len(self.rows('launch')), 1)
        self.assertEqual(self.rows('finish')[0]['problem'], 'CLI failure')


class Adoption(Harness):
    def test_adopted_identity_mismatch_without_result_fails_closed(self):
        adopted, proc = self.adopt(8)
        adopted.identity = dict(adopted.identity, startedUTC='2000-01-01T00:00:00+00:00')
        self.set_modes(t9=[{'kind': 'fit'}])
        self.controller([9], adopted=[adopted])
        self.join()
        self.assertIsInstance(self.error, RuntimeError)
        self.assertEqual(self.rows('launch'), [])
        self.assertEqual(self.gate.calls, [])
        finish = self.rows('finish')[0]
        self.assertEqual((finish['adopted'], finish['problem']),
                         (True, 'failure or missing exact-once result'))
        self.assertIsNone(proc.poll(), 'the mismatched process is never signalled')

    def test_adopted_claim_bytes_must_match_the_handoff(self):
        adopted, _ = self.adopt(8)
        adopted.claim_sha256 = '0' * 64
        self.controller([], adopted=[adopted])
        self.release(8)
        self.join()
        self.assertIsInstance(self.error, RuntimeError)
        self.assertEqual(self.rows('finish')[0]['problem'],
                         'adopted claim identity or bytes changed')

    def plan_fixture(self):
        (self.tmp / 'src').write_text('pinned')
        sources = {str(self.tmp / 'src'): c.digest(self.tmp / 'src')}
        entries = []
        for idx in range(4, 16):
            receipt = self.tmp / f'receipt-{idx}.json'
            receipt.write_text(json.dumps({'task': ['M1', 'curvature', idx], 'receiptVersion': 4,
                                           'resourceSourceSha256': sources}))
            entry = self.entry(idx)
            entry['receipt'] = {'path': str(receipt), 'sha256': c.digest(receipt)}
            entries.append(entry)
        by = {e['task'][2]: e for e in entries}
        completed = []
        for idx in range(4, 8):
            Path(by[idx]['expectedResult']).write_text('{"done": %d}' % idx)
            completed.append({'task': by[idx]['task'], 'result': {
                'path': by[idx]['expectedResult'], 'sha256': c.digest(by[idx]['expectedResult'])}})
        identity = {'pid': 4242, 'startedUTC': '2026-09-28T07:37:25+00:00', 'command': 'fit'}
        name = old.claim_name(by[8])
        claim_path, started_path = self.root / 'claims' / name, self.root / 'started' / name
        claim_path.write_text(json.dumps({'task': by[8]['task'], 'pid': 4242,
                                          'processIdentity': identity,
                                          'launch': by[8]['receipt']}))
        claim_ref = {'path': str(claim_path), 'sha256': c.digest(claim_path)}
        started_path.write_text(json.dumps({'pid': 4242, 'processIdentity': identity,
                                            'claim': claim_ref}))
        handoff = {'completed': completed, 'policySourceSha256': sources,
                   'liveChild': {'task': by[8]['task'], 'pid': 4242, 'processIdentity': identity,
                                 'receipt': by[8]['receipt'], 'claim': claim_ref,
                                 'solverStarted': {'path': str(started_path),
                                                   'sha256': c.digest(started_path)},
                                 'expectedResult': by[8]['expectedResult']},
                   'pending': [{'task': by[i]['task'], 'receipt': by[i]['receipt'],
                                'expectedResult': by[i]['expectedResult']} for i in range(9, 16)]}
        return entries, handoff

    def test_plan_skips_completed_adopts_live_and_verifies_pending(self):
        entries, handoff = self.plan_fixture()
        done, adopted, pending = c.plan(entries, handoff, root=self.root,
                                        verify_pending=self.verify)
        self.assertEqual([d['path'] for d in done], [e['expectedResult'] for e in entries[:4]])
        self.assertEqual((adopted.entry['task'][2], adopted.pid, adopted.adopted), (8, 4242, True))
        self.assertEqual([e['task'][2] for e in pending], list(range(9, 16)))
        self.assertEqual(self.verified, list(range(9, 16)))

    def test_plan_refuses_changed_completed_result(self):
        entries, handoff = self.plan_fixture()
        Path(entries[1]['expectedResult']).write_text('{"done": "changed"}')
        with self.assertRaisesRegex(ValueError, 'completed result changed'):
            c.plan(entries, handoff, root=self.root, verify_pending=self.verify)

    def test_plan_refuses_handoff_identity_that_the_claim_does_not_record(self):
        entries, handoff = self.plan_fixture()
        handoff['liveChild']['processIdentity'] = dict(
            handoff['liveChild']['processIdentity'], command='another process')
        with self.assertRaisesRegex(ValueError, 'adopted identity mismatch'):
            c.plan(entries, handoff, root=self.root, verify_pending=self.verify)

    def test_plan_refuses_a_pending_start_whose_generation_is_used(self):
        entries, handoff = self.plan_fixture()
        (self.root / 'claims' / 'curvature-M1-start-12.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'already used'):
            c.plan(entries, handoff, root=self.root, verify_pending=self.verify)

    def test_plan_refuses_a_reordered_partition(self):
        entries, handoff = self.plan_fixture()
        handoff['pending'][0], handoff['pending'][1] = handoff['pending'][1], handoff['pending'][0]
        with self.assertRaisesRegex(ValueError, 'partition'):
            c.plan(entries, handoff, root=self.root, verify_pending=self.verify)


class Cleanup(Harness):
    def test_admission_exception_halts_but_the_live_fit_finishes_and_is_audited(self):
        self.set_modes(t9=[{'kind': 'fit'}], t10=[{'kind': 'fit'}])
        self.controller([9, 10], gate=Gate(self.root, 1))
        wait_for(lambda: self.rows('resource_wait'), what='10 held at the cap')
        self.gate.error = ValueError('synthetic reader failure')
        wait_for(lambda: self.rows('halt'), what='halt')
        self.assertIn('synthetic reader failure', self.rows('halt')[0]['reason'])
        self.assertTrue(self.thread.is_alive())
        self.release(9)
        self.join()
        self.assertIsInstance(self.error, RuntimeError)
        self.assertEqual([(f['task'][2], f['problem']) for f in self.rows('finish')], [(9, None)])
        self.assertEqual([r['task'][2] for r in self.rows('launch')], [9])

    def test_unexpected_exception_records_and_leaves_fits_running(self):
        self.set_modes(t9=[{'kind': 'fit'}])
        broken = threading.Event()

        def identify(pid):
            if broken.is_set():
                raise ValueError('synthetic ps failure')
            return old.s.process_identity(pid)
        adopted, adopted_proc = self.adopt(8)
        self.controller([9], adopted=[adopted], identify=identify)
        wait_for(lambda: self.started(9), what='own start')
        broken.set()
        self.join()
        self.assertIsInstance(self.error, ValueError)
        stop = self.rows()[-1]
        self.assertEqual(stop['kind'], 'stop')
        own = self.rows('launch')[0]['pid']
        self.assertEqual(sorted(f['pid'] for f in stop['liveFitsLeftRunning']),
                         sorted([own, adopted_proc.pid]))
        child = self.ctl.slots[('M1', 'curvature', 9)].proc
        self.children.append(child)
        self.assertIsNone(child.poll(), 'own fit keeps running after the controller stops')
        self.assertEqual(os.getpgid(child.pid), child.pid, 'fit runs in its own session')
        self.assertIsNone(adopted_proc.poll())
        self.release(9)
        self.assertEqual(child.wait(timeout=30), 0)
        self.assertTrue(Path(self.entry(9)['expectedResult']).exists())

    def test_health_failure_halts_new_dispatch_only(self):
        self.set_modes(t9=[{'kind': 'fit'}], t10=[{'kind': 'fit'}])
        reason = []
        self.controller([9, 10], gate=Gate(self.root, 1),
                        healthy=lambda: reason[0] if reason else None)
        wait_for(lambda: self.rows('resource_wait'), what='10 held at the cap')
        reason.append('serial controller resumed; dispatch cannot have two owners')
        wait_for(lambda: self.rows('halt'), what='halt')
        self.release(9)
        self.join()
        self.assertIsInstance(self.error, RuntimeError)
        self.assertEqual([r['task'][2] for r in self.rows('launch')], [9])
        self.assertIsNone(self.rows('finish')[0]['problem'])

    def test_journal_is_never_overwritten(self):
        journal = c.Journal(self.out / 'run.jsonl')
        journal('restart')
        journal.close()
        with self.assertRaises(FileExistsError):
            c.Journal(self.out / 'run.jsonl')


class Reuse(unittest.TestCase):
    def test_serial_driver_is_the_reviewed_bytes(self):
        self.assertEqual(hashlib.sha256(c.SERIAL_DRIVER.read_bytes()).hexdigest(),
                         c.SERIAL_DRIVER_SHA256)
        self.assertIs(c.Deferred, old.s.Deferred)

    def test_cli_deferral_parse_requires_policy_v4_kernel_metric(self):
        decision = {'policyVersion': 4, 'admitted': False, 'memory': {'metric': METRIC}}
        text = 'Traceback (most recent call last):\nx.Deferred: ' + json.dumps(decision)
        self.assertEqual(old.parse_cli_deferred(text), decision)
        wrong = dict(decision, memory={'metric': 'counter'})
        self.assertIsNone(old.parse_cli_deferred(
            'Traceback (most recent call last):\nx.Deferred: ' + json.dumps(wrong)))


if __name__ == '__main__':
    unittest.main()
