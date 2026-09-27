"""Actual StoreV2 gates composed with fake verification; no native execution."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import test_verification_slot as base
import verification_policy_v2 as driver

artifact, ref, v = base.artifact, base.ref, base.v


class PolicyDriverTests(unittest.TestCase):
    setUpBase = base.VerificationTests.setUp
    body = base.VerificationTests.body
    terminal = base.VerificationTests.terminal

    def setUp(self):
        self.setUpBase()
        self.clock = datetime(2026, 9, 27, 13, 0, tzinfo=timezone.utc)
        self.store = driver.PolicyStore(self.root, clock=lambda: self.clock)
        self.watcher_pid = 900
        self.live.add(self.watcher_pid)
        self.policy = self.base/'policy.json'; artifact(self.policy, {'revision': 2})
        self.counter = self.base/'counter.json'; artifact(self.counter, {'counter': 'max'})
        self.resource_source = self.base/'scheduler_v2.py'; self.resource_source.write_text('# frozen policy\n')
        for target, name, value in ((driver, 'POLICY', self.policy),
                (driver, 'COUNTER_DIRECTION', self.counter),
                (driver.v2, '__file__', str(self.resource_source))):
            p = patch.object(target, name, value); p.start(); self.addCleanup(p.stop)
        self.snapshot = self.base/'completed-pressure.jsonl'
        self.snapshot.write_text(json.dumps(dict(sampledUTC=self.at(-300), pressureLevel=1,
                                                periodic=True, rawSysctl='1\n'))+'\n')
        self.store.import_pressure(ref(self.snapshot))
        self.watcher = artifact(self.base/'watcher.json', dict(kind='STROKE_PRESSURE_WATCH',
            schedulerRoot=str(self.root), pid=self.watcher_pid, startedUTC=self.at(-30),
            intervalSeconds=30, readings=2880, schedulerSourceSha256=ref(self.resource_source)['sha256']))
        self.watch(-5)
        self.memory = self.reading(20*v.s.GIB, 0)

    def at(self, offset):
        return (self.clock+timedelta(seconds=offset)).isoformat()

    def reading(self, inactive, purgeable, level=1):
        reading = driver.v2.parse_memory_v2(
            'Mach Virtual Memory Statistics: (page size of 4096 bytes)\n'
            f'Pages free: 0.\nPages inactive: {inactive//4096}.\n'
            f'Pages purgeable: {purgeable//4096}.\n', str(level))
        reading['sampledUTC'] = self.at(0)
        return reading

    def watch(self, offset=0, level=1):
        with patch.object(driver.v2.os, 'getpid', return_value=self.watcher_pid):
            return self.store.log_pressure(level, sampled=self.at(offset), source='watch')

    def receipt(self, **changes):
        values = dict(receiptVersion=2, maxConcurrency=3,
            resourceSourceSha256={str(p): ref(p)['sha256'] for p in driver.resource_sources()},
            memoryPolicy=ref(self.policy), memoryCounterDirection=ref(self.counter),
            pressureSnapshot=ref(self.snapshot), pressureImport=ref(self.root/'pressure-import.json'),
            pressureWatcher=self.watcher)
        values.update(changes)
        return base.VerificationTests.receipt(self, **values)

    def run_slot(self, receipt=None, body=None):
        return driver.run(self.root, receipt or self.receipt(), proof_body=body or self.body,
            clock=lambda: self.clock, alive=self.live.__contains__,
            memory=lambda: dict(self.memory, sampledUTC=self.at(0)), rss=lambda pid: v.s.GIB//2,
            peak=lambda: self.peak_value, system=lambda: 'Darwin')

    def test_two_actual_v2_gates_apply_one_gib_floor_and_resident_credit(self):
        self.memory = self.reading(3*v.s.GIB, 2*v.s.GIB)
        self.run_slot()
        first, second = self.stage_calls
        self.assertEqual(first['policyVersion'], 2)
        self.assertEqual(first['policyCounter'], 'free + max(inactive, purgeable)')
        self.assertEqual(first['requiredAvailableBytes'], 3*v.s.GIB)
        self.assertEqual(first['memory']['availableBytes'], 3*v.s.GIB)
        self.assertEqual(first['effectiveConcurrency'], 3)
        self.assertEqual(first['ownRSSBytes'], 0)
        self.assertEqual(second['ownRSSBytes'], v.s.GIB//2)
        self.assertEqual(second['requiredAvailableBytes'], 5*v.s.GIB//2)
        self.assertEqual(second['resourceSourceSha256'], v.s.record(self.receipt())['resourceSourceSha256'])
        self.assertEqual(second['pressureWatcher'], self.watcher)
        for name in ('claims', 'results', 'started', 'failures', 'deferrals'):
            self.assertEqual(list((self.root/name).iterdir()), [])
        self.assertIn(self.peak_value, self.store.observed_rss())

    def test_max_counter_refuses_where_double_counted_sum_would_admit(self):
        self.memory = self.reading(2*v.s.GIB, v.s.GIB)
        with self.assertRaises(v.s.Deferred): self.run_slot()
        self.assertEqual(self.terminal()['status'], 'refused-before-preparation-no-fit')
        self.assertEqual(self.stage_calls, [])

    def test_actual_v2_gate_counts_candidate_even_matching_verification_subject(self):
        self.live.remove(102); self.live.add(200)
        candidate = dict(task=['M1', 'device', 0], pid=200, generation=0,
                         prospectivePeakBytes=v.s.GIB, reservationBytes=v.s.GIB)
        original = artifact(self.root/'claims/device-M1-start-00.json', candidate)
        self.run_slot()
        self.assertEqual({p['pid'] for p in self.stage_calls[1]['processes']}, {101, 200})
        self.assertEqual(ref(Path(original['path'])), original)
        self.assertEqual(driver.v2.claim_name(candidate), 'device-M1-start-00.json')
        self.assertEqual(driver.v2.claim_name(v.VerificationOwner('wrapped')), 'verification-wrapped')

    def test_nested_peak_evidence_pin_is_checked_by_actual_v2_gate(self):
        sample = self.base/'peak-sample'; sample.write_text('original')
        peak = v.s.record(self.peak); peak['evidence'] = [ref(sample)]
        peak_ref = artifact(self.base/'new-peak.json', peak)
        sample.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'hash changed'):
            self.run_slot(self.receipt(peakEvidence=peak_ref))
        self.assertFalse(self.terminal()['solverStarted'])
        self.assertIn(self.peak_value, self.store.observed_rss())

    def test_operational_sources_must_be_pinned_and_unchanged(self):
        for sources in ({}, {str(self.resource_source): ref(self.resource_source)['sha256']}):
            with self.subTest(sources=sources), self.assertRaises(ValueError):
                self.run_slot(self.receipt(resourceSourceSha256=sources))
        receipt = self.receipt()
        self.resource_source.write_text('# changed\n')
        with self.assertRaisesRegex(ValueError, 'hash changed'): self.run_slot(receipt)
        self.assertFalse((self.root/'verification').exists())

    def test_operational_source_change_during_preparation_refuses_fit(self):
        def body(mode, out, admit):
            admit('before-preparation')
            self.resource_source.write_text('# changed during prep\n')
            admit('before-fit')
        with self.assertRaises(ValueError): self.run_slot(body=body)
        self.assertFalse(self.terminal()['solverStarted'])

    def test_operational_source_change_after_fit_cannot_publish_success(self):
        def body(mode, out, admit):
            result = self.body(mode, out, admit)
            self.resource_source.write_text('# changed during fit\n')
            return result
        with self.assertRaises(ValueError): self.run_slot(body=body)
        self.assertEqual(self.terminal()['status'], 'failed-after-solver-start')
        self.assertNotIn('proof', self.terminal())

    def test_no_implicit_import_and_missing_imported_rows_fail_closed(self):
        imported = self.root/'pressure-import.json'
        receipt = self.receipt()
        value = imported.read_bytes(); imported.unlink()
        with self.assertRaises(FileNotFoundError): self.run_slot(receipt)
        imported.write_bytes(value)
        next((self.root/'pressure').glob('import-*.json')).unlink()
        with self.assertRaises(FileNotFoundError):
            driver.PolicyStore(self.root, clock=lambda: self.clock).check_resources(
                v.s.record(self.receipt()), self.live.__contains__)

    def test_wrong_policy_direction_and_changed_import_are_refused(self):
        receipt = self.receipt(memoryCounterDirection=ref(self.policy))
        with self.assertRaises(ValueError): self.run_slot(receipt)
        receipt = self.receipt()
        record = next((self.root/'pressure').glob('import-*.json'))
        value = json.loads(record.read_text()); value['pressureLevel'] = 4
        record.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'imported pressure record changed'): self.run_slot(receipt)

    def test_dead_stale_or_future_watcher_refuses_admission(self):
        launch = v.s.record(self.receipt())
        store = driver.PolicyStore(self.root, clock=lambda: self.clock)
        self.live.remove(self.watcher_pid)
        with self.assertRaises(ValueError): store.check_resources(launch, self.live.__contains__)
        self.live.add(self.watcher_pid)
        self.clock += timedelta(seconds=61)
        with self.assertRaises(ValueError): store.check_resources(launch, self.live.__contains__)
        self.watch(1)
        with self.assertRaisesRegex(ValueError, 'future'):
            store.check_resources(launch, self.live.__contains__)

    def test_watcher_publication_during_collection_is_not_mistaken_for_future_history(self):
        launch = v.s.record(self.receipt())
        collect = self.store.pressure_readings
        published = []
        def collect_with_publication():
            # An unlocked watcher publishes after validation begins, but before
            # its history snapshot is complete. No sleeping or real processes.
            self.clock += timedelta(microseconds=1)
            published.append(self.watch())
            return collect()
        with patch.object(self.store, 'pressure_readings', side_effect=collect_with_publication):
            latest = self.store.check_resources(launch, self.live.__contains__)
        self.assertEqual(latest, ref(self.root/'pressure'/(published[0]['id']+'.json')))

    def test_watcher_must_be_bounded_thirty_second_driver_for_same_root_and_source(self):
        launch = v.s.record(self.receipt())
        original = v.s.record(self.watcher)
        for changes in ({'intervalSeconds': 5}, {'readings': 0}, {'readings': 2881},
                        {'schedulerRoot': str(self.base)}, {'schedulerSourceSha256': 'f'*64}):
            launch['pressureWatcher'] = artifact(Path(self.watcher['path']), dict(original, **changes))
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.store.check_resources(launch, self.live.__contains__)

    def test_watcher_expiry_after_preparation_blocks_solver(self):
        def body(mode, out, admit):
            admit('before-preparation'); self.clock += timedelta(seconds=61)
            admit('before-fit')
        with self.assertRaises(ValueError): self.run_slot(body=body)
        self.assertFalse(self.terminal()['solverStarted'])

    def test_warning_history_requires_five_spaced_normal_readings(self):
        self.store.log_pressure(2, sampled=self.at(-1), source='synthetic warning')
        launch = v.s.record(self.receipt())
        with self.store.locked(), self.assertRaises(v.s.Deferred):
            v.resource_admission(self.store, launch, 999, self.live.__contains__,
                lambda: dict(self.memory, sampledUTC=self.at(0)), lambda pid: 0, prepared=False)
        for i in range(1, 5):
            self.clock += timedelta(seconds=30); self.watch()
            with self.store.locked():
                if i < 4:
                    with self.assertRaises(v.s.Deferred):
                        v.resource_admission(self.store, launch, 999, self.live.__contains__,
                            lambda: dict(self.memory, sampledUTC=self.at(0)), lambda pid: 0,
                            prepared=False)
                else:
                    decision = v.resource_admission(self.store, launch, 999, self.live.__contains__,
                        lambda: dict(self.memory, sampledUTC=self.at(0)), lambda pid: 0, prepared=False)
                    self.assertTrue(decision['pressureState']['admissionsOpen'])

    def test_unreadable_memory_stops_pressure_state_and_keeps_peak(self):
        with self.assertRaisesRegex(OSError, 'unreadable'):
            driver.run(self.root, self.receipt(), proof_body=self.body, clock=lambda: self.clock,
                alive=self.live.__contains__, memory=lambda: (_ for _ in ()).throw(OSError('unreadable')),
                rss=lambda pid: v.s.GIB//2, peak=lambda: self.peak_value, system=lambda: 'Darwin')
        self.assertFalse(driver.v2.pressure_state(self.store.pressure_readings())['admissionsOpen'])
        self.assertIn(self.peak_value, self.store.observed_rss())

    def test_v1_metric_and_concurrency_above_three_cannot_enter(self):
        launch = v.s.record(self.receipt(maxConcurrency=4))
        with self.store.locked(), self.assertRaisesRegex(ValueError, 'three'):
            v.resource_admission(self.store, launch, 999, self.live.__contains__,
                lambda: dict(self.memory), lambda pid: 0, prepared=False)
        self.memory['metric'] = v.s.MEMORY_METRIC
        with self.assertRaises(v.s.Deferred): self.run_slot()

    def test_refused_preflight_does_not_consume_mode_and_run_still_checks_both_gates(self):
        receipt = self.receipt()
        self.memory = self.reading(2*v.s.GIB, v.s.GIB)
        with self.assertRaises(v.s.Deferred):
            driver.preflight(self.root, receipt, clock=lambda: self.clock,
                alive=self.live.__contains__, memory=lambda: dict(self.memory),
                rss=lambda pid: v.s.GIB//2)
        self.assertFalse((self.root/'verification').exists())
        self.assertEqual(list((self.root/'claims').iterdir()), [])
        self.memory = self.reading(3*v.s.GIB, 2*v.s.GIB)
        self.run_slot(receipt)
        self.assertEqual(len(self.stage_calls), 2)

    def test_successful_preflight_is_not_a_reservation_or_a_substitute_gate(self):
        receipt = self.receipt()
        decision = driver.preflight(self.root, receipt, clock=lambda: self.clock,
            alive=self.live.__contains__, memory=lambda: dict(self.memory),
            rss=lambda pid: v.s.GIB//2)
        self.assertTrue(decision['admitted'])
        self.assertTrue(decision['preflight'])
        self.assertFalse(decision['reservationHeld'])
        self.assertFalse((self.root/'verification').exists())
        self.memory['pressureLevel'] = 2
        with self.assertRaises(v.s.Deferred): self.run_slot(receipt)
        self.assertEqual(self.stage_calls, [])

    def test_cli_delegates_native_body_to_unchanged_adapter_entry(self):
        original = v.run
        called = []
        def adapter_main():
            body = object()
            v.run(v.s.Store(self.root), self.receipt(), proof_body=body)
            called.append(body)
        with patch.object(v, 'main', side_effect=adapter_main), patch.object(driver, 'run') as composed:
            driver.main()
        self.assertIs(v.run, original)
        self.assertIs(composed.call_args.kwargs['proof_body'], called[0])


if __name__ == '__main__':
    unittest.main()
