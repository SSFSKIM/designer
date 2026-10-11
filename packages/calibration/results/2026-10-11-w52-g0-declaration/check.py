"""Check the sealed G0 scientific declaration; this grants no execution capability.

The committed charter revision, exact scientific data, runtime sources and G0
proof bytes must agree. G1 separately seals candidate-bound execution roots.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(pin):
    path = REPO / pin['path']
    if path.resolve() != path or not path.is_file():
        raise ValueError('Declaration input is not an ordinary repository file: ' + str(path))
    raw = path.read_bytes()
    if sha(raw) != pin['sha256']:
        raise ValueError('Declaration input changed: ' + str(path))
    return raw


def verify():
    raw = (HERE / 'declaration.json').read_bytes()
    witness = (HERE / 'declaration.sha256').read_text().split()
    if witness != [sha(raw), 'declaration.json']:
        raise ValueError('Declaration hash differs')
    declaration = json.loads(raw)
    if declaration['schema'] != 'w52-g0-declaration-1' or declaration['executionAuthority'] is not False:
        raise ValueError('Wrong scientific declaration authority')
    charter = declaration['charter']
    archived = subprocess.run(['git', '-C', str(REPO), 'show',
                              charter['commit'] + ':' + charter['path']],
                             check=True, capture_output=True).stdout
    if sha(archived) != charter['sha256']:
        raise ValueError('Committed scientific charter differs')
    paths = [p['path'] for p in declaration['sources']]
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate declaration source')
    for pin in declaration['sources']:
        checked(pin)
    proof = json.loads(checked(declaration['proof']))
    expected = {'shippedDocumentCount': 10, 'unchangedDigestCount': 10,
                'goldenTestsPassed': 34, 'gpuOperatorTestsPassed': 4,
                'workspaceBuildExitCode': 0, 'workspaceLintExitCode': 0,
                'freeze26Count': 1818, 'freeze05Count': 911,
                'scientificFitOrGateRun': False}
    if any(proof[k] != v for k, v in expected.items()):
        raise ValueError('G0 proof is incomplete or claims a scientific phase')
    for pin in proof['logs']:
        checked(pin)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'populations/build.py'), 'check'],
                   check=True)
    print(f"W52 G0 declaration intact: {len(paths)} source files; ten identities, 34 goldens; "
          'no fit/gate/exposure authority')


if __name__ == '__main__':
    verify()
