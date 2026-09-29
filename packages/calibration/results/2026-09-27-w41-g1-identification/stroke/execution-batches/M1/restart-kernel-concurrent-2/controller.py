"""Concurrent M1 curvature dispatch after curvature-09's linked no-fit readmission.

The first concurrent controller (../restart-kernel-concurrent-1/controller.py) audited the
adopted curvature-08 fit and then halted: curvature-09 generation 0 was claimed and its
fresh pre-fit gate wrote a no-fit deferral. The parent sealed a generation-1 receipt for
09 and a new manifest (remaining-batch-M1-kernel-readmit-3.json); the operator's closed
boundary snapshot pins 08's settled claim/start/result, 09's generation-0 claim/deferral,
both earlier controllers gone and 10-15 untouched.

This entry reuses that controller's scheduling engine, loaded by SHA-256 and unchanged:
dynamic v4 admission re-evaluated every 30 s after a refusal and at once after a capacity
change, one handshake at a time until the solver-start marker, no-claim CLI Deferred
retries, halt-and-drain on every other unclean end, children in their own session. What is
new is only the plan the engine is given:

  * No adopted fit: the live list starts empty.
  * Generation-aware naming. The serial driver's claim_name and verify hard-code the
    generation-1 readmission of curvature-04; here the generation-1 task is read from the
    sealed manifest's linkedReadmission (curvature-09), so its lifecycle files are
    curvature-M1-start-09.readmit-01.json while its exact-once result keeps the task name
    curvature-M1-start-09.json. 10-15 stay generation 0.
  * Completed results are checked by hash: device-15 and curvature 00-03 against the
    serial driver's FINISHED table, 04-07 against the first handoff, 08 against the closed
    boundary (with its claim and solver-start bytes and result-to-claim linkage).

CLI (operational imports: /tmp/w39-g2-wgpu/bin/python -B -X pycache_prefix=FRESH_EMPTY_DIR):
  controller.py --full-test --manifest-sha256 SHA --boundary-sha256 SHA   (read-only)
  controller.py --run       --manifest-sha256 SHA --boundary-sha256 SHA
The synthetic suite is test_controller.py beside this file.
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal

HERE = Path(__file__).resolve().parent
STROKE = HERE.parents[2]
BATCHES = STROKE / 'execution-batches/M1'
ENGINE = BATCHES / 'restart-kernel-concurrent-1/controller.py'
ENGINE_SHA256 = 'fc768f12deb46c60ed9b514135b67d7875281b7b5fb0468979b7965b5ec5488e'
MANIFEST = STROKE / 'remaining-batch-M1-kernel-readmit-3.json'
PREVIOUS_MANIFEST = STROKE / 'remaining-batch-M1-kernel-readmit-2.json'
BOUNDARY = BATCHES / 'restart-kernel-concurrent-1/closed-readmission-boundary-1.json'
HANDOFF_1 = BATCHES / 'restart-kernel-readmit-2/handoff-concurrent-1.json'
HANDOFF_1_SHA256 = 'a7700f3b347759eab5eac6caa0ec42d2198c9404e14d72b619310b31041757a4'
LINKED_TASK = ('M1', 'curvature', 9)
COMPLETED_BY_HANDOFF_1 = [('M1', 'curvature', i) for i in range(4, 8)]
SETTLED_TASK = ('M1', 'curvature', 8)
PENDING_TASKS = [('M1', 'curvature', i) for i in range(9, 16)]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_engine():
    if digest(ENGINE) != ENGINE_SHA256:
        raise ValueError('concurrent engine source changed')
    spec = importlib.util.spec_from_file_location('m1_concurrent_engine_1', ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


engine = load_engine()
old = engine.old
ROOT = old.ROOT


def claim_name(entry, linked_task=LINKED_TASK):
    """Current-generation lifecycle name; the result keeps old.result_name (task name)."""
    return old.base(entry) + ('.readmit-01.json' if old.key(entry) == linked_task else '.json')


def verify(entry, linked, *, root=ROOT, stroke=STROKE):
    """The serial driver's verify with the linked generation read from the manifest.

    Unchanged: receipt hash/task/version, argv shape and pycache pin, watcher epoch, an
    unused current generation with an absent result and empty prefix, every source pin.
    Changed: only the linked task carries the deferred predecessor, and its current
    generation is readmit-01, so 09's settled generation-0 files do not count as use.
    """
    ref = entry['receipt']
    launch = json.loads(Path(ref['path']).read_bytes())
    if digest(ref['path']) != ref['sha256'] or launch['task'] != entry['task'] \
            or launch['receiptVersion'] != 4:
        raise ValueError('receipt changed: ' + old.base(entry))
    linked_task = tuple(linked['task'])
    predecessor = linked['predecessor'] if old.key(entry) == linked_task else None
    if launch.get('deferredPredecessor') != predecessor:
        raise ValueError('linked predecessor mismatch: ' + old.base(entry))
    argv = entry['argv']
    if argv[:3] != ['/tmp/w39-g2-wgpu/bin/python', '-B', '-X'] \
            or argv[4:8] != [str(stroke / 'scheduler/memo_runner_v3.py'), '--root', str(root),
                             '--receipt'] \
            or argv[8:] != [ref['path'], '--sha256', ref['sha256']] \
            or launch['operationalImportPolicy']['pycachePrefix'] != argv[3].split('=', 1)[1]:
        raise ValueError('sealed argv changed: ' + old.base(entry))
    if launch['pressureWatcher']['path'] != str(stroke / 'scheduler-pressure-watcher-2.json'):
        raise ValueError('watcher epoch changed')
    current = claim_name(entry, linked_task)
    if Path(entry['expectedResult']).exists() or not old.prefix_empty(entry) \
            or any((root / d / current).exists() for d in engine.LIFECYCLE):
        raise ValueError('current generation already used: ' + current)
    for path, expected in launch['resourceSourceSha256'].items():
        if digest(path) != expected:
            raise ValueError('pinned source changed: ' + path)
    return launch


def read_manifest(expected_sha):
    if digest(MANIFEST) != expected_sha:
        raise ValueError('manifest hash changed')
    batch = json.loads(MANIFEST.read_bytes())
    entries = batch['entries'][5:]
    if batch['kind'] != 'STROKE_SEALED_START_BATCH' or batch['receiptVersion'] != 4 \
            or batch['memoryReader'] != 'scheduler_v3.kernel_memory' \
            or batch['validationRead'] is not False or batch['holdoutRead'] is not False \
            or batch['automaticRetryAfterSolverStart'] is not False \
            or len(batch['entries']) != 17 or [old.key(e) for e in entries] != [
                ('M1', 'curvature', i) for i in range(4, 16)]:
        raise ValueError('batch scope/order changed')
    linked = batch['linkedReadmission']
    predecessor = linked['predecessor']
    if tuple(linked['task']) != LINKED_TASK \
            or linked['previousManifest']['path'] != str(PREVIOUS_MANIFEST) \
            or digest(PREVIOUS_MANIFEST) != linked['previousManifest']['sha256'] \
            or predecessor['path'] != str(ROOT / 'deferrals' / 'curvature-M1-start-09.json') \
            or digest(predecessor['path']) != predecessor['sha256'] \
            or digest(batch['supersedes']['path']) != batch['supersedes']['sha256']:
        raise ValueError('linked predecessor or supersession changed')
    for history in batch['linkedReadmissionHistory']:
        for ref in (history['predecessor'], history['previousManifest']):
            if digest(ref['path']) != ref['sha256']:
                raise ValueError('linked readmission history changed')
    # Only the linked task's entry may differ from the manifest this one supersedes.
    previous = json.loads(PREVIOUS_MANIFEST.read_bytes())['entries']
    changed = [old.key(b) for a, b in zip(previous, batch['entries']) if a != b]
    if changed != [LINKED_TASK] or len(previous) != 17:
        raise ValueError('manifest changed more than the linked readmission')
    prior = json.loads(Path(predecessor['path']).read_bytes())
    if prior['kind'] != 'STROKE_NO_FIT_DEFERRAL' or tuple(prior['task']) != LINKED_TASK \
            or prior['generation'] != 0 or prior['solverStarted'] is not False \
            or prior['claim']['path'] != str(ROOT / 'claims' / 'curvature-M1-start-09.json') \
            or digest(prior['claim']['path']) != prior['claim']['sha256']:
        raise ValueError('generation-zero no-fit evidence changed')
    if any((ROOT / d / 'curvature-M1-start-09.json').exists() for d in ('started', 'failures',
                                                                        'results')):
        raise ValueError('generation-zero no-fit boundary crossed')
    for entry in batch['entries'][:5]:
        if digest(entry['expectedResult']) != old.FINISHED[old.key(entry)]:
            raise ValueError('completed result changed')
    return entries, linked


def gone(pid, marker):
    """True unless the process at PID is still the named controller (command contains marker)."""
    identity = old.s.process_identity(pid)
    return identity is None or marker not in identity['command']


def check_completed(entries, boundary, handoff):
    by_key = {old.key(e): e for e in entries}
    done = []
    if [tuple(c['task']) for c in handoff['completed']] != COMPLETED_BY_HANDOFF_1:
        raise ValueError('first handoff completed scope changed')
    for item in handoff['completed']:
        entry = by_key[tuple(item['task'])]
        if item['result']['path'] != entry['expectedResult'] \
                or digest(item['result']['path']) != item['result']['sha256']:
            raise ValueError('completed result changed: ' + old.base(entry))
        done.append(item['result'])
    entry = by_key[SETTLED_TASK]
    settled = boundary['completed08']
    name = claim_name(entry)
    expected = {'claims': str(ROOT / 'claims' / name), 'started': str(ROOT / 'started' / name),
                'results': entry['expectedResult']}
    if {k: v['path'] for k, v in settled.items()} != expected \
            or any(digest(v['path']) != v['sha256'] for v in settled.values()) \
            or any((ROOT / d / name).exists() for d in ('deferrals', 'failures')):
        raise ValueError('curvature-08 settlement changed')
    claim = json.loads(Path(settled['claims']['path']).read_bytes())
    body = json.loads(Path(settled['results']['path']).read_bytes())
    launch = json.loads(Path(entry['receipt']['path']).read_bytes())
    if claim.get('launch') != entry['receipt'] or body.get('schedulerClaim') != claim \
            or engine.result_problem(launch, body) is not None:
        raise ValueError('curvature-08 result does not settle its sealed claim')
    done.append(settled['results'])
    return done


def production(manifest_sha, boundary_sha):
    entries, linked = read_manifest(manifest_sha)
    if digest(BOUNDARY) != boundary_sha:
        raise ValueError('boundary snapshot hash changed')
    if digest(HANDOFF_1) != HANDOFF_1_SHA256:
        raise ValueError('first handoff changed')
    boundary = json.loads(BOUNDARY.read_bytes())
    handoff = json.loads(HANDOFF_1.read_bytes())
    by_key = {old.key(e): e for e in entries}
    serial, first = boundary['oldSerialController'], boundary['concurrentController']
    if boundary['kind'] != 'M1_CLOSED_CONCURRENT_READMISSION_BOUNDARY' \
            or boundary['schedulerRoot'] != str(ROOT) \
            or boundary['manifest'] != {'path': str(MANIFEST), 'sha256': manifest_sha} \
            or boundary['noFit09']['deferrals'] != linked['predecessor'] \
            or digest(boundary['noFit09']['claims']['path']) != boundary['noFit09']['claims']['sha256'] \
            or boundary['noFit09SolverStarted'] is not False \
            or boundary['linked09Receipt'] != by_key[LINKED_TASK]['receipt'] \
            or boundary['readmit09LifecycleAbsent'] is not True \
            or serial['pid'] != 10224 or serial['terminatedWithoutResume'] is not True \
            or serial['currentIdentity'] is not None \
            or first['pid'] != 81463 or first['currentIdentity'] is not None \
            or first['source'] != {'path': str(ENGINE), 'sha256': ENGINE_SHA256} \
            or [tuple(p['task']) for p in boundary['pending']] != PENDING_TASKS[1:] \
            or any(p['receipt'] != by_key[tuple(p['task'])]['receipt']
                   for p in boundary['pending']):
        raise ValueError('boundary scope changed')
    if not gone(serial['pid'], str(engine.SERIAL_DRIVER)) or not gone(first['pid'], str(ENGINE)):
        raise ValueError('an earlier controller is live again')
    # read_manifest has already checked these five against the serial FINISHED table.
    done = [{'path': e['expectedResult'], 'sha256': old.FINISHED[old.key(e)]}
            for e in json.loads(MANIFEST.read_bytes())['entries'][:5]]
    done += check_completed(entries, boundary, handoff)
    pending = [by_key[k] for k in PENDING_TASKS]
    for entry in pending:
        verify(entry, linked)
    return entries, linked, boundary, done, pending


def full_test(manifest_sha, boundary_sha):
    entries, linked, _, done, pending = production(manifest_sha, boundary_sha)
    print(json.dumps({'kind': 'M1_CONCURRENT_READMIT3_FULL_PASS',
                      'manifestSha256': manifest_sha, 'boundarySha256': boundary_sha,
                      'engineSha256': ENGINE_SHA256, 'completed': len(done),
                      'liveFits': [],
                      'pending': [[e['task'][2], claim_name(e)] for e in pending],
                      'linkedResult': old.result_name(pending[0]),
                      'receiptSourcePrefixChecks': 'pass'}, sort_keys=True))


def run(manifest_sha, boundary_sha):
    entries, linked, boundary, done, pending = production(manifest_sha, boundary_sha)
    watcher = old.s.record(json.loads(Path(pending[0]['receipt']['path']).read_bytes())[
        'pressureWatcher'])
    deadline = dt.datetime.fromisoformat(watcher['startedUTC']) + dt.timedelta(
        seconds=watcher['readings'] * watcher['intervalSeconds'])
    serial_pid, first_pid = boundary['oldSerialController']['pid'], boundary['concurrentController']['pid']

    def healthy():
        if dt.datetime.now(dt.timezone.utc) >= deadline \
                or old.s.process_identity(watcher['pid']) != watcher['processIdentity']:
            return 'watcher expired or process identity changed'
        if not gone(serial_pid, str(engine.SERIAL_DRIVER)) or not gone(first_pid, str(ENGINE)):
            return 'an earlier controller is live again; dispatch cannot have two owners'
        return None

    store = old.policy.PolicyStore(ROOT)
    metric = old.policy.v3.MEMORY_METRIC_V4

    def admit(launch):
        try:
            with store.locked():
                decision = store.admission(launch, os.getpid(), old.s.alive,
                                           old.policy.v3.kernel_memory, old.s.process_rss)
        except engine.Deferred as deferred:
            if deferred.decision['memory']['metric'] != metric:
                raise ValueError('wrong metric disguised as resource wait')
            raise
        if decision['memory']['metric'] != metric:
            raise ValueError('wrong preview memory reader')
        return decision

    def terminate(signum, frame):
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, terminate)
    journal = engine.Journal(HERE / 'run.jsonl')
    try:
        journal('restart', manifestPath=str(MANIFEST), manifestSha256=manifest_sha,
                boundaryPath=str(BOUNDARY), boundarySha256=boundary_sha,
                handoffPath=str(HANDOFF_1), handoffSha256=HANDOFF_1_SHA256,
                controllerPID=os.getpid(), controllerSourceSha256=digest(Path(__file__)),
                engineSha256=ENGINE_SHA256, completed=done, liveFits=[],
                pending=[{'task': e['task'], 'currentGenerationClaim': claim_name(e),
                          'result': e['expectedResult']} for e in pending],
                linkedPredecessor=linked['predecessor'], watcherPID=watcher['pid'],
                watcherDeadlineUTC=deadline.isoformat(), memoryMetric=metric,
                scheduling='dynamic v4 gate; 30 s re-evaluation after refusal; one handshake '
                           'at a time; empty initial live list')
        engine.Controller(root=ROOT, out=HERE, pending=pending, adopted=[],
                          verify=lambda e: verify(e, linked), admit=admit,
                          identify=old.s.process_identity, healthy=healthy, journal=journal,
                          claim_name=claim_name).run()
    finally:
        journal.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--full-test', action='store_true')
    action.add_argument('--run', action='store_true')
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--boundary-sha256', required=True)
    args = parser.parse_args()
    (full_test if args.full_test else run)(args.manifest_sha256, args.boundary_sha256)
