"""Authorized W41 step4 only. Outputs are additive and no path is canonical.

Use a fresh attempt directory beneath stroke/. The CLI requires an explicit
steps2/3 completion signal; it is not preparation's default command. Every
native payload is admitted by the recorded fetched-cache Reader. The sealed
optimizer remains the only fitting implementation and runs at its full budgets.
"""
import argparse
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
import replay as r
import scoring
import diagnostics


def json_write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def gzip_rows(path, produce):
    with Path(path).open('xb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as stream:
            def emit(row):
                stream.write((json.dumps(row, allow_nan=False, separators=(',', ':'))+'\n').encode())
            return produce(emit)


def select_prediction(result, objective):
    selected = result[objective]
    if selected is not None:
        return selected, 'selected local candidate'
    metric = 'weightedSquaredError' if objective == 'leastSquares' else 'maximumCodes'
    candidate = min((row[objective] for row in result['starts']), key=lambda v: v[metric])
    return candidate, 'unconverged forward diagnostic; no survival claim'


def coefficient_table(row, family, curvature, inactive_only):
    q = np.asarray(row['coefficients'])
    endpoints = (1, 3) if inactive_only else (1, 3, 0, 2)
    return dict(width=float(q[0]), rho=float(q[-1]) if curvature else None,
        endpoints={r.ENDPOINTS[e]: dict(beta=r.f.unpack(q, family, e)[1],
            gamma=r.f.unpack(q, family, e)[2], material=r.f.unpack(q, family, e)[3].tolist())
            for e in endpoints},
        omittedActiveCoordinates=inactive_only,
        gauge='max-normal convention; neither opacity nor physical width identification')


def sensitivity(observations, q, family, css, curvature, emit):
    """Freeze coefficients; evaluate the declared 32x32 grid, never fit it."""
    maxima = {}
    cache = {}
    for o in observations:
        prediction16 = r.compact_predict(q, o, family, css, curvature)
        prediction32 = []
        for part in o['parts']:
            shape, xy = part['shape'], part['xy']
            key = (shape, o['scale'], hashlib.sha256(xy.tobytes()).hexdigest(), o['endpoint'])
            if key not in cache:
                # Keep one geometry/endpoint rather than accumulating a second
                # full bed at four times the quadrature storage.
                cache.clear()
                g = r.m.samples(shape, xy, o['scale'], 32)
                material = r.shadow.materials()[r.ENDPOINTS[o['endpoint']]]
                fall = r.held_falloff(g, shape, material) if o['endpoint'] in (0, 2) \
                    else np.zeros_like(g['d'])
                cache[key] = (g, r.CoverageKernel(g, fall))
            g, kernel = cache[key]
            backdrop = r.m.bilinear(part['reference'], g['q'])
            compact = r.CompactComposite(g, backdrop, kernel.fall, kernel)
            prediction32.append(compact.predict(q, o['endpoint'], part['amplitude'],
                                                 family, css, curvature))
        difference = abs(np.concatenate(prediction32)-prediction16)
        for part in o['parts']:
            for bi, row in enumerate(part['bins']):
                if row['pixels'] < 4:
                    continue
                at = o['binids'] == part['offset']+bi
                mean = difference[at].mean(0)
                maximum = difference[at].max(0)
                key = f'{r.ENDPOINTS[o["endpoint"]]}/{o["role"]}/{o["scale"]}x'
                maxima[key] = max(maxima.get(key, 0.), float(maximum.max()))
                emit(dict(cell=o['cell'], role=o['role'], endpoint=r.ENDPOINTS[o['endpoint']],
                    scale=o['scale'], member=part['member'], part=row['part'],
                    side=row['side'], shell=row['shell'], bin=row['bin'],
                    pixels=row['pixels'], meanAbsoluteDifferenceRGB=mean.tolist(),
                    maximumPixelDifferenceRGB=maximum.tolist(), coefficientsFixed=True))
    return dict(maximumPixelDifferenceCodesByStratum=maxima, fittedQuadrature=16,
                diagnosticQuadrature=32, coefficientsChanged=False)


def run(args):
    r.verify_seal()
    output = Path(args.out).resolve()
    if r.HERE not in output.parents:
        raise ValueError('outputs must stay beneath this stroke evidence directory')
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    json_write(output/'execution.json', dict(startedUTC=started, signal=args.fit_start_signal,
        family=args.family, geometry=args.geometry, mode=args.mode,
        declarationSha256=r.DECLARATION_SHA,
        sourceFiles={str(p.relative_to(r.m.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in [Path(__file__), Path(r.__file__), Path(scoring.__file__),
                               Path(r.f.__file__), Path(r.m.__file__), Path(r.shadow.__file__),
                               Path(diagnostics.__file__)]},
        classification='LOCAL; unchanged sealed domains, starts and budgets',
        roles=['calibration', 'validation'], holdout=False, browser=False, nativeCapture=False))
    preparation = r.Preparation()
    admission = []
    calibration = r.load_role(preparation, 'calibration', admission.append)
    json_write(output/'calibration-admission.json', admission)
    inactive_only = args.mode == 'inactive-diagnostic'
    fit_cells = [o for o in calibration if not inactive_only or o['endpoint'] in (1, 3)]
    print(json.dumps(dict(event='prepared', cells=len(calibration), fitCells=len(fit_cells),
        pixels=sum(len(o['target']) for o in fit_cells),
        peakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)), flush=True)
    css, curvature = args.geometry == 'css', args.geometry == 'curvature'
    t = time.perf_counter()
    result = r.fit_observations(fit_cells, args.family, css, curvature)
    result['fitSeconds'] = time.perf_counter()-t
    result['mode'] = args.mode
    result['survivalAuthority'] = not inactive_only
    json_write(output/'optimizer.json', result)
    # No validation statistic has contributed to fitting. Read-only transfer
    # follows the completed calibration optimization and cannot change q.
    admission = []
    validation = r.load_role(preparation, 'validation', admission.append)
    json_write(output/'validation-admission.json', admission)
    observations = calibration+validation
    if inactive_only:
        observations = [o for o in observations if o['endpoint'] in (1, 3)]
    controls = scoring.inactive_zero_controls(calibration+validation)
    if not inactive_only:
        def held_controls(emit):
            rows = list(scoring.shadow_control_rows(observations, controls))
            for row in rows:
                emit(row)
            return scoring.summarize(rows)
        control_summary = gzip_rows(output/'held-shadow-controls.jsonl.gz', held_controls)
        json_write(output/'held-shadow-controls-summary.json', control_summary)
    results = {}
    for objective in ('leastSquares', 'minimax'):
        row, status = select_prediction(result, objective)
        q = np.asarray(row['coefficients'])
        candidate = dict(status=status, objective=objective,
                         coefficients=coefficient_table(row, args.family, curvature, inactive_only),
                         optimizerConverged=row['converged'], rank=row['rank'],
                         singularValues=row['singularValues'], railDeficitCodes=row['railDeficitCodes'])
        candidate['scoring'] = gzip_rows(output/f'{objective}-bins.jsonl.gz', lambda emit:
            scoring.score_candidate(observations, q, args.family, css, curvature, controls, emit))
        candidate['survives'] = not inactive_only and result[objective] is not None \
            and candidate['scoring']['survives']
        candidate['quadratureSensitivity'] = gzip_rows(output/f'{objective}-quadrature.jsonl.gz',
            lambda emit: sensitivity(observations, q, args.family, css, curvature, emit))
        candidate['straddlingDiagnostic'] = gzip_rows(output/f'{objective}-straddling.jsonl.gz',
            lambda emit: diagnostics.straddling(observations, q, args.family, css, curvature, emit))
        json_write(output/f'{objective}-summary.json', candidate)
        results[objective] = candidate
    json_write(output/'witnesses.json', [dict(cell=o['cell'], role=o['role'],
        endpoint=r.ENDPOINTS[o['endpoint']], scale=o['scale'], stateMembership=o['stateMembership'],
        members=[dict(member=p['member'], interior=p['interior'], boundary=p['boundary'])
                 for p in o['parts']]) for o in observations])
    json_write(output/'complete.json', dict(completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        fitSeconds=result['fitSeconds'], peakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        nativeHoldoutRead=False, survivalAuthority=not inactive_only,
        objectiveSurvival={k: v['survives'] for k, v in results.items()}))
    print(json.dumps(dict(event='complete', path=str(output))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fit-start-signal', required=True, choices=['steps-2-3-complete'])
    parser.add_argument('--family', required=True, choices=['M0', 'M1', 'M2'])
    parser.add_argument('--geometry', required=True, choices=['device', 'css', 'curvature'])
    parser.add_argument('--mode', required=True, choices=['joint', 'inactive-diagnostic'])
    parser.add_argument('--out', required=True)
    run(parser.parse_args())
