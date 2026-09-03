"""The two terms separated on the checkerboard, and each one's own geometry.

The pitch-16 checkerboard separates the composite exactly, with no model in the way. Its blur-40
copy is flat to 0.001 across the plate (`parts/vibrant.json`: blur-40 reads 0.749 over the black
squares of pitches 4 through 32 alike), so the vibrant term's contribution is the SAME on a black
square and on the white square beside it, and at one distance and one side

    y_black = Lambda(d)                      the lift alone — a multiply is inert over black,
    y_white = 1 * (1 - alpha_enc * F_b(d)) + Lambda(d),

so `y_white - y_black` is the black term's transmission with the lift removed, and `y_black` is the
lift with the black term removed. Neither reading needs the other's model.

Two fits per cell, both in the encoded domain, both over the pixels rather than the ring means:

  * the BLACK term — y_white - Lambda(d, side) = 1 - alpha_enc * Phi(-(sdf(x, y-offset) - spread)/sigma),
    four free parameters, against W8's landed 0.1304 / 15.55 / 7.95 / 3.1;
  * the LIFT — y_black = A_v * Phi(-(sdf(x, y-height) - amount)/sigma_v), four free parameters,
    against the layer tree's `inputShadowHeight` 0.4*span, `inputShadowAmount` min(0.625*span, 75)
    and `inputShadowBlurRadius` 40 (claims 5.50 2).

`Lambda(d, side)` is tabulated from the black squares at one CSS px of resolution per side, so the
black term's fit carries the lift as measured rather than as modelled.

vitrea's own capture is fitted the same way (X4): its black term must return W8's four constants and
its lift must return an amplitude of zero.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.optimize import least_squares
import w14lib as L

COMPONENTS = ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg', 'glass-over-glass']
MAXD = 60.0
BLACK, WHITE = 0.02, 0.98
GUARD = 2.0
"""CSS px of exterior dropped at the contour, on every source. The surface's own antialiased edge
lives there, and on the CSS tier so does the element's rim: the CSS captures read 0.279 (rrect-md)
and 0.288 (capsule) on the black squares 0-4 px out and 0.000 from 4 px on, where the native
fixtures read a smooth 0.030 falling to 0.001. One guard for every source keeps the three
comparable."""


def lambda_table(Y, BG, d, side, scale):
    """The lift per (side, 1 CSS px ring) from the black squares; NaN where the ring has none."""
    k = np.clip(np.floor(d).astype(int), 0, int(MAXD) - 1)
    key = side.astype(int) * int(MAXD) + k
    dark = (BG < BLACK) & (d >= GUARD) & (d < MAXD)
    table = np.full(len(L.SIDES) * int(MAXD), np.nan)
    counts = np.bincount(key[dark], minlength=table.size)
    sums = np.bincount(key[dark], weights=Y[dark], minlength=table.size)
    ok = counts >= 8
    table[ok] = sums[ok] / counts[ok]
    return table, key


def fit_black_term(Y, BG, comp, scale, d, side, table, key):
    shapes = L.place_component(comp)
    m = (BG > WHITE) & (d >= GUARD) & (d < MAXD) & np.isfinite(table[key])
    if m.sum() < 200:
        return None
    target = Y[m] - table[key][m]

    def resid(p):
        F = L.w8_falloff_field(comp, scale, p[1], p[2], p[3], shapes)
        return (1.0 - p[0] * F[m]) - target

    best = None
    for start in ([L.outer_shadow_alpha(), L.W8_SIGMA, L.W8_OFFSET, L.W8_SPREAD],
                  [0.20, 16.0, 8.0, 0.0], [0.35, 20.0, 8.0, 6.0], [0.10, 12.0, 6.0, 0.0]):
        cand = least_squares(resid, start, bounds=([0, 2, -40, -30], [1, 80, 80, 60]))
        if best is None or cand.cost < best.cost:
            best = cand
    r = best
    return dict(alpha_enc=float(r.x[0]), occlusion_lin=float(1 - (1 - r.x[0]) ** 2.4),
                sigma=float(r.x[1]), offset=float(r.x[2]), spread=float(r.x[3]),
                rms=float(np.sqrt(np.mean(r.fun ** 2))), n=int(m.sum()))


def fit_lift(Y, BG, comp, scale, d, span):
    shapes = L.place_component(comp)
    m = (BG < BLACK) & (d >= GUARD) & (d < MAXD)
    if m.sum() < 200:
        return None
    y = Y[m]
    if y.max() < 0.004:                       # below one 8-bit code: no lift to fit
        return dict(absent='no lift above one 8-bit code', peak=float(y.max()), n=int(m.sum()))

    def resid(p):
        F = L.w8_falloff_field(comp, scale, p[1], p[2], p[3], shapes)
        return p[0] * F[m] - y

    best = None
    for start in ([0.05, 20.0, L.apple_shadow_height(span), L.apple_shadow_amount(span)],
                  [0.08, 16.0, 8.0, 0.0], [0.10, 40.0, 0.4 * span, 0.0]):
        cand = least_squares(resid, start, bounds=([0, 2, -20, -20], [1, 120, 200, 200]))
        if best is None or cand.cost < best.cost:
            best = cand
    r = best
    # the same amplitude at W8's own three lengths, to say whether the lift needs its own geometry
    Fw = L.w8_falloff_field(comp, scale, L.W8_SIGMA, L.W8_OFFSET, L.W8_SPREAD, shapes)[m]
    a_fixed = float((Fw * y).sum() / (Fw * Fw).sum())
    rms_fixed = float(np.sqrt(np.mean((a_fixed * Fw - y) ** 2)))
    return dict(amplitude=float(r.x[0]), sigma=float(r.x[1]), height=float(r.x[2]),
                amount=float(r.x[3]), rms=float(np.sqrt(np.mean(r.fun ** 2))), n=int(m.sum()),
                amplitude_at_w8=a_fixed, rms_at_w8=rms_fixed,
                apple_height=L.apple_shadow_height(span), apple_amount=L.apple_shadow_amount(span),
                apple_blur_radius=L.apple_shadow_blur_radius(span))


out = {}
for scale in (1, 2):
    prof = L.profile_key(scale)
    BG = L.luma_of(L.image_srgb(L.backdrop_path('checkerboard', scale)))
    for comp in COMPONENTS:
        scene = f'checkerboard__{comp}__rest'
        if not L.has_native(prof, scene):
            continue
        d, side = L.geometry(comp, scale)
        span = L.span_of(comp)
        cell = dict(span=span, vibrancy=L.apple_vibrancy(span))
        for src, path in (('native', L.native_path(prof, scene)),
                          ('webgpu', L.web_path(prof, scene) if L.has_web(prof, scene) else None),
                          ('css', L.web_path(prof, scene, 'css')
                           if L.has_web(prof, scene, 'css') else None)):
            if path is None:
                continue
            Y = L.luma_of(L.image_srgb(path))
            table, key = lambda_table(Y, BG, d, side, scale)
            cell[src] = dict(black_term=fit_black_term(Y, BG, comp, scale, d, side, table, key),
                             lift=fit_lift(Y, BG, comp, scale, d, span),
                             lambda_profile={f'{L.SIDES[i]}': [None if np.isnan(v) else float(v)
                                                               for v in table[i * int(MAXD):
                                                                              (i + 1) * int(MAXD)]]
                                             for i in range(len(L.SIDES))})
        out[f'{scale}x/{comp}'] = cell

path = L.dump('geometry', out)
print('wrote', path)

print("\nthe BLACK term, lift removed — alpha_enc / occlusion / sigma / offset / spread")
print(f"{'cell':22s} {'src':7s} {'alpha':>7s} {'occ':>7s} {'sigma':>7s} {'offset':>7s} "
      f"{'spread':>7s} {'rms x255':>9s}")
for key in sorted(out):
    for src in ('native', 'webgpu', 'css'):
        f = out[key].get(src, {}).get('black_term')
        if not f:
            continue
        print(f"{key:22s} {src:7s} {f['alpha_enc']:7.4f} {f['occlusion_lin']:7.4f} "
              f"{f['sigma']:7.3f} {f['offset']:7.3f} {f['spread']:7.3f} {f['rms']*255:9.3f}")

print("\nthe LIFT — amplitude / sigma / height / amount, against Apple's own span laws")
print(f"{'cell':22s} {'src':7s} {'A_v':>7s} {'sigma':>7s} {'height':>7s} {'amount':>7s} "
      f"{'0.4span':>8s} {'.625span':>8s} {'rms x255':>9s}")
for key in sorted(out):
    for src in ('native', 'webgpu', 'css'):
        f = out[key].get(src, {}).get('lift')
        if not f:
            continue
        if 'absent' in f:
            print(f"{key:22s} {src:7s}  — {f['absent']} (peak {f['peak']*255:.2f}/255)")
            continue
        print(f"{key:22s} {src:7s} {f['amplitude']:7.4f} {f['sigma']:7.3f} {f['height']:7.2f} "
              f"{f['amount']:7.2f} {f['apple_height']:8.2f} {f['apple_amount']:8.2f} "
              f"{f['rms']*255:9.3f}")


# ------------------------------------------------------------------ the joint decomposition
#
# `y_white - Lambda` is NOT the black term on its own. The vibrant layer covers the white square as
# well as the black one, so with alpha_v*F_v the vibrant layer's own coverage and C its colour,
#
#     y_black = alpha_v * F_v * C                       = Lambda
#     y_white = (1 - alpha_v * F_v) * (1 - alpha_b * F_b) + Lambda,
#
# and the subtraction above leaves (1 - alpha_v F_v)(1 - alpha_b F_b), whose fitted amplitude is the
# COMPOSITE's and not the black term's. One number closes it: the vibrant colour C. Given C the
# coverage is alpha_v*F_v = Lambda/C, and the black term follows. C is identifiable because the two
# terms have different shapes — F_v's extent is the layer tree's Height/Amount and F_b's is W8's
# offset/spread — so this stage fits C together with the black term's four parameters, taking F_v's
# shape from the lift fit above.

print("\nthe joint decomposition — the vibrant colour C, then the BLACK term alone")
print(f"{'cell':22s} {'src':7s} {'C':>7s} {'alpha_v':>8s} {'alpha_b':>8s} {'occ_b':>7s} "
      f"{'sigma_b':>8s} {'off_b':>7s} {'spr_b':>7s} {'rms x255':>9s}")
print("(the two terms share one falloff on this bed, so C, alpha_v and alpha_b trade off against\n"
      " each other along it; the collinearity of the two shapes is printed beside every row.)")
joint = {}
for scale in (1, 2):
    prof = L.profile_key(scale)
    BG = L.luma_of(L.image_srgb(L.backdrop_path('checkerboard', scale)))
    for comp in COMPONENTS:
        scene = f'checkerboard__{comp}__rest'
        key = f'{scale}x/{comp}'
        lift = out.get(key, {}).get('native', {}).get('lift')
        if not lift or 'absent' in lift:
            continue
        d, side = L.geometry(comp, scale)
        shapes = L.place_component(comp)
        Fv = L.w8_falloff_field(comp, scale, lift['sigma'], lift['height'], lift['amount'], shapes)
        Y = L.luma_of(L.image_srgb(L.native_path(prof, scene)))
        m = (BG > WHITE) & (d >= GUARD) & (d < MAXD)
        y = Y[m]
        Av = lift['amplitude']

        def resid(p):
            C, alpha_b, sigma, offset, spread = p
            cov = np.clip(Av * Fv[m] / C, 0, 1)
            Fb = L.w8_falloff_field(comp, scale, sigma, offset, spread, shapes)[m]
            return (1 - cov) * (1 - alpha_b * Fb) + Av * Fv[m] - y

        best = None
        for start in ([0.60, 0.13, 15.5, 8.0, 3.0], [0.75, 0.13, 16.0, 8.0, 0.0],
                      [0.40, 0.20, 16.0, 8.0, 0.0], [0.90, 0.10, 15.0, 8.0, 3.0]):
            cand = least_squares(resid, start,
                                 bounds=([Av + 0.01, 0, 2, -40, -30], [1.0, 1, 80, 80, 60]))
            if best is None or cand.cost < best.cost:
                best = cand
        C, ab, sb, ob, pb = best.x
        Fb = L.w8_falloff_field(comp, scale, sb, ob, pb, shapes)[m]
        collinearity = float(np.corrcoef(Fv[m], Fb)[0, 1])
        rec = dict(collinearity=collinearity,C=float(C), alpha_v=float(Av / C), alpha_b=float(ab),
                   occlusion_b=float(1 - (1 - ab) ** 2.4), sigma_b=float(sb), offset_b=float(ob),
                   spread_b=float(pb), rms=float(np.sqrt(np.mean(best.fun ** 2))), n=int(m.sum()),
                   blurred_backdrop_enc=0.749, span=out[key]['span'],
                   vibrancy=out[key]['vibrancy'])
        joint[key] = rec
        print(f"{key:22s} {'native':7s} {C:7.4f} {Av/C:8.4f} {ab:8.4f} "
              f"{rec['occlusion_b']:7.4f} {sb:8.3f} {ob:7.3f} {pb:7.3f} {rec['rms']*255:9.3f} "
              f"  corr(F_v, F_b) = {collinearity:.5f}"
              + ('   NOT SEPARABLE' if collinearity > 0.999 else ''))

L.dump('geometry-joint', joint)
