#!/usr/bin/env python3
"""W13 G2: the dry run of the landing configuration (W13 Decision Log 8) read against its
predictions — the 1x GPU rows against sweep-4's confirmation (the ramp unchanged at dpr 1) and
the 2x GPU rows against the W14 bed (the ramp a null there and the widths restored), on every
perceptual row, plus byte identity of the captures where the prediction is identity.

    python3 results/2026-09-03-w13-ramp/g2/g2-verify.py <dry-run matrix> <dry-run captures dir>
"""
import json, os, sys, hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CAL = os.path.join(ROOT, 'packages', 'calibration')
dry = json.load(open(sys.argv[1]))['cells']
dry_caps = sys.argv[2]
bed = json.load(open(os.path.join(CAL, 'results', 'matrix.json')))['cells']
s4 = json.load(open(os.path.join(CAL, 'results', '2026-09-03-w13-ramp', 'g1', 'sweep-4', 'matrix-confirm.json')))['cells']
idx = lambda cells: {(c['key']['profileKey'], c['key']['web']['renderer'], c['key']['sceneId']): c for c in cells}
D, B, S = idx(dry), idx(bed), idx(s4)

def v(c, axis, k):
    x = (c.get(axis) or {}).get(k)
    return None if x is None else (x['value'] if isinstance(x, dict) else x)

METRICS = [('perceptual', 'ssimMean'), ('perceptual', 'ssimBand'), ('perceptual', 'ssimOutside'),
           ('perceptual', 'oklabDeltaEMean'), ('material', 'interiorStdDevWeb'), ('shape', 'silhouetteIoU')]
worst = 0.0
for key, c in sorted(D.items()):
    prof, rend, scene = key
    ref = S.get(key) if '1x' in prof else B.get(key)
    label = 'sweep-4' if '1x' in prof else 'W14 bed'
    if ref is None:
        print(f"  no reference for {scene} @ {prof}"); continue
    for ax, met in METRICS:
        a, b = v(c, ax, met), v(ref, ax, met)
        if a is None or b is None: continue
        d = abs(a - b); worst = max(worst, d)
        if d > 0.0002: print(f"  DEVIATION {d:+.5f} {met} {scene} @ {prof} against {label}: {a:.5f} vs {b:.5f}")
print(f"worst |delta| over {len(D)} cells x {len(METRICS)} metrics: {worst:.6f} (tolerance 0.0002)")

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.exists(p) else None
ident = 0; total = 0; diff = []
for key in D:
    prof, rend, scene = key
    if '2x' not in prof: continue
    total += 1
    a = sha(os.path.join(dry_caps, prof, scene, f'{scene}__{rend}.png'))
    b = sha(os.path.join(CAL, 'web-captures', prof, scene, f'{scene}__{rend}.png'))
    if a == b: ident += 1
    else: diff.append((prof, scene))
print(f"2x captures byte-identical to the W14 bed: {ident} / {total}")
for prof, scene in diff[:10]: print(f"  differs: {scene} @ {prof}")
