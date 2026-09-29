"""Derive endpoint-versus-family verdicts and the diagnostic spatial handoff.

This reads the write-once step-2 results, never native payloads and never fits.
It supplements attempt-1/summary.json: that file's generic 'LOCAL candidate
failure' label for a forward-feasible linear endpoint is a TRANSFER failure,
not a claim of global infeasibility. Colour and thick-transfer scopes stay apart.
Run with the pinned Python interpreter: report.py ATTEMPT NEW_OUTPUT_DIRECTORY.
"""
import argparse
import csv
import gzip
from itertools import combinations
import json
from pathlib import Path
import numpy as np
import replay


def derive(attempt, out):
    out.mkdir(parents=True, exist_ok=False)
    summary = json.loads((attempt / 'summary.json').read_text())
    rows = summary['strata']
    scores = json.loads(gzip.decompress((attempt / 'scores.json.gz').read_bytes()))
    endpoints = {}
    for path in sorted(attempt.glob('*-fit.json')):
        fit = json.loads(path.read_text())
        family, endpoint = fit['family'], fit['endpoint']
        method = 'localMinimax' if family == 'O12' else 'globalMinimax'
        rr = [r for r in rows if r['family'] == family and r['endpoint'] == endpoint and r['method'] == method]
        colour_pass = not any(r['failedCells'] for r in rr if r['population'] == 'colour')
        thick_pass = not any(r['failedCells'] for r in rr if r['population'] == 'thick-transfer')
        if colour_pass and thick_pass:
            status = 'endpoint survives both colour and thick transfer'
        elif colour_pass:
            status = 'colour endpoint survives; thick transfer fails'
        elif fit.get('survival', {}).get('status') == 'certified-infeasible':
            status = 'certified calibration rejection'
        else:
            status = 'LOCAL candidate fails; no global nonlinear negative'
        endpoints.setdefault(family, {})[endpoint] = dict(status=status,
            colourSurvives=colour_pass, thickTransferPasses=thick_pass,
            fullEndpointSurvives=colour_pass and thick_pass,
            calibrationAuthority=fit.get('survival', {}).get('status', 'LOCAL only'),
            method=method, source=path.name, sourceSha256=replay.digest(path))
    complete = {family: all(v['fullEndpointSurvives'] for v in eps.values())
                for family, eps in endpoints.items()}
    assert not any(complete.values()), 'A survivor needs its declared selection, not this diagnostic handoff'
    resolution = []
    for scope in ['colour', 'colour-and-thick-transfer']:
        for endpoint in replay.NEUTRALS:
            surviving = [f for f, eps in endpoints.items() if eps[endpoint][
                'colourSurvives' if scope == 'colour' else 'fullEndpointSurvives']]
            for a, b in combinations(surviving, 2):
                def predictions(f):
                    return {r['cell']: r for r in scores if r['family'] == f and
                            r['endpoint'] == endpoint and r['method'] == endpoints[f][endpoint]['method'] and
                            (scope != 'colour' or r['population'] == 'colour')}
                aa, bb = predictions(a), predictions(b)
                assert aa.keys() == bb.keys()
                comparisons = []
                for cell in sorted(aa):
                    delta = abs(np.array(aa[cell]['predictedRGB']) - bb[cell]['predictedRGB'])
                    threshold = np.maximum(3, np.array(aa[cell]['barRGB']) + bb[cell]['barRGB'])
                    # Rail-only comparisons do not invent measured resolution.
                    observed = np.array(aa[cell]['nativeRGB'])
                    admitted = (observed > 5) & (observed < 250)
                    for j in np.flatnonzero(admitted):
                        comparisons.append(dict(cell=cell, channel='RGB'[j],
                            separationCodes=float(delta[j]), thresholdCodes=float(threshold[j])))
                separated = [r for r in comparisons if r['separationCodes'] >= r['thresholdCodes']]
                resolution.append(dict(scope=scope, endpoint=endpoint, families=[a, b],
                    comparisons=len(comparisons), admittedSeparators=separated,
                    maximum=max(comparisons, key=lambda r: r['separationCodes']),
                    verdict='insufficient resolution' if not separated else 'resolved at listed instances',
                    rule='max(3 codes,sum of per-channel bars); fixed minimax instances, not universal family separation'))
    replay.save(out / 'endpoint-verdicts.json', dict(endpoints=endpoints,
        completeFourEndpointFamilies=complete,
        explanation='Light colour endpoints can survive without a complete four-endpoint family; thick transfer is independently tabled.',
        correctionToAttemptSummary='Linear light-active endpoint label LOCAL candidate failure means thick-transfer failure; it is forward feasible on calibration and colour validation.',
        resolution=resolution, exposureEligibleBodyFamilies=[]))
    mapping = {}
    for endpoint, neutral in replay.NEUTRALS.items():
        path = attempt / f'{endpoint}-E3-fit.json'
        fit = json.loads(path.read_text())
        mapping[endpoint] = dict(family='E3', coefficients=fit['globalMinimax']['coefficients'],
            neutral=neutral, status=endpoints['E3'][endpoint]['status'],
            colourSurvives=endpoints['E3'][endpoint]['colourSurvives'],
            fullEndpointSurvives=endpoints['E3'][endpoint]['fullEndpointSurvives'],
            purpose='DIAGNOSTIC B1, not a surviving four-endpoint body',
            source=str(path.resolve()), sourceSha256=replay.digest(path))
    replay.save(out / 'spatial-selection.json', dict(schema='w41-step2-spatial-selection-1',
        completeFamilySurvives=False, selectedFamily='E3', selection='diagnostic B1 by G1 step3 rule',
        declarationSha256=replay.DECLARATION_SHA, endpoints=mapping,
        resolution=resolution, holdoutOpened=False))
    table = []
    for path in sorted(attempt.glob('*-fit.json')):
        fit = json.loads(path.read_text())
        family, endpoint = fit['family'], fit['endpoint']
        mm = fit['local']['minimax'] if family == 'O12' else fit['globalMinimax']
        ls = fit['local']['leastSquares']
        table.append(dict(family=family, endpoint=endpoint,
            calibrationLSMaximumCodes=ls['maximumCodes'],
            calibrationMinimaxLowerCodes=mm.get('lowerCodes', ''),
            calibrationMinimaxUpperCodes=mm.get('upperCodes', mm.get('maximumCodes')),
            authority='LOCAL' if family == 'O12' else 'certified bracket',
            rank=mm['rank'], columns=mm['columns'],
            leastSquaresConvergedStarts=sum(r['leastSquares']['converged'] for r in fit['local']['starts']),
            minimaxConvergedStarts=sum(r['minimax']['converged'] for r in fit['local']['starts']),
            starts=16, status=endpoints[family][endpoint]['status']))
    with (out / 'fit-table.csv').open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0])); writer.writeheader(); writer.writerows(table)
    fields = ['family', 'endpoint', 'scale', 'method', 'role', 'population', 'cells', 'failedCells',
              'medianFailedChannels', 'medianRailFailures', 'allChannelFailedCells',
              'repeatFailedChannels', 'repeatRailFailures', 'maximumCodes', 'repeatMaximumCodes',
              'maximumRailDeficitCodes', 'worstCell', 'worstChannel']
    with (out / 'survival-table.csv').open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)
    replay.save(out / 'manifest.json', dict(scriptSha256=replay.digest(Path(__file__)),
        attemptManifestSha256=replay.digest(attempt / 'manifest.json'),
        files={p.name: replay.digest(p) for p in sorted(out.iterdir()) if p.is_file()}))
    print(json.dumps(dict(completeFamilies=complete, resolution=resolution), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('attempt', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    derive(args.attempt, args.out)
