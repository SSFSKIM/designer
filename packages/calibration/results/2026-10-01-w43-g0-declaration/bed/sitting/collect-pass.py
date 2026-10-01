#!/usr/bin/env python3.12
"""collect-pass.py <pass> [<pass> ...]: copy a sitting pass's attestations into the G1 evidence.

Derived from W42 G0's collect-pass.py. Roots come from the environment (VITREA_SITTING_DIR,
W43_EVIDENCE). Per run (admitted run-N and every QUARANTINE-*): the machine and session reads,
attest.read, launch.json, admission.json or refusal.txt, the idle-wait log, the watchdog's log, a
dump run's sentinel check, and a distilled record (manifest SHA-256, fixture count, capture times,
protocol). Never a manifest, a capture log, a dump JSON or a PNG: those go to the archive.

W43's change: the idle-wait log is `driver-idle.txt` (the driver writes it so), because the
repository ignores `*.log` and W42's per-pass commits silently dropped every `driver-idle.log`
(W42 G1 phase 1; tech-debt-tracker). A legacy `.log` is still copied, renamed to `.txt`.
"""
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

KEEP = ['attest.open.json', 'attest.close.json', 'attest.read', 'attest.close', 'session-before.json',
        'session-after.json', 'launch.json', 'admission.json', 'refusal.txt', 'driver-idle.txt', 'watchdog.txt',
        'check.json', 'timing.json', 'rehearsal.json', 'bridge.json']
RENAMED = {'driver-idle.log': 'driver-idle.txt'}


def collect(run_root, evidence, name):
    src, dst = run_root / name, evidence / 'attest' / name
    dst.mkdir(parents=True, exist_ok=True)
    for spec in sorted(src.glob('scenes-*.json')):
        (dst / (spec.name + '.sha256')).write_text(hashlib.sha256(spec.read_bytes()).hexdigest() + '\n')
    record = []
    for run in sorted(p for p in src.iterdir() if p.is_dir() and p.name.startswith(('run-', 'QUARANTINE-'))):
        out = dst / run.name
        out.mkdir(exist_ok=True)
        for f in KEEP:
            if (run / f).exists():
                shutil.copy2(run / f, out / f)
        for old, new in RENAMED.items():
            if (run / old).exists() and not (run / new).exists():
                shutil.copy2(run / old, out / new)
        row = dict(run=run.name, admitted=(run / 'admission.json').exists())
        if (run / 'manifest.json').exists():
            raw = (run / 'manifest.json').read_bytes()
            m = json.loads(raw)
            fx = [f for p in m['profiles'] for f in p['fixtures']]
            times = sorted(f['capturedAt'] for f in fx if f.get('capturedAt'))
            row.update(manifestSha256=hashlib.sha256(raw).hexdigest(), fixtures=len(fx),
                       firstCapture=times[0] if times else None, lastCapture=times[-1] if times else None,
                       captureProtocol={k: v for k, v in (m.get('captureProtocol') or {}).items() if k != 'scenes'})
        if (run / 'refusal.txt').exists():
            row['refusal'] = (run / 'refusal.txt').read_text().strip()
        record.append(row)
    (dst / 'runs.json').write_text(json.dumps(record, indent=2) + '\n')
    log = run_root / 'logs' / f'{name}-driver.txt'
    if log.exists():
        shutil.copy2(log, dst / 'driver.txt')
    return record


if __name__ == '__main__':
    run_root, evidence = Path(os.environ['VITREA_SITTING_DIR']), Path(os.environ['W43_EVIDENCE'])
    for name in sys.argv[1:]:
        rows = collect(run_root, evidence, name)
        print(name, [(r['run'], r['admitted'], r.get('fixtures')) for r in rows])
