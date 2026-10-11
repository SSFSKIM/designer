"""Project pinned W51 membership and exposed facts into UNSEALED W52-DL1/DL2 data.

This script reads no pixels, blind payloads, capture trees or new measurements and grants no
fit, rehearsal, gate, exposure or capture authority. The only external JSON reads are exact
own-history measurements selected by the already exposed committed W51 gate report. Nested
capture/evidence paths are witnesses, not permission to open those paths. Static exposure
histories are already-published reference facts, not new exposure/native/candidate scores.

Run `python -I -B <absolute build.py> generate` to materialize data, or `check` to rederive and
compare it byte for byte. Source pins are fixed separately; neither operation re-pins a source.
The parent's numerical comparator is named, not executed as a new judge or scientific reading.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SOURCE_PINS_SHA256 = '5197992bb08525daa921c7422c5e71a65fb5a7bb535684c457f26627ae217d6f'
KEY = ('profile', 'renderer', 'scene', 'statistic')
PHYSICAL = KEY[:3]
CHANNELS = ('deep8-channel-median', 'central8-channel-median')
LUMA = ('deep8-far24-luma-mean', 'deep8-far24-luma-median')
PROFILE = re.compile(r'apple-macos-27\.0-([12])x-dark-standard-glass(0\.25|0\.5)')
REFEREE_SCENES = tuple(f'impulse__{s}__rest' for s in
                       ('capsule-button', 'rrect-sm', 'rrect-ml', 'rrect-lg'))


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ordinary(path):
    path = Path(path).absolute()
    require(path.resolve() == path and not any(p.is_symlink() for p in (path, *path.parents)),
            'Source must be an ordinary canonical file')
    require(path.is_file(), 'Source must be an ordinary canonical file')
    return path


def read_bytes(pin, repo=REPO):
    path = ordinary(Path(repo) / pin['path'])
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'Changed source hash: ' + str(path))
    return raw


def parse(raw):
    def nonfinite(_):
        raise ValueError('Nonfinite JSON operand')
    return json.loads(raw, parse_constant=nonfinite)


def read_source(pin, repo=REPO):
    return parse(read_bytes(pin, repo))


def key(row):
    return tuple(row[k] for k in KEY)


def index(rows):
    result = {key(r): r for r in rows}
    require(len(result) == len(rows), 'Duplicate source statistic key')
    return result


def load_sources(repo=REPO):
    raw = ordinary(HERE / 'source-pins.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_PINS_SHA256, 'Changed source-pins hash')
    document = parse(raw)
    pins = document['sources']
    data = {'pins': pins}
    json_sources = ('fit', 'gate', 'exposure', 'policy', 'costs', 'report', 'inventory', 'bed', 'scenes')
    for name, pin in pins.items():
        raw = read_bytes(pin, repo)
        if name in json_sources:
            data[name] = parse(raw)
    report_rows = index(data['report']['cells'])
    expected = sorted(k for k, r in report_rows.items() if any(
        c['rule'].startswith('own-history[') for c in r['route'].get('checks', [])))
    records = document['historyMeasurements']
    require([tuple(p['key']) for p in records] == expected,
            'History source list differs from exact exposed report selection')
    data['historyRows'] = {}
    data['historyPins'] = {}
    for pin in records:
        identity = tuple(pin['key'])
        report_pin = report_rows[identity]['evidence']
        require({k: pin[k] for k in ('path', 'sha256')} == report_pin,
                'History measurement pin differs from exposed report')
        data['historyRows'][identity] = read_source(report_pin, repo)
        data['historyPins'][identity] = report_pin
    require(data['report']['inventory'] == pins['inventory'], 'Report names another original inventory')
    require(data['report']['landingPolicy'] == pins['policy'], 'Report names another W51 policy')
    return data


def document(**fields):
    return dict(schema='w52-population-scaffold-1', status='UNSEALED_DATA_SCAFFOLD_ONLY',
                captureAuthority=False, **fields)


def validate_population(source, physical_count, statistic_count):
    keys = list(map(tuple, source['statisticKeys']))
    physical = list(map(tuple, source['physicalCells']))
    require(keys == sorted(set(keys)) and physical == sorted(set(physical)),
            'Population keys must be exact, sorted and unique')
    require(len(keys) == source['statisticCount'] == statistic_count and
            len(physical) == source['physicalCount'] == physical_count, 'Population count changed')
    require(physical == sorted({k[:3] for k in keys}), 'Population physical projection changed')
    require([key(r) for r in source['originalMetadata']] == keys, 'Metadata does not cover exact keys')
    require(source['physicalFields'] == list(PHYSICAL) and source['statisticFields'] == list(KEY),
            'Population field order changed')


def population(source, pin, purpose):
    fields = ('physicalCells', 'physicalCount', 'physicalFields', 'statisticKeys', 'statisticCount',
              'statisticFields', 'originalMetadata')
    return document(purpose=purpose, source=pin,
                    **{k: copy.deepcopy(source[k]) for k in fields})


def union(left, right, purpose):
    keys = sorted(set(map(tuple, left['statisticKeys'])) | set(map(tuple, right['statisticKeys'])))
    physical = sorted({k[:3] for k in keys})
    metadata = index(left['originalMetadata'])
    for row in right['originalMetadata']:
        require(key(row) not in metadata or metadata[key(row)] == row, 'Overlapping metadata differs')
        metadata[key(row)] = row
    return document(purpose=purpose, physicalFields=list(PHYSICAL), statisticFields=list(KEY),
                    physicalCells=list(map(list, physical)), physicalCount=len(physical),
                    statisticKeys=list(map(list, keys)), statisticCount=len(keys),
                    originalMetadata=[copy.deepcopy(metadata[k]) for k in keys])


def epsilon(data):
    return {'source': copy.deepcopy(data['pins']['precision']), 'function': 'less_equal',
            'operands': ['growth_or_error', 'bound', 'native', 'reference', 'candidate'],
            'units': 'same component units; include original subtraction operands',
            'authority': 'Prospective data descriptor, not live judge authority'}


def bound(base, multiplier, data):
    return {'base': base, 'multiplier': multiplier, 'expression': 'base + numericalEpsilon',
            'numericalEpsilon': epsilon(data)}


def histories(data, full):
    gate_keys = set(map(tuple, data['gate']['statisticKeys']))
    complete = set(map(tuple, full['statisticKeys']))
    rows = index(data['inventory']['cells'])
    report_rows = index(data['report']['cells'])
    records = []
    for identity in sorted(complete):
        original = rows[identity]
        for i, historical in enumerate(original.get('historical', [])):
            native, current, budget = original['native'], original['current'], original['B']
            require(all(type(v) in (float, int) and math.isfinite(v) for v in
                        (native, current, budget, historical['value'])) and budget > 0,
                    'Historical source has missing or nonfinite operands')
            raw = abs(current - native) - abs(historical['value'] - native)
            require(raw / budget == historical['frozenCurrentGrowthInB'],
                    'Historical frozen normalized witness differs from original operands')
            require(historical['enforced'] is True, 'Historical source cannot silently be declined')
            cap = budget if historical.get('repaired', False) else max(budget, raw)
            require(not historical.get('repaired', False) or raw <= budget, 'Repaired history exceeds B')
            membership = 'gate' if identity in gate_keys else 'exposure'
            source = {'source': data['pins']['inventory'], 'selector': {'collection': 'cells',
                      'key': list(identity), 'field': ['historical', i]}}
            witness = {'kind': 'published-static-reference', **source, 'original': historical}
            if membership == 'gate':
                measured = data['historyRows'][identity]['row']
                require(measured['originalReference'] == original and key(measured) == identity,
                        'Exact exposed measurement differs from original historical record')
                witness = measured['readings'][original['statistic']]['evidence']['historical'][i]
                require(witness['original'] == historical, 'Historical evidence witness changed')
                check = next(c for c in report_rows[identity]['route']['checks'] if
                             c['rule'] == f'own-history[{i}]')
                require(check['comparison']['components'][0]['bound'] == cap,
                        'Exposed original history cap differs from source normalization')
                source = {'source': data['historyPins'][identity], 'selector':
                          {'field': ['row', 'originalReference', 'historical', i]}}
            occupied = raw == cap
            records.append({'key': list(identity), 'historyIndex': i, 'membership': membership,
                'source': source, 'originalReference': copy.deepcopy(original),
                'historicalWitness': copy.deepcopy(witness), 'occupied': occupied,
                'originalOperands': {'native': native, 'current': current, 'B': budget,
                    'historicalValue': historical['value'], 'currentGrowth': raw, 'cap': cap,
                    'frozenCurrentGrowthInB': historical['frozenCurrentGrowthInB']},
                'prospective': {'action': 'CURRENT_GENERATION_WITH_B_HEADROOM' if occupied else
                                'RETAIN_HISTORY_AND_CAP',
                    'referenceValue': current if occupied else historical['value'],
                    'referenceGeneration': original['currentGeneration'] if occupied else historical['generation'],
                    'referenceDocumentPair': copy.deepcopy(original['currentDocumentPair'] if occupied else
                                                           historical['documentPair']),
                    'bound': bound(budget if occupied else cap, 1, data),
                    'historicalDebtRetained': True}})
    inventories = {phase: {'comparisons': sum(r['membership'] == phase for r in records),
                          'occupied': sum(r['membership'] == phase and r['occupied'] for r in records)}
                   for phase in ('gate', 'exposure')}
    require(inventories['gate'] == {'comparisons': 16, 'occupied': 14} and
            inventories['exposure'] == {'comparisons': 4, 'occupied': 1}, 'Own-history inventory changed')
    return document(authority=['W52-DL1', 'W52-DL2'], gateInventory=inventories['gate'],
        exposureStaticInventory=inventories['exposure'], comparisons=records,
        scope='Complete declared union. Exposure entries use published static references only; no new exposure score.',
        noGlobalBaselineReplacement=True, numericalEpsilon=epsilon(data))


def costs(data):
    require(data['costs']['exceptions'] == data['policy']['exceptions'], 'W51 cost declarations differ')
    report_rows = index(data['report']['cells'])
    records = []
    for original in data['policy']['exceptions']:
        if original['key'][3] != 'T1-full-silhouette':
            continue
        identity = tuple(original['key'])
        q = original['readings']['T1-full-silhouette']
        report = report_rows[identity]['readings']['T1-full-silhouette']
        require(all(q[k] == report[k] for k in ('native', 'current', 'B')),
                'Declared texture-cost reference differs from exposed gate reference')
        records.append({'key': list(identity), 'w51DeclaredCost': copy.deepcopy(original),
            'w51ExposedGate': {'source': data['pins']['report'], 'selector': {'collection': 'cells',
                'key': list(identity)}, 'reading': {k: report[k] for k in
                                                   ('native', 'current', 'candidate', 'B', 'bar', 'code')}},
            'prospective': {'referenceValue': q['current'], 'native': q['native'],
                            'bound': bound(q['B'], 1, data)}})
    require(len(records) == 18 and sum(r['key'][2].startswith('cell-impulse-sparse-') for r in records) == 16,
            'Named texture-cost population changed')
    require([r['key'][2] for r in records if not r['key'][2].startswith('cell-impulse-sparse-')] ==
            ['impulse__capsule-button__rest'] * 2, 'Canonical texture-cost identities changed')
    return document(authority='W52-DL2', costs=records, genericT1GrowthMultiplier=2,
                    w52Exceptions=[], numericalEpsilon=epsilon(data),
                    noW51ExceptionsCarry=True, source=data['pins']['policy'])


def aggregate_memberships(data, full):
    """Retain W51's exact gate components, including all 22 already-member cost keys.

    The 80 definitions comprise 76 historical W51 gate definitions and four prospectively
    added W52 exposure-only inactive-T groups (positions 0.25/0.5, scales 1/2). Substatistics
    and RGB components follow W51's generator exactly; no gate member component is added.
    These records contain membership only, not fitted operands or scoring permission.
    `w51Gate` and `w51Timing` preserve source gate/diagnostic and timing provenance only for
    the historical definitions; `timing` describes prospective W52 full-union membership.
    Source-owned full-union owner-contract timing and applicability remain unchanged.
    """
    originals = index(data['inventory']['cells'])
    bed = {(r['profile'], r['scene']): r for r in data['bed']['cells']}
    scenes = {r['id']: r for r in data['scenes']['scenes']}
    gate_keys = set(map(tuple, data['gate']['statisticKeys']))
    groups, exclusions, owner = {}, [], []

    def add(kind, dims, identity, statistic, component=None):
        label = (kind, json.dumps(dims, sort_keys=True))
        member = {'key': list(identity), 'statistic': statistic, 'component': component,
                  'membership': 'gate' if identity in gate_keys else 'exposure'}
        groups.setdefault(label, {'kind': kind, 'dimensions': dims, 'members': []})['members'].append(member)

    for identity in map(tuple, full['statisticKeys']):
        original = originals[identity]
        statistic = original['statistic']
        if statistic == 'owner-contracts':
            owner.append(list(identity)); continue
        match = PROFILE.fullmatch(original['profile'])
        require(match is not None and original['renderer'] in ('css', 'webgpu'), 'Unknown material dimension')
        dims = {'position': float(match[2]), 'scale': int(match[1]), 'renderer': original['renderer']}
        newbed = original.get('nativeIdentity') is not None
        if newbed:
            cell = bed[(original['profile'], original['scene'])]
            dims['pose'] = 'inactive' if cell['pose'] == 'receded' else 'rest'
            if cell['family'] == 'span' and statistic in LUMA + ('T1-full-silhouette',):
                exclusions.append({'key': list(identity), 'reason': 'W51 reported span reading'}); continue
            if cell.get('level') == 64:
                exclusions.append({'key': list(identity), 'reason': 'W51 held-64 identity'}); continue
        else:
            scene = scenes[original['scene']]
            dims['pose'] = 'inactive' if scene['state'] == 'inactive' else 'rest'
        if statistic in ('T1-full-silhouette', 'T1-low'):
            if newbed:
                require(cell['family'] == 'structured', 'Unreported neutral texture key')
                add('newbed-t1', dict(dims, family=cell['family']), identity, statistic)
            else:
                require(original['renderer'] == 'webgpu' and original['stratum'] in ('F', 'T', 'C', 'P'),
                        'Unknown canonical texture stratum')
                stratum = original['stratum']
                require(statistic == ('T1-low' if stratum == 'T' else 'T1-full-silhouette'),
                        'Canonical texture band differs from source stratum')
                add('t1', dict(dims, stratum=stratum), identity,
                    'T1-fine' if stratum == 'T' else statistic)
        else:
            if newbed:
                require(statistic in CHANNELS + LUMA, 'Unknown new-bed level key')
                names = (statistic,)
            else:
                require(statistic == 'low-end-path-level', 'Unknown canonical level key')
                kind = data['scenes']['backgrounds'][scene['background']]['kind']
                require(kind in ('solid', 'impulse'), 'Unknown canonical level support')
                names = LUMA if kind == 'impulse' else (CHANNELS[0],)
            for name in names:
                for component in (('R', 'G', 'B') if name in CHANNELS else (None,)):
                    add('level', dims, identity, name, component)
    aggregates = []
    for group in groups.values():
        members = sorted(group['members'], key=lambda m:
                         (m['key'], m['statistic'], {None: 0, 'R': 1, 'G': 2, 'B': 3}[m['component']]))
        require(len({(tuple(m['key']), m['statistic'], m['component']) for m in members}) == len(members),
                'Duplicate aggregate component')
        for reduction in (('max', 'mean') if group['kind'] == 'level' else ('median-log-ratio',)):
            label = '/'.join(f'{k}={v}' for k, v in sorted(group['dimensions'].items()))
            aggregates.append({**group, 'id': group['kind'] + '/' + label + '/' + reduction,
                'members': members, 'reduction': reduction,
                'timing': 'full-union', 'membershipSha256': hashlib.sha256(encoded(members)).hexdigest()})
    expected = {a['id']: a for a in data['policy']['aggregates']}
    actual = {a['id']: a for a in aggregates}
    extra_ids = {f't1/pose=inactive/position={position}/renderer=webgpu/scale={scale}/'
                 'stratum=T/median-log-ratio' for position in (.25, .5) for scale in (1, 2)}
    require(set(actual) == set(expected) | extra_ids, 'Aggregate dimensions differ from W51 source law')
    require(all(m['membership'] == 'exposure' for label in extra_ids for m in actual[label]['members']),
            'Additional text stratum is not exposure-only')
    for label in extra_ids:
        actual[label]['definitionOrigin'] = 'prospective-w52-exposure-only-inactive-t'
    for label, original in expected.items():
        old = {(tuple(m['key']), m['statistic'], m['component']) for m in original['members']}
        present = {(tuple(m['key']), m['statistic'], m['component']) for m in actual[label]['members']
                   if m['membership'] == 'gate'}
        require(old == present, 'Aggregate projection differs from exact W51 gate components')
        actual[label].update(definitionOrigin='historical-w51-gate',
                             w51Gate=original['gate'], w51Timing=original['timing'])
    require(data['report']['ownerChecks'] == 'PENDING_FULL_UNION',
            'Source-owned full-union owner-contract timing changed')
    return document(aggregates=sorted(aggregates, key=lambda a: a['id']),
        definitionCounts={'historicalW51Gate': len(expected),
                          'prospectiveW52ExposureOnlyInactiveT': len(extra_ids)},
        ownerContractKeys=owner, ownerContractTiming={'timing': 'full-union', 'unchanged': True,
            'source': data['pins']['report'], 'sourceField': 'ownerChecks',
            'sourceValue': data['report']['ownerChecks']},
        exclusions=exclusions, excludedExceptionKeys=[],
        retainedW51CostKeys=[e['key'] for e in data['policy']['exceptions']],
        sourceLaw=data['pins']['w51Generator'], sourcePolicy=data['pins']['policy'],
        authorityBoundary='Membership only. No blind operands, policy seal or executable judging authority.')


def derive(data):
    for name, physical, keys in (('fit', 840, 1856), ('gate', 1341, 2553), ('exposure', 322, 974)):
        validate_population(data[name], physical, keys)
    fit = population(data['fit'], data['pins']['fit'], 'Original fit840; identical real rehearsal only')
    gate = population(data['gate'], data['pins']['gate'], 'Fresh gate1341, unchanged membership')
    exposure = population(data['exposure'], data['pins']['exposure'], 'Exposure322; identities only, no payload read')
    gate_set = set(map(tuple, gate['statisticKeys']))
    exposure_set = set(map(tuple, exposure['statisticKeys']))
    require(not gate_set & exposure_set and not set(map(tuple, gate['physicalCells'])) &
            set(map(tuple, exposure['physicalCells'])), 'Gate and exposure overlap')
    require(set(map(tuple, fit['statisticKeys'])) <= gate_set, 'Fit keys are not exact gate subset')
    require(data['policy']['completeKeys'] == gate['statisticKeys'], 'W51 policy key coverage changed')
    require(sorted(index(data['report']['cells'])) == sorted(gate_set), 'Exposed report key coverage changed')
    full = union(gate, exposure, 'Complete gate plus conditional exposure; no membership change')
    originals = index(data['inventory']['cells'])
    require(set(originals) == set(map(tuple, full['statisticKeys'])), 'Original inventory is not complete union')
    referee_keys = [k for k in gate['statisticKeys'] if k[1] == 'webgpu' and k[2] in REFEREE_SCENES]
    referee_meta = [r for r in gate['originalMetadata'] if list(key(r)) in referee_keys]
    referee_physical = sorted({tuple(k[:3]) for k in referee_keys})
    fit_keys = set(map(tuple, fit['statisticKeys'])); fit_physical = set(map(tuple, fit['physicalCells']))
    referees = document(purpose='Named impulse-rest referees read at fit; all non-blind at gate',
        physicalFields=list(PHYSICAL), statisticFields=list(KEY),
        physicalCells=list(map(list, referee_physical)), physicalCount=len(referee_physical),
        statisticKeys=referee_keys, statisticCount=len(referee_keys), originalMetadata=referee_meta,
        overlapPhysicalCells=list(map(list, sorted(set(referee_physical) & fit_physical))),
        extraPhysicalCells=list(map(list, sorted(set(referee_physical) - fit_physical))),
        extraStatisticKeys=list(map(list, sorted(set(map(tuple, referee_keys)) - fit_keys))),
        gateBlindness='NON_BLIND_READ_AT_FIT', source=data['pins']['gate'])
    require((referees['physicalCount'], len(referees['overlapPhysicalCells']),
             len(referees['extraPhysicalCells']), len(referees['extraStatisticKeys'])) == (16, 4, 12, 22),
            'Named referee overlap changed')
    gate['nonBlindRefereePhysicalCells'] = referees['physicalCells']
    gate['nonBlindRefereeStatisticKeys'] = referees['statisticKeys']
    gate['refereeGateBlindness'] = referees['gateBlindness']
    fit_union = union(fit, referees, 'Fit-time union852; not the real-pipeline rehearsal')
    require((fit_union['physicalCount'], fit_union['statisticCount']) == (852, 1878), 'Fit-time union changed')
    return {'fit-population.json': fit, 'gate-population.json': gate,
        'exposure-population.json': exposure, 'impulse-referees.json': referees,
        'fit-time-union.json': fit_union, 'full-union.json': full,
        'rehearsal.json': document(population='fit-population.json', physicalCount=840, statisticCount=1856,
            expandedFitTimeUnionIsNotRehearsal=True, authorityBoundary='No rehearsal execution authorised'),
        'own-history.json': histories(data, full), 'texture-costs.json': costs(data),
        'aggregate-memberships.json': aggregate_memberships(data, full)}


def write_outputs(outputs, directory=HERE):
    directory = Path(directory)
    for name, value in outputs.items():
        path = directory / name
        require(not path.is_symlink(), 'Output is not an ordinary file')
        path.write_bytes(encoded(value))


def check_outputs(directory=HERE, data=None):
    expected = derive(load_sources() if data is None else data)
    for name, value in expected.items():
        path = ordinary(Path(directory) / name)
        require(path.read_bytes() == encoded(value), 'Data differs from exact source projection: ' + name)
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('generate', 'check'))
    args = parser.parse_args()
    data = load_sources()
    if args.command == 'generate':
        write_outputs(derive(data))
    outputs = check_outputs(data=data)
    print(f'W52 unsealed data: {len(outputs)} projections checked; no capture authority; '
          'fit840/1856, fit-time852/1878, gate1341/2553, exposure322/974; '
          'own-history gate16/14 occupied + static exposure4/1 occupied; texture-cost18')


if __name__ == '__main__':
    main()
