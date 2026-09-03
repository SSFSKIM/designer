"""G3 reading 5: the lens crossings at 2x on the probe's coarse pitches, as a check of G2's law.

Model-free boundary crossings, the G0/G1 instrument's own primitive (claims 5.49 1): along every
pixel line normal to a straight edge, the profile crosses the midpoint of its plateaus exactly where
the sampled source sits on a known checker boundary, so D = s − u with no model in it. Only the
*window* that assigns a crossing to a boundary uses a prior (5.49 2's power law); the number
reported is the measurement. The same code path reads the 1x probe as its instrument check, where
5.49 2 has published values to reproduce (34 / 24 / 12 at u 2 / 4 / 8 on `rrect-md`).

This is a check of the landed G2 law at 2x, not a fit: nothing here is fitted to the reference.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f'{os.path.dirname(os.path.abspath(__file__))}/../g1')
import numpy as np

from g3lib import *  # noqa: F401,F403
import w12lib  # the G1 instrument, unmodified

# G2's landed law (packages/renderer-webgpu/src/material.ts), CSS px
LENS = dict(amountPerSpan=0.8, amountMax=60.0, refractionGain=0.745,
            heightPerSpan=0.25, heightMax=20.0, extentGain=1.337, profileExponent=3.69)


def g2_law(u, span):
    S = LENS['refractionGain'] * min(LENS['amountPerSpan'] * span, LENS['amountMax'])
    L = LENS['extentGain'] * min(LENS['heightPerSpan'] * span, LENS['heightMax'])
    return S * np.clip(1 - np.asarray(u, float) / L, 0, 1) ** LENS['profileExponent']


def d_prior(u):
    """5.49 2's published reference profile, used only to place the assignment windows."""
    return 42.0 * np.clip(1 - np.asarray(u, float) / 23.0, 0, 1) ** 3


def boundaries(comp, edge, pitch):
    """Checker boundaries in the source coordinate s (CSS px inward from the contour)."""
    c = w12lib.contour(comp)
    k = np.arange(0, 60)
    if edge == 'top':
        s = (CANVAS[1] - k * pitch) - c['y0']
    elif edge == 'bottom':
        s = c['y1'] - (CANVAS[1] - k * pitch)
    elif edge == 'left':
        s = k * pitch - c['x0']
    else:
        s = c['x1'] - k * pitch
    return np.sort(s[(s > 0) & (s < 60)])


def crossings(Y, comp, edge, pitch, scale, u_lo=1.2, u_hi=26.0, win=2.0):
    L = w12lib.EdgeLines(Y, comp, edge, pitch, scale)
    cr = []
    for i in range(L.n_lines):
        y = L.Y[i]
        u = L.u
        yy = y[u >= 1.5]
        mid = 0.5 * (np.percentile(yy, 95) + np.percentile(yy, 5))
        sel = (u >= u_lo) & (u <= u_hi)
        us, ys = u[sel], y[sel]
        for j in range(len(us) - 1):
            if (ys[j] - mid) * (ys[j + 1] - mid) < 0:
                cr.append(us[j] + (mid - ys[j]) / (ys[j + 1] - ys[j]) * (us[j + 1] - us[j]))
    cr = np.array(cr)
    ue = np.arange(0, 30.01, 0.25)
    s_of_u = ue + d_prior(ue)
    found = []
    for sb in boundaries(comp, edge, pitch):
        uc = [ue[j] + (sb - s_of_u[j]) / (s_of_u[j + 1] - s_of_u[j]) * 0.25
              for j in range(len(ue) - 1)
              if (s_of_u[j] - sb) * (s_of_u[j + 1] - sb) <= 0 and s_of_u[j] != s_of_u[j + 1]]
        for u_exp in uc:
            inw = cr[(cr > u_exp - win) & (cr < u_exp + win)]
            if len(inw) >= max(2, L.n_lines // 3):
                um = float(np.median(inw))
                found.append(dict(s=float(sb), u_expected=float(u_exp), u=um, D=float(sb - um),
                                  p25=float(np.percentile(inw, 25)), p75=float(np.percentile(inw, 75)),
                                  n=int(len(inw)), n_lines=int(L.n_lines),
                                  D_g2_law=float(g2_law(um, SPAN[comp]))))
    return found


out = dict(law=LENS, cells={})
for scale in SCALES:
    for comp in ['rrect-md', 'rrect-lg']:
        for pitch in (16, 32, 64):
            b = 'checkerboard' if pitch == 16 else f'checkerboard-{pitch}'
            Y = capture(f'{b}__{comp}__rest', scale)
            # instrument self-test: the analytic plate must equal the raster along the same lines
            L = w12lib.EdgeLines(plate(b, scale), comp, 'top', pitch, scale)
            selftest = float(np.abs(L.Y - L.sharp_plate(L.u)).max())
            rows = []
            for edge in w12lib.EDGES:
                for r in crossings(Y, comp, edge, pitch, scale):
                    r['edge'] = edge
                    rows.append(r)
            key = f'{comp}-p{pitch}-{scale}x'
            out['cells'][key] = dict(comp=comp, span=SPAN[comp], pitch=pitch, scale=scale,
                                     plate_selftest=selftest, crossings=rows,
                                     note=('no boundary of this pitch lands where the profile can be '
                                           'read: u + D(u) never reaches those source depths'
                                           if not rows else None))
            print(f'== {key} (plate self-test {selftest:.2e})')
            for r in sorted(rows, key=lambda r: r['u']):
                print(f'   {r["edge"]:6s} s {r["s"]:5.1f}  u {r["u"]:6.2f} [{r["p25"]:.2f}–{r["p75"]:.2f}] '
                      f'n {r["n"]:3d}/{r["n_lines"]:3d} → D {r["D"]:6.2f} | G2 law {r["D_g2_law"]:6.2f} '
                      f'| Δ {r["D"] - r["D_g2_law"]:+.2f}')

# summary: reference − law, pooled by depth bucket
buckets = {}
for key, rec in out['cells'].items():
    for r in rec['crossings']:
        b = round(r['u'] * 2) / 2
        buckets.setdefault((rec['scale'], rec['comp'], b), []).append(r['D'] - r['D_g2_law'])
out['law_gap'] = {f'{s}x|{c}|u{u}': dict(n=len(v), mean=float(np.mean(v)), max_abs=float(np.max(np.abs(v))))
                  for (s, c, u), v in sorted(buckets.items())}
print('\n== reference − G2 law, by scale / cell / depth')
for k, v in out['law_gap'].items():
    print(f'   {k:26s} n {v["n"]:2d}  mean {v["mean"]:+.2f} px  max |Δ| {v["max_abs"]:.2f}')

write_part('lens2x', out)
