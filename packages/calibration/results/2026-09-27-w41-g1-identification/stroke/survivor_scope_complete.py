"""Freeze surviving-scope starts, then perform only their read-only transfer.

M0bothinactive/M1darkinactive/allCSS rivals retain exact certificate determinations; no absent
optimizer outcome is fabricated for them. M1 predictions interpret LIonly, M2both.
"""
import argparse
from collections import Counter
from itertools import combinations
import hashlib
import json
import re
from pathlib import Path
import numpy as np
import inactive_runner as runner
import survivor_scope_runner as scope
import execute
import scoring
import diagnostics

r = runner.r


def merge(starts, family, geometry):
    if sorted(row['startIndex'] for row in starts) != list(range(16)):
        raise ValueError('complete unique original16start population required')
    records = sorted(starts, key=lambda row: row['startIndex'])
    def best(key, objective):
        good = [row for row in records if row[key]['converged'] or
                (key == 'minimax' and row[key]['zeroFloorBracketCodes'] is not None)]
        if not good:
            return None
        row = min(good, key=lambda v: (v[key][objective], v['startIndex']))
        return dict(startIndex=row['startIndex'], **row[key])
    return dict(family=family, geometry=geometry, starts=records,
        leastSquares=best('leastSquares', 'weightedSquaredError'),
        minimax=best('minimax', 'maximumCodes'),
        classification='LOCAL; full sealed multistart/width budgets; active slots unobserved',
        authority='fresh inactive endpoint candidate under explicit parent authority deviation')


def interior_support_rows(observations):
    """Persist the already-prepared interior support facts, not a body fit."""
    return [dict(cell=o['cell'], role=o['role'], endpoint=r.ENDPOINTS[o['endpoint']],
                 scale=o['scale'], member=part['member'], shell=row['shell'],
                 pixels=row['pixels'], outsideSubpixels=row['outsideSubpixels'],
                 zeroStrokeWitness=row['zeroStrokeWitness'],
                 qualification='support only; not inside-body accuracy')
            for o in observations for part in o['parts'] for row in part['interior']]


def separation_availability(available, endpoint, objective, statuses=None):
    """Only an actually frozen local candidate supplies predictions; certificates do not."""
    names = [f'{family}-{geometry}' for family in ('M0', 'M1', 'M2')
             for geometry in ('device', 'css', 'curvature')]
    rows = []
    for left, right in combinations(names, 2):
        if left == right:
            continue
        missing = [name for name in (left, right) if name not in available]
        reason = None
        if endpoint.endswith('-active'):
            reason = 'certified held-shadow-control endpoint; unfitted'
        elif any(name.startswith('M0-') for name in missing):
            reason = 'certified M0 inactive scope; unfitted'
        elif endpoint == 'dark-inactive' and any(name.startswith('M1-') for name in missing):
            reason = 'certified M1 dark-inactive endpoint; unfitted'
        elif any(name.endswith('-css') for name in missing):
            reason = 'certified geometry; unfitted'
        elif missing:
            reason = 'unfitted; no prediction available'
        status = 'UNAVAILABLE: '+reason if reason else \
            'AVAILABLE: unconverged forward diagnostic; no survival claim' if \
            any((statuses or {}).get(name, '').startswith('unconverged') for name in (left, right)) \
            else 'AVAILABLE: local model-instance predictions only'
        rows.append(dict(models=[left, right], endpoint=endpoint, objective=objective,
                         status=status))
    return rows


def separation_rows(o, predictions):
    """Compare actual pixel predictions, not signed bin means or family envelopes."""
    for part in o['parts']:
        for bi, binrow in enumerate(part['bins']):
            if binrow['pixels'] < 4:
                continue
            at = o['binids'] == part['offset']+bi
            if int(at.sum()) != binrow['pixels']:
                raise ValueError('prepared array lost an admitted separation bin pixel')
            native = o['runs'][:, at]
            bar = .5+.5*np.ptp(native.mean(1), axis=0)
            # A channel with any rail sample cannot witness an uncensored separation.
            uncensored = np.all((native > 5) & (native < 250), axis=(0, 1))
            for left, right in combinations(sorted(predictions), 2):
                difference = abs(predictions[left][at]-predictions[right][at])
                for channel in range(3):
                    if not uncensored[channel]:
                        continue
                    threshold = max(3., float(2*bar[channel]))
                    mean = float(difference[:, channel].mean())
                    yield dict(cell=o['cell'], role=o['role'], endpoint=r.ENDPOINTS[o['endpoint']],
                        scale=o['scale'], member=part['member'], part=binrow['part'],
                        side=binrow['side'], shell=binrow['shell'], bin=binrow['bin'],
                        models=[left, right], channel='RGB'[channel], pixels=binrow['pixels'],
                        meanAbsoluteDifferenceCodes=mean, resolutionBoundCodes=threshold,
                        resolvedInstance=mean >= threshold,
                        qualification='local model-instance separation; no global family claim')


def separation_report(observations, selected, objective, emit):
    counts = Counter()
    maxima = {}
    for o in observations:
        endpoint = r.ENDPOINTS[o['endpoint']]
        predictions = {name: r.compact_predict(q, o, family, False, geometry == 'curvature')
                       for name, (q, family, geometry) in selected.items()
                       if family == 'M2' or endpoint == 'light-inactive'}
        for row in separation_rows(o, predictions):
            row['objective'] = objective
            emit(row)
            key = '/'.join((*row['models'], endpoint, o['role'], str(o['scale'])+'x'))
            counts[key+'/uncensoredBinChannels'] += 1
            counts[key+'/resolvedBinChannels'] += row['resolvedInstance']
            maxima[key] = max(maxima.get(key, 0.), row['meanAbsoluteDifferenceCodes'])
    return dict(counts=dict(counts), maximumMeanAbsoluteDifferenceCodes=maxima,
                qualification='available local instances only; no global family theorem')


def collect_inputs(partitions):
    merged, source_files = {}, {}
    records = {(family, geometry): [] for family in ('M1', 'M2')
               for geometry in ('device', 'curvature')}
    seeds = {}
    for family, geometry in records:
        low, high, initial = r.f.domain(family, geometry == 'curvature')
        seeds[(family, geometry)] = [initial, *np.random.default_rng(4100).uniform(
            low, high, (15, len(initial)))]
    for partition in partitions:
        if not partition.is_dir():
            raise ValueError('partition result directory missing: '+str(partition))
        for path in sorted(partition.glob('*-start-*.json')):
            match = re.fullmatch(r'(device|curvature|css)-(M[012])-start-(\d+)\.json', path.name)
            if not match:
                raise ValueError('malformed result filename: '+str(path))
            geometry, family, indexed = match.groups()
            if (family, geometry) not in records:
                continue  # The CSS and M0 scopes are certified elsewhere, never fitted here.
            raw = path.read_bytes()
            try:
                result = json.loads(raw)
                starts = result['starts']
                if len(starts) != 1 or not isinstance(starts[0], dict):
                    raise ValueError('malformed single-start result')
                row = starts[0]
                if not all(isinstance(row.get(key), dict) and
                           isinstance(row[key].get('converged'), bool) and
                           isinstance(row[key].get(metric), (float, int)) and
                           np.isfinite(row[key][metric]) for key, metric in
                           (('leastSquares', 'weightedSquaredError'), ('minimax', 'maximumCodes'))):
                    raise ValueError('malformed optimizer objective')
                if row.get('startIndex') != int(indexed) or not 0 <= int(indexed) < 16:
                    raise ValueError('start identity differs from result filename')
                original = np.asarray(row['initial'], dtype=float)
                if not np.array_equal(original, seeds[(family, geometry)][int(indexed)]):
                    raise ValueError('original seeded start changed')
                for key in ('leastSquares', 'minimax'):
                    fitted = row[key]
                    coefficients = np.asarray(fitted['coefficients'], dtype=float)
                    if coefficients.shape != original.shape or not np.all(np.isfinite(coefficients)) \
                            or not isinstance(fitted['rank'], int) \
                            or not isinstance(fitted['singularValues'], list) \
                            or not np.isfinite(fitted['railDeficitCodes']) \
                            or 'zeroFloorBracketCodes' not in fitted:
                        raise ValueError('malformed optimizer objective')
                if result['family'] != family or result['cssWidth'] is not False or \
                        result['curvature'] != (geometry == 'curvature'):
                    raise ValueError('partition result family/geometry mismatch')
                expected = ['light-inactive'] if family == 'M1' else \
                    ['light-inactive', 'dark-inactive']
                if result.get('fittedEndpoints') != expected:
                    raise ValueError('result fitted a different endpoint scope')
            except (KeyError, TypeError, json.JSONDecodeError) as error:
                raise ValueError('malformed result: '+str(path)) from error
            records[(family, geometry)].append(row)
            source_files[str(path)] = hashlib.sha256(raw).hexdigest()
    for (family, geometry), starts in records.items():
        indices = [row['startIndex'] for row in starts]
        if len(indices) != len(set(indices)):
            raise ValueError('duplicate original start: '+family+'/'+geometry)
        merged[geometry+'-'+family] = merge(starts, family, geometry)
    return merged, source_files


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--partition', action='append', help='override default partition/result directories')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    output = Path(args.out).resolve()
    if runner.PRIMARY not in output.parents:
        raise ValueError('outputs must stay beneath primary stroke evidence')
    r.verify_seal()
    authority = scope.verify_authority()
    css_path = runner.PRIMARY/'css-width-certificate/bounded/certificate.json'
    css_digest = hashlib.sha256(css_path.read_bytes()).hexdigest()
    css_review_path = runner.PRIMARY/'css-width-independent-review.json'
    css_review = json.loads(css_review_path.read_text())
    if css_digest != '72ab4a2bfc68d0d5e2864cc2f7a49ec05d64aba6f123811818194d0f5610b28d' \
            or css_review['certificateSha256'] != css_digest \
            or css_review['verdict'] != 'correct; no material findings':
        raise ValueError('reviewed CSS determination required before omitting its optimizer work')
    authority = dict(authority, cssWidthDetermination=dict(path=str(css_path), sha256=css_digest,
        reviewSha256=hashlib.sha256(css_review_path.read_bytes()).hexdigest()))
    defaults = [runner.PRIMARY/f'survivor-scope-partition-{i}' for i in range(3)] + \
        [runner.PRIMARY/'scheduler-run-1/results']
    partitions = [Path(p).resolve() for p in args.partition] if args.partition else defaults
    if len(set(partitions)) != len(partitions):
        raise ValueError('duplicate partition directory')
    merged, source_files = collect_inputs(partitions)
    output.mkdir(exist_ok=False)
    execute.json_write(output/'frozen-optimizer-inputs.json', source_files)
    execute.json_write(output/'certificate-authority.json', authority)
    if any(hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest
           for path, digest in source_files.items()):
        raise ValueError('frozen optimizer input changed before native boundary')
    for name, result in merged.items():
        execute.json_write(output/(name+'-optimizer.json'), result)
    preparation = r.Preparation()
    calibration = runner.load_inactive(preparation, 'calibration')
    validation = runner.load_inactive(preparation, 'validation')
    all_observations = calibration+validation
    execute.json_write(output/'admission.json', [dict(cell=o['cell'], role=o['role'],
        scale=o['scale'], stateMembership=o['stateMembership']) for o in all_observations])
    execute.json_write(output/'interior-support-witnesses.json',
                       interior_support_rows(all_observations))
    controls = scoring.inactive_zero_controls(all_observations)
    all_candidates = {}
    for name, result in merged.items():
        family, geometry = result['family'], result['geometry']
        css, curvature = geometry == 'css', geometry == 'curvature'
        observations = [o for o in all_observations if family == 'M2' or o['endpoint'] == 1]
        endpoints = ('light-inactive',) if family == 'M1' else ('light-inactive', 'dark-inactive')
        candidates = {}
        for objective in ('leastSquares', 'minimax'):
            row, status = execute.select_prediction(result, objective)
            q = np.array(row['coefficients'])
            score = execute.gzip_rows(output/f'{name}-{objective}-bins.jsonl.gz', lambda emit:
                scoring.score_candidate(observations, q, family, css, curvature, controls, emit))
            # The reused scorer's absent-active summary is not a failed endpoint.
            score.pop('activeSecond')
            score['survives'] = score['inactiveFirst']['survives']
            score['scope'] = 'surviving inactive endpoints only; certified endpoints not interpreted'
            endpoint_survival = {}
            for endpoint in endpoints:
                strata = [v for k, v in score['strata'].items() if k.startswith(endpoint+'/')]
                endpoint_survival[endpoint] = len(strata) == 4 and all(v['survives'] for v in strata) \
                    and result[objective] is not None
            coefficients = execute.coefficient_table(row, family, curvature, True)
            if family == 'M1':
                coefficients['endpoints'].pop('dark-inactive')
            coefficients['interpretedEndpoints'] = list(endpoints)
            candidate = dict(objective=objective, status=status,
                coefficients=coefficients,
                optimizerConverged=row['converged'], rank=row['rank'],
                singularValues=row['singularValues'], railDeficitCodes=row['railDeficitCodes'],
                scoring=score, endpointSurvival=endpoint_survival,
                activeEndpoints='identity; universally rejected by held-shadow control certificate')
            candidate['quadratureSensitivity'] = execute.gzip_rows(
                output/f'{name}-{objective}-quadrature.jsonl.gz', lambda emit:
                execute.sensitivity(observations, q, family, css, curvature, emit))
            candidate['straddlingDiagnostic'] = execute.gzip_rows(
                output/f'{name}-{objective}-straddling.jsonl.gz', lambda emit:
                diagnostics.straddling(observations, q, family, css, curvature, emit))
            execute.json_write(output/f'{name}-{objective}-summary.json', candidate)
            candidates[objective] = candidate
        all_candidates[name] = candidates
    for objective in ('leastSquares', 'minimax'):
        selected, statuses = {}, {}
        for name, result in merged.items():
            row, status = execute.select_prediction(result, objective)
            label = result['family']+'-'+result['geometry']
            selected[label] = (np.asarray(row['coefficients']), result['family'], result['geometry'])
            statuses[label] = status
        available = {endpoint: separation_availability(
            {name for name, (_, family, _) in selected.items()
             if family == 'M2' or endpoint == 'light-inactive'}, endpoint, objective, statuses)
            for endpoint in ('light-inactive', 'dark-inactive', 'light-active', 'dark-active')}
        execute.json_write(output/f'{objective}-separation-availability.json', available)
        summary = execute.gzip_rows(output/f'{objective}-separations.jsonl.gz',
            lambda emit: separation_report(all_observations, selected, objective, emit))
        execute.json_write(output/f'{objective}-separations-summary.json', summary)
    execute.json_write(output/'complete.json', dict(
        candidates={name: {objective: v['endpointSurvival'] for objective, v in rows.items()}
                    for name, rows in all_candidates.items()}, holdoutRead=False,
        authority='surviving model-endpoint scope; certified endpoints never fitted or interpreted'))


if __name__ == '__main__':
    main()
