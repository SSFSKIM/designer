"""Bounded read-only RSS sampling of existing fits; never a lifetime-peak claim."""
import datetime
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
PIDS = (80101, 80133, 80167)
output = HERE/'rss-observation-1'
output.mkdir(exist_ok=False)
maximum = {}
with (output/'readings.jsonl').open('x') as stream:
    for index in range(120):
        stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        raw = subprocess.check_output(['ps', '-p', ','.join(map(str, PIDS)),
                                       '-o', 'pid=,rss=,etime=,command='], text=True)
        rows = []
        for line in raw.splitlines():
            pid, kib, elapsed, command = line.strip().split(None, 3)
            pid = int(pid)
            if pid not in PIDS or 'survivor_scope_runner.py' not in command:
                raise ValueError('PID is not the named stroke fit process')
            row = dict(pid=pid, residentRSSBytes=int(kib)*1024, psRSSKiB=int(kib),
                       elapsed=elapsed, sampledUTC=stamp, command=command)
            rows.append(row)
            if pid not in maximum or row['residentRSSBytes'] > maximum[pid]['residentRSSBytes']:
                maximum[pid] = row
        if {row['pid'] for row in rows} != set(PIDS):
            raise ValueError('a fit exited during the bounded RSS sample; preserve partial readings')
        stream.write(json.dumps(dict(index=index, readings=rows))+'\n')
        stream.flush()
        if index < 119:
            time.sleep(1)
samples = [dict(pid=pid, peakRSSBytes=row['residentRSSBytes'], sampledUTC=row['sampledUTC'],
                source='maximum of1201Hz psRSSKiB observations; KiB convertedby1024',
                qualification='sampled observed high-water, not process lifetime ru_maxrss')
           for pid, row in maximum.items()]
samples.append(dict(pid=61407, peakRSSBytes=895440*1024, sampledUTC=None,
    source='Earlier tool-result ps sample in this same session: PID61407 elapsed35:15 RSS895440KiB; '
           'that stoppedM0fit has no persisted ru_maxrss and no exact sampleUTC was recorded',
    qualification='single documented observedRSS; timestamp unavailable, not invented'))
record = dict(kind='STROKE_PEAK_RSS', largestObservedPeakRSSBytes=max(s['peakRSSBytes'] for s in samples),
    samples=samples, historicalLifetimeRSSPeakAvailable=False,
    metric='actualresidentRSS, sampledobservedhighwater; excludes physicalfootprint/non-fitpreparation peaks',
    operationalLimit='reservation estimate plus3GiBheadroom/pressuregate, not an absolute futureRSSbound')
with (output/'peak.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps(record), flush=True)
