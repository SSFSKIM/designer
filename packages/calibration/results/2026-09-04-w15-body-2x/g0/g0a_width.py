"""W15 G0 (a): the base width on the large spans at 2x, fitted jointly with the deep value.

W13 G0 left three defensible answers for the reference's heavy σ at 2x (`g0-ramp.md` §4, §7):
the windowed fit's RMS optimum at **9 device px**, which forces negative sharp shares deep
inside `rrect-ml` and `rrect-lg`; the layer tree's radius law at **16**, which makes every
share physical at a 28% RMS cost; and the deep-interior pitch-axis fit's **11**. The three
were never scored against each other on one surface, and the width was never fitted with the
share held inside [0, 1] — which is the point, because a share that wants to be zero deep
inside and a heavy kernel that is slightly too narrow are the same residual seen twice.

This run sweeps σ_heavy over 8–16 device px (step 1, refined to 0.25 near each cell's
minimum) at the pitch-axis fit's sharp σ (0.5 CSS px = 1 device px, §5.55 §1), pooling
pitches 16 / 32 / 64, and at every width solves the windowed fit twice: **bounded**, the
share held in [0, 1], and **free**, the share unconstrained. What it reports per cell is the
RMS surface over width for both, the width at which the free fit stops asking for a negative
share, and the RMS cost of the bounded solve against the free one at the same width — the
number that says whether the negative shares are the deep value's or the width's.
"""
import numpy as np

import w15lib as W

COARSE = [float(x) for x in range(8, 17)]
SHARP_CHECKS = [('gauss', 0.25), ('gauss', 0.5), ('gauss', 1.0)]

out = {'sweep': {}, 'summary': {}, 'sharp_sensitivity': {}}

print('(a) the base width at 2x, share bounded to [0, 1] against free\n')
for comp in W.COMPS:
    span = W.L.SPAN[comp]
    fit, tags = W.build(comp, 2)
    rows_out = []

    def at(sig_dev, sharp=W.SHARP_2X):
        prep = fit.prepare(sharp, W.heavy(sig_dev))
        rb = fit.solve_shared_t(sharp, W.heavy(sig_dev), bounds=(0.0, 1.0), t_min=0.0, prep=prep)
        rf = fit.solve_shared_t(sharp, W.heavy(sig_dev), bounds=None, t_min=-9, prep=prep)
        ob = W.readoff(fit.rows(rb), span)
        of = W.readoff(fit.rows(rf), span)
        return dict(sigma_device=float(sig_dev), sigma_css=float(sig_dev) / 2,
                    rms_bounded=rb['rms'], rms_free=rf['rms'],
                    t_bounded=float(np.mean([t for _, t in rb['at']])),
                    t_free=float(np.mean([t for _, t in rf['at']])),
                    bounded=ob, free=of)

    for sig in COARSE:
        rows_out.append(at(sig))
        r = rows_out[-1]
        print(f'  {comp:<15} σ {sig:5.2f} dev  rms bounded {r["rms_bounded"]:.5f}  free '
              f'{r["rms_free"]:.5f}  s free {r["free"]["s_first"]:+.3f} → '
              f'{r["free"]["s_last"]:+.3f} (min {r["free"]["s_min"]:+.3f})  s bounded deep '
              f'{r["bounded"]["s_deep"]:+.3f}')

    # refine to 0.25 device px around the free surface's minimum and the bounded one's
    best_f = min(rows_out, key=lambda z: z['rms_free'])['sigma_device']
    best_b = min(rows_out, key=lambda z: z['rms_bounded'])['sigma_device']
    fine = sorted({round(x, 2) for c in (best_f, best_b)
                   for x in np.arange(max(c - 1.0, 6.0), c + 1.01, 0.25)}
                  - {r['sigma_device'] for r in rows_out})
    for sig in fine:
        rows_out.append(at(sig))
    rows_out.sort(key=lambda z: z['sigma_device'])
    out['sweep'][comp] = rows_out

    # the width at which the free fit stops asking for a negative share
    physical = [r['sigma_device'] for r in rows_out if r['free']['s_min'] >= -1e-9]
    sigma_physical = min(physical) if physical else None
    rf_best = min(rows_out, key=lambda z: z['rms_free'])
    rb_best = min(rows_out, key=lambda z: z['rms_bounded'])
    at_phys = next((r for r in rows_out if r['sigma_device'] == sigma_physical), None)
    summ = dict(
        span=span, n_sets=len(fit.sets), tags=tags,
        sigma_free_best=rf_best['sigma_device'], rms_free_best=rf_best['rms_free'],
        sigma_bounded_best=rb_best['sigma_device'], rms_bounded_best=rb_best['rms_bounded'],
        s_min_at_free_best=rf_best['free']['s_min'],
        sigma_physical=sigma_physical,
        rms_free_at_physical=at_phys['rms_free'] if at_phys else None,
        cost_physical=(at_phys['rms_free'] / rf_best['rms_free'] - 1) if at_phys else None,
        # the bounded solve's own cost at the free optimum: how much RMS the physical
        # constraint costs when the width is left where the free fit wants it
        cost_bound_at_free_best=(rf_best['rms_bounded'] / rf_best['rms_free'] - 1),
        s_deep_bounded_at_free_best=rf_best['bounded']['s_deep'],
        s_deep_bounded_at_bounded_best=rb_best['bounded']['s_deep'],
    )
    out['summary'][comp] = summ
    print(f'  → {comp}: free best σ {summ["sigma_free_best"]} dev (rms '
          f'{summ["rms_free_best"]:.5f}, s_min {summ["s_min_at_free_best"]:+.3f}); '
          f'bounded best σ {summ["sigma_bounded_best"]} dev (rms {summ["rms_bounded_best"]:.5f}); '
          f'first physical σ {summ["sigma_physical"]}; cost of it '
          f'{"n/a" if summ["cost_physical"] is None else f"{100 * summ['cost_physical']:.1f}%"}; '
          f'cost of the bound at the free optimum '
          f'{100 * summ["cost_bound_at_free_best"]:.2f}%\n')

# ---- sensitivity to the assumed sharp σ, on the two cells the question is about
print('the same surface at three sharp widths (the pitch-axis fit reads 1 device px)')
for comp in ('rrect-ml', 'rrect-lg'):
    fit, _ = W.build(comp, 2)
    span = W.L.SPAN[comp]
    tab = []
    for sh in SHARP_CHECKS:
        for sig in (8.0, 9.0, 10.0, 11.0, 12.0, 14.0, 16.0):
            prep = fit.prepare(sh, W.heavy(sig))
            rf = fit.solve_shared_t(sh, W.heavy(sig), bounds=None, t_min=-9, prep=prep)
            rb = fit.solve_shared_t(sh, W.heavy(sig), bounds=(0.0, 1.0), t_min=0.0, prep=prep)
            of, ob = W.readoff(fit.rows(rf), span), W.readoff(fit.rows(rb), span)
            tab.append(dict(sharp_css=sh[1], sigma_device=sig, rms_free=rf['rms'],
                            rms_bounded=rb['rms'], s_min_free=of['s_min'],
                            s_deep_bounded=ob['s_deep'], s_first_bounded=ob['s_first']))
    out['sharp_sensitivity'][comp] = tab
    for sh in SHARP_CHECKS:
        sub = [z for z in tab if z['sharp_css'] == sh[1]]
        b = min(sub, key=lambda z: z['rms_free'])
        phys = [z['sigma_device'] for z in sub if z['s_min_free'] >= -1e-9]
        print(f'  {comp} sharp σ {sh[1]} CSS px: free best σ_heavy {b["sigma_device"]:.0f} dev '
              f'(rms {b["rms_free"]:.5f}, s_min {b["s_min_free"]:+.3f}); first physical '
              f'{min(phys) if phys else "none ≤ 16"}')

W.write_part('g0a-width', out)
