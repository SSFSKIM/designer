"""The reference's composite, per side x ring, on every untinted rest cell of the bed.

For every cell the native fixture, vitrea's canonical GPU capture, vitrea's CSS capture and W8's own
analytic composite over the same backdrop are read by the SAME code, so every reference table
carries the instrument's recovery of the landed W8 shadow beside it (X4).

Every ring is fitted in BOTH spaces (`lin`, linear luminance — the space the charter binds; `enc`,
encoded Rec.709 luma — the space claims 5.60 3's +0.039 was read in and the space both tiers
composite in). See `w14lib.fit_pair`.

Output: `parts/reference.json`, keyed `<profile>/<scene>` -> `<renderer>` -> side -> `<ring>/<window>`
-> {lin, enc}.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import w14lib as L

PROFILES = [(1, 'light', 'standard'), (2, 'light', 'standard'),
            (1, 'dark', 'standard'), (2, 'dark', 'standard'),
            (1, 'light', 'increased-contrast'), (1, 'light', 'reduced-transparency')]

BACKDROPS = ['checkerboard', 'photo', 'light-solid', 'mid-dark-solid', 'dark-solid', 'impulse',
             'hc-text']
COMPONENTS = ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg', 'glass-over-glass',
              'toolbar-group']


def read(Y_lin, Y_enc, BG_lin, BG_enc, d, side, scale):
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
                per[f'{label}/{window}'] = L.fit_pair(Y_lin, BG_lin, Y_enc, BG_enc, m)
        rows[side_name] = per
    return rows


out = {}
for scale, scheme, a11y in PROFILES:
    prof = L.profile_key(scale, scheme, a11y)
    for backdrop in BACKDROPS:
        for comp in COMPONENTS:
            scene = f'{backdrop}__{comp}__rest'
            if not L.has_native(prof, scene):
                continue
            BG_enc = L.image_srgb(L.backdrop_path(backdrop, scale))
            BG_lin = L.image_luma(L.backdrop_path(backdrop, scale))
            BG_encL = L.luma_of(BG_enc)
            F = L.w8_falloff_field(comp, scale)
            d, side = L.geometry(comp, scale)
            cell = {'span': L.span_of(comp), 'backdrop_mean_L': float(BG_lin.mean()),
                    'apple_vibrancy': L.apple_vibrancy(L.span_of(comp)),
                    'apple_thin_shadow_alpha': L.APPLE_THIN_SHADOW_ALPHA.get(backdrop)}
            sources = [('native', L.native_path(prof, scene))]
            for renderer in ('webgpu', 'css'):
                if L.has_web(prof, scene, renderer):
                    sources.append((renderer, L.web_path(prof, scene, renderer)))
            for name, path in sources:
                Y_enc = L.image_srgb(path)
                if Y_enc.shape != BG_enc.shape:
                    cell[name] = dict(absent=f'shape {Y_enc.shape}')
                    continue
                cell[name] = read(L.luma_of(L.srgb_to_lin(Y_enc)), L.luma_of(Y_enc),
                                  BG_lin, BG_encL, d, side, scale)
            # W8's landed shadow over the same backdrop, analytically, read by the same instrument
            pred_enc = BG_enc * (1.0 - L.outer_shadow_alpha() * F[..., None])
            pred_enc = np.round(pred_enc * 255.0) / 255.0
            cell['w8_model'] = read(L.luma_of(L.srgb_to_lin(pred_enc)), L.luma_of(pred_enc),
                                    BG_lin, BG_encL, d, side, scale)
            out[f'{prof}/{scene}'] = cell

path = L.dump('reference', out)
print('wrote', path, '—', len(out), 'cells')

print(f"\nthe lift c BELOW the surface, guarded rings, native | vitrea GPU | W8 model")
print(f"{'cell':56s} {'span':>4s} {'Vc':>4s} {'space':>5s} " +
      ' '.join(f'{lab:>22s}' for lab in ('0-6', '6-12', '12-24', '24-48')))
for key, cell in out.items():
    nat = cell.get('native', {}).get('below', {})
    if not any(v['lin'].get('identifiable') for v in nat.values()):
        continue
    for space in ('lin', 'enc'):
        cols = []
        for lab in ('0-6', '6-12', '12-24', '24-48'):
            trio = []
            for src in ('native', 'webgpu', 'w8_model'):
                f = cell.get(src, {}).get('below', {}).get(f'{lab}/guard', {})
                trio.append(L.fmt(f.get(space, {}).get('c'), 4) if f else '—')
            cols.append('/'.join(f'{t:>7s}' for t in trio))
        print(f"{key:56s} {cell['span']:4.0f} {cell['apple_vibrancy']:4.2f} {space:>5s} " +
              ' '.join(cols))
