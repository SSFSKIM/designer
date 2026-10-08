"""Pure W50 numeric row routing over the authenticated phase reader's JSON interface.

No evidence file is opened, no caller data is authenticated, and no whole-phase verdict is
issued here. The caller binds the original inventory, rows, declared scene metadata, side
identities and exact reported/eligible-empty key sets before calling. Each original key stays
ONE key: compound path cuts and the T1-fine companion remain subordinate readings.

All comparison arithmetic, frozen-history normalization and target aggregation belong to
numerical.py. Producer-native code/bar/B remain visible beside explicitly preserved original
canonical0.25 T1 budgets; neither code=B nor a fabricated replacement native bar is used.
"""
from __future__ import annotations

import copy
from dataclasses import asdict
import hashlib
from pathlib import Path
import re
import sys
import types

HERE = Path(__file__).resolve().parent
N = types.ModuleType('w50_rules_numerical')
N.__file__ = str(HERE/'numerical.py')
sys.modules[N.__name__] = N
exec(compile((HERE/'numerical.py').read_bytes(), N.__file__, 'exec'), N.__dict__)
KEY = ('profile', 'renderer', 'scene', 'statistic')
SUPPORT = {
    'deep8-channel-median': 'deep8', 'central8-channel-median': 'center8',
    'deep8-far24-luma-mean': 'deep8_far24', 'deep8-far24-luma-median': 'deep8_far24',
    'T1-full-silhouette': 'full-silhouette', 'T1-low': 'eroded4', 'T1-fine': 'eroded4',
}
TARGETS = tuple((name, scale) for name in ('C rest', 'F inactive', 'P') for scale in (1, 2))


def _key(row):
    key = tuple(row[k] for k in KEY)
    if any(not isinstance(v, str) or not v for v in key) or key[1] not in ('webgpu', 'css'):
        raise ValueError('An exact original four-field row key is required')
    return key


def _policy(keys, what):
    values = [tuple(key) for key in keys]
    if any(len(key) != 4 or any(not isinstance(v, str) or not v for v in key) for key in values) \
            or len(values) != len(set(values)):
        raise ValueError('Invalid or duplicate exact '+what+' keys')
    return set(values)


def _value(value):
    return tuple(value) if isinstance(value, list) else value


def _evidence(record, side, *, frozen_records=False):
    numeric, capture = record['numericIdentity'], record['captureIdentity']
    if capture.get('digest') != numeric.get('captureSha256'):
        raise ValueError('Numeric capture identity differs from its labelled source identity')
    allowed = ('png', 'native-three-run-cohort') if side == 'native' else \
        ('png', 'frozen-reference-record') if side == 'historical' else ('png',)
    if frozen_records and side in ('native', 'current'):
        allowed = ('frozen-reference-record',)
    if capture.get('kind') not in allowed:
        raise ValueError('Capture/cohort/frozen-record identity has the wrong source kind')
    if capture['kind'] == 'png' and capture['pin']['sha256'] != capture['digest']:
        raise ValueError('PNG identity differs from its content pin')
    if capture['kind'] == 'native-three-run-cohort' and \
            [r['run'] for r in capture['runs']] != [1, 2, 3]:
        raise ValueError('Native aggregate identity needs three ordered original runs')
    pair = numeric['documentPair']
    pair = None if pair is None else N.DocumentPair(pair['activeSha256'], pair['recededSha256'])
    return N.Evidence(numeric['captureSha256'], numeric['statisticSha256'], pair,
                      source_kind=capture['kind'])


def _reading(source, side, *, original=None):
    status = source[side+'MeasurementStatus']
    frozen = original is not None and side in ('native', 'current')
    evidence = _evidence(source['evidence'][side], side, frozen_records=frozen) if status == 'MEASURED' else None
    reason = '' if status == 'MEASURED' else source.get(side+'Reason', source.get('reason', status))
    value = original[side] if frozen else source[side]
    return N.Reading(status, source['units'], _value(value), evidence, reason)


def _original_operands(row, name, inventory):
    """Frozen TS figures stay criteria; fresh reductions are diagnostic source observations."""
    source, original = row['readings'][name], row['originalReference']
    diagnostic = source.get('sourceReading')
    if source.get('routingOperands') != 'ORIGINAL_INVENTORY' or not isinstance(diagnostic, dict):
        raise ValueError('Frozen canonical T1 requires explicit original operands and separate source diagnostics')
    for side in ('native', 'current'):
        if source[side] != original.get(side) or row['reference'].get(side) != original.get(side):
            raise ValueError('Frozen native/current operand differs from the original inventory figure')
        capture = source['evidence'][side]['captureIdentity']
        if capture.get('kind') != 'frozen-reference-record' or capture.get('side') != side or \
                capture.get('key') != list(_key(row)) or capture.get('original') != original or \
                capture.get('inventory', {}).get('sha256') != inventory:
            raise ValueError('Original operand evidence is not the exact frozen inventory record')
    for field in ('units', 'support', 'code', 'bar', 'B', 'nativeRepeat', 'nativeSupportWitnesses'):
        if source.get(field) != diagnostic.get(field):
            raise ValueError('Fresh source code/bar/support diagnostics were changed or rebased')
    estimator, producer, field = (
        ('PRODUCTION_TS_INTERIOR_LEVEL', 'packages/calibration/src/metrics/material.ts#interiorLevel',
         'material.interiorStdDevWeb') if name == 'T1-full-silhouette' else
        ('CANONICAL_NUMPY_GAUSSIAN_LOW',
         'packages/calibration/results/2026-10-08-w50-g1-fit/references/statistics.py#canonical_read',
         'web.statistics.T1-low'))
    evidence = source['evidence']['candidate']
    production = evidence.get('productionStatistic', {})
    expected = dict(estimator=estimator, producer=producer, field=field, statistic=name,
                    reading='first', scene=row['scene'], units='linear-luma', value=source['candidate'])
    if source.get('candidateEstimator') != estimator or \
            any(production.get(k) != v for k, v in expected.items()) or \
            production.get('capture') != evidence['captureIdentity'].get('pin') or \
            production.get('capture') != diagnostic['evidence']['candidate']['captureIdentity'].get('pin') or \
            not isinstance(production.get('matrix'), dict):
        raise ValueError('Authoritative candidate lacks its named original-estimator production statistic')
    # These are shape checks, not file authentication. The phase reader owns both content pins.
    matrix = production['matrix']
    if not isinstance(matrix.get('path'), str) or not matrix['path'] or \
            not isinstance(matrix.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', matrix['sha256']):
        raise ValueError('Production statistic has no explicit matrix content identity')
    return original


def _contracts(row, name, inventory, *, frozen=False, source_override=None):
    source = row['readings'][name] if source_override is None else source_override
    units = 'encoded-RGB-codes' if name in N.CHANNELS else \
        'encoded-luma-codes' if name in N.LUMA else 'linear-luma'
    if source['support'] != SUPPORT[name] or source['units'] != units:
        raise ValueError('Producer statistic/support/units differ from the declared reader')
    identity = N.RowIdentity(row['profile'], row['renderer'], row['scene'], name, source['support'])
    code, bar, budget = (_value(source.get(k)) for k in ('code', 'bar', 'B'))
    original = source.get('originalBudgetB')
    witness, operands = None, None
    if frozen and name in N.T1_REGRESSION:
        declared = row['originalReference'].get('B')
        if original != declared or (declared is not None and row['reference'].get('B') != declared):
            raise ValueError('Frozen T1 B differs from the unchanged original/reference budget')
        if original is not None:
            operands = _original_operands(row, name, inventory)
            witness = N.FrozenT1Budget(identity, inventory, original)
            budget = original
    if budget is None:
        # Reported rows retain their native-repeat bundle in sourceReadings; they have no
        # numerical budget contract. No new B is reconstructed from their native bar.
        code = bar = None
    native, current, candidate = (_reading(source, side, original=operands)
                                  for side in ('native', 'current', 'candidate'))
    ref = N.Reference(identity, inventory, native, current, code, bar, budget, witness)
    return ref, N.Candidate(identity, candidate)


def _names(row):
    name, source, family = row['statistic'], row['sceneSource'], row['family']
    if name == 'owner-contracts':
        return ()
    if source == 'canonical':
        if name == 'low-end-path-level':
            if family == 'impulse': return N.LUMA
            if family == 'solid': return (N.CHANNELS[0],)
            raise ValueError('Canonical path closure requires its declared impulse or solid family')
        if name == 'T1-low': return ('T1-low', 'T1-fine')
        if name == 'T1-full-silhouette': return (name,)
    elif source == 'w50' and family in ('uniform', 'span', 'structured') and name in SUPPORT:
        if name in ('T1-low', 'T1-fine'):
            raise ValueError('The W50 new bed declares full-silhouette T1, not text-band statistics')
        return (name,)
    raise ValueError('Numeric row is outside the declared W50 routing population')


def _same_sources(contracts):
    """Compound subreadings belong to the same actual capture/cohort and document pair."""
    for lane in ('native', 'current', 'candidate'):
        readings = [candidate.reading if lane == 'candidate' else getattr(ref, lane)
                    for ref, candidate in contracts.values()]
        signatures = {(r.evidence.source_kind, r.evidence.source_sha256, r.evidence.document_pair)
                      for r in readings if r.status == 'MEASURED'}
        if len(signatures) > 1:
            raise ValueError('Compound readings refer to different source captures or document pairs')


def _check(rule, ref, comparison):
    return dict(rule=rule, statistic=ref.identity.statistic, comparison=asdict(comparison))


def _empty_witness(row, name):
    source = row['readings'][name]
    if name != 'T1-full-silhouette' or any(source[side] is not None or \
            source[side+'MeasurementStatus'] != 'UNMEASURED_EMPTY_SUPPORT'
            for side in ('native', 'current', 'candidate')):
        raise ValueError('Optional empty T1 requires null original/native/current/candidate readings')
    witnesses = source['nativeSupportWitnesses']
    scale = row['scale']
    if type(scale) is not int or scale not in (1, 2) or \
            [w['run'] for w in witnesses] != [1, 2, 3]:
        raise ValueError('Empty support needs three original run witnesses at the declared scale')
    shape = [384*scale, 512*scale]
    # This checks only the mathematical empty-witness consistency, not image/file authenticity.
    empty_hash = hashlib.sha256(bytes((shape[0]*shape[1]+7)//8)).hexdigest()
    for witness in witnesses:
        if type(witness.get('pixels')) is not int or witness['pixels'] != 0 or \
                witness.get('maskShape') != shape or witness.get('maskPackedBitsSha256') != empty_hash:
            raise ValueError('Empty support witness is not the exact zero native mask')
    return copy.deepcopy(witnesses)


def _histories(row, name, reference, candidate):
    originals = row.get('historical', [])
    if originals != row['originalReference'].get('historical', []) or \
            originals != row['reference'].get('historical', []):
        raise ValueError('Own historical references were changed or rebaselined')
    records = row['readings'][name]['evidence'].get('historical', [])
    if len(records) != len(originals):
        raise ValueError('Every own historical reference needs its aligned frozen evidence')
    checks = []
    for index, (original, record) in enumerate(zip(originals, records)):
        if record.get('original') != original:
            raise ValueError('Historical evidence refers to another frozen source record')
        evidence = _evidence(record, 'historical')
        pair = original['documentPair']
        if evidence.document_pair != N.DocumentPair(pair['active.dark'], pair['receded.dark']):
            raise ValueError('Own historical reading has another full document pair')
        if original.get('enforced') is not True:
            raise ValueError('Original historical constraint cannot be silently declined')
        value, frozen = original['value'], original.get('frozenCurrentGrowthInB')
        reading = N.Reading('MEASURED' if value is not None else 'UNMEASURED',
            reference.native.units, value, evidence, '' if value is not None else 'Frozen historical value absent')
        if frozen is None:
            history = N.Historical(reading, None, original.get('repaired', False))
        else:
            history = N.historical_from_frozen_in_b(reference, reading,
                frozen_current_growth_in_b=frozen, repaired=original.get('repaired', False))
        checks.append(_check('own-history['+str(index)+']', reference,
                             N.historical_growth(reference, candidate, history)))
    return checks


def route_row(row, *, inventory_sha256, reported_keys=(), empty_support_keys=()):
    """Return one key's comparison evidence; the caller has already authenticated its inputs."""
    key = _key(row)
    for source in ('originalReference', 'reference'):
        if _key(row[source]) != key:
            raise ValueError('An original key cannot be replaced by a compound subreading key')
    reported = _policy(reported_keys, 'reported')
    empty = _policy(empty_support_keys, 'empty-support')
    if not empty <= reported:
        raise ValueError('Eligible empty keys must be an exact subset of the declared reported keys')
    names = _names(row)
    if set(row['readings']) != set(names):
        raise ValueError('Exact original subreading population is required; no dropped or invented statistic')
    result = dict(**{k: row[k] for k in KEY}, role=row['role'], inventorySha256=inventory_sha256,
        originalReference=copy.deepcopy(row['originalReference']), reference=copy.deepcopy(row['reference']),
        sourceReadings=copy.deepcopy(row['readings']), sourceHistorical=copy.deepcopy(row.get('historical', [])),
        checks=[], diagnostics=[], failures=[], unmeasured=[], complete=False)
    if row['statistic'] == 'owner-contracts':
        result.update(status='OWNER_CONTRACT_REQUIRED', reason='Source-owned owner referee is separate from numeric routing')
        return result
    is_reported = key in reported
    if is_reported and (row['sceneSource'] != 'w50' or row['family'] != 'span' or \
            row['statistic'] not in N.LUMA+('T1-full-silhouette',)):
        raise ValueError('A reported-key policy cannot waive a required level or unrelated statistic')
    for name in names:
        source = row['readings'][name]
        if source.get('reported') is not is_reported or \
                source.get('eligibleEmptySupport', False) is not (key in empty):
            raise ValueError('Reading reporting/empty flags differ from the exact root key sets')
        if is_reported and source.get('B') is not None:
            raise ValueError('Exact reported rows must retain B:null')
    contracts = {name: _contracts(row, name, inventory_sha256,
        frozen=row['sceneSource'] == 'canonical' and row['renderer'] == 'webgpu' and name == row['statistic'])
        for name in names}
    source_contracts = {
        name: _contracts(row, name, inventory_sha256, source_override=row['readings'][name]['sourceReading'])
        if reference.frozen_t1_budget is not None else (reference, candidate)
        for name, (reference, candidate) in contracts.items()}
    _same_sources(source_contracts)
    if is_reported:
        for name, (ref, candidate) in contracts.items():
            result['diagnostics'].append(_check('reported-native-error', ref, N.diagnostic_reading(ref, candidate)))
        if any(row['readings'][n]['nativeMeasurementStatus'] == 'UNMEASURED_EMPTY_SUPPORT' for n in names):
            if key not in empty: raise ValueError('An empty native T1 has no exact eligibility')
            result.update(status='UNMEASURED_EMPTY_SUPPORT', complete=True,
                          emptySupportWitnesses=_empty_witness(row, names[0]))
            return result
    elif row['sceneSource'] == 'w50' and row['family'] in ('uniform', 'span'):
        code = row['inputCode']
        if type(code) not in (int, float) or not (0 <= code <= 40 or code == 64):
            raise ValueError('Only declared low-end0..40 and held64 controls are routed')
        if names[0] not in N.CHANNELS:
            raise ValueError('Non-reported uniform/span closure is a deep8 or central8 channel row')
        ref, candidate = contracts[names[0]]
        if code == 64:
            result['diagnostics'].append(_check('held64-native-error', ref, N.diagnostic_reading(ref, candidate)))
            result['numericalIdentity'] = 'REQUIRED_SEPARATE_JOIN_REFEREE'
        elif row['renderer'] == 'css':
            result['checks'].append(_check('css-level-error-growth', ref, N.css_level_growth(ref, candidate)))
            result['diagnostics'].append(_check('css-absolute-native-error', ref, N.diagnostic_reading(ref, candidate)))
        else:
            result['checks'].append(_check('absolute-level', ref, N.channel_level(ref, candidate)))
    elif row['sceneSource'] == 'canonical' and row['statistic'] == 'low-end-path-level':
        if row['renderer'] == 'webgpu' and row['family'] == 'impulse':
            comparisons = N.luma_levels(*contracts[N.LUMA[0]], *contracts[N.LUMA[1]])
        elif row['renderer'] == 'webgpu':
            comparisons = (N.channel_level(*contracts[N.CHANNELS[0]]),)
        else:
            comparisons = tuple(N.css_level_growth(*contracts[n]) for n in names)
        for name, comparison in zip(names, comparisons):
            ref, candidate = contracts[name]
            result['checks'].append(_check('absolute-level' if row['renderer']=='webgpu' else
                                          'css-level-error-growth', ref, comparison))
            if row['renderer'] == 'css':
                result['diagnostics'].append(_check('css-absolute-native-error', ref, N.diagnostic_reading(ref, candidate)))
    elif row['statistic'] in N.T1_REGRESSION:
        ref, candidate = contracts[row['statistic']]
        if row['sceneSource'] == 'w50':
            result['checks'].append(_check('newbed-structured-T1-growth', ref,
                                           N.newbed_structured_t1_growth(ref, candidate)))
        elif row['renderer'] == 'webgpu':
            result['checks'].append(_check('canonical-T1-growth', ref, N.t1_growth(ref, candidate)))
            result['checks'].extend(_histories(row, row['statistic'], ref, candidate))
        for name in names:
            result['diagnostics'].append(_check('texture-native-error', source_contracts[name][0],
                                                N.diagnostic_reading(*source_contracts[name])))
    else:
        # The NEWBED structured family has level rows as well as its separately keyed T1 row.
        for name in names:
            ref, candidate = contracts[name]
            if name in N.CHANNELS:
                comparison = N.channel_level(ref, candidate) if row['renderer']=='webgpu' else N.css_level_growth(ref,candidate)
            elif name in N.LUMA:
                # These structured mean/median keys are independent original keys. The
                # numeric primitive owns their arithmetic; the whole-key population owns
                # the intersection, never a manufactured companion reference.
                comparison = N.luma_level(ref, candidate) if row['renderer']=='webgpu' else N.css_level_growth(ref, candidate)
            else: raise ValueError('Unknown structured level statistic')
            result['checks'].append(_check('absolute-level' if row['renderer']=='webgpu' else
                                          'css-level-error-growth', ref, comparison))
            if row['renderer']=='css':
                result['diagnostics'].append(_check('css-absolute-native-error', ref, N.diagnostic_reading(ref,candidate)))
    for check in result['checks']:
        label = check['rule']+':'+check['statistic']
        if check['comparison']['status'] == 'EXCEEDS': result['failures'].append(label)
        elif check['comparison']['status'] == 'UNMEASURED': result['unmeasured'].append(label)
    for check in result['diagnostics']:
        if check['comparison']['status'] == 'UNMEASURED':
            result['unmeasured'].append(check['rule']+':'+check['statistic'])
    for name in names:
        for side in ('native', 'current', 'candidate'):
            if row['readings'][name][side+'MeasurementStatus'] != 'MEASURED':
                result['unmeasured'].append('source-'+side+':'+name)
    result['status'] = 'UNMEASURED' if result['unmeasured'] else 'EXCEEDS' if result['failures'] else \
        'WITHIN' if result['checks'] else 'DIAGNOSTIC'
    result['complete'] = not result['unmeasured']
    return result


def route_rows(rows, **policy):
    keys = [_key(row) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate original numeric row key')
    return [route_row(row, **policy) for row in rows]


def route_targets(contract, *, full_union=False):
    """The six declared aggregates wait for the authenticated complete union (DL5d).

    On the full union, contract maps each (target, scale) to {cells, expectedKeys}, using
    numerical.AggregateCell/RowIdentity contracts with source-native code and original
    full-pair W48 baselines already authenticated by the caller. No B-derived epsilon exists.
    """
    if type(full_union) is not bool:
        raise ValueError('Explicit authenticated full-union timing must be boolean')
    if not full_union:
        return [dict(target=name, scale=scale, status='PENDING_FULL_UNION') for name, scale in TARGETS]
    if not isinstance(contract, dict) or set(contract) != set(TARGETS):
        raise ValueError('Full-union target evaluation requires all six exact population contracts')
    return [asdict(N.target_aggregate(name, scale, contract[(name,scale)]['cells'],
                                     expected_keys=contract[(name,scale)]['expectedKeys']))
            for name, scale in TARGETS]
