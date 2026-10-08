"""Additive DL5–DL5g completion checks; the G0 inventory is never rewritten.

Only named measurement placeholders can be completed. Every other original field,
including provenance, historical caps and order, survives. Blind rows carry identities
and dependency pins only. Reported span-control rows require actual readings except
for exact DL5b/c keys whose pinned native read proves all three detected masks empty.
DL5g retains blind capture nulls until the exposure-only helper binds real evidence, keeps
canonical T1's typed fidelity label, and binds new-bed native evidence through all three
admitted runs without replacing the original support text. This module is deliberately
outside the already-sealed current-only capture closure; the future live root must pin it.
"""
import hashlib
import importlib.util
import gzip
import base64
import json
import re
import math
from pathlib import Path

KEY = ('profile', 'renderer', 'scene', 'statistic')
PROOFS = ('nativeArchive', 'repeatBar', 'referenceCompletion', 'dark05Bands',
          'active05ScratchBaselines', 'identityDigestsGoldens', 'numericalRehearsal',
          'shaderCpuAgreement', 'negativeNeutralDiagnostic', 'newBedRendererAdapter',
          'executionClosure', 'independentReview')
EXTRA = {'deep8-far24-luma-mean', 'deep8-far24-luma-median', 'T1-full-silhouette'}
FILLABLE = {'B', 'native', 'current', 'fidelity', 'nativeEvidence', 'currentEvidence',
            'currentMetadata'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def key(cell):
    return tuple(cell[k] for k in KEY)


def pin_path(pin, repo, external=False):
    if not isinstance(pin, dict) or not isinstance(pin.get('path'), str):
        raise ValueError('Missing content pin')
    path = (Path(repo) / pin['path']).resolve()
    if (not external and not path.is_relative_to(Path(repo).resolve())) or \
            not path.is_file() or sha(path) != pin.get('sha256'):
        raise ValueError(f'Changed or missing pinned input: {path}')
    return path


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def numerical_shape(value):
    if finite(value):
        return 'number'
    if isinstance(value, list) and value:
        return [numerical_shape(v) for v in value]
    if isinstance(value, dict) and value and all(isinstance(k, str) and k for k in value):
        return {k: numerical_shape(v) for k, v in value.items()}
    raise ValueError('Absent, nonfinite or malformed measured value')


def reading(cell):
    statistic = cell['statistic']
    native, current = cell.get('native'), cell.get('current')
    shape = numerical_shape(native)
    if numerical_shape(current) != shape:
        raise ValueError('Native/current measured shapes differ')
    if statistic in ('deep8-channel-median', 'central8-channel-median'):
        if shape != ['number'] * 3 or any(not 0 <= v <= 255 for v in native + current):
            raise ValueError('Channel medians require three finite encoded channels')
    elif statistic in EXTRA or statistic in ('T1', 'T1-low', 'T1-fine'):
        if shape != 'number' or native < 0 or current < 0:
            raise ValueError('Texture/luma readings require finite nonnegative scalars')
    elif statistic == 'low-end-path-level':
        wanted = ({'deep8Far24LumaMean': 'number', 'deep8Far24LumaMedian': 'number'}
                  if cell['scene'].startswith('impulse__') else
                  {'deep8ChannelMedian': ['number'] * 3})
        if shape != wanted:
            raise ValueError('Low-end path reading differs from declared cut/channel shape')
    elif statistic == 'owner-contracts' and not isinstance(native, dict):
        raise ValueError('Owner readings require nonempty named numerical maps')
    if statistic == 'T1-low' or (statistic == 'T1-full-silhouette' and isinstance(cell.get('fidelity'), dict)):
        fidelity = cell.get('fidelity')
        label = 'T1-fine' if statistic == 'T1-low' else 'T1-full-silhouette'
        if not isinstance(fidelity, dict) or set(fidelity) != {'statistic', 'native', 'current', 'reference'} or \
                fidelity['statistic'] != label or any(not finite(fidelity[k]) or fidelity[k] < 0
                    for k in ('native', 'current', 'reference')):
            raise ValueError('T1 fidelity requires its typed statistic and finite native/current/reference readings')
    elif cell.get('fidelity') is not None:
        fidelity_shape = numerical_shape(cell['fidelity'])
        if statistic in ('deep8-channel-median', 'central8-channel-median', 'low-end-path-level') and \
                fidelity_shape != shape:
            raise ValueError('Fidelity shape differs from the measured cut')


def validate_exemptions(references, manifest, exemptions):
    """The bound list is exact, not a runtime pattern granting an open-ended waiver."""
    controls = {(c['profile'], c['scene']) for c in manifest['cells']
                if c.get('family') == 'span' and c.get('span') in (128, 224)
                and c.get('level') in (0, 4, 28, 64)
                and c.get('background') == f'grey-{c.get("level"):03d}'}
    expected = [list(key(c)) for c in references['cells']
                if (c['profile'], c['scene']) in controls and c['statistic'] in EXTRA]
    if exemptions != expected:
        raise ValueError('Reported rows must be the exact enumerated neutral span extras')


def validate_empty_eligibility(references, manifest, exemptions, eligible):
    controls = {(c['profile'], c['scene']) for c in manifest['cells']
                if c.get('family') == 'span' and c.get('pose') == 'receded'
                and c.get('level') in (0, 4, 28)
                and c.get('background') == f'grey-{c.get("level"):03d}'
                and ((c.get('span') == 128 and c.get('role') != 'blind') or
                     (c.get('span') == 224 and c.get('role') == 'blind'))}
    expected = [list(key(c)) for c in references['cells']
                if (c['profile'], c['scene']) in controls and c['statistic'] == 'T1-full-silhouette']
    if eligible != expected or not {tuple(k) for k in eligible} <= {tuple(k) for k in exemptions}:
        raise ValueError('Empty-support eligibility differs from exact DL5b/DL5c identities')


def validate_empty_support(cell, eligible, repo, candidate=False):
    if key(cell) not in {tuple(k) for k in eligible} or cell.get('status') != 'UNMEASURED_EMPTY_SUPPORT':
        raise ValueError('Empty-support status is not eligible for this exact key')
    fields = ('native', 'current', 'fidelity', 'value', 'B') + (('candidate',) if candidate else ())
    if any(name not in cell or cell[name] is not None for name in fields):
        raise ValueError('Empty support requires explicit null readings, never analytical support or zero')
    witness = json.loads(pin_path(cell.get('emptySupportWitness'), repo, external=True).read_text())
    if witness.get('schema') != 'w50-empty-native-support-witness-1' or any(
            witness.get(k) != cell[k] for k in ('profile', 'scene')):
        raise ValueError('Empty-support witness has another native identity')
    native_path = pin_path(witness.get('nativeRead'), repo, external=True)
    raw = native_path.read_bytes()
    native = json.loads(gzip.decompress(raw) if native_path.name.endswith('.json.gz') else raw)
    if native.get('schema') != 'w50-native-role-read-1' or native.get('role') != cell['role']:
        raise ValueError('Empty-support witness must name the role-isolated native read')
    matches = [c for c in native.get('cells', []) if all(c.get(k) == cell[k] for k in ('profile', 'scene'))]
    if len(matches) != 1 or matches[0].get('role') != cell['role']:
        raise ValueError('Native support witness identity is missing or ambiguous')
    runs = matches[0].get('runs', [])
    if [r.get('run') for r in runs] != [1, 2, 3]:
        raise ValueError('Empty support requires all three native runs')
    scale = re.search(r'-([12])x-', cell['profile'])
    if not scale or native.get('canvas') != {'width': 512, 'height': 384}:
        raise ValueError('Native support witness has another canvas/scale')
    dpr = int(scale[1]); shape = [384*dpr, 512*dpr]
    for run in runs:
        reading = run.get('readings', {})
        support = reading.get('supports', {}).get('full-silhouette', {})
        statistic = reading.get('statistics', {}).get('T1-full-silhouette', {})
        if (support.get('status') != 'UNMEASURED_EMPTY_SUPPORT' or
                type(support.get('pixels')) is not int or support['pixels'] != 0 or
                support.get('maskShape') != shape or statistic.get('status') != 'UNMEASURED_EMPTY_SUPPORT' or
                'value' not in statistic or statistic['value'] is not None):
            raise ValueError('Native witness does not record empty detected support')
        try:
            raw = base64.b64decode(support['maskPackedBitsBase64'], validate=True)
        except (KeyError, ValueError) as error:
            raise ValueError('Missing native packed support mask') from error
        if len(raw) != (shape[0]*shape[1]+7)//8 or hashlib.sha256(raw).hexdigest() != support.get('maskPackedBitsSha256') or any(raw):
            raise ValueError('Native packed mask is changed, malformed or nonempty')


def validate_completion(original, completed, exemptions, repo, empty_support_keys=(),
                        owner_budget_keys=(), owner_contracts=None, owner_source=None):
    cells, after = original.get('cells', []), completed.get('cells', [])
    if not cells or [key(c) for c in cells] != [key(c) for c in after] or \
            len({key(c) for c in cells}) != len(cells):
        raise ValueError('Reference key membership/order changed')
    for name, value in original.items():
        if name != 'cells' and completed.get(name) != value:
            raise ValueError(f'Original reference metadata changed: {name}')
    expected_owners = [list(key(c)) for c in cells if c['statistic']=='owner-contracts']
    if list(owner_budget_keys) != expected_owners:
        raise ValueError('Owner null-budget keys must be the exact original owner-contracts inventory')
    owner = None
    if expected_owners:
        path = Path(__file__).with_name('owner_evidence.py')
        spec = importlib.util.spec_from_file_location('w50_owner_evidence_checker', path)
        checker = importlib.util.module_from_spec(spec)
        exec(compile(path.read_bytes(), str(path), 'exec'), checker.__dict__)
        owner = checker.OwnerEvidence(repo, owner_contracts, owner_source)
    exempt = {tuple(k) for k in exemptions}
    if len(exempt) != len(exemptions) or not exempt.issubset({key(c) for c in cells}):
        raise ValueError('Unknown/duplicate reported key')
    native = None
    for before, cell in zip(cells, after):
        for name, value in before.items():
            if name == 'status' or (name in FILLABLE and value is None):
                continue
            if name not in cell or cell[name] != value:
                raise ValueError(f'Original reference field changed: {key(cell)}/{name}')
        blind = cell.get('role') == 'blind'
        if blind:
            if set(cell) - set(before) - FILLABLE:
                raise ValueError('Blind completion admits no added statistics/metadata')
            if cell.get('status') != 'SEALED_BLIND' or any(
                    cell.get(name) is not None for name in ('native', 'current', 'fidelity', 'B')):
                raise ValueError('Blind reference must remain identity-only')
        elif cell['statistic']=='owner-contracts':
            if cell.get('status')!='MEASURED' or 'B' not in cell or cell['B'] is not None:
                raise ValueError('Owner laws remain MEASURED and gated with no invented scalar B')
            owner.validate(cell, cell.get('ownerEvidence'))
        elif cell.get('status') == 'UNMEASURED_EMPTY_SUPPORT':
            validate_empty_support(cell, empty_support_keys, repo)
        else:
            reading(cell)
            if key(cell) in exempt:
                if cell.get('status') != 'REPORTED' or cell.get('B') is not None:
                    raise ValueError('Reported span row requires REPORTED and null B')
            elif cell.get('status') != 'MEASURED' or not finite(cell.get('B')) or cell['B'] <= 0:
                raise ValueError('Gated reference requires MEASURED and positive finite B')
        if blind:
            # DL5g: an identity-only row cannot name pixels not yet captured. Preserve
            # original nulls; the separate exposure helper requires actual evidence later.
            for name in ('nativeEvidence', 'currentEvidence', 'currentMetadata'):
                if cell.get(name) != before.get(name):
                    raise ValueError('Blind pre-fit evidence must retain its original identity-only provenance')
        else:
            if before.get('nativeIdentity') and before.get('nativeEvidence') is None:
                if native is None:
                    path = Path(__file__).with_name('native_evidence.py')
                    spec = importlib.util.spec_from_file_location('w50_native_evidence_checker', path)
                    checker = importlib.util.module_from_spec(spec)
                    exec(compile(path.read_bytes(), str(path), 'exec'), checker.__dict__)
                    native = checker.NativeEvidence(repo, original.get('inputs', {}).get('bed'))
                native.validate(cell, cell.get('nativeEvidence'))
            for name in ('nativeEvidence', 'currentEvidence'):
                pin_path(cell.get(name), repo, external=True)
            if cell.get('currentMetadata') is not None:
                pin_path(cell['currentMetadata'], repo, external=True)
        if not cell.get('currentDocumentPair') or not cell.get('support') or not cell.get('role'):
            raise ValueError('Incomplete reference provenance')
        for history in cell.get('historical', []):
            if not history.get('documentPair') or not finite(history.get('maxGrowthInB')):
                raise ValueError('Incomplete historical reference')

    if owner is not None: owner.finish()
    if native is not None: native.finish()


def validate_proof(proof, kind, repo):
    if proof.get('schema') != 'w50-prefit-proof-1' or proof.get('kind') != kind or \
            proof.get('status') != 'PASS':
        raise ValueError(f'Missing measured pre-fit proof: {kind}')
    checks = proof.get('checks', [])
    if not checks or any(not c.get('id') or c.get('status') != 'PASS' for c in checks) or \
            len({c['id'] for c in checks}) != len(checks):
        raise ValueError(f'Incomplete pre-fit checks: {kind}')
    for field in ('sources', 'outputs'):
        if not proof.get(field):
            raise ValueError(f'Missing pre-fit {field}: {kind}')
        for pin in proof[field]:
            pin_path(pin, repo)
