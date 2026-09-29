"""W42 G0 rehearsal round 2, item (e): does the landed T's non-monotone black end drive any dark
failure? Prints, per endpoint and surface kind, where the per-pixel landed response dips below
its value at black and where it climbs back (the join the REHEARSAL DEVICE holds the black value
flat to, variant c1d; a device, not a declaration), which dark cells have body pixels below that
join, and every L1 / M1 / M2 / Stop reading c1d moves against c1.

    python3.12 -B monotone.py --root /scratch/w42gate > round2/monotone.txt
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import body as B
from swap import population

ap = argparse.ArgumentParser(); ap.add_argument('--root', type=Path, required=True); args = ap.parse_args()
print(__doc__.split('\n\n')[0])
print('\nThe landed response per pixel near black (codes; input -> output):')
for ep in ('light-active', 'light-receded', 'dark-active', 'dark-receded'):
    for s, comp in ((1, 'capsule-button'), (2, 'rrect-md')):
        for key, (xj, y0, xm, ym) in B.black_join(ep, s, comp).items():
            print(f'  {ep:13s} {s}x {key:9s} black {B.enc(y0) * 255:6.1f}; dip to {B.enc(ym) * 255:6.1f} at input '
                  f'{xm * 255:5.2f}; back to the black value at input {xj * 255:5.2f}')
print('\nDark cells with body pixels whose argument luma lies below the join (the only pixels the device moves):')
for r in population([p for p in ('apple-macos-27.0-1x-dark-standard-glass0.5', 'apple-macos-27.0-2x-dark-standard-glass0.5')]):
    p, sc = r['key']['profileKey'], r['key']['sceneId']
    bg, comp, _ = sc.split('__')
    s = 2 if '-2x-' in p else 1
    ep = B.endpoint_of('dark', B.pose_of(sc))
    xj = min(v[0] for v in B.black_join(ep, s, comp).values()) * 255
    if xj <= 0:
        continue
    _, ML, _ = B.lt_argument(ep, s, bg, comp)
    m = B.field(comp, s).d < 0
    f = float(np.mean(ML[m] < xj))
    if f > 0:
        print(f'  {p[17:]:28s} {sc:48s} {f * 100:6.2f} % below {xj:.2f}')
print('\nc1d against c1 (dark stages; the light stage is c1\'s in both):')
a = {c['cell']: c for c in json.loads((args.root / 'ref-c1' / 'l1-cut.json').read_text())['cells']}
d = {c['cell']: c for c in json.loads((args.root / 'ref-c1d' / 'l1-cut.json').read_text())['cells']}
for k in sorted(a):
    if '-dark-' in k and a[k]['web'] is not None and abs(a[k]['web'] - d[k]['web']) > 1e-12:
        print(f"  L1 {k[17:]:62s} web {a[k]['web']:.4f} -> {d[k]['web']:.4f}; growth {a[k]['growth']:+.4f} -> {d[k]['growth']:+.4f}")
ca = {(c['profile'], c['scene']): c for c in json.loads((args.root / 'ref-c1' / 'chroma-cut.json').read_text())['cells']}
cd = {(c['profile'], c['scene']): c for c in json.loads((args.root / 'ref-c1d' / 'chroma-cut.json').read_text())['cells']}
moved = [k for k in ca if ca[k]['scheme'] == 'dark' and (ca[k]['R'] != cd[k]['R'] or ca[k]['interiorStdDevWeb'] != cd[k]['interiorStdDevWeb'])]
print(f'  M1/M2 dark cells moved: {len(moved)}')
sa = json.loads((args.root / 'ref-c1' / 'stops.json').read_text())['stops']
sd = json.loads((args.root / 'ref-c1d' / 'stops.json').read_text())['stops']
for key in ('halo', 'chroma'):
    A = {(c['profile'], c['scene']): c for c in sa[key]['cells']}
    for c in sd[key]['cells']:
        k = (c['profile'], c['scene'])
        if '-dark-' not in c['profile'] or c['verdict'] == 'UNMEASURED':
            continue
        diffs = {n: (round(A[k]['statistics'][n]['candidate'], 4), round(st['candidate'], 4), st['verdict'])
                 for n, st in c['statistics'].items() if abs(A[k]['statistics'][n]['candidate'] - st['candidate']) > 1e-9}
        if diffs:
            print(f'  Stop {key} {k[0][17:19]} {k[1]}: {diffs}')
