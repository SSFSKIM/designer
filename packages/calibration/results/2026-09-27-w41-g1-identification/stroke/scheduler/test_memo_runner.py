"""New-start opt-in only: synthetic proof fixtures, no native payload or fit."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import memo_runner as runner
from test_scheduler import artifact, ref
import test_scheduler_v2 as policy_tests

BRIDGE = runner.load_policy()
ENGINE = BRIDGE.v2.v1
sys.path.insert(0, str(runner.MEMO))
from fixtures import f
import numpy as np
sys.path.pop(0)
EVENTS = []
FAIL_CALLBACK = False


def tiny_fit(observations, family, css, curvature):
    """Actual SciPy callbacks at a planted zero; not a scientific fit candidate."""
    low, high, initial = f.domain(family, curvature)
    starts = [initial, *np.random.default_rng(4100).uniform(low, high, (15, len(initial)))]
    records = []
    for i, start in enumerate(starts):
        EVENTS.append(('optimizer', i))
        def residual(q):
            if FAIL_CALLBACK:
                raise RuntimeError('synthetic callback failed')
            return np.array([f.unpack(q, family, 1)[1]-start[2]])
        solved = f.least_squares(residual, start, bounds=(low, high), max_nfev=3000,
                                ftol=1e-10, xtol=1e-10, gtol=1e-10)
        records.append(dict(startIndex=i, initial=start.tolist(), answer=solved.x.tolist(),
                            evaluations=int(solved.nfev), success=bool(solved.success)))
    return dict(family=family, cssWidth=css, curvature=curvature, starts=records,
                unchangedMetadata={'label': 'uninterpreted', 'signedZero': -0.})


class MemoRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.store = BRIDGE.PolicyStore(self.root/'scheduler')
        self.original = ENGINE.selected_fit
        self.proofs = self.proof_fixture()
        self.launch = dict(kind='STROKE_LAUNCH', receiptVersion=2,
            memoization=self.proofs,
            resourceSourceSha256={str(p): ref(p)['sha256'] for p in runner.operational_sources(BRIDGE)})
        EVENTS.clear()

    def proof_fixture(self):
        scientific = {str(p): ref(p)['sha256'] for p in runner.scientific_sources()}
        result_hash, boundary_hash, trace_hash = ['a'*64, 'b'*64, 'c'*64]
        trace = dict(sha256=trace_hash, events=4,
                     counts={'solver-input': 1, 'callback-input': 1,
                             'callback-output': 1, 'solver-output': 1})
        manifests = {}
        for mode in ('unwrapped', 'wrapped'):
            directory = self.root/mode; directory.mkdir()
            pins = {}
            for name in ('trace.jsonl.gz', 'raw-result.json', 'replay.json'):
                path = directory/name
                path.write_bytes(('synthetic proof fixture '+mode+name).encode())
                pins[name] = ref(path)['sha256']
            manifests[mode] = artifact(directory/'completed-start-proof.json', dict(
                schema='w41-memoization-native-one-mode-1', verified=True, mode=mode,
                classification='verification replay, not a new candidate',
                completedArtifact='/synthetic/original', completedSha256='d'*64,
                rawResultBitsSha256=result_hash, jsonBoundaryResultBitsSha256=boundary_hash,
                trace=trace, sourceSha256=scientific, artifacts=pins))
        comparison = artifact(self.root/'comparison.json', dict(
            schema='w41-memoization-native-bit-identity-1', verified=True,
            unwrapped=manifests['unwrapped'], wrapped=manifests['wrapped'],
            completedSha256='d'*64, rawResultBitsSha256=result_hash,
            jsonBoundaryResultBitsSha256=boundary_hash, trace=trace,
            executionSourceSha256={'unwrapped': scientific, 'wrapped': scientific},
            driverCompatibility=None))
        return dict(comparison=comparison, wrappedProof=manifests['wrapped'])

    def repin(self, key, value):
        path = Path(self.proofs[key]['path']); path.write_text(json.dumps(value))
        self.proofs[key] = ref(path)
        self.launch['memoization'] = self.proofs

    def evidence(self):
        return runner.validate_launch(self.launch, BRIDGE)

    def test_missing_or_failed_proof_refuses_before_claim_and_wrapper_import(self):
        for bad in ({}, dict(self.proofs, comparison={'path': str(self.root/'absent'), 'sha256': 'a'*64})):
            launch = dict(self.launch, memoization=bad)
            reference = artifact(self.root/'launch.json', launch)
            with patch.object(ENGINE, 'run') as delegate, patch.object(runner, 'load_wrapper') as load:
                with self.assertRaises((ValueError, KeyError, FileNotFoundError)):
                    runner.run(self.store, reference, bridge=BRIDGE)
                delegate.assert_not_called(); load.assert_not_called()
        comparison = ENGINE.record(self.proofs['comparison']); comparison['verified'] = False
        self.repin('comparison', comparison)
        with self.assertRaises(ValueError): self.evidence()

    def test_artifact_tampering_source_mismatch_and_missing_operational_pin_refuse(self):
        path = self.root/'wrapped/raw-result.json'
        original = path.read_bytes(); path.write_bytes(b'changed')
        with self.assertRaises(ValueError): self.evidence()
        path.write_bytes(original)
        wrapped = ENGINE.record(self.proofs['wrappedProof'])
        wrapped['sourceSha256'][str(runner.MEMO/'solver_memo.py')] = 'f'*64
        self.repin('wrappedProof', wrapped)
        with self.assertRaises(ValueError): self.evidence()
        self.launch['resourceSourceSha256'].pop(str(Path(runner.__file__).resolve()))
        with self.assertRaises(ValueError): self.evidence()

    def test_witness_mismatch_refuses_even_with_a_rehashed_comparison(self):
        comparison = ENGINE.record(self.proofs['comparison'])
        comparison['rawResultBitsSha256'] = 'e'*64
        self.repin('comparison', comparison)
        with self.assertRaises(ValueError): self.evidence()

    def test_missing_artifact_and_matching_but_wrong_scientific_epoch_refuse(self):
        path = self.root/'unwrapped/trace.jsonl.gz'
        raw = path.read_bytes(); path.unlink()
        with self.assertRaises(FileNotFoundError): self.evidence()
        path.write_bytes(raw)
        comparison = ENGINE.record(self.proofs['comparison'])
        wrong = copy.deepcopy(comparison['executionSourceSha256']['wrapped'])
        wrong[str(runner.MEMO/'solver_memo.py')] = 'f'*64
        for mode in ('unwrapped', 'wrapped'):
            reference = comparison[mode]
            manifest = ENGINE.record(reference); manifest['sourceSha256'] = wrong
            comparison[mode] = artifact(Path(reference['path']), manifest)
            comparison['executionSourceSha256'][mode] = wrong
        self.proofs['wrappedProof'] = comparison['wrapped']
        self.repin('comparison', comparison)
        with self.assertRaisesRegex(ValueError, 'artifact hash changed'):
            self.evidence()

    def test_callback_exception_restores_solver_functions_and_selection_hook(self):
        evidence = self.evidence()
        prior = types.SimpleNamespace(r=types.SimpleNamespace(f=f))
        solvers = f.least_squares, f.minimize
        with patch.object(f, 'fit_local', tiny_fit), patch.dict(sys.modules, survivor_scope_runner=prior), \
                patch.dict(globals(), FAIL_CALLBACK=True):
            with self.assertRaisesRegex(RuntimeError, 'synthetic callback failed'):
                with runner.selection(evidence, self.launch, BRIDGE):
                    ENGINE.selected_fit(f.fit_local, [{'endpoint': 1}], ['M1', 'device', 0],
                                        lambda: EVENTS.append(('marker', 0)))
        self.assertEqual(EVENTS, [('marker', 0), ('optimizer', 0)])
        self.assertEqual((f.least_squares, f.minimize), solvers)
        self.assertIs(ENGINE.selected_fit, self.original)

    def test_selected_fit_preserves_marker_vector_scope_provenance_and_metadata(self):
        evidence = self.evidence()
        prior = types.SimpleNamespace(r=types.SimpleNamespace(f=f))
        obs = [{'endpoint': 1}]; task = ['M1', 'device', 0]
        with patch.object(f, 'fit_local', tiny_fit), patch.dict(sys.modules, survivor_scope_runner=prior):
            expected, expected_provenance = self.original(f.fit_local, obs, task)
            EVENTS.clear()
            marker = lambda: EVENTS.append(('marker', 0))
            with runner.selection(evidence, self.launch, BRIDGE):
                actual, provenance = ENGINE.selected_fit(f.fit_local, obs, task, before_fit=marker)
        memo = actual.pop('memoization')
        operational = actual.pop('memoizationOperationalSourceSha256')
        self.assertEqual(actual, expected)
        self.assertEqual(provenance, expected_provenance)
        self.assertEqual(EVENTS, [('marker', 0), ('optimizer', 0)])
        self.assertTrue(memo['enabled'])
        self.assertEqual(memo['comparison'], self.proofs['comparison'])
        self.assertGreater(memo['cache']['hits'], 0)
        self.assertEqual(operational, self.launch['resourceSourceSha256'])
        self.assertIs(ENGINE.selected_fit, self.original)

    def test_fit_identity_and_context_restore_on_marker_exception(self):
        evidence = self.evidence()
        prior = types.SimpleNamespace(r=types.SimpleNamespace(f=f))
        solvers = f.least_squares, f.minimize
        with patch.object(f, 'fit_local', tiny_fit), patch.dict(sys.modules, survivor_scope_runner=prior):
            with self.assertRaisesRegex(ValueError, 'identity'):
                with runner.selection(evidence, self.launch, BRIDGE):
                    ENGINE.selected_fit(lambda: None, [{'endpoint': 1}], ['M1', 'device', 0])
            def refuse(): raise RuntimeError('marker refused')
            with self.assertRaisesRegex(RuntimeError, 'marker refused'):
                with runner.selection(evidence, self.launch, BRIDGE):
                    ENGINE.selected_fit(f.fit_local, [{'endpoint': 1}], ['M1', 'device', 0], refuse)
        self.assertIs(ENGINE.selected_fit, self.original)
        self.assertEqual((f.least_squares, f.minimize), solvers)
        self.assertEqual(EVENTS, [])

    def test_run_delegates_same_store_reference_and_loads_wrapper_after_claim(self):
        reference = artifact(self.root/'launch.json', self.launch)
        prior = types.SimpleNamespace(r=types.SimpleNamespace(f=f))
        original_load = runner.load_wrapper
        def load():
            self.assertIn(('claim', 0), EVENTS)
            return original_load()
        def delegate(store, received):
            self.assertIs(store, self.store); self.assertIs(received, reference)
            EVENTS.append(('claim', 0))
            return ENGINE.selected_fit(f.fit_local, [{'endpoint': 1}], ['M1', 'device', 0],
                                       lambda: EVENTS.append(('marker', 0)))
        with patch.object(f, 'fit_local', tiny_fit), patch.dict(sys.modules, survivor_scope_runner=prior), \
                patch.object(ENGINE, 'run', side_effect=delegate), \
                patch.object(runner, 'load_wrapper', side_effect=load):
            runner.run(self.store, reference, bridge=BRIDGE)
        self.assertEqual(EVENTS, [('claim', 0), ('marker', 0), ('optimizer', 0)])
        self.assertIs(ENGINE.selected_fit, self.original)
        with patch.object(ENGINE, 'run', side_effect=RuntimeError('claim refused')), \
                patch.object(runner, 'load_wrapper') as load:
            with self.assertRaises(RuntimeError): runner.run(self.store, reference, bridge=BRIDGE)
            load.assert_not_called()
        self.assertIs(ENGINE.selected_fit, self.original)

    def test_real_storev2_finish_still_requires_marker_and_is_exactly_once(self):
        # Use the existing scheduler's synthetic ownership setup and real StoreV2
        # claim/marker/finish methods. No resource or publication method is replaced.
        h = policy_tests.PolicyV2Tests(methodName='runTest'); h.setUp(); self.addCleanup(h.doCleanups)
        claim = h.claim()
        evidence = self.evidence()
        prior = types.SimpleNamespace(r=types.SimpleNamespace(f=f))
        h.store.check_before_fit(claim, alive=h.live.__contains__, memory=lambda: h.memory)
        with patch.object(f, 'fit_local', tiny_fit), patch.dict(sys.modules, survivor_scope_runner=prior):
            with runner.selection(evidence, self.launch, BRIDGE):
                result, _ = ENGINE.selected_fit(f.fit_local, [{'endpoint': 1}], claim['task'],
                                                before_fit=lambda: h.store.start_solver(claim))
        h.store.finish(claim, result)
        saved = json.loads((h.root/'results/device-M1-start-00.json').read_text())
        self.assertEqual(saved['memoization'], result['memoization'])
        self.assertEqual(saved['starts'], result['starts'])
        with self.assertRaises(FileExistsError): h.store.finish(claim, result)
        with self.assertRaises(ValueError): h.claim()


if __name__ == '__main__': unittest.main()
