"""Endpoint-scoped W41 G1 exposure; Decision Log 7, clauses 2/11, X26, §5.192.

This extends W39's procedural boundary, not its authority. There is no production
log argument, retry, alternate archive, or synthetic production backend. Native
scoring is supplied by a committed module; only that module receives a live token.
Importing this file reads code only, never the receipt or native archive.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time

from PIL import Image

HERE = Path(__file__).resolve().parent
BOUNDARY_PATH = HERE.parents[1] / '2026-09-26-w39-g0-colour-edge-bed/wave.py'
spec = importlib.util.spec_from_file_location('w41_inherited_wave', BOUNDARY_PATH)
boundary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boundary)
ROOT = boundary.ROOT
X6_SOURCES = (
    'packages/calibration/results/2026-09-27-w41-g1-identification/x6/observe.py',
    'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/record-machine.py')
x6_spec = importlib.util.spec_from_file_location('w41_exposure_x6', ROOT / X6_SOURCES[0])
x6 = importlib.util.module_from_spec(x6_spec)
x6_spec.loader.exec_module(x6)  # Code only. No observation, wait loop or machine access at import.
PRODUCTION_LOG = BOUNDARY_PATH.parent / 'wave-identification-receipt.jsonl'
INVENTORY_SHA = '58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61'
INVENTORY_PATH = ('packages/calibration/results/'
                  '2026-09-26-w39-g1-colour-edge-sitting/archive/inventory.json')
POLICY_DIST = 'packages/policy/dist'
# Most runtime packages are source-aliased; policy executes dist and is bound separately.
SOURCE_ROOTS = tuple('packages/' + p + '/src' for p in
                     ('core', 'platform-web', 'renderer-webgpu', 'policy', 'geometry', 'motion')) + (
    'packages/calibration/web', 'packages/calibration/scripts', 'packages/calibration/src')
INSTRUMENT_ROOTS = tuple('packages/calibration/results/' + directory for directory in (
    '2026-09-26-w39-g0-colour-edge-bed', '2026-09-26-w39-g2-identification',
    '2026-09-27-w41-g0-declaration', '2026-09-27-w41-g1-identification'))
CLAIM_DOMAIN = dict(policy='nominal', variant='regular', samplingBackend='gpu-texture',
                    presence=dict(identified=1, intermediate='unmeasured-linear-interpolation',
                                  zero='exact-skip'))
SOURCE_FILES = ('package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'tsconfig.base.json')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def load(path):
    value = json.loads(Path(path).read_text())
    stable(value)  # Reject NaN/Infinity in every nested prediction/configuration.
    return value


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE)


def local(root, name):
    path = root / name
    if not isinstance(name, str) or Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError('artifact must be a repository-relative path')
    if path.is_symlink() or root not in path.resolve().parents:
        raise ValueError('artifact escaped repository or is symlinked: ' + name)
    return path


def committed(root, name):
    path = local(root, name)
    saved = git(root, 'show', 'HEAD:' + name)
    if saved != path.read_bytes():
        raise ValueError('uncommitted frozen input: ' + name)
    return hashlib.sha256(saved).hexdigest()


def sources(root):
    """Include newly-created/ignored source too, so an added import cannot evade freeze."""
    files = {name for name in SOURCE_FILES if (root / name).exists()}
    for directory in SOURCE_ROOTS:
        base = root / directory
        if base.exists():
            files.update(str(p.relative_to(root)) for p in base.rglob('*')
                         if p.is_file() and '__pycache__' not in p.parts)
    for directory in INSTRUMENT_ROOTS:
        files.update(str(p.relative_to(root)) for p in (root / directory).rglob('*.py'))
    for package in ('core', 'platform-web', 'renderer-webgpu', 'policy', 'geometry', 'motion',
                    'calibration'):
        base = root / 'packages' / package
        files.update(str(p.relative_to(root)) for p in base.glob('*.json'))
        files.update(str(p.relative_to(root)) for p in base.glob('*.mjs'))
    return sorted(files)


def coverage(actual, expected, label):
    if set(actual) != set(expected):
        raise ValueError(label + ' coverage mismatch: missing=' + str(sorted(set(expected) - set(actual)))
                         + ', extra=' + str(sorted(set(actual) - set(expected))))


def cells_for(wave, roles, web=False):
    # Metadata inspection does not authorize a holdout read. In particular, do
    # NOT mint a token merely to call launch_plan before the real Receipt.
    ids = {sid for sid, role in wave.roles.items() if role in roles
           and not boundary.native_only(wave.component(sid))}
    if web:
        ids = {sid for sid in ids
               if boundary.web_placement_refusal(wave.component(sid), wave.spec['canvas']) is None}
    return sorted(c for c in wave.cells if c.split('/', 1)[1] in ids)


def admitted_scope(root, wave):
    """Use the fixed committed inventory's cell metadata, never its payload paths.

    Declared but uncaptured phase probes cannot veto a survivor. This intersection
    changes admission only; it neither recuts the split nor narrows standing sheets.
    """
    path = local(root, INVENTORY_PATH)
    if not path.is_file():
        raise ValueError('fixed archive inventory is missing')
    if committed(root, INVENTORY_PATH) != INVENTORY_SHA:
        raise ValueError('fixed archive inventory hash mismatch')
    admitted = {entry['cell'] for entry in load(path)['entries']}
    included, excluded = {}, {}
    for kind in ('numerical', 'rendered'):
        declared = set(cells_for(wave, boundary.ROLES, kind == 'rendered'))
        included[kind] = sorted(declared & admitted)
        excluded[kind] = {cell: 'not admitted by fixed archive inventory'
                          for cell in sorted(declared - admitted)}
    return included, excluded


def verify_runtime_artifacts(root, mapping, *, required):
    """Bind executed policy modules, not a claim that a lockfile attests a build.

    The complete generated JS inventory must match explicit committed evidence
    snapshots byte-for-byte. Empty synthetic configurations need no workspace build.
    """
    if not isinstance(mapping, dict):
        raise ValueError('runtime artifact mapping must be an object')
    if not required and not mapping:
        return
    modules = sorted(str(path.relative_to(root)) for path in (root / POLICY_DIST).rglob('*')
                     if path.is_file() and path.suffix in ('.js', '.mjs', '.cjs'))
    if POLICY_DIST + '/index.js' not in modules:
        raise ValueError('runtime artifact policy entry point is missing')
    coverage(mapping, modules, 'runtime artifact inventory')
    for actual, snapshot in mapping.items():
        if (not isinstance(snapshot, str)
                or not snapshot.startswith('packages/calibration/results/')):
            raise ValueError('runtime artifact snapshot must be committed evidence')
        expected = committed(root, snapshot)
        if sha(local(root, actual)) != expected:
            raise ValueError('runtime artifact differs from committed snapshot: ' + actual)


def dimension(wave, cell):
    profile = cell.split('/', 1)[0]
    match = re.search(r'-(1|2)x-', profile)
    if match is None:
        raise ValueError('unknown device scale: ' + profile)
    scale = int(match[1])
    return (wave.spec['canvas']['width'] * scale, wave.spec['canvas']['height'] * scale)


def png(path, expected=None):
    with Image.open(path) as image:
        image.load()
        if image.format != 'PNG' or image.mode not in ('RGB', 'RGBA'):
            raise ValueError('rendered prediction must be an RGB(A) PNG')
        if expected is not None and image.size != expected:
            raise ValueError('rendered prediction has wrong pixel size')


def endpoint(wave, cell):
    """A claim is a material endpoint, not a chosen scene, scale, colour or bin."""
    profile, sid = cell.split('/', 1)
    scheme = next(p['colorScheme'] for p in wave.spec['profiles'] if p['key'] == profile)
    state = wave.scenes[sid]['state']
    if scheme not in ('light', 'dark') or state not in ('rest', 'inactive'):
        raise ValueError('unsupported endpoint metadata')
    return (scheme, 'active' if state == 'rest' else 'inactive')


def claim_scope(root, wave, candidate):
    if 'claimScope' not in candidate:
        raise ValueError('candidate requires committed claimScope')
    scope = load(local(root, candidate['claimScope']))
    if not isinstance(scope, dict) or set(scope) != {'endpoints', 'domain', 'numericalDomain', 'renderedDeepDomain'}:
        raise ValueError('claim scope must declare endpoints, domain, numericalDomain and renderedDeepDomain only')
    if scope['numericalDomain'] != 'uniform-backdrop':
        raise ValueError('claim scope numericalDomain must be uniform-backdrop')
    if scope['renderedDeepDomain'] != 'uniform-backdrop':
        raise ValueError('claim scope renderedDeepDomain must be uniform-backdrop')
    if stable(scope['domain']) != stable(CLAIM_DOMAIN):
        raise ValueError('claim scope domain is not the identified nominal sampled domain')
    entries = scope['endpoints']
    if not isinstance(entries, list) or not entries:
        raise ValueError('claim scope must be nonempty')
    allowed = {endpoint(wave, c) for c in wave.cells}
    selected = set()
    for item in entries:
        if (not isinstance(item, dict) or set(item) != {'colorScheme', 'activation'}
                or not isinstance(item['colorScheme'], str)
                or not isinstance(item['activation'], str)):
            raise ValueError('claim scope must name only colorScheme and activation')
        pair = (item['colorScheme'], item['activation'])
        if pair not in allowed or pair in selected:
            raise ValueError('claim scope has unknown or duplicate endpoint')
        selected.add(pair)
    return selected


def unclaimed_reason(wave, cell, kind, selected):
    if endpoint(wave, cell) not in selected:
        return 'not claimed (identity)'
    background = wave.spec['backgrounds'][wave.scenes[cell.split('/', 1)[1]]['background']]
    if background['kind'] != 'solid':
        return 'not claimed (structured backdrop)'
    return None


def domain_documents(root, documents):
    """Bind the driver's short file hashes and patches to the frozen config's bytes.

    Paths printed by the capture may name an earlier worktree. The content hash,
    not that incidental absolute pathname, identifies a configured document.
    This mirrors material-profile-file.ts's document/bare-patch extraction only;
    it does not interpret renderer constants or treat a root digest as a tune hash.
    """
    result = {}
    for key, field in (('material', 'materialProfile'), ('receded', 'recededProfile')):
        path = local(root, documents[key])
        document = load(path)
        wrapped = 'patch' in document or 'cssTierMapping' in document
        result[field] = dict(sha256=sha(path)[:12],
                            patch=document.get('patch', {}) if wrapped else document)
        if key == 'material':
            result[field]['cssTierMapping'] = document.get('cssTierMapping') if wrapped else None
    return result


def merge_patch(left, right):
    """The capture page deep-merges candidate recede over active; arrays replace."""
    result = deepcopy(left)
    for key, value in right.items():
        result[key] = (merge_patch(result[key], value)
                       if isinstance(result.get(key), dict) and isinstance(value, dict) else value)
    return result


def validate_domain(wave, identity, descriptor, report, documents):
    """Validate actual producer records, separately from the authored source chain."""
    profile, sid = identity.split('/', 1)
    definition = next(p for p in wave.spec['profiles'] if p['key'] == profile)
    if definition.get('a11y') != 'standard':
        raise ValueError('claim domain requires standard profile metadata')
    page = report.get('page', {})
    policy = page.get('accessibilityPolicy', {})
    groups = page.get('groups', [])
    if (descriptor.get('sceneId') != sid or page.get('sceneId') != sid
            or descriptor.get('renderer') != 'webgpu'
            or descriptor.get('samplingBackend') != 'gpu-texture'
            or page.get('requestedBackdropMode') != 'texture'
            or 'requestedBackdropLevel' not in page or page['requestedBackdropLevel'] is not None
            or any(policy.get(flag) is not False for flag in
                   ('reducedTransparency', 'increasedContrast', 'forcedColors', 'reducedMotion'))
            or not groups or any(g.get('configuredSource') != 'texture'
                or (g.get('state') or {}).get('activeRenderer') != 'webgpu'
                or (g.get('state') or {}).get('samplingBackend') != 'gpu-texture' for g in groups)):
        raise ValueError('capture domain is not nominal actual sampled texture: ' + identity)
    scale = int(re.search(r'-(1|2)x-', profile)[1])
    size = list(dimension(wave, identity))
    if (descriptor.get('pixelSize') != size or page.get('pixelSize') != size
            or page.get('canvas') != wave.spec['canvas']
            or page.get('requestedScale') != scale or page.get('devicePixelRatio') != scale
            or report.get('colorScheme') != definition['colorScheme']
            or page.get('colorScheme') != definition['colorScheme']
            or descriptor.get('engine') != 'chromium' or descriptor.get('colorSpace') != 'srgb'
            or descriptor.get('deterministic') is not True or descriptor.get('repeatNoise') != 0
            or 'fallback' not in report or report['fallback'] is not None
            or report.get('problems') != [] or page.get('problems') != []):
        raise ValueError('capture domain profile/scale/descriptor mismatch: ' + identity)
    for field, expected in documents.items():
        actual = report.get(field) or {}
        if any(key not in actual or actual[key] != value for key, value in expected.items()):
            raise ValueError('capture domain material document mismatch: ' + identity)
    # capture_web always supplies BOTH documents. The producer poses inactive
    # scenes by merging the candidate patch, while deliberately pinning the root
    # active. Requiring root inactive would reject the actual candidate path.
    active = documents['materialProfile']['patch']
    receded = documents['recededProfile']['patch'] if wave.scenes[sid]['state']=='inactive' else None
    # The driver omits an empty active patch; SceneReport serializes that as
    # null. A supplied candidate recede still materializes its merged object.
    posed = merge_patch(active, receded) if receded is not None else active or None
    if (page.get('windowActivation') != 'active'
            or 'candidateRecededMaterialProfile' not in page
            or page['candidateRecededMaterialProfile'] != receded
            or 'recededMaterialProfile' not in page or page['recededMaterialProfile'] is not None
            or 'materialProfile' not in page or page['materialProfile'] != posed
            or 'cssTierMapping' not in page
            or page['cssTierMapping'] != documents['materialProfile']['cssTierMapping']):
        raise ValueError('capture domain actual candidate pose/material mismatch: ' + identity)


def freeze_domain(root, wave, candidate, rendered, source_list, files, runtime):
    if 'domainEvidence' not in candidate:
        raise ValueError('claim domain requires frozen capture domainEvidence')
    evidence_path = candidate['domainEvidence']
    evidence = load(local(root, evidence_path))
    coverage(evidence, ('attestation', 'cells'), 'claim domain evidence fields')
    coverage(evidence['cells'], rendered, 'claim domain records')
    profiles = runtime['candidates'][candidate['id']]['profiles']
    documents = {profile: domain_documents(root, paths) for profile, paths in profiles.items()}
    for cell, record in evidence['cells'].items():
        coverage(record, ('descriptor', 'report'), 'claim domain record fields')
        validate_domain(wave, cell, record['descriptor'], record['report'],
                        documents[cell.split('/', 1)[0]])
    attestation = load(local(root, evidence['attestation']))
    if (attestation.get('basis') != 'source-derived' or attestation.get('variant') != 'regular'
            or type(attestation.get('presence')) not in (int, float) or attestation['presence'] != 1
            or not isinstance(attestation.get('effectivePresenceBasis'), str)
            or not attestation['effectivePresenceBasis'].strip()
            or not isinstance(attestation.get('limitations'), str)
            or not attestation['limitations'].strip()):
        raise ValueError('domain attestation must distinguish source-derived presence from observations')
    chain = attestation.get('sourceChain')
    if not isinstance(chain, list) or not chain:
        raise ValueError('domain attestation requires an effective-presence source chain')
    paths = set()
    for link in chain:
        if (not isinstance(link, dict) or set(link) != {'path', 'sha256', 'claim'}
                or link['path'] not in source_list or link['path'] in paths
                or not isinstance(link['claim'], str) or not link['claim'].strip()
                or sha(local(root, link['path'])) != link['sha256']):
            raise ValueError('domain attestation source chain is missing, stale or unbound')
        paths.add(link['path'])
    if ('packages/calibration/web/scene.ts' not in paths
            or not any(p.startswith(SOURCE_ROOTS[:6]) for p in paths)):
        raise ValueError('domain attestation must bind registration and runtime default source chain')
    files.update((evidence_path, evidence['attestation']))


def observation(row):
    """Validate a returned observation without mistaking a retained miss for a pass."""
    if isinstance(row, dict):
        if row.get('status') == 'measured' and type(row.get('passes')) is bool:
            return 'measured'
        if (row.get('status') == 'UNMEASURED' and row.get('reason') == 'censored'
                and 'passes' in row and row['passes'] is None
                and type(row.get('constraintsPass')) is bool):
            return 'censored'
    raise ValueError('closure failed or UNMEASURED: malformed score')


def aggregate(wave, scores, candidates, claims, numerical, rendered):
    """Keep all scores; bind deep closure on claimed uniform cells and veto everywhere."""
    coverage(scores, candidates, 'native candidate scores')
    measured_coverage, assessments = {}, {}
    for candidate, values in scores.items():
        measured_coverage[candidate], assessments[candidate] = {}, {}
        coverage(values, ('numerical', 'rendered'), 'native score kinds')
        selected = {(e['colorScheme'], e['activation']) for e in claims[candidate]['endpoints']}
        for kind, expected in [('numerical', numerical), ('rendered', rendered)]:
            coverage(values[kind], expected, kind + ' native scores')
            rows = assessments[candidate][kind] = {}
            measured, censored, unclaimed = 0, 0, 0
            for cell, cell_score in values[kind].items():
                state = observation(cell_score)
                if kind == 'rendered' and cell_score.get('vetoPass') is not True:
                    raise ValueError('rendered per-bin veto failed: ' + candidate + '/' + cell)
                reason = unclaimed_reason(wave, cell, kind, selected)
                if reason is not None:
                    if (kind == 'numerical' and reason == 'not claimed (structured backdrop)'
                            and cell_score.get('diagnostic') != 'S0'):
                        raise ValueError('structured numerical reading requires S0 diagnostic')
                    unclaimed += 1
                    rows[cell] = dict(status=reason, passes=None, score=cell_score)
                    continue
                rows[cell] = cell_score
                if state == 'measured' and cell_score['passes'] is True:
                    measured += 1
                elif state == 'censored' and cell_score['constraintsPass'] is True:
                    censored += 1
                else:
                    raise ValueError('closure failed or UNMEASURED: '
                                     + candidate + '/' + kind + '/' + cell)
            total = len(expected) - unclaimed
            measured_coverage[candidate][kind] = dict(
                measured=measured, censored=censored, total=total,
                fraction=measured / total if total else None,
                scoredTotal=len(expected), notClaimed=unclaimed)
    return measured_coverage, assessments


def freeze(root, wave, candidates, *, config, scorer, declaration, closure,
           instruments=(), dry_cells=None):
    """Return a manifest to commit BEFORE exposure; build bytes need committed snapshots.

    Production covers declared AND archive-admitted glass cells numerically and
    their web-plannable subset, across calibration, validation AND holdout.
    A scratch manifest instead covers an explicit nonempty calibration subset.
    """
    root = Path(root).resolve()
    dry = dry_cells is not None
    if not dry and root != ROOT:
        raise ValueError('production freeze belongs to the inherited W39 repository')
    excluded = {'numerical': {}, 'rendered': {}}
    if dry:
        numerical = sorted(set(dry_cells))
        rendered = sorted(set(numerical) & set(cells_for(wave, ('calibration',), True)))
    else:
        included, excluded = admitted_scope(root, wave)
        numerical, rendered = included['numerical'], included['rendered']
    if not numerical or (dry and not set(numerical) <= set(cells_for(wave, ('calibration',)))):
        raise ValueError('synthetic stand-ins must be nonempty calibration glass cells')
    if not rendered:
        raise ValueError('no web-plannable coverage')
    if not candidates or len({c['id'] for c in candidates}) != len(candidates):
        raise ValueError('candidate identities must be nonempty and unique')
    for candidate in candidates:
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', candidate['id']):
            raise ValueError('unsafe candidate identity')
    source_list = sources(root)
    schema_path = str((HERE / 'manifest.schema.json').relative_to(ROOT))
    files = set(source_list) | {config, scorer, declaration, closure, schema_path} | set(instruments)
    files.update(str(p.resolve().relative_to(root)) for p in (wave.scenes_path, wave.split_path))
    if not dry:
        for name in X6_SOURCES:
            if not local(root, name).is_file() or name not in source_list:
                raise ValueError('required X6 observer source missing: ' + name)
        files.update(X6_SOURCES)
        files.add(INVENTORY_PATH)
        g0 = HERE.parents[1] / '2026-09-27-w41-g0-declaration'
        if (local(root, declaration) != g0 / 'bounds-declaration.txt'
                or local(root, closure) != g0 / 'closure.json'):
            raise ValueError('production must bind the unchanged W41 G0 declaration')
        files.update(str(p.relative_to(root)) for p in
                     (BOUNDARY_PATH, Path(__file__).resolve(), BOUNDARY_PATH.parent / 'w39_readers.py',
                      BOUNDARY_PATH.parent / 'w39_archive.py', BOUNDARY_PATH.parent / 'pins.json'))
        if sha(local(root, declaration)) != load(local(root, closure))['boundsDeclarationSha256']:
            raise ValueError('declaration/closure hash disagreement')
    runtime = load(local(root, config))
    runtime_artifacts = runtime.get('runtimeArtifacts', {})
    verify_runtime_artifacts(root, runtime_artifacts, required=not dry)
    files.update(runtime_artifacts.values())
    coverage(runtime['candidates'], [c['id'] for c in candidates], 'renderer candidates')
    for candidate in candidates:
        profiles = runtime['candidates'][candidate['id']]['profiles']
        coverage(profiles, {c.split('/', 1)[0] for c in rendered}, 'renderer profiles')
        for documents in profiles.values():
            coverage(documents, ('material', 'receded'), 'material document pair')
            files.update(documents.values())
    if not dry:
        fixture = local(root, runtime['fixtures'])
        if not (fixture / 'manifest.json').is_file():
            raise ValueError('committed web backdrop manifest absent')
        backdrop_manifest = load(fixture / 'manifest.json')
        if set(backdrop_manifest) - {'schema', 'backgrounds'}:
            raise ValueError('web backdrop bundle must not contain native fixture metadata')
        files.add(str((fixture / 'manifest.json').relative_to(root)))
        for cell in rendered:
            profile, sid = cell.split('/', 1)
            scale = int(re.search(r'-(1|2)x-', profile)[1])
            background = wave.scenes[sid]['background']
            raster = backdrop_manifest['backgrounds'][f'{background}@{scale}x']
            raster_path = local(fixture, raster)
            png(raster_path, dimension(wave, cell))
            files.add(str(raster_path.relative_to(root)))
    claims, identity_equality = {}, {}
    for candidate in candidates:
        selected = claim_scope(root, wave, candidate)
        freeze_domain(root, wave, candidate, rendered, source_list, files, runtime)
        if not any(endpoint(wave, c) in selected for c in numerical):
            raise ValueError('claim scope contains no admitted cells')
        claims[candidate['id']] = load(local(root, candidate['claimScope']))
        files.update(candidate[k] for k in ('parameters', 'predictions', 'rendered', 'survival',
                                             'claimScope'))
        parameters = load(local(root, candidate['parameters']))
        if not parameters:
            raise ValueError('empty numerical candidate')
        predictions = load(local(root, candidate['predictions']))['cells']
        coverage(predictions, numerical, 'numerical predictions')
        if any(value is None or value == {} or value == [] for value in predictions.values()):
            raise ValueError('empty numerical prediction payload')
        images = load(local(root, candidate['rendered']))['cells']
        coverage(images, rendered, 'rendered predictions')
        for cell, prediction in images.items():
            coverage(prediction, ('png', 'projection'), 'rendered artifacts')
            files.update(prediction.values())
            png(local(root, prediction['png']), None if dry else dimension(wave, cell))
            if load(local(root, prediction['projection'])) is None:
                raise ValueError('empty rendered projection')
        survival = load(local(root, candidate['survival']))
        for kind, expected in [('numerical', numerical), ('rendered', rendered)]:
            before = [c for c in expected if wave.roles[c.split('/', 1)[1]] != 'holdout']
            coverage(survival[kind], before, kind + ' pre-exposure survival')
            for cell, value in survival[kind].items():
                reason = unclaimed_reason(wave, cell, kind, selected)
                if reason is None:
                    if value is not True:
                        raise ValueError('candidate did not survive before freeze')
                else:
                    if (not isinstance(value, dict)
                            or value.get('status') != reason
                            or 'passes' not in value or value['passes'] is not None):
                        raise ValueError('unclaimed survival must report ' + reason)
                    observation(value.get('score'))
                    if (kind == 'numerical' and reason == 'not claimed (structured backdrop)'
                            and value['score'].get('diagnostic') != 'S0'):
                        raise ValueError('structured numerical reading requires S0 diagnostic')
        before_web = [c for c in rendered if wave.roles[c.split('/', 1)[1]] != 'holdout']
        coverage(survival.get('veto', {}), before_web, 'rendered per-bin veto')
        if any(value is not True for value in survival['veto'].values()):
            raise ValueError('rendered per-bin veto failed before freeze')
        unclaimed = [c for c in rendered if endpoint(wave, c) not in selected]
        equality = identity_equality[candidate['id']] = {}
        if unclaimed or 'identityBaseline' in candidate:
            if 'identityBaseline' not in candidate:
                raise ValueError('unclaimed endpoints require committed identity baseline')
            files.add(candidate['identityBaseline'])
            baseline = load(local(root, candidate['identityBaseline']))['cells']
            coverage(baseline, unclaimed, 'identity baseline')
            for cell, artifact in baseline.items():
                coverage(artifact, ('png', 'projection'), 'identity baseline artifacts')
                files.update(artifact.values())
                baseline_png = local(root, artifact['png'])
                png(baseline_png, None if dry else dimension(wave, cell))
                candidate_png = local(root, images[cell]['png'])
                baseline_projection = load(local(root, artifact['projection']))
                candidate_projection = load(local(root, images[cell]['projection']))
                if (sha(baseline_png) != sha(candidate_png)
                        or stable(baseline_projection) != stable(candidate_projection)):
                    raise ValueError('identity baseline differs from candidate: ' + cell)
                equality[cell] = dict(
                    role=wave.roles[cell.split('/', 1)[1]],
                    baseline=artifact, candidate=images[cell],
                    baselinePngSha256=sha(baseline_png), candidatePngSha256=sha(candidate_png),
                    baselineProjectionSha256=sha(local(root, artifact['projection'])),
                    candidateProjectionSha256=sha(local(root, images[cell]['projection'])))
    hashes = {name: committed(root, name) for name in sorted(files)}
    return dict(schema='w41-renderer-exposure-2', mode='synthetic' if dry else 'production',
                revision=git(root, 'rev-parse', 'HEAD').decode().strip(),
                boundarySha256=sha(BOUNDARY_PATH), runnerSha256=sha(__file__),
                scenes=wave.scenes_sha, split=wave.split_sha,
                generation=[hashlib.sha256(b'W41 synthetic calibration only').hexdigest()
                            if dry else INVENTORY_SHA],
                inventory=None if dry else INVENTORY_PATH, excludedCells=excluded,
                runtimeArtifacts=runtime_artifacts, claimScopes=claims, identityEquality=identity_equality,
                numericalCells=numerical, renderedCells=rendered,
                sourceFiles=source_list, files=hashes, candidates=candidates,
                config=config, scorer=scorer, declaration=declaration, closure=closure,
                instruments=list(instruments))


def verify(root, wave, manifest_path, mode):
    manifest_path = Path(manifest_path).resolve()
    committed(root, str(manifest_path.relative_to(root)))
    manifest = load(manifest_path)
    if manifest.get('schema') != 'w41-renderer-exposure-2' or manifest.get('mode') != mode:
        raise ValueError('wrong exposure manifest mode/schema')
    if sha(BOUNDARY_PATH) != manifest['boundarySha256'] or sha(__file__) != manifest['runnerSha256']:
        raise ValueError('receipt boundary or runner mutated after freeze')
    if manifest['sourceFiles'] != sources(root):
        raise ValueError('renderer source inventory changed after freeze')
    for name, expected in manifest['files'].items():
        if committed(root, name) != expected:
            raise ValueError('frozen artifact changed: ' + name)
    # Source revision is not HEAD: the later commit containing the manifest must
    # not change its frozen source. Prove each source belonged to that revision.
    for name in manifest['sourceFiles']:
        saved = git(root, 'show', manifest['revision'] + ':' + name)
        if hashlib.sha256(saved).hexdigest() != manifest['files'][name]:
            raise ValueError('renderer revision does not own source: ' + name)
    rebuilt = freeze(root, wave, manifest['candidates'], config=manifest['config'],
                     scorer=manifest['scorer'], declaration=manifest['declaration'],
                     closure=manifest['closure'], instruments=manifest['instruments'],
                     dry_cells=manifest['numericalCells'] if mode == 'synthetic' else None)
    rebuilt['revision'] = manifest['revision']
    if stable(rebuilt) != stable(manifest):
        raise ValueError('manifest does not describe the complete frozen configuration')
    return manifest


@dataclass(frozen=True)
class CaptureRequest:
    wave: object
    authorization: object
    root: Path
    manifest: dict
    candidate: str
    cells: tuple
    output: Path
    verify_snapshot: object = None
    wait_budget: object = None


@dataclass
class X6WaitBudget:
    """Shared across every candidate/profile; browser and scoring time never enter it."""
    used_seconds: float = 0.0


@dataclass(frozen=True)
class ScoreRequest:
    wave: object
    authorization: object
    root: Path
    manifest: dict
    candidates: dict
    numerical_cells: tuple
    rendered_cells: tuple
    captures: dict


def observe_x6():
    """One fresh observation; never call the observer's bounded-wait CLI here."""
    return x6.observe()


def x6_record(root, manifest, candidate, profile, error_path):
    """Read one observation; exceptions retain unknown facts, never synthetic failures."""
    source_hashes = {}
    for name, executed in zip(X6_SOURCES, (x6.__file__, x6.machine.__file__), strict=True):
        expected = manifest['files'].get(name)
        if not expected or sha(root / name) != expected or sha(executed) != expected:
            raise ValueError('X6 observer source is not bound to the freeze: ' + name)
        source_hashes[name] = expected
    record = dict(candidate=candidate, profile=profile, sources=source_hashes,
                  observation=None, verdict=None)
    try:
        record['observation'] = observe_x6()
        record['verdict'] = x6.verdict(record['observation'])
    except Exception as error:
        record.update(status='observation-error', error=dict(
            type=type(error).__name__, message=str(error)))
        persist(error_path, record)
        raise
    return record


def prebegin_x6(root, manifest, output):
    """A fresh PASS is required before begin; no waiting or receipt exists here."""
    path = output / 'x6-prebegin.json'
    record = x6_record(root, manifest, None, None, path)
    record['status'] = 'passed' if record['verdict']['passes'] else 'refused'
    persist(path, record)
    if not record['verdict']['passes']:
        raise PermissionError('X6 pre-begin gate refused; receipt not begun')


def prelaunch_x6(request, profile):
    """Wait on machine facts only, sharing one cumulative hour inside this receipt."""
    request.authorization.check(request.wave)
    if request.wait_budget is None or request.verify_snapshot is None:
        raise ValueError('X6 launch requires shared waiting budget and frozen snapshot verifier')
    started = time.monotonic()
    already_used = request.wait_budget.used_seconds
    summary = request.output / ('x6-' + profile + '.json')
    attempt = 0
    try:
        while True:
            request.authorization.check(request.wave)
            attempt += 1
            path = request.output / f'x6-{profile}-observation-{attempt:04d}.json'
            record = x6_record(request.root, request.manifest, request.candidate, profile, path)
            elapsed = already_used + time.monotonic() - started
            record.update(observationNumber=attempt, cumulativeWaitSeconds=elapsed,
                          waitBudgetSeconds=3600)
            if record['verdict']['passes'] and elapsed <= 3600:
                try:
                    # The waiting interval may have outlived the original preflight.
                    # Revalidate the full snapshot before any browser process can start.
                    request.verify_snapshot()
                except Exception as error:
                    record.update(status='snapshot-error', error=dict(
                        type=type(error).__name__, message=str(error)))
                    persist(path, record)
                    persist(summary, record)
                    raise
                elapsed = already_used + time.monotonic() - started
                record['cumulativeWaitSeconds'] = elapsed
                if elapsed <= 3600:
                    record['status'] = 'passed'
                    persist(path, record)
                    persist(summary, record)
                    return
            record['status'] = 'deadline-exceeded' if elapsed >= 3600 else 'waiting'
            persist(path, record)  # Every observation is durable before sleep or launch.
            if elapsed >= 3600:
                persist(summary, record)
                raise PermissionError('X6 cumulative waiting budget exhausted before browser launch')
            time.sleep(min(30, 3600 - elapsed))
    finally:
        # Account only time inside guards; captures between them are explicitly excluded.
        request.wait_budget.used_seconds = already_used + time.monotonic() - started


def capture_web(request):
    """Real web-only backend. No compare/matrix CLI, native Reader or harness bundle.

    Uses the existing Chromium driver with source aliases and the bound policy build.
    It captures once per candidate/profile.
    Its two independent page loads are a single capture's determinism measurement,
    not a retry of the archive exposure. Any process/cell failure propagates.
    """
    request.authorization.check(request.wave)
    runtime = load(request.root / request.manifest['config'])
    profiles = runtime['candidates'][request.candidate]['profiles']
    definitions = {p['key']: p for p in request.wave.spec['profiles']}
    env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
    env.update(VITREA_SCENES=str(request.wave.scenes_path),
               VITREA_FIXTURES=str(request.root / runtime['fixtures']),
               VITREA_ALLOW_FALLBACK_ADAPTER='0')
    answer = {}
    for profile in sorted({cell.split('/', 1)[0] for cell in request.cells}):
        request.authorization.check(request.wave)
        ids = sorted(cell.split('/', 1)[1] for cell in request.cells if cell.startswith(profile + '/'))
        documents = profiles[profile]
        scale = int(re.search(r'-(1|2)x-', profile)[1])
        destination = request.output / profile
        command = ['pnpm', '--dir', str(request.root / 'packages/calibration'), 'exec', 'tsx',
                   'scripts/capture-web.ts', *ids, '--renderer', 'webgpu', '--color-scheme',
                   definitions[profile]['colorScheme'], '--scale', str(scale), '--out', str(destination),
                   '--material-profile', str(request.root / documents['material']),
                   '--receded-profile', str(request.root / documents['receded'])]
        prelaunch_x6(request, profile)
        subprocess.run(command, env=env, check=True)
        request.authorization.check(request.wave)
        for sid in ids:
            directory = destination / sid
            cell = load(directory / 'cell__webgpu.json')
            report = load(directory / 'report__webgpu.json')
            identity = profile + '/' + sid
            validate_domain(request.wave, identity, cell, report,
                            domain_documents(request.root, documents))
            answer[identity] = directory / (sid + '__webgpu.png')
    return answer


def scratch_path(path):
    """Scratch can neither name nor alias the production log, even before it exists."""
    path = Path(path).resolve()
    if path == PRODUCTION_LOG.resolve() or ROOT == path or ROOT in path.parents:
        raise PermissionError('synthetic/output path must be outside the evidence repository')
    # Do not open/read/stat the production receipt in G0. A hardlink necessarily
    # has multiple links and is refused without resolving its other name.
    if path.exists() and (path.is_symlink() or path.stat().st_nlink != 1):
        raise PermissionError('scratch path cannot be a filesystem alias')
    return path


def persist(path, value):
    """Install one runner-owned evidence file durably; never overwrite an earlier reading."""
    payload = stable(value) + '\n'
    with path.open('x') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def _run(root, wave, manifest_path, log, output, capture, project, score, mode):
    root = Path(root).resolve()
    manifest = verify(root, wave, manifest_path, mode)
    manifest_sha = sha(manifest_path)
    output = scratch_path(output)
    score_report = Path(log).with_name(Path(log).stem + '-scores.json')
    if output.exists() or score_report.exists():
        raise ValueError('capture destination or score record already exists; no reuse or retry')
    numerical = [c for c in manifest['numericalCells']
                 if mode == 'synthetic' or wave.roles[c.split('/', 1)[1]] == 'holdout']
    rendered = [c for c in manifest['renderedCells']
                if mode == 'synthetic' or wave.roles[c.split('/', 1)[1]] == 'holdout']
    candidates = {c['id']: c for c in manifest['candidates']}
    configuration = dict(scenes=manifest['scenes'], split=manifest['split'],
                         generation=manifest['generation'], instrument=manifest['boundarySha256'],
                         closure=manifest['files'][manifest['closure']],
                         candidate=manifest['candidates'], frozenFiles=manifest['files'],
                         manifestSha256=manifest_sha, mode=mode, claimScopes=manifest['claimScopes'],
                         renderer=dict(revision=manifest['revision'],
                                       runtimeArtifacts=manifest['runtimeArtifacts'],
                                       sources={p: manifest['files'][p] for p in manifest['sourceFiles']},
                                       configuration=manifest['files'][manifest['config']]))

    def verify_snapshot():
        if (sha(manifest_path) != manifest_sha
                or verify(root, wave, manifest_path, mode) != manifest):
            raise ValueError('frozen manifest mutated during exposure')

    wait_budget = X6WaitBudget()
    if mode == 'production':
        output.mkdir(parents=True, exist_ok=False)
        prebegin_x6(root, manifest, output)

    # No closure assertion or capture occurs before begin. Failure after this
    # point spends W39's complete exposure, even if no native pixel was reached.
    with boundary.Receipt(log, configuration).expose() as authorization:
        if mode != 'production':
            output.mkdir(parents=True, exist_ok=False)
        result = dict(mode=mode, numericalCells=len(numerical), renderedCells=len(rendered),
                      candidates=len(candidates), manifestSha256=manifest_sha, captures={},
                      claimScopes=manifest['claimScopes'], identityEquality=manifest['identityEquality'])
        try:
            authorization.check(wave)
            if mode == 'production':
                planned = wave.launch_scenes(('holdout',), authorization)
                coverage({c.split('/', 1)[1] for c in rendered}, planned, 'authorized web plan')
            captures = {}
            for candidate in manifest['candidates']:
                destination = output / candidate['id']
                destination.mkdir()
                # Dataclass freezing alone does not protect nested dicts. Callbacks
                # get detached snapshots; no callback owns the comparison state.
                request = CaptureRequest(wave, authorization, root, deepcopy(manifest),
                                         candidate['id'], tuple(rendered), destination,
                                         verify_snapshot, wait_budget)
                captured = capture(request)
                verify_runtime_artifacts(root, manifest['runtimeArtifacts'],
                                         required=mode == 'production')
                if request.manifest != manifest:
                    raise ValueError('capture callback mutated its manifest')
                coverage(captured, rendered, 'captured cells')
                frozen = load(root / candidate['rendered'])['cells']
                verified = {}
                records = result['captures'][candidate['id']] = {}
                for cell, path in captured.items():
                    path = Path(path).resolve()
                    if destination not in path.parents or not path.is_file():
                        raise ValueError('capture backend returned a missing or reused artifact')
                    digest = sha(path)
                    records[cell] = dict(path=str(path), sha256=digest)
                    if mode == 'production':
                        sidecars = [path.parent / name for name in
                                    ('cell__webgpu.json', 'report__webgpu.json')]
                        records[cell]['domainEvidence'] = {str(p): sha(p) for p in sidecars}
                    png(path, None if mode == 'synthetic' else dimension(wave, cell))
                    if digest != manifest['files'][frozen[cell]['png']]:
                        raise ValueError('capture changed a frozen rendered prediction')
                    projection = project(cell, path)
                    verify_runtime_artifacts(root, manifest['runtimeArtifacts'],
                                             required=mode == 'production')
                    if stable(projection) != stable(load(root / frozen[cell]['projection'])):
                        raise ValueError('capture changed a frozen rendered prediction projection')
                    verified[cell] = path
                captures[candidate['id']] = verified
            verify_snapshot()
            request = ScoreRequest(wave, authorization, root, deepcopy(manifest),
                                   deepcopy(candidates), tuple(numerical), tuple(rendered),
                                   deepcopy(captures))
            # Preserve the complete returned JSON before any verdict, including
            # callback/freeze checks. This receipt-adjacent record is authoritative
            # even if a later check fails or the process dies before result.json.
            scores = json.loads(stable(score(request)))
            result['scores'] = scores
            persist(score_report, dict(result, status='scored'))
            result['scoreReport'] = dict(path=str(score_report), sha256=sha(score_report))
            if (request.manifest != manifest or request.candidates != candidates
                    or request.captures != captures):
                raise ValueError('score callback mutated its input snapshots')
            verify_snapshot()
            for candidate, paths in captures.items():
                for cell, path in paths.items():
                    record = result['captures'][candidate][cell]
                    if sha(path) != record['sha256']:
                        raise ValueError('capture mutated during scoring')
                    for sidecar, expected in record.get('domainEvidence', {}).items():
                        if sha(sidecar) != expected:
                            raise ValueError('capture domain evidence mutated during scoring')
            measured_coverage, assessments = aggregate(
                wave, scores, candidates, manifest['claimScopes'], numerical, rendered)
            result.update(status='complete', coverage=measured_coverage, assessments=assessments)
        except BaseException as error:
            result.update(status='failed', error=dict(type=type(error).__name__, message=str(error)))
            persist(output / 'result.json', result)
            raise
        # Persist the verdict before the Receipt can append complete.
        persist(output / 'result.json', result)
    return result


def run_synthetic(root, wave, manifest_path, log, output, capture, project, score):
    """Synthetic only: injected backend, calibration cells, external scratch log."""
    log = scratch_path(log)
    # Check spent before the output-exists guard so a failed attempt cannot look
    # retryable simply because its scratch capture directory remains on disk.
    if log.exists() and log.stat().st_size:
        raise PermissionError('scratch exposure already spent')
    return _run(root, wave, manifest_path, log, output, capture, project, score, 'synthetic')


def run_production(manifest_path, output):
    """G1 only. The committed scorer implements project(cell, png) and score(request).

    The scorer must construct native Readers with request.authorization and read
    only generation-pinned fetched evidence. No scorer import happens in G0.
    """
    wave = boundary.default_wave()
    manifest = verify(ROOT, wave, manifest_path, 'production')
    source = ROOT / manifest['scorer']
    module_spec = importlib.util.spec_from_file_location('w41_frozen_scorer', source)
    module = importlib.util.module_from_spec(module_spec)
    # Module import belongs INSIDE authorization too; a module with import-time
    # native reads cannot perform them before the exposure is spent.
    loaded = False

    def module_ready():
        nonlocal loaded
        if not loaded:
            module_spec.loader.exec_module(module)
            loaded = True
        return module

    return _run(ROOT, wave, manifest_path, PRODUCTION_LOG, output, capture_web,
                lambda cell, path: module_ready().project(cell, path),
                lambda request: module_ready().score(request), 'production')
