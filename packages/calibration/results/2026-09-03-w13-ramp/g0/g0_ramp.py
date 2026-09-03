"""W13 G0, step 3: the reference's sharp share by depth, on both probes.

k(u) per 4 CSS px depth window with the lens fixed at `main`'s landed law, on the committed
1x (W9) and 2x (W12) probe beds, per span and scale. The primary reading pools pitches 16 /
32 / 64 — the configuration the estimator was validated in (`g0-validation.json`); pitch 8
and pitch 4 are run separately as checks, because at 2x the reference passes almost nothing
at pitch 8 and what it does pass is anti-correlated with the plate (claims §5.55 §3).

The widths are the reference's own as §5.55 §1 measured them (1x: a 4 CSS px box sharp core,
σ 9 device px base; 2x: σ 0.5 CSS px sharp, σ 9 device px base) and, as a sensitivity check,
free on a coarse grid.

Two hypotheses are scored on the measured windows:
  H1  s(u) = 0.5 · max(0, 1 − u/(span/2))            — the layer tree's opacity ramp
  H2  s(u) = s0 · max(0, 1 − u/(ρ·span/2)) + floor   — a ramp with a free start, reach, floor
"""
import numpy as np
from scipy.optimize import least_squares

import w13lib as L

COMPS = ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg']
PRIMARY = ['checkerboard', 'checkerboard-32', 'checkerboard-64']
CHECKS = {'pitch-8': ['checkerboard-8'], 'pitch-4': ['checkerboard-4'],
          'four-pitch': ['checkerboard-8', 'checkerboard', 'checkerboard-32', 'checkerboard-64']}


def widths(scale):
    """§5.55 §1's reading of the reference's own kernel, in CSS px at this scale."""
    return (('box', 4.0), ('gauss', 9.0)) if scale == 1 else (('gauss', 0.5), ('gauss', 4.5))


def validated(rows, span):
    return [r for r in rows if r['u0'] >= 4 - 1e-9 and r['u1'] <= span / 2 - 4 + 1e-9]


def read(comp, scale, bds, sharp=None, heavy=None, edges=L.EDGES):
    span = L.SPAN[comp]
    sh, hv = widths(scale)
    sh, hv = sharp or sh, heavy or hv
    sets, tags = L.build_sets(L.probe_loader(comp, scale), comp, scale, bds,
                              edges=edges, u_fit_min=2.0)
    if not sets:
        return None
    f = L.WindowFit(sets, L.windows_for(span))
    r = f.solve_shared_t(sh, hv, bounds=None, t_min=-9)
    rows = f.rows(r)
    for i, row in enumerate(rows):
        row['rms'] = float(r['rms_by_window'][i])
        row['n'] = float(r['n_by_window'][i])
    return dict(comp=comp, scale=scale, backdrops=bds, sharp=list(sh), heavy=list(hv),
                rms=r['rms'], t=[float(t) for _, t in r['at']], tags=tags, rows=rows)


def readoff(rows, span):
    """The start, the reach, the floor and the linearity of s(u) over the validated windows."""
    v = validated(rows, span)
    if len(v) < 3:
        return None
    u = np.array([x['u_mid'] for x in v])
    s = np.array([1 - x['k'] for x in v])
    A = np.stack([np.ones_like(u), u], 1)
    c, *_ = np.linalg.lstsq(A, s, rcond=None)
    resid = s - A @ c
    ss = float(np.sum((s - s.mean()) ** 2))
    # the reach: where the straight line through the measured windows crosses zero
    reach = float(-c[0] / c[1]) if c[1] < -1e-6 else float('inf')
    return dict(s_first=float(s[0]), u_first=float(u[0]), s_peak=float(s.max()),
                u_peak=float(u[np.argmax(s)]), s_last=float(s[-1]), u_last=float(u[-1]),
                slope=float(c[1]), intercept=float(c[0]),
                linear_r2=float(1 - np.sum(resid ** 2) / ss) if ss > 0 else float('nan'),
                reach_px=reach, reach_frac=reach / (span / 2) if np.isfinite(reach) else None)


def score_h1(rows, span):
    v = validated(rows, span)
    u = np.array([x['u_mid'] for x in v])
    s = np.array([1 - x['k'] for x in v])
    return float(np.sqrt(np.mean((s - L.h1_sharp(u, span)) ** 2)))


def fit_h2(pack, per_span):
    """Fit (s0, ρ, floor) on the pooled windows; `per_span` fits one triple per span."""
    groups = {}
    for key, rows, span in pack:
        groups.setdefault(key if per_span else '_all', []).append((rows, span))
    out = {}
    for gk, items in groups.items():
        us, ss, sp = [], [], []
        for rows, span in items:
            v = validated(rows, span)
            us += [x['u_mid'] for x in v]
            ss += [1 - x['k'] for x in v]
            sp += [span] * len(v)
        u, s, span_a = np.array(us), np.array(ss), np.array(sp)

        def res(p):
            return L.h2_sharp(u, span_a, p[0], p[1], p[2]) - s
        best = None
        for p0 in ((0.5, 1.0, 0.0), (0.6, 0.6, 0.1), (0.5, 1.5, 0.0), (0.4, 0.8, 0.2)):
            r = least_squares(res, p0, bounds=([0, 0.05, -0.2], [1.5, 4.0, 0.6]))
            v = float(np.sqrt(np.mean(res(r.x) ** 2)))
            if best is None or v < best[0]:
                best = (v, r.x)
        out[gk] = dict(rms=best[0], s0=float(best[1][0]), rho=float(best[1][1]),
                       floor=float(best[1][2]), n=len(u))
    return out


out = {'primary': {}, 'checks': {}, 'readoff': {}, 'h1': {}, 'h2': {}, 'width_grid': {}}
print('the reference, pitches 16/32/64, the widths §5.55 §1 measured\n')
for scale in (1, 2):
    print(f'--- {scale}x   sharp {widths(scale)[0]}   heavy {widths(scale)[1]}')
    for comp in COMPS:
        span = L.SPAN[comp]
        rec = read(comp, scale, PRIMARY)
        out['primary'][f'{comp}@{scale}x'] = rec
        ro = readoff(rec['rows'], span)
        out['readoff'][f'{comp}@{scale}x'] = ro
        out['h1'][f'{comp}@{scale}x'] = score_h1(rec['rows'], span)
        print(f'  {comp:<15} rms {rec["rms"]:.5f}  t {np.mean(rec["t"]):.3f}')
        print('     s(u):', ' '.join(f'{x["u_mid"]:.0f}:{1 - x["k"]:.3f}' for x in rec['rows']))
        if ro:
            print(f'     start {ro["s_first"]:.3f} at u {ro["u_first"]:.0f}; peak '
                  f'{ro["s_peak"]:.3f} at u {ro["u_peak"]:.0f}; last {ro["s_last"]:.3f} at u '
                  f'{ro["u_last"]:.0f}; linear R² {ro["linear_r2"]:.3f}; reach '
                  f'{ro["reach_px"]:.1f} px = {ro["reach_frac"]:.2f}·span/2; '
                  f'H1 rms {out["h1"][f"{comp}@{scale}x"]:.3f}')

# ---- the checks: the other pitches
print('\nchecks on the other pitches (the primary reading is 16/32/64)')
for name, bds in CHECKS.items():
    for scale in (1, 2):
        for comp in ('rrect-md', 'rrect-lg'):
            rec = read(comp, scale, bds)
            if rec is None:
                continue
            out['checks'][f'{name}|{comp}@{scale}x'] = rec
            v = validated(rec['rows'], L.SPAN[comp])
            print(f'  {name:<11} {comp}@{scale}x  t {np.mean(rec["t"]):+.3f}  rms {rec["rms"]:.5f}'
                  f'  s {v[0]["s"]:+.3f} → {v[-1]["s"]:+.3f}')

# ---- H2, shared over spans per scale and per span
for scale in (1, 2):
    pack = [(f'{c}@{scale}x', out['primary'][f'{c}@{scale}x']['rows'], L.SPAN[c])
            for c in COMPS if out['primary'][f'{c}@{scale}x'] is not None
            and len(validated(out['primary'][f'{c}@{scale}x']['rows'], L.SPAN[c])) >= 3]
    out['h2'][f'shared@{scale}x'] = fit_h2(pack, per_span=False)['_all']
    out['h2'][f'per-span@{scale}x'] = fit_h2(pack, per_span=True)
print('\nH2, s = s0·max(0, 1 − u/(ρ·span/2)) + floor')
for scale in (1, 2):
    h = out['h2'][f'shared@{scale}x']
    print(f'  {scale}x shared over spans: s0 {h["s0"]:.3f}  ρ {h["rho"]:.3f}  floor '
          f'{h["floor"]:.3f}  rms {h["rms"]:.4f}')
    for k, v in out['h2'][f'per-span@{scale}x'].items():
        print(f'      {k:<18} s0 {v["s0"]:.3f}  ρ {v["rho"]:.3f}  floor {v["floor"]:.3f}  '
              f'rms {v["rms"]:.4f}   H1 rms {out["h1"][k]:.4f}')

# ---- sensitivity to the assumed widths
print('\nthe same reading with the widths free on a coarse grid')
SH = {1: [('box', 4.0), ('gauss', 0.75), ('gauss', 1.0), ('gauss', 1.5)],
      2: [('gauss', 0.25), ('gauss', 0.5), ('gauss', 1.0), ('box', 2.0)]}
HV = {1: [('gauss', x) for x in (6.0, 7.5, 9.0, 11.0, 13.0)],
      2: [('gauss', x) for x in (3.0, 4.5, 6.0, 7.5, 9.0)]}
for scale in (1, 2):
    for comp in ('rrect-md', 'rrect-lg'):
        span = L.SPAN[comp]
        tab = []
        for sh in SH[scale]:
            for hv in HV[scale]:
                rec = read(comp, scale, PRIMARY, sharp=sh, heavy=hv)
                v = validated(rec['rows'], span)
                tab.append(dict(rms=rec['rms'], sharp=list(sh), heavy=list(hv),
                                s=[float(1 - x['k']) for x in v],
                                u=[float(x['u_mid']) for x in v],
                                h1=score_h1(rec['rows'], span)))
        tab.sort(key=lambda z: z['rms'])
        out['width_grid'][f'{comp}@{scale}x'] = tab
        b = tab[0]
        print(f'  {comp}@{scale}x best {b["sharp"]} / {b["heavy"]} rms {b["rms"]:.5f}  '
              f's {b["s"][0]:.3f} → {b["s"][-1]:.3f}')
        top = tab[:5]
        print('     over the five best grid points: s(first) '
              f'{min(z["s"][0] for z in top):.3f}–{max(z["s"][0] for z in top):.3f}, '
              f's(last) {min(z["s"][-1] for z in top):.3f}–{max(z["s"][-1] for z in top):.3f}')

# ---- the heavy width per span: one number against the layer tree's radius law
# §5.55 §1 fitted one base width for spans ≥ 96 (σ 9 device px). The layer tree's own
# `inputBlurRadius` is a function of the span — max(4/3, (span + 8)/42) buffer px, one buffer
# px being 4 device px — so 9.9 / 13.0 / 16.0 CSS px at 1x on md / ml / lg. The two readings
# cannot both be right; this asks the windowed instrument which width the pixels want, with
# the ramp free underneath it.
print('\nthe heavy width per span, against the layer tree`s radius law')
hw = {}
for scale in (1, 2):
    for comp in ('rrect-md', 'rrect-ml', 'rrect-lg'):
        span = L.SPAN[comp]
        radius_css = 4 * L.g3lib.blur_radius_buffer_px(span) / scale
        cands = [('one-number (§5.55 §1)', 9.0 / scale)]
        cands += [(f'radius law × {f}', radius_css * f) for f in (0.5, 0.75, 1.0)]
        cands += [('grid', x) for x in ((11.0, 13.0, 16.0, 20.0) if scale == 1
                                        else (6.0, 8.0, 10.0, 12.0))]
        tab = []
        for name, sig in cands:
            rec = read(comp, scale, PRIMARY, heavy=('gauss', sig))
            v = validated(rec['rows'], span)
            tab.append(dict(name=name, sigma_heavy=sig, rms=rec['rms'],
                            s_first=float(1 - v[0]['k']), s_last=float(1 - v[-1]['k']),
                            s_min=float(min(1 - x['k'] for x in v))))
        tab.sort(key=lambda z: z['rms'])
        hw[f'{comp}@{scale}x'] = dict(radius_law_css=radius_css, table=tab)
        print(f'  {comp}@{scale}x  radius law {radius_css:.2f} CSS px')
        for b in tab[:4]:
            print(f'     rms {b["rms"]:.5f}  σ_heavy {b["sigma_heavy"]:5.2f}  '
                  f'{b["name"]:<22} s {b["s_first"]:+.3f} → {b["s_last"]:+.3f} '
                  f'(min {b["s_min"]:+.3f})')
out['heavy_width'] = hw

# ---- the same reading with k held inside [0, 1], where the free one leaves the mix
print('\nthe primary reading with k bounded to [0, 1] (a mix cannot have a negative weight)')
bnd = {}
for scale in (1, 2):
    for comp in COMPS:
        span = L.SPAN[comp]
        sh, hv = widths(scale)
        sets, _ = L.build_sets(L.probe_loader(comp, scale), comp, scale, PRIMARY, u_fit_min=2.0)
        f = L.WindowFit(sets, L.windows_for(span))
        r = f.solve_shared_t(sh, hv, bounds=(0.0, 1.0), t_min=0.0)
        v = validated(f.rows(r), span)
        free = out['primary'][f'{comp}@{scale}x']['rms']
        bnd[f'{comp}@{scale}x'] = dict(rms=r['rms'], rms_free=free,
                                       s=[float(1 - x['k']) for x in v],
                                       u=[float(x['u_mid']) for x in v])
        print(f'  {comp}@{scale}x rms {r["rms"]:.5f} (free {free:.5f})  s '
              f'{1 - v[0]["k"]:+.3f} → {1 - v[-1]["k"]:+.3f}')
out['bounded'] = bnd

L.write_part('g0-ramp', out)
