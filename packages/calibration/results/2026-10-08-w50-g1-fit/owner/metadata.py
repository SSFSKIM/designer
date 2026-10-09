#!/usr/bin/env python3
"""Prepare blocked owner input metadata without opening any image bytes.

G0 remains the authority for current/native pins and owner membership. Matrix reads
project only identity, role and document descriptors, never their measured values.
Missing hashes are requests for a separately authorised prospective witness, not
fabricated capture-time pins. This script cannot run the owner referee or complete
those witnesses. Only the owner directory receives output.
"""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parents[1]
G0 = CAL / 'results/2026-10-08-w50-g0-declaration'
CURRENT = ('b2d074d2df24-940384c06f73', '0eac5b294cc2')
ORIGINAL = ('d0219cd684bf', 'eab099cc6698')
INVENTORY_SHA = 'a666c1b00f4b1aff48bddeca9dacc1c1bc05dcf83bf908efddbe46c24c322d0c'
FULL_SHA = re.compile(r'^[0-9a-f]{64}$')


def read_json(path):
    path = Path(path)
    if path.suffix != '.json':
        raise ValueError('Metadata reader accepts JSON only')
    return json.loads(path.read_text())


def source_pin(path):
    """Only called for declarative source files, never matrices or captures."""
    return {'path': str(path), 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()}


def locate(path):
    path = Path(path)
    if path.is_absolute():
        return path
    return (ROOT if str(path).startswith(('packages/', 'apps/')) else CAL) / path


def copy_pin(pin):
    if not isinstance(pin, dict) or not FULL_SHA.fullmatch(pin.get('sha256') or ''):
        raise ValueError('Pin requires full SHA256')
    return {'path': str(locate(pin['path'])), 'sha256': pin['sha256']}


def key(row):
    return '/'.join(row[k] for k in ('profile', 'renderer', 'scene'))


def owner_rows(inventory, expected=640):
    rows = [{k: r[k] for k in ('profile', 'renderer', 'scene', 'statistic')}
            for r in inventory['cells'] if r['statistic'] == 'owner-contracts']
    if len({key(r) for r in rows}) != len(rows):
        raise ValueError('Owner inventory contains duplicate identity')
    if len(rows) != expected:
        raise ValueError('Owner inventory count differs')
    return sorted(rows, key=key)


def matrix_identities(envelope):
    if envelope['schemaVersion'] != 5:
        raise ValueError('Expected schema5 generation')
    rows = []
    for raw in envelope['cells']:
        k, web = raw['key'], raw['key']['web']
        rows.append({'profile': k['profileKey'], 'renderer': web['renderer'],
                     'scene': k['sceneId'], **{f: web[f] for f in
                     ('samplingBackend', 'capturePath', 'pixelSize')},
                     'fixtureSet': raw['fixtureSet'], 'state': raw['state']})
    if len({key(r) for r in rows}) != len(rows):
        raise ValueError('Generation contains duplicate identity')
    return rows


def document_map(descriptor, pair):
    entries = re.findall(r'(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})(?![0-9a-f])',
                         descriptor)
    if len(entries) != 2 or len({r for r, _, _ in entries}) != 2 or len({p for _, p, _ in entries}) != 2:
        raise ValueError('Descriptor lacks unambiguous document pair')
    result = {}
    for role, path, short in entries:
        digest = pair['active.dark' if role == 'materialProfile' else 'receded.dark']
        if not FULL_SHA.fullmatch(digest) or digest[:12] != short:
            raise ValueError('Descriptor document role differs from original pair')
        result[path] = digest
    return result


def check_metadata(row, metadata):
    for field, expected in [('sceneId', row['scene']), *[(k, row[k]) for k in
                            ('renderer', 'samplingBackend', 'capturePath', 'pixelSize')]]:
        if metadata.get(field) != expected:
            raise ValueError(f'Capture identity mismatch: {field}')


def backdrop_from_manifest(manifest, fixture_root, background, scale):
    name = f'{background}@{scale}x'
    entry = manifest.get('backgrounds', {}).get(name)
    if entry != f'backgrounds/{name}.png':
        raise ValueError('Fixture manifest lacks exact background/scale path')
    return fixture_root / entry


def build():
    declaration = read_json(G0 / 'declaration.json')
    inventory_pin = next(copy_pin(p) for p in declaration['sources']
                         if p['path'].endswith('w50-g0-declaration/references.json'))
    if inventory_pin['sha256'] != INVENTORY_SHA or source_pin(Path(inventory_pin['path'])) != inventory_pin:
        raise ValueError('Original G0 reference inventory changed')
    inventory = read_json(inventory_pin['path'])
    owners = owner_rows(inventory)
    scene_pin = next(copy_pin(p) for p in declaration['sources']
                     if p['path'] == 'apps/reference-apple/scenes.json')
    if source_pin(Path(scene_pin['path'])) != scene_pin:
        raise ValueError('Original scene declaration changed')
    scenes = {s['id']: s for s in read_json(scene_pin['path'])['scenes']}
    # The W33 sealing manifest records full hashes, unlike its twelve-hex index aliases.
    historical_manifest = CAL / 'results/2026-09-22-w33-g1b-rim-fit/sealed-manifest.json'
    manifest = read_json(historical_manifest)
    historical_index = CAL / 'results/superseded/index.json'
    index = read_json(historical_index)
    original_name = index['byDocumentSha256']['eab099cc6698']
    if original_name != 'eab099cc6698.json':
        raise ValueError('Original owner baseline alias changed')
    documents = manifest['documents']
    pair05 = {'active.dark': documents['apple-macos-27.0-1x-dark-standard-glass0.5.json']['fileSha256'],
              'receded.dark': documents['apple-macos-27.0-1x-dark-standard-glass0.5-receded.json']['fileSha256']}
    if pair05['active.dark'][:12] != 'eab099cc6698' or pair05['receded.dark'][:12] != '4e68f81869f6':
        raise ValueError('Original 0.5 baseline document pair changed')
    canonical = Path(inventory['generations'][CURRENT[0]]['captureTree'])
    generations = {g: inventory['generations'][g] for g in (*CURRENT, ORIGINAL[0])}
    generations[ORIGINAL[1]] = {
        'matrix': {'path': str(CAL / 'results/superseded' / original_name),
                   'sha256': index['files'][original_name]['sha256']},
        'documentPair': pair05,
        'captureTree': str(canonical.parent / 'web-captures-superseded' / ORIGINAL[1])}

    # Merge only pins from G0 rows; numerical and blind fields never enter this projection.
    current_pins = {}
    for row in inventory['cells']:
        if row.get('currentGeneration') not in CURRENT:
            continue
        fields = ('nativeEvidence', 'currentEvidence', 'currentMetadata')
        if not all(row.get(f) for f in fields):
            continue
        pins = {f: copy_pin(row[f]) for f in fields}
        cell = key(row)
        if cell in current_pins and current_pins[cell] != pins:
            raise ValueError('Conflicting original G0 pins for one current identity')
        current_pins[cell] = pins

    fixture_roots = {Path(p['nativeEvidence']['path']).parent.parent for p in current_pins.values()}
    if len(fixture_roots) != 1:
        raise ValueError('Original native pins do not share one fixture root')
    fixture_root = next(iter(fixture_roots))
    fixture_manifest_path = fixture_root / 'manifest.json'
    fixture_manifest_pin = source_pin(fixture_manifest_path)
    fixture_manifest = read_json(fixture_manifest_path)
    blockers, requests, checks = [], {}, []
    def missing(code, **fields):
        blockers.append({'code': code, **fields})

    def existing(pin, kind):
        if not Path(pin['path']).is_file():
            missing('MISSING_PATH', kind=kind, path=pin['path'])
        return pin

    def required(path, kind, cell):
        path = str(path)
        if path not in requests:
            requests[path] = {'path': path, 'kind': kind, 'status': 'FRESH_WITNESS_REQUIRED',
                              'historicalCaptureTimePin': False, 'cells': []}
            if not Path(path).is_file():
                missing('MISSING_PATH', kind=kind, path=path)
        if cell not in requests[path]['cells']:
            requests[path]['cells'].append(cell)
        return {'path': path, 'sha256': None}

    inputs = {'declaration': scene_pin, 'current': [], 'references': [],
              'captures': {}, 'referenceCaptures': {}, 'python': str(HERE / 'python-shim')}
    membership = {}
    for generation in (*CURRENT, *ORIGINAL):
        gen = generations[generation]
        matrix_pin = existing(copy_pin(gen['matrix']), 'matrix')
        if not Path(matrix_pin['path']).is_file():
            continue
        rows = matrix_identities(read_json(matrix_pin['path']))
        membership[generation] = sorted(key(r) for r in rows)
        maps = [document_map(r['capturePath'], gen['documentPair']) for r in rows]
        if not maps or any(m != maps[0] for m in maps):
            raise ValueError('Mixed document descriptors within generation')
        docs = maps[0]
        reference = generation in ORIGINAL
        inputs['references' if reference else 'current'].append({'matrix': matrix_pin, 'documents': docs})
        for row in rows:
            cell = key(row)
            if cell not in current_pins:
                missing('MISSING_ORIGINAL_CURRENT_PINS', cell=cell, generation=generation)
                continue
            pins = current_pins[cell]
            native = existing(pins['nativeEvidence'], 'native')
            # G0 native path, profile and scene bind both generations to the same fixed fixture.
            native_path = Path(native['path'])
            if native_path.parent.name != row['profile'] or native_path.name != row['scene'] + '.png':
                raise ValueError('Original native pin differs from profile/scene identity')
            if reference:
                directory = Path(gen['captureTree']) / row['profile'] / row['scene']
                web = required(directory / f"{row['scene']}__{row['renderer']}.png", 'historical-web', cell)
                metadata = required(directory / f"cell__{row['renderer']}.json", 'historical-metadata', cell)
            else:
                web = existing(pins['currentEvidence'], 'current-web')
                metadata = existing(pins['currentMetadata'], 'current-metadata')
            scene = scenes.get(row['scene'])
            if scene is None:
                missing('MISSING_DECLARED_SCENE', cell=cell)
                continue
            scale = 2 if '-2x-' in row['profile'] else 1
            try:
                backdrop_path = backdrop_from_manifest(fixture_manifest, fixture_root, scene['background'], scale)
            except ValueError as error:
                missing('MISSING_FIXTURE_MANIFEST_MAPPING', cell=cell, reason=str(error))
                continue
            backdrop = required(backdrop_path, 'backdrop', cell)
            requests[str(backdrop_path)]['authority'] = {
                'manifestPin': fixture_manifest_pin, 'entry': f"backgrounds/{scene['background']}@{scale}x",
                'declaredPath': fixture_manifest['backgrounds'][f"{scene['background']}@{scale}x"]}
            if Path(metadata['path']).is_file():
                try:
                    check_metadata(row, read_json(metadata['path']))
                except ValueError as error:
                    missing('METADATA_IDENTITY_MISMATCH', cell=cell, generation=generation,
                            path=metadata['path'], reason=str(error))
                else:
                    checks.append({'cell': cell, 'generation': generation, 'metadataPath': metadata['path'],
                                   'identityMatchesMatrix': True, 'nativePin': native,
                                   'nativePairing': 'Original G0 fixture pin matched by profile/scene; not a historical capture-time digest'})
            capture = {'web': web, 'native': native, 'backdrop': backdrop,
                       'metadata': metadata, 'documents': docs}
            inputs['referenceCaptures' if reference else 'captures'][cell] = capture
    current_keys = {k for g in CURRENT for k in membership.get(g, [])}
    for owner in owners:
        if key(owner) not in current_keys:
            missing('OWNER_NOT_IN_CURRENT_GENERATION', cell=key(owner))
    if requests:
        missing('FRESH_WITNESS_REQUIRED', paths=len(requests),
                reason='No new image or metadata hashes computed; complete under separately authorised byte-only guard')
    return {'schema': 'w50-owner-inputs-metadata-1', 'status': 'BLOCKED' if blockers else 'METADATA_ONLY',
            'inventoryPin': inventory_pin, 'ownerKeys': [key(r) for r in owners], 'ownerRows': owners,
            'inputs': inputs, 'blockers': blockers,
            'witnessRequirements': sorted(requests.values(), key=lambda r: r['path']),
            'generationMembership': membership, 'captureIdentityChecks': checks,
            'additionalSources': {'original05Index': source_pin(historical_index),
                                  'original05DocumentHashes': source_pin(historical_manifest),
                                  'fixtureManifest': fixture_manifest_pin},
            'verification': {'imagesOpened': False, 'imageHashesComputed': False,
                             'generationFileHashesRecomputed': False,
                             'ownerRefereeExecuted': False,
                             'note': 'Existing pin retention and identity checks only; this is not runnable PrepareInputs.'}}


if __name__ == '__main__':
    result = build()
    output = HERE / 'inputs-metadata.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'ownerKeys': len(result['ownerKeys']),
                      'currentCaptureKeys': len(result['inputs']['captures']),
                      'referenceCaptureKeys': len(result['inputs']['referenceCaptures']),
                      'witnessPaths': len(result['witnessRequirements']),
                      'blockers': len(result['blockers']), 'output': str(output)}))
