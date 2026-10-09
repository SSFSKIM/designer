#!/Users/new/vitrea-w49/py/bin/python -I -B
"""W50 G1 LIVE operator: one fit point, the frozen gate and the one exposure (charter DL4, DL5).

    /Users/new/vitrea-w49/py/bin/python -I -B live-run/run.py [--work DIR] <step>

Steps, in order:
    prefit                       executionClosure + independentReview proofs, the root's pre-fit evidence
    initialize                   the initializer once: the ONE candidate cohort and its numerical cohort,
                                 recorded in run/initialized.json before anything else runs; then the
                                 G0 numerical referee report and run/candidate.json. A rerun after a
                                 failed referee resumes from that record and runs only the referee.
                                 Refused on a root that registers the DL5p recovery declaration.
    recover-bind                 DL5p, instead of initialize, on root 3 only: the committed root-2 point
                                 (dl5p-recovery.json, recovery.py) is authenticated, bound by
                                 bind_arguments under this root, recorded in run/recovered.json before
                                 the referee runs, then refereed into run/candidate.json as initialize
                                 does. Never assembles or initializes; a rerun runs only the referee.
    fit-batch                    run/fit-batch.json
    run fit [--retries N]        create, then attempts until captured, then the analysis
    fit-record                   run/fit-record.json over the one completed fit (fit/live.fit_record)
    gate-batch                   owner intrinsic records (DL5o) and run/gate-batch.json
    run gate
    exposure-batch               run/exposure-batch.json; only after a gate PASS_EXPOSED_OWNER_PENDING
    run exposure
    status                       public status and verdict of every phase that exists

The root is the newest root of the LIVE chain (live-execution common.newest_root) and each
phase slot is that root's (common.slot). Operator records sit in run/ beside the root; phase
outputs are <work>/<phase>, outside every checkout, and the exposure's fixtures are planned
under <work>/exposure/native-blind, so the exposure batch and run share one output.

The sealed dispatcher's import guard is permanent, so every dispatcher step runs in its own
isolated child (child.py) whose streams stay in <work>/operator/. This process prints one JSON
line per event, built only from an allowlist: its own step and code, counts, ordinals, paths
and the verdict; a dispatcher event or status only after LIVE's own allowlist reproduces it
(DL5k). A failed child prints a code and its log path, never its message.

Operational stops are recovered as DL5k allows and nothing else is retried: a killed attempt
is preserved (stop_stale_attempt) and the next attempt planned; an INSTRUMENT_FAULT attempt is
retried up to --retries times; a census refusal or a held/lost lease stops for the operator,
who never touches another owner's process. Past a one-shot marker nothing is retried: an
incomplete native read or a started analysis without a sealed result stops (only a result
whose one write survived before its sidecar is completed, which the dispatcher reads as a
seal, not a replay). A second fit point, gate or exposure is never created; an existing slot
is resumed. A gate that is not PASS_EXPOSED_OWNER_PENDING stops everything after it.

The candidate record carries the point's provenance (recovery.provenance: the pre-fit evidence
initializer.json and the endpoint method lines name). Every step that reads it admits that
provenance only when it is this root's own pre-fit evidence, or when the record names a recovery
record that recovery.admit authenticates for this root (DL5p (c)); nothing else is admitted.

The initializer's outputs are write-once (fit/execution.py assemble and bind_arguments), so its
result is recorded before the referee runs and is never asked for twice. The referee's report
is read if an earlier attempt wrote it, never regenerated; its log is fresh per attempt. Any
exception the step does not stop on is printed as code ERROR with the path of a fresh log that
holds its traceback, never the traceback itself.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REPO = FIT.parents[3]
PY = '/Users/new/vitrea-w49/py/bin/python'
WORK = Path('/Users/new/vitrea-w50/g1-live')
PHASES = ('fit', 'gate', 'exposure')
VERDICTS = ('CAPTURED', 'PASS_EXPOSED_OWNER_PENDING', 'NEITHER', 'PASS')
GATE_SUCCESS = 'PASS_EXPOSED_OWNER_PENDING'
STEPS = ('prefit', 'initialize', 'recover-bind', 'fit-batch', 'run', 'fit-record', 'gate-batch', 'exposure-batch', 'status')
CODES = ('PREFIT_WRITTEN', 'CANDIDATE_WRITTEN', 'NUMERICAL_NOT_PASS', 'BATCH_WRITTEN', 'RECORD_WRITTEN',
         'PHASE_CREATED', 'PHASE_RESUMED', 'ATTEMPT', 'STALE_STOPPED', 'ANALYSIS', 'VERDICT', 'STATUS',
         'OWNER_RECORDS_BLOCKED', 'STOPPED_AFTER_GATE', 'NO_PHASE', 'REFUSED', 'STALE_ATTEMPT',
         'NATIVE_INCOMPLETE', 'ANALYSIS_STARTED', 'LEASE_HELD', 'EXISTS', 'ONE_FIT_ONLY', 'INITIALIZER_RECORDED',
         'INITIALIZE_RESUMED', 'TOOL_MISSING', 'RECOVERY_RECORDED', 'RECOVERY_RESUMED', 'ERROR')
INITIALIZED = ('cohort', 'initializer', 'numericalCohort', 'argumentManifest')
RECOVERED = (*INITIALIZED, 'preFitEvidence')
DECLARATION = HERE/'dl5p-recovery.json'
FIELDS = {'step': str, 'code': str, 'phase': str, 'attempt': int, 'members': int, 'runs': int, 'cells': int,
          'verdict': str, 'path': str, 'log': str, 'event': dict, 'status': dict}
# Dispatcher messages that name an operator state, read only to choose the code.
STATES = (('Prior attempt is not a preserved stop', 'STALE_ATTEMPT'),
          ('Incomplete native subread cannot be replayed', 'NATIVE_INCOMPLETE'),
          ('Native subread started without complete checkpoint', 'NATIVE_INCOMPLETE'),
          ('Analysis already started', 'ANALYSIS_STARTED'),
          ('Scientific analysis already started', 'ANALYSIS_STARTED'))


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path); sys.modules.setdefault(name, module)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text())


B = source(HERE/'batches.py', 'w50_live_run_batches')
C = source(HERE/'child.py', 'w50_live_run_child')
V = source(HERE/'recovery.py', 'w50_live_run_recovery')


class Stop(Exception):
    """An operator stop: its event is printed and the step exits nonzero."""
    def __init__(self, **event):
        super().__init__(event.get('code')); self.event = event


class Operator:
    """One operator over one sealed root. Every collaborator is injectable for the synthetic
    end-to-end test; the defaults are the real tree."""

    def __init__(self, *, repo=REPO, live=None, root=None, records=None, work=WORK, call=None, numerical=None,
                 declarations=None, transport=None, owner_records=None, prefit=None, out=print, pnpm='pnpm',
                 recovery=DECLARATION):
        self.repo = Path(repo).resolve(); self.live = Path(live or FIT/'live-execution')
        self.chain = source(self.live/'common.py', 'w50_live_run_chain_ops')
        self.root = Path(root or self.chain.newest_root(self.live)).resolve()
        self.records = Path(records or self.root.parent/'run'); self.work = Path(work)
        self.Q = source(self.live/'quarantine.py', 'w50_live_run_quarantine')
        if call is None:
            doc = load(self.root)
            call = C.Child(PY, self.repo/doc['bootstrap']['path'],
                           self.repo/doc['instruments']['initializer']['entrypoint']['path'], self.work/'operator', self.repo)
        self.call = call
        self.numerical = numerical or self._numerical
        self.declarations = declarations or (lambda: B.Declarations.sealed(self.root))
        self.transport = transport or B.transport_fields
        self.owner_records = owner_records or (lambda decl, candidate: B.owner_intrinsic_records(
            self.repo, decl.root['references'], candidate['cohort'], self.records/'owner-records'))
        self.prefit = prefit; self.out = out; self.pnpm = pnpm; self.declaration = Path(recovery)

    # paths ----------------------------------------------------------------------------------
    def record(self, name): return self.records/name
    def output(self, phase): return self.work/phase
    def rel(self, path):
        path = Path(path).resolve()
        return str(path.relative_to(self.repo)) if path.is_relative_to(self.repo) else str(path)

    def slot(self, phase):
        if phase != 'fit': return Path(self.chain.slot(self.root, phase))
        return Path(self.chain.slot(self.root, 'fit', sha(self.record('fit-batch.json'))))

    def fit_contracts(self):
        """Every fit contract of this root (DL4: there must be at most one)."""
        folder = Path(self.chain.slot(self.root, 'fit', '0'*64)).parent
        prefix = self.root.name.removesuffix('.json')
        return sorted(p for p in folder.glob('*.json') if re.fullmatch(
            re.escape(prefix)+r'\.[0-9a-f]{64}\.json|[0-9a-f]{64}\.json', p.name) and
            Path(self.chain.slot(self.root, 'fit', p.name.removesuffix('.json')[-64:])) == p)

    # output ---------------------------------------------------------------------------------
    def emit(self, **event):
        """Print one allowlisted event; anything else refuses before it is printed (DL5k)."""
        if set(event) - set(FIELDS) or event.get('step') not in STEPS or event.get('code') not in CODES or \
                any(not isinstance(v, FIELDS[k]) or (FIELDS[k] is int and isinstance(v, bool)) for k, v in event.items()) or \
                event.get('phase', 'fit') not in PHASES or event.get('verdict', 'PASS') not in VERDICTS:
            raise ValueError('Not an allowlisted operator event')
        if 'event' in event: self.public(event['event'])
        if 'status' in event: self.public_status(event['status'])
        self.out(json.dumps({'schema': 'w50-live-run-event-1', **event}, sort_keys=True))

    def public(self, value):
        body = {k: v for k, v in value.items() if k not in ('schema', 'code')}
        if value.get('schema') != 'w50-live-public-event-1' or self.Q.public_event(value.get('code'), **body) != value:
            raise ValueError('Not a LIVE public event')

    def public_status(self, value):
        if value.get('schema') == 'w50-live-public-event-1': return self.public(value)
        types_ = {'schema': str, 'phase': str, 'attempts': int, 'retained': int, 'remaining': int,
                  'analysisStarted': bool, 'nativeComplete': bool}
        if set(value) != set(types_) or value['schema'] != 'w50-live-public-status-1' or \
                any(type(value[k]) is not t for k, t in types_.items()) or value['phase'] not in PHASES:
            raise ValueError('Not a LIVE public status')

    def failed(self, step, result, phase=None):
        message = result.get('message') or ''
        code = next((c for text, c in STATES if text in message), 'LEASE_HELD' if result.get('error') == 'LeaseHeld' else 'REFUSED')
        return Stop(step=step, code=code, **({'phase': phase} if phase else {}),
                    **({'log': str(result['log'])} if result.get('log') else {}))

    def child(self, step, op, phase=None, **request):
        result = self.call(op, root=str(self.root), **request)
        if not result.get('ok'): raise self.failed(step, result, phase)
        return result

    # steps ----------------------------------------------------------------------------------
    def step_prefit(self):
        if self.prefit is None:
            prefit = source(HERE/'prefit.py', 'w50_live_run_prefit')
            verify = lambda root: self.child('prefit', 'verify_prefit')['preFitEvidence']
            layout = prefit.Layout(self.repo, live=self.live, root=self.root, verify=verify)
            built = prefit.build(layout)
        else: built = self.prefit(self)
        self.emit(step='prefit', code='PREFIT_WRITTEN', path=built['preFitEvidence']['path'])

    def recovery_root(self):
        """Whether this root registers the DL5p declaration (any bytes of it) among its inputs."""
        relative = self.rel(self.declaration)
        return any(isinstance(i, dict) and i.get('path') == relative for i in load(self.root).get('inputs', []))

    def step_initialize(self):
        target = self.record('candidate.json')
        if target.exists(): raise Stop(step='initialize', code='EXISTS', path=self.rel(target))
        if self.recovery_root() or self.record('recovered.json').exists():
            # DL5p (c): root 3 carries root 2's point; a second initialize would compute another.
            raise Stop(step='initialize', code='REFUSED', path=self.rel(self.declaration))
        recorded = self.record('initialized.json')
        if recorded.exists():
            made = self.initialized(recorded)
            self.emit(step='initialize', code='INITIALIZE_RESUMED', path=self.rel(recorded), members=len(made['cohort']))
        else:
            result = self.child('initialize', 'initialize')
            made = {k: result[k] for k in INITIALIZED}
            B.write_once(recorded, {'schema': 'w50-live-run-initialized-1', 'executionRootSha256': sha(self.root), **made})
            self.emit(step='initialize', code='INITIALIZER_RECORDED', path=self.rel(recorded), members=len(made['cohort']))
        self.referee('initialize', made)

    def referee(self, step, made, extra=None):
        """G0's numerical referee over the recorded numerical cohort, then run/candidate.json."""
        target = self.record('candidate.json')
        report = Path(self.numerical(made['numericalCohort']))
        try: verdict = load(report).get('status')
        except (OSError, ValueError): raise Stop(step=step, code='REFUSED', path=self.rel(report)) from None
        if verdict != 'PASS': raise Stop(step=step, code='NUMERICAL_NOT_PASS', path=self.rel(report))
        g0 = (self.repo/load(self.root)['partTwo']['path']).parent
        runner = source(g0/'audit/runner.py', 'w50_live_run_numerical_runner')
        try:
            for item in made['cohort']: runner.validate_numerical_referee(load(report), item['sha256'], self.repo)
        except ValueError: raise Stop(step=step, code='NUMERICAL_NOT_PASS', path=self.rel(report)) from None
        B.write_once(target, {'schema': 'w50-live-run-candidate-1', 'executionRootSha256': sha(self.root),
                              **{k: made[k] for k in INITIALIZED}, 'numericalReferee': B.D.pin(self.repo, report),
                              **(extra or {})})
        self.emit(step=step, code='CANDIDATE_WRITTEN', path=self.rel(target), members=len(made['cohort']))

    # DL5p bind-only recovery ------------------------------------------------------------------
    def own_prefit(self, step):
        """This root's own pre-fit evidence, as the sealed dispatcher's verify_prefit admits it."""
        return self.child(step, 'verify_prefit')['preFitEvidence']

    def admitted_recovery(self, step):
        """The DL5p declaration, authenticated for this root (recovery.admit), or a stop."""
        try:
            if not self.declaration.is_file(): raise V.Refused('No recovery declaration')
            return V.admit(self.repo, self.root, load(self.root), self.declaration)
        except (V.Refused, OSError, ValueError, KeyError, TypeError):
            raise Stop(step=step, code='REFUSED', path=self.rel(self.declaration)) from None

    def step_recover_bind(self):
        """DL5p (c): bind root 2's committed point under this root, never computing another."""
        step = 'recover-bind'; target = self.record('candidate.json')
        if target.exists(): raise Stop(step=step, code='EXISTS', path=self.rel(target))
        decl = self.admitted_recovery(step)
        if self.record('initialized.json').exists(): raise Stop(step=step, code='REFUSED', path=self.rel(self.record('initialized.json')))
        recorded = self.record('recovered.json')
        if recorded.exists():
            made = self.recovered(step, recorded, decl)
            self.emit(step=step, code='RECOVERY_RESUMED', path=self.rel(recorded), members=len(made['cohort']))
        else:
            own = self.own_prefit(step)
            if own == decl['predecessor']['preFitEvidence']: raise Stop(step=step, code='REFUSED', path=self.rel(self.declaration))
            bound = self.child(step, 'bind', cohort=decl['cohort'])
            made = {'cohort': decl['cohort'], 'initializer': decl['initializer'],
                    'numericalCohort': bound['numericalCohort'], 'argumentManifest': bound['argumentManifest'],
                    'preFitEvidence': bound['preFitEvidence']}
            self.bound_cohort(step, made, own)
            B.write_once(recorded, {'schema': V.RECORD, 'executionRootSha256': sha(self.root),
                                    'declaration': V.pin(self.repo, self.declaration), **made})
            self.emit(step=step, code='RECOVERY_RECORDED', path=self.rel(recorded), members=len(made['cohort']))
        self.referee(step, made, {'recovery': B.D.pin(self.repo, recorded)})

    def bound_cohort(self, step, made, own):
        """The bind ran under this root's own pre-fit evidence over exactly the declared cohort."""
        try:
            numerical = load(B.D.checked(self.repo, made['numericalCohort']))
            B.D.checked(self.repo, made['argumentManifest'])
            ok = made['preFitEvidence'] == own and numerical.get('candidates') == made['cohort'] and \
                numerical.get('structuredArguments') == made['argumentManifest']
        except (OSError, ValueError, KeyError, TypeError, AttributeError): ok = False
        if not ok: raise Stop(step=step, code='REFUSED', path=self.rel(self.record('recovered.json')))

    def recovered(self, step, path, decl):
        """The recorded bind, for this root and this declaration's point, every output unchanged."""
        value = load(path)
        if value.get('schema') != V.RECORD or value.get('executionRootSha256') != sha(self.root) or \
                set(value) != {'schema', 'executionRootSha256', 'declaration', *RECOVERED} or \
                value['declaration'] != V.pin(self.repo, self.declaration) or value['cohort'] != decl['cohort'] or \
                value['initializer'] != decl['initializer']:
            raise Stop(step=step, code='REFUSED', path=self.rel(path))
        made = {k: value[k] for k in RECOVERED}
        self.bound_cohort(step, made, self.own_prefit(step))
        return made

    def initialized(self, path):
        """The recorded initializer result, for this root, with every output it names unchanged."""
        value = load(path)
        if value.get('schema') != 'w50-live-run-initialized-1' or value.get('executionRootSha256') != sha(self.root) or \
                set(value) != {'schema', 'executionRootSha256', *INITIALIZED}:
            raise Stop(step='initialize', code='REFUSED', path=self.rel(path))
        try:
            for item in [*value['cohort'], *(value[k] for k in INITIALIZED[1:])]:
                B.D.checked(self.repo, {k: item.get(k) for k in ('path', 'sha256')})
        except (AttributeError, ValueError): raise Stop(step='initialize', code='REFUSED', path=self.rel(path)) from None
        return {k: value[k] for k in INITIALIZED}

    def _numerical(self, cohort):
        """G0's numerical referee over the numerical cohort (audit/numerical.ts), report beside it.
        A report an earlier attempt wrote is returned as it is (numerical.ts writes it exclusively,
        and a referee is never re-run to replace one); each attempt logs to a fresh file."""
        g0 = (self.repo/load(self.root)['partTwo']['path']).parent
        cohort_path = self.repo/cohort['path']; report = cohort_path.with_name('referee.json')
        if report.exists(): return report
        _, log = C._fresh(self.work/'operator', 'numerical-referee')
        with log.open('x') as stream:
            tool = shutil.which(self.pnpm)
            if tool is None:
                stream.write(f'{self.pnpm} is not on PATH\n')
                raise Stop(step='initialize', code='TOOL_MISSING', log=str(log))
            try:
                subprocess.run([tool, 'exec', 'tsx', str((g0/'audit/numerical.ts').relative_to(self.repo/'packages/calibration')),
                                '--cohort', cohort['path'], '--out', str(report)], cwd=self.repo/'packages/calibration',
                               stdout=stream, stderr=subprocess.STDOUT)
            except OSError as error:
                stream.write(f'{type(error).__name__}: {error}\n')
                raise Stop(step='initialize', code='TOOL_MISSING', log=str(log)) from None
        if not report.is_file(): raise Stop(step='initialize', code='REFUSED', log=str(log))
        return report

    def candidate(self, step):
        path = self.record('candidate.json')
        if not path.is_file(): raise Stop(step=step, code='NO_PHASE', path=self.rel(path))
        value = load(path)
        if value['executionRootSha256'] != sha(self.root): raise Stop(step=step, code='REFUSED', path=self.rel(path))
        self.admitted_provenance(step, path, value)
        return value

    def admitted_provenance(self, step, path, value):
        """The point's provenance is this root's own pre-fit evidence, or the record names a recovery
        that recovery.admit authenticates for this root and whose point it is (DL5p (c))."""
        refused = Stop(step=step, code='REFUSED', path=self.rel(path))
        try: named = V.provenance(self.repo, value['initializer'], value['cohort'])
        except (V.Refused, OSError, ValueError, KeyError, TypeError, AttributeError): raise refused from None
        if 'recovery' not in value:
            if named != [self.own_prefit(step)]: raise refused
            return
        decl = self.admitted_recovery(step)
        try: recorded = B.D.checked(self.repo, value['recovery'])
        except ValueError: raise refused from None
        if recorded != self.record('recovered.json').resolve(): raise refused
        made = self.recovered(step, recorded, decl)
        if any(value.get(k) != made[k] for k in INITIALIZED) or named != [decl['predecessor']['preFitEvidence']]:
            raise refused

    def write_batch(self, step, phase, doc):
        path = self.record(f'{phase}-batch.json')
        if path.exists(): raise Stop(step=step, code='EXISTS', path=self.rel(path))
        B.write_once(path, doc)
        self.emit(step=step, code='BATCH_WRITTEN', phase=phase, path=self.rel(path), runs=len(doc['runs']),
                  cells=len(B.members(doc)))

    def step_fit_batch(self):
        decl = self.declarations()
        self.write_batch('fit-batch', 'fit', B.build(decl, 'fit', self.candidate('fit-batch'), self.transport(decl)))

    def step_fit_record(self):
        target = self.record('fit-record.json')
        if target.exists(): raise Stop(step='fit-record', code='EXISTS', path=self.rel(target))
        fits = self.fit_contracts()
        if len(fits) != 1: raise Stop(step='fit-record', code='ONE_FIT_ONLY' if fits else 'NO_PHASE', phase='fit')
        result = Path(str(fits[0])+'.result.json')
        if not Path(str(result)+'.sha256').is_file(): raise Stop(step='fit-record', code='NO_PHASE', phase='fit')
        record = self.child('fit-record', 'fit_record', 'fit', completed=[B.D.pin(self.repo, result)])['record']
        B.write_once(target, record)
        self.emit(step='fit-record', code='RECORD_WRITTEN', phase='fit', path=self.rel(target))

    def step_gate_batch(self):
        candidate = self.candidate('gate-batch')
        record = self.record('fit-record.json')
        if not record.is_file(): raise Stop(step='gate-batch', code='NO_PHASE', phase='fit', path=self.rel(record))
        decl = self.declarations()
        if load(record)['selected'] != [B.plain(c) for c in sorted(candidate['cohort'], key=lambda c: c['position'])]:
            raise Stop(step='gate-batch', code='REFUSED', path=self.rel(record))
        existing = self.records/'owner-records'/'owner-intrinsic-records.json'
        try:
            intrinsic = B.D.pin(self.repo, existing) if existing.is_file() else self.owner_records(decl, candidate)
        except B.Blocked:
            raise Stop(step='gate-batch', code='OWNER_RECORDS_BLOCKED') from None
        self.write_batch('gate-batch', 'gate', B.build(decl, 'gate', candidate, self.transport(decl), intrinsic))

    def gate_verdict(self, step):
        gate = self.slot('gate')
        if not Path(str(gate)+'.result.json.sha256').is_file(): raise Stop(step=step, code='NO_PHASE', phase='gate')
        verdict = self.child(step, 'verdict', 'gate', contract=str(gate))['verdict']
        if verdict != GATE_SUCCESS: raise Stop(step=step, code='STOPPED_AFTER_GATE', phase='gate', verdict=verdict)

    def step_exposure_batch(self):
        self.gate_verdict('exposure-batch')
        candidate = self.candidate('exposure-batch'); decl = self.declarations()
        gate = load(self.record('gate-batch.json'))
        plans = B.exposure_plans(decl, self.output('exposure'))
        self.write_batch('exposure-batch', 'exposure', B.build(decl, 'exposure', candidate, self.transport(decl),
                                                               gate['ownerIntrinsicRecords'], plans))

    def step_run(self, phase, retries=1):
        batch = self.record(f'{phase}-batch.json')
        if not batch.is_file(): raise Stop(step='run', code='NO_PHASE', phase=phase, path=self.rel(batch))
        if phase == 'exposure':
            self.gate_verdict('run')
            output = (self.output('exposure')/'native-blind').resolve()
            if any(Path(r['fixtures']['path']).parent.parent != output/'fixtures'
                   for r in load(batch)['runs'] if r['sceneSource'] == 'w50'):
                raise Stop(step='run', code='REFUSED', phase=phase, path=self.rel(batch))
        contract = self.slot(phase)
        if Path(str(contract)+'.sha256').is_file():
            if load(contract)['batch'] != B.D.pin(self.repo, batch): raise Stop(step='run', code='REFUSED', phase=phase)
            self.emit(step='run', code='PHASE_RESUMED', phase=phase, path=self.rel(contract))
        else:
            if phase == 'fit' and [p for p in self.fit_contracts() if p != contract]:
                raise Stop(step='run', code='ONE_FIT_ONLY', phase='fit')
            request = {'batch': str(batch), 'output': str(self.output(phase))}
            if phase == 'gate':
                record = self.record('fit-record.json')
                if not record.is_file(): raise Stop(step='run', code='NO_PHASE', phase='fit', path=self.rel(record))
                request['fitRecord'] = str(record)
            made = Path(self.child('run', 'create_phase', phase, **request)['contract'])
            if made != contract: raise Stop(step='run', code='REFUSED', phase=phase)
            self.emit(step='run', code='PHASE_CREATED', phase=phase, path=self.rel(contract))
        stale = False
        while True:
            try:
                state = self.child('run', 'advance', phase, contract=str(contract))
            except Stop as stop:
                code = stop.event['code']
                if code == 'STALE_ATTEMPT' and not stale:
                    stale = True
                    event = self.child('run', 'stop_stale', phase, contract=str(contract))['event']
                    self.emit(step='run', code='STALE_STOPPED', phase=phase, event=event)
                    continue
                result = Path(str(contract)+'.result.json')
                if code == 'ANALYSIS_STARTED' and result.is_file() and not Path(str(result)+'.sha256').exists():
                    event = self.child('run', 'analysis', phase, contract=str(contract))['event']
                    self.emit(step='run', code='ANALYSIS', phase=phase, event=event)
                    if event['code'] == 'ANALYSIS_COMPLETE': return self.verdict(phase, contract)
                raise
            if state['state'] == 'complete': return self.verdict(phase, contract)
            event = state['event']
            if state['state'] == 'analysis':
                self.emit(step='run', code='ANALYSIS', phase=phase, event=event)
                if event['code'] != 'ANALYSIS_COMPLETE': raise Stop(step='run', code='REFUSED', phase=phase)
                return self.verdict(phase, contract)
            self.emit(step='run', code='ATTEMPT', phase=phase, attempt=state['attempt'], members=state['members'], event=event)
            if event['code'] == 'ATTEMPT_COMPLETE': continue
            if event['code'] == 'INSTRUMENT_FAULT' and retries > 0:
                retries -= 1; continue
            raise Stop(step='run', code='REFUSED', phase=phase)

    def verdict(self, phase, contract):
        verdict = self.child('run', 'verdict', phase, contract=str(contract))['verdict']
        self.emit(step='run', code='VERDICT', phase=phase, verdict=verdict)
        return verdict

    def step_status(self):
        phases = [('fit', p) for p in self.fit_contracts()]
        phases += [(phase, self.slot(phase)) for phase in ('gate', 'exposure') if Path(str(self.slot(phase))+'.sha256').is_file()]
        if not phases: self.emit(step='status', code='NO_PHASE')
        for phase, contract in phases:
            status = self.child('status', 'status', phase, contract=str(contract))['status']
            event = {'step': 'status', 'code': 'STATUS', 'phase': phase, 'status': status}
            if Path(str(contract)+'.result.json.sha256').is_file():
                event['verdict'] = self.child('status', 'verdict', phase, contract=str(contract))['verdict']
            self.emit(**event)


def main(argv=None, operator=None):
    parser = argparse.ArgumentParser(description='W50 G1 LIVE operator (module docstring).')
    parser.add_argument('--work', type=Path, default=WORK)
    parser.add_argument('step', choices=STEPS)
    parser.add_argument('phase', nargs='?', choices=PHASES)
    parser.add_argument('--retries', type=int, default=1)
    args = parser.parse_args(argv)
    if (args.step == 'run') != (args.phase is not None): parser.error('run takes exactly one phase')
    try:
        operator = operator or Operator(work=args.work)
        if args.step == 'run': return 0 if operator.step_run(args.phase, args.retries) else 1
        getattr(operator, 'step_'+args.step.replace('-', '_'))()
        return 0
    except Stop as stop:
        try:
            operator.emit(**stop.event)
            return 1
        except BaseException as error:
            return failure(args.step, operator, args.work, error)
    except BaseException as error:
        return failure(args.step, operator, args.work, error)


def failure(step, operator, work, error):
    """Prints code ERROR and the path of a fresh log holding the traceback; nothing the error
    says reaches the terminal (DL5k)."""
    out = operator.out if operator is not None else print
    event = {'schema': 'w50-live-run-event-1', 'step': step, 'code': 'ERROR'}
    try:
        _, log = C._fresh(Path(operator.work if operator is not None else work)/'operator', 'operator-error')
        with log.open('x') as stream: traceback.print_exception(error, file=stream)
        event['log'] = str(log)
    except BaseException:
        pass
    out(json.dumps(event, sort_keys=True))
    return 1


if __name__ == '__main__':
    sys.exit(main())
