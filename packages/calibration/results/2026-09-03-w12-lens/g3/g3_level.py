"""G3 reading 4: level and transmission per span at both scales, over every backdrop family.

The interior mean of the 5.41 box against the plate's own interior statistics, 1x beside 2x, on all
thirteen probe backdrops; and the transmission t per span at both scales (the single-Gaussian fit's
t where a width is identifiable). 5.49 7 claims the reference's interior mean is scale-invariant to
±0.001 on every cell; this puts a number on every cell of the probe rather than the canonical bed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

from g3lib import *  # noqa: F401,F403

scenes1 = {f[:-4] for f in os.listdir(probe_dir(1)) if f.endswith('.png')}
scenes2 = {f[:-4] for f in os.listdir(probe_dir(2)) if f.endswith('.png')}
shared = sorted(scenes1 & scenes2)
out = dict(n_scenes=len(shared), cells={})
print(f'== {len(shared)} scenes present in both probes ({len(scenes1)} at 1x, {len(scenes2)} at 2x)')

worst = []
for scene in shared:
    backdrop, comp, variant = scene.split('__')
    if comp not in COMP:
        continue
    rec = dict(backdrop=backdrop, comp=comp, span=SPAN[comp], variant=variant)
    for scale in SCALES:
        m = box_mask(comp, scale)
        Y = capture(scene, scale)
        P = plate(backdrop, scale)
        pstd = float(P[m].std())
        r = dict(interior_mean=float(Y[m].mean()), interior_std=float(Y[m].std()),
                 plate_mean=float(P[m].mean()), plate_std=pstd)
        if pstd >= 0.02:
            s, _ = fit_single(Y, P, m, scale, backdrop)
            r.update(sigma=s['sigma'], sigma_dev=s['sigma'] * scale, t=s['t'], a=s['a'],
                     rms=s['rms'], r2=s['r2'], retained=r['interior_std'] / pstd,
                     sigma_ceiling=sigma_ceiling(P, backdrop, m, scale))
        rec[f'{scale}x'] = r
    rec['mean_delta_2x_minus_1x'] = rec['2x']['interior_mean'] - rec['1x']['interior_mean']
    if 't' in rec['1x'] and 't' in rec['2x']:
        rec['t_delta_2x_minus_1x'] = rec['2x']['t'] - rec['1x']['t']
    out['cells'][scene] = rec
    worst.append((abs(rec['mean_delta_2x_minus_1x']), scene))

worst.sort(reverse=True)
out['mean_scale_invariance'] = dict(
    max_abs_delta=worst[0][0], worst=[dict(scene=s, delta=out['cells'][s]['mean_delta_2x_minus_1x'])
                                      for _, s in worst[:10]],
    n_within_0_001=int(sum(1 for d, _ in worst if d <= 0.001)), n=len(worst))
print(f'== interior mean, 2x − 1x: {out["mean_scale_invariance"]["n_within_0_001"]}/{len(worst)} cells '
      f'within ±0.001; largest |Δ| {worst[0][0]:.4f} on {worst[0][1]}')
for d, s in worst[:10]:
    print(f'   {s:42s} Δ {out["cells"][s]["mean_delta_2x_minus_1x"]:+.4f}')

print('\n== transmission t by span, per backdrop (1x → 2x)')
for backdrop in PITCHES5 + [LC16, 'photo', 'hc-text']:
    row = []
    for comp in COMPS:
        scene = f'{backdrop}__{comp}__rest'
        if scene not in out['cells']:
            continue
        c = out['cells'][scene]
        if 't' not in c['1x'] or 't' not in c['2x']:
            continue
        row.append(f'{comp.replace("rrect-", "").replace("capsule-button", "cap"):3s} '
                   f'{c["1x"]["t"]:+.3f}→{c["2x"]["t"]:+.3f} (σ {c["1x"]["sigma"]:.2f}→{c["2x"]["sigma"]:.2f})')
    print(f'   {backdrop:18s} ' + ' | '.join(row))

print('\n== level a by span (1x → 2x), checkerboard pitch 16 and the photo null')
for backdrop in ['checkerboard', 'photo']:
    for comp in COMPS:
        scene = f'{backdrop}__{comp}__rest'
        if scene not in out['cells'] or 'a' not in out['cells'][scene]['1x']:
            continue
        c = out['cells'][scene]
        print(f'   {backdrop:14s} {comp:15s} a {c["1x"]["a"]:.3f} → {c["2x"]["a"]:.3f} | '
              f'mean {c["1x"]["interior_mean"]:.4f} → {c["2x"]["interior_mean"]:.4f} | '
              f'retained {c["1x"].get("retained", float("nan")):.3f} → {c["2x"].get("retained", float("nan")):.3f}')

write_part('level', out)
