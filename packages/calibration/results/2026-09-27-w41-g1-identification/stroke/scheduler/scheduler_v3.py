"""Stroke scheduler adaptive resource policy: an additive source epoch over v1 and v2.

scheduler.py (v1) and scheduler_v2.py (v2) are unchanged. This module reuses their
claim, handoff, RSS high-water, NO-FIT deferral, solver-marker, exact-once, pressure
log, snapshot import and watcher machinery, and replaces only the admission gate.
Every admission first evaluates v2's normal gate; if it does not clear, the same
admission is evaluated against the degraded gate. The choice is made afresh each
time, so it is reversible in both directions and nothing running is touched.

  normal:   pressure 1 now, five consecutive NORMAL readings >= 30 s apart since the
            last non-NORMAL one, counter - reservations >= 1 GiB, <= 3 fits.
  degraded: pressure 1 or 2 (never 4 or unreadable), counter >= reservations (no
            floor), >= 20 GiB free disk, and this is the ONLY live fit.

The counter is v2's free + max(inactive, purgeable), a reclaimable-headroom
heuristic, not a free-memory guarantee. See policy-v3-interface.txt.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import uuid

import scheduler as v1
import scheduler_v2 as v2
from scheduler import Deferred, RSS_OBSERVATION, claim_name, filename, immutable, now, record
from scheduler_v2 import (COUNTER, COUNTER_EPOCH, FLOOR_BYTES, MAX_CONCURRENT_FITS,
                          MEMORY_METRIC_V2, pressure_state)

POLICY_VERSION = 3
RESOURCE_POLICY = 'stroke-adaptive-v3'
DEGRADED_CAP = 1
DEGRADED_PRESSURE_LEVELS = (1, 2)
DISK_FLOOR_BYTES = 20 * v1.GIB
VM_VOLUME = Path('/System/Volumes/VM')


def spaced_normal_run(readings):
    """Trailing run of consecutive NORMAL readings, each >= 30 s after the last counted.

    Unlike v2's pressure_state, which starts open with no history, this proves the
    readings: an empty or short history counts what is there and no more. Any
    non-NORMAL or unreadable reading resets the run; a NORMAL reading inside 30 s of
    the previous counted one extends nothing, so duplicate readings cannot accelerate.
    """
    run, last = 0, None
    for reading in sorted(readings, key=lambda r: (v2.timestamp(r['sampledUTC']), r['id'])):
        moment = v2.timestamp(reading['sampledUTC'])
        if reading['pressureLevel'] != 1:
            run, last = 0, None
        elif last is None or (moment - last).total_seconds() >= v2.WATCH_INTERVAL_SECONDS:
            run, last = run + 1, moment
    return run


def check_direction(direction):
    """The pinned parent direction must state exactly the numbers this code enforces."""
    normal, degraded = direction.get('normal'), direction.get('degraded')
    if direction.get('kind') != 'STROKE_ADAPTIVE_MEMORY_DIRECTION' \
            or direction.get('counter') != COUNTER or normal != {
                'pressureLevels': [1], 'spacedNormalReadings': v2.RESUME_NORMAL_READINGS,
                'intervalSeconds': v2.WATCH_INTERVAL_SECONDS, 'floorBytes': FLOOR_BYTES,
                'maxConcurrency': MAX_CONCURRENT_FITS} or degraded != {
                'pressureLevels': list(DEGRADED_PRESSURE_LEVELS), 'floorBytes': 0,
                'maxConcurrency': DEGRADED_CAP, 'diskFreeMinimumBytes': DISK_FLOOR_BYTES}:
        raise ValueError('resource direction does not state the adaptive policy this code enforces')


def disk_free(paths):
    """Free bytes on each volume (statvfs via shutil); the gate uses the minimum."""
    volumes = {str(path): shutil.disk_usage(path).free for path in paths}
    return {'freeBytes': min(volumes.values()), 'volumes': volumes, 'sampledUTC': now(),
            'source': 'shutil.disk_usage free bytes (statvfs)'}


def swap_usage():
    """Raw vm.swapusage, recorded as evidence only; a failed read does not gate."""
    try:
        raw = subprocess.check_output(['/usr/sbin/sysctl', '-n', 'vm.swapusage'], text=True)
        return {'raw': raw, 'sampledUTC': now()}
    except Exception as error:
        return {'error': repr(error), 'sampledUTC': now()}


class StoreV3(v2.StoreV2):
    """v2 Store whose admission gate is the adaptive normal/degraded policy."""

    def __init__(self, root, *, disk=None, swap=swap_usage):
        super().__init__(root)
        # The scheduler root's volume and the swap volume; on APFS both report the
        # shared container, and the minimum is taken either way.
        self.read_disk = disk or (lambda: disk_free(
            [self.root] + ([VM_VOLUME] if VM_VOLUME.exists() else [])))
        self.read_swap = swap

    def finish(self, claim, result):
        # Bypass v2's finish, which would label the result policyVersion 2.
        admitted = self.root / 'admissions' / claim_name(claim)
        mode = json.loads(admitted.read_text()).get('resourceMode') if admitted.exists() else None
        sources = {str(Path(path).resolve()): hashlib.sha256(Path(path).read_bytes()).hexdigest()
                   for path in (v2.__file__, __file__)}
        result = dict(result, policyVersion=POLICY_VERSION, resourcePolicy=RESOURCE_POLICY,
                      admissionMode=mode, policyCounter=COUNTER, counterEpoch=COUNTER_EPOCH,
                      policySourceSha256=sources)
        return v1.Store.finish(self, claim, result)

    def _admission(self, launch, pid, alive, memory, rss, *, own_claim=None):
        # receiptVersion 3 selects this policy; StoreV2 refuses it, so a v3 receipt is
        # never admitted under the v2 gate, and a v2 receipt never reaches this one.
        if launch.get('receiptVersion') != POLICY_VERSION:
            raise ValueError('adaptive admission requires receiptVersion 3')
        selector = launch['adaptiveMemoryPolicy']
        check_direction(record(selector))
        _, roster = self.roster()
        release = self.release(launch['captureRelease'])
        cap = launch['maxConcurrency']
        if type(cap) is not int or not 1 <= cap <= release['maxConcurrency']:
            raise ValueError('concurrency cap exceeds explicit capture release authority')
        if cap > MAX_CONCURRENT_FITS:
            raise ValueError('the adaptive policy admits at most three concurrent fits')
        peak = record(launch['peakEvidence'])
        measured = peak['largestObservedPeakRSSBytes']
        if peak['kind'] != 'STROKE_PEAK_RSS' or type(measured) is not int or measured <= 0 \
                or not peak['samples'] or measured != max(s['peakRSSBytes'] for s in peak['samples']):
            raise ValueError('measured wave fit peak RSS evidence required')
        for sample in peak['samples']:
            if type(sample['peakRSSBytes']) is not int or sample['peakRSSBytes'] <= 0 \
                    or not sample['source'] or not sample['sampledUTC'] or sample['pid'] <= 0:
                raise ValueError('peak evidence must identify its measurements')
        for evidence in peak.get('evidence', []):
            v1.pinned(evidence)
        for key in ('reservationBytes', 'oldWorkerReservationBytes'):
            if type(launch[key]) is not int or launch[key] < measured:
                raise ValueError('reservation is below measured wave peak RSS')
        processes = []
        for owner in roster['oldOwners']:
            if alive(owner['pid']):
                processes.append({'pid': owner['pid'], 'owner': f"old-{owner['partition']}",
                                  'peakBytes': launch['oldWorkerReservationBytes']})
        # Every valid RSS reading any earlier admission took (refused, failed or
        # pre-fit included) stays in the high-water: a fit whose RSS later falls
        # can regrow to what it was already seen to hold.
        historical_peaks = [measured] + self.observed_rss()
        for path in sorted((self.root / 'results').glob('*.json')):
            result = json.loads(path.read_text())
            historical_peaks.append(result['peakRSSBytes'])
        for path in sorted((self.root / 'claims').glob('*.json')):
            claim = json.loads(path.read_text())
            historical_peaks.append(claim['prospectivePeakBytes'])
            if own_claim is not None and claim_name(claim) == claim_name(own_claim):
                continue
            if alive(claim['pid']):
                processes.append({'pid': claim['pid'], 'owner': filename(claim['task']),
                                  'peakBytes': claim['reservationBytes']})
        if pid in [p['pid'] for p in processes] or len({p['pid'] for p in processes}) != len(processes):
            raise ValueError('one process cannot own multiple simultaneous slots')
        # Before the fit, preparation's own RSS is already resident; reserve only
        # its remaining peak. At the initial claim reserve the entire new peak.
        own = {'pid': pid, 'owner': claim_name(own_claim) if own_claim else filename(launch['task'])}
        sampled = processes + ([own] if own_claim is not None else [])
        readings = []
        try:
            for process in sampled:
                process['rssBytes'] = rss(process['pid']) if rss else 0
                if type(process['rssBytes']) is not int or process['rssBytes'] < 0:
                    raise ValueError('invalid process RSS reading')
                if rss:
                    readings.append({key: process[key] for key in ('pid', 'owner', 'rssBytes')})
        finally:
            # Published before the memory read and before any refusal, still under
            # the allocation lock, so a later failure cannot forget a valid reading.
            if readings:
                immutable(self.root / 'admissions' / f'rss-{uuid.uuid4().hex}.json',
                          {'kind': RSS_OBSERVATION, 'sampledUTC': now(), 'task': launch['task'],
                           'source': '/bin/ps -o rss= KiB * 1024', 'samples': readings})
        own_rss = own.get('rssBytes', 0)
        observed_peak = max(historical_peaks + [p['rssBytes'] for p in sampled])
        for process in processes:
            process['peakBytes'] = max(process['peakBytes'], observed_peak)
            process['remainingBytes'] = max(0, process['peakBytes'] - process['rssBytes'])
        prospective_peak = max(launch['reservationBytes'], observed_peak)
        reserved = sum(p['remainingBytes'] for p in processes) + max(0, prospective_peak - own_rss)
        try:
            reading = memory()
        except Exception as error:
            # An unreadable reading is an abnormal pressure reading: it stops new
            # admissions until five spaced NORMAL readings, and still fails closed.
            self.log_pressure(None, error=repr(error), source='admission')
            raise
        level = reading.get('pressureLevel')
        self.log_pressure(level if type(level) is int else None,
                          sampled=reading.get('sampledUTC'), source='admission',
                          error=None if type(level) is int else 'unparseable pressure level')
        readings = self.pressure_readings()
        state = pressure_state(readings)  # v2's view, recorded as history only
        normal_run = spaced_normal_run(readings)
        # A shared watcher can publish between this admission's sample and the read
        # above. Both gates use the FRESHEST logged reading (this one included), so a
        # newer CRITICAL or unreadable row is never ignored for an older sample.
        freshest = max(readings, key=lambda r: (v2.timestamp(r['sampledUTC']), r['id']))
        level = freshest['pressureLevel']
        # Disk is reported in both modes but gates only the degraded one; swap is
        # evidence only. An unreadable disk fails a degraded admission closed below.
        try:
            disk = self.read_disk()
            if type(disk['freeBytes']) is not int or disk['freeBytes'] < 0:
                raise ValueError('invalid disk free reading')
        except Exception as error:
            disk = {'error': repr(error), 'sampledUTC': now()}
        swap = self.read_swap()
        effective = len(processes) + 1
        available = reading['availableBytes']
        metric = reading['metric'] == MEMORY_METRIC_V2
        # Every admission evaluates the normal gate first (reversible both ways).
        normal_gate = {'pressureNormal': level == 1,
                       'fiveSpacedNormal': normal_run >= v2.RESUME_NORMAL_READINGS,
                       'floorClears': available >= FLOOR_BYTES + reserved}
        if metric and all(normal_gate.values()):
            mode, limit, required = 'normal', cap, FLOOR_BYTES + reserved
            admitted = effective <= cap
            expectation = 'normal gate: 1 GiB headroom floor kept after reservations'
        else:
            if 'error' in disk:
                raise ValueError('degraded admission requires a readable disk: ' + disk['error'])
            mode, limit, required = 'degraded', DEGRADED_CAP, reserved
            admitted = metric and level in DEGRADED_PRESSURE_LEVELS \
                and available >= reserved and disk['freeBytes'] >= DISK_FLOOR_BYTES \
                and effective <= DEGRADED_CAP
            expectation = ('degraded gate: no headroom floor, one fit at a time; paging to '
                           'swap is expected and accepted, bounded by the 20 GiB disk floor')
        decision = {'sampledUTC': now(), 'policyVersion': POLICY_VERSION,
                    'resourcePolicy': RESOURCE_POLICY, 'adaptiveMemoryPolicy': selector,
                    'resourceMode': mode, 'normalGate': normal_gate,
                    'policyCounter': COUNTER, 'counterEpoch': COUNTER_EPOCH, 'memory': reading,
                    'pressureState': state, 'spacedNormalRun': normal_run,
                    'freshestPressure': {key: freshest[key] for key in
                                         ('id', 'sampledUTC', 'pressureLevel', 'source')},
                    'disk': disk, 'diskFreeBytes': disk.get('freeBytes'),
                    'diskFloorBytes': DISK_FLOOR_BYTES,
                    'swap': swap, 'swapExpectation': expectation, 'processes': processes,
                    'effectiveConcurrency': effective, 'maxConcurrency': cap,
                    'modeConcurrencyLimit': limit,
                    'reservedBytes': reserved, 'ownRSSBytes': own_rss,
                    'observedPeakBytes': observed_peak,
                    'prospectivePeakBytes': prospective_peak, 'peakEvidence': launch['peakEvidence'],
                    'requiredAvailableBytes': required,
                    'headroomAfterReservationBytes': available - reserved}
        if not admitted:
            decision['admitted'] = False
            immutable(self.root / 'admissions' / f'{uuid.uuid4().hex}.json', decision)
            refusal = Deferred(json.dumps(decision, sort_keys=True))
            refusal.decision = decision
            raise refusal
        decision['admitted'] = True
        immutable(self.root / 'admissions' / f'{uuid.uuid4().hex}.json', decision)
        return decision


def main():
    raise SystemExit('scheduler_v3 is a library for a reviewed driver; it has no CLI. Use '
                     'scheduler_v2.py watch/import-pressure for pressure history.')


if __name__ == '__main__':
    main()
