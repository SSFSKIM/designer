"""Prospective one-shot native blind preparation, callable only inside dispatcher exposure.

No CLI, actual contract, archive location or export is installed here. A root-pinned config
names the independently verified downloaded archive, its asset/index, pack and G0 sources.
The same live dispatcher instance must admit the candidate run, own its exposure claim and
same-candidate PASS_EXPOSED_OWNER_PENDING gate before any archive/frame bytes are opened.
That gate has passed exposed cells only: ownerChecks remains PENDING_FULL_UNION and its
ordered pendingOwnerKeys must exactly match the root's physical dependency closure. A fixed
subclaim burns
this native preparation once, including failures; neither another destination nor a retry
can create a second analytical exposure.

The immutable native/statistics.py supplies every formula. Original archive rows, roles and
native metadata survive unchanged; blind is never relabelled validation. Native path cuts and
native-detected T1 supports remain separate. DL5c admits only exactly enumerated receded224
neutral0/4/28 T1 rows with three genuine zero-mask witnesses; all level rows remain required.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import types

HERE = Path(__file__).resolve().parent
G0 = HERE.parents[1]/'2026-10-08-w50-g0-declaration'


def source_module(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


# The dispatcher source guard audits these dynamic exec imports before execution. The dry
# closure probe also sees them; no repository pyc or extracted-tree code is loaded.
R = source_module('w50_blind_native_primitives', HERE.parent/'native/reader.py')
A = source_module('w50_blind_archive_primitives', G0/'bed/sitting/archive.py')


def encoded(doc):
    return (json.dumps(doc, indent=2, allow_nan=False)+'\n').encode()


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def external_pin(path):
    return {'path': str(Path(path).resolve()), 'sha256': sha(path)}


def write_once(path, doc):
    raw = encoded(doc)
    with Path(path).open('xb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())
    return external_pin(path)


def blind_membership(manifest, scenes):
    """Pure exact blind identifying/dependency closure, without reading archive bytes."""
    if manifest.get('schema') != 'w50-native-bed-1' or manifest.get('canvas') != scenes['canvas'] \
            or manifest.get('repeatRule') != dict(runs=3, maxRequiredSpreadCodes=1, barFloorCodes=.5):
        raise ValueError('Blind bed/canvas/repetition identity mismatch')
    cells = R.unique(manifest['cells'], 'id', 'bed cell')
    refs = R.unique(manifest['references'], 'id', 'bed reference')
    by_scene = R.unique(scenes['scenes'], 'id', 'scene')
    profiles = R.unique(scenes['profiles'], 'key', 'profile')
    if set(cells) & set(refs):
        raise ValueError('Blind identifying cells and dependencies overlap')
    selected = {}
    for identity, cell in cells.items():
        if cell['role'] != 'blind':
            continue
        scene = by_scene[cell['scene']]
        reference = refs.get(cell['reference'])
        if identity != cell['profile']+'/'+cell['scene'] or cell['runs'] != [1, 2, 3] \
                or cell['scene'] not in profiles[cell['profile']]['scenes'] \
                or cell['scene'] not in scenes['split']['holdout'] \
                or cell['background'] != scene['background'] or cell['scale'] not in (1, 2) \
                or cell['pose'] not in ('active', 'receded') \
                or (scene['state'] == 'rest') != (cell['pose'] == 'active') \
                or cell['family'] not in ('uniform', 'span', 'structured'):
            raise ValueError('Blind cell differs from its declared role/scene/repetitions')
        if reference is None or 'blind' not in reference['roles'] \
                or reference['profile'] != cell['profile'] \
                or reference['background'] != cell['background'] \
                or reference['passName'] != cell['passName']:
            raise ValueError('Blind cell has a missing or exclusive exposed dependency')
        selected[identity] = cell
    dependencies = {k: r for k, r in refs.items() if 'blind' in r['roles']}
    if not selected or set(dependencies) != {c['reference'] for c in selected.values()}:
        raise ValueError('Blind dependency membership differs from exact identifying closure')
    for identity, reference in dependencies.items():
        scene = by_scene[reference['scene']]
        if identity != reference['profile']+'/'+reference['scene'] or reference['run'] != 1 \
                or reference['background'] != scene['background'] \
                or scenes['components'][scene['component']]['kind'] != 'none' \
                or reference['scene'] not in profiles[reference['profile']]['scenes']:
            raise ValueError('Blind no-glass dependency identity/scene/run mismatch')
    return selected, dependencies


def empty_support_keys(manifest, scenes):
    """Exact prospective DL5c keys, identity metadata only, never an empty-mask assumption."""
    by_scene = {s['id']: s for s in scenes['scenes']}
    keys = []
    for cell in manifest['cells']:
        if cell.get('role') == 'blind' and cell.get('family') == 'span' \
                and cell.get('span') == 224 and cell.get('pose') == 'receded' \
                and cell.get('level') in (0, 4, 28) \
                and cell.get('background') == f'grey-{cell["level"]:03d}' \
                and scenes['backgrounds'][by_scene[cell['scene']]['background']]['kind'] == 'solid':
            for renderer in ('webgpu', 'css'):
                keys.append((cell['profile'], renderer, cell['scene'], 'T1-full-silhouette'))
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate DL5c native key')
    return sorted(keys)


def selected_rows(index, manifest, scenes, declaration_sha256):
    """Check blind rows against their ORIGINAL roles, native geometry and three run identities."""
    cells, dependencies = blind_membership(manifest, scenes)
    expected = {(k, run) for k in cells for run in (1, 2, 3)} | {(k, 1) for k in dependencies}
    by_scene = {s['id']: s for s in scenes['scenes']}
    found, manifests, paths = {}, {}, set()
    for row in index['files']:
        if 'blind' not in row.get('roles', []):
            continue
        if row.get('kind') != 'frame' or type(row.get('run')) is not int:
            raise ValueError('Unexpected operational row in native blind membership')
        key = (row['cell'], row['run'])
        if key not in expected or key in found or row['path'] in paths:
            raise ValueError('Foreign, duplicate or relabelled blind cell/repetition')
        dependency = row['cell'] in dependencies
        spec = dependencies[row['cell']] if dependency else cells[row['cell']]
        original_roles = spec['roles'] if dependency else ['blind']
        if row['roles'] != original_roles or row.get('declarationSha256') != declaration_sha256:
            raise ValueError('Blind archive row changed original role/declaration provenance')
        R.digest(row['sha256'], 'Native frame hash')
        R.digest(row['manifestSha256'], 'Native run manifest hash')
        R.validate_native(row, row['cell'], spec, by_scene[spec['scene']], scenes,
                          dependency=dependency)
        run_key = (spec['passName'], row['run'])
        if run_key in manifests and manifests[run_key] != row['manifestSha256']:
            raise ValueError('Blind rows disagree on their admitted native run manifest')
        manifests[run_key] = row['manifestSha256']
        found[key] = row; paths.add(row['path'])
    if set(found) != expected:
        raise ValueError('Blind archive lacks exact cells/dependencies/three repetitions')
    return cells, dependencies, found


def plan_fixture_metadata(index, manifest, scenes, destination):
    """Pure planning from index identities/hashes only: no frame paths are opened or decoded.

    Each (profile,pose) has a separate tree. The returned hashes/pins can be bound into the
    single future exposure batch before copying any exclusive blind dependency pixels.
    """
    cells, dependencies = blind_membership(manifest, scenes)
    expected = {(k, 1) for k in dependencies}
    rows = {}
    for row in index['files']:
        key = (row.get('cell'), row.get('run'))
        if key not in expected:
            continue
        if key in rows or row.get('kind') != 'frame' \
                or row.get('roles') != dependencies[key[0]]['roles']:
            raise ValueError('Fixture planning dependency identity/original role mismatch')
        R.digest(row['sha256'], 'Planned no-glass frame hash')
        rows[key] = row
    if set(rows) != expected:
        raise ValueError('Fixture planning lacks exact blind dependencies')
    groups = {}
    for cell in cells.values():
        group = (cell['profile'], cell['pose'])
        groups.setdefault(group, {})[cell['reference']] = dependencies[cell['reference']]
    result = {}
    destination = Path(destination).absolute()
    for (profile, pose), refs in sorted(groups.items()):
        root = destination/'fixtures'/profile/pose
        backgrounds, originals = {}, []
        for identity, spec in sorted(refs.items()):
            row = rows[(identity, 1)]
            scale = int(re.search(r'-(1|2)x-', profile).group(1))
            key = f'{spec["background"]}@{scale}x'
            file = 'backgrounds/'+key+'.png'
            if key in backgrounds:
                raise ValueError('Two distinct no-glass dependencies collide within one pose')
            backgrounds[key] = {'path': file, 'sha256': row['sha256']}
            originals.append({'id': identity, 'path': row['path'], 'sha256': row['sha256'],
                              'roles': copy.deepcopy(row['roles']), 'fixturePath': file})
        doc = {'schema': 'w50-native-exposure-fixtures-1', 'profile': profile, 'pose': pose,
               'backgrounds': {key: value['path'] for key, value in sorted(backgrounds.items())},
               'dependencies': originals}
        result[profile+'|'+pose] = {'path': str(root), 'manifestSha256': A.sha(encoded(doc)),
            'backgrounds': backgrounds, 'manifest': doc}
    return result


def read_fixture_plan(index_path, expected_index_sha256, manifest, scenes, destination):
    """Metadata-only index read; do not verify/decode frame bytes in the planning phase."""
    R.digest(expected_index_sha256, 'Expected original archive index hash')
    raw = Path(index_path).read_bytes()
    if A.sha(raw) != expected_index_sha256:
        raise ValueError('Fixture plan index differs from its registered archive')
    doc = json.loads(raw)
    if doc.get('schema') != 'w50-role-archive-1':
        raise ValueError('Unknown original archive index schema')
    return plan_fixture_metadata(doc, manifest, scenes, destination)


def admission(context, run, config_pin):
    """Require the live, claimed same-candidate exposed PASS with owner rows still pending."""
    dispatcher = sys.modules.get('w50_g1_dispatch')
    if dispatcher is None:
        raise ValueError('Direct native exposure call: no live dispatcher capability')
    dispatcher.require_render_admission(context, run)
    if context['phase'] != 'exposure':
        raise ValueError('Native blind preparation is exposure-only')
    repo = Path(context['repo'])
    root = dispatcher.sealed(context['executionRoot'])
    if dispatcher.checked(repo, root['bootstrap']) != Path(dispatcher.__file__).resolve() \
            or config_pin not in root['inputs'] or config_pin not in context['inputs']:
        raise ValueError('Blind input config is not pinned by the admitted dispatcher root')
    contract = dispatcher.sealed(context['contract'])
    claim_path = Path(context['contract']+'.started.json')
    if not claim_path.is_file():
        raise ValueError('Native exposure lacks its dispatcher claim')
    claim = dispatcher.load(claim_path)
    if claim.get('phase') != 'exposure' or claim.get('pid') != os.getpid() \
            or claim.get('contractSha256') != dispatcher.sha(context['contract']) \
            or claim.get('batchSha256') != dispatcher.sha(context['batchPath']) \
            or claim.get('output') != context['output'] \
            or claim.get('gpuLease') != dispatcher._LEASE['token']:
        raise ValueError('Native exposure dispatcher claim differs from the live invocation')
    gate = dispatcher.checked(repo, contract['gateContract'])
    dispatcher.checked(repo, contract['gateResult'])
    result = dispatcher.result_for(gate)
    cohort = context['batch']['cohort']
    pending = (root.get('phaseDependencies') or {}).get('pendingOwnerKeys')
    if contract.get('phase') != 'exposure' or contract.get('cohort') != cohort \
            or dispatcher.sealed(gate).get('cohort') != cohort \
            or result['report'].get('status') != 'PASS_EXPOSED_OWNER_PENDING' \
            or result['report'].get('ownerChecks') != 'PENDING_FULL_UNION' \
            or not isinstance(pending, list) or result['report'].get('pendingOwnerKeys') != pending \
            or result['report'].get('candidateSha256s') != sorted(p['sha256'] for p in cohort):
        raise ValueError('Native exposure lacks same-candidate exposed gate PASS with owner rows pending')
    config = dispatcher.load(dispatcher.checked(repo, config_pin))
    if config.get('schema') != 'w50-native-exposure-inputs-1':
        raise ValueError('Unknown native exposure input schema')
    for name, root_name in (('partOne', 'partOne'), ('partTwo', 'partTwo'), ('manifest', 'manifest')):
        if config.get(name) != root[root_name]:
            raise ValueError('Native exposure substituted immutable G0 inputs')
    paths = {name: dispatcher.checked(repo, config[name])
             for name in ('partOne', 'partTwo', 'manifest', 'scenes', 'pack')}
    one, two = dispatcher.load(paths['partOne']), dispatcher.load(paths['partTwo'])
    if two.get('partOneSha256') != config['partOne']['sha256']:
        raise ValueError('Native exposure G0 parts differ')
    for part in (one, two):
        if config['manifest'] not in part['sources'] or config['scenes'] not in part['sources']:
            raise ValueError('Native exposure bed/scenes are not sealed by both G0 parts')
    pack = dispatcher.load(paths['pack'])
    asset = config.get('archiveAsset', {})
    if pack.get('declarationSha256') != config['partOne']['sha256'] \
            or pack.get('indexSha256') != config.get('archiveIndexSha256') \
            or pack.get('sha256') != asset.get('sha256'):
        raise ValueError('Original archive/index pins differ from the pinned G1 pack')
    if not isinstance(asset.get('path'), str) or not Path(asset['path']).is_absolute() \
            or not isinstance(config.get('archiveRoot'), str) \
            or not Path(config['archiveRoot']).is_absolute():
        raise ValueError('Native exposure needs explicit absolute downloaded archive/asset paths')
    R.digest(config['archiveIndexSha256'], 'Original archive index hash')
    R.digest(asset['sha256'], 'Original archive asset hash')
    manifest, scenes = dispatcher.load(paths['manifest']), dispatcher.load(paths['scenes'])
    cells, _ = blind_membership(manifest, scenes)
    requested = {(r['profile'], s) for r in context['batch']['runs'] for s in r['scenes']}
    if not {(c['profile'], c['scene']) for c in cells.values()} <= requested:
        raise ValueError('Native blind cells are outside the admitted exposure batch')
    reported = set(R.reported_reference_keys(manifest, scenes))
    identities = {(c['profile'], c['scene']) for c in cells.values()}
    expected_reported = {k for k in reported if (k[0], k[2]) in identities}
    if expected_reported != {tuple(k) for k in root['reportedKeys'] if (k[0], k[2]) in identities} \
            or set(empty_support_keys(manifest, scenes)) != \
            {tuple(k) for k in root['emptySupportKeys'] if (k[0], k[2]) in identities}:
        raise ValueError('Native blind reporting/empty-support keys differ from the exact root enumeration')
    return dispatcher, root, config, manifest, scenes


def zero_support_witness(runs):
    if [r['run'] for r in runs] != [1, 2, 3]:
        raise ValueError('DL5c empty support needs exactly three native repetitions')
    for run in runs:
        support = run['readings']['supports']['full-silhouette']
        statistic = run['readings']['statistics']['T1-full-silhouette']
        if support['status'] != 'UNMEASURED_EMPTY_SUPPORT' or support['pixels'] != 0 \
                or statistic['status'] != 'UNMEASURED_EMPTY_SUPPORT' or statistic['value'] is not None \
                or R.S.decode_support(support).any():
            raise ValueError('DL5c witness is not three real zero native silhouettes')
    return True


def _require_preparation(context, run):
    dispatcher = sys.modules.get('w50_g1_dispatch')
    if dispatcher is None:
        raise ValueError('Direct native file read: no dispatcher capability')
    dispatcher.require_render_admission(context, run)
    if context['phase'] != 'exposure':
        raise ValueError('Native blind file reading is exposure-only')
    claim = Path(context['output'])/'native-blind.started.json'
    if not claim.is_file():
        raise ValueError('Native blind file reading lacks the one-shot preparation claim')
    record = dispatcher.load(claim)
    if record.get('schema') != 'w50-native-blind-claim-1' or record.get('role') != 'blind' \
            or record.get('dispatcherContract') != external_pin(context['contract']) \
            or record.get('dispatcherClaim') != external_pin(context['contract']+'.started.json') \
            or record.get('batch') != external_pin(context['batchPath']):
        raise ValueError('Native blind preparation claim differs from the live exposure')


def _measure_blind(context, run, export_root, index_hash, found, manifest, scenes, declaration_sha256):
    """Internal admitted read; no role substitution or analytical T1 fallback."""
    _require_preparation(context, run)
    cells, deps = blind_membership(manifest, scenes)
    backgrounds, dependencies = {}, []
    for identity, spec in sorted(deps.items()):
        row = found[(identity, 1)]
        scale = int(re.search(r'-(1|2)x-', spec['profile']).group(1))
        backgrounds[identity] = R.read_verified_frame(export_root, row, scenes['canvas'], scale)
        dependencies.append({'id': identity, 'evidence': copy.deepcopy(row)})
    by_scene = {s['id']: s for s in scenes['scenes']}
    reported_keys = set(R.reported_reference_keys(manifest, scenes))
    eligible = set(empty_support_keys(manifest, scenes))
    output, stops = [], []
    for identity, cell in sorted(cells.items()):
        component = scenes['components'][by_scene[cell['scene']]['component']]
        impulse = scenes['backgrounds'][cell['background']]['kind'] == 'impulse'
        runs = []
        for run in (1, 2, 3):
            row = found[(identity, run)]
            rgb = R.read_verified_frame(export_root, row, scenes['canvas'], cell['scale'])
            readings = R.S.read_frame(rgb, backgrounds[cell['reference']], component, scenes['canvas'],
                cell['scale'], impulse=impulse, include_structured=cell['family'] != 'uniform')
            runs.append({'run': run, 'evidence': copy.deepcopy(row),
                         'dependency': cell['reference'], 'readings': readings})
        reported = (cell['profile'], 'webgpu', cell['scene'], 'T1-full-silhouette') in reported_keys
        statistics = R.aggregate_runs(runs, reported=reported)
        for name, statistic in statistics.items():
            key = (cell['profile'], 'webgpu', cell['scene'], name)
            if statistic['measurementStatus'] != 'MEASURED':
                if key in eligible:
                    zero_support_witness(runs)
                    statistic.update(status='UNMEASURED_EMPTY_SUPPORT', value=None, B=None, required=False)
                else:
                    stops.append({'cell': identity, 'statistic': name,
                                  'reason': 'UNMEASURED_UNAUTHORISED_POPULATION', 'repeat': None})
            elif statistic['required'] and not statistic['repeat']['passes']:
                stops.append({'cell': identity, 'statistic': name,
                              'reason': 'NATIVE_SPREAD_EXCEEDS_ONE_CODE', 'repeat': statistic['repeat']})
        output.append(dict(copy.deepcopy(cell), runs=runs, statistics=statistics))
    return {'schema': 'w50-native-role-read-1', 'role': 'blind', 'indexSha256': index_hash,
            'declarationSha256': declaration_sha256, 'canvas': copy.deepcopy(scenes['canvas']),
            'supportDefinitions': dict(R.S.SUPPORT_DEFINITIONS),
            'repeatRule': copy.deepcopy(manifest['repeatRule']),
            'reportedReferenceKeys': [list(k) for k in sorted(reported_keys)
                                      if any(k[0] == c['profile'] and k[2] == c['scene'] for c in cells.values())],
            'emptySupportKeys': [list(k) for k in sorted(eligible)],
            'dependencies': dependencies, 'cells': output, 'stops': stops, 'ready': not stops}


def _copy_fixtures(context, run, source, plans):
    _require_preparation(context, run)
    result = {}
    for key, plan in plans.items():
        root = Path(plan['path']); root.mkdir(parents=True, exist_ok=False)
        for original in plan['manifest']['dependencies']:
            raw = A.safe(source, original['path']).read_bytes()
            if A.sha(raw) != original['sha256']:
                raise ValueError('No-glass frame changed before fixture copying')
            target = root/original['fixturePath']; target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as handle:
                handle.write(raw)
        manifest = write_once(root/'manifest.json', plan['manifest'])
        if manifest['sha256'] != plan['manifestSha256']:
            raise ValueError('Copied fixture manifest differs from its prospective metadata plan')
        result[key] = {name: copy.deepcopy(plan[name]) for name in ('path', 'manifestSha256', 'backgrounds')}
    return result


def prepare_native_exposure(context, run, config_pin):
    """One dispatcher-admitted blind native exposure and fixture preparation before web rendering."""
    dispatcher, root, config, manifest, scenes = admission(context, run, config_pin)
    destination = Path(context['output'])/'native-blind'
    archive = Path(config['archiveRoot']).resolve()
    if destination.exists() or destination.is_symlink() \
            or destination.resolve().is_relative_to(archive) or archive.is_relative_to(destination.resolve()):
        raise ValueError('Native exposure destination exists or overlaps its original archive')
    claim = destination.with_name('native-blind.started.json')
    claim_pin = write_once(claim, {'schema': 'w50-native-blind-claim-1',
        'dispatcherContract': external_pin(context['contract']),
        'dispatcherClaim': external_pin(context['contract']+'.started.json'),
        'batch': external_pin(context['batchPath']), 'config': config_pin, 'role': 'blind'})
    destination.mkdir(exist_ok=False)
    if not Path(config['archiveAsset']['path']).is_file() \
            or sha(config['archiveAsset']['path']) != config['archiveAsset']['sha256']:
        raise ValueError('Original downloaded archive asset hash mismatch')
    index = A.verify_archive(archive, config['archiveIndexSha256'])
    _, _, found = selected_rows(index, manifest, scenes, config['partOne']['sha256'])
    export_root = destination/'role-export'
    export_hash = A.write_archive(archive, export_root, [copy.deepcopy(r) for r in found.values()])
    export = A.verify_archive(export_root, export_hash)
    _, _, exported_rows = selected_rows(export, manifest, scenes, config['partOne']['sha256'])
    plans = plan_fixture_metadata(index, manifest, scenes, destination)
    fixtures = _copy_fixtures(context, run, archive, plans)
    report = _measure_blind(context, run, export_root, export_hash, exported_rows, manifest, scenes,
                            config['partOne']['sha256'])
    report['originalArchive'] = {'asset': config['archiveAsset'],
        'indexSha256': config['archiveIndexSha256'], 'pack': config['pack'], 'claim': claim_pin}
    native_pin = write_once(destination/'native-read.json', report)
    witnesses = []
    witness_root = destination/'empty-support-witnesses'; witness_root.mkdir()
    eligible = {tuple(k) for k in report['emptySupportKeys']}
    for cell in report['cells']:
        statistic = cell['statistics'].get('T1-full-silhouette', {})
        key = (cell['profile'], 'webgpu', cell['scene'], 'T1-full-silhouette')
        if statistic.get('status') != 'UNMEASURED_EMPTY_SUPPORT' or key not in eligible:
            continue
        zero_support_witness(cell['runs'])
        identity = cell['profile']+'/'+cell['scene']
        path = witness_root/(hashlib.sha256(identity.encode()).hexdigest()+'.json')
        witness = write_once(path, {'schema': 'w50-empty-native-support-witness-1',
            'profile': cell['profile'], 'scene': cell['scene'], 'role': 'blind', 'nativeRead': native_pin})
        witnesses.append({'profile': cell['profile'], 'scene': cell['scene'], 'pin': witness})
    artifacts = {'schema': 'w50-native-exposure-artifacts-1', 'role': 'blind', 'ready': report['ready'],
        'nativeRead': native_pin, 'claim': claim_pin,
        'export': {'path': str(export_root), 'indexSha256': export_hash},
        'fixtures': fixtures, 'emptySupportWitnesses': witnesses,
        'originalArchive': report['originalArchive']}
    artifacts['artifactManifest'] = write_once(destination/'artifacts.json', artifacts)
    dispatcher.require_render_admission(context, run)
    return artifacts


def source_probe():
    """Synthetic-only source closure exercise; no config, archive locator or output is consulted."""
    np = R.np
    rgb = np.full((64, 64, 3), 20, dtype=np.uint8)
    bg = np.zeros_like(rgb)
    readings = R.S.read_frame(rgb, bg, {'kind': 'rrect', 'size': [48, 48], 'radius': 0},
                              {'width': 64, 'height': 64}, 1, include_structured=True)
    runs = [{'run': run, 'readings': readings} for run in (1, 2, 3)]
    zero_support_witness(runs)
    R.aggregate_runs(runs, reported=True)
