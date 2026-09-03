"""W13 G0, contract X4: the windowed instrument validated before any reference reading.

Three checks, in the order they have to pass:

1. The analytic plate equals the committed raster along every line the instrument uses.
2. The estimator recovers a KNOWN k(u) — flat and ramped — from a synthetic field built by
   the same forward model, in each of the configurations the readings actually use: one
   pitch (what vitrea's canonical bed offers), one pitch plus `photo`, and the three- and
   four-pitch pools the reference is read on.
3. The instrument recovers `main`'s own uniform heavy share from vitrea's own canonical
   captures at both scales, with the widths pinned at the profile's (σ_sharp 1.25,
   σ_heavy 10 CSS px) and with the widths free on a coarse grid.

Run from this directory with the analysis venv.
"""
import numpy as np

import w13lib as L

rng = np.random.default_rng(0)
NOISE = 0.002
SHARP_V, HEAVY_V = ('gauss', 1.25), ('gauss', 10.0)
out = {}


def validated(rows, span):
    return [r for r in rows if r['u0'] >= 4 - 1e-9 and r['u1'] <= span / 2 - 4 + 1e-9]


# ---------------------------------------------------------------- 1. the plate self-test
pst = {}
for scale in (1, 2):
    for comp in ('rrect-md', 'rrect-ml', 'rrect-lg', 'capsule-button', 'rrect-sm'):
        for pitch in (8, 16, 32, 64):
            for edge in L.EDGES:
                pst[f'{comp}@{scale}x-p{pitch}-{edge}'] = L.plate_self_test(comp, pitch, scale, edge)
ok = {k: v for k, v in pst.items() if v == v}
out['plate_self_test'] = dict(max=max(ok.values()), n=len(ok), empty=len(pst) - len(ok))
print(f'1. plate self-test over {len(ok)} line sets: max |analytic − raster| = {max(ok.values()):.8f}'
      f'  ({len(pst) - len(ok)} (component, pitch, edge) combinations have no straight-edge line)')

# ---------------------------------------------------------------- 2. the estimator on synthetic
CONFIGS = {
    'one-pitch (vitrea canonical)': ['checkerboard'],
    'one-pitch + photo': ['checkerboard', 'photo'],
    'three pitches (the reference reading)': ['checkerboard', 'checkerboard-32', 'checkerboard-64'],
    'four pitches': ['checkerboard-8', 'checkerboard', 'checkerboard-32', 'checkerboard-64'],
}
syn = {}
print('\n2. the estimator on a synthetic field with a known k(u) '
      f'(noise σ {NOISE} in linear luminance)')
print(f'   {"configuration":<40} {"cell":<14} {"flat":>10} {"ramp":>10}')
for comp in ('rrect-md', 'rrect-lg'):
    span = L.SPAN[comp]
    truths = {
        'flat': lambda d, s=span: 0 * d + L.vitrea_k(s),
        'ramp': lambda d, s=span: 1.0 - 0.5 * np.maximum(0.0, 1 - d / (s / 2)),
    }
    for name, bds in CONFIGS.items():
        row = {}
        for tname, kfun in truths.items():
            sets, _ = L.build_sets(L.probe_loader(comp, 1), comp, 1, bds, u_fit_min=2.0)
            for s in sets:
                s.Y = (L.forward(s, SHARP_V, HEAVY_V, 0.45, 0.42, kfun)
                       + rng.normal(0, NOISE, (s.n_lines, len(s.u))))
            f = L.WindowFit(sets, L.windows_for(span))
            r = f.solve_shared_t(SHARP_V, HEAVY_V, bounds=None, t_min=-9)
            err = [abs(x['k'] - float(np.mean(kfun(np.linspace(x['u0'], x['u1'], 17)))))
                   for x in validated(f.rows(r), span)]
            row[tname] = dict(max_abs_k_error=float(max(err)), rms=r['rms'],
                              t=float(r['at'][0][1]))
        syn[f'{comp}@1x|{name}'] = row
        print(f'   {name:<40} {comp:<14} {row["flat"]["max_abs_k_error"]:>10.4f} '
              f'{row["ramp"]["max_abs_k_error"]:>10.4f}')
out['synthetic'] = syn

# ---------------------------------------------------------------- 3. vitrea's own captures
print('\n3. the instrument on vitrea`s canonical GPU captures (`main`, the W12 close)')
print(f'   {"cell":<18} {"truth k":>8} {"k mean":>8} {"k min":>7} {"k max":>7} '
      f'{"spread":>7} {"level err":>10} {"t":>6} {"rms":>8}')
vit = {}
for scale in (1, 2):
    for comp in ('capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg'):
        span = L.SPAN[comp]
        truth = L.vitrea_k(span)
        for bds in (['checkerboard'], ['checkerboard', 'photo']):
            try:
                sets, tags = L.build_sets(L.web_loader(comp, scale), comp, scale, bds,
                                          u_fit_min=2.0)
            except FileNotFoundError:
                continue
            f = L.WindowFit(sets, L.windows_for(span))
            r = f.solve_shared_t(SHARP_V, HEAVY_V, bounds=None, t_min=-9)
            rows = f.rows(r)
            vr = validated(rows, span)
            ks = [x['k'] for x in vr]
            rec = dict(truth=truth, k_mean=float(np.mean(ks)), k_min=float(min(ks)),
                       k_max=float(max(ks)), spread=float(max(ks) - min(ks)),
                       level_error=float(np.mean(ks) - truth), t=float(r['at'][0][1]),
                       rms=r['rms'], n_windows=len(vr),
                       rows=[dict(u_mid=x['u_mid'], k=x['k'], se_k=x['se_k']) for x in rows],
                       rms_by_window=list(r['rms_by_window']))
            # the same fit run on each edge alone: the honest systematic spread
            per_edge = []
            for e in L.EDGES:
                se_, _ = L.build_sets(L.web_loader(comp, scale), comp, scale, bds,
                                      edges=(e,), u_fit_min=2.0)
                if not se_:
                    continue
                fe = L.WindowFit(se_, L.windows_for(span))
                re_ = fe.solve_shared_t(SHARP_V, HEAVY_V, bounds=None, t_min=-9)
                per_edge.append([float(x['k']) for x in validated(fe.rows(re_), span)])
            rec['per_edge_k'] = per_edge
            rec['per_edge_sd'] = [float(np.std([e[i] for e in per_edge]))
                                  for i in range(len(vr))]
            vit[f'{comp}@{scale}x|{"+".join(bds)}'] = rec
            print(f'   {comp}@{scale}x {"+photo" if len(bds) > 1 else "      ":<7} '
                  f'{truth:>8.3f} {rec["k_mean"]:>8.3f} {rec["k_min"]:>7.3f} '
                  f'{rec["k_max"]:>7.3f} {rec["spread"]:>7.3f} {rec["level_error"]:>10.3f} '
                  f'{rec["t"]:>6.3f} {rec["rms"]:>8.5f}')
out['vitrea'] = vit

# ---------------------------------------------------------------- 3b. the widths free
print('\n3b. the same with the two widths free on a coarse grid (the mip tap is not a Gaussian)')
grid = {}
SH = [('gauss', x) for x in (0.75, 1.0, 1.25, 1.5, 2.0)]
HV = [('gauss', x) for x in (6.0, 8.0, 10.0, 12.0, 14.0, 18.0)]
for scale in (1, 2):
    for comp in ('rrect-md', 'rrect-lg'):
        span = L.SPAN[comp]
        bds = ['checkerboard', 'photo']
        sets, _ = L.build_sets(L.web_loader(comp, scale), comp, scale, bds, u_fit_min=2.0)
        f = L.WindowFit(sets, L.windows_for(span))
        tab = []
        for sh in SH:
            for hv in HV:
                r = f.solve_shared_t(sh, hv, bounds=None, t_min=-9)
                ks = [x['k'] for x in validated(f.rows(r), span)]
                tab.append(dict(rms=r['rms'], sigma_sharp=sh[1], sigma_heavy=hv[1],
                                k_mean=float(np.mean(ks)), spread=float(max(ks) - min(ks)),
                                t=float(r['at'][0][1])))
        tab.sort(key=lambda z: z['rms'])
        grid[f'{comp}@{scale}x'] = tab
        b = tab[0]
        print(f'   {comp}@{scale}x best σ_sharp {b["sigma_sharp"]:.2f} σ_heavy '
              f'{b["sigma_heavy"]:.1f}  k mean {b["k_mean"]:.3f} spread {b["spread"]:.3f} '
              f'(truth {L.vitrea_k(span):.3f})  rms {b["rms"]:.5f}')
        print(f'      spread over the whole grid: k mean '
              f'{min(z["k_mean"] for z in tab):.3f}–{max(z["k_mean"] for z in tab):.3f}, '
              f'flatness {min(z["spread"] for z in tab):.3f}–{max(z["spread"] for z in tab):.3f}')
out['vitrea_width_grid'] = grid

L.write_part('g0-validation', out)
