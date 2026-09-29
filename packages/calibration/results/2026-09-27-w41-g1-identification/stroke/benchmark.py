"""Synthetic resource sizing only; no archive, optimizer or native measurement.

The declared 504 calibration cells are a planning count from G0's replay, not a
native read. This stress fixture repeats the large 2x circular footprint for all
504 cells. Actual geometry membership and gradient costs must be measured after
authorized preparation; the numbers below are not an end-to-end fit promise.
"""
import json
import resource
import time
import numpy as np
import scipy
import replay

m, f = replay.m, replay.f
start = time.perf_counter()
shape = m.readers.Shape('capsule-circular', (120., 44.), (20., 20.))
geo = m.readers.geometry((180, 340), [shape], 2)
bins, labels, selected = replay.required_bins(geo, 0)
yy, xx = np.nonzero(selected)
g = m.samples(shape, np.c_[xx, yy], 2)
# A nonconstant synthetic held falloff catches the cost of the shadow correction.
fall = np.exp(-np.maximum(g['d'], 0)/5)
kernel = replay.CoverageKernel(g, fall)
observations = []
for i in range(504):
    colour = np.array([48+i%140, 60+(3*i)%120, 80+(7*i)%100], float)
    b = np.broadcast_to(colour, (*g['d'].shape, 3))
    observations.append(dict(endpoint=i%4,
        compact=replay.CompactComposite(g, b, fall, kernel), amplitude=.12 if i%2 == 0 else 0.))
setup_seconds = time.perf_counter()-start
rows = []
for family in ('M0', 'M1', 'M2'):
    for css, curvature in ((False, False), (True, False), (False, True)):
        _, _, q = f.domain(family, curvature)
        t = time.perf_counter()
        predictions = [replay.compact_predict(q, o, family, css, curvature) for o in observations]
        cold = time.perf_counter()-t
        t = time.perf_counter()
        for _ in range(3):
            q[7] += .00001
            predictions = [replay.compact_predict(q, o, family, css, curvature) for o in observations]
        warm = (time.perf_counter()-t)/3
        rows.append(dict(family=family,cssWidth=css,curvature=curvature,
            fullForwardColdSeconds=cold,materialPerturbationSeconds=warm,
            worst3000ForwardSecondsAtThisCost=3000*cold,
            optimizerFiniteDifferencesAndConstraintsNotIncluded=True))
pixels = len(xx)*len(observations)
samples = pixels*256
print(json.dumps(dict(schema='w41-stroke-synthetic-resource-1',nativePayloadReads=0,
    syntheticCells=len(observations),pixelsPerCell=len(xx),totalPixels=pixels,
    setupSeconds=setup_seconds,peakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    python=__import__('sys').version,numpy=np.__version__,scipy=scipy.__version__,
    naiveAllCellArraysBytes=samples*(2*8+3*8+1+3*8+3*8),
    largestRawJacobianBytes=pixels*3*44*8,rows=rows,
    qualification='Repeated 2x circular uniform fixture. No native payloads, no fitting; '
        'continuous-path construction, gradients, SLSQP constraints, rank SVD and '
        'optimizer evaluation counts remain additional costs. Full declared budgets '
        'must not be reduced to meet this estimate.'),indent=2,allow_nan=False))
