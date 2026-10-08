"""Independently bind numerical results to the fixed producer, runtime and measured cohort.

A PASS flag is not provenance. The producer's runtime closure is discovered separately on
the assembled G0 tree and pinned by the root; every report must name that exact closure and
complete candidate/argument/reference bytes. This verifier never opens blind pixels.
"""
import hashlib
import json
import math
from pathlib import Path
import re

BASE = 'packages/calibration/results/2026-10-08-w50-g0-declaration'
PRODUCER = f'{BASE}/audit/numerical.ts'
CLOSURE = f'{BASE}/audit/runtime-closure.json'
REFERENCES = f'{BASE}/references.json'
REQUIRED_RUNTIME = (PRODUCER, 'pnpm-lock.yaml', 'packages/platform-web/src/optics.ts',
    'packages/renderer-webgpu/src/material.ts', 'packages/calibration/scripts/candidate-document.ts',
    'packages/platform-web/src/material-document.ts')
ARGUMENT_PROJECTION = ('id', 'candidateSha256', 'position', 'pose', 'dpr', 'span', 'role',
                       'profile', 'renderer', 'scene', 'variant')
HASH = re.compile(r'[0-9a-f]{64}')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_pin(pin, root):
    if (not isinstance(pin, dict) or not isinstance(pin.get('path'), str) or
            not isinstance(pin.get('sha256'), str) or not HASH.fullmatch(pin['sha256']) or
            Path(pin['path']).is_absolute()):
        raise ValueError('Missing repository-relative content pin')
    path = (root / pin['path']).resolve()
    if not path.is_relative_to(root) or not path.is_file() or sha(path) != pin['sha256']:
        raise ValueError(f'Pinned numerical input changed: {pin["path"]}')
    if str(path.relative_to(root)) != pin['path']:
        raise ValueError('Numerical pin uses a noncanonical path')
    return path


def pin_map(pins, root):
    if not isinstance(pins, list) or not pins:
        raise ValueError('Missing numerical source provenance')
    result = {}
    for pin in pins:
        read_pin(pin, root)
        if pin['path'] in result:
            raise ValueError('Duplicate numerical source pin')
        result[pin['path']] = pin['sha256']
    return result


def required_arguments(inventory):
    if inventory.get('schema') != 'w50-reference-inventory-1' or not inventory.get('cells'):
        raise ValueError('Missing fixed low-end reference population')
    result = {}
    for cell in inventory['cells']:
        if cell['role'] in ('blind', 'historical-prediction-check'):
            continue
        scene = cell['scene']
        uniform = re.fullmatch(r'cell-grey-(\d{3})-s\d+__(rest|inactive)', scene)
        selected = (re.fullmatch(r'impulse__rrect-(ml|lg)__(rest|inactive)', scene) or
                    re.fullmatch(r'dark-solid__[^_]+__(rest|inactive)', scene) or
                    re.fullmatch(r'cell-(impulse-sparse|checker-low)-s\d+__(rest|inactive)', scene) or
                    (uniform and int(uniform[1]) <= 64))
        if selected:
            identity = f'{cell["profile"]}|{cell["renderer"]}|{scene}'
            if identity in result and result[identity]['role'] != cell['role']:
                raise ValueError('Reference has conflicting measured roles')
            result[identity] = cell
    if not result:
        raise ValueError('UNMEASURED: fixed low-end argument population is empty')
    return result


def validate_tone_values(record):
    values = [record.get('encodedLuminance'), record.get('linearLuminance')]
    rgb = record.get('rgb')
    if not isinstance(rgb, list) or len(rgb) != 3:
        raise ValueError('Measured argument has no linear RGB')
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1
           for v in values + rgb):
        raise ValueError('Invalid independent measured tone arguments')
    # The scene's declared identity fixes the measured population. Preserve observed means,
    # including grey64's f32 value just above64/255; the runtime owns its <64 stand-down.
    # Independent GPU reductions agree within gamma8, not an arbitrary double-precision bar.
    unit_roundoff = 2 ** -24
    rounding = (8 * unit_roundoff / (1 - 8 * unit_roundoff)) * max(*rgb, values[1]) + 8 * 2 ** -149
    if abs(sum(v*w for v,w in zip(rgb, (0.2126,0.7152,0.0722))) - values[1]) > rounding:
        raise ValueError('Independent RGB/Y reductions differ beyond the binary32 bound')
    return values, rgb


def validate_endpoint_identity(profile_key, slot, position):
    """Read the candidate's numeric material position without accepting shipped identities.

    Candidate mode deliberately uses non-shipped decimal spellings such as 0.250/0.500.
    The glass token is numeric; OS, scale, scheme and the receded suffix remain exact.
    """
    if slot not in ('active.light', 'active.dark', 'receded.light', 'receded.dark') or position not in (0.25, 0.5):
        raise ValueError('Endpoint slot or position is outside W50 candidate scope')
    match = re.fullmatch(r'apple-macos-27\.0-1x-(light|dark)-standard-glass'
                         r'([0-9]+(?:\.[0-9]+)?)(-receded)?', profile_key) if isinstance(profile_key, str) else None
    pose, scheme = slot.split('.')
    if (not match or match[1] != scheme or float(match[2]) != position or
            bool(match[3]) != (pose == 'receded')):
        raise ValueError('Candidate endpoint OS/scale/scheme/position/pose differs from cohort')
    if match[2] == str(position):
        raise ValueError('Candidate endpoint uses a shipped identity instead of a candidate key')


def validate_provenance(report, candidate_sha, root):
    root = Path(root).resolve()
    sources = pin_map(report.get('sources'), root)
    producer = report.get('producer')
    if not isinstance(producer, dict) or producer.get('path') != PRODUCER:
        raise ValueError('Numerical report names no fixed producer')
    read_pin(producer, root)
    witness_path = root / CLOSURE
    if not witness_path.is_file():
        raise ValueError('UNMEASURED: assembled numerical runtime closure is not recorded')
    witness = json.loads(witness_path.read_text())
    if witness.get('schema') != 'w50-numerical-runtime-closure-1':
        raise ValueError('Wrong numerical runtime closure witness')
    runtime = pin_map(report.get('runtimeSources'), root)
    if runtime != pin_map(witness.get('sources'), root) or not set(REQUIRED_RUNTIME).issubset(runtime):
        raise ValueError('Numerical exercised runtime closure is incomplete or changed')
    if runtime.get(PRODUCER) != producer['sha256']:
        raise ValueError('Numerical producer is not in the exercised runtime')
    expected_sources = dict(runtime)

    def read(pin):
        path = read_pin(pin, root)
        expected_sources[pin['path']] = pin['sha256']
        return path, json.loads(path.read_text())

    _, cohort = read(report.get('cohort'))
    if cohort.get('schema') != 'w50-numerical-cohort-1':
        raise ValueError('Missing explicit numerical cohort')
    candidates = report.get('candidateDocuments')
    if (not isinstance(candidates, list) or len(candidates) != 2 or
            candidates != cohort.get('candidates') or
            sorted(c.get('position', -1) for c in candidates) != [0.25, 0.5]):
        raise ValueError('Candidate document cohort/positions differ')
    positions = {}
    for pin in candidates:
        path, candidate = read(pin)
        position = pin['position']
        if (candidate.get('kind') != 'vitrea-candidate-material-document' or
                candidate.get('schemaVersion') != 1 or candidate.get('glassTintAmount') != position):
            raise ValueError('Candidate bytes do not name the declared glass position')
        positions[position] = pin['sha256']
        endpoints = candidate.get('endpoints', {})
        if set(endpoints) != {'active.light', 'active.dark', 'receded.light', 'receded.dark'}:
            raise ValueError('Incomplete numerical candidate endpoints')
        endpoint_documents = {}
        for slot, endpoint_pin in endpoints.items():
            endpoint_path = (path.parent / endpoint_pin['path']).resolve()
            if not endpoint_path.is_relative_to(root):
                raise ValueError('Candidate endpoint escapes repository')
            _, endpoint = read({'path': str(endpoint_path.relative_to(root)),
                                'sha256': endpoint_pin['sha256']})
            validate_endpoint_identity(endpoint.get('profileKey'), slot, position)
            endpoint_documents[slot] = endpoint
        active_strength = endpoint_documents['active.dark'].get('patch', {}).get('lowEndStrength', 0)
        receded_strength = endpoint_documents['receded.dark'].get('patch', {}).get('lowEndStrength', active_strength)
        if active_strength != 1 or receded_strength != 1:
            raise ValueError('Current gate0 documents are not live-chart numerical candidates')
    hashes = sorted(positions.values())
    if len(set(hashes)) != 2 or hashes != report.get('candidateSha256s') or candidate_sha not in hashes:
        raise ValueError('Requested candidate is not the measured numerical cohort')
    argument_pin = report.get('argumentManifest')
    if argument_pin != cohort.get('structuredArguments'):
        raise ValueError('Argument manifest differs from candidate cohort')
    _, manifest = read(argument_pin)
    reference_pin = report.get('referenceInventory')
    if (not isinstance(reference_pin, dict) or reference_pin.get('path') != REFERENCES or
            reference_pin != manifest.get('references')):
        raise ValueError('Measured argument population is not the fixed reference inventory')
    _, inventory = read(reference_pin)
    required = required_arguments(inventory)
    ids = sorted(required)
    records = manifest.get('records')
    if (manifest.get('schema') != 'w50-structured-arguments-1' or
            sorted(manifest.get('candidateSha256s', [])) != hashes or
            manifest.get('requiredIds') != ids or not isinstance(records, list) or
            sorted(r.get('id', '') for r in records) != ids or
            report.get('structuredArgumentIds') != ids or report.get('requiredStructuredArgumentIds') != ids):
        raise ValueError('Incomplete declared measured low-end argument population')
    projections = []
    non_equivalent = set()
    for record in records:
        reference = required[record['id']]
        match = re.fullmatch(r'apple-macos-27\.0-([12])x-dark-standard-glass(0\.25|0\.5)', record['profile'])
        pose = 'receded' if record['scene'].endswith('__inactive') else 'active'
        if (not match or record.get('dpr') != int(match[1]) or
                record.get('position') != float(match[2]) or record.get('pose') != pose or
                any(record.get(k) != reference[k] for k in ('profile', 'renderer', 'scene', 'role')) or
                record.get('candidateSha256') != positions.get(record.get('position')) or
                record.get('variant') not in ('regular', 'clear') or
                not isinstance(record.get('span'), (float, int)) or not 32 <= record['span'] <= 224):
            raise ValueError('Measured argument identity differs from fixed reference/candidate')
        values, rgb = validate_tone_values(record)
        decoded = values[0] / 12.92 if values[0] <= 0.04045 else ((values[0] + 0.055) / 1.055) ** 2.4
        if abs(decoded - values[1]) > 1e-12:
            non_equivalent.add(f'{record["position"]}:{record["pose"]}:{record["dpr"]}')
        fields = {k: v for k, v in record.items() if k != 'evidence'}
        _, evidence = read(record.get('evidence'))
        if evidence != {'schema': 'w50-measured-tone-argument-1', **fields}:
            raise ValueError('Numerical argument differs from measured evidence bytes')
        projections.append({k: record[k] for k in ARGUMENT_PROJECTION})
    coverage = sorted(f'{position}:{pose}:{dpr}' for position in (0.25, 0.5)
                      for pose in ('active', 'receded') for dpr in (1, 2))
    if (report.get('structuredArguments') != projections or
            report.get('structuredCoverage') != coverage or not set(coverage).issubset(non_equivalent)):
        raise ValueError('Numerical reported arguments or independent-mean coverage differ from measured records')
    if report.get('negativeRequests') != []:
        raise ValueError('Numerical report is missing unclamped diagnostics or records negative requests')
    if sources != expected_sources:
        raise ValueError('Numerical source union differs from complete runtime/input closure')
