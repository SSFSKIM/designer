"""W42 renderer-bound single exposure on H: charter clause 11, X26 as carried, X33, X40,
Decision Logs 3 and 5b.

Reuses W41's X26 machinery (results/2026-09-27-w41-g0-declaration/exposure/runner.py) by
IMPORT, never by edit and never by rebinding its module globals: the W41 helpers whose
behaviour is independent of the wave (sha, stable, load, git, local, committed, coverage,
verify_runtime_artifacts, dimension, png, persist, capture_web and the two request
dataclasses) are called as they are. What W41 hard-binds to W39/W41 — the boundary module,
the receipt log, the fixed archive inventory, the W41 declaration, the source inventory
roots and an all-must-pass verdict — is replaced here by the minimum W42 derivation.
README.md lists every behavioural difference.

Importing this module reads code only: never the receipt, never an archive payload.
"""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
_boundary_spec = importlib.util.spec_from_file_location('w42_wave_boundary', HERE.parent / 'wave.py')
boundary = importlib.util.module_from_spec(_boundary_spec)
_boundary_spec.loader.exec_module(boundary)
W41_RUNNER = HERE.parents[2] / '2026-09-27-w41-g0-declaration/exposure/runner.py'
_w41_spec = importlib.util.spec_from_file_location('w41_runner_for_w42', W41_RUNNER)
w41 = importlib.util.module_from_spec(_w41_spec)
_w41_spec.loader.exec_module(w41)

ROOT = boundary.ROOT
PRODUCTION_LOG = boundary.RECEIPT_LOG
PIN_PATH = HERE / 'production-pin.json'
BOUNDARY_PATH = HERE.parent / 'wave.py'
INHERITED = (w41.BOUNDARY_PATH, W41_RUNNER)          # W39's wave.py (Receipt, Reader) and W41's runner
ENDPOINTS = ('light-active', 'light-receded', 'dark-active', 'dark-receded')
ROLES = {'landed-T': 'candidate 1: the structure composed with the LANDED T',
         'native-T': "candidate 2: the structure composed with Apple's native T from family A"}
PIN_FIELDS = ('inventoryPath', 'inventorySha256', 'declarationPath', 'declarationSha256',
              'closurePath', 'closureSha256')
SCHEMA = 'w42-renderer-exposure-1'
PROBE_REASON = 'probe: a family F bridge, read only to tie the bar across sittings (not under clause 6 or 11)'

# Unchanged W41 helpers.
sha, stable, load, git = w41.sha, w41.stable, w41.load, w41.git
local, committed, coverage = w41.local, w41.committed, w41.coverage
verify_runtime_artifacts, dimension, png = w41.verify_runtime_artifacts, w41.dimension, w41.png
persist, capture_web = w41.persist, w41.capture_web
CaptureRequest, ScoreRequest = w41.CaptureRequest, w41.ScoreRequest

# W41's source roots and files, plus every Python file of the inherited boundaries and of
# every W42 result tree, so an import added anywhere in W42's instrument cannot evade freeze.
SOURCE_ROOTS, SOURCE_FILES = w41.SOURCE_ROOTS, w41.SOURCE_FILES
INSTRUMENT_ROOTS = ('packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed',
                    'packages/calibration/results/2026-09-27-w41-g0-declaration')
W42_TREES = 'packages/calibration/results/*-w42-*'


def sources(root):
    files = {name for name in SOURCE_FILES if (root / name).exists()}
    for directory in SOURCE_ROOTS:
        base = root / directory
        if base.exists():
            files.update(str(p.relative_to(root)) for p in base.rglob('*')
                         if p.is_file() and '__pycache__' not in p.parts)
    trees = [root / d for d in INSTRUMENT_ROOTS] + sorted(root.glob(W42_TREES))
    for base in trees:
        files.update(str(p.relative_to(root)) for p in base.rglob('*.py') if '__pycache__' not in p.parts)
    for package in ('core', 'platform-web', 'renderer-webgpu', 'policy', 'geometry', 'motion', 'calibration'):
        base = root / 'packages' / package
        files.update(str(p.relative_to(root)) for p in base.glob('*.json'))
        files.update(str(p.relative_to(root)) for p in base.glob('*.mjs'))
    return sorted(files)


# --------------------------------------------------------------------- scope

def endpoint_of(wave, cell):
    """'<scheme>-<pose>': the profile's colour scheme and the scene's presentation state."""
    profile, sid = cell.split('/', 1)
    scheme = next(p['colorScheme'] for p in wave.spec['profiles'] if p['key'] == profile)
    pose = {'rest': 'active', 'inactive': 'receded'}.get(wave.scenes[sid]['state'])
    if pose is None:
        raise ValueError('a W42 glass cell is rest or inactive: ' + cell)
    return f'{scheme}-{pose}'


def declared_scope(wave, web=False):
    """Declared glass cells across calibration, validation and H (metadata only; listing H
    opens nothing). Probe bridges are excluded with a reason; `web` also applies the
    launcher's placement rule, which admits every glass cell of the W42 bed."""
    included, excluded = [], {}
    for cell in sorted(wave.cells):
        sid = cell.split('/', 1)[1]
        component = wave.component(sid)
        if boundary.native_only(component):
            continue   # no-glass references are dependencies, not predictions
        role = wave.roles[sid]
        if role == 'probe':
            excluded[cell] = PROBE_REASON
            continue
        if role not in boundary.ROLES:
            raise ValueError('undeclared identification role: ' + cell)
        refusal = boundary.web_placement_refusal(component, wave.spec['canvas']) if web else None
        if refusal:
            excluded[cell] = refusal
            continue
        included.append(cell)
    return included, excluded


def admitted_scope(root, wave, inventory):
    """Declared scope intersected with the bound archive inventory's cell metadata. The
    inventory must name this declaration; no payload path is opened."""
    path = local(root, inventory)
    if not path.is_file():
        raise ValueError('archive inventory is missing: ' + inventory)
    value = load(path)
    if value.get('scenesSha256') != wave.scenes_sha or value.get('splitSha256') != wave.split_sha:
        raise ValueError('archive inventory does not name this declaration')
    admitted = {entry['cell'] for entry in value['entries']}
    included, excluded = {}, {}
    for kind in ('numerical', 'rendered'):
        declared, reasons = declared_scope(wave, kind == 'rendered')
        included[kind] = sorted(set(declared) & admitted)
        excluded[kind] = dict(reasons)
        excluded[kind].update({c: 'not admitted by the bound archive inventory'
                               for c in sorted(set(declared) - admitted)})
    return included, excluded


def production_pins():
    """G1 fills the archive inventory pin; the G0 integration fills the declaration and
    closure pins. Until then a production freeze or run refuses before reading anything else."""
    pins = load(PIN_PATH)
    missing = [k for k in PIN_FIELDS if not pins.get(k)]
    if missing:
        raise ValueError('production refuses: production-pin.json leaves ' + ', '.join(missing)
                         + ' unset; G1 pins the W42 archive inventory (path and SHA-256) and the G0 '
                         'integration pins the declaration and closure before any production freeze')
    return pins


# -------------------------------------------------------------------- freeze

def _check_artifact(root, artifact, numerical, rendered, wave, kinds):
    parameters = load(local(root, artifact['parameters']))
    if not parameters:
        raise ValueError('empty numerical parameters: ' + artifact['id'])
    predictions = load(local(root, artifact['predictions']))['cells']
    coverage(predictions, numerical, artifact['id'] + ' numerical predictions')
    if any(value is None or value == {} or value == [] for value in predictions.values()):
        raise ValueError('empty numerical prediction payload: ' + artifact['id'])
    survival = load(local(root, artifact['survival']))
    coverage(survival, kinds, artifact['id'] + ' survival kinds')
    for kind in kinds:
        expected = numerical if kind == 'numerical' else rendered
        before = [c for c in expected if wave.roles[c.split('/', 1)[1]] != 'holdout']
        coverage(survival[kind], before, artifact['id'] + ' ' + kind + ' pre-exposure survival')
        if any(value is not True for value in survival[kind].values()):
            raise ValueError(artifact['id'] + ' did not survive calibration/validation before freeze')


def freeze(root, wave, candidates, *, law, config, scorer, declaration, closure, inventory,
           claimed_endpoints, instruments=(), mode):
    """Return the manifest to commit BEFORE the exposure (clause 11: frozen by hash first).

    `law` is the identified structure through NATIVE T ({parameters, predictions,
    survival}); `candidates` are one landed-T and at most one native-T composite, each
    {id, role, parameters, predictions, rendered, survival}. `claimed_endpoints` is
    Decision Log 3's claim scope. Scope: declared glass cells admitted by `inventory`,
    across calibration, validation AND H, numerically; their web-plannable subset rendered.
    """
    root = Path(root).resolve()
    if mode not in ('synthetic', 'production'):
        raise ValueError('mode is synthetic or production')
    production = mode == 'production'
    if production:
        pins = production_pins()
        if root != ROOT:
            raise ValueError('production freeze belongs to the W42 evidence repository')
        if (wave.scenes_path.resolve() != boundary.SCENES.resolve()
                or wave.split_path.resolve() != boundary.BED.resolve()):
            raise ValueError('production freeze binds the declared W42 bed only')
        for key, name in (('inventory', inventory), ('declaration', declaration), ('closure', closure)):
            if name != pins[key + 'Path'] or committed(root, name) != pins[key + 'Sha256']:
                raise ValueError(f'production {key} is not the pinned one')
    else:
        if wave.scenes_sha == sha(boundary.SCENES):
            raise ValueError('a synthetic freeze never binds the production W42 declaration')
        if root == ROOT or ROOT in root.parents:
            raise ValueError('a synthetic freeze belongs outside the evidence repository')
    claimed = list(claimed_endpoints)
    if not claimed or len(set(claimed)) != len(claimed) or not set(claimed) <= set(ENDPOINTS):
        raise ValueError('claimed endpoints must be a nonempty, duplicate-free subset of ' + str(ENDPOINTS))
    generation = committed(root, inventory)
    included, excluded = admitted_scope(root, wave, inventory)
    numerical, rendered = included['numerical'], included['rendered']
    if not numerical or not rendered:
        raise ValueError('no admitted numerical or web-plannable coverage')
    held = {endpoint_of(wave, c) for c in numerical if wave.roles[c.split('/', 1)[1]] == 'holdout'}
    if not set(claimed) <= held:
        raise ValueError('a claimed endpoint has no admitted held-out cell: ' + str(sorted(set(claimed) - held)))
    ids = [c['id'] for c in candidates]
    roles = [c.get('role') for c in candidates]
    if not candidates or len(set(ids)) != len(ids) or len(set(roles)) != len(roles) \
            or not set(roles) <= set(ROLES) or 'landed-T' not in roles:
        raise ValueError('candidates are one landed-T and at most one native-T composite, unique ids')
    for candidate in candidates:
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', candidate['id']) or candidate['id'] == 'law':
            raise ValueError('unsafe candidate identity')
    source_list = sources(root)
    files = set(source_list) | {config, scorer, declaration, closure, inventory} | set(instruments)
    files.update(str(p.resolve().relative_to(root)) for p in (wave.scenes_path, wave.split_path))
    if production:
        files.update(str(p.relative_to(root)) for p in
                     (BOUNDARY_PATH, boundary.PINS, Path(__file__).resolve(), PIN_PATH, *INHERITED))
    law = dict(law, id='law')
    _check_artifact(root, law, numerical, rendered, wave, ('numerical',))
    files.update(law[k] for k in ('parameters', 'predictions', 'survival'))
    runtime = load(local(root, config))
    runtime_artifacts = runtime.get('runtimeArtifacts', {})
    verify_runtime_artifacts(root, runtime_artifacts, required=production)
    files.update(runtime_artifacts.values())
    if production:
        coverage(runtime['candidates'], ids, 'renderer candidates')
        for candidate in candidates:
            profiles = runtime['candidates'][candidate['id']]['profiles']
            coverage(profiles, {c.split('/', 1)[0] for c in rendered}, 'renderer profiles')
            for documents in profiles.values():
                coverage(documents, ('material', 'receded'), 'material document pair')
                files.update(documents.values())
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
            raster = local(fixture, backdrop_manifest['backgrounds'][f"{wave.scenes[sid]['background']}@{scale}x"])
            png(raster, dimension(wave, cell))
            files.add(str(raster.relative_to(root)))
    for candidate in candidates:
        _check_artifact(root, candidate, numerical, rendered, wave, ('numerical', 'rendered'))
        files.update(candidate[k] for k in ('parameters', 'predictions', 'rendered', 'survival'))
        images = load(local(root, candidate['rendered']))['cells']
        coverage(images, rendered, candidate['id'] + ' rendered predictions')
        for cell, prediction in images.items():
            coverage(prediction, ('png', 'projection'), 'rendered artifacts')
            files.update(prediction.values())
            png(local(root, prediction['png']), dimension(wave, cell))
            if load(local(root, prediction['projection'])) is None:
                raise ValueError('empty rendered projection')
    hashes = {name: committed(root, name) for name in sorted(files)}
    return dict(schema=SCHEMA, mode=mode, revision=git(root, 'rev-parse', 'HEAD').decode().strip(),
                boundarySha256=sha(BOUNDARY_PATH), runnerSha256=sha(__file__),
                inheritedSha256={str(p.relative_to(ROOT)): sha(p) for p in INHERITED},
                scenes=wave.scenes_sha, split=wave.split_sha, generation=[generation], inventory=inventory,
                excludedCells=excluded, runtimeArtifacts=runtime_artifacts,
                numericalCells=numerical, renderedCells=rendered, claimedEndpoints=sorted(claimed),
                sourceFiles=source_list, files=hashes, law=law, candidates=candidates,
                config=config, scorer=scorer, declaration=declaration, closure=closure,
                instruments=list(instruments))


def verify(root, wave, manifest_path, mode):
    manifest_path = Path(manifest_path).resolve()
    committed(root, str(manifest_path.relative_to(root)))
    manifest = load(manifest_path)
    if manifest.get('schema') != SCHEMA or manifest.get('mode') != mode:
        raise ValueError('wrong exposure manifest mode/schema')
    if (sha(BOUNDARY_PATH) != manifest['boundarySha256'] or sha(__file__) != manifest['runnerSha256']
            or {str(p.relative_to(ROOT)): sha(p) for p in INHERITED} != manifest['inheritedSha256']):
        raise ValueError('receipt boundary, runner or inherited machinery mutated after freeze')
    if manifest['sourceFiles'] != sources(root):
        raise ValueError('renderer source inventory changed after freeze')
    for name, expected in manifest['files'].items():
        if committed(root, name) != expected:
            raise ValueError('frozen artifact changed: ' + name)
    for name in manifest['sourceFiles']:
        saved = git(root, 'show', manifest['revision'] + ':' + name)
        if hashlib.sha256(saved).hexdigest() != manifest['files'][name]:
            raise ValueError('renderer revision does not own source: ' + name)
    law = {k: v for k, v in manifest['law'].items() if k != 'id'}
    rebuilt = freeze(root, wave, manifest['candidates'], law=law, config=manifest['config'],
                     scorer=manifest['scorer'], declaration=manifest['declaration'], closure=manifest['closure'],
                     inventory=manifest['inventory'], claimed_endpoints=manifest['claimedEndpoints'],
                     instruments=manifest['instruments'], mode=mode)
    rebuilt['revision'] = manifest['revision']
    if stable(rebuilt) != stable(manifest):
        raise ValueError('manifest does not describe the complete frozen configuration')
    return manifest


# ------------------------------------------------------------------- verdict

def classify(row, where):
    """X31's statuses as W41 carries them. A measured row passes or fails; a censored
    UNMEASURED row is excluded from pass and coverage when its uncensored and rail
    constraints hold, and FAILS when they do not; anything else is a procedural refusal."""
    if not isinstance(row, dict):
        raise ValueError('score row is not an object: ' + where)
    if row.get('status') == 'measured' and row.get('passes') in (True, False):
        return 'passed' if row['passes'] else 'failed'
    if (row.get('status') == 'UNMEASURED' and row.get('reason') == 'censored' and 'passes' in row
            and row['passes'] is None and row.get('constraintsPass') in (True, False)):
        return 'censored' if row['constraintsPass'] else 'failed'
    raise ValueError('invalid or non-censored UNMEASURED score: ' + where)


def tally(wave, rows, claimed, where):
    groups = {'claimed': {}, 'notClaimed': {}}
    for cell, row in sorted(rows.items()):
        endpoint = endpoint_of(wave, cell)
        side = 'claimed' if endpoint in claimed else 'notClaimed'
        g = groups[side].setdefault(endpoint, dict(total=0, measured=0, passed=0, failed=0, censored=0,
                                                   failedCells=[]))
        state = classify(row, f'{where}/{cell}')
        g['total'] += 1
        g[state] += 1
        if state != 'censored':
            g['measured'] += 1
        if state == 'failed':
            g['failedCells'].append(cell)
    for g in groups['notClaimed'].values():
        g['status'] = 'not claimed (identity)'
    for g in groups['claimed'].values():
        g['fraction'] = g['measured'] / g['total']
    closes = all(endpoint in groups['claimed'] and groups['claimed'][endpoint]['failed'] == 0
                 and groups['claimed'][endpoint]['measured'] >= 1 for endpoint in claimed)
    return groups, closes


def verdict(wave, manifest, scores, numerical, rendered):
    """Clause 11's bar on one receipt. The law (structure through native T) closes iff every
    measured held-out cell of every claimed endpoint passes, with at least one measured cell
    per claimed endpoint. Candidate 2 (native T) is its render against Apple; candidate 1
    (landed T) is its render against its own frozen prediction, the gap to Apple recorded as
    the named level miss. A candidate is landable only where the law closes; one candidate's
    failure never fails the other. Unclaimed endpoints are scored and reported."""
    coverage(scores, ('law', 'candidates'), 'score sections')
    coverage(scores['law'], ('numerical',), 'law score kinds')
    coverage(scores['law']['numerical'], numerical, 'law numerical scores')
    claimed = manifest['claimedEndpoints']
    law_groups, law_closes = tally(wave, scores['law']['numerical'], claimed, 'law/numerical')
    candidates = {c['id']: c for c in manifest['candidates']}
    coverage(scores['candidates'], candidates, 'candidate scores')
    out = {}
    for cid, artifact in candidates.items():
        coverage(scores['candidates'][cid], ('rendered',), cid + ' score kinds')
        rows = scores['candidates'][cid]['rendered']
        coverage(rows, rendered, cid + ' rendered scores')
        groups, passes = tally(wave, rows, claimed, cid + '/rendered')
        entry = dict(role=artifact['role'],
                     referee=('its frozen structure-with-landed-T prediction' if artifact['role'] == 'landed-T'
                              else "Apple's held-out pixels"),
                     rendered=groups, passes=passes, landable=law_closes and passes)
        if artifact['role'] == 'landed-T':
            missing = [c for c, row in rows.items()
                       if row.get('status') == 'measured' and row.get('levelMiss') is None]
            if missing:
                raise ValueError('landed-T rows must record the levelMiss against Apple: ' + ', '.join(missing))
            entry['levelMiss'] = {c: row.get('levelMiss') for c, row in sorted(rows.items())}
        out[cid] = entry
    landable = sorted(cid for cid, e in out.items() if e['landable'])
    by_role = {e['role']: cid for cid, e in out.items()}
    selected = next((by_role[r] for r in ('native-T', 'landed-T') if r in by_role and by_role[r] in landable), None)
    return dict(law=dict(closes=law_closes, endpoints=law_groups), candidates=out, landable=landable,
                selectedByX40=selected, claimedEndpoints=claimed,
                notClaimed=sorted(set(ENDPOINTS) - set(claimed)),
                rule='X40: candidate 2 lands instead of candidate 1 only if it passes every check; '
                     'nothing lands unless the law closes (clause 11)')


# ------------------------------------------------------------------ exposure

def scratch_path(path):
    """Scratch can neither name nor alias the production receipt, nor live in the repository."""
    path = Path(path).resolve()
    if path == PRODUCTION_LOG.resolve() or ROOT == path or ROOT in path.parents:
        raise PermissionError('synthetic/output path must be outside the evidence repository')
    if path.exists() and (path.is_symlink() or path.stat().st_nlink != 1):
        raise PermissionError('scratch path cannot be a filesystem alias')
    return path


def _run(root, wave, manifest_path, log, output, capture, project, score, mode):
    root = Path(root).resolve()
    manifest = verify(root, wave, manifest_path, mode)
    manifest_sha = sha(manifest_path)
    output = scratch_path(output)
    score_report = Path(log).with_name(Path(log).stem + '-scores.json')
    if output.exists() or score_report.exists():
        raise ValueError('capture destination or score record already exists; no reuse or retry')

    def holdout(cells):
        return [c for c in cells if wave.roles[c.split('/', 1)[1]] == 'holdout']
    numerical, rendered = holdout(manifest['numericalCells']), holdout(manifest['renderedCells'])
    candidates = {c['id']: c for c in manifest['candidates']}
    configuration = dict(scenes=manifest['scenes'], split=manifest['split'], generation=manifest['generation'],
                         instrument=manifest['boundarySha256'], closure=manifest['files'][manifest['closure']],
                         candidate=manifest['candidates'], law=manifest['law'],
                         claimedEndpoints=manifest['claimedEndpoints'], frozenFiles=manifest['files'],
                         manifestSha256=manifest_sha, mode=mode,
                         renderer=dict(revision=manifest['revision'], runtimeArtifacts=manifest['runtimeArtifacts'],
                                       sources={p: manifest['files'][p] for p in manifest['sourceFiles']},
                                       configuration=manifest['files'][manifest['config']]))

    def verify_snapshot():
        if sha(manifest_path) != manifest_sha or verify(root, wave, manifest_path, mode) != manifest:
            raise ValueError('frozen manifest mutated during exposure')

    # Nothing is captured, scored or asserted before begin. Any failure after it spends H.
    with boundary.Receipt(log, configuration).expose() as authorization:
        output.mkdir(parents=True, exist_ok=False)
        result = dict(mode=mode, numericalCells=len(numerical), renderedCells=len(rendered),
                      candidates=len(candidates), manifestSha256=manifest_sha, captures={})
        try:
            authorization.check(wave)
            # The launcher's H plan must be exactly the frozen rendered scope, less any H
            # scene the archive admitted in no profile (excluded with its reason at freeze).
            posed = {c.split('/', 1)[1] for c in rendered}
            unadmitted = {c.split('/', 1)[1] for c, why in manifest['excludedCells']['rendered'].items()
                          if why.startswith('not admitted')} - posed
            planned = set(wave.launch_scenes(('holdout',), authorization)) - unadmitted
            coverage(posed, planned, 'authorized web plan')
            captures = {}
            for candidate in manifest['candidates']:
                destination = output / candidate['id']
                destination.mkdir()
                request = CaptureRequest(wave, authorization, root, deepcopy(manifest), candidate['id'],
                                         tuple(rendered), destination)
                captured = capture(request)
                verify_runtime_artifacts(root, manifest['runtimeArtifacts'], required=mode == 'production')
                if request.manifest != manifest:
                    raise ValueError('capture callback mutated its manifest')
                coverage(captured, rendered, 'captured cells')
                frozen = load(root / candidate['rendered'])['cells']
                verified, records = {}, result['captures'].setdefault(candidate['id'], {})
                for cell, path in captured.items():
                    path = Path(path).resolve()
                    if destination not in path.parents or not path.is_file():
                        raise ValueError('capture backend returned a missing or reused artifact')
                    digest = sha(path)
                    records[cell] = dict(path=str(path), sha256=digest)
                    png(path, dimension(wave, cell))
                    if digest != manifest['files'][frozen[cell]['png']]:
                        raise ValueError('capture changed a frozen rendered prediction')
                    projection = project(cell, path)
                    verify_runtime_artifacts(root, manifest['runtimeArtifacts'], required=mode == 'production')
                    if stable(projection) != stable(load(root / frozen[cell]['projection'])):
                        raise ValueError('capture changed a frozen rendered prediction projection')
                    verified[cell] = path
                captures[candidate['id']] = verified
            verify_snapshot()
            request = ScoreRequest(wave, authorization, root, deepcopy(manifest), deepcopy(candidates),
                                   tuple(numerical), tuple(rendered), deepcopy(captures))
            # The complete returned report is durable before any check or aggregation.
            scores = json.loads(stable(score(request)))
            result['scores'] = scores
            persist(score_report, dict(result, status='scored'))
            result['scoreReport'] = dict(path=str(score_report), sha256=sha(score_report))
            if request.manifest != manifest or request.candidates != candidates or request.captures != captures:
                raise ValueError('score callback mutated its input snapshots')
            verify_snapshot()
            for cid, paths in captures.items():
                for cell, path in paths.items():
                    if sha(path) != result['captures'][cid][cell]['sha256']:
                        raise ValueError('capture mutated during scoring')
            result.update(status='complete', verdict=verdict(wave, manifest, scores, numerical, rendered))
        except BaseException as error:
            result.update(status='failed', error=dict(type=type(error).__name__, message=str(error)))
            persist(output / 'result.json', result)
            raise
        persist(output / 'result.json', result)
    return result


def run_synthetic(root, wave, manifest_path, log, output, capture, project, score):
    """G0 proof only: a toy declaration outside the repository, injected backends, a scratch log."""
    log = scratch_path(log)
    if log.exists() and log.stat().st_size:
        raise PermissionError('scratch exposure already spent')
    if wave.scenes_sha == sha(boundary.SCENES):
        raise PermissionError('the synthetic path never exposes the production W42 declaration')
    return _run(root, wave, manifest_path, log, output, capture, project, score, 'synthetic')


def run_production(manifest_path, output):
    """G2 only, after clause 10 and the frozen blind H predictions. The committed scorer
    exports project(cell, png) and score(request); it is imported inside the receipt."""
    production_pins()
    wave = boundary.default_wave()
    manifest = verify(ROOT, wave, manifest_path, 'production')
    source = ROOT / manifest['scorer']
    module_spec = importlib.util.spec_from_file_location('w42_frozen_scorer', source)
    module = importlib.util.module_from_spec(module_spec)
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
