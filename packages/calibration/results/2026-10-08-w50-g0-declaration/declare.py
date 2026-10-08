#!/usr/bin/env python3
"""W50's prospective seals. Native authorisation is not a complete fitting referee.

The operational declaration fixes the experiment before capture. A separate append-only
pre-fit evidence seal fills its declared reference identities from the admitted archive and
current renders; it cannot change the law, membership, budget or reference generation.
There is deliberately no amendment command. Missing evidence blocks fitting and rendering.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ACTIVITY = Path('/Users/new/vitrea-w50/g0-scratch')
PARTS = ('declaration', 'fit-declaration')
FAILURE = 'NEITHER: no seal, no publication, no re-selection'
X41_SCOPE = {
    'condition': 'PASS of every declared gate and the single exposure; NEITHER changes nothing',
    'newGeneration': 'One immutable complete dark0.5 generation and its index.files record',
    'aliases': 'Add new document aliases only; preserve every old alias owner',
    'retirement': 'Only 0eac5b294cc2.json status may retire; all its other fields stay unchanged',
    'selection': 'Only the two dark0.5 currentByProfile selections may change',
    'sourceDocuments': [
        'packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json',
        'packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json'],
    'generated': 'Only dark active/receded endpoints in packages/platform-web/src/macos27-profile.ts',
    'defaultProjections': ['macos27MaterialProfileDocument', 'DEFAULT_MATERIAL_PROFILE_DOCUMENT'],
    'unchanged': ['light endpoints and bytes', 'fixtures', 'old generation files',
                  'document identity', 'CSS mapping', 'glass position', 'default selection macOS27 at0.5',
                  'all unrelated index units', 'original X41 witness and projection'],
    'witness': 'Preserve pre-change source bytes; add prospective supersession witness before mutation',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def verify_pin(pin, root):
    target = (Path(root) / pin['path']).resolve()
    if not target.is_relative_to(Path(root).resolve()) or not target.is_file() or sha(target) != pin['sha256']:
        raise ValueError(f'Changed, missing or escaped source: {pin["path"]}')
    return target


def checked(part, directory=HERE, root=ROOT):
    directory, root = Path(directory), Path(root)
    path = directory / f'{part}.json'
    doc = load(path)
    if doc.get('schema') != f'w50-{part}-1':
        raise ValueError('Wrong declaration schema')
    sources = doc.get('sources', [])
    if not sources or len({p['path'] for p in sources}) != len(sources):
        raise ValueError('Missing or duplicate source pins')
    for item in sources:
        verify_pin(item, root)
    if part == 'declaration' and doc.get('contracts'):
        # G0 can fix the native sitting before the web candidate batch exists. The native
        # execution contract and its sidecar nevertheless have to be pinned by the root.
        contract = directory / doc['contracts']['native']
        pinned = {item['path'] for item in sources}
        for target in (contract, Path(str(contract) + '.sha256')):
            if str(target.relative_to(root)) not in pinned:
                raise ValueError('Native contract or sidecar missing from root source pins')
        if Path(str(contract) + '.sha256').read_text() != f'{sha(contract)}  {contract.name}\n':
            raise ValueError('Native execution contract differs from seal')
    if part == 'fit-declaration':
        if doc.get('partOneSha256') != sha(directory / 'declaration.json'):
            raise ValueError('Part two names another part one')
        if doc.get('noPostGateAmendment') is not True or doc.get('onFailure') != FAILURE:
            raise ValueError('Missing fixed no-post-gate-amendment stop')
        if doc.get('conditionalX41') != X41_SCOPE:
            raise ValueError('Conditional X41 scope differs from DL2')
    return path


def seal(directory=HERE, root=ROOT, activity=ACTIVITY):
    directory = Path(directory)
    if any((directory / f'{part}.sha256').exists() for part in PARTS):
        raise ValueError('Existing declaration: no amendment or rehash')
    if Path(activity).exists() and any(Path(activity).iterdir()):
        raise ValueError('Experiment activity exists: operational declaration must precede it')
    paths = [checked(part, directory, root) for part in PARTS]
    for path in paths:
        with path.with_suffix('.sha256').open('x') as handle:
            handle.write(f'{sha(path)}  {path.name}\n')


def validate_references(doc, root):
    cells = doc.get('cells', [])
    if not cells:
        raise ValueError('UNMEASURED: empty reference population')
    seen = set()
    for cell in cells:
        key = tuple(cell[k] for k in ('profile', 'renderer', 'scene', 'statistic'))
        if key in seen:
            raise ValueError(f'Duplicate reference identity: {key}')
        seen.add(key)
        blind = cell.get('role') == 'blind'
        if blind:
            if cell.get('status') != 'SEALED_BLIND' or any(
                    cell.get(k) is not None for k in ('native', 'current', 'fidelity', 'B')):
                raise ValueError(f'Missing sealed blind identity or leaked blind statistic: {key}')
        else:
            if cell.get('status') != 'MEASURED':
                raise ValueError(f'UNMEASURED reference: {key}')
            if not isinstance(cell.get('B'), (float, int)) or not math.isfinite(cell['B']) or cell['B'] <= 0:
                raise ValueError(f'Invalid reference budget: {key}')
        for name in ('nativeEvidence', 'currentEvidence'):
            pin = cell.get(name)
            if not isinstance(pin, dict):
                raise ValueError(f'Missing {name}: {key}')
            # Reference trees may be on the capture machine, outside this checkout. The path is
            # fixed in the sealed evidence map and hash-checked, never treated as code to execute.
            path = Path(pin['path'])
            if not path.is_absolute():
                path = Path(root) / path
            if not path.is_file() or sha(path) != pin['sha256']:
                raise ValueError(f'Changed or missing {name}: {key}')
        if not cell.get('currentDocumentPair') or not cell.get('support') or not cell.get('role'):
            raise ValueError(f'Incomplete reference provenance: {key}')
        for history in cell.get('historical', []):
            if not history.get('documentPair') or not math.isfinite(history.get('maxGrowthInB', float('nan'))):
                raise ValueError(f'Incomplete historical reference: {key}')


def validate_proof(proof, kind, root):
    """A named proof must carry reproducible input/output bytes, not a readiness placeholder."""
    if (proof.get('schema') != 'w50-prefit-proof-1' or proof.get('kind') != kind or
            proof.get('status') != 'PASS'):
        raise ValueError(f'Missing measured pre-fit proof: {kind}')
    checks = proof.get('checks', [])
    if not checks or any(not c.get('id') or c.get('status') != 'PASS' for c in checks):
        raise ValueError(f'Incomplete pre-fit checks: {kind}')
    if len({c['id'] for c in checks}) != len(checks):
        raise ValueError(f'Duplicate pre-fit checks: {kind}')
    for field in ('sources', 'outputs'):
        if not proof.get(field):
            raise ValueError(f'Missing pre-fit {field}: {kind}')
        for pin in proof[field]:
            verify_pin(pin, root)


def require_execution_contract(evidence, directory, root):
    pins = {pin['path']: pin for pin in evidence.get('sources', [])}
    contract = Path(directory) / 'audit/execution-contract.json'
    for path in (contract, Path(str(contract) + '.sha256')):
        relative = str(path.relative_to(root))
        if relative not in pins:
            raise ValueError('Web contract is not authorised by the pre-fit source seal')
        verify_pin(pins[relative], root)
    if Path(str(contract) + '.sha256').read_text() != f'{sha(contract)}  {contract.name}\n':
        raise ValueError('Web execution contract differs from authorised pre-fit seal')


def verify(directory=HERE, root=ROOT, phase='native'):
    if phase not in ('native', 'fit'):
        raise ValueError('Unknown declaration phase')
    directory = Path(directory)
    for part in PARTS:
        path = checked(part, directory, root)
        if path.with_suffix('.sha256').read_text() != f'{sha(path)}  {path.name}\n':
            raise ValueError(f'{part} bytes differ from prospective seal')
    if phase == 'fit':
        path = directory / 'pre-fit-evidence.json'
        if path.with_suffix('.sha256').read_text() != f'{sha(path)}  {path.name}\n':
            raise ValueError('Pre-fit evidence differs from seal')
        evidence = load(path)
        if evidence.get('partTwoSha256') != sha(directory / 'fit-declaration.json'):
            raise ValueError('Evidence names another fixed landing rule')
        for pin in evidence.get('sources', []):
            verify_pin(pin, root)
        require_execution_contract(evidence, directory, root)
        completed = load(verify_pin(evidence['references'], root))
        declared = load(directory / 'references.json')
        key = lambda c: tuple(c[k] for k in ('profile', 'renderer', 'scene', 'statistic'))
        if [key(c) for c in completed['cells']] != [key(c) for c in declared['cells']]:
            raise ValueError('Pre-fit reference membership changed')
        for before, after in zip(declared['cells'], completed['cells']):
            for field in ('profile', 'renderer', 'scene', 'statistic', 'support', 'role',
                          'currentGeneration', 'currentDocumentPair', 'historical'):
                if before.get(field) != after.get(field):
                    raise ValueError(f'Pre-fit reference changed fixed {field}')
            for field in ('B', 'native', 'current', 'fidelity', 'nativeEvidence',
                          'currentEvidence', 'currentMetadata'):
                if before.get(field) is not None and before[field] != after.get(field):
                    raise ValueError(f'Pre-fit reference changed known {field}')
        validate_references(completed, root)
        required = load(directory / 'fit-declaration.json')['requiredEvidence']
        if set(evidence.get('evidence', {})) != set(required):
            raise ValueError('Missing required pre-fit evidence')
        for name in required:
            validate_proof(load(verify_pin(evidence['evidence'][name], root)), name, root)
    return {'status': 'SEALED', 'phase': phase, 'candidateVerdict': 'NOT_READ'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('hash', 'check'))
    parser.add_argument('--phase', choices=('native', 'fit'), default='native')
    args = parser.parse_args()
    if args.command == 'hash':
        seal()
    print(json.dumps(verify(phase=args.phase), indent=2))
