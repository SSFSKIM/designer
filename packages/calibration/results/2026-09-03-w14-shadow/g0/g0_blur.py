"""The lift's blur, from the probes' pitch axis.

If the lift is a blurred, darkened copy of the backdrop composited under the shadow, then at a coarse
checker pitch it FOLLOWS the squares and at a fine one it is flat: a sigma-40 CSS px copy of a
pitch-4 checker is a constant, of a pitch-64 checker is nearly the checker itself. So the pitch axis
is where the blur becomes identifiable at all — which is why claims 5.60 3's unweighted blur term on
pitch 16 added nothing to R^2 and concluded "no blurred copy detectable".

Per ring x side x pitch x span, in the ENCODED domain (the space both a `box-shadow` and a
CoreAnimation layer composite in), the fit is

    y = a*bg + alpha*B_sigma + c0,     B_sigma = a blurred copy of the same backdrop,

over a sigma grid of 8 ... 64 CSS px, with `a` carrying the black multiply. Two forms of the blurred
column are tried and both are reported, because the reference's own blur space is not known: `lin`
blurs the backdrop in LINEAR light and re-encodes it (the physical form), `enc` blurs the encoded
image directly.

A column whose surviving standard deviation under the mask falls below max(0.005, 5% of the
backdrop's own) carries no information about its width; the fit refuses it and the largest sigma
that survives is recorded, so "sigma is not identifiable beyond X at this pitch" is said rather than
fitted (the rule g3lib's `sigma_ceiling` established for W12 G3).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import w14lib as L

PITCHES = ['checkerboard-4', 'checkerboard-8', 'checkerboard', 'checkerboard-32', 'checkerboard-64']
COMPS = ['rrect-md', 'rrect-ml', 'rrect-lg']
SIGMAS = [8.0, 12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 40.0, 48.0, 56.0, 64.0]
RING_SET = ('0-6', '6-12', '12-24')
MIN_COL_ABS, MIN_COL_REL = 0.005, 0.05

_cols = {}


def column(backdrop, scale, sigma, form):
    key = (backdrop, scale, sigma, form)
    if key not in _cols:
        enc = L.image_srgb(L.probe_backdrop_path(backdrop, scale))
        if form == 'lin':
            blurred = L.blur_css(L.srgb_to_lin(enc), sigma, scale)
            _cols[key] = L.luma_of(np.clip(blurred, 0, 1) ** (1 / 2.4))  # a monotone re-encode
        else:
            _cols[key] = L.blur_css(L.luma_of(enc), sigma, scale)
    return _cols[key]


def fit3(y, bg, col):
    X = np.stack([bg, col, np.ones_like(bg)], 1)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    ss = float(np.sum((y - y.mean()) ** 2))
    return dict(a=float(coef[0]), alpha=float(coef[1]), c0=float(coef[2]),
                rms=float(np.sqrt(np.mean(res ** 2))),
                r2=(1 - float(res @ res) / ss if ss > 0 else float('nan')), n=int(y.size))


out = {}
for scale in (1, 2):
    for comp in COMPS:
        d, side = L.geometry(comp, scale)
        for backdrop in PITCHES:
            p = L.probe_path(f'{backdrop}__{comp}__rest', scale)
            if not os.path.exists(p):
                continue
            Y = L.luma_of(L.image_srgb(p))
            BG = L.luma_of(L.image_srgb(L.probe_backdrop_path(backdrop, scale)))
            key = f'{scale}x/{comp}/{backdrop}'
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
                    y, bg = Y[m], BG[m]
                    floor = max(MIN_COL_ABS, MIN_COL_REL * float(bg.std()))
                    rec = dict(n=int(m.sum()), bg_std=float(bg.std()),
                               affine=L.fit_affine(y, bg))
                    for form in ('lin', 'enc'):
                        curve, best, ceiling = [], None, None
                        for sigma in SIGMAS:
                            col = column(backdrop, scale, sigma, form)[m]
                            if col.std() < floor:
                                continue
                            ceiling = sigma
                            r = fit3(y, bg, col)
                            r['sigma'] = sigma
                            r['col_std'] = float(col.std())
                            curve.append(r)
                            if best is None or r['rms'] < best['rms']:
                                best = r
                        rec[form] = dict(best=best, ceiling=ceiling,
                                         curve=[(c['sigma'], c['rms'], c['alpha']) for c in curve])
                    rows[f'{label}/{side_name}'] = rec
            out[key] = rows

path = L.dump('blur', out)
print('wrote', path)

print("\nthe sigma that best explains the modulation — ring 0-6 BELOW, blurred in linear")
print(f"{'cell':30s} {'n':>6s} {'bgSD':>6s} {'affR2':>7s} {'sig*':>5s} {'alpha':>7s} "
      f"{'rms3':>7s} {'rms2':>7s} {'gain':>6s} {'ceil':>5s}")
for key in sorted(out):
    rec = out[key].get('0-6/below')
    if not rec:
        continue
    b = rec['lin']['best']
    aff = rec['affine']
    if b is None:
        print(f"{key:30s} {rec['n']:6d} {rec['bg_std']:6.3f}  — no sigma identifiable at this pitch")
        continue
    gain = aff['rms'] / b['rms'] if b['rms'] > 0 else float('nan')
    print(f"{key:30s} {rec['n']:6d} {rec['bg_std']:6.3f} {aff['r2']:7.4f} {b['sigma']:5.0f} "
          f"{b['alpha']:7.4f} {b['rms']:7.5f} {aff['rms']:7.5f} {gain:6.2f} "
          f"{rec['lin']['ceiling'] or 0:5.0f}")


# ------------------------------------------------------------------ the black-square read
#
# The ring fit above is weak because a ring is a thin band and a blurred plate has little surviving
# contrast inside one. The BLACK squares give the same measurement with nothing to disentangle: over
# a black square the backdrop sends no light, so a multiply removes nothing (claims 5.12) and every
# code that is there is the lift itself. Pooling the five pitches puts the blurred copy's own value
# over a wide range at one distance — pitch 4's blur-40 copy is flat at the plate's mean, pitch 64's
# follows the squares — so one regression of the lift on B_sigma over the pool identifies sigma.

print("\nthe lift on the BLACK squares by pitch (0-6 below, guarded, encoded)")
print(f"{'cell':22s} " + ' '.join(f'{p.replace("checkerboard","p"):>8s}' for p in PITCHES)
      + '   B40 at the black centres')
pool = {}
for scale in (1, 2):
    for comp in COMPS:
        d, side = L.geometry(comp, scale)
        row, brow = [], []
        for backdrop in PITCHES:
            p = L.probe_path(f'{backdrop}__{comp}__rest', scale)
            if not os.path.exists(p):
                row.append(None); brow.append(None); continue
            Y = L.luma_of(L.image_srgb(p))
            BG = L.luma_of(L.image_srgb(L.probe_backdrop_path(backdrop, scale)))
            for label, ring in zip(L.RING_LABELS, L.RINGS):
                if label not in RING_SET:
                    continue
                m = (L.ring_side_mask(d, side, ring, 'below') & (d >= 1.5 / scale) & (BG < 0.02))
                if m.sum() < L.MIN_N:
                    continue
                key = (scale, comp, label)
                pool.setdefault(key, {'y': [], 'B': {s: [] for s in SIGMAS}, 'pitch': []})
                pool[key]['y'].append(Y[m])
                pool[key]['pitch'].append(np.full(int(m.sum()), L.PITCH[backdrop]))
                for s in SIGMAS:
                    pool[key]['B'][s].append(column(backdrop, scale, s, 'lin')[m])
                if label == '0-6':
                    row.append(float(Y[m].mean()))
                    brow.append(float(column(backdrop, scale, 40.0, 'lin')[m].mean()))
        print(f'{scale}x/{comp:16s} ' + ' '.join(L.fmt(v).rjust(8) for v in row)
              + '   ' + ' '.join(L.fmt(v, 3).rjust(6) for v in brow))

print("\nsigma from the pooled black-square regression (lift = alpha*B_sigma + c0)")
print(f"{'cell':22s} {'ring':>6s} {'n':>6s} {'sig*':>5s} {'alpha':>7s} {'c0':>8s} {'r2':>7s} "
      f"{'rms':>8s} {'rms(flat)':>9s}")
sigma_out = {}
for key in sorted(pool):
    scale, comp, label = key
    y = np.concatenate(pool[key]['y'])
    best = None
    curve = []
    for s in SIGMAS:
        B = np.concatenate(pool[key]['B'][s])
        X = np.stack([B, np.ones_like(B)], 1)
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        res = y - X @ coef
        rms = float(np.sqrt(np.mean(res ** 2)))
        ss = float(np.sum((y - y.mean()) ** 2))
        rec = dict(sigma=s, alpha=float(coef[0]), c0=float(coef[1]), rms=rms,
                   r2=1 - float(res @ res) / ss if ss > 0 else float('nan'), n=int(y.size))
        curve.append(rec)
        if best is None or rms < best['rms']:
            best = rec
    flat = float(y.std())
    sigma_out[f'{scale}x/{comp}/{label}'] = dict(best=best, curve=curve, rms_flat=flat)
    print(f"{scale}x/{comp:16s} {label:>6s} {best['n']:6d} {best['sigma']:5.0f} "
          f"{best['alpha']:7.4f} {best['c0']:+8.4f} {best['r2']:7.4f} {best['rms']:8.5f} "
          f"{flat:9.5f}")

L.dump('blur-black-square', sigma_out)
