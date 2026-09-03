"""The lift's colour, on `photo`: the backdrop's own light, or a fixed gray?

Two readings, per cell x side x ring, in linear RGB and in the encoded domain:

  1. the affine fit PER CHANNEL, y_k = a_k*bg_k + c_k. A fixed gray composited at low alpha lifts
     the three channels by the SAME amount whatever the backdrop; a darkened copy of the backdrop
     lifts them in the backdrop's own ratio. The two are told apart by comparing (c_R, c_G, c_B)
     with the local blurred backdrop's own channel ratio — and by comparing `photo` (coloured) with
     the checkerboard (gray), where a fixed gray and a copy of the backdrop predict the same thing.
  2. the model comparison: y_k = a*bg_k + c_k (a per-channel CONSTANT lift, three free numbers)
     against y_k = a*bg_k + alpha*B_sigma,k + c0 (a blurred COPY of the backdrop at one amplitude,
     two free numbers plus sigma). The residuals say which family the lift is in, over the same
     pixels with the same black term.

`glass-over-glass` is included because its exterior is the base surface's, at span 130.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import w14lib as L

CELLS = [('photo', 'rrect-md'), ('photo', 'rrect-lg'), ('photo', 'glass-over-glass'),
         ('checkerboard', 'rrect-lg')]
SIGMAS = [8.0, 16.0, 24.0, 32.0, 40.0, 48.0, 64.0]
RING_SET = ('0-6', '6-12', '12-24')


def fit_channels(Y, BG, m):
    """Per-channel affine. Returns a, c and R^2 per channel over the mask."""
    out = {}
    for k, name in enumerate('rgb'):
        y, bg = Y[..., k][m], BG[..., k][m]
        out[name] = L.fit_affine(y, bg)
    return out


def compare_models(Y, BG, Bs, m):
    """Constant-lift against blurred-copy, pooled over the three channels with one shared `a`."""
    y = np.concatenate([Y[..., k][m] for k in range(3)])
    bg = np.concatenate([BG[..., k][m] for k in range(3)])
    n = int(m.sum())
    ind = [np.concatenate([np.where(np.arange(3) == j, 1.0, 0.0)[k] * np.ones(n)
                           for k in range(3)]) for j in range(3)]

    def rms(X):
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        res = y - X @ coef
        return float(np.sqrt(np.mean(res ** 2))), coef

    const_rms, const_coef = rms(np.stack([bg] + ind, 1))
    best = None
    for sigma, B in Bs.items():
        col = np.concatenate([B[..., k][m] for k in range(3)])
        r, coef = rms(np.stack([bg, col, np.ones_like(bg)], 1))
        rec = dict(sigma=sigma, rms=r, a=float(coef[0]), alpha=float(coef[1]), c0=float(coef[2]))
        if best is None or r < best['rms']:
            best = rec
    return dict(n=n, const=dict(rms=const_rms, a=float(const_coef[0]),
                                c=[float(v) for v in const_coef[1:]]),
                copy=best)


out = {}
for scale in (1, 2):
    prof = L.profile_key(scale)
    for backdrop, comp in CELLS:
        scene = f'{backdrop}__{comp}__rest'
        if not L.has_native(prof, scene):
            continue
        BG_enc = L.image_srgb(L.backdrop_path(backdrop, scale))
        BG_lin = L.srgb_to_lin(BG_enc)
        Bs = {s: L.blur_css(BG_lin, s, scale) for s in SIGMAS}
        d, side = L.geometry(comp, scale)
        for src, path in (('native', L.native_path(prof, scene)),
                          ('webgpu', L.web_path(prof, scene) if L.has_web(prof, scene) else None)):
            if path is None:
                continue
            Y_enc = L.image_srgb(path)
            Y_lin = L.srgb_to_lin(Y_enc)
            rows = {}
            for label, ring in zip(L.RING_LABELS, L.RINGS):
                if label not in RING_SET:
                    continue
                for side_name in ('below', 'all'):
                    m = L.ring_side_mask(d, side, ring, None if side_name == 'all' else side_name)
                    if side_name == 'all':
                        m &= (side != L.SIDES.index('corner'))
                    m &= (d >= 1.5 / scale)
                    if m.sum() < L.MIN_N:
                        continue
                    rows[f'{label}/{side_name}'] = dict(
                        channels_lin=fit_channels(Y_lin, BG_lin, m),
                        channels_enc=fit_channels(Y_enc, BG_enc, m),
                        models_lin=compare_models(Y_lin, BG_lin, Bs, m),
                        blurred_mean=[float(Bs[40.0][..., k][m].mean()) for k in range(3)],
                        backdrop_mean=[float(BG_lin[..., k][m].mean()) for k in range(3)],
                    )
            out[f'{scale}x/{scene}/{src}'] = rows

path = L.dump('photo-colour', out)
print('wrote', path)

print("\nthe lift per channel, linear RGB, 0-6 BELOW (guarded) — c_R / c_G / c_B, then the ratio")
print(f"{'cell':44s} {'c_R':>8s} {'c_G':>8s} {'c_B':>8s} | {'R:G':>6s} {'B:G':>6s} | "
      f"{'blur40 R:G':>10s} {'B:G':>6s}")
for key in sorted(out):
    rec = out[key].get('0-6/below')
    if not rec:
        continue
    ch = rec['channels_lin']
    if not all(ch[k].get('identifiable') for k in 'rgb'):
        continue
    c = [ch[k]['c'] for k in 'rgb']
    b = rec['blurred_mean']
    print(f"{key:44s} {c[0]:8.4f} {c[1]:8.4f} {c[2]:8.4f} | "
          f"{c[0]/c[1] if abs(c[1])>1e-6 else float('nan'):6.3f} "
          f"{c[2]/c[1] if abs(c[1])>1e-6 else float('nan'):6.3f} | "
          f"{b[0]/b[1]:10.3f} {b[2]/b[1]:6.3f}")

print("\nconstant lift against a blurred copy of the backdrop (linear, pooled over RGB)")
print(f"{'cell':44s} {'ring':>6s} {'rms const':>10s} {'rms copy':>10s} {'sig*':>5s} "
      f"{'alpha':>7s} {'c0':>8s}")
for key in sorted(out):
    for label in ('0-6/below', '6-12/below', '12-24/below'):
        rec = out[key].get(label)
        if not rec:
            continue
        m = rec['models_lin']
        print(f"{key:44s} {label.split('/')[0]:>6s} {m['const']['rms']:10.5f} "
              f"{m['copy']['rms']:10.5f} {m['copy']['sigma']:5.0f} {m['copy']['alpha']:7.4f} "
              f"{m['copy']['c0']:+8.4f}")
