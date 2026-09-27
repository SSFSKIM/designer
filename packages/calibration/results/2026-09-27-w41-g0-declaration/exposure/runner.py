"""Renderer-bound W41 exposure; clauses 2/11, X26, claims §5.191.

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

from PIL import Image

HERE = Path(__file__).resolve().parent
BOUNDARY_PATH = HERE.parents[1] / '2026-09-26-w39-g0-colour-edge-bed/wave.py'
spec = importlib.util.spec_from_file_location('w41_inherited_wave', BOUNDARY_PATH)
boundary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boundary)
ROOT = boundary.ROOT
PRODUCTION_LOG = BOUNDARY_PATH.parent / 'wave-identification-receipt.jsonl'
INVENTORY_SHA = '58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61'
# Source aliases in calibration/web/vite.config.ts draw these trees, not dist.
SOURCE_ROOTS = tuple('packages/' + p + '/src' for p in
                     ('core', 'platform-web', 'renderer-webgpu', 'policy', 'geometry', 'motion')) + (
    'packages/calibration/web', 'packages/calibration/scripts', 'packages/calibration/src')
INSTRUMENT_ROOTS = tuple('packages/calibration/results/' + directory for directory in (
    '2026-09-26-w39-g0-colour-edge-bed', '2026-09-26-w39-g2-identification',
    '2026-09-27-w41-g0-declaration'))
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


def freeze(root, wave, candidates, *, config, scorer, declaration, closure,
           instruments=(), dry_cells=None):
    """Return a manifest to write and commit BEFORE exposure. All inputs already committed.

    Production covers all glass cells numerically and all web-plannable glass
    cells in rendered predictions, across calibration, validation AND holdout.
    A scratch manifest instead covers an explicit nonempty calibration subset.
    """
    root = Path(root).resolve()
    dry = dry_cells is not None
    if not dry and root != ROOT:
        raise ValueError('production freeze belongs to the inherited W39 repository')
    numerical = sorted(set(dry_cells)) if dry else cells_for(wave, boundary.ROLES)
    rendered = (sorted(set(numerical) & set(cells_for(wave, ('calibration',), True))) if dry
                else cells_for(wave, boundary.ROLES, True))
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
    files = set(source_list) | {config, scorer, declaration, closure} | set(instruments)
    files.update(str(p.resolve().relative_to(root)) for p in (wave.scenes_path, wave.split_path))
    if not dry:
        if (local(root, declaration) != HERE.parent / 'bounds-declaration.txt'
                or local(root, closure) != HERE.parent / 'closure.json'):
            raise ValueError('production must bind the unchanged W41 G0 declaration')
        files.update(str(p.relative_to(root)) for p in
                     (BOUNDARY_PATH, Path(__file__).resolve(), BOUNDARY_PATH.parent / 'w39_readers.py',
                      BOUNDARY_PATH.parent / 'w39_archive.py', BOUNDARY_PATH.parent / 'pins.json'))
        if sha(local(root, declaration)) != load(local(root, closure))['boundsDeclarationSha256']:
            raise ValueError('declaration/closure hash disagreement')
    runtime = load(local(root, config))
    if not dry:
        coverage(runtime['candidates'], [c['id'] for c in candidates], 'renderer candidates')
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
            background = wave.scenes[sid]['background']
            raster = backdrop_manifest['backgrounds'][f'{background}@{scale}x']
            raster_path = local(fixture, raster)
            png(raster_path, dimension(wave, cell))
            files.add(str(raster_path.relative_to(root)))
    for candidate in candidates:
        files.update(candidate[k] for k in ('parameters', 'predictions', 'rendered', 'survival'))
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
            if any(value is not True for value in survival[kind].values()):
                raise ValueError('candidate did not survive before freeze')
    hashes = {name: committed(root, name) for name in sorted(files)}
    return dict(schema='w41-renderer-exposure-1', mode='synthetic' if dry else 'production',
                revision=git(root, 'rev-parse', 'HEAD').decode().strip(),
                boundarySha256=sha(BOUNDARY_PATH), runnerSha256=sha(__file__),
                scenes=wave.scenes_sha, split=wave.split_sha,
                generation=[hashlib.sha256(b'W41 synthetic calibration only').hexdigest()
                            if dry else INVENTORY_SHA],
                numericalCells=numerical, renderedCells=rendered,
                sourceFiles=source_list, files=hashes, candidates=candidates,
                config=config, scorer=scorer, declaration=declaration, closure=closure,
                instruments=list(instruments))


def verify(root, wave, manifest_path, mode):
    manifest_path = Path(manifest_path).resolve()
    committed(root, str(manifest_path.relative_to(root)))
    manifest = load(manifest_path)
    if manifest.get('schema') != 'w41-renderer-exposure-1' or manifest.get('mode') != mode:
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


def capture_web(request):
    """Real web-only backend. No compare/matrix CLI, native Reader or harness bundle.

    Uses the existing source-aliased Chromium driver once per candidate/profile.
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
        subprocess.run(command, env=env, check=True)
        request.authorization.check(request.wave)
        for sid in ids:
            directory = destination / sid
            cell = load(directory / 'cell__webgpu.json')
            report = load(directory / 'report__webgpu.json')
            identity = profile + '/' + sid
            if (cell['sceneId'] != sid or cell['renderer'] != 'webgpu'
                    or cell['engine'] != 'chromium' or cell['colorSpace'] != 'srgb'
                    or cell['pixelSize'] != list(dimension(request.wave, identity))
                    or cell['deterministic'] is not True or cell['repeatNoise'] != 0
                    or report['fallback'] is not None or report['problems']):
                raise ValueError('capture descriptor does not attest the requested WebGPU cell')
            for key, field in [('material', 'materialProfile'), ('receded', 'recededProfile')]:
                if report[field]['sha256'] != request.manifest['files'][documents[key]][:12]:
                    raise ValueError('capture drew a different material document')
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
    numerical = (manifest['numericalCells'] if mode == 'synthetic' else
                 cells_for(wave, ('holdout',)))
    rendered = (manifest['renderedCells'] if mode == 'synthetic' else
                cells_for(wave, ('holdout',), True))
    candidates = {c['id']: c for c in manifest['candidates']}
    configuration = dict(scenes=manifest['scenes'], split=manifest['split'],
                         generation=manifest['generation'], instrument=manifest['boundarySha256'],
                         closure=manifest['files'][manifest['closure']],
                         candidate=manifest['candidates'], frozenFiles=manifest['files'],
                         manifestSha256=manifest_sha, mode=mode,
                         renderer=dict(revision=manifest['revision'],
                                       sources={p: manifest['files'][p] for p in manifest['sourceFiles']},
                                       configuration=manifest['files'][manifest['config']]))

    def verify_snapshot():
        if (sha(manifest_path) != manifest_sha
                or verify(root, wave, manifest_path, mode) != manifest):
            raise ValueError('frozen manifest mutated during exposure')

    # No closure assertion or capture occurs before begin. Failure after this
    # point spends W39's complete exposure, even if no native pixel was reached.
    with boundary.Receipt(log, configuration).expose() as authorization:
        output.mkdir(parents=True, exist_ok=False)
        result = dict(mode=mode, numericalCells=len(numerical), renderedCells=len(rendered),
                      candidates=len(candidates), manifestSha256=manifest_sha, captures={})
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
                                         candidate['id'], tuple(rendered), destination)
                captured = capture(request)
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
                    png(path, None if mode == 'synthetic' else dimension(wave, cell))
                    if digest != manifest['files'][frozen[cell]['png']]:
                        raise ValueError('capture changed a frozen rendered prediction')
                    projection = project(cell, path)
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
                    if sha(path) != result['captures'][candidate][cell]['sha256']:
                        raise ValueError('capture mutated during scoring')
            coverage(scores, candidates, 'native candidate scores')
            measured_coverage = {}
            for candidate, values in scores.items():
                measured_coverage[candidate] = {}
                coverage(values, ('numerical', 'rendered'), 'native score kinds')
                for kind, expected in [('numerical', numerical), ('rendered', rendered)]:
                    coverage(values[kind], expected, kind + ' native scores')
                    measured, censored = 0, 0
                    for cell, cell_score in values[kind].items():
                        if cell_score.get('status') == 'measured' and cell_score.get('passes') is True:
                            measured += 1
                        elif (cell_score.get('status') == 'UNMEASURED'
                              and cell_score.get('reason') == 'censored'
                              and 'passes' in cell_score and cell_score['passes'] is None
                              and cell_score.get('constraintsPass') is True):
                            # X31 v2.2: censoring is neither a pass nor coverage.
                            # The scorer must still enforce every uncensored and
                            # rail constraint; censoring cannot hide a binding miss.
                            censored += 1
                        else:
                            raise ValueError('closure failed or UNMEASURED: ' + candidate + '/' + kind + '/' + cell)
                    measured_coverage[candidate][kind] = dict(
                        measured=measured, censored=censored, total=len(expected),
                        fraction=measured / len(expected))
            result.update(status='complete', coverage=measured_coverage)
        except BaseException as error:
            result.update(status='failed', error=dict(type=type(error).__name__, message=str(error)))
            persist(output / 'result.json', result)
            raise
        # Persist the verdict before the Receipt can append complete.
        persist(output / 'result.json', result)
    return result


def run_synthetic(root, wave, manifest_path, log, output, capture, project, score):
    """G0 only: injected synthetic backend, calibration cells, external scratch log."""
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
