"""Saved-evidence, exact matched-input necessary cut; never an optimizer result.

For a common per-pixel prediction z, MAE(z,R)+MAE(z,G) >= mean(abs(R-G)).
The weaker Jensen bound is abs(mean(R)-mean(G)). Equal geometry, reference
channel and inactive shadow make M1's prediction common for EVERY allowed
coefficient vector. This is a relaxation even allowing arbitrary z per pixel.
M2's contextual correction is deliberately outside this equality.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE/'sources'
RESULTS = SOURCE/'packages/calibration/results'
DECLARATION = RESULTS/'2026-09-27-w41-g0-declaration'
DECLARATION_SHA = '850747c1f03781a6efe9b433bd4ce3bd6cf72b63c9befd8d5d98de9eadf7f759'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def array_record(value):
    value = np.ascontiguousarray(value)
    return dict(shape=list(value.shape), dtype=value.dtype.str, sha256=sha(value.tobytes()))


def deny_external_pixels():
    # Replay must work without either original archive or raw tree. The captured
    # bundles retain their historical path strings; those paths are never opened.
    forbidden = [Path.home()/'vitrea-w39', Path.home()/'.cache/vitrea-archives']
    def audit(event, values):
        if event == 'open' and isinstance(values[0], (str, bytes)):
            p = Path(values[0].decode() if isinstance(values[0], bytes) else values[0]).resolve()
            if any(p == root or root in p.parents for root in forbidden):
                raise PermissionError('certificate replay permits saved input bundles only')
    sys.addaudithook(audit)


def load_law():
    manifest = json.loads((HERE/'sources.json').read_text())
    assert manifest['revision'] == 'd35b4cbf43f1fcdda55063b3b8e0fa178d720a78'
    for row in manifest['files']:
        assert sha((SOURCE/row['path']).read_bytes()) == row['sha256'], row['path']
    assert sha((DECLARATION/'bounds-declaration.txt').read_bytes()) == DECLARATION_SHA
    sys.path.insert(0, str(DECLARATION/'instrument'))
    import instrument
    import shadow
    sys.path.insert(0, str(instrument.G0))
    import w39_archive
    # Invoke the original provenance-enforcing loader, not a replacement lookup.
    materials = shadow.materials()
    return instrument, shadow, w39_archive, materials


def exact_mean(values):
    vals = np.asarray(values).ravel()
    assert np.all(vals == vals.astype(np.int64))
    return Fraction(sum(int(v) for v in vals), len(vals))


def exact_witness(left, right):
    """Seven repeats, one uncensored channel; population and bars are unchanged."""
    left, right = np.asarray(left), np.asarray(right)
    assert left.shape == right.shape and left.ndim == 2 and left.shape[0] == 7
    assert left.shape[1] >= 4
    assert np.all((left > 5) & (left < 250))
    assert np.all((right > 5) & (right < 250))
    means = [[exact_mean(row) for row in v] for v in (left, right)]
    bars = [Fraction(1, 2)+(max(v)-min(v))/2 for v in means]
    bounds = [max(Fraction(1), b) for b in bars]
    target_left = [np.median(left, axis=0), *left]
    target_right = [np.median(right, axis=0), *right]
    rows = []
    for i, (a, b) in enumerate(zip(target_left, target_right)):
        gap = abs(exact_mean(a)-exact_mean(b))
        paired = exact_mean(abs(a.astype(np.int64)-b.astype(np.int64)))
        rows.append(dict(state='pixelwise-median' if i == 0 else f'repeat-{i}',
            leftMean=str(exact_mean(a)), rightMean=str(exact_mean(b)),
            absoluteMeanDifference=str(gap), meanAbsolutePairedDifference=str(paired),
            sumAllowedMAE=str(sum(bounds)), jensenExcess=str(gap-sum(bounds)),
            pairwiseTriangleExcess=str(paired-sum(bounds)),
            necessaryWorstMAELowerBound=str(paired/2),
            rejects=bool(paired > sum(bounds))))
    return dict(bar=[str(b) for b in bars], allowedMAE=[str(b) for b in bounds],
                allSevenAndMedianReject=all(r['rejects'] for r in rows),
                rejects=any(r['rejects'] for r in rows), states=rows)


def assert_equal_inputs(a, b):
    assert a['component'] == b['component'], 'supplied shape/path/position'
    assert a['scale'] == b['scale'], 'scale'
    assert a['bin'] == b['bin'], 'required bin and population'
    assert a['g']['radiusCSS'] == b['g']['radiusCSS'], 'nominal radius'
    for key in ('xy', 'channel', 'shadow'):
        assert np.array_equal(a[key], b[key]), key
    for key in ('q', 'd', 'nx', 'ny', 'arc'):
        assert np.array_equal(a['g'][key], b['g'][key]), key
    assert np.array_equal(a['g']['nx']**2, b['g']['nx']**2), 'nx squared'
    assert np.all(a['shadow'] == 0) and np.all(b['shadow'] == 0), 'inactive shadow'
    assert np.all(a['channel'] == a['channel'][0, 0]), 'uniform channel reference'


def extract(row, m, shadow, archive, materials, arrays):
    raw = (HERE/'inputs'/row['file']).read_bytes()
    assert sha(raw) == row['sha256'] and row['role'] == 'calibration'
    runs, states = archive.unbundle(raw)
    runs = [r for r in runs if r['admitted'] and r['protocol'] == 'normal']
    assert len(runs) == 7 and len({r['run'] for r in runs}) == 7
    payloads = [archive.unpack(states[r['state']]) for r in runs]
    p = payloads[0]
    assert all(v['pose'] == 'inactive' and v['scheme'] == row['scheme']
               and v['scale'] == row['scale'] and v['component'] == p['component']
               and v['profile']+'/'+v['sceneId'] == row['cell'] for v in payloads)
    assert all(v['rgb'].shape == p['rgb'].shape for v in payloads)
    # Retain each repeat's references, not a presumed shared dependency.
    assert all(np.array_equal(v['noGlass'], p['noGlass']) for v in payloads)
    assert np.all(p['noGlass'] == p['noGlass'][0, 0]), 'whole-frame uniform reference'
    shapes = m.readers.shapes_of(p['component'])
    assert len(shapes) == 1
    shape = shapes[0]
    geo = m.readers.geometry(p['rgb'].shape[:2], shapes, row['scale'])
    bins, labels = m.readers.edge_bins(geo, inner_css=0, outer_css=4)
    index = next(i for i, b in enumerate(bins) if b['shell'] == 0
                 and b['part'] == 'straight' and b['side'] == 'top')
    binrow = bins[index]
    yy, xx = np.nonzero(labels == index)
    xy = np.c_[xx, yy]
    assert len(xy) == binrow['pixels'] >= 4 and binrow['admissible']
    native = np.array([v['rgb'][yy, xx] for v in payloads])
    references = np.array([v['noGlass'][yy, xx] for v in payloads])
    prefix = f"{row['scheme']}_{row['scale']}x_{row['colour']}"
    arrays[prefix+'_xy'] = xy
    arrays[prefix+'_nativeRGBSevenRuns'] = native
    arrays[prefix+'_referenceRGBSevenRuns'] = references
    variants = {}
    material = materials[row['scheme']+'-inactive']
    luminance = float(m.body.decode(p['noGlass'].mean((0, 1))/255) @ m.body.W)
    for order in (16, 32):
        g = m.samples(shape, xy, row['scale'], order=order)
        b = m.bilinear(p['noGlass'], g['q'])
        alpha = shadow.at(g['q'], shape, row['scale'], material, luminance)
        assert np.all(alpha == 0), 'unchanged loader and shadow law must give exact zero'
        for key in ('q', 'd', 'nx', 'ny', 'arc'):
            arrays[f'{prefix}_{order}_{key}'] = g[key]
        arrays[f'{prefix}_{order}_nxSquared'] = g['nx']**2
        arrays[f'{prefix}_{order}_referenceRGBSubpixels'] = b
        arrays[f'{prefix}_{order}_shadowAlpha'] = alpha
        variants[order] = dict(component=p['component'], scale=row['scale'], bin=binrow,
            xy=xy, g=g, b=b, channel=b[..., 2], shadow=alpha)
    # score_bin's bar and censor status are checked against the exact arithmetic.
    # This arbitrary prediction is not a fitted candidate or a closure claim.
    score = m.score_bin(np.full((len(xy), 3), 17.5), native)
    detail = dict(**row, component=p['component'], bin=binrow,
        frameShape=list(p['rgb'].shape), runIds=[r['run'] for r in runs],
        stateMembership=[r['state'] for r in runs], uniqueStates=len(states),
        wholeFrameReferenceRGB=p['noGlass'][0, 0].tolist(),
        nativeMeanRGBSevenRuns=native.mean(1).tolist(),
        scoreBinAtArbitraryCommon17point5=score,
        inactiveGamma=0, shadowAlphaExactlyZeroBothOrders=True,
        allSevenReferencesExactlyEqual=True, allSevenSuppliedComponentsExactlyEqual=True)
    return dict(variants=variants, native=native, detail=detail)


def forward_checks(m, left, right, dark):
    """Finite implementation checks beside (not in place of) the symbolic identity."""
    rng = np.random.default_rng(4100)
    cases = [(0., 0., False, None), (.5, .4, False, None), (1., 0., False, None),
             (2., 1., False, None), (2., .3, True, None),
             (1., .5, False, -22.), (1., .5, False, 22.), (2., 1., True, 22.)]
    max_difference = 0.
    for width, beta, css, rho in cases:
        q = np.sort(rng.uniform(0, 255, 8))
        preds = [m.composite(v['g'], v['b'], v['b'], width, beta, 0,
                            'M1', q, dark, css, rho) for v in (left, right)]
        difference = float(abs(preds[0][:, 2]-preds[1][:, 2]).max())
        assert difference == 0
        max_difference = max(max_difference, difference)
    # Same *frozen* coefficients at 16/32; never a new fit at the higher order.
    fixed = .8*m.NODES
    contextual = None
    if dark:
        q = np.r_[fixed, .01, 0.]
        preds = [m.composite(v['g'], v['b'], v['b'], 1., 0., 0., 'M2', q, True)
                 for v in (left, right)]
        contextual = float(abs(preds[0][:, 2]-preds[1][:, 2]).max())
        assert contextual > 0
    return dict(cases=len(cases), maximumM1ChannelDifference=max_difference,
                M2NonFitContextualCounterexampleDifference=contextual)


def evaluate():
    deny_external_pixels()
    m, shadow, archive, materials = load_law()
    manifest = json.loads((HERE/'inputs/manifest.json').read_text())
    assert manifest['roles'] == ['calibration'] and len(manifest['cells']) == 8
    arrays = {}
    observations = {}
    for row in manifest['cells']:
        key = row['scheme'], row['scale'], row['colour']
        assert key not in observations
        observations[key] = extract(row, m, shadow, archive, materials, arrays)
    pairs = []
    for scheme in ('light', 'dark'):
        for scale in (1, 2):
            left, right = [observations[scheme, scale, c] for c in ('red', 'green')]
            assert left['detail']['runIds'] == right['detail']['runIds'], 'paired repeat identities'
            checks = []
            for order in (16, 32):
                a, b = left['variants'][order], right['variants'][order]
                assert_equal_inputs(a, b)
                checks.append(dict(order=order, **forward_checks(m, a, b, scheme == 'dark')))
            witness = exact_witness(left['native'][..., 2], right['native'][..., 2])
            for v, bar in zip((left, right), witness['bar']):
                assert v['detail']['scoreBinAtArbitraryCommon17point5']['barRGB'][2] == float(Fraction(bar))
                assert all(s['railPixels'][2] == 0 for s in
                    [v['detail']['scoreBinAtArbitraryCommon17point5']['median'],
                     *v['detail']['scoreBinAtArbitraryCommon17point5']['runs']])
            pairs.append(dict(endpoint=scheme+'-inactive', scale=scale, channel='B',
                inputCode=32, pixels=left['detail']['bin']['pixels'],
                identicalFullSubpixelGeometryAndReference=True, exact=witness,
                unchangedForwardChecks=checks))
    result = dict(schema='w41-m1-matched-channel-necessary-certificate-1',
        declarationSha256=DECLARATION_SHA, sourceManifestSha256=sha((HERE/'sources.json').read_bytes()),
        inputManifestSha256=sha((HERE/'inputs/manifest.json').read_bytes()),
        nativeRoles=['calibration'], cellsRead=8, fitsRun=0, existingFitsStopped=False,
        theorem='For each paired pixel M1 predicts the same B channel for all bounded ordinates, '
            'width, beta and rho: identical q,d,nx squared,arc,scale,radius; gamma=0; shadow=reference; '
            'identical uniform local B=32. Arbitrary common per-pixel predictions relax every '
            'declared geometry rival. Triangle gives MAE_left+MAE_right >= mean(abs(native_left-native_right)); '
            'Jensen also gives >= abs(mean(native_left)-mean(native_right)). Exact rational bars and '
            'fully uncensored populations below prove infeasibility when either bound exceeds their sum.',
        scope=['M1/device-width/dark-inactive', 'M1/CSS-width/dark-inactive',
               'M1/nominal-curvature/dark-inactive'],
        endpoints={scheme+'-inactive': 'rejected-by-necessary-cut' if any(
            p['exact']['rejects'] for p in pairs if p['endpoint'] == scheme+'-inactive')
            else 'not-rejected-by-this-pair; no survival claim' for scheme in ('light', 'dark')},
        exclusions=['M2 contextual correction depends on full RGB luminance and gamut; equality does not apply.',
                    'Active endpoints were not read; no extrapolation from inactive.',
                    'No claim about remaining light M1 bins or whole-endpoint survival.',
                    'No optimizer output, candidate fit, validation transfer or holdout result.'],
        sensitivity='Both 16x16 and fixed-coefficient 32x32 preserve exact paired-channel identity.',
        pairs=pairs, cells=[v['detail'] for v in observations.values()],
        arrays={k:array_record(v) for k, v in sorted(arrays.items())})
    return result, arrays


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='recompute without writing any evidence')
    args = parser.parse_args()
    result, arrays = evaluate()
    out = HERE/'proof'
    if args.check:
        assert json.loads((out/'certificate.json').read_text()) == result
        with np.load(out/'paired-pixels-and-subpixels.npz', allow_pickle=False) as saved:
            assert set(saved.files) == set(arrays)
            for key, value in arrays.items():
                assert np.array_equal(saved[key], value), key
        print('SAVED-EVIDENCE REPLAY PASS; raw tree and fetched archive denied')
    else:
        out.mkdir(exist_ok=False)
        (out/'certificate.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
        np.savez_compressed(out/'paired-pixels-and-subpixels.npz', **arrays)
    print(json.dumps(dict(endpoints=result['endpoints'], pairs=[dict(endpoint=p['endpoint'],
        scale=p['scale'], pixels=p['pixels'], exact=p['exact']) for p in result['pairs']]), indent=2))


if __name__ == '__main__':
    main()
