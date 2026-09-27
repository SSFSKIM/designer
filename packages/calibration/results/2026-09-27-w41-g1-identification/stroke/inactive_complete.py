"""Freeze all original start outcomes, then read validation for inactive transfer."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import inactive_runner as runner
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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--partition', action='append', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    output = Path(args.out).resolve()
    if runner.PRIMARY not in output.parents:
        raise ValueError('outputs must stay beneath primary stroke evidence')
    partitions = [Path(p).resolve() for p in args.partition]
    merged = {}
    source_files = {}
    # Refuse before any native read unless every9x16originalstart outcome exists.
    for family in ('M0', 'M1', 'M2'):
        for geometry in ('device', 'css', 'curvature'):
            starts = []
            for partition in partitions:
                for path in sorted(partition.glob(f'{geometry}-{family}-start-*.json')):
                    raw = path.read_bytes()
                    result = json.loads(raw)
                    if result['family'] != family or result['cssWidth'] != (geometry == 'css') \
                            or result['curvature'] != (geometry == 'curvature'):
                        raise ValueError('partition result family/geometry mismatch')
                    starts.extend(result['starts'])
                    source_files[str(path)] = hashlib.sha256(raw).hexdigest()
            merged[geometry+'-'+family] = merge(starts, family, geometry)
    output.mkdir(exist_ok=False)
    execute.json_write(output/'frozen-optimizer-inputs.json', source_files)
    for name, result in merged.items():
        execute.json_write(output/(name+'-optimizer.json'), result)
    preparation = r.Preparation()
    calibration = runner.load_inactive(preparation, 'calibration')
    validation = runner.load_inactive(preparation, 'validation')
    observations = calibration+validation
    execute.json_write(output/'admission.json', [dict(cell=o['cell'], role=o['role'],
        scale=o['scale'], stateMembership=o['stateMembership']) for o in observations])
    controls = scoring.inactive_zero_controls(observations)
    all_candidates = {}
    for name, result in merged.items():
        family, geometry = result['family'], result['geometry']
        css, curvature = geometry == 'css', geometry == 'curvature'
        candidates = {}
        for objective in ('leastSquares', 'minimax'):
            row, status = execute.select_prediction(result, objective)
            q = np.array(row['coefficients'])
            score = execute.gzip_rows(output/f'{name}-{objective}-bins.jsonl.gz', lambda emit:
                scoring.score_candidate(observations, q, family, css, curvature, controls, emit))
            # The reused scorer's absent-active summary is not a failed endpoint.
            score.pop('activeSecond')
            score['survives'] = score['inactiveFirst']['survives']
            score['scope'] = 'inactive pair only; active endpoints outside this authority'
            endpoint_survival = {}
            for endpoint in ('light-inactive', 'dark-inactive'):
                strata = [v for k, v in score['strata'].items() if k.startswith(endpoint+'/')]
                endpoint_survival[endpoint] = len(strata) == 4 and all(v['survives'] for v in strata) \
                    and result[objective] is not None
            candidate = dict(objective=objective, status=status,
                coefficients=execute.coefficient_table(row, family, curvature, True),
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
    execute.json_write(output/'complete.json', dict(
        candidates={name: {objective: v['endpointSurvival'] for objective, v in rows.items()}
                    for name, rows in all_candidates.items()}, holdoutRead=False,
        authority='inactive-only candidate; explicit scope deviation, no full-four-endpoint survival'))


if __name__ == '__main__':
    main()
