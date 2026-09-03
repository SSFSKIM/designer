"""The thin regime's black term, by backdrop — the adaptive alpha, against claims 5.50 2's table.

Below the knee at span 64 the reference's vibrancy contribution is exactly zero (claims 5.50 2), and
this bed confirms it: `rrect-sm` and `capsule-button` lift a black square by 0.0000 on every
checkerboard pitch at both scales (`parts/span.json`). So on the thin spans the exterior is the
black term alone, and one ratio identifies its amplitude with nothing to disentangle:

    y_enc / bg_enc = 1 - alpha_enc * F(d; sigma, offset, spread)

fitted over every exterior pixel whose backdrop clears a brightness floor, in the ENCODED domain —
the domain a black layer composites in, and the domain in which the ratio is independent of the
backdrop's own level. `alpha_enc` is reported beside its linear-light equivalent
1 - (1 - alpha_enc)^2.4, which is the quantity the shadow axis normalises and the quantity
`MaterialOuterShadow.occlusion` names.

Two fits per cell: `fixed`, W8's landed geometry with only the amplitude free — the comparable
number across backdrops — and `free`, all four parameters, which is item 8's geometry reading.
Every reference row carries vitrea's own capture read the same way (X4): its `fixed` alpha must come
back at `outerShadowAlpha(0.285)` = 0.1304 on every backdrop, since vitrea's shadow does not adapt.

The thick cells are fitted too and flagged: above the knee the lift rides on the same pixels, so
their amplitude is the composite's and not the black term's. `g0_geometry.py` separates those.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.optimize import least_squares
import w14lib as L

BRIGHT = 0.05
"""LINEAR backdrop luminance a pixel must clear for the ratio to carry information — the shadow
axis's own floor (claims 5.12, `DEFAULT_SHADOW_BACKDROP_FLOOR`), for the same reason: below it there
is no light for a multiplicative shadow to remove. It admits `mid-dark-solid` (0.0595) and excludes
`dark-solid` (0.0117) and `impulse` (0.0037), whose cells are reported absent rather than fitted."""
BACKDROPS = ['impulse', 'dark-solid', 'mid-dark-solid', 'photo', 'checkerboard', 'hc-text',
             'light-solid']
COMPONENTS = ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg']
PROFILES = [(1, 'light', 'standard'), (2, 'light', 'standard'),
            (1, 'dark', 'standard'), (2, 'dark', 'standard'),
            (1, 'light', 'increased-contrast'), (1, 'light', 'reduced-transparency')]


BRIGHTEN_CEILING = 1.02
"""A shadow cannot brighten its surround, so an exterior pixel reading more than 2% above its own
backdrop is not shadow: it is the surface's own edge or rim caught by the window. Native and GPU
captures have none past the guard (their ratio maxes at 1.009), the CSS captures have a few whose
ratio runs to 3.4, and one such pixel has enough leverage to pull a least-squares amplitude to zero
— which is what the first pass of this script reported for the CSS tier over `photo`. They are
dropped and counted rather than winsorised."""

GUARD = 2.0
"""CSS px of exterior dropped at the contour — see `g0_geometry.GUARD`."""


def fit_black_term(Y, BG, comp, scale, m, free):
    ratio = (Y[m] / np.maximum(BG[m], 1e-6))
    shapes = L.place_component(comp)

    def model(p):
        alpha, sigma, offset, spread = p
        F = L.w8_falloff_field(comp, scale, sigma, offset, spread, shapes)
        return 1.0 - alpha * F[m] - ratio

    p0 = [L.outer_shadow_alpha(), L.W8_SIGMA, L.W8_OFFSET, L.W8_SPREAD]
    if free:
        r = least_squares(model, p0, bounds=([0, 2, -40, -20], [1, 60, 60, 40]))
        p = r.x
    else:
        r = least_squares(lambda q: model([q[0], L.W8_SIGMA, L.W8_OFFSET, L.W8_SPREAD]),
                          [p0[0]], bounds=([0], [1]))
        p = [r.x[0], L.W8_SIGMA, L.W8_OFFSET, L.W8_SPREAD]
    rms = float(np.sqrt(np.mean(r.fun ** 2)))
    return dict(alpha_enc=float(p[0]), occlusion_lin=float(1 - (1 - p[0]) ** 2.4),
                sigma=float(p[1]), offset=float(p[2]), spread=float(p[3]), rms=rms, n=int(m.sum()))


out = {}
for scale, scheme, a11y in PROFILES:
    prof = L.profile_key(scale, scheme, a11y)
    for backdrop in BACKDROPS:
        for comp in COMPONENTS:
            scene = f'{backdrop}__{comp}__rest'
            if not L.has_native(prof, scene):
                continue
            BG = L.luma_of(L.image_srgb(L.backdrop_path(backdrop, scale)))
            BGl = L.image_luma(L.backdrop_path(backdrop, scale))
            d, side = L.geometry(comp, scale)
            if float(BGl.mean()) < BRIGHT:
                out[f'{prof}/{scene}'] = dict(
                    absent='backdrop mean below the shadow axis floor — no ratio is identifiable',
                    backdrop_mean_L=float(BGl.mean()))
                continue
            m = (d >= GUARD) & (d < 60.0) & (BGl >= BRIGHT)
            if m.sum() < 200:
                out[f'{prof}/{scene}'] = dict(absent='too few supported pixels',
                                              bright_px=int(m.sum()))
                continue
            cell = dict(span=L.span_of(comp), vibrancy=L.apple_vibrancy(L.span_of(comp)),
                        apple_thin_alpha=L.APPLE_THIN_SHADOW_ALPHA.get(backdrop),
                        bright_px=int(m.sum()))
            for src, path in (('native', L.native_path(prof, scene)),
                              ('webgpu', L.web_path(prof, scene) if L.has_web(prof, scene)
                               else None),
                              ('css', L.web_path(prof, scene, 'css')
                               if L.has_web(prof, scene, 'css') else None)):
                if path is None:
                    continue
                Y = L.luma_of(L.image_srgb(path))
                ms = m & (Y <= BRIGHTEN_CEILING * BG)
                cell[src] = dict(fixed=fit_black_term(Y, BG, comp, scale, ms, False),
                                 free=fit_black_term(Y, BG, comp, scale, ms, True),
                                 trimmed=int(m.sum() - ms.sum()))
                # per-ring occlusion below the surface, linear light, for the ratio table
                Yl = L.luma_of(L.srgb_to_lin(L.image_srgb(path)))
                rings = {}
                for label, ring in zip(L.RING_LABELS, L.RINGS):
                    mm = L.ring_side_mask(d, side, ring, 'below') & (d >= GUARD) \
                        & (BGl >= BRIGHT)
                    if mm.sum() >= L.MIN_N:
                        rings[label] = float(np.mean((BGl[mm] - Yl[mm]) / BGl[mm]))
                cell[src]['ring_occlusion_below'] = rings
            out[f'{prof}/{scene}'] = cell

path = L.dump('thin-alpha', out)
print('wrote', path)

print("\nthe black term's amplitude at W8's geometry — alpha_enc (linear occlusion in brackets)")
print(f"{'cell':56s} {'span':>4s} {'5.50':>5s} {'native':>16s} {'vitrea GPU':>16s} "
      f"{'vitrea CSS':>16s} {'ratio':>6s}")
for key, cell in out.items():
    if 'absent' in cell:
        print(f"{key:56s}  — {cell['absent']}")
        continue
    def col(src):
        f = cell.get(src, {}).get('fixed')
        return f"{f['alpha_enc']:.4f}({f['occlusion_lin']:.3f})" if f else '—'
    n = cell.get('native', {}).get('fixed')
    w = cell.get('webgpu', {}).get('fixed')
    ratio = (w['occlusion_lin'] / n['occlusion_lin']) if n and w and n['occlusion_lin'] > 1e-6 \
        else float('nan')
    print(f"{key:56s} {cell['span']:4.0f} {L.fmt(cell['apple_thin_alpha'], 3):>5s} "
          f"{col('native'):>16s} {col('webgpu'):>16s} {col('css'):>16s} {L.fmt(ratio, 2):>6s}")
