"""Authenticated fit/gate/exposure measurement evidence, not a phase or owner verdict.

Only the registered LIVE dispatcher's analysis stage can invoke this reader: it runs after the
exclusive full-union analysis marker, over the complete capture union. Each receipt is bound to
its OWN member run (dispatcher.resolve_capture_run: the receipt must equal its immutable member
checkpoint) under read admission; LIVE issues render admission to capture members only. Fixed
config and completed-reference/current/canonical reports are prospective root inputs; candidate
artifacts belong to this logical phase's members. Every fresh pair is replayed through the
root-bound DL5h helper and the transports' pure report validators, and only its FIRST image is
measured.

Snapshots are exclusive scratch evidence beneath context.output, never execution seals. A
failed read retains its directory and cannot silently run again. Original rows, adopted
budgets and history remain unchanged beside additive readings. Owner rows are opaque pointers;
any gate pending annotation is disposition metadata, not a measured result or owner evaluation.
The phase body and every keyed row name the analysis claim (executionClaim) they were read under.
"""
import copy
import hashlib
import os
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
KEY = ('profile', 'renderer', 'scene', 'statistic')


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


Q = source(HERE/'projection.py', 'w50_phase_projection')
S = source(HERE/'phase_sources.py', 'w50_phase_sources')


def write_once(path, value):
    raw = Q.encoded(value)
    with Path(path).open('xb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())
    return {'path': str(Path(path)), 'sha256': hashlib.sha256(raw).hexdigest()}


def unique(rows):
    keys = [tuple(r[k] for k in KEY) for r in rows]
    if len(keys) != len(set(keys)): raise ValueError('Duplicate original measurement key')
    return dict(zip(keys, rows))


def inputs(context, dispatcher, config_pin):
    root = dispatcher.sealed(context['executionRoot'])
    def registered(pin, *, parse=False):
        if pin not in root['inputs'] or pin not in context['inputs']:
            raise ValueError('Measurement input is not bound by the actual root/context')
        path = dispatcher.checked(context['repo'], pin)
        return dispatcher.load(path) if parse else path
    config = registered(config_pin, parse=True)
    if config.get('schema') != 'w50-phase-measurement-inputs-1' or set(config) != {
            'schema', 'completedReferences', 'completedCurrentEvidence', 'canonicalReferenceEvidence', 'native'}:
        raise ValueError('Unknown phase measurement config')
    native = config['native']
    if set(native) != {'batch', 'scenes', 'reports'} or set(native['reports']) != {'calibration', 'validation'}:
        raise ValueError('Measurement needs exactly the original exposed native inputs')
    if config['completedCurrentEvidence'] != root.get('currentEvidence'):
        raise ValueError('Measurement current evidence is not the root-bound composed current evidence')
    for pin in (config['completedCurrentEvidence'], config['canonicalReferenceEvidence'],
                native['batch'], native['scenes'], *native['reports'].values()):
        registered(pin)
    contract = dispatcher.sealed(context['contract'])
    prefit = dispatcher.load(dispatcher.checked(context['repo'], contract['preFitEvidence']))
    if prefit.get('references') != config['completedReferences']:
        raise ValueError('Measurement references differ from the invocation pre-fit proof')
    completed = unique(registered(config['completedReferences'], parse=True)['cells'])
    original = unique(dispatcher.load(dispatcher.checked(context['repo'], root['references']))['cells'])
    if set(completed) != set(original):
        raise ValueError('Completed references changed original key membership')
    for key, row in original.items():
        for field in ('role', 'support', 'currentGeneration', 'currentDocumentPair', 'historical',
                      'nativeIdentity', 'referenceIdentity'):
            if completed[key].get(field) != row.get(field):
                raise ValueError('Completed reference changed original provenance/history')
    return root, config, original, completed


def members(context, captures, dispatcher, root):
    """Bind every receipt to its own logical member run; population and lanes stay exact."""
    dispatcher.admission_module(root).validate_captures(context['batch'], captures, context['output'])
    expected = set()
    for run in context['batch']['runs']:
        lanes = ['candidate']
        if context['phase'] == 'exposure':
            if run.get('baselineCandidate') not in context['baselineDocuments']:
                raise ValueError('Exposure measurement requires its registered same-cell baseline')
            lanes.append('current')
        for scene in run['scenes']:
            for lane in lanes:
                expected.add((run['profile'], run['renderer'], scene, lane))
    result = {}
    for receipt in captures['captures']:
        if not receipt.get('repeatPair') or not receipt.get('repeatAdmission'):
            raise ValueError('Measurement needs one original member with both fresh repeat pins')
        # The member's own derived run (per-member captureRoot/matrixPath, baseline lane already
        # carrying its baseline candidate); a receipt differing from its checkpoint refuses.
        run = dispatcher.resolve_capture_run(context, receipt)
        dispatcher.require_read_admission(context, run, current=receipt['lane'] == 'current')
        if receipt.get('sceneSource') != run.get('sceneSource'):
            raise ValueError('Measurement receipt differs from its member scene source')
        key = tuple(receipt[k] for k in KEY[:3]) + (receipt['lane'],)
        if key in result: raise ValueError('Duplicate measurement capture member')
        result[key] = (run, receipt)
    if set(result) != expected: raise ValueError('Measurement capture population differs from phase batch')
    return result


def measure_phase(context, captures, config_pin):
    dispatcher = sys.modules.get('w50_g1_dispatch')
    if dispatcher is None: raise ValueError('Phase measurement requires the registered live dispatcher')
    dispatcher.require_context(context)
    if context.get('stage') != 'analysis':
        raise ValueError('Phase measurement runs only after the full-union analysis marker')
    phase = context.get('phase')
    if phase not in ('fit', 'gate', 'exposure') or context['batch'].get('phase') != phase:
        raise ValueError('Only matching live fit/gate/exposure phases may be measured')
    root, config, originals, completed = inputs(context, dispatcher, config_pin)
    expected = unique(context['expectedCells'])
    if not expected or not set(expected) <= set(originals):
        raise ValueError('Measurement expected keys differ from the admitted original subset')
    if phase != 'exposure' and any(originals[k]['role'] == 'blind' for k in expected):
        raise ValueError('Blind measurement is exposure-only')
    bound = members(context, captures, dispatcher, root)
    triples = {k[:3] for k in expected}
    if triples != {k[:3] for k in bound} or set(expected) != {k for k in originals if k[:3] in triples}:
        raise ValueError('Measurement keys omit or add an original phase statistic')
    destination = Path(context['output'])/'measurement'
    destination.mkdir(exist_ok=False)
    body = {'schema': 'w50-phase-measurement-evidence-1', 'status': 'EVIDENCE_ONLY', 'phase': phase,
        'candidateSha256s': sorted(p['sha256'] for p in context['batch']['cohort']),
        'cohort': copy.deepcopy(context['batch']['cohort']), 'config': copy.deepcopy(config_pin),
        'referenceInventory': copy.deepcopy(root['references']),
        'completedReferences': copy.deepcopy(config['completedReferences']),
        'expectedKeys': [list(k) for k in sorted(expected)], 'rows': [],
        'gateResult': copy.deepcopy(context.get('gateResult')),
        'executionClaim': copy.deepcopy(context['executionClaim'])}
    for name, field in (('executionRoot', 'executionRoot'), ('contract', 'contract'), ('batch', 'batchPath')):
        body[name] = {'path': context[field], 'sha256': dispatcher.sha(context[field])}
    backend = S.PhaseSources(context, root, config)
    reported = {tuple(k) for k in root['reportedKeys']}
    empty = {tuple(k) for k in root['emptySupportKeys']}
    for triple in sorted(triples):
        keys = sorted(k for k in expected if k[:3] == triple)
        originals_for_member = [originals[k] for k in keys]
        run, receipt = bound[triple + ('candidate',)]
        candidate = backend.measure_member(run, receipt, originals_for_member)
        baseline = None; baseline_receipt = None
        if phase == 'exposure':
            baseline_run, baseline_receipt = bound[triple + ('current',)]
            baseline = backend.measure_member(baseline_run, baseline_receipt, originals_for_member)
        for key in keys:
            original, reference = originals[key], completed[key]
            row = {k: copy.deepcopy(original[k]) for k in KEY}
            for field in ('role', 'support', 'nativeIdentity', 'referenceIdentity', 'currentGeneration',
                          'currentDocumentPair'):
                if field in original: row[field] = copy.deepcopy(original[field])
            row.update(originalReference=copy.deepcopy(original), reference=copy.deepcopy(reference),
                historical=copy.deepcopy(original.get('historical', [])), readings={},
                candidateCapture=copy.deepcopy(receipt), material=copy.deepcopy(candidate['material']),
                arguments=copy.deepcopy(candidate.get('arguments', [])),
                **copy.deepcopy(candidate['declaration']))
            if key[3] == 'owner-contracts':
                row['measurementStatus'] = 'POINTERS_ONLY'
                if phase == 'gate': row['disposition'] = 'PENDING_OWNER_UNION'
            else:
                for name in Q.statistic_names(original, candidate['declaration']):
                    measured = candidate['statistics'][name]
                    if original['role'] == 'blind':
                        current, current_evidence = baseline['statistics'][name], baseline['evidence']
                    else:
                        current, current_evidence = backend.current_measurement(original, name=name)
                    value = Q.reading(measured, current, candidate['evidence'], current_evidence,
                        reported=key in reported, eligible_empty=key in empty)
                    value['originalBudgetB'] = copy.deepcopy(original.get('B')) if name == key[3] else None
                    value['evidence']['historical'] = Q.histories(original, root['references'], name)
                    if name == key[3]:
                        value = Q.frozen_primary(original, reference, value,
                            measured.get('productionStatistic'), root['references'])
                    if baseline is not None and original['role'] != 'blind':
                        value['exposureBaseline'] = Q.reading(baseline['statistics'][name], None,
                            baseline['evidence'], {}, reported=key in reported, eligible_empty=key in empty)
                    row['readings'][name] = value
                row['measurementStatus'] = 'MEASUREMENT_EVIDENCE'
            if original['role'] == 'blind':
                envelope = backend.blind_envelope(original, candidate)
                envelope_path = destination/(Q.digest({'key': list(key), 'kind': 'native'})+'.json')
                row['nativeEvidence'] = write_once(envelope_path, envelope)
                row['currentCapture'] = copy.deepcopy(baseline_receipt)
                primary = row['readings'][key[3]]
                # validate_blind_rows binds row['native'] to the native report's aggregate. A
                # native side the projection left UNMEASURED has no value to bind: a reported
                # key's defect or incomplete reading (DL5m (4)), or a statistic the not-ready
                # read stopped (DL5n), whose aggregate may still carry the stopped spread. The
                # field is omitted and the rest of the envelope still binds.
                if primary['nativeMeasurementStatus'] != 'UNMEASURED':
                    row['native'] = copy.deepcopy(primary['native'])
                row['readings'][key[3]]['evidence']['native']['nativeEvidence'] = copy.deepcopy(row['nativeEvidence'])
            row_body = {'schema': 'w50-keyed-measurement-evidence-1',
                'phase': phase, 'executionRoot': body['executionRoot'], 'contract': body['contract'],
                'batch': body['batch'], 'cohort': body['cohort'], 'referenceInventory': body['referenceInventory'],
                'completedReferences': body['completedReferences'], 'config': body['config'],
                'gateResult': body['gateResult'], 'executionClaim': body['executionClaim'],
                'row': copy.deepcopy(row)}
            row['evidence'] = write_once(destination/(Q.digest(list(key))+'.json'), row_body)
            body['rows'].append(row)
    blind = [r for r in body['rows'] if r['role'] == 'blind']
    if blind: backend.validate_blind_rows(blind)
    dispatcher.require_context(context)
    body['snapshot'] = write_once(destination/'phase.json', body)
    return body


def source_probe():
    S.source_probe()
    return {'status': 'SOURCE_ONLY'}
