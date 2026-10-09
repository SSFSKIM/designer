#!/usr/bin/env python3
"""DL5f attempt-two copy of the reviewed prospective dispatcher.

The original g1-fit implementation and burned claim are immutable. This sibling admits
only the declared replacement, names its prior failure and exact ruling, and binds the
new-bed host that current and subsequent candidate phases must share. The first forty-two
GPU PNGs must compare byte-for-byte with attempt one before any CSS/later current run.
A failure retains its claim; even a completed GPU proof cannot unburn the failed batch.

Inherited DL5–DL5e interfaces and full candidate/owner controls remain below.

API (all paths are explicit; no production seal is made on import):
  seal_current_root(repo, directory, part_one, part_two, references, manifest, adapter,
                    probe, sources, baseline_documents, current_batches, inputs=(),
                    replacement_attempt={attempt:2,priorRoot,priorClaim,priorFailure,ruling})
  seal_root(repo, directory, part_one, part_two, references, manifest, adapter,
            judge, probe, sources, reported_keys, baseline_documents=(), inputs=(),
            instruments={'fit': pin, 'measurement': pin, 'bands': pin}, empty_support_keys=(),
            current_instrument=<current-only root path>, current_results=[pins], owner_contracts=pin)
  current_contract(root, batch); fit_contract(root, batch)
  gate_contract(root, batch, fit_record); exposure_contract(root, batch)
  execute(root, contract, supplied_batch, output)

The separate current-instrument-root.json admits only prospectively fixed current batches,
refusing the entire physical exposure closure. It uses the same dispatcher capability and
lease, but no future judge/fitter/pre-fit placeholder or live numerical admission. The later
single live execution-root.json requires every completed current result, binds that chain
in inputs, and can never open another current lane. Baseline draws inside the single claimed
exposure remain deterministic same-cell derivatives, not another current instrument run.

The adapter exports execute(context) and execute_current(context). After a fit capture,
the pinned fit instrument's evaluate(context, captures) supplies analysis, not a verdict.
A separately pinned judge exports evaluate(context, captures); only this full intersection
referee can issue PASS. The fit record selects one cohort from completed fit batches, not another candidate.
Every contract/result/attempt is exclusive. A failed/interrupted launch burns its attempt.
The API grants no retry, amendment, publication, fixture override or scene override.

A batch has schema w50-g1-batch-1, phase, cohort=[{path,sha256}], and runs containing
id/profile/renderer/scenes/sets/candidate. Adapter-specific run fields are content-bound,
never supplied as extra CLI flags. Root inputs hold non-Python Node/Vite closure pins;
only the adapter's pinned guards can enforce that subprocess boundary. A fit record has
schema w50-g1-fit-record-1, executionRootSha256, selected (one cohort), and completed
(content pins of fit contract .result.json files). Gate/exposure reports have status,
sorted candidateSha256s, and exact keyed cells. REPORTED rows also require finite scalar
native/current/candidate readings and B:null; they do not waive the two level cuts.

Run execute in its own -I process: its import guard is permanent. Adapters import
require_context from w50_g1_dispatch and call it before any capture helper. Neither
current nor fit capture completion claims a gate PASS; that belongs to the judge.
The dispatcher admits live candidates through G0's unchanged numerical referee and owns
/tmp/w49-gpu.lock once through adapter, fit analysis and judge. Adapters call
require_render_admission(context, run, current=False), never acquire a nested lease.
DL5d derives phaseDependencies from original identities: any withheld statistic defers
its entire (profile, scene) across both declared tiers. Original roles/budgets never move.
Gate success is PASS_EXPOSED_OWNER_PENDING with exact pendingOwnerKeys and
ownerChecks=PENDING_FULL_UNION; exposed owner-contracts rows remain PENDING_OWNER_UNION.
ownerUnionKeys names ALL original owner keys, not just the owners whose captures moved.
Exposure receives gateResult (a content pin), gateCaptures, gateReport and unionExpectedCells.
Its final PASS/NEITHER covers every original key and binds that same gateResult; aggregate
owners are evaluated on the full union, never given a partial-population PASS.

Returned captures must cover the entire cohort and membership with pinned cell/report/PNG
artifacts beneath context.output. Gate selection rechecks those receipts and artifact bytes.

DL5b/c emptySupportKeys are exact manifest-derived subsets of reportedKeys, not a general
null allowance. An admitted nativeRead zero-mask witness is required even on those keys;
blind rows remain identity-only until exposure. The two level rows never gain this status.
DL5e ownerBudgetKeys enumerates the original owner laws exactly. Their B is null, not a
waiver: ownerContracts pins the source-generated per-axis snapshot, and each ownerEvidence
pins its matching CURRENT report projection with actual values, exclusions and limits.
"""
import argparse
import copy
import contextlib
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys
import uuid

HERE = Path(__file__).resolve().parent
PROOFS = ('nativeArchive', 'repeatBar', 'referenceCompletion', 'dark05Bands',
          'active05ScratchBaselines', 'identityDigestsGoldens', 'numericalRehearsal',
          'shaderCpuAgreement', 'negativeNeutralDiagnostic', 'newBedRendererAdapter',
          'executionClosure', 'independentReview')
SLOTS = {'fit': 'fit', 'gate': 'gate-contract.json', 'exposure': 'exposure-contract.json'}
CURRENT_NAME = 'current-instrument-root.json'
CURRENT_SCHEMA = 'w50-g1-current-instrument-root-1'
CURRENT_SLOTS = {'current': 'current-instrument'}
WITHHELD = {'blind', 'historical-prediction-check'}
GATE_SUCCESS = 'PASS_EXPOSED_OWNER_PENDING'
KEY = ('profile', 'renderer', 'scene', 'statistic')
_ACTIVE = None
GPU_LOCK = Path("/tmp/w49-gpu.lock")
_LEASE = None
_REPLAY_VERIFIED = False


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    def invalid(value):
        raise ValueError(f'Nonfinite JSON constant: {value}')
    return json.loads(Path(path).read_text(), parse_constant=invalid)


def pin(repo, path):
    path = Path(path).resolve()
    return {'path': str(path.relative_to(Path(repo).resolve())), 'sha256': sha(path)}


def checked(repo, item):
    if not isinstance(item, dict) or not isinstance(item.get('path'), str) or \
            not re.fullmatch('[0-9a-f]{64}', item.get('sha256', '')):
        raise ValueError('Missing content pin')
    path = (Path(repo) / item['path']).resolve()
    if not path.is_relative_to(Path(repo).resolve()) or not path.is_file() or sha(path) != item['sha256']:
        raise ValueError(f'Changed or missing pinned source/input: {item["path"]}')
    return path


def write_once(path, value):
    """O_EXCL is the claim. Retain partial bytes on interruption, never silently retry."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    return path


def sealed(path):
    path = Path(path)
    sidecar = Path(str(path) + '.sha256')
    if not sidecar.is_file():
        sidecar = path.with_suffix('.sha256')
    if not sidecar.is_file() or sidecar.read_text() != f'{sha(path)}  {path.name}\n':
        raise ValueError(f'Missing or changed prospective seal: {path}')
    return load(path)


def write_sealed(path, value):
    path = Path(path)
    if Path(str(path) + '.sha256').exists():
        raise ValueError('Existing seal; no amendment')
    write_once(path, value)
    with Path(str(path) + '.sha256').open('x') as handle:
        handle.write(f'{sha(path)}  {path.name}\n'); handle.flush(); os.fsync(handle.fileno())
    return path


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    exec(compile(Path(path).read_bytes(), str(Path(path).resolve()), 'exec'), result.__dict__)
    return result


def owner_budget_keys(cells):
    return [[c[k] for k in KEY] for c in cells if c['statistic']=='owner-contracts']


def derive_phase_dependencies(cells):
    """DL5d changes timing only: any withheld statistic closes its physical pair."""
    identity = lambda c: [c[k] for k in KEY]
    keys = [identity(c) for c in cells]
    if not cells or len({tuple(k) for k in keys}) != len(keys):
        raise ValueError('Physical dependency closure needs unique original reference keys')
    physical = lambda c: (c['profile'], c['scene'])
    withheld = {physical(c) for c in cells if c['role'] in WITHHELD}
    groups = []
    for profile, scene in sorted(withheld):
        rows = [c for c in cells if physical(c) == (profile, scene)]
        groups.append({'profile': profile, 'scene': scene, 'keys': [identity(c) for c in rows],
                       'withheldKeys': [identity(c) for c in rows if c['role'] in WITHHELD],
                       'deferredKeys': [identity(c) for c in rows if c['role'] not in WITHHELD]})
    return {'schema': 'w50-phase-dependencies-1', 'groups': groups,
            'gateKeys': [identity(c) for c in cells if physical(c) not in withheld],
            'exposureKeys': [identity(c) for c in cells if physical(c) in withheld],
            'pendingOwnerKeys': [identity(c) for c in cells if physical(c) in withheld
                                 and c['role'] not in WITHHELD and c['statistic'] == 'owner-contracts'],
            'ownerUnionKeys': [identity(c) for c in cells if c['statistic'] == 'owner-contracts']}


def verify_phase_dependencies(doc, cells):
    expected = derive_phase_dependencies(cells)
    if doc.get('phaseDependencies') != expected:
        raise ValueError('Missing, unclosed or changed physical dependency table')
    return expected


def declared_inputs(repo, part_one, part_two, references, manifest):
    one, two = load(part_one), load(part_two)
    expected_refs = (Path(part_one).parent / one['references']).resolve()
    if (Path(part_two).parent / two['references']).resolve() != expected_refs or \
            Path(references).resolve() != expected_refs or Path(manifest).resolve() != \
            (Path(part_one).parent / one['native']['manifest']).resolve():
        raise ValueError('Root inventory/manifest differs from immutable declaration selection')
    for source in (one, two):
        for target in (references, manifest):
            if pin(repo, target) not in source['sources']:
                raise ValueError('Selected inventory/manifest is not pinned by immutable G0')


def admission_module(doc):
    path = checked(doc['repo'], doc['bootstrap'])
    return module(path.with_name('admission.py'), 'w50_g1_admission')


def seal_root(repo, directory, part_one, part_two, references, manifest, adapter,
              judge, probe, sources, reported_keys, baseline_documents=(), inputs=(), instruments=None,
              empty_support_keys=(), current_instrument=None, current_results=None, owner_contracts=None):
    repo, directory = Path(repo).resolve(), Path(directory).resolve()
    if not directory.is_relative_to(repo):
        raise ValueError('Execution root must live inside its repository')
    # A relocated execution root still registers exactly these bootstrap bytes.
    for name in ('dispatch.py', 'guard.py', 'prefit.py', 'admission.py', 'owner_evidence.py', 'replacement.py'):
        if sha(directory / name) != sha(HERE / name):
            raise ValueError('Root bootstrap is not these dispatcher bytes')
    path = directory / 'execution-root.json'
    if path.exists() or Path(str(path)+'.sha256').exists():
        raise ValueError('Execution root already exists; no amendment')
    one, two = sealed(part_one), sealed(part_two)
    if two.get('partOneSha256') != sha(part_one) or tuple(two.get('requiredEvidence', [])) != PROOFS:
        raise ValueError('Part two has another parent or proof population')
    for part in (one, two):
        for item in part.get('sources', []): checked(repo, item)
    required_paths = [directory / name for name in ('dispatch.py', 'guard.py', 'prefit.py', 'admission.py', 'owner_evidence.py', 'replacement.py')]
    declared_inputs(repo, part_one, part_two, references, manifest)
    required_paths += [Path(adapter), Path(judge), Path(probe)]
    required_paths += [Path(part_two).parent / "audit" / n for n in ("runner.py", "numerical_guard.py")]
    if not isinstance(instruments, dict) or set(instruments) != {'fit', 'measurement', 'bands'}:
        raise ValueError('Root requires fit, measurement and band instrument source pins')
    required_paths += [checked(repo, item) for item in instruments.values()]
    for relative, digest in sources.items(): checked(repo, {'path': relative, 'sha256': digest})
    if any(sources.get(str(p.resolve().relative_to(repo))) != sha(p) for p in required_paths):
        raise ValueError('Bootstrap/adapter/judge/probe absent from source closure')
    for item in (*baseline_documents, *inputs): checked(repo, item)
    prefit = module(directory / 'prefit.py', 'w50_g1_prefit_seal')
    prefit.validate_exemptions(load(references), load(manifest), reported_keys)
    prefit.validate_empty_eligibility(load(references), load(manifest), reported_keys, list(empty_support_keys))
    if current_instrument is None:
        raise ValueError('Live root requires its completed current-only instrument')
    current_pin = pin(repo, current_instrument)
    current_results = list(current_results or [])
    evidence_inputs = current_evidence_inputs(repo, directory, current_pin, current_results)
    owners = owner_budget_keys(load(references)['cells'])
    if owners:
        checked(repo, owner_contracts)
        evidence_inputs.append(owner_contracts)
    elif owner_contracts is not None:
        raise ValueError('Owner snapshot supplied without original owner rows')
    bound_inputs = list(inputs)
    evidence_inputs.append(root_doc(current_instrument)['newBedHost'])
    for item in evidence_inputs:
        if item not in bound_inputs: bound_inputs.append(item)
    guard = module(directory / 'guard.py', 'w50_g1_guard_seal')
    closure = guard.discover(repo, probe, sources)
    doc = {'schema': 'w50-g1-execution-root-1', 'repo': str(repo), 'slots': SLOTS,
           'bootstrap': pin(repo, directory/'dispatch.py'),
           'partOne': pin(repo, part_one), 'partTwo': pin(repo, part_two),
           'candidateDomain': two['candidateDomain'], 'references': pin(repo, references),
           'manifest': pin(repo, manifest), 'adapter': pin(repo, adapter), 'judge': pin(repo, judge),
           'probe': pin(repo, probe), 'closure': closure, 'reportedKeys': reported_keys,
           'baselineDocuments': list(baseline_documents), 'inputs': bound_inputs,
           'currentInstrument': current_pin, 'currentResults': current_results,
           'ownerBudgetKeys': owners, 'ownerContracts': owner_contracts,
           'newBedHost': root_doc(current_instrument)['newBedHost'],
           'instruments': instruments, 'emptySupportKeys': list(empty_support_keys),
           'phaseDependencies': derive_phase_dependencies(load(references)['cells'])}
    if owners:
        checker = module(directory/'owner_evidence.py', 'w50_g1_owner_seal')
        checker.OwnerEvidence(repo, owner_contracts, owner_source(doc)).finish()
    return write_sealed(path, doc)


def current_only(doc):
    return doc.get('schema') == CURRENT_SCHEMA


def seal_current_root(repo, directory, part_one, part_two, references, manifest, adapter,
                      probe, sources, baseline_documents, current_batches, inputs=(), replacement_attempt=None):
    """A separate, non-promotable current instrument; no future judge/fitter placeholder."""
    repo, directory = Path(repo).resolve(), Path(directory).resolve()
    path = directory / CURRENT_NAME
    if not directory.is_relative_to(repo) or path.exists() or Path(str(path)+'.sha256').exists():
        raise ValueError('Current instrument root is outside the repository or already sealed')
    required = [directory/name for name in ('dispatch.py', 'guard.py', 'admission.py', 'replacement.py')]
    for source in required:
        if sha(source) != sha(HERE/source.name):
            raise ValueError('Current root must use the actual dispatcher bootstrap')
    one, two = sealed(part_one), sealed(part_two)
    if two.get('partOneSha256') != sha(part_one) or tuple(two.get('requiredEvidence', [])) != PROOFS:
        raise ValueError('Original current-instrument declarations differ')
    for part in (one, two):
        for item in part.get('sources', []): checked(repo, item)
    declared_inputs(repo, part_one, part_two, references, manifest)
    required += [Path(adapter), Path(probe)]
    for relative, digest in sources.items(): checked(repo, {'path': relative, 'sha256': digest})
    if any(sources.get(str(p.resolve().relative_to(repo))) != sha(p) for p in required):
        raise ValueError('Current adapter/probe/bootstrap absent from source closure')
    for item in [*baseline_documents, *current_batches, *inputs]: checked(repo, item)
    if not baseline_documents or not current_batches or len({p['path'] for p in current_batches}) != len(current_batches):
        raise ValueError('Current instrument needs fixed baseline documents and unique fixed batches')
    replacement = module(directory/'replacement.py', 'w50_current2_replacement')
    attempt = replacement.validate(repo, directory, replacement_attempt,
        [load(checked(repo, item)) for item in current_batches])
    bound_inputs = list(inputs)
    for item in [replacement_attempt[k] for k in ('priorRoot','priorClaim','priorFailure','ruling')]:
        if item not in bound_inputs: bound_inputs.append(item)
    host = pin(repo, directory.parent/'web/host.mjs')
    if host not in bound_inputs: bound_inputs.append(host)
    doc = {'schema': CURRENT_SCHEMA, 'repo': str(repo), 'slots': CURRENT_SLOTS,
           'bootstrap': pin(repo, directory/'dispatch.py'), 'adapter': pin(repo, adapter),
           'probe': pin(repo, probe), 'partOne': pin(repo, part_one), 'partTwo': pin(repo, part_two),
           'candidateDomain': two['candidateDomain'], 'references': pin(repo, references),
           'manifest': pin(repo, manifest), 'baselineDocuments': list(baseline_documents),
           'currentBatches': list(current_batches), 'inputs': bound_inputs,
           'replacementAttempt': replacement_attempt, 'replacement': attempt, 'newBedHost': host,
           'phaseDependencies': derive_phase_dependencies(load(references)['cells'])}
    # Domain/membership checks use only pinned current documents and reference identities.
    for item in current_batches: validate_batch(doc, checked(repo, item), 'current')
    guard = module(directory/'guard.py', 'w50_g1_current_guard')
    doc['closure'] = guard.discover(repo, probe, sources)
    return write_sealed(path, doc)


def root_doc(path):
    path = Path(path).resolve(); doc = sealed(path)
    repo = Path(doc['repo']).resolve()
    is_current = current_only(doc)
    name, slots = (CURRENT_NAME, CURRENT_SLOTS) if is_current else ('execution-root.json', SLOTS)
    if doc.get('schema') not in (CURRENT_SCHEMA, 'w50-g1-execution-root-1') or \
            doc.get('slots') != slots or path.name != name or not path.is_relative_to(repo):
        raise ValueError('Invalid execution root mode/phase slots')
    if is_current and any(k in doc for k in ('judge', 'instruments', 'currentInstrument', 'currentResults')):
        raise ValueError('Current-only root cannot carry live execution authority')
    if checked(repo, doc['bootstrap']) != path.parent/'dispatch.py':
        raise ValueError('Root bootstrap selection differs')
    sources = doc['closure']['sources']
    for relative, digest in sources.items(): checked(repo, {'path': relative, 'sha256': digest})
    bootstrap = ('dispatch.py', 'guard.py', 'admission.py', 'replacement.py') + (() if is_current else ('prefit.py', 'owner_evidence.py'))
    for name in bootstrap:
        relative = str((path.parent/name).relative_to(repo))
        if sources.get(relative) != sha(path.parent/name):
            raise ValueError('Missing bootstrap closure pin')
    if sha(__file__) != sources[str((path.parent/'dispatch.py').relative_to(repo))]:
        raise ValueError('Unregistered dispatcher entrypoint')
    for name in ('partOne', 'partTwo', 'references', 'manifest', 'adapter', 'probe'):
        checked(repo, doc[name])
    entries = [doc['adapter'], doc['probe']]
    if not is_current:
        if not doc.get('judge') or set(doc.get('instruments', {})) != {'fit', 'measurement', 'bands'}:
            raise ValueError('Live root needs its real judge and complete instrument roles')
        entries += [doc['judge'], *doc['instruments'].values()]
    for item in entries:
        checked(repo, item)
        if sources.get(item['path']) != item['sha256']:
            raise ValueError('Instrument not in exercised source closure')
    for item in doc['baselineDocuments'] + doc['inputs']: checked(repo, item)
    one, two = sealed(checked(repo, doc['partOne'])), sealed(checked(repo, doc['partTwo']))
    if two.get('partOneSha256') != doc['partOne']['sha256'] or \
            two.get('candidateDomain') != doc['candidateDomain'] or tuple(two['requiredEvidence']) != PROOFS:
        raise ValueError('Original declaration/domain changed')
    for part in (one, two):
        for item in part.get('sources', []): checked(repo, item)
    declared_inputs(repo, checked(repo, doc['partOne']), checked(repo, doc['partTwo']),
                    checked(repo, doc['references']), checked(repo, doc['manifest']))
    verify_phase_dependencies(doc, load(checked(repo, doc['references']))['cells'])
    if is_current:
        batches = doc.get('currentBatches', [])
        if not batches or len({p['path'] for p in batches}) != len(batches):
            raise ValueError('Current instrument has no fixed unique batches')
        for item in batches: validate_batch(doc, checked(repo, item), 'current')
    else:
        for name in ('runner.py', 'numerical_guard.py'):
            source = checked(repo, doc['partTwo']).parent/'audit'/name
            if sources.get(str(source.relative_to(repo))) != sha(source):
                raise ValueError('Missing fixed numerical referee source')
        evidence_inputs = current_evidence_inputs(repo, path.parent, doc.get('currentInstrument'),
                                                 doc.get('currentResults'))
        if doc.get('newBedHost') != root_doc(checked(repo,doc['currentInstrument']))['newBedHost'] or doc['newBedHost'] not in doc['inputs']:
            raise ValueError('Candidate and current must use the identical declared new-bed host')
        if any(item not in doc['inputs'] for item in evidence_inputs):
            raise ValueError('Live root omitted current-only instrument/results from its pinned inputs')
        owners = owner_budget_keys(load(checked(repo, doc['references']))['cells'])
        if doc.get('ownerBudgetKeys') != owners:
            raise ValueError('Live root changed the exact owner null-budget key population')
        if owners:
            checked(repo, doc.get('ownerContracts'))
            if doc['ownerContracts'] not in doc['inputs']:
                raise ValueError('Owner contracts snapshot is not a prospective root input')
            checker = module(path.parent/'owner_evidence.py', 'w50_g1_owner_checker')
            checker.OwnerEvidence(repo, doc['ownerContracts'], owner_source(doc)).finish()
        elif doc.get('ownerContracts') is not None:
            raise ValueError('Owner snapshot supplied without original owner rows')
        prefit = module(path.parent/'prefit.py', 'w50_g1_root_prefit')
        prefit.validate_empty_eligibility(load(checked(repo, doc['references'])),
            load(checked(repo, doc['manifest'])), doc['reportedKeys'], doc['emptySupportKeys'])
    if is_current:
        replacement = module(path.parent/'replacement.py', 'w50_current2_replacement')
        actual = replacement.validate(repo, path.parent, doc.get('replacementAttempt'),
            [load(checked(repo,item)) for item in doc['currentBatches']])
        if actual != doc.get('replacement'):
            raise ValueError('Changed attempt-two prior GPU identity closure')
        for item in [doc['replacementAttempt'][k] for k in ('priorRoot','priorClaim','priorFailure','ruling')]:
            if item not in doc['inputs']: raise ValueError('Replacement authority missing from root inputs')
        if checked(repo, doc['newBedHost']) != path.parent.parent/'web/host.mjs' or doc['newBedHost'] not in doc['inputs']:
            raise ValueError('Replacement new-bed host differs from the declared source')
    return doc


def current_evidence_inputs(repo, directory, instrument, results):
    """The live root consumes completed current evidence; it cannot supply a placeholder."""
    root = checked(repo, instrument)
    if root.name != CURRENT_NAME or root.parent != Path(directory).resolve() or \
            sealed(root).get('schema') != CURRENT_SCHEMA:
        raise ValueError('Live root must bind its separate current-only sibling instrument')
    current = root_doc(root)
    if Path(current['repo']).resolve() != Path(repo).resolve() or not isinstance(results, list) or not results:
        raise ValueError('Missing same-repository completed current results')
    expected, inputs = [], [pin(repo, root), pin(repo, Path(str(root)+'.sha256'))]
    for item in current['currentBatches']:
        batch_path = checked(repo, item)
        batch, _ = validate_batch(current, batch_path, 'current')
        contract_path = root.parent / CURRENT_SLOTS['current'] / f'{item["sha256"]}.json'
        contract = sealed(contract_path)
        if (contract.get('schema') != 'w50-g1-phase-contract-1' or contract.get('phase') != 'current' or
                contract.get('executionRootSha256') != sha(root) or contract.get('batch') != item or
                contract.get('cohort') != batch['cohort'] or contract.get('preFitEvidence') is not None):
            raise ValueError('Current evidence contract differs from its fixed current-only batch')
        result_path = Path(str(contract_path)+'.result.json')
        expected.append(pin(repo, result_path))
        result = result_for(contract_path)
        claim = load(Path(str(contract_path)+'.started.json'))
        if claim.get('phase') != 'current' or claim.get('numericalAdmission') is not None or \
                result['report'].get('status') != 'CAPTURED' or 'analysis' in result['report']:
            raise ValueError('Current-only evidence cannot stand in for candidate admission or fit')
        receipt = admission_module(current).validate_captures(batch, result['captures'], claim['output'])
        if receipt != result['captureReceipt'] or result['report'].get('captures') != result['captures']:
            raise ValueError('Current-only result does not cover its fixed captures')
        for artifact in (contract_path, Path(str(contract_path)+'.sha256'),
                         Path(str(contract_path)+'.started.json'), result_path, Path(str(result_path)+'.sha256')):
            inputs.append(pin(repo, artifact))
    if results != expected:
        raise ValueError('Live root must pin every completed fixed current batch result in declaration order')
    replay = read_current_replay(root, current, require_complete=True)
    for artifact in (root.parent/'gpu-replay-proof.json', Path(str(root.parent/'gpu-replay-proof.json')+'.sha256')):
        inputs.append(pin(repo, artifact))
    if not replay['cells']: raise ValueError('Current evidence has no prior GPU byte proof')
    return inputs


def owner_source(doc):
    wanted = 'packages/calibration/test/adopted-thresholds.test.ts'
    pins = load(checked(doc['repo'], doc['partTwo']))['sources']
    matches = [p for p in pins if p['path']==wanted]
    if len(matches)!=1:
        raise ValueError('Original declaration lacks its unique source-owned owner contracts')
    checked(doc['repo'], matches[0])
    return matches[0]


def verify_prefit(path, doc):
    repo = Path(doc['repo']); directory = Path(path).resolve().parent
    evidence = sealed(directory / 'pre-fit-evidence.json')
    if evidence.get('partTwoSha256') != doc['partTwo']['sha256']:
        raise ValueError('Pre-fit evidence names another part two')
    pins = evidence.get('sources', [])
    for item in pins: checked(repo, item)
    for target in (Path(path), Path(str(path)+'.sha256')):
        if pin(repo, target) not in pins:
            raise ValueError('Pre-fit evidence did not prospectively pin execution root')
    if evidence.get('executionClosure') != doc['closure']:
        raise ValueError('Pre-fit evidence lacks exact exercised closure')
    prefit = module(directory / 'prefit.py', 'w50_g1_prefit')
    original = load(checked(repo, doc['references']))
    prefit.validate_exemptions(original, load(checked(repo, doc['manifest'])), doc['reportedKeys'])
    prefit.validate_completion(original, load(checked(repo, evidence['references'])),
                               doc['reportedKeys'], repo, empty_support_keys=doc['emptySupportKeys'],
                               owner_budget_keys=doc['ownerBudgetKeys'], owner_contracts=doc['ownerContracts'],
                               owner_source=owner_source(doc) if doc['ownerBudgetKeys'] else None)
    if set(evidence.get('evidence', {})) != set(PROOFS):
        raise ValueError('All twelve pre-fit proofs are required')
    for kind in PROOFS:
        prefit.validate_proof(load(checked(repo, evidence['evidence'][kind])), kind, repo)
    return pin(repo, directory / 'pre-fit-evidence.json')


def cohort(doc, value):
    if not isinstance(value, list) or not value:
        raise ValueError('Missing candidate cohort')
    for item in value: checked(doc['repo'], item)
    if len({p['path'] for p in value}) != len(value) or len({p['sha256'] for p in value}) != len(value):
        raise ValueError('Duplicate candidate cohort')
    return value


def validate_batch(doc, path, phase):
    if current_only(doc) != (phase=='current'):
        raise ValueError('Current-only instrument and live execution phases cannot be promoted or interchanged')
    if phase=='current' and pin(doc['repo'], path) not in doc.get('currentBatches', []):
        raise ValueError('Current batch was not fixed in the current-only root')
    batch = load(path)
    if batch.get('schema') != 'w50-g1-batch-1' or batch.get('phase') != phase or \
            not batch.get('runs') or phase not in (*SLOTS, 'current'):
        raise ValueError('Wrong or empty phase batch')
    selected = cohort(doc, batch.get('cohort'))
    if phase == 'current' and any(item not in doc['baselineDocuments'] for item in selected):
        raise ValueError('Current instrument requires prospectively pinned baseline documents')
    positions = admission_module(doc).validate_cohort(doc, selected, current=phase=='current')
    refs = load(checked(doc['repo'], doc['references']))['cells']
    dependencies = verify_phase_dependencies(doc, refs)
    withheld_physical = {(g['profile'], g['scene']) for g in dependencies['groups']}
    by_cell = {}
    for row in refs:
        by_cell.setdefault(tuple(row[k] for k in KEY[:3]), []).append(row)
    seen, ids = set(), set()
    for run in batch['runs']:
        if not re.fullmatch('[A-Za-z0-9_-]+', run.get('id', '')) or run['id'] in ids:
            raise ValueError('Unsafe or duplicate run identity')
        ids.add(run['id'])
        if run.get('candidate') not in selected:
            raise ValueError('Run is not bound to the selected candidate cohort')
        if not run.get('profile', '').endswith('glass'+str(positions[run['candidate']['sha256']])):
            raise ValueError('Run profile selects another candidate position')
        scenes, sets = run.get('scenes'), run.get('sets')
        allowed = {'calibration', 'validation', 'recorded', 'probe'}
        if phase in ('exposure', 'current'): allowed.add('holdout')
        if not isinstance(scenes, list) or not scenes or len(set(scenes)) != len(scenes) or \
                any(not isinstance(s, str) or not s or ',' in s for s in scenes) or \
                not isinstance(sets, list) or not sets or len(set(sets)) != len(sets) or not set(sets) <= allowed:
            raise ValueError('Invalid scenes or withheld set outside exposure')
        if 'baselineCandidate' in run and (phase != 'exposure' or
                run['baselineCandidate'] not in doc['baselineDocuments']):
            raise ValueError('Baseline candidate must be root-pinned and exposure-only')
        if run.get('sceneSource')=='w50':
            closure = load(checked(doc['repo'], run.get('webSourceClosure')))
            source_pins = closure.get('sources', [])
            if not isinstance(source_pins,list) or doc['newBedHost'] not in source_pins:
                raise ValueError('New-bed run lacks the identical current/candidate host source')
        if 'webSourceClosure' in run and run['webSourceClosure'] not in doc['inputs']:
            raise ValueError('Web source closure is not a prospective root input')
        for scene in scenes:
            cell = (run['profile'], run['renderer'], scene)
            if cell in seen or cell not in by_cell:
                raise ValueError('Duplicate or out-of-batch declared cell')
            seen.add(cell)
            physical = (run['profile'], scene)
            if phase in ('fit', 'gate') and physical in withheld_physical:
                raise ValueError('Physically withheld dependency requested outside exposure')
            if phase == 'current' and physical in withheld_physical:
                raise ValueError('Every exposure-closed current capture belongs only to exposure')
            if phase == 'exposure' and physical not in withheld_physical:
                raise ValueError('Unbound exposed cell in exposure batch')
    if {r['candidate']['sha256'] for r in batch['runs']} != {p['sha256'] for p in selected}:
        raise ValueError('Every candidate cohort member must have declared captures')
    if phase in ('gate', 'exposure'):
        expected = {tuple(k[:3]) for k in dependencies[phase+'Keys']}
        if seen != expected:
            raise ValueError('Phase membership must exactly equal the original declaration')
    rows = [r for r in refs if tuple(r[k] for k in KEY[:3]) in seen]
    return batch, [{k: r[k] for k in KEY} for r in rows]


def create_contract(path, batch_path, phase, extra=None):
    path = Path(path).resolve(); doc = root_doc(path)
    batch, _ = validate_batch(doc, batch_path, phase)
    evidence = None if phase == 'current' else verify_prefit(path, doc)
    folder = path.parent
    target = folder / doc['slots'][phase] / f'{sha(batch_path)}.json' if phase in ('fit', 'current') else folder / SLOTS[phase]
    value = {'schema': 'w50-g1-phase-contract-1', 'executionRootSha256': sha(path),
             'phase': phase, 'batch': pin(doc['repo'], batch_path), 'cohort': batch['cohort'],
             'preFitEvidence': evidence, **(extra or {})}
    return write_sealed(target, value)


def fit_contract(path, batch):
    if (Path(path).parent / SLOTS['gate']).exists():
        raise ValueError('Gate contract froze selection; no later fit')
    return create_contract(path, batch, 'fit')


def current_contract(path, batch):
    return create_contract(path, batch, 'current')


def result_for(contract):
    result = sealed(Path(str(contract)+'.result.json'))
    claim = load(Path(str(contract)+'.started.json'))
    if result.get('contractSha256') != sha(contract) or result.get('claimSha256') != \
            sha(Path(str(contract)+'.started.json')) or claim.get('contractSha256') != sha(contract):
        raise ValueError('Result not bound to its claimed invocation')
    for item in result.get('captureReceipt', {}).get('artifacts', []):
        if not Path(item['path']).is_file() or sha(item['path']) != item['sha256']:
            raise ValueError('Completed capture artifact changed')
    if not result.get('captureReceipt', {}).get('members'):
        raise ValueError('Completed result has no bound capture membership')
    return result


def validate_fit_record(path, doc, selected, fit_record):
    record = load(fit_record)
    if record.get('schema') != 'w50-g1-fit-record-1' or \
            record.get('executionRootSha256') != sha(path) or record.get('selected') != selected:
        raise ValueError('Gate requires the fit record single selected cohort')
    if not record.get('completed'):
        raise ValueError('Fit record has no completed, content-pinned fit')
    selected_seen = False
    for item in record['completed']:
        result_path = checked(doc['repo'], item)
        if not str(result_path).endswith('.result.json'):
            raise ValueError('Fit completion is not a dispatcher result')
        contract = Path(str(result_path)[:-len('.result.json')])
        fit = sealed(contract)
        if contract.parent != Path(path).resolve().parent / 'fit' or fit.get('phase') != 'fit' or \
                fit.get('executionRootSha256') != sha(path):
            raise ValueError('Fit completion belongs to another execution root')
        completed = result_for(contract)
        if completed['report'].get('status') != 'CAPTURED':
            raise ValueError('Selected fit did not complete measurement')
        fitted_batch, _ = validate_batch(doc, checked(doc['repo'], fit['batch']), 'fit')
        claim = load(Path(str(contract)+'.started.json'))
        receipt = admission_module(doc).validate_captures(fitted_batch, completed['report']['captures'], claim['output'])
        if receipt != completed['captureReceipt']:
            raise ValueError('Fit record capture receipt differs from its full cohort/membership')
        selected_seen |= fit['cohort'] == selected
    if not selected_seen:
        raise ValueError('Selected candidate cohort was never completed by fit')


def gate_contract(path, batch_path, fit_record):
    doc = root_doc(path)
    batch, _ = validate_batch(doc, batch_path, 'gate')
    validate_fit_record(path, doc, batch['cohort'], fit_record)
    return create_contract(path, batch_path, 'gate', {'fitRecord': pin(doc['repo'], fit_record)})


def checked_gate_result(path, doc):
    gate = Path(path).resolve().parent / SLOTS['gate']
    if not gate.is_file() or not Path(str(gate)+'.result.json').is_file():
        raise ValueError('Exposure requires a completed qualified gate success')
    contract = sealed(gate)
    if contract.get('executionRootSha256') != sha(path) or contract.get('phase') != 'gate':
        raise ValueError('Gate belongs to another root/phase')
    batch, expected = validate_batch(doc, checked(doc['repo'], contract['batch']), 'gate')
    result = result_for(gate)
    claim = load(Path(str(gate)+'.started.json'))
    receipt = admission_module(doc).validate_captures(batch, result['captures'], claim['output'])
    if receipt != result['captureReceipt']:
        raise ValueError('Gate capture result differs from complete declared membership')
    validate_report(doc, batch, expected, result['report'])
    if result['report']['status'] != GATE_SUCCESS:
        raise ValueError('Only PASS on exposed cells with owners pending admits exposure')
    return gate, result


def exposure_contract(path, batch_path):
    doc = root_doc(path); batch, _ = validate_batch(doc, batch_path, 'exposure')
    gate, result = checked_gate_result(path, doc)
    if batch['cohort'] != sealed(gate)['cohort'] or result['report'].get('candidateSha256s') != \
            sorted(p['sha256'] for p in batch['cohort']):
        raise ValueError('Exposure requires qualified gate success at identical candidate bytes')
    return create_contract(path, batch_path, 'exposure',
        {'gateContract': pin(doc['repo'], gate),
         'gateResult': pin(doc['repo'], Path(str(gate)+'.result.json'))})


def lease_owned():
    if _LEASE is None:
        return False
    try:
        stat = GPU_LOCK.stat()
        return (stat.st_dev, stat.st_ino) == _LEASE['identity'] and GPU_LOCK.read_text() == _LEASE['token']
    except FileNotFoundError:
        return False


@contextlib.contextmanager
def owned_gpu_lock():
    global _LEASE
    if _LEASE is not None:
        raise ValueError('Nested GPU lease is not admitted')
    token = f'W50 pid={os.getpid()} owner={uuid.uuid4().hex}\n'
    with GPU_LOCK.open('x') as handle:
        handle.write(token); handle.flush(); os.fsync(handle.fileno())
        stat = os.fstat(handle.fileno())
    _LEASE = {'identity': (stat.st_dev, stat.st_ino), 'token': token}
    try:
        yield
    finally:
        if lease_owned(): GPU_LOCK.unlink()
        _LEASE = None


def first_current_contract(path, doc):
    return Path(path).parent/CURRENT_SLOTS['current']/f'{doc["currentBatches"][0]["sha256"]}.json'


def read_current_replay(path, doc, require_complete=False):
    proof_path = Path(path).parent/'gpu-replay-proof.json'
    if not proof_path.is_file(): raise ValueError('Attempt two has not proved the retained forty-two GPU PNGs')
    proof = sealed(proof_path)
    first = first_current_contract(path,doc)
    claim = Path(str(first)+'.started.json')
    if (proof.get('schema')!='w50-current2-gpu-replay-proof-1' or proof.get('status')!='BYTE_IDENTICAL' or
            proof.get('executionRootSha256')!=sha(path) or proof.get('contractSha256')!=sha(first) or
            proof.get('claimSha256')!=sha(claim) or proof.get('replacementAttempt')!=doc['replacementAttempt']):
        raise ValueError('GPU replay proof differs from the attempt-two root and first claim')
    output = Path(load(claim)['output'])
    local = output/'gpu-replay-proof.json'
    if not local.is_file() or local.read_bytes()!=proof_path.read_bytes():
        raise ValueError('GPU replay output witness differs from the root proof')
    if not isinstance(proof.get('cells'),list) or len(proof['cells'])!=42:
        raise ValueError('GPU replay proof does not contain exactly forty-two cells')
    records = [{'profile':c['profile'],'renderer':c['renderer'],'scene':c['scene'],
                'candidate':doc['replacement']['priorGpu'][i]['candidate'],'lane':'current',
                'artifacts':{'png':c['replacementPng']}} for i,c in enumerate(proof.get('cells',[]))]
    replacement = module(Path(path).parent/'replacement.py','w50_current2_replacement')
    compared = replacement.compare(doc['replacement'],records,output)
    if compared!=proof['cells']: raise ValueError('GPU replay proof changed its original PNG binding')
    if require_complete:
        completed=result_for(first)
        if completed['report'].get('status')!='CAPTURED':
            raise ValueError('A failed replacement batch cannot license later CSS/current capture')
    return proof


def is_replay_run(context,run):
    require_context(context)
    doc=_ACTIVE[5]
    return (context['phase']=='current' and Path(context['contract'])==first_current_contract(context['executionRoot'],doc)
            and run==context['batch']['runs'][0])


def require_current_replay(context,run):
    require_context(context)
    if context['phase']!='current' or run not in context['batch']['runs']:
        raise ValueError('GPU replay prerequisite applies only to original current runs')
    if not _REPLAY_VERIFIED and not is_replay_run(context,run):
        raise ValueError('No CSS or later run before exact forty-two GPU byte-identity proof')


def record_current_replay(context,records):
    global _REPLAY_VERIFIED
    require_context(context)
    if _REPLAY_VERIFIED or not is_replay_run(context,context['batch']['runs'][0]):
        raise ValueError('GPU replay is a single first-run proof, not a retry')
    doc=_ACTIVE[5]; path=Path(context['executionRoot'])
    replacement=module(path.parent/'replacement.py','w50_current2_replacement')
    cells=replacement.compare(doc['replacement'],records,context['output'])
    proof={'schema':'w50-current2-gpu-replay-proof-1','status':'BYTE_IDENTICAL',
           'executionRootSha256':sha(path),'contractSha256':sha(context['contract']),
           'claimSha256':sha(str(context['contract'])+'.started.json'),
           'replacementAttempt':doc['replacementAttempt'],'cells':cells}
    write_sealed(Path(context['output'])/'gpu-replay-proof.json',proof)
    write_sealed(path.parent/'gpu-replay-proof.json',proof)
    _REPLAY_VERIFIED=True


def baseline_run(run):
    return {**run, 'candidate': run['baselineCandidate'],
            'captureRoot': str(Path(run['captureRoot'])/'baseline'),
            'matrixPath': str(Path(run['matrixPath']).with_name(Path(run['matrixPath']).stem+'-baseline.json'))}


def require_render_admission(context, run, current=False):
    require_context(context)
    if context['phase']=='current': require_current_replay(context,run)
    admitted = [(r, context['phase']=='current') for r in context['batch']['runs']]
    if context['phase']=='exposure':
        admitted += [(baseline_run(r), True) for r in context['batch']['runs']
                     if r.get('baselineCandidate') in context['baselineDocuments']]
    if (run, current) not in admitted:
        raise ValueError('Render request differs from admitted immutable run/lane')
    admission_module(_ACTIVE[5]).endpoints(_ACTIVE[5], run['candidate'], current=current)
    if not current: checked(context['repo'], _ACTIVE[6])
    return run


def require_context(context):
    """Adapter entrypoint guard: caller-created/copied contexts carry no capability."""
    if _ACTIVE is None or context is not _ACTIVE[0]:
        raise ValueError('Direct/bypassed adapter entrypoint: no dispatcher capability')
    if not lease_owned() or not _ACTIVE[4]:
        raise ValueError('No live GPU lease and numerical/baseline admission')
    if context != _ACTIVE[1]:
        raise ValueError('Execution context was mutated after batch binding')
    if context.get('gateResult') is not None:
        checked(context['repo'], context['gateResult'])
    if sha(context['contract']) != _ACTIVE[2] or sha(context['batchPath']) != _ACTIVE[3]:
        raise ValueError('Registered contract/batch changed during invocation')
    return context


def validate_report(doc, batch, expected, report, gate_result=None):
    phase = batch['phase']
    if phase not in ('gate', 'exposure'):
        raise ValueError('Only gate/exposure receive a phase-qualified referee verdict')
    positive = GATE_SUCCESS if phase=='gate' else 'PASS'
    if report.get('status') not in (positive, 'NEITHER') or report.get('candidateSha256s') != \
            sorted(p['sha256'] for p in batch['cohort']):
        raise ValueError('Full referee did not bind verdict to candidate bytes')
    dependencies = doc['phaseDependencies']
    pending = dependencies['pendingOwnerKeys'] if phase=='gate' else []
    scope = 'PENDING_FULL_UNION' if phase=='gate' else 'FULL_UNION'
    if report.get('pendingOwnerKeys') != pending or report.get('ownerChecks') != scope:
        raise ValueError('Referee did not preserve pending owners/full-union scope')
    if phase=='exposure' and (gate_result is None or report.get('gateResult') != gate_result):
        raise ValueError('Final union verdict does not bind the same-candidate gate result')
    original = {tuple(c[k] for k in KEY): c for c in load(checked(doc['repo'], doc['references']))['cells']}
    expected_keys = set(original) if phase=='exposure' else {tuple(c[k] for k in KEY) for c in expected}
    cells = report.get('cells', [])
    keys = [tuple(c[k] for k in KEY) for c in cells]
    if len(keys) != len(set(keys)) or set(keys) != expected_keys:
        raise ValueError('Full referee membership differs from phase contract')
    exemptions = {tuple(k) for k in doc['reportedKeys']}
    for cell in cells:
        identity = tuple(cell[k] for k in KEY)
        if cell.get('status') == 'UNMEASURED_EMPTY_SUPPORT':
            if identity not in exemptions:
                raise ValueError('Empty-support status cannot waive a gated row')
            prefit = module(checked(doc['repo'], doc['bootstrap']).with_name('prefit.py'), 'w50_g1_report_prefit')
            prefit.validate_empty_support({**cell, 'role': original[identity]['role']},
                doc['emptySupportKeys'], doc['repo'], candidate=True)
            continue
        if cell.get('status') == 'REPORTED':
            if identity not in exemptions:
                raise ValueError('Overbroad reported-row exemption')
            if 'B' not in cell or cell['B'] is not None or any(
                    type(cell.get(k)) not in (int, float) or not math.isfinite(cell[k]) or cell[k] < 0
                    for k in ('native', 'current', 'candidate')):
                raise ValueError('Reported row still requires finite native/current/candidate and null B')
        wanted = ('REPORTED' if identity in exemptions else 'PENDING_OWNER_UNION'
                  if phase=='gate' and cell['statistic']=='owner-contracts' else 'PASS')
        if report['status'] == positive and cell.get('status') != wanted:
            raise ValueError('Qualified verdict lacks the complete phase/owner intersection')


def execute(path, contract_path, supplied_batch, output):
    global _ACTIVE
    path, contract_path = Path(path).resolve(), Path(contract_path).resolve()
    doc = root_doc(path); repo = Path(doc['repo'])
    contract = sealed(contract_path); phase = contract.get('phase')
    if phase not in (*SLOTS, 'current') or contract.get('executionRootSha256') != sha(path):
        raise ValueError('Unregistered execution contract')
    registered = checked(repo, contract['batch'])
    if Path(supplied_batch).read_bytes() != registered.read_bytes():
        raise ValueError('Supplied batch differs from registered content')
    if current_only(doc) != (phase=='current'):
        raise ValueError('Current-only root cannot execute a live phase contract')
    target = path.parent / doc['slots'][phase] / f'{sha(registered)}.json' if phase in ('fit', 'current') else path.parent / SLOTS[phase]
    if contract_path != target:
        raise ValueError('Contract is not the fixed phase slot')
    batch, expected = validate_batch(doc, registered, phase)
    if contract['cohort'] != batch['cohort']:
        raise ValueError('Contract cohort differs from batch')
    if phase == 'fit' and (path.parent / SLOTS['gate']).exists():
        raise ValueError('Gate froze fit; no later fit launch')
    if phase == 'gate':
        validate_fit_record(path, doc, batch['cohort'], checked(repo, contract['fitRecord']))
    if phase == 'exposure':
        gate = checked(repo, contract['gateContract']); checked(repo, contract['gateResult'])
        actual_gate, _ = checked_gate_result(path, doc)
        if gate != actual_gate or sealed(gate)['cohort'] != batch['cohort']:
            raise ValueError('Exposure lacks same-candidate qualified gate success')
    if phase=='current' and contract_path != first_current_contract(path,doc):
        read_current_replay(path,doc,require_complete=True)
    output = Path(output).resolve()
    if output.is_relative_to(repo) or output.exists() or any(
            name in output.parts for name in ('profiles', 'generations', 'web-captures-superseded')):
        raise ValueError('Output must be a fresh external scratch directory')
    # No repository helper executes before the bootstrap verified every source above.
    guard = module(path.parent / 'guard.py', 'w50_g1_guard')
    if guard.environment() != doc['closure']['environment']:
        raise ValueError('Interpreter/environment differs from prospective closure')
    guard.enforce(repo, doc['closure']['sources'])
    if guard.discover(repo, checked(repo, doc['probe']), doc['closure']['sources']) != doc['closure']:
        raise ValueError('Exercised import closure changed')
    if phase != 'current' and verify_prefit(path, doc) != contract['preFitEvidence']:
        raise ValueError('Pre-fit evidence changed after phase binding')
    admission = admission_module(doc)
    numerical = None if phase=='current' else admission.validate_numerical(doc, batch)
    # Claim before launch; current is exempt from live numerical admission, never from the lease.
    with owned_gpu_lock():
        return execute_admitted(path, contract_path, registered, output, doc, batch, expected, admission, numerical)


def execute_admitted(path, contract_path, registered, output, doc, batch, expected, admission, numerical):
    global _ACTIVE, _REPLAY_VERIFIED
    _REPLAY_VERIFIED = False
    repo = Path(doc['repo']); phase = batch['phase']
    claim = Path(str(contract_path)+'.started.json')
    write_once(claim, {'contractSha256': sha(contract_path), 'batchSha256': sha(registered),
                       'phase': phase, 'pid': os.getpid(), 'output': str(output),
                       'numericalAdmission': numerical, 'gpuLease': _LEASE['token']})
    output.mkdir(parents=True, exist_ok=False)
    if phase=='current' and contract_path != first_current_contract(path,doc):
        read_current_replay(path,doc,require_complete=True)
        _REPLAY_VERIFIED = True
    gate_result = None; gate_captures = None; gate_report = None
    if phase=='exposure':
        gate, gate_data = checked_gate_result(path, doc)
        gate_result = pin(repo, Path(str(gate)+'.result.json'))
        gate_captures = gate_data['captures']; gate_report = gate_data['report']
    union = [{k: r[k] for k in KEY} for r in load(checked(repo, doc['references']))['cells']]
    context = {'repo': str(repo), 'executionRoot': str(path), 'contract': str(contract_path),
               'batchPath': str(registered), 'batch': batch, 'phase': phase, 'output': str(output),
               'expectedCells': expected, 'baselineDocuments': doc['baselineDocuments'],
               'inputs': doc['inputs'], 'phaseDependencies': doc['phaseDependencies'],
               'unionExpectedCells': union, 'ownerUnionKeys': doc['phaseDependencies']['ownerUnionKeys'],
               'gateResult': gate_result, 'gateCaptures': gate_captures, 'gateReport': gate_report}
    _ACTIVE = (context, copy.deepcopy(context), sha(contract_path), sha(registered),
               phase=='current' or numerical is not None, doc, numerical)
    # The adapter imports this exact module instance; loading a second copy has no capability.
    sys.modules['w50_g1_dispatch'] = sys.modules[__name__]
    try:
        adapter = module(checked(repo, doc['adapter']), 'w50_g1_adapter')
        captures = (adapter.execute_current if phase == 'current' else adapter.execute)(context)
        require_context(context)
        if not isinstance(captures, dict) or captures.get('status') != 'CAPTURED':
            raise ValueError('Adapter did not complete the declared capture population')
        if phase=='current' and not _REPLAY_VERIFIED:
            raise ValueError('Replacement current batch did not prove the prior forty-two GPU bytes')
        receipt = admission.validate_captures(batch, captures, output)
        if phase in ('gate', 'exposure'):
            judge = module(checked(repo, doc['judge']), 'w50_g1_judge')
            report = judge.evaluate(context, captures)
            require_context(context)
            validate_report(doc, batch, expected, report, gate_result=gate_result)
        else:
            report = {'status': 'CAPTURED', 'captures': captures}
            if phase == 'fit':
                fitter = module(checked(repo, doc['instruments']['fit']), 'w50_g1_fitter')
                analysis = fitter.evaluate(context, captures)
                require_context(context)
                if not isinstance(analysis, dict) or not analysis or analysis.get('status') in ('PASS', 'NEITHER', GATE_SUCCESS):
                    raise ValueError('Fit analysis is not a gate verdict')
                report['analysis'] = analysis
        return write_sealed(Path(str(contract_path)+'.result.json'),
            {'contractSha256': sha(contract_path), 'claimSha256': sha(claim), 'report': report,
             'captureReceipt': receipt, 'captures': captures})
    finally:
        _ACTIVE = None
        _REPLAY_VERIFIED = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('execute', 'fit', 'gate', 'exposure', 'current'))
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--batch', required=True, type=Path)
    parser.add_argument('--contract', type=Path)
    parser.add_argument('--fit-record', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.command == 'execute':
        if not args.contract or not args.out: parser.error('execute needs --contract and --out')
        print(execute(args.root, args.contract, args.batch, args.out))
    elif args.command == 'gate':
        if not args.fit_record: parser.error('gate needs --fit-record')
        print(gate_contract(args.root, args.batch, args.fit_record))
    else:
        print({'fit': fit_contract, 'current': current_contract, 'exposure': exposure_contract}
              [args.command](args.root, args.batch))
