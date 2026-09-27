"""Proof artifacts and deferred, externally admitted completed-start verification.

The CLI runs SYNTHETIC data only. Native work is deliberately a callable worker,
not an autonomous CLI: the resource owner must invoke native_once only after
CAPTURESRELEASE, with an admission callback that accounts for this verification
process. It is one mode per process, never an additional candidate or new start.
"""
import argparse
import gzip
import hashlib
import json
import os
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
    metadata = {'partitionProvenance', 'seconds', 'fittedEndpoints', 'dummyEndpoints', 'authority'}
    if set(completed)-set(result) != metadata or set(result)-set(completed):
        raise ValueError('completed artifact schema differs from unchanged raw result')
    identical(result, {k: completed[k] for k in result}, 'completed native raw result')
    # Preserve all original metadata; exclude ONLY its external elapsed time.
    reconstructed = dict(result, **{k: completed[k] for k in metadata if k != 'seconds'})
    identical(reconstructed, {k: v for k, v in completed.items() if k != 'seconds'},
              'entire completed artifact except external elapsed time')
    proof = dict(schema='w41-memoization-native-one-mode-1', mode=mode, verified=True,
        completedArtifact=str(COMPLETED), completedSha256=hashlib.sha256(completed_raw).hexdigest(),
        completedExceptSecondsBitsSha256=fingerprint(reconstructed),
        partitionProvenance=provenance, nativeScope='calibration only; device M1 original start 0',
        classification='verification replay, not a new candidate', rawResultBitsSha256=fingerprint(result),
        trace=record['trace'], sourceSha256=record['sourceSha256'], environment=record['environment'],
        artifacts={name: sha(out/name) for name in NATIVE_ARTIFACTS})
    write(out/'completed-start-proof.json', proof)
    return proof


def compare_native(unwrapped, wrapped, path):
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
            artifact = manifest.parent/name
            try:
                actual = sha(artifact)
            except OSError as error:
                raise ValueError('artifact missing or unreadable: '+str(artifact)) from error
            if actual != pins[name]:
                raise ValueError('artifact bytes changed: '+str(artifact))
    for field in ('schema', 'completedArtifact', 'completedSha256',
                  'completedExceptSecondsBitsSha256', 'partitionProvenance', 'nativeScope',
                  'classification', 'rawResultBitsSha256', 'trace', 'sourceSha256', 'environment'):
        identical(left[field], right[field], field)
    receipt = dict(schema='w41-memoization-native-bit-identity-1', verified=True,
        unwrapped=dict(path=str(left_path.resolve()), sha256=sha(left_path)),
        wrapped=dict(path=str(right_path.resolve()), sha256=sha(right_path)),
        completedSha256=left['completedSha256'], trace=left['trace'],
        rawResultBitsSha256=left['rawResultBitsSha256'], sourceSha256=left['sourceSha256'],
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
