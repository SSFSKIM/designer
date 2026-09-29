"""Concurrent M1 curvature dispatch after the serial controller's sealed boundary pause.

The serial controller (../restart-kernel-readmit-2/driver.py, PID 10224) blocked in
child.wait(), so no second fit could start however much capacity the v4 gate had. This
controller reuses the same sealed manifest, receipts, argv, validation and v4 gate, and
changes only the scheduling:

  * The live curvature-08 fit is ADOPTED from the immutable handoff snapshot by process
    identity (PID, start time, command), never by PID alone. It is not our child, so its
    end is observed as that identity leaving the PID (exit, zombie or reuse) and its
    outcome is audited from the scheduler's own claim/started/result files; no exit code
    is available or needed.
  * While fits run, a queued start is evaluated against the unchanged gate at most every
    30 s after a refusal, and at once after any capacity change. The gate alone decides
    how many fits run: running claims keep their reservations because the gate reads them
    from the claims directory, exactly as for the serial controller's own children.
  * A launched child is in HANDSHAKE until its current-generation solver-start marker
    exists. No admission is evaluated meanwhile: the child's own claim and pre-fit gate
    must not interleave with a preview for the next start (a duplicate dispatch, or a
    preview that turns the child's pre-fit check into a claimed no-fit deferral).
  * A no-claim CLI Deferred (the child's own claim-time gate refused, nothing written)
    returns the start to the head of the queue for a new attempt. Every other end without
    a clean exact-once result, a claimed no-fit deferral included, halts NEW dispatch:
    readmission needs a new sealed manifest. Running fits are never signalled; a halted
    controller keeps auditing them to their terminal before it stops.
  * Children start in their own session, so a signal to this controller's process group
    does not reach a fit. Any exception leaves every fit running and records them.

CLI (operational imports: /tmp/w39-g2-wgpu/bin/python -B -X pycache_prefix=FRESH_EMPTY_DIR):
  controller.py --full-test --manifest-sha256 SHA --handoff-sha256 SHA   (read-only)
  controller.py --run       --manifest-sha256 SHA --handoff-sha256 SHA
The synthetic suite is test_controller.py beside this file.
"""
import argparse
import collections
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback

HERE = Path(__file__).resolve().parent
STROKE = HERE.parents[2]
SERIAL = STROKE / 'execution-batches/M1/restart-kernel-readmit-2'
SERIAL_DRIVER = SERIAL / 'driver.py'
SERIAL_DRIVER_SHA256 = 'd914997a5995fd596b061ebb87d30b241cad72164fd6c1172008cc36291cb787'
HANDOFF = SERIAL / 'handoff-concurrent-1.json'
ADOPTED_TASK = ('M1', 'curvature', 8)
COMPLETED_TASKS = [('M1', 'curvature', i) for i in range(4, 8)]
PENDING_TASKS = [('M1', 'curvature', i) for i in range(9, 16)]
LIFECYCLE = ('claims', 'started', 'deferrals', 'failures')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_serial_driver():
    """The reviewed serial driver as a library: its validation, naming and CLI parser."""
    if digest(SERIAL_DRIVER) != SERIAL_DRIVER_SHA256:
        raise ValueError('serial driver source changed')
    spec = importlib.util.spec_from_file_location('m1_serial_readmit2_driver', SERIAL_DRIVER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


old = load_serial_driver()
Deferred = old.s.Deferred


def result_problem(launch, body):
    """The serial driver's result scope/source/policy check, unchanged."""
    if body.get('validationRead') is not False or body.get('holdoutRead') is not False \
            or body.get('memoizationOperationalSourceSha256') != launch['resourceSourceSha256'] \
            or body.get('policyVersion') != 4:
        return 'result scope/source/policy mismatch'
    return None


class Slot:
    """One fit this controller answers for: its own child, or the adopted one."""

    def __init__(self, entry, launch, pid, *, ordinal, attempt=None, proc=None, identity=None,
                 claim_sha256=None, stdout=None):
        self.entry, self.launch, self.pid, self.ordinal = entry, launch, pid, ordinal
        self.attempt, self.proc, self.identity = attempt, proc, identity
        self.claim_sha256, self.stdout = claim_sha256, stdout
        self.adopted = proc is None
        self.phase = 'fit' if self.adopted else 'handshake'
        self.start = time.monotonic()


def default_spawn(argv, stdout):
    return subprocess.Popen(argv, stdout=stdout, stderr=subprocess.STDOUT, close_fds=True,
                            start_new_session=True)


class Controller:
    def __init__(self, *, root, out, pending, adopted, verify, admit, identify, healthy,
                 journal, prefix_empty=old.prefix_empty, claim_name=old.claim_name,
                 parse_deferred=old.parse_cli_deferred, spawn=default_spawn,
                 admission_interval=30.0, poll_interval=5.0, clock=time.monotonic,
                 sleep=time.sleep):
        self.root, self.out = Path(root), Path(out)
        self.queue = collections.deque(pending)
        self.ordinals = {old.key(e): n for n, e in enumerate(pending, start=1)}
        self.slots = {}
        self.verify, self.admit, self.identify, self.healthy = verify, admit, identify, healthy
        self.record, self.prefix_empty, self.claim_name = journal, prefix_empty, claim_name
        self.parse_deferred, self.spawn = parse_deferred, spawn
        self.admission_interval, self.poll_interval = admission_interval, poll_interval
        self.clock, self.sleep = clock, sleep
        self.attempts = collections.Counter()
        self.launches = self.completed = 0
        self.halted = None
        self.next_admission = clock()
        for slot in adopted:
            self.slots[old.key(slot.entry)] = slot

    # Lifecycle files of an entry's CURRENT generation, and its exact-once result.
    def paths(self, entry):
        name = self.claim_name(entry)
        return {d: self.root / d / name for d in LIFECYCLE}, Path(entry['expectedResult'])

    def halt(self, reason):
        if self.halted is None:
            self.halted = reason
            self.record('halt', reason=reason, queued=[e['task'] for e in self.queue],
                        liveFits=self.live())

    def live(self):
        return [{'task': s.entry['task'], 'pid': s.pid, 'adopted': s.adopted, 'phase': s.phase}
                for s in self.slots.values()]

    def run(self):
        try:
            while True:
                if self.halted is None:
                    reason = self.healthy()
                    if reason:
                        self.halt(reason)
                self.poll()
                if self.halted is None and self.queue and self.clock() >= self.next_admission \
                        and not any(s.phase == 'handshake' for s in self.slots.values()):
                    self.try_admit()
                if not self.slots and (self.halted is not None or not self.queue):
                    break
                self.sleep(self.poll_interval)
        except BaseException as error:
            # Nothing is signalled: every fit keeps running and is named here.
            self.record('stop', error=repr(error), traceback=traceback.format_exc(),
                        launched=self.launches, completed=self.completed,
                        liveFitsLeftRunning=self.live(),
                        queued=[e['task'] for e in self.queue])
            raise
        if self.halted is not None:
            self.record('stop', reason=self.halted, launched=self.launches,
                        completed=self.completed, queued=[e['task'] for e in self.queue])
            raise RuntimeError('dispatch halted: ' + self.halted)
        self.record('batch_end', launched=self.launches, completed=self.completed,
                    status='complete')

    def try_admit(self):
        entry = self.queue[0]
        try:
            launch = self.verify(entry)
            decision = self.admit(launch)
        except Deferred as deferred:
            d = deferred.decision
            self.record('resource_wait', task=entry['task'], mode=d['resourceMode'],
                        availableBytes=d['memory']['availableBytes'],
                        reservedBytes=d['reservedBytes'],
                        effectiveConcurrency=d['effectiveConcurrency'],
                        pressureLevel=d['freshestPressure']['pressureLevel'],
                        liveFits=self.live())
            self.next_admission = self.clock() + self.admission_interval
            return
        except Exception as error:
            self.halt('admission step raised ' + repr(error))
            return
        try:
            reason = self.healthy()
            if reason:
                raise ValueError(reason)
            self.verify(entry)
        except Exception as error:
            self.halt('pre-launch recheck failed: ' + repr(error))
            return
        key = old.key(entry)
        self.attempts[key] += 1
        attempt = self.attempts[key]
        stdout = self.out / f'{old.base(entry)}.attempt-{attempt:03d}.stdout'
        with stdout.open('x') as fd:
            proc = self.spawn(entry['argv'], fd)
        self.queue.popleft()
        self.launches += 1
        slot = Slot(entry, launch, proc.pid, ordinal=self.ordinals[key], attempt=attempt,
                    proc=proc, stdout=stdout)
        self.slots[key] = slot
        self.record('launch', ordinal=slot.ordinal, attempt=attempt, task=entry['task'],
                    pid=proc.pid, argv=entry['argv'], receiptSha256=entry['receipt']['sha256'],
                    sourceSha256=launch['resourceSourceSha256'], prefixInitiallyEmpty=True,
                    preflightMode=decision['resourceMode'],
                    preflightAvailableBytes=decision['memory']['availableBytes'],
                    preflightMetric=decision['memory']['metric'],
                    preflightEffectiveConcurrency=decision['effectiveConcurrency'],
                    preflightModeConcurrencyLimit=decision.get('modeConcurrencyLimit'),
                    stdoutPath=str(stdout), expectedResult=entry['expectedResult'],
                    currentGenerationClaim=self.claim_name(entry), liveFits=self.live())

    def poll(self):
        for key, slot in list(self.slots.items()):
            if slot.adopted:
                current = self.identify(slot.pid)
                if current == slot.identity:
                    continue
                exit_code = None
                ended = {'observedIdentity': current}
            else:
                exit_code = slot.proc.poll()
                if exit_code is None:
                    if slot.phase == 'handshake':
                        self.handshake(slot)
                    continue
                ended = {}
            del self.slots[key]
            self.terminal(slot, exit_code, ended)

    def handshake(self, slot):
        lifecycle, _ = self.paths(slot.entry)
        if not lifecycle['claims'].exists():
            return
        claim = json.loads(lifecycle['claims'].read_bytes())
        if claim.get('pid') != slot.pid:
            self.halt(f"current-generation claim of {old.base(slot.entry)} is held by PID "
                      f"{claim.get('pid')}, not child {slot.pid}")
            slot.phase = 'foreign-claim'
            return
        if lifecycle['started'].exists():
            slot.phase = 'fit'
            self.record('solver_started', task=slot.entry['task'], attempt=slot.attempt,
                        pid=slot.pid, claimSha256=digest(lifecycle['claims']),
                        startedSha256=digest(lifecycle['started']), liveFits=self.live())
            self.next_admission = self.clock()

    def terminal(self, slot, exit_code, ended):
        entry = slot.entry
        lifecycle, result = self.paths(entry)
        present = {d: p.exists() for d, p in lifecycle.items()}
        wall = round(time.monotonic() - slot.start, 3)
        stdout_sha = digest(slot.stdout) if slot.stdout and slot.stdout.exists() else None
        common = dict(ordinal=slot.ordinal, attempt=slot.attempt, task=entry['task'],
                      pid=slot.pid, adopted=slot.adopted, exitCode=exit_code,
                      exitCodeSource='adopted: not our child, none observable' if slot.adopted
                      else 'Popen.poll', wallSeconds=wall,
                      receiptSha256=entry['receipt']['sha256'],
                      sourceSha256=slot.launch['resourceSourceSha256'],
                      stdoutPath=str(slot.stdout) if slot.stdout else None,
                      stdoutSha256=stdout_sha, **ended)
        if not slot.adopted and exit_code and not any(present.values()) \
                and not result.exists() and self.prefix_empty(entry):
            d = self.parse_deferred(slot.stdout.read_text(errors='replace'))
            if d is not None:
                self.record('cli_resource_wait', claimAbsent=True, startedAbsent=True,
                            deferralAbsent=True, failureAbsent=True, resultAbsent=True,
                            prefixEmptyAfter=True, mode=d['resourceMode'],
                            availableBytes=d['memory']['availableBytes'],
                            reservedBytes=d['reservedBytes'],
                            effectiveConcurrency=d['effectiveConcurrency'], **common)
                self.queue.appendleft(entry)
                self.next_admission = self.clock() + self.admission_interval
                return
        problem = claim = None
        if present['deferrals']:
            problem = 'claimed no-fit deferral; readmission needs a new sealed manifest'
        elif not slot.adopted and exit_code != 0:
            problem = 'CLI failure'
        elif not result.exists() or not present['claims'] or not present['started'] \
                or present['failures']:
            problem = 'failure or missing exact-once result'
        else:
            claim = json.loads(lifecycle['claims'].read_bytes())
            body = json.loads(result.read_bytes())
            if claim.get('pid') != slot.pid:
                problem = "claim is not this fit's process"
            elif slot.adopted and (claim.get('processIdentity') != slot.identity
                                   or digest(lifecycle['claims']) != slot.claim_sha256):
                problem = 'adopted claim identity or bytes changed'
            elif body.get('schedulerClaim') != claim:
                problem = 'result does not name this claim'
            else:
                problem = result_problem(slot.launch, body)
        self.record('finish', resultPath=str(result),
                    resultSha256=digest(result) if result.exists() else None,
                    claimSha256=digest(lifecycle['claims']) if present['claims'] else None,
                    solverStarted=present['started'], failureExists=present['failures'],
                    deferralExists=present['deferrals'], prefixEmptyAfter=self.prefix_empty(entry),
                    problem=problem, **common)
        self.next_admission = self.clock()  # Capacity freed: re-evaluate at once.
        if problem:
            self.halt(old.base(entry) + ': ' + problem)
        else:
            self.completed += 1


class Journal:
    """Append-only fsynced JSONL; the file is created exclusively, never overwritten."""

    def __init__(self, path):
        self.stream = Path(path).open('x', encoding='utf8')

    def __call__(self, kind, **fields):
        row = {'atUTC': dt.datetime.now(dt.timezone.utc).isoformat(), 'kind': kind, **fields}
        self.stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + '\n')
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def close(self):
        self.stream.close()


# ---- Production plan: sealed manifest + immutable handoff -> completed/adopted/pending ----

def read_manifest_after_boundary(expected_sha):
    """The serial driver's read_manifest, less the one check the boundary has since crossed.

    It refused any results/curvature-M1-start-04.json because generation 0 of start 04 was a
    no-fit deferral; the generation-1 readmission has since published that exact-once
    result (the handoff pins its bytes). The generation-zero claim still has no started or
    failure marker, and every other scope/order/linkage/completed check is unchanged.
    """
    if digest(old.MANIFEST) != expected_sha:
        raise ValueError('manifest hash changed')
    batch = json.loads(old.MANIFEST.read_bytes())
    entries = batch['entries'][5:]
    if batch['kind'] != 'STROKE_SEALED_START_BATCH' or batch['receiptVersion'] != 4 \
            or batch['memoryReader'] != 'scheduler_v3.kernel_memory' \
            or batch['validationRead'] is not False or batch['holdoutRead'] is not False \
            or len(batch['entries']) != 17 or [old.key(e) for e in entries] != [
                ('M1', 'curvature', i) for i in range(4, 16)]:
        raise ValueError('batch scope/order changed')
    linked = batch['linkedReadmission']
    predecessor = linked['predecessor']
    if linked['task'] != list(old.key(entries[0])) \
            or digest(predecessor['path']) != predecessor['sha256'] \
            or digest(linked['previousManifest']['path']) != linked['previousManifest']['sha256'] \
            or digest(batch['supersedes']['path']) != batch['supersedes']['sha256']:
        raise ValueError('linked predecessor or supersession changed')
    prior = json.loads(Path(predecessor['path']).read_bytes())
    if prior['kind'] != 'STROKE_NO_FIT_DEFERRAL' or prior['task'] != list(old.key(entries[0])) \
            or prior['generation'] != 0 or prior['solverStarted'] is not False \
            or digest(prior['claim']['path']) != prior['claim']['sha256']:
        raise ValueError('generation-zero no-fit evidence changed')
    if any((old.ROOT / d / 'curvature-M1-start-04.json').exists() for d in ('started', 'failures')):
        raise ValueError('original no-fit boundary crossed')
    for entry in batch['entries'][:5]:
        if digest(entry['expectedResult']) != old.FINISHED[old.key(entry)]:
            raise ValueError('completed result changed')
    return entries, linked


def plan(entries, handoff, *, root, verify_pending, identity_of_claim=None):
    """Split the sealed entries by the handoff; any disagreement fails closed.

    Returns (completed results, adopted Slot, pending entries in manifest order). A
    completed entry is skipped only when its result exists with the handoff's bytes; the
    adopted entry needs the handoff's receipt, claim, solver-start marker and identity to
    agree with each other and with the files; a pending entry passes the serial driver's
    own verify() (no lifecycle, empty prefix, receipt/argv/source pins).
    """
    by_key = {old.key(e): e for e in entries}
    order = [old.key(e) for e in entries]
    completed = [tuple(c['task']) for c in handoff['completed']]
    pending = [tuple(p['task']) for p in handoff['pending']]
    child = handoff['liveChild']
    if completed + [tuple(child['task'])] + pending != order:
        raise ValueError('handoff does not partition the sealed entries in order')
    done = []
    for item in handoff['completed']:
        entry = by_key[tuple(item['task'])]
        if item['result']['path'] != entry['expectedResult'] \
                or digest(item['result']['path']) != item['result']['sha256']:
            raise ValueError('completed result changed: ' + old.base(entry))
        done.append(item['result'])
    entry = by_key[tuple(child['task'])]
    name = old.claim_name(entry)
    receipt = entry['receipt']
    if child['receipt'] != receipt or digest(receipt['path']) != receipt['sha256'] \
            or child['expectedResult'] != entry['expectedResult'] \
            or child['claim']['path'] != str(root / 'claims' / name) \
            or child['solverStarted']['path'] != str(root / 'started' / name):
        raise ValueError('adopted child does not name its sealed entry')
    claim = json.loads(Path(child['claim']['path']).read_bytes())
    started = json.loads(Path(child['solverStarted']['path']).read_bytes())
    identity = child['processIdentity']
    if digest(child['claim']['path']) != child['claim']['sha256'] \
            or digest(child['solverStarted']['path']) != child['solverStarted']['sha256'] \
            or claim.get('pid') != child['pid'] or identity.get('pid') != child['pid'] \
            or claim.get('processIdentity') != identity \
            or started.get('processIdentity') != identity or started.get('pid') != child['pid'] \
            or claim.get('launch') != receipt or claim.get('task') != list(old.key(entry)) \
            or started.get('claim') != child['claim']:
        raise ValueError('adopted identity mismatch between handoff, claim and solver start')
    if any((root / d / name).exists() for d in ('deferrals', 'failures')):
        raise ValueError('adopted claim already settled without a result')
    launch = json.loads(Path(receipt['path']).read_bytes())
    if launch['task'] != entry['task'] or launch['receiptVersion'] != 4 \
            or launch['resourceSourceSha256'] != handoff['policySourceSha256']:
        raise ValueError('adopted receipt scope or source pins changed')
    for path, expected in launch['resourceSourceSha256'].items():
        if digest(path) != expected:
            raise ValueError('pinned source changed: ' + path)
    adopted = Slot(entry, launch, child['pid'], ordinal=order.index(old.key(entry)) + 1,
                   identity=identity, claim_sha256=child['claim']['sha256'],
                   stdout=SERIAL / f'{old.base(entry)}.attempt-001.stdout')
    waiting = []
    for item in handoff['pending']:
        entry = by_key[tuple(item['task'])]
        if item['receipt'] != entry['receipt'] or item['expectedResult'] != entry['expectedResult']:
            raise ValueError('pending entry disagrees with the sealed manifest')
        verify_pending(entry)
        waiting.append(entry)
    return done, adopted, waiting


def process_state(pid, command):
    """'gone', 'stopped' or 'running' for the process that holds PID with this command."""
    identity = old.s.process_identity(pid)
    if identity is None or identity['command'] != command:
        return 'gone'
    stat = subprocess.run(['/bin/ps', '-o', 'stat=', '-p', str(pid)], capture_output=True,
                          text=True, env={'LC_ALL': 'C'}).stdout.strip()
    return 'stopped' if stat.startswith('T') else 'gone' if stat.startswith('Z') \
        or not stat else 'running'


def production(manifest_sha, handoff_sha):
    entries, linked = read_manifest_after_boundary(manifest_sha)
    if digest(HANDOFF) != handoff_sha:
        raise ValueError('handoff snapshot hash changed')
    handoff = json.loads(HANDOFF.read_bytes())
    controller = handoff['controller']
    if handoff['kind'] != 'M1_CONCURRENT_ADOPTION_HANDOFF' \
            or handoff['schedulerRoot'] != str(old.ROOT) \
            or handoff['manifest'] != {'path': str(old.MANIFEST), 'sha256': manifest_sha} \
            or controller['source'] != {'path': str(SERIAL_DRIVER), 'sha256': SERIAL_DRIVER_SHA256} \
            or handoff.get('oldControllerResumeForbidden') is not True \
            or [tuple(c['task']) for c in handoff['completed']] != COMPLETED_TASKS \
            or tuple(handoff['liveChild']['task']) != ADOPTED_TASK \
            or [tuple(p['task']) for p in handoff['pending']] != PENDING_TASKS:
        raise ValueError('handoff scope changed')
    done, adopted, pending = plan(entries, handoff, root=old.ROOT,
                                 verify_pending=lambda e: old.verify(e, linked))
    return entries, linked, handoff, done, adopted, pending


def full_test(manifest_sha, handoff_sha):
    entries, _, handoff, done, adopted, pending = production(manifest_sha, handoff_sha)
    controller = handoff['controller']
    print(json.dumps({'kind': 'M1_CONCURRENT_CONTROLLER_FULL_PASS',
                      'manifestSha256': manifest_sha, 'handoffSha256': handoff_sha,
                      'completed': len(done), 'adoptedTask': adopted.entry['task'],
                      'adoptedIdentityLive': old.s.process_identity(adopted.pid) == adopted.identity,
                      'pending': [e['task'][2] for e in pending],
                      'oldController': process_state(controller['pid'], controller['command']),
                      'receiptSourcePrefixChecks': 'pass'}, sort_keys=True))


def run(manifest_sha, handoff_sha):
    entries, linked, handoff, done, adopted, pending = production(manifest_sha, handoff_sha)
    controller = handoff['controller']
    if process_state(controller['pid'], controller['command']) == 'running':
        raise ValueError('serial controller is running; it must stay stopped or be gone')
    watcher = old.s.record(json.loads(Path(entries[0]['receipt']['path']).read_bytes())[
        'pressureWatcher'])
    deadline = dt.datetime.fromisoformat(watcher['startedUTC']) + dt.timedelta(
        seconds=watcher['readings'] * watcher['intervalSeconds'])

    def healthy():
        if dt.datetime.now(dt.timezone.utc) >= deadline \
                or old.s.process_identity(watcher['pid']) != watcher['processIdentity']:
            return 'watcher expired or process identity changed'
        if process_state(controller['pid'], controller['command']) == 'running':
            return 'serial controller resumed; dispatch cannot have two owners'
        return None

    store = old.policy.PolicyStore(old.ROOT)
    metric = old.policy.v3.MEMORY_METRIC_V4

    def admit(launch):
        try:
            with store.locked():
                decision = store.admission(launch, os.getpid(), old.s.alive,
                                           old.policy.v3.kernel_memory, old.s.process_rss)
        except Deferred as deferred:
            if deferred.decision['memory']['metric'] != metric:
                raise ValueError('wrong metric disguised as resource wait')
            raise
        if decision['memory']['metric'] != metric:
            raise ValueError('wrong preview memory reader')
        return decision

    def terminate(signum, frame):
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, terminate)
    journal = Journal(HERE / 'run.jsonl')
    try:
        journal('restart', manifestPath=str(old.MANIFEST), manifestSha256=manifest_sha,
                handoffPath=str(HANDOFF), handoffSha256=handoff_sha,
                serialJournalSha256=digest(controller['journalPath']),
                controllerPID=os.getpid(), controllerSourceSha256=digest(Path(__file__)),
                serialDriverSha256=SERIAL_DRIVER_SHA256, completed=done,
                adopted={'task': adopted.entry['task'], 'pid': adopted.pid,
                         'processIdentity': adopted.identity,
                         'currentIdentity': old.s.process_identity(adopted.pid),
                         'claimSha256': adopted.claim_sha256},
                pending=[e['task'] for e in pending], watcherPID=watcher['pid'],
                watcherDeadlineUTC=deadline.isoformat(), memoryMetric=metric,
                scheduling='dynamic v4 gate; 30 s re-evaluation after refusal; one handshake '
                           'at a time; adopted fit audited by identity')
        Controller(root=old.ROOT, out=HERE, pending=pending, adopted=[adopted],
                   verify=lambda e: old.verify(e, linked), admit=admit,
                   identify=old.s.process_identity, healthy=healthy, journal=journal).run()
    finally:
        journal.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--full-test', action='store_true')
    action.add_argument('--run', action='store_true')
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--handoff-sha256', required=True)
    args = parser.parse_args()
    (full_test if args.full_test else run)(args.manifest_sha256, args.handoff_sha256)
