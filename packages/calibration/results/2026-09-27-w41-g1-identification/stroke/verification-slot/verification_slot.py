"""One externally admitted completed-start verification, under the allocation lock.

This resource lease is not a candidate claim. Existing static workers continue;
new scheduler claims and ownership handovers wait until verification releases the
same lock. A crash leaves evidence requiring manual reconciliation, not a retry.
Only main() imports the native proof; importing this adapter reads no payload.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys

ADAPTER = Path(__file__).resolve()
HERE = ADAPTER.parent
STROKE = HERE.parent
MEMO = STROKE/'memoization'
COMPLETED = STROKE/'survivor-scope-partition-0/device-M1-start-00.json'
_spec = importlib.util.spec_from_file_location('verification_scheduler', STROKE/'scheduler/scheduler.py')
s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s)
ARTIFACTS = ('trace.jsonl.gz', 'raw-result.json', 'replay.json')


class VerificationOwner:
    """Resource label, deliberately carrying no candidate task or generation."""
    def __init__(self, mode):
        self.name = 'verification-' + mode


_candidate_name = s.claim_name


def owner_name(owner):
    # This private scheduler module is used only by this adapter. Its admission
    # routine accepts an own_claim for resident-RSS subtraction, but uses it only
    # through claim_name(). Extend that naming seam to a resource-only owner;
    # never fabricate a candidate claim. No valid candidate filename can equal
    # this resource label, so admission cannot skip a real candidate's reservation.
    return owner.name if isinstance(owner, VerificationOwner) else _candidate_name(owner)


s.claim_name = owner_name


def reference(path):
    path = Path(path).resolve()
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'path': str(path), 'sha256': digest}


def required_sources():
    instrument = s.PROOF/'packages/calibration/results/2026-09-27-w41-g0-declaration/instrument'
    held_stroke = s.PROOF/STROKE.relative_to(STROKE.parents[4])
    return [ADAPTER, Path(s.__file__).resolve(),
            *(MEMO/name for name in ('proof.py', 'solver_memo.py', 'fixtures.py')),
            *(STROKE/name for name in ('start_partition.py', 'survivor_scope_runner.py',
                                      'inactive_runner.py')),
            held_stroke/'replay.py',
            *(instrument/name for name in ('stroke_fit.py', 'instrument.py', 'shadow.py'))]


def check_proof(proof_ref, receipt, *, artifact_directory=None):
    proof = s.record(proof_ref)
    if proof.get('schema') != 'w41-memoization-native-one-mode-1' \
            or proof.get('verified') is not True or proof.get('mode') != receipt['mode'] \
            or proof.get('completedArtifact') != receipt['completedArtifact']['path'] \
            or proof.get('completedSha256') != receipt['completedArtifact']['sha256'] \
            or proof.get('classification') != 'verification replay, not a new candidate':
        raise ValueError('completed-start proof does not verify this mode and artifact')
    if set(proof.get('artifacts', {})) != set(ARTIFACTS):
        raise ValueError('proof must pin the complete artifact set')
    directory = artifact_directory or Path(proof_ref['path']).parent
    for name in ARTIFACTS:
        s.pinned({'path': str(directory/name),
                  'sha256': proof['artifacts'][name]})
    return proof



def check_recovery(store, receipt, previous, prior):
    """Accept a separately authorized comparison, never a rewritten failed solve.

    The helper's reviewed comparator owns numerical/trace verification. This
    boundary binds its immutable recovery to the original resource owner, saved
    solve and exact source transition permitted by the parent's new direction.
    """
    recovery = receipt['comparisonRecovery']
    direction = s.record(recovery['direction'])
    failure = receipt['predecessor']
    expected_error = dict(type='AssertionError',
        message='completed native raw result differs at exact typed/bit witness')
    if previous['status'] != 'failed-after-solver-start' or previous.get('proof') is not None \
            or previous.get('error') != expected_error \
            or previous.get('admissionStages') != ['before-preparation', 'before-fit']:
        raise ValueError('only the completed serialization-comparison failure is recoverable')
    if direction.get('kind') != 'STROKE_VERIFICATION_COMPARISON_RECOVERY' \
            or direction.get('schedulerRoot') != str(store.root) \
            or direction.get('failedTerminal') != failure \
            or direction.get('recoveredProof') != recovery['proof']:
        raise ValueError('parent recovery direction must bind this failed terminal and recovered proof')
    old, new = prior['sourceSha256'], receipt['sourceSha256']
    driver = str(MEMO/'proof.py')
    if set(old) != set(new):
        raise ValueError('recovery cannot change source membership')
    transitions = {key: dict(oldSha256=old[key], newSha256=value)
                   for key, value in new.items() if old[key] != value}
    if driver not in transitions or not set(transitions) <= {driver, str(ADAPTER)} \
            or direction.get('sourceTransitions') != transitions:
        raise ValueError('recovery requires explicit comparator/validator-only source transitions')
    saved = Path(prior['out'])
    proof_path = Path(recovery['proof']['path'])
    if proof_path.resolve() != proof_path or MEMO not in proof_path.parents \
            or proof_path.name != 'completed-start-proof.json' or proof_path.parent == saved:
        raise ValueError('recovery proof must be separate immutable evidence beneath memoization')
    proof = check_proof(recovery['proof'], prior, artifact_directory=saved)
    rerun = proof['comparisonRerun']
    if proof.get('artifactDirectory') != str(saved) \
            or rerun.get('action') != 'solve reused, comparison rerun' \
            or type(rerun.get('optimizerRuns')) is not int or rerun['optimizerRuns'] != 0 \
            or type(rerun.get('nativeArchiveReads')) is not int or rerun['nativeArchiveReads'] != 0 \
            or rerun.get('priorFailure') != failure \
            or rerun.get('comparatorSourceSha256') != new[driver]:
        raise ValueError('recovery must reuse this saved solve without fitting or archive reads')
    amendment = s.record(rerun['driverCompatibility'])
    if amendment.get('schema') != 'w41-proof-driver-comparison-amendment-1' \
            or amendment.get('sourcePath') != driver \
            or amendment.get('oldSourceSha256') != old[driver] \
            or amendment.get('newSourceSha256') != new[driver] \
            or set(amendment.get('unchangedExecutionBlocks', {})) != {
                'replay_once', 'native_onceThroughSolve'}:
        raise ValueError('comparator amendment must name the exact old/new execution source pair')
    s.pinned(amendment['diff'])
    replay = s.record({'path': str(saved/'replay.json'), 'sha256': proof['artifacts']['replay.json']})
    sources = replay['sourceSha256']
    if replay.get('mode') != 'unwrapped' or sources.get(driver) != old[driver] \
            or any(old.get(key) != value for key, value in sources.items()) \
            or proof.get('sourceSha256') != sources \
            or any(proof.get(key) != replay[key] for key in (
                'rawResultBitsSha256', 'trace', 'environment')) \
            or rerun.get('originalInMemoryResultBitsSha256') != replay['rawResultBitsSha256'] \
            or not proof.get('jsonBoundaryResultBitsSha256') \
            or rerun.get('jsonBoundaryResultBitsSha256') != proof['jsonBoundaryResultBitsSha256']:
        raise ValueError('recovery changed the saved execution source or live-result/trace witness')


def validate(store, admission_ref):
    receipt = s.record(admission_ref)
    roster_ref, _ = store.roster()
    if receipt['kind'] != 'STROKE_VERIFICATION_ADMIT' \
            or receipt['schedulerRoot'] != str(store.root) \
            or receipt['heldRevision'] != s.REVISION or receipt['roster'] != roster_ref:
        raise ValueError('verification receipt must name the held revision and registered root/roster')
    mode = receipt['mode']
    if mode not in ('unwrapped', 'wrapped'):
        raise ValueError('exactly one verification mode is required')
    out = Path(receipt['out'])
    if not out.is_absolute() or out.resolve() != out or MEMO not in out.parents:
        raise ValueError('output must be a canonical new path beneath memoization/')
    if out.exists():
        raise FileExistsError(out)
    s.verify_sources(receipt['sourceSha256'], required_sources())
    if receipt['completedArtifact']['path'] != str(COMPLETED):
        raise ValueError('only the completed original device M1 start zero may be verified')
    completed = s.record(receipt['completedArtifact'])
    if (completed['family'], completed['cssWidth'], completed['curvature'],
            [row['startIndex'] for row in completed['starts']]) != ('M1', False, False, [0]):
        raise ValueError('completed artifact identity changed')
    store.release(receipt['captureRelease'])
    s.record(receipt['peakEvidence'])
    predecessor = receipt['predecessor']
    if mode == 'unwrapped':
        if predecessor is not None or 'comparisonRecovery' in receipt:
            raise ValueError('unwrapped verification cannot have a predecessor')
    else:
        if not isinstance(predecessor, dict) or predecessor.get('path') != str(
                store.root/'verification/unwrapped/terminal.json'):
            raise ValueError('wrapped verification requires this root successful unwrapped predecessor')
        previous = s.record(predecessor)
        if previous.get('kind') != 'STROKE_VERIFICATION_TERMINAL' \
                or previous.get('mode') != 'unwrapped' \
                or previous.get('solverStarted') is not True:
            raise ValueError('unwrapped predecessor is not successful')
        if previous['lease']['path'] != str(store.root/'verification/unwrapped/lease.json'):
            raise ValueError('unwrapped lease is not from this resource root')
        prior_lease = s.record(previous['lease'])
        if prior_lease.get('kind') != 'STROKE_VERIFICATION_LEASE' \
                or prior_lease.get('mode') != 'unwrapped' \
                or prior_lease.get('pid') != previous['pid'] \
                or prior_lease.get('allocationLock') != str(store.root/'.lock'):
            raise ValueError('unwrapped resource owner identity changed')
        prior = s.record(prior_lease['receipt'])
        if prior['mode'] != 'unwrapped' or prior['completedArtifact'] != receipt['completedArtifact'] \
                or prior['schedulerRoot'] != str(store.root) \
                or prior['heldRevision'] != receipt['heldRevision'] \
                or prior['roster'] != receipt['roster']:
            raise ValueError('unwrapped predecessor verified a different source/artifact/roster')
        if 'comparisonRecovery' in receipt:
            check_recovery(store, receipt, previous, prior)
            return receipt
        if previous.get('status') != 'verified' or prior['sourceSha256'] != receipt['sourceSha256']:
            raise ValueError('unwrapped predecessor is not successful at this source epoch')
        if previous['proof']['path'] != str(Path(prior['out'])/'completed-start-proof.json'):
            raise ValueError('unwrapped proof is not its admitted output')
        check_proof(previous['proof'], prior)
    return receipt


def run(store, admission_ref, *, proof_body, alive=s.alive, memory=s.mac_memory,
        rss=s.process_rss, peak=lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        system=platform.system):
    """Inject only the body/OS readings in synthetic tests; never the memory policy."""
    with store.locked():
        receipt = validate(store, admission_ref)
        if system() != 'Darwin':
            raise ValueError('ru_maxrss bytes and memory admission require Darwin')
        mode, out = receipt['mode'], Path(receipt['out'])
        folder = store.root/'verification'/mode
        folder.parent.mkdir(exist_ok=True)
        folder.mkdir(exist_ok=False)
        pid = os.getpid()
        s.immutable(folder/'lease.json', dict(kind='STROKE_VERIFICATION_LEASE',
            pid=pid, mode=mode, receipt=admission_ref, startedUTC=s.now(),
            classification='resource-only verification; not a candidate claim',
            allocationLock=str(store.root/'.lock')))
        lease_ref = reference(folder/'lease.json')
        stages = []
        attempted = None
        proof_ref = None
        error_record = None

        def admit(stage):
            nonlocal attempted
            expected = 'before-preparation' if not stages else 'before-fit'
            if stage != expected or len(stages) >= 2:
                raise ValueError('verification admission stages must run once, in order')
            attempted = stage
            # Sources and external authority must still match at the solver gate.
            s.pinned(admission_ref)
            s.verify_sources(receipt['sourceSha256'], required_sources())
            s.pinned(receipt['completedArtifact'])
            decision = resource_admission(store, receipt, pid, alive, memory, rss,
                                          prepared=stage == 'before-fit')
            decision = dict(decision, kind='STROKE_VERIFICATION_ADMISSION',
                            mode=mode, stage=stage, pid=pid, lease=lease_ref)
            s.immutable(folder/(stage+'-admission.json'), decision)
            if stage == 'before-fit':
                s.immutable(folder/'solver-verification-start.json', dict(
                    kind='STROKE_SOLVER_VERIFICATION_START', pid=pid, mode=mode,
                    lease=lease_ref, admittedUTC=s.now(),
                    qualification='Durable pre-optimizer boundary, not a completed fit.'))
            stages.append(stage)
            return decision

        try:
            proof_body(mode, out, admit)
            if stages != ['before-preparation', 'before-fit']:
                raise ValueError('proof returned without both preparation and solver admission')
            s.pinned(admission_ref)
            s.verify_sources(receipt['sourceSha256'], required_sources())
            s.pinned(receipt['completedArtifact'])
            proof_ref = reference(out/'completed-start-proof.json')
            check_proof(proof_ref, receipt)
        except BaseException as error:
            error_record = dict(type=type(error).__name__, message=str(error))
            raise
        finally:
            # This high-water survives a refused gate and any caught failure. It
            # deliberately shares the scheduler's monotonic RSS observation path.
            observed = peak()
            if type(observed) is not int or observed <= 0:
                raise ValueError('Darwin process peak RSS must be positive integer bytes')
            observation = dict(kind=s.RSS_OBSERVATION, sampledUTC=s.now(),
                source='resource.getrusage(RUSAGE_SELF).ru_maxrss', platform='Darwin',
                unit='bytes', lease=lease_ref, samples=[dict(pid=pid,
                    owner='verification-'+mode, rssBytes=observed)])
            s.immutable(store.root/'admissions'/f'rss-verification-{mode}.json', observation)
            started = (folder/'solver-verification-start.json').exists()
            if error_record is None:
                status = 'verified'
            elif started:
                status = 'failed-after-solver-start'
            elif error_record['type'] == 'Deferred':
                status = 'refused-'+str(attempted)+'-no-fit'
            elif stages:
                status = 'preparation-attempted-no-fit'
            else:
                status = 'failed-before-preparation-no-fit'
            terminal = dict(kind='STROKE_VERIFICATION_TERMINAL', mode=mode, pid=pid,
                lease=lease_ref, endedUTC=s.now(), status=status, solverStarted=started,
                admissionStages=stages, peakRSSBytes=observed, peakRSSPlatform='Darwin',
                peakRSSUnit='bytes', rssObservation=reference(
                    store.root/'admissions'/f'rss-verification-{mode}.json'))
            if error_record is not None:
                terminal['error'] = error_record
            else:
                terminal['proof'] = proof_ref
            s.immutable(folder/'terminal.json', terminal)
        return terminal


def resource_admission(store, receipt, pid, alive, memory, rss, *, prepared):
    # task is only the subject of the admission log, not a claim request. The
    # immutable lease above owns the resource slot; the unchanged scheduler
    # routine owns every memory/concurrency calculation.
    launch = dict(receipt, task=['M1', 'device', 0])
    owner = VerificationOwner(receipt['mode']) if prepared else None
    return store.admission(launch, pid, alive, memory, rss, own_claim=owner)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--receipt', required=True, help='Absolute external admission receipt')
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()

    def native_body(mode, out, admit):
        # This CLI is the only native import/call site. It runs after receipt and
        # source verification, under the resource lease, with an admission callback.
        if subprocess.check_output(['git', '-C', str(s.PROOF), 'rev-parse', 'HEAD'],
                                   text=True).strip() != s.REVISION:
            raise ValueError('proof tree is not the held revision')
        subprocess.run(['git', '-C', str(s.PROOF), 'diff', '--quiet', 'HEAD', '--'], check=True)
        sys.path.insert(0, str(MEMO))
        sys.path.insert(1, str(STROKE))
        import proof
        if Path(proof.__file__).resolve() != MEMO/'proof.py':
            raise ValueError('proof module loaded from the wrong path')
        return proof.native_once(mode, out, admit)

    terminal = run(s.Store(args.root), {'path': args.receipt, 'sha256': args.sha256},
                   proof_body=native_body)
    print(json.dumps(terminal, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
