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
