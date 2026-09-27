"""Adaptive composition uses actual StoreV3, fake OS readings and fake proof body."""
from datetime import timedelta
from pathlib import Path
import unittest
from unittest.mock import patch

import test_policy_v2 as previous
import verification_policy_v3 as driver

artifact, ref, v = previous.artifact, previous.ref, previous.v


class AdaptiveDriverTests(unittest.TestCase):
    body = previous.PolicyDriverTests.body
    terminal = previous.PolicyDriverTests.terminal
    at = previous.PolicyDriverTests.at
    reading = previous.PolicyDriverTests.reading
    watch = previous.PolicyDriverTests.watch

    def setUp(self):
        previous.PolicyDriverTests.setUp(self)
        self.live = {self.watcher_pid}
        self.disk_bytes = 25*v.s.GIB
        self.adaptive = self.base/'adaptive-policy.json'
        artifact(self.adaptive, dict(kind='STROKE_ADAPTIVE_MEMORY_DIRECTION',
            counter='free + max(inactive, purgeable)', normal=dict(pressureLevels=[1],
                spacedNormalReadings=5, intervalSeconds=30, floorBytes=v.s.GIB, maxConcurrency=3),
            degraded=dict(pressureLevels=[1, 2], floorBytes=0, maxConcurrency=1,
                          diskFreeMinimumBytes=20*v.s.GIB)))
        self.adaptive_source = self.base/'scheduler_v3.py'
        self.adaptive_source.write_text('# adaptive policy fixture\n')
        for target, name, value in ((driver, 'ADAPTIVE_POLICY', self.adaptive),
                                   (driver.v3, '__file__', str(self.adaptive_source))):
            p = patch.object(target, name, value); p.start(); self.addCleanup(p.stop)
        self.store = driver.PolicyStore(self.root, clock=lambda: self.clock,
                                       disk=lambda: {'freeBytes': self.disk_bytes}, swap=lambda: {'synthetic': True})
        watcher = v.s.record(self.watcher); watcher['startedUTC'] = self.at(-300)
        self.watcher = artifact(Path(self.watcher['path']), watcher)

    def setUpBase(self):
        previous.PolicyDriverTests.setUpBase(self)

    def receipt(self, **changes):
        fields = dict(receiptVersion=3, adaptiveMemoryPolicy=ref(self.adaptive),
            resourceSourceSha256={str(p): ref(p)['sha256'] for p in driver.resource_sources()})
        fields.update(changes)
        return previous.PolicyDriverTests.receipt(self, **fields)

    def normals(self):
        for offset in (-150, -120, -90, -60, -30):
            self.watch(offset)

    def run_slot(self, receipt=None, body=None):
        return driver.run(self.root, receipt or self.receipt(), proof_body=body or self.body,
            clock=lambda: self.clock, disk=lambda: {'freeBytes': self.disk_bytes}, swap=lambda: {'synthetic': True}, alive=self.live.__contains__,
            memory=lambda: dict(self.memory, sampledUTC=self.at(0)), rss=lambda pid: v.s.GIB//2,
            peak=lambda: self.peak_value, system=lambda: 'Darwin')

    def test_warning_uses_real_degraded_gate_at_both_boundaries(self):
        self.memory = self.reading(v.s.GIB, 0, level=2)
        self.run_slot()
        first, second = self.stage_calls
        self.assertEqual(first['policyVersion'], 3)
        self.assertEqual(first['resourceMode'], 'degraded')
        self.assertEqual(first['memory']['pressureLevel'], 2)
        self.assertEqual(first['requiredAvailableBytes'], v.s.GIB)
        self.assertEqual(second['requiredAvailableBytes'], v.s.GIB//2)
        self.assertEqual(first['diskFreeBytes'], self.disk_bytes)
        self.assertEqual(first['adaptiveMemoryPolicy'], ref(self.adaptive))
        self.assertEqual(first['resourceSourceSha256'], v.s.record(self.receipt())['resourceSourceSha256'])
        self.assertEqual(self.terminal()['status'], 'verified')
        self.assertEqual(list((self.root/'claims').iterdir()), [])
        self.assertEqual(list((self.root/'results').iterdir()), [])

    def test_fresh_normal_history_is_degraded_until_five_readings_are_proven(self):
        self.memory = self.reading(20*v.s.GIB, 0, level=1)
        self.run_slot()
        self.assertEqual(self.stage_calls[0]['resourceMode'], 'degraded')
        self.assertEqual(self.stage_calls[0]['memory']['pressureLevel'], 1)
        self.assertFalse(self.stage_calls[0]['normalGate']['fiveSpacedNormal'])

    def test_five_spaced_normals_prefer_normal_policy_and_preserve_floor(self):
        self.normals()
        self.memory = self.reading(2*v.s.GIB, 0)
        self.run_slot()
        self.assertEqual(self.stage_calls[0]['resourceMode'], 'normal')
        self.assertEqual(self.stage_calls[0]['requiredAvailableBytes'], 2*v.s.GIB)

    def test_normal_history_can_fall_back_to_degraded_when_only_floor_fails(self):
        self.normals()
        self.memory = self.reading(v.s.GIB, 0)
        self.run_slot()
        self.assertEqual(self.stage_calls[0]['resourceMode'], 'degraded')
        self.assertEqual(self.stage_calls[0]['memory']['pressureLevel'], 1)
        self.assertEqual(self.stage_calls[0]['requiredAvailableBytes'], v.s.GIB)

    def test_pressure_change_between_gates_is_reversible_not_a_sticky_driver_mode(self):
        self.normals()
        def body(mode, out, admit):
            self.stage_calls.append(admit('before-preparation'))
            self.clock += timedelta(microseconds=1)
            self.memory['pressureLevel'] = 2
            self.stage_calls.append(admit('before-fit'))
            raise RuntimeError('synthetic stop after gates')
        with self.assertRaisesRegex(RuntimeError, 'synthetic stop'): self.run_slot(body=body)
        self.assertEqual([d['resourceMode'] for d in self.stage_calls], ['normal', 'degraded'])
        self.assertEqual(self.stage_calls[-1]['memory']['pressureLevel'], 2)

    def test_degraded_can_return_to_normal_after_five_new_spaced_readings(self):
        self.memory = self.reading(20*v.s.GIB, 0, level=2)
        def body(mode, out, admit):
            self.stage_calls.append(admit('before-preparation'))
            for _ in range(5):
                self.clock += timedelta(seconds=30)
                self.watch(level=1)
            self.memory['pressureLevel'] = 1
            self.stage_calls.append(admit('before-fit'))
            raise RuntimeError('synthetic stop after gates')
        with self.assertRaisesRegex(RuntimeError, 'synthetic stop'): self.run_slot(body=body)
        self.assertEqual([d['resourceMode'] for d in self.stage_calls], ['degraded', 'normal'])

    def test_degraded_refuses_another_live_fit_and_critical_pressure(self):
        launch = v.s.record(self.receipt())
        self.memory = self.reading(20*v.s.GIB, 0, level=2)
        self.live.add(101)
        with self.store.locked(), self.assertRaises(v.s.Deferred):
            v.resource_admission(self.store, launch, 999, self.live.__contains__,
                lambda: dict(self.memory), lambda pid: v.s.GIB//2, prepared=False)
        self.live.remove(101); self.clock += timedelta(microseconds=1)
        self.memory['pressureLevel'] = 4
        with self.assertRaises(v.s.Deferred): self.run_slot()
        self.assertFalse(self.terminal()['solverStarted'])

    def test_newer_critical_watcher_row_survives_composition_without_masking_own_sample(self):
        receipt = self.receipt()
        self.memory = self.reading(v.s.GIB, 0, level=1)
        def memory_with_publication():
            measured = dict(self.memory, sampledUTC=self.at(0))
            self.clock += timedelta(microseconds=1)
            self.watch(level=4)
            return measured
        with self.assertRaises(v.s.Deferred) as refused:
            driver.preflight(self.root, receipt, clock=lambda: self.clock,
                disk=lambda: {'freeBytes': self.disk_bytes}, swap=lambda: {'synthetic': True},
                alive=self.live.__contains__, memory=memory_with_publication,
                rss=lambda pid: v.s.GIB//2)
        self.assertEqual(refused.exception.decision['memory']['pressureLevel'], 1)
        self.assertEqual(refused.exception.decision['freshestPressure']['pressureLevel'], 4)
        self.assertFalse((self.root/'verification').exists())

    def test_degraded_disk_floor_and_unreadable_disk_fail_closed(self):
        self.memory = self.reading(v.s.GIB, 0, level=2)
        self.disk_bytes = 20*v.s.GIB-1
        with self.assertRaises(v.s.Deferred): self.run_slot()
        self.assertFalse(self.terminal()['solverStarted'])
        store = driver.PolicyStore(self.root, clock=lambda: self.clock,
            disk=lambda: (_ for _ in ()).throw(OSError('disk unreadable')),
            swap=lambda: {'synthetic': True})
        launch = v.s.record(self.receipt())
        with store.locked(), self.assertRaises((OSError, ValueError, v.s.Deferred)):
            v.resource_admission(store, launch, 999, self.live.__contains__,
                lambda: dict(self.memory), lambda pid: 0, prepared=False)

    def test_degraded_accepts_exact_disk_boundary_without_masking_value(self):
        self.memory = self.reading(v.s.GIB, 0, level=2)
        self.disk_bytes = 20*v.s.GIB
        self.run_slot()
        self.assertEqual(self.stage_calls[0]['diskFreeBytes'], 20*v.s.GIB)

    def test_adaptive_policy_and_all_operational_dependencies_must_be_pinned(self):
        original = v.s.record(self.receipt())['resourceSourceSha256']
        for path in driver.resource_sources():
            pins = {key: value for key, value in original.items() if key != str(path)}
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.run_slot(self.receipt(resourceSourceSha256=pins))
        with self.assertRaises(ValueError):
            self.run_slot(self.receipt(adaptiveMemoryPolicy=ref(self.policy)))
        receipt = self.receipt(); self.adaptive_source.write_text('# changed adaptive source\n')
        with self.assertRaises(ValueError): self.run_slot(receipt)
        self.assertFalse((self.root/'verification').exists())

    def test_existing_watcher_and_import_are_checked_without_v2_admission(self):
        self.memory = self.reading(v.s.GIB, 0, level=2)
        self.live.remove(self.watcher_pid)
        with self.assertRaises(ValueError): self.run_slot()
        self.assertFalse(self.terminal()['solverStarted'])
        self.assertEqual(self.stage_calls, [])

    def test_refused_preflight_keeps_mode_unused_and_actual_run_has_two_fresh_gates(self):
        receipt = self.receipt()
        self.memory = self.reading(v.s.GIB, 0, level=2)
        self.disk_bytes = 19*v.s.GIB
        with self.assertRaises(v.s.Deferred):
            driver.preflight(self.root, receipt, clock=lambda: self.clock,
                disk=lambda: {'freeBytes': self.disk_bytes}, swap=lambda: {'synthetic': True}, alive=self.live.__contains__,
                memory=lambda: dict(self.memory), rss=lambda pid: v.s.GIB//2)
        self.assertFalse((self.root/'verification').exists())
        self.disk_bytes = 25*v.s.GIB
        self.run_slot(receipt)
        self.assertEqual(len(self.stage_calls), 2)

    def test_post_fit_source_change_does_not_publish_success(self):
        def body(mode, out, admit):
            result = self.body(mode, out, admit)
            self.adaptive_source.write_text('# changed during fit\n')
            return result
        with self.assertRaises(ValueError): self.run_slot(body=body)
        self.assertEqual(self.terminal()['status'], 'failed-after-solver-start')
        self.assertNotIn('proof', self.terminal())

    def test_legacy_view_never_changes_original_receipt_or_actual_admission_version(self):
        receipt = self.receipt()
        original_bytes = Path(receipt['path']).read_bytes()
        actual_gate = driver.v3.StoreV3._admission
        versions = []
        def observe_gate(store, launch, *args, **kwargs):
            versions.append(launch['receiptVersion'])
            return actual_gate(store, launch, *args, **kwargs)
        with patch.object(driver.v3.StoreV3, '_admission', autospec=True, side_effect=observe_gate):
            self.run_slot(receipt)
        self.assertEqual(versions, [3, 3])
        self.assertEqual(Path(receipt['path']).read_bytes(), original_bytes)
        terminal = self.terminal()
        self.assertEqual(v.s.record(terminal['lease'])['receipt'], receipt)

    def test_private_modules_share_identity_and_cli_uses_original_native_entry(self):
        self.assertIs(driver.v3.v2, driver.legacy.v2)
        self.assertIs(driver.s, driver.legacy.v2.v1)
        self.assertEqual(driver.v3.claim_name(v.VerificationOwner('wrapped')), 'verification-wrapped')
        original = v.run
        body = object()
        def adapter_main():
            v.run(v.s.Store(self.root), self.receipt(), proof_body=body)
        with patch.object(v, 'main', side_effect=adapter_main), patch.object(driver, 'run') as composed:
            driver.main()
        self.assertIs(v.run, original)
        self.assertIs(composed.call_args.kwargs['proof_body'], body)


if __name__ == '__main__':
    unittest.main()
