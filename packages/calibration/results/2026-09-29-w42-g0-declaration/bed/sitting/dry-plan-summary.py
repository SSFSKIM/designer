#!/usr/bin/env python3.12
"""Reproduce dry-plan.json / dry-plan.txt / dry-plan-stdout.txt from `sitting.py plan`.

Runs the dry mode into a fresh scratch directory outside the repository (it executes nothing),
then distils its plan.json for the record: each launch argv is replaced by its SHA-256 (the
full argv stays in the scratch plan), and the bed's pins are named.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    scratch = Path(tempfile.mkdtemp(prefix='w42-dry-plan-')) / 'plan'
    out = subprocess.run([sys.executable, str(HERE / 'sitting.py'), 'plan', '--out', str(scratch)],
                         check=True, capture_output=True, text=True).stdout
    plan = json.loads((scratch / 'plan.json').read_text())
    for p in plan['passes']:
        for r in p['runs']:
            r['argvSha256'] = hashlib.sha256(json.dumps(r.pop('argv')).encode()).hexdigest()
    plan['bedPins'] = json.loads((HERE.parent / 'pins.json').read_text())
    (HERE / 'dry-plan.json').write_text(json.dumps(plan, indent=1) + '\n')
    (HERE / 'dry-plan-stdout.txt').write_text(out)
    pins = plan['bedPins']
    lines = ['W42 sitting dry plan (sitting.py plan): executed nothing; every document and argv was written',
             'under a scratch directory. Per pass: display mode, runs, cells per run (glass + references).',
             f'bed pins: scenes {pins["scenes-w42-body.json"][:12]}, bed {pins["bed.json"][:12]}', '']
    for p in plan['passes']:
        if p['kind'] == 'dump':
            r = p['runs'][0]
            lines.append(f'{p["name"]:28s} mode {p["mode"]}  1 dump launch  {r["scenes"]} scenes  '
                         f'(timeout {r["timeoutSeconds"]} s)')
        else:
            cells = ' '.join(str(r['cells']) for r in p['runs'])
            lines.append(f'{p["name"]:28s} mode {p["mode"]}  {len(p["runs"])} runs  cells/run {cells}  '
                         f'protocol {p["runs"][0]["protocol"]}')
    lines += ['', 'totals: ' + json.dumps(plan['totals'])]
    (HERE / 'dry-plan.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
