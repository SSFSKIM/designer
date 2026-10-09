"""W50 G1 LIVE fit role: the single rendered point's exposed readings and selection quantities.

evaluate(context, measured, config_pin) -> analysis, called by the LIVE dispatcher in the fit
phase's exclusive analysis stage after the measurement role. It is evidence for the frozen
gate, never a verdict: the analysis carries no PASS, NEITHER, gate status or per-row
WITHIN/EXCEEDS, and the dispatcher refuses one that does. The one joint analytical point was
proposed by fit/execution.py's initializer before rendering; nothing here searches, refits
or chooses among coefficients (charter DL4: no second point).

The selection quantities are the charter's order, declared in part 2 (fit-declaration.json
"selection"): minimum worst exposed low-end level error, then minimum mean absolute low-end
level error, then minimum squared normalised coefficient distance from current over the
declared range, then lexicographic candidate id. Withheld cells never enter (they are not in
a fit batch, and their presence refuses).

DECISION (level population): "low-end level error" is read as every WebGPU absolute-level
component that clauses 1-2 gate (judge/rules 'absolute-level': new uniform/span inputs 0-40
deep8 and centre8 per channel, canonical impulse deep8/far24 luma mean and median, canonical
dark-solid deep8 per channel, new structured level rows), in encoded codes per channel. CSS
level components are recorded separately because DL5i gates CSS by error growth, not by an
absolute closure. Input 64 and DL5a reported rows are outside clauses 1-2.

DECISION (distance origin): current is gate0, whose chart rows are unread at strength 0; their
resolved leaves are the identity-table defaults [0, 0, 0, 0] (renderer-webgpu material.ts),
the same origin fit/uniform.py's squaredNormalizedDistance uses. Strength is fixed at 1 by the
candidate domain and is not a free coefficient.

DECISION (id): a cohort's id is its two candidate document SHA-256s, sorted and joined by '+'.

Before reading the measurement it also reads the registered judge's config, binding, target
config and cut and builds every target reference, and runs the registered owner's metadata-only
preflight (owner-candidate/live.preflight), so a root wiring fault or owner drift surfaces here
and not inside the gate's or the exposure's one exclusive analysis.

fit_record(execution_root, completed) builds the metadata-only w50-g1-fit-record-1 body that
names the ONE completed fit result; the caller writes it exclusively and passes it to the
gate contract. Nothing here prints, logs or formats a measured value (DL5k).
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
SCHEMA = 'w50-fit-analysis-config-1'
ANALYSIS = 'w50-fit-analysis-1'
VERDICTS = {'PASS', 'NEITHER', 'PASS_EXPOSED_OWNER_PENDING'}
SELECTION = ['Minimum worst exposed low-end level error', 'Minimum mean absolute low-end level error',
             'Minimum squared normalized coefficient distance from current over range[0,1]',
             'Lexicographic candidate id']
ROWS = (44, 96, 160)
IDENTITY_ROW = [0, 0, 0, 0]


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


J = source(HERE.parent/'judge/live.py', 'w50_fit_live_judge')
O = source(HERE.parent/'owner-candidate/live.py', 'w50_fit_live_owner')
KEY = J.KEY


def _verdict_free(analysis):
    for field in ('status', 'verdict', 'gateStatus'):
        if analysis.get(field) in VERDICTS:
            raise ValueError('A fit analysis cannot carry a phase verdict')
    return analysis


def _document(repo, pin, base=None):
    path = (Path(repo)/pin['path']).resolve() if base is None else (Path(base)/pin['path']).resolve()
    if not path.is_relative_to(Path(repo).resolve()) or not path.is_file() or J.sha(path) != pin['sha256']:
        raise ValueError('Changed or missing candidate document')
    return path, J.parse(path.read_bytes())


def charts(repo, pin):
    """Resolved dark chart rows per pose of one candidate/baseline document."""
    path, document = _document(repo, pin)
    position = document.get('glassTintAmount')
    if position not in (.25, .5):
        raise ValueError('Chart document has no declared glass position')
    patches = {slot: _document(repo, document['endpoints'][slot], path.parent)[1]['patch']
               for slot in ('active.dark', 'receded.dark')}
    resolved = {'active': patches['active.dark'], 'receded': {**patches['active.dark'], **patches['receded.dark']}}
    return {f'{pose}.dark.{position}': [list(resolved[pose].get(f'lowEnd{row}', IDENTITY_ROW)) for row in ROWS]
            for pose in ('active', 'receded')}


def distance(context, domain):
    """Squared normalised ordinate distance of the cohort's charts from current's."""
    candidate, current = {}, {}
    for pin in context['batch']['cohort']:
        candidate.update(charts(context['repo'], pin))
    for pin in context['baselineDocuments']:
        current.update(charts(context['repo'], pin))
    if set(candidate) != set(domain['endpoints']) or set(current) != set(domain['endpoints']):
        raise ValueError('Cohort and baseline must cover the four declared dark endpoints')
    span = domain['rankingNormalisationRange']
    total = 0.0
    for endpoint in domain['endpoints']:
        for a, b in zip(candidate[endpoint], current[endpoint]):
            if len(a) != len(domain['inputCodes']) or len(b) != len(domain['inputCodes']):
                raise ValueError('Chart rows must carry one ordinate per declared input code')
            total += sum(((x - y)/span)**2 for x, y in zip(a, b))
    return total, candidate


def readings(row):
    """Raw per-statistic native/current/candidate readings, without any comparison status."""
    fields = ('units', 'support', 'nativeMeasurementStatus', 'currentMeasurementStatus',
              'candidateMeasurementStatus', 'native', 'current', 'candidate')
    return {name: {k: copy.deepcopy(value.get(k)) for k in fields} for name, value in row['readings'].items()}


def level_components(routed, rule):
    out = []
    for check in routed['checks']:
        if check['rule'] == rule:
            for component in check['comparison']['components']:
                out.append({'statistic': check['statistic'], 'channel': component['name'],
                            'error': component['error'], 'currentError': component['current_error'],
                            'growth': component['growth']})
    return out


def evaluate(context, measured, config_pin):
    live = J.dispatcher(context)
    if context.get('phase') != 'fit' or context['batch'].get('phase') != 'fit':
        raise ValueError('The fit role analyses only a fit phase')
    root = J.root_of(context, live)
    config = J.registered(context, live, root, config_pin)
    if not isinstance(config, dict) or config.get('schema') != SCHEMA or set(config) != {
            'schema', 'partTwo', 'references'} or config['partTwo'] != root['partTwo'] or \
            config['references'] != root['references']:
        raise ValueError('Unknown fit analysis config')
    part_two = J.parse(live.checked(context['repo'], root['partTwo']).read_bytes())
    if part_two.get('selection') != SELECTION:
        raise ValueError('Declared selection order differs from the implemented order')
    domain = part_two['candidateDomain']
    document, inventory = J.originals(context, live, root)
    # The judge's own inputs and target references are read here first: a root that omits one
    # of them fails this fit analysis instead of the gate's exclusive analysis.
    judge = ((root.get('instruments') or {}).get('judge') or {}).get('config')
    _, _, targets, cut = J.inputs(context, live, root, judge)
    J.preflight(document, root, cut, targets)
    O.preflight(context, ((root.get('instruments') or {}).get('owner') or {}).get('config'))
    rows = J.measurement(context, live, root, inventory, measured)
    if any(row['role'] in J.WITHHELD for row in rows.values()):
        raise ValueError('Withheld cells never enter fit analysis or ranking')
    reported = {tuple(k) for k in root['reportedKeys']}
    numeric = {k: v for k, v in rows.items() if k[3] != 'owner-contracts'}
    # Routing every row here exercises the judge's exact rules before the one-shot gate; only
    # component errors are kept, never a comparison status.
    routed = dict(zip(numeric, J.route(list(numeric.values()), root)))
    gpu, css, records = [], [], []
    for item in sorted(rows):
        row = rows[item]
        record = {**dict(zip(KEY, item)), 'role': row['role'], 'evidence': copy.deepcopy(row.get('evidence'))}
        if item in numeric:
            record.update({k: copy.deepcopy(row.get(k)) for k in
                           ('sceneSource', 'family', 'inputCode', 'span', 'pose', 'scale', 'position')},
                          reported=item in reported, readings=readings(row))
            if item not in reported:
                record['levelErrors'] = level_components(routed[item], 'absolute-level')
                record['cssLevelGrowth'] = level_components(routed[item], 'css-level-error-growth')
                gpu += record['levelErrors']
                css += record['cssLevelGrowth']
        records.append(record)
    if not gpu:
        raise ValueError('Fit batch carries no exposed low-end level component')
    errors = [c['error'] for c in gpu]
    worst, mean = max(errors), sum(errors)/len(errors)
    squared, chart = distance(context, domain)
    cohort = sorted(p['sha256'] for p in context['batch']['cohort'])
    identity = '+'.join(cohort)
    analysis = {'schema': ANALYSIS, 'status': 'FIT_ANALYSIS_ONLY', 'phase': 'fit',
                'candidateSha256s': cohort, 'cohort': copy.deepcopy(context['batch']['cohort']),
                'config': copy.deepcopy(config_pin), 'inventory': copy.deepcopy(root['references']),
                'measurement': copy.deepcopy(measured['snapshot']), 'charts': chart,
                'selection': {'order': list(SELECTION), 'candidateId': identity,
                              'worstLowEndLevelErrorCodes': worst, 'meanAbsoluteLowEndLevelErrorCodes': mean,
                              'squaredNormalizedDistanceFromCurrent': squared,
                              'key': [worst, mean, squared, identity], 'levelComponents': len(errors),
                              'cssWorstLevelErrorGrowthCodes': max((c['growth'] for c in css), default=None)},
                'rows': records}
    live.require_context(context)
    return _verdict_free(json.loads(json.dumps(analysis, allow_nan=False)))


def _sealed(path):
    path = Path(path)
    sidecar = Path(str(path)+'.sha256')
    if not sidecar.is_file() or sidecar.read_text() != f'{J.sha(path)}  {path.name}\n':
        raise ValueError('Missing or changed seal')
    return J.parse(path.read_bytes())


def fit_record(execution_root, completed):
    """Metadata-only record naming the ONE completed fit point (DL4; DL5 (c)).

    completed holds exactly one repository-relative pin of a fit contract's .result.json. The
    record selects that contract's cohort; the caller writes the record once and hands it to
    the gate contract, which names the point by this record's hash.
    """
    root_path = Path(execution_root).resolve()
    root = _sealed(root_path)
    repo = Path(root['repo']).resolve()
    if not isinstance(completed, list) or len(completed) != 1:
        raise ValueError('W50 fits one point; the record names exactly one completed fit (DL4)')
    pin = completed[0]
    path = (repo/pin['path']).resolve()
    if not path.is_relative_to(repo) or not path.is_file() or J.sha(path) != pin['sha256'] or \
            not path.name.endswith('.result.json'):
        raise ValueError('Fit completion is not a pinned dispatcher result')
    contract_path = Path(str(path)[:-len('.result.json')])
    contract = _sealed(contract_path)
    if contract_path.parent != root_path.parent/'fit' or contract.get('phase') != 'fit' or \
            contract.get('executionRootSha256') != J.sha(root_path):
        raise ValueError('Fit completion belongs to another root or phase')
    result = _sealed(path)
    if result.get('contractSha256') != J.sha(contract_path):
        raise ValueError('Fit result is not bound to its contract')
    report = result.get('report', {})
    analysis = report.get('analysis')
    if report.get('status') != 'CAPTURED' or not isinstance(analysis, dict) or \
            analysis.get('schema') != ANALYSIS or \
            analysis.get('candidateSha256s') != sorted(p['sha256'] for p in contract['cohort']):
        raise ValueError('Fit completion lacks this role\'s analysis of its own cohort')
    _verdict_free(analysis)
    return {'schema': 'w50-g1-fit-record-1', 'executionRootSha256': J.sha(root_path),
            'selected': copy.deepcopy(contract['cohort']), 'completed': [copy.deepcopy(pin)],
            'selection': {'order': list(SELECTION), 'candidateId': analysis['selection']['candidateId']}}


def source_probe():
    J.source_probe()
    _verdict_free({'status': 'FIT_ANALYSIS_ONLY'})
    return {'status': 'SOURCE_ONLY'}
