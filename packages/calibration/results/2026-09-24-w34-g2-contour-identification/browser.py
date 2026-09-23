#!/usr/bin/env python3.12
"""G0's glass allowlist, one attested browser profile at a time (§5.176, X6)."""
import datetime
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
G0 = HERE.parent / '2026-09-23-w34-g0-contour-bed'
G1 = HERE.parent / '2026-09-23-w34-g1-contour-sitting'
spec = importlib.util.spec_from_file_location('machine', G0 / 'record-machine.py')
machine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(machine)


def preflight(label):
    settings = {}
    for domain, key, expected in [
        ('com.apple.universalaccess', 'reduceTransparency', 0),
        ('com.apple.universalaccess', 'increaseContrast', 0),
        ('-g', 'NSGlassTintAmount', .5),
        ('com.apple.Accessibility', 'ButtonShapesEnabled', 0),
    ]:
        value = subprocess.check_output(['defaults', 'read', domain, key], text=True).strip()
        settings[key] = value
        if float(value) != expected:
            raise RuntimeError('X6 setting mismatch: ' + key)
    raw = subprocess.check_output(['ioreg', '-c', 'IOHIDSystem'], text=True)
    idle = int(re.search(r'"HIDIdleTime"\s*=\s*(\d+)', raw)[1]) / 1e9
    foreign = machine.processes()
    row = dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(), label=label,
               settings=settings, idleSeconds=idle, foreignProcessCount=len(foreign),
               foreignProcesses=foreign, admitted=idle >= 60 and not foreign,
               renderer='webgpu', channel='chromium', captureProcessesToLaunch=1)
    with (HERE / 'browser-runs.txt').open('a') as f:
        f.write(json.dumps(row, sort_keys=True) + '\n')
        f.flush(); os.fsync(f.fileno())
    if not row['admitted']:
        raise RuntimeError('X6 preflight refused; attempt recorded, no browser launched')


def verify_completed_profile(key, log):
    # G1's producer omits the optional-looking caveats list which compare's
    # final reporter requires. Measurement and matrix serialization precede
    # that failure. Do not recapture successful pixels to repair a report.
    text = log.read_text()
    matrix = json.loads((HERE / 'matrix.json').read_text())
    rows = [r for r in matrix['cells'] if r['key']['profileKey'] == key]
    split = json.loads((G0 / 'split.json').read_text())
    scenes = json.loads((ROOT / 'apps/reference-apple/scenes-w34-contour.json').read_text())
    allowed = set(split['calibration'] + split['validation'])
    expected = {s['id'] for s in scenes['scenes'] if s['id'] in allowed and
                scenes['components'][s['component']]['kind'] != 'none' and
                not scenes['components'][s['component']].get('opaque')}
    captured = set()
    for scene in expected:
        path = HERE / 'web-captures' / key / scene
        cell = json.loads((path / 'cell__webgpu.json').read_text())
        report = json.loads((path / 'report__webgpu.json').read_text())
        if cell['renderer'] != 'webgpu' or cell['gpuAdapter'] != 'apple/metal-3' or report['fallback']:
            raise RuntimeError('Fallback capture: ' + scene)
        if report['page']['material']['name'] != 'apple-macos-27.0-glass0.5':
            raise RuntimeError('Unexpected material: ' + scene)
        captured.add(scene)
    if captured != expected or any(r['tier'] != 'texture' for r in rows):
        raise RuntimeError('Incomplete or fallback profile; retained ' + str(log))
    errors = [line for line in text.splitlines() if line.startswith('compare:')]
    if errors and errors != ['compare: manifest.caveats is not iterable']:
        raise RuntimeError('Unexpected compare failure: ' + repr(errors))
    with (HERE / 'browser-runs.txt').open('a') as f:
        f.write(json.dumps(dict(profile=key, matrixCells=len(rows),
            captureComplete=True, missingMatrixScenes=sorted(expected-{r['key']['sceneId'] for r in rows}), reportingError=errors,
            recaptured=False)) + '\n')


def main():
    # Obtain the command from G0, not a duplicate split implementation. Narrowing
    # that allowlist to one profile makes the per-browser preflight executable.
    raw = subprocess.check_output([
        'python3.12', str(G0 / 'wave.py'), 'plan', '--roles', 'calibration,validation',
        '--fixtures', str(HERE / 'compare-fixtures'), '--out-matrix', str(HERE / 'matrix.json'),
        '--captures', str(HERE / 'web-captures'),
    ], text=True)
    plan = json.loads(raw)
    (HERE / 'browser-plan.json').write_text(raw)
    profiles = json.loads((G1 / 'probe/manifest.json').read_text())['profiles']
    for profile in profiles:
        key = profile['profileKey']
        log = HERE / ('browser-' + key + '.txt')
        if log.exists():
            verify_completed_profile(key, log)
            continue
        command = plan['command'] + ['--profile', key]
        preflight(key)
        with log.open('w') as f:
            result = subprocess.run(command, env={**os.environ, **plan['environment']},
                                    stdout=f, stderr=subprocess.STDOUT)
        with (HERE / 'browser-runs.txt').open('a') as f:
            f.write(json.dumps(dict(profile=key, exitCode=result.returncode,
                                   completed=datetime.datetime.now(datetime.timezone.utc).isoformat()))+'\n')
        verify_completed_profile(key, log)


if __name__ == '__main__':
    main()
