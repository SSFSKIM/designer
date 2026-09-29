"""Additive adaptive-resource dispatch; the reviewed memo proof gate/hook are reused.

The original hash-pinned STROKE_LAUNCH has receiptVersion 4 (policy v4: the kernel
memory level) with the explicit kernelMemoryPolicy reference and the historical
adaptiveMemoryPolicy one, alongside its inherited operational fields.
Only the legacy memo proof checker receives a metadata-only receiptVersion 2
view. That view changes no scientific field, proof reference or source pin and
never reaches resource admission, the scheduler claim or result publication.

No policy is implemented here, and no proof success is created. StoreV3 selects
its normal/degraded resource mode. The unchanged memo gate still requires the
wrapped native bit/trace PASS before the unchanged v1 runner may claim a start.
"""
import argparse
import importlib
from pathlib import Path
import sys

import memo_runner as memo

HERE = Path(__file__).resolve().parent
BRIDGE = HERE.parent/'verification-slot/verification_policy_v3.py'


def load_policy():
    sys.path.insert(0, str(BRIDGE.parent))
    try:
        module = importlib.import_module('verification_policy_v3')
    finally:
        sys.path.pop(0)
    if Path(module.__file__).resolve() != BRIDGE:
        raise ValueError('unexpected adaptive policy module identity')
    return module


def operational_sources(bridge):
    paths = [Path(__file__), Path(bridge.__file__), Path(bridge.v3.__file__),
             *memo.operational_sources(bridge.legacy), *bridge.resource_sources()]
    return list(dict.fromkeys(path.resolve() for path in paths))


def run(store, reference, *, bridge=None):
    bridge = bridge or load_policy()
    engine = bridge.legacy.v2.v1
    if bridge.s is not engine or bridge.v3.v1 is not engine \
            or not isinstance(store, bridge.PolicyStore) \
            or type(store).finish is not bridge.v3.StoreV3.finish:
        raise ValueError('actual adaptive PolicyStore, private engine and StoreV3.finish are required')
    launch = engine.record(reference)
    if launch.get('kind') != 'STROKE_LAUNCH' or launch.get('receiptVersion') != 4:
        raise ValueError('adaptive memoization requires an explicit policy-v4 candidate launch')
    bridge.verify_resource_receipt(launch)
    engine.verify_sources(launch['resourceSourceSha256'], operational_sources(bridge))
    # Compatibility concerns only the legacy checker's version discriminator.
    # Preserve the original receipt and pass its exact reference to v1.run.
    proof_view = dict(launch, receiptVersion=2)
    evidence = memo.validate_launch(proof_view, bridge.legacy)
    with memo.selection(evidence, proof_view, bridge.legacy):
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
