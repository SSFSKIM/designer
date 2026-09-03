"""W15 G0 (c), contract X4: what the instrument recovers from two known 2x laws.

Two known laws, because the reference readings of (a) and (b) mean nothing without them:

1. **vitrea's own 2x captures of the W13 bed.** There the share is one number per span
   (`scatterThickness(span) = 0.4 + 0.6·smoothstep(32, 256, span)` — the depth ramp is a
   verified null at 2x, claims §5.67 §2) and the widths are CSS-px quantities (σ_sharp 1.25,
   σ_heavy 10 CSS px = 2.5 and 20 device px at this scale). The instrument must read that
   share flat across depth to ±0.05 — the property every reference table turns on, since a
   ramp read where the material has none would be the instrument's and not Apple's. Its
   widths are recovered on the same captures, on a grid, which is the only way to see what
   the fitted width owes to the mip chain's tap rather than to the material's nominal σ.
2. **A synthetic 2x ramp with the reference's own widths** (σ_sharp 1 / σ_heavy 9 device px)
   and a share that starts at 0.30 at the contour and falls linearly to 0 over 50 CSS px —
   the shape (b) reads on the large spans. Built from the forward model with a constant
   transmission and Gaussian noise, then refitted blind.

The acceptance the charter set: ±0.05 in every window over 4 ≤ u ≤ span/2 − 4 on `rrect-md`
and `rrect-lg` for the first, and the synthetic's start within 0.05 and reach within 10 CSS
px for the second.
"""
import numpy as np

import w15lib as W

L = W.L
rng = np.random.default_rng(15)
NOISE = 0.002
SHARP_V, HEAVY_V = ('gauss', 1.25), ('gauss', 10.0)   # what vitrea draws, CSS px
SHARP_R, HEAVY_R = ('gauss', 0.5), ('gauss', 4.5)     # the reference's, 1 and 9 device px
CELLS = ['capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg']

out = {'vitrea': [], 'widths': [], 'synthetic': []}

# ---------------------------------------------------------------- 1. vitrea's own 2x law
print('1. vitrea`s own 2x captures of the W13 bed, widths pinned at what it draws\n')
print(f'   {"cell":<26} {"truth":>7} {"mean":>7} {"min":>7} {"max":>7} {"spread":>7} '
      f'{"level":>7} {"t":>6} {"rms":>8}')
for comp in CELLS:
    span = L.SPAN[comp]
    truth = L.vitrea_k(span)
    for bds in (['checkerboard'], ['checkerboard', 'photo']):
        try:
            sets, tags = L.build_sets(L.web_loader(comp, 2), comp, 2, bds, u_fit_min=2.0)
        except FileNotFoundError:
            continue
        f = L.WindowFit(sets, L.windows_for(span))
        r = f.solve_shared_t(SHARP_V, HEAVY_V, bounds=None, t_min=-9)
        v = W.validated(f.rows(r), span)
        ks = [x['k'] for x in v]
        label = f'{comp} 2x' + (' + photo' if len(bds) > 1 else '')
        rec = dict(label=label, comp=comp, backdrops=bds, truth_k=truth,
                   k_mean=float(np.mean(ks)), k_min=float(min(ks)), k_max=float(max(ks)),
                   spread=float(max(ks) - min(ks)),
                   level_error=float(np.mean(ks) - truth),
                   max_dev_from_mean=float(max(abs(k - np.mean(ks)) for k in ks)),
                   max_dev_from_truth=float(max(abs(k - truth) for k in ks)),
                   t=float(np.mean([t for _, t in r['at']])), rms=r['rms'],
                   n_windows=len(v), u=[x['u_mid'] for x in v], k=[float(x) for x in ks])
        out['vitrea'].append(rec)
        print(f'   {label:<26} {truth:>7.3f} {rec["k_mean"]:>7.3f} {rec["k_min"]:>7.3f} '
              f'{rec["k_max"]:>7.3f} {rec["spread"]:>7.3f} {rec["level_error"]:>+7.3f} '
              f'{rec["t"]:>6.3f} {rec["rms"]:>8.4f}')

md_lg = [r for r in out['vitrea'] if r['comp'] in ('rrect-md', 'rrect-lg')]
print(f'\n   X4 flatness on `rrect-md` and `rrect-lg`: every window within '
      f'{max(r["max_dev_from_mean"] for r in md_lg):.3f} of its cell`s own mean '
      f'(the contract asks 0.05); spread {min(r["spread"] for r in md_lg):.3f}–'
      f'{max(r["spread"] for r in md_lg):.3f}')
print(f'   the same against the TRUE share: within '
      f'{max(r["max_dev_from_truth"] for r in md_lg):.3f} '
      f'(`rrect-md` {max(r["max_dev_from_truth"] for r in md_lg if r["comp"] == "rrect-md"):.3f})')

# ---------------------------------------------------------------- 2. the widths recovered
print('\n2. the widths recovered from the same captures (vitrea draws 1.25 / 10.0 CSS px)\n')
SH_GRID = [('gauss', x) for x in (1.0, 1.25, 1.5, 2.0)]
HV_GRID = [('gauss', x) for x in (6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0)]
for comp in ('rrect-md', 'rrect-lg'):
    span = L.SPAN[comp]
    truth = L.vitrea_k(span)
    sets, _ = L.build_sets(L.web_loader(comp, 2), comp, 2, ['checkerboard', 'photo'],
                           u_fit_min=2.0)
    f = L.WindowFit(sets, L.windows_for(span))
    tab = []
    for sh in SH_GRID:
        for hv in HV_GRID:
            r = f.solve_shared_t(sh, hv, bounds=None, t_min=-9)
            v = W.validated(f.rows(r), span)
            ks = [x['k'] for x in v]
            tab.append(dict(label=f'{comp} 2x + photo', comp=comp, sharp_css=sh[1],
                            heavy_css=hv[1], rms=r['rms'], k_mean=float(np.mean(ks)),
                            spread=float(max(ks) - min(ks)), truth_k=truth,
                            t=float(np.mean([t for _, t in r['at']]))))
    tab.sort(key=lambda z: z['rms'])
    out['widths'].append(tab[0])
    out[f'width_grid_{comp}'] = tab
    print(f'   {comp}: best σ_sharp {tab[0]["sharp_css"]:.2f} / σ_heavy '
          f'{tab[0]["heavy_css"]:.2f} CSS px (rms {tab[0]["rms"]:.4f}, k {tab[0]["k_mean"]:.3f} '
          f'against {truth:.3f}); flatness over the whole grid '
          f'{min(z["spread"] for z in tab):.3f}–{max(z["spread"] for z in tab):.3f}')

# ---------------------------------------------------------------- 3. the synthetic 2x ramp
print('\n3. a synthetic 2x ramp at the reference`s widths (start 0.30, reach 50 CSS px)\n')
START, REACH, T_TRUE, A_TRUE = 0.30, 50.0, 0.42, 0.45


def truth_k(depth):
    return 1.0 - START * np.maximum(0.0, 1.0 - np.asarray(depth, dtype=float) / REACH)


for comp in ('rrect-md', 'rrect-lg'):
    span = L.SPAN[comp]
    sets, _ = L.build_sets(L.probe_loader(comp, 2), comp, 2, W.PRIMARY, u_fit_min=2.0)
    for s in sets:
        s.Y = (L.forward(s, SHARP_R, HEAVY_R, A_TRUE, T_TRUE, truth_k)
               + rng.normal(0, NOISE, (s.n_lines, len(s.u))))
    f = L.WindowFit(sets, L.windows_for(span))
    r = f.solve_shared_t(SHARP_R, HEAVY_R, bounds=(0.0, 1.0), t_min=0.0)
    rows = f.rows(r)
    ro = W.readoff(rows, span)
    v = W.validated(rows, span)
    # the truth, window by window: the model's own k averaged over the window
    tru = [float(np.mean(1 - truth_k(np.linspace(x['u0'], x['u1'], 17)))) for x in v]
    err = [abs(a - b) for a, b in zip(ro['s'], tru)]
    rec = dict(label=f'{comp} 2x synthetic', comp=comp,
               truth_start=tru[0], truth_reach=REACH,
               fit_start=ro['s_first'], fit_reach=ro['reach_px'],
               d_start=ro['s_first'] - tru[0], d_reach=ro['reach_px'] - REACH,
               fit_reach_unclamped=ro['reach_unclamped'],
               d_reach_unclamped=ro['reach_unclamped'] - REACH,
               u_zero=ro['u_zero'], n_clamped=ro['n_clamped'],
               intercept=ro['intercept'], truth_intercept=START,
               max_abs_err=float(max(err)), rms=r['rms'],
               t=float(np.mean([t for _, t in r['at']])), t_truth=T_TRUE,
               u=ro['u'], s=ro['s'], truth_s=tru)
    out['synthetic'].append(rec)
    print(f'   {comp}: start {rec["fit_start"]:.3f} against {rec["truth_start"]:.3f} '
          f'(Δ {rec["d_start"]:+.3f}); reach {rec["fit_reach"]:.1f} against {REACH:.0f} CSS px '
          f'(Δ {rec["d_reach"]:+.1f}); max |s − truth| over the validated windows '
          f'{rec["max_abs_err"]:.3f}; t {rec["t"]:.3f} against {T_TRUE}; '
          f'line intercept at u 0 {rec["intercept"]:.3f} against {START}')
    print(f'      reach through the unclamped windows only {rec["fit_reach_unclamped"]:.1f} '
          f'(Δ {rec["d_reach_unclamped"]:+.1f}); the profile first reaches zero at u '
          f'{rec["u_zero"]}, {rec["n_clamped"]} of {len(v)} validated windows clamped')

W.write_part('g0c-recovery', out)
