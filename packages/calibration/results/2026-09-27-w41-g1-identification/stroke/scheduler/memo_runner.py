"""Opt-in memoization for NEW exact-once scheduler starts, after native proof PASS.

The parent STROKE_LAUNCH remains a policy-v2 launch with its existing ownership,
pressure-history, watcher and memory fields. It additionally names
  memoization: {comparison: REF, wrappedProof: REF}
and includes this runner, the operational bridge/adapter and both scheduler
sources in resourceSourceSha256. REF is an absolute path plus its SHA-256.

No successful proof is created here. No existing start, fitter, scheduler, budget
or receipt is rewritten. The unchanged v1 runner owns preparation, both resource
gates, the durable solver marker, settlement and StoreV2's exact-once finish.
"""
import argparse
from contextlib import contextmanager
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STROKE = HERE.parent
MEMO = STROKE/'memoization'
BRIDGE = STROKE/'verification-slot/verification_policy_v2.py'
PROOF = Path('/Users/new/vitrea-w41/pre-w41-proof')
ARTIFACTS = ('trace.jsonl.gz', 'raw-result.json', 'replay.json')


def load_policy():
    """Operational imports only; no NumPy, native reader or fitter is loaded."""
    sys.path.insert(0, str(BRIDGE.parent))
    try:
        module = importlib.import_module('verification_policy_v2')
    finally:
        sys.path.pop(0)
    if Path(module.__file__).resolve() != BRIDGE:
        raise ValueError('unexpected operational policy module identity')
    return module


def operational_sources(bridge):
    return [Path(p).resolve() for p in (
        __file__, bridge.__file__, bridge.adapter.__file__,
        bridge.v2.__file__, bridge.v2.v1.__file__)]


def scientific_sources():
    held = PROOF/STROKE.relative_to(STROKE.parents[4])
    instrument = PROOF/'packages/calibration/results/2026-09-27-w41-g0-declaration/instrument'
    return [*(MEMO/name for name in ('proof.py', 'solver_memo.py', 'fixtures.py')),
            STROKE/'start_partition.py', held/'replay.py',
            instrument/'stroke_fit.py', instrument/'instrument.py']


def verify_file(path, digest):
    with Path(path).open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != digest:
        raise ValueError('artifact hash changed: '+str(path))


def same(left, right, label):
    # Manifest comparison must not conflate JSON true with 1, or 1 with 1.0.
    if json.dumps(left, sort_keys=True, allow_nan=False) != json.dumps(right, sort_keys=True, allow_nan=False):
        raise ValueError(label+' differs')


def validate_launch(launch, bridge):
    """Lightweight proof/source gate before claiming; repeated at the fit boundary."""
    engine = bridge.v2.v1
    if launch.get('kind') != 'STROKE_LAUNCH' or launch.get('receiptVersion') != 2:
        raise ValueError('memoization requires an explicit policy-v2 candidate launch')
    engine.verify_sources(launch['resourceSourceSha256'], operational_sources(bridge))
    requested = launch.get('memoization')
    if not isinstance(requested, dict) or set(requested) != {'comparison', 'wrappedProof'}:
        raise ValueError('hash-pinned wrapped proof and native comparison PASS are required')
    comparison = engine.record(requested['comparison'])
    if comparison.get('schema') != 'w41-memoization-native-bit-identity-1' \
            or comparison.get('verified') is not True:
        raise ValueError('native wrapped comparison has not passed')
    same(comparison['wrapped'], requested['wrappedProof'], 'explicit wrapped proof reference')
    proofs = {}
    for mode in ('unwrapped', 'wrapped'):
        reference = comparison[mode]
        receipt = engine.record(reference)
        if receipt.get('schema') != 'w41-memoization-native-one-mode-1' \
                or receipt.get('verified') is not True or receipt.get('mode') != mode \
                or receipt.get('classification') != 'verification replay, not a new candidate':
            raise ValueError('native mode proof is not a verified completed-start replay')
        pins = receipt.get('artifacts')
        if not isinstance(pins, dict) or set(pins) != set(ARTIFACTS):
            raise ValueError('native proof must retain all required artifact pins')
        directory = Path(receipt.get('artifactDirectory', Path(reference['path']).parent))
        if not directory.is_absolute():
            raise ValueError('proof artifact directory must be absolute')
        for name in ARTIFACTS:
            verify_file(directory/name, pins[name])
        for key in ('rawResultBitsSha256', 'jsonBoundaryResultBitsSha256', 'trace', 'completedSha256'):
            same(receipt[key], comparison[key], mode+' '+key)
        same(receipt['sourceSha256'], comparison['executionSourceSha256'][mode],
             mode+' execution source map')
        proofs[mode] = receipt
    same(proofs['unwrapped']['completedArtifact'], proofs['wrapped']['completedArtifact'],
         'completed-start baseline')
    old, new = [proofs[mode]['sourceSha256'] for mode in ('unwrapped', 'wrapped')]
    required = {str(p) for p in scientific_sources()}
    if set(old) != required or set(new) != required:
        raise ValueError('native proof scientific source membership changed')
    driver = str(MEMO/'proof.py')
    same({k: v for k, v in old.items() if k != driver},
         {k: v for k, v in new.items() if k != driver}, 'scientific and solver-wrapper sources')
    amendment_ref = comparison.get('driverCompatibility')
    if old[driver] != new[driver]:
        amendment = engine.record(amendment_ref)
        if amendment.get('schema') != 'w41-proof-driver-comparison-amendment-1' \
                or amendment.get('sourcePath') != driver \
                or (amendment.get('oldSourceSha256'), amendment.get('newSourceSha256')) != (
                    old[driver], new[driver]):
            raise ValueError('native driver transition lacks its exact pinned amendment')
        engine.pinned(amendment['diff'])
    # The wrapped run's source epoch is the one new starts must execute. The old
    # unwrapped driver is historical; its actual source map is never rewritten.
    for path, digest in new.items():
        verify_file(path, digest)
    return dict(comparison=requested['comparison'], wrappedProof=requested['wrappedProof'],
        typedResultBitsSha256=comparison['rawResultBitsSha256'],
        jsonBoundaryResultBitsSha256=comparison['jsonBoundaryResultBitsSha256'],
        trace=comparison['trace'], scientificSourceSha256=new,
        driverCompatibility=amendment_ref)


def load_wrapper():
    """Called only inside selected_fit, after v1 has claimed and admitted the fit."""
    spec = importlib.util.spec_from_file_location('w41_new_start_solver_memo', MEMO/'solver_memo.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def selection(evidence, launch, bridge):
    engine = bridge.v2.v1
    original = engine.selected_fit
    if getattr(original, '__memo_selected__', False) \
            or original.__globals__ is not vars(engine) \
            or Path(original.__code__.co_filename).resolve() != Path(engine.__file__).resolve():
        raise ValueError('original selected_fit function identity required')

    def selected(function, observations, task, before_fit=None):
        same(validate_launch(launch, bridge), evidence, 'proof gate at fit entry')
        # The unchanged v1 runner already imported this exact scope/fitter pair
        # after its claim. Do not import or substitute a second fitter namespace.
        prior = sys.modules.get('survivor_scope_runner')
        if prior is None or function is not prior.r.f.fit_local:
            raise ValueError('selected fitter function identity changed')
        family, geometry, _ = engine.task_tuple(task)
        wrapper = load_wrapper()
        with wrapper.SolverMemo(prior.r.f, observations, family, geometry == 'curvature') as memo:
            result, provenance = original(function, observations, task, before_fit=before_fit)
        # Publication may not silently outlive a change to its cited proof or
        # operational sources. This is integrity checking, not another admission.
        same(validate_launch(launch, bridge), evidence, 'proof gate at fit return')
        if 'memoization' in result or 'memoizationOperationalSourceSha256' in result:
            raise ValueError('unwrapped result already contains memoization metadata')
        result = dict(result,
            memoization=dict(enabled=True, **copy.deepcopy(evidence), cache=memo.summary()),
            memoizationOperationalSourceSha256=copy.deepcopy(launch['resourceSourceSha256']))
        return result, provenance

    selected.__memo_selected__ = True
    engine.selected_fit = selected
    try:
        yield
    finally:
        engine.selected_fit = original


def run(store, reference, *, bridge=None):
    bridge = bridge or load_policy()
    if not isinstance(store, bridge.PolicyStore) \
            or type(store).finish is not bridge.v2.StoreV2.finish:
        raise ValueError('unchanged operational PolicyStore and StoreV2.finish are required')
    engine = bridge.v2.v1
    launch = engine.record(reference)
    evidence = validate_launch(launch, bridge)
    with selection(evidence, launch, bridge):
        return engine.run(store, reference)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    bridge = load_policy()
    run(bridge.PolicyStore(args.root), {'path': args.receipt, 'sha256': args.sha256}, bridge=bridge)


if __name__ == '__main__':
    main()
