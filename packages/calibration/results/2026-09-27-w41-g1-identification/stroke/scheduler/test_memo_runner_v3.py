"""Operational dispatch only: no native reader, wrapper import or optimizer."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

import memo_runner as memo
import memo_runner_v3 as runner


def ref(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def artifact(path, value):
    path.write_text(json.dumps(value))
    return ref(path)


class MemoV3Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.legacy = memo.load_policy()
        self.engine = self.legacy.v2.v1
        self.original = self.engine.selected_fit
        # Only the new resource-policy dependency is a test double. The memo
        # proof gate, selection context and private v1 engine are the real ones.
        class StoreV3(self.legacy.v2.StoreV2):
            pass
        class PolicyStore(StoreV3):
            pass
        bridge_path, policy_path = self.root/'bridge.py', self.root/'scheduler_v3.py'
        bridge_path.write_text('# synthetic operational bridge\n')
        policy_path.write_text('# synthetic resource policy\n')
        self.policy_calls = []
        def verify_resource_receipt(launch):
            self.policy_calls.append(copy.deepcopy(launch))
            if launch['receiptVersion'] != 3:
                raise ValueError('resource gate requires original v3 receipt')
            self.engine.record(launch['adaptiveMemoryPolicy'])
        self.bridge = types.SimpleNamespace(__file__=str(bridge_path), legacy=self.legacy,
            s=self.engine, v2=self.legacy.v2,
            v3=types.SimpleNamespace(__file__=str(policy_path), v1=self.engine, StoreV3=StoreV3),
            PolicyStore=PolicyStore, verify_resource_receipt=verify_resource_receipt,
            resource_sources=lambda: [bridge_path, policy_path, *self.legacy.resource_sources()])
        self.store = PolicyStore(self.root/'state')
        self.launch = dict(kind='STROKE_LAUNCH', receiptVersion=3, task=['M1', 'device', 3],
            adaptiveMemoryPolicy=artifact(self.root/'adaptive.json', {'syntheticPolicy': 3}),
            memoization=self.proof_fixture(), resourceSourceSha256={
                str(p): ref(p)['sha256'] for p in runner.operational_sources(self.bridge)})
        self.reference = artifact(self.root/'launch.json', self.launch)

    def proof_fixture(self):
        sources = {str(p): ref(p)['sha256'] for p in memo.scientific_sources()}
        trace = dict(sha256='c'*64, events=4, counts={
            'solver-input': 1, 'callback-input': 1, 'callback-output': 1, 'solver-output': 1})
        references = {}
        for mode in ('unwrapped', 'wrapped'):
            directory = self.root/mode; directory.mkdir()
            pins = {}
            for name in memo.ARTIFACTS:
                p = directory/name; p.write_text('synthetic proof artifact')
                pins[name] = ref(p)['sha256']
            references[mode] = artifact(directory/'proof.json', dict(
                schema='w41-memoization-native-one-mode-1', mode=mode, verified=True,
                classification='verification replay, not a new candidate',
                completedArtifact='/synthetic/baseline', completedSha256='d'*64,
                rawResultBitsSha256='a'*64, jsonBoundaryResultBitsSha256='b'*64,
                trace=trace, artifacts=pins, sourceSha256=sources))
        comparison = artifact(self.root/'comparison.json', dict(
            schema='w41-memoization-native-bit-identity-1', verified=True,
            unwrapped=references['unwrapped'], wrapped=references['wrapped'],
            completedSha256='d'*64, rawResultBitsSha256='a'*64,
            jsonBoundaryResultBitsSha256='b'*64, trace=trace,
            executionSourceSha256=dict(unwrapped=sources, wrapped=sources), driverCompatibility=None))
        return dict(comparison=comparison, wrappedProof=references['wrapped'])

    def save_launch(self):
        self.reference = artifact(self.root/'launch.json', self.launch)

    def test_actual_adaptive_bridge_store_dispatches_without_resource_or_fit_execution(self):
        bridge = runner.load_policy()
        store = bridge.PolicyStore(self.root/'actual-v3-state')
        launch = dict(self.launch, resourceSourceSha256={
            str(p): ref(p)['sha256'] for p in runner.operational_sources(bridge)},
            memoryPolicy=ref(memo.STROKE/'scheduler-memory-parent-direction-v2.json'),
            memoryCounterDirection=ref(memo.STROKE/'scheduler-memory-counter-clarification.json'),
            adaptiveMemoryPolicy=ref(memo.STROKE/'scheduler-memory-parent-direction-v3.json'))
        reference = artifact(self.root/'actual-v3-launch.json', launch)
        engine = bridge.s
        original = engine.selected_fit
        def delegate(received_store, received_reference):
            self.assertIs(received_store, store)
            self.assertIs(received_reference, reference)
            self.assertIsInstance(received_store, bridge.v3.StoreV3)
            self.assertIs(received_store.finish.__func__, bridge.v3.StoreV3.finish)
            self.assertEqual(engine.record(received_reference)['receiptVersion'], 3)
            return 'actual store accepted; no claim or fit executed'
        with patch.object(engine, 'run', side_effect=delegate), \
                patch.object(memo, 'load_wrapper', side_effect=AssertionError('no wrapper import')):
            self.assertEqual(runner.run(store, reference, bridge=bridge),
                             'actual store accepted; no claim or fit executed')
        self.assertIs(engine.selected_fit, original)
        self.assertFalse(store.root.exists())

    def test_original_v3_reference_reaches_engine_and_only_proof_view_uses_v2(self):
        before = Path(self.reference['path']).read_bytes()
        def delegate(store, reference):
            self.assertIs(store, self.store)
            self.assertIs(reference, self.reference)
            self.assertEqual(self.engine.record(reference)['receiptVersion'], 3)
            self.assertIsNot(self.engine.selected_fit, self.original)
            return 'delegated without a fit'
        with patch.object(self.engine, 'run', side_effect=delegate), \
                patch.object(memo, 'validate_launch', wraps=memo.validate_launch) as proof_gate, \
                patch.object(memo, 'selection', wraps=memo.selection) as selection, \
                patch.object(memo, 'load_wrapper', side_effect=AssertionError('no wrapper import')):
            self.assertEqual(runner.run(self.store, self.reference, bridge=self.bridge),
                             'delegated without a fit')
        view, received_bridge = proof_gate.call_args.args
        self.assertEqual(view, dict(self.launch, receiptVersion=2))
        self.assertIs(received_bridge, self.legacy)
        self.assertEqual(selection.call_args.args[1], view)
        self.assertIs(selection.call_args.args[2], self.legacy)
        self.assertEqual(self.policy_calls, [self.launch])
        self.assertEqual(Path(self.reference['path']).read_bytes(), before)
        self.assertIs(self.engine.selected_fit, self.original)

    def test_wrapped_pass_is_still_required_before_engine_claim(self):
        self.launch['memoization']['comparison'] = dict(path=str(self.root/'not-passed'), sha256='a'*64)
        self.save_launch()
        with patch.object(self.engine, 'run') as delegate, patch.object(memo, 'load_wrapper') as wrapper:
            with self.assertRaises(FileNotFoundError):
                runner.run(self.store, self.reference, bridge=self.bridge)
            delegate.assert_not_called(); wrapper.assert_not_called()
        self.assertIs(self.engine.selected_fit, self.original)

    def test_v2_or_implicit_adaptive_receipt_cannot_enter_v3_dispatch(self):
        for change in (dict(receiptVersion=2), dict(kind='STROKE_VERIFICATION')):
            self.launch.update(change); self.save_launch()
            with patch.object(self.engine, 'run') as delegate:
                with self.assertRaises(ValueError): runner.run(self.store, self.reference, bridge=self.bridge)
                delegate.assert_not_called()
        self.launch.update(kind='STROKE_LAUNCH', receiptVersion=3)
        del self.launch['adaptiveMemoryPolicy']; self.save_launch()
        with patch.object(self.engine, 'run') as delegate:
            with self.assertRaises(KeyError): runner.run(self.store, self.reference, bridge=self.bridge)
            delegate.assert_not_called()

    def test_new_operational_dependencies_are_required_and_hash_checked(self):
        for path in (Path(runner.__file__).resolve(), Path(self.bridge.v3.__file__),
                     Path(self.bridge.__file__), Path(self.legacy.__file__)):
            saved = self.launch['resourceSourceSha256'].pop(str(path))
            self.save_launch()
            with self.subTest(path=path), patch.object(self.engine, 'run') as delegate:
                with self.assertRaises(ValueError): runner.run(self.store, self.reference, bridge=self.bridge)
                delegate.assert_not_called()
            self.launch['resourceSourceSha256'][str(path)] = saved
        self.launch['resourceSourceSha256'][str(Path(runner.__file__).resolve())] = 'f'*64
        self.save_launch()
        with self.assertRaises(ValueError): runner.run(self.store, self.reference, bridge=self.bridge)

    def test_engine_exception_restores_unchanged_selection_and_finish(self):
        finish = self.store.finish.__func__
        with patch.object(self.engine, 'run', side_effect=RuntimeError('claim deferred')):
            with self.assertRaisesRegex(RuntimeError, 'claim deferred'):
                runner.run(self.store, self.reference, bridge=self.bridge)
        self.assertIs(self.engine.selected_fit, self.original)
        self.assertIs(self.store.finish.__func__, finish)

    def test_mismatched_engine_or_finish_override_is_rejected(self):
        original_engine = self.bridge.v3.v1
        self.bridge.v3.v1 = types.SimpleNamespace()
        with self.assertRaises(ValueError): runner.run(self.store, self.reference, bridge=self.bridge)
        self.bridge.v3.v1 = original_engine
        class ChangedFinish(self.bridge.PolicyStore):
            def finish(self, claim, result): pass
        with self.assertRaises(ValueError):
            runner.run(ChangedFinish(self.store.root), self.reference, bridge=self.bridge)


if __name__ == '__main__': unittest.main()
