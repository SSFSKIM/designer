"""Bounded W50 native analytical reader: one supplied calibration OR validation export.

There is no archive discovery, export, blind read, render, write or CLI here. Callers supply
trusted sealed bed documents and the expected export-index and declaration hashes. The
prospective execution root owns instrument/import sealing before calling these functions.
Membership and native metadata are checked before any frame is decoded. No-glass frames
are dependencies, never identifying observations; an exclusive other-role dependency is
refused even if a supplied export relabels it.

Per-frame evidence and supports are retained. Cell values are deterministic coordinatewise
medians of the three per-run statistics (not pooled pixels or averaged RGB channels). Native
spread stops readiness rather than widening a budget or silently accepting extra repetitions.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import types

import numpy as np

HERE = Path(__file__).resolve().parent
S = types.ModuleType('w50_native_statistics')
S.__file__ = str(HERE/'statistics.py')
exec(compile((HERE/'statistics.py').read_bytes(), S.__file__, 'exec'), S.__dict__)

ROLES = ('calibration', 'validation')
REPORTED_STATISTICS = ('deep8-far24-luma-mean', 'deep8-far24-luma-median', 'T1-full-silhouette')


def digest(value, what):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError(what+' must be a complete lowercase SHA-256')
    return value


def safe(root, relative):
    part = Path(relative)
    if not isinstance(relative, str) or part.is_absolute() or '..' in part.parts \
            or not part.parts or str(part) != relative:
        raise ValueError('Export path escapes its root or is not canonical')
    current = root
    for p in part.parts:
        current /= p
        if current.is_symlink():
            raise ValueError('Export symlinks are refused')
    if not current.resolve().is_relative_to(root):
        raise ValueError('Export path escapes its root')
    return current


def unique(rows, field, what):
    result = {}
    for row in rows:
        key = row[field]
        if key in result:
            raise ValueError('Duplicate '+what+' identity')
        result[key] = row
    return result


def role_membership(manifest, scenes, role):
    """Pure exact role/dependency closure; no images, export paths or measured data are read."""
    if role not in ROLES:
        raise ValueError('Only calibration or validation role exports may be analysed')
    if manifest.get('schema') != 'w50-native-bed-1' or manifest['canvas'] != scenes['canvas']:
        raise ValueError('Native bed/canvas identity mismatch')
    if manifest.get('repeatRule') != dict(runs=3, maxRequiredSpreadCodes=1, barFloorCodes=.5):
        raise ValueError('Native bed must declare the fixed three-run W50 repeat rule')
    cells = unique(manifest['cells'], 'id', 'bed cell')
    references = unique(manifest['references'], 'id', 'bed reference')
    if set(cells) & set(references):
        raise ValueError('Identifying cell and dependency identities overlap')
    scene_by_id = unique(scenes['scenes'], 'id', 'scene')
    profiles = unique(scenes['profiles'], 'key', 'profile')
    selected = {}
    for identity, cell in cells.items():
        if cell['role'] != role:
            continue
        scene = scene_by_id[cell['scene']]
        profile = profiles[cell['profile']]
        if identity != cell['profile']+'/'+cell['scene'] or cell['scene'] not in profile['scenes'] \
                or cell['scene'] not in scenes['split'][role] or cell['runs'] != [1, 2, 3] \
                or cell['background'] != scene['background'] \
                or cell['scale'] not in (1, 2) or cell['pose'] not in ('active', 'receded') \
                or (scene['state'] == 'rest') != (cell['pose'] == 'active'):
            raise ValueError('Cell does not match its declared role/scene/repetitions')
        # Native span224 is withheld irrespective of an accidentally relabelled bed input.
        if cell['span'] == 224 or cell['family'] not in ('uniform', 'span', 'structured'):
            raise ValueError('Withheld span224 or unknown identifying family')
        reference = references.get(cell['reference'])
        if reference is None or role not in reference['roles'] \
                or reference['profile'] != cell['profile'] \
                or reference['background'] != cell['background'] \
                or reference['passName'] != cell['passName']:
            raise ValueError('Missing or exclusive other-role no-glass dependency')
        selected[identity] = cell
    dependencies = {k: r for k, r in references.items() if role in r['roles']}
    if not selected or set(dependencies) != {c['reference'] for c in selected.values()}:
        raise ValueError('Dependency membership is not exactly the identifying role closure')
    for identity, reference in dependencies.items():
        scene = scene_by_id[reference['scene']]
        if identity != reference['profile']+'/'+reference['scene'] or reference['run'] != 1 \
                or reference['background'] != scene['background'] \
                or scenes['components'][scene['component']]['kind'] != 'none' \
                or reference['scene'] not in profiles[reference['profile']]['scenes']:
            raise ValueError('No-glass dependency identity/scene/run mismatch')
    return selected, dependencies


def reported_reference_keys(manifest, scenes):
    """Enumerate DL5a's exact prospective keys, including blind identities but no pixels.

    These keys can be copied into the G1 root and checked by exact membership. No pattern or
    renderer-wide exemption is returned; the two channel-level rows per control are absent.
    """
    by_scene = unique(scenes['scenes'], 'id', 'scene')
    keys = []
    for cell in manifest['cells']:
        background = scenes['backgrounds'][by_scene[cell['scene']]['background']]
        if cell['family'] == 'span' and cell['span'] in (128, 224) and background['kind'] == 'solid':
            for renderer in ('webgpu', 'css'):
                for statistic in REPORTED_STATISTICS:
                    keys.append((cell['profile'], renderer, cell['scene'], statistic))
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate DL5a reference key')
    return sorted(keys)


def validate_native(row, identity, spec, scene, scenes, *, dependency):
    native = row['native']
    expected_file = spec['profile']+'/'+spec['scene']+'.png'
    run = spec['run'] if dependency else row['run']
    if native.get('sceneId') != spec['scene'] or native.get('file') != expected_file \
            or row['path'] != f'{spec["passName"]}/run-{run}/{expected_file}':
        raise ValueError('Frame path/native metadata differs from cell/run identity: '+identity)
    scale = int(re.search(r'-(1|2)x-', spec['profile']).group(1))
    if not dependency and scale != spec['scale']:
        raise ValueError('Profile/bed scale mismatch')
    pixels = [scenes['canvas']['width']*scale, scenes['canvas']['height']*scale]
    if [native.get('width'), native.get('height')] != pixels:
        raise ValueError('Native fixture pixel size mismatch')
    if native.get('captureMethod') != 'screencapturekit' or native.get('materialRendered') is not True \
            or native.get('deterministic') is not True:
        raise ValueError('Native capture/material/repeat attestation failed')
    active = scene['state'] == 'rest'
    if native.get('presentedActive') is not active:
        raise ValueError('Native pose attestation failed')
    if not active:
        presentation = native.get('presentation') or {}
        if presentation.get('observedPose') != 'inactive' \
                or presentation.get('isKeyWindow') is not False \
                or presentation.get('appIsActive') is not False:
            raise ValueError('Native inactive presentation attestation failed')
    frame = native.get('windowFrame') or {}
    requested = frame.get('requested', [])
    if frame.get('coordinateSpace') != 'appkit-global-bottom-left' \
            or frame.get('actual') != requested or len(requested) != 4 \
            or not np.isfinite(np.asarray(requested, dtype=float)).all() \
            or requested[2:] != [scenes['canvas']['width'], scenes['canvas']['height']] \
            or frame.get('backingScaleFactor') != scale:
        raise ValueError('Native window frame/scale attestation failed')
    if not isinstance(native.get('capturedAt'), str) or not native['capturedAt']:
        raise ValueError('Native capture time is missing')
    paths = native.get('suppliedPaths')
    component = scenes['components'][scene['component']]
    if dependency:
        if paths != []:
            raise ValueError('No-glass dependency carries a supplied material path')
    else:
        placed = S.P.place_component(component, scenes['canvas'])
        if not isinstance(paths, list) or len(paths) != 1 or len(placed) != 1:
            raise ValueError('Native supplied path count mismatch')
        path, want = paths[0], placed[0]
        origin = np.asarray(path.get('frameOrigin', []), dtype=float)
        if origin.shape != (2,) or not np.isfinite(origin).all() \
                or np.max(np.abs(origin-[want['left'], want['top']])) > 1e-9 \
                or path.get('rect') != [0, 0, want['width'], want['height']] \
                or path.get('kind') != component['kind'] or path.get('opaque') is not False:
            raise ValueError('Native supplied path placement/size/kind mismatch')
        # Elements are retained as attested evidence; W50's analytical cut does not fit their
        # curves. Placement was also checked by the sealed sitting admission before archiving.
        if not isinstance(path.get('elements'), list):
            raise ValueError('Native supplied path elements are absent')
    return scale


def verify_role_export(root, expected_index_sha256, role, manifest, scenes, *,
                       expected_declaration_sha256):
    """Verify role, exact cells/dependencies, three runs, metadata, tree membership and hashes.

    All identities are checked before frame bytes are opened. Frame hashes are rechecked at
    decode, so a changed file between verification and measurement is not trusted.
    """
    selected, dependencies = role_membership(manifest, scenes, role)
    digest(expected_index_sha256, 'Expected export index hash')
    digest(expected_declaration_sha256, 'Expected native declaration hash')
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Supplied export root is not an ordinary directory')
    root = root.resolve()
    raw = safe(root, 'index.json').read_bytes()
    if S.sha(raw) != expected_index_sha256:
        raise ValueError('Export index hash differs from registered evidence')
    if safe(root, 'index.sha256').read_text() != expected_index_sha256+'  index.json\n':
        raise ValueError('Export index hash sidecar mismatch')
    index = json.loads(raw)
    if index.get('schema') != 'w50-role-archive-1' or not isinstance(index.get('files'), list):
        raise ValueError('Unknown role export schema')
    expected = {(k, run) for k in selected for run in (1, 2, 3)} | {(k, 1) for k in dependencies}
    found, paths, manifests = {}, set(), {}
    scene_by_id = {s['id']: s for s in scenes['scenes']}
    for row in index['files']:
        if row.get('roles') != [role] or row.get('kind') != 'frame':
            raise ValueError('Raw, mixed-role or operational export row is not analytical evidence')
        key = (row['cell'], row['run'])
        if type(row['run']) is not int or key not in expected or key in found:
            raise ValueError('Unexpected, duplicate or missing role cell/repetition membership')
        path = safe(root, row['path'])
        if row['path'] in paths or row['path'] in ('index.json', 'index.sha256'):
            raise ValueError('Duplicate or reserved export path')
        paths.add(row['path'])
        digest(row['sha256'], 'Frame hash')
        digest(row['manifestSha256'], 'Native manifest hash')
        if row.get('declarationSha256') != expected_declaration_sha256:
            raise ValueError('Native declaration hash differs from the registered sitting')
        dependency = row['cell'] in dependencies
        spec = dependencies[row['cell']] if dependency else selected[row['cell']]
        validate_native(row, row['cell'], spec, scene_by_id[spec['scene']], scenes,
                        dependency=dependency)
        run_key = (spec['passName'], row['run'])
        if run_key in manifests and manifests[run_key] != row['manifestSha256']:
            raise ValueError('Conflicting native manifest hashes for one admitted run')
        manifests[run_key] = row['manifestSha256']
        found[key] = row
    if set(found) != expected:
        raise ValueError('Role export is missing declared cells/dependencies/repetitions')
    actual = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('Export symlinks are refused')
        if path.is_file():
            actual.add(str(path.relative_to(root)))
    if actual != paths | {'index.json', 'index.sha256'}:
        raise ValueError('Role export tree membership mismatch')
    for row in found.values():
        path = safe(root, row['path'])
        if not path.is_file() or S.sha(path.read_bytes()) != row['sha256']:
            raise ValueError('Role frame hash mismatch: '+row['path'])
    return {'root': root, 'indexSha256': expected_index_sha256, 'rows': copy.deepcopy(found),
            'cells': copy.deepcopy(selected), 'dependencies': copy.deepcopy(dependencies)}


def read_verified_frame(root, row, canvas, scale):
    raw = safe(root, row['path']).read_bytes()
    if S.sha(raw) != row['sha256']:
        raise ValueError('Role frame changed before decode: '+row['path'])
    rgb = S.decode_png(raw)
    if rgb.shape[:2] != (canvas['height']*scale, canvas['width']*scale):
        raise ValueError('Actual PNG dimensions differ from native metadata/declared canvas')
    return rgb


def aggregate_runs(runs, *, reported=False):
    """Pure role-independent aggregation: retain individual values and coordinatewise median."""
    if [r['run'] for r in runs] != [1, 2, 3]:
        raise ValueError('Exactly ordered admitted repetitions 1, 2, 3 are required')
    names = set(runs[0]['readings']['statistics'])
    if any(set(r['readings']['statistics']) != names for r in runs):
        raise ValueError('Native repetitions carry different statistics')
    output = {}
    for name in sorted(names):
        readings = [r['readings']['statistics'][name] for r in runs]
        values = [r['value'] for r in readings]
        is_reported = reported and name in REPORTED_STATISTICS
        required = not is_reported
        complete = all(r['status'] == 'MEASURED' and r['value'] is not None for r in readings)
        measurement_status = 'MEASURED' if complete else 'UNMEASURED_EMPTY_SUPPORT'
        item = {'status': 'REPORTED' if is_reported else measurement_status,
                'measurementStatus': measurement_status, 'required': required,
                'support': readings[0]['support'], 'units': readings[0]['units'],
                'value': None, 'runValues': values, 'repeat': None,
                'aggregation': 'coordinatewise-median-of-three-run-statistics'}
        if complete:
            array = np.asarray(values, dtype=float)
            if not np.isfinite(array).all():
                raise ValueError('Native measurement is nonfinite')
            item['value'] = np.median(array, axis=0).tolist()
            if name == 'T1-full-silhouette':
                means = [r['readings']['supports']['full-silhouette']['linearLumaMean'] for r in runs]
                item['repeat'] = S.repeat_t1(values, means)
            else:
                item['repeat'] = S.repeat_codes(values)
        if is_reported:
            item['B'] = None
        output[name] = item
    return output


def read_role_export(root, expected_index_sha256, role, manifest, scenes, *,
                     expected_declaration_sha256):
    """Orchestrate one registered role; a ready=False report is a stop, never a fit permission."""
    verified = verify_role_export(root, expected_index_sha256, role, manifest, scenes,
                                   expected_declaration_sha256=expected_declaration_sha256)
    rows = verified['rows']
    by_scene = {s['id']: s for s in scenes['scenes']}
    backgrounds, dependencies = {}, []
    for identity, spec in sorted(verified['dependencies'].items()):
        row = rows[(identity, 1)]
        scale = int(re.search(r'-(1|2)x-', spec['profile']).group(1))
        backgrounds[identity] = read_verified_frame(verified['root'], row, scenes['canvas'], scale)
        dependencies.append({'id': identity, 'evidence': copy.deepcopy(row)})
    cells, stops = [], []
    reported_keys = set(reported_reference_keys(manifest, scenes))
    for identity, cell in sorted(verified['cells'].items()):
        scene = by_scene[cell['scene']]
        component = scenes['components'][scene['component']]
        structured = cell['family'] != 'uniform'
        impulse = scenes['backgrounds'][cell['background']]['kind'] == 'impulse'
        runs = []
        for run in (1, 2, 3):
            row = rows[(identity, run)]
            rgb = read_verified_frame(verified['root'], row, scenes['canvas'], cell['scale'])
            readings = S.read_frame(rgb, backgrounds[cell['reference']], component, scenes['canvas'],
                                     cell['scale'], impulse=impulse, include_structured=structured)
            runs.append({'run': run, 'evidence': copy.deepcopy(row),
                         'dependency': cell['reference'], 'readings': readings})
        reported = (cell['profile'], 'webgpu', cell['scene'], 'T1-full-silhouette') in reported_keys
        statistics = aggregate_runs(runs, reported=reported)
        for name, statistic in statistics.items():
            if statistic['required'] and (statistic['measurementStatus'] != 'MEASURED' or
                                           not statistic['repeat']['passes']):
                stops.append({'cell': identity, 'statistic': name,
                              'reason': ('UNMEASURED_REQUIRED_POPULATION' if statistic['repeat'] is None
                                         else 'NATIVE_SPREAD_EXCEEDS_ONE_CODE'),
                              'repeat': statistic['repeat']})
        cells.append(dict(copy.deepcopy(cell), runs=runs, statistics=statistics))
    return {'schema': 'w50-native-role-read-1', 'role': role, 'indexSha256': expected_index_sha256,
            'declarationSha256': expected_declaration_sha256,
            'canvas': copy.deepcopy(scenes['canvas']), 'supportDefinitions': dict(S.SUPPORT_DEFINITIONS),
            'repeatRule': copy.deepcopy(manifest['repeatRule']),
            'reportedReferenceKeys': [list(k) for k in sorted(reported_keys)],
            'dependencies': dependencies, 'cells': cells, 'stops': stops, 'ready': not stops}


def reference_rows(report):
    """Project native readings onto exact sealed reference keys; no current/historical/B invention."""
    if report['role'] not in ROLES:
        raise ValueError('Only calibration or validation reports can be projected')
    rows = []
    for cell in report['cells']:
        for renderer in ('webgpu', 'css'):
            for name, statistic in cell['statistics'].items():
                row = {'profile': cell['profile'], 'renderer': renderer, 'scene': cell['scene'],
                       'statistic': name, 'role': report['role'], 'nativeIdentity': cell['id'],
                       'referenceIdentity': cell['reference'],
                       'native': copy.deepcopy(statistic['value']),
                       'status': statistic['status'], 'measurementStatus': statistic['measurementStatus'],
                       'required': statistic['required'], 'units': statistic['units'],
                       'support': statistic['support'], 'repeat': copy.deepcopy(statistic['repeat']),
                       'runValues': copy.deepcopy(statistic['runValues']),
                       'aggregation': statistic['aggregation'],
                       'nativeEvidence': [copy.deepcopy(r['evidence']) for r in cell['runs']]}
                if statistic['status'] == 'REPORTED':
                    row['B'] = None
                rows.append(row)
    return sorted(rows, key=lambda r: (r['profile'], r['renderer'], r['scene'], r['statistic']))
