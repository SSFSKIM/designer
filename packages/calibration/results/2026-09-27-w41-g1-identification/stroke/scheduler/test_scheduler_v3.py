"""Synthetic tests of the adaptive normal/degraded admission gate; no fit, no native read."""
import json
from pathlib import Path
import tempfile
import unittest

import scheduler
import scheduler_v2
import scheduler_v3
from test_scheduler import artifact, example, fake_processes, ref, run_as_claimants
from test_scheduler_v2 import at

GIB = scheduler.GIB
DIRECTION = {
    'kind': 'STROKE_ADAPTIVE_MEMORY_DIRECTION', 'counter': 'free + max(inactive, purgeable)',
    'normal': {'pressureLevels': [1], 'spacedNormalReadings': 5, 'intervalSeconds': 30,
               'floorBytes': 1073741824, 'maxConcurrency': 3},
    'degraded': {'pressureLevels': [1, 2], 'floorBytes': 0, 'maxConcurrency': 1,
                 'diskFreeMinimumBytes': 21474836480}}


class AdaptivePolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / 'state'
        self.live = set()  # no old static fit is live
        self.processes = fake_processes(self)
        owners = []
        for p in range(3):
            out = self.base / f'old-{p}'
            out.mkdir()
            execution = artifact(out / 'execution.json', {
                'partition': p, 'indices': list(range(p, 16, 3)), 'seed': 4100,
                'heldRevision': scheduler.REVISION})
            owners.append({'partition': p, 'pid': 101 + p, 'taskId': f'old-{p}',
                           'outputRoot': str(out), 'execution': execution})
        self.roster = artifact(self.base / 'roster.json', {
            'kind': 'STROKE_ROSTER', 'schedulerRoot': str(self.root), 'oldOwners': owners})
        self.release = artifact(self.base / 'release.json', {
            'kind': 'CAPTURESRELEASE', 'schedulerRoot': str(self.root), 'maxConcurrency': 6})
        direction = artifact(self.base / 'direction.json', {'ruling': 'explicit handoff'})
        self.peak = artifact(self.base / 'peak.json', {
            'kind': 'STROKE_PEAK_RSS', 'largestObservedPeakRSSBytes': GIB,
            'samples': [{'pid': 101, 'peakRSSBytes': GIB, 'source': 'synthetic measurement',
                         'sampledUTC': '2026-09-27T12:00:00Z'}]})
        self.policy = artifact(self.base / 'adaptive-direction.json', DIRECTION)
        self.disk = {'freeBytes': 100 * GIB, 'volumes': {'/': 100 * GIB},
                     'sampledUTC': at(0), 'source': 'synthetic'}
        self.store = run_as_claimants(scheduler_v3.StoreV3(
            self.root, disk=lambda: dict(self.disk), swap=lambda: {'raw': 'synthetic swap'}))
        self.store.initialize(self.roster)
        for p in range(3):
            self.store.transfer(artifact(self.base / f'handoff-{p}.json', {
                'kind': 'STROKE_HANDOFF', 'rosterSha256': self.roster['sha256'], 'partition': p,
                'oldPid': 101 + p, 'oldTaskId': f'old-{p}',
                'stoppedUTC': '2026-09-27T12:00:00+00:00', 'boundaryTask': None,
                'completed': [], 'aborted': [], 'excluded': [],
                'captureRelease': self.release, 'direction': direction}),
                alive=self.live.__contains__)
        self.memory = {'availableBytes': 32 * GIB, 'pressureLevel': 1,
                       'metric': scheduler_v2.MEMORY_METRIC_V2}

    def launch(self, task=('M1', 'device', 0), **changes):
        value = {'kind': 'STROKE_LAUNCH', 'rosterSha256': self.roster['sha256'],
                 'receiptVersion': 3, 'task': list(task), 'captureRelease': self.release,
                 'maxConcurrency': 3, 'peakEvidence': self.peak,
                 'reservationBytes': GIB, 'oldWorkerReservationBytes': GIB,
                 'adaptiveMemoryPolicy': self.policy}
        value.update(changes)
        return artifact(self.base / f'launch-{len(list(self.base.glob("launch-*")))}.json', value)

    def claim(self, task=('M1', 'device', 0), pid=200, launch=None, memory=None, rss=None):
        launch = self.processes.spawn(pid, launch or self.launch(task))
        return self.store.claim(launch, pid=pid, alive=self.live.__contains__,
                                memory=memory or (lambda: dict(self.memory)), rss=rss)

    def refused(self, *args, **kwargs):
        with self.assertRaises(scheduler.Deferred) as refusal:
            self.claim(*args, **kwargs)
        return refusal.exception.decision

    def claims(self):
        return list((self.root / 'claims').glob('*.json'))

    def normal_history(self, count=4, start=-400):
        # Synthetic fixture history (as the watcher would have logged): spaced NORMALs,
        # so this admission's own reading can be the fifth.
        for i in range(count):
            self.store.log_pressure(1, sampled=at(start + 30 * i), source='synthetic')

    def stop(self, level=2):
        self.store.log_pressure(level, sampled=at(-600), source='synthetic')

    def test_normal_gate_is_v2_and_allows_three_fits(self):
        self.normal_history()
        decision = self.claim()
        self.assertEqual((decision['resourceMode'], decision['policyVersion']), ('normal', 3))
        self.assertEqual(decision['requiredAvailableBytes'], GIB + GIB)
        for pid, index in ((201, 3), (202, 6)):
            self.live.add(pid - 1)
            self.assertEqual(self.claim(('M1', 'device', index), pid=pid)['resourceMode'], 'normal')
        self.live.add(202)
        self.assertEqual(self.refused(('M1', 'device', 9), pid=203)['effectiveConcurrency'], 4)

    def test_floor_miss_falls_to_degraded_without_floor_and_one_fit_only(self):
        self.memory['availableBytes'] = GIB + GIB - 1  # normal floor misses by one byte
        decision = self.claim()
        self.assertEqual((decision['resourceMode'], decision['requiredAvailableBytes']), ('degraded', GIB))
        self.assertFalse(decision['normalGate']['floorClears'])
        self.assertIn('swap', decision['swapExpectation'])
        self.assertEqual(decision['headroomAfterReservationBytes'], GIB - 1)
        self.live.add(200)
        refusal = self.refused(('M1', 'device', 3), pid=201)
        self.assertEqual((refusal['resourceMode'], refusal['modeConcurrencyLimit']), ('degraded', 1))
        self.assertEqual(len(self.claims()), 1)

    def test_degraded_pressure_disk_and_headroom_limits(self):
        self.memory['pressureLevel'] = 2
        self.assertEqual(self.claim()['resourceMode'], 'degraded')  # WARNING admits one fit
        cases = [({'pressureLevel': 4}, None), ({'availableBytes': GIB - 1}, None),
                 ({}, 20 * GIB - 1)]
        for index, (memory, disk) in zip((3, 6, 9), cases):
            self.memory.update({'pressureLevel': 2, 'availableBytes': 32 * GIB, **memory})
            self.disk['freeBytes'] = disk if disk is not None else 100 * GIB
            self.assertEqual(self.refused(('M1', 'device', index), pid=201)['resourceMode'], 'degraded')
        self.memory['pressureLevel'] = 2
        self.disk['freeBytes'] = 20 * GIB
        self.assertEqual(self.claim(('M1', 'device', 12), pid=202)['diskFreeBytes'], 20 * GIB)

    def test_unreadable_values_fail_closed(self):
        def broken():
            raise ValueError('unparseable vm_stat')
        with self.assertRaisesRegex(ValueError, 'vm_stat'):
            self.claim(memory=broken)
        self.assertEqual([r['pressureLevel'] for r in self.store.pressure_readings()], [None])
        self.memory['availableBytes'] = GIB  # degraded territory
        self.store.read_disk = lambda: (_ for _ in ()).throw(OSError('statvfs failed'))
        with self.assertRaisesRegex(ValueError, 'readable disk'):
            self.claim(('M1', 'device', 3), pid=201)
        self.assertFalse(self.claims())

    def test_disk_is_evidence_only_in_normal_mode(self):
        self.normal_history()
        self.store.read_disk = lambda: (_ for _ in ()).throw(OSError('statvfs failed'))
        decision = self.claim()
        self.assertEqual(decision['resourceMode'], 'normal')
        self.assertIn('statvfs', decision['disk']['error'])
        self.assertIsNone(decision['diskFreeBytes'])
        self.assertEqual(decision['swap'], {'raw': 'synthetic swap'})

    def test_mode_is_reevaluated_both_ways_with_spaced_normal_readings(self):
        self.stop(2)
        for offset in (-500, -470, -440, -410):
            self.store.log_pressure(1, sampled=at(offset), source='synthetic')
        first = self.claim()  # its own reading is the 5th spaced NORMAL: normal again
        self.assertEqual(first['resourceMode'], 'normal')
        self.store.log_pressure(2, sampled=at(-1), source='synthetic')
        self.live.add(200)
        refusal = self.refused(('M1', 'device', 3), pid=201)  # WARNING: back to degraded
        self.assertEqual((refusal['resourceMode'], refusal['normalGate']['fiveSpacedNormal']),
                         ('degraded', False))
        self.live.discard(200)
        self.assertEqual(self.claim(('M1', 'device', 3), pid=201)['resourceMode'], 'degraded')
        crowded = scheduler_v2.pressure_state(self.store.pressure_readings())
        self.assertFalse(crowded['admissionsOpen'])

    def test_newer_logged_reading_overrides_this_admissions_older_sample(self):
        self.memory.update(availableBytes=GIB, pressureLevel=2, sampledUTC=at(-5))
        for index, (newer, blocked) in enumerate(((4, True), (None, True), (2, False))):
            def memory(newer=newer, index=index):
                # A watcher row lands after this admission sampled (-5 s) but before it
                # reads the history: it is newer and must win.
                self.store.log_pressure(newer, sampled=at(-1 + index * 0.01), source='watch')
                return dict(self.memory)
            task = ('M1', 'device', 3 * index)
            if blocked:
                refusal = self.refused(task, pid=201 + index, memory=memory)
                self.assertEqual(refusal['freshestPressure']['pressureLevel'], newer)
                self.assertEqual(refusal['memory']['pressureLevel'], 2)  # real sample kept
            else:
                self.assertEqual(self.claim(task, pid=201 + index, memory=memory)
                                 ['resourceMode'], 'degraded')
        self.assertEqual(len(self.claims()), 1)

    def test_fresh_history_needs_five_proven_spaced_normals(self):
        # No abnormal history at all: v2's pressure_state reads open, but one NORMAL
        # reading proves nothing. One, then four, spaced NORMALs stay degraded.
        first = self.claim()
        self.assertEqual((first['resourceMode'], first['spacedNormalRun']), ('degraded', 1))
        self.assertTrue(first['pressureState']['admissionsOpen'])  # v2 history view kept
        self.normal_history(count=3, start=-200)  # -200, -170, -140, then own at ~0: four
        self.live.add(200)
        self.assertEqual(self.refused(('M1', 'device', 3), pid=201)['spacedNormalRun'], 4)
        # Rapid duplicate readings (one per worker) inside 30 s cannot accelerate.
        for offset in (-139, -120, -115, -112, -111):
            self.store.log_pressure(1, sampled=at(offset), source='synthetic')
        self.assertEqual(self.refused(('M1', 'device', 3), pid=201)['spacedNormalRun'], 4)
        # A fifth reading >= 30 s after the last counted one reaches the normal gate.
        self.store.log_pressure(1, sampled=at(-100), source='synthetic')
        decision = self.claim(('M1', 'device', 3), pid=201)
        self.assertEqual((decision['resourceMode'], decision['spacedNormalRun']), ('normal', 5))

    def test_spaced_normal_run_resets_on_any_non_normal(self):
        def row(offset, level=1):
            return {'id': f'{offset + 5000:06d}', 'sampledUTC': at(offset), 'pressureLevel': level}
        run = scheduler_v3.spaced_normal_run
        self.assertEqual(run([]), 0)
        self.assertEqual(run([row(-300 + 30 * i) for i in range(5)]), 5)
        self.assertEqual(run([row(-300 + 5 * i) for i in range(12)]), 2)
        for level in (2, 4, None):
            self.assertEqual(run([row(-300 + 30 * i) for i in range(5)] + [row(-10, level)]), 0)
            self.assertEqual(run([row(-300, level)] + [row(-200 + 30 * i) for i in range(4)]), 4)

    def test_receipt_selector_and_direction_numbers_are_required(self):
        wrong = artifact(self.base / 'wrong-direction.json',
                         dict(DIRECTION, degraded=dict(DIRECTION['degraded'], floorBytes=1)))
        for launch in (self.launch(adaptiveMemoryPolicy=None), self.launch(receiptVersion=2),
                       self.launch(adaptiveMemoryPolicy=wrong)):
            with self.assertRaises((ValueError, TypeError)):
                self.claim(launch=launch)
        # The v2 gate refuses a v3 receipt rather than admitting it under v2 numbers.
        with self.assertRaisesRegex(ValueError, 'receiptVersion 2'):
            scheduler_v2.StoreV2(self.root).claim(self.processes.spawn(200, self.launch()), pid=200,
                alive=self.live.__contains__, memory=lambda: dict(self.memory))
        Path(self.policy['path']).write_text(json.dumps(DIRECTION) + ' ')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.claim()
        self.assertFalse(self.claims())

    def test_refusal_rss_highwater_is_retained_in_degraded_mode(self):
        self.normal_history(start=-900)  # the later normal admission's history
        self.memory['availableBytes'] = GIB
        self.live.add(300)
        running = self.claim(pid=300, rss=lambda pid: 4 * GIB)
        self.assertEqual(running['resourceMode'], 'degraded')
        # A degraded refusal samples the running fit at 4 GiB; that reading is kept.
        self.memory['availableBytes'] = 4 * GIB + GIB // 2
        refusal = self.refused(('M1', 'device', 3), pid=301, rss=lambda pid: 4 * GIB)
        self.assertEqual((refusal['resourceMode'], refusal['observedPeakBytes']), ('degraded', 4 * GIB))
        self.live.discard(300)
        self.memory['availableBytes'] = 5 * GIB
        later = self.claim(('M1', 'device', 3), pid=301, rss=lambda pid: GIB)
        self.assertEqual((later['prospectivePeakBytes'], later['resourceMode']), (4 * GIB, 'normal'))

    def test_prefit_refusal_is_no_fit_and_results_name_the_adaptive_policy(self):
        claim = self.claim()
        self.memory['pressureLevel'] = 4
        with self.assertRaises(scheduler.Deferred):
            self.store.check_before_fit(claim, alive=self.live.__contains__,
                                        memory=lambda: dict(self.memory))
        self.assertTrue((self.root / 'deferrals' / scheduler.claim_name(claim)).exists())
        self.memory['pressureLevel'] = 2
        self.memory['availableBytes'] = GIB
        linked = self.launch(deferredPredecessor=ref(
            self.root / 'deferrals' / scheduler.claim_name(claim)))
        second = self.claim(launch=linked, pid=201)
        self.store.check_before_fit(second, alive=self.live.__contains__,
                                    memory=lambda: dict(self.memory))
        self.store.start_solver(second)
        result, _ = scheduler.selected_fit(example, [], second['task'])
        self.store.finish(second, result)
        published = json.loads((self.root / 'results' / scheduler.filename(second['task'])).read_text())
        self.assertEqual((published['policyVersion'], published['admissionMode']), (3, 'degraded'))
        self.assertEqual(set(published['policySourceSha256']),
                         {str(Path(m.__file__).resolve()) for m in (scheduler_v2, scheduler_v3)})

    def test_reissued_pid_of_a_handed_off_old_owner_reserves_nothing(self):
        # W41 G1 regression: partition 1's old owner stopped and was handed off; macOS
        # reissued its PID to a small OS service, and a bare liveness probe reserved a
        # full fit peak for it, so the one-fit degraded gate refused every start.
        self.live.add(102)
        self.processes.reissue(102, '/System/Library/ExtensionKit/Extensions/'
                               'AppleIntelligenceReportingSELFIngestor.appex/Contents/MacOS/'
                               'AppleIntelligenceReportingSELFIngestor')
        self.memory['availableBytes'] = GIB  # room for exactly one fit
        decision = self.claim(('M1', 'device', 1))  # partition 1's own task claims too
        self.assertEqual((decision['resourceMode'], decision['effectiveConcurrency'],
                          decision['reservedBytes'], decision['processes']),
                         ('degraded', 1, GIB, []))
        self.assertIn({'pid': 102, 'owner': 'old-1', 'reason': 'registered stop handoff'},
                      decision['excludedProcesses'])

    def test_claim_pid_reissued_with_the_same_command_reserves_nothing(self):
        self.live.add(300)
        running = self.claim(pid=300)
        # The genuine claimant, live and unchanged, holds the one degraded slot.
        refusal = self.refused(('M1', 'device', 3), pid=301)
        self.assertEqual([(p['pid'], p['processIdentity']) for p in refusal['processes']],
                         [(300, running['processIdentity'])])
        self.assertEqual(refusal['effectiveConcurrency'], 2)
        # Same PID and same command, a later start: another process, no reservation.
        self.processes.reissue(300)
        decision = self.claim(('M1', 'device', 3), pid=301)
        self.assertEqual((decision['effectiveConcurrency'], decision['processes']), (1, []))
        self.assertIn({'pid': 300, 'owner': 'device-M1-start-00.json',
                       'reason': 'PID reused: creation identity differs',
                       'processIdentity': self.processes(300)}, decision['excludedProcesses'])

    def test_claims_recorded_before_identities_use_start_time_and_receipt(self):
        # The live root's claims predate identities. Their claimant started no later
        # than the claim and ran the launch receipt on its command line.
        launch = self.launch()
        legacy = {'task': ['M1', 'device', 0], 'generation': 0, 'pid': 400,
                  'claimedUTC': '2026-09-27T14:55:58+00:00', 'launch': launch,
                  'prospectivePeakBytes': GIB, 'reservationBytes': GIB}
        artifact(self.root / 'claims' / 'device-M1-start-00.json', legacy)
        driver = (f"/tmp/python -B memo_runner_v3.py --root {self.root} "
                  f"--receipt {launch['path']} --sha256 {launch['sha256']}")
        self.live.add(400)
        cases = [('2026-09-27T17:58:06+00:00', driver,
                  'PID reused: process started after the claim'),
                 ('2026-09-27T14:55:00+00:00', '/usr/libexec/unrelated',
                  "PID reused: command does not run the claim's launch receipt"),
                 ('2026-09-27T14:55:00+00:00', driver, None)]
        for index, (started, command, reason) in enumerate(cases):
            self.processes.reissue(400, command, started)
            task = ('M1', 'device', 3 + 3 * index)
            if reason is None:  # the genuine claimant still reserves its slot
                refusal = self.refused(task, pid=401)
                self.assertEqual([p['pid'] for p in refusal['processes']], [400])
            else:
                decision = self.claim(task, pid=401 + index)
                self.assertEqual(decision['processes'], [])
                self.assertIn(reason, [p['reason'] for p in decision['excludedProcesses']])


if __name__ == '__main__':
    unittest.main()
