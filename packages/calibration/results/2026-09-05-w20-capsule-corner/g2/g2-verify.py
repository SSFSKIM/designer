#!/usr/bin/env python3
"""W20 G2: the canonical rebuild read against the W19 bed and G0's conformance run (claims §5.86).

The GPU tier is where the change is: every capsule-button and toolbar-group cell (21 of 40 scenes,
every profile, holdout included — read once here under X8) against the W19 bed's fidelity rows
and against G0's bed-wide conformance rows; every other GPU cell (rounded rectangles and the
stack) equal to the W19 bed's row and byte-identical to its capture, holdout included, which is
the render path returning bit for bit what it returned below the crossing. The CSS tier did not
move (X3's inverse): its rows equal the W19 bed's except the two coherence rows, which are measured
against the GPU capture on disk and were predicted at G1 to move on the capsule cells; its captures
byte-identical. Then the seven held checkerboard rows, every dom row against its adopted bound,
the conformance rows over the canonical bed per component and tier (the bound W20 Decision Log 2
recommends), and the GPU tier's OKLab ΔE mean per profile, bed → canonical.

    python3 g2-verify.py <W19 bed matrix> <W19 bed captures dir> <G0 conformance matrix>

Derived from W19 G2's `g2-verify.py`.
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
g0 = load(sys.argv[3])
def v(c, ax, k):
    if c is None: return None
    x = (c.get(ax) or {}).get(k); return None if x is None else (x['value'] if isinstance(x, dict) else x)
def setof(c):
    for src in (c, c.get('key') or {}):
        for k in ('fixtureSet', 'set', 'split', 'partition'):
            if isinstance(src, dict) and k in src: return src[k]
    return '?'
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
corner = lambda scene: scene.split('__')[1] in ('capsule-button', 'toolbar-group')
P = 'apple-macos-26.5-'
M = [('perceptual','ssimMean'),('perceptual','oklabDeltaEMean'),('perceptual','oklabDeltaEP95'),
     ('material','interiorMeanWeb'),('material','rimPeakLuminanceWeb'),('shape','silhouetteIoU'),('shape','contourDistanceP95')]
COH = [('coherence','crossTierOklabDeltaEMean'),('coherence','interiorLevelRatioGpuOverCss')]
print(f"canonical: {len(canon)} cells; W19 bed: {len(bed)}; G0 conformance run: {len(g0)}")
lost = sorted(k for k in bed if k not in canon); new = sorted(k for k in canon if k not in bed)
print(f"rows on the W19 bed and not on the canonical bed: {lost if lost else 'none'}; new rows: {new if new else 'none'}")

print("\nGPU tier, the corner cells (capsule-button, toolbar-group) — W19 bed → canonical:")
imp = {m: [0, 0] for _, m in M[:2]}; best = {}; worst = {}
rows = []
for (prof, r, scene), c in sorted(canon.items()):
    if r != 'webgpu' or not corner(scene): continue
    bc = bed.get((prof, r, scene))
    de0, de1 = v(bc, 'perceptual', 'oklabDeltaEMean'), v(c, 'perceptual', 'oklabDeltaEMean')
    ss0, ss1 = v(bc, 'perceptual', 'ssimMean'), v(c, 'perceptual', 'ssimMean')
    g = g0.get((prof, r, scene))
    conf0 = (v(g, 'shape', 'declaredIoUWeb'), v(g, 'shape', 'declaredContourMaxWeb'))
    conf1 = (v(c, 'shape', 'declaredIoUWeb'), v(c, 'shape', 'declaredContourMaxWeb'))
    rows.append((prof, scene, setof(c), de0, de1, ss0, ss1, conf0, conf1))
    for m, a, b in (('oklabDeltaEMean', de0, de1), ('ssimMean', ss0, ss1)):
        if a is None or b is None: continue
        d = b - a
        better = d < 0 if m == 'oklabDeltaEMean' else d > 0
        imp[m][0 if better else 1] += 1
        if better and (m not in best or abs(d) > abs(best[m][0])): best[m] = (d, scene, prof)
        if not better and (m not in worst or abs(d) > abs(worst[m][0])): worst[m] = (d, scene, prof)
for m in ('oklabDeltaEMean', 'ssimMean'):
    b, w = best.get(m), worst.get(m)
    print(f"  {m:16s} improved {imp[m][0]:2d}  worsened {imp[m][1]:2d}   best {b[0]:+.5f} {b[1]} @ {b[2].replace(P,'')}" + (f"   worst {w[0]:+.6f} {w[1]} @ {w[2].replace(P,'')}" if w else ''))
print(f"  {'cell':46s} {'profile':28s} {'set':11s}  ΔE bed→canon        SSIM bed→canon      conformance IoU/contour G0→canon")
for prof, scene, st, de0, de1, ss0, ss1, c0, c1 in rows:
    f = lambda x, n=4: ('  —  ' if x is None else f"{x:.{n}f}")
    print(f"  {scene:46s} {prof.replace(P,''):28s} {st:11s}  {f(de0)} → {f(de1)}    {f(ss0)} → {f(ss1)}    {f(c0[0])}/{f(c0[1],2)} → {f(c1[0])}/{f(c1[1],2)}")
worsened = [(scene, prof, de1 - de0, ss1 - ss0) for prof, scene, st, de0, de1, ss0, ss1, c0, c1 in rows
            if de0 is not None and ((de1 - de0) > 0 or (ss1 - ss0) < 0)]
print(f"  corner cells worsening on ΔE or SSIM: {len(worsened)}")
for scene, prof, dd, ds in worsened: print(f"    {scene} @ {prof.replace(P,'')}: ΔΔE {dd:+.6f}  ΔSSIM {ds:+.6f}")

print("\nGPU tier, every other cell — rows equal to the W19 bed and captures byte-identical (holdout included):")
n = same = diff = 0; worst_d = 0.0
for (prof, r, scene), c in sorted(canon.items()):
    if r != 'webgpu' or corner(scene): continue
    bc = bed.get((prof, r, scene)); n += 1
    for ax, m in M:
        a, b = v(c, ax, m), v(bc, ax, m)
        if a is None or b is None: continue
        d = abs(a - b); worst_d = max(worst_d, d)
        if d > 0.0002: print(f"  DEVIATION {d:+.5f} {m} {scene} @ {prof.replace(P,'')}: {a:.5f} vs {b:.5f}")
    rel = os.path.join(prof, scene, f'{scene}__webgpu.png')
    a, b = os.path.join(CAL, 'web-captures', rel), os.path.join(bed_caps, rel)
    if os.path.exists(b):
        if sha(a) == sha(b): same += 1
        else: diff += 1; print(f"  capture differs from the W19 bed: {scene} @ {prof.replace(P,'')} ({setof(c)})")
print(f"  {n} cells, worst |Δ| {worst_d:.6f}; captures byte-identical {same} / {same + diff}")

print("\nCSS tier — rows equal to the W19 bed (coherence rows listed where they moved), captures byte-identical:")
n = same = diff = 0; worst_d = 0.0; moved = []
for (prof, r, scene), c in sorted(canon.items()):
    if r != 'css': continue
    bc = bed.get((prof, r, scene)); n += 1
    for ax, m in M:
        a, b = v(c, ax, m), v(bc, ax, m)
        if a is None or b is None: continue
        d = abs(a - b); worst_d = max(worst_d, d)
        if d > 0.0002: print(f"  DEVIATION {d:+.5f} {m} {scene} @ {prof.replace(P,'')}: {a:.5f} vs {b:.5f}")
    for ax, m in COH:
        a, b = v(c, ax, m), v(bc, ax, m)
        if a is not None and b is not None and abs(a - b) > 0.0002: moved.append((scene, prof, m, b, a))
    rel = os.path.join(prof, scene, f'{scene}__css.png')
    a, b = os.path.join(CAL, 'web-captures', rel), os.path.join(bed_caps, rel)
    if os.path.exists(b):
        if sha(a) == sha(b): same += 1
        else: diff += 1; print(f"  capture differs from the W19 bed: {scene} @ {prof.replace(P,'')}")
print(f"  {n} cells, worst |Δ| on the non-coherence rows {worst_d:.6f}; captures byte-identical {same} / {same + diff}")
print(f"  coherence rows that moved (predicted at G1 on the corner cells): {len(moved)}; on non-corner cells: {sum(1 for s, *_ in moved if not corner(s))}")
for scene, prof, m, b, a in moved:
    if not corner(scene): print(f"    NON-CORNER {m} {scene} @ {prof.replace(P,'')}: {b:.5f} → {a:.5f}")

L1, L2 = P + '1x-light-standard', P + '2x-light-standard'
RT, IC = P + '1x-light-reduced-transparency', P + '1x-light-increased-contrast'
D1, D2 = P + '1x-dark-standard', P + '2x-dark-standard'
BOUNDS = {L1: (0.90, 0.08), L2: (0.92, 0.08), D1: (0.83, 0.09), D2: (0.85, 0.09), RT: (0.91, 0.04), IC: (0.83, 0.07)}
FLOORS = {(L2, 'checkerboard__rrect-md__rest'): 0.9142,
          (L1, 'checkerboard__rrect-ml__rest'): 0.8748, (L2, 'checkerboard__rrect-ml__rest'): 0.8779,
          (L1, 'checkerboard__glass-over-glass__rest'): 0.8604, (L2, 'checkerboard__glass-over-glass__rest'): 0.8677,
          (L1, 'checkerboard__rrect-lg__rest'): 0.8693, (L2, 'checkerboard__rrect-lg__rest'): 0.8712}
floor4 = lambda x: math.floor((x - 0.001) * 10000 + 1e-9) / 10000
print("\nthe seven rows held by floor — ssimMean, CSS tier, checkerboard:")
print(f"  {'cell':18s} dpr   W19 bed   canonical   floor now   landing floor")
for scene in ['rrect-md', 'rrect-ml', 'glass-over-glass', 'rrect-lg']:
    for prof, dpr in ((L1, 1), (L2, 2)):
        key = (prof, 'css', f'checkerboard__{scene}__rest'); c = canon[key]
        b, x = v(bed[key], 'perceptual', 'ssimMean'), v(c, 'perceptual', 'ssimMean')
        fl = FLOORS.get((prof, key[2])); bound = BOUNDS[prof][0]
        if fl is None: new = f"no floor (≥ {bound} {'met' if x >= bound else 'MISSED'})"
        elif x >= bound: new = f"OFF (≥ {bound})"
        elif x >= fl: new = f"{fl:.4f} kept" if floor4(x) <= fl else f"{floor4(x):.4f} (ratchet)"
        else: new = f"{floor4(x):.4f} (RE-PIN, was {fl})"
        print(f"  {scene:18s} {dpr}x   {b:.5f}   {x:.5f}    {'  —  ' if fl is None else f'{fl:.4f}'}      {new}")
print("\nevery dom row against its adopted ssimMean / ΔE bound (rows under a bound listed):")
under = 0
for (prof, r, scene), c in sorted(canon.items()):
    if r != 'css' or prof not in BOUNDS: continue
    s, e = v(c, 'perceptual', 'ssimMean'), v(c, 'perceptual', 'oklabDeltaEMean'); sb, eb = BOUNDS[prof]
    if s < sb or e > eb:
        under += 1; fl = FLOORS.get((prof, scene))
        print(f"  {scene:44s} {prof.replace(P, ''):28s} ssimMean {s:.4f} (≥ {sb}{', floor ' + str(fl) if fl else ''})  ΔE {e:.4f} (≤ {eb})")
print(f"  {under} dom rows under an adopted bound")

print("\nthe conformance rows over the canonical bed, per tier and component (min IoU, max contour, cells carrying rows / cells with a shape axis):")
agg = {}
for (prof, r, scene), c in sorted(canon.items()):
    if c.get('shape') is None: continue
    comp = scene.split('__')[1]; k = (r, comp)
    a = agg.setdefault(k, [1.0, 0.0, 0, 0]); a[3] += 1
    iou, cm = v(c, 'shape', 'declaredIoUWeb'), v(c, 'shape', 'declaredContourMaxWeb')
    if iou is None: continue
    a[2] += 1; a[0] = min(a[0], iou); a[1] = max(a[1], cm)
for (r, comp), (iou, cm, n1, n2) in sorted(agg.items()):
    print(f"  {r:7s} {comp:18s} min IoU {iou:.4f}  max contour {cm:.2f} px   rows {n1:3d} / {n2:3d}")

print("\nthe GPU tier's OKLab ΔE mean per profile, W19 bed → canonical (non-holdout | holdout):")
for prof in (L1, L2, IC, RT, D1, D2):
    out = []
    for hold in (False, True):
        xs, bs = [], []
        for (p, r, scene), c in canon.items():
            if p != prof or r != 'webgpu' or (setof(c) == 'holdout') != hold: continue
            x, b = v(c, 'perceptual', 'oklabDeltaEMean'), v(bed.get((p, r, scene)), 'perceptual', 'oklabDeltaEMean')
            if x is None or b is None: continue
            xs.append(x); bs.append(b)
        out.append(f"{sum(bs)/len(bs):.5f} → {sum(xs)/len(xs):.5f} ({len(xs)})" if xs else '—')
    print(f"  {prof.replace(P, ''):28s} {out[0]}  |  {out[1]}")
