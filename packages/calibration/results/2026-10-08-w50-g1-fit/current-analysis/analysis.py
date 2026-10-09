"""Completed-current evidence on original native masks; never candidate or pre-fit PASS.

The outer stdlib bootstrap binds every source/config byte before importing this module.
No live dispatcher context or invented admission is constructed. Original G0 rows remain
verbatim under originalReference; measured values are additive evidence, not replacements.
"""
import copy
import gzip
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REPO = HERE.parents[4]
KEY = ('profile', 'renderer', 'scene', 'statistic')


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


B = source(HERE/'run.py', 'w50_completed_bootstrap_helpers')
M = source(FIT/'measurement/capture.py', 'w50_completed_pure_measurement')
C = source(FIT/'canonical/adapter.py', 'w50_completed_original_canonical')
E = source(HERE/'native_evidence.py', 'w50_completed_native_provenance')


class _CompletedRepeat:
    """Internal evidence bound only after the completed root/result chain was authenticated."""
    def __init__(self, member, *, legacy=False, pair=None):
        self.member = copy.deepcopy({k: member[k] for k in ('run', 'receipt', 'output')})
        self.legacy, self.pair = legacy, pair


def bind_completed_repeat(root, root_pin, member, original_rows, *, dispatcher=None, result=None):
    """Bind one row AFTER current_evidence_inputs, without creating a live capability.

    completed() supplies its already checked dispatcher/result once per batch. The standalone
    test path rechecks the exact pinned result/claim/contract link. The shared repeat helper
    owns pair/statistic semantics; this consumer subsequently validates BOTH raw pages with
    the original pure source validators before any analytical pixel reading.
    """
    authenticated = result is not None
    if not authenticated:
        root_path = B.checked(REPO, root_pin)
        if B.load(root_path) != root:
            raise ValueError('Repeat registration differs from the authenticated current root')
    if dispatcher is None:
        dispatcher = source(B.checked(REPO, root['bootstrap']), 'w50_archived_repeat_dispatch')
    path = (lambda item: REPO/item['path']) if authenticated else (lambda item: B.checked(REPO, item))
    contract_path = path(member['contract'])
    batch_path = path(member['batch'])
    claim_path = path(member['claim'])
    if claim_path != Path(str(contract_path)+'.started.json'):
        raise ValueError('Archived repeat claim differs from its registered contract')
    result_path = path(member['result'])
    if result_path != Path(str(contract_path)+'.result.json'):
        raise ValueError('Archived repeat result differs from its registered contract')
    if result is None:
        result = dispatcher.result_for(contract_path)
    if result.get('contractSha256') != member['contract']['sha256'] or \
            result.get('claimSha256') != member['claim']['sha256'] or \
            result.get('report', {}).get('status') != 'CAPTURED':
        raise ValueError('Archived repeat result/claim chain is not completed capture evidence')
    receipt = member['receipt']
    matches = [r for r in result['captures']['captures'] if all(r.get(k) == receipt.get(k) for k in KEY[:3])]
    if matches != [receipt]:
        raise ValueError('Archived repeat row differs from its exact completed result member')
    if receipt.get('origin', {}).get('kind') == 'retained-attempt2':
        if not authenticated:
            dispatcher.verify_recovery_records({'batchPath': str(batch_path)}, result['captures'], doc=root)
        member['_repeat'] = _CompletedRepeat(member, legacy=True)
        return
    required_pins = [receipt.get('repeatPair'), receipt.get('repeatAdmission')]
    if any(pin not in result.get('repeatReceipt', []) for pin in required_pins):
        raise ValueError('Archived repeat proof/pair is absent from the registered result inventory')
    rows = [r for r in original_rows if all(r[k] == receipt[k] for k in KEY[:3])]
    binding = dict(executionRootSha256=root_pin['sha256'], contractSha256=member['contract']['sha256'],
        batchSha256=member['batch']['sha256'], config=root['repeatAdmission']['config'], declaredRows=rows)
    if member['run']['sceneSource'] == 'canonical':
        scenes = C.read(C.SCENES)
        scene = next(s for s in scenes['scenes'] if s['id'] == receipt['scene'])
        binding['canonicalBackgroundKind'] = scenes['backgrounds'][scene['background']]['kind']
    pair = M.repeat_helper(root, REPO).verify_archived_pair(binding, member['run'], receipt, member['output'])
    member['_repeat'] = _CompletedRepeat(member, pair=pair)


def bound_repeat(member):
    bound = member.get('_repeat')
    if bound is not None:
        if not isinstance(bound, _CompletedRepeat) or bound.member != {
                k: member[k] for k in ('run', 'receipt', 'output')}:
            raise ValueError('Completed repeat member changed after source admission')
        return bound
    if any(k in member['receipt'] for k in ('repeatPair', 'repeatAdmission', 'origin')):
        raise ValueError('Repeat/origin evidence lacks the authenticated completed result chain')
    return None


def completed_repeat(member, metadata):
    bound = bound_repeat(member)
    if bound is not None:
        if bound.legacy and (metadata.get('deterministic') is not True or \
                type(metadata.get('repeatNoise')) not in (int, float) or metadata['repeatNoise'] != 0):
            raise ValueError('Retained original lost its true/zero equality attestation')
        return bound
    if metadata.get('deterministic') is not True or type(metadata.get('repeatNoise')) not in (int, float) \
            or metadata['repeatNoise'] != 0:
        raise ValueError('Non-identical current capture lacks an admitted archived repeat proof')
    return None


def completed(config, root_path):
    """Verify BOTH full chains and exact original gate0 endpoints before analytical reads."""
    root = B.load(root_path)
    dispatcher = source(B.checked(REPO, root['bootstrap']), 'w50_completed_dispatch')
    current = config['current']
    chain = dispatcher.current_evidence_inputs(REPO, root_path.parent,
                                               current['instrument'], current['results'])
    root = dispatcher.root_doc(root_path)
    part = dispatcher.load(dispatcher.checked(REPO, root['partTwo']))
    original_pins = {p['path']: p for p in part['sources']}
    candidates = {}
    for candidate_pin in root['baselineDocuments']:
        position = dispatcher.admission_module(root).endpoints(root, candidate_pin, current=True)
        path = B.checked(REPO, candidate_pin); document = B.load(path)
        endpoints, pair = {}, {}
        for slot, item in document['endpoints'].items():
            pose, scheme = slot.split('.')
            suffix = '-receded' if pose == 'receded' else ''
            original_path = FIT.parents[1]/'profiles'/f'apple-macos-27.0-1x-{scheme}-standard-glass{position}{suffix}.json'
            original_pin = original_pins[str(original_path.relative_to(REPO))]
            original = B.load(B.checked(REPO, original_pin))
            endpoint_path = B.ordinary(path.parent/item['path'])
            if not endpoint_path.is_relative_to(REPO): raise ValueError('Endpoint escaped repository')
            actual_pin = {'path': str(endpoint_path.relative_to(REPO)), 'sha256': item['sha256']}
            actual = B.load(B.checked(REPO, actual_pin))
            if {k:v for k,v in actual.items() if k != 'profileKey'} != \
                    {k:v for k,v in original.items() if k != 'profileKey'}:
                raise ValueError('Gate0 endpoint changed original document bytes beyond its namespace')
            endpoints[slot] = dict(actual, source=original_pin, candidateEndpoint=actual_pin)
            if scheme == 'dark': pair[slot] = original_pin['sha256']
        candidates[candidate_pin['sha256']] = dict(document=candidate_pin, endpoints=endpoints,
                                                   originalDocumentPair=pair, position=position)
    members = []
    repeat_rows = dispatcher.load(dispatcher.checked(REPO, root['references']))['cells'] \
        if root.get('repeatAdmission') else None
    root_pin = B.pin(REPO, root_path)
    for batch_pin, result_pin in zip(root['currentBatches'], current['results'], strict=True):
        batch = B.load(B.checked(REPO, batch_pin))
        result_path = B.checked(REPO, result_pin)
        result = dispatcher.sealed(result_path)
        contract_path = result_path.with_name(result_path.name.removesuffix('.result.json'))
        claim = B.load(Path(str(contract_path)+'.started.json'))
        if repeat_rows is not None:
            dispatcher.verify_recovery_records({'batchPath': str(REPO/batch_pin['path'])},
                                               result['captures'], doc=root)
        for receipt in result['captures']['captures']:
            runs = [run for run in batch['runs'] if all(run[k] == receipt[k]
                for k in ('profile', 'renderer', 'candidate')) and receipt['scene'] in run['scenes']]
            if len(runs) != 1 or receipt['lane'] != 'current':
                raise ValueError('Completed capture has no exact original current run')
            run = runs[0]
            if receipt.get('sceneSource') != run['sceneSource']:
                raise ValueError('Completed receipt changed scene source')
            member = dict(run=run, receipt=receipt, output=claim['output'], result=result_pin,
                contract=B.pin(REPO, contract_path), claim=B.pin(REPO, Path(str(contract_path)+'.started.json')),
                batch=batch_pin)
            if repeat_rows is not None:
                bind_completed_repeat(root, root_pin, member, repeat_rows, dispatcher=dispatcher, result=result)
            members.append(member)
    triples = [tuple(m['receipt'][k] for k in KEY[:3]) for m in members]
    if len(triples) != len(set(triples)):
        raise ValueError('Duplicate completed-current member across result chains')
    return dict(root=root, chain=chain, candidates=candidates, members=members)


def measure_pixels(web, background, native_cell, component, canvas, *, impulse, renderer):
    """Pure remeasurement with native no-glass support and native three-run aggregation."""
    native = M.R.aggregate_runs(native_cell['runs'], reported=any(
        not s['required'] for s in native_cell['statistics'].values()))
    if native != native_cell['statistics']:
        raise ValueError('Original native aggregation differs from its run statistics')
    if web.shape != background.shape or web.shape != (canvas['height']*native_cell['scale'],
                                                       canvas['width']*native_cell['scale'], 3):
        raise ValueError('Current/native no-glass dimensions differ from original canvas')
    masks = M.R.S.analytical_masks(component, canvas, native_cell['scale'], web.shape[:2],
                                  background=background, impulse=impulse)
    if native_cell['family'] == 'uniform': del masks['deep8_far24']
    return M.evaluate_native_supports(web, native_cell, masks, renderer=renderer)


def project_rows(original_rows, measured, provenance):
    triple = tuple(measured[k] for k in KEY[:3])
    rows = [r for r in original_rows if tuple(r[k] for k in KEY[:3]) == triple]
    if len(rows) != len(measured['statistics']) or {r['statistic'] for r in rows} != set(measured['statistics']) \
            or any(r['role'] != measured['role'] for r in rows):
        raise ValueError('Measurement must cover the exact original statistic/role population')
    output = []
    for row in rows:
        output.append(dict(**{k: row[k] for k in KEY}, role=row['role'],
            evidenceKind='completed-current-gate0', originalReference=copy.deepcopy(row),
            currentDocumentPair=copy.deepcopy(row['currentDocumentPair']),
            currentGeneration=row['currentGeneration'], measurement=copy.deepcopy(measured['statistics'][row['statistic']]),
            provenance=copy.deepcopy(provenance)))
    return output


def project_native_rows(original_rows, measured, provenance, native_cell):
    """Keep DL5g's content-pinnable native envelope beside, never inside, original G0 rows."""
    rows = project_rows(original_rows, measured, provenance)
    for row in rows:
        row['nativeEvidenceEnvelope'] = E.envelope(row['originalReference'], native_cell, provenance)
    return rows


def argument_population(records, required):
    ids = [r['id'] for r in records]
    if len(ids) != len(set(ids)) or set(ids) != set(required):
        raise ValueError('Arguments must equal every exact original required_argument ID once')
    for record in records:
        if any(record[k] != required[record['id']][k] for k in KEY[:3]):
            raise ValueError('Measured argument changed original cell identity')
        M.N.validate_tone_values(record)
    return sorted(copy.deepcopy(records), key=lambda r: r['id'])


def native_contract(repo, config):
    """Verify the immutable native bootstrap chain with its own synthetic-only referee."""
    root_path = B.checked(repo, config['instrument']); B.sidecar(root_path)
    root = B.load(root_path)
    contract_path = B.checked(repo, config['contract']); B.sidecar(contract_path)
    contract = B.load(contract_path)
    batch_path = B.checked(repo, config['batch'])
    if root.get('schema') != 'w50-native-instrument-root-1' or root['batch'] != config['batch'] \
            or root['contract'] != config['contract'] or contract['batch'] != config['batch'] \
            or B.checked(repo, root['contractSidecar']) != Path(str(contract_path)+'.sha256'):
        raise ValueError('Original native prospective contract chain differs')
    for path, digest in root['sources'].items(): B.checked(repo, {'path': path, 'sha256': digest})
    entry = root_path.parent/'run.py'
    if contract.get('renderer') != str(entry.relative_to(repo)) or \
            contract.get('probe') != str((root_path.parent/'probe.py').relative_to(repo)):
        raise ValueError('Original native contract entrypoint changed')
    if root['sources'].get(str(entry.relative_to(repo))) != B.sha(entry):
        raise ValueError('Native run source is outside its prospective closure')
    native = source(entry, 'w50_completed_original_native_contract')
    batch, guards = native.read_batch(batch_path)
    expected = dict(contract['closure']['sources']); expected.update(guards)
    if root['sources'] != expected or root['inputs'] != batch['inputs']:
        raise ValueError('Original native source closure/input mapping differs')
    referee = source(native.G0/'audit/next_wave.py', 'w50_completed_native_referee')
    _, registered, renderer = referee.verify(contract_path, repo, batch_path)
    if registered != batch_path or renderer != entry:
        raise ValueError('Original native referee selected another batch/entrypoint')
    return batch


def native_roles(config, native_batch, scenes):
    """Open only the two externally pinned exposed shards after completed chain validation."""
    manifest = B.load(B.checked(REPO, native_batch['inputs']['manifest']))
    result = {}
    for export in native_batch['exports']:
        role = export['role']
        if role not in ('calibration', 'validation'): raise ValueError('Blind role is closed')
        report_pin = config['native']['reports'][role]
        report = M._json(gzip.decompress(B.checked(REPO, report_pin).read_bytes()))
        if report.get('schema') != 'w50-native-role-read-1' or report.get('role') != role \
                or report.get('indexSha256') != export['indexSha256'] \
                or report.get('declarationSha256') != native_batch['inputs']['declaration']['sha256'] \
                or report.get('canvas') != scenes['canvas'] or report.get('ready') is not True \
                or report.get('stops') != [] or report.get('supportDefinitions') != M.R.S.SUPPORT_DEFINITIONS \
                or report.get('repeatRule') != manifest['repeatRule']:
            raise ValueError('Native role report differs from original exposed read contract')
        verified = M.R.verify_role_export(export['root'], export['indexSha256'], role, manifest, scenes,
            expected_declaration_sha256=report['declarationSha256'])
        cells = M.R.unique(report['cells'], 'id', 'native role cell')
        deps = M.R.unique(report['dependencies'], 'id', 'native role dependency')
        if set(cells) != set(verified['cells']) or set(deps) != set(verified['dependencies']):
            raise ValueError('Native report omitted/added original role cells or dependencies')
        for identity, cell in cells.items():
            expected = verified['cells'][identity]
            if any(cell.get(k) != v for k, v in expected.items() if k != 'runs') \
                    or [r['run'] for r in cell['runs']] != expected['runs']:
                raise ValueError('Native report cell identity differs from the original role export')
            for run in cell['runs']:
                if run['evidence'] != verified['rows'][(identity, run['run'])] \
                        or run['dependency'] != cell['reference']:
                    raise ValueError('Native report run/dependency provenance differs')
        for identity, dep in deps.items():
            if dep['evidence'] != verified['rows'][(identity, 1)]:
                raise ValueError('Original no-glass dependency differs from role-pinned index')
        result[role] = dict(report=report, cells=cells, deps=deps, export=export, reportPin=report_pin)
    return result


def canonical_argument(page, run, plan, spec, abscissa):
    """Read canonical solve lanes without asserting native border-box geometry equivalence.

    The declared source path retains CSS's historical content box, including its border.
    Preserve the measured bounds as provenance; only NEWBED's original validator asserts
    the native box. Independent encoded/linear/RGB lanes remain independent here too.
    """
    groups, surfaces = page['groups'], page['surfaces']
    if len(groups) != 1 or len(surfaces) != 1 or spec['component']['kind'] not in ('capsule', 'rrect'):
        raise ValueError('Canonical required argument needs one declared surface/group')
    group, surface = groups[0], surfaces[0]; state = group['state']
    bounds = surface.get('bounds') or {}
    if set(bounds) != {'x','y','width','height'} or any(
            type(v) not in (int,float) or not M.np.isfinite(v) for v in bounds.values()) \
            or bounds['width'] <= 0 or bounds['height'] <= 0:
        raise ValueError('Missing/invalid actual canonical surface bounds')
    shape = spec['component']; declared_span = min(shape['size'])
    # The solve rides the measured host span, not the declared content-box span.
    # Canonical source-mode CSS includes its border; GPU and silhouette boxes do not.
    span = min(bounds['width'], bounds['height'])
    family = 'capsule' if shape['kind'] == 'capsule' else 'fixed-rounded-rect'
    radius = declared_span/2 if shape['kind'] == 'capsule' else shape['radius']
    pixels = [plan['canvas']['width']*plan['dpr'], plan['canvas']['height']*plan['dpr']]
    background = page.get('background') or {}
    if page.get('requestedBackdropLevel') is not None or page.get('requestedBackdropMode') != 'texture' \
            or group.get('configuredSource') != 'texture' \
            or state.get('samplingBackend') != ('gpu-texture' if run['renderer']=='webgpu' else 'css-backdrop') \
            or background.get('id') != spec['background'] \
            or [background.get('naturalWidth'),background.get('naturalHeight')] != pixels:
        raise ValueError('Canonical argument has wrong backdrop source, raster or hint')
    if surface.get('family') != family or surface.get('radius') != radius:
        raise ValueError('Wrong declared canonical shape family/radius')
    if abscissa == 'source':
        reading = group.get('backdropTone')
        if not reading or not M.A.unit(reading.get('level')):
            raise ValueError('UNMEASURED: missing canonical source solve argument')
        e, y, rgb = M.A.encode(reading['level']), reading.get('linearLuminance'), reading.get('rgb')
        provenance = dict(copy.deepcopy(reading), kind='source',
            operation='srgb_encode(recorded decoded encoded-mean level)')
    elif abscissa == 'silhouette':
        readings = state.get('backdropToneAbscissae', [])
        if len(readings) != 1 or readings[0].get('surfaceId') != surface['nodeId']:
            raise ValueError('UNMEASURED: missing canonical surface solve argument')
        reading = readings[0]
        if reading.get('kind') != 'silhouette' or not reading.get('sampleCount',0) > 0:
            raise ValueError('UNMEASURED: empty or hinted canonical reduction')
        e, y, rgb = reading.get('encodedLuminance'), reading.get('linearLuminance'), reading.get('color')
        provenance = copy.deepcopy(reading)
    else: raise ValueError('Unregistered canonical abscissa mode')
    # scene.ts registers every canonical host as regular, even a scene named clear20.
    # Its report exposes no variant lane, so use that source contract, never the scene name.
    provenance.update(surface=copy.deepcopy(surface), groupId=group['id'],
        configuredSource=group['configuredSource'], samplingBackend=state['samplingBackend'],
        background=copy.deepcopy(background), declaredSpan=declared_span, actualSolveSpan=span,
        variant='regular', variantSource='packages/calibration/web/scene.ts registerHost source contract')
    record = dict(id=f'{run["profile"]}|{run["renderer"]}|{spec["scene"]}',
        profile=run['profile'], renderer=run['renderer'], scene=spec['scene'], variant='regular',
        pose=spec['pose'], position=plan['position'], dpr=plan['dpr'], span=span, role=spec['role'],
        candidateSha256=run['candidate']['sha256'], encodedLuminance=e, linearLuminance=y, rgb=rgb,
        provenance=provenance)
    M.N.validate_tone_values(record)
    return record


def canonical_inputs(member, candidate, *, argument_required):
    """Verify the original canonical receipt/report and all transport pins, with no live wrapper."""
    receipt, run = member['receipt'], member['run']
    repeat = bound_repeat(member)
    if repeat is not None and repeat.legacy:
        raise ValueError('The retained501 declaration carries no canonical legacy draw')
    plan = C.scene_plan(run, 'current')
    if plan['scheme'] != 'dark' or plan['a11y'] != 'standard' or candidate['position'] != plan['position'] \
            or candidate['document'] != run['candidate']:
        raise ValueError('Canonical capture differs from original dark gate0 candidate selection')
    scene = next(s for s in plan['scenes'] if s['id'] == receipt['scene'])
    pose = 'receded' if scene['state']=='inactive' else 'active'
    spec = dict(scene=scene['id'], pose=pose, role=scene['fixtureSet'], background=scene['background'],
                component=copy.deepcopy(plan['components'][scene['component']]))
    endpoint = candidate['endpoints'][pose+'.dark']; original = endpoint['source']
    stated = receipt.get('endpoint') or {}
    if any(stated.get(k) != endpoint[k] for k in ('profileKey','resolvedMaterialSha256','patch')) \
            or stated.get('path') != str(REPO/endpoint['candidateEndpoint']['path']) \
            or stated.get('sha256') != endpoint['candidateEndpoint']['sha256'] \
            or stated.get('currentSource') != dict(path=str(REPO/original['path']),sha256=original['sha256']) \
            or any(candidate['originalDocumentPair'].get(slot) != candidate['endpoints'][slot]['source']['sha256']
                   for slot in ('active.dark','receded.dark')):
        raise ValueError('Canonical receipt endpoint/original document pair differs')
    folder = Path(run['captureRoot'])/run['profile']/scene['id']; artifacts = receipt['artifacts']; blobs = {}
    def read_artifact(item):
        B.ordinary(Path(item['path']))
        return M._pin_bytes(item, Path(member['output']), external=True)
    for name, filename in (('png',f'{scene["id"]}__{run["renderer"]}.png'),
                           ('report',f'report__{run["renderer"]}.json'),('cell',f'cell__{run["renderer"]}.json')):
        if artifacts[name]['path'] != str(folder/filename):
            raise ValueError('Canonical artifact path differs from original fixed run')
        blobs[name] = read_artifact(artifacts[name])
    for collection in ('files','transport'):
        pins = artifacts.get(collection, []); paths = [p['path'] for p in pins]
        if not pins or len(paths) != len(set(paths)):
            raise ValueError('Missing/duplicate canonical artifact transport pins')
        if collection == 'files':
            required = [artifacts[n] for n in blobs]
            if repeat is not None:
                required += [receipt['repeatPair']]
                required += [repeat.pair['proof']['pair'][side][kind]
                             for side in ('first','second') for kind in ('image','report')]
            if any(Path(p).parent != folder for p in paths) or any(item not in pins for item in required):
                raise ValueError('Canonical file inventory differs from capture folder or retained pair')
        else:
            expected = {str(Path(run['captureRoot'])/name) for name in (
                f'census-{scene["id"]}.json',f'request-{scene["id"]}.json',f'exit-{scene["id"]}.json',
                f'compare-{scene["id"]}.log','request.json','native-request.json',f'native-admission-{scene["id"]}.json')}
            if repeat is not None:
                expected |= {str(Path(run['captureRoot'])/name) for name in (
                    f'capture-{scene["id"]}.log', f'fresh-{scene["id"]}.json')}
            if set(paths) != expected: raise ValueError('Canonical transport paths differ from fixed run')
        for item in pins: read_artifact(item)
    matrix_pin = receipt['matrix']
    if matrix_pin['path'] != run['matrixPath']: raise ValueError('Canonical matrix path differs')
    matrix = M._json(read_artifact(matrix_pin))
    rows = C.validate_matrix(matrix, run, REPO/run['candidate']['path'])
    row = next(r for r in rows if r['key']['sceneId']==scene['id'])
    metadata = M._json(blobs['cell'])
    if row != receipt['row'] or metadata != row['key']['web'] or metadata.get('renderer') != run['renderer'] \
            or metadata.get('colorSpace') != 'srgb':
        raise ValueError('Canonical row/cell transport metadata differs')
    repeat = completed_repeat(member, metadata)
    pixels = tuple(plan['canvas'][k]*plan['dpr'] for k in ('width','height'))
    raw = blobs['png']
    if len(raw) < 24 or raw[:8] != b'\x89PNG\r\n\x1a\n' \
            or tuple(int.from_bytes(raw[i:i+4],'big') for i in (16,20)) != pixels:
        raise ValueError('Canonical PNG dimensions differ from original raster')
    envelope = M._json(blobs['report'])
    C.validate_report(envelope, run, plan, scene, endpoint)
    if repeat is not None:
        if envelope != repeat.pair['envelope']:
            raise ValueError('Canonical first envelope differs from its archived repeat reading')
        for page in repeat.pair['pages']:
            C.validate_report({**envelope, 'page': page}, run, plan, scene, endpoint)
    scenes_path = B.ordinary(C.SCENES)
    plan.update(source='canonical', scenesPath=str(scenes_path), scenesSha256=B.sha(scenes_path))
    provenance = dict(capture=copy.deepcopy(artifacts['png']),report=copy.deepcopy(artifacts['report']),
        cell=copy.deepcopy(artifacts['cell']),artifacts=copy.deepcopy(artifacts),matrix=copy.deepcopy(matrix_pin),
        originalRow=copy.deepcopy(row),candidateDocument=copy.deepcopy(run['candidate']),
        originalDocumentPair=copy.deepcopy(candidate['originalDocumentPair']),result=member['result'],
        contract=member['contract'],claim=member['claim'],sceneSource='canonical',scenesSha256=plan['scenesSha256'],
        endpoint={k:copy.deepcopy(v) for k,v in endpoint.items() if k != 'patch'},
        reportedSurfaces=copy.deepcopy(envelope['page']['surfaces']),evidenceKind='completed-current-gate0',baseline=True,
        geometryDomain='canonical-reported-bounds-not-native-mask-equivalence')
    if repeat is not None:
        provenance.update(repeatAdmission=copy.deepcopy(receipt['repeatAdmission']),
                          repeatPair=copy.deepcopy(receipt['repeatPair']), reading='first')
    arguments = []
    if argument_required:
        resolved = {**candidate['endpoints']['active.dark']['patch'], **endpoint['patch']}
        abscissa = resolved.get('backdropToneAbscissa','source')
        abscissa = 'silhouette' if isinstance(abscissa,dict) else abscissa
        if repeat is not None:
            for page in repeat.pair['pages']: canonical_argument(page,run,plan,spec,abscissa)
        argument = canonical_argument(envelope['page'],run,plan,spec,abscissa)
        argument['provenance'].update(copy.deepcopy(provenance)); arguments.append(argument)
    return plan, spec, raw, arguments, provenance


def capture_inputs(member, candidate, *, argument_required=True):
    receipt, run = member['receipt'], member['run']
    if any(receipt.get(k) != run[k] for k in ('profile','renderer','candidate','sceneSource')) \
            or receipt.get('lane') != 'current' or receipt.get('scene') not in run['scenes']:
        raise ValueError('Completed receipt differs from exact original current run')
    if run['sceneSource'] == 'canonical':
        return canonical_inputs(member,candidate,argument_required=argument_required)
    if run['sceneSource'] != 'w50' or not argument_required:
        raise ValueError('NEWBED requires its original numerical argument')
    plan = M.A.scene_plan(run, 'current')
    spec = next(s for s in plan['scenes'] if s['scene'] == receipt['scene'])
    if receipt.get('canvas') != plan['canvas'] or receipt.get('dpr') != plan['dpr']:
        raise ValueError('Completed capture canvas/scale differs from original run')
    repeat = bound_repeat(member)
    folder = Path(run['captureRoot'])/receipt['scene']
    if repeat is not None and repeat.legacy:
        folder = Path(member['output'])/'retained-attempt2'/receipt['profile']/receipt['scene']/receipt['renderer']
    artifacts = receipt['artifacts']; blobs = {}
    for name, filename in (('png', f'{receipt["scene"]}__{receipt["renderer"]}.png'),
                           ('report', f'report__{receipt["renderer"]}.json'),
                           ('cell', f'cell__{receipt["renderer"]}.json')):
        expected = folder/filename
        if artifacts[name]['path'] != str(expected):
            raise ValueError('Completed artifact path differs from the original fixed run')
        B.ordinary(expected)
        blobs[name] = M._pin_bytes(artifacts[name], Path(member['output']), external=True)
    metadata = M._json(blobs['cell'])
    if metadata.get('renderer') != run['renderer'] or metadata.get('colorSpace') != 'srgb' \
            or f'declarationSha256={run["candidate"]["sha256"][:12]}' not in metadata.get('capturePath', ''):
        raise ValueError('Completed current cell metadata lacks original candidate/tier identity')
    repeat = completed_repeat(member, metadata)
    endpoint = candidate['endpoints'][spec['pose']+'.dark']
    resolved = {**candidate['endpoints']['active.dark']['patch'], **endpoint['patch']}
    abscissa = resolved.get('backdropToneAbscissa', 'source')
    abscissa = 'silhouette' if isinstance(abscissa, dict) else abscissa
    envelope = M._json(blobs['report'])
    arguments = M.A.validate_report(envelope, run, endpoint, abscissa=abscissa, phase='current')
    if repeat is not None and not repeat.legacy:
        if envelope != repeat.pair['envelope']:
            raise ValueError('Completed first envelope differs from its archived repeat reading')
        for page in repeat.pair['pages']:
            readings = M.A.validate_report({**envelope, 'page': page}, run, endpoint,
                                          abscissa=abscissa, phase='current')
            for argument in readings: M.N.validate_tone_values(argument)
    provenance = dict(capture=copy.deepcopy(artifacts['png']), report=copy.deepcopy(artifacts['report']),
        cell=copy.deepcopy(artifacts['cell']), candidateDocument=copy.deepcopy(run['candidate']),
        originalDocumentPair=copy.deepcopy(candidate['originalDocumentPair']),
        result=member['result'], contract=member['contract'], claim=member['claim'],
        sceneSource=run['sceneSource'], scenesSha256=plan['scenesSha256'],
        endpoint={k:copy.deepcopy(v) for k,v in endpoint.items() if k != 'patch'},
        evidenceKind='completed-current-gate0', baseline=True)
    if repeat is not None:
        provenance.update(repeatAdmission=copy.deepcopy(receipt['repeatAdmission']), reading='first')
        if repeat.legacy: provenance['origin'] = copy.deepcopy(receipt['origin'])
        else: provenance['repeatPair'] = copy.deepcopy(receipt['repeatPair'])
    for argument in arguments:
        M.N.validate_tone_values(argument)
        argument['provenance'].update(copy.deepcopy(provenance))
    return plan, spec, blobs['png'], arguments, provenance


def current_routes(members, rows, required):
    """Partition original IDs before numerical reads; the twelve T1 gaps are artifact-only."""
    def identity(row): return '|'.join(row[k] for k in KEY[:3])
    newbed = {identity(m['receipt']) for m in members if m['run']['sceneSource']=='w50'}
    canonical = {identity(m['receipt']) for m in members if m['run']['sceneSource']=='canonical'}
    if len(newbed) != 672 or len(canonical) != 127 or len(members) != 799 or len(required) != 787 \
            or not newbed <= set(required) or not set(required)-newbed <= canonical \
            or len(canonical & set(required)) != 115:
        raise ValueError('Completed evidence differs from exact 672/115/12 original argument routes')
    missing = {}
    for row in rows:
        key = identity(row)
        if key not in required and row['statistic'] in ('T1-full-silhouette','T1-low') \
                and row['role']=='gate' and (row.get('currentEvidence') is None or row.get('currentMetadata') is None):
            missing.setdefault(key, []).append(copy.deepcopy(row))
    if len(missing) != 12 or canonical-set(required) != set(missing):
        raise ValueError('Canonical extras differ from exact original missing T1 references')
    routes = {key:dict(requiredArgument=True,originalReferences=[]) for key in required}
    routes.update({key:dict(requiredArgument=False,originalReferences=refs) for key,refs in missing.items()})
    return routes


def read_completed(config, root_path):
    admitted = completed(config, root_path)
    native_batch = native_contract(REPO, config['native'])
    inventory = B.load(B.checked(REPO, config['originals']['references']))
    scenes = B.load(B.checked(REPO, config['originals']['scenes']))
    rows = inventory['cells']; keys = [tuple(r[k] for k in KEY) for r in rows]
    if len(keys) != len(set(keys)): raise ValueError('Original G0 references contain duplicate keys')
    required = M.N.required_arguments(inventory)
    newbed = [m for m in admitted['members'] if m['run']['sceneSource'] == 'w50']
    routes = current_routes(admitted['members'], rows, required)
    if any(r['role'] in ('blind', 'historical-prediction-check') for r in rows if
           any(tuple(r[k] for k in KEY[:3]) == tuple(m['receipt'][k] for k in KEY[:3]) for m in newbed)):
        raise ValueError('Closed native physical population is not current evidence')
    roles = native_roles(config, native_batch, scenes)
    evidence, arguments, extras = [], [], []
    by_scene = {s['id']: s for s in scenes['scenes']}
    background_cache = {}
    for member in admitted['members']:
        receipt = member['receipt']; triple = tuple(receipt[k] for k in KEY[:3])
        candidate = admitted['candidates'][receipt['candidate']['sha256']]
        originals = [r for r in rows if tuple(r[k] for k in KEY[:3]) == triple]
        if not originals or any(r['currentDocumentPair'] != candidate['originalDocumentPair'] for r in originals):
            raise ValueError('Completed gate0 draw differs from the original G0 current document pair')
        route = routes['|'.join(triple)]
        plan, spec, png, measured_arguments, provenance = capture_inputs(member, candidate,
            argument_required=route['requiredArgument'])
        if route['requiredArgument']: arguments.extend(measured_arguments)
        else:
            extras.append(dict(profile=triple[0], renderer=triple[1], scene=triple[2],
                originalReferences=copy.deepcopy(route['originalReferences']), provenance=provenance,
                status='ARTIFACTS_ONLY_USE_EXISTING_CANONICAL_REFERENCE_READER'))
        if member['run']['sceneSource'] != 'w50': continue
        role = roles[spec['role']]; native_id = receipt['profile']+'/'+receipt['scene']
        cell = role['cells'][native_id]
        if any(cell[k] != spec[k] for k in ('pose', 'span', 'background')) or \
                cell['scale'] != plan['dpr'] or cell['glass'] != plan['position']:
            raise ValueError('Original native cell differs from completed current scene geometry')
        dependency = role['deps'][cell['reference']]['evidence']
        cache_key = (spec['role'], cell['reference'])
        if cache_key not in background_cache:
            background_cache[cache_key] = M.R.read_verified_frame(Path(role['export']['root']),
                dependency, scenes['canvas'], plan['dpr'])
        scene = by_scene[receipt['scene']]
        measured = measure_pixels(M.R.S.decode_png(png), background_cache[cache_key], cell,
            scenes['components'][scene['component']], scenes['canvas'],
            impulse=scenes['backgrounds'][scene['background']]['kind'] == 'impulse', renderer=receipt['renderer'])
        provenance.update(nativeRead=role['reportPin'], nativeBatch=config['native']['batch'],
            nativeInstrument=config['native']['instrument'], nativeContract=config['native']['contract'],
            nativeExport=role['export'], nativeDependency=copy.deepcopy(dependency),
            scenes=config['originals']['scenes'])
        evidence.extend(project_native_rows(rows, measured, provenance, cell))
    if len(extras) != 12: raise ValueError('Missing T1 artifact route must contain its exact twelve captures')
    arguments = argument_population(arguments, required)
    return dict(schema='w50-completed-current-evidence-1', status='EVIDENCE_ONLY',
        currentInstrument=config['current']['instrument'], currentResults=config['current']['results'],
        chainPins=admitted['chain'], originals=config['originals'], native=config['native'],
        referenceEvidence=sorted(evidence, key=lambda r: tuple(r[k] for k in KEY)),
        arguments=arguments, canonicalMissingT1=extras,
        policy='ADDITIVE_ORIGINAL_KEYS_NO_NUMERIC_OVERRIDE_NO_PREFIT_PASS_NO_CANDIDATE_REBIND')


def source_probe():
    """Exercise the real pure core and projection with generated arrays, never captured data."""
    M.source_probe()
    E.source_probe()
    np = M.np
    canvas = {'width': 64, 'height': 64}; component = {'kind': 'rrect', 'size': [48, 48], 'radius': 0}
    background = np.zeros((64, 64, 3), dtype=np.uint8)
    web = np.full_like(background, 20)
    readings = M.R.S.read_frame(web, background, component, canvas, 1, include_structured=True,
                               silhouette_mask=np.ones((64, 64), dtype=bool))
    runs = [dict(run=n, evidence={'sha256': str(n)*64}, readings=readings) for n in (1, 2, 3)]
    cell = dict(profile='synthetic', scene='synthetic', family='structured', role='calibration',
                pose='active', scale=1, runs=runs, statistics=M.R.aggregate_runs(runs))
    read = measure_pixels(web, background, cell, component, canvas, impulse=False, renderer='css')
    rows = [dict(profile='synthetic', renderer='css', scene='synthetic', statistic=name, role='calibration',
                 currentDocumentPair={'active.dark': 'a'*64, 'receded.dark': 'b'*64}, currentGeneration='synthetic')
            for name in read['statistics']]
    if len(project_rows(rows, read, {})) != 5: raise ValueError('Synthetic current projection failed')
    argument = dict(id='synthetic|css|synthetic', profile='synthetic', renderer='css', scene='synthetic',
                    encodedLuminance=.1, linearLuminance=.2, rgb=[.2]*3)
    argument_population([argument], {argument['id']: rows[0]})
    return {'status': 'SOURCE_ONLY'}
