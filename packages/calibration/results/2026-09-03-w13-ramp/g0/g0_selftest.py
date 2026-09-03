"""W13 G0, step 0: the instrument's own self-tests before it is pointed at a capture.

1. The analytic plate equals the committed raster along every line used, both scales, every
   pitch (w12lib's self-test, re-run in this wave's geometry).
2. The estimator recovers a KNOWN k(u) from a synthetic capture produced by the same forward
   model at the same widths — with and without noise. This separates estimator error from
   model error: whatever the instrument misses on vitrea's real capture is the renderer
   differing from the model, not the solve.
"""
import numpy as np

import w13lib as L

rng = np.random.default_rng(0)
out = {'plate_self_test': {}, 'synthetic': {}}

for scale in (1, 2):
    for comp in ('rrect-md', 'rrect-lg'):
        for pitch in (8, 16, 32, 64):
            for edge in L.EDGES:
                key = f'{comp}@{scale}x-p{pitch}-{edge}'
                out['plate_self_test'][key] = L.plate_self_test(comp, pitch, scale, edge)
worst = max(out['plate_self_test'].values())
print(f'plate self-test: max |analytic − raster| = {worst:.8f} over '
      f"{len(out['plate_self_test'])} line sets")

# ---- the estimator on a synthetic field with a known ramp
for scale in (1, 2):
    for comp in ('rrect-md', 'rrect-lg'):
        span = L.SPAN[comp]
        sharp = ('gauss', 1.25 / 1)          # CSS px, the same at both scales here
        heavy = ('gauss', 10.0)
        truth_ramp = lambda d: 1.0 - (0.5 * np.maximum(0.0, 1 - d / (span / 2)))  # noqa: E731
        truth_flat = lambda d: 0.0 * d + L.vitrea_k(span)                          # noqa: E731
        for name, kfun in (('flat', truth_flat), ('ramp', truth_ramp)):
            sets, tags = L.build_sets(L.probe_loader(comp, scale), comp, scale,
                                      [16] if scale == 1 else [16], u_fit_min=2.0)
            for s in sets:
                s.Y = L.forward(s, sharp, heavy, 0.45, 0.42, kfun)
                s.Y += rng.normal(0, 0.002, s.Y.shape)
            wins = L.windows_for(span)
            fit = L.WindowFit(sets, wins)
            res = fit.solve_shared_t(sharp, heavy)
            rows = fit.rows(res)
            err = []
            for r in rows:
                if r['u0'] < 4 or r['u1'] > span / 2 - 4 + 1e-9:
                    continue
                truth = float(np.mean(kfun(np.linspace(r['u0'], r['u1'], 17))))
                err.append(abs(r['k'] - truth))
            out['synthetic'][f'{comp}@{scale}x-{name}'] = dict(
                rms=res['rms'], max_abs_k_error=float(max(err)), n_windows=len(err),
                at=res['at'],
                rows=[dict(u_mid=r['u_mid'], k=r['k'], se=r['se_k']) for r in rows])
            print(f'synthetic {comp}@{scale}x {name}: rms {res["rms"]:.5f}  '
                  f'max |k − truth| over the validated windows {max(err):.4f}')

L.write_part('g0-selftest', out)
