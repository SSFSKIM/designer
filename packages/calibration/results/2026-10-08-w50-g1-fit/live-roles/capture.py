"""LIVE capture role: one centrally derived member, one DL5h paired draw, on one lane.

capture(context, member, config) draws exactly the dispatcher's member run (candidate, or the
exposure's current baseline) through CURRENT3's paired transport for its scene source: the
canonical compare transport or the W50 new-bed transport, each with its own classifying census,
paired capture, repeat admission and report validators. The record is the transport's own,
unchanged; the member's whole retained tree is declared as its artifacts.

verify(context, member, record, config) re-derives the record from the member's retained files
with the transports' pure source validators and replays its pair proof through the root-bound
DL5h helper (common.archived_pair). It never scores. One path serves the capture stage and LIVE
qualification (retained members and adopted orphans) alike.

recover(context, member, config) adopts an orphan of a preserved stopped attempt only through
that same source reconstruction, never because a file of the right name exists. Without a
member-owned pair proof nothing was admitted, so it returns None and LIVE draws the member again
(a DL5h repeat fault is such a member). A proof whose draw does not reconstruct refuses; LIVE
then keeps the reconciliation as a preserved stop rather than rendering over an admitted draw.

A census refusal is raised as the dispatcher's CensusRefused. It is classified from the census
record the transport writes before its draw (refused and no request beside it), never from an
error message; any other failure is the dispatcher's INSTRUMENT_FAULT or LEASE_LOST.

The config (schema w50-live-capture-config-1) pins the two transports by content. Their paths
are fixed to CURRENT3's DL5h transports, so a config cannot route a member elsewhere.

Two seams of the role's own W50 transport instance change (W50 DL5n). After a completed native
read that is not ready, the root-bound DL5h helper's sealed sources refuse it: blind_cell refuses
the checkpoint, and the sealed native evaluator (measurement/capture.evaluate_native_supports,
through sources.native_statistics) raises on a stopped required statistic whose support is
empty and on a reported T1 empty in only some runs. The helper is loaded by the transport's
load_source(path, 'w50_repeat_admission'); the role wraps that loader so the loaded helper's
sources resolve
* blind_cell to measurement/readiness.blind_cell with readiness from LIVE's checkpoint (the
  sealed signature, as readiness.checkpointed_blind_cell), and
* the evaluator native_statistics calls to measurement/readiness.evaluate_supports, with the
  checkpoint's stops for that cell that leave a statistic unreadable (second pre-seal review P3).
A ready checkpoint reads exactly as the sealed functions do; a not-ready one only with its own
stops. A spread stop is not passed: its statistic has its native value and its own finite bar,
so DL5h (c) admits its pair by that bar as before; the stop decides the verdict (the judge reads
the key UNMEASURED), not the pair's qualification. Any other stop names a statistic the read
could not measure; evaluate_supports does not compute it, so it has no finite bar and its pair
needs byte identity (DL5h (ii)). A non-identical pair there, and on a reported T1 that some runs
read empty, is the helper's IdentityRequired fault, recorded in its fault receipt and recovered
as an instrument fault, never the sealed evaluator's refusal of the checkpoint. Byte-identical
pairs never reach either seam, and no other loader call, transport or helper function changes.

Every record the role returns is rebuilt from the member's source files. The transport writes its
raw record and run index (w50-capture.json and the scratch matrix; canonical complete.json) after
admission, so a kill can tear them; such a file is evidence of the interrupted write, read as
absent and never adopted, while a complete one must equal the reconstruction (second pre-seal
review P3).
"""
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def _common():
    module = types.ModuleType('w50_live_capture_common'); module.__file__ = str(HERE/'common.py')
    exec(compile((HERE/'common.py').read_bytes(), module.__file__, 'exec', dont_inherit=True), module.__dict__)
    return module


C = _common()
SCHEMA = 'w50-live-capture-config-1'
REPO = C.FIT.parents[3]
TRANSPORTS = {'canonical': str((C.CURRENT3/'canonical/adapter.py').relative_to(REPO)),
              'w50': str((C.CURRENT3/'web/adapter.py').relative_to(REPO))}


READINESS = C.FIT/'measurement/readiness.py'
REPEAT_HELPER = 'w50_repeat_admission'
SPREAD = 'NATIVE_SPREAD_EXCEEDS_ONE_CODE'


def checkpointed(transport):
    """Wrap the W50 transport's helper loader so the loaded DL5h helper's sources read blind
    readiness from LIVE's native checkpoint (module docstring). Returns the transport."""
    load_source = transport.load_source
    def loader(path, name):
        module = load_source(path, name)
        if name == REPEAT_HELPER:
            rebind(module.S, C.source(READINESS, 'w50_live_capture_readiness'))
        return module
    transport.load_source = loader
    return transport


def rebind(sources, readiness):
    """The helper instance's two seams (module docstring). newbed_pair reads a blind cell through
    blind_cell before native_statistics evaluates it, so the stops blind_cell read from the
    checkpoint for that cell are the ones its evaluation applies; a non-blind cell has none."""
    stops = {}
    def checkpointed_blind_cell(context, run, row, scenes):
        live = sys.modules.get('w50_g1_dispatch')
        if live is None: raise sources.C.InstrumentFault('Blind repeat source requires live exposure')
        live.require_context(context)
        state = readiness.native_readiness(context, live); identity = row['profile']+'/'+row['scene']
        stops[identity] = frozenset(s['statistic'] for s in state['stops']
                                    if s['cell'] == identity and s['reason'] != SPREAD)
        return readiness.blind_cell(context, run, row, scenes, state)
    def evaluate_native_supports(rgb, native_cell, analytical_masks, *, renderer):
        stopped = stops.get(native_cell['profile']+'/'+native_cell['scene'], frozenset())
        return readiness.evaluate_supports(rgb, native_cell, analytical_masks, renderer=renderer, stopped=stopped)
    measurement = types.ModuleType(sources.M.__name__); measurement.__dict__.update(vars(sources.M))
    measurement.evaluate_native_supports = evaluate_native_supports
    sources.blind_cell, sources.M = checkpointed_blind_cell, measurement


def transports(context, live, config):
    """The two content-pinned DL5h transports, loaded from bytes at their fixed paths."""
    _, doc = C.registered(context, live, config, SCHEMA)
    if set(doc) != {'schema', 'transports'} or set(doc['transports']) != set(TRANSPORTS):
        raise ValueError('Capture config must name exactly the canonical and W50 transports')
    loaded = {}
    for name, item in doc['transports'].items():
        if item.get('path') != TRANSPORTS[name]:
            raise ValueError('Capture transport is not the DL5h paired transport')
        loaded[name] = C.source(live.checked(context['repo'], item), 'w50_live_capture_'+name)
    checkpointed(loaded['w50'])
    return loaded


def _member(context, live, member):
    run = C.admit_run(context, live, member)
    if run['scenes'] != [member['scene']] or run['candidate'] != member['candidate'] or \
            member['lane'] not in ('candidate', 'current') or run.get('sceneSource') not in TRANSPORTS:
        raise ValueError('Capture member is not one admitted scene on one lane')
    return run


def _folder(run, scene):
    root = Path(run['captureRoot']).resolve()
    return root/run['profile']/scene if run['sceneSource'] == 'canonical' else root/scene


def tree(run):
    """Every retained file of the member: its capture root and its scratch matrix."""
    files = [p for p in sorted(Path(run['captureRoot']).resolve().rglob('*')) if p.is_file()]
    matrix = Path(run['matrixPath']).resolve()
    if matrix.is_file(): files.append(matrix)
    return [C.pin(p) for p in files]


def census_refused(run, scene):
    """The transport wrote a refusing census and stopped before any request for that draw."""
    root = Path(run['captureRoot']).resolve()
    census = root/f'census-{scene}.json'
    return census.is_file() and C.read(census).get('passes') is not True and \
        not (root/f'request-{scene}.json').exists()


def capture(context, member, config):
    live = C.dispatcher(context, 'capture'); C.execution_claim(context, live)
    loaded = transports(context, live, config)
    run = _member(context, live, member); current = member['lane'] == 'current'
    transport = loaded[run['sceneSource']]
    draw = transport.capture_run if run['sceneSource'] == 'canonical' else transport._capture_run
    try:
        records = draw(context, run, current=current)
    except Exception as error:
        if census_refused(run, member['scene']):
            raise live.CensusRefused('Classifying census refused before the draw') from error
        raise
    live.require_context(context)
    if not isinstance(records, list) or len(records) != 1:
        raise ValueError('A member run draws exactly its one scene')
    return {'record': records[0], 'artifacts': tree(run)}


def _png(raw, size):
    if raw[:8] != b'\x89PNG\r\n\x1a\n' or len(raw) < 24 or \
            tuple(int.from_bytes(raw[i:i+4], 'big') for i in (16, 20)) != size:
        raise ValueError('Retained PNG dimensions differ from the declared canvas')


def _argv(argv, flags):
    for flag, wanted in flags:
        if argv.count(flag) != 1 or argv[argv.index(flag)+1] != wanted:
            raise ValueError('Retained launch differs from its member, source or candidate')


def _closure(context, transport, run):
    item = run['webSourceClosure']
    if item not in context['inputs']: raise ValueError('Node/Vite closure is not a prospective root input')
    for source in C.read(transport.pin_file(item))['sources']: transport.pin_file(source)


ABSENT = object()


def written(path):
    """A transport's after-admission write, as one complete JSON document or ABSENT (module
    docstring): missing, or torn by a kill mid-write, which no complete write can be."""
    try: raw = Path(path).read_bytes()
    except FileNotFoundError: return ABSENT
    def invalid(value): raise ValueError('Nonfinite JSON')
    try: return json.loads(raw, parse_constant=invalid)
    except ValueError: return ABSENT


def _w50(context, member, run, web):
    """The W50 transport's record, from its retained request/census/report (as _capture_run)."""
    current = member['lane'] == 'current'; scene = member['scene']; tier = run['renderer']
    plan = web.scene_plan(run, context['phase'])
    if [s['scene'] for s in plan['scenes']] != [scene]: raise ValueError('Member plan differs from its scene')
    spec = plan['scenes'][0]
    candidate = web.candidate_info(run['candidate'], plan['position'], current=current)
    fixture = web.fixture_info(run, plan)
    _closure(context, web, run)
    root = Path(run['captureRoot']).resolve(); folder = root/scene
    census, request = C.read(root/f'census-{scene}.json'), C.read(root/f'request-{scene}.json')
    if census.get('passes') is not True or not (root/f'capture-{scene}.log').is_file() or \
            {k: request.get(k) for k in ('sceneSource', 'scenesSha256', 'candidate', 'fixture', 'lane')} != \
            {'sceneSource': plan['source'], 'scenesSha256': plan['scenesSha256'], 'candidate': run['candidate'],
             'fixture': fixture, 'lane': member['lane']} or request.get('argv', [None])[-1] != scene:
        raise ValueError('Retained draw does not reproduce its census-cleared member request')
    _argv(request['argv'], [('--renderer', tier), ('--scale', str(plan['dpr'])),
                            ('--candidate-document', candidate['path']), ('--out', str(root))])
    endpoint = candidate['endpoints'][f'{spec["pose"]}.dark']
    mode = {**candidate['endpoints']['active.dark']['patch'], **endpoint['patch']}.get('backdropToneAbscissa', 'source')
    mode = 'silhouette' if isinstance(mode, dict) else mode
    paths = {'png': folder/f'{scene}__{tier}.png', 'report': folder/f'report__{tier}.json',
             'cell': folder/f'cell__{tier}.json'}
    arguments = web.validate_report(C.read(paths['report']), run, endpoint, abscissa=mode, phase=context['phase'])
    cell = C.read(paths['cell'])
    if cell.get('renderer') != tier or cell.get('colorSpace') != 'srgb': raise ValueError('Wrong tier/colour space')
    _png(paths['png'].read_bytes(), (plan['canvas']['width']*plan['dpr'], plan['canvas']['height']*plan['dpr']))
    artifacts = {name: C.pin(path) for name, path in paths.items()}
    for argument in arguments:
        argument['provenance'].update(report=artifacts['report'], capture=artifacts['png'],
            sceneSource=plan['source'], scenesSha256=plan['scenesSha256'], candidateDocument=run['candidate'],
            baseline=current, endpoint={k: v for k, v in endpoint.items() if k != 'patch'})
    record = dict(profile=run['profile'], renderer=tier, scene=scene, candidate=run['candidate'],
        lane=member['lane'], sceneSource=plan['source'], canvas=plan['canvas'], dpr=plan['dpr'],
        artifacts=artifacts, arguments=arguments,
        background=next(b for b in fixture['backgrounds'] if b['key'] == f'{spec["background"]}@{plan["dpr"]}x'))
    record['repeatPair'] = C.pin(folder/f'repeat__{tier}.json')
    record['repeatAdmission'] = C.pin(folder/f'repeat-admission__{tier}.json')
    # The raw record and run index are written after admission; a crash may precede or tear either.
    raw = written(folder/'w50-capture.json')
    if raw is not ABSENT and raw != record: raise ValueError('Raw record differs from its source reconstruction')
    index = written(Path(run['matrixPath']).resolve())
    if index is not ABSENT and index != {'schema': 'w50-web-capture-index-1', 'captures': [record]}:
        raise ValueError('Member run index differs from its source reconstruction')
    return record


def _canonical(context, member, run, canonical, web):
    """The canonical transport's record, from its retained census/request/compare files (as capture_run)."""
    current = member['lane'] == 'current'; tier = run['renderer']
    plan = canonical.scene_plan(run, context['phase'])
    if [s['id'] for s in plan['scenes']] != [member['scene']]: raise ValueError('Member plan differs from its scene')
    scene = plan['scenes'][0]; sid = scene['id']
    candidate = web.candidate_info(run['candidate'], plan['position'], current=current)
    _closure(context, web, run)
    captures, matrix = Path(run['captureRoot']).resolve(), Path(run['matrixPath']).resolve()
    request = C.read(captures/'request.json')
    if request.get('run') != run or request.get('phase') != context['phase'] or request.get('lane') != member['lane'] \
            or request.get('contractSha256') != C.sha(context['contract']) \
            or request.get('batchSha256') != C.sha(context['batchPath']) or request.get('scenesSha256') != C.sha(canonical.SCENES):
        raise ValueError('Retained compare request belongs to another member, phase or contract')
    census, exit_ = C.read(captures/f'census-{sid}.json'), C.read(captures/f'exit-{sid}.json')
    fresh = C.read(captures/f'fresh-{sid}.json')
    paired = C.read(captures/f'request-{sid}.json').get('paired') or [None]*5
    if census.get('passes') is not True or exit_ != {'returncode': 0} or \
            fresh.get('schema') != 'w50-fresh-paired-input-1' or not fresh.get('artifacts') or \
            any(C.sha(path) != digest for path, digest in fresh['artifacts'].items()) or paired[4] != sid:
        raise ValueError('Retained draw lacks its census-cleared completed compare')
    _argv(paired, [('--renderer', tier), ('--candidate-document', candidate['path']),
                   ('--out', str(captures/run['profile']))])
    rows = canonical.validate_matrix(C.read(matrix), run, Path(candidate['path']))
    row = next(r for r in rows if r['key']['sceneId'] == sid)
    if row['fixtureSet'] != scene['fixtureSet']: raise ValueError('Scene split differs')
    folder = captures/run['profile']/sid
    endpoint = candidate['endpoints'][f'{"receded" if scene["state"] == "inactive" else "active"}.{plan["scheme"]}']
    canonical.validate_report(C.read(folder/f'report__{tier}.json'), run, plan, scene, endpoint)
    artifacts = canonical.capture_artifacts(folder, scene, tier, row['key']['web'], plan['dpr'])
    # capture_artifacts listed the folder before admission wrote the member's own proof.
    receipt = str(folder/f'repeat-admission__{tier}.json')
    artifacts['files'] = [p for p in artifacts['files'] if p['path'] != receipt]
    artifacts['transport'] = [C.pin(captures/name) for name in (
        f'census-{sid}.json', f'request-{sid}.json', f'exit-{sid}.json', f'compare-{sid}.log',
        f'capture-{sid}.log', f'fresh-{sid}.json', 'request.json', 'native-request.json',
        f'native-admission-{sid}.json')]
    record = dict(profile=run['profile'], renderer=tier, scene=sid, sceneSource='canonical',
        lane=member['lane'], candidate=run['candidate'], endpoint=endpoint, matrix=C.pin(matrix), row=row,
        artifacts=artifacts, coherenceStatus=('NOT_APPLICABLE' if tier == 'webgpu' else
            'MEASURED' if row.get('coherence') is not None else 'UNMEASURED'))
    record['repeatPair'] = C.pin(folder/f'repeat__{tier}.json')
    record['repeatAdmission'] = C.pin(receipt)
    raw = written(captures/'complete.json')
    if raw is not ABSENT and raw != {'status': 'CAPTURED', 'captures': [record], 'matrixSha256': C.sha(matrix)}:
        raise ValueError('Raw completion differs from its source reconstruction')
    return record


def reconstruct(context, member, run, loaded):
    if run['sceneSource'] == 'canonical': return _canonical(context, member, run, loaded['canonical'], loaded['w50'])
    return _w50(context, member, run, loaded['w50'])


def verify(context, member, record, config):
    live = C.dispatcher(context, 'capture', 'qualification'); C.execution_claim(context, live)
    loaded = transports(context, live, config)
    run = _member(context, live, member)
    if 'origin' in record or record != reconstruct(context, member, run, loaded):
        raise ValueError('Capture record differs from its source reconstruction')
    C.archived_pair(context, live, run, record, loaded)


def recover(context, member, config):
    live = C.dispatcher(context, 'qualification'); C.execution_claim(context, live)
    loaded = transports(context, live, config)
    run = _member(context, live, member)
    if not (_folder(run, member['scene'])/f'repeat-admission__{run["renderer"]}.json').is_file():
        return None
    return {'record': reconstruct(context, member, run, loaded), 'artifacts': tree(run)}


def source_probe():
    """Load both transports, their census, and the DL5h helper the archived replay executes,
    through each module's own source-only probe; no capture, report or native data is read."""
    for name, relative in TRANSPORTS.items():
        C.source(REPO/relative, 'w50_live_capture_probe_'+name).source_probe()
    C.source(C.CURRENT3/'repeat/admission.py', 'w50_live_capture_probe_repeat').source_probe()
    C.source(READINESS, 'w50_live_capture_probe_readiness')
    return {'status': 'SOURCE_ONLY'}
