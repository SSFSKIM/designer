"""Serializable measurement identities and unit-preserving projections, never comparisons.

Producer-native budgets stay together. A populated adopted reference budget is recorded
separately as originalBudgetB by phase.py; new native repeats do not rebase it. Native three-run
aggregate identities hash the ordered original run records, not a fictitious single PNG.
"""
import copy
import hashlib
import json
import math
import re

KEY = ('profile', 'renderer', 'scene', 'statistic')


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def checked_hash(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Complete measurement identity SHA-256 required')
    return value


def statistic_names(row, declaration):
    name = row['statistic']
    if name == 'owner-contracts': return []
    if name == 'low-end-path-level':
        if declaration['family'] == 'impulse':
            return ['deep8-far24-luma-mean', 'deep8-far24-luma-median']
        if declaration['family'] == 'solid': return ['deep8-channel-median']
        raise ValueError('Compound path reading needs its declared solid/impulse family')
    return [name, 'T1-fine'] if name == 'T1-low' else [name]


def budget(statistic):
    repeat = statistic.get('nativeRepeat')
    if repeat is None: return None, None, None
    units = statistic['units']
    if 'code' in repeat:
        code, bar, bound = repeat['code'], repeat['bar'], repeat['B']
    elif units == 'linear-luma':
        code, bar = repeat['codeStepLinear'], repeat['barLinear']
        bound = max(code, 2*bar)
    else:
        bar = repeat['barCodes']
        code = [1]*3 if units == 'encoded-RGB-codes' else 1
        bound = [max(1, 2*v) for v in bar] if isinstance(bar, list) else max(1, 2*bar)
    return copy.deepcopy(code), copy.deepcopy(bar), copy.deepcopy(bound)


def identity(statistic, value, evidence, *, native=False):
    content = {k: copy.deepcopy(statistic.get(k)) for k in
               ('units', 'support', 'nativeSupportWitnesses', 'nativeRepeat')}
    content['value'] = copy.deepcopy(value)
    if native:
        if statistic.get('nativeImage') is not None:
            capture = {'kind': 'png', 'pin': copy.deepcopy(statistic['nativeImage'])}
            capture_hash = checked_hash(capture['pin']['sha256'])
        else:
            runs = statistic['nativeRuns']
            if [r['run'] for r in runs] != [1, 2, 3]:
                raise ValueError('Native aggregate identity needs its three ordered true run records')
            capture = {'kind': 'native-three-run-cohort', 'runs': copy.deepcopy(runs)}
            capture_hash = digest(capture)
        pair = None
    else:
        capture = {'kind': 'png', 'pin': copy.deepcopy(evidence['capture'])}
        capture_hash = checked_hash(capture['pin']['sha256'])
        pair = copy.deepcopy(evidence['material']['documentPair'])
        for slot in ('activeSha256', 'recededSha256'): checked_hash(pair[slot])
    capture['digest'] = capture_hash
    provenance = statistic.get('nativeProvenance', {}) if native else evidence
    return dict(copy.deepcopy(provenance), captureIdentity=capture,
        numericIdentity={'captureSha256': capture_hash, 'statisticSha256': digest(content),
                         'documentPair': pair})


def reading(candidate, current, candidate_evidence, current_evidence, *, reported, eligible_empty):
    """A same-native-support reading; transport MAD is not a statistic, code step or budget."""
    for field in ('units', 'support', 'nativeValue', 'nativeRepeat', 'nativeSupportWitnesses'):
        if current is not None and current.get(field) != candidate.get(field):
            raise ValueError('Current/candidate readings differ on their original native source/support')
    status = candidate['measurementStatus']
    witnesses = candidate['nativeSupportWitnesses']
    if status == 'UNMEASURED_EMPTY_SUPPORT' and candidate['support'] == 'full-silhouette':
        if not reported or not eligible_empty or len(witnesses) != 3 or \
                [w['run'] for w in witnesses] != [1, 2, 3] or any(w['pixels'] != 0 for w in witnesses):
            raise ValueError('Empty T1 needs exact eligibility and three original zero-support witnesses')
    units = candidate['units']
    ceiling = 1 if units == 'linear-luma' else 255
    values = (candidate.get('nativeValue'), candidate['value'], current['value'] if current else None)
    for value in values:
        if value is None: continue
        members = value if isinstance(value, list) else [value]
        if units == 'encoded-RGB-codes' and (not isinstance(value, list) or len(value) != 3):
            raise ValueError('RGB reading must retain all three channels')
        if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= ceiling for v in members):
            raise ValueError('Nonfinite or out-of-domain producer reading')
    code, bar, bound = budget(candidate)
    evidence = {'native': identity(candidate, values[0], candidate_evidence, native=True),
                'candidate': identity(candidate, candidate['value'], candidate_evidence)}
    if current is not None:
        evidence['current'] = identity(current, current['value'], current_evidence)
    return {'units': units, 'support': candidate['support'], 'measurementStatus': status,
        'nativeMeasurementStatus': 'MEASURED' if values[0] is not None else status,
        'currentMeasurementStatus': current['measurementStatus'] if current else 'UNMEASURED',
        'candidateMeasurementStatus': status, 'native': copy.deepcopy(values[0]),
        'current': copy.deepcopy(values[2]), 'candidate': copy.deepcopy(values[1]),
        'code': code, 'bar': bar, 'B': None if reported else bound,
        'budgetDomain': 'PRODUCER_NATIVE_REPEAT', 'nativeRepeat': copy.deepcopy(candidate['nativeRepeat']),
        'nativeSupportWitnesses': copy.deepcopy(witnesses), 'required': candidate['required'],
        'reported': reported, 'eligibleEmptySupport': eligible_empty, 'evidence': evidence}


def frozen_scope(row):
    return (row['renderer'] == 'webgpu' and
        re.fullmatch(r'apple-macos-27\.0-[12]x-dark-standard-glass0\.25', row['profile']) is not None and
        row['statistic'] in ('T1-full-silhouette', 'T1-low') and row.get('B') is not None and
        row.get('nativeIdentity') is None)


def frozen_operand(row, inventory_pin, name, side):
    """Bind an ORIGINAL inventory operand as a source record, not a recomputed PNG statistic."""
    record = {'kind': 'frozen-reference-record', 'inventory': copy.deepcopy(inventory_pin),
        'key': [row[k] for k in KEY], 'side': side, 'original': copy.deepcopy(row)}
    capture_hash = digest(record)
    pair = None if side == 'native' else {'activeSha256': checked_hash(row['currentDocumentPair']['active.dark']),
                                        'recededSha256': checked_hash(row['currentDocumentPair']['receded.dark'])}
    return {'captureIdentity': dict(record, digest=capture_hash),
        'originalCapture': copy.deepcopy(row.get(side+'Evidence')),
        'routingOperands': 'ORIGINAL_INVENTORY',
        'numericIdentity': {'captureSha256': capture_hash,
            'statisticSha256': digest({'inventory': inventory_pin, 'key': record['key'],
                'statistic': name, 'side': side, 'value': row[side], 'original': row}),
            'documentPair': pair}}


def frozen_primary(original, reference, source_reading, production, inventory_pin):
    """Reconcile the frozen comparison contract without changing its operands or estimator.

    Full T1 is source-owned TS sequential accumulation; text low is the original NumPy
    Gaussian-band estimator. Recomputed native/current statistics and native-repeat budgets
    remain complete diagnostics. Original normalized history is never recomputed from them.
    """
    if not frozen_scope(original): return copy.deepcopy(source_reading)
    for field in ('native', 'current', 'B', 'historical'):
        if reference.get(field) != original.get(field):
            raise ValueError('Frozen canonical reference changed its original operands/history')
    if original.get('native') is None or original.get('current') is None:
        raise ValueError('Frozen canonical primary requires its original finite operands')
    name = original['statistic']
    full = name == 'T1-full-silhouette'
    estimator = 'PRODUCTION_TS_INTERIOR_LEVEL' if full else 'CANONICAL_NUMPY_GAUSSIAN_LOW'
    producer = ('packages/calibration/src/metrics/material.ts#interiorLevel' if full else
        'packages/calibration/results/2026-10-08-w50-g1-fit/references/statistics.py#canonical_read')
    field = 'material.interiorStdDevWeb' if full else 'web.statistics.T1-low'
    if not isinstance(production, dict) or any(production.get(k) != v for k, v in (
            ('estimator', estimator), ('statistic', name), ('producer', producer), ('field', field),
            ('reading', 'first'), ('scene', original['scene']), ('units', 'linear-luma'))):
        raise ValueError('Frozen candidate needs its named source-owned first-image producer')
    checked_hash(production['matrix']['sha256'])
    capture = source_reading['evidence']['candidate']['captureIdentity']
    if capture.get('kind') != 'png' or production['capture'] != capture['pin']:
        raise ValueError('Production statistic differs from the authenticated first PNG')
    value = production.get('value')
    if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1):
        raise ValueError('Production T1 must be finite linear-luma SD')
    result = copy.deepcopy(source_reading)
    result['sourceReading'] = copy.deepcopy(source_reading)
    result.update(native=original['native'], current=original['current'], candidate=value,
        nativeMeasurementStatus='MEASURED', currentMeasurementStatus='MEASURED',
        candidateMeasurementStatus='MEASURED' if value is not None else 'UNMEASURED',
        measurementStatus='MEASURED' if value is not None else 'UNMEASURED',
        routingOperands='ORIGINAL_INVENTORY', candidateEstimator=estimator,
        originalBudgetB=original['B'], supportWitnessDomain='NUMPY_DIAGNOSTIC_NATIVE_MASK')
    if value is None:
        result['candidateReason'] = 'Source-owned production statistic is absent on the first reading'
    result['evidence']['native'] = frozen_operand(original, inventory_pin, name, 'native')
    result['evidence']['current'] = frozen_operand(original, inventory_pin, name, 'current')
    candidate_evidence = result['evidence']['candidate']
    candidate_evidence['productionStatistic'] = copy.deepcopy(production)
    candidate_evidence['numericIdentity']['statisticSha256'] = digest(production)
    return result


def histories(row, inventory_pin, name):
    """Frozen numeric history has source-record identity, never an invented per-PNG pin."""
    if name != row['statistic']: return []
    output = []
    for index, item in enumerate(row.get('historical', [])):
        pair = item['documentPair']
        normalized = {'activeSha256': checked_hash(pair['active.dark']),
                      'recededSha256': checked_hash(pair['receded.dark'])}
        binding = {'kind': 'frozen-reference-record', 'inventory': copy.deepcopy(inventory_pin),
            'key': [row[k] for k in KEY], 'index': index, 'original': copy.deepcopy(item)}
        capture_hash = digest(binding)
        output.append({'original': copy.deepcopy(item), 'captureIdentity': dict(binding, digest=capture_hash),
            'numericIdentity': {'captureSha256': capture_hash, 'statisticSha256': digest(item),
                                'documentPair': normalized}})
    return output
