"""Stroke scheduler memory policy v2: an additive source epoch over scheduler.py.

scheduler.py (v1) receipts, refusals and pinned proofs keep meaning what they meant.
This module reuses v1's claim, handoff, deferral, solver-marker and exact-once
machinery and its owner enumeration (process identity, not bare PIDs, since the W41
G1 PID-reuse fix) and replaces only the admission gate, for launch receipts that
carry receiptVersion 2:

  admit iff kern.memorystatus_vm_pressure_level == 1 now, the shared pressure log
  is not stopped, at most three fits run concurrently, and
  (free + max(inactive, purgeable) pages) * page size - remaining reservations
  >= 1 GiB. The counter is the parent's correction of the ruled free + inactive +
  purgeable sum (../scheduler-memory-counter-clarification.json): purgeable pages
  can also sit on the inactive queue, and the maximum does not credit them twice.
  It is a reclaimable-headroom heuristic, not a free-memory guarantee.

A WARNING, CRITICAL or unreadable reading stops NEW admissions (running fits are
never touched); admissions resume only after five consecutive NORMAL readings at
least 30 s apart. `watch` is a bounded, explicit pressure logger that never takes
the allocation lock. See policy-v2-interface.txt.
"""
import argparse
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

import scheduler as v1
from scheduler import Deferred, RSS_OBSERVATION, claim_name, filename, immutable, now, record

RECEIPT_VERSION = 2
MAX_CONCURRENT_FITS = 3
FLOOR_BYTES = v1.GIB
WATCH_INTERVAL_SECONDS = 30
RESUME_NORMAL_READINGS = 5
MAX_WATCH_READINGS = 2880
PRESSURE_READING = 'STROKE_PRESSURE_READING'
PRESSURE_IMPORT = 'STROKE_PRESSURE_IMPORT'
MAX_IMPORT_ROWS = 100000
COUNTER = 'free + max(inactive, purgeable)'
COUNTER_EPOCH = 'policy-v2 counter correction: max, not the superseded inactive + purgeable sum'
MEMORY_METRIC_V2 = ('macOS (vm_stat Pages free + max(Pages inactive, Pages purgeable)) * page '
                    'size; reclaimable-headroom heuristic, not a free-memory guarantee')


def parse_memory_v2(vm_stat, pressure):
    page = int(re.search(r'page size of (\d+) bytes', vm_stat)[1])
    pages = {name: int(re.search(rf'^Pages {name}:\s+(\d+)\.', vm_stat, re.M)[1])
             for name in ('free', 'inactive', 'purgeable')}
    counted = pages['free'] + max(pages['inactive'], pages['purgeable'])
    return {'availableBytes': page * counted, 'pressureLevel': int(pressure.strip()),
            'pageSizeBytes': page, 'freePages': pages['free'],
            'inactivePages': pages['inactive'], 'purgeablePages': pages['purgeable'],
            'countedPages': counted, 'counter': COUNTER, 'counterEpoch': COUNTER_EPOCH,
            'metric': MEMORY_METRIC_V2, 'sampledUTC': now()}


def mac_memory_v2():
    return parse_memory_v2(subprocess.check_output(['/usr/bin/vm_stat'], text=True),
        subprocess.check_output(['/usr/sbin/sysctl', '-n',
                                 'kern.memorystatus_vm_pressure_level'], text=True))


def read_pressure():
    raw = subprocess.check_output(['/usr/sbin/sysctl', '-n',
                                   'kern.memorystatus_vm_pressure_level'], text=True)
    return int(raw.strip())


def timestamp(value):
    moment = datetime.fromisoformat(value)
    if moment.tzinfo is None:
        raise ValueError('pressure reading time requires a timezone')
    return moment


def pressure_state(readings):
    """Admission state implied by every logged pressure reading, in time order.

    Any non-NORMAL or unreadable reading stops admissions. While stopped, a NORMAL
    reading counts toward resumption only if it is at least 30 s after the last
    counted one, so several workers reading within one interval count once.
    """
    stopped, counted, last, abnormal = False, 0, None, None
    for reading in sorted(readings, key=lambda r: (timestamp(r['sampledUTC']), r['id'])):
        moment = timestamp(reading['sampledUTC'])
        if reading['pressureLevel'] != 1:
            stopped, counted, last, abnormal = True, 0, None, reading['sampledUTC']
        elif stopped and (last is None
                          or moment - last >= timedelta(seconds=WATCH_INTERVAL_SECONDS)):
            counted, last = counted + 1, moment
            if counted >= RESUME_NORMAL_READINGS:
                stopped, counted, last = False, 0, None
    return {'admissionsOpen': not stopped, 'spacedNormalReadings': counted,
            'requiredNormalReadings': RESUME_NORMAL_READINGS,
            'lastAbnormalUTC': abnormal, 'readings': len(readings)}


class StoreV2(v1.Store):
    """v1 Store with the policy-v2 admission gate; every other method is v1's."""

    def claim(self, reference, *, pid, alive=v1.alive, memory=mac_memory_v2, rss=None):
        return super().claim(reference, pid=pid, alive=alive, memory=memory, rss=rss)

    def check_before_fit(self, claim, *, alive=v1.alive, memory=mac_memory_v2, rss=None):
        return super().check_before_fit(claim, alive=alive, memory=memory, rss=rss)

    def finish(self, claim, result):
        # v1.run pins scheduler.py; the result also names the policy that admitted it.
        result = dict(result, policyVersion=RECEIPT_VERSION, policyCounter=COUNTER,
                      counterEpoch=COUNTER_EPOCH, policySourceSha256={
            str(Path(__file__).resolve()): hashlib.sha256(
                Path(__file__).read_bytes()).hexdigest()})
        return super().finish(claim, result)

    def log_pressure(self, level, *, sampled=None, error=None, source):
        """Publish one immutable pressure reading WITHOUT the allocation lock.

        Uniquely named no-overwrite files need no lock, so a watcher never waits
        behind a verification or fit that holds the allocation lock for hours.
        """
        if level is not None and type(level) is not int:
            raise ValueError('pressure level must be an integer or unreadable')
        folder = self.root / 'pressure'
        folder.mkdir(exist_ok=True)
        name = uuid.uuid4().hex
        value = {'kind': PRESSURE_READING, 'id': name, 'sampledUTC': sampled or now(),
                 'pressureLevel': level, 'error': error, 'source': source, 'pid': os.getpid(),
                 'sysctl': 'kern.memorystatus_vm_pressure_level'}
        timestamp(value['sampledUTC'])
        immutable(folder / f'{name}.json', value)
        return value

    def import_pressure(self, reference):
        """Import one completed, hash-pinned manual pressure JSONL snapshot, once.

        Every row keeps its original sampledUTC and pressureLevel (and periodic flag,
        raw sysctl text and line reference); nothing is resampled and no NORMAL
        reading is added. The whole snapshot is validated before anything is
        written. One snapshot per root: re-importing the same bytes only verifies
        the records already published; a different snapshot fails closed.
        """
        raw = v1.pinned(reference)
        text = raw.decode()
        if not text.endswith('\n'):
            raise ValueError('pressure snapshot must be complete: final line unterminated')
        lines = text[:-1].split('\n')
        if not 1 <= len(lines) <= MAX_IMPORT_ROWS:
            raise ValueError(f'pressure snapshot must hold 1..{MAX_IMPORT_ROWS} rows')
        records = []
        for number, line in enumerate(lines, 1):
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f'malformed pressure snapshot row {number}')
            level = row['pressureLevel']
            if (level is not None and type(level) is not int) \
                    or type(row['periodic']) is not bool or type(row['rawSysctl']) is not str:
                raise ValueError(f'malformed pressure snapshot row {number}')
            timestamp(row['sampledUTC'])
            name = f"import-{reference['sha256'][:16]}-{number:06d}"
            records.append({
                'kind': PRESSURE_READING, 'id': name, 'sampledUTC': row['sampledUTC'],
                'pressureLevel': level,
                'error': None if level is not None else row['rawSysctl'],
                'source': 'manual-import', 'pid': None,
                'sysctl': 'kern.memorystatus_vm_pressure_level',
                'imported': {'snapshot': reference, 'line': number,
                             'periodic': row['periodic'], 'rawSysctl': row['rawSysctl']}})
        folder = self.root / 'pressure'
        folder.mkdir(exist_ok=True)
        manifest = {'kind': PRESSURE_IMPORT, 'snapshot': reference, 'rows': len(records)}
        try:
            immutable(self.root / 'pressure-import.json', manifest)
        except FileExistsError:
            if json.loads((self.root / 'pressure-import.json').read_text()) != manifest:
                raise ValueError('a different pressure snapshot was already imported')
        expected = {}
        for value in records:
            path = folder / f"{value['id']}.json"
            expected[path] = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
            try:
                immutable(path, value)
            except FileExistsError:
                pass
        for path, raw in expected.items():
            if path.read_bytes() != raw:
                raise ValueError('imported pressure record changed: ' + path.name)
        return manifest

    def pressure_readings(self):
        readings = []
        for path in sorted((self.root / 'pressure').glob('*.json')):
            reading = json.loads(path.read_text())
            if reading['kind'] != PRESSURE_READING or path.name != reading['id'] + '.json' \
                    or (reading['pressureLevel'] is not None
                        and type(reading['pressureLevel']) is not int):
                raise ValueError('malformed pressure reading')
            readings.append(reading)
        return readings

    def _admission(self, launch, pid, alive, memory, rss, *, own_claim=None):
        if launch.get('receiptVersion') != RECEIPT_VERSION:
            raise ValueError('policy-v2 admission requires receiptVersion 2; v1 receipts use v1')
        roster_ref, roster = self.roster()
        release = self.release(launch['captureRelease'])
        cap = launch['maxConcurrency']
        if type(cap) is not int or not 1 <= cap <= release['maxConcurrency']:
            raise ValueError('concurrency cap exceeds explicit capture release authority')
        if cap > MAX_CONCURRENT_FITS:
            raise ValueError('policy v2 admits at most three concurrent fits')
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
        # v1's shared enumeration: registered handoffs retire old owners, and a
        # claim reserves only while its PID still holds the recorded claimant.
        processes, excluded, claim_peaks = self.reservations(roster_ref, roster, launch, alive,
                                                             own_claim)
        # Every valid RSS reading any earlier admission took (refused, failed or
        # pre-fit included) stays in the high-water: a fit whose RSS later falls
        # can regrow to what it was already seen to hold.
        historical_peaks = [measured] + self.observed_rss() + claim_peaks
        for path in sorted((self.root / 'results').glob('*.json')):
            result = json.loads(path.read_text())
            historical_peaks.append(result['peakRSSBytes'])
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
        state = pressure_state(self.pressure_readings())
        decision = {'sampledUTC': now(), 'policyVersion': RECEIPT_VERSION,
                    'policyCounter': COUNTER, 'counterEpoch': COUNTER_EPOCH, 'memory': reading,
                    'pressureState': state, 'processes': processes,
                    'excludedProcesses': excluded,
                    'effectiveConcurrency': len(processes) + 1, 'maxConcurrency': cap,
                    'reservedBytes': reserved, 'ownRSSBytes': own_rss,
                    'observedPeakBytes': observed_peak,
                    'prospectivePeakBytes': prospective_peak, 'peakEvidence': launch['peakEvidence'],
                    'requiredAvailableBytes': FLOOR_BYTES + reserved}
        if reading['metric'] != MEMORY_METRIC_V2 or reading['pressureLevel'] != 1 \
                or not state['admissionsOpen'] \
                or reading['availableBytes'] < decision['requiredAvailableBytes'] \
                or decision['effectiveConcurrency'] > cap:
            decision['admitted'] = False
            immutable(self.root / 'admissions' / f'{uuid.uuid4().hex}.json', decision)
            refusal = Deferred(json.dumps(decision, sort_keys=True))
            refusal.decision = decision
            raise refusal
        decision['admitted'] = True
        immutable(self.root / 'admissions' / f'{uuid.uuid4().hex}.json', decision)
        return decision


def watch(store, readings, *, interval=WATCH_INTERVAL_SECONDS, sample=read_pressure,
          sleep=time.sleep, report=print):
    """Take a bounded number of pressure readings; never admits, launches or stops."""
    if type(readings) is not int or not 1 <= readings <= MAX_WATCH_READINGS:
        raise ValueError(f'watch takes 1..{MAX_WATCH_READINGS} readings')
    if not (store.root / 'roster.json').exists():
        raise ValueError('watch requires an initialized scheduler root')
    for n in range(readings):
        if n:
            sleep(interval)
        try:
            level, error = sample(), None
            if type(level) is not int:
                level, error = None, 'unparseable pressure level'
        except Exception as caught:
            level, error = None, repr(caught)
        reading = store.log_pressure(level, error=error, source='watch')
        report(json.dumps({'reading': reading,
                           'state': pressure_state(store.pressure_readings())}))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=('init', 'transfer', 'run', 'watch',
                                            'import-pressure'))
    parser.add_argument('--root', required=True)
    parser.add_argument('--receipt', help='Absolute parent-authored receipt path (not watch)')
    parser.add_argument('--sha256', help='Explicit expected receipt SHA-256 (not watch)')
    parser.add_argument('--readings', type=int, help='watch only: readings, 30 s apart')
    args = parser.parse_args()
    store = StoreV2(args.root)
    if args.command == 'watch':
        if args.receipt or args.sha256 or args.readings is None:
            parser.error('watch takes --root and --readings only')
        watch(store, args.readings)
        return
    if not args.receipt or not args.sha256 or args.readings is not None:
        parser.error(f'{args.command} takes --root, --receipt and --sha256')
    reference = {'path': args.receipt, 'sha256': args.sha256}
    if args.command == 'init':
        store.initialize(reference)
    elif args.command == 'import-pressure':
        print(json.dumps(store.import_pressure(reference)))
    elif args.command == 'transfer':
        print(json.dumps(store.transfer(reference)))
    else:
        v1.run(store, reference)


if __name__ == '__main__':
    main()
