"""LIVE native role: the single exposure's one-shot blind native preparation (DL5k).

LIVE writes native.started.json and then calls prepare(context, config) at stage 'native',
once per logical exposure; a started preparation is never replayed, whatever stops it. Later
attempts call verify(context, payload, config) at 'qualification' on the retained checkpoint.

exposure/prepare.py (sealed in the current3 closure) supplies the science unchanged: blind
membership, original-role row selection, the role export, fixture planning/copying and
_measure_blind's per-statistic stop policy. Its entrypoints authenticate through the
whole-batch dispatcher's render admission, which LIVE issues only to a remaining capture
member, and its admission binds the LOGICAL claim's pid/lease, which only the first attempt's
process holds. So this role owns the admission (LIVE's require_native_preparation, this
attempt's claim held by this process, and every policy check of prepare.admission unchanged),
replaces only prepare's private `_require_preparation` hook in its own sourced instance with
the native-stage equivalent, and orchestrates prepare_native_exposure's steps in the same
order, writing byte-identical artifacts in the same layout. current3 repeat/sources.blind_cell
and current2 native_evidence._blind_authority read exactly that layout at analysis.

The payload carries metadata and content pins only; neither prepare nor verify prints, and
verify hashes files without reading a native value.
"""
import copy
import hashlib
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
SCHEMA = 'w50-native-exposure-inputs-1'


def _source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


CM = _source(HERE/'common.py', 'w50_live_native_common')
P = _source(FIT/'exposure/prepare.py', 'w50_live_native_prepare')
ROUTER = _source(FIT/'live/router.py', 'w50_live_native_router')


def _admit_run(context, live, run):
    """Render admission's checks in their native-stage form: this exposure's own capability,
    a logical new-bed candidate run, its numerical admission and its admitted endpoints."""
    live.require_native_preparation(context)
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


def admission(context, live, config_pin):
    """prepare.admission's policy, bound to LIVE's native capability and this attempt's claim.

    The root's bootstrap identity is LIVE's own process admission (dispatch._prepare), so it is
    not repeated against a module path here. The logical claim keeps its phase/contract/batch/
    output binding; its pid/lease belong to the first attempt, so the process/lease binding is
    this attempt's claim (common.execution_claim)."""
    live.require_native_preparation(context)
    CM.execution_claim(context, live)
    if context['phase'] != 'exposure': raise ValueError('Native blind preparation is exposure-only')
    repo = Path(context['repo'])
    root = live.sealed(context['executionRoot'])
    if config_pin not in root['inputs'] or config_pin not in context['inputs']:
        raise ValueError('Blind input config is not pinned by the admitted dispatcher root')
    newbed = [r for r in context['batch']['runs'] if r.get('sceneSource') == 'w50']
    if not newbed or any(r.get('nativeExposureConfig') != config_pin for r in newbed):
        raise ValueError('W50 exposure requires one shared registered nativeExposureConfig pin')
    for run in newbed: _admit_run(context, live, run)
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


def _prepare(context, live, run, config_pin, config, manifest, scenes, destination):
    """prepare.prepare_native_exposure after its admission, step for step and byte for byte."""
    archive = Path(config['archiveRoot']).resolve()
    if destination.exists() or destination.is_symlink() \
            or destination.resolve().is_relative_to(archive) or archive.is_relative_to(destination.resolve()):
        raise ValueError('Native exposure destination exists or overlaps its original archive')
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
    report = P._measure_blind(context, run, export_root, export_hash, exported_rows, manifest, scenes,
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
    return artifacts


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
    """One-shot blind preparation; returns {ready, nativeExposure, artifacts}."""
    live = CM.dispatcher(context, 'native')
    newbed, settings, manifest, scenes = admission(context, live, config)
    keys = _fixture_keys(newbed)
    destination = Path(context['output'])/'native-blind'
    # router.prepare_exposure's metadata-only plan: the archive index alone, no frame opened,
    # must name exactly the fixtures every immutable run already carries.
    plans = P.read_fixture_plan(Path(settings['archiveRoot'])/'index.json', settings['archiveIndexSha256'],
                                manifest, scenes, destination)
    ROUTER.verify_fixtures(newbed, keys, plans)
    artifacts = _prepare(context, live, newbed[0], config, settings, manifest, scenes, destination)
    ROUTER.verify_fixtures(newbed, keys, artifacts['fixtures'])
    live.require_context(context)
    return {'ready': artifacts['ready'], 'nativeExposure': artifacts, 'artifacts': _pins(artifacts)}


def verify(context, payload, config):
    """Recheck the checkpoint's identity, layout and every pin by hash; no native value is read."""
    live = CM.dispatcher(context, 'native', 'qualification')
    if context['phase'] != 'exposure': raise ValueError('Native blind preparation is exposure-only')
    root = live.sealed(context['executionRoot'])
    if config not in root['inputs'] or config not in context['inputs']:
        raise ValueError('Blind input config is not pinned by the admitted dispatcher root')
    if not isinstance(payload, dict) or set(payload) != {'ready', 'nativeExposure', 'artifacts'} \
            or payload['ready'] is not True:
        raise ValueError('Native checkpoint is not one complete ready preparation')
    artifacts = payload['nativeExposure']
    destination = (Path(context['output'])/'native-blind').resolve()
    if artifacts.get('schema') != 'w50-native-exposure-artifacts-1' or artifacts.get('role') != 'blind' \
            or artifacts.get('ready') is not True \
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
