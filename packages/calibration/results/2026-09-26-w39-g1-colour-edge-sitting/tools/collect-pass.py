"""collect-pass.py <pass> [<pass> ...]: copy a sitting pass's attestations into the G1 evidence.

Per run (admitted run-N and every QUARANTINE-*): the machine reads (attest.open/close .json and
their portable .read/.close), the session reads, launch.json, admission.json or refusal.txt,
and a distilled record (manifest SHA-256, fixture count, capture times, protocol). Never the
manifest itself, the producer's capture logs or any PNG: those can carry holdout-role cells'
diagnostics and stay producer-only under ~/vitrea-w39/run (the sitting's docstring; X12).
The driver log is copied from ~/vitrea-w39/run/logs/<pass>-driver.txt.
"""
import hashlib, json, shutil, sys
from pathlib import Path
RUN = Path('/Users/new/vitrea-w39/run')
EV = Path('/Users/new/vitrea-w39/g1/packages/calibration/results/2026-09-26-w39-g1-colour-edge-sitting')
KEEP = ['attest.open.json', 'attest.close.json', 'attest.read', 'attest.close', 'session-before.json',
        'session-after.json', 'launch.json', 'admission.json', 'refusal.txt']
for name in sys.argv[1:]:
    src, dst = RUN / name, EV / 'attest' / name
    dst.mkdir(parents=True, exist_ok=True)
    for spec in sorted(src.glob('scenes-run-*.json')):
        (dst / (spec.name + '.sha256')).write_text(hashlib.sha256(spec.read_bytes()).hexdigest() + '\n')
    record = []
    for run in sorted(p for p in src.iterdir() if p.is_dir() and p.name.startswith(('run-', 'QUARANTINE-'))):
        out = dst / run.name
        out.mkdir(exist_ok=True)
        for f in KEEP:
            if (run / f).exists():
                shutil.copy2(run / f, out / f)
        row = dict(run=run.name, admitted=(run / 'admission.json').exists())
        if (run / 'manifest.json').exists():
            raw = (run / 'manifest.json').read_bytes(); m = json.loads(raw)
            fx = [f for p in m['profiles'] for f in p['fixtures']]
            times = sorted(f['capturedAt'] for f in fx if f.get('capturedAt'))
            row.update(manifestSha256=hashlib.sha256(raw).hexdigest(), fixtures=len(fx),
                       firstCapture=times[0] if times else None, lastCapture=times[-1] if times else None,
                       captureProtocol={k: v for k, v in (m.get('captureProtocol') or {}).items()
                                        if k != 'scenes'})
        if (run / 'refusal.txt').exists():
            row['refusal'] = (run / 'refusal.txt').read_text().strip()
        record.append(row)
    (dst / 'runs.json').write_text(json.dumps(record, indent=2) + '\n')
    log = RUN / 'logs' / f'{name}-driver.txt'
    if log.exists():
        shutil.copy2(log, dst / 'driver.txt')
    print(name, [(r['run'], r['admitted'], r.get('fixtures')) for r in record])
