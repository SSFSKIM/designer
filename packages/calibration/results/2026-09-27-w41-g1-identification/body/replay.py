"""W41 G1 step 2, charter clause 4 and c9a §5.192: uniform-body identification.

Replay with the pinned external interpreter and the fetched archive root:
  /tmp/w39-g2-wgpu/bin/python replay.py ARCHIVE --out NEW_DIRECTORY
Outputs are write-once. Calibration is the sole coefficient source; all twelve
fits are written and hashed before a validation-only Reader is constructed.
The sealed body41.py supplies every optimizer and numerical budget unchanged.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
G0 = RESULTS / '2026-09-27-w41-g0-declaration'
G2 = RESULTS / '2026-09-26-w39-g2-identification'
sys.path.insert(0, str(G0 / 'body-instrument'))
sys.path.insert(0, str(G2))
import body41 as body
import native

DECLARATION_SHA = '850747c1f03781a6efe9b433bd4ce3bd6cf72b63c9befd8d5d98de9eadf7f759'
INVENTORY_SHA = '58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61'
NEUTRALS = {
    'light-active': [152, 160, 168, 176, 183, 195, 205],
    'light-inactive': [150, 157, 164, 171, 178, 188, 197],
    'dark-active': [69, 83, 96, 108, 119, 134, 146],
    'dark-inactive': [60, 74, 87, 100, 111, 127, 140],
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    data = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    if path.suffix == '.gz':
        data = gzip.compress(data, mtime=0)
    with path.open('xb') as stream:
        stream.write(data)


def collect(archive, role):
    wave, reader = native.guarded(archive, (role,))
    assert reader.generation == INVENTORY_SHA
    rows = []
    for cell, kind in sorted(reader.entries):
        sid = cell.split('/', 1)[1]
        if kind != 'crop' or sid not in reader.allowed:
            continue
        component = wave.component(sid)
        background = wave.spec['backgrounds'][wave.scenes[sid]['background']]
        if component['kind'] == 'none' or component.get('opaque') or background['kind'] != 'solid':
            continue
        colour = '-colour__' in sid
        thick = min(component.get('size', [0, 0])) in (64, 96)
        if not (colour or thick):
            continue
        row = native.cell(reader, cell)
        assert len(row['members']) == 1
        assert len(row['stateMembership']) == 7
        assert min(row['members'][0]['pixels']) >= 4
        row.update(population='colour' if colour else 'thick-transfer',
                   inputCodes=background['srgb'], span=min(component['size']),
                   endpoint=row['scheme'] + ('-active' if row['pose'] == 'rest' else '-inactive'))
        rows.append(row)
    return rows


def arrays(rows):
    return (np.array([r['inputCodes'] for r in rows], float),
            np.array([r['members'][0]['medianRGB'] for r in rows], float),
            np.array([r['members'][0]['barRGB'] for r in rows], float))


def rank(family, x, neutral, target, q):
    measured = (target > 5) & (target < 250)
    p = body.SIZES[family]
    low, high = (-8., 8.) if family == 'O12' else (0., 3.)
    jac = body.approx_derivative(lambda v: body.forward(family, x, neutral, v)[measured],
                                np.array(q), bounds=(np.full(p, low), np.full(p, high)))
    return dict(rank=int(np.linalg.matrix_rank(jac)), columns=p,
                singularValues=np.linalg.svd(jac, compute_uv=False).tolist())


def verify_linear(family, x, neutral, target, bar, survival, minimax):
    checks = {}
    if survival['status'] == 'certified-infeasible':
        a, b, _ = body.constraints(family, x, neutral, target, np.maximum(1, bar))
        assert body.verify_certificate(survival['certificate'], a, b)
        checks['survivalCertificate'] = True
    elif survival['status'] == 'forward-feasible':
        s = body.score(body.forward(family, x, neutral, survival['coefficients']), target, bar)
        assert s['uncensoredFailures'] == s['railFailures'] == 0
        checks['survivalForward'] = True
    else:
        raise RuntimeError('STOP: sealed survival certificate budget exhausted: ' + str(survival))
    if minimax['status'] == 'global minimax bracket':
        a, b, _ = body.constraints(family, x, neutral, target, minimax['lowerCodes'])
        assert minimax['lowerCodes'] == 0 or body.verify_certificate(minimax['lowerCertificate'], a, b)
        prediction = body.forward(family, x, neutral, minimax['coefficients'])
        assert body._maximum(prediction, target) == minimax['upperCodes']
        assert not np.any(body._rail_deficit(prediction, target))
        assert minimax['bracketWidthCodes'] <= 1e-5
        checks.update(minimaxLowerCertificate=True, minimaxForwardUpper=True)
    elif minimax['status'] == 'certified-hard-rail-infeasible':
        a, b, _ = body.constraints(family, x, neutral, target, 255.)
        assert body.verify_certificate(minimax['lowerCertificate'], a, b)
        checks['hardRailCertificate'] = True
    else:
        raise RuntimeError('STOP: sealed minimax certificate budget exhausted: ' + str(minimax))
    return checks


def scored(fit, method, candidate, rows):
    family, endpoint = fit['family'], fit['endpoint']
    neutral, q = fit['neutralOrdinatesCodes'], candidate['coefficients']
    out = []
    for row in rows:
        if row['endpoint'] != endpoint:
            continue
        pred = body.forward(family, [row['inputCodes']], neutral, q)
        deep = row['members'][0]
        median = body.score(pred, [deep['medianRGB']], [deep['barRGB']])
        runs = body.score(np.repeat(pred, 7, axis=0), deep['runMediansRGB'], deep['barRGB'])
        out.append(dict(cell=row['cell'], family=family, endpoint=endpoint, scale=row['scale'],
                        role=row['role'], population=row['population'], method=method,
                        predictedRGB=pred[0].tolist(), nativeRGB=deep['medianRGB'],
                        barRGB=deep['barRGB'], pixels=deep['pixels'],
                        median=median, repeats=runs, stateMembership=row['stateMembership']))
    return out


def summarize(scores):
    summaries = []
    keys = sorted({(r['family'], r['endpoint'], r['scale'], r['method'], r['role'],
                    r['population']) for r in scores})
    for key in keys:
        rows = [r for r in scores if (r['family'], r['endpoint'], r['scale'], r['method'],
                                     r['role'], r['population']) == key]
        worst = max(rows, key=lambda r: r['median']['worstChannelCodes'])
        maximum = worst['median']['worstChannelCodes']
        errors = worst['median']['uncensoredErrorCodes'][0]
        channel = next(i for i, e in enumerate(errors) if e == maximum)
        worst_repeat = max(rows, key=lambda r: r['repeats']['worstChannelCodes'])
        failed = lambda s: s['uncensoredFailures'] + s['railFailures'] > 0
        statuses = Counter(v for r in rows for v in r['median']['statuses'][0])
        repeat_statuses = Counter(v for r in rows for rr in r['repeats']['statuses'] for v in rr)
        summaries.append(dict(zip(['family', 'endpoint', 'scale', 'method', 'role', 'population'], key),
            cells=len(rows), populationDeficientCells=0, statusCounts=dict(statuses),
            repeatStatusCounts=dict(repeat_statuses),
            failedCells=sum(failed(r['median']) or failed(r['repeats']) for r in rows),
            medianFailedChannels=sum(r['median']['uncensoredFailures'] for r in rows),
            medianRailFailures=sum(r['median']['railFailures'] for r in rows),
            allChannelFailedCells=sum(r['median']['allChannelFailedCells'] for r in rows),
            repeatFailedChannels=sum(r['repeats']['uncensoredFailures'] for r in rows),
            repeatRailFailures=sum(r['repeats']['railFailures'] for r in rows),
            worstCell=worst['cell'], worstChannel='RGB'[channel], maximumCodes=maximum,
            worstRepeatCell=worst_repeat['cell'],
            repeatMaximumCodes=worst_repeat['repeats']['worstChannelCodes'],
            maximumRailDeficitCodes=max(max(r['median']['boundDeficitCodes'][0]) for r in rows)))
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    assert digest(G0 / 'bounds-declaration.txt') == DECLARATION_SHA
    assert np.__version__ == '2.5.3' and scipy.__version__ == '1.18.1'
    sources = [Path(__file__), G0 / 'body-instrument/body41.py',
               G0 / 'body-instrument/execution-parameters.json', G2 / 'native.py',
               G2 / 'instrument/body.py', native.G0 / 'wave.py', native.G0 / 'w39_readers.py',
               native.G0 / 'w39_archive.py', native.G0 / 'replay-archive.py']
    save(args.out / 'provenance.json', dict(startedAt=stamp(), archive=str(args.archive),
         declarationSha256=DECLARATION_SHA, inventorySha256=INVENTORY_SHA,
         python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
         rawRootDenied=str(Path.home() / 'vitrea-w39'), holdoutOpened=False,
         sources={str(p.relative_to(RESULTS)): digest(p) for p in sources}))
    calibration = collect(args.archive, 'calibration')
    colours = [r for r in calibration if r['population'] == 'colour']
    assert len(colours) == 408
    _, y, _ = arrays(colours)
    measured = (y > 5) & (y < 250)
    assert measured.sum() == 1220 and (~measured).sum() == 4
    assert np.all(measured, axis=1).sum() == 404
    for endpoint, neutral in NEUTRALS.items():
        for code, ordinate in zip(body.KNOTS.astype(int), neutral):
            rows = [r for r in colours if r['endpoint'] == endpoint and
                    r['cell'].split('/', 1)[1].startswith(f'neutral-{code}-colour__')]
            assert len(rows) == 2 and {r['scale'] for r in rows} == {1, 2}
            assert all(r['members'][0]['medianRGB'] == [ordinate] * 3 for r in rows)
    save(args.out / 'calibration.json.gz', dict(rows=calibration, verifiedNeutrals=NEUTRALS,
         populations=dict(w41Cells=408, w41UncensoredChannels=1220, w41RailBounds=4,
                          w39WholeCellIncluded=404, w39UncensoredChannels=1212)))
    fits = []
    for endpoint, neutral in NEUTRALS.items():
        rows = [r for r in colours if r['endpoint'] == endpoint]
        x, y, bar = arrays(rows)
        for family in ['E3', 'EH6', 'O12']:
            print(stamp(), endpoint, family, 'start', flush=True)
            fit = dict(endpoint=endpoint, family=family, neutralOrdinatesCodes=neutral,
                       fitCells=[r['cell'] for r in rows], fitRole='calibration')
            if family != 'O12':
                fit['survival'] = body.survival_linear(family, x, neutral, y, bar)
                fit['globalMinimax'] = body.solve_linear(family, x, neutral, y)
                save(args.out / f'{endpoint}-{family}-lp.json', fit)
                fit['certificateReplay'] = verify_linear(family, x, neutral, y, bar,
                                                        fit['survival'], fit['globalMinimax'])
                if 'coefficients' in fit['globalMinimax']:
                    fit['globalMinimax'].update(rank(family, x, neutral, y,
                                                     fit['globalMinimax']['coefficients']))
            fit['local'] = body.fit_local(family, x, neutral, y)
            save(args.out / f'{endpoint}-{family}-fit.json', fit)
            fits.append(fit)
            print(stamp(), endpoint, family, 'done',
                  [(k, (v or {}).get('maximumCodes')) for k, v in fit['local'].items()
                   if k in ('leastSquares', 'minimax')], flush=True)
    frozen_at = stamp()
    save(args.out / 'fit-freeze.json', dict(frozenAt=frozen_at,
         meaning='Numerical calibration fits frozen before validation-only Reader; NOT exposure freeze',
         files={p.name: digest(p) for p in sorted(args.out.glob('*-fit.json'))}))
    # The role boundary is temporal as well as explicit: no validation payload
    # is opened until every coefficient and optimizer attempt is on disk.
    validation = collect(args.archive, 'validation')
    save(args.out / 'validation.json.gz', dict(readAfterFitFreeze=frozen_at, rows=validation))
    scores = []
    for fit in fits:
        candidates = {'leastSquares': fit['local']['leastSquares']}
        if fit['family'] == 'O12':
            candidates['localMinimax'] = fit['local']['minimax']
        else:
            candidates['globalMinimax'] = fit['globalMinimax']
            if fit['survival']['status'] == 'forward-feasible':
                candidates['survivalWitness'] = fit['survival']
        for method, candidate in candidates.items():
            if candidate is not None and 'coefficients' in candidate:
                scores.extend(scored(fit, method, candidate, calibration + validation))
    save(args.out / 'scores.json.gz', scores)
    summary = summarize(scores)
    verdicts = []
    for fit in fits:
        rows = [r for r in summary if r['family'] == fit['family'] and r['endpoint'] == fit['endpoint']]
        surviving_methods = [method for method in sorted({r['method'] for r in rows})
                             if not any(r['failedCells'] for r in rows if r['method'] == method)]
        verdicts.append(dict(family=fit['family'], endpoint=fit['endpoint'],
             certifiedCalibrationSurvival=fit.get('survival', {}).get('status', 'LOCAL only'),
             survivingMethods=surviving_methods,
             verdict='SURVIVES' if surviving_methods else ('certified calibration rejection' if
                 fit.get('survival', {}).get('status') == 'certified-infeasible' else 'LOCAL candidate failure')))
    historical = G2 / 'body-correction/correction-attempt-1.json.gz'
    old = json.loads(gzip.decompress(historical.read_bytes()))
    b0 = [r for r in old['fits'] if r['family'] == 'H3']
    save(args.out / 'b0-recorded-brackets.json', dict(source=str(historical.relative_to(RESULTS)),
         sha256=digest(historical), refitted=False, w41Certification=False,
         population='W39 whole-cell censor: 404/408 cells, 1212 uncensored channels', fits=b0))
    save(args.out / 'summary.json', dict(completedAt=stamp(), strata=summary, verdicts=verdicts,
         resolutionRule='Among survivors, separation below max(3 codes,sum of bars) at every admitted discriminator means insufficient resolution; no tolerance widens.',
         resolutionVerdict='No pair of surviving body families' if not any(v['survivingMethods'] for v in verdicts)
                           else 'Surviving endpoint candidates require the declared discriminator comparison',
         populationDeficientCells=0, holdoutOpened=False))
    save(args.out / 'manifest.json', {p.name: digest(p) for p in sorted(args.out.iterdir()) if p.is_file()})
    print('COMPLETE', args.out, flush=True)


if __name__ == '__main__':
    main()
