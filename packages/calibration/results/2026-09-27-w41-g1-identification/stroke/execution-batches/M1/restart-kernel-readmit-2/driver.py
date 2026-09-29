"""Serial M1 curvature execution after a sealed, linked no-fit readmission.

One process per start; each terminal result is audited before another task is
admitted. This controller neither changes the actual v4 gate nor a fit budget.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

STROKE = Path('/Users/new/vitrea-w41/g1/packages/calibration/results/2026-09-27-w41-g1-identification/stroke')
ROOT = STROKE / 'scheduler-run-1'
OUT = STROKE / 'execution-batches/M1/restart-kernel-readmit-2'
MANIFEST = STROKE / 'remaining-batch-M1-kernel-readmit-2.json'
FINISHED = {
    ('M1', 'device', 15): '13fe6023f1c497edf8bf9188fcf97e38f72ed9ff012694d928d01edff7996954',
    ('M1', 'curvature', 0): '74643ec2617b106d92ed5674e9bb7a4fbf2dc1d60b3399ae2258eb39aadbb5e0',
    ('M1', 'curvature', 1): 'f158ff32896be4b65029f70fa6707fd85b459c43070d4396ee909835a2e21436',
    ('M1', 'curvature', 2): 'b95bb1fb0d380eae4cdce9d4c5445e0eb37b54876236d48647994b9b8b8e3dff',
    ('M1', 'curvature', 3): '65e10ac4b1d35719cda1967393cce1b81e918321ad5df5db089e848051f3a019',
}
sys.path.insert(0, str(STROKE / 'verification-slot'))
import verification_policy_v3 as policy
s = policy.s


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def key(entry):
    return tuple(entry['task'])


def base(entry):
    family, geometry, index = entry['task']
    return f'{geometry}-{family}-start-{index:02d}'


def claim_name(entry):
    return base(entry) + ('.readmit-01.json' if key(entry) == ('M1', 'curvature', 4) else '.json')


def result_name(entry):
    return base(entry) + '.json'


def stdout_path(entry, attempt):
    return OUT / f'{base(entry)}.attempt-{attempt:03d}.stdout'


def prefix_empty(entry):
    prefix = Path(entry['argv'][3].split('=', 1)[1])
    return not prefix.exists() or (prefix.is_dir() and not any(prefix.iterdir()))


def synthetic_test():
    def e(index):
        return {'task': ['M1', 'curvature', index]}
    assert claim_name(e(4)) == 'curvature-M1-start-04.readmit-01.json'
    assert result_name(e(4)) == 'curvature-M1-start-04.json'
    assert claim_name(e(5)) == result_name(e(5)) == 'curvature-M1-start-05.json'
    entries = [e(index) for index in range(4, 16)]
    paths = [stdout_path(entry, attempt) for entry in entries for attempt in (1, 2)]
    assert len(paths) == len(set(paths)) == 24
    print(json.dumps({'kind': 'M1_SERIAL_READMISSION_SYNTHETIC_PASS',
                      'generationOneClaim': claim_name(e(4)),
                      'generationOneResult': result_name(e(4)),
                      'generationZeroClaim': claim_name(e(5)),
                      'distinctPathsTwoAttempts': len(paths)}, sort_keys=True))


def read_manifest(expected_sha):
    if digest(MANIFEST) != expected_sha:
        raise ValueError('manifest hash changed')
    batch = json.loads(MANIFEST.read_bytes())
    entries = batch['entries'][5:]
    if batch['kind'] != 'STROKE_SEALED_START_BATCH' or batch['receiptVersion'] != 4 \
            or batch['memoryReader'] != 'scheduler_v3.kernel_memory' \
            or batch['validationRead'] is not False or batch['holdoutRead'] is not False \
            or len(batch['entries']) != 17 or [key(e) for e in entries] != [
                ('M1', 'curvature', i) for i in range(4, 16)]:
        raise ValueError('batch scope/order changed')
    linked = batch['linkedReadmission']
    predecessor = linked['predecessor']
    if linked['task'] != list(key(entries[0])) \
            or digest(predecessor['path']) != predecessor['sha256'] \
            or digest(linked['previousManifest']['path']) != linked['previousManifest']['sha256'] \
            or digest(batch['supersedes']['path']) != batch['supersedes']['sha256']:
        raise ValueError('linked predecessor or supersession changed')
    prior = json.loads(Path(predecessor['path']).read_bytes())
    if prior['kind'] != 'STROKE_NO_FIT_DEFERRAL' or prior['task'] != list(key(entries[0])) \
            or prior['generation'] != 0 or prior['solverStarted'] is not False \
            or digest(prior['claim']['path']) != prior['claim']['sha256']:
        raise ValueError('generation-zero no-fit evidence changed')
    if any((ROOT / d / 'curvature-M1-start-04.json').exists()
           for d in ('started', 'failures', 'results')):
        raise ValueError('original no-fit boundary crossed')
    for entry in batch['entries'][:5]:
        if digest(entry['expectedResult']) != FINISHED[key(entry)]:
            raise ValueError('completed result changed')
    return entries, linked


def verify(entry, linked):
    ref = entry['receipt']
    launch = json.loads(Path(ref['path']).read_bytes())
    if digest(ref['path']) != ref['sha256'] or launch['task'] != entry['task'] \
            or launch['receiptVersion'] != 4:
        raise ValueError('receipt changed: ' + base(entry))
    predecessor = linked['predecessor'] if key(entry) == ('M1', 'curvature', 4) else None
    if launch.get('deferredPredecessor') != predecessor:
        raise ValueError('linked predecessor mismatch: ' + base(entry))
    argv = entry['argv']
    if argv[:3] != ['/tmp/w39-g2-wgpu/bin/python', '-B', '-X'] \
            or argv[4:8] != [str(STROKE / 'scheduler/memo_runner_v3.py'), '--root',
                             str(ROOT), '--receipt'] \
            or argv[8:] != [ref['path'], '--sha256', ref['sha256']] \
            or launch['operationalImportPolicy']['pycachePrefix'] != argv[3].split('=', 1)[1]:
        raise ValueError('sealed argv changed: ' + base(entry))
    if launch['pressureWatcher']['path'] != str(STROKE / 'scheduler-pressure-watcher-2.json'):
        raise ValueError('watcher epoch changed')
    current = claim_name(entry)
    if Path(entry['expectedResult']).exists() or not prefix_empty(entry) \
            or any((ROOT / d / current).exists() for d in ('claims', 'started', 'deferrals', 'failures')):
        raise ValueError('current generation already used: ' + current)
    for path, expected in launch['resourceSourceSha256'].items():
        if digest(path) != expected:
            raise ValueError('pinned source changed: ' + path)
    return launch


def full_test(expected_sha):
    synthetic_test()
    entries, linked = read_manifest(expected_sha)
    for entry in entries:
        verify(entry, linked)
    print(json.dumps({'kind': 'M1_SERIAL_READMISSION_FULL_PASS',
                      'manifestSha256': expected_sha, 'entries': len(entries),
                      'receiptSourcePrefixChecks': 'pass'}, sort_keys=True))


def parse_cli_deferred(text):
    lines = text.splitlines()
    match = re.fullmatch(r'[\w.]+\.Deferred: (\{.*\})', lines[-1]) if lines else None
    if not match or 'Traceback (most recent call last):' not in lines:
        return None
    try:
        decision = json.loads(match[1])
    except json.JSONDecodeError:
        return None
    return decision if decision.get('policyVersion') == 4 \
        and decision.get('admitted') is False \
        and decision.get('memory', {}).get('metric') == policy.v3.MEMORY_METRIC_V4 else None


def run(expected_sha):
    entries, linked = read_manifest(expected_sha)
    for entry in entries:
        verify(entry, linked)
    watcher = s.record(json.loads(Path(entries[0]['receipt']['path']).read_bytes())['pressureWatcher'])
    deadline = dt.datetime.fromisoformat(watcher['startedUTC']) + dt.timedelta(
        seconds=watcher['readings'] * watcher['intervalSeconds'])
    def watcher_ok():
        return dt.datetime.now(dt.timezone.utc) < deadline \
            and s.process_identity(watcher['pid']) == watcher['processIdentity']
    store = policy.PolicyStore(ROOT)
    previous = STROKE / 'execution-batches/M1/restart-kernel-readmit-1/run.jsonl'
    previous_sha = digest(previous)
    journal = (OUT / 'run.jsonl').open('x', encoding='utf8')

    def record(kind, **fields):
        row = {'atUTC': dt.datetime.now(dt.timezone.utc).isoformat(), 'kind': kind, **fields}
        journal.write(json.dumps(row, sort_keys=True, allow_nan=False) + '\n')
        journal.flush()
        os.fsync(journal.fileno())

    completed = launches = 0
    try:
        record('restart', manifestPath=str(MANIFEST), manifestSha256=expected_sha,
               previousRunPath=str(previous), previousRunSha256=previous_sha,
               linkedPredecessorSha256=linked['predecessor']['sha256'],
               controllerPID=os.getpid(), controllerSourceSha256=digest(Path(__file__)),
               count=len(entries), watcherPID=watcher['pid'],
               watcherDeadlineUTC=deadline.isoformat(), memoryMetric=policy.v3.MEMORY_METRIC_V4,
               scheduling='one fit terminal before the next claim')
        for ordinal, entry in enumerate(entries, start=1):
            attempt = 0
            while True:
                if not watcher_ok():
                    record('stop', reason='watcher expired or process identity changed')
                    raise RuntimeError('observer is not live')
                launch = verify(entry, linked)
                try:
                    with store.locked():
                        decision = store.admission(launch, os.getpid(), s.alive,
                                                   policy.v3.kernel_memory, s.process_rss)
                    if decision['memory']['metric'] != policy.v3.MEMORY_METRIC_V4:
                        raise ValueError('wrong preview memory reader')
                except s.Deferred as deferred:
                    d = deferred.decision
                    if d['memory']['metric'] != policy.v3.MEMORY_METRIC_V4:
                        raise ValueError('wrong metric disguised as resource wait')
                    record('resource_wait', ordinal=ordinal, task=entry['task'],
                           mode=d['resourceMode'], availableBytes=d['memory']['availableBytes'],
                           reservedBytes=d['reservedBytes'],
                           effectiveConcurrency=d['effectiveConcurrency'],
                           pressureLevel=d['freshestPressure']['pressureLevel'])
                    time.sleep(30)
                    continue
                if not watcher_ok():
                    raise ValueError('watcher invalid before CLI launch')
                verify(entry, linked)
                attempt += 1
                stdout = stdout_path(entry, attempt)
                start = time.monotonic()
                with stdout.open('x') as fd:
                    child = subprocess.Popen(entry['argv'], stdout=fd,
                                             stderr=subprocess.STDOUT, close_fds=True)
                    launches += 1
                    record('launch', ordinal=ordinal, attempt=attempt, task=entry['task'],
                           pid=child.pid, argv=entry['argv'], receiptSha256=entry['receipt']['sha256'],
                           sourceSha256=launch['resourceSourceSha256'], prefixInitiallyEmpty=True,
                           preflightMode=decision['resourceMode'],
                           preflightAvailableBytes=decision['memory']['availableBytes'],
                           preflightMetric=decision['memory']['metric'],
                           stdoutPath=str(stdout), expectedResult=entry['expectedResult'],
                           currentGenerationClaim=claim_name(entry))
                    exit_code = child.wait()  # Terminal barrier; no other fit is launched meanwhile.
                wall = round(time.monotonic() - start, 3)
                current = claim_name(entry)
                claim = ROOT / 'claims' / current
                result = Path(entry['expectedResult'])
                no_claim = not any((ROOT / d / current).exists()
                                   for d in ('claims', 'started', 'deferrals', 'failures')) \
                    and not result.exists()
                d = parse_cli_deferred(stdout.read_text(errors='replace')) \
                    if exit_code and no_claim and prefix_empty(entry) else None
                if d is not None:
                    record('cli_resource_wait', ordinal=ordinal, attempt=attempt,
                           task=entry['task'], pid=child.pid, exitCode=exit_code,
                           wallSeconds=wall, receiptSha256=entry['receipt']['sha256'],
                           sourceSha256=launch['resourceSourceSha256'],
                           stdoutPath=str(stdout), stdoutSha256=digest(stdout),
                           claimAbsent=True, startedAbsent=True, deferralAbsent=True,
                           failureAbsent=True, resultAbsent=True, prefixEmptyAfter=True,
                           mode=d['resourceMode'], availableBytes=d['memory']['availableBytes'],
                           reservedBytes=d['reservedBytes'],
                           effectiveConcurrency=d['effectiveConcurrency'])
                    time.sleep(30)
                    continue
                result_sha = digest(result) if result.exists() else None
                problem = None
                if exit_code or result_sha is None or not claim.exists() \
                        or (ROOT / 'failures' / current).exists() \
                        or (ROOT / 'deferrals' / current).exists():
                    problem = 'claimed deferral, CLI failure or missing exact-once result'
                else:
                    body = json.loads(result.read_bytes())
                    if body.get('validationRead') is not False \
                            or body.get('holdoutRead') is not False \
                            or body.get('memoizationOperationalSourceSha256') != launch['resourceSourceSha256'] \
                            or body.get('policyVersion') != 4:
                        problem = 'result scope/source/policy mismatch'
                record('finish', ordinal=ordinal, attempt=attempt, task=entry['task'],
                       pid=child.pid, exitCode=exit_code, wallSeconds=wall,
                       receiptSha256=entry['receipt']['sha256'],
                       sourceSha256=launch['resourceSourceSha256'], stdoutPath=str(stdout),
                       stdoutSha256=digest(stdout), resultPath=str(result),
                       resultSha256=result_sha, claimSha256=digest(claim) if claim.exists() else None,
                       solverStarted=(ROOT / 'started' / current).exists(),
                       failureExists=(ROOT / 'failures' / current).exists(),
                       deferralExists=(ROOT / 'deferrals' / current).exists(),
                       prefixEmptyAfter=prefix_empty(entry), problem=problem)
                if problem:
                    raise RuntimeError(base(entry) + ': ' + problem)
                completed += 1
                break
        record('batch_end', launched=launches, completed=completed, total=len(entries),
               status='complete', previousRunUnchanged=digest(previous) == previous_sha)
    except BaseException as error:
        record('stop', error=repr(error), traceback=traceback.format_exc(),
               launched=launches, completed=completed)
        raise
    finally:
        journal.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--synthetic-test', action='store_true')
    action.add_argument('--full-test', action='store_true')
    action.add_argument('--run', action='store_true')
    parser.add_argument('--manifest-sha256', help='Required for full test and run')
    args = parser.parse_args()
    if args.synthetic_test:
        synthetic_test()
    elif not args.manifest_sha256:
        parser.error('--manifest-sha256 is required')
    elif args.full_test:
        full_test(args.manifest_sha256)
    else:
        run(args.manifest_sha256)
