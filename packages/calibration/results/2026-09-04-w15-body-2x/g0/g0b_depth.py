"""W15 G0 (b): the sharp share by depth at 2x with the base width settled, on every span.

(a) leaves two defensible width choices and this run reads the ramp under both, beside the
reading W13 G0 published at σ 9 device px so the difference is visible rather than implied:

  * **per span** — the width at which each cell's own bounded surface minimises;
  * **one number** — the width that minimises the pooled surface over the five spans
    (each cell's RMS normalised by its own minimum, so no cell's absolute residual sets the
    weight), which is the form §5.56 declared: one heavy σ in device pixels for the material.

The share is held inside [0, 1] throughout: a mix cannot have a negative weight, and (a)
measured that the free solve's negative deep windows cost 5–8% of RMS to remove at the width
the pixels prefer against 24–34% to remove by widening the kernel.
"""
import numpy as np

import w15lib as W

GRID = [round(x, 2) for x in np.arange(7.0, 16.01, 0.5)]

fits = {}
for comp in W.COMPS:
    fits[comp], _ = W.build(comp, 2)

# ---- the pooled surface: every cell's bounded RMS normalised by its own minimum
print('the pooled bounded surface over the five spans\n')
surface = {}
for comp in W.COMPS:
    fit = fits[comp]
    span = W.L.SPAN[comp]
    row = {}
    for sig in GRID:
        r = fit.solve_shared_t(W.SHARP_2X, W.heavy(sig), bounds=(0.0, 1.0), t_min=0.0)
        row[sig] = dict(rms=r['rms'], readoff=W.readoff(fit.rows(r), span),
                        t=float(np.mean([t for _, t in r['at']])))
    surface[comp] = row
    best = min(row, key=lambda s: row[s]['rms'])
    print(f'  {comp:<15} own best σ {best:5.2f} dev  rms {row[best]["rms"]:.5f}')

norm = {sig: float(np.mean([surface[c][sig]['rms'] / min(v['rms'] for v in surface[c].values())
                            for c in W.COMPS])) for sig in GRID}
pooled = min(norm, key=lambda s: norm[s])
norm_large = {sig: float(np.mean([surface[c][sig]['rms'] / min(v['rms'] for v in surface[c].values())
                                  for c in ('rrect-md', 'rrect-ml', 'rrect-lg')])) for sig in GRID}
pooled_large = min(norm_large, key=lambda s: norm_large[s])
print(f'\n  pooled over five spans: σ {pooled} device px (mean normalised RMS {norm[pooled]:.4f})')
print(f'  pooled over the three large spans: σ {pooled_large} device px '
      f'({norm_large[pooled_large]:.4f})')
print('  the normalised surface, five spans: '
      + ' '.join(f'{s:.1f}:{norm[s]:.3f}' for s in GRID))
print('  the normalised surface, large spans: '
      + ' '.join(f'{s:.1f}:{norm_large[s]:.3f}' for s in GRID))

# ---- the tables: W13's σ 9, the pooled number, the per-span optimum
W13_2X = {  # `g0-ramp.md` §1's 2x read-off, at σ 9 device px with the share free
    'rrect-sm': '0.474 / 0.439 (u 10) / —',
    'capsule-button': '0.437 / 0.430 / 484',
    'rrect-md': '0.192 / 0.075 / 59',
    'rrect-ml': '0.179 / −0.143 / 41',
    'rrect-lg': '0.141 / −0.247 / 39',
}
per_span = {c: min(surface[c], key=lambda s: surface[c][s]['rms']) for c in W.COMPS}
choices = [('σ 9 device px, share bounded (W13 G0\'s width)', {c: 9.0 for c in W.COMPS}),
           (f'σ {pooled:.1f} device px, share bounded (the pooled optimum)',
            {c: pooled for c in W.COMPS}),
           ('the per-span optimum, share bounded', per_span)]

out = {'grid': GRID, 'pooled_sigma': pooled, 'pooled_sigma_large': pooled_large,
       'normalised_surface': norm, 'normalised_surface_large': norm_large,
       'per_span_sigma': per_span, 'surface': surface, 'tables': {}, 'readoff': []}

for label, widths in choices:
    block = {}
    for comp in W.COMPS:
        fit, span, sig = fits[comp], W.L.SPAN[comp], widths[comp]
        r = fit.solve_shared_t(W.SHARP_2X, W.heavy(sig), bounds=(0.0, 1.0), t_min=0.0)
        rows = fit.rows(r)
        v = W.validated(rows, span)
        ro = W.readoff(rows, span)
        block[comp] = dict(sigma_device=sig, rms=r['rms'],
                           t=float(np.mean([t for _, t in r['at']])),
                           u=[x['u_mid'] for x in v], s=[1 - x['k'] for x in v],
                           u_all=[x['u_mid'] for x in rows], s_all=[1 - x['k'] for x in rows])
        out['readoff'].append(dict(comp=comp, choice=label, sigma_device=sig,
                                   s_first=ro['s_first'], u_first=ro['u_first'],
                                   s_deep=ro['s_deep'], deep_n=ro['deep_n'],
                                   s_last=ro['s_last'], u_last=ro['u_last'],
                                   reach_px=None if not np.isfinite(ro['reach_px'])
                                   else ro['reach_px'],
                                   reach_frac=ro['reach_frac'], rms=r['rms'],
                                   u_zero=ro['u_zero'], n_clamped=ro['n_clamped'],
                                   reach_unclamped=None if not np.isfinite(ro['reach_unclamped'])
                                   else ro['reach_unclamped'],
                                   w13=W13_2X[comp]))
    out['tables'][label] = block
    print(f'\n{label}')
    for comp, rec in block.items():
        print(f'  {comp:<15} σ {rec["sigma_device"]:5.2f}  rms {rec["rms"]:.5f}  t '
              f'{rec["t"]:.3f}  s: '
              + ' '.join(f'{u:.0f}:{s:+.3f}' for u, s in zip(rec['u'], rec['s'])))

print('\nthe read-off (start, deep value, reach) beside W13 G0\'s σ 9 free-share reading')
for row in out['readoff']:
    print(f'  {row["comp"]:<15} {row["choice"][:34]:<36} σ {row["sigma_device"]:5.2f}  start '
          f'{row["s_first"]:+.3f}  deep {row["s_deep"]:+.3f}  reach '
          f'{"—" if row["reach_px"] is None else f"{row['reach_px']:.0f}"}  reach* '
          f'{"—" if row["reach_unclamped"] is None else f"{row['reach_unclamped']:.0f}"}  '
          f'zero at {row["u_zero"]}   [W13 σ9 free: '
          f'{row["w13"]}]')

W.write_part('g0b-depth', out)
