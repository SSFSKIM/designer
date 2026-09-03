"""W15 G0: render every `parts/*.json` this spike wrote as the tables the document quotes.

One place where a number is formatted, so the document and the JSON cannot drift.
"""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))


def part(name):
    with open(f'{OUT}/parts/{name}.json') as f:
        return json.load(f)


lines = []


def w(s=''):
    lines.append(s)


# ---------------------------------------------------------------- (a) the width surface
a = part('g0a-width')
w('# (a) The RMS surface over the base width at 2x, share bounded to [0, 1] and free')
w()
w('σ_heavy in device px; the sharp term is the pitch-axis fit\'s σ 1 device px (§5.55 §1);')
w('pitches 16 / 32 / 64 pooled; RMS in linear luminance over every fitted pixel.')
w('`s_min` is the smallest sharp share over the validated windows (4 ≤ u ≤ span/2 − 4) in the')
w('FREE solve — negative means the model is asking for a sharpening weight. `s_deep` is the')
w('mean share over the three deepest validated windows in the BOUNDED solve.')
w()
for comp, rows in a['sweep'].items():
    w(f'## {comp} (span {a["summary"][comp]["span"]}), {a["summary"][comp]["n_sets"]} line sets')
    w()
    w('| σ_heavy dev | σ_heavy CSS | RMS bounded | RMS free | s first (free) | s last (free) '
      '| s_min (free) | s_deep (bounded) | t (bounded) |')
    w('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    for r in rows:
        w(f'| {r["sigma_device"]:.2f} | {r["sigma_css"]:.3f} | {r["rms_bounded"]:.5f} | '
          f'{r["rms_free"]:.5f} | {r["free"]["s_first"]:+.3f} | {r["free"]["s_last"]:+.3f} | '
          f'{r["free"]["s_min"]:+.3f} | {r["bounded"]["s_deep"]:+.3f} | {r["t_bounded"]:.3f} |')
    w()
w('## Summary')
w()
w('| cell | free-solve best σ (RMS) | s_min there | **bounded best σ (RMS)** | s_deep there '
  '| first σ with no negative share | its RMS cost vs the free best | cost of the bound at the '
  'free best |')
w('| --- | --- | --- | --- | --- | --- | --- | --- |')
for comp, s in a['summary'].items():
    cp = 'n/a' if s['cost_physical'] is None else f'{100 * s["cost_physical"]:+.1f}%'
    w(f'| `{comp}` | {s["sigma_free_best"]:.2f} ({s["rms_free_best"]:.5f}) | '
      f'{s["s_min_at_free_best"]:+.3f} | **{s["sigma_bounded_best"]:.2f}** '
      f'({s["rms_bounded_best"]:.5f}) | {s["s_deep_bounded_at_bounded_best"]:+.3f} | '
      f'{"—" if s["sigma_physical"] is None else f"{s['sigma_physical']:.2f}"} | {cp} | '
      f'{100 * s["cost_bound_at_free_best"]:+.2f}% |')
w()
w('## Sensitivity to the assumed sharp σ')
w()
w('| cell | sharp σ CSS px | free best σ_heavy dev | RMS | s_min there | bounded best σ_heavy '
  '| RMS | s_deep there |')
w('| --- | --- | --- | --- | --- | --- | --- | --- |')
for comp, tab in a['sharp_sensitivity'].items():
    for sh in sorted({z['sharp_css'] for z in tab}):
        sub = [z for z in tab if z['sharp_css'] == sh]
        bf = min(sub, key=lambda z: z['rms_free'])
        bb = min(sub, key=lambda z: z['rms_bounded'])
        w(f'| `{comp}` | {sh:.2f} | {bf["sigma_device"]:.0f} | {bf["rms_free"]:.5f} | '
          f'{bf["s_min_free"]:+.3f} | {bb["sigma_device"]:.0f} | {bb["rms_bounded"]:.5f} | '
          f'{bb["s_deep_bounded"]:+.3f} |')
w()

# ---------------------------------------------------------------- (b) the share by depth
if os.path.exists(f'{OUT}/parts/g0b-depth.json'):
    b = part('g0b-depth')
    w('# (b) The sharp share by depth at 2x at the settled widths, beside W13 G0\'s σ 9 reading')
    w()
    for width_key, block in b['tables'].items():
        w(f'## {width_key}')
        w()
        us = sorted({float(u) for rec in block.values() for u in rec['u']})
        w('| cell | RMS | t | ' + ' | '.join(f'{u:.0f}' for u in us) + ' |')
        w('| --- | --- | --- | ' + ' | '.join('---' for _ in us) + ' |')
        for comp, rec in block.items():
            cells = {round(float(u), 1): s for u, s in zip(rec['u'], rec['s'])}
            w(f'| `{comp}` | {rec["rms"]:.4f} | {rec["t"]:.3f} | '
              + ' | '.join(f'{cells[round(u, 1)]:+.3f}' if round(u, 1) in cells else ''
                           for u in us) + ' |')
        w()
    w('## Read-off: the deep value, the start and the reach')
    w()
    w('`reach` is W13 G0\'s statistic (a straight line through every validated window);')
    w('`reach*` fits the line through the windows before the first that arrives at zero,')
    w('which (c) measures to be the unbiased one where the profile bottoms out inside the')
    w('half-span. `zero at` is where the profile first reaches zero.')
    w()
    w('| cell | width, device px | start s (u) | deep value s | reach | **reach\\*** | zero at '
      '| reach ÷ (span/2) | W13 G0 at σ 9, share free: start / last / reach |')
    w('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    for row in b['readoff']:
        w(f'| `{row["comp"]}` | {row["sigma_device"]:.2f} | {row["s_first"]:+.3f} '
          f'({row["u_first"]:.0f}) | {row["s_deep"]:+.3f} | '
          f'{"—" if row["reach_px"] is None else f"{row['reach_px']:.0f}"} | '
          f'{"—" if row["reach_unclamped"] is None else f"**{row['reach_unclamped']:.0f}**"} | '
          f'{"—" if row["u_zero"] is None else f"{row['u_zero']:.0f}"} | '
          f'{"—" if row["reach_frac"] is None else f"{row['reach_frac']:.2f}"} | '
          f'{row["w13"]} |')
    w()
    w('The pooled bounded surface over the width, each cell\'s RMS normalised by its own')
    w('minimum (the mean over the five spans, and over the three large ones):')
    w()
    w('| σ_heavy, device px | ' + ' | '.join(f'{s:.1f}' for s in b['grid']) + ' |')
    w('| --- | ' + ' | '.join('---' for _ in b['grid']) + ' |')
    w('| five spans | ' + ' | '.join(f'{b["normalised_surface"][str(s)]:.3f}'
                                     for s in b['grid']) + ' |')
    w('| the three large spans | ' + ' | '.join(f'{b["normalised_surface_large"][str(s)]:.3f}'
                                                for s in b['grid']) + ' |')
    w()

# ---------------------------------------------------------------- (c) the recovery
if os.path.exists(f'{OUT}/parts/g0c-recovery.json'):
    c = part('g0c-recovery')
    w('# (c) Contract X4 — what the instrument recovers from two known 2x laws')
    w()
    w('## vitrea\'s own 2x captures of the W13 bed (uniform share per span, CSS-px widths)')
    w()
    w('| cell | truth k | k mean | k min | k max | **spread** | level error | fitted t | RMS |')
    w('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    for r in c['vitrea']:
        w(f'| `{r["label"]}` | {r["truth_k"]:.3f} | {r["k_mean"]:.3f} | {r["k_min"]:.3f} | '
          f'{r["k_max"]:.3f} | **{r["spread"]:.3f}** | {r["level_error"]:+.3f} | '
          f'{r["t"]:.3f} | {r["rms"]:.4f} |')
    w()
    w('## The widths recovered from the same captures (vitrea draws σ_sharp 1.25 / σ_heavy 10 '
      'CSS px)')
    w()
    w('| cell | best σ_sharp CSS | best σ_heavy CSS | ratio to the drawn 10 | k mean there '
      '| spread | RMS |')
    w('| --- | --- | --- | --- | --- | --- | --- |')
    for r in c['widths']:
        w(f'| `{r["label"]}` | {r["sharp_css"]:.2f} | {r["heavy_css"]:.2f} | '
          f'{r["heavy_css"] / 10:.2f}× | {r["k_mean"]:.3f} | {r["spread"]:.3f} | '
          f'{r["rms"]:.4f} |')
    w()
    w('## The synthetic 2x ramp (σ_sharp 1 / σ_heavy 9 device px; s 0.30 at the contour '
      'falling linearly to 0 over 50 CSS px)')
    w()
    w('| cell | truth start / reach | recovered start / reach | Δ start | Δ reach, CSS px '
      '| Δ reach\\* | max \\|s − truth\\| | RMS |')
    w('| --- | --- | --- | --- | --- | --- | --- | --- |')
    for r in c['synthetic']:
        w(f'| `{r["label"]}` | {r["truth_start"]:.3f} / {r["truth_reach"]:.0f} | '
          f'{r["fit_start"]:.3f} / {r["fit_reach"]:.1f} | {r["d_start"]:+.3f} | '
          f'{r["d_reach"]:+.1f} | {r["d_reach_unclamped"]:+.1f} | {r["max_abs_err"]:.3f} '
          f'| {r["rms"]:.5f} |')
    w()

# ---------------------------------------------------------------- (d) the CSS ceiling
if os.path.exists(f'{OUT}/parts/g0d-css.json'):
    d = part('g0d-css')
    w('# (d) The CSS tier at 2x: the reference\'s own ceiling, what the tier draws, and the '
      'projection')
    w()
    w('The three columns the charter asks for, and a fourth that says why they differ: the')
    w('tier\'s gain law maps a mix to a width whose fully-heavy end is the GPU tier\'s 1x')
    w('nominal 10 CSS px, where the reference\'s own heavy component at 2x is σ 4–5.5 CSS px.')
    w('The fourth column carries the same measured mix through the reference\'s measured')
    w('widths instead, as a moment-matched single Gaussian — not a fit, an arithmetic.')
    w()
    w('| cell | span | **the reference\'s ceiling** σ, CSS px (RMS) | §5.55 §5 | **what the tier '
      'draws at 2x** σ (its mix) | **(b)\'s law through the tier\'s gain** σ (its mix) '
      '| (b)\'s law through the reference\'s widths, moment-matched |')
    w('| --- | --- | --- | --- | --- | --- | --- |')
    for r in d['rows']:
        w(f'| `{r["comp"]}` | {r["span"]} | {r["ceiling_sigma"]:.2f} ({r["ceiling_rms"]:.4f}) | '
          f'{r["published"]:.1f} | {r["tier_sigma"]:.3f} ({r["tier_mix"]:.3f}) | '
          f'{r["projected_sigma"]:.3f} ({r["projected_mix"]:.3f}) | '
          f'{r["projected_moment_sigma"]:.3f} |')
    w()

with open(f'{OUT}/g0-tables.md', 'w') as f:
    f.write('\n'.join(lines) + '\n')
print(f'[wrote] {OUT}/g0-tables.md ({len(lines)} lines)')
