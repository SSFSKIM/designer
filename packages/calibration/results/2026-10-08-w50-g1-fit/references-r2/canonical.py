"""Prospective canonical REFERENCE evidence reader, never a coefficient input or verdict.

Callers supply pinned declarations/publication metadata and explicit source roots. Nothing
is discovered from the machine. W29 commits admission metadata, not per-PNG digests: those
seven image hashes are freshly witnessed before decoding and rechecked at decode, never
called historical capture-time pins. Published bytes/capturedAt must belong to the selected
raw state. W43 has the stronger inventory + admission frame binding. Neither source may
lend repeats/bars to the other glass position. No new W50 512x384 or blind input is accepted.

Missing, changed, unadmitted or unmeasurable evidence is UNMEASURED with its reason; there
is no alternate mask, assumed bar or source fallback. Historical spread is reported only.
All roles remain separated; this module emits no fit summary, coefficients or gate result.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
from pathlib import Path
import re
import types

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
W43_READER = HERE.parents[1]/'2026-10-01-w43-g0-declaration/bed/sitting/w43_archive.py'


def module(name, path):
    value = types.ModuleType(name); value.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), value.__dict__)
    return value


M = module('w50_canonical_metrics', HERE/'statistics.py')
A = module('w50_canonical_w43_archive', W43_READER)
ROLES = ('gate', 'historical-prediction-check', 'reference-only')
PROFILE = re.compile(r'apple-macos-27\.0-([12])x-(dark|light)-standard-glass(0\.25|0\.5)$')
PASSES = tuple(f'standard-{pose}-{scale}x' for scale in (1, 2) for pose in ('active', 'inactive'))


class EvidenceUnavailable(ValueError):
    pass


def sha(raw): return hashlib.sha256(raw).hexdigest()


def digest(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise EvidenceUnavailable('Missing full evidence SHA-256')
    return value


def read_pin(item):
    if not isinstance(item, dict) or not isinstance(item.get('path'), str):
        raise EvidenceUnavailable('Missing evidence file pin')
    path = Path(item['path']); path = path if path.is_absolute() else REPO/path
    if path.is_symlink() or not path.is_file():
        raise EvidenceUnavailable('Missing or symlinked evidence: '+str(path))
    raw = path.read_bytes()
    if sha(raw) != digest(item.get('sha256')):
        raise EvidenceUnavailable('Changed evidence bytes: '+str(path))
    return raw


def json_pin(item):
    try: return json.loads(read_pin(item))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise EvidenceUnavailable('Unreadable evidence JSON') from error


def safe(root, relative):
    if not isinstance(relative, str): raise EvidenceUnavailable('Missing source file path')
    part = Path(relative)
    if part.is_absolute() or '..' in part.parts or not part.parts or str(part) != relative:
        raise EvidenceUnavailable('Source path escapes its root')
    current = Path(root).resolve()
    for name in part.parts:
        current /= name
        if current.is_symlink(): raise EvidenceUnavailable('Source symlink is not evidence')
    return current


def file_pin(path):
    if not path.is_file() or path.is_symlink():
        raise EvidenceUnavailable('Missing source file: '+str(path))
    return {'path': str(path.resolve()), 'sha256': sha(path.read_bytes())}


def fields(raw):
    return dict(line.split('=', 1) for line in raw.decode().splitlines() if '=' in line)


def attest_pair(opened, closed, *, pass_name, scale, position, spec_hash=None, full_drift=False):
    reads = (fields(opened), fields(closed))
    for phase, item in zip(('open', 'close'), reads):
        if item.get('phase') != phase or item.get('pass') != pass_name \
                or item.get('osProductVersion') != '27.0' or item.get('osBuild') != '26A428' \
                or item.get('glassTintAmount') != position or item.get('reduceTransparency') != '0' \
                or item.get('increaseContrast') != '0' or item.get('a11yMode') != 'standard' \
                or item.get('showBorders') != '0' \
                or item.get('displayplacerMode') != ('68' if scale == 2 else '69') \
                or item.get('displayModeDeclaredForScale') != ('68' if scale == 2 else '69'):
            raise EvidenceUnavailable('Source OS/glass/scale/pose/pass attestation mismatch')
        digest(item.get('bundleBinarySha256')); digest(item.get('passSpecSha256'))
        if spec_hash is not None and item['passSpecSha256'] != spec_hash:
            raise EvidenceUnavailable('Source pass specification differs from its attestation')
    keys = set(reads[0]) | set(reads[1]) if full_drift else {
        'osProductVersion', 'osBuild', 'glassTintAmount', 'reduceTransparency', 'increaseContrast',
        'a11yMode', 'showBorders', 'displayplacerMode', 'displayModeDeclaredForScale',
        'bundlePath', 'bundleBinarySha256', 'bundleMinOS', 'bundleRecordedSdk', 'passSpecSha256'}
    if any(reads[0].get(k) != reads[1].get(k) for k in keys-{'phase', 'readAt'}):
        raise EvidenceUnavailable('Source opening/closing configuration drift')
    return reads


def native_entry(entry, key, scale, state, canvas):
    active = state in ('rest', 'pressed')
    if entry.get('file') != key+'/'+entry.get('sceneId', '')+'.png' \
            or entry.get('captureMethod') != 'screencapturekit' \
            or entry.get('deterministic') is not True or entry.get('materialRendered') is not True \
            or entry.get('presentedActive') is not active \
            or [entry.get('width'), entry.get('height')] != [canvas['width']*scale, canvas['height']*scale]:
        raise EvidenceUnavailable('Source native identity/pose/scale/material admission mismatch')
    if not active:
        p = entry.get('presentation') or {}
        if p.get('observedPose') != 'inactive' or p.get('isKeyWindow') is not False \
                or p.get('appIsActive') is not False:
            raise EvidenceUnavailable('Source inactive presentation is not attested')
    if not isinstance(entry.get('capturedAt'), str) or not entry['capturedAt']:
        raise EvidenceUnavailable('Source native capture timestamp is missing')


def manifest_profiles(manifest, *, scale, position, pose, scenes):
    hardware = manifest.get('hardware') or {}
    if not re.search(r'\b27\.0\b', hardware.get('osVersion', '')) or hardware.get('osBuild') != '26A428':
        raise EvidenceUnavailable('Source manifest OS/build admission mismatch')
    result = {}
    by_scene = {s['id']: s for s in scenes['scenes']}
    for header in manifest.get('profiles', []):
        key = header.get('profileKey'); match = PROFILE.fullmatch(key or '')
        if not match or int(match[1]) != scale or match[3] != position or key in result:
            raise EvidenceUnavailable('Source profile does not name its own OS/scale/glass position')
        display = header.get('display') or {}
        if display.get('actualBackingScale') != scale or display.get('requestedScale') != scale \
                or display.get('pixelSize') != [scenes['canvas']['width']*scale, scenes['canvas']['height']*scale] \
                or display.get('colorSpace') != 'kCGColorSpaceSRGB' \
                or header.get('a11yMode') != 'standard' or header.get('colorScheme') != match[2]:
            raise EvidenceUnavailable('Source profile scale/colour/accessibility admission mismatch')
        entries = {}
        for entry in header['fixtures']:
            sid = entry['sceneId']
            if sid in entries or sid not in by_scene \
                    or (by_scene[sid]['state'] == 'inactive') != (pose == 'inactive'):
                raise EvidenceUnavailable('Source fixture is duplicate, foreign or in another pose')
            native_entry(entry, key, scale, by_scene[sid]['state'], scenes['canvas'])
            entries[sid] = entry
        result[key] = {'header': copy.deepcopy(header), 'entries': entries}
    if not result: raise EvidenceUnavailable('Source manifest has no admitted profiles')
    return result


def verify_w29_source(config):
    provenance = json_pin(config['provenance']); root = Path(config['root']).resolve()
    if root != Path(provenance['sittingDir']).expanduser().resolve():
        raise EvidenceUnavailable('W29 source root differs from its committed provenance')
    output = {'kind': 'W29', 'provenance': copy.deepcopy(config['provenance']), 'runs': [], 'passes': {}}
    for name in PASSES:
        p = provenance['passes'].get(name)
        if p is None or [r.get('run') for r in p['runs']] != [f'run-{n}' for n in range(1, 8)]:
            raise EvidenceUnavailable('W29 requires the exact seven named repetitions for all four standard passes')
        scale = int(name[-2]); pose = 'inactive' if '-inactive-' in name else 'active'
        spec_path = safe(root, p['passSpec']); spec_pin = {'path': str(spec_path), 'sha256': p['passSpecSha256']}
        spec = json_pin(spec_pin)
        captured = []
        for row in p['runs']:
            run_root = safe(root, name+'/'+row['run'])
            pins = {label: {'path': str(safe(run_root, filename)), 'sha256': row[field]}
                for label, filename, field in (('manifest', 'manifest.json', 'manifestSha256'),
                    ('open', 'attest.read', 'attestReadSha256'), ('close', 'attest.close', 'attestCloseSha256'))}
            manifest = json_pin(pins['manifest'])
            attestations = attest_pair(read_pin(pins['open']), read_pin(pins['close']), pass_name=name,
                scale=scale, position='0.5', spec_hash=p['passSpecSha256'], full_drift=True)
            profiles = manifest_profiles(manifest, scale=scale, position='0.5', pose=pose, scenes=spec)
            if sorted(profiles) != sorted(p['profiles']) or \
                    sum(len(v['entries']) for v in profiles.values()) != row['cells']:
                raise EvidenceUnavailable('W29 manifest profile/cell membership differs from provenance')
            stamps = sorted(f['capturedAt'] for v in profiles.values() for f in v['entries'].values())
            if ('firstCapturedAt' in row and row['firstCapturedAt'] != stamps[0]) or \
                    ('lastCapturedAt' in row and row['lastCapturedAt'] != stamps[-1]):
                raise EvidenceUnavailable('W29 native timestamps differ from committed provenance')
            record = {'label': 'r'+row['run'][4:], 'directory': str(run_root), 'pins': pins,
                      'profiles': profiles, 'backgrounds': manifest.get('backgrounds', {}),
                      'attestations': attestations, 'hardware': manifest['hardware']}
            captured.append(record)
            output['runs'].append({'pass': name, 'label': record['label'], 'pins': pins})
        output['passes'][name] = {'spec': spec, 'specPin': spec_pin, 'runs': captured}
    output['frameHashBinding'] = 'FRESHLY_WITNESSED_NOT_CAPTURE_TIME_PINNED'
    return output


def verify_w43_source(config):
    fetch = json_pin(config['fetch']); root = Path(config['root']).resolve()
    if fetch.get('tag') != 'w43-archive-g1a': raise EvidenceUnavailable('Wrong canonical0.25 archive generation')
    digest(fetch.get('sha256')); digest(fetch.get('inventorySha256'))
    inventory_pin = {'path': str(root/'inventory.json'), 'sha256': fetch['inventorySha256']}
    inventory = json_pin(inventory_pin)
    if inventory.get('schema') != A.SCHEMA or inventory.get('sitting') != 'g1a' \
            or not isinstance(inventory.get('sources', {}).get('canonical'), str):
        raise EvidenceUnavailable('Wrong W43 canonical archive/source identity')
    if inventory.get('producer', {}).get('w43_archive.py') != sha(W43_READER.read_bytes()):
        raise EvidenceUnavailable('W43 recorded archive reader source differs')
    try: verification = A.verify_tree(root)
    except (ValueError, OSError) as error: raise EvidenceUnavailable(str(error)) from error
    if verification['inventorySha256'] != fetch['inventorySha256']:
        raise EvidenceUnavailable('W43 inventory hash mismatch')
    return {'kind': 'W43', 'root': root, 'inventory': inventory, 'fetch': copy.deepcopy(config['fetch']),
            'inventoryPin': inventory_pin, 'archiveAssetSha256': fetch['sha256'],
            'frameHashBinding': 'ARCHIVE_INVENTORY_AND_ADMISSION_PINNED'}


def declared(value):
    """A declaration's geometry without its `$`-prefixed annotations.

    scenes.json records rulings beside a component as `$comment…` keys (W32 G0 added
    `$comment-w32-g0` to rrect-ml after W29 captured it). An annotation is prose, never a
    dimension, so equality is taken over every other key, recursively. The first W50 reference
    read compared whole dicts and refused all 26 dark 0.5 rrect-ml rows on that comment alone.
    """
    if isinstance(value, dict):
        return {k: declared(v) for k, v in value.items() if not str(k).startswith('$')}
    if isinstance(value, list): return [declared(v) for v in value]
    return value


def same_geometry(source, canonical, sid):
    own = next((s for s in source['scenes'] if s['id'] == sid), None)
    current = next((s for s in canonical['scenes'] if s['id'] == sid), None)
    if own is None or current is None or declared(source['canvas']) != declared(canonical['canvas']) \
            or own['background'] != current['background'] or own['state'] != current['state'] \
            or declared(source['components'][own['component']]) \
            != declared(canonical['components'][current['component']]) \
            or declared(source['backgrounds'][own['background']]) \
            != declared(canonical['backgrounds'][current['background']]):
        raise EvidenceUnavailable('Canonical geometry/background differs from its native source declaration')


def _w29_repeats(source, row, scene, scenes, background_pin):
    scale = int(PROFILE.fullmatch(row['profile'])[1]); inactive = scene['state'] == 'inactive'
    name = f'standard-{"inactive" if inactive else "active"}-{scale}x'
    p = source['passes'][name]; same_geometry(p['spec'], scenes, row['scene'])
    result = []
    bg_key = f'{scene["background"]}@{scale}x'
    for run in p['runs']:
        profile = run['profiles'].get(row['profile'])
        entry = None if profile is None else profile['entries'].get(row['scene'])
        if entry is None: raise EvidenceUnavailable('W29 repeat lacks the requested canonical native file')
        frame_pin = file_pin(safe(run['directory'], entry['file']))
        bg_file = run['backgrounds'].get(bg_key)
        if bg_file is None: raise EvidenceUnavailable('W29 lacks an explicit same-scale no-glass raster')
        bg_pin = file_pin(safe(run['directory'], bg_file))
        if bg_pin['sha256'] != background_pin['sha256']:
            raise EvidenceUnavailable('W29 no-glass source bytes differ from canonical background')
        result.append({'label': run['label'], 'frame': frame_pin, 'metadata': copy.deepcopy(entry),
                       'sourcePins': run['pins'], 'background': bg_pin})
    return result


def _w43_repeats(source, row, scene, scenes, background_pin):
    root, inventory = source['root'], source['inventory']
    identity = row['profile']+'/'+row['scene']
    matches = [c for c in inventory['cells'] if c['cell'] == identity]
    if len(matches) != 1: raise EvidenceUnavailable('W43 canonical native cell is missing or duplicate')
    index = matches[0]; record_pin = {'path': str(safe(root, index['path'])), 'sha256': index['sha256']}
    record = json.loads(gzip.decompress(read_pin(record_pin)))
    if record.get('schema') != A.SCHEMA or record.get('cell') != identity \
            or record.get('source') != 'canonical' or record.get('role') != index['role']:
        raise EvidenceUnavailable('W43 cell/source/original role metadata mismatch')
    members = sorted((r for r in record['runs'] if r['pass'].startswith('bed-')), key=lambda r: r['run'])
    if [r['run'] for r in members] != list(range(1, 8)) or len({r['pass'] for r in members}) != 1:
        raise EvidenceUnavailable('W43 canonical native cell requires exactly seven bed repetitions')
    scale = int(PROFILE.fullmatch(row['profile'])[1]); result = []
    for member in members:
        matching = [r for r in inventory['runs'] if (r['pass'], r['run']) == (member['pass'], member['run'])]
        if len(matching) != 1: raise EvidenceUnavailable('W43 native run identity is missing or duplicate')
        run = matching[0]; op = f'operational/{member["pass"]}/run-{member["run"]}'
        pins = {name: file_pin(safe(root, op+'/'+filename)) for name, filename in (
            ('manifest', 'manifest.json'), ('admission', 'admission.json'),
            ('open', 'attest.read'), ('close', 'attest.close'))}
        manifest, admission = json_pin(pins['manifest']), json_pin(pins['admission'])
        if pins['manifest']['sha256'] != member['manifestSha256'] or run['manifestSha256'] != member['manifestSha256'] \
                or pins['admission']['sha256'] != run['admissionSha256'] \
                or admission.get('schema') != 'w43-run-admission-1' or admission.get('admitted') is not True \
                or admission.get('dry') is not False or admission.get('glass') != .25 \
                or (admission.get('pass'), admission.get('run')) != (member['pass'], member['run']) \
                or admission.get('manifestSha256') != member['manifestSha256'] \
                or admission.get('frames', {}).get(identity) != member['frame'] \
                or admission.get('predeclaration') or (admission.get('declaration') or {}).get('predeclaration') \
                or (admission.get('sitting'), admission.get('planSha256')) != (inventory['sitting'], inventory['planSha256']):
            raise EvidenceUnavailable('W43 frame/run/declaration admission mismatch')
        attested = fields(read_pin(pins['open']))
        spec_pin = {'path': str(safe(root, f'operational/{member["pass"]}/scenes-run-{member["run"]}.json')),
                    'sha256': digest(attested.get('passSpecSha256'))}
        source_spec = json_pin(spec_pin)
        same_geometry(source_spec, scenes, row['scene'])
        pins['sourceSpec'] = spec_pin
        attest_pair(read_pin(pins['open']), read_pin(pins['close']), pass_name=member['pass'], scale=scale,
                    position='0.25', spec_hash=spec_pin['sha256'])
        profiles = manifest_profiles(manifest, scale=scale, position='0.25',
            pose='inactive' if scene['state'] == 'inactive' else 'active', scenes=scenes)
        entry = profiles.get(row['profile'], {}).get('entries', {}).get(row['scene'])
        if entry is None or {k: v for k, v in entry.items() if k != 'file'} != member['attestation']:
            raise EvidenceUnavailable('W43 archived attestation differs from admitted native metadata')
        frame_pin = {'path': str(safe(root, 'frames/'+digest(member['frame'])+'.png')), 'sha256': member['frame']}
        read_pin(frame_pin)
        bg_rel = manifest.get('backgrounds', {}).get(f'{scene["background"]}@{scale}x')
        if bg_rel is None or run.get('backgrounds', {}).get(bg_rel) != background_pin['sha256']:
            raise EvidenceUnavailable('W43 no-glass source differs from canonical background')
        bg_pin = {'path': str(safe(root, 'frames/'+background_pin['sha256']+'.png')),
                  'sha256': background_pin['sha256']}; read_pin(bg_pin)
        result.append({'label': 'r'+str(member['run']), 'frame': frame_pin,
            'metadata': copy.deepcopy(entry), 'sourcePins': pins, 'background': bg_pin,
            'cellRecord': record_pin, 'archiveRole': record['role'], 'archiveSource': record['source']})
    return result


def decode_verified(item, shape):
    rgb = M.S.decode_png(read_pin(item))
    if rgb.shape[:2] != tuple(shape): raise EvidenceUnavailable('Actual PNG dimensions differ from declared scale/canvas')
    return rgb


def _reference(row, config, published, scenes, source):
    match = PROFILE.fullmatch(row['profile'])
    if not match or match[2] != 'dark': raise EvidenceUnavailable('Reference is not standard dark at a fixed measured position')
    scale, position = int(match[1]), match[3]
    if (position, source['kind']) not in (('0.5', 'W29'), ('0.25', 'W43')):
        raise EvidenceUnavailable('A source cannot lend repeat bars to another glass position')
    profiles = [p for p in published['profiles'] if p['profileKey'] == row['profile']]
    declarations = [p for p in scenes['profiles'] if p['key'] == row['profile']]
    if len(profiles) != 1 or len(declarations) != 1 or row['scene'] not in declarations[0]['scenes']:
        raise EvidenceUnavailable('Published native profile/scene is outside the canonical declaration')
    entries = [f for f in profiles[0]['fixtures'] if f['sceneId'] == row['scene']]
    if len(entries) != 1: raise EvidenceUnavailable('Published native state metadata is missing or ambiguous')
    entry = entries[0]; scene = next(s for s in scenes['scenes'] if s['id'] == row['scene'])
    native_entry(entry, row['profile'], scale, scene['state'], scenes['canvas'])
    expected_native = safe(config['fixtureRoot'], entry['file'])
    if Path(row['nativeEvidence']['path']).resolve() != expected_native.resolve():
        raise EvidenceUnavailable('Reference selected another canonical native file')
    native_pin = copy.deepcopy(row['nativeEvidence']); read_pin(native_pin)
    bg_rel = published.get('backgrounds', {}).get(f'{scene["background"]}@{scale}x')
    if bg_rel is None: raise EvidenceUnavailable('Published native lacks explicit same-scale background')
    background_pin = file_pin(safe(config['fixtureRoot'], bg_rel))
    runs = (_w29_repeats if source['kind'] == 'W29' else _w43_repeats)(source, row, scene, scenes, background_pin)
    selected = [r for r in runs if r['frame']['sha256'] == native_pin['sha256']]
    if not selected or not any(r['metadata'].get('capturedAt') == entry['capturedAt'] for r in selected):
        raise EvidenceUnavailable('Published native bytes/timestamp do not belong to a selected raw state')
    current_pin = row.get('currentEvidence')
    if current_pin is None: raise EvidenceUnavailable('Current reference PNG is missing; native cannot substitute')
    read_pin(current_pin)
    metadata_pin = row.get('currentMetadata')
    if metadata_pin is not None: read_pin(metadata_pin)
    shape = (scenes['canvas']['height']*scale, scenes['canvas']['width']*scale)
    native, bg, current = (decode_verified(p, shape) for p in (native_pin, background_pin, current_pin))
    component = scenes['components'][scene['component']]
    options = {'text': row.get('stratum') == 'T',
               'impulse': scenes['backgrounds'][scene['background']]['kind'] == 'impulse'}
    reading = M.canonical_read(native, bg, component, scenes['canvas'], scale, web_rgb=current, **options)
    repeats = []
    for run in runs:
        own = M.canonical_read(decode_verified(run['frame'], shape), bg, component, scenes['canvas'], scale, **options)
        repeats.append({**run, 'reading': own})
    evidence = M.evidence_reading(reading, [r['reading'] for r in repeats])
    result = {'profile': row['profile'], 'renderer': row['renderer'], 'scene': row['scene'], 'role': row['role'],
        'statistic': row['statistic'], 'readings': evidence, 'publishedReading': reading, 'runs': repeats,
        'pins': {'native': native_pin, 'background': background_pin, 'current': current_pin,
                 'currentMetadata': metadata_pin, 'publishedManifest': config['publishedManifest'], 'scenes': config['scenes']},
        'source': {'kind': source['kind'], 'frameHashBinding': source['frameHashBinding'],
                   'selectedRuns': [r['label'] for r in selected]}, 'reference': copy.deepcopy(row)}
    name = row['statistic']
    if name in ('T1-low', 'T1-full-silhouette'):
        primary = evidence[name]
        fidelity_name = 'T1-fine' if row.get('stratum') == 'T' else 'T1-full-silhouette'
        fidelity = evidence[fidelity_name]
        complete = primary['status'] == 'MEASURED' and primary['current'] is not None \
                   and fidelity['status'] == 'MEASURED' and fidelity['current'] is not None
        update = {k: primary[k] for k in ('native', 'current', 'B')}
        update['fidelity'] = {'statistic': fidelity_name, 'native': fidelity['native'], 'current': fidelity['current']}
        result['reference'] = M.complete_t1_reference(row, update)
    else:
        prefix = 'deep8-far24' if options['impulse'] else 'deep8'
        required = [prefix+'-luma-mean', prefix+'-luma-median']
        if scenes['backgrounds'][scene['background']]['kind'] == 'solid': required.append('deep8-channel-median')
        complete = all(evidence[k]['status'] == 'MEASURED' and evidence[k]['current'] is not None for k in required)
    result['status'] = 'MEASURED' if complete else 'UNMEASURED'
    return result


def read_references(rows, config):
    """Reference evidence only, grouped by original roles; every mismatch is UNMEASURED."""
    if any(r.get('role') not in ROLES or r.get('statistic') not in
           ('T1-low', 'T1-full-silhouette', 'low-end-path-level') for r in rows):
        raise ValueError('Only canonical reference roles/statistics may be read; never fit calibration')
    report = {'schema': 'w50-canonical-reference-evidence-1',
              'purpose': 'REFERENCE_EVIDENCE_ONLY_NOT_COEFFICIENT_INPUT',
              'partitions': {role: [] for role in ROLES}, 'sources': {}, 'sourceFailures': {}}
    try:
        scenes, published = json_pin(config['scenes']), json_pin(config['publishedManifest'])
        if scenes['canvas'] != {'width': 320, 'height': 200}:
            raise EvidenceUnavailable('This canonical reader never consumes the new W50 512x384 bed')
    except (EvidenceUnavailable, KeyError, OSError) as error:
        for row in rows:
            report['partitions'][row['role']].append({**copy.deepcopy(row), 'reference': copy.deepcopy(row),
                'status': 'UNMEASURED', 'reason': str(error), 'readings': {}, 'runs': []})
        return report
    sources = {}
    for name, verifier in (('w29', verify_w29_source), ('w43', verify_w43_source)):
        position = '0.5' if name == 'w29' else '0.25'
        if not any(r['profile'].endswith('-glass'+position) for r in rows): continue
        try:
            sources[name] = verifier(config[name])
            report['sources'][name] = {k: v for k, v in sources[name].items() if k not in ('passes', 'inventory', 'root')}
        except (EvidenceUnavailable, KeyError, OSError, ValueError) as error:
            report['sourceFailures'][name] = str(error)
    for row in rows:
        name = 'w43' if row['profile'].endswith('-glass0.25') else 'w29'
        try:
            if name not in sources: raise EvidenceUnavailable(report['sourceFailures'].get(name, 'Missing own native source'))
            result = _reference(row, config, published, scenes, sources[name])
        except (EvidenceUnavailable, KeyError, OSError, ValueError) as error:
            result = {**copy.deepcopy(row), 'reference': copy.deepcopy(row), 'status': 'UNMEASURED',
                      'reason': str(error), 'readings': {}, 'runs': []}
        report['partitions'][row['role']].append(result)
    return report


def source_probe():
    """Synthetic numerical imports only; no metadata/pixel source root is consulted."""
    M.source_probe()
