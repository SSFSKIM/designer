"""Additive operational composition: unchanged verification adapter, real StoreV2.

No memory policy is implemented here. The parent imports the completed pressure
snapshot and starts a bounded watcher separately. This driver verifies those
prerequisites and operational source pins at both existing admission gates.
"""
from datetime import timedelta
import importlib.util
import os
from pathlib import Path
import sys

import verification_slot as adapter

s = adapter.s
POLICY = adapter.STROKE/'scheduler-memory-parent-direction-v2.json'
COUNTER_DIRECTION = adapter.STROKE/'scheduler-memory-counter-clarification.json'
_spec = importlib.util.spec_from_file_location('verification_scheduler_v2',
                                              adapter.STROKE/'scheduler/scheduler_v2.py')
v2 = importlib.util.module_from_spec(_spec)
# v2 imports scheduler by name. Bind that import to the adapter's PRIVATE v1
# module only while loading; restore the process import table immediately.
_prior_scheduler = sys.modules.get('scheduler')
sys.modules['scheduler'] = s
try:
    _spec.loader.exec_module(v2)
finally:
    if _prior_scheduler is None:
        del sys.modules['scheduler']
    else:
        sys.modules['scheduler'] = _prior_scheduler
# v2 captured claim_name with a from-import: its own attribute needs the same
# resource-only naming bridge. Real candidate names still delegate unchanged.
v2.claim_name = adapter.owner_name
_ADAPTER_RUN = adapter.run


def resource_sources():
    return [Path(__file__).resolve(), Path(v2.__file__).resolve()]


def verify_resource_receipt(receipt):
    if receipt.get('receiptVersion') != 2:
        raise ValueError('operational driver requires receiptVersion 2')
    s.verify_sources(receipt['resourceSourceSha256'], resource_sources())
    for field, path in (('memoryPolicy', POLICY), ('memoryCounterDirection', COUNTER_DIRECTION)):
        if receipt[field]['path'] != str(path):
            raise ValueError('explicit superseding policy and counter direction are required')
        s.pinned(receipt[field])


class PolicyStore(v2.StoreV2):
    """Operational provenance/freshness checks around the unchanged v2 gate."""
    def __init__(self, root, *, clock=lambda: v2.timestamp(s.now())):
        super().__init__(root)
        self.clock = clock

    def check_resources(self, receipt, alive):
        verify_resource_receipt(receipt)
        imported_ref = receipt['pressureImport']
        if imported_ref['path'] != str(self.root/'pressure-import.json'):
            raise ValueError('pressure import must belong to this root')
        imported = s.record(imported_ref)
        if imported.get('kind') != v2.PRESSURE_IMPORT \
                or imported.get('snapshot') != receipt['pressureSnapshot'] \
                or type(imported.get('rows')) is not int \
                or not 1 <= imported['rows'] <= v2.MAX_IMPORT_ROWS:
            raise ValueError('matching completed pressure snapshot import is required')
        # Reuse v2's exact snapshot/parser/byte checks, but do not silently create
        # an import or restore a missing historical row. The parent must import
        # first. Existing rows are only verified by idempotent import_pressure.
        prefix = 'import-'+receipt['pressureSnapshot']['sha256'][:16]
        for number in range(1, imported['rows']+1):
            path = self.root/'pressure'/f'{prefix}-{number:06d}.json'
            if not path.is_file():
                raise FileNotFoundError(path)
        if self.import_pressure(receipt['pressureSnapshot']) != imported:
            raise ValueError('pressure import manifest changed')
        watcher = s.record(receipt['pressureWatcher'])
        if watcher.get('kind') != 'STROKE_PRESSURE_WATCH' \
                or watcher.get('schedulerRoot') != str(self.root) \
                or type(watcher.get('pid')) is not int or watcher['pid'] <= 0 \
                or watcher.get('intervalSeconds') != v2.WATCH_INTERVAL_SECONDS \
                or type(watcher.get('readings')) is not int \
                or not 1 <= watcher['readings'] <= v2.MAX_WATCH_READINGS \
                or watcher.get('schedulerSourceSha256') != receipt['resourceSourceSha256'][
                    str(Path(v2.__file__).resolve())]:
            raise ValueError('bounded 30-second watcher for this root and source is required')
        # The watcher publishes without this lock. Finish the history snapshot
        # before dating its validation, so a concurrent legitimate row cannot
        # appear future-dated merely because it arrived during collection.
        readings = self.pressure_readings()
        current = self.clock()
        started = v2.timestamp(watcher['startedUTC'])
        fresh = timedelta(seconds=2*v2.WATCH_INTERVAL_SECONDS)
        expires = started + timedelta(seconds=(watcher['readings']-1)*v2.WATCH_INTERVAL_SECONDS)
        if not alive(watcher['pid']) or current < started or current > expires+fresh:
            raise ValueError('declared pressure watcher is not active within its bounded interval')
        if any(v2.timestamp(row['sampledUTC']) > current for row in readings):
            raise ValueError('pressure history contains a future reading')
        watched = [row for row in readings if row.get('source') == 'watch'
                   and row.get('pid') == watcher['pid']
                   and v2.timestamp(row['sampledUTC']) >= started]
        if not watched or len(watched) > watcher['readings']:
            raise ValueError('declared pressure watcher has no bounded reading history')
        latest = max(watched, key=lambda row: v2.timestamp(row['sampledUTC']))
        if current-v2.timestamp(latest['sampledUTC']) > fresh:
            raise ValueError('pressure watcher reading is stale')
        return adapter.reference(self.root/'pressure'/(latest['id']+'.json'))

    def _admission(self, launch, pid, alive, memory, rss, *, own_claim=None):
        latest = self.check_resources(launch, alive)
        decision = super()._admission(launch, pid, alive, memory, rss, own_claim=own_claim)
        # The adapter persists this augmented decision in its existing gate
        # records; the terminal's lease also pins the full operational receipt.
        return dict(decision, **{key: launch[key] for key in (
            'resourceSourceSha256', 'memoryPolicy', 'memoryCounterDirection',
            'pressureSnapshot', 'pressureImport', 'pressureWatcher')}, watcherReading=latest)


def run(root, reference, *, proof_body, memory=v2.mac_memory_v2,
        clock=lambda: v2.timestamp(s.now()), **process_readings):
    receipt = s.record(reference)
    verify_resource_receipt(receipt)

    def checked_body(mode, out, admit):
        result = proof_body(mode, out, admit)
        # A changed operational source cannot acquire a successful terminal.
        # This is an integrity check, not another pressure/admission gate.
        verify_resource_receipt(receipt)
        return result

    return _ADAPTER_RUN(PolicyStore(root, clock=clock), reference, proof_body=checked_body,
                        memory=memory, **process_readings)



def preflight(root, reference, *, alive=s.alive, memory=v2.mac_memory_v2, rss=s.process_rss,
              clock=lambda: v2.timestamp(s.now())):
    """One observed gate, no lease or held reservation; never launches or retries."""
    store = PolicyStore(root, clock=clock)
    with store.locked():
        receipt = adapter.validate(store, reference)
        decision = adapter.resource_admission(store, receipt, os.getpid(), alive, memory, rss,
                                              prepared=False)
        return dict(decision, preflight=True, reservationHeld=False)


def main():
    # Keep the reviewed CLI's exact native import/call boundary. Substitute only
    # its run dispatch in this process, then call the ORIGINAL run function above
    # with StoreV2 and its memory sampler. No adapter source/function is rewritten.
    original = adapter.run
    adapter.run = lambda store, reference, **kwargs: run(store.root, reference, **kwargs)
    try:
        adapter.main()
    finally:
        adapter.run = original


if __name__ == '__main__':
    main()
