"""Synthetic suite for the readmit-3 concurrent entry: real children, fake root, fake gate.

The stand-in runner publishes claim/started/deferral/failure files under the lifecycle name
it is given and its result under the task name, as memo_runner_v3 does for a linked
readmission. The stand-in gate counts identity-valid live claims (any generation) as
reservations and admits within its cap, so concurrency is the gate's decision. No scheduler
root, receipt, native reader or fit is touched.

Run: /tmp/w39-g2-wgpu/bin/python -B -X pycache_prefix=FRESH_EMPTY_DIR -m unittest -v test_controller
(from this directory).
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import controller as c  # noqa: E402

engine, old = c.engine, c.old
METRIC = old.policy.v3.MEMORY_METRIC_V4
SCHEDULER = c.STROKE / 'scheduler/scheduler.py'
SOURCES = {'synthetic-source': 'synthetic'}

RUNNER = r'''
import importlib.util, json, os, pathlib, sys, time
root, idx, script, scheduler, metric, name = sys.argv[1:7]
root, idx = pathlib.Path(root), int(idx)
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
time.sleep(mode.get('beforeClaim', 0))
if mode['kind'] == 'cli_deferred':
    decision = {'policyVersion': 4, 'admitted': False, 'resourceMode': 'degraded',
                'memory': {'metric': metric, 'availableBytes': 1}, 'reservedBytes': 2,
                'effectiveConcurrency': 2}
    print('Traceback (most recent call last):')
    print('verification_scheduler.Deferred: ' + json.dumps(decision), flush=True)
    sys.exit(1)
claim = {'task': ['M1', 'curvature', idx], 'pid': os.getpid(),
         'processIdentity': s.process_identity(os.getpid())}
s.immutable(root / 'claims' / name, claim)
if mode['kind'] == 'claimed_deferral':
    s.immutable(root / 'deferrals' / name, {'kind': 'STROKE_NO_FIT_DEFERRAL'})
    sys.exit(1)
s.immutable(root / 'started' / name, {'pid': os.getpid()})
deadline = time.monotonic() + 120
while not (root / f'release-{idx}').exists() and time.monotonic() < deadline:
    time.sleep(0.02)
s.immutable(root / 'results' / f'curvature-M1-start-{idx:02d}.json',
            {'validationRead': False, 'holdoutRead': False, 'policyVersion': 4,
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
    def __init__(self, root, cap):
        self.root, self.cap, self.calls = root, cap, []

    def __call__(self, launch):
        live = []
        for path in sorted((self.root / 'claims').glob('*.json')):
            claim = json.loads(path.read_text())
            if old.s.process_identity(claim['pid']) == claim['processIdentity']:
                live.append(claim['task'][2])
        effective = len(live) + 1
        admitted = effective <= self.cap
        self.calls.append({'task': launch['task'][2], 'live': live, 'effective': effective,
                           'admitted': admitted})
        decision = {'resourceMode': 'normal', 'memory': {'availableBytes': 10, 'metric': METRIC},
                    'reservedBytes': len(live), 'effectiveConcurrency': effective,
                    'modeConcurrencyLimit': self.cap, 'freshestPressure': {'pressureLevel': 1}}
        if not admitted:
            refusal = old.s.Deferred('synthetic refusal')
            refusal.decision = decision
            raise refusal
        return decision


class Harness(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='m1-concurrent2-test-'))
        self.root = self.tmp / 'root'
        for name in ('claims', 'started', 'deferrals', 'failures', 'results'):
            (self.root / name).mkdir(parents=True)
        self.out = self.tmp / 'out'
        self.out.mkdir()
        (self.tmp / 'runner.py').write_text(RUNNER)
        self.modes = {}

    def tearDown(self):
        for idx in range(16):
            (self.root / f'release-{idx}').touch()
        if hasattr(self, 'thread'):
            self.thread.join(timeout=60)

    def entry(self, idx):
        entry = {'task': ['M1', 'curvature', idx],
                 'receipt': {'path': f'/synthetic/receipt-{idx}', 'sha256': f'r{idx}'},
                 'expectedResult': str(self.root / 'results' / f'curvature-M1-start-{idx:02d}.json')}
        entry['argv'] = [sys.executable, '-B', '-X', f'pycache_prefix={self.tmp}/prefix-{idx:02d}',
                         str(self.tmp / 'runner.py'), str(self.root), str(idx),
                         str(self.tmp / 'modes.json'), str(SCHEDULER), METRIC,
                         c.claim_name(entry)]
        return entry

    def set_modes(self, **modes):
        self.modes.update({k.lstrip('t'): v for k, v in modes.items()})
        (self.tmp / 'modes.json').write_text(json.dumps(self.modes))

    def settled_generation_zero_09(self):
        """What the root holds for 09 after the first concurrent run: gen-0 claim + deferral."""
        for folder in ('claims', 'deferrals'):
            (self.root / folder / 'curvature-M1-start-09.json').write_text(
                json.dumps({'task': ['M1', 'curvature', 9], 'pid': 1, 'generation': 0,
                            'processIdentity': {'pid': 1, 'startedUTC': '2026-09-28T08:38:03+00:00',
                                                'command': 'exited generation-0 claimant'}}))

    def verify(self, entry, *, name=c.claim_name):
        if Path(entry['expectedResult']).exists() \
                or any((self.root / d / name(entry)).exists() for d in engine.LIFECYCLE):
            raise ValueError('current generation already used')
        return {'task': entry['task'], 'resourceSourceSha256': SOURCES}

    def controller(self, pending, cap=3, name=c.claim_name, verify=None):
        self.gate = Gate(self.root, cap)
        self.journal = engine.Journal(self.out / 'run.jsonl')
        self.ctl = engine.Controller(
            root=self.root, out=self.out, pending=[self.entry(i) for i in pending], adopted=[],
            verify=verify or (lambda e: self.verify(e, name=name)), admit=self.gate,
            identify=old.s.process_identity, healthy=lambda: None, journal=self.journal,
            claim_name=name, admission_interval=0.3, poll_interval=0.02)
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
        return (self.root / 'started' / c.claim_name(self.entry(idx))).exists()

    def release(self, *indices):
        for idx in indices:
            (self.root / f'release-{idx}').touch()


class Naming(unittest.TestCase):
    def test_linked_task_is_generation_one_and_others_generation_zero(self):
        def e(i):
            return {'task': ['M1', 'curvature', i]}
        self.assertEqual(c.claim_name(e(9)), 'curvature-M1-start-09.readmit-01.json')
        self.assertEqual(old.result_name(e(9)), 'curvature-M1-start-09.json')
        self.assertEqual([c.claim_name(e(i)) for i in range(10, 16)],
                         [f'curvature-M1-start-{i:02d}.json' for i in range(10, 16)])
        # The serial driver's naming is the one being replaced for 09.
        self.assertEqual(old.claim_name(e(9)), 'curvature-M1-start-09.json')

    def test_engine_is_the_pinned_bytes(self):
        self.assertEqual(hashlib.sha256(c.ENGINE.read_bytes()).hexdigest(), c.ENGINE_SHA256)


class Dispatch(Harness):
    def test_empty_live_list_launches_the_generation_one_start_at_once(self):
        self.settled_generation_zero_09()
        self.set_modes(t9=[{'kind': 'fit'}])
        self.controller([9])
        wait_for(lambda: self.started(9), what='09 generation 1')
        self.assertEqual(self.gate.calls[0], {'task': 9, 'live': [], 'effective': 1,
                                              'admitted': True})
        launch = self.rows('launch')[0]
        self.assertEqual(launch['currentGenerationClaim'], 'curvature-M1-start-09.readmit-01.json')
        self.release(9)
        self.join()
        self.assertIsNone(self.error)
        finish = self.rows('finish')[0]
        self.assertIsNone(finish['problem'])
        self.assertTrue(finish['resultPath'].endswith('/results/curvature-M1-start-09.json'))
        self.assertEqual(finish['claimSha256'], engine.digest(
            self.root / 'claims' / 'curvature-M1-start-09.readmit-01.json'))
        self.assertTrue((self.root / 'deferrals' / 'curvature-M1-start-09.json').exists())
        self.assertEqual(self.rows()[-1]['kind'], 'batch_end')

    def test_serial_naming_would_misread_the_settled_generation_zero(self):
        # Negative control: with the serial driver's naming, 09's settled generation-0
        # files are read as this attempt's, and a clean generation-1 fit halts dispatch.
        self.settled_generation_zero_09()
        self.set_modes(t9=[{'kind': 'fit'}])
        self.release(9)
        self.controller([9], name=old.claim_name,
                        verify=lambda e: {'task': e['task'], 'resourceSourceSha256': SOURCES})
        self.join()
        self.assertIsInstance(self.error, RuntimeError)
        self.assertTrue(self.rows('halt'))
        self.assertNotEqual(self.rows('finish')[0]['problem'], None)

    def test_gate_admits_three_concurrent_starts_and_holds_the_fourth(self):
        self.settled_generation_zero_09()
        self.set_modes(**{f't{i}': [{'kind': 'fit'}] for i in (9, 10, 11, 12)})
        self.controller([9, 10, 11, 12])
        wait_for(lambda: all(self.started(i) for i in (9, 10, 11)), what='three live starts')
        wait_for(lambda: any(not call['admitted'] for call in self.gate.calls), what='refusal')
        admitted = [(a['task'], a['live']) for a in self.gate.calls if a['admitted']]
        self.assertEqual(admitted, [(9, []), (10, [9]), (11, [9, 10])])
        self.assertTrue(all(r['effectiveConcurrency'] == 4 and r['task'][2] == 12
                            for r in self.rows('resource_wait')))
        self.assertEqual(self.rows('finish'), [])
        self.release(10)
        wait_for(lambda: self.started(12), what='fourth start after capacity frees')
        self.release(9, 11, 12)
        self.join()
        self.assertIsNone(self.error)
        self.assertEqual(sorted(f['task'][2] for f in self.rows('finish')), [9, 10, 11, 12])
        self.assertTrue(all(f['problem'] is None for f in self.rows('finish')))
        end = self.rows()[-1]
        self.assertEqual((end['kind'], end['launched'], end['completed']), ('batch_end', 4, 4))

    def test_cap_one_is_serial(self):
        self.settled_generation_zero_09()
        self.set_modes(t9=[{'kind': 'fit'}], t10=[{'kind': 'fit'}])
        self.controller([9, 10], cap=1)
        wait_for(lambda: self.started(9) and self.rows('resource_wait'), what='10 held')
        self.assertEqual([r['task'][2] for r in self.rows('launch')], [9])
        self.release(9)
        wait_for(lambda: self.started(10), what='10 after 09')
        self.release(10)
        self.join()
        self.assertIsNone(self.error)
        kinds = [(r['kind'], r.get('task', [0, 0, 0])[2]) for r in self.rows()]
        self.assertLess(kinds.index(('finish', 9)), kinds.index(('launch', 10)))


class Deferrals(Harness):
    def test_no_claim_deferral_of_generation_one_retries(self):
        self.settled_generation_zero_09()
        self.set_modes(t9=[{'kind': 'cli_deferred'}, {'kind': 'fit'}])
        self.controller([9])
        wait_for(lambda: self.started(9), what='attempt 2')
        self.release(9)
        self.join()
        self.assertIsNone(self.error)
        self.assertEqual(self.rows('cli_resource_wait')[0]['attempt'], 1)
        self.assertEqual([r['attempt'] for r in self.rows('launch')], [1, 2])
        self.assertEqual([(f['attempt'], f['problem']) for f in self.rows('finish')], [(2, None)])

    def test_claimed_deferral_halts_new_dispatch_and_drains_the_live_fit(self):
        self.settled_generation_zero_09()
        self.set_modes(t9=[{'kind': 'fit'}], t10=[{'kind': 'claimed_deferral'}],
                       t11=[{'kind': 'fit'}])
        self.controller([9, 10, 11])
        wait_for(lambda: self.rows('halt'), what='halt')
        self.assertIn('curvature-M1-start-10: claimed no-fit deferral',
                      self.rows('halt')[0]['reason'])
        time.sleep(0.4)
        self.assertEqual([r['task'][2] for r in self.rows('launch')], [9, 10])
        self.assertTrue(self.thread.is_alive(), 'halted controller still audits 09')
        self.release(9)
        self.join()
        self.assertIsInstance(self.error, RuntimeError)
        finishes = {f['task'][2]: f for f in self.rows('finish')}
        self.assertIsNone(finishes[9]['problem'])
        self.assertEqual(self.rows()[-1]['queued'], [['M1', 'curvature', 11]])


class Verify(unittest.TestCase):
    """The generation-aware verify on synthetic receipts and a synthetic root."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='m1-concurrent2-verify-'))
        self.root = self.tmp / 'root'
        for name in ('claims', 'started', 'deferrals', 'failures', 'results'):
            (self.root / name).mkdir(parents=True)
        (self.tmp / 'src').write_text('pinned')
        self.predecessor = {'path': str(self.root / 'deferrals/curvature-M1-start-09.json'),
                            'sha256': 'p'}
        self.linked = {'task': ['M1', 'curvature', 9], 'predecessor': self.predecessor}

    def entry(self, idx, *, predecessor):
        prefix = str(self.tmp / f'prefix-{idx}')
        receipt = self.tmp / f'receipt-{idx}.json'
        receipt.write_text(json.dumps({
            'task': ['M1', 'curvature', idx], 'receiptVersion': 4,
            'deferredPredecessor': predecessor,
            'operationalImportPolicy': {'pycachePrefix': prefix},
            'pressureWatcher': {'path': str(self.tmp / 'scheduler-pressure-watcher-2.json')},
            'resourceSourceSha256': {str(self.tmp / 'src'): engine.digest(self.tmp / 'src')}}))
        ref = {'path': str(receipt), 'sha256': engine.digest(receipt)}
        return {'task': ['M1', 'curvature', idx], 'receipt': ref,
                'expectedResult': str(self.root / f'results/curvature-M1-start-{idx:02d}.json'),
                'argv': ['/tmp/w39-g2-wgpu/bin/python', '-B', '-X', 'pycache_prefix=' + prefix,
                         str(self.tmp / 'scheduler/memo_runner_v3.py'), '--root',
                         str(self.root), '--receipt', ref['path'], '--sha256', ref['sha256']]}

    def check(self, entry):
        return c.verify(entry, self.linked, root=self.root, stroke=self.tmp)

    def test_generation_one_passes_beside_its_settled_generation_zero(self):
        for folder in ('claims', 'deferrals'):
            (self.root / folder / 'curvature-M1-start-09.json').write_text('{}')
        self.assertEqual(self.check(self.entry(9, predecessor=self.predecessor))['task'][2], 9)
        self.assertEqual(self.check(self.entry(10, predecessor=None))['task'][2], 10)

    def test_used_generation_one_is_refused(self):
        (self.root / 'claims/curvature-M1-start-09.readmit-01.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'readmit-01.json'):
            self.check(self.entry(9, predecessor=self.predecessor))

    def test_predecessor_only_on_the_linked_task(self):
        with self.assertRaisesRegex(ValueError, 'linked predecessor mismatch'):
            self.check(self.entry(9, predecessor=None))
        with self.assertRaisesRegex(ValueError, 'linked predecessor mismatch'):
            self.check(self.entry(10, predecessor=self.predecessor))

    def test_existing_result_nonempty_prefix_and_changed_source_are_refused(self):
        entry = self.entry(10, predecessor=None)
        Path(entry['expectedResult']).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'already used'):
            self.check(entry)
        entry = self.entry(11, predecessor=None)
        (self.tmp / 'prefix-11').mkdir()
        (self.tmp / 'prefix-11/x').write_text('')
        with self.assertRaisesRegex(ValueError, 'already used'):
            self.check(entry)
        entry = self.entry(12, predecessor=None)
        (self.tmp / 'src').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'pinned source changed'):
            self.check(entry)


if __name__ == '__main__':
    unittest.main()
