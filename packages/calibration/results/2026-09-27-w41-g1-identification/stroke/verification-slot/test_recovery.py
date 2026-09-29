"""Comparator-only recovery admission; saved synthetic artifacts, never a fit."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import test_verification_slot as base

artifact, ref, v = base.artifact, base.ref, base.v


class RecoveryTests(unittest.TestCase):
    setUp = base.VerificationTests.setUp
    receipt = base.VerificationTests.receipt
    run_slot = base.VerificationTests.run_slot
    terminal = base.VerificationTests.terminal
    body = base.VerificationTests.body

    def prepare_recovery(self):
        self.driver = self.memo/'proof.py'; self.driver.write_text('# old comparator\n')
        self.adapter = self.base/'validator.py'; self.adapter.write_text('# old validator\n')
        p = patch.object(v, 'ADAPTER', self.adapter, create=True)
        p.start(); self.addCleanup(p.stop)
        old_sources = {str(p): ref(p)['sha256'] for p in
                       (self.source, self.driver, self.adapter)}
        self.old_receipt = self.receipt(sourceSha256=old_sources)
        self.saved = Path(v.s.record(self.old_receipt)['out'])
        execution_sources = {k: value for k, value in old_sources.items() if k != str(self.adapter)}
        self.trace = dict(sha256='a'*64, events=2, counts={'callback': 2})
        self.bits = 'b'*64

        def failed(mode, out, admit):
            admit('before-preparation'); out.mkdir(); admit('before-fit')
            (out/'trace.jsonl.gz').write_bytes(b'synthetic saved trace')
            artifact(out/'raw-result.json', {'synthetic': 1.0})
            artifact(out/'replay.json', dict(mode='unwrapped', sourceSha256=execution_sources,
                trace=self.trace, rawResultBitsSha256=self.bits, environment={'synthetic': True}))
            raise AssertionError('completed native raw result differs at exact typed/bit witness')
        with self.assertRaises(AssertionError): self.run_slot(self.old_receipt, body=failed)
        self.failure = ref(self.root/'verification/unwrapped/terminal.json')
        self.retained = [ref(p) for p in self.saved.iterdir()]
        self.retained += [self.old_receipt, self.failure, self.terminal()['lease']]
        self.driver.write_text('# new comparator\n')
        self.adapter.write_text('# new validator\n')
        self.new_sources = {str(p): ref(p)['sha256'] for p in
                            (self.source, self.driver, self.adapter)}
        self.transitions = {key: dict(oldSha256=old_sources[key], newSha256=value)
                            for key, value in self.new_sources.items() if value != old_sources[key]}
        diff = self.base/'driver.diff'; diff.write_text('synthetic comparator-only diff\n')
        self.amendment = artifact(self.base/'driver-amendment.json', dict(
            schema='w41-proof-driver-comparison-amendment-1', sourcePath=str(self.driver),
            oldDriverCommit='synthetic-held-commit', oldSourceSha256=old_sources[str(self.driver)],
            newSourceSha256=self.new_sources[str(self.driver)], diff=ref(diff),
            unchangedExecutionBlocks={'replay_once': 'c'*64, 'native_onceThroughSolve': 'd'*64}))
        folder = self.memo/'recovered'; folder.mkdir()
        self.proof = artifact(folder/'completed-start-proof.json', dict(
            schema='w41-memoization-native-one-mode-1', mode='unwrapped', verified=True,
            completedArtifact=str(self.completed), completedSha256=ref(self.completed)['sha256'],
            classification='verification replay, not a new candidate',
            artifactDirectory=str(self.saved), artifacts={name: ref(self.saved/name)['sha256']
                                                        for name in v.ARTIFACTS},
            sourceSha256=execution_sources, rawResultBitsSha256=self.bits, trace=self.trace,
            environment={'synthetic': True}, jsonBoundaryResultBitsSha256='e'*64,
            comparisonRerun=dict(action='solve reused, comparison rerun', optimizerRuns=0,
                nativeArchiveReads=0, priorFailure=self.failure, driverCompatibility=self.amendment,
                comparatorSourceSha256=self.new_sources[str(self.driver)],
                originalInMemoryResultBitsSha256=self.bits, jsonBoundaryResultBitsSha256='e'*64)))
        return self.refresh_direction()

    def refresh_direction(self, **changes):
        direction = dict(kind='STROKE_VERIFICATION_COMPARISON_RECOVERY',
            schedulerRoot=str(self.root), failedTerminal=self.failure, recoveredProof=self.proof,
            sourceTransitions=self.transitions)
        direction.update(changes)
        direction_ref = artifact(self.base/'recovery-direction.json', direction)
        self.recovery = dict(direction=direction_ref, proof=self.proof)
        return self.receipt('wrapped', predecessor=self.failure,
                            sourceSha256=self.new_sources, comparisonRecovery=self.recovery)

    def alter_proof(self, change):
        value = v.s.record(self.proof); change(value)
        self.proof = artifact(Path(self.proof['path']), value)
        return self.refresh_direction()

    def test_recovered_comparison_admits_wrapped_without_relabelling_old_failure(self):
        receipt = self.prepare_recovery()
        self.run_slot(receipt)
        self.assertEqual(self.terminal()['status'], 'failed-after-solver-start')
        self.assertEqual(self.terminal('wrapped')['status'], 'verified')
        for pinned in self.retained:
            self.assertEqual(ref(Path(pinned['path'])), pinned)
        self.assertEqual(list((self.root/'claims').iterdir()), [])
        self.assertEqual(list((self.root/'results').iterdir()), [])

    def test_recovery_requires_explicit_parent_direction(self):
        self.prepare_recovery()
        receipt = self.receipt('wrapped', predecessor=self.failure, sourceSha256=self.new_sources,
                               comparisonRecovery={'proof': self.proof})
        with self.assertRaises((ValueError, KeyError)): self.run_slot(receipt)
        self.assertFalse((self.root/'verification/wrapped').exists())

    def test_recovery_direction_must_pin_the_same_failure_and_proof(self):
        self.prepare_recovery()
        for field in ('failedTerminal', 'recoveredProof'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'parent recovery direction'):
                self.run_slot(self.refresh_direction(**{field: self.old_receipt}))

    def test_recovery_rejects_changed_lease_owner_even_with_fresh_outer_pins(self):
        self.prepare_recovery()
        terminal = v.s.record(self.failure)
        lease = v.s.record(terminal['lease'])
        lease['pid'] += 1
        terminal['lease'] = artifact(Path(terminal['lease']['path']), lease)
        self.failure = artifact(Path(self.failure['path']), terminal)
        receipt = self.alter_proof(lambda p: p['comparisonRerun'].update(priorFailure=self.failure))
        with self.assertRaisesRegex(ValueError, 'resource owner identity'): self.run_slot(receipt)

    def test_recovery_still_requires_unchanged_external_reference_hashes(self):
        receipt = self.prepare_recovery()
        Path(self.recovery['direction']['path']).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'artifact hash changed'): self.run_slot(receipt)
        receipt = self.refresh_direction()
        Path(self.proof['path']).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'artifact hash changed'): self.run_slot(receipt)

    def test_recovery_rejects_changed_saved_artifact(self):
        receipt = self.prepare_recovery()
        (self.saved/'raw-result.json').write_text('{"changed":true}')
        with self.assertRaises(ValueError): self.run_slot(receipt)

    def test_recovery_rejects_missing_or_false_source_transition(self):
        self.prepare_recovery()
        for transitions in ({}, {str(self.driver): self.transitions[str(self.driver)]},
                            {**self.transitions, str(self.source): {'oldSha256': '0'*64,
                                                                  'newSha256': '0'*64}}):
            with self.subTest(transitions=transitions), self.assertRaises(ValueError):
                self.run_slot(self.refresh_direction(sourceTransitions=transitions))

    def test_recovery_cannot_authorize_a_solver_source_change(self):
        self.prepare_recovery()
        old = self.new_sources[str(self.source)]
        self.source.write_text('# changed solver\n')
        self.new_sources[str(self.source)] = ref(self.source)['sha256']
        self.transitions[str(self.source)] = dict(oldSha256=old,
                                                 newSha256=self.new_sources[str(self.source)])
        with self.assertRaises(ValueError): self.run_slot(self.refresh_direction())

    def test_recovery_rejects_generic_failure_even_with_pinned_parent_direction(self):
        self.prepare_recovery()
        value = v.s.record(self.failure)
        value['error'] = dict(type='RuntimeError', message='solver failed')
        self.failure = artifact(Path(self.failure['path']), value)
        receipt = self.alter_proof(lambda p: p['comparisonRerun'].update(priorFailure=self.failure))
        with self.assertRaises(ValueError): self.run_slot(receipt)

    def test_recovery_rejects_unstarted_or_foreign_root_failure(self):
        self.prepare_recovery()
        for changes in ({'solverStarted': False}, {'mode': 'wrapped'},
                        {'status': 'refused-before-fit-no-fit'}):
            before = v.s.record(self.failure)
            modified = dict(before, **changes)
            self.failure = artifact(Path(self.failure['path']), modified)
            receipt = self.alter_proof(lambda p: p['comparisonRerun'].update(priorFailure=self.failure))
            with self.subTest(changes=changes), self.assertRaises(ValueError): self.run_slot(receipt)
            self.failure = artifact(Path(self.failure['path']), before)
        with self.assertRaises(ValueError):
            self.run_slot(self.refresh_direction(schedulerRoot=str(self.base/'foreign')))

    def test_recovery_rejects_rerun_or_changed_live_witness(self):
        self.prepare_recovery()
        original = v.s.record(self.proof)
        changes = [lambda p: p['comparisonRerun'].update(optimizerRuns=1),
                   lambda p: p['comparisonRerun'].update(nativeArchiveReads=1),
                   lambda p: p.update(rawResultBitsSha256='f'*64),
                   lambda p: p.update(trace={'sha256': 'f'*64}),
                   lambda p: p.update(sourceSha256={}),
                   lambda p: p.update(artifactDirectory=str(self.base)),
                   lambda p: p['comparisonRerun'].update(comparatorSourceSha256='f'*64)]
        for change in changes:
            self.proof = artifact(Path(self.proof['path']), original)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.run_slot(self.alter_proof(change))

    def test_recovery_requires_actual_old_new_driver_pair_and_pinned_diff(self):
        self.prepare_recovery()
        amendment = v.s.record(self.amendment)
        for key in ('oldSourceSha256', 'newSourceSha256'):
            modified = dict(amendment, **{key: 'f'*64})
            self.amendment = artifact(Path(self.amendment['path']), modified)
            receipt = self.alter_proof(lambda p: p['comparisonRerun'].update(
                driverCompatibility=self.amendment))
            with self.subTest(key=key), self.assertRaises(ValueError): self.run_slot(receipt)
        self.amendment = artifact(Path(self.amendment['path']), amendment)
        receipt = self.alter_proof(lambda p: p['comparisonRerun'].update(driverCompatibility=self.amendment))
        Path(amendment['diff']['path']).write_text('tampered')
        with self.assertRaises(ValueError): self.run_slot(receipt)

    def test_recovery_cannot_be_attached_to_unwrapped_launch(self):
        self.prepare_recovery()
        receipt = self.receipt(sourceSha256=self.new_sources, comparisonRecovery=self.recovery)
        with self.assertRaises(ValueError): v.validate(self.store, receipt)


if __name__ == '__main__':
    unittest.main()
