"""W12 G3 whole-bed scan (the device-pixel body, claims §5.56).

Reports the scratch matrix `matrix-g3.json` against BOTH beds:
  (a) THE MATERIAL ON `main` — the webgpu rows from the ω 0.8 round (`matrix-g2b.json`)
      and the CSS rows from the G2 landing (`matrix-g2.json`), which together are what
      `main` draws today;
  (b) the 0.3.0 bed `matrix-w11c-g2-close.json` — the W12 stops of claims §5.51 §3.
The newest row per (profile, renderer, scene) key is used on every side.

Then each of §5.56 §4's six stops is checked and given its own verdict line.
"""
import collections
import json
import os

import numpy as np
from PIL import Image

T = '/Users/new/.claude/jobs/5c70e47f/tmp/w12'
BED030 = json.load(open('/Users/new/.claude/jobs/5c70e47f/tmp/matrix-w11c-g2-close.json'))['cells']
G2 = json.load(open(f'{T}/matrix-g2.json'))['cells']
G2B = json.load(open(f'{T}/matrix-g2b.json'))['cells']
G3 = json.load(open(f'{T}/matrix-g3.json'))['cells']


def key(c):
    return (c['key']['profileKey'], c['key']['web']['renderer'], c['key']['sceneId'])


def latest(cells):
    out = {}
    for c in cells:
        k = key(c)
        if k not in out or c['capturedAt'] > out[k]['capturedAt']:
            out[k] = c
    return out


bed = latest(BED030)
g2 = latest(G2)
g2b = latest(G2B)
new = latest(G3)

# The material on `main`: webgpu from the ω 0.8 round, css from the G2 landing.
main = {k: v for k, v in g2.items() if k[1] == 'css'}
main.update({k: v for k, v in g2b.items() if k[1] == 'webgpu'})
for k, v in g2.items():
    main.setdefault(k, v)

# Which capture directory each baseline row's PNG lives in.
MAIN_CAPS = {k: ('web-captures-g2b' if k in g2b else 'web-captures-g2') for k in main}


def m(c, ax, k):
    v = c.get(ax, {}).get(k)
    return v['value'] if isinstance(v, dict) else None


def ssim(c):
    return m(c, 'perceptual', 'ssimMean')


def backdrop(scene):
    return scene.split('__')[0]


def cls(scene):
    b = backdrop(scene)
    return 'solid' if b in ('light-solid', 'dark-solid', 'mid-dark-solid') else b


print(f'cells: 0.3.0 bed {len(bed)}  main {len(main)}  G3 {len(new)}')
missing = sorted(k for k in main if k not in new)
print(f'  rows on main missing from G3: {len(missing)} {missing[:5]}')
print(f'  rows in G3 not on main: {len(set(new) - set(main))}')


def rows_against(base, label):
    rows = []
    for k in sorted(set(base) & set(new)):
        o, n = base[k], new[k]

        def d(ax, kk):
            a, b = m(o, ax, kk), m(n, ax, kk)
            return None if a is None or b is None else b - a
        rows.append((k, ssim(o), ssim(n), d('perceptual', 'ssimMean'),
                     d('perceptual', 'oklabDeltaEMean'), d('perceptual', 'oklabDeltaEP95'),
                     d('material', 'interiorMeanWeb'), d('shape', 'silhouetteIoU'),
                     d('shape', 'contourDistanceP95')))
    print(f'\n\n######## AGAINST {label} ########')
    print('\n== class summary (max |Δ| over cells): class, tier, n, ΔSSIM, Δ(ΔE mean), Δ(ΔE p95), Δlevel')
    agg = collections.defaultdict(list)
    for r in rows:
        agg[(cls(r[0][2]), r[0][1])].append(r)
    for (c, t), rs in sorted(agg.items()):
        def mx(i):
            return max((abs(r[i]) for r in rs if r[i] is not None), default=0)
        print(f'  {c:13s} {t:7s} n={len(rs):3d}  ΔSSIM {mx(3):.4f}  ΔΔE {mx(4):.4f} '
              f' ΔΔEp95 {mx(5):.4f}  Δlevel {mx(6):.4f}')
    print('\n== cells with |ΔSSIM| > 0.005 (profile, renderer, scene: before → after)')
    named = 0
    for r in sorted(rows, key=lambda r: -(abs(r[3]) if r[3] else 0)):
        if r[3] is not None and abs(r[3]) > 0.005:
            named += 1
            print(f'  {r[0][0]:44s} {r[0][1]:6s} {r[0][2]:46s} '
                  f'{r[1]:.4f} → {r[2]:.4f} ({r[3]:+.4f})')
    if named == 0:
        print('  (none)')
    print(f'  [{named} cell(s) past 0.005]')
    print('\n== worst movers on the other axes (top 5 by |Δ| each)')
    for i, name in ((4, 'ΔE mean'), (5, 'ΔE p95'), (6, 'interior level'),
                    (7, 'silhouette IoU'), (8, 'contour p95')):
        top = sorted((r for r in rows if r[i] is not None), key=lambda r: -abs(r[i]))[:5]
        print(f'  {name:15s} ' + '; '.join(f'{r[0][2]}@{r[0][0][16:]}={r[i]:+.4f}' for r in top))
    return rows


def texture_rows(base, label, tier='webgpu'):
    print(f'\n== checkerboard texture rows, {label} → G3 ({tier}, light standard)')
    for scale in ('1x', '2x'):
        for comp in ('rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg',
                     'glass-over-glass', 'toolbar-group'):
            k = (f'apple-macos-26.5-{scale}-light-standard', tier,
                 f'checkerboard__{comp}__rest')
            if k in base and k in new:
                a, b = ssim(base[k]), ssim(new[k])
                print(f'  {scale} {comp:17s} {a:.4f} → {b:.4f}  ({b - a:+.4f})')


def photo_rows(base, label):
    print(f'\n== photo rows at 2x, {label} → G3')
    for tier in ('webgpu', 'css'):
        for k in sorted(set(base) & set(new)):
            if '-2x-' not in k[0] or k[1] != tier or not k[2].startswith('photo__'):
                continue
            a, b = ssim(base[k]), ssim(new[k])
            if a is None or b is None:
                continue
            print(f'  {tier:6s} {k[0][16:]:34s} {k[2]:44s} {a:.4f} → {b:.4f} ({b - a:+.4f})')


def capture_delta(k):
    """Max code-value delta between main's capture of this cell and G3's, or None."""
    prof, rend, scene = k
    a = f'{T}/{MAIN_CAPS.get(k, "web-captures-g2")}/{prof}/{scene}/{scene}__{rend}.png'
    b = f'{T}/web-captures-g3/{prof}/{scene}/{scene}__{rend}.png'
    if not (os.path.exists(a) and os.path.exists(b)):
        return None
    A = np.asarray(Image.open(a).convert('RGBA')).astype(int)
    B = np.asarray(Image.open(b).convert('RGBA')).astype(int)
    if A.shape != B.shape:
        return -1
    return int(np.abs(A - B).max())


rows_main = rows_against(main, 'THE MATERIAL ON main (webgpu ω 0.8, css G2)')
texture_rows(main, 'main')
texture_rows(main, 'main', tier='css')
photo_rows(main, 'main')

print('\n== captures: max code-value delta per class, main → G3')
capagg = collections.defaultdict(lambda: [0, 0, 0])
deltas = {}
for k in sorted(set(main) & set(new)):
    dd = capture_delta(k)
    if dd is None:
        continue
    deltas[k] = dd
    e = capagg[(cls(k[2]), k[1])]
    e[0] += 1
    e[1] += (dd > 0)
    e[2] = max(e[2], dd)
for (c, r), (n, chg, mx) in sorted(capagg.items()):
    print(f'  {c:13s} {r:6s} n={n:3d} changed={chg:3d} max code value={mx}')

rows_bed = rows_against(bed, 'THE 0.3.0 BED — the W12 stops of claims §5.51 §3')
texture_rows(bed, '0.3.0 bed')

# ─────────────────────────── the six stops of §5.56 §4 ───────────────────────────
print('\n\n######## THE SIX STOPS (claims §5.56 §4) ########')

# Stop 1 — the W12 stops of §5.51 §3.
print('\n--- STOP 1: every cell past 0.005 against the 0.3.0 bed named; no bound or floor '
      'regressed; no solid capture differing by a code value at either scale')
named = [(k, ssim(bed[k]), ssim(new[k])) for k in sorted(set(bed) & set(new))
         if ssim(bed[k]) is not None and ssim(new[k]) is not None
         and abs(ssim(new[k]) - ssim(bed[k])) > 0.005]
print(f'  cells past 0.005 against 0.3.0: {len(named)} (named in the section above)')
solid_moved = [(k, deltas[k]) for k in sorted(deltas)
               if cls(k[2]) == 'solid' and deltas[k] > 0]
print(f'  solid captures differing by a code value: {len(solid_moved)}'
      + (f' {solid_moved[:10]}' if solid_moved else ''))
print('  (bounds and floors: see the adopted-thresholds run beside this file)')

# Stop 2 — 1x unchanged.
print('\n--- STOP 2: every 1x row within 0.002 of main, and predicted +0.0000')
moved1x = []
for k in sorted(set(main) & set(new)):
    if '-1x-' not in k[0]:
        continue
    a, b = ssim(main[k]), ssim(new[k])
    if a is None or b is None:
        continue
    if abs(b - a) > 1e-9:
        moved1x.append((k, a, b, deltas.get(k)))
worst1x = max((abs(b - a) for _, a, b, _ in moved1x), default=0.0)
print(f'  1x rows compared: {len([k for k in set(main) & set(new) if "-1x-" in k[0]])}')
print(f'  1x rows that moved AT ALL: {len(moved1x)}; largest |ΔSSIM| {worst1x:.6f}')
for k, a, b, dd in sorted(moved1x, key=lambda r: -abs(r[2] - r[1]))[:40]:
    print(f'    {k[0][16:]:34s} {k[1]:6s} {k[2]:44s} {a:.6f} → {b:.6f} '
          f'({b - a:+.6f})  capture max code delta={dd}')
past = [r for r in moved1x if abs(r[2] - r[1]) > 0.002]
print(f'  VERDICT: {"PASS" if not past else "FAIL"} — {len(past)} row(s) past 0.002')
capmoved1x = [(k, deltas[k]) for k in sorted(deltas) if '-1x-' in k[0] and deltas[k] > 0]
print(f'  1x captures differing by a code value: {len(capmoved1x)}'
      + (f' {capmoved1x[:20]}' if capmoved1x else ''))

# Stop 3 — the three 2x GPU texture rows.
print('\n--- STOP 3: the 2x GPU texture rows within ±0.003 of the prediction, none below main')
PRED = {'rrect-md': 0.9545, 'rrect-ml': 0.9219, 'rrect-lg': 0.9164}
FLOOR = {'rrect-md': 0.93, 'rrect-ml': 0.9013, 'rrect-lg': 0.9002}
ok3 = True
for comp, pred in PRED.items():
    k = ('apple-macos-26.5-2x-light-standard', 'webgpu', f'checkerboard__{comp}__rest')
    a, b = ssim(main.get(k, {})), ssim(new.get(k, {}))
    if b is None:
        print(f'  {comp}: MISSING')
        ok3 = False
        continue
    within = abs(b - pred) <= 0.003
    notbelow = b >= a - 1e-9
    clears = b >= FLOOR[comp] - 1e-9
    ok3 = ok3 and within and notbelow and clears
    print(f'  {comp:9s} main {a:.4f} → G3 {b:.4f}  predicted {pred:.4f} '
          f'(Δ {b - pred:+.4f}, within ±0.003 {within}); not below main {notbelow}; '
          f'clears {FLOOR[comp]} {clears}')
print(f'  VERDICT: {"PASS" if ok3 else "FAIL"}')

# Stop 4 — the 2x CSS rows.
print('\n--- STOP 4: no 2x CSS row more than 0.002 below main')
below = []
for k in sorted(set(main) & set(new)):
    if '-2x-' not in k[0] or k[1] != 'css':
        continue
    a, b = ssim(main[k]), ssim(new[k])
    if a is None or b is None:
        continue
    if b < a - 0.002:
        below.append((k, a, b))
for k, a, b in below:
    print(f'    BELOW {k[0][16:]:34s} {k[2]:44s} {a:.4f} → {b:.4f} ({b - a:+.4f})')
print(f'  VERDICT: {"PASS" if not below else "FAIL"} — {len(below)} row(s) past 0.002 below')
print('  the three named 2x CSS dom rows (predicted 0.9187 / 0.8795 / 0.8700):')
for comp in ('rrect-md', 'rrect-ml', 'rrect-lg'):
    k = ('apple-macos-26.5-2x-light-standard', 'css', f'checkerboard__{comp}__rest')
    if k in new:
        a, b = ssim(main.get(k, {})), ssim(new[k])
        print(f'    {comp:9s} {a:.4f} → {b:.4f} ({b - a:+.4f})')

print('\n--- STOP 5: renderer goldens — see the golden run recorded in the round\'s report')
print('--- STOP 6: by eye — the user\'s, on the sheets beside this file')
print('\n  (done)')
