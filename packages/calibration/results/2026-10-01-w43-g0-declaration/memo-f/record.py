#!/usr/bin/env python3.12
"""W43 G0 (c): memo F's record, taken after the window (RUNBOOK "After it completes").

    python3.12 -B record.py <run-root> [--into <dir>]     # --into defaults to this directory

The run root stays in scratch, as memo D's did. This writes into `run/` beside it:
- `run-sha256.txt`: every regular file under the run root, by SHA-256 and path (the dumps included),
  so the scratch can be checked against the record on the machine that holds it;
- the attestations, copied: `preflight*.json`, `as-found.json`, `restore*.json`,
  every launch's `launch.json`, `machine-open.json`, `machine-close.json`, `check.json`,
  `admission.json` and `session-trace.jsonl`, every quarantine's `quarantine.json`, and `logs/`;
and runs `memo_f_read.py` on the admitted launches into `reading/`. It refuses unless `restore.json`
reads verified and the slider reads its as-found value now (a record of an unrestored machine is not
a record; restore first).
"""
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
KEEP = ('launch.json', 'machine-open.json', 'machine-close.json', 'check.json', 'admission.json',
        'session-trace.jsonl', 'quarantine.json')


def main(argv):
    if len(argv) not in (2, 4) or (len(argv) == 4 and argv[2] != '--into'):
        print(__doc__)
        return 64
    root = Path(argv[1]).resolve()
    into = Path(argv[3]).resolve() if len(argv) == 4 else HERE
    restore = json.loads((root / 'restore.json').read_text())
    if not restore.get('verified'):
        raise SystemExit('REFUSE: restore.json is not verified; restore first (RUNBOOK)')
    as_found = json.loads((root / 'as-found.json').read_text())
    exported = plistlib.loads(subprocess.run(['/usr/bin/defaults', 'export', '-g', '-'], capture_output=True,
                                             check=True).stdout)
    now = exported.get('NSGlassTintAmount')
    if (now is None) != (not as_found['present']) or (now is not None and now != as_found['value']):
        raise SystemExit(f"REFUSE: the slider reads {now!r}, its as-found value was {as_found['value']!r}")
    out = into / 'run'
    if out.exists():
        raise SystemExit(f'REFUSE: {out} exists; a record is written once')
    out.mkdir()
    lines = []
    for p in sorted(x for x in root.rglob('*') if x.is_file()):
        lines.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}')
    (out / 'run-sha256.txt').write_text('\n'.join(lines) + '\n')
    for p in sorted(root.glob('*.json')):
        if p.name != 'scenes.json':
            shutil.copy2(p, out / p.name)
    shutil.copytree(root / 'logs', out / 'logs')
    for d in sorted((root / 'runs').iterdir()):
        for name in KEEP:
            if (d / name).exists():
                (out / 'runs' / d.name).mkdir(parents=True, exist_ok=True)
                shutil.copy2(d / name, out / 'runs' / d.name / name)
    r = subprocess.run([sys.executable, '-B', str(HERE / 'memo_f_read.py'), str(root), '--out', str(into / 'reading')],
                       capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-1000:])
    print(f'recorded {len(lines)} files by SHA-256 into {out}; the reading is in {into / "reading"}')
    return r.returncode


if __name__ == '__main__':
    sys.exit(main(sys.argv))
