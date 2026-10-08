"""Pure selection/projection beneath execution.py's verified root boundary.

These functions authenticate NOTHING: callers of the execution API cannot supply their inputs
as numeric overrides. Only the root-bound files, admitted before their values are read, feed
these functions in production. Tests use synthetic documents. No filesystem or solver imports.
"""
import copy
import hashlib
import json
import math
import re

ENDPOINTS = ('active.dark.0.25', 'receded.dark.0.25', 'active.dark.0.5', 'receded.dark.0.5')
CHANNELS = {'deep8-channel-median': 'deep8', 'central8-channel-median': 'center8'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def number(value, low, high):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError('Invalid finite observation/domain value')
    return value


def pin(value):
    if not isinstance(value, dict) or set(value) != {'path', 'sha256'} or \
            not isinstance(value['path'], str) or not value['path'] or \
            not isinstance(value['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', value['sha256']):
        raise ValueError('Exact content pin required')
    return copy.deepcopy(value)


def uniform_observations(manifest, scenes, reports, inventory, declaration_sha):
    """Exact exposed declared cells, not inferred native ordinates or per-pixel pooling."""
    if set(reports) != {'calibration', 'validation'}:
        raise ValueError('Exactly the two exposed native role reports are required')
    by_scene = {s['id']: s for s in scenes['scenes']}
    if len(by_scene) != len(scenes['scenes']):
        raise ValueError('Duplicate scene identity')
    observed = {}
    for role, report in reports.items():
        if (report.get('schema') != 'w50-native-role-read-1' or report.get('role') != role or
                report.get('ready') is not True or report.get('stops') != [] or
                report.get('declarationSha256') != declaration_sha):
            raise ValueError('Native role report is not admitted under the original declaration')
        expected = {c['id'] for c in manifest['cells'] if c['role'] == role}
        rows = report.get('cells', [])
        if len({c['id'] for c in rows}) != len(rows) or {c['id'] for c in rows} != expected:
            raise ValueError('Native report membership differs from the original exposed role')
        for cell in rows:
            if cell['role'] != role or cell['id'] in observed:
                raise ValueError('Duplicate or withheld native role member')
            observed[cell['id']] = cell
    declared = [c for c in manifest['cells'] if c['role'] in reports and c['family'] in ('uniform', 'span')]
    if len({c['id'] for c in manifest['cells']}) != len(manifest['cells']):
        raise ValueError('Duplicate original native identity')
    references = {}
    for row in inventory['cells']:
        references.setdefault((row['profile'], row['scene']), []).append(row)
    out = []
    for original in declared:
        scene = by_scene[original['scene']]
        background = scenes['backgrounds'][scene['background']]
        rgb = background.get('srgb')
        if background.get('kind') != 'solid' or not isinstance(rgb, list) or len(rgb) != 3 or len(set(rgb)) != 1:
            raise ValueError('Uniform/span initializer requires declared achromatic solid controls')
        level = number(rgb[0], 0, 255)
        if level > 40:
            continue  # input64 is a fixed-join diagnostic, not a fitted native ordinate.
        span = number(original['span'], 32, 224)
        match = re.fullmatch(r'cell-grey-(\d{3})-s(\d{3})__(rest|inactive)', original['scene'])
        profile = re.fullmatch(r'apple-macos-27\.0-([12])x-dark-standard-glass(0\.25|0\.5)', original['profile'])
        pose = 'receded' if original['scene'].endswith('__inactive') else 'active'
        if (not match or not profile or int(match[1]) != level or int(match[2]) != span or
                original['pose'] != pose or original['scale'] != int(profile[1]) or
                original['glass'] != float(profile[2]) or span == 224 or
                original['id'] != original['profile']+'/'+original['scene']):
            raise ValueError('Native uniform identity/domain differs from the original bed')
        owners = references.get((original['profile'], original['scene']), [])
        if not owners or any(r['role'] in ('blind', 'historical-prediction-check') for r in owners):
            raise ValueError('Missing or physically withheld reference cannot identify coefficients')
        for name in CHANNELS:
            if not any(r['statistic'] == name for r in owners):
                raise ValueError('Both original channel statistic keys are required')
        cell = observed[original['id']]
        if any(cell.get(k) != v for k, v in original.items() if k != 'runs'):
            raise ValueError('Native report changed declared cell identity/geometry/role')
        runs = cell.get('runs', [])
        if original.get('runs') != [1, 2, 3] or [r.get('run') for r in runs] != [1, 2, 3] or any(
                r.get('dependency') != original['reference'] or
                r.get('evidence', {}).get('run') != r['run'] or
                r.get('evidence', {}).get('cell') != original['id'] for r in runs):
            raise ValueError('Native report must retain its three original run/dependency identities')
        endpoint = f'{pose}.dark.{original["glass"]}'
        for name, support in CHANNELS.items():
            statistic = cell.get('statistics', {}).get(name, {})
            if (statistic.get('status') != 'MEASURED' or statistic.get('measurementStatus') != 'MEASURED' or
                    statistic.get('required') is not True or statistic.get('units') != 'encoded-RGB-codes' or
                    statistic.get('support') != support):
                raise ValueError('Missing exact measured native channel support')
            values = statistic.get('value')
            if not isinstance(values, list) or len(values) != 3:
                raise ValueError('All three native channel medians required')
            for channel, value in zip(('R', 'G', 'B'), values):
                out.append(dict(endpoint=endpoint, inputCode=level, span=span, dpr=original['scale'],
                    value=number(value, 0, 255), role=original['role'], nativeIdentity=original['id'],
                    statistic=name, channel=channel))
    if {(r['endpoint'], r['dpr']) for r in out} != {(e, d) for e in ENDPOINTS for d in (1, 2)}:
        raise ValueError('Initializer needs all four endpoints and both scales')
    return out


def join_observations(joins):
    if set(joins) != set(ENDPOINTS):
        raise ValueError('Every pinned gate0 endpoint requires fixed64 joins')
    expected = {(span, dpr) for span in range(32, 225) for dpr in (1, 2)}
    out = []
    for endpoint in ENDPOINTS:
        rows = joins[endpoint]
        if len(rows) != len(expected) or {(r['span'], r['dpr']) for r in rows} != expected:
            raise ValueError('Fixed joins must include every actual span32..224 at both scales')
        for row in rows:
            out.append(dict(endpoint=endpoint, span=row['span'], dpr=row['dpr'],
                            value=number(row['value'], 0, 255)))
    return out


def _cohort(values):
    if not isinstance(values, list) or len(values) != 2:
        raise ValueError('Exactly one candidate per declared position required')
    out = {}
    for row in values:
        if set(row) != {'position', 'path', 'sha256'} or row['position'] not in (.25, .5):
            raise ValueError('Wrong candidate cohort entry')
        if row['position'] in out:
            raise ValueError('Duplicate cohort position')
        out[row['position']] = pin({k: row[k] for k in ('path', 'sha256')})
    return out


def evaluation_arguments(records, required, captured_cohort, evaluation_cohort, held_proofs, source_pin):
    """Label evaluated material separately from actually captured material.

    candidateSha256 is the unchanged G0 schema's evaluation-cohort field. Every original
    record stays intact inside capturedArgument with its original candidateSha256, report,
    capture and currentCandidate pins; no source record or PNG metadata is rewritten.
    Proofs here are pure inputs, not self-authenticating credentials. execution.py obtains
    them only by invoking the source-guarded production material bridge after prefit.
    """
    source_pin = pin(source_pin)
    captured, evaluation = _cohort(captured_cohort), _cohort(evaluation_cohort)
    if (not required or len(records) != len(required) or {r['id'] for r in records} != set(required)):
        raise ValueError('Measured arguments must equal the complete original required-ID population')
    proofs = {}
    for proof in held_proofs:
        position = proof.get('position')
        if (proof.get('schema') != 'w50-held-sampling-proof-1' or position in proofs or
                proof.get('capturedCandidate') != captured.get(position) or
                proof.get('evaluationCandidate') != evaluation.get(position)):
            raise ValueError('Held sampling proof names another captured/evaluation pair')
        for value in (proof.get('heldMaterialSha256'), proof.get('cssTierMappingSha256'),
                      *proof.get('lightEndpointSha256s', [])):
            if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
                raise ValueError('Missing held-material evidence digest')
        if len(proof.get('lightEndpointSha256s', [])) != 2:
            raise ValueError('Both light endpoint byte witnesses required')
        proofs[position] = proof
    if set(proofs) != {.25, .5}:
        raise ValueError('Both positions need production held-sampling equality')
    output = []
    for source in sorted(records, key=lambda r: r['id']):
        reference = required[source['id']]
        if any(source.get(k) != reference.get(k) for k in ('profile', 'renderer', 'scene', 'role')) or \
                source['role'] in ('blind', 'historical-prediction-check'):
            raise ValueError('Measured argument has changed or withheld reference identity')
        position = source.get('position')
        before = captured.get(position)
        if before is None or source.get('candidateSha256') != before['sha256']:
            raise ValueError('Measured argument does not name its actually captured gate0 candidate')
        provenance = source.get('provenance', {})
        if provenance.get('candidateDocument') != before:
            raise ValueError('Original currentCandidate provenance differs from captured bytes')
        for name in ('report', 'capture'):
            pin(provenance.get(name))
        for field in ('encodedLuminance', 'linearLuminance'):
            number(source.get(field), 0, 1)
        rgb = source.get('rgb')
        if not isinstance(rgb, list) or len(rgb) != 3:
            raise ValueError('Measured argument requires original independent linear RGB')
        for value in rgb: number(value, 0, 1)
        wrapped = copy.deepcopy(source)
        evaluated = evaluation[position]['sha256']
        wrapped.update(candidateSha256=evaluated, evaluationCandidateSha256=evaluated,
            capturedCandidateSha256=before['sha256'], currentCandidate=copy.deepcopy(before),
            capturedArgument=copy.deepcopy(source), capturedArgumentSha256=digest(source),
            originalCurrentEvidence=copy.deepcopy(source_pin), heldSamplingProof=copy.deepcopy(proofs[position]),
            argumentSemantics='EVALUATED_CANDIDATE_USING_HELD_GATE0_SAMPLING')
        output.append(wrapped)
    return output
