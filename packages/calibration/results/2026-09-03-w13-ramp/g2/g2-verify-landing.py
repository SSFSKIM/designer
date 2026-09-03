#!/usr/bin/env python3
"""W13 G2: the canonical rebuild read against the dry run (claims §5.68 §7) — every GPU-tier
cell's rows equal to the dry run's and its capture byte-identical to the dry run's; every CSS-tier
cell's rows against sweep-4's CSS confirmation (the tier unchanged since); and, for the record,
the twelve rows of claims §5.68 §4 printed from the canonical matrix.

    python3 results/2026-09-03-w13-ramp/g2/g2-verify-landing.py <dry-run matrix> <dry-run captures>
"""
import json, os, sys, hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CAL = os.path.join(ROOT, 'packages', 'calibration')
S4 = os.path.join(CAL, 'results', '2026-09-03-w13-ramp', 'g1', 'sweep-4')
idx = lambda cells: {(c['key']['profileKey'], c['key']['web']['renderer'], c['key']['sceneId']): c for c in cells}
canon = idx(json.load(open(os.path.join(CAL, 'results', 'matrix.json')))['cells'])
dry = idx(json.load(open(sys.argv[1]))['cells'])
css = idx(json.load(open(os.path.join(S4, 'matrix-confirm-css.json')))['cells'])
dry_caps = sys.argv[2]

def v(c, axis, k):
    x = (c.get(axis) or {}).get(k)
    return None if x is None else (x['value'] if isinstance(x, dict) else x)

METRICS = [('perceptual', 'ssimMean'), ('perceptual', 'ssimBand'), ('perceptual', 'ssimOutside'),
           ('perceptual', 'oklabDeltaEMean'), ('material', 'interiorStdDevWeb'), ('shape', 'silhouetteIoU')]
worst = {'webgpu': 0.0, 'css': 0.0}; n = {'webgpu': 0, 'css': 0}; missing = []
for key, c in sorted(canon.items()):
    prof, rend, scene = key
    ref = dry.get(key) if rend == 'webgpu' else css.get(key)
    if ref is None:
        missing.append(key); continue
    n[rend] += 1
    for ax, met in METRICS:
        a, b = v(c, ax, met), v(ref, ax, met)
        if a is None or b is None: continue
        d = abs(a - b); worst[rend] = max(worst[rend], d)
        if d > 0.0002:
            print(f"  DEVIATION {d:+.5f} {met} {scene} @ {prof} / {rend} against "
                  f"{'dry run' if rend == 'webgpu' else 'sweep-4 CSS confirm'}: {a:.5f} vs {b:.5f}")
print(f"GPU tier: {n['webgpu']} cells against the dry run, worst |delta| {worst['webgpu']:.6f}")
print(f"CSS tier: {n['css']} cells against sweep-4's CSS confirmation, worst |delta| {worst['css']:.6f}")
if missing: print("no reference for:", missing)

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()
same = diff = 0
for (prof, rend, scene) in sorted(canon):
    if rend != 'webgpu': continue
    rel = os.path.join(prof, scene, f'{scene}__webgpu.png')
    a, b = os.path.join(CAL, 'web-captures', rel), os.path.join(dry_caps, rel)
    if not (os.path.exists(a) and os.path.exists(b)):
        print(f"  capture missing: {rel}"); continue
    if sha(a) == sha(b): same += 1
    else:
        diff += 1; print(f"  differs from the dry run: {scene} @ {prof}")
print(f"GPU captures byte-identical to the dry run: {same} / {same + diff}")

print("\nclaims §5.68 §4 — ssimMean, GPU tier, checkerboard cells (canonical):")
for scene in ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'glass-over-glass', 'rrect-lg', 'toolbar-group']:
    row = []
    for prof in ['apple-macos-26.5-1x-light-standard', 'apple-macos-26.5-2x-light-standard']:
        c = canon.get((prof, 'webgpu', f'checkerboard__{scene}__rest'))
        row.append('   -  ' if c is None else f"{v(c, 'perceptual', 'ssimMean'):.4f}")
    print(f"  {scene:18s} 1x {row[0]}  2x {row[1]}")
