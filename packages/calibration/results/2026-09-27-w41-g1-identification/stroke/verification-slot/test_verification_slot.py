"""Resource-only verification contract; tiny Store, fake proof, no native imports."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import verification_slot as v


def ref(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def artifact(path, value):
    path.write_text(json.dumps(value))
    return ref(path)


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base/'state'
        self.memo = self.base/'memoization'; self.memo.mkdir()
        self.completed = self.base/'completed.json'
        artifact(self.completed, {'family': 'M1', 'cssWidth': False, 'curvature': False,
                                 'starts': [{'startIndex': 0}]})
        self.source = self.base/'source.py'; self.source.write_text('# source\n')
        for name, value in [('MEMO', self.memo), ('COMPLETED', self.completed)]:
            p = patch.object(v, name, value); p.start(); self.addCleanup(p.stop)
        p = patch.object(v, 'required_sources', return_value=[self.source])
        p.start(); self.addCleanup(p.stop)
        self.owners = []
        for partition in range(3):
            out = self.base/f'old-{partition}'; out.mkdir()
            execution = artifact(out/'execution.json', dict(partition=partition,
                indices=list(range(partition, 16, 3)), seed=4100, heldRevision=v.s.REVISION))
            self.owners.append(dict(partition=partition, pid=101+partition,
                taskId=f'old-{partition}', outputRoot=str(out), execution=execution))
        self.roster = artifact(self.base/'roster.json', dict(kind='STROKE_ROSTER',
            schedulerRoot=str(self.root), oldOwners=self.owners))
        self.release = artifact(self.base/'release.json', dict(kind='CAPTURESRELEASE',
            schedulerRoot=str(self.root), maxConcurrency=4))
        self.peak = artifact(self.base/'peak.json', dict(kind='STROKE_PEAK_RSS',
            largestObservedPeakRSSBytes=v.s.GIB, samples=[dict(pid=101,
                peakRSSBytes=v.s.GIB, source='synthetic', sampledUTC=v.s.now())]))
        self.store = v.s.Store(self.root); self.store.initialize(self.roster)
        self.live = {101, 102}
        self.memory = dict(availableBytes=20*v.s.GIB, pressureLevel=1, metric=v.s.MEMORY_METRIC)
        self.stage_calls = []
        self.peak_value = 2*v.s.GIB
        self.count = 0

    def receipt(self, mode='unwrapped', **changes):
        self.count += 1
        value = dict(kind='STROKE_VERIFICATION_ADMIT', schedulerRoot=str(self.root),
            heldRevision=v.s.REVISION, roster=self.roster, captureRelease=self.release,
            peakEvidence=self.peak, reservationBytes=v.s.GIB,
            oldWorkerReservationBytes=v.s.GIB, maxConcurrency=4, mode=mode,
            out=str(self.memo/f'{mode}-{self.count}'), completedArtifact=ref(self.completed),
            sourceSha256={str(self.source): ref(self.source)['sha256']}, predecessor=None)
        value.update(changes)
        return artifact(self.base/f'admit-{self.count}.json', value)

    def body(self, mode, out, admit):
        self.stage_calls.append(admit('before-preparation'))
        out.mkdir()
        self.stage_calls.append(admit('before-fit'))
        self.assertTrue((self.root/'verification'/mode/'solver-verification-start.json').exists())
        pins = {}
        for name in ('trace.jsonl.gz', 'raw-result.json', 'replay.json'):
            (out/name).write_text('synthetic '+name)
            pins[name] = ref(out/name)['sha256']
        proof = dict(schema='w41-memoization-native-one-mode-1', mode=mode, verified=True,
            completedArtifact=str(self.completed), completedSha256=ref(self.completed)['sha256'],
            classification='verification replay, not a new candidate', artifacts=pins)
        artifact(out/'completed-start-proof.json', proof)
        return proof

    def run_slot(self, receipt=None, body=None):
        return v.run(self.store, receipt or self.receipt(), proof_body=body or self.body,
            alive=self.live.__contains__, memory=lambda: dict(self.memory),
            rss=lambda pid: v.s.GIB//2, peak=lambda: self.peak_value, system=lambda: 'Darwin')

    def terminal(self, mode='unwrapped'):
        return json.loads((self.root/'verification'/mode/'terminal.json').read_text())

    def test_counts_old_fits_and_subtracts_own_resident_bytes_before_fit(self):
        self.run_slot()
        before, after = self.stage_calls
        self.assertEqual(before['effectiveConcurrency'], 3)
        self.assertEqual({p['pid'] for p in before['processes']}, self.live)
        self.assertEqual(before['ownRSSBytes'], 0)
        self.assertEqual(before['reservedBytes'], 2*v.s.GIB)
        self.assertEqual(after['ownRSSBytes'], v.s.GIB//2)
        self.assertEqual(after['reservedBytes'], 3*v.s.GIB//2)
        self.assertEqual(self.terminal()['status'], 'verified')
        self.assertEqual(self.terminal()['pid'], os.getpid())
        self.assertIn(2*v.s.GIB, self.store.observed_rss())
        for folder in ('claims', 'results', 'started', 'failures', 'deferrals'):
            self.assertEqual(list((self.root/folder).iterdir()), [])

    def test_resource_owner_never_skips_or_rewrites_a_candidate_claim(self):
        # Even a synthetic candidate with the verification subject's exact task
        # must be counted. A fake own_claim for seed zero would silently skip it.
        claim = dict(task=['M1', 'device', 0], generation=0, pid=104,
                     prospectivePeakBytes=v.s.GIB, reservationBytes=v.s.GIB)
        claim_ref = artifact(self.root/'claims/device-M1-start-00.json', claim)
        self.live.add(104)
        receipt = self.receipt()
        self.run_slot(receipt)
        self.assertEqual(self.stage_calls[1]['effectiveConcurrency'], 4)
        self.assertEqual({p['pid'] for p in self.stage_calls[1]['processes']}, self.live)
        self.assertEqual(ref(Path(claim_ref['path'])), claim_ref)
        self.assertEqual(v.s.claim_name(claim), 'device-M1-start-00.json')
        self.assertNotEqual(v.s.claim_name(v.VerificationOwner('unwrapped')),
                            v.s.claim_name(claim))
        self.assertEqual(list((self.root/'results').iterdir()), [])

    def test_allocation_lock_excludes_second_process_for_entire_proof(self):
        code = ('import fcntl,sys; f=open(sys.argv[1],"r+"); '
                'fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)')
        def probe():
            return subprocess.run([sys.executable, '-c', code, str(self.root/'.lock')],
                                  capture_output=True).returncode
        def body(mode, out, admit):
            self.assertNotEqual(probe(), 0)
            result = self.body(mode, out, admit)
            self.assertNotEqual(probe(), 0)
            return result
        self.run_slot(body=body)
        self.assertEqual(probe(), 0)

    def test_pressure_before_preparation_refuses_and_retains_peak(self):
        self.memory['pressureLevel'] = 2
        with self.assertRaises(v.s.Deferred): self.run_slot()
        self.assertEqual(self.stage_calls, [])
        terminal = self.terminal()
        self.assertFalse(terminal['solverStarted'])
        self.assertEqual(terminal['status'], 'refused-before-preparation-no-fit')
        self.assertNotIn('proof', terminal)
        self.assertIn(self.peak_value, self.store.observed_rss())

    def test_post_preparation_pressure_refuses_without_solver_marker(self):
        def body(mode, out, admit):
            admit('before-preparation')
            self.memory['availableBytes'] = 0
            admit('before-fit')
            self.fail('optimizer must not be reached')
        with self.assertRaises(v.s.Deferred): self.run_slot(body=body)
        self.assertEqual(self.terminal()['status'], 'refused-before-fit-no-fit')
        self.assertFalse((self.root/'verification/unwrapped/solver-verification-start.json').exists())

    def test_exception_after_start_is_failure_not_proof_and_peak_survives(self):
        def body(mode, out, admit):
            admit('before-preparation'); admit('before-fit')
            self.peak_value = 5*v.s.GIB
            raise RuntimeError('synthetic solver failure')
        with self.assertRaisesRegex(RuntimeError, 'solver failure'): self.run_slot(body=body)
        terminal = self.terminal()
        self.assertEqual(terminal['status'], 'failed-after-solver-start')
        self.assertNotIn('proof', terminal)
        self.assertIn(5*v.s.GIB, self.store.observed_rss())
        self.assertEqual(terminal['peakRSSPlatform'], 'Darwin')
        self.assertEqual(terminal['peakRSSUnit'], 'bytes')

    def test_arrays_preparation_only_cannot_claim_verification(self):
        def body(mode, out, admit):
            admit('before-preparation')
            return {'verified': True}
        with self.assertRaises(ValueError): self.run_slot(body=body)
        self.assertEqual(self.terminal()['status'], 'preparation-attempted-no-fit')
        self.assertFalse(self.terminal()['solverStarted'])

    def test_sources_modes_scope_and_receipts_fail_closed_before_body(self):
        for changes in ({'mode': 'both'}, {'sourceSha256': {}}, {'roster': self.release},
                        {'heldRevision': 'wrong'}, {'completedArtifact': self.release},
                        {'out': str(self.base/'elsewhere')}, {'predecessor': self.release}):
            with self.subTest(changes=changes):
                with self.assertRaises((ValueError, KeyError)):
                    self.run_slot(self.receipt(**changes))
        self.assertFalse((self.root/'verification').exists())
        receipt = self.receipt()
        self.source.write_text('# changed\n')
        with self.assertRaises(ValueError): self.run_slot(receipt)
        self.assertEqual(self.stage_calls, [])

    def test_changed_receipt_is_refused(self):
        receipt = self.receipt()
        Path(receipt['path']).write_text('{}')
        with self.assertRaises(ValueError): self.run_slot(receipt)
        self.assertEqual(self.stage_calls, [])

    def test_wrapped_requires_successful_same_root_unwrapped_proof(self):
        with self.assertRaises(ValueError): self.run_slot(self.receipt('wrapped'))
        self.run_slot()
        predecessor = ref(self.root/'verification/unwrapped/terminal.json')
        self.run_slot(self.receipt('wrapped', predecessor=predecessor))
        self.assertEqual(self.terminal('wrapped')['status'], 'verified')

    def test_tampered_unwrapped_artifact_blocks_wrapped(self):
        self.run_slot()
        terminal = self.terminal()
        proof_path = Path(terminal['proof']['path'])
        (proof_path.parent/'raw-result.json').write_text('changed')
        with self.assertRaises(ValueError):
            self.run_slot(self.receipt('wrapped', predecessor=ref(
                self.root/'verification/unwrapped/terminal.json')))
        self.assertFalse((self.root/'verification/wrapped').exists())

    def test_failed_unwrapped_blocks_wrapped_and_no_automatic_retry(self):
        self.memory['pressureLevel'] = 2
        with self.assertRaises(v.s.Deferred): self.run_slot()
        self.memory['pressureLevel'] = 1
        with self.assertRaises(ValueError):
            self.run_slot(self.receipt('wrapped', predecessor=ref(
                self.root/'verification/unwrapped/terminal.json')))
        with self.assertRaises(FileExistsError): self.run_slot()

    def test_changed_source_during_preparation_blocks_solver(self):
        def body(mode, out, admit):
            admit('before-preparation')
            self.source.write_text('# changed after preparation\n')
            admit('before-fit')
            self.fail('optimizer must not be reached')
        with self.assertRaises(ValueError): self.run_slot(body=body)
        self.assertFalse(self.terminal()['solverStarted'])
        self.assertEqual(self.terminal()['status'], 'preparation-attempted-no-fit')

    def test_source_drift_after_fit_cannot_publish_success(self):
        def body(mode, out, admit):
            result = self.body(mode, out, admit)
            self.source.write_text('# changed during fit\n')
            return result
        with self.assertRaises(ValueError): self.run_slot(body=body)
        self.assertEqual(self.terminal()['status'], 'failed-after-solver-start')
        self.assertNotIn('proof', self.terminal())

    def test_replay_without_persisted_success_artifacts_is_failure(self):
        def body(mode, out, admit):
            admit('before-preparation'); admit('before-fit')
            return {'verified': True}
        with self.assertRaises(FileNotFoundError): self.run_slot(body=body)
        self.assertEqual(self.terminal()['status'], 'failed-after-solver-start')
        self.assertNotIn('proof', self.terminal())

    def test_old_worker_rss_remains_a_future_reservation_after_it_exits(self):
        receipt = self.receipt()
        def body(mode, out, admit):
            first = admit('before-preparation')
            self.assertEqual(first['observedPeakBytes'], 4*v.s.GIB)
            self.live.clear()
            second = admit('before-fit')
            self.assertEqual(second['observedPeakBytes'], 4*v.s.GIB)
            self.assertEqual(second['prospectivePeakBytes'], 4*v.s.GIB)
            self.assertEqual(second['reservedBytes'], 4*v.s.GIB-v.s.GIB//2)
            raise RuntimeError('stop synthetic body')
        with self.assertRaisesRegex(RuntimeError, 'stop synthetic'):
            v.run(self.store, receipt, proof_body=body, alive=self.live.__contains__,
                memory=lambda: dict(self.memory), rss=lambda pid:
                    4*v.s.GIB if pid in self.live else v.s.GIB//2,
                peak=lambda: self.peak_value, system=lambda: 'Darwin')
        self.assertIn(4*v.s.GIB, self.store.observed_rss())

    def test_missing_peak_or_capture_release_fails_before_preparation(self):
        for field in ('peakEvidence', 'captureRelease'):
            receipt = self.receipt(**{field: {'path': str(self.base/'missing'), 'sha256': '0'*64}})
            with self.subTest(field=field), self.assertRaises(FileNotFoundError):
                self.run_slot(receipt)
        self.assertEqual(self.stage_calls, [])

    def test_non_darwin_cannot_publish_peak_as_bytes(self):
        with self.assertRaisesRegex(ValueError, 'Darwin'):
            v.run(self.store, self.receipt(), proof_body=self.body, system=lambda: 'Linux')
        self.assertFalse((self.root/'verification').exists())

    def test_duplicate_or_reversed_gate_never_starts_solver(self):
        def body(mode, out, admit):
            admit('before-fit')
        with self.assertRaises(ValueError): self.run_slot(body=body)
        self.assertFalse(self.terminal()['solverStarted'])

    def test_concurrency_cap_counts_old_workers_before_preparation(self):
        with self.assertRaises(v.s.Deferred): self.run_slot(self.receipt(maxConcurrency=2))
        self.assertEqual(self.stage_calls, [])
        self.assertEqual(self.terminal()['status'], 'refused-before-preparation-no-fit')

    def test_missing_memory_observation_fails_closed_and_retains_peak(self):
        del self.memory['metric']
        with self.assertRaises(KeyError): self.run_slot()
        self.assertNotIn('proof', self.terminal())
        self.assertIn(self.peak_value, self.store.observed_rss())


if __name__ == '__main__':
    unittest.main()
