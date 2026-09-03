#!/usr/bin/env python3
"""W15 G1: the confirmation run read against the W13 bed (canonical results/matrix.json) and the
sweep's own point — the 1x rows within 0.0002 and the 1x GPU captures byte-identical (the binding
rule), the 2x light calibration rows equal to the sweep's chosen point, the 2x holdout and the 2x
dark rows against the bed, the non-checkerboard cells and the outside rows for S5.

    python3 verify-confirm.py <matrix-confirm.json> <web-captures-confirm dir> <sweep point matrix>
"""
import json, os, sys, hashlib
CAL = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
idx = lambda cells: {(c['key']['profileKey'], c['key']['sceneId']): c for c in cells if c['key']['web']['renderer'] == 'webgpu'}
bed = idx(json.load(open(os.path.join(CAL, 'results', 'matrix.json')))['cells'])
conf = idx(json.load(open(sys.argv[1]))['cells'])
point = idx(json.load(open(sys.argv[3]))['cells']) if len(sys.argv) > 3 else {}
caps = sys.argv[2]
def v(c, ax, k):
    x = (c.get(ax) or {}).get(k); return None if x is None else (x['value'] if isinstance(x, dict) else x)
M = [('perceptual','ssimMean'),('perceptual','ssimBand'),('perceptual','ssimInterior'),('perceptual','ssimOutside'),('perceptual','oklabDeltaEMean'),('material','interiorStdDevWeb'),('material','interiorMeanWeb'),('shape','silhouetteIoU')]
sha = lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
# 1x: rows and bytes
worst1 = 0.0; same = diff = 0
for (p, s), c in sorted(conf.items()):
    if '1x' not in p: continue
    b = bed.get((p, s))
    if b:
        for ax, m in M:
            a, bb = v(c, ax, m), v(b, ax, m)
            if a is not None and bb is not None: worst1 = max(worst1, abs(a - bb))
    rel = os.path.join(p, s, f'{s}__webgpu.png')
    a, b2 = os.path.join(CAL, 'web-captures', rel), os.path.join(caps, rel)
    if os.path.exists(a) and os.path.exists(b2):
        if sha(a) == sha(b2): same += 1
        else: diff += 1; print(f"  1x capture differs: {s} @ {p}")
print(f"1x: {sum(1 for p,_ in conf if '1x' in p)} cells, worst |Δ| against the bed {worst1:.6f}; captures byte-identical {same} / {same + diff}")
# 2x light calibration vs the sweep's point
if point:
    w = 0.0; n = 0
    for (p, s), c in conf.items():
        if p != 'apple-macos-26.5-2x-light-standard': continue
        q = point.get((p, s))
        if q is None: continue
        n += 1
        for ax, m in M:
            a, bb = v(c, ax, m), v(q, ax, m)
            if a is not None and bb is not None: w = max(w, abs(a - bb))
    print(f"2x light against the sweep's point: {n} cells, worst |Δ| {w:.6f}")
# 2x rows against the bed
print(f"\n{'profile':8s} {'scene':44s} {'set':11s} {'ssimMean':>16s} {'band':>16s} {'interior':>16s} {'outside':>16s} {'stdWeb':>8s} {'stdNat':>8s}")
for (p, s), c in sorted(conf.items()):
    if '2x' not in p: continue
    b = bed.get((p, s))
    def cell(ax, m):
        a = v(c, ax, m); bb = v(b, ax, m) if b else None
        if a is None: return f"{'-':>16s}"
        return f"{a:.4f} ({a-bb:+.4f})" if bb is not None else f"{a:.4f}   (n/a)"
    print(f"{p.split('-')[3]+'-'+p.split('-')[4][:5]:8s} {s:44s} {c['fixtureSet']:11s} {cell('perceptual','ssimMean'):>16s} {cell('perceptual','ssimBand'):>16s} {cell('perceptual','ssimInterior'):>16s} {cell('perceptual','ssimOutside'):>16s} {v(c,'material','interiorStdDevWeb') or 0:8.4f} {v(c,'material','interiorStdDevNative') or 0:8.4f}")
