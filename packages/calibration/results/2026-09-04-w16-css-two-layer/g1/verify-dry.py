#!/usr/bin/env python3
"""W16 G1: the dry run read against the W15 bed under the charter's stops (W16 G2 stops S1–S6,
refined here with numbers). The canonical matrix and captures are the MAIN checkout's (the W15
bed, `c00f89e`); the dry run's are the scratch matrix and captures this branch's build wrote.

    python3 verify-dry.py <dry matrix> <dry captures dir> [--pre-w11c <matrix>] [--label dry]

Prints the GPU tier's byte-identity scan (S1), the CSS tier's rows per profile beside the bed
with every bound and floor (S2), the interior spread (S3) and level (S4) stops, the untouched
cells (S5), the coherence rows (S6), and a verdict line per stop. Numbers are printed as read;
nothing is rounded away.
"""
import argparse, hashlib, json, os
MAIN = '/Users/new/Developer/GitHub/designer/packages/calibration'
ap = argparse.ArgumentParser()
ap.add_argument('matrix'); ap.add_argument('captures')
ap.add_argument('--pre-w11c', default='/Users/new/.claude/jobs/5c70e47f/tmp/w16/matrix-pre-w11c.json')
ap.add_argument('--label', default='dry')
args = ap.parse_args()

def load(p):
    cells = json.load(open(p))['cells']; best = {}
    for c in cells:
        k = (c['key']['profileKey'], c['key']['web']['renderer'], c['key']['sceneId'])
        if k not in best or c['capturedAt'] > best[k]['capturedAt']: best[k] = c
    return best
bed = load(os.path.join(MAIN, 'results', 'matrix.json')); dry = load(args.matrix)
pre = load(args.pre_w11c) if os.path.exists(args.pre_w11c) else {}
def v(c, ax, k):
    if c is None: return None
    x = (c.get(ax) or {}).get(k); return None if x is None else (x['value'] if isinstance(x, dict) else x)
f = lambda x: '   —  ' if x is None else f'{x:.4f}'
sd = lambda a, b: '   —   ' if a is None or b is None else f'{a-b:+.4f}'
P = 'apple-macos-26.5-'
L1, L2, D1, D2 = P+'1x-light-standard', P+'2x-light-standard', P+'1x-dark-standard', P+'2x-dark-standard'
IC, RT = P+'1x-light-increased-contrast', P+'1x-light-reduced-transparency'
BOUNDS = {L1: (0.90, 0.08), L2: (0.92, 0.08), D1: (0.83, 0.09), D2: (0.85, 0.09), RT: (0.91, 0.04), IC: (0.83, 0.07)}
FLOORS = {(L1, 'checkerboard__rrect-md__rest'): 0.8952, (L2, 'checkerboard__rrect-md__rest'): 0.9159,
          (L1, 'checkerboard__rrect-ml__rest'): 0.847, (L2, 'checkerboard__rrect-ml__rest'): 0.8754,
          (L1, 'checkerboard__glass-over-glass__rest'): 0.8489, (L2, 'checkerboard__glass-over-glass__rest'): 0.8677,
          (L1, 'checkerboard__rrect-lg__rest'): 0.8361, (L2, 'checkerboard__rrect-lg__rest'): 0.8686}
CAL_CHECKER = ['checkerboard__rrect-sm__rest', 'checkerboard__capsule-button__rest', 'checkerboard__rrect-md__rest',
               'checkerboard__rrect-ml__rest', 'checkerboard__toolbar-group__rest']
PRE_LARGE = {'checkerboard__rrect-md__rest': 0.6451, 'checkerboard__rrect-ml__rest': 0.6444,
             'checkerboard__rrect-lg__rest': 0.6440, 'checkerboard__glass-over-glass__rest': 0.6818}
PRE_THIN = {'checkerboard__rrect-sm__rest': 0.6158, 'checkerboard__capsule-button__rest': 0.6133,
            'checkerboard__toolbar-group__rest': 0.6090}
PRE_HC = {'hc-text__capsule-button__rest': 0.9799, 'hc-text__rrect-md__rest': 0.9295}
verdict = {}
def stop(name, ok, note=''):
    verdict[name] = verdict.get(name, True) and ok
    if not ok: print(f'  STOP {name}: {note}')

# ---- S1: the GPU tier byte-identical, rows within 0.0002 ----
print(f'== S1 · the GPU tier against the W15 bed ({args.label})')
same = diff = missing = 0; worst = 0.0
M = [('perceptual','ssimMean'),('perceptual','ssimBand'),('perceptual','ssimInterior'),('perceptual','ssimOutside'),
     ('perceptual','oklabDeltaEMean'),('material','interiorStdDevWeb'),('material','interiorMeanWeb'),('shape','silhouetteIoU')]
for (prof, rend, scene), c in sorted(bed.items()):
    if rend != 'webgpu': continue
    d = dry.get((prof, rend, scene))
    if d is None: missing += 1; continue
    for ax, m in M:
        a, b = v(d, ax, m), v(c, ax, m)
        if a is None or b is None: continue
        worst = max(worst, abs(a-b))
        if abs(a-b) > 0.0002: stop('S1', False, f'{m} {scene} @ {prof}: {a:.5f} vs bed {b:.5f}')
    rel = os.path.join(prof, scene, f'{scene}__webgpu.png')
    a, b = os.path.join(MAIN, 'web-captures', rel), os.path.join(args.captures, rel)
    if os.path.exists(a) and os.path.exists(b):
        if hashlib.sha256(open(a,'rb').read()).digest() == hashlib.sha256(open(b,'rb').read()).digest(): same += 1
        else: diff += 1; stop('S1', False, f'capture differs: {scene} @ {prof}')
print(f'  GPU captures byte-identical {same}, differing {diff}, not captured {missing}; worst row |Δ| {worst:.6f}')
verdict.setdefault('S1', True)

# ---- the CSS tier per profile ----
def rows(prof, scenes=None):
    keys = sorted(k for k in bed if k[0] == prof and k[1] == 'css' and (scenes is None or k[2] in scenes))
    return [(k, bed[k], dry.get(k)) for k in keys]
for prof in (L1, L2):
    print(f'\n== CSS tier · {prof[16:]} — ssimMean bed→{args.label} | bound/floor | std bed→{args.label} / native | mean bed→{args.label} / native | band Δ | interior Δ | outside Δ | ΔE bed→{args.label} | xtier ΔE bed→{args.label} | level ratio')
    sb, de = BOUNDS[prof]
    for (p, r, scene), b, d in rows(prof):
        if d is None: print(f'  {scene:44s} not captured ({b["fixtureSet"]})'); continue
        floor = FLOORS.get((prof, scene)); bound = f'floor {floor}' if floor else f'≥ {sb}'
        s0, s1 = v(b,'perceptual','ssimMean'), v(d,'perceptual','ssimMean')
        ok = s1 >= (floor if floor else sb)
        print(f'  {scene:44s} {b["fixtureSet"][:4]} {f(s0)}→{f(s1)} {sd(s1,s0)} | {bound:13s} {"ok " if ok else "MISS"} | '
              f'{f(v(b,"material","interiorStdDevWeb"))}→{f(v(d,"material","interiorStdDevWeb"))} / {f(v(d,"material","interiorStdDevNative"))} | '
              f'{f(v(b,"material","interiorMeanWeb"))}→{f(v(d,"material","interiorMeanWeb"))} / {f(v(d,"material","interiorMeanNative"))} | '
              f'{sd(v(d,"perceptual","ssimBand"),v(b,"perceptual","ssimBand"))} | {sd(v(d,"perceptual","ssimInterior"),v(b,"perceptual","ssimInterior"))} | '
              f'{sd(v(d,"perceptual","ssimOutside"),v(b,"perceptual","ssimOutside"))} | {f(v(b,"perceptual","oklabDeltaEMean"))}→{f(v(d,"perceptual","oklabDeltaEMean"))} | '
              f'{f(v(b,"coherence","crossTierOklabDeltaEMean"))}→{f(v(d,"coherence","crossTierOklabDeltaEMean"))} | {f(v(d,"coherence","interiorLevelRatioGpuOverCss"))}')
        # S2: bounds, floors, the eight held rows not below the bed
        stop('S2', s1 >= sb or (floor is not None and s1 >= floor), f'{scene} @ {prof[16:]} ssimMean {s1:.4f} below its bound/floor')
        if floor is not None: stop('S2', s1 >= s0, f'{scene} @ {prof[16:]} held row below the bed {s1:.4f} < {s0:.4f}')
        e1 = v(d,'perceptual','oklabDeltaEMean')
        if e1 is not None: stop('S2', e1 <= de, f'{scene} @ {prof[16:]} ΔE {e1:.4f} above {de}')
        x1 = v(d,'coherence','crossTierOklabDeltaEMean'); lr = v(d,'coherence','interiorLevelRatioGpuOverCss')
        if x1 is not None: stop('S6', x1 <= 0.05, f'{scene} @ {prof[16:]} cross-tier ΔE {x1:.4f} above 0.05')
        if lr is not None: stop('S6', 0.8 <= lr <= 1.25, f'{scene} @ {prof[16:]} level ratio {lr:.4f} outside 0.8–1.25')
        # S3: the spread on the calibration checkerboard spans
        if scene in CAL_CHECKER:
            tol = 0.01 if prof == L1 else 0.015
            g = v(d,'material','interiorStdDevWeb') - v(d,'material','interiorStdDevNative')
            stop('S3', abs(g) <= tol, f'{scene} @ {prof[16:]} spread {g:+.4f} beyond ±{tol}')
        # S4: the level and hc-text at 1x
        if prof == L1:
            m1 = v(d,'material','interiorMeanWeb')
            if scene in PRE_LARGE: stop('S4', m1 >= PRE_LARGE[scene], f'{scene} mean {m1:.4f} below pre-W11c {PRE_LARGE[scene]}')
            if scene in PRE_THIN: stop('S4', m1 >= PRE_THIN[scene] - 0.002, f'{scene} mean {m1:.4f} below pre-W11c {PRE_THIN[scene]} − 0.002')
            if scene in PRE_HC: stop('S4', s1 >= PRE_HC[scene], f'{scene} ssimMean {s1:.4f} below pre-W11c {PRE_HC[scene]}')
        # S5: the solids and tinted cells within 0.002; photo reported, a fall beyond 0.002 stops
        fam = scene.split('__')[0]; tinted = 'tint' in scene
        if fam in ('light-solid','dark-solid','mid-dark-solid','impulse') or tinted:
            stop('S5', abs(s1-s0) <= 0.002 and abs(e1-v(b,'perceptual','oklabDeltaEMean')) <= 0.002, f'{scene} @ {prof[16:]} moved ssim {s1-s0:+.4f} ΔE {e1-v(b,"perceptual","oklabDeltaEMean"):+.4f}')
        elif fam == 'photo':
            stop('S5', s1 >= s0 - 0.002, f'{scene} @ {prof[16:]} photo fell {s1-s0:+.4f}')
for prof in (D1, D2, IC, RT):
    print(f'\n== CSS tier · {prof[16:]} — ssimMean bed→{args.label} | bound | ΔE bed→{args.label} | std {args.label}/native | xtier ΔE')
    sb, de = BOUNDS[prof]
    for (p, r, scene), b, d in rows(prof):
        if d is None: print(f'  {scene:44s} not captured ({b["fixtureSet"]})'); continue
        s0, s1 = v(b,'perceptual','ssimMean'), v(d,'perceptual','ssimMean'); e1 = v(d,'perceptual','oklabDeltaEMean')
        print(f'  {scene:44s} {b["fixtureSet"][:4]} {f(s0)}→{f(s1)} {sd(s1,s0)} | ≥ {sb} {"ok " if s1 >= sb else "MISS"} | {f(v(b,"perceptual","oklabDeltaEMean"))}→{f(e1)} | '
              f'{f(v(d,"material","interiorStdDevWeb"))}/{f(v(d,"material","interiorStdDevNative"))} | {f(v(b,"coherence","crossTierOklabDeltaEMean"))}→{f(v(d,"coherence","crossTierOklabDeltaEMean"))}')
        stop('S2', s1 >= sb, f'{scene} @ {prof[16:]} ssimMean {s1:.4f} below {sb}')
        if e1 is not None: stop('S2', e1 <= de, f'{scene} @ {prof[16:]} ΔE {e1:.4f} above {de}')
        x1 = v(d,'coherence','crossTierOklabDeltaEMean')
        if x1 is not None: stop('S6', x1 <= 0.05, f'{scene} @ {prof[16:]} cross-tier ΔE {x1:.4f} above 0.05')
# S6: the cross-tier ΔE over the fitted sets does not rise
for prof in (L1, L2, D1, D2):
    xs = [(v(b,'coherence','crossTierOklabDeltaEMean'), v(d,'coherence','crossTierOklabDeltaEMean')) for (p,r,s), b, d in rows(prof) if d is not None and b['fixtureSet'] != 'holdout']
    xs = [(a, c) for a, c in xs if a is not None and c is not None]
    if xs:
        m0, m1 = sum(a for a, _ in xs)/len(xs), sum(c for _, c in xs)/len(xs)
        print(f'\n  cross-tier ΔE over the fitted sets @ {prof[16:]}: bed {m0:.5f} → {args.label} {m1:.5f} ({len(xs)} cells)')
        stop('S6', m1 <= m0 + 1e-9, f'cross-tier ΔE rose @ {prof[16:]}')
print('\n== verdicts'); [print(f'  {k}: {"met" if ok else "FIRED"}') for k, ok in sorted(verdict.items())]
