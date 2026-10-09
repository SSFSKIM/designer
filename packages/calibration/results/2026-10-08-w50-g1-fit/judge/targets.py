"""The six W48 T1 target-aggregate contracts, read from the ORIGINAL G0 inventory (DL5d).

DL5d's clarification moves only the timing of these aggregates: the gate reports them
PENDING_FULL_UNION, and the one exposure evaluates their unchanged complete populations
against their original references. This reader builds those populations and references; the
arithmetic stays in numerical.target_aggregate, and judge/rules.route_targets routes them.

* Membership is the original inventory's dark 0.25 WebGPU full-silhouette T1 rows whose
  (stratum, pose) is a declared W46/W48 target (results/2026-10-05-w46-g0-declaration/
  cuts/rule.py TARGETS): C rest, F inactive and P with both poses pooled, per scale. Every
  role is included, gate and historical prediction check alike; nothing is dropped.
* Native and current are the inventory's frozen W49a operands; the W48 halving reference is
  the cell's own fidelity.reference, the d0219cd684bf/f0b36a71772a reading.
* Each cell's epsilon is its ORIGINAL linear code step from the W49a landing cut
  (cut-025-dark-w49a-landing.json, T1.cells[].code), never B. The cut is cross-bound to the
  inventory: its native, W49a current, d0219 reference and B must equal the inventory's
  figures exactly, so the cut cannot carry another generation's operands into the aggregate.
* The candidate is supplied by the caller from the authenticated complete union. A target
  member without a candidate reading stays in the population as UNMEASURED.

Nothing here opens a file, prints or formats a value: callers authenticate every document
and pass parsed JSON. Errors name fields and keys only.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import types

HERE = Path(__file__).resolve().parent
KEY = ('profile', 'renderer', 'scene', 'statistic')
SCHEMA = 'w50-target-contract-config-1'
STATISTIC = 'T1-full-silhouette'
SUPPORT = 'full-silhouette'
PROFILE = re.compile(r'apple-macos-27\.0-([12])x-dark-standard-glass0\.25')
# W46 G0 cuts/rule.py TARGETS, bound unchanged by W48 and named by W50 clause 3.
TARGETS = {'C rest': (('C', 'rest'),), 'F inactive': (('F', 'inactive'),),
           'P': (('P', 'rest'), ('P', 'inactive'))}


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


R = source(HERE/'rules.py', 'w50_judge_targets_rules')
N = R.N


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def _pin(value):
    return isinstance(value, dict) and set(value) == {'path', 'sha256'} and \
        isinstance(value['path'], str) and bool(value['path']) and \
        isinstance(value['sha256'], str) and re.fullmatch('[0-9a-f]{64}', value['sha256']) is not None


def validate_config(config):
    if not isinstance(config, dict) or config.get('schema') != SCHEMA or set(config) != {
            'schema', 'inventory', 'cut', 'currentGeneration', 'w48Generation'}:
        raise ValueError('Unknown target-contract config')
    if not _pin(config['inventory']) or not _pin(config['cut']):
        raise ValueError('Target contract inventory and cut need exact content pins')
    for name in ('currentGeneration', 'w48Generation'):
        if not isinstance(config[name], str) or not config[name]:
            raise ValueError('Target contract generations must be named')
    return config


def pose(scene):
    """Every canonical scene ends in its state, optionally tinted or pressed."""
    state = scene.rsplit('__', 1)[-1]
    if not state.startswith(('rest', 'pressed', 'inactive')):
        raise ValueError('Target scene has no declared state suffix')
    return 'inactive' if state.startswith('inactive') else 'rest'


def _pair(generations, name):
    pair = generations.get(name, {}).get('documentPair')
    if not isinstance(pair, dict) or set(pair) != {'active.dark', 'receded.dark'}:
        raise ValueError('Target generation lacks its full document pair in the original inventory')
    return N.DocumentPair(pair['active.dark'], pair['receded.dark'])


def population(inventory, cut, config):
    """Exact original target membership: {(target, scale): [(inventory row, cut cell), ...]}."""
    validate_config(config)
    rows = [r for r in inventory['cells'] if r['renderer'] == 'webgpu' and r['statistic'] == STATISTIC
            and PROFILE.fullmatch(r['profile']) and r.get('stratum') in ('C', 'F', 'P')]
    cells = {}
    for cell in cut['T1']['cells']:
        if cell.get('tier') != 'webgpu' or not PROFILE.fullmatch(cell.get('profile', '')) or \
                cell.get('stratum') not in ('C', 'F', 'P'):
            continue
        identity = (cell['profile'], cell['scene'])
        if identity in cells:
            raise ValueError('Ambiguous target cell in the W49a cut')
        cells[identity] = cell
    keys = [(r['profile'], r['scene']) for r in rows]
    if len(set(keys)) != len(keys) or set(keys) != set(cells):
        raise ValueError('Target membership differs between the original inventory and the W49a cut')
    current = None
    result = {(name, scale): [] for name in TARGETS for scale in (1, 2)}
    for row in rows:
        cell = cells[(row['profile'], row['scene'])]
        scale = int(PROFILE.fullmatch(row['profile'])[1])
        fidelity = row.get('fidelity')
        if row['currentGeneration'] != config['currentGeneration'] or cell.get('stratum') != row['stratum'] or \
                cell.get('scale') != scale or cell.get('pose') != pose(row['scene']):
            raise ValueError('Target row differs from its W49a cut generation, stratum, scale or pose')
        if not isinstance(fidelity, dict) or fidelity.get('statistic') != STATISTIC or \
                fidelity.get('native') != row['native'] or fidelity.get('current') != row['current']:
            raise ValueError('Target row lacks its typed original full-silhouette fidelity reading')
        # The cut's candidate column is W49a's own render, i.e. the inventory's frozen current.
        if any(cell.get(a) != b for a, b in (('native', row['native']), ('candidate', row['current']),
                                             ('reference', fidelity['reference']), ('B', row['B']))):
            raise ValueError('W49a cut operands differ from the original inventory figures')
        current = current or row['currentDocumentPair']
        if row['currentDocumentPair'] != current:
            raise ValueError('Target population mixes current document pairs')
        for name, groups in TARGETS.items():
            if (row['stratum'], pose(row['scene'])) in groups:
                result[(name, scale)].append((row, cell))
    if any(not members for members in result.values()):
        raise ValueError('A declared target has an empty original population')
    if N.DocumentPair(current['active.dark'], current['receded.dark']) != \
            _pair(inventory['generations'], config['currentGeneration']):
        raise ValueError('Target current pair is not the named W49a generation')
    return result


def _frozen(inventory_pin, row, side, value, pair):
    record = {'kind': 'frozen-reference-record', 'inventory': inventory_pin,
              'key': [row[k] for k in KEY], 'side': side}
    evidence = N.Evidence(digest({**record, 'original': row}),
                          digest({**record, 'statistic': STATISTIC, 'value': value}),
                          pair, source_kind='frozen-reference-record')
    if value is None:
        return N.Reading('UNMEASURED', 'linear-luma', None, None, 'Original '+side+' reading absent')
    return N.Reading('MEASURED', 'linear-luma', value, evidence)


def _candidate(identity, source):
    if source is None:
        return N.Candidate(identity, N.Reading('UNMEASURED', 'linear-luma', None, None,
                                               'Candidate reading absent from the complete union'))
    if source.get('support') != SUPPORT or source.get('units') != 'linear-luma':
        raise ValueError('Target candidate is not the declared full-silhouette linear reading')
    return N.Candidate(identity, R._reading(source, 'candidate'))


def contracts(inventory, inventory_pin, cut, config, candidates):
    """Six {cells, expectedKeys} contracts for rules.route_targets(full_union=True).

    candidates maps an exact original key tuple to its authenticated candidate source reading
    (a rules-shaped reading dict for T1-full-silhouette). Keys outside the target population
    are ignored; a missing member is retained as UNMEASURED, never dropped.
    """
    if not _pin(inventory_pin) or config['inventory'] != inventory_pin:
        raise ValueError('Target contracts must read the configured original inventory')
    old = _pair(inventory['generations'], config['w48Generation'])
    out = {}
    for (name, scale), members in population(inventory, cut, config).items():
        cells = []
        for row, cut_cell in members:
            identity = N.RowIdentity(row['profile'], row['renderer'], row['scene'], STATISTIC, SUPPORT)
            current_pair = N.DocumentPair(row['currentDocumentPair']['active.dark'],
                                          row['currentDocumentPair']['receded.dark'])
            reference = N.Reference(identity, inventory_pin['sha256'],
                _frozen(inventory_pin, row, 'native', row['native'], None),
                _frozen(inventory_pin, row, 'current', row['current'], current_pair),
                cut_cell['code'], cut_cell['bar'], row['B'])
            w48 = _frozen(inventory_pin, row, 'w48-reference', row['fidelity']['reference'], old)
            key = tuple(row[k] for k in KEY)
            cells.append(N.AggregateCell(reference, _candidate(identity, copy.deepcopy(candidates.get(key))), w48))
        out[(name, scale)] = {'cells': cells, 'expectedKeys': tuple(c.reference.identity for c in cells)}
    return out


def keys(inventory, cut, config):
    """Metadata-only target membership by exact original key."""
    return {target: [[row[k] for k in KEY] for row, _ in members]
            for target, members in population(inventory, cut, config).items()}


def source_probe():
    R.route_targets(None, full_union=False)
    return {'status': 'SOURCE_ONLY'}
