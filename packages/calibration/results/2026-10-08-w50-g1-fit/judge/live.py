"""W50 G1 LIVE judge role: the fixed per-cell landing rule's phase verdict (charter DL4, DL5d).

evaluate(context, {'measurement', 'owner', 'captures'}, config_pin) -> report, called by the
LIVE dispatcher in its exclusive analysis stage of the gate and of the one exposure. The
report is a value-bearing payload; the dispatcher seals it and validates it with current3's
validate_report. Nothing here prints, logs or formats a measured value; errors carry field
names and keys only (DL5k).

Gate. Exactly the exposed (gateKeys) rows are routed by judge/rules.route_row. A positive
gate is PASS_EXPOSED_OWNER_PENDING: every numeric row WITHIN (PASS), every DL5a reported row
REPORTED with finite readings and B null, every DL5b key UNMEASURED_EMPTY_SUPPORT with its
witness or REPORTED, every owner-contracts row PENDING_OWNER_UNION. ownerChecks and
targetChecks are PENDING_FULL_UNION and pendingOwnerKeys is the root's ordered closure.

Exposure. The complete union is the sealed gate report's exposed cells, this exposure's
routed rows (blind and historical prediction checks with their DL5d physical closure), the
owner referee's full-union report and the six W48 target aggregates over their unchanged
complete populations against their original references (judge/targets.py). PASS needs all
of them; anything else is NEITHER (DL4). Owner rows never pass on a partial population.

Routing decisions the charter text fixes and this module only maps:
* Input 64 (DL5j) is reported on both tiers; its gating condition is numerical identity of the
  law at the join, carried by the G0 numerical referee the dispatcher admitted the cohort
  under (fixedJoinPass). The rendered candidate/current difference is recorded, not gated.
* Missing evidence is UNMEASURED and never a pass, including a reported row whose readings are
  incomplete: validate_report admits REPORTED only with finite native/current/candidate.
* An owner axis passes when NOT_APPLICABLE, MEASURED within/reported, a named miss of an
  EXISTING record, or UNMEASURED under a source-owned exception of the root's owner contracts
  snapshot (owner_evidence.py's rule). A named outcome that would need a NEW owner record
  (M2's wouldRequireNewOwnerRecord) widens an exclusion and fails (charter clause 4).

Readings the text leaves open are marked DECISION below and listed in the G1 report.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import types

HERE = Path(__file__).resolve().parent
KEY = ('profile', 'renderer', 'scene', 'statistic')
GATE_SUCCESS = 'PASS_EXPOSED_OWNER_PENDING'
WITHHELD = {'blind', 'historical-prediction-check'}
SCHEMA = 'w50-judge-config-1'
REPORT = 'w50-judge-report-1'
AXES = ('M1', 'M2', 'C1', 'X1', 'L1', 'E2', 'coherence')
JOIN = 'REQUIRED_SEPARATE_JOIN_REFEREE'
READING_FIELDS = ('units', 'support', 'measurementStatus', 'nativeMeasurementStatus',
                  'currentMeasurementStatus', 'candidateMeasurementStatus', 'native', 'current',
                  'candidate', 'code', 'bar', 'B', 'originalBudgetB', 'reported',
                  'eligibleEmptySupport', 'routingOperands', 'candidateEstimator', 'reason',
                  'nativeReason', 'currentReason', 'candidateReason')
OUTSIDE = [
    'Clause 5 visual price: native/current/candidate views at 1x/2x are a parent stop, not a judge reading.',
    'Clause 5 identity and shader/CPU agreement: pre-fit proofs identityDigestsGoldens and '
    'shaderCpuAgreement, bound by the pre-fit evidence the contract names, not re-read here.',
]


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


T = source(HERE/'targets.py', 'w50_judge_live_targets')
R = T.R
N = R.N


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse(raw):
    def invalid(_):
        raise ValueError('Nonfinite JSON constant in judge input')
    return json.loads(raw, parse_constant=invalid)


def key(row):
    return tuple(row[k] for k in KEY)


def dispatcher(context):
    """The registered LIVE dispatcher, its live context and the exclusive analysis marker."""
    live = sys.modules.get('w50_g1_dispatch')
    if live is None:
        raise ValueError('Judge/fit analysis requires the registered live dispatcher')
    live.require_context(context)
    claim = context.get('executionClaim') or {}
    marker = Path(context['contract']+'.phase/analysis.started.json')
    if context.get('stage') != 'analysis' or Path(claim.get('path', '')) != marker or \
            not marker.is_file() or sha(marker) != claim.get('sha256'):
        raise ValueError('Analytical reading refuses before the authenticated full-union marker')
    return live


def root_of(context, live):
    root = live.sealed(context['executionRoot'])
    if Path(root['repo']).resolve() != Path(context['repo']).resolve() or root['inputs'] != context['inputs'] or \
            root['phaseDependencies'] != context['phaseDependencies']:
        raise ValueError('Analysis context differs from its sealed root')
    return root


def registered(context, live, root, pin):
    if pin not in root['inputs'] or pin not in context['inputs']:
        raise ValueError('Analysis input is not prospectively bound by the root')
    return parse(live.checked(context['repo'], pin).read_bytes())


def originals(context, live, root):
    """The original G0 inventory document and its rows by exact key, in declaration order."""
    document = parse(live.checked(context['repo'], root['references']).read_bytes())
    rows = document['cells']
    result = {key(r): r for r in rows}
    if len(result) != len(rows) or [list(k) for k in result] != [[c[k] for k in KEY] for c in context['unionExpectedCells']]:
        raise ValueError('Original inventory differs from the dispatcher union population')
    return document, result


def measurement(context, live, root, inventory, measured):
    """Authenticate the measurement role's output as its own exclusive phase snapshot."""
    cohort = context['batch']['cohort']
    if not isinstance(measured, dict) or measured.get('schema') != 'w50-phase-measurement-evidence-1' or \
            measured.get('status') != 'EVIDENCE_ONLY' or measured.get('phase') != context['phase'] or \
            measured.get('cohort') != cohort or \
            measured.get('candidateSha256s') != sorted(p['sha256'] for p in cohort) or \
            measured.get('referenceInventory') != root['references'] or \
            measured.get('gateResult') != context.get('gateResult') or \
            measured.get('executionClaim', context['executionClaim']) != context['executionClaim']:
        raise ValueError('Measurement evidence is not this phase, cohort, inventory or analysis claim')
    for name, field in (('executionRoot', 'executionRoot'), ('contract', 'contract'), ('batch', 'batchPath')):
        if measured.get(name) != {'path': context[field], 'sha256': sha(context[field])}:
            raise ValueError('Measurement evidence names another root, contract or batch')
    expected = [key(c) for c in context['expectedCells']]
    if len(set(expected)) != len(expected) or measured.get('expectedKeys') != [list(k) for k in sorted(expected)]:
        raise ValueError('Measurement keys differ from the phase contract')
    rows = measured.get('rows')
    found = [key(r) for r in rows]
    if len(found) != len(set(found)) or set(found) != set(expected):
        raise ValueError('Measurement rows omit or add an original phase key')
    for item, row in zip(found, rows):
        if row.get('originalReference') != inventory[item] or row.get('role') != inventory[item]['role']:
            raise ValueError('Measurement row changed its original reference or role')
    snapshot = measured.get('snapshot') or {}
    path = Path(snapshot.get('path', ''))
    if not path.is_absolute() or path.resolve() != path or not path.is_relative_to(Path(context['output'])) or \
            not path.is_file() or sha(path) != snapshot.get('sha256') or \
            parse(path.read_bytes()) != json.loads(json.dumps({k: v for k, v in measured.items() if k != 'snapshot'})):
        raise ValueError('Measurement evidence differs from its exclusive phase snapshot')
    return dict(zip(found, rows))


def route(rows, root):
    return R.route_rows(rows, inventory_sha256=root['references']['sha256'],
                        reported_keys=root['reportedKeys'], empty_support_keys=root['emptySupportKeys'])


def compact_reading(source_reading):
    """Every reading with its candidate identity, small enough for the sealed gate report."""
    out = {k: copy.deepcopy(source_reading[k]) for k in READING_FIELDS if k in source_reading}
    evidence = source_reading.get('evidence', {})
    out['evidence'] = {'candidate': copy.deepcopy(evidence.get('candidate'))}
    for side in ('native', 'current'):
        if isinstance(evidence.get(side), dict):
            out['evidence'][side] = {'numericIdentity': copy.deepcopy(evidence[side].get('numericIdentity'))}
    return out


def compact_route(routed):
    return {k: copy.deepcopy(routed[k]) for k in ('status', 'checks', 'diagnostics', 'failures',
            'unmeasured', 'complete', 'numericalIdentity', 'emptySupportWitnesses') if k in routed}


def scalar(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def join_identity(context, live, root):
    """The numerical referee the dispatcher admitted this cohort under, re-run unchanged."""
    claim = context['logicalClaim']
    path = Path(claim['path'])
    if not path.is_file() or sha(path) != claim['sha256']:
        raise ValueError('Logical phase claim changed')
    admitted = parse(path.read_bytes()).get('numericalAdmission')
    if live.admission_module(root).validate_numerical(root, context['batch']) != admitted:
        raise ValueError('Numerical admission differs from the logical phase claim')
    report = parse(live.checked(context['repo'], admitted).read_bytes())
    if report.get('candidateSha256s') != sorted(p['sha256'] for p in context['batch']['cohort']):
        raise ValueError('Numerical admission names another cohort')
    return admitted, report.get('status') == 'PASS' and report.get('fixedJoinPass') is True


def held_difference(row):
    """Candidate minus current at input64, recorded beside the identity condition (DL5j)."""
    reading = row['readings'][row['statistic']]
    k, c = reading.get('candidate'), reading.get('current')
    if k is None or c is None:
        return None
    k, c = (k, c) if isinstance(k, list) else ([k], [c])
    return [a - b for a, b in zip(k, c)]


def cell(item, row, routed, root, *, join, witness):
    """Map one routed original key to the report's per-cell status."""
    cell = {**dict(zip(KEY, item)), 'role': row['role'], 'route': compact_route(routed),
            'readings': {name: compact_reading(value) for name, value in row['readings'].items()},
            'evidence': copy.deepcopy(row.get('evidence'))}
    reported = item in {tuple(k) for k in root['reportedKeys']}
    status = routed['status']
    if item[3] == 'owner-contracts':
        cell['status'] = 'PENDING_OWNER_UNION'
    elif reported and status == 'UNMEASURED_EMPTY_SUPPORT':
        pin = witness(item, row)
        cell.update(status='UNMEASURED_EMPTY_SUPPORT', native=None, current=None, candidate=None,
                    fidelity=None, value=None, B=None, emptySupportWitness=pin)
    elif reported:
        value = row['readings'][item[3]]
        complete = status == 'DIAGNOSTIC' and all(scalar(value.get(k)) for k in ('native', 'current', 'candidate'))
        cell.update(status='REPORTED' if complete else 'UNMEASURED', B=None,
                    **{k: copy.deepcopy(value.get(k)) for k in ('native', 'current', 'candidate')})
    elif status == 'WITHIN':
        cell['status'] = 'PASS'
    elif status == 'EXCEEDS':
        cell['status'] = 'FAIL'
    elif status == 'UNMEASURED':
        cell['status'] = 'UNMEASURED'
    elif status == 'DIAGNOSTIC' and routed.get('numericalIdentity') == JOIN:
        cell.update(status='PASS' if join else 'FAIL', joinIdentity=join, heldDifference=held_difference(row))
    else:
        raise ValueError('Required original key has no declared referee')
    if row['role'] == 'blind':
        # DL5g (1): a blind row without real exposure content pins blocks.
        pin = row.get('nativeEvidence') or {}
        path = Path(pin.get('path', ''))
        if not path.is_file() or sha(path) != pin.get('sha256'):
            cell['status'] = 'UNMEASURED'
        cell['nativeEvidence'] = copy.deepcopy(pin)
    return cell


def wanted(item, phase, root):
    if item in {tuple(k) for k in root['reportedKeys']}:
        return {'REPORTED', 'UNMEASURED_EMPTY_SUPPORT'} if item in {tuple(k) for k in root['emptySupportKeys']} \
            else {'REPORTED'}
    if item[3] == 'owner-contracts' and phase == 'gate':
        return {'PENDING_OWNER_UNION'}
    return {'PASS'}


# Owner union (exposure only) ----------------------------------------------------------------

def _at(value, path):
    for part in path.split('.'):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _same(a, b):
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)


def axis(profile, scene, evidence, contract):
    """(status, reason) for one owner axis, using the snapshot's source-owned reading schema."""
    if not isinstance(evidence, dict):
        return 'UNMEASURED', 'Owner axis evidence absent'
    state = evidence.get('state')
    if state == 'NOT_APPLICABLE':
        return ('PASS', 'not applicable') if evidence.get('reason') else ('UNMEASURED', 'Unexplained applicability')
    schema = contract['readingSchema']
    if state == 'UNMEASURED':
        for exception in schema['unmeasuredExceptions']:
            if exception.get('kind') == 'named-cell' and (exception.get('identity') != 'profile/scene' or
                    f'{profile}/{scene}' not in exception.get('keys', [])):
                continue
            if exception.get('kind') not in ('named-cell', 'diagnostic-only'):
                continue
            equality = exception.get('evidenceEquals')
            if isinstance(equality, dict) and equality and evidence.get('reason') and \
                    all(_same(_at(evidence, k), v) for k, v in equality.items()):
                return 'PASS', 'source-owned '+exception['kind']+' exception'
        return 'UNMEASURED', 'Owner axis UNMEASURED without a source-owned exception'
    if state != 'MEASURED':
        return 'UNMEASURED', 'Invalid owner evidence state'
    missing = [p for p in schema['requiredFinite'] if not _finite(_at(evidence, p))]
    missing += [p for p in schema['requiredArrays'] if not isinstance(_at(evidence, p), list) or not _at(evidence, p)]
    for rule in schema['conditionalFinite']:
        if not _same(_at(evidence, rule['unless']['field']), rule['unless']['equals']):
            missing += [p for p in rule['paths'] if not _finite(_at(evidence, p))]
    if missing:
        return 'UNMEASURED', 'Missing source-owned owner reading: '+','.join(missing)
    verdict = evidence.get('verdict')
    if verdict in ('within', 'reported'):
        return 'PASS', verdict
    if verdict == 'named-miss':
        if evidence.get('wouldRequireNewOwnerRecord') is True:
            return 'FAIL', 'Named outcome would require a new owner record (exclusion widened)'
        return 'PASS', 'existing named owner record'
    if verdict == 'failure':
        return 'FAIL', 'Owner verdict failure'
    return 'UNMEASURED', 'Owner evidence carries no verdict'


def owner_cell(identity, axes, contracts):
    """One owner-referee cell over all seven axes; any failure fails, any gap is UNMEASURED."""
    profile, _, scene = identity.split('/', 2)
    if not isinstance(axes, dict) or set(axes) != set(AXES):
        return {'status': 'UNMEASURED', 'axes': {}, 'reason': 'Owner cell lacks the seven original axes'}
    results = {name: axis(profile, scene, axes[name], contracts['axes'][name]) for name in AXES}
    statuses = {s for s, _ in results.values()}
    status = 'FAIL' if 'FAIL' in statuses else 'UNMEASURED' if 'UNMEASURED' in statuses else 'PASS'
    return {'status': status, 'axes': {name: {'status': s, 'reason': r, 'state': axes[name].get('state'),
            'verdict': axes[name].get('verdict')} for name, (s, r) in results.items()}}


def _leaves(value):
    if isinstance(value, dict) and 'state' in value:
        return {'': value}
    return value if isinstance(value, dict) else {}


def owner_union(context, owner, contracts):
    """Authenticate the owner referee's full-union report and grade every owner check."""
    if not isinstance(owner, dict) or set(owner) != {'report', 'snapshot'}:
        raise ValueError('Exposure requires the owner referee report and its snapshot')
    output = Path(context['output'])
    snapshot = owner['snapshot']
    path = Path(snapshot.get('path', ''))
    if path != output/'owner-candidate.snapshot.json' or not path.is_file() or sha(path) != snapshot.get('sha256'):
        raise ValueError('Owner snapshot is not this invocation output')
    report_path = output/'owner-candidate.report.json'
    if not report_path.is_file() or parse(report_path.read_bytes()) != owner['report']:
        raise ValueError('Owner report differs from its exclusive output file')
    report = owner['report']
    live = report.get('liveUnion') or {}
    gate = context['gateResult']
    if live.get('ownerKeys') != context['ownerUnionKeys'] or live.get('cohort') != context['batch']['cohort'] or \
            (live.get('gateResult') or {}).get('sha256') != gate['sha256'] or \
            Path(live['gateResult']['path']).resolve() != (Path(context['repo'])/gate['path']).resolve() or \
            live.get('snapshot') != snapshot:
        raise ValueError('Owner report names another union, cohort or gate')
    cells = report.get('cells')
    owners = {'/'.join(k[:3]) for k in context['ownerUnionKeys']}
    if not isinstance(cells, dict) or not owners <= set(cells):
        raise ValueError('Owner report omits an original owner key')
    graded = {identity: owner_cell(identity, axes, contracts) for identity, axes in sorted(cells.items())}
    aggregates = []
    for name, evidence in sorted((report.get('aggregates') or {}).items()):
        ok = isinstance(evidence, dict) and evidence.get('state') == 'MEASURED' and evidence.get('verdict') == 'within'
        aggregates.append({'name': name, 'status': 'PASS' if ok else 'FAIL' if
                           (evidence or {}).get('verdict') == 'failure' else 'UNMEASURED'})
    if not any(a['name'] == 'C1' for a in aggregates):
        aggregates.append({'name': 'C1', 'status': 'UNMEASURED'})
    intrinsic = []
    expected = {'X75': 12, 'X76': {'0.25', '0.5'}}
    for name, shape in expected.items():
        leaves = _leaves((report.get('intrinsic') or {}).get(name))
        complete = len(leaves) == shape if isinstance(shape, int) else set(leaves) == shape
        for member, evidence in sorted(leaves.items()):
            ok = evidence.get('state') == 'MEASURED' and evidence.get('verdict') == 'within'
            intrinsic.append({'name': name, 'member': member, 'status': 'PASS' if ok else
                              'FAIL' if evidence.get('verdict') == 'failure' else 'UNMEASURED'})
        if not complete:
            intrinsic.append({'name': name, 'member': '*', 'status': 'UNMEASURED'})
    # DECISION (owner context): the 105 low-end path cells are in the owner referee's 745-cell
    # context but carry no owner-contracts key, because G0 keyed them by their path statistic.
    # Clause 4 retains every applicable owner contract at both positions, so their per-cell
    # owner verdicts gate here too; nothing is added beyond the owner's own bounds.
    context_checks = [{'id': identity, **value} for identity, value in graded.items() if identity not in owners]
    return {'cells': graded, 'aggregates': aggregates, 'intrinsic': intrinsic, 'context': context_checks,
            'report': {'path': str(report_path), 'sha256': sha(report_path)}, 'snapshot': copy.deepcopy(snapshot)}


# Evaluation ---------------------------------------------------------------------------------

def inputs(context, live, root, config_pin):
    config = registered(context, live, root, config_pin)
    if not isinstance(config, dict) or config.get('schema') != SCHEMA or set(config) != {
            'schema', 'references', 'binding', 'ownerContracts', 'targets'}:
        raise ValueError('Unknown judge config')
    if config['references'] != root['references'] or config['ownerContracts'] != root.get('ownerContracts'):
        raise ValueError('Judge config names another inventory or owner snapshot')
    binding = registered(context, live, root, config['binding'])
    if binding.get('original') != root['references'] or binding.get('reportedKeys') != root['reportedKeys'] or \
            binding.get('emptySupportKeys') != root['emptySupportKeys'] or \
            binding.get('ownerContracts') != root.get('ownerContracts'):
        raise ValueError('Root reported/empty-support keys differ from the registered binding')
    contracts = parse(live.checked(context['repo'], root['ownerContracts']).read_bytes())
    if contracts.get('schema') != 'w50-owner-contracts-1' or set(contracts.get('axes', {})) != set(AXES):
        raise ValueError('Owner contracts snapshot lacks its seven axes')
    targets = T.validate_config(registered(context, live, root, config['targets']))
    if targets['inventory'] != root['references']:
        raise ValueError('Target contracts must read the original inventory')
    cut = registered(context, live, root, targets['cut'])
    return config, contracts, targets, cut


def preflight(document, root, cut, targets):
    """Build every target reference with no candidate, so membership, cut cross-binding and
    Reference construction fail before the one exposure rather than inside it."""
    T.contracts(document, root['references'], cut, targets, {})


def empty_witness(context, live, phase):
    """DL5b exposed witnesses are the completed reference's; DL5c blind ones the exposure's.

    The exposure's are the native role's checkpointed payload, {ready, nativeExposure:
    exposure/prepare.py artifacts, artifacts}, whose emptySupportWitnesses name one zero-mask
    witness per eligible (profile, scene), shared by both tiers' keys."""
    native = live.qualification_native(context) if phase == 'exposure' else None
    witnesses = None
    if native is not None:
        if not isinstance(native, dict) or native.get('ready') is not True or \
                not isinstance(native.get('nativeExposure'), dict):
            raise ValueError('Exposure native checkpoint is not one ready preparation')
        witnesses = {(w['profile'], w['scene']): w['pin']
                     for w in native['nativeExposure'].get('emptySupportWitnesses', [])}
    def lookup(item, row):
        if row['role'] == 'blind':
            if witnesses is None or (item[0], item[2]) not in witnesses:
                raise ValueError('Eligible blind empty support has no exposure zero-support witness')
            return copy.deepcopy(witnesses[(item[0], item[2])])
        pin = (row.get('reference') or {}).get('emptySupportWitness')
        if not isinstance(pin, dict):
            raise ValueError('Exposed empty support has no completed-reference witness')
        return copy.deepcopy(pin)
    return lookup


def evaluate(context, evidence, config_pin):
    live = dispatcher(context)
    phase = context.get('phase')
    if phase not in ('gate', 'exposure') or context['batch'].get('phase') != phase:
        raise ValueError('The judge issues only gate and exposure verdicts')
    if not isinstance(evidence, dict) or set(evidence) != {'measurement', 'owner', 'captures'}:
        raise ValueError('Judge evidence must be measurement, owner and captures')
    if (phase == 'gate') != (evidence['owner'] is None):
        raise ValueError('The owner referee runs on the full union at exposure only')
    if not isinstance(evidence['captures'], dict) or evidence['captures'].get('status') != 'CAPTURED' or \
            evidence['captures'].get('candidateSha256s') != sorted(p['sha256'] for p in context['batch']['cohort']):
        raise ValueError('Judge captures are not this cohort')
    root = root_of(context, live)
    config, contracts, targets, cut = inputs(context, live, root, config_pin)
    document, inventory = originals(context, live, root)
    preflight(document, root, cut, targets)
    rows = measurement(context, live, root, inventory, evidence['measurement'])
    admitted, join = join_identity(context, live, root)
    lookup = empty_witness(context, live, phase)
    routed = dict(zip(rows, route(list(rows.values()), root)))
    fresh = {item: cell(item, rows[item], routed[item], root, join=join, witness=lookup) for item in rows}
    cohort = sorted(p['sha256'] for p in context['batch']['cohort'])
    dependencies = context['phaseDependencies']
    report = {'schema': REPORT, 'phase': phase, 'candidateSha256s': cohort,
              'cohort': copy.deepcopy(context['batch']['cohort']), 'config': copy.deepcopy(config_pin),
              'inventory': copy.deepcopy(root['references']), 'measurement': copy.deepcopy(evidence['measurement']['snapshot']),
              'numericalAdmission': copy.deepcopy(admitted), 'joinIdentity': join, 'outsideJudge': list(OUTSIDE)}
    if phase == 'gate':
        if set(rows) != {tuple(k) for k in dependencies['gateKeys']}:
            raise ValueError('Gate rows differ from the exposed physical closure')
        cells = [fresh[key(c)] for c in context['expectedCells']]
        report.update(ownerChecks='PENDING_FULL_UNION', pendingOwnerKeys=copy.deepcopy(dependencies['pendingOwnerKeys']),
                      targetChecks='PENDING_FULL_UNION', targets=R.route_targets(None, full_union=False))
        failed = [c for c in cells if c['status'] not in wanted(key(c), phase, root)]
        report['status'] = GATE_SUCCESS if not failed else 'NEITHER'
    else:
        gate_report = context.get('gateReport') or {}
        if gate_report.get('schema') != REPORT or gate_report.get('phase') != 'gate' or \
                gate_report.get('status') != GATE_SUCCESS or gate_report.get('candidateSha256s') != cohort:
            raise ValueError('Exposure requires this judge\'s same-candidate qualified gate report')
        gate_cells = {key(c): c for c in gate_report['cells']}
        if set(gate_cells) != {tuple(k) for k in dependencies['gateKeys']} or \
                set(rows) != {tuple(k) for k in dependencies['exposureKeys']} or set(gate_cells) & set(rows):
            raise ValueError('Gate and exposure rows do not partition the original union')
        for item, value in gate_cells.items():
            if value.get('status') not in wanted(item, 'gate', root):
                raise ValueError('Qualified gate report carries an unqualified cell')
        graded = owner_union(context, evidence['owner'], contracts)
        cells = []
        for original in context['unionExpectedCells']:
            item = key(original)
            value = copy.deepcopy(gate_cells[item] if item in gate_cells else fresh[item])
            value['phase'] = 'gate' if item in gate_cells else 'exposure'
            if item[3] == 'owner-contracts':
                owner = graded['cells'].get('/'.join(item[:3]), {'status': 'UNMEASURED', 'axes': {}})
                value.update(status=owner['status'], owner=owner['axes'])
            cells.append(value)
        candidates = {}
        for value in cells:
            reading = value.get('readings', {}).get(T.STATISTIC)
            if value['statistic'] == T.STATISTIC and value['renderer'] == 'webgpu' and reading is not None:
                candidates[key(value)] = reading
        contract = T.contracts(document, root['references'], cut, targets, candidates)
        target_checks = R.route_targets(contract, full_union=True)
        report.update(ownerChecks='FULL_UNION', pendingOwnerKeys=[], targetChecks='FULL_UNION',
                      targets=target_checks, gateResult=copy.deepcopy(context['gateResult']),
                      owner={k: graded[k] for k in ('aggregates', 'intrinsic', 'context', 'report', 'snapshot')})
        failed = [c for c in cells if c['status'] not in wanted(key(c), phase, root)]
        failed += [t for t in target_checks if t['status'] != 'WITHIN']
        failed += [c for group in ('aggregates', 'intrinsic', 'context') for c in graded[group] if c['status'] != 'PASS']
        report['status'] = 'PASS' if not failed else 'NEITHER'
    report['cells'] = cells
    live.require_context(context)
    # The sealed result is JSON; normalize now so the in-memory and archived reports agree.
    return json.loads(json.dumps(report, allow_nan=False))


def public_summary(report):
    """Metadata-only projection of a judge report: statuses, counts and keys, never a reading."""
    counts = {}
    for value in report['cells']:
        counts[value['status']] = counts.get(value['status'], 0) + 1
    blocking = sorted([c[k] for k in KEY] for c in report['cells']
                      if c['status'] not in ('PASS', 'REPORTED', 'UNMEASURED_EMPTY_SUPPORT', 'PENDING_OWNER_UNION'))
    owner = report.get('owner') or {}
    return {'schema': 'w50-judge-public-summary-1', 'phase': report['phase'], 'status': report['status'],
            'candidateSha256s': list(report['candidateSha256s']), 'ownerChecks': report['ownerChecks'],
            'targetChecks': report['targetChecks'], 'cellCounts': dict(sorted(counts.items())),
            'blockingKeys': blocking,
            'targets': [{'target': t['target'], 'scale': t['scale'], 'status': t['status']} for t in report['targets']],
            'ownerUnion': {group: sorted(str(c.get('name', c.get('id')))+(':'+c['member'] if c.get('member') else '')
                                         for c in owner.get(group, []) if c['status'] != 'PASS')
                           for group in ('aggregates', 'intrinsic', 'context')}}


def source_probe():
    T.source_probe()
    axis('p', 's', {'state': 'NOT_APPLICABLE', 'reason': 'probe'}, {'readingSchema': {}})
    return {'status': 'SOURCE_ONLY'}
