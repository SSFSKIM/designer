#!/usr/bin/env python3
"""W15 G2: the canonical rebuild read against the G1 confirmation (claims §5.70 §8) and the W13 bed
— every GPU cell of the four standard profiles equal to the confirmation's rows and byte-identical
to its captures (holdout included: the confirmation's reading stands, the landing reproduces it);
every 1x GPU capture byte-identical to the W13 bed's (the binding rule, on the canonical bed
itself); every CSS-tier row equal to the W13 bed's (W13 Decision Log 5 kept); the accessibility
profiles' GPU rows against the W13 bed (no confirmation reference); and the twelve rows printed.

    python3 g2-verify.py <confirmation matrix> <confirmation captures dir> <W13 bed matrix> <W13 bed captures dir>
"""
import json, os, sys, hashlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CAL = os.path.join(ROOT, 'packages', 'calibration')
idx = lambda cells: {(c['key']['profileKey'], c['key']['web']['renderer'], c['key']['sceneId']): c for c in cells}
canon = idx(json.load(open(os.path.join(CAL, 'results', 'matrix.json')))['cells'])
conf = idx(json.load(open(sys.argv[1]))['cells']); conf_caps = sys.argv[2]
bed = idx(json.load(open(sys.argv[3]))['cells']); bed_caps = sys.argv[4]
def v(c, ax, k):
    x = (c.get(ax) or {}).get(k); return None if x is None else (x['value'] if isinstance(x, dict) else x)
M = [('perceptual','ssimMean'),('perceptual','ssimBand'),('perceptual','ssimOutside'),('perceptual','oklabDeltaEMean'),('material','interiorStdDevWeb'),('shape','silhouetteIoU')]
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
worst = {'gpu-conf': 0.0, 'css-bed': 0.0}; n = {'gpu-conf': 0, 'css-bed': 0}; acc = []
for key, c in sorted(canon.items()):
    prof, rend, scene = key
    if rend == 'css':
        ref, tag = bed.get(key), 'css-bed'
    elif key in conf:
        ref, tag = conf[key], 'gpu-conf'
    else:
        acc.append(key); continue
    if ref is None: print(f"  no reference: {key}"); continue
    n[tag] += 1
    for ax, m in M:
        a, b = v(c, ax, m), v(ref, ax, m)
        if a is None or b is None: continue
        d = abs(a - b); worst[tag] = max(worst[tag], d)
        if d > 0.0002: print(f"  DEVIATION {d:+.5f} {m} {scene} @ {prof} / {rend} against {tag}: {a:.5f} vs {b:.5f}")
print(f"GPU tier, four standard profiles: {n['gpu-conf']} cells against the confirmation, worst |Δ| {worst['gpu-conf']:.6f}")
print(f"CSS tier: {n['css-bed']} cells against the W13 bed, worst |Δ| {worst['css-bed']:.6f}")
same = diff = 0; same1 = diff1 = 0
for (prof, rend, scene) in sorted(canon):
    if rend != 'webgpu': continue
    rel = os.path.join(prof, scene, f'{scene}__webgpu.png'); a = os.path.join(CAL, 'web-captures', rel)
    b = os.path.join(conf_caps, rel)
    if os.path.exists(b):
        if sha(a) == sha(b): same += 1
        else: diff += 1; print(f"  differs from the confirmation: {scene} @ {prof}")
    if '1x' in prof:
        b1 = os.path.join(bed_caps, rel)
        if os.path.exists(b1):
            if sha(a) == sha(b1): same1 += 1
            else: diff1 += 1; print(f"  1x differs from the W13 bed: {scene} @ {prof}")
print(f"GPU captures byte-identical to the confirmation: {same} / {same + diff}")
print(f"1x GPU captures byte-identical to the W13 bed: {same1} / {same1 + diff1}")
print(f"\naccessibility profiles, GPU tier ({len(acc)} cells), against the W13 bed:")
for key in acc:
    c, b = canon[key], bed.get(key)
    if b is None: continue
    dm = v(c,'perceptual','ssimMean') - v(b,'perceptual','ssimMean'); db = (v(c,'perceptual','ssimBand') or 0) - (v(b,'perceptual','ssimBand') or 0)
    print(f"  {key[0].replace('apple-macos-26.5-1x-light-',''):22s} {key[2]:44s} ssimMean {dm:+.4f} band {db:+.4f}")
print("\nthe twelve rows — ssimMean, GPU tier, checkerboard (canonical):")
for scene in ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'glass-over-glass', 'rrect-lg', 'toolbar-group']:
    row = []
    for prof in ['apple-macos-26.5-1x-light-standard', 'apple-macos-26.5-2x-light-standard']:
        c = canon.get((prof, 'webgpu', f'checkerboard__{scene}__rest')); row.append('   -  ' if c is None else f"{v(c,'perceptual','ssimMean'):.4f}")
    print(f"  {scene:18s} 1x {row[0]}  2x {row[1]}")
