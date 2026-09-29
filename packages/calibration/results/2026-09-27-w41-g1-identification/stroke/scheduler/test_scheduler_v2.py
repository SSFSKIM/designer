"""Synthetic tests of the policy-v2 admission gate and pressure watcher; no fit."""
import concurrent.futures
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

import scheduler
import scheduler_v2
from test_scheduler import artifact, example, fake_processes, ref, run_as_claimants

GIB = scheduler.GIB
# v1's source epoch after the authorized W41 G1 PID-reuse fix; the reviewed epoch
# before it was b2b103bcd1fbb77507d97b1e612fae0d802a17b816c3d80ecb8288b00664712c.
V1_SHA256 = '2c0fba175bf26f38fd436d3a42edaae9bc9c4b8dce428b37ed1a06630e825e33'


def at(seconds):
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()


class PolicyV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / 'state'
        self.live = {102, 103}
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
        self.direction = artifact(self.base / 'direction.json', {'ruling': 'explicit handoff'})
        self.peak = artifact(self.base / 'peak.json', {
            'kind': 'STROKE_PEAK_RSS', 'largestObservedPeakRSSBytes': GIB,
            'samples': [{'pid': 101, 'peakRSSBytes': GIB, 'source': 'synthetic measurement',
                         'sampledUTC': '2026-09-27T12:00:00Z'}]})
        self.store = run_as_claimants(scheduler_v2.StoreV2(self.root))
        self.store.initialize(self.roster)
        self.store.transfer(artifact(self.base / 'handoff.json', {
            'kind': 'STROKE_HANDOFF', 'rosterSha256': self.roster['sha256'], 'partition': 0,
            'oldPid': 101, 'oldTaskId': 'old-0', 'stoppedUTC': '2026-09-27T12:00:00+00:00',
            'boundaryTask': None, 'completed': [], 'aborted': [], 'excluded': [],
            'captureRelease': self.release, 'direction': self.direction}),
            alive=self.live.__contains__)
        self.memory = {'availableBytes': 32 * GIB, 'pressureLevel': 1,
                       'metric': scheduler_v2.MEMORY_METRIC_V2}

    def launch(self, task=('M1', 'device', 0), cap=3, **changes):
        value = {'kind': 'STROKE_LAUNCH', 'rosterSha256': self.roster['sha256'],
                 'receiptVersion': 2, 'task': list(task), 'captureRelease': self.release,
                 'maxConcurrency': cap, 'peakEvidence': self.peak,
                 'reservationBytes': GIB, 'oldWorkerReservationBytes': GIB}
        value.update(changes)
        return artifact(self.base / f'launch-{len(list(self.base.glob("launch-*")))}.json', value)

    def claim(self, launch=None, pid=200, memory=None):
        launch = self.processes.spawn(pid, launch or self.launch())
        return self.store.claim(launch, pid=pid, alive=self.live.__contains__,
                                memory=memory or (lambda: dict(self.memory)))

    def claims(self):
        return list((self.root / 'claims').glob('*.json'))

    def test_purgeable_pages_count_and_floor_is_one_gib_after_reservations(self):
        def parsed(inactive, purgeable):
            return scheduler_v2.parse_memory_v2(
                'Mach Virtual Memory Statistics: (page size of 16384 bytes)\n'
                f'Pages free: 200.\nPages inactive: {inactive}.\nPages speculative: 999.\n'
                f'Pages purgeable: {purgeable}.\n', '1\n')
        # Overlapping purgeable pages are not credited twice: max, never the sum.
        self.assertEqual(parsed(300, 50)['availableBytes'], 500 * 16384)
        self.assertEqual(parsed(300, 400)['availableBytes'], 600 * 16384)
        self.assertEqual(parsed(300, 300)['countedPages'], 500)
        value = parsed(300, 50)
        self.assertEqual((value['metric'], value['counter']),
                         (scheduler_v2.MEMORY_METRIC_V2, 'free + max(inactive, purgeable)'))
        self.assertIn('not a free-memory guarantee', value['metric'])
        # Two live old fits (1 GiB remaining each) + the new 1 GiB fit + 1 GiB floor.
        self.memory['availableBytes'] = 4 * GIB - 1
        with self.assertRaises(scheduler.Deferred) as refused:
            self.claim()
        self.assertEqual(json.loads(str(refused.exception))['requiredAvailableBytes'], 4 * GIB)
        self.assertFalse(self.claims())
        self.memory['availableBytes'] = 4 * GIB
        decision = self.claim()
        self.assertEqual((decision['policyVersion'], decision['reservedBytes']), (2, 3 * GIB))
        self.assertEqual(decision['policyCounter'], scheduler_v2.COUNTER)

    def test_peak_evidence_pins_are_checked_and_tampering_fails_closed(self):
        raw = self.base / 'rss-samples.jsonl'
        raw.write_text('{"pid": 101, "rssKiB": 1048576}\n')
        evidence = artifact(self.base / 'peak-with-evidence.json', {
            'kind': 'STROKE_PEAK_RSS', 'largestObservedPeakRSSBytes': GIB,
            'samples': [{'pid': 101, 'peakRSSBytes': GIB, 'source': 'synthetic measurement',
                         'sampledUTC': '2026-09-27T12:00:00Z'}],
            'evidence': [ref(raw)]})
        launch = self.launch(peakEvidence=evidence)
        raw.write_text('{"pid": 101, "rssKiB": 1}\n')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.claim(launch)
        self.assertFalse(self.claims())
        raw.write_text('{"pid": 101, "rssKiB": 1048576}\n')
        self.assertEqual(self.claim(launch)['peakEvidence'], evidence)

    def test_v1_metric_or_receipt_cannot_enter_the_v2_gate(self):
        for launch, memory in ((self.launch(receiptVersion=None), None),
                               (self.launch(receiptVersion=3), None),
                               (self.launch(), lambda: dict(self.memory, metric=scheduler.MEMORY_METRIC))):
            with self.assertRaises((ValueError, scheduler.Deferred)):
                self.claim(launch, memory=memory)
        self.assertFalse(self.claims())
        # v1 is the reviewed, pinned source epoch; v2 is a separate one.
        self.assertEqual(ref(Path(scheduler.__file__))['sha256'], V1_SHA256)

    def test_cap_is_strictly_three_concurrent_fits(self):
        with self.assertRaisesRegex(ValueError, 'three'):
            self.claim(self.launch(cap=4))
        self.claim()
        self.live.add(200)
        with self.assertRaises(scheduler.Deferred) as refused:
            self.claim(self.launch(('M1', 'device', 3)), pid=201)
        self.assertEqual(json.loads(str(refused.exception))['effectiveConcurrency'], 4)

    def test_resumption_needs_five_normal_readings_thirty_seconds_apart(self):
        def reading(offset, level=1):
            return {'id': f'{offset + 1000:06d}', 'sampledUTC': at(offset), 'pressureLevel': level}
        state = scheduler_v2.pressure_state
        self.assertTrue(state([reading(-10)])['admissionsOpen'])
        for level in (2, 4, None):
            self.assertFalse(state([reading(-300), reading(-200, level)])['admissionsOpen'])
        spaced = [reading(-400, 4)] + [reading(-300 + 30 * i) for i in range(5)]
        self.assertTrue(state(spaced)['admissionsOpen'])
        self.assertFalse(state(spaced[:-1])['admissionsOpen'])
        # Duplicate readings inside one interval (several workers) count once.
        crowded = [reading(-400, 4)] + [reading(-300 + 10 * i) for i in range(12)]
        self.assertEqual(state(crowded)['spacedNormalReadings'], 4)
        self.assertFalse(state(crowded)['admissionsOpen'])
        self.assertFalse(state(spaced + [reading(-10, 2)])['admissionsOpen'])

    def test_admission_reading_resumes_and_abnormal_reading_stops_admissions(self):
        self.store.log_pressure(4, sampled=at(-400), source='synthetic')
        for offset in (-300, -290, -270, -240):
            self.store.log_pressure(1, sampled=at(offset), source='synthetic')
        with self.assertRaises(scheduler.Deferred):
            self.claim(self.launch(('M1', 'device', 6)), pid=202)  # its reading is 4th
        # One more NORMAL reading 30 s after the previous counted one reopens.
        self.store.log_pressure(1, sampled=at(-200), source='synthetic')
        self.assertEqual(self.claim()['task'], ['M1', 'device', 0])
        self.memory['pressureLevel'] = 2
        with self.assertRaises(scheduler.Deferred):
            self.claim(self.launch(('M1', 'device', 3)), pid=201)
        self.memory['pressureLevel'] = 1
        with self.assertRaises(scheduler.Deferred) as refused:
            self.claim(self.launch(('M1', 'device', 3)), pid=201)
        self.assertFalse(json.loads(str(refused.exception))['pressureState']['admissionsOpen'])
        self.assertEqual(len(self.claims()), 1)

    def test_unreadable_memory_fails_closed_and_stops_later_admissions(self):
        def broken():
            raise ValueError('unparseable vm_stat')
        with self.assertRaisesRegex(ValueError, 'vm_stat'):
            self.claim(memory=broken)
        readings = self.store.pressure_readings()
        self.assertEqual([r['pressureLevel'] for r in readings], [None])
        self.assertIn('vm_stat', readings[0]['error'])
        with self.assertRaises(scheduler.Deferred):
            self.claim()
        self.assertFalse(self.claims())

    def test_prefit_stop_is_a_no_fit_deferral_and_running_fits_are_untouched(self):
        running = self.claim()
        self.store.check_before_fit(running, alive=self.live.__contains__,
                                    memory=lambda: dict(self.memory))
        self.store.start_solver(running)
        waiting = self.claim(self.launch(('M1', 'device', 3)), pid=201)
        self.store.log_pressure(4, source='synthetic')
        with self.assertRaises(scheduler.Deferred):
            self.store.check_before_fit(waiting, alive=self.live.__contains__,
                                        memory=lambda: dict(self.memory))
        self.assertTrue((self.root / 'deferrals' / scheduler.claim_name(waiting)).exists())
        # The started fit still publishes; v2 records the policy that admitted it.
        result, _ = scheduler.selected_fit(example, [], running['task'])
        self.store.finish(running, result)
        published = json.loads((self.root / 'results' / scheduler.filename(running['task'])).read_text())
        self.assertEqual((published['policyVersion'], published['policyCounter']),
                         (2, scheduler_v2.COUNTER))
        self.assertIn(str(Path(scheduler_v2.__file__).resolve()), published['policySourceSha256'])

    def test_watch_is_bounded_logs_unreadable_and_never_waits_for_allocation_lock(self):
        with self.assertRaises(ValueError):
            scheduler_v2.watch(self.store, 0)
        with self.assertRaises(ValueError):
            scheduler_v2.watch(self.store, scheduler_v2.MAX_WATCH_READINGS + 1)
        samples = iter([1, 'garbage', None])
        def sample():
            value = next(samples)
            if value is None:
                raise OSError('sysctl failed')
            return value
        sleeps, reports = [], []
        with self.store.locked():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(scheduler_v2.watch, self.store, 3, sample=sample,
                            sleep=sleeps.append, report=reports.append).result(timeout=5)
        self.assertEqual(sleeps, [30, 30])
        levels = [json.loads(r)['reading']['pressureLevel'] for r in reports]
        self.assertEqual(levels, [1, None, None])
        self.assertFalse(json.loads(reports[-1])['state']['admissionsOpen'])


    def snapshot(self, name, rows, terminated=True):
        path = self.base / name
        text = '\n'.join(json.dumps(row) for row in rows) + ('\n' if terminated else '')
        path.write_text(text)
        return ref(path)

    def manual(self, offset, level=1, periodic=True):
        return {'sampledUTC': at(offset), 'pressureLevel': level, 'periodic': periodic,
                'rawSysctl': f'{level}\n', 'blocked': level != 1, 'normalStreak': 0,
                'policy': 'parent-v2; no process is killed on pressure changes'}

    def test_imported_manual_warning_blocks_until_fifth_spaced_normal(self):
        rows = [self.manual(-500), self.manual(-400, 2)] + \
            [self.manual(o) for o in (-200, -195, -170, -140, -130, -110)] + \
            [self.manual(-105, periodic=False)]
        snapshot = self.snapshot('manual.jsonl', rows)
        manifest = self.store.import_pressure(snapshot)
        self.assertEqual(manifest['rows'], len(rows))
        imported = self.store.pressure_readings()
        self.assertEqual(sorted((r['sampledUTC'], r['pressureLevel']) for r in imported),
                         sorted((r['sampledUTC'], r['pressureLevel']) for r in rows))
        self.assertEqual({r['source'] for r in imported}, {'manual-import'})
        state = scheduler_v2.pressure_state(imported)
        self.assertEqual((state['admissionsOpen'], state['spacedNormalReadings']), (False, 4))
        # Re-importing the same bytes adds nothing and cannot accelerate resumption.
        self.store.import_pressure(snapshot)
        self.assertEqual(len(self.store.pressure_readings()), len(rows))
        self.assertEqual(scheduler_v2.pressure_state(self.store.pressure_readings())
                         ['spacedNormalReadings'], 4)
        # The admission's own fresh reading, 110 s after the last counted one, is the 5th.
        self.assertEqual(self.claim()['pressureState']['admissionsOpen'], True)

    def test_imported_warning_with_too_few_spaced_normals_stays_blocked(self):
        rows = [self.manual(-400, 4)] + [self.manual(o) for o in (-100, -80, -60, -40, -10)]
        self.store.import_pressure(self.snapshot('manual.jsonl', rows))
        with self.assertRaises(scheduler.Deferred) as refused:
            self.claim()  # -100, -60, -10 counted; its own reading is within 30 s
        self.assertEqual(json.loads(str(refused.exception))['pressureState']
                         ['spacedNormalReadings'], 3)
        self.assertFalse(self.claims())

    def test_pressure_import_fails_closed_without_partial_records(self):
        good = [self.manual(-100, 2), self.manual(-50)]
        bad = [('partial.jsonl', good, False),
               ('string-level.jsonl', good + [dict(self.manual(-20), pressureLevel='1')], True),
               ('naive-time.jsonl', good + [dict(self.manual(-20), sampledUTC='2026-09-27T12:00:00')], True),
               ('no-periodic.jsonl', [{k: v for k, v in self.manual(-20).items() if k != 'periodic'}], True)]
        for name, rows, terminated in bad:
            with self.assertRaises((ValueError, KeyError, TypeError)):
                self.store.import_pressure(self.snapshot(name, rows, terminated))
        stale = self.snapshot('stale.jsonl', good)
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.store.import_pressure(dict(stale, sha256='0' * 64))
        self.assertFalse((self.root / 'pressure').exists() and self.store.pressure_readings())
        self.store.import_pressure(stale)
        with self.assertRaisesRegex(ValueError, 'different'):
            self.store.import_pressure(self.snapshot('longer.jsonl', good + [self.manual(-5)]))
        record = next((self.root / 'pressure').glob('import-*.json'))
        record.chmod(0o644)
        record.write_text(record.read_text().replace('"manual-import"', '"forged"'))
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.store.import_pressure(stale)


if __name__ == '__main__':
    unittest.main()
