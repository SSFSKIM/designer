#!/usr/bin/env python3.12
"""b7's pre-sitting dumps, distilled: per launch the dumpcheck verdict, the measured rate against
the timeout, the machine load during the launch and the foreign-process census.

Usage: summarize.py <rehearsal root> [<rehearsal root> ...] --load <samples> [--load <samples>]
       --out-dir <this directory>

Each root is an orchestrator rehearsal root (`REHEARSAL=1 STOP_AFTER=dumps`). Per launch it
copies the small records (check.json, rehearsal.json, timing.json, attest.read, attest.close)
into <out-dir>/<root name>/<launch>/, the orchestrator's small logs and the load samples into
<out-dir>/logs/, hashes every file of the run and the root's logs (the dump JSONs, the full
machine reads and the display listings stay in scratch) into scratch-sha256.txt, and writes
b7.json and b7.txt. The load average is sampled OUTSIDE the driver (every 15 s, `sysctl
vm.loadavg`); a launch's load is every sample between its opening and closing machine reads,
and the samples' coverage of that window is stated beside it.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import statistics

KEEP = ('check.json', 'rehearsal.json', 'timing.json', 'attest.read', 'attest.close')


def when(text):
    return datetime.datetime.fromisoformat(text.replace('Z', '+00:00')).timestamp()


def portable(path):
    return dict(line.split('=', 1) for line in path.read_text().splitlines() if '=' in line)


def samples(paths):
    out = []
    for path in paths:
        for line in Path(path).read_text().splitlines():
            m = re.match(r'(\S+) \{ ([\d.]+) ([\d.]+) ([\d.]+) \}', line)
            if m:
                out.append((when(m[1]), float(m[2]), float(m[3]), float(m[4])))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('roots', nargs='+', type=Path)
    ap.add_argument('--load', action='append', default=[], type=Path)
    ap.add_argument('--out-dir', type=Path, required=True)
    args = ap.parse_args()
    load = samples(args.load)
    rows, hashes = [], []
    logs = args.out_dir / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    for path in args.load:
        shutil.copy2(path, logs / path.name)
    for root in args.roots:
        for f in sorted(p for p in (root / 'logs').iterdir() if p.is_file()):
            hashes.append(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {root.name}/logs/{f.name}')
            if f.name in ('orchestrator-status.txt', 'pin-check.json', 'mode-switch-idle.txt') or \
                    f.name.endswith('-driver.txt'):
                shutil.copy2(f, logs / f.name)
        for passdir in sorted(p for p in root.iterdir() if p.name.startswith('rehearsal-dump-')):
            for run in sorted(q for q in passdir.iterdir() if q.is_dir()):
                dest = args.out_dir / root.name / passdir.name / run.name
                dest.mkdir(parents=True, exist_ok=True)
                for name in KEEP:
                    if (run / name).exists():
                        shutil.copy2(run / name, dest / name)
                for f in sorted(p for p in run.rglob('*') if p.is_file()):
                    hashes.append(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  '
                                  f'{root.name}/{passdir.name}/{run.name}/{f.relative_to(run)}')
                opened, closed = portable(run / 'attest.read'), (portable(run / 'attest.close')
                                                                  if (run / 'attest.close').exists() else {})
                t0 = when(opened['readAt'])
                t1 = when(closed['readAt']) if closed else None
                window = [s for s in load if t0 <= s[0] <= (t1 or t0)]
                rec = json.loads((run / 'rehearsal.json').read_text()) if (run / 'rehearsal.json').exists() else {}
                timing = json.loads((run / 'timing.json').read_text()) if (run / 'timing.json').exists() else {}
                refusal = (run / 'refusal.txt').read_text().strip() if (run / 'refusal.txt').exists() else None
                rows.append(dict(
                    root=root.name, launch=passdir.name, run=run.name, openedAt=opened['readAt'],
                    closedAt=closed.get('readAt'), mode=opened.get('displayplacerMode'),
                    outcome=rec.get('outcome') or ('REFUSED: ' + refusal if refusal else 'incomplete'),
                    scenes=timing.get('scenes'), elapsedSeconds=timing.get('elapsedSeconds'),
                    perSceneSeconds=timing.get('perSceneSeconds'), timeoutSeconds=timing.get('timeoutSeconds'),
                    marginSeconds=(round(timing['timeoutSeconds'] - timing['elapsedSeconds'], 1)
                                   if timing.get('elapsedSeconds') is not None else None),
                    departures=rec.get('departures'), unpredicted=rec.get('unpredicted'),
                    load1=dict(samples=len(window),
                               coverage=[datetime.datetime.fromtimestamp(window[i][0], datetime.timezone.utc)
                                         .strftime('%H:%M:%SZ') for i in (0, -1)] if window else None,
                               min=min((s[1] for s in window), default=None),
                               median=statistics.median([s[1] for s in window]) if window else None,
                               max=max((s[1] for s in window), default=None)),
                    census=rec.get('foreignCensus'),
                    predeclaration=opened.get('predeclaration'), scenesSha256=opened.get('scenesSha256'),
                    splitSha256=opened.get('splitSha256')))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / 'scratch-sha256.txt').write_text('\n'.join(hashes) + '\n')
    (args.out_dir / 'b7.json').write_text(json.dumps(rows, indent=1) + '\n')
    lines = ['b7: dump-layers over one full 2x endpoint (the largest pass) and the four 1x endpoints, before the',
             'sitting, through the orchestrator (REHEARSAL=1 STOP_AFTER=dumps, W42_PREDECLARATION=1) behind the',
             "driver's idle gate; load = the 1-minute load average sampled every 15 s between the launch's",
             'opening and closing machine reads (10 cores).', '']
    for r in rows:
        load1 = r['load1']
        loadtext = (f'load {load1["min"]:.0f}-{load1["max"]:.0f} (median {load1["median"]:.0f}, {load1["samples"]} '
                    f'samples covering {load1["coverage"][0]}-{load1["coverage"][1]} of the launch\'s '
                    f'{r["openedAt"][11:19]}Z-{(r["closedAt"] or "?")[11:19]}Z)'
                    if load1['samples'] else 'load not sampled in this window')
        census = r['census'] or {}
        names = sorted(set(census.get('open', {}).get('names', [])) | set(census.get('close', {}).get('names', [])))
        lines.append(f'{r["root"]}/{r["launch"]} {r["run"]} (mode {r["mode"]}): {r["outcome"]}; '
                     f'{r["scenes"]} scenes in {r["elapsedSeconds"]} s = {r["perSceneSeconds"]} s a scene against a '
                     f'{r["timeoutSeconds"]} s timeout (margin {r["marginSeconds"]} s); departures {r["departures"]}, '
                     f'unpredicted {r["unpredicted"]}; {loadtext}; foreign census open '
                     f'{census.get("open", {}).get("count")} / close {census.get("close", {}).get("count")} '
                     f'({", ".join(names)})')
    (args.out_dir / 'b7.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
