"""LIVE native role: the single exposure's one-shot blind native preparation (DL5k).

LIVE first calls admit(context, config) at stage 'native-admission': every check prepare makes
before it writes its one-shot claim or opens a frame, read-only, so a refusal is an ordinary
recoverable stop that leaves no marker. Only then does LIVE write native.started.json and call
prepare(context, config) at stage 'native', once per logical exposure; a started preparation is
never replayed, whatever stops it, and prepare re-checks everything admit checked. Later
attempts call verify(context, payload, config) at 'qualification' on the retained checkpoint.

exposure/prepare.py (sealed in the current3 closure) supplies the science unchanged: blind
membership, original-role row selection, the role export, fixture planning/copying and the
native reader's per-frame readings and three-run aggregation. Its entrypoints authenticate
through the whole-batch dispatcher's render admission, which LIVE issues only to a remaining
capture member, and its admission binds the LOGICAL claim's pid/lease, which only the first
attempt's process holds. So this role owns the admission (LIVE's require_native_preparation,
this attempt's claim held by this process, and every policy check of prepare.admission
unchanged), replaces only prepare's private `_require_preparation` hook in its own sourced
instance with the native-stage equivalent, and orchestrates prepare_native_exposure's steps in
the same order and layout. current3 repeat/sources.blind_cell and current2
native_evidence._blind_authority read exactly that layout at analysis.

One step is this role's own: _measure_blind keeps prepare._measure_blind's reading, ordering
and report shape, and changes only what may stop the read, because a started read is never
replayed (DL5k) and a deterministic property of the blind data must yield a verdict, never a
burned exposure (DL5m item 4, DL5n). A DL5a/b/c REPORTED statistic never stops: an incomplete
one is UNMEASURED_REPORTED with a metadata-only cause, and a DL5c-eligible key becomes
UNMEASURED_EMPTY_SUPPORT only with three genuine zero-support witnesses. A REQUIRED statistic
that is unmeasurable or whose native spread passes the sealed one-code stop is a stop exactly
as before; the read still completes, ready false, and its stops travel as metadata (cell,
statistic, reason; no repeat values) so the affected required rows reach the judge UNMEASURED.
Where no such case arises the artifacts are byte-identical to prepare_native_exposure's.

The payload is {ready, complete, stops, nativeExposure, artifacts}: metadata and content pins
only. Neither prepare nor verify prints; verify hashes the protected files and compares the
native read's stop list (metadata) with the payload's, without formatting a native value.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
SCHEMA = 'w50-native-exposure-inputs-1'
PAYLOAD = {'ready', 'complete', 'stops', 'nativeExposure', 'artifacts'}
STOP = ('cell', 'statistic', 'reason')
REASONS = ('UNMEASURED_UNAUTHORISED_POPULATION', 'NATIVE_SPREAD_EXCEEDS_ONE_CODE')


def _source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


CM = _source(HERE/'common.py', 'w50_live_native_common')
P = _source(FIT/'exposure/prepare.py', 'w50_live_native_prepare')
ROUTER = _source(FIT/'live/router.py', 'w50_live_native_router')


def _admit_run(context, live, run, capability=None):
    """Render admission's checks in their native-stage form: this exposure's own capability,
    a logical new-bed candidate run, its numerical admission and its admitted endpoints."""
    (capability or live.require_native_preparation)(context)
    if run not in context['batch']['runs'] or run.get('sceneSource') != 'w50':
        raise ValueError('Native preparation authenticates only a logical new-bed exposure run')
    numerical = CM.read(context['logicalClaim']['path']).get('numericalAdmission')
    if numerical is None: raise ValueError('Candidate exposure has no numerical admission')
    live.checked(context['repo'], numerical)
    root = live.sealed(context['executionRoot'])
    live.admission_module(root).endpoints(root, run['candidate'], current=False)
    return run


def _require_preparation(context, run):
    """prepare._require_preparation with LIVE's native capability in place of render admission;
    the one-shot claim checks are the original's."""
    live = sys.modules.get('w50_g1_dispatch')
    if live is None: raise ValueError('Direct native file read: no dispatcher capability')
    _admit_run(context, live, run)
    if context['phase'] != 'exposure': raise ValueError('Native blind file reading is exposure-only')
    claim = Path(context['output'])/'native-blind.started.json'
    if not claim.is_file(): raise ValueError('Native blind file reading lacks the one-shot preparation claim')
    record = live.load(claim)
    if record.get('schema') != 'w50-native-blind-claim-1' or record.get('role') != 'blind' \
            or record.get('dispatcherContract') != P.external_pin(context['contract']) \
            or record.get('dispatcherClaim') != P.external_pin(context['contract']+'.started.json') \
            or record.get('batch') != P.external_pin(context['batchPath']):
        raise ValueError('Native blind preparation claim differs from the live exposure')


P._require_preparation = _require_preparation


def admission(context, live, config_pin, capability=None):
    """prepare.admission's policy, bound to LIVE's native capability and this attempt's claim.

    The root's bootstrap identity is LIVE's own process admission (dispatch._prepare), so it is
    not repeated against a module path here. The logical claim keeps its phase/contract/batch/
    output binding; its pid/lease belong to the first attempt, so the process/lease binding is
    this attempt's claim (common.execution_claim). `capability` is the stage's own LIVE grant:
    preparation by default, the read-only pre-start admission for admit."""
    capability = capability or live.require_native_preparation
    capability(context)
    CM.execution_claim(context, live)
    if context['phase'] != 'exposure': raise ValueError('Native blind preparation is exposure-only')
    repo = Path(context['repo'])
    root = live.sealed(context['executionRoot'])
    if config_pin not in root['inputs'] or config_pin not in context['inputs']:
        raise ValueError('Blind input config is not pinned by the admitted dispatcher root')
    newbed = [r for r in context['batch']['runs'] if r.get('sceneSource') == 'w50']
    if not newbed or any(r.get('nativeExposureConfig') != config_pin for r in newbed):
        raise ValueError('W50 exposure requires one shared registered nativeExposureConfig pin')
    for run in newbed: _admit_run(context, live, run, capability)
    contract = live.sealed(context['contract'])
    claim = CM.read(context['logicalClaim']['path'])
    if claim.get('phase') != 'exposure' or claim.get('contractSha256') != live.sha(context['contract']) \
            or claim.get('batchSha256') != live.sha(context['batchPath']) or claim.get('output') != context['output']:
        raise ValueError('Native exposure logical claim differs from the live invocation')
    gate = live.checked(repo, contract['gateContract'])
    live.checked(repo, contract['gateResult'])
    result = live.result_for(gate)
    cohort = context['batch']['cohort']
    pending = (root.get('phaseDependencies') or {}).get('pendingOwnerKeys')
    if contract.get('phase') != 'exposure' or contract.get('cohort') != cohort \
            or live.sealed(gate).get('cohort') != cohort \
            or result['report'].get('status') != 'PASS_EXPOSED_OWNER_PENDING' \
            or result['report'].get('ownerChecks') != 'PENDING_FULL_UNION' \
            or not isinstance(pending, list) or result['report'].get('pendingOwnerKeys') != pending \
            or result['report'].get('candidateSha256s') != sorted(p['sha256'] for p in cohort):
        raise ValueError('Native exposure lacks same-candidate exposed gate PASS with owner rows pending')
    config = live.load(live.checked(repo, config_pin))
    if config.get('schema') != SCHEMA: raise ValueError('Unknown native exposure input schema')
    for name in ('partOne', 'partTwo', 'manifest'):
        if config.get(name) != root[name]: raise ValueError('Native exposure substituted immutable G0 inputs')
    paths = {name: live.checked(repo, config[name]) for name in ('partOne', 'partTwo', 'manifest', 'scenes', 'pack')}
    one, two = live.load(paths['partOne']), live.load(paths['partTwo'])
    if two.get('partOneSha256') != config['partOne']['sha256']: raise ValueError('Native exposure G0 parts differ')
    for part in (one, two):
        if config['manifest'] not in part['sources'] or config['scenes'] not in part['sources']:
            raise ValueError('Native exposure bed/scenes are not sealed by both G0 parts')
    pack = live.load(paths['pack'])
    asset = config.get('archiveAsset', {})
    if pack.get('declarationSha256') != config['partOne']['sha256'] \
            or pack.get('indexSha256') != config.get('archiveIndexSha256') \
            or pack.get('sha256') != asset.get('sha256'):
        raise ValueError('Original archive/index pins differ from the pinned G1 pack')
    if not isinstance(asset.get('path'), str) or not Path(asset['path']).is_absolute() \
            or not isinstance(config.get('archiveRoot'), str) or not Path(config['archiveRoot']).is_absolute():
        raise ValueError('Native exposure needs explicit absolute downloaded archive/asset paths')
    P.R.digest(config['archiveIndexSha256'], 'Original archive index hash')
    P.R.digest(asset['sha256'], 'Original archive asset hash')
    manifest, scenes = live.load(paths['manifest']), live.load(paths['scenes'])
    cells, _ = P.blind_membership(manifest, scenes)
    requested = {(r['profile'], s) for r in context['batch']['runs'] for s in r['scenes']}
    if not {(c['profile'], c['scene']) for c in cells.values()} <= requested:
        raise ValueError('Native blind cells are outside the admitted exposure batch')
    reported = set(P.R.reported_reference_keys(manifest, scenes))
    identities = {(c['profile'], c['scene']) for c in cells.values()}
    if {k for k in reported if (k[0], k[2]) in identities} != \
            {tuple(k) for k in root['reportedKeys'] if (k[0], k[2]) in identities} \
            or set(P.empty_support_keys(manifest, scenes)) != \
            {tuple(k) for k in root['emptySupportKeys'] if (k[0], k[2]) in identities}:
        raise ValueError('Native blind reporting/empty-support keys differ from the exact root enumeration')
    return newbed, config, manifest, scenes


def _fresh_destination(config, destination):
    archive = Path(config['archiveRoot']).resolve()
    if destination.exists() or destination.is_symlink() \
            or destination.resolve().is_relative_to(archive) or archive.is_relative_to(destination.resolve()):
        raise ValueError('Native exposure destination exists or overlaps its original archive')
    return archive


def admit(context, config):
    """Read-only pre-start admission (DL5k), before LIVE writes native.started.json.

    Every check prepare runs before its one-shot claim or its first decoded frame: root/config
    pins, the runs' shape and admission, the logical claim and gate binding, a fresh
    destination, the downloaded asset's compressed-bytes hash, the archive's own verify_archive
    (index hash and sidecar, every member's bytes against the index, exact membership), the blind
    rows' original identities and the index-only fixture plan against every immutable run. So a
    corrupt or partly extracted frame refuses here, as an ordinary recoverable stop, rather than
    in prepare after the marker. It reads JSON and hashes bytes; it decodes no image, computes
    no statistic and writes nothing. prepare repeats every one of these checks."""
    live = CM.dispatcher(context, 'native-admission')
    newbed, settings, manifest, scenes = admission(context, live, config, live.require_native_admission)
    destination = Path(context['output'])/'native-blind'
    archive = _fresh_destination(settings, destination)
    if destination.with_name('native-blind.started.json').exists():
        raise ValueError('Native blind preparation claim already exists')
    asset = settings['archiveAsset']
    if not Path(asset['path']).is_file() or P.sha(asset['path']) != asset['sha256']:
        raise ValueError('Original downloaded archive asset hash mismatch')
    index = P.A.verify_archive(archive, settings['archiveIndexSha256'])
    P.selected_rows(index, manifest, scenes, settings['partOne']['sha256'])
    plans = P.read_fixture_plan(archive/'index.json', settings['archiveIndexSha256'], manifest, scenes, destination)
    ROUTER.verify_fixtures(newbed, _fixture_keys(newbed), plans)
    live.require_context(context)
    return {'admitted': True}


def _all_empty(runs, name):
    """Every run's detected silhouette and its T1 reading genuinely empty (metadata only)."""
    return all(r['readings']['supports']['full-silhouette']['status'] == 'UNMEASURED_EMPTY_SUPPORT'
               and r['readings']['supports']['full-silhouette']['pixels'] == 0
               and r['readings']['statistics'][name]['status'] == 'UNMEASURED_EMPTY_SUPPORT'
               and r['readings']['statistics'][name]['value'] is None for r in runs)


def _measure_blind(context, run, export_root, index_hash, found, manifest, scenes, declaration_sha256):
    """prepare._measure_blind, reading for reading and field for field, with the DL5m item 4 /
    DL5n stop policy (module docstring): only a REQUIRED statistic stops the read's readiness.

    A REPORTED statistic (aggregate_runs' required False: the DL5a/b/c keys) whose three-run
    reading is incomplete is recorded, never a stop: UNMEASURED_EMPTY_SUPPORT when it is a DL5c
    key and every run's silhouette is genuinely empty (zero_support_witness, as before), else
    UNMEASURED_REPORTED with value and B null and a cause naming the side, the runs that read
    nothing and whether the key was DL5c-eligible. That covers a non-eligible key with an empty
    silhouette and an eligible key empty in only some runs; both were stops (or a raise) in
    prepare. A required statistic that is unmeasurable (UNMEASURED_UNAUTHORISED_POPULATION) or
    whose native spread passes one code (NATIVE_SPREAD_EXCEEDS_ONE_CODE) stops readiness exactly
    as prepare does. Integrity faults (a frame that does not verify, a nonfinite reading, a
    corrupt mask) still raise: they are DL5k stops, not properties of the blind data."""
    P._require_preparation(context, run)
    cells, deps = P.blind_membership(manifest, scenes)
    backgrounds, dependencies = {}, []
    for identity, spec in sorted(deps.items()):
        row = found[(identity, 1)]
        scale = int(re.search(r'-(1|2)x-', spec['profile']).group(1))
        backgrounds[identity] = P.R.read_verified_frame(export_root, row, scenes['canvas'], scale)
        dependencies.append({'id': identity, 'evidence': copy.deepcopy(row)})
    by_scene = {s['id']: s for s in scenes['scenes']}
    reported_keys = set(P.R.reported_reference_keys(manifest, scenes))
    eligible = set(P.empty_support_keys(manifest, scenes))
    output, stops = [], []
    for identity, cell in sorted(cells.items()):
        component = scenes['components'][by_scene[cell['scene']]['component']]
        impulse = scenes['backgrounds'][cell['background']]['kind'] == 'impulse'
        runs = []
        for number in (1, 2, 3):
            row = found[(identity, number)]
            rgb = P.R.read_verified_frame(export_root, row, scenes['canvas'], cell['scale'])
            readings = P.R.S.read_frame(rgb, backgrounds[cell['reference']], component, scenes['canvas'],
                cell['scale'], impulse=impulse, include_structured=cell['family'] != 'uniform')
            runs.append({'run': number, 'evidence': copy.deepcopy(row),
                         'dependency': cell['reference'], 'readings': readings})
        reported = (cell['profile'], 'webgpu', cell['scene'], 'T1-full-silhouette') in reported_keys
        statistics = P.R.aggregate_runs(runs, reported=reported)
        for name, statistic in statistics.items():
            key = (cell['profile'], 'webgpu', cell['scene'], name)
            if statistic['measurementStatus'] != 'MEASURED':
                if statistic['required']:
                    stops.append({'cell': identity, 'statistic': name,
                                  'reason': 'UNMEASURED_UNAUTHORISED_POPULATION', 'repeat': None})
                elif key in eligible and _all_empty(runs, name):
                    P.zero_support_witness(runs)
                    statistic.update(status='UNMEASURED_EMPTY_SUPPORT', value=None, B=None, required=False)
                else:
                    unread = [r['run'] for r in runs if r['readings']['statistics'][name]['status'] != 'MEASURED'
                              or r['readings']['statistics'][name]['value'] is None]
                    statistic.update(status='UNMEASURED_REPORTED', value=None, B=None, required=False,
                                     cause={'kind': 'INCOMPLETE_READING', 'side': 'native', 'unmeasuredRuns': unread,
                                            'eligibleEmptySupport': key in eligible})
            elif statistic['required'] and not statistic['repeat']['passes']:
                stops.append({'cell': identity, 'statistic': name,
                              'reason': 'NATIVE_SPREAD_EXCEEDS_ONE_CODE', 'repeat': statistic['repeat']})
        output.append(dict(copy.deepcopy(cell), runs=runs, statistics=statistics))
    return {'schema': 'w50-native-role-read-1', 'role': 'blind', 'indexSha256': index_hash,
            'declarationSha256': declaration_sha256, 'canvas': copy.deepcopy(scenes['canvas']),
            'supportDefinitions': dict(P.R.S.SUPPORT_DEFINITIONS),
            'repeatRule': copy.deepcopy(manifest['repeatRule']),
            'reportedReferenceKeys': [list(k) for k in sorted(reported_keys)
                                      if any(k[0] == c['profile'] and k[2] == c['scene'] for c in cells.values())],
            'emptySupportKeys': [list(k) for k in sorted(eligible)],
            'dependencies': dependencies, 'cells': output, 'stops': stops, 'ready': not stops}


def public_stops(report):
    """The read's stops as metadata: cell, statistic and reason, never the repeat values."""
    return [{k: stop[k] for k in STOP} for stop in report['stops']]


def _prepare(context, live, run, config_pin, config, manifest, scenes, destination):
    """prepare.prepare_native_exposure after its admission, step for step and byte for byte,
    with this role's _measure_blind. Returns the artifacts and the read's public stops."""
    archive = _fresh_destination(config, destination)
    claim = destination.with_name('native-blind.started.json')
    claim_pin = P.write_once(claim, {'schema': 'w50-native-blind-claim-1',
        'dispatcherContract': P.external_pin(context['contract']),
        'dispatcherClaim': P.external_pin(context['contract']+'.started.json'),
        'batch': P.external_pin(context['batchPath']), 'config': config_pin, 'role': 'blind'})
    destination.mkdir(exist_ok=False)
    if not Path(config['archiveAsset']['path']).is_file() \
            or P.sha(config['archiveAsset']['path']) != config['archiveAsset']['sha256']:
        raise ValueError('Original downloaded archive asset hash mismatch')
    index = P.A.verify_archive(archive, config['archiveIndexSha256'])
    _, _, found = P.selected_rows(index, manifest, scenes, config['partOne']['sha256'])
    export_root = destination/'role-export'
    export_hash = P.A.write_archive(archive, export_root, [copy.deepcopy(r) for r in found.values()])
    export = P.A.verify_archive(export_root, export_hash)
    _, _, exported_rows = P.selected_rows(export, manifest, scenes, config['partOne']['sha256'])
    plans = P.plan_fixture_metadata(index, manifest, scenes, destination)
    fixtures = P._copy_fixtures(context, run, archive, plans)
    report = _measure_blind(context, run, export_root, export_hash, exported_rows, manifest, scenes,
                            config['partOne']['sha256'])
    report['originalArchive'] = {'asset': config['archiveAsset'],
        'indexSha256': config['archiveIndexSha256'], 'pack': config['pack'], 'claim': claim_pin}
    native_pin = P.write_once(destination/'native-read.json', report)
    witnesses = []
    witness_root = destination/'empty-support-witnesses'; witness_root.mkdir()
    eligible = {tuple(k) for k in report['emptySupportKeys']}
    for cell in report['cells']:
        statistic = cell['statistics'].get('T1-full-silhouette', {})
        key = (cell['profile'], 'webgpu', cell['scene'], 'T1-full-silhouette')
        if statistic.get('status') != 'UNMEASURED_EMPTY_SUPPORT' or key not in eligible:
            continue
        P.zero_support_witness(cell['runs'])
        identity = cell['profile']+'/'+cell['scene']
        path = witness_root/(hashlib.sha256(identity.encode()).hexdigest()+'.json')
        witness = P.write_once(path, {'schema': 'w50-empty-native-support-witness-1',
            'profile': cell['profile'], 'scene': cell['scene'], 'role': 'blind', 'nativeRead': native_pin})
        witnesses.append({'profile': cell['profile'], 'scene': cell['scene'], 'pin': witness})
    artifacts = {'schema': 'w50-native-exposure-artifacts-1', 'role': 'blind', 'ready': report['ready'],
        'nativeRead': native_pin, 'claim': claim_pin,
        'export': {'path': str(export_root), 'indexSha256': export_hash},
        'fixtures': fixtures, 'emptySupportWitnesses': witnesses,
        'originalArchive': report['originalArchive']}
    artifacts['artifactManifest'] = P.write_once(destination/'artifacts.json', artifacts)
    _admit_run(context, live, run)
    return artifacts, public_stops(report)


def _pins(artifacts):
    """Every artifact the checkpoint protects, at its RECORDED hash (LIVE rechecks each)."""
    pin = lambda path, digest: {'path': str(Path(path).resolve()), 'sha256': digest}
    pins = [artifacts['artifactManifest'], artifacts['claim'], artifacts['nativeRead'],
            pin(Path(artifacts['export']['path'])/'index.json', artifacts['export']['indexSha256'])]
    for key in sorted(artifacts['fixtures']):
        fixture = artifacts['fixtures'][key]; root = Path(fixture['path'])
        pins.append(pin(root/'manifest.json', fixture['manifestSha256']))
        for name in sorted(fixture['backgrounds']):
            item = fixture['backgrounds'][name]; pins.append(pin(root/item['path'], item['sha256']))
    pins += [w['pin'] for w in artifacts['emptySupportWitnesses']]
    return pins


def _fixture_keys(newbed):
    return ROUTER.fixture_keys(newbed, ROUTER.adapters()['w50'])


def prepare(context, config):
    """One-shot blind preparation; returns {ready, complete, stops, nativeExposure, artifacts}.

    A completed read is checkpointed whether or not it is ready (DL5n): ready is the sealed G0
    readiness, stops its metadata. Anything that stops the preparation itself raises, and LIVE
    keeps that as a DL5k stop that is never replayed."""
    live = CM.dispatcher(context, 'native')
    newbed, settings, manifest, scenes = admission(context, live, config)
    keys = _fixture_keys(newbed)
    destination = Path(context['output'])/'native-blind'
    # router.prepare_exposure's metadata-only plan: the archive index alone, no frame opened,
    # must name exactly the fixtures every immutable run already carries.
    plans = P.read_fixture_plan(Path(settings['archiveRoot'])/'index.json', settings['archiveIndexSha256'],
                                manifest, scenes, destination)
    ROUTER.verify_fixtures(newbed, keys, plans)
    artifacts, stops = _prepare(context, live, newbed[0], config, settings, manifest, scenes, destination)
    ROUTER.verify_fixtures(newbed, keys, artifacts['fixtures'])
    live.require_context(context)
    return {'ready': artifacts['ready'], 'complete': True, 'stops': stops, 'nativeExposure': artifacts,
            'artifacts': _pins(artifacts)}


def _checked_stops(stops, ready, root):
    """Payload stop metadata: exact fields and reasons, no duplicate, ready iff none, and never a
    DL5a/b/c reported key (those are recorded, not stops)."""
    reported = {tuple(k) for k in root['reportedKeys']}
    if not isinstance(stops, list) or type(ready) is not bool or ready != (stops == []):
        raise ValueError('Native checkpoint readiness differs from its stops')
    seen = set()
    for stop in stops:
        if not isinstance(stop, dict) or set(stop) != set(STOP) or stop['reason'] not in REASONS \
                or not isinstance(stop['cell'], str) or stop['cell'].count('/') != 1 \
                or not isinstance(stop['statistic'], str) or (stop['cell'], stop['statistic']) in seen:
            raise ValueError('Native checkpoint stop is not metadata on one required statistic')
        seen.add((stop['cell'], stop['statistic']))
        profile, scene = stop['cell'].split('/')
        if any((profile, renderer, scene, stop['statistic']) in reported for renderer in ('webgpu', 'css')):
            raise ValueError('A reported key is recorded, never a native stop')


def verify(context, payload, config):
    """Recheck the checkpoint's identity, layout and every pin by hash, and its stop metadata
    against the read's own stops; nothing is printed or formatted from the native read."""
    live = CM.dispatcher(context, 'native', 'qualification')
    if context['phase'] != 'exposure': raise ValueError('Native blind preparation is exposure-only')
    root = live.sealed(context['executionRoot'])
    if config not in root['inputs'] or config not in context['inputs']:
        raise ValueError('Blind input config is not pinned by the admitted dispatcher root')
    if not isinstance(payload, dict) or set(payload) != PAYLOAD or payload['complete'] is not True:
        raise ValueError('Native checkpoint is not one complete preparation')
    _checked_stops(payload['stops'], payload['ready'], root)
    artifacts = payload['nativeExposure']
    destination = (Path(context['output'])/'native-blind').resolve()
    if artifacts.get('schema') != 'w50-native-exposure-artifacts-1' or artifacts.get('role') != 'blind' \
            or artifacts.get('ready') is not payload['ready'] \
            or artifacts['artifactManifest']['path'] != str(destination/'artifacts.json') \
            or artifacts['claim']['path'] != str(destination.with_name('native-blind.started.json')) \
            or artifacts['nativeRead']['path'] != str(destination/'native-read.json') \
            or artifacts['export']['path'] != str(destination/'role-export') \
            or any(Path(w['pin']['path']).parent != destination/'empty-support-witnesses'
                   for w in artifacts['emptySupportWitnesses']) \
            or any(Path(f['path']).resolve().parent.parent != destination/'fixtures'
                   for f in artifacts['fixtures'].values()):
        raise ValueError('Native checkpoint names another preparation layout')
    pins = _pins(artifacts)
    if payload['artifacts'] != pins: raise ValueError('Native checkpoint pins differ from its artifacts')
    for item in pins:
        if not Path(item['path']).is_file() or CM.sha(item['path']) != item['sha256']:
            raise ValueError('Native checkpoint artifact changed')
    manifest = CM.read(artifacts['artifactManifest']['path'])
    if manifest != {k: v for k, v in artifacts.items() if k != 'artifactManifest'}:
        raise ValueError('Native artifact manifest differs from its checkpoint')
    report = CM.read(artifacts['nativeRead']['path'])
    if report.get('ready') is not payload['ready'] or public_stops(report) != payload['stops']:
        raise ValueError('Native checkpoint stops differ from its native read')
    claim = CM.read(artifacts['claim']['path'])
    if claim != {'schema': 'w50-native-blind-claim-1', 'dispatcherContract': P.external_pin(context['contract']),
                 'dispatcherClaim': P.external_pin(context['contract']+'.started.json'),
                 'batch': P.external_pin(context['batchPath']), 'config': config, 'role': 'blind'}:
        raise ValueError('Native preparation claim belongs to another exposure')
    newbed = [r for r in context['batch']['runs'] if r.get('sceneSource') == 'w50']
    if not newbed or any(r.get('nativeExposureConfig') != config for r in newbed):
        raise ValueError('W50 exposure requires one shared registered nativeExposureConfig pin')
    ROUTER.verify_fixtures(newbed, _fixture_keys(newbed), artifacts['fixtures'])
    live.require_context(context)


def source_probe():
    """Every module the role executes, on synthetic arrays only: no config, archive or output."""
    P.source_probe()
    ROUTER.adapters()
    return {'status': 'SOURCE_ONLY'}
