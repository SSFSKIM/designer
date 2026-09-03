"""G3 reading 2: depth — how the two components change with the inset u, 1x against 2x.

Bands are annuli of the silhouette's own distance field, 8 CSS px wide, from u = 20 (outside the
lens: 5.49 2 puts D < 1 px from u ≈ 17–18 at every span, so a band from 20 in is displacement-free)
to the half-span. Per (cell, scale, pitch) the heavy width is fixed once from the whole inset
interior joint over the three pitches; each band then reads the sharp component's σ and amplitude
and the heavy component's share at that σ_heavy, which is what 5.49 7's depth claim is about
("at 1x the sharp component keeps its width and loses amplitude linearly over the half-span; at 2x
its σ widens instead").
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

from g3lib import *  # noqa: F401,F403

CELLS = ['rrect-md', 'rrect-ml', 'rrect-lg']
PITCHES = ['checkerboard-8', 'checkerboard', 'checkerboard-32', 'checkerboard-64']
BAND_W = 8.0
U0 = 20.0

out = dict(band_width=BAND_W, u_start=U0, cells={})
for scale in SCALES:
    for comp in CELLS:
        half = SPAN[comp] / 2
        edges = list(np.arange(U0, half + 1e-6, BAND_W))
        if edges[-1] < half - 1e-6:
            edges.append(half)
        m_all = box_mask(comp, scale)
        Ys = {b: capture(f'{b}__{comp}__rest', scale) for b in PITCHES}
        joint = fit_two_joint([Ys[b] for b in PITCHES], [(b, plate(b, scale)) for b in PITCHES],
                              [m_all] * len(PITCHES), scale)
        sh = joint['sigma_heavy']
        key = f'{comp}@{scale}x'
        out['cells'][key] = dict(comp=comp, scale=scale, span=SPAN[comp],
                                 sigma_heavy_fixed=sh, whole_interior=joint, bands={})
        print(f'== {scale}x {comp} (span {SPAN[comp]}): σ_heavy fixed at {sh} CSS px '
              f'({sh * scale} dev), whole-interior share {joint["share"]:.3f} rms {joint["rms"]:.4f}')
        for b in PITCHES:
            rows = []
            for u0, u1 in zip(edges[:-1], edges[1:]):
                mask = band_mask(comp, scale, u0, u1)
                if mask.sum() < 200:
                    continue
                P = plate(b, scale)
                if P[mask].std() < 0.02:
                    continue
                two = fit_two(Ys[b], P, mask, scale, b, sig_heavy=[sh])
                single, _ = fit_single(Ys[b], P, mask, scale, b)
                rows.append(dict(u0=u0, u1=u1, px=int(mask.sum()),
                                 sigma_sharp=two['sigma_sharp'], t_sharp=two['t_sharp'],
                                 t_heavy=two['t_heavy'], share=two['share'], t=two['t'],
                                 a=two['a'], rms=two['rms'],
                                 single_sigma=single['sigma'], single_t=single['t'],
                                 single_a=single['a'], single_rms=single['rms'],
                                 heavy_unresolved=bool(two.get('heavy_unresolved', False)),
                                 interior_std=float(Ys[b][mask].std()),
                                 retained=float(Ys[b][mask].std() / P[mask].std())))
            out['cells'][key]['bands'][b] = rows
            if rows:
                print(f'   {b:16s} ' + ' | '.join(
                    f'u{r["u0"]:.0f}-{r["u1"]:.0f}: σ1 {r["single_sigma"]:.2f} t1 {r["single_t"]:.3f}'
                    + ('' if r['heavy_unresolved'] else
                       f' [σs {r["sigma_sharp"]:.2f} ts {r["t_sharp"]:.3f} k {r["share"]:.2f}]')
                    for r in rows), flush=True)

write_part('depth', out)
