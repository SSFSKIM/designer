"""The vibrant hypothesis, tested where a fixed colour and a copy of the backdrop must disagree.

A fixed gray composited at low alpha lifts a BLACK pixel by the same amount over every backdrop. A
darkened copy of the backdrop lifts it in proportion to the BLURRED backdrop around it, and lifts
nothing at all over a black one. The bed separates the two directly: it carries near-black pixels
under six different local blur levels at one span —

    `impulse` and `dark-solid`      the whole exterior is dark, blur-40 near zero,
    `photo`                          dark regions with a bright surround, blur-40 in the middle,
    `hc-text`                        black glyphs on white, blur-40 near the plate's own mean,
    `checkerboard` 4 ... 64          black squares, blur-40 from the plate mean down to 0.72,

and the black term removes nothing from any of them (a multiply is inert over black, claims 5.12),
so their level IS the lift. One regression of the lift on the blurred backdrop over the pool answers
both questions at once: the slope is the vibrant term's amplitude times its darkening, and the
intercept is whatever fixed colour is left over — zero if the term is the backdrop's own light.

vitrea's own capture is pooled the same way as the X4 null: its shadow is a black multiply, so its
lift must be 0.0000 at every blur level, with no slope and no intercept.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import w14lib as L

DARK = 0.05          # encoded luma below which the backdrop sends effectively no light
SIGMAS = [8.0, 16.0, 24.0, 32.0, 40.0, 48.0, 64.0]
CANON_BACKDROPS = ['impulse', 'dark-solid', 'photo', 'hc-text', 'checkerboard']
PROBE_BACKDROPS = ['checkerboard-4', 'checkerboard-8', 'checkerboard', 'checkerboard-32',
                   'checkerboard-64']
RING = ('0-6', (0.0, 6.0))

out = {}
for scale in (1, 2):
    prof = L.profile_key(scale)
    for comp in ('rrect-md', 'rrect-ml', 'rrect-lg', 'capsule-button'):
        d, side = L.geometry(comp, scale)
        m_ring = L.ring_side_mask(d, side, RING[1], 'below') & (d >= 1.5 / scale)
        samples = {'native': [], 'webgpu': []}
        rows = []
        def take(label, bg_path, src_paths):
            BG = L.luma_of(L.image_srgb(bg_path))
            BGlin = L.srgb_to_lin(L.image_srgb(bg_path))
            B = {s: L.luma_of(np.clip(L.blur_css(BGlin, s, scale), 0, 1) ** (1 / 2.4))
                 for s in SIGMAS}
            m = m_ring & (BG < DARK)
            if m.sum() < L.MIN_N:
                return
            for src, path in src_paths.items():
                Y = L.luma_of(L.image_srgb(path))
                samples[src].append(dict(label=label, n=int(m.sum()),
                                         lift=float(Y[m].mean()),
                                         bg=float(BG[m].mean()),
                                         B={s: float(B[s][m].mean()) for s in SIGMAS},
                                         lift_px=Y[m], B_px={s: B[s][m] for s in SIGMAS}))
        for backdrop in CANON_BACKDROPS:
            scene = f'{backdrop}__{comp}__rest'
            if not L.has_native(prof, scene):
                continue
            src = {'native': L.native_path(prof, scene)}
            if L.has_web(prof, scene):
                src['webgpu'] = L.web_path(prof, scene)
            take(backdrop, L.backdrop_path(backdrop, scale), src)
        for backdrop in PROBE_BACKDROPS:
            p = L.probe_path(f'{backdrop}__{comp}__rest', scale)
            if os.path.exists(p):
                take(f'probe:{backdrop}', L.probe_backdrop_path(backdrop, scale), {'native': p})
        cell = {}
        for src, rec in samples.items():
            if len(rec) < 3:
                continue
            y = np.concatenate([r['lift_px'] for r in rec])
            best = None
            curve = []
            for s in SIGMAS:
                X = np.stack([np.concatenate([r['B_px'][s] for r in rec]), np.ones_like(y)], 1)
                coef, *_ = np.linalg.lstsq(X, y, rcond=None)
                res = y - X @ coef
                ss = float(np.sum((y - y.mean()) ** 2))
                r = dict(sigma=s, slope=float(coef[0]), intercept=float(coef[1]),
                         rms=float(np.sqrt(np.mean(res ** 2))),
                         r2=1 - float(res @ res) / ss if ss > 0 else float('nan'), n=int(y.size))
                curve.append(r)
                if best is None or r['rms'] < best['rms']:
                    best = r
            cell[src] = dict(best=best, curve=curve,
                             groups=[{k: v for k, v in r.items() if k not in ('lift_px', 'B_px')}
                                     for r in rec])
        if cell:
            out[f'{scale}x/{comp}'] = cell

path = L.dump('vibrant', out)
print('wrote', path)

print("\nthe lift on near-black pixels, 0-6 below (guarded), by backdrop — encoded luma x255")
print(f"{'cell':16s} {'backdrop':22s} {'n':>6s} {'bg':>7s} {'blur40':>7s} "
      f"{'native':>8s} {'vitrea':>8s}")
for key in sorted(out):
    nat = {g['label']: g for g in out[key]['native']['groups']}
    web = {g['label']: g for g in out[key].get('webgpu', {'groups': []})['groups']}
    for label, g in nat.items():
        w = web.get(label)
        print(f"{key:16s} {label:22s} {g['n']:6d} {g['bg']*255:7.2f} {g['B'][40.0]*255:7.2f} "
              f"{g['lift']*255:8.2f} " +
              (f"{w['lift']*255:8.2f}" if w else '       —'))

print("\nlift = slope * blur_sigma(backdrop) + intercept, pooled over the backdrops")
print(f"{'cell':16s} {'src':7s} {'n':>7s} {'sig*':>5s} {'slope':>8s} {'intercept':>10s} "
      f"{'r2':>7s} {'rms x255':>9s}")
for key in sorted(out):
    for src in ('native', 'webgpu'):
        if src not in out[key]:
            continue
        b = out[key][src]['best']
        print(f"{key:16s} {src:7s} {b['n']:7d} {b['sigma']:5.0f} {b['slope']:8.4f} "
              f"{b['intercept']:+10.5f} {b['r2']:7.4f} {b['rms']*255:9.3f}")
