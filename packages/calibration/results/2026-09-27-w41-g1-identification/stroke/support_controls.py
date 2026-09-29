"""Coefficient-independent required bins beyond every declared stroke support.

The maximum is2 CSSpx at2x (4devicepx), not2devicepx. A bin is admitted only
when EVERY sealed quadrature sample is beyond that bound. No optimizer is run.
"""
import argparse
import copy
import datetime
import json
from pathlib import Path
import numpy as np
import execute
import replay as r
import scoring


def outside_every_rival(g, selected):
    return bool(np.any(selected) and np.all(g['d'][selected] >= 2*g['scale']))


def controls(observations, emit):
    materials = r.shadow.materials()
    rows = []
    union_checks = []
    for o in observations:
        shapes = [p['shape'] for p in o['parts']]
        for part in o['parts']:
            compact = part['compact']
            g = compact.kernel.g
            baseline = compact.mean_b-part['amplitude']*compact.mean_bfall
            # A column is not silently collapsed to one member. Check the held
            # shifted UNION at every sample. Equal span44 columns share the same
            # held falloff/amplitude law; nearest contour is its maximum alpha.
            difference = 0.
            if len(shapes) > 1:
                mat = materials[r.ENDPOINTS[o['endpoint']]]
                alphas = [r.shadow.at(g['q'], shape, o['scale'], mat, o['groupLuminance'])
                          for shape in shapes]
                union = np.maximum.reduce(alphas)
                member = part['amplitude']*compact.kernel.fall
                difference = float(abs(union-member).max())
                union_checks.append(dict(cell=o['cell'], member=part['member'],
                    maximumSubpixelAlphaDifference=difference,
                    nearestMemberEqualsFullHeldUnion=bool(np.array_equal(union, member))))
                if difference > 1e-15:
                    raise ValueError('column member shadow differs from complete shifted union')
            for bi, binrow in enumerate(part['bins']):
                if binrow['pixels'] < 4:
                    continue
                local = part['binids'] == part['offset']+bi
                if not outside_every_rival(g, local):
                    continue
                indices = np.flatnonzero(local)+part['pixelOffset']
                prediction = baseline[local]
                runs = o['runs'][:, indices]
                score = r.m.score_bin(prediction, runs)
                # Expose the hard-bound deficit beside measured MAE, never turn
                # white native255 into a spurious measured zero-error reference.
                deficits = []
                for native in [np.median(runs, axis=0), *runs]:
                    low, high = native <= 5, native >= 250
                    deficit = np.where(low, np.maximum(prediction-5, 0),
                              np.where(high, np.maximum(250-prediction, 0), 0))
                    deficits.append(deficit.max(0).tolist())
                row = dict(cell=o['cell'], role=o['role'], endpoint=r.ENDPOINTS[o['endpoint']],
                    scale=o['scale'], member=part['member'], part=binrow['part'],
                    side=binrow['side'], shell=binrow['shell'], bin=binrow['bin'],
                    score=score, shadowControl=True,
                    minimumDeviceDistance=float(g['d'][local].min()),
                    maximalDeclaredDeviceReach=2*o['scale'], allSubpixelsBeyondEveryRival=True,
                    maximumHeldUnionAlphaDifference=difference,
                    railDeficitRGBMedianThenSevenRuns=deficits,
                    nativeMeanRGBMedianThenSevenRuns=[v.mean(0).tolist() for v in
                        [np.median(runs, axis=0), *runs]],
                    predictionMeanRGB=prediction.mean(0).tolist(),
                    predictionMinimumRGB=prediction.min(0).tolist(),
                    classification='coefficient-independent held-shadow control; no fit')
                emit(row); rows.append(row)
    groups = {}
    for endpoint in (1, 3, 0, 2):
        for scale in (1, 2):
            selected = [row for row in rows if row['endpoint'] == r.ENDPOINTS[endpoint]
                        and row['scale'] == scale]
            groups[f'{r.ENDPOINTS[endpoint]}/{scale}x'] = scoring.summarize(selected)
    return dict(strata=groups, overall=scoring.summarize(rows), columnUnionChecks=union_checks,
                nativeFits=0, support='each admitted bin: min(all pixel subpixel distances)>=2*scale',
                conclusion='Any binding row is independent of all declared stroke coefficients; '
                    'this does not stand in for the declared optimizer outcomes.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    if r.HERE not in out.parents:
        raise ValueError('outputs stay beneath stroke/')
    out.mkdir(exist_ok=False)
    prep = r.Preparation()
    observations = r.load_role(prep, 'calibration')
    result = execute.gzip_rows(out/'bins.jsonl.gz', lambda emit: controls(observations, emit))
    execute.json_write(out/'summary.json', result)
    print(json.dumps(result, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
