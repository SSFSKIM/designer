"""Execute only the declared M1 curvature tail with one linked no-fit readmission.

Run --self-test before --run. This operational controller is not a scientific
source, policy implementation, or scheduler override. Only the sealed CLI argv
may claim a task; a preview is an unreserved resource reading.
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
import threading
import time
import traceback

STROKE = Path('/Users/new/vitrea-w41/g1/packages/calibration/results/2026-09-27-w41-g1-identification/stroke')
ROOT = STROKE / 'scheduler-run-1'
OUT = STROKE / 'execution-batches/M1/restart-kernel-readmit-1'
MANIFEST = STROKE / 'remaining-batch-M1-kernel-readmit-1.json'
MANIFEST_SHA256 = '70b437813878ae7f8f5e947262858b9636379b0992b202e0d27ef22fdf2ab40a'
PREDECESSOR_SHA256 = '65806438e0783c42dc059a06fba6e65bef47860fce149cfb845396484252fab8'
FINISHED = {
    ('M1', 'device', 15): '13fe6023f1c497edf8bf9188fcf97e38f72ed9ff012694d928d01edff7996954',
    ('M1', 'curvature', 0): '74643ec2617b106d92ed5674e9bb7a4fbf2dc1d60b3399ae2258eb39aadbb5e0',
    ('M1', 'curvature', 1): 'f158ff32896be4b65029f70fa6707fd85b459c43070d4396ee909835a2e21436',
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
    return base(entry) + ('.readmit-01.json' if key(entry) == ('M1', 'curvature', 2) else '.json')


def result_name(entry):
    return base(entry) + '.json'


def stdout_path(entry, attempt):
    return OUT / f'{base(entry)}.attempt-{attempt:03d}.stdout'


def prefix_empty(entry):
    prefix = Path(entry['argv'][3].split('=', 1)[1])
    return not prefix.exists() or (prefix.is_dir() and not any(prefix.iterdir()))


def read_manifest():
    if digest(MANIFEST) != MANIFEST_SHA256:
        raise ValueError('manifest hash changed')
    batch = json.loads(MANIFEST.read_bytes())
    entries = batch['entries'][3:]
    if batch['kind'] != 'STROKE_SEALED_START_BATCH' or batch['receiptVersion'] != 4 \
            or batch['memoryReader'] != 'scheduler_v3.kernel_memory' \
            or batch['validationRead'] is not False or batch['holdoutRead'] is not False \
            or len(batch['entries']) != 17 or [key(e) for e in entries] != [
                ('M1', 'curvature', i) for i in range(2, 16)]:
        raise ValueError('batch order and scope changed')
    linked = batch['linkedReadmission']
    if linked['task'] != list(key(entries[0])) \
            or linked['predecessor']['sha256'] != PREDECESSOR_SHA256 \
            or digest(linked['predecessor']['path']) != PREDECESSOR_SHA256 \
            or digest(linked['previousManifest']['path']) != linked['previousManifest']['sha256'] \
            or digest(batch['supersedes']['path']) != batch['supersedes']['sha256']:
        raise ValueError('linked predecessor/supersession changed')
    predecessor = json.loads(Path(linked['predecessor']['path']).read_bytes())
    if predecessor['kind'] != 'STROKE_NO_FIT_DEFERRAL' \
            or predecessor['task'] != list(key(entries[0])) \
            or predecessor['generation'] != 0 or predecessor['solverStarted'] is not False \
            or digest(predecessor['claim']['path']) != predecessor['claim']['sha256']:
        raise ValueError('generation-zero no-fit evidence changed')
    if any((ROOT / d / 'curvature-M1-start-02.json').exists()
           for d in ('started', 'failures', 'results')):
        raise ValueError('original no-fit boundary was crossed')
    for entry in batch['entries'][:3]:
        if digest(entry['expectedResult']) != FINISHED[key(entry)]:
            raise ValueError('already completed result changed')
    return entries, linked


def verify(entry, linked):
    receipt = entry['receipt']
    launch = json.loads(Path(receipt['path']).read_bytes())
    if digest(receipt['path']) != receipt['sha256'] or launch['task'] != entry['task'] \
            or launch['receiptVersion'] != 4:
        raise ValueError('receipt hash/version/task mismatch: ' + base(entry))
    expected_predecessor = linked['predecessor'] if key(entry) == ('M1', 'curvature', 2) else None
    if launch.get('deferredPredecessor') != expected_predecessor:
        raise ValueError('linked predecessor mismatch: ' + base(entry))
    argv = entry['argv']
    if argv[:3] != ['/tmp/w39-g2-wgpu/bin/python', '-B', '-X'] \
            or argv[4:8] != [str(STROKE / 'scheduler/memo_runner_v3.py'), '--root',
                             str(ROOT), '--receipt'] \
            or argv[8:] != [receipt['path'], '--sha256', receipt['sha256']] \
            or launch['operationalImportPolicy']['pycachePrefix'] != argv[3].split('=', 1)[1]:
        raise ValueError('sealed argv/prefix changed: ' + base(entry))
    if launch['pressureWatcher']['path'] != str(STROKE / 'scheduler-pressure-watcher-2.json'):
        raise ValueError('watcher epoch changed')
    current = claim_name(entry)
    if Path(entry['expectedResult']).exists() or not prefix_empty(entry) \
            or any((ROOT / d / current).exists() for d in ('claims', 'started', 'deferrals', 'failures')):
        raise ValueError('current generation already used: ' + current)
    return launch


def self_test():
    entries, linked = read_manifest()
    assert claim_name(entries[0]) == 'curvature-M1-start-02.readmit-01.json'
    assert result_name(entries[0]) == 'curvature-M1-start-02.json'
    assert claim_name(entries[1]) == 'curvature-M1-start-03.json'
    assert result_name(entries[1]) == 'curvature-M1-start-03.json'
    assert claim_name(entries[0]) != 'curvature-M1-start-02.json'
    paths = [stdout_path(entry, attempt) for entry in entries for attempt in (1, 2)]
    assert len(paths) == len(set(paths)) == 28
    for entry in entries:
        verify(entry, linked)
        for path, value in json.loads(Path(entry['receipt']['path']).read_bytes())['resourceSourceSha256'].items():
            if digest(path) != value:
                raise ValueError('pinned source changed: ' + path)
    print(json.dumps({'kind': 'M1_READMISSION_CONTROLLER_PRECHECK',
                      'manifestSha256': MANIFEST_SHA256, 'entries': len(entries),
                      'generationOneClaim': claim_name(entries[0]),
                      'generationOneResult': result_name(entries[0]),
                      'generationZeroNextClaim': claim_name(entries[1]),
                      'distinctPathsTwoAttempts': len(paths),
                      'receiptSourceAndPrefixChecks': 'pass'}, sort_keys=True))


def run():
    entries, linked = read_manifest()
    for entry in entries:
        verify(entry, linked)
    watcher = s.record(json.loads(Path(entries[0]['receipt']['path']).read_bytes())['pressureWatcher'])
    deadline = dt.datetime.fromisoformat(watcher['startedUTC']) + dt.timedelta(
        seconds=watcher['readings'] * watcher['intervalSeconds'])
    def watcher_ok():
        return dt.datetime.now(dt.timezone.utc) < deadline \
            and s.process_identity(watcher['pid']) == watcher['processIdentity']
    store = policy.PolicyStore(ROOT)
    prior = STROKE / 'execution-batches/M1/restart-kernel-3/run.jsonl'
    prior_sha = digest(prior)
    journal = (OUT / 'run.jsonl').open('x', encoding='utf8')
    cv = threading.Condition()
    active, outcomes = {}, {}
    completed, launches, failure = 0, 0, None

    def record(kind, **data):
        with cv:
            row = {'atUTC': dt.datetime.now(dt.timezone.utc).isoformat(), 'kind': kind, **data}
            journal.write(json.dumps(row, sort_keys=True, allow_nan=False) + '\n')
            journal.flush()
            os.fsync(journal.fileno())
            cv.notify_all()

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

    def settle(index, entry, attempt, child, fd, start, sources, stdout):
        nonlocal completed, failure
        exit_code = child.wait()
        wall = round(time.monotonic() - start, 3)
        fd.close()
        current = claim_name(entry)
        claim = ROOT / 'claims' / current
        marker = ROOT / 'started' / current
        result = Path(entry['expectedResult'])
        problem = None
        try:
            no_claim = not any((ROOT / d / current).exists()
                               for d in ('claims', 'started', 'deferrals', 'failures')) \
                and not result.exists()
            decision = parse_cli_deferred(stdout.read_text(errors='replace')) \
                if exit_code and no_claim and prefix_empty(entry) else None
            if decision is not None:
                state = 'resource_wait'
                record('cli_resource_wait', ordinal=index+1, attempt=attempt, task=entry['task'],
                       pid=child.pid, exitCode=exit_code, wallSeconds=wall,
                       receiptSha256=entry['receipt']['sha256'], sourceSha256=sources,
                       stdoutPath=str(stdout), stdoutSha256=digest(stdout),
                       claimAbsent=True, startedAbsent=True, deferralAbsent=True,
                       failureAbsent=True, resultAbsent=True, prefixEmptyAfter=True,
                       mode=decision['resourceMode'],
                       availableBytes=decision['memory']['availableBytes'],
                       reservedBytes=decision['reservedBytes'],
                       effectiveConcurrency=decision['effectiveConcurrency'])
            else:
                result_sha = digest(result) if result.exists() else None
                if exit_code or result_sha is None \
                        or (ROOT / 'failures' / current).exists() \
                        or (ROOT / 'deferrals' / current).exists():
                    problem = 'claimed deferral, CLI failure or missing exact-once result'
                else:
                    body = json.loads(result.read_bytes())
                    if body.get('validationRead') is not False \
                            or body.get('holdoutRead') is not False \
                            or body.get('memoizationOperationalSourceSha256') != sources \
                            or body.get('policyVersion') != 4:
                        problem = 'result scope/source/policy mismatch'
                state = 'failed' if problem else 'complete'
                record('finish', ordinal=index+1, attempt=attempt, task=entry['task'],
                       pid=child.pid, exitCode=exit_code, wallSeconds=wall,
                       receiptSha256=entry['receipt']['sha256'], sourceSha256=sources,
                       stdoutPath=str(stdout), stdoutSha256=digest(stdout),
                       resultPath=str(result), resultSha256=result_sha,
                       claimSha256=digest(claim) if claim.exists() else None,
                       solverStarted=marker.exists(),
                       failureExists=(ROOT / 'failures' / current).exists(),
                       deferralExists=(ROOT / 'deferrals' / current).exists(),
                       prefixEmptyAfter=prefix_empty(entry), problem=problem)
        except BaseException as error:
            state = 'failed'
            problem = 'completion audit error: ' + repr(error)
            record('audit_failure', task=entry['task'], attempt=attempt,
                   error=problem, traceback=traceback.format_exc())
        with cv:
            del active[index]
            outcomes[index] = state
            if problem:
                failure = failure or base(entry) + ': ' + problem
            elif state == 'complete':
                completed += 1
            cv.notify_all()

    try:
        record('restart', manifestPath=str(MANIFEST), manifestSha256=MANIFEST_SHA256,
               priorRunPath=str(prior), priorRunSha256=prior_sha,
               linkedPredecessorSha256=PREDECESSOR_SHA256, count=len(entries),
               watcherPID=watcher['pid'], watcherDeadlineUTC=deadline.isoformat(),
               controllerPID=os.getpid(), memoryMetric=policy.v3.MEMORY_METRIC_V4,
               controllerSourceSha256=digest(Path(__file__)))
        for index, entry in enumerate(entries):
            attempt = 0
            while True:
                with cv:
                    if failure:
                        break
                if not watcher_ok():
                    failure = 'observer expired or process identity changed'
                    record('stop', reason=failure)
                    break
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
                    record('resource_wait', ordinal=index+1, task=entry['task'],
                           mode=d['resourceMode'], availableBytes=d['memory']['availableBytes'],
                           reservedBytes=d['reservedBytes'],
                           effectiveConcurrency=d['effectiveConcurrency'],
                           pressureLevel=d['freshestPressure']['pressureLevel'])
                    with cv:
                        cv.wait(timeout=30)
                    continue
                for path, expected in launch['resourceSourceSha256'].items():
                    if digest(path) != expected:
                        raise ValueError('pinned source changed: ' + path)
                if not watcher_ok():
                    failure = 'observer invalid before CLI launch'
                    record('stop', reason=failure)
                    break
                verify(entry, linked)
                attempt += 1
                stdout = stdout_path(entry, attempt)
                fd = stdout.open('x')
                start = time.monotonic()
                try:
                    child = subprocess.Popen(entry['argv'], stdout=fd, stderr=subprocess.STDOUT,
                                             close_fds=True)
                except BaseException:
                    fd.close()
                    raise
                with cv:
                    active[index] = child
                    outcomes.pop(index, None)
                launches += 1
                record('launch', ordinal=index+1, attempt=attempt, task=entry['task'],
                       pid=child.pid, argv=entry['argv'],
                       receiptSha256=entry['receipt']['sha256'],
                       sourceSha256=launch['resourceSourceSha256'],
                       prefixInitiallyEmpty=True, preflightMode=decision['resourceMode'],
                       preflightAvailableBytes=decision['memory']['availableBytes'],
                       preflightMetric=decision['memory']['metric'],
                       stdoutPath=str(stdout), expectedResult=entry['expectedResult'],
                       currentGenerationClaim=claim_name(entry))
                threading.Thread(target=settle, args=(index, entry, attempt, child, fd, start,
                                                     launch['resourceSourceSha256'], stdout),
                                 daemon=True).start()
                claim = ROOT / 'claims' / claim_name(entry)
                while not claim.exists():
                    with cv:
                        if failure or outcomes.get(index) is not None:
                            break
                        cv.wait(timeout=1)  # Durable claim handshake, not fit-completion polling.
                if claim.exists():
                    record('claim_observed', ordinal=index+1, attempt=attempt,
                           task=entry['task'], claimSha256=digest(claim),
                           generation=1 if index == 0 else 0)
                    if child.poll() is not None:
                        with cv:
                            while outcomes.get(index) is None:
                                cv.wait()
                    break
                with cv:
                    if failure:
                        break
                    state = outcomes.get(index)
                if state != 'resource_wait':
                    failure = 'missing claim without genuine current-generation Deferred'
                    record('stop', reason=failure)
                    break
                with cv:
                    cv.wait(timeout=30)
            if failure:
                break
        with cv:
            while active:
                cv.wait()
        record('batch_end', launched=launches, completed=completed, total=len(entries),
               status='complete' if completed == len(entries) and failure is None else 'stopped',
               problem=failure, priorRunUnchanged=digest(prior) == prior_sha)
        if failure or completed != len(entries):
            raise SystemExit(2)
    except BaseException as error:
        if not isinstance(error, SystemExit):
            record('fatal', error=repr(error), traceback=traceback.format_exc(),
                   launched=launches, completed=completed)
        with cv:
            while active:
                cv.wait()
        raise
    finally:
        journal.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.self_test == args.run:
        parser.error('select exactly one of --self-test and --run')
    self_test() if args.self_test else run()
