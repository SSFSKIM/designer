"""The lift by span, and the black term by span, on the two-level backdrop.

A checkerboard backdrop takes exactly two values, so the affine fit's two coefficients are the two
level means and nothing more: the BLACK squares read c directly and the WHITE squares read a + c.
This script reads those two levels straight, with no regression, per side x ring, on

  * the canonical bed's checkerboard cells at both scales (spans 32, 44, 96, 128, 130, 160), and
  * the pitch-16 cells of the two probe beds at both scales (spans 32, 44, 96, 128, 160),

and puts the lift on the black squares against the layer tree's
`inputShadowVibrancyContribution` = clamp((span - 64)/96, 0, 1) (claims 5.50 2).

The black level is the composited lift with nothing subtracted: over a black square the reference's
own black term removes nothing (a multiply is inert over black, claims 5.12), so whatever light is
there arrived from a term that is NOT a multiply. vitrea's own capture reads 0.0000 on the same
squares, which is the X4 recovery for this reading.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import w14lib as L

CANON = [('checkerboard', c) for c in ('rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml',
                                       'rrect-lg', 'glass-over-glass', 'toolbar-group')]
PROBE_COMPS = ('rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg')

BLACK, WHITE = 0.02, 0.98


def levels(Y_lin, Y_enc, BG_lin, d, side, scale, source):
    rows = {}
    for side_name in list(L.SIDES) + ['all']:
        per = {}
        for ring, label in zip(L.RINGS, L.RING_LABELS):
            base = L.ring_side_mask(d, side, ring, None if side_name == 'all' else side_name)
            if side_name == 'all':
                base &= (side != L.SIDES.index('corner'))
            base &= (d >= 1.5 / scale)
            rec = {}
            for name, sel in (('black', BG_lin < BLACK), ('white', BG_lin > WHITE)):
                m = base & sel
                if m.sum() < L.MIN_N:
                    continue
                rec[f'{name}_n'] = int(m.sum())
                rec[f'{name}_lin'] = float(Y_lin[m].mean())
                rec[f'{name}_enc'] = float(Y_enc[m].mean())
            if 'white_lin' in rec:
                rec['white_occlusion'] = 1.0 - rec['white_lin']  # the white square's own level is 1
            per[label] = rec
        rows[side_name] = per
    return rows


out = {}


def add(key, comp, scale, path, bg_path, source):
    BG_lin = L.image_luma(bg_path)
    Y_enc_img = L.image_srgb(path)
    if Y_enc_img.shape != L.image_srgb(bg_path).shape:
        return
    d, side = L.geometry(comp, scale)
    out.setdefault(key, {})[source] = levels(L.luma_of(L.srgb_to_lin(Y_enc_img)),
                                             L.luma_of(Y_enc_img), BG_lin, d, side, scale, source)
    out[key]['span'] = L.span_of(comp)
    out[key]['scale'] = scale
    out[key]['vibrancy'] = L.apple_vibrancy(L.span_of(comp))


for scale in (1, 2):
    prof = L.profile_key(scale)
    for backdrop, comp in CANON:
        scene = f'{backdrop}__{comp}__rest'
        if L.has_native(prof, scene):
            add(f'canonical/{scale}x/{comp}', comp, scale, L.native_path(prof, scene),
                L.backdrop_path(backdrop, scale), 'native')
        if L.has_web(prof, scene):
            add(f'canonical/{scale}x/{comp}', comp, scale, L.web_path(prof, scene),
                L.backdrop_path(backdrop, scale), 'webgpu')
    for comp in PROBE_COMPS:
        p = L.probe_path(f'checkerboard__{comp}__rest', scale)
        if os.path.exists(p):
            add(f'probe/{scale}x/{comp}', comp, scale, p,
                L.probe_backdrop_path('checkerboard', scale), 'native')

path = L.dump('span', out)
print('wrote', path)

print("\nthe lift on the BLACK squares, 0-6 CSS px BELOW the surface (guarded), native | vitrea GPU")
print(f"{'cell':34s} {'span':>4s} {'Vc':>5s} {'c_enc':>8s} {'c_lin':>8s} {'vitrea':>8s} "
      f"{'c_enc/Vc':>9s} {'c_lin/Vc':>9s} {'occ_white':>9s}")
for key in sorted(out, key=lambda k: (out[k]['scale'], out[k]['span'], k)):
    cell = out[key]
    nat = cell.get('native', {}).get('below', {}).get('0-6', {})
    web = cell.get('webgpu', {}).get('below', {}).get('0-6', {})
    if 'black_enc' not in nat:
        continue
    vc = cell['vibrancy']
    r_e = nat['black_enc'] / vc if vc > 0 else float('nan')
    r_l = nat['black_lin'] / vc if vc > 0 else float('nan')
    print(f"{key:34s} {cell['span']:4.0f} {vc:5.2f} {nat['black_enc']:8.4f} "
          f"{nat['black_lin']:8.4f} {L.fmt(web.get('black_enc')):>8s} "
          f"{L.fmt(r_e):>9s} {L.fmt(r_l):>9s} {L.fmt(nat.get('white_occlusion')):>9s}")

print("\nthe same lift by side, canonical 1x (0-6 guarded, encoded)")
print(f"{'cell':34s} " + ' '.join(f'{s:>9s}' for s in L.SIDES))
for key in sorted(out):
    if not key.startswith('canonical/1x'):
        continue
    nat = out[key].get('native', {})
    row = [L.fmt(nat.get(s, {}).get('0-6', {}).get('black_enc')) for s in L.SIDES]
    print(f'{key:34s} ' + ' '.join(f'{v:>9s}' for v in row))
