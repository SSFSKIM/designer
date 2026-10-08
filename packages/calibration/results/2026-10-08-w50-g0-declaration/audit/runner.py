"""Scratch-only compare launcher; failure preserves evidence, never publishes or kills peers."""
import contextlib
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess

LOCK = Path('/tmp/w49-gpu.lock')
GUARD_PATH = Path(__file__).resolve().parent / 'numerical_guard.py'
_guard_spec = importlib.util.spec_from_file_location('w50_numerical_guard', GUARD_PATH)
G = importlib.util.module_from_spec(_guard_spec)
exec(compile(GUARD_PATH.read_bytes(), str(GUARD_PATH), 'exec'), G.__dict__)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def validate_membership(plan, references):
    roles = {}
    for cell in references['cells']:
        key = (cell['profile'], cell['renderer'], cell['scene'])
        roles.setdefault(key, set()).add(cell['role'])
    for run in plan['runs']:
        for scene in run['scenes']:
            admitted = roles.get((run['profile'], run['renderer'], scene))
            if not admitted:
                raise ValueError('Requested cell outside declared reference population')
            if plan['phase'] != 'exposure' and admitted & {'blind', 'historical-prediction-check'}:
                raise ValueError('Withheld cell requested outside the single exposure')


@contextlib.contextmanager
def owned_lock():
    with LOCK.open('x') as handle:
        handle.write(f'W50 pid={os.getpid()}\n')
    inode = LOCK.stat().st_ino
    try:
        yield
    finally:
        if LOCK.exists() and LOCK.stat().st_ino == inode:
            LOCK.unlink()


def census(cal):
    path = cal / 'results/2026-10-02-w43-g3-refit/stage/census.py'
    spec = importlib.util.spec_from_file_location('w50_census', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    observed = module.observe()
    if not observed['passes']:
        raise ValueError(f'Classifying census refuses: {observed["refusals"]}')
    return observed


def validate_numerical_referee(report, candidate_sha, root):
    domain = {'inputCodeMin': 0, 'inputCodeMax': 64, 'stepCode': 1/64,
              'spanMin': 32, 'spanMax': 224, 'scales': [1, 2],
              'positions': [0.25, 0.5], 'poses': ['active', 'receded']}
    candidates = report.get('candidateSha256s', [])
    if (report.get('schema') != 'w50-candidate-numerical-referee-1' or
            not isinstance(candidates, list) or len(candidates) != 2 or
            any(not isinstance(value, str) or len(value) != 64 for value in candidates) or
            candidates != sorted(set(candidates)) or candidate_sha not in candidates or
            report.get('status') != 'PASS' or
            report.get('domain') != domain or report.get('samples') != 6325768):
        raise ValueError('Missing candidate-bound full-domain numerical referee')
    drawdown = report.get('maxRunningDrawdownCode', float('nan'))
    neutral = report.get('minimumRequestedNeutral', float('nan'))
    if (not isinstance(drawdown, (int, float)) or not math.isfinite(drawdown) or
            not 0 <= drawdown <= 1e-4 or not isinstance(neutral, (int, float)) or
            not math.isfinite(neutral) or neutral < 0 or
            any(report.get(k) is not True for k in
                ('fixedJoinPass', 'standDownPass', 'structuredArgumentPass'))):
        raise ValueError('Numerical candidate fails monotonicity, unclamped neutral or eligibility')
    G.validate_provenance(report, candidate_sha, root)


def claim_exposure(directory, frozen):
    # Claim before any launch. A failed or interrupted read is not permission to select
    # another point or read again; the marker remains evidence for the parent decision.
    write(Path(directory) / 'exposure-started.json', frozen)


def execute(plan, output, root, batch_path):
    root, output = Path(root).resolve(), Path(output).resolve()
    cal = root / 'packages/calibration'
    common = Path(subprocess.check_output(['git', '-C', str(root), 'rev-parse',
                  '--path-format=absolute', '--git-common-dir'], text=True).strip()).parent
    if output.is_relative_to(root) or output.is_relative_to(common) or any(
            p in ('profiles', 'generations', 'web-captures-superseded') for p in output.parts):
        raise ValueError('Capture destination must be scratch, outside authoritative trees')
    declaration = Path(__file__).resolve().parent.parent
    references = json.loads((declaration / 'references.json').read_text())
    validate_membership(plan, references)
    candidate_paths = {}
    for run in plan['runs']:
        path = (root / run['candidate']['path']).resolve()
        if not path.is_file() or sha(path) != run['candidate']['sha256']:
            raise ValueError('Candidate document differs from registered bytes')
        proof = run.get('numericalReferee')
        if not proof:
            raise ValueError('UNMEASURED: candidate numerical referee is required before rendering')
        referee = (root / proof['path']).resolve()
        if not referee.is_relative_to(root) or not referee.is_file() or sha(referee) != proof['sha256']:
            raise ValueError('Candidate numerical referee bytes changed or are missing')
        validate_numerical_referee(json.loads(referee.read_text()), run['candidate']['sha256'], root)
        candidate_paths[run['id']] = path
    if plan['phase'] == 'exposure':
        frozen_path = declaration / 'frozen-candidate.json'
        frozen = json.loads(frozen_path.read_text())
        if (frozen.get('partTwoSha256') != sha(declaration / 'fit-declaration.json') or
                frozen.get('batchSha256') != sha(batch_path) or frozen.get('gateStatus') != 'PASS' or
                not frozen.get('candidateId')):
            raise ValueError('Exposure requires the one frozen passing candidate and bound batch')
        gate = frozen['gateEvidence']
        gate_path = (root / gate['path']).resolve()
        if not gate_path.is_relative_to(root) or sha(gate_path) != gate['sha256']:
            raise ValueError('Frozen candidate gate evidence changed')
        report = json.loads(gate_path.read_text())
        if report.get('status') != 'PASS' or not report.get('cells') or report.get('candidateId') != frozen['candidateId']:
            raise ValueError('Missing measured candidate gate')
        key = lambda cell: tuple(cell[k] for k in ('profile', 'renderer', 'scene', 'statistic'))
        expected = {key(c) for c in references['cells']
                    if c['role'] not in ('blind', 'historical-prediction-check')}
        measured = [key(c) for c in report['cells']]
        if (len(measured) != len(expected) or set(measured) != expected or
                any(c.get('status') != 'PASS' for c in report['cells'])):
            raise ValueError('Candidate gate is not the full exposed reference intersection')
        documents = frozen.get('documents', {})
        if any(documents.get(run['candidate']['path']) != run['candidate']['sha256'] for run in plan['runs']):
            raise ValueError('Exposure document differs from frozen candidate')
        claim_exposure(declaration, frozen)
    output.mkdir(parents=True, exist_ok=False)
    write(output / 'plan.json', {**plan, 'batchSha256': sha(batch_path)})
    for run in plan['runs']:
        folder = output / run['id']
        folder.mkdir()
        candidate = candidate_paths[run['id']]
        argv = ['pnpm', 'run', '-s', 'compare', '--', '--profile', run['profile'],
                '--renderer', run['renderer'], '--candidate-document', str(candidate),
                '--set', ','.join(run['sets']), '--scene', ','.join(run['scenes']),
                '--alpha', '--write-partial', '--out-matrix', str(folder / 'matrix.json')]
        write(folder / 'request.json', {'run': run, 'argv': argv, 'candidateSha256': sha(candidate)})
        with owned_lock():
            write(folder / 'census.json', census(cal))
            env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
            env['VITREA_WEB_CAPTURES'] = str(folder / 'web-captures')
            with (folder / 'render.txt').open('x') as log:
                result = subprocess.run(argv, cwd=cal, env=env, stdout=log, stderr=subprocess.STDOUT)
            write(folder / 'exit.json', {'returncode': result.returncode})
            if result.returncode:
                raise ValueError(f'Capture failed; partial evidence retained at {folder}')
            rows = json.loads((folder / 'matrix.json').read_text())['cells']
            expected = {(run['profile'], run['renderer'], scene) for scene in run['scenes']}
            actual = [(r['key']['profileKey'], r['key']['web']['renderer'], r['key']['sceneId']) for r in rows]
            if len(actual) != len(expected) or set(actual) != expected:
                raise ValueError('Requested/planned/measured membership differs')
            captures = {}
            stamp = f'candidateDocument={candidate} declarationSha256={sha(candidate)[:12]}'
            for row in rows:
                web = row['key']['web']
                if stamp not in web['capturePath'] or 'crossPosition=' in web['capturePath']:
                    raise ValueError('Measured material differs from candidate')
                if row['fixtureSet'] not in run['sets']:
                    raise ValueError('Measured split differs from registered run')
                scene = row['key']['sceneId']
                cell = folder / 'web-captures' / run['profile'] / scene
                meta = cell / f'cell__{run["renderer"]}.json'
                if json.loads(meta.read_text()) != web:
                    raise ValueError('Capture metadata differs from measured row')
                for path in (meta, cell / f'{scene}__{run["renderer"]}.png'):
                    captures[str(path.relative_to(folder))] = sha(path)
            write(folder / 'complete.json', {'matrixSha256': sha(folder / 'matrix.json'),
                'measured': actual, 'captureEvidence': captures})
