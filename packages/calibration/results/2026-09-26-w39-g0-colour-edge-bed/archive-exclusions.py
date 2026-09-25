#!/usr/bin/env python3.12
"""The archive already excludes H1 and the shipped H2 (charter v2 clause 3; c9a §5.184).

Reproduces memo A's deep-body tables (the colour grounding memo, 2026-09-26) for the
104 admitted W34 circular-120 solid cells, 88 calibration and 16 validation, through
W34's guarded `wave.Reader` at roles calibration and validation ONLY. The reader
refuses every holdout scene before any payload opens, and this script never names
W34's holdout directory, its sealed bulk files or a holdout-role cell: grey-208 is
identification holdout and stays UNREAD in all eight strata.

Statistic (the declaration's): per admitted normal run, the per-channel median at
signed d <= -6 CSS px (>= 4 pixels) over the archived native crop; the cell's value
is the median of the seven run medians; its bar is 0.5 + half the largest pairwise
separation of those run medians. The supplied-path geometry is read twice, once at
the archive's recorded alignment (as memo A and W35 read it) and once at the
attested origin alone (as W39's reader reads it); the two must agree to the code.

Evidence written: `archive-exclusions.json` (write-once). Validation readings are
labelled wherever they enter (grey-96 in the neutral interpolant; cyan).
"""
import base64
import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w39_readers as R

W35_LEVEL_TABLE = HERE.parent / '2026-09-24-w35-g0-edge-cut' / 'level-table.json'
MEMO_READINGS = Path.home() / 'vitrea-w39/grounding/colour/readings.json'  # scratch, outside the repository
W = np.array([.2126, .7152, .0722])
ROLES = ('calibration', 'validation')


def decode(v):
    v = np.asarray(v, float) / 255
    return np.where(v <= .04045, v / 12.92, ((v + .055) / 1.055) ** 2.4)


def encode(y):
    y = np.asarray(y, float)
    return 255 * np.where(y <= .0031308, 12.92 * y, 1.055 * np.maximum(y, 0) ** (1 / 2.4) - .055)


def censored(rgb): return [bool(v >= 250 or v <= 5) for v in rgb]


def stratum(cell):
    profile = cell.split('/')[0]
    return ('dark' if '-dark-' in profile else 'light', 'active' if cell.endswith('__rest') else 'inactive',
            '2x' if '-2x-' in profile else '1x')


def read_cell(wave, repeat, cell):
    crop = json.loads(gzip.decompress(repeat.read(cell, 'crop')))
    runs = [r for r in crop['runs'] if r['admitted'] and r['protocol'] == 'normal']
    medians, inputs, attested, spatial = [], [], [], []
    for run in runs:
        raw = base64.b64decode(crop['states'][run['state']])
        if hashlib.sha256(raw).hexdigest() != run['state']: raise ValueError('state hash mismatch')
        p = R.I.unpack(raw); scale = p['scale']
        shapes = R.shapes_of(p['component'])
        recorded = R.geometry(p['rgb'].shape[:2], shapes, scale, p['alignment']['translationDevicePx'])
        origin = R.geometry(p['rgb'].shape[:2], shapes, scale)
        deep = R.deep_body(p['rgb'], recorded); plain = R.deep_body(p['rgb'], origin)
        if deep['status'] != 'measured': raise ValueError('deep population below four')
        medians.append(deep['medianRGB']); attested.append(plain['medianRGB'])
        spatial.append([deep['minimumRGB'], deep['maximumRGB']])
        inputs.append(np.median(p['background'][recorded.d <= -R.DEEP_CSS * scale], 0).tolist())
    a = np.asarray(medians)
    return dict(runs=len(runs), runMedians=medians, output=np.median(a, 0).tolist(),
                bar=(np.ptp(a, 0) / 2 + .5).tolist(),
                attestedOriginOutput=np.median(np.asarray(attested), 0).tolist(),
                deepSpatialMinimum=np.min([s[0] for s in spatial], 0).tolist(),
                deepSpatialMaximum=np.max([s[1] for s in spatial], 0).tolist(),
                measuredInput=np.median(np.asarray(inputs), 0).tolist())


def main():
    # The reading is recorded under the declaration in force when it ran; the numbers do
    # not depend on its text, so --verify recomputes them and reports both digests.
    declaration = hashlib.sha256((HERE / 'bounds-declaration.txt').read_bytes()).hexdigest()
    out_path = HERE / 'archive-exclusions.json'
    if out_path.exists() and '--verify' not in sys.argv: raise FileExistsError('archive-exclusions.json is write-once')

    wave = R.w34_wave()
    repeat = wave.reader(R.W34_SITTING / 'repeat', roles=ROLES)
    selected = []
    for cell in sorted(wave.cells):
        sid = cell.split('/')[1]; scene = wave.scenes[sid]
        # Role first: nothing outside calibration/validation is even looked up further.
        if wave.roles[sid] not in ROLES: continue
        background = wave.spec['backgrounds'][scene['background']]
        if scene['component'] != 'circular-120' or background['kind'] != 'solid': continue
        selected.append((cell, scene['background'], background['srgb'], wave.roles[sid]))
    rows = []
    for cell, name, srgb, role in selected:
        r = read_cell(wave, repeat, cell)
        rows.append(dict(cell=cell, background=name, role=role, input=srgb, stratum=list(stratum(cell)),
                         outputCensored=censored(r['output']), **r))
    assert len(rows) == 104 and sum(r['role'] == 'calibration' for r in rows) == 88
    assert all(r['runs'] == 7 for r in rows) and all(max(r['bar']) == .5 for r in rows)
    assert all(r['attestedOriginOutput'] == r['output'] for r in rows)
    assert all(r['measuredInput'] == [float(v) for v in r['input']] for r in rows)

    # Neutral interpolant per stratum through the seven readable greys (grey-96 is
    # validation: labelled; grey-208 is W34 holdout: UNREAD, never interpolated from).
    strata = {}
    for r in rows: strata.setdefault(tuple(r['stratum']), []).append(r)
    curves, departures = {}, {}
    for key, rr in sorted(strata.items()):
        greys = sorted([r for r in rr if r['background'].startswith('grey')], key=lambda r: r['input'][0])
        xs = [g['input'][0] for g in greys]; ys = [g['output'][0] for g in greys]
        curves['-'.join(key)] = dict(inputs=xs, outputs=ys, roles=[g['role'] for g in greys],
                                     note='grey-96 is validation (labelled); grey-208 UNREAD (W34 holdout)')
        for r in rr:
            if r['background'].startswith('grey'): continue
            departures[r['cell']] = (np.asarray(r['output']) - np.interp(r['input'], xs, ys)).tolist()

    by = {(r['background'], tuple(r['stratum'])): r for r in rows}
    # H1: input channel 32 against the EXACT calibration grey-32 observation of the
    # same stratum; low channels only, each checked uncensored. No interpolation.
    low = {'red': [1, 2], 'blue': [0, 1], 'green': [0, 2], 'yellow': [2], 'magenta': [1], 'cyan': [0]}
    h1 = []
    for key in sorted(strata):
        g32 = by[('grey-32', key)]['output'][0]
        entries = []
        for colour, channels in low.items():
            r = by[(colour, key)]
            for c in channels:
                assert r['input'][c] == 32
                entries.append(dict(background=colour, role=r['role'], channel='RGB'[c], native=r['output'][c],
                                    censored=r['outputCensored'][c], departureFromGrey32=r['output'][c] - g32))
        cal = [e for e in entries if e['role'] == 'calibration' and not e['censored']]
        worst = max(cal, key=lambda e: abs(e['departureFromGrey32']))
        rb = by[('red', key)]['output'][1] - by[('blue', key)]['output'][1]
        h1.append(dict(stratum='-'.join(key), grey32=g32, inputChannel32=entries,
                       largestCalibrationDeparture=worst, redMinusBlueG=rb,
                       redBlueRoles=[by[('red', key)]['role'], by[('blue', key)]['role']]))
    la = {h['stratum']: h for h in h1}
    for s in ['light-active-1x', 'light-active-2x']:
        got = {e['background']: e['native'] for e in la[s]['inputChannel32'] if e['background'] != 'cyan'}
        assert la[s]['grey32'] == 148 and got == dict(red=133, blue=143, green=96, yellow=81, magenta=127), got
        assert la[s]['redMinusBlueG'] == -10
    for s in ['dark-active-1x', 'dark-active-2x']: assert la[s]['redMinusBlueG'] == -8
    minimum_worst = min(abs(h['largestCalibrationDeparture']['departureFromGrey32']) for h in h1)

    # A grey-anchored luminance-only diagnostic: green's output luma against the
    # neutral interpolant evaluated at green's input luma (finite-interpolant witness).
    excess = {}
    for key in [('dark', 'active', '1x'), ('light', 'active', '1x')]:
        r = by[('green', key)]; curve = curves['-'.join(key)]
        y_in = float(decode(r['input']) @ W); y_out = float(decode(r['output']) @ W)
        neutral = float(decode(np.interp(encode(y_in), curve['inputs'], curve['outputs'])))
        excess['-'.join(key)] = dict(inputY=y_in, outputY=y_out, neutralInterpolantY=neutral,
                                     excess=y_out - neutral, interpolantRoles='calibration greys + validation grey-96')
    assert round(excess['dark-active-1x']['excess'], 8) == .06482068
    assert round(excess['light-active-1x']['excess'], 8) == .02917607

    # The shipped H2 as a body predictor: W35's recorded native/web deep medians.
    raw_table = W35_LEVEL_TABLE.read_bytes(); table = {r['cell']: r for r in json.loads(raw_table)}
    h2 = []
    for scale in ['1x', '2x']:
        cell = f'apple-macos-27.0-{scale}-dark-standard-glass0.5/red__circular-120__rest'
        t = table[cell]; mine = by[('red', ('dark', 'active', scale))]
        assert t['role'] == 'calibration' and t['nativeMedian'] == mine['output'] == [242.0, 50.0, 50.0]
        assert t['webMedian'] == [160.0, 90.0, 90.0] and not any(censored(t['nativeMedian']))
        h2.append(dict(cell=cell, role=t['role'], native=t['nativeMedian'], shippedRender=t['webMedian'],
                       renderMinusNative=(np.asarray(t['webMedian']) - t['nativeMedian']).tolist(),
                       nativeUncensored=True, guardedNativeReadingAgrees=True))

    memo = None
    if MEMO_READINGS.exists():
        prior = {r['cell']: r for r in json.loads(MEMO_READINGS.read_text())}
        assert set(prior) == {r['cell'] for r in rows}
        for r in rows:
            m = prior[r['cell']]
            assert m['output'] == r['output'] and m['bar'] == r['bar'] and m['measuredInput'] == r['measuredInput']
        memo = dict(path=str(MEMO_READINGS), sha256=hashlib.sha256(MEMO_READINGS.read_bytes()).hexdigest(),
                    cells=len(prior), outputsBarsAndInputsIdentical=True,
                    note='scratch grounding artefact outside the repository; the tables below stand alone')

    result = dict(
        declarationSha256=declaration, clause='charter v2 clause 3; c9a §5.184',
        access=dict(reader='W34 wave.Reader (packages/calibration/results/2026-09-23-w34-g0-contour-bed/wave.py)',
                    roles=list(ROLES), repeatInventorySha256=repeat.generation,
                    unread='grey-208 (W34 identification holdout) in all eight strata; no holdout directory, '
                           'sealed bulk file or holdout-role cell was opened'),
        statistic='per run: channel median at d<=-6 CSS px (>=4 px) of the archived native crop; cell: median '
                  'of seven run medians; bar: 0.5 + half the largest pairwise run-median separation',
        geometry='recorded alignment and attested origin alone agree to the code on all 104 cells',
        counts=dict(cells=len(rows), calibration=88, validation=16, runsPerCell=7, maximumBar=.5),
        neutralCurves=curves, h1=dict(
            verdict='REJECTED on unclipped calibration channels against the exact grey-32 observation',
            smallestStratumWorstDepartureCodes=minimum_worst, strata=h1,
            note='departure = native low channel minus the same stratum grey-32 output; H1 predicts 0'),
        lumaExcess=excess,
        h2Shipped=dict(verdict='REJECTED as a body predictor on unclipped dark active red',
                       source=str(W35_LEVEL_TABLE.relative_to(R.HERE.parents[3])),
                       sourceSha256=hashlib.sha256(raw_table).hexdigest(), cells=h2,
                       note='W35 calibration reading of the shipped render; W36 changed only the black '
                            'branch and W37/W38 shipped no colour change, so the reading still applies; '
                            'not a new render'),
        departuresFromNeutralInterpolant=departures, memoReproduction=memo, cells=rows)
    if '--verify' in sys.argv:
        recorded = json.loads(out_path.read_text())
        assert {**result, 'declarationSha256': None} == {**recorded, 'declarationSha256': None}
        print('archive-exclusions.json reproduced; recorded under declaration', recorded['declarationSha256'],
              '; current declaration', declaration)
        return
    with out_path.open('x') as f: json.dump(result, f, indent=1, sort_keys=True); f.write('\n')
    print(json.dumps(dict(cells=len(rows), h1Worst={h['stratum']: h['largestCalibrationDeparture']['departureFromGrey32']
                                                     for h in h1},
                          smallestStratumWorst=minimum_worst,
                          redMinusBlueG={h['stratum']: h['redMinusBlueG'] for h in h1},
                          lumaExcess={k: round(v['excess'], 8) for k, v in excess.items()},
                          h2=[(c['cell'], c['native'], c['shippedRender']) for c in h2], memo=bool(memo)), indent=1))


if __name__ == '__main__':
    main()
