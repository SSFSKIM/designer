"""Fixed-held-coefficient32x32 sensitivity on the four deciding witnesses."""
import json
import numpy as np
import sys
from pathlib import Path
from types import SimpleNamespace
PRIMARY = Path(__file__).resolve().parent
PROOF = Path('/Users/new/vitrea-w41/pre-w41-proof')
SEALED = PROOF/'packages/calibration/results/2026-09-27-w41-g0-declaration/instrument'
sys.path.insert(0, str(SEALED))
import instrument
import shadow
sys.path.insert(0, str(instrument.G2))
import native
r = SimpleNamespace(m=instrument, shadow=shadow, HERE=PRIMARY)

wave, reader = native.guarded(Path((PRIMARY.parent/'archive-root.txt').read_text().strip()), ('calibration',))
assert reader.generation == '58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61'
rows = []
for scheme in ('light', 'dark'):
    for scale in (1, 2):
        cell = f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5/g128-c-capsule-circular-120x64__rest'
        runs, states = native.archive.unbundle(reader.read(cell, 'crop'))
        runs = [v for v in runs if v['admitted'] and v['protocol'] == 'normal']
        assert len(runs) == 7
        payloads = [native.archive.unpack(states[v['state']]) for v in runs]
        p = payloads[0]
        shape = r.m.readers.shapes_of(p['component'])[0]
        geo = r.m.readers.geometry(p['rgb'].shape[:2], [shape], scale)
        bins, labels = r.m.readers.edge_bins(geo)
        shell = 2*scale
        index = next(i for i, b in enumerate(bins) if b['shell'] == shell
                     and b['part'] == 'straight' and b['side'] == 'bottom')
        yy, xx = np.nonzero(labels == index)
        g = r.m.samples(shape, np.c_[xx, yy], scale, order=32)
        assert len(xx) >= 4 and g['d'].min() >= 2*scale
        b = r.m.bilinear(p['noGlass'], g['q'])
        luminance = float(r.m.body.decode(p['noGlass'].mean(axis=(0, 1))/255) @ r.m.body.W)
        alpha = r.shadow.at(g['q'], shape, scale, r.shadow.materials()[scheme+'-active'], luminance)
        prediction = (b*(1-alpha[..., None])).mean(1)
        rgb = np.array([v['rgb'][yy, xx] for v in payloads])
        error = abs(prediction[None]-rgb).mean(1)
        bar = .5+.5*np.ptp(rgb.mean(1), axis=0)
        assert np.all(error > np.maximum(1, bar))
        assert np.all((rgb > 5) & (rgb < 250))
        rows.append(dict(cell=cell, shell=shell, pixels=len(xx),
            minimumDeviceSubpixelDistance=float(g['d'].min()),
            predictionRGB=prediction.mean(0).tolist(), nativeRunMeanRGB=rgb.mean(1).tolist(),
            absolutePixelErrorMeanRGBAllSevenRuns=error.tolist(), barRGB=bar.tolist(),
            everyRunEveryChannelFails=True, source='sealed shadow.at dense quadrature; no compact predictor',
            cropSha256=reader.entries[cell, 'crop']['sha256']))
with (PRIMARY/'support-controls-attempt-1/dense-witness-quadrature32.json').open('x') as f:
    json.dump(dict(proofRoot=str(PROOF), revision='d35b4cbf43f1fcdda55063b3b8e0fa178d720a78', quadrature=32, heldCoefficientsUnchanged=True, rows=rows), f, indent=2)
print(json.dumps(rows, indent=2))
