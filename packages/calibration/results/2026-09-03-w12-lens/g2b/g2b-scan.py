"""W12 G2b whole-bed scan (the ω 0.8 A/B round, W12 Decision Log 4).

Reports the scratch matrix `matrix-g2b.json` against BOTH beds:
  (a) the G2 landing `matrix-g2.json` — the A/B proper, what ω 0.6 → 0.8 changes;
  (b) the 0.3.0 bed `matrix-w11c-g2-close.json` — the W12 stops of claims §5.51 §3.
The newest row per (profile, renderer, scene) key is used on every side, as the G2 scan did.
Only the webgpu tier was re-captured (the CSS tier has no lens), so the CSS rows are read
from the G2 bed and reported as carried, not re-measured.
"""
import json, sys, os, collections
import numpy as np
from PIL import Image

T = '/Users/new/.claude/jobs/5c70e47f/tmp/w12'
W = '/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a82623fa9fc3b23f9'
BED030 = json.load(open('/Users/new/.claude/jobs/5c70e47f/tmp/matrix-w11c-g2-close.json'))['cells']
G2 = json.load(open(f'{T}/matrix-g2.json'))['cells']
G2B = json.load(open(f'{T}/matrix-g2b.json'))['cells']


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
new = latest(G2B)


def m(c, ax, k):
    v = c.get(ax, {}).get(k)
    return v['value'] if isinstance(v, dict) else None


def backdrop(scene):
    return scene.split('__')[0]


def cls(scene):
    b = backdrop(scene)
    return 'solid' if b in ('light-solid', 'dark-solid', 'mid-dark-solid') else b


print(f'cells: 0.3.0 bed {len(bed)}  G2 {len(g2)}  G2b {len(new)} (webgpu only)')
print(f'  webgpu cells in G2 missing from G2b: '
      f'{sorted(k for k in g2 if k[1] == "webgpu" and k not in new)[:5]} '
      f'({len([k for k in g2 if k[1] == "webgpu" and k not in new])}); '
      f'extra in G2b: {len(set(new) - set(g2))}')


def rows_against(base, label):
    rows = []
    for k in sorted(set(base) & set(new)):
        o, n = base[k], new[k]

        def d(ax, kk):
            a, b = m(o, ax, kk), m(n, ax, kk)
            return None if a is None or b is None else b - a
        rows.append((k, m(o, 'perceptual', 'ssimMean'), m(n, 'perceptual', 'ssimMean'),
                     d('perceptual', 'ssimMean'), d('perceptual', 'oklabDeltaEMean'),
                     d('perceptual', 'oklabDeltaEP95'), d('material', 'interiorMeanWeb'),
                     d('shape', 'silhouetteIoU'), d('shape', 'contourDistanceP95')))
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
    print('\n== worst movers on the other axes (top 5 by |Δ| each)')
    for i, name in ((4, 'ΔE mean'), (5, 'ΔE p95'), (6, 'interior level'),
                    (7, 'silhouette IoU'), (8, 'contour p95')):
        top = sorted((r for r in rows if r[i] is not None), key=lambda r: -abs(r[i]))[:5]
        print(f'  {name:15s} ' + '; '.join(f'{r[0][2]}@{r[0][0][16:]}={r[i]:+.4f}' for r in top))
    return rows


def checkerboard_rows(base, label):
    print(f'\n== checkerboard texture rows, {label} → G2b (webgpu, light standard)')
    for scale in ('1x', '2x'):
        for comp in ('rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg',
                     'glass-over-glass', 'toolbar-group'):
            k = (f'apple-macos-26.5-{scale}-light-standard', 'webgpu',
                 f'checkerboard__{comp}__rest')
            if k in base and k in new:
                a = m(base[k], 'perceptual', 'ssimMean')
                b = m(new[k], 'perceptual', 'ssimMean')
                print(f'  {scale} {comp:17s} {a:.4f} → {b:.4f}  ({b - a:+.4f})')


rows_g2 = rows_against(g2, 'THE G2 LANDING (ω 0.6) — the A/B')
checkerboard_rows(g2, 'G2 (ω 0.6)')

print('\n== captures: max code-value delta per class, and the CSS tier')
capagg = collections.defaultdict(lambda: [0, 0, 0])  # n, changed, maxdelta
worst = []
for k in sorted(set(g2) & set(new)):
    prof, rend, scene = k
    a = f'{T}/web-captures-g2/{prof}/{scene}/{scene}__{rend}.png'
    b = f'{T}/web-captures-g2b/{prof}/{scene}/{scene}__{rend}.png'
    if not (os.path.exists(a) and os.path.exists(b)):
        continue
    A = np.asarray(Image.open(a).convert('RGBA')).astype(int)
    B = np.asarray(Image.open(b).convert('RGBA')).astype(int)
    if A.shape != B.shape:
        print('  shape mismatch', k)
        continue
    dd = int(np.abs(A - B).max())
    ch = int((np.abs(A - B).max(axis=2) > 0).sum())
    e = capagg[(cls(scene), rend)]
    e[0] += 1
    e[1] += (dd > 0)
    e[2] = max(e[2], dd)
    worst.append((dd, ch, k))
for (c, r), (n, chg, mx) in sorted(capagg.items()):
    print(f'  {c:13s} {r:6s} n={n:3d} changed={chg:3d} max code value={mx}')
print('  solid GPU captures that differ by > 1:',
      [(k, d) for d, ch, k in worst if cls(k[2]) == 'solid' and k[1] == 'webgpu' and d > 1][:10])
print('  CSS tier: not re-captured this round — no lens on that tier by contract; the G2 '
      'referee proved it byte-stable under the far larger G2 lens change.')

rows_bed = rows_against(bed, 'THE 0.3.0 BED — the W12 stops of claims §5.51 §3')
checkerboard_rows(bed, '0.3.0 bed')

print('\n== STOP: small-span texture cells below their 0.3.0 SSIM by more than 0.005')
fired = 0
for k in sorted(set(bed) & set(new)):
    if k[1] != 'webgpu':
        continue
    if any(x in k[2] for x in ('rrect-sm', 'capsule-button', 'toolbar-group')):
        o = m(bed[k], 'perceptual', 'ssimMean')
        n = m(new[k], 'perceptual', 'ssimMean')
        if o is not None and n is not None and n < o - 0.005:
            fired += 1
            print('  STOP', k, f'{o:.4f} → {n:.4f}')
if fired == 0:
    print('  (none)')
print('\n== STOP: any 1x row below its G2-landing SSIM by more than 0.002')
fired = 0
for k in sorted(set(g2) & set(new)):
    if '-1x-' not in k[0]:
        continue
    o = m(g2[k], 'perceptual', 'ssimMean')
    n = m(new[k], 'perceptual', 'ssimMean')
    if o is not None and n is not None and n < o - 0.002:
        fired += 1
        print('  BELOW', k, f'{o:.4f} → {n:.4f}')
if fired == 0:
    print('  (none)')
print('\n  (done)')
