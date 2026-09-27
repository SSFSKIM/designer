"""Replay the numerical correction from guarded-derived body data, never pixels.

H3/H3prime use only the body artifact. H2prime additionally uses the committed
resolved shipped materials (its fixed family structure) and their provenance
sidecar. No native module, archive, capture, matrix, profile or holdout reader
is imported. Outputs use exclusive creation; --verify writes nothing.

Usage: python replay.py --out correction.json.gz --provenance-sha <sidecar SHA>
       python replay.py --verify correction.json.gz
"""
import argparse
from collections import defaultdict
import copy
import gzip
import hashlib
import json
from pathlib import Path
import platform
import re
import sys
sys.dont_write_bytecode = True
import numpy as np
import scipy
from solver import solve_h3
from multistart import diagnostics, fit_multistart
import body

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
PINS = {
    'body/identification-attempt-1.json.gz': '3da0925a97dfb8dd7db0fa3e109931292ecdefc13c1ad527f226dbe01589029e',
    'instrument/resolved-materials.json': '214eb600c5fe88f8690efc742b729587c93dae3b8837e993df69bfea03447d73',
    'instrument/body.py': '6b15fea4459402dbc5affc0642767c93abb2ced4b69cfea6683048688c45c842',
}
VERSIONS = dict(python='3.12.3', implementation='CPython', numpy='2.5.3', scipy='1.18.1')
PROJECTION = ('e = signed predicted-minus-native encoded RGB codes. Y = W dot e; '
    'parallel = W*(W dot e)/(W dot W); perpendicular = e-parallel. This is an '
    'encoded-space diagnostic, not physical linear-light luminance; means are '
    'over both C levels and both scales, with equal cell mass.')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked_inputs(provenance_sha):
    actual = dict(python=platform.python_version(), implementation=platform.python_implementation(),
                  numpy=np.__version__, scipy=scipy.__version__)
    if actual != VERSIONS:
        raise RuntimeError(f'Numerical runtime mismatch: expected {VERSIONS}, got {actual}')
    pins = {**PINS, 'instrument/resolved-materials.provenance.json': provenance_sha}
    loaded = {}
    for name, digest in pins.items():
        payload = (BASE / name).read_bytes()
        if sha(payload) != digest:
            raise RuntimeError(f'Input hash mismatch: {name}')
        loaded[name] = payload
    data = json.loads(gzip.decompress(loaded['body/identification-attempt-1.json.gz']))
    materials = json.loads(loaded['instrument/resolved-materials.json'])
    if any(r['role'] not in ('calibration', 'validation') for r in data['rows']):
        raise RuntimeError('Body artifact contains a role outside this correction')
    return data, materials, pins


def starts_for(family, old, material):
    starts = [np.array(old[m]['coefficients']) for m in ('leastSquares', 'minimax')]
    if family == 'H3prime':
        starts += [np.array([s, 0., 0., s]) for s in (.25, .5, .75, 1., 1.25, 1.5, 2.)]
        rng = np.random.default_rng(3902)
        starts += [np.array([1., 0., 0., 1.]) + rng.normal(0, .25, 4) for _ in range(5)]
    else:
        thin = np.array(material['backdropToneResponseThin'])
        starts.append(np.r_[material['bodyChromaRetention'], thin])
        # 12 prescribed endpoint/retention starts plus the two recorded candidates
        # and the shipped point. Sorting respects the declared thin-row constraint.
        for r in (0., .5, 1.):
            for row in (thin, np.array([.01, .1, .4, .8]),
                        np.array([.1, .3, .6, .9]), np.array([0., .05, .2, .5])):
                starts.append(np.r_[r, np.sort(row)])
    return starts


def score(row, endpoint, family, method, fit, pred):
    deep = row['members'][0]
    obs = np.array(deep['medianRGB']); tau = np.maximum(1, deep['barRGB'])
    def residual(values):
        values = np.asarray(values)
        return np.where(values >= 250, np.maximum(250-pred, 0),
                        np.where(values <= 5, np.maximum(pred-5, 0), abs(pred-values)))
    err = residual(obs); perrun = residual(deep['runMediansRGB'])
    return dict(cell=row['cell'], endpoint=endpoint, scale=row['scale'], role=row['role'],
        population=row['population'], family=family, method=method, converged=fit['converged'],
        predictedRGB=pred.tolist(), nativeRGB=obs.tolist(), residualRGB=err.tolist(),
        absoluteDiagnosticRGB=abs(pred-obs).tolist(), toleranceRGB=tau.tolist(),
        censoredChannels=deep['censoredChannels'],
        censorRule='one-sided threshold bound; entire cell excluded from RGB inversion; censored required cell is UNMEASURED',
        failedChannels=np.flatnonzero(err > tau+1e-8).tolist(), repeatResidualRGB=perrun.tolist(),
        repeatFailedChannels=[np.flatnonzero(e > tau+1e-8).tolist() for e in perrun])


def summarize(scores):
    groups = defaultdict(list)
    for row in scores:
        key = tuple(row[k] for k in ('family', 'endpoint', 'scale', 'method', 'population'))
        groups[key].append(row)
    summary = []
    for key, rows in groups.items():
        worst = max(rows, key=lambda r: max(r['residualRGB']))
        allchannel = max(rows, key=lambda r: min(r['residualRGB']))
        mean = max(rows, key=lambda r: np.mean(r['residualRGB']))
        failed = [r for r in rows if r['failedChannels'] or any(r['repeatFailedChannels'])]
        censored = [r for r in rows if r['censoredChannels']]
        status = ('failed' if failed or not all(r['converged'] for r in rows) else
                  'UNMEASURED' if censored else 'survived')
        summary.append(dict(zip(('family', 'endpoint', 'scale', 'method', 'population'), key),
            cells=len(rows), failedCells=len(failed),
            failedChannels=sum(len(r['failedChannels']) for r in rows),
            allChannelFailedCells=sum(len(r['failedChannels']) == 3 for r in rows),
            censoredCells=len(censored), status=status, worstCell=worst['cell'],
            worstRole=worst['role'], worstChannel=int(np.argmax(worst['residualRGB'])),
            maximumCodes=max(worst['residualRGB']),
            allChannelsMaximumMinimum=dict(cell=allchannel['cell'], residualRGB=allchannel['residualRGB'],
                                           minimumChannelCodes=min(allchannel['residualRGB'])),
            maximumRGBMean=dict(cell=mean['cell'], meanCodes=float(np.mean(mean['residualRGB'])),
                                residualRGB=mean['residualRGB']),
            repeatVsMedianMaximumDifference=max(float(np.max(abs(np.array(r['repeatResidualRGB']) -
                                                  r['residualRGB']))) for r in rows)))
    return summary


def projections(scores):
    groups = defaultdict(list)
    for row in scores:
        match = re.search(r'/factor-y(\d+)-c\d+-h(\d+)-colour', row['cell'])
        if match:
            key = (row['family'], row['endpoint'], row['method'], int(match[1]), int(match[2]))
            groups[key].append(row)
    result = []
    for (family, endpoint, method, level, hue), rows in groups.items():
        e = np.mean([np.array(r['predictedRGB']) - r['nativeRGB'] for r in rows], axis=0)
        y = float(e @ body.W); parallel = body.W*y/(body.W @ body.W)
        result.append(dict(family=family, endpoint=endpoint, method=method,
            factorYLevel=[.05, .11, .18][level], hueDegrees=hue, cells=[r['cell'] for r in rows],
            signedMeanRGB=e.tolist(), encodedLumaProjection=y,
            parallelToLumaVectorRGB=parallel.tolist(), perpendicularToLumaVectorRGB=(e-parallel).tolist()))
    return result


def run(data, materials, pins):
    rows_by_cell = {r['cell']: r for r in data['rows']}
    fits = []; scores = copy.deepcopy(data['scores'])
    # Keep every recorded coefficient/LS score beside the correction. Only method
    # labels change in this new artifact so old SLSQP never masquerades as certified.
    for row in scores:
        if row['method'] == 'minimax' and row['family'] in ('H2prime', 'H3', 'H3prime'):
            row['method'] = 'legacyLocalMinimax'
    for old in data['fits']:
        family = old['family']; endpoint = old['endpoint']
        if family not in ('H3', 'H2prime', 'H3prime'):
            continue
        calibration = [rows_by_cell[c] for c in old['fitCells']]
        if any(r['role'] != 'calibration' or r['population'] != 'colour' or
               r['members'][0]['censoredChannels'] for r in calibration):
            raise RuntimeError('Recorded fit membership violated the declared restriction')
        x = np.array([r['inputCodes'] for r in calibration]) / 255
        target = np.array([r['members'][0]['medianRGB'] for r in calibration])
        neutral = np.array(old['neutralOrdinatesCodes']) / 255
        material = materials[endpoint]
        if family == 'H3':
            forward = lambda q: body.h3(x, neutral, q)
            fit = solve_h3(x, neutral, target)
            fit.update(diagnostics(forward, target / 255, np.array(fit['coefficients'])))
            method = 'globalMinimax'
        else:
            forward = ((lambda q: body.h2(x, material, q=q)) if family == 'H2prime' else
                       (lambda q: body.h3prime(x, neutral, q)))
            fit = fit_multistart(forward, target / 255, starts_for(family, old, material),
                                [(0, 1)]*5 if family == 'H2prime' else None,
                                monotone_start=1 if family == 'H2prime' else None)
            method = 'multistartMinimaxCandidate'
        fit.update(endpoint=endpoint, family=family, method=method, fitCells=old['fitCells'],
                   neutralOrdinatesCodes=old['neutralOrdinatesCodes'],
                   legacyLeastSquares=old['leastSquares'], legacyLocalMinimax=old['minimax'])
        fits.append(fit)
        print(endpoint, family, 'old', old['minimax']['maximum']*255,
              'corrected', fit['maximum']*255, fit.get('status', fit.get('classification')),
              file=sys.stderr, flush=True)
        q = np.array(fit['coefficients'])
        for row in data['rows']:
            ep = row['scheme'] + ('-active' if row['pose'] == 'rest' else '-inactive')
            if ep != endpoint:
                continue
            xx = np.array([row['inputCodes']]) / 255
            if family == 'H3':
                pred = body.h3(xx, neutral, q)[0]*255
            elif family == 'H3prime':
                pred = body.h3prime(xx, neutral, q)[0]*255
            else:
                pred = body.h2(xx, material, row['span'], q)[0]*255
            scores.append(score(row, endpoint, family, method, fit, pred))
    summary = summarize(scores)
    survivals = [r for r in summary if r['population'] == 'colour' and
                 r['method'] in ('globalMinimax', 'multistartMinimaxCandidate') and r['status'] == 'survived']
    if survivals:
        print('ATTENTION: candidate scale survival; check all strata before any exposure',
              json.dumps(survivals), file=sys.stderr, flush=True)
    source_code = {name: sha((HERE / name).read_bytes()) for name in ('replay.py', 'solver.py', 'multistart.py')}
    return dict(schema=1, correction='clipped nonlinear plateau is not a global minimax certificate',
        provenance=dict(inputs=pins, numericalRuntime=VERSIONS, implementationSha256=source_code,
                        originalInventorySha256=data['inventorySha256'], originalNeutralSha256=data['neutralSha256']),
        interpretation=dict(H3='global encoded minimax bracket; exact rational lower witness for floating-point LP',
            H2prime='best converged deterministic multistart candidate, not globally certified; failure is candidate failure',
            H3prime='best converged deterministic multistart candidate, not globally certified; failure is candidate failure',
            H4='not applicable: no surviving body law identified',
            holdout='not read; no exposure authorization follows from optimizer status',
            ties='H3 feasible coefficients need not be unique; no rank repair or fitted secondary objective',
            censoring='censored required cells cannot pass; one-sided errors retained; no bridge anchor removed'),
        fits=fits, originalFits=data['fits'], scores=scores, summary=summary,
        projectionDefinition=PROJECTION, diagnostic=projections(scores))


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def main():
    p = argparse.ArgumentParser(); group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--out', type=Path); group.add_argument('--verify', type=Path)
    p.add_argument('--provenance-sha'); args = p.parse_args()
    expected = None
    if args.verify:
        expected = json.loads(gzip.decompress(args.verify.read_bytes()))
        provenance_sha = expected['provenance']['inputs']['instrument/resolved-materials.provenance.json']
        for name, digest in expected['provenance']['implementationSha256'].items():
            if sha((HERE / name).read_bytes()) != digest:
                raise RuntimeError(f'Implementation hash mismatch: {name}')
    else:
        if args.out.exists():
            raise FileExistsError('Write-once output already exists')
        if not args.provenance_sha or not re.fullmatch('[0-9a-f]{64}', args.provenance_sha):
            p.error('--out requires --provenance-sha from the sealed sidecar')
        provenance_sha = args.provenance_sha
    data, materials, pins = checked_inputs(provenance_sha)
    result = run(data, materials, pins)
    payload = canonical(result)
    if expected is not None:
        if payload != canonical(expected):
            raise RuntimeError('Replayed correction differs from recorded artifact')
        print('Replay byte-equivalent canonical JSON:', sha(payload))
    else:
        with args.out.open('xb') as stream:
            stream.write(gzip.compress(payload, mtime=0))
        print('Wrote', args.out, 'canonical JSON SHA256', sha(payload))


if __name__ == '__main__':
    main()
