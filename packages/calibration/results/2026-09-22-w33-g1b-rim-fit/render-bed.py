#!/usr/bin/env python3.12
"""W33 G1b scratch-only bed, with X6 attested before each browser (§5.172).

The bed retains W32's ladder and adds every non-holdout black-bearing scene.
Each invocation uses a fresh destination: evidence and captures are never replaced.
The sixty-second pause is a declared idle interval, not completion polling.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
CAL = HERE.parent.parent
ROOT = CAL.parent.parent
BLACK = {'checkerboard', 'checkerboard-4', 'checkerboard-8', 'checkerboard-32',
         'checkerboard-64', 'impulse', 'hc-text', 'hc-text-7', 'hc-text-28'}


def x6(label):
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    time.sleep(60)
    values = []
    for domain, key in [('com.apple.universalaccess', 'reduceTransparency'),
                        ('com.apple.universalaccess', 'increaseContrast'),
                        ('-g', 'NSGlassTintAmount')]:
        p = subprocess.run(['defaults', 'read', domain, key], capture_output=True, text=True)
        values.append(p.stdout.strip() if p.returncode == 0 else 'absent')
    p = subprocess.run(['pgrep', '-ifl', 'Chromium|playwright|compare.ts|capture-web|VitreaReference'],
                       capture_output=True, text=True)
    processes = p.stdout.strip().splitlines() if p.stdout.strip() else []
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    line = (f'{now} {label} RT={values[0]} IC={values[1]} slider={values[2]} '
            f'foreignProcessCount={len(processes)} idleStart={start} idleSeconds=60\n')
    with (HERE / 'browser-runs.txt').open('a') as f:
        f.write(line)
        for process in processes:
            f.write('  ' + process + '\n')
    print(line, end='', flush=True)
    if values != ['0', '0', '0.5'] or processes:
        raise SystemExit('X6 refused: settings or foreign capture processes')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('label')
    p.add_argument('--documents', type=Path, default=CAL / 'profiles')
    p.add_argument('--scratch', type=Path, default=Path('/tmp/w33-g1b-fit'))
    a = p.parse_args()
    dest = a.scratch / a.label
    dest.mkdir(parents=True, exist_ok=False)
    scenes = json.loads((ROOT / 'apps/reference-apple/scenes.json').read_text())
    roles = {s: role for role, ids in scenes['split'].items() if not role.startswith('$') for s in ids}
    ladder = (CAL / 'results/2026-09-21-w32-g1-shadow-fit/ladder.sh').read_text()
    selected = set(re.search(r'LADDER_45="([^"]+)"', ladder)[1].split(','))
    selected.update(re.search(r'LADDER_W32="([^"]+)"', ladder)[1].split(','))
    selected.update(s['id'] for s in scenes['scenes']
                    if s['id'].split('__')[0] in BLACK and roles.get(s['id']) == 'probe')
    assert all(roles[s] == 'probe' for s in selected)
    profiles = [p['key'] for p in scenes['profiles'] if '27.0' in p['key']
                and '-increased-contrast-glass' not in p['key']]
    (dest / 'selection.json').write_text(json.dumps(dict(profiles=profiles, probe=sorted(selected)), indent=2)+'\n')
    for profile in profiles:
        scheme = 'dark' if '-dark-' in profile else 'light'
        doc = a.documents / f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json'
        receded = doc.with_name(doc.stem + '-receded.json')
        for role in ['calibration,validation', 'probe']:
            x6(f'{a.label}/{profile}/{role}')
            cmd = ['npx', 'tsx', 'cli/compare.ts', '--profile', profile,
                   '--material-profile', str(doc), '--receded-profile', str(receded),
                   '--renderer', 'webgpu', '--alpha', '--write-partial',
                   '--out-matrix', str(dest / 'matrix.json'), '--set', role]
            if role == 'probe':
                cmd += ['--scene', ','.join(sorted(selected))]
            env = dict(os.environ, VITREA_WEB_CAPTURES=str(dest / 'captures'))
            subprocess.run(cmd, cwd=CAL, env=env, check=True)
    print(f'complete {dest}', flush=True)


if __name__ == '__main__':
    main()
