"""W15 G0 (d): the CSS tier's 2x ceiling re-read, beside what the tier draws and what (b) projects.

Three σ per span, in CSS px, at 2x — no decision, three columns:

1. **The reference's own ceiling.** The best single Gaussian σ that matches the reference's
   interior across the probe's pitches, with a level and a transmission free per cell — the
   reading claims §5.55 §5 published (3.0 / 2.5 / 4.0 / 5.0 / 5.0 CSS px at RMS 0.016–0.046).
   Reproduced first from the same primitives (`g3lib`'s plate, box mask and Gaussian; the
   pooled one-column normal equations of `g3_forms.py`), because a column nobody can
   reproduce is not evidence.
2. **What the tier draws at 2x today.** `groupScatterSigma` / `sizeScatterSigmaAt` at
   `CSS_TIER_RAMP_SCALE`, read out of the built package rather than transcribed, so the
   number is the code's and not this document's.
3. **What (b)'s law projects.** The measured 2x share averaged over the surface, carried
   through the tier's own gain law (`σ = blurSigma · (1 + (gainMax − 1)·k̄)`), and — because
   that gain law's fully-heavy end is the GPU tier's 1x nominal width of 10 CSS px while the
   reference's own 2x heavy component is σ 4.5 CSS px — the same mix carried through the
   reference's measured widths as a moment-matched single Gaussian.

The area average is taken over the component's own SDF depth map at 2x rather than through a
closed form, so it needs no rectangle approximation: s(u) is the measured profile of (b),
held at its first window's value inside u < 4 and at its deep value beyond the last.
"""
import json
import os
import subprocess

import numpy as np

import w15lib as W

L = W.L
g3 = L.g3lib
ROOT = '/Users/new/Developer/GitHub/designer'
PITCHES4 = g3.PITCHES4  # 8 / 16 / 32 / 64, the pitches §5.55 §5 pooled
PUBLISHED = {'rrect-sm': 3.0, 'capsule-button': 2.5, 'rrect-md': 4.0, 'rrect-ml': 5.0,
             'rrect-lg': 5.0}

# ---------------------------------------------------------------- 1. the reference's ceiling
DATA = {}
for comp in W.COMPS:
    m = g3.box_mask(comp, 2)
    DATA[comp] = dict(mask=m, y={b: g3.capture(f'{b}__{comp}__rest', 2)[m] for b in PITCHES4})


def sse_of(M):
    """Least-squares SSE of y ≈ a + t·x from pooled sums (`g3_forms.py`, verbatim)."""
    det = M['n'] * M['Sxx'] - M['Sx'] ** 2
    if abs(det) < 1e-12:
        return M['Syy'] - M['Sy'] ** 2 / M['n']
    t = (M['n'] * M['Sxy'] - M['Sx'] * M['Sy']) / det
    a = (M['Sy'] - t * M['Sx']) / M['n']
    return max(M['Syy'] - 2 * a * M['Sy'] - 2 * t * M['Sxy'] + a * a * M['n']
               + 2 * a * t * M['Sx'] + t * t * M['Sxx'], 0.0)


def moments(comp, b, sigma):
    X = g3.G(g3.plate(b, 2), b, sigma, 2)[DATA[comp]['mask']]
    y = DATA[comp]['y'][b]
    return dict(n=len(y), Sy=float(y.sum()), Syy=float(y @ y), Sx=float(X.sum()),
                Sxx=float(X @ X), Sxy=float(X @ y))


def pool(ms):
    out = dict.fromkeys(['n', 'Sy', 'Syy', 'Sx', 'Sxx', 'Sxy'], 0.0)
    for m in ms:
        for k in out:
            out[k] += m[k]
    return out


print('1. the reference`s own 2x ceiling (best single σ, pitches 8/16/32/64 pooled)\n')
ceiling = {}
for comp in W.COMPS:
    tab = []
    for s in g3.SIG_SINGLE:
        M = pool([moments(comp, b, s) for b in PITCHES4])
        tab.append((float(np.sqrt(sse_of(M) / M['n'])), s))
    tab.sort()
    ceiling[comp] = dict(sigma=tab[0][1], rms=tab[0][0],
                         curve=[(s, r) for r, s in sorted(tab, key=lambda z: z[1])])
    print(f'   {comp:<15} σ {tab[0][1]:5.2f} CSS px  rms {tab[0][0]:.4f}   '
          f'(§5.55 §5 published {PUBLISHED[comp]})')

# ---------------------------------------------------------------- 2. what the tier draws
NODE = """
import('%s/packages/platform-web/dist/index.js').then(m => {
  const COMP = %s;
  const size = m.MATERIAL_SOURCE_SIZE, blur = m.MATERIAL_OPTICS.regular.blurRadius;
  const out = { blurRadius: blur, gainMax: size.sizeScatterGainMax, cells: {} };
  for (const [c, [w, h]] of Object.entries(COMP)) {
    const span = Math.min(w, h);
    out.cells[c] = {
      span,
      // the tier's own call: CSS_TIER_RAMP_SCALE is 1, so this is the number it draws at
      // every device scale, 2x included (W13 Decision Log 5)
      sigma: m.groupScatterSigma(blur, 1, [[w, h]], size, 1),
      k: m.scatterThickness(span, 1, size, 1, [w, h]),
      kDeep: m.scatterDeepThickness(span, size),
      sigmaIfProjectedAt2x: m.groupScatterSigma(blur, 1, [[w, h]], size, 2),
    };
  }
  console.log(JSON.stringify(out));
});
""" % (ROOT, json.dumps({c: [g3.COMP[c][0], g3.COMP[c][1]] for c in W.COMPS}))
tier = json.loads(subprocess.run(['node', '-e', NODE], capture_output=True, text=True,
                                 check=True, cwd=f'{ROOT}/packages/platform-web').stdout)
print('\n2. what the CSS tier draws at 2x today (read out of the built package)\n')
for c, r in tier['cells'].items():
    print(f'   {c:<15} σ {r["sigma"]:.3f} CSS px  (mix {r["k"]:.3f} at CSS_TIER_RAMP_SCALE 1; '
          f'the same call at the live ratio would give {r["sigmaIfProjectedAt2x"]:.3f})')

# ---------------------------------------------------------------- 3. (b)'s law projected
depth_b = json.load(open(f'{W.OUT}/parts/g0b-depth.json'))
label = next(k for k in depth_b['tables'] if k.startswith('the per-span optimum'))
prof = depth_b['tables'][label]
SHARP_CSS, HEAVY_CSS = 0.5, None  # heavy is per span, from (b)'s own settled width

print('\n3. (b)`s measured 2x mix projected over each surface\n')
rows = []
for comp in W.COMPS:
    rec = prof[comp]
    u_meas, s_meas = np.array(rec['u']), np.array(rec['s'])
    d = g3.depth(comp, 2)
    u = d[d > 0]
    s_of_u = np.interp(u, u_meas, s_meas, left=float(s_meas[0]), right=float(s_meas[-1]))
    s_bar = float(s_of_u.mean())
    k_bar = 1 - s_bar
    gain = tier['blurRadius'] * (1 + (tier['gainMax'] - 1) * k_bar)
    heavy_css = rec['sigma_device'] / 2
    moment = float(np.sqrt((1 - k_bar) * SHARP_CSS ** 2 + k_bar * heavy_css ** 2))
    rows.append(dict(comp=comp, span=L.SPAN[comp],
                     ceiling_sigma=ceiling[comp]['sigma'], ceiling_rms=ceiling[comp]['rms'],
                     published=PUBLISHED[comp],
                     tier_sigma=tier['cells'][comp]['sigma'],
                     tier_mix=tier['cells'][comp]['k'],
                     projected_sigma=gain, projected_mix=k_bar, projected_sharp_share=s_bar,
                     projected_moment_sigma=moment, heavy_css=heavy_css))
    print(f'   {comp:<15} mean sharp share {s_bar:.3f} → mix {k_bar:.3f}; through the tier`s '
          f'gain law σ {gain:.3f}; moment-matched on the reference`s own widths '
          f'(σ_sharp {SHARP_CSS}, σ_heavy {heavy_css:.2f} CSS px) σ {moment:.3f}')

print('\n   the three columns, CSS px at 2x')
print(f'   {"cell":<15} {"reference ceiling":>18} {"tier draws":>12} {"(b) projected":>14} '
      f'{"(b) moment":>12}')
for r in rows:
    print(f'   {r["comp"]:<15} {r["ceiling_sigma"]:>18.2f} {r["tier_sigma"]:>12.3f} '
          f'{r["projected_sigma"]:>14.3f} {r["projected_moment_sigma"]:>12.3f}')

W.write_part('g0d-css', dict(rows=rows, ceiling=ceiling, tier=tier, profile_choice=label))
os.makedirs(f'{W.OUT}/parts', exist_ok=True)
