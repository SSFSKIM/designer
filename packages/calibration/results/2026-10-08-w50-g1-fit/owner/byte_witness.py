#!/usr/bin/env python3
"""Witness frozen existing owner inputs by bytes, with no image decoding or referee.

This is a separate prospective act, not a reconstruction of capture-time hashes.
The caller supplies the externally frozen metadata-config hash. All previously
pinned bytes must still match; only its exact missing-pin inventory is witnessed.
Outputs are a new plain PrepareInputs document and its separate provenance record.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
CONFIG_SHA = '093ea234780182665100b59a6aca5f35b44b1be2d5f661afdab5700bd354c684'
METADATA_SHA = 'e478cf0e17f11ff223bf3e28bffcce7ca7a3e529b95d0f5a8a4ec913426f693d'
INVENTORY_SHA = 'a666c1b00f4b1aff48bddeca9dacc1c1bc05dcf83bf908efddbe46c24c322d0c'
WITNESS_COUNT = 1522
FULL_SHA = re.compile(r'^[0-9a-f]{64}$')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode()


def pinned_bytes(pin):
    if not FULL_SHA.fullmatch(pin.get('sha256') or ''):
        raise ValueError('Expected full original hash')
    data = Path(pin['path']).read_bytes()
    if digest(data) != pin['sha256']:
        raise ValueError(f"Original hash mismatch: {pin['path']}")
    return data


def hash_file(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def check_config_identity(config):
    pin = config.get('inventoryPin', {})
    if pin.get('sha256') != INVENTORY_SHA or not pin.get('path', '').endswith(
            '/packages/calibration/results/2026-10-08-w50-g0-declaration/references.json'):
        raise ValueError('Wrong original inventory identity')
    if config.get('schema') != 'w50-owner-inputs-metadata-1' or config.get('status') != 'BLOCKED':
        raise ValueError('Expected frozen blocked metadata config')
    if len(config.get('ownerKeys', [])) != 640 or len(set(config['ownerKeys'])) != 640:
        raise ValueError('Original owner inventory count differs')
    if [b['code'] for b in config['blockers']] != ['FRESH_WITNESS_REQUIRED']:
        raise ValueError('Metadata has unresolved identity/path blockers')


def load_config(path, expected_sha):
    pin = {'path': str(path), 'sha256': expected_sha}
    data = pinned_bytes(pin)
    if expected_sha != CONFIG_SHA:
        raise ValueError('External config hash differs from reviewed frozen config')
    config = json.loads(data)
    check_config_identity(config)
    return config, pin


def identity(row):
    return '/'.join(row[k] for k in ('profile', 'renderer', 'scene'))


def matrix_rows(pin):
    raw = json.loads(pinned_bytes(pin))
    if raw.get('schemaVersion') != 5:
        raise ValueError('Wrong matrix schema')
    result = {}
    for cell in raw['cells']:
        key, web = cell['key'], cell['key']['web']
        row = {'profile': key['profileKey'], 'scene': key['sceneId'],
               **{field: web[field] for field in
                  ('renderer', 'samplingBackend', 'capturePath', 'pixelSize')}}
        name = identity(row)
        if name in result:
            raise ValueError('Duplicate generation identity')
        result[name] = row
    return result


def check_metadata(row, metadata):
    for field, expected in [('sceneId', row['scene']), *[(f, row[f]) for f in
                            ('renderer', 'samplingBackend', 'capturePath', 'pixelSize')]]:
        if metadata.get(field) != expected:
            raise ValueError(f'Capture metadata mismatch: {field}')


def allowed_path(path, root):
    path, root = Path(path), Path(root)
    resolved_path, resolved_root = path.resolve(), root.resolve()
    if not path.is_absolute() or not resolved_path.is_relative_to(resolved_root):
        raise ValueError('Evidence path escapes its approved tree')
    if any(part.lower() in ('raw', 'blind')
           for candidate in (path, root, resolved_path, resolved_root) for part in candidate.parts):
        raise ValueError('Raw/blind evidence path refused')
    return path


def allowed_current_pin(pin, original, canonical):
    if pin != original or not FULL_SHA.fullmatch(original.get('sha256') or ''):
        raise ValueError('Current capture differs from original per-cell pin')
    path = Path(pin['path'])
    if path.is_relative_to(canonical):
        return allowed_path(path, canonical)
    # G0 also pinned exact scratch-control files. That pin admits this file, not
    # its directory or any alias into another tree; byte verification still follows.
    if path != path.resolve():
        raise ValueError('External original control path may not contain a symlink')
    return allowed_path(path, path.parent)


def check_requests(requests, expected):
    if len(requests) != WITNESS_COUNT or len(expected) != WITNESS_COUNT:
        raise ValueError('Fresh request inventory count differs')
    seen = set()
    for request in requests:
        path = request['path']
        if path in seen or path not in expected:
            raise ValueError('Unexpected or duplicate fresh request path')
        seen.add(path)
        wanted = expected[path]
        if request['kind'] != wanted['kind'] or set(request['cells']) != wanted['cells'] \
                or len(request['cells']) != len(wanted['cells']) \
                or request.get('status') != 'FRESH_WITNESS_REQUIRED' \
                or request.get('historicalCaptureTimePin') is not False:
            raise ValueError('Fresh request scope/provenance differs')


def resolve_inputs(inputs, hashes):
    result = copy.deepcopy(inputs)
    for section in ('captures', 'referenceCaptures'):
        for capture in result[section].values():
            for field in ('web', 'native', 'backdrop', 'metadata'):
                if field not in capture:
                    continue
                pin = capture[field]
                if pin['sha256'] is None:
                    sha = hashes.get(pin['path'])
                    if not FULL_SHA.fullmatch(sha or ''):
                        raise ValueError('Missing full fresh witness hash')
                    pin['sha256'] = sha
    return result


def write_pair(witness_path, witness, inputs_path, inputs):
    paths = [Path(witness_path), Path(inputs_path)]
    if paths[0] == paths[1] or any(not p.is_absolute() or p.parent.resolve() != HERE.resolve()
                                 for p in paths):
        raise ValueError('Outputs must be distinct direct children of the owner directory')
    if any(p.exists() or p.is_symlink() for p in paths):
        raise FileExistsError('Write-once output already occupied')
    made = []
    try:
        # Open both exclusively before writing either; a late collision removes only ours.
        for path in paths:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            made.append((path, descriptor))
        for (_, descriptor), value in zip(made, (witness, inputs)):
            data = encoded(value)
            with os.fdopen(os.dup(descriptor), 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
    except BaseException:
        for path, _ in made:
            path.unlink(missing_ok=True)
        raise
    finally:
        for _, descriptor in made:
            os.close(descriptor)


def witness(config_path, config_sha, witness_path, inputs_path):
    config, config_pin = load_config(config_path, config_sha)
    # Sources are verified before interpreting the source-bound input identities. No
    # helpers from either source are imported or executed by this standalone tool.
    metadata_pin = {'path': str(HERE / 'metadata.py'), 'sha256': METADATA_SHA}
    pinned_bytes(metadata_pin)
    source_pins = {'metadata.py': metadata_pin,
                   'byte_witness.py': {'path': str(Path(__file__).resolve()),
                                       'sha256': hash_file(Path(__file__).resolve())}}
    verified = {config_pin['path']: config_pin, metadata_pin['path']: metadata_pin}
    inputs = config['inputs']
    inventory = json.loads(pinned_bytes(config['inventoryPin']))
    verified[config['inventoryPin']['path']] = config['inventoryPin']
    declarations = {}
    for name, pin in {'scenes': inputs['declaration'], **config['additionalSources']}.items():
        declarations[name] = json.loads(pinned_bytes(pin))
        verified[pin['path']] = pin
    if inputs['python'] != str(HERE / 'python-shim'):
        raise ValueError('Wrong owner Python boundary')
    scenes = {s['id']: s for s in declarations['scenes']['scenes']}
    fixture_root = Path(config['additionalSources']['fixtureManifest']['path']).parent
    canonical = Path(inventory['generations']['b2d074d2df24-940384c06f73']['captureTree'])
    original_pins = {}
    for row in inventory['cells']:
        if row.get('currentGeneration') not in ('b2d074d2df24-940384c06f73', '0eac5b294cc2'):
            continue
        if all(row.get(f) for f in ('currentEvidence', 'nativeEvidence', 'currentMetadata')):
            pins = {'web': row['currentEvidence'], 'native': row['nativeEvidence'],
                    'metadata': row['currentMetadata']}
            cell = identity(row)
            if cell in original_pins and original_pins[cell] != pins:
                raise ValueError('Conflicting original current pins')
            original_pins[cell] = pins

    expected, capture_checks, fresh_hashes = {}, {}, {}
    original_to_hash = {}
    metadata_to_check = []
    for section, matrices in [('captures', inputs['current']), ('referenceCaptures', inputs['references'])]:
        rows, generation_of, documents_of = {}, {}, {}
        for matrix in matrices:
            generation = Path(matrix['matrix']['path']).stem
            projected = matrix_rows(matrix['matrix'])
            verified[matrix['matrix']['path']] = matrix['matrix']
            if sorted(projected) != config['generationMembership'].get(generation):
                raise ValueError('Generation membership differs from metadata config')
            for cell, row in projected.items():
                if cell in rows:
                    raise ValueError('Duplicate input generation identity')
                rows[cell], generation_of[cell], documents_of[cell] = row, generation, matrix['documents']
        if set(rows) != set(inputs[section]):
            raise ValueError('Capture maps differ from complete generation membership')
        for cell, row in rows.items():
            capture = inputs[section][cell]
            generation, documents = generation_of[cell], documents_of[cell]
            entries = re.findall(r'(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})(?![0-9a-f])',
                                 row['capturePath'])
            if len(entries) != 2 or {e[0] for e in entries} != {'materialProfile', 'recededProfile'} \
                    or len({e[1] for e in entries}) != 2 or len(documents) != 2 \
                    or capture['documents'] != documents \
                    or any(not FULL_SHA.fullmatch(documents.get(path, ''))
                           or documents[path][:12] != short for _, path, short in entries):
                raise ValueError('Generation document roles differ')
            native = original_pins[cell]['native']
            if capture['native'] != native or Path(native['path']) != fixture_root / row['profile'] / (row['scene'] + '.png'):
                raise ValueError('Original native pairing differs')
            allowed_path(native['path'], fixture_root)
            if section == 'captures':
                for field in ('web', 'metadata'):
                    allowed_current_pin(capture[field], original_pins[cell][field], canonical)
            else:
                tree = canonical.parent / 'web-captures-superseded' / generation
                if generation not in ('d0219cd684bf', 'eab099cc6698'):
                    raise ValueError('Wrong original historical generation')
                directory = tree / row['profile'] / row['scene']
                for field, name in [('web', f"{row['scene']}__{row['renderer']}.png"),
                                    ('metadata', f"cell__{row['renderer']}.json")]:
                    if capture[field]['path'] != str(directory / name) or capture[field]['sha256'] is not None:
                        raise ValueError('Historical fresh witness path differs')
                    allowed_path(capture[field]['path'], tree)
            scale = 2 if '-2x-' in row['profile'] else 1
            background = scenes[row['scene']]['background']
            name = f'{background}@{scale}x'
            declared_path = declarations['fixtureManifest']['backgrounds'].get(name)
            if declared_path != f'backgrounds/{name}.png' \
                    or capture['backdrop'] != {'path': str(fixture_root / declared_path), 'sha256': None}:
                raise ValueError('Backdrop differs from original fixture manifest')
            allowed_path(capture['backdrop']['path'], fixture_root)
            check_id = generation + '/' + cell
            capture_checks[check_id] = {'cell': cell, 'generation': generation,
                'metadataPath': capture['metadata']['path'], 'identityMatchesMatrix': True, 'nativePin': native,
                'nativePairing': 'Original G0 fixture pin matched by profile/scene; not a historical capture-time digest'}
            metadata_to_check.append((row, capture['metadata']))
            for field in ('web', 'native', 'backdrop', 'metadata'):
                pin = capture[field]
                if pin['sha256'] is not None:
                    previous = original_to_hash.setdefault(pin['path'], pin)
                    if previous != pin:
                        raise ValueError('Conflicting original hashes')
                    continue
                kind = 'backdrop' if field == 'backdrop' else 'historical-' + field
                request = expected.setdefault(pin['path'], {'kind': kind, 'cells': set(), 'generationMatches': set()})
                if request['kind'] != kind:
                    raise ValueError('Fresh path has multiple roles')
                request['cells'].add(cell)
                request['generationMatches'].add(check_id)
    check_requests(config['witnessRequirements'], expected)
    if {x['generation'] + '/' + x['cell']: x for x in config['captureIdentityChecks']} != capture_checks:
        raise ValueError('Capture identity provenance changed')
    for request in config['witnessRequirements']:
        if request['kind'] == 'backdrop':
            authority = request.get('authority', {})
            key = Path(request['path']).stem
            if authority != {'manifestPin': config['additionalSources']['fixtureManifest'],
                             'entry': 'backgrounds/' + key,
                             'declaredPath': declarations['fixtureManifest']['backgrounds'].get(key)}:
                raise ValueError('Backdrop manifest authority changed')

    # Only after all path and generation scopes are established are image bytes opened.
    for pin in original_to_hash.values():
        if hash_file(pin['path']) != pin['sha256']:
            raise ValueError(f"Original hash mismatch: {pin['path']}")
        verified[pin['path']] = pin
    for row, pin in metadata_to_check:
        data = Path(pin['path']).read_bytes()
        sha = digest(data)
        if pin['sha256'] is not None and sha != pin['sha256']:
            raise ValueError('Original metadata hash mismatch')
        if pin['sha256'] is None:
            fresh_hashes[pin['path']] = sha
        check_metadata(row, json.loads(data))
    for request in config['witnessRequirements']:
        if request['path'] not in fresh_hashes:
            fresh_hashes[request['path']] = hash_file(request['path'])
    resolved = resolve_inputs(inputs, fresh_hashes)
    fresh = []
    for request in config['witnessRequirements']:
        path = request['path']
        fresh.append({'path': path, 'sha256': fresh_hashes[path], 'kind': request['kind'],
            'cells': request['cells'], 'generationMatches': sorted(expected[path]['generationMatches']),
            'witnessKind': 'prospective-byte-only', 'historicalCaptureTimePin': False,
            **({'authority': request['authority']} if 'authority' in request else {})})
    result = {'schema': 'w50-owner-byte-witness-1', 'metadataConfig': config_pin,
              'resolvedInputs': {'path': str(inputs_path), 'sha256': digest(encoded(resolved))},
              'sourcePins': source_pins, 'originalVerified': sorted(verified.values(), key=lambda p: p['path']),
              'fresh': fresh, 'captureIdentityChecks': capture_checks,
              'scope': 'Existing canonical and original historical owner evidence; byte-only prospective witness, no decode or statistics'}
    # Refuse a moving input rather than claim that the frozen config was preserved.
    pinned_bytes(config_pin)
    write_pair(witness_path, result, inputs_path, resolved)
    return {'witness': str(witness_path), 'inputs': str(inputs_path),
            'freshPins': len(fresh), 'originalVerified': len(verified)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--config-sha256', required=True)
    parser.add_argument('--witness', type=Path, default=HERE / 'byte-witness.json')
    parser.add_argument('--inputs', type=Path, default=HERE / 'inputs-resolved.json')
    args = parser.parse_args()
    print(json.dumps(witness(args.config, args.config_sha256, args.witness, args.inputs)))
