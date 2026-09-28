"""Additive adaptive-policy composition; no numerical or memory policy here.

CLI: python -B -X pycache_prefix=FRESH_EMPTY_DIR verification_policy_v3.py
       --root ROOT --receipt RECEIPT --sha256 SHA

Receipt version 4 (policy v4, kernel memory level) retains all scientific/recovery
pins and the legacy observer fields (memoryPolicy, memoryCounterDirection,
pressureSnapshot, pressureImport, pressureWatcher) and the policy-v3
adaptiveMemoryPolicy reference as HISTORY (path and hash checked, numbers not
used). kernelMemoryPolicy must point to the v4 parent direction and selects the
gate. resourceSourceSha256 must pin this driver, scheduler_v3.py, the reviewed v2
composition and scheduler_v2.py; additional operational pins are also checked.
Version 3 receipts are refused: their counter reading is superseded.

The frozen v2 observer checker receives a NEW metadata-only dict with version 2.
It checks sources, completed imported history and the existing live v2 watcher;
it does not admit work. The original version-3 receipt and actual memory/disk
readings reach StoreV3 unchanged; run and preflight default to StoreV3's kernel
reader (v3.kernel_memory), never to v2's counter. Its resourceMode is retained beside
the original adapter's verification mode. No synthetic NORMAL reading or headroom is
supplied.

PolicyStore(root, clock=..., disk=None, swap=...) exposes the actual StoreV3 with
those observer checks. Module aliases v3, v2=legacy.v2, s=v3.v1 expose the exact
private engines. Candidate clients may reuse PolicyStore with original version-3
STROKE_LAUNCH receipts and the established allocation-lock protocol.

run(root, receipt_ref, proof_body=..., memory=..., disk=None, swap=..., clock=...)
uses the unchanged adapter. preflight(root, receipt_ref, ...) takes the same lock
and real gate once, without a mode lease or reservation; both fresh gates still
run during execution. Neither starts a watcher, retries, stops work or imports a
native proof. CLI main delegates the original adapter's native import/call path.
"""
import importlib.util
import os
from pathlib import Path
import sys

import verification_policy_v2 as legacy

adapter, s, v2 = legacy.adapter, legacy.s, legacy.v2
ADAPTIVE_POLICY = adapter.STROKE/'scheduler-memory-parent-direction-v3.json'
KERNEL_POLICY = adapter.STROKE/'scheduler-memory-parent-direction-v4.json'
_spec = importlib.util.spec_from_file_location('verification_scheduler_v3',
                                              adapter.STROKE/'scheduler/scheduler_v3.py')
v3 = importlib.util.module_from_spec(_spec)
_prior_modules = {name: sys.modules.get(name) for name in ('scheduler', 'scheduler_v2')}
sys.modules.update(scheduler=s, scheduler_v2=v2)
try:
    _spec.loader.exec_module(v3)
finally:
    for _name, _module in _prior_modules.items():
        if _module is None:
            del sys.modules[_name]
        else:
            sys.modules[_name] = _module
v3.claim_name = adapter.owner_name


def resource_sources():
    return [Path(__file__).resolve(), Path(v3.__file__).resolve(), *legacy.resource_sources()]


def verify_resource_receipt(receipt):
    if receipt.get('receiptVersion') != 4:
        raise ValueError('kernel-level adaptive composition requires receiptVersion 4')
    s.verify_sources(receipt['resourceSourceSha256'], resource_sources())
    for field, path, check in (('adaptiveMemoryPolicy', ADAPTIVE_POLICY, v3.check_direction),
                               ('kernelMemoryPolicy', KERNEL_POLICY, v3.check_kernel_direction)):
        if receipt[field]['path'] != str(path):
            raise ValueError('explicit historical v3 and authoritative v4 directions are required')
        check(s.record(receipt[field]))
    # Compatibility is only for frozen source/direction validation, never for
    # an admission or persisted receipt. The original mapping is not mutated.
    legacy.verify_resource_receipt(dict(receipt, receiptVersion=2))


class PolicyStore(v3.StoreV3):
    def __init__(self, root, *, clock=lambda: v2.timestamp(s.now()), disk=None, swap=v3.swap_usage):
        super().__init__(root, disk=disk, swap=swap)
        self.clock = clock

    def check_resources(self, receipt, alive):
        verify_resource_receipt(receipt)
        return legacy.PolicyStore.check_resources(self, dict(receipt, receiptVersion=2), alive)

    def _admission(self, launch, pid, alive, memory, rss, *, own_claim=None):
        latest = self.check_resources(launch, alive)
        decision = super()._admission(launch, pid, alive, memory, rss, own_claim=own_claim)
        return dict(decision, **{key: launch[key] for key in (
            'resourceSourceSha256', 'memoryPolicy', 'memoryCounterDirection',
            'pressureSnapshot', 'pressureImport', 'pressureWatcher',
            'adaptiveMemoryPolicy')}, watcherReading=latest)


def run(root, reference, *, proof_body, memory=v3.kernel_memory, disk=None, swap=v3.swap_usage,
        clock=lambda: v2.timestamp(s.now()), **process_readings):
    receipt = s.record(reference)
    verify_resource_receipt(receipt)

    def checked_body(mode, out, admit):
        result = proof_body(mode, out, admit)
        verify_resource_receipt(receipt)
        return result

    return legacy._ADAPTER_RUN(PolicyStore(root, clock=clock, disk=disk, swap=swap), reference,
                              proof_body=checked_body, memory=memory, **process_readings)


def preflight(root, reference, *, alive=s.alive, memory=v3.kernel_memory, rss=s.process_rss,
              disk=None, swap=v3.swap_usage, clock=lambda: v2.timestamp(s.now())):
    store = PolicyStore(root, clock=clock, disk=disk, swap=swap)
    with store.locked():
        receipt = adapter.validate(store, reference)
        decision = adapter.resource_admission(store, receipt, os.getpid(), alive, memory, rss,
                                              prepared=False)
        return dict(decision, preflight=True, reservationHeld=False)


def main():
    original = adapter.run
    adapter.run = lambda store, reference, **kwargs: run(store.root, reference, **kwargs)
    try:
        adapter.main()
    finally:
        adapter.run = original


if __name__ == '__main__':
    main()
