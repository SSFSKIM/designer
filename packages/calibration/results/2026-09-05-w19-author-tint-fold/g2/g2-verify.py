#!/usr/bin/env python3
"""W19 G2: the canonical rebuild read against the W18 bed and G1's dry run (claims §5.82) —
every GPU cell at every profile equal to the W18 bed's row and byte-identical to its capture
(contract X3, verified on the canonical bed itself; the holdout's GPU rows reproduce the bed's one
reading rather than re-reading it); every CSS-tier cell equal to the dry run's row (claims §5.81,
the holdout included, read once there under X8), with the byte-identity of its captures counted
against the dry run AND against the W18 bed (the untinted ones should equal the bed's bytes, the
full-strength tinted ones differ on the contour only, the dark scheme's equal the bed's); then the
seven held checkerboard rows with the W18 bed, the dry run, the canonical reading, the floor the
file holds today and the floor the landing pins (one FLOOR_EPSILON under the reading, or OFF where
the bound is met); every dom row against its adopted `ssimMean` / ΔE bound; the cross-tier
interior level (CSS − GPU, `interiorMeanWeb`) on the bed's tinted cells under Decision Log 3's
clauses; the tinted cells' OKLab ΔE against native and across the tiers, bed → canonical; the
cross-tier ΔE mean per profile; and the form and the shadow carrier each group drew, read off the
capture's own `report__css.json` (`cssTint`, `cssShadow`), which the matrix schema does not carry.

    python3 g2-verify.py <W18 bed matrix> <W18 bed captures dir> <dry-run matrix> <dry-run captures dir>

Derived from W18 G2's `g2-verify.py`.
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
def setof(c):
    for src in (c, c.get('key') or {}):
        for k in ('fixtureSet', 'set', 'split', 'partition'):
            if isinstance(src, dict) and k in src: return src[k]
    return '?'
M = [('perceptual','ssimMean'),('perceptual','ssimBand'),('perceptual','ssimInterior'),('perceptual','ssimOutside'),
     ('perceptual','oklabDeltaEMean'),('perceptual','oklabDeltaEP95'),('material','interiorStdDevWeb'),
     ('material','interiorMeanWeb'),('shape','silhouetteIoU'),('shape','contourDistanceMean')]
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
tinted = lambda scene: '-tint-' in scene
print(f"canonical: {len(canon)} cells; W18 bed: {len(bed)}; dry run: {len(dry)}")
lost = sorted(k for k in bed if k not in canon); new = sorted(k for k in canon if k not in bed)
print(f"rows on the W18 bed and not on the canonical bed: {lost if lost else 'none'}; new rows: {new if new else 'none'}")
for tag, ref, caps, rend in (('W18 bed', bed, bed_caps, 'webgpu'), ('dry run', dry, dry_caps, 'css')):
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
print("\nthe CSS captures against the W18 bed's bytes (S3's clause as the acceptance wrote it):")
cnt = {'untinted': [0, 0], 'tinted': [0, 0]}
for (prof, r, scene) in sorted(canon):
    if r != 'css': continue
    rel = os.path.join(prof, scene, f'{scene}__css.png')
    a, b = os.path.join(CAL, 'web-captures', rel), os.path.join(bed_caps, rel)
    if not os.path.exists(b): continue
    kind = 'tinted' if tinted(scene) else 'untinted'
    if sha(a) == sha(b): cnt[kind][0] += 1
    else:
        cnt[kind][1] += 1
        if kind == 'untinted': print(f"  UNTINTED capture differs from the W18 bed: {scene} @ {prof}")
for kind, (s_, d_) in cnt.items(): print(f"  {kind}: byte-identical {s_} / {s_ + d_}")
P = 'apple-macos-26.5-'
L1, L2 = P + '1x-light-standard', P + '2x-light-standard'
RT, IC = P + '1x-light-reduced-transparency', P + '1x-light-increased-contrast'
D1, D2 = P + '1x-dark-standard', P + '2x-dark-standard'
BOUNDS = {L1: (0.90, 0.08), L2: (0.92, 0.08), D1: (0.83, 0.09), D2: (0.85, 0.09), RT: (0.91, 0.04), IC: (0.83, 0.07)}
FLOORS = {(L2, 'checkerboard__rrect-md__rest'): 0.9142,
          (L1, 'checkerboard__rrect-ml__rest'): 0.8748, (L2, 'checkerboard__rrect-ml__rest'): 0.8779,
          (L1, 'checkerboard__glass-over-glass__rest'): 0.8604, (L2, 'checkerboard__glass-over-glass__rest'): 0.8677,
          (L1, 'checkerboard__rrect-lg__rest'): 0.8693, (L2, 'checkerboard__rrect-lg__rest'): 0.8712}
floor4 = lambda x: math.floor((x - 0.001) * 10000 + 1e-9) / 10000
print("\nthe seven rows held by floor — ssimMean, CSS tier, checkerboard (rrect-md 1x met its bound at W16):")
print(f"  {'cell':18s} dpr   W18 bed   dry      canonical   floor now   landing floor")
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
def level(mat, prof, scene):
    a, b = mat.get((prof, 'css', scene)), mat.get((prof, 'webgpu', scene))
    x, y = v(a, 'material', 'interiorMeanWeb'), v(b, 'material', 'interiorMeanWeb')
    return None if x is None or y is None else x - y
print("\nthe cross-tier interior level, CSS − GPU (interiorMeanWeb), on the bed's tinted cells (Decision Log 3):")
print(f"  {'cell':46s} {'profile':28s}  W18 bed    canonical   clause")
for (prof, r, scene) in sorted(canon):
    if r != 'css' or not tinted(scene): continue
    b, x = level(bed, prof, scene), level(canon, prof, scene)
    if prof in (L1, L2): clause, verdict = '0.005', ('met' if abs(x) <= 0.005 else 'FIRES (standing)' if abs(abs(x) - abs(b)) < 0.0002 else 'FIRES')
    elif prof in (RT, IC):
        # every bed cell is at s = 1, so ruling 3 (1)'s (1 − s) term is zero and the clause is the gap itself
        clause, verdict = '0.01 (s=1)', ('met' if abs(x) <= 0.01 else 'FIRES')
    else: clause, verdict = 'recorded', ''
    print(f"  {scene:46s} {prof.replace(P, ''):28s}  {b:+.4f}    {x:+.4f}     {clause} {verdict}")
print("\nthe tinted cells' OKLab ΔE, W18 bed → canonical (against native / across the tiers); rows that moved by ≥ 0.0001 marked:")
for (prof, r, scene) in sorted(canon):
    if r != 'css' or not tinted(scene): continue
    c, bc = canon[(prof, r, scene)], bed.get((prof, r, scene))
    nb, nx = v(bc, 'perceptual', 'oklabDeltaEMean'), v(c, 'perceptual', 'oklabDeltaEMean')
    cb, cx = v(bc, 'coherence', 'crossTierOklabDeltaEMean'), v(c, 'coherence', 'crossTierOklabDeltaEMean')
    mark = ' MOVED' if (nb is not None and abs(nx - nb) >= 0.0001) or (cb is not None and cx is not None and abs(cx - cb) >= 0.0001) else ''
    cbs = f"{cb:.4f}" if cb is not None else '  —   '; cxs = f"{cx:.4f}" if cx is not None else '  —   '
    print(f"  {scene:46s} {prof.replace(P, ''):28s} native {nb:.4f} → {nx:.4f}   tiers {cbs} → {cxs}{mark}")
print("\nthe cross-tier OKLab ΔE mean per profile over the non-holdout dom cells, W18 bed → canonical:")
for prof in (L1, L2, IC, RT, D1, D2):
    xs, bs = [], []
    for (p, r, scene), c in canon.items():
        if p != prof or r != 'css' or setof(c) == 'holdout': continue
        x, b = v(c, 'coherence', 'crossTierOklabDeltaEMean'), v(bed.get((p, r, scene)), 'coherence', 'crossTierOklabDeltaEMean')
        if x is None or b is None: continue
        xs.append(x); bs.append(b)
    if xs: print(f"  {prof.replace(P, ''):28s} {sum(bs)/len(bs):.5f} → {sum(xs)/len(xs):.5f}  ({len(xs)} cells)")
print("\nthe form and the shadow carrier each group drew (report__css.json: cssTint, cssShadow), counted over the canonical bed:")
forms, carriers = {}, {}
for (prof, r, scene) in sorted(canon):
    if r != 'css': continue
    rp = os.path.join(CAL, 'web-captures', prof, scene, 'report__css.json')
    if not os.path.exists(rp): continue
    rep = json.load(open(rp)); groups = (rep.get('page') or {}).get('groups') or []
    for g in groups:
        st = g.get('state') or {}
        forms.setdefault(st.get('cssTint') or '—', []).append((scene, prof))
        carriers.setdefault(st.get('cssShadow') or '—', []).append((scene, prof))
for f, cells in sorted(forms.items()):
    profs = sorted({p.replace(P, '') for _, p in cells}); tcount = sum(1 for s, _ in cells if tinted(s))
    print(f"  cssTint {f:8s} {len(cells):4d} groups ({tcount} on tinted scenes); profiles: {', '.join(profs)}")
    if f == 'encoded':
        for scene, prof in sorted(cells, key=lambda t: (t[1], t[0])):
            if tinted(scene): print(f"      encoded tinted: {scene} @ {prof.replace(P, '')}")
for f, cells in sorted(carriers.items()):
    print(f"  cssShadow {f:6s} {len(cells):4d} groups")
