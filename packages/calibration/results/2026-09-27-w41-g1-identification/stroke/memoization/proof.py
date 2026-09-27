"""Proof artifacts and deferred, externally admitted completed-start verification.

The CLI runs SYNTHETIC data only. Native work is deliberately a callable worker,
not an autonomous CLI: the resource owner must invoke native_once only after
CAPTURESRELEASE, with an admission callback that accounts for this verification
process. It is one mode per process, never an additional candidate or new start.
"""
import argparse
import ast
import copy
import difflib
import gzip
import hashlib
import json
import os
from numbers import Real
from pathlib import Path
import platform
import resource
import subprocess
import time
import numpy as np
import scipy
from fixtures import HERE, PROOF, STROKE, f, r, observations, start_partition
from solver_memo import SolverMemo, Trace, fingerprint

HELD = 'd35b4cbf43f1fcdda55063b3b8e0fa178d720a78'
COMPLETED = HERE.parent/'survivor-scope-partition-0/device-M1-start-00.json'
NATIVE_ARTIFACTS = ('trace.jsonl.gz', 'raw-result.json', 'replay.json')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def environment():
    return dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                platform=platform.platform(), threads={k: os.environ.get(k) for k in
                ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')})


def sources():
    files = [Path(__file__), HERE/'fixtures.py', HERE/'solver_memo.py',
             Path(start_partition.__file__), Path(f.__file__), Path(r.__file__), Path(r.m.__file__)]
    return {str(p): sha(p) for p in files}


def destination(path):
    path = Path(path).resolve()
    if HERE not in path.parents:
        raise ValueError('new proof output must remain beneath memoization/')
    path.mkdir(exist_ok=False)
    return path


def replay_once(fit, obs, family, *, curvature=False, enabled, output):
    """Execute unchanged fit once, persisting trace, raw result and separate timing."""
    start = time.perf_counter()
    with gzip.open(output/'trace.jsonl.gz', 'wt', encoding='utf8') as stream:
        trace = Trace(stream)
        with SolverMemo(f, obs, family, curvature, enabled=enabled, trace=trace) as memo:
            result = fit(obs, family, False, curvature)
    write(output/'raw-result.json', result)
    record = dict(mode='wrapped' if enabled else 'unwrapped',
        rawResultBitsSha256=fingerprint(result), trace=trace.summary(), cache=memo.summary(),
        seconds=time.perf_counter()-start, peakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        peakRSSUnit='bytes on macOS; whole process observed high-water, not a future bound',
        environment=environment(), sourceSha256=sources())
    write(output/'replay.json', record)
    return result, record


def identical(left, right, label):
    if fingerprint(left) != fingerprint(right):
        raise AssertionError(label+' differs at exact typed/bit witness')


# Only these declared result coordinates/measurements cross the JSON numeric
# boundary. Counts, statuses, strings, undeclared keys and all trace data retain
# the original typed fingerprint. In particular bool is never a numeric value.
REPORT_NAMES = ('leastSquares', 'minimax', 'rawStartMinimax', 'lsSeededMinimax',
                'originalLeastSquares', 'originalMinimax', 'widthLsSeededMinimax')
REPORT_NUMBERS = ('maximumCodes', 'weightedSquaredError', 'railDeficitCodes',
                  'epigraphGapCodes')
REPORT_VECTORS = ('coefficients', 'singularValues', 'zeroFloorBracketCodes')


def result_boundary_fingerprint(value):
    """Compare declared JSON result numbers by float64 bits, including signed zero."""
    result = copy.deepcopy(value)

    def number(value):
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
            raise TypeError('declared result number must be a real numeric scalar')
        converted = float(value)
        if not np.isfinite(converted):
            raise ValueError('declared result number must be finite')
        return converted

    def vector(values):
        if not isinstance(values, list):
            raise TypeError('declared result vector must be a list')
        return [number(v) for v in values]

    def report(row):
        if row is None:
            return
        for name in REPORT_NUMBERS:
            if name in row and not (name == 'epigraphGapCodes' and row[name] is None):
                row[name] = number(row[name])
        for name in REPORT_VECTORS:
            if name in row and not (name == 'zeroFloorBracketCodes' and row[name] is None):
                row[name] = vector(row[name])

    for name in ('leastSquares', 'minimax'):
        if name in result:
            report(result[name])
    for start in result.get('starts', []):
        if 'initial' in start:
            start['initial'] = vector(start['initial'])
        for name in REPORT_NAMES:
            if name in start:
                report(start[name])
        for name in ('leastSquares', 'minimax'):
            for step in start.get('widthSearch', {}).get(name, {}).get('rounds', []):
                report(step['coefficientSolve'])
                step['sweep']['width'] = number(step['sweep']['width'])
                if step['sweep']['objective'] is not None:
                    step['sweep']['objective'] = number(step['sweep']['objective'])
    return fingerprint(result)


def identical_result_boundary(left, right, label):
    if result_boundary_fingerprint(left) != result_boundary_fingerprint(right):
        raise AssertionError(label+' differs at the schema-declared float64-bit JSON boundary')


def baseline_witnesses(result, completed):
    metadata = {'partitionProvenance', 'seconds', 'fittedEndpoints', 'dummyEndpoints', 'authority'}
    if set(completed)-set(result) != metadata or set(result)-set(completed):
        raise ValueError('completed artifact schema differs from unchanged raw result')
    identical_result_boundary(result, {k: completed[k] for k in result}, 'completed native raw result')
    reconstructed = dict(result, **{k: completed[k] for k in metadata if k != 'seconds'})
    identical_result_boundary(reconstructed, {k: v for k, v in completed.items() if k != 'seconds'},
                              'entire completed artifact except external elapsed time')
    return dict(jsonBoundaryResultBitsSha256=result_boundary_fingerprint(result),
                completedExceptSecondsBitsSha256=result_boundary_fingerprint(reconstructed))


def synthetic(path):
    out = destination(path)
    obs = observations(endpoints=(1,), rails=True)
    fit, provenance = start_partition.partition(f.fit_local, [0])
    untouched = fit(obs, 'M0')
    write(out/'untouched-result.json', untouched)
    results, records = [], []
    for enabled, mode in ((False, 'unwrapped'), (True, 'wrapped')):
        folder = out/mode; folder.mkdir()
        result, record = replay_once(fit, obs, 'M0', enabled=enabled, output=folder)
        identical(untouched, result, 'untouched versus '+mode)
        results.append(result); records.append(record)
    identical(records[0]['trace'], records[1]['trace'], 'solver and callback trace')
    receipt = dict(schema='w41-memoization-synthetic-proof-1', nativePayloadReads=0,
        pixels=4, endpoint=1, originalStartIndices=[0], partitionProvenance=provenance,
        resultBitIdentical=True, solverArgumentsBudgetsAndCallbackTraceIdentical=True,
        trace=records[0]['trace'], rawResultBitsSha256=fingerprint(untouched),
        cache=records[1]['cache'], sourceSha256=sources(),
        qualification='Small synthetic planted solution, not native optimizer verification.')
    write(out/'proof.json', receipt)
    return receipt


def native_once(mode, path, admit):
    """DEFERRED: one completed native start replay, callable only by resource owner.

    admit(stage) must perform the CURRENT parent's memory/concurrency admission
    and return its JSON record with admitted=True. It must register this process
    as heavy verification, not claim a new candidate. Called before preparation
    and immediately before fitting. It must account for all concurrent fits,
    the observed peak reservation and the 3 GiB floor. This module cannot discover
    or grant a resource slot, and there is deliberately no native CLI switch.
    """
    if mode not in ('unwrapped', 'wrapped') or not callable(admit):
        raise ValueError('one replay mode and an external admission callback are required')
    out = destination(path)
    def admission(stage):
        record = admit(stage)
        write(out/(stage+'-admission.json'), record)
        if not isinstance(record, dict) or record.get('admitted') is not True:
            raise PermissionError('native proof not admitted: '+stage)
    admission('before-preparation')
    if subprocess.check_output(['git', '-C', str(PROOF), 'rev-parse', 'HEAD'], text=True).strip() != HELD:
        raise ValueError('proof worktree revision changed')
    if subprocess.check_output(['git', '-C', str(PROOF), 'status', '--porcelain',
                                '--untracked-files=no'], text=True).strip():
        raise ValueError('tracked proof bytes changed')
    r.verify_seal()
    # Importing the existing scope loader does not read pixels; load_inactive
    # below is the sole native entry, reached only after external admission.
    import survivor_scope_runner as scope
    scope.verify_authority()
    completed_raw = COMPLETED.read_bytes()
    completed = json.loads(completed_raw)
    if (completed['family'], completed['cssWidth'], completed['curvature'],
            [s['startIndex'] for s in completed['starts']]) != ('M1', False, False, [0]):
        raise ValueError('expected completed device M1 original start zero')
    fit, provenance = start_partition.partition(f.fit_local, [0])
    identical(provenance, completed['partitionProvenance'], 'original start provenance')
    preparation = r.Preparation()
    inactive = scope.prior.load_inactive(preparation, 'calibration')
    obs = scope.observations_for('M1', inactive)
    # The original runner retained all inactive observations while solving M1;
    # retain the same allocation rather than change its preparation population.
    admission_rows = [dict(cell=o['cell'], endpoint=o['endpoint'], scale=o['scale'],
        pixels=len(o['target']), stateMembership=o['stateMembership']) for o in inactive]
    original_admission = json.loads((COMPLETED.parent/'calibration-admission.json').read_text())
    identical(admission_rows, original_admission, 'native preparation membership')
    write(out/'calibration-admission.json', admission_rows)
    admission('before-fit')
    with r.compact_forward():
        result, record = replay_once(fit, obs, 'M1', enabled=mode == 'wrapped', output=out)
    witnesses = baseline_witnesses(result, completed)
    proof = dict(schema='w41-memoization-native-one-mode-1', mode=mode, verified=True,
        completedArtifact=str(COMPLETED), completedSha256=hashlib.sha256(completed_raw).hexdigest(),
        **witnesses,
        partitionProvenance=provenance, nativeScope='calibration only; device M1 original start 0',
        classification='verification replay, not a new candidate', rawResultBitsSha256=fingerprint(result),
        trace=record['trace'], sourceSha256=record['sourceSha256'], environment=record['environment'],
        artifacts={name: sha(out/name) for name in NATIVE_ARTIFACTS})
    write(out/'completed-start-proof.json', proof)
    return proof


def pinned_json(reference):
    if sha(reference['path']) != reference['sha256']:
        raise ValueError('referenced proof bytes changed: '+reference['path'])
    return json.loads(Path(reference['path']).read_text())


def driver_amendment_data(old_commit):
    """Pin a driver-only amendment, proving the actual execution blocks unchanged."""
    driver = Path(__file__).resolve()
    root = Path(subprocess.check_output(['git', '-C', str(HERE), 'rev-parse',
                                        '--show-toplevel'], text=True).strip())
    old = subprocess.check_output(['git', '-C', str(root), 'show',
                                   old_commit+':'+str(driver.relative_to(root))], text=True)
    new = driver.read_text()

    def blocks(source):
        functions = {node.name: node for node in ast.parse(source).body
                     if isinstance(node, ast.FunctionDef)}
        replay = ast.get_source_segment(source, functions['replay_once'])
        native = functions['native_once']
        solves = [node for node in native.body if isinstance(node, ast.With)
                  and ast.unparse(node.items[0].context_expr) == 'r.compact_forward()']
        if len(solves) != 1:
            raise ValueError('native execution prefix is not uniquely identified')
        prefix = ''.join(source.splitlines(keepends=True)[native.lineno-1:solves[0].end_lineno])
        return dict(replay_once=hashlib.sha256(replay.encode()).hexdigest(),
                    native_onceThroughSolve=hashlib.sha256(prefix.encode()).hexdigest())

    unchanged = blocks(old)
    identical(unchanged, blocks(new), 'proof-driver execution blocks')
    old_sha, new_sha = [hashlib.sha256(text.encode()).hexdigest() for text in (old, new)]
    diff = ''.join(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile='proof.py@'+old_sha, tofile='proof.py@'+new_sha)).encode()
    return dict(schema='w41-proof-driver-comparison-amendment-1', sourcePath=str(driver),
        oldDriverCommit=old_commit, oldSourceSha256=old_sha, newSourceSha256=new_sha,
        unchangedExecutionBlocks=unchanged,
        scope='Schema-declared float64-bit JSON boundary and additive saved-proof comparison; '
              'typed live-result witnesses, solver callbacks and execution are unchanged'), diff


def compatible_sources(left, right, amendment=None):
    if left == right:
        return
    driver = str(Path(__file__).resolve())
    if set(left) != set(right) or driver not in left:
        raise AssertionError('execution source membership changed')
    identical({k: v for k, v in left.items() if k != driver},
              {k: v for k, v in right.items() if k != driver}, 'scientific and solver-wrapper sources')
    if amendment is None:
        raise AssertionError('proof-driver mismatch requires a pinned compatibility amendment')
    record = pinned_json(amendment)
    expected, diff = driver_amendment_data(record['oldDriverCommit'])
    identical({k: record[k] for k in expected}, expected, 'proof-driver compatibility amendment')
    if (left[driver], right[driver]) != (record['oldSourceSha256'], record['newSourceSha256']):
        raise AssertionError('proof-driver hashes do not match the admitted old/new pair')
    if sha(record['diff']['path']) != record['diff']['sha256'] \
            or hashlib.sha256(diff).hexdigest() != record['diff']['sha256']:
        raise ValueError('proof-driver compatibility diff bytes changed')


def verify_saved_trace(path, expected):
    digest = hashlib.sha256()
    events, counts = 0, {}
    with gzip.open(path, 'rb') as stream:
        for line in stream:
            digest.update(line)
            event = json.loads(line)['event']
            events += 1
            counts[event] = counts.get(event, 0)+1
    actual = dict(sha256=digest.hexdigest(), events=events, counts=counts)
    identical(actual, expected, 'saved ordered trace and callback counts')


def reuse_native(saved, path, terminal, driver_amendment):
    """Solve reused, comparison rerun. Read saved evidence only; never run a fitter.

    Keep the failed execution terminal and all old artifacts unchanged. The new
    receipt points to their own artifact directory and preserves the recorded
    typed in-memory result witness separately from the JSON-boundary witness.
    """
    saved = Path(saved).resolve()
    failure = pinned_json(terminal)
    if failure.get('kind') != 'STROKE_VERIFICATION_TERMINAL' \
            or failure.get('mode') != 'unwrapped' \
            or failure.get('status') != 'failed-after-solver-start' \
            or failure.get('solverStarted') is not True or failure.get('error') != dict(
                type='AssertionError', message='completed native raw result differs at exact typed/bit witness'):
        raise ValueError('expected the retained unwrapped serialization-comparison failure')
    record = json.loads((saved/'replay.json').read_text())
    if record['mode'] != 'unwrapped':
        raise ValueError('reuse is restricted to the completed unwrapped solve')
    compatible_sources(record['sourceSha256'], sources(), driver_amendment)
    verify_saved_trace(saved/'trace.jsonl.gz', record['trace'])
    result = json.loads((saved/'raw-result.json').read_text())
    completed = json.loads(COMPLETED.read_text())
    if (result['family'], result['cssWidth'], result['curvature'],
            [row['startIndex'] for row in result['starts']]) != ('M1', False, False, [0]):
        raise ValueError('expected completed device M1 original start zero')
    _, provenance = start_partition.partition(f.fit_local, [0])
    identical(provenance, completed['partitionProvenance'], 'original start provenance')
    identical(json.loads((saved/'calibration-admission.json').read_text()),
              json.loads((COMPLETED.parent/'calibration-admission.json').read_text()),
              'saved preparation membership')
    witnesses = baseline_witnesses(result, completed)
    out = destination(path)
    receipt = dict(schema='w41-memoization-native-one-mode-1', mode='unwrapped', verified=True,
        completedArtifact=str(COMPLETED), completedSha256=sha(COMPLETED), **witnesses,
        partitionProvenance=provenance, nativeScope='calibration only; device M1 original start 0',
        classification='verification replay, not a new candidate',
        rawResultBitsSha256=record['rawResultBitsSha256'], trace=record['trace'],
        sourceSha256=record['sourceSha256'], environment=record['environment'],
        artifactDirectory=str(saved), artifacts={name: sha(saved/name) for name in NATIVE_ARTIFACTS},
        comparisonRerun=dict(action='solve reused, comparison rerun', optimizerRuns=0,
            nativeArchiveReads=0, priorFailure=terminal, driverCompatibility=driver_amendment,
            comparatorSourceSha256=sha(__file__),
            originalInMemoryResultBitsSha256=record['rawResultBitsSha256'],
            jsonBoundaryResultBitsSha256=witnesses['jsonBoundaryResultBitsSha256']))
    write(out/'completed-start-proof.json', receipt)
    return receipt


def compare_native(unwrapped, wrapped, path, driver_amendment=None):
    """Verify persisted proof artifacts; no archive, optimizer or admission needed."""
    left_path = Path(unwrapped)/'completed-start-proof.json'
    right_path = Path(wrapped)/'completed-start-proof.json'
    left, right = [json.loads(p.read_text()) for p in (left_path, right_path)]
    if (left['mode'], right['mode'], left['verified'], right['verified']) != (
            'unwrapped', 'wrapped', True, True):
        raise ValueError('both verified modes are required')
    # Each compressed trace has its OWN byte pin: gzip metadata can differ
    # between equal ordered traces. Verify the full required artifact set before
    # accepting the semantic witnesses below, not merely whichever pins remain.
    for manifest, receipt in ((left_path, left), (right_path, right)):
        pins = receipt.get('artifacts')
        if not isinstance(pins, dict) or set(pins) != set(NATIVE_ARTIFACTS):
            raise ValueError('required artifact pins are missing or unexpected')
        for name in NATIVE_ARTIFACTS:
            artifact = Path(receipt.get('artifactDirectory', manifest.parent))/name
            try:
                actual = sha(artifact)
            except OSError as error:
                raise ValueError('artifact missing or unreadable: '+str(artifact)) from error
            if actual != pins[name]:
                raise ValueError('artifact bytes changed: '+str(artifact))
    for field in ('schema', 'completedArtifact', 'completedSha256',
                  'completedExceptSecondsBitsSha256', 'partitionProvenance', 'nativeScope',
                  'classification', 'rawResultBitsSha256', 'jsonBoundaryResultBitsSha256',
                  'trace', 'environment'):
        identical(left[field], right[field], field)
    compatible_sources(left['sourceSha256'], right['sourceSha256'], driver_amendment)
    receipt = dict(schema='w41-memoization-native-bit-identity-1', verified=True,
        unwrapped=dict(path=str(left_path.resolve()), sha256=sha(left_path)),
        wrapped=dict(path=str(right_path.resolve()), sha256=sha(right_path)),
        completedSha256=left['completedSha256'], trace=left['trace'],
        rawResultBitsSha256=left['rawResultBitsSha256'],
        jsonBoundaryResultBitsSha256=left['jsonBoundaryResultBitsSha256'],
        executionSourceSha256=dict(unwrapped=left['sourceSha256'], wrapped=right['sourceSha256']),
        driverCompatibility=driver_amendment,
        adoption='Not automatic: independent review and new-scheduler run-record citation required.')
    output = Path(path).resolve()
    if HERE not in output.parents:
        raise ValueError('comparison receipt must remain beneath memoization/')
    write(output, receipt)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--synthetic-out', required=True,
                        help='New directory beneath memoization; only small synthetic fits run')
    args = parser.parse_args()
    print(json.dumps(synthetic(args.synthetic_out), indent=2, allow_nan=False))
