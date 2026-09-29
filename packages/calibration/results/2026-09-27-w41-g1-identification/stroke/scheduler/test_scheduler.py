"""Synthetic ownership, admission and sealed-start tests; no native reader or optimizer."""
import concurrent.futures
import contextlib
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

import scheduler


def ref(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def artifact(path, value):
    path.write_text(json.dumps(value))
    return ref(path)


def example(observations, family, css, curvature):
    rng = random.Random(4100)
    starts = [[1., .4, 0., 0.]] + [[rng.random() for _ in range(4)] for _ in range(15)]
    records = []
    for i, start in enumerate(starts):
        # Synthetic budget and full-vector work; selecting an index must change neither.
        answer = sum(sum(v * v for v in start) for _ in range(13))
        records.append({'startIndex': i, 'vector': start, 'answer': answer, 'budget': 13})
    return {'family': family, 'cssWidth': css, 'curvature': curvature, 'starts': records}


class FakeProcesses:
    """Synthetic OS process table. Liveness stays each test's own alive() set; this
    only answers WHICH process holds a PID: one stable creation identity per PID
    until a test reissues that PID to another process or removes it."""
    def __init__(self):
        self.table, self.gone = {}, set()

    def __call__(self, pid):
        if pid in self.gone:
            return None
        return dict(self.table.setdefault(pid, {
            'pid': pid, 'startedUTC': '2026-09-27T11:00:00+00:00',
            'command': f'synthetic fit driver {pid}'}))

    def reissue(self, pid, command=None, started='2026-09-27T17:58:06+00:00'):
        self.table[pid] = {'pid': pid, 'startedUTC': started,
                           'command': command or self(pid)['command']}

    def spawn(self, pid, reference):
        """PID runs the fit driver for this launch receipt, as a parent launches it."""
        self.table[pid] = dict(self(pid), command=driver_command(reference))
        return reference


def driver_command(reference):
    return (f"/tmp/w39-g2-wgpu/bin/python -B memo_runner_v3.py --root ROOT "
            f"--receipt {reference['path']} --sha256 {reference['sha256']}")


REAL_PROCESS_IDENTITY = scheduler.process_identity


@contextlib.contextmanager
def as_process(pid):
    """Run a block, in this thread only, as the synthetic process PID."""
    prior = getattr(SIMULATED, 'pid', None)
    SIMULATED.pid = pid
    try:
        yield
    finally:
        SIMULATED.pid = prior


def run_as_claimants(store):
    """Execute each synthetic claim and lifecycle step inside its simulated claimant.

    Production run() claims with os.getpid() and runs its own lifecycle. Tests
    name synthetic claimant PIDs, so each claim, pre-fit check, solver start and
    finish on this store runs as the process its claim names. The real guards
    still run; a test that must act from another process calls the class method.
    """
    claim = store.claim

    def claimed(reference, *, pid, **kwargs):
        with as_process(pid):
            return claim(reference, pid=pid, **kwargs)
    store.claim = claimed
    for name in ('check_before_fit', 'start_solver', 'finish'):
        def step(record, *args, _method=getattr(store, name), **kwargs):
            with as_process(record['pid']):
                return _method(record, *args, **kwargs)
        setattr(store, name, step)
    return store


SIMULATED = threading.local()
REAL_GETPID = os.getpid


def simulated_getpid():
    pid = getattr(SIMULATED, 'pid', None)
    return REAL_GETPID() if pid is None else pid


def fake_processes(case, module=scheduler):
    """Fake process table, and os.getpid() answering as_process's simulated PID."""
    processes = FakeProcesses()
    for target, name, value in ((module, 'process_identity', processes),
                                (module.os, 'getpid', simulated_getpid)):
        patcher = mock.patch.object(target, name, value)
        patcher.start()
        case.addCleanup(patcher.stop)
    return processes


EVENTS = []


def recorded_example(observations, family, css, curvature):
    # Records the first optimizer entry so a test can see what was durable then.
    rng = random.Random(4100)
    starts = [[1., .4, 0., 0.]] + [[rng.random() for _ in range(4)] for _ in range(15)]
    records = []
    for i, start in enumerate(starts):
        EVENTS.append(('optimizer', i))
        records.append({'startIndex': i, 'vector': start, 'answer': sum(start), 'budget': 13})
    return {'family': family, 'cssWidth': css, 'curvature': curvature, 'starts': records}


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / 'state'
        self.live = {102, 103}
        self.processes = fake_processes(self)
        self.owners = []
        for p in range(3):
            out = self.base / f'old-{p}'
            out.mkdir()
            execution = artifact(out / 'execution.json', {
                'partition': p, 'indices': list(range(p, 16, 3)), 'seed': 4100,
                'heldRevision': scheduler.REVISION})
            self.owners.append({'partition': p, 'pid': 101+p, 'taskId': f'old-{p}',
                                'outputRoot': str(out), 'execution': execution})
        self.roster = artifact(self.base / 'roster.json', {
            'kind': 'STROKE_ROSTER', 'schedulerRoot': str(self.root),
            'oldOwners': self.owners})
        self.release = artifact(self.base / 'release.json', {
            'kind': 'CAPTURESRELEASE', 'schedulerRoot': str(self.root), 'maxConcurrency': 6})
        self.direction = artifact(self.base / 'direction.json', {'ruling': 'explicit handoff'})
        self.peak = artifact(self.base / 'peak.json', {
            'kind': 'STROKE_PEAK_RSS', 'largestObservedPeakRSSBytes': scheduler.GIB,
            'samples': [{'pid': 101, 'peakRSSBytes': scheduler.GIB,
                         'source': 'synthetic measurement', 'sampledUTC': '2026-09-27T12:00:00Z'}]})
        self.store = run_as_claimants(scheduler.Store(self.root))
        self.store.initialize(self.roster)
        self.memory = {'availableBytes': 32 * scheduler.GIB, 'pressureLevel': 1,
                       'metric': scheduler.MEMORY_METRIC}

    def handoff(self, completed=None, aborted=None, **changes):
        completed = completed or []
        value = {'kind': 'STROKE_HANDOFF', 'rosterSha256': self.roster['sha256'],
                 'partition': 0, 'oldPid': 101, 'oldTaskId': 'old-0',
                 'stoppedUTC': '2026-09-27T12:00:00+00:00',
                 'boundaryTask': completed[-1]['task'] if completed else None,
                 'completed': completed, 'aborted': aborted or [], 'excluded': [],
                 'captureRelease': self.release, 'direction': self.direction}
        value.update(changes)
        return artifact(self.base / f'handoff-{len(list(self.base.glob("handoff-*")))}.json', value)

    def transfer(self, handoff=None):
        return self.store.transfer(handoff or self.handoff(), alive=self.live.__contains__)

    def launch(self, task=('M1', 'device', 0), cap=3, **changes):
        value = {'kind': 'STROKE_LAUNCH', 'rosterSha256': self.roster['sha256'],
                 'task': list(task), 'captureRelease': self.release, 'maxConcurrency': cap,
                 'peakEvidence': self.peak,
                 'reservationBytes': scheduler.GIB, 'oldWorkerReservationBytes': scheduler.GIB}
        value.update(changes)
        return artifact(self.base / f'launch-{len(list(self.base.glob("launch-*")))}.json', value)

    def spawned(self, pid, launch=None):
        return self.processes.spawn(pid, launch or self.launch())

    def claim(self, launch=None, pid=200):
        launch = self.spawned(pid, launch)
        return self.store.claim(launch, pid=pid, alive=self.live.__contains__,
                                memory=lambda: dict(self.memory))

    def started(self, claim):
        self.store.check_before_fit(claim, alive=self.live.__contains__,
                                    memory=lambda: dict(self.memory))
        self.store.start_solver(claim)
        return claim

    def complete_old(self, task=('M1', 'device', 0)):
        path = Path(self.owners[0]['outputRoot']) / scheduler.filename(task)
        result = example([], task[0], task[1] == 'css', task[1] == 'curvature')
        result['starts'] = [result['starts'][task[2]]]
        result['fittedEndpoints'] = ['light-inactive']
        result['dummyEndpoints'] = ['light-active', 'dark-active', 'dark-inactive']
        return {'task': list(task), 'artifact': artifact(path, result)}

    def test_live_old_owner_cannot_transfer(self):
        self.live.add(101)
        with self.assertRaisesRegex(ValueError, 'live'):
            self.transfer()

    def test_release_is_required_for_transfer_not_only_increase(self):
        with self.assertRaises((ValueError, KeyError)):
            self.transfer(self.handoff(captureRelease=None))

    def test_partition_remains_owned_until_individual_transfer(self):
        with self.assertRaisesRegex(ValueError, 'handoff'):
            self.claim()
        self.transfer()
        with self.assertRaisesRegex(ValueError, 'handoff'):
            self.claim(self.launch(('M1', 'device', 1)))

    def test_duplicate_transfer_and_completed_restart_are_refused(self):
        completed = self.complete_old()
        h = self.handoff([completed])
        self.transfer(h)
        with self.assertRaises(FileExistsError):
            self.transfer(h)
        with self.assertRaisesRegex(ValueError, 'completed'):
            self.claim()
        self.assertEqual(self.claim(self.launch(('M1', 'device', 3)))['task'], ['M1', 'device', 3])

    def test_unlisted_or_modified_old_checkpoint_conflicts(self):
        completed = self.complete_old()
        with self.assertRaisesRegex(ValueError, 'checkpoint'):
            self.transfer()
        h = self.handoff([completed])
        Path(completed['artifact']['path']).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.transfer(h)

    def test_completed_prefix_and_aborted_next_start_preserve_evidence(self):
        completed = self.complete_old()
        log = artifact(self.base / 'aborted.log', {'event': 'start', 'index': 3})
        aborted = [{'task': ['M1', 'device', 3], 'label': 'aborted', 'neverScored': True,
                    'evidence': [log]}]
        self.transfer(self.handoff([completed], aborted))
        self.assertEqual(self.claim(self.launch(('M1', 'device', 3)))['task'][2], 3)
        with self.assertRaisesRegex(ValueError, 'claimed'):
            self.claim(self.launch(('M1', 'device', 3)))
        self.assertEqual(ref(Path(log['path'])), log)

    def test_no_silent_retry_after_dead_claim_or_failed_result(self):
        self.transfer()
        claim = self.claim()
        self.store.fail(claim, RuntimeError('synthetic failure'))
        with self.assertRaisesRegex(ValueError, 'claimed'):
            self.claim()
        self.assertTrue((self.root / 'failures' / scheduler.filename(claim['task'])).exists())

    def test_claim_contention_has_one_winner(self):
        self.transfer()
        launch = self.launch()
        def attempt(_):
            try:
                return self.claim(launch)
            except (ValueError, FileExistsError):
                return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            winners = [x for x in pool.map(attempt, range(8)) if x is not None]
        self.assertEqual(len(winners), 1)

    def test_live_old_and_new_processes_share_one_cap(self):
        self.transfer()
        self.claim()
        self.live.add(200)
        with self.assertRaises(scheduler.Deferred):
            self.claim(self.launch(('M1', 'device', 3)), pid=201)

    def test_large_cap_requires_release_and_is_bounded_by_it(self):
        self.transfer()
        with self.assertRaises((ValueError, KeyError)):
            self.claim(self.launch(cap=4, captureRelease=None))
        with self.assertRaises(ValueError):
            self.claim(self.launch(cap=7))
        self.assertEqual(self.claim(self.launch(cap=4))['effectiveConcurrency'], 3)

    def test_memory_floor_reservations_and_pressure_defer_without_claim(self):
        self.transfer()
        launch = self.launch()
        for available, pressure in [(5 * scheduler.GIB, 1), (32 * scheduler.GIB, 2)]:
            self.memory.update(availableBytes=available, pressureLevel=pressure)
            with self.assertRaises(scheduler.Deferred):
                self.claim(launch)
            self.assertFalse(list((self.root / 'claims').glob('*.json')))
        self.memory.update(availableBytes=6 * scheduler.GIB, pressureLevel=1)
        self.assertEqual(self.claim(launch)['reservedBytes'], 3 * scheduler.GIB)

    def test_changed_pressure_defers_execution_but_preserves_claim(self):
        self.transfer()
        claim = self.claim()
        self.memory['pressureLevel'] = 2
        with self.assertRaises(scheduler.Deferred):
            self.store.check_before_fit(claim, alive=self.live.__contains__,
                                        memory=lambda: dict(self.memory))
        with self.assertRaisesRegex(ValueError, 'claimed'):
            self.claim()

    def test_results_cannot_overwrite_and_identity_must_match(self):
        self.transfer()
        claim = self.started(self.claim())
        result, _ = scheduler.selected_fit(example, [], claim['task'])
        self.store.finish(claim, result)
        with self.assertRaises(FileExistsError):
            self.store.finish(claim, result)
        self.assertEqual(json.loads((self.root / 'results' / scheduler.filename(claim['task'])).read_text())['starts'], result['starts'])

    def test_all_original_vectors_and_budgets_survive_selection(self):
        reference = example([], 'M1', False, False)
        for i in range(16):
            result, provenance = scheduler.selected_fit(example, [], ['M1', 'device', i])
            self.assertEqual(result['starts'], [reference['starts'][i]])
            self.assertFalse(provenance['budgetsChanged'])
            self.assertFalse(provenance['parameterizationChanged'])
            self.assertEqual(provenance['originalSeed'], 4100)

    def test_rss_subtraction_counts_only_unallocated_commitment(self):
        self.transfer()
        self.memory['availableBytes'] = 5 * scheduler.GIB
        claim = self.store.claim(self.spawned(200), pid=200, alive=self.live.__contains__,
            memory=lambda: dict(self.memory), rss=lambda pid: scheduler.GIB)
        self.assertEqual(claim['reservedBytes'], scheduler.GIB)
        self.assertEqual([p['rssBytes'] for p in claim['processes']], [scheduler.GIB] * 2)

    def test_unparseable_memory_fails_closed_and_logs_refusal(self):
        self.transfer()
        def broken():
            raise ValueError('unparseable vm_stat')
        with self.assertRaises(ValueError):
            self.store.claim(self.spawned(200), pid=200, alive=self.live.__contains__,
                             memory=broken)
        records = [json.loads(p.read_text()) for p in (self.root / 'admissions').glob('*.json')]
        self.assertEqual(len(records), 1)
        self.assertFalse(records[0]['admitted'])
        self.assertFalse(list((self.root / 'claims').glob('*.json')))

    def test_peak_evidence_required_and_cannot_underreserve(self):
        self.transfer()
        for change in ({'peakEvidence': None}, {'reservationBytes': scheduler.GIB - 1}):
            with self.assertRaises(ValueError):
                self.claim(self.launch(**change))
        self.assertFalse(list((self.root / 'claims').glob('*.json')))

    def test_css_remains_claimable_without_explicit_certificate_exclusion(self):
        self.transfer()
        self.assertEqual(self.claim(self.launch(('M1', 'css', 0)))['task'], ['M1', 'css', 0])

    def test_only_reviewed_css_exclusions_remove_remaining_tasks(self):
        cert = artifact(self.base / 'cert.json', {'synthetic': True})
        review = artifact(self.base / 'review.json', {'synthetic': True})
        excluded = [{'task': ['M1', 'css', 0], 'certificate': cert, 'review': review}]
        self.transfer(self.handoff(excluded=excluded))
        with self.assertRaisesRegex(ValueError, 'excluded'):
            self.claim(self.launch(('M1', 'css', 0)))
        self.assertEqual(self.claim(self.launch(('M1', 'css', 3)))['task'][2], 3)

    def test_foreign_root_and_mismatched_result_are_rejected(self):
        with self.assertRaises(ValueError):
            scheduler.Store(self.base / 'second-root').initialize(self.roster)
        self.transfer()
        claim = self.started(self.claim())
        wrong, _ = scheduler.selected_fit(example, [], ['M1', 'device', 3])
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.store.finish(claim, wrong)
        self.assertFalse(list((self.root / 'results').glob('*.json')))

    def test_simultaneous_different_starts_cannot_overbook_slots(self):
        self.transfer()
        launches = [self.launch(('M1', 'device', i)) for i in (0, 3)]
        # Both prospective PIDs are visible in the OS snapshot but only the
        # winner's immutable claim makes that process occupy a registered slot.
        self.live.update([200, 201])
        def attempt(i):
            try:
                return self.claim(launches[i], pid=200+i)
            except scheduler.Deferred:
                return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            winners = [x for x in pool.map(attempt, range(2)) if x is not None]
        self.assertEqual(len(winners), 1)

    def test_source_pins_detect_changed_partition_helper(self):
        helper = self.base / 'helper.py'
        helper.write_text('unchanged implementation')
        sources = {str(helper): ref(helper)['sha256']}
        scheduler.verify_sources(sources, [helper])
        helper.write_text('changed seed or budget')
        with self.assertRaisesRegex(ValueError, 'hash'):
            scheduler.verify_sources(sources, [helper])
        with self.assertRaises(ValueError):
            scheduler.verify_sources({}, [helper])

    def test_previous_fit_highwater_increases_next_reservation(self):
        self.transfer()
        claim = self.started(self.claim())
        result, _ = scheduler.selected_fit(example, [], claim['task'])
        result['peakRSSBytes'] = 2 * scheduler.GIB
        self.store.finish(claim, result)
        next_claim = self.claim(self.launch(('M1', 'device', 3)), pid=201)
        self.assertEqual(next_claim['reservationBytes'], 2 * scheduler.GIB)
        self.assertEqual(next_claim['reservedBytes'], 6 * scheduler.GIB)

    def test_refused_admission_rss_highwater_persists_after_rss_falls(self):
        # Receipt peak 1 GiB; two live old fits read 4 GiB each during a refusal.
        self.transfer()
        launch = self.launch()
        readings = {102: 4 * scheduler.GIB, 103: 4 * scheduler.GIB}
        claim = lambda: self.store.claim(self.spawned(200, launch), pid=200,
            alive=self.live.__contains__,
            memory=lambda: dict(self.memory), rss=readings.__getitem__)
        self.memory['availableBytes'] = 6 * scheduler.GIB
        with self.assertRaises(scheduler.Deferred):
            claim()
        # Their RSS later falls to 1 GiB. The known 4 GiB high-water still binds:
        # each old fit may regrow 3 GiB and the new fit reserves 4 GiB.
        readings.update({102: scheduler.GIB, 103: scheduler.GIB})
        with self.assertRaises(scheduler.Deferred) as refused:
            claim()
        decision = json.loads(str(refused.exception))
        self.assertEqual(decision['prospectivePeakBytes'], 4 * scheduler.GIB)
        self.assertEqual(decision['reservedBytes'], 10 * scheduler.GIB)
        self.assertFalse(list((self.root / 'claims').glob('*.json')))
        self.memory['availableBytes'] = 13 * scheduler.GIB
        self.assertEqual(claim()['reservedBytes'], 10 * scheduler.GIB)

    def test_prefit_rss_highwater_outlives_its_process(self):
        self.transfer()
        readings = {102: scheduler.GIB, 103: scheduler.GIB, 200: 4 * scheduler.GIB}
        claim = self.store.claim(self.spawned(200, self.launch(cap=4)), pid=200,
            alive=self.live.__contains__,
            memory=lambda: dict(self.memory), rss=readings.__getitem__)
        self.store.check_before_fit(claim, alive=self.live.__contains__,
            memory=lambda: dict(self.memory), rss=readings.__getitem__)
        # PID 200 died without a result (for example SIGKILL); its reading is kept.
        readings[200] = 0
        later = self.store.claim(self.spawned(201, self.launch(('M1', 'device', 3), cap=4)),
                                 pid=201,
            alive=self.live.__contains__, memory=lambda: dict(self.memory),
            rss=readings.__getitem__)
        self.assertEqual(later['prospectivePeakBytes'], 4 * scheduler.GIB)
        self.assertEqual(later['reservedBytes'], 10 * scheduler.GIB)

    def test_error_paths_fail_closed_but_retain_valid_rss_readings(self):
        self.transfer()
        def vanished(pid):
            if pid == 103:
                raise RuntimeError('ps: process disappeared')
            return 5 * scheduler.GIB
        def broken():
            raise ValueError('unparseable vm_stat')
        for rss, memory in ((vanished, lambda: dict(self.memory)),
                            (lambda pid: 6 * scheduler.GIB, broken)):
            with self.assertRaises((RuntimeError, ValueError)):
                self.store.claim(self.spawned(200), pid=200, alive=self.live.__contains__,
                                 memory=memory, rss=rss)
            self.assertFalse(list((self.root / 'claims').glob('*.json')))
        later = self.store.claim(self.spawned(200), pid=200, alive=self.live.__contains__,
            memory=lambda: dict(self.memory), rss=lambda pid: scheduler.GIB)
        self.assertEqual(later['prospectivePeakBytes'], 6 * scheduler.GIB)
        records = [json.loads(p.read_text()) for p in (self.root / 'admissions').glob('*.json')]
        self.assertEqual(sum(not r['admitted'] and 'error' in r for r in records
                             if r.get('kind') != scheduler.RSS_OBSERVATION), 2)

    def check(self, claim):
        return self.store.check_before_fit(claim, alive=self.live.__contains__,
                                           memory=lambda: dict(self.memory))

    def defer(self, claim):
        self.memory['pressureLevel'] = 2
        with self.assertRaises(scheduler.Deferred):
            self.check(claim)
        self.memory['pressureLevel'] = 1
        return ref(self.root / 'deferrals' / scheduler.claim_name(claim))

    def test_prefit_memory_deferral_links_exactly_one_readmission(self):
        self.transfer()
        first = self.claim()
        self.memory['pressureLevel'] = 2
        with self.assertRaises(scheduler.Deferred) as refused:
            self.check(first)
        scheduler.settle(self.store, first, refused.exception)
        deferral = ref(self.root / 'deferrals' / scheduler.claim_name(first))
        receipt = scheduler.record(deferral)
        self.assertIs(receipt['solverStarted'], False)
        self.assertEqual(receipt['memory']['pressureLevel'], 2)
        self.assertEqual(receipt['claim'], ref(self.root / 'claims' / scheduler.filename(first['task'])))
        self.assertFalse(list((self.root / 'failures').glob('*.json')))
        # A deferred claim can never start a solver or produce a result.
        with self.assertRaises(ValueError):
            self.store.start_solver(first)
        with self.assertRaises(ValueError):
            self.store.finish(first, scheduler.selected_fit(example, [], first['task'])[0])
        # No automatic or unlinked retry; only an explicit linked launch re-admits.
        self.memory['pressureLevel'] = 1
        with self.assertRaisesRegex(ValueError, 'claimed'):
            self.claim(pid=201)
        linked = self.launch(deferredPredecessor=deferral)
        second = self.claim(linked, pid=201)
        self.assertEqual((second['generation'], second['deferredPredecessor']), (1, deferral))
        for launch in (linked, self.launch(deferredPredecessor=deferral)):
            with self.assertRaisesRegex(ValueError, 'claimed'):
                self.claim(launch, pid=202)
        self.check(second)
        result, _ = scheduler.selected_fit(example, [], second['task'],
                                           before_fit=lambda: self.store.start_solver(second))
        self.store.finish(second, result)
        with self.assertRaises(FileExistsError):
            self.store.finish(second, result)
        self.assertEqual(sorted(p.name for p in (self.root / 'results').glob('*.json')),
                         [scheduler.filename(first['task'])])
        with self.assertRaisesRegex(ValueError, 'claimed|result'):
            self.claim(self.launch(deferredPredecessor=deferral), pid=203)

    def test_solver_marker_is_durable_before_first_optimizer_call(self):
        self.transfer()
        claim = self.claim()
        self.check(claim)
        marker = self.root / 'started' / scheduler.claim_name(claim)
        EVENTS.clear()
        def before():
            self.store.start_solver(claim)
            EVENTS.append(('marker', marker.exists()))
        scheduler.selected_fit(recorded_example, [], claim['task'], before_fit=before)
        self.assertEqual(EVENTS[:2], [('marker', True), ('optimizer', 0)])
        self.assertIs(json.loads(marker.read_text())['solverStarted'], True)
        with self.assertRaises(FileExistsError):
            self.store.start_solver(claim)

    def test_started_attempt_is_never_deferred_or_readmitted(self):
        self.transfer()
        claim = self.claim()
        self.check(claim)
        self.store.start_solver(claim)
        # Crash after the marker: conservatively a failed attempt, not a deferral.
        self.memory['pressureLevel'] = 2
        with self.assertRaisesRegex(ValueError, 'settled|started'):
            self.check(claim)
        self.assertFalse(list((self.root / 'deferrals').glob('*.json')))
        scheduler.settle(self.store, claim, RuntimeError('killed after solver start'))
        self.assertTrue((self.root / 'failures' / scheduler.claim_name(claim)).exists())
        self.memory['pressureLevel'] = 1
        forged = artifact(self.base / 'forged-deferral.json', {
            'kind': scheduler.NO_FIT_DEFERRAL, 'task': claim['task'], 'solverStarted': False,
            'claim': ref(self.root / 'claims' / scheduler.claim_name(claim))})
        with self.assertRaisesRegex(ValueError, 'deferral'):
            self.claim(self.launch(deferredPredecessor=forged), pid=201)
        self.assertEqual(len(list((self.root / 'claims').glob('*.json'))), 1)

    def test_partial_linked_attempt_blocks_further_readmission(self):
        self.transfer()
        first = self.claim()
        deferral = self.defer(first)
        second = self.claim(self.launch(deferredPredecessor=deferral), pid=201)
        self.check(second)
        self.store.start_solver(second)
        scheduler.settle(self.store, second, RuntimeError('partial fit interrupted'))
        with self.assertRaisesRegex(ValueError, 'claimed'):
            self.claim(self.launch(deferredPredecessor=deferral), pid=202)
        self.assertEqual(len(list((self.root / 'claims').glob('*.json'))), 2)

    def test_preparation_failure_and_other_refusals_are_not_deferrals(self):
        self.transfer()
        claim = self.claim()
        scheduler.settle(self.store, claim, scheduler.Deferred('not the pre-fit check'))
        self.assertTrue((self.root / 'failures' / scheduler.claim_name(claim)).exists())
        self.assertFalse(list((self.root / 'deferrals').glob('*.json')))
        with self.assertRaisesRegex(ValueError, 'settled'):
            self.check(claim)
        missing = {'path': str(self.root / 'deferrals' / scheduler.claim_name(claim)),
                   'sha256': '0' * 64}
        with self.assertRaises((ValueError, FileNotFoundError)):
            self.claim(self.launch(deferredPredecessor=missing), pid=201)
        other = self.claim(self.launch(('M1', 'device', 3)), pid=201)
        def broken():
            raise ValueError('unparseable vm_stat')
        with self.assertRaisesRegex(ValueError, 'vm_stat'):
            self.store.check_before_fit(other, alive=self.live.__contains__, memory=broken)
        self.assertFalse(list((self.root / 'deferrals').glob('*.json')))

    def test_result_requires_this_claims_solver_start_marker(self):
        self.transfer()
        claim = self.claim()
        result, _ = scheduler.selected_fit(example, [], claim['task'])
        result['peakRSSBytes'] = scheduler.GIB
        with self.assertRaisesRegex(ValueError, 'marker'):
            self.store.finish(claim, result)
        self.check(claim)
        with self.assertRaisesRegex(ValueError, 'marker'):
            self.store.finish(claim, result)
        self.assertFalse(list((self.root / 'results').glob('*.json')))
        self.store.start_solver(claim)
        self.store.finish(claim, result)
        # A failed started claim publishes nothing either.
        other = self.claim(self.launch(('M1', 'device', 3)), pid=201)
        self.check(other)
        self.store.start_solver(other)
        self.store.fail(other, RuntimeError('synthetic failure'))
        with self.assertRaisesRegex(ValueError, 'failed'):
            self.store.finish(other, scheduler.selected_fit(example, [], other['task'])[0])
        self.assertEqual([p.name for p in (self.root / 'results').glob('*.json')],
                         [scheduler.filename(claim['task'])])

    def test_result_requires_the_registered_claim_and_its_matching_marker(self):
        self.transfer()
        claim = self.claim()
        self.check(claim)
        result, _ = scheduler.selected_fit(example, [], claim['task'])
        name = scheduler.claim_name(claim)
        # A marker that names other claim bytes is not this claim's solver start.
        forged = {'kind': scheduler.SOLVER_START, 'task': claim['task'], 'pid': claim['pid'],
                  'generation': 0, 'solverStarted': True, 'startedUTC': scheduler.now(),
                  'claim': {'path': str(self.root / 'claims' / name), 'sha256': '0' * 64}}
        scheduler.immutable(self.root / 'started' / name, forged)
        with self.assertRaisesRegex(ValueError, 'marker does not match'):
            self.store.finish(claim, result)
        # A caller's altered copy of the claim is not the registered claim.
        other = self.started(self.claim(self.launch(('M1', 'device', 3)), pid=201))
        altered = dict(other, pid=999)
        with self.assertRaisesRegex(ValueError, 'claim changed'):
            self.store.finish(altered, scheduler.selected_fit(example, [], other['task'])[0])
        self.assertFalse(list((self.root / 'results').glob('*.json')))
        self.store.finish(other, scheduler.selected_fit(example, [], other['task'])[0])

    def test_process_identity_reads_the_real_process_table(self):
        own = REAL_PROCESS_IDENTITY(os.getpid())
        self.assertEqual(own['pid'], os.getpid())
        self.assertIsNotNone(scheduler.datetime.fromisoformat(own['startedUTC']).tzinfo)
        self.assertIn('unittest', own['command'])
        self.assertEqual(REAL_PROCESS_IDENTITY(os.getpid()), own)
        child = subprocess.Popen([sys.executable, '-B', '-c', 'pass'])
        child.wait()
        self.assertIsNone(REAL_PROCESS_IDENTITY(child.pid))

    def test_registered_handoff_retires_its_old_owner_even_if_the_pid_is_reissued(self):
        self.transfer()
        # Partition 0's owner stopped and was handed off; its PID now belongs to a
        # small OS service. It reserves nothing and cannot block partition 0 claims.
        self.live.add(101)
        self.processes.reissue(101, '/System/Library/ExtensionKit/synthetic-os-service')
        decision = self.claim()
        self.assertEqual([p['owner'] for p in decision['processes']], ['old-1', 'old-2'])
        self.assertEqual(decision['excludedProcesses'], [
            {'pid': 101, 'owner': 'old-0', 'reason': 'registered stop handoff'}])
        self.assertEqual(decision['effectiveConcurrency'], 3)
        # Unregistered partitions' live owners still reserve, and still block transfer.
        with self.assertRaisesRegex(ValueError, 'live'):
            self.store.transfer(self.handoff(partition=1, oldPid=102, oldTaskId='old-1'),
                                alive=self.live.__contains__)

    def test_settled_claim_reserves_only_while_its_claimant_process_lives(self):
        self.transfer()
        claim = self.started(self.claim())
        result = scheduler.selected_fit(example, [], claim['task'])[0]
        self.store.finish(claim, dict(result, peakRSSBytes=scheduler.GIB))
        # The finished claimant has not exited yet: it is genuinely live and counts.
        self.live.add(200)
        with self.assertRaises(scheduler.Deferred) as refusal:
            self.claim(self.launch(('M1', 'device', 3)), pid=201)
        self.assertIn('device-M1-start-00.json',
                      [p['owner'] for p in refusal.exception.decision['processes']])
        # The same PID reissued, same command, later start: not the claimant.
        self.processes.reissue(200)
        decision = self.claim(self.launch(('M1', 'device', 3)), pid=201)
        self.assertEqual([p['pid'] for p in decision['processes']], [102, 103])
        self.assertEqual([(p['owner'], p['reason']) for p in decision['excludedProcesses']],
                         [('old-0', 'registered stop handoff'),
                          ('device-M1-start-00.json', 'PID reused: creation identity differs')])

    def test_claim_requires_a_readable_claimant_launched_with_this_receipt(self):
        self.transfer()
        launch, other = self.launch(), self.launch(('M1', 'device', 3))
        cases = [(None, 'identity is unreadable'),
                 ('/usr/libexec/unrelated-service', 'not launched with this receipt'),
                 (driver_command(other), 'not launched with this receipt')]
        for command, message in cases:
            if command is None:
                self.processes.gone.add(200)
            else:
                self.processes.gone.discard(200)
                self.processes.reissue(200, command)
            with self.assertRaisesRegex(ValueError, message):
                self.store.claim(launch, pid=200, alive=self.live.__contains__,
                                 memory=lambda: dict(self.memory))
        self.assertFalse(list((self.root / 'claims').glob('*.json')))
        claim = self.claim(launch)
        self.assertEqual((claim['processIdentity'], claim['processIdentitySource']),
                         (self.processes(200), scheduler.PROCESS_IDENTITY_SOURCE))
        self.assertTrue(scheduler.names_receipt(claim['processIdentity']['command'], launch))

    def test_prefit_rereads_the_claimants_live_identity(self):
        self.transfer()
        claim = self.claim()
        # A later process at the claimant's PID fails the pre-fit check, and that
        # refusal is not a re-admissible no-fit deferral.
        self.processes.reissue(200)
        with self.assertRaisesRegex(ValueError, 'claimant'):
            self.check(claim)
        self.assertFalse(list((self.root / 'deferrals').glob('*.json')))

    def test_solved_fit_finishes_without_reading_the_process_table(self):
        self.transfer()
        claim = self.claim()
        self.check(claim)
        # After the pre-fit check nothing may shell out: an unreadable process table
        # cannot cost a legitimately started or completed fit its marker or result.
        def unavailable(pid):
            raise OSError('ps unavailable after solve')
        with mock.patch.object(scheduler, 'process_identity', unavailable):
            self.store.start_solver(claim)
            marker = json.loads((self.root / 'started' / scheduler.claim_name(claim)).read_text())
            self.assertEqual(marker['processIdentity'], claim['processIdentity'])
            result = scheduler.selected_fit(example, [], claim['task'])[0]
            self.store.finish(claim, result)
        self.assertTrue((self.root / 'results' / scheduler.filename(claim['task'])).exists())

    def test_only_the_claiming_process_and_store_start_or_finish_a_claim(self):
        self.transfer()
        claim = self.claim()
        self.check(claim)
        another_process = scheduler.Store(self.root)
        with as_process(200), self.assertRaisesRegex(ValueError, 'did not make this claim'):
            another_process.start_solver(claim)
        with as_process(201), self.assertRaisesRegex(ValueError, 'did not make this claim'):
            scheduler.Store.start_solver(self.store, claim)
        self.assertFalse(list((self.root / 'started').glob('*.json')))
        self.store.start_solver(claim)
        result = scheduler.selected_fit(example, [], claim['task'])[0]
        with as_process(200), self.assertRaisesRegex(ValueError, 'did not make this claim'):
            another_process.finish(claim, result)
        with as_process(201), self.assertRaisesRegex(ValueError, 'did not make this claim'):
            scheduler.Store.finish(self.store, claim, result)
        self.assertFalse(list((self.root / 'results').glob('*.json')))
        self.store.finish(claim, result)

    def test_a_controller_that_claimed_for_its_child_owns_no_lifecycle(self):
        self.transfer()
        # A controller (this real process, no simulation) claims on behalf of a
        # child fit driver whose identity it read. It made the claim in this store
        # and process, but the claim's PID is not its own: it holds no lifecycle.
        controller = scheduler.Store(self.root)
        child = self.spawned(500)
        claim = controller.claim(child, pid=500, alive=self.live.__contains__,
                                 memory=lambda: dict(self.memory))
        name = scheduler.claim_name(claim)
        with self.assertRaisesRegex(ValueError, 'not this process'):
            controller.check_before_fit(claim, alive=self.live.__contains__,
                                        memory=lambda: dict(self.memory))
        self.assertFalse(list((self.root / 'deferrals').glob('*.json')))
        # Fixture: the admitted pre-fit record the previous source epoch let such a
        # controller write. The child's PID is then reissued; the controller still
        # cannot start the solver, which no longer re-reads the process table.
        scheduler.immutable(self.root / 'admissions' / name, {'admitted': True})
        self.processes.reissue(500)
        with self.assertRaisesRegex(ValueError, 'not this process'):
            controller.start_solver(claim)
        self.assertFalse(list((self.root / 'started').glob('*.json')))
        # Fixture: that epoch's marker, bound to the child's recorded identity.
        claim_path = self.root / 'claims' / name
        scheduler.immutable(self.root / 'started' / name, {
            'kind': scheduler.SOLVER_START, 'task': claim['task'], 'generation': 0,
            'pid': 500, 'processIdentity': claim['processIdentity'], 'solverStarted': True,
            'claim': {'path': str(claim_path), 'sha256': ref(claim_path)['sha256']},
            'startedUTC': scheduler.now()})
        with self.assertRaisesRegex(ValueError, 'not this process'):
            controller.finish(claim, scheduler.selected_fit(example, [], claim['task'])[0])
        self.assertFalse(list((self.root / 'results').glob('*.json')))

    def test_memory_parser_states_exact_metric(self):
        value = scheduler.parse_memory('Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free: 200.\nPages inactive: 300.\nPages speculative: 999.\n', '1')
        self.assertEqual(value['availableBytes'], 500 * 16384)
        self.assertEqual(value['metric'], scheduler.MEMORY_METRIC)


if __name__ == '__main__':
    unittest.main()
