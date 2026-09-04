#!/usr/bin/env python3
"""W17 G2: the canonical rebuild read against the W16 bed and G1's frozen configuration 3 (claims §5.76) —
every GPU cell at every profile equal to the W16 bed's row and byte-identical to its capture
(contract X2, verified on the canonical bed itself; the holdout's GPU rows reproduce the bed's
one reading rather than re-reading it); every CSS-tier cell equal to configuration 3's row
(claims §5.75, the holdout included), with the byte-identity of its captures counted; then the eight held checkerboard
rows with the W16 bed, configuration 3, the canonical reading, the floor the file holds today and the
floor the landing pins (one FLOOR_EPSILON under the reading, or OFF where the bound is met), and
every dom row against its adopted `ssimMean` / ΔE bound.

    python3 g2-verify.py <W16 bed matrix> <W16 bed captures dir> <configuration 3 matrix> <configuration 3 captures dir>
"""
import json, os, sys, hashlib, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CAL = os.path.join(ROOT, 'packages', 'calibration')
def load(p):
    best = {}
    for c in json.load(open(p))['cells']:
        k = (c['key']['profileKey'], c['key']['web']['renderer'], c['key']['sceneId'])
        if k not in best or c['capturedAt'] > best[k]['capturedAt']: best[k] = c
    return best
canon = load(os.path.join(CAL, 'results', 'matrix.json'))
bed, bed_caps = load(sys.argv[1]), sys.argv[2]
dry, dry_caps = load(sys.argv[3]), sys.argv[4]
def v(c, ax, k):
    if c is None: return None
    x = (c.get(ax) or {}).get(k); return None if x is None else (x['value'] if isinstance(x, dict) else x)
M = [('perceptual','ssimMean'),('perceptual','ssimBand'),('perceptual','ssimInterior'),('perceptual','ssimOutside'),
     ('perceptual','oklabDeltaEMean'),('perceptual','oklabDeltaEP95'),('material','interiorStdDevWeb'),
     ('material','interiorMeanWeb'),('shape','silhouetteIoU'),('shape','contourDistanceMean')]
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
print(f"canonical: {len(canon)} cells; W16 bed: {len(bed)}; configuration 3: {len(dry)}")
for tag, ref, caps, rend in (('W16 bed', bed, bed_caps, 'webgpu'), ('configuration 3', dry, dry_caps, 'css')):
    n = 0; worst = 0.0; same = diff = 0; missing = []
    for key, c in sorted(canon.items()):
        prof, r, scene = key
        if r != rend: continue
        rc = ref.get(key)
        if rc is None: missing.append(key); continue
        n += 1
        for ax, m in M:
            a, b = v(c, ax, m), v(rc, ax, m)
            if a is None or b is None: continue
            d = abs(a - b); worst = max(worst, d)
            if d > 0.0002: print(f"  DEVIATION {d:+.5f} {m} {scene} @ {prof} / {r} against the {tag}: {a:.5f} vs {b:.5f}")
        rel = os.path.join(prof, scene, f'{scene}__{rend}.png')
        a, b = os.path.join(CAL, 'web-captures', rel), os.path.join(caps, rel)
        if os.path.exists(b):
            if sha(a) == sha(b): same += 1
            else: diff += 1; print(f"  capture differs from the {tag}: {scene} @ {prof} / {rend}")
    print(f"{rend} tier: {n} cells against the {tag}, worst |Δ| {worst:.6f}; captures byte-identical {same} / {same + diff}"
          + (f"; no reference for {len(missing)}: {missing}" if missing else ""))
P = 'apple-macos-26.5-'
L1, L2 = P + '1x-light-standard', P + '2x-light-standard'
BOUNDS = {L1: (0.90, 0.08), L2: (0.92, 0.08), P + '1x-dark-standard': (0.83, 0.09), P + '2x-dark-standard': (0.85, 0.09),
          P + '1x-light-reduced-transparency': (0.91, 0.04), P + '1x-light-increased-contrast': (0.83, 0.07)}
FLOORS = {(L2, 'checkerboard__rrect-md__rest'): 0.9138,
          (L1, 'checkerboard__rrect-ml__rest'): 0.8582, (L2, 'checkerboard__rrect-ml__rest'): 0.8772,
          (L1, 'checkerboard__glass-over-glass__rest'): 0.8518, (L2, 'checkerboard__glass-over-glass__rest'): 0.8677,
          (L1, 'checkerboard__rrect-lg__rest'): 0.8502, (L2, 'checkerboard__rrect-lg__rest'): 0.8698}
floor4 = lambda x: math.floor((x - 0.001) * 10000 + 1e-9) / 10000
print("\nthe eight rows W11c floored — ssimMean, CSS tier, checkerboard (rrect-md 1x met its bound at W16):")
print(f"  {'cell':18s} dpr   W16 bed   cfg 3    canonical   floor now   landing floor")
for scene in ['rrect-md', 'rrect-ml', 'glass-over-glass', 'rrect-lg']:
    for prof, dpr in ((L1, 1), (L2, 2)):
        key = (prof, 'css', f'checkerboard__{scene}__rest'); c = canon[key]
        b, d, x = v(bed[key], 'perceptual', 'ssimMean'), v(dry[key], 'perceptual', 'ssimMean'), v(c, 'perceptual', 'ssimMean')
        fl = FLOORS.get((prof, key[2])); bound = BOUNDS[prof][0]
        if fl is None: new = f"no floor (≥ {bound} {'met' if x >= bound else 'MISSED'})"
        elif x >= bound: new = f"OFF (≥ {bound})"
        elif x >= fl: new = f"{fl:.4f} kept" if floor4(x) <= fl else f"{floor4(x):.4f} (ratchet)"
        else: new = f"{floor4(x):.4f} (RE-PIN, was {fl})"
        print(f"  {scene:18s} {dpr}x   {b:.5f}   {d:.5f}   {x:.5f}    {'  —  ' if fl is None else f'{fl:.4f}'}      {new}")
print("\nevery dom row against its adopted ssimMean / ΔE bound (rows under a bound listed):")
under = 0
for (prof, r, scene), c in sorted(canon.items()):
    if r != 'css' or prof not in BOUNDS: continue
    s, e = v(c, 'perceptual', 'ssimMean'), v(c, 'perceptual', 'oklabDeltaEMean'); sb, eb = BOUNDS[prof]
    if s < sb or e > eb:
        under += 1; fl = FLOORS.get((prof, scene))
        print(f"  {scene:44s} {prof.replace(P, ''):28s} ssimMean {s:.4f} (≥ {sb}{', floor ' + str(fl) if fl else ''})  ΔE {e:.4f} (≤ {eb})")
print(f"  {under} dom rows under an adopted bound")
