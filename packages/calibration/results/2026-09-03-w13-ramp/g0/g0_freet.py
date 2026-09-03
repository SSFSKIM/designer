"""W13 G0, addendum: does the reference's TRANSMISSION ramp, or only its mix?

Every table in `g0-ramp.md` §1 holds the transmission constant with depth and lets one share
per window carry all of the depth dependence. If the reference's transmission itself changes
with depth, part of what those tables call a share ramp is a transmission ramp — and the two
land as different shader terms. `WindowFit.solve_free_t` asks the question directly: two
coefficients per depth window, ordinary least squares, per-line-set intercepts, no constraint
that t is the same at every depth. It is identified only where the pooled pitches separate
the two components' contrast ratios, which is the same condition every §1 reading needs.

Three steps:

1. **The mode on a synthetic field with a known constant t and a known ramped k**, pooled over
   pitches 16 / 32 / 64 — the configuration the reference is read in. t must come back flat.
2. **The mode on vitrea's own `main` captures**, where the material's t is constant with depth
   and its share is one number per span. The canonical bed carries one pitch, so this is the
   weakest of the three checks and is reported with that limit attached.
3. **The reference**, `rrect-md` / `-ml` / `-lg` at both scales, widths as §1.
"""
import numpy as np

import w13lib as L

PRIMARY = ['checkerboard', 'checkerboard-32', 'checkerboard-64']
CELLS = ['rrect-md', 'rrect-ml', 'rrect-lg']


def widths(scale):
    return (('box', 4.0), ('gauss', 9.0)) if scale == 1 else (('gauss', 0.5), ('gauss', 4.5))


def validated(rows, span):
    return [r for r in rows if r['u0'] >= 4 - 1e-9 and r['u1'] <= span / 2 - 4 + 1e-9]


def reach_of(u, s):
    """Where a straight line through (u, s) crosses zero, in CSS px."""
    A = np.stack([np.ones_like(u), u], 1)
    c, *_ = np.linalg.lstsq(A, s, rcond=None)
    return float(-c[0] / c[1]) if c[1] < -1e-6 else float('inf')


out = {'synthetic': {}, 'vitrea': {}, 'reference': {}}

# ---------------------------------------------------------------- 1. the mode on a known field
print('1. the free-t mode on a synthetic field: t constant 0.42, k ramping 0.5 → 1.0,'
      ' pitches 16/32/64')
rng = np.random.default_rng(3)
print(f'   {"cell":<12} {"t first":>8} {"t last":>8} {"t spread":>9} {"max |k − truth|":>16}')
for comp in CELLS:
    span = L.SPAN[comp]
    kfun = lambda d, s=span: 1.0 - 0.5 * np.maximum(0.0, 1 - d / (s / 2))  # noqa: E731
    sets, _ = L.build_sets(L.probe_loader(comp, 1), comp, 1, PRIMARY, u_fit_min=2.0)
    for st in sets:
        st.Y = (L.forward(st, ('gauss', 1.25), ('gauss', 10.0), 0.45, 0.42, kfun)
                + rng.normal(0, 0.002, (st.n_lines, len(st.u))))
    f = L.WindowFit(sets, L.windows_for(span))
    r = f.solve_free_t(('gauss', 1.25), ('gauss', 10.0))
    v = validated(f.rows(r), span)
    t = np.array([x['t'] for x in v])
    err = max(abs(x['k'] - float(np.mean(kfun(np.linspace(x['u0'], x['u1'], 17))))) for x in v)
    out['synthetic'][f'{comp}@1x'] = dict(t=list(t), t_first=float(t[0]), t_last=float(t[-1]),
                                          t_spread=float(t.max() - t.min()),
                                          max_k_error=float(err), rms=r['rms'])
    print(f'   {comp:<12} {t[0]:>8.3f} {t[-1]:>8.3f} {t.max() - t.min():>9.3f} {err:>16.4f}')

# ---------------------------------------------------------------- 2. the mode on vitrea
print('\n2. the free-t mode on vitrea `main` (the canonical bed carries pitch 16 only;'
      ' `photo` pooled where it exists)')
print(f'   {"cell":<16} {"truth k":>8} {"t first":>8} {"t last":>8} {"t spread":>9} '
      f'{"k first":>8} {"k last":>8} {"k spread":>9}')
for scale in (1, 2):
    for comp in CELLS:
        span = L.SPAN[comp]
        bds = ['checkerboard', 'photo']
        try:
            sets, _ = L.build_sets(L.web_loader(comp, scale), comp, scale, bds, u_fit_min=2.0)
        except FileNotFoundError:
            bds = ['checkerboard']
            sets, _ = L.build_sets(L.web_loader(comp, scale), comp, scale, bds, u_fit_min=2.0)
        f = L.WindowFit(sets, L.windows_for(span))
        r = f.solve_free_t(('gauss', 1.25), ('gauss', 10.0))
        v = validated(f.rows(r), span)
        t = np.array([x['t'] for x in v])
        k = np.array([x['k'] for x in v])
        out['vitrea'][f'{comp}@{scale}x'] = dict(
            backdrops=bds, truth_k=L.vitrea_k(span), t=list(t), k=list(k), rms=r['rms'],
            t_first=float(t[0]), t_last=float(t[-1]), t_spread=float(t.max() - t.min()),
            k_spread=float(k.max() - k.min()))
        print(f'   {comp}@{scale}x{"":<6} {L.vitrea_k(span):>8.3f} {t[0]:>8.3f} {t[-1]:>8.3f} '
              f'{t.max() - t.min():>9.3f} {k[0]:>8.3f} {k[-1]:>8.3f} {k.max() - k.min():>9.3f}')

# ---------------------------------------------------------------- 3. the reference
print('\n3. the free-t mode on the reference, pitches 16/32/64, the widths of §1')
print(f'   {"cell":<14} {"t first":>8} {"t last":>8} {"Δt":>7} {"t/t̄":>7} | '
      f'{"s fixed-t first→last":>22} {"s free-t first→last":>22} {"reach fixed / free":>20}')
for scale in (1, 2):
    sh, hv = widths(scale)
    for comp in CELLS:
        span = L.SPAN[comp]
        sets, _ = L.build_sets(L.probe_loader(comp, scale), comp, scale, PRIMARY, u_fit_min=2.0)
        f = L.WindowFit(sets, L.windows_for(span))
        prep = f.prepare(sh, hv)
        rf = f.solve_free_t(sh, hv, prep=prep)
        rs = f.solve_shared_t(sh, hv, prep=prep, bounds=None, t_min=-9)
        vf, vs = validated(f.rows(rf), span), validated(f.rows(rs), span)
        u = np.array([x['u_mid'] for x in vf])
        t = np.array([x['t'] for x in vf])
        s_free = np.array([1 - x['k'] for x in vf])
        s_fix = np.array([1 - x['k'] for x in vs])
        rec = dict(u=list(u), t=list(t), s_free=list(s_free), s_fixed=list(s_fix),
                   t_first=float(t[0]), t_last=float(t[-1]),
                   t_change=float(t[-1] - t[0]), t_mean=float(t.mean()),
                   t_rel_change=float((t[-1] - t[0]) / t.mean()),
                   s_free_first=float(s_free[0]), s_free_last=float(s_free[-1]),
                   s_fixed_first=float(s_fix[0]), s_fixed_last=float(s_fix[-1]),
                   reach_fixed=reach_of(u, s_fix), reach_free=reach_of(u, s_free),
                   rms_free=rf['rms'], rms_fixed=rs['rms'],
                   t_shared=float(np.mean([x for _, x in rs['at']])))
        out['reference'][f'{comp}@{scale}x'] = rec
        print(f'   {comp}@{scale}x{"":<4} {t[0]:>8.3f} {t[-1]:>8.3f} {rec["t_change"]:>+7.3f} '
              f'{rec["t_rel_change"]:>+7.1%} | {s_fix[0]:>10.3f} →{s_fix[-1]:>10.3f} '
              f'{s_free[0]:>10.3f} →{s_free[-1]:>10.3f} '
              f'{rec["reach_fixed"]:>9.0f} /{rec["reach_free"]:>9.0f}')

L.write_part('g0-free-t', out)
