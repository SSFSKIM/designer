"""X4: the instrument must recover W8's black multiply from vitrea's own canonical GPU captures.

Five cells at both scales. For each side x ring the fitted (a, c) is put beside two predictions of
the SAME landed shadow, each projected onto the ring's own affine fit so that the comparison carries
no ring-width caveat:

  * `exact` — the composite the GPU tier actually produces: a pure black layer at
    `outerShadowAlpha(0.285) * F` in the canvas's ENCODED space, rounded to 8 bits, decoded;
  * `charter` — the charter's stated form of it, the linear-light multiply 1 - 0.285*F.

Two windows are reported for every ring: `plain`, the ring as the charter declares it, and `guard`,
the same ring with the first 1.5 DEVICE px outside the declared contour dropped. The guard exists
because the innermost ring contains the surface's own antialiased boundary — which is the component,
not its shadow — and on a capsule, whose whole cap is a corner arc, that band is a third of the
corner class's ring 0-3.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import w14lib as L

CELLS = ['checkerboard__rrect-lg__rest', 'checkerboard__rrect-md__rest',
         'checkerboard__capsule-button__rest', 'photo__rrect-md__rest',
         'light-solid__capsule-button__rest']

out = {}
for scale in (1, 2):
    prof = L.profile_key(scale)
    for scene in CELLS:
        backdrop, comp, _ = L.scene_parts(scene)
        if not L.has_web(prof, scene):
            out[f'{prof}/{scene}'] = dict(absent='no web capture')
            continue
        Y = L.image_luma(L.web_path(prof, scene))
        BG = L.image_luma(L.backdrop_path(backdrop, scale))
        BG_enc = L.image_srgb(L.backdrop_path(backdrop, scale))
        assert Y.shape == BG.shape, (scene, Y.shape, BG.shape)
        d, side = L.geometry(comp, scale)
        F = L.w8_falloff_field(comp, scale)
        Y_exact = L.w8_predicted_capture(BG_enc, F)
        Y_chart = L.w8_linear_factor_charter(F) * BG
        rows = {}
        for side_name in list(L.SIDES) + ['all']:
            per = {}
            for ring, label in zip(L.RINGS, L.RING_LABELS):
                base = L.ring_side_mask(d, side, ring, None if side_name == 'all' else side_name)
                if side_name == 'all':
                    base &= (side != L.SIDES.index('corner'))
                for window, m in (('plain', base), ('guard', base & (d >= 1.5 / scale))):
                    if m.sum() < L.MIN_N:
                        continue
                    fit = L.fit_affine(Y[m], BG[m])
                    fit['occlusion'] = L.occlusion_ratio(Y[m], BG[m])
                    fit['F_mean'] = float(F[m].mean())
                    fit['F_min'] = float(F[m].min())
                    fit['F_max'] = float(F[m].max())
                    fit['pred_exact'] = L.predict_affine_from(Y_exact, BG, m)
                    fit['pred_charter'] = L.predict_affine_from(Y_chart, BG, m)
                    fit['level_pred_exact'] = float(Y_exact[m].mean())
                    fit['level_pred_charter'] = float(Y_chart[m].mean())
                    per[f'{label}/{window}'] = fit
            rows[side_name] = per
        out[f'{prof}/{scene}'] = rows

path = L.dump('validation', out)
print('wrote', path)

hdr = f"{'cell':56s} {'win':6s} {'|dA|ex':>8s} {'|dC|ex':>8s} {'|dA|ch':>8s} {'|dC|ch':>8s} {'rings':>6s}"
print(hdr)
for key, rows in out.items():
    if 'absent' in rows:
        print(f'{key:56s} absent'); continue
    for window in ('plain', 'guard'):
        worst = [0.0, 0.0, 0.0, 0.0]
        ident = 0
        for side_name, per in rows.items():
            if side_name == 'all':
                continue
            for label, fit in per.items():
                if not label.endswith('/' + window) or not fit.get('identifiable'):
                    continue
                ident += 1
                for i, (p, k) in enumerate([('pred_exact', 'a'), ('pred_exact', 'c'),
                                            ('pred_charter', 'a'), ('pred_charter', 'c')]):
                    if fit[p].get('identifiable'):
                        worst[i] = max(worst[i], abs(fit[k] - fit[p][k]))
        if ident:
            print(f'{key:56s} {window:6s} ' + ' '.join(f'{w:8.4f}' for w in worst) + f' {ident:6d}')
        else:
            print(f'{key:56s} {window:6s} flat backdrop — a and c not separable (level rows only)')
