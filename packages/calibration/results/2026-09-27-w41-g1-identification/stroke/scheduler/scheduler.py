"""One-shot stroke scheduling after an explicit, hash-pinned ownership handoff.

This is a local filesystem protocol, not a queue service. The parent supplies a
single roster/root, stopped-owner receipts and per-start launch receipts. A claim
is permanent even if its process dies. Only two starts can run again: the OLD
static runner's explicitly recorded aborted start, and a claim refused at its
pre-fit memory check before its durable solver-start marker, which a new parent
launch must name as its predecessor. Nothing here stops a process or retries work.
Run --help for commands; see interface.txt for receipt fields and memory semantics.
"""
import argparse
import contextlib
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import tempfile
import time
import uuid

REVISION = 'd35b4cbf43f1fcdda55063b3b8e0fa178d720a78'
PROOF = Path('/Users/new/vitrea-w41/pre-w41-proof')
STROKE = Path(__file__).resolve().parent.parent
GIB = 1024 ** 3
MEMORY_METRIC = 'macOS (vm_stat Pages free + Pages inactive) * page size; reclaimable-headroom estimate'
RSS_OBSERVATION = 'STROKE_RSS_OBSERVATION'
NO_FIT_DEFERRAL = 'STROKE_NO_FIT_DEFERRAL'
SOLVER_START = 'STROKE_SOLVER_START'


class Deferred(RuntimeError):
    """No new fit is admitted; ongoing fits are never interrupted."""


def now():
    return datetime.now(timezone.utc).isoformat()


def pinned(reference):
    if not isinstance(reference, dict) or not Path(reference['path']).is_absolute():
        raise ValueError('an absolute, hash-pinned artifact is required')
    raw = Path(reference['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != reference['sha256']:
        raise ValueError('artifact hash changed: ' + reference['path'])
    return raw


def record(reference):
    return json.loads(pinned(reference))


def verify_sources(sources, required):
    if any(str(path) not in sources for path in required):
        raise ValueError('execution receipt does not pin required scope/fitter/helper sources')
    for path, digest in sources.items():
        pinned({'path': path, 'sha256': digest})


def immutable(path, value):
    """Publish complete bytes with an atomic no-overwrite hard link, then fsync."""
    raw = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    fd, temporary = tempfile.mkstemp(prefix='.publishing-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(temporary)


def task_tuple(task):
    if not isinstance(task, (list, tuple)) or len(task) != 3:
        raise ValueError('task must be [family, geometry, originalIndex]')
    family, geometry, index = task
    if family not in ('M1', 'M2') or geometry not in ('device', 'css', 'curvature') \
            or type(index) is not int or not 0 <= index < 16:
        raise ValueError('invalid original task')
    return tuple(task)


def filename(task):
    family, geometry, index = task_tuple(task)
    return f'{geometry}-{family}-start-{index:02d}.json'


def claim_filename(task, generation):
    # Generation 0 keeps the original claim name; a linked re-admission after a
    # no-fit deferral is a NEW claim beside it, never a rewrite of the old one.
    base = filename(task)
    return base if generation == 0 else f'{base[:-5]}.readmit-{generation:02d}.json'


def claim_name(claim):
    return claim_filename(claim['task'], claim.get('generation', 0))


def tasks(partition):
    return [(family, geometry, index) for family in ('M1', 'M2')
            for geometry in ('device', 'css', 'curvature')
            for index in range(partition, 16, 3)]


def validate_result(result, task):
    family, geometry, index = task_tuple(task)
    if result['family'] != family or result['cssWidth'] != (geometry == 'css') \
            or result['curvature'] != (geometry == 'curvature') \
            or len(result['starts']) != 1 or result['starts'][0]['startIndex'] != index:
        raise ValueError('result changed original task identity')
    if result['fittedEndpoints'] != (['light-inactive'] if family == 'M1' else
                                     ['light-inactive', 'dark-inactive']):
        raise ValueError('result changed endpoint scope')


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def process_rss(pid):
    # ps reports KiB on macOS. A disappearing process merely makes this check
    # defer; the next explicitly requested invocation can take a fresh snapshot.
    raw = subprocess.check_output(['/bin/ps', '-o', 'rss=', '-p', str(pid)], text=True)
    return int(raw.strip()) * 1024


def parse_memory(vm_stat, pressure):
    page = int(re.search(r'page size of (\d+) bytes', vm_stat)[1])
    free = int(re.search(r'^Pages free:\s+(\d+)\.', vm_stat, re.M)[1])
    inactive = int(re.search(r'^Pages inactive:\s+(\d+)\.', vm_stat, re.M)[1])
    return {'availableBytes': page * (free + inactive), 'pressureLevel': int(pressure.strip()),
            'pageSizeBytes': page, 'freePages': free, 'inactivePages': inactive,
            'metric': MEMORY_METRIC, 'sampledUTC': now()}


def mac_memory():
    return parse_memory(subprocess.check_output(['/usr/bin/vm_stat'], text=True),
        subprocess.check_output(['/usr/sbin/sysctl', '-n',
                                 'kern.memorystatus_vm_pressure_level'], text=True))


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def initialize(self, reference):
        roster = record(reference)
        if roster['kind'] != 'STROKE_ROSTER' or roster['schedulerRoot'] != str(self.root):
            raise ValueError('roster must authorize this exact scheduler root')
        owners = roster['oldOwners']
        if sorted(o['partition'] for o in owners) != [0, 1, 2] \
                or len({o['pid'] for o in owners}) != 3 \
                or len({o['taskId'] for o in owners}) != 3 \
                or len({o['outputRoot'] for o in owners}) != 3:
            raise ValueError('one unique old owner per modulo-three partition required')
        for owner in owners:
            if type(owner['pid']) is not int or owner['pid'] <= 0 or not owner['taskId']:
                raise ValueError('positive owner PID and task identity required')
            output = Path(owner['outputRoot'])
            if not output.is_absolute() or str(output.resolve()) != str(output):
                raise ValueError('old output root must be canonical and absolute')
            if Path(owner['execution']['path']) != output / 'execution.json':
                raise ValueError('old execution artifact must belong to this owner')
            execution = record(owner['execution'])
            p = owner['partition']
            if execution['partition'] != p or execution['indices'] != list(range(p, 16, 3)) \
                    or execution['seed'] != 4100 or execution['heldRevision'] != REVISION:
                raise ValueError('old queue changed original starts or sealed revision')
        self.root.mkdir(exist_ok=False)
        for name in ('handoffs', 'claims', 'results', 'failures', 'admissions', 'deferrals',
                     'started'):
            (self.root / name).mkdir()
        (self.root / '.lock').touch(exist_ok=False)
        immutable(self.root / 'roster.json', reference)

    @contextlib.contextmanager
    def locked(self):
        with (self.root / '.lock').open('r+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                for name in ('deferrals', 'started'):
                    (self.root / name).mkdir(exist_ok=True)
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def roster(self):
        reference = json.loads((self.root / 'roster.json').read_text())
        roster = record(reference)
        if roster['schedulerRoot'] != str(self.root):
            raise ValueError('scheduler root changed')
        return reference, roster

    def release(self, reference):
        release = record(reference)
        if release['kind'] != 'CAPTURESRELEASE' or release['schedulerRoot'] != str(self.root) \
                or type(release['maxConcurrency']) is not int or release['maxConcurrency'] < 1:
            raise ValueError('explicit capture release for this root required')
        return release

    def validate_handoff(self, reference, alive):
        handoff = record(reference)
        roster_ref, roster = self.roster()
        p = handoff['partition']
        if type(p) is not int or p not in range(3) or handoff['kind'] != 'STROKE_HANDOFF' \
                or handoff['rosterSha256'] != roster_ref['sha256']:
            raise ValueError('handoff does not name the registered partition')
        owner = next(o for o in roster['oldOwners'] if o['partition'] == p)
        if handoff['oldPid'] != owner['pid'] or handoff['oldTaskId'] != owner['taskId']:
            raise ValueError('handoff old owner identity changed')
        if alive(owner['pid']):
            raise ValueError('old owner is still live; ownership cannot transfer')
        self.release(handoff['captureRelease'])
        pinned(handoff['direction'])
        if datetime.fromisoformat(handoff['stoppedUTC']).tzinfo is None:
            raise ValueError('stop time requires a timezone')
        record(owner['execution'])
        ordered = tasks(p)
        completed = [task_tuple(c['task']) for c in handoff['completed']]
        if completed != ordered[:len(completed)]:
            raise ValueError('completed checkpoints must be the old queue prefix')
        boundary = tuple(handoff['boundaryTask']) if handoff['boundaryTask'] else None
        if boundary != (completed[-1] if completed else None):
            raise ValueError('boundary must identify the last completed original start')
        output = Path(owner['outputRoot'])
        for entry in handoff['completed']:
            if Path(entry['artifact']['path']) != output / filename(entry['task']):
                raise ValueError('checkpoint belongs to a different old owner')
            validate_result(record(entry['artifact']), entry['task'])
        actual = {p.name for p in output.glob('*-start-*.json')}
        if actual != {filename(task) for task in completed}:
            raise ValueError('unlisted or missing old checkpoint conflicts with handoff')
        aborted = handoff['aborted']
        if len(aborted) > 1:
            raise ValueError('one old sequential worker can abort at most one start')
        for entry in aborted:
            if len(completed) == len(ordered) or task_tuple(entry['task']) != ordered[len(completed)] \
                    or entry['label'] != 'aborted' or entry['neverScored'] is not True \
                    or not entry['evidence']:
                raise ValueError('aborted evidence must name only the next uncompleted start')
            for evidence in entry['evidence']:
                pinned(evidence)
        excluded = []
        for entry in handoff['excluded']:
            task = task_tuple(entry['task'])
            if task not in ordered or task in completed or task[1] != 'css' or task in excluded:
                raise ValueError('only uncompleted CSS tasks may be certified excluded')
            pinned(entry['certificate'])
            pinned(entry['review'])
            excluded.append(task)
        return handoff, [t for t in ordered if t not in completed and t not in excluded]

    def transfer(self, reference, *, alive=alive):
        with self.locked():
            handoff, remaining = self.validate_handoff(reference, alive)
            immutable(self.root / 'handoffs' / f"{handoff['partition']}.json", reference)
            return {'remaining': remaining, 'handoffSha256': reference['sha256']}

    def admission(self, launch, pid, alive, memory, rss, *, own_claim=None):
        try:
            return self._admission(launch, pid, alive, memory, rss, own_claim=own_claim)
        except Deferred:
            raise
        except Exception as error:
            immutable(self.root / 'admissions' / f'{uuid.uuid4().hex}.json',
                      {'sampledUTC': now(), 'task': launch.get('task'), 'pid': pid,
                       'admitted': False, 'error': repr(error)})
            raise

    def _admission(self, launch, pid, alive, memory, rss, *, own_claim=None):
        _, roster = self.roster()
        release = self.release(launch['captureRelease'])
        cap = launch['maxConcurrency']
        if type(cap) is not int or not 1 <= cap <= release['maxConcurrency']:
            raise ValueError('concurrency cap exceeds explicit capture release authority')
        peak = record(launch['peakEvidence'])
        measured = peak['largestObservedPeakRSSBytes']
        if peak['kind'] != 'STROKE_PEAK_RSS' or type(measured) is not int or measured <= 0 \
                or not peak['samples'] or measured != max(s['peakRSSBytes'] for s in peak['samples']):
            raise ValueError('measured wave fit peak RSS evidence required')
        for sample in peak['samples']:
            if type(sample['peakRSSBytes']) is not int or sample['peakRSSBytes'] <= 0 \
                    or not sample['source'] or not sample['sampledUTC'] or sample['pid'] <= 0:
                raise ValueError('peak evidence must identify its measurements')
        for evidence in peak.get('evidence', []):
            pinned(evidence)
        for key in ('reservationBytes', 'oldWorkerReservationBytes'):
            if type(launch[key]) is not int or launch[key] < measured:
                raise ValueError('reservation is below measured wave peak RSS')
        processes = []
        for owner in roster['oldOwners']:
            if alive(owner['pid']):
                processes.append({'pid': owner['pid'], 'owner': f"old-{owner['partition']}",
                                  'peakBytes': launch['oldWorkerReservationBytes']})
        # Every valid RSS reading any earlier admission took (refused, failed or
        # pre-fit included) stays in the high-water: a fit whose RSS later falls
        # can regrow to what it was already seen to hold.
        historical_peaks = [measured] + self.observed_rss()
        for path in sorted((self.root / 'results').glob('*.json')):
            result = json.loads(path.read_text())
            historical_peaks.append(result['peakRSSBytes'])
        for path in sorted((self.root / 'claims').glob('*.json')):
            claim = json.loads(path.read_text())
            historical_peaks.append(claim['prospectivePeakBytes'])
            if own_claim is not None and claim_name(claim) == claim_name(own_claim):
                continue
            if alive(claim['pid']):
                processes.append({'pid': claim['pid'], 'owner': filename(claim['task']),
                                  'peakBytes': claim['reservationBytes']})
        if pid in [p['pid'] for p in processes] or len({p['pid'] for p in processes}) != len(processes):
            raise ValueError('one process cannot own multiple simultaneous slots')
        # Before the fit, preparation's own RSS is already resident; reserve only
        # its remaining peak. At the initial claim reserve the entire new peak.
        own = {'pid': pid, 'owner': claim_name(own_claim) if own_claim else filename(launch['task'])}
        sampled = processes + ([own] if own_claim is not None else [])
        readings = []
        try:
            for process in sampled:
                process['rssBytes'] = rss(process['pid']) if rss else 0
                if type(process['rssBytes']) is not int or process['rssBytes'] < 0:
                    raise ValueError('invalid process RSS reading')
                if rss:
                    readings.append({key: process[key] for key in ('pid', 'owner', 'rssBytes')})
        finally:
            # Published before the memory read and before any refusal, still under
            # the allocation lock, so a later failure cannot forget a valid reading.
            if readings:
                immutable(self.root / 'admissions' / f'rss-{uuid.uuid4().hex}.json',
                          {'kind': RSS_OBSERVATION, 'sampledUTC': now(), 'task': launch['task'],
                           'source': '/bin/ps -o rss= KiB * 1024', 'samples': readings})
        own_rss = own.get('rssBytes', 0)
        observed_peak = max(historical_peaks + [p['rssBytes'] for p in sampled])
        for process in processes:
            process['peakBytes'] = max(process['peakBytes'], observed_peak)
            process['remainingBytes'] = max(0, process['peakBytes'] - process['rssBytes'])
        prospective_peak = max(launch['reservationBytes'], observed_peak)
        reserved = sum(p['remainingBytes'] for p in processes) + max(0, prospective_peak - own_rss)
        reading = memory()
        decision = {'sampledUTC': now(), 'memory': reading, 'processes': processes,
                    'effectiveConcurrency': len(processes) + 1, 'maxConcurrency': cap,
                    'reservedBytes': reserved, 'ownRSSBytes': own_rss,
                    'observedPeakBytes': observed_peak,
                    'prospectivePeakBytes': prospective_peak, 'peakEvidence': launch['peakEvidence'],
                    'requiredAvailableBytes': 3 * GIB + reserved}
        if reading['metric'] != MEMORY_METRIC or reading['pressureLevel'] != 1 \
                or reading['availableBytes'] < decision['requiredAvailableBytes'] \
                or decision['effectiveConcurrency'] > cap:
            decision['admitted'] = False
            immutable(self.root / 'admissions' / f'{uuid.uuid4().hex}.json', decision)
            refusal = Deferred(json.dumps(decision, sort_keys=True))
            refusal.decision = decision
            raise refusal
        decision['admitted'] = True
        immutable(self.root / 'admissions' / f'{uuid.uuid4().hex}.json', decision)
        return decision

    def observed_rss(self):
        peaks = []
        for path in sorted((self.root / 'admissions').glob('rss-*.json')):
            observation = json.loads(path.read_text())
            if observation['kind'] != RSS_OBSERVATION:
                raise ValueError('foreign RSS observation record')
            for sample in observation['samples']:
                if type(sample['rssBytes']) is not int or sample['rssBytes'] < 0:
                    raise ValueError('invalid persisted RSS observation')
                peaks.append(sample['rssBytes'])
        return peaks

    def claim(self, reference, *, pid, alive=alive, memory=mac_memory, rss=None):
        with self.locked():
            launch = record(reference)
            roster_ref, _ = self.roster()
            if launch['kind'] != 'STROKE_LAUNCH' or launch['rosterSha256'] != roster_ref['sha256']:
                raise ValueError('launch must name registered roster')
            if type(pid) is not int or pid <= 0:
                raise ValueError('positive worker PID required')
            task = task_tuple(launch['task'])
            handoff_path = self.root / 'handoffs' / f'{task[2] % 3}.json'
            if not handoff_path.exists():
                raise ValueError('partition has no explicit handoff')
            handoff_ref = json.loads(handoff_path.read_text())
            handoff, remaining = self.validate_handoff(handoff_ref, alive)
            if launch['captureRelease'] != handoff['captureRelease']:
                raise ValueError('launch and handoff must name the same capture release')
            if task not in remaining:
                raise ValueError('task already completed or certified excluded')
            predecessor = launch.get('deferredPredecessor')
            generation = 0 if predecessor is None else self.readmission(predecessor, task)
            destination = self.root / 'claims' / claim_filename(task, generation)
            if destination.exists():
                raise ValueError('task already claimed; no silent retry')
            decision = self.admission(launch, pid, alive, memory, rss)
            claim = dict(decision, task=list(task), pid=pid, claimedUTC=now(),
                         launch=reference, handoff=handoff_ref, generation=generation,
                         deferredPredecessor=predecessor,
                         reservationBytes=decision['prospectivePeakBytes'])
            immutable(destination, claim)
            return claim

    def readmission(self, reference, task):
        """Generation of a linked claim; only an unstarted no-fit deferral qualifies."""
        path = Path(reference['path'])
        if path.parent != self.root / 'deferrals':
            raise ValueError("predecessor must be this root's no-fit deferral receipt")
        deferral = record(reference)
        if deferral['kind'] != NO_FIT_DEFERRAL or deferral['solverStarted'] is not False \
                or task_tuple(deferral['task']) != task:
            raise ValueError('predecessor is not an unstarted no-fit deferral of this task')
        prior = record(deferral['claim'])
        name = claim_name(prior)
        if path.name != name or deferral['claim']['path'] != str(self.root / 'claims' / name) \
                or task_tuple(prior['task']) != task:
            raise ValueError('deferral does not belong to its predecessor claim')
        # A marker means a solver may have run: that attempt is never re-admitted.
        if (self.root / 'started' / name).exists() or (self.root / 'failures' / name).exists():
            raise ValueError('a started or failed attempt is never re-admitted')
        if (self.root / 'results' / filename(task)).exists():
            raise ValueError('task already has its exact-once result')
        return prior.get('generation', 0) + 1

    def settled(self, claim):
        name = claim_name(claim)
        if any((self.root / d / name).exists() for d in ('started', 'deferrals', 'failures')) \
                or (self.root / 'results' / filename(claim['task'])).exists():
            raise ValueError('attempt already started or settled')

    def check_before_fit(self, claim, *, alive=alive, memory=mac_memory, rss=None):
        with self.locked():
            self.check_claim(claim)
            self.settled(claim)
            name = claim_name(claim)
            launch = record(claim['launch'])
            try:
                decision = self.admission(launch, claim['pid'], alive, memory, rss,
                                          own_claim=claim)
            except Deferred as refusal:
                # Refused before any solver call: a NO-FIT deferral, not an attempt.
                # Unparseable readings and other errors are not Deferred and fail.
                immutable(self.root / 'deferrals' / name, {
                    'kind': NO_FIT_DEFERRAL, 'task': claim['task'],
                    'generation': claim.get('generation', 0), 'pid': claim['pid'],
                    'claim': {'path': str(self.root / 'claims' / name),
                              'sha256': hashlib.sha256(
                                  (self.root / 'claims' / name).read_bytes()).hexdigest()},
                    'solverStarted': False, 'memory': refusal.decision['memory'],
                    'decision': refusal.decision, 'deferredUTC': now(),
                    'readmission': 'only by an explicit parent STROKE_LAUNCH naming this '
                                   'receipt as deferredPredecessor'})
                raise
            immutable(self.root / 'admissions' / name, decision)
            return decision

    def start_solver(self, claim):
        """Durable marker: published and fsynced before the first optimizer call."""
        with self.locked():
            self.check_claim(claim)
            name = claim_name(claim)
            admitted = self.root / 'admissions' / name
            if not admitted.exists() or json.loads(admitted.read_text())['admitted'] is not True:
                raise ValueError("solver start requires this claim's admitted pre-fit check")
            if (self.root / 'started' / name).exists():
                raise FileExistsError('solver already started for this claim')
            self.settled(claim)
            immutable(self.root / 'started' / name, {
                'kind': SOLVER_START, 'task': claim['task'],
                'generation': claim.get('generation', 0), 'pid': claim['pid'],
                'claim': {'path': str(self.root / 'claims' / name),
                          'sha256': hashlib.sha256(
                              (self.root / 'claims' / name).read_bytes()).hexdigest()},
                'solverStarted': True, 'startedUTC': now()})

    def check_claim(self, claim):
        if json.loads((self.root / 'claims' / claim_name(claim)).read_text()) != claim:
            raise ValueError('claim changed')

    def finish(self, claim, result):
        with self.locked():
            self.check_claim(claim)
            name = claim_name(claim)
            if (self.root / 'failures' / name).exists() or (self.root / 'deferrals' / name).exists():
                raise ValueError('failed or deferred claim cannot produce a scored result')
            # Only a solver this claim durably marked as started can publish a result.
            marker = self.root / 'started' / name
            if not marker.exists():
                raise ValueError("result requires this claim's solver-start marker")
            started = json.loads(marker.read_text())
            claim_path = self.root / 'claims' / name
            if started['kind'] != SOLVER_START or started['solverStarted'] is not True \
                    or started['task'] != claim['task'] or started['pid'] != claim['pid'] \
                    or started['claim'] != {'path': str(claim_path), 'sha256': hashlib.sha256(
                        claim_path.read_bytes()).hexdigest()}:
                raise ValueError("solver-start marker does not match this claim")
            validate_result(result, claim['task'])
            immutable(self.root / 'results' / filename(claim['task']), result)

    def fail(self, claim, error):
        with self.locked():
            self.check_claim(claim)
            if (self.root / 'results' / filename(claim['task'])).exists():
                raise ValueError('completed result cannot be relabelled failed')
            if (self.root / 'deferrals' / claim_name(claim)).exists():
                raise ValueError('no-fit deferral cannot be relabelled failed')
            immutable(self.root / 'failures' / claim_name(claim),
                      {'task': claim['task'], 'pid': claim['pid'], 'failedUTC': now(),
                       'error': repr(error), 'retryAuthorized': False})


def selected_fit(function, observations, task, before_fit=None):
    # This helper imports no native reader. The same AST partition helper builds
    # all original sixteen starts and skips only the other outer-loop entries.
    sys.path.insert(0, str(STROKE))
    try:
        import start_partition
    finally:
        sys.path.pop(0)
    family, geometry, index = task_tuple(task)
    fit, provenance = start_partition.partition(function, [index])
    if before_fit is not None:
        before_fit()
    result = fit(observations, family, geometry == 'css', geometry == 'curvature')
    result.update(partitionProvenance=provenance,
                  fittedEndpoints=['light-inactive'] if family == 'M1' else
                                  ['light-inactive', 'dark-inactive'],
                  dummyEndpoints=['light-active', 'dark-active', 'dark-inactive'] if family == 'M1'
                                 else ['light-active', 'dark-active'])
    validate_result(result, task)
    return result, provenance


def run(store, reference):
    # Claim and account for the process BEFORE heavy imports or preparation.
    claim = store.claim(reference, pid=os.getpid(), rss=process_rss)
    started = time.perf_counter()
    try:
        revision = subprocess.check_output(['git', '-C', str(PROOF), 'rev-parse', 'HEAD'], text=True).strip()
        if revision != REVISION:
            raise ValueError('proof tree is not the held revision')
        # Refuse tracked proof edits too; a clean HEAD alone is not a byte seal.
        subprocess.run(['git', '-C', str(PROOF), 'diff', '--quiet', 'HEAD', '--'], check=True)
        sys.path.insert(0, str(STROKE))
        import survivor_scope_runner as prior
        prior.verify_authority()
        _, roster = store.roster()
        required_sources = [Path(prior.__file__), Path(prior.start_partition.__file__),
                            Path(prior.r.f.__file__)]
        for owner in roster['oldOwners']:
            verify_sources(record(owner['execution'])['sourceSha256'], required_sources)
        if not Path(prior.r.f.__file__).resolve().is_relative_to(PROOF) \
                or not Path(prior.r.__file__).resolve().is_relative_to(PROOF):
            raise ValueError('fitter did not load from sealed proof tree')
        prior.r.verify_seal()
        preparation = prior.r.Preparation()
        inactive = prior.prior.load_inactive(preparation, 'calibration')
        observations = prior.observations_for(claim['task'][0], inactive)
        store.check_before_fit(claim, rss=process_rss)
        with prior.r.compact_forward():
            result, _ = selected_fit(prior.r.f.fit_local, observations, claim['task'],
                                     before_fit=lambda: store.start_solver(claim))
        result.update(seconds=time.perf_counter()-started, heldRevision=REVISION,
                      peakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      schedulerClaim=claim, validationRead=False, holdoutRead=False,
                      sourceSha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in required_sources + [Path(__file__), Path(prior.prior.__file__)]},
                      authority='Explicit stopped-partition handoff; unchanged surviving endpoint scope')
        store.finish(claim, result)
    except BaseException as error:
        settle(store, claim, error)
        raise


def settle(store, claim, error):
    """Record a caught end of a claim that produced no result.

    Only the pre-fit check's own immutable deferral makes a claim re-admissible;
    every other caught end, including one after the solver-start marker, is a
    failed attempt. SIGKILL leaves the permanent claim (and any marker) without an
    outcome: also an attempt requiring human reconciliation, never a free task.
    """
    if (store.root / 'deferrals' / claim_name(claim)).exists() \
            or (store.root / 'results' / filename(claim['task'])).exists():
        return
    store.fail(claim, error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'transfer', 'run'))
    parser.add_argument('--root', required=True)
    parser.add_argument('--receipt', required=True, help='Absolute parent-authored receipt path')
    parser.add_argument('--sha256', required=True, help='Explicit expected receipt SHA-256')
    args = parser.parse_args()
    store = Store(args.root)
    reference = {'path': args.receipt, 'sha256': args.sha256}
    if args.command == 'init':
        store.initialize(reference)
    elif args.command == 'transfer':
        print(json.dumps(store.transfer(reference)))
    else:
        run(store, reference)


if __name__ == '__main__':
    main()
