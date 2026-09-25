#!/usr/bin/env python3.12
"""Run the real publisher and append witness together in a disposable source-copy repository."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
PROFILE = 'apple-macos-27.0-1x-light-standard-glass0.5'


def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout


def protected():
    paths = [PACKAGE / 'results/matrix.json']
    for directory in ('generations', 'superseded'):
        paths.extend(p for p in (PACKAGE / 'results' / directory).rglob('*') if p.is_file())
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


before = protected()
with tempfile.TemporaryDirectory(prefix='w40-publisher-demo-') as temporary:
    root = Path(temporary)
    package = root / 'packages/calibration'
    package.mkdir(parents=True)
    run(['git', 'init', '--quiet', str(root)], root)
    for directory in ('src', 'cli'):
        shutil.copytree(PACKAGE / directory, package / directory)
    shutil.copyfile(PACKAGE / 'package.json', package / 'package.json')
    (package / 'node_modules').symlink_to(PACKAGE / 'node_modules', target_is_directory=True)
    results = package / 'results'
    (results / 'generations').mkdir(parents=True)
    (results / 'superseded').mkdir()
    (results / 'matrix.json').write_text('{"schemaVersion":5,"cells":[]}\n')
    (results / 'superseded/index.json').write_text('{"files":{},"byDocumentSha256":{}}\n')
    (results / 'generations/index.json').write_text(json.dumps({
        'schemaVersion': 1, 'files': {}, 'byDocumentSha256': {}, 'currentByProfile': {}}))
    reference = root / 'apps/reference-apple'
    (reference / 'fixtures').mkdir(parents=True)
    (reference / 'scenes.json').write_text(json.dumps({
        'scenes': [{'id': 'cal'}, {'id': 'held'}],
        'split': {'calibration': ['cal'], 'holdout': ['held']}}))
    (reference / 'fixtures/manifest.json').write_text(json.dumps({'profiles': [{
        'profileKey': PROFILE, 'fixtures': [
            {'sceneId': 'cal', 'fixtureSet': 'calibration'},
            {'sceneId': 'held', 'fixtureSet': 'holdout'}]}]}))
    document = package / 'active.json'
    document.write_text('{"syntheticCandidate":1}\n')
    active = hashlib.sha256(document.read_bytes()).hexdigest()[:12]
    command = ['node', '--import', 'tsx', 'cli/matrix.ts']
    run(command + ['stage', 'stage', '--profile', PROFILE, '--renderer', 'webgpu,css',
                   '--set', 'calibration,holdout', '--material-profile', 'active.json'], package)
    witness = root / 'before.json'
    run(['python3.12', str(HERE / 'append-check.py'), 'snapshot', str(results), str(witness)], package)
    rows = []
    for tier in ('webgpu', 'css'):
        for scene, fixture_set in (('cal', 'calibration'), ('held', 'holdout')):
            rows.append({'key': {'profileKey': PROFILE, 'sceneId': scene, 'web': {
                'engine': 'chromium', 'engineVersion': '1', 'renderer': tier,
                'samplingBackend': 'gpu-texture' if tier == 'webgpu' else 'css-backdrop',
                'gpuAdapter': 'synthetic', 'colorSpace': 'srgb',
                'capturePath': f'materialProfile=packages/calibration/active.json sha256:{active}'}},
                'fixtureSet': fixture_set, 'syntheticReading': 0.0000001})
    # An equivalent JSON reserialization loses these lexical bytes; the witness must retain them.
    staged = json.dumps({'schemaVersion': 5, 'cells': rows}, indent=2).replace('1e-07', '1.000e-7')
    (package / 'stage/matrix.json').write_text(staged)
    published = json.loads(run(command + ['publish', 'stage'], package))
    filename = Path(published['file']).name
    print('Real publisher on disposable synthetic repository:')
    print(json.dumps({**published, 'file': f'generations/{filename}'}, indent=2))
    print(run(['python3.12', str(HERE / 'append-check.py'), 'verify', str(results), str(witness),
               str(package / 'stage/matrix.json'), filename], package), end='')
    assert b'1.000e-7' in (results / 'generations' / filename).read_bytes()
    print('PASS original numeric spelling 1.000e-7 retained; no row reserialization')
assert protected() == before
print('PASS real canonical files unchanged before/after')
