"""Parent-authorized first-proof admission under the superseding memory policy.

The reviewed adapter/proof/scheduler sources are unchanged. This manual bridge
replaces only the adapter's resource-admission callable in this process. It is
restricted to one unwrapped verification, with no other live registered fit.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import uuid

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE/'verification-slot'))
import verification_slot as v
s = v.s
ROOT = HERE/'scheduler-run-1'
PRESSURE_LOG = ROOT/'manual-policy-v2-pressure.jsonl'
POLICY = HERE/'scheduler-memory-parent-direction-v2.json'
state_lock = threading.Lock()
stop = threading.Event()
state = dict(blocked=False, normalStreak=0, lastPeriodic=0.)


def pressure_read(periodic=False):
    with state_lock:
        try:
            raw = subprocess.check_output(['/usr/sbin/sysctl', '-n',
                'kern.memorystatus_vm_pressure_level'], text=True)
            level = int(raw.strip())
        except Exception as error:
            raw = repr(error); level = None
        if level != 1:
            state['blocked'] = True; state['normalStreak'] = 0
        elif periodic and state['blocked']:
            state['normalStreak'] += 1
            if state['normalStreak'] >= 5:
                state['blocked'] = False
        if periodic:
            state['lastPeriodic'] = time.monotonic()
        row = dict(sampledUTC=s.now(), pressureLevel=level, rawSysctl=raw,
            periodic=periodic, blocked=state['blocked'], normalStreak=state['normalStreak'],
            policy='parent-v2; no process is killed on pressure changes')
        with PRESSURE_LOG.open('a') as stream:
            stream.write(json.dumps(row)+'\n'); stream.flush()
        return row


def watch():
    while not stop.wait(30):
        pressure_read(periodic=True)


def manual_admission(store, receipt, pid, alive, memory, rss, *, prepared):
    if receipt['mode'] != 'unwrapped' or receipt['maxConcurrency'] != 3:
        raise ValueError('this manual authorization is for one unwrapped proof, cap3')
    s.pinned(receipt['memoryPolicy'])
    if receipt['memoryPolicy']['path'] != str(POLICY):
        raise ValueError('superseding parent policy must be named explicitly')
    _, roster = store.roster()
    live = [owner['pid'] for owner in roster['oldOwners'] if alive(owner['pid'])]
    for path in (store.root/'claims').glob('*.json'):
        owner = json.loads(path.read_text())
        if alive(owner['pid']):
            live.append(owner['pid'])
    if live:
        raise ValueError('manual first-proof scope requires no other live registered fit')
    own_rss = rss(pid) if prepared else 0
    peak_record = s.record(receipt['peakEvidence'])
    peak = max([peak_record['largestObservedPeakRSSBytes'], own_rss,
                receipt['reservationBytes'], *store.observed_rss()])
    if prepared:
        s.immutable(store.root/'admissions'/f'rss-manual-v2-{uuid.uuid4().hex}.json',
            dict(kind=s.RSS_OBSERVATION, sampledUTC=s.now(), source='manual-v2 live RSS',
                 samples=[dict(pid=pid, owner='verification-unwrapped', rssBytes=own_rss)]))
    raw = subprocess.check_output(['/usr/bin/vm_stat'], text=True)
    page = int(re.search(r'page size of (\d+) bytes', raw)[1])
    counts = {name: int(re.search(r'^Pages '+name+r':\s+(\d+)\.', raw, re.M)[1])
              for name in ('free', 'inactive', 'purgeable')}
    pressure = pressure_read()
    available = page*sum(counts.values())
    reserved = max(0, peak-own_rss)
    decision = dict(sampledUTC=s.now(), policyRevision=2, memoryPolicy=receipt['memoryPolicy'],
        metric='(free+inactive+purgeable pages)*page size; parent-v2 estimate',
        rawVmStat=raw, pageSizeBytes=page, pages=counts, availableBytes=available,
        pressure=pressure, ownRSSBytes=own_rss, observedPeakBytes=peak,
        reservedBytes=reserved, floorBytes=1024**3, effectiveConcurrency=1,
        maxConcurrency=3, resource='one unwrapped verification, not a candidate',
        prepared=prepared)
    decision['admitted'] = pressure['pressureLevel'] == 1 and not pressure['blocked'] \
        and available-reserved >= 1024**3
    s.immutable(store.root/'admissions'/f'manual-v2-{uuid.uuid4().hex}.json', decision)
    if not decision['admitted']:
        error = s.Deferred(json.dumps(decision)); error.decision = decision
        raise error
    return decision


if __name__ == '__main__':
    # A fresh NORMAL reading allows initial admission. Once any warning/error is
    # observed, only five periodic30s NORMAL readings reopen admission.
    pressure_read(periodic=True)
    observer = threading.Thread(target=watch, daemon=True)
    observer.start()
    v.resource_admission = manual_admission
    try:
        v.main()
    finally:
        stop.set(); observer.join()
