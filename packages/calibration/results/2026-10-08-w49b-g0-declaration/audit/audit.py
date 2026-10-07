#!/Users/new/vitrea-w49/py/bin/python -I
"""Additive post-seal provenance/membership audit. This is NOT a ladder or landing verdict.

The authority is the registered batch in fb74ebc1e, never a caller-defined domain. Final mode
fails an unfinished run; --partial is diagnostic only and always reports INCOMPLETE. No pixels
are decoded and no metric, native capture, GPU render, selection or publication is performed.
"""
import argparse
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
DECL = 'packages/calibration/results/2026-10-08-w49b-g0-declaration'
SEAL = 'fb74ebc1e54cdb5c668df64d04f9d717fdfc3770'
PARTS = {'declaration': 'f8cf52f6846977e32afa322b1890aa7180acd2ca1d39f1bbe2bf584d59311b2e',
         'fit-declaration': '0bbad26c0fd1bec4b196424c4a04e53faeb81e04f38c37eb358a1ce7c097a715'}
SLOTS = ('active.light', 'active.dark', 'receded.light', 'receded.dark')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Frozen tools themselves use spec_from_file_location for shared modules. Force those
    # nested loads to compile checked source rather than reading a stale .pyc as well.
    previous = importlib.machinery.SourceFileLoader.get_code
    def source_code(loader, fullname):
        filename = loader.get_filename(fullname)
        return compile(Path(filename).read_bytes(), filename, 'exec', dont_inherit=True)
    importlib.machinery.SourceFileLoader.get_code = source_code
    try:
        exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    finally:
        importlib.machinery.SourceFileLoader.get_code = previous
    return module


K = load_module('w49b_audit_closure', HERE / 'closure.py')
sha, discover = K.sha, K.discover


def read(path):
    # Duplicate object fields and non-finite numbers cannot disguise contradictory witnesses.
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'Duplicate JSON field {key}: {path}')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError(f'Non-finite JSON: {path}')
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs, parse_constant=invalid)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def contract(root=ROOT):
    root = Path(root).resolve()
    directory = root / DECL
    source_pins = {}
    for part, wanted in PARTS.items():
        path = directory / f'{part}.json'
        require(sha(path) == wanted, f'{part} differs from fixed seal')
        require(K.git_bytes(root, SEAL, f'{DECL}/{part}.json') == path.read_bytes(),
                f'{part} differs from seal commit')
        require((directory / f'{part}.sha256').read_text() == f'{wanted}  {part}.json\n',
                f'{part} seal file differs')
        doc = read(path)
        for pin in doc['sources']:
            rel = pin['path']
            target = (root / rel).resolve()
            require(target.is_relative_to(root), f'Escaped source pin: {rel}')
            require(sha(target) == pin['sha256'], f'Changed source pin: {rel}')
            require(hashlib.sha256(K.git_bytes(root, SEAL, rel)).hexdigest() == pin['sha256'],
                    f'Source pin is not seal-commit bytes: {rel}')
            source_pins[rel] = pin['sha256']
    batch_path = directory / 'batches/identification.json'
    refs_path = directory / 'references.json'
    L = load_module('w49b_audit_frozen_render', directory / 'tools/render.py')
    C = L.C
    registry = C.load_registry(refs_path)
    # Snapshot, generation and external manifest pins must be read as actual bytes too.
    additional = {}
    def pin_record(pin):
        path = Path(pin['path'])
        if not path.is_absolute():
            path = C.CAL / path
        require(sha(path) == pin['sha256'], f'Changed reference pin: {path}')
        additional[str(path)] = pin['sha256']
    for pin in registry['inputs'].values():
        pin_record(pin)
    for pin in registry['endpoints'].values():
        pin_record(pin)
    for generation in registry['generations'].values():
        pin_record(generation['matrix'])
        for pin in generation['documents'].values():
            pin_record(pin)
    batch = C.validate_batch(read(batch_path))
    plans = [L.plan_run(registry, point, scale) for point in batch['points'] for scale in point['scales']]
    expected = {'batchSha256': sha(batch_path), 'referencesSha256': sha(refs_path),
                'points': len(batch['points']), 'runs': len(plans),
                'gateCells': sum(p['cells'] for p in plans), 'plans': plans}
    require((expected['points'], expected['runs'], expected['gateCells']) == (27, 54, 1686),
            'Registered batch does not have sealed 27-point/54-run/1686-cell membership')
    return {'root': root, 'directory': directory, 'batchPath': batch_path, 'referencesPath': refs_path,
            'batch': batch, 'registry': registry, 'plan': expected, 'L': L,
            'sourcePins': dict(sorted(source_pins.items())), 'referencePins': additional}


def bound_batch(c, path):
    require(Path(path).read_bytes() == c['batchPath'].read_bytes(),
            'Supplied bytes are not the sealed registered batch')


def audit_candidates(c, candidates):
    candidates = Path(candidates).resolve()
    bound_batch(c, candidates / 'batch.json')
    built = read(candidates / 'build.json')
    require(built.get('schemaVersion') == 1 and
            built.get('batchSha256') == c['plan']['batchSha256'] and
            built.get('referencesSha256') == c['plan']['referencesSha256'] and
            built.get('builderSha256') == sha(c['directory'] / 'tools/build.ts'),
            'Build record differs from sealed batch/reference/builder')
    labels = [p['label'] for p in c['batch']['points']]
    require([p['label'] for p in built['points']] == labels, 'Build point membership differs')
    require({p.name for p in candidates.iterdir() if p.is_dir()} == set(labels),
            'Candidate point directory membership differs')
    sources = {slot: read(c['L'].C.CAL / c['registry']['endpoints'][slot]['path']) for slot in SLOTS}
    reports = []
    for point, record in zip(c['batch']['points'], built['points']):
        label = point['label']
        folder = candidates / label
        require({p.name for p in folder.iterdir()} ==
                {'point.json', 'candidate.json', *(f'{slot}.json' for slot in SLOTS)},
                f'{label}: candidate file membership differs')
        point_path = folder / 'point.json'
        require(sha(point_path) == record['pointSha256'] and read(point_path) == point,
                f'{label}: built point is not the sealed point')
        candidate_path = folder / 'candidate.json'
        candidate = read(candidate_path)
        require(sha(candidate_path) == record['candidateSha256'], f'{label}: changed candidate bytes')
        require(candidate.get('kind') == 'vitrea-candidate-material-document' and
                candidate.get('schemaVersion') == 1 and candidate.get('glassTintAmount') == 0.25 and
                candidate.get('platform') == 'macOS 27.0' and
                candidate.get('name') == f'apple-macos-27.0-glass0.25-w49b-{c["batch"]["id"]}-{label}' and
                set(candidate['endpoints']) == set(SLOTS) and set(record['digests']) == set(SLOTS),
                f'{label}: candidate declaration differs from registered builder contract')
        endpoint_shas = {}
        for slot in SLOTS:
            entry = candidate['endpoints'][slot]
            path = folder / f'{slot}.json'
            require(entry == {'path': path.name, 'sha256': sha(path)},
                    f'{label}: changed candidate endpoint bytes {slot}')
            doc = read(path)
            source = sources[slot]
            pin = c['registry']['endpoints'][slot]
            expected = {**source, 'profileKey': source['profileKey'].replace('glass0.25', 'glass0.250'),
                        'recordedBy': f'W49b G0 scratch {c["batch"]["id"]}/{label}; not a sealed document',
                        'derivedFrom': {'path': pin['source'], 'sha256': pin['sha256']},
                        'patch': {**source['patch'], **point['overrides'].get(slot, {})},
                        'resolvedMaterialSha256': record['digests'][slot]}
            if slot.startswith('receded.'):
                expected['resolvedOverActiveDocument'] = f'active.{slot.split(".")[1]}.json'
            require(doc == expected, f'{label}: {slot} does not derive from the sealed point')
            endpoint_shas[slot] = sha(path)
        mapping = sources['active.light']['cssTierMapping']
        expected_candidate = {'kind': 'vitrea-candidate-material-document', 'schemaVersion': 1,
                              'name': f'apple-macos-27.0-glass0.25-w49b-{c["batch"]["id"]}-{label}',
                              'platform': 'macOS 27.0', 'glassTintAmount': 0.25,
                              'endpoints': {slot: {'path': f'{slot}.json', 'sha256': endpoint_shas[slot]}
                                            for slot in SLOTS}, 'cssTierMappingSha256': digest(mapping)}
        require(candidate == expected_candidate, f'{label}: candidate differs from sealed point declaration')
        reports.append({'label': label, 'pointSha256': sha(point_path),
                        'candidateSha256': sha(candidate_path), 'endpoints': endpoint_shas,
                        'digests': record['digests']})
    return {'buildSha256': sha(candidates / 'build.json'), 'points': reports}


def argv_for(c, plan, candidate, folder):
    return ['pnpm', 'run', '-s', 'compare', '--', '--profile', plan['profile'], '--renderer', 'webgpu',
            '--candidate-document', str(candidate), '--set', ','.join(c['L'].C.SETS),
            '--scene', ','.join(plan['scenes']), '--alpha', '--write-partial',
            '--out-matrix', str(folder / 'matrix.json')]


def request_check(c, plan, folder, candidate):
    request = read(folder / 'request.json')
    expected = {**plan, 'argv': argv_for(c, plan, candidate, folder),
                'batchSha256': c['plan']['batchSha256'], 'referencesSha256': c['plan']['referencesSha256'],
                'candidate': str(candidate), 'candidateSha256': sha(candidate)}
    require(request == expected, f'{plan["label"]}/{plan["scale"]}x: request/argv differs from sealed plan')


def completed_run(c, plan, folder, candidate):
    complete = read(folder / 'complete.json')
    matrix_path = folder / 'matrix.json'
    require(complete['matrixSha256'] == sha(matrix_path), f'{folder}: changed matrix bytes')
    matrix = read(matrix_path)
    require(matrix.get('schemaVersion') == 5, f'{folder}: wrong matrix schema')
    rows = matrix['cells']
    c['L'].check_rows(plan, rows, candidate)
    measured = [[r['key']['profileKey'], r['key']['web']['renderer'], r['key']['sceneId']] for r in rows]
    require(complete['requested'] == plan['requested'] and complete['planned'] == plan['planned'] and
            complete['measured'] == measured, f'{folder}: completion membership differs')
    census = read(folder / 'census.json')
    require(census.get('passes') is True and not census.get('refusals') and
            census.get('browserPin') == {'playwright': '1.62.1', 'revision': '1234',
                                        'browserVersion': c['L'].C.ENGINE_VERSION},
            f'{folder}: launch census/browser pin fails')
    require(read(folder / 'exit.json') == {'returncode': 0}, f'{folder}: failed completed run')
    owner = read(folder / 'lock.json')
    require(isinstance(owner.get('pid'), int) and isinstance(owner.get('token'), str) and owner['token'],
            f'{folder}: no launch lock ownership witness')
    captures, additional = {}, {}
    for row in rows:
        scene = row['key']['sceneId']
        base = Path('web-captures') / plan['profile'] / scene
        captures[str(base / 'cell__webgpu.json')] = None
        captures[str(base / f'{scene}__webgpu.png')] = None
        for name in ('report__webgpu.json', 'report.cell__webgpu.json', f'{scene}__webgpu__alpha.png'):
            additional[str(base / name)] = None
        require(row['key']['web']['pixelSize'] == [320 * plan['scale'], 200 * plan['scale']],
                f'{folder}: wrong capture pixel size')
    require(set(complete['captureEvidence']) == set(captures), f'{folder}: capture membership differs')
    # List names first. An extra withheld capture is rejected before its contents are opened.
    found = {str(p.relative_to(folder)) for p in (folder / 'web-captures').rglob('*') if p.is_file()}
    require(found == set(captures) | set(additional), f'{folder}: physical capture membership differs')
    for relative in additional:
        path = folder / relative
        require(path.resolve().is_relative_to(folder.resolve()), f'{folder}: escaped capture report')
        additional[relative] = sha(path)
    for relative in captures:
        path = folder / relative
        require(path.resolve().is_relative_to(folder.resolve()), f'{folder}: escaped capture')
        require(sha(path) == complete['captureEvidence'][relative], f'{folder}: changed capture bytes')
        captures[relative] = sha(path)
    for row in rows:
        scene = row['key']['sceneId']
        meta = folder / 'web-captures' / plan['profile'] / scene / 'cell__webgpu.json'
        require(read(meta) == row['key']['web'], f'{folder}: capture metadata differs from matrix')
        require(read(meta.parent / 'report.cell__webgpu.json') == row,
                f'{folder}: capture report row differs from matrix')
        report = read(meta.parent / 'report__webgpu.json')
        page = report['page']
        require(report['requestedRenderer'] == 'webgpu' and not report['problems'] and
                report.get('fallback') is None and report.get('crossPosition') is None and
                report['candidateDocument']['declarationPath'] == str(candidate) and
                report['candidateDocument']['declarationSha256'] == sha(candidate)[:12],
                f'{folder}: capture report names another candidate/renderer')
        candidate_doc = read(candidate)
        for slot in SLOTS:
            captured = report['candidateDocument']['endpoints'][slot]
            endpoint = candidate.parent / f'{slot}.json'
            require(captured['path'] == str(endpoint) and captured['sha256'] == sha(endpoint) and
                    captured['resolvedMaterialSha256'] == read(endpoint)['resolvedMaterialSha256'],
                    f'{folder}: captured endpoint differs from built candidate')
        pose = 'receded' if row['state'] == 'inactive' else 'active'
        endpoint = read(candidate.parent / f'{pose}.dark.json')
        material = {'name': candidate_doc['name'], 'platform': 'macOS 27.0', 'glassTintAmount': 0.25,
                    'profileKey': endpoint['profileKey'],
                    'resolvedMaterialSha256': endpoint['resolvedMaterialSha256'], 'tuned': False}
        require(page['sceneId'] == scene and page['materialMode'] == 'candidate' and
                page['material'] == material and page['pixelSize'] == row['key']['web']['pixelSize'] and
                page['candidateDocument']['declarationSha256'] == sha(candidate)[:12] and
                page['groups'], f'{folder}: drawn material differs from sealed point')
        for group in page['groups']:
            state = group['state']
            require(state['activeRenderer'] == 'webgpu' and state['samplingBackend'] == 'gpu-texture' and
                    state['health'] == 'ok' and state['materialDocument'] == material,
                    f'{folder}: group did not draw requested material/backend')
    return {'label': plan['label'], 'scale': plan['scale'], 'cells': len(rows),
            'requested': plan['requested'], 'planned': plan['planned'], 'measured': measured,
            'records': {name: sha(folder / name) for name in
                        ('request.json', 'complete.json', 'matrix.json', 'census.json', 'exit.json', 'lock.json')},
            'captureEvidence': captures, 'additionalCaptureWitnesses': additional,
            'lockToken': owner['token']}


def audit_records(c, candidates, renders, partial=False):
    candidates, renders = Path(candidates).resolve(), Path(renders).resolve()
    build = audit_candidates(c, candidates)
    require(read(renders / 'plan.json') == c['plan'], 'Actual root plan differs from sealed root plan')
    plans = {(p['label'], f'{p["scale"]}x'): p for p in c['plan']['plans']}
    label_dirs = [p for p in renders.iterdir() if p.is_dir()]
    require({p.name for p in label_dirs}.issubset({k[0] for k in plans}), 'Extra run membership (point)')
    folders = {(p.name, q.name): q for p in label_dirs for q in p.iterdir() if q.is_dir()}
    require(set(folders).issubset(plans), 'Extra run membership (scale)')
    reports, missing, in_progress = [], [], []
    for key, plan in plans.items():
        folder = renders / key[0] / key[1]
        candidate = candidates / key[0] / 'candidate.json'
        if not folder.is_dir():
            missing.append('/'.join(key)); continue
        if (folder / 'request.json').exists():
            request_check(c, plan, folder, candidate)
        elif any(folder.iterdir()):
            raise ValueError(f'{folder}: records exist without a request')
        if not (folder / 'complete.json').exists():
            if (folder / 'exit.json').exists():
                require(read(folder / 'exit.json') == {'returncode': 0}, f'{folder}: failed run')
            in_progress.append('/'.join(key)); continue
        request_check(c, plan, folder, candidate)
        reports.append(completed_run(c, plan, folder, candidate))
    tokens = [r['lockToken'] for r in reports]
    require(len(set(tokens)) == len(tokens), 'Duplicated launch ownership token')
    complete = not missing and not in_progress
    return {'status': 'INCOMPLETE' if partial else 'PASS' if complete else 'FAIL',
            'diagnosticOnly': partial, 'registeredPoints': 27, 'registeredRuns': 54,
            'registeredGateCells': 1686, 'completedRuns': len(reports),
            'measuredCells': sum(r['cells'] for r in reports), 'missingRuns': missing,
            'inProgressRuns': in_progress, 'build': build, 'rootPlanSha256': sha(renders / 'plan.json'),
            'runs': reports}


def fixture_witnesses(c, runs):
    cells = {(v['profile'], v['scene']): v for v in c['registry']['cells'] if v['partition'] == 'gate'}
    spec = read(c['L'].C.ROOT / 'apps/reference-apple/scenes.json')
    scenes = {v['id']: v for v in spec['scenes']}
    paths = {}
    for run in runs:
        for profile, renderer, scene in run['measured']:
            ref = cells[profile, scene]
            native = Path(ref['nativeFixture']).resolve()
            rel = f'apps/reference-apple/fixtures/{profile}/{scene}.png'
            paths[str(native)] = rel
            background = scenes[scene]['background']
            rel = f'apps/reference-apple/fixtures/backgrounds/{background}@{run["scale"]}x.png'
            paths[str(c['root'] / rel)] = rel
    report = {}
    for path, relative in sorted(paths.items()):
        actual = sha(path)
        require(actual == hashlib.sha256(K.git_bytes(c['root'], SEAL, relative)).hexdigest(),
                f'Changed gate fixture/background seal bytes: {relative}')
        report[path] = {'source': relative, 'sha256': actual}
    return report


def verify_runtime_candidates(c, candidates):
    result = subprocess.run(['pnpm', 'exec', 'tsx', str(HERE / 'verify-candidates.ts'),
                             str(Path(candidates).resolve())], cwd=c['L'].C.CAL,
                            capture_output=True, text=True)
    require(result.returncode == 0, f'CPU candidate digest/X75 validation failed: {result.stderr}')
    report = json.loads(result.stdout)
    report['environment']['pnpm'] = subprocess.check_output(['pnpm', '--version'], text=True).strip()
    return report


def audit(root, candidates, renders, partial=False):
    env = K.environment()
    c = contract(root)
    closure = discover(root, HERE / 'instrument_probe.py', commit=SEAL)
    report = audit_records(c, candidates, renders, partial)
    report.update(schema='w49b-post-seal-audit-1', sealCommit=SEAL, parts=PARTS,
                  provenanceOnly=True, ladderVerdict='NOT_SELECTED', environment=env,
                  measurementClosure=closure, sourcePins=c['sourcePins'], referencePins=c['referencePins'],
                  fixtureWitnesses=fixture_witnesses(c, report['runs']),
                  runtimeCandidates=verify_runtime_candidates(c, candidates),
                  auditSources={p.name: sha(p) for p in HERE.iterdir() if p.suffix in ('.py', '.ts')})
    # Recheck closure, source and evidence witnesses at the end rather than blessing a moving tree.
    again = discover(root, HERE / 'instrument_probe.py', commit=SEAL)
    require(again == closure, 'Instrument/environment changed during audit')
    end = audit_records(contract(root), candidates, renders, partial)
    require(end == {k: report[k] for k in end}, 'Evidence changed during audit')
    require(fixture_witnesses(c, report['runs']) == report['fixtureWitnesses'], 'Fixture bytes changed')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidates', type=Path, required=True)
    parser.add_argument('--renders', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--partial', action='store_true')
    args = parser.parse_args()
    try:
        report = audit(ROOT, args.candidates, args.renders, args.partial)
    except (ValueError, KeyError, OSError, TypeError, subprocess.SubprocessError) as error:
        report = {'schema': 'w49b-post-seal-audit-1', 'status': 'FAIL', 'sealCommit': SEAL,
                  'parts': PARTS, 'provenanceOnly': True, 'ladderVerdict': 'NOT_SELECTED',
                  'error': str(error), 'auditSources': {p.name: sha(p) for p in HERE.iterdir()
                                                      if p.suffix in ('.py', '.ts')}}
    text = json.dumps(report, indent=2, allow_nan=False) + '\n'
    if args.out:
        with args.out.open('x') as handle:
            handle.write(text)
        print(json.dumps({k: report[k] for k in ('status', 'sealCommit', 'ladderVerdict')} |
                         {'out': str(args.out.resolve()), 'reportSha256': sha(args.out)}))
    else:
        print(text, end='')
    raise SystemExit(0 if report['status'] == 'PASS' else 2 if report['status'] == 'INCOMPLETE' else 1)
