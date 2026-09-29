"""W42 G0 instrument: the region statistics clause 6 gates on, and their populations.

Clause 6 gates a family on region statistics, never on per-cell rms (which is reported beside them). Each
statistic is a MEDIAN of output codes over a declared population of deep-mask pixels, read per channel:

- uniform (family A): the deep median;
- two-level checker (families B, B', E and the checker bridges): one median per checker square whose core
  (the pixels at least `core_pt` = min(4, pitch / 4) pt from every checker edge) lies inside the deep mask,
  labelled knee side or far side (light: the darker level is the knee side; dark: the brighter), plus the
  pooled knee-side and far-side core medians;
- single patch (family C, the impulse bridges): the patch core (at least min(1, size / 4) pt inside the
  square) and the surround annuli, rings of distance to the patch's edge in PATCH_RINGS pt;
- step (family D): the two plateaus (at least 24 pt from the step) and the transition bins of signed distance
  to the step in STEP_BINS pt, each inside the deep mask;
- anything else (photo, text): the deep median only.

A population with fewer than MIN_PX pixels is not a statistic. Medians of integer codes are themselves
quantised to 0.5 code; that is the statistic's own resolution on a single capture, and proof 2 states it.
"""
import numpy as np
from scipy import ndimage

import geometry as G

MIN_PX = 12
PATCH_RINGS = (0.0, 2.0, 4.0, 8.0, 16.0, 32.0, 48.0)
STEP_BINS = (-24.0, -16.0, -8.0, -4.0, -2.0, 0.0, 2.0, 4.0, 8.0, 16.0, 24.0)
PLATEAU_PT = 24.0


def _edges_distance(levels, scale):
    """Distance (pt) from every pixel to the nearest level change of a piecewise-constant backdrop."""
    e = np.zeros(levels.shape, bool)
    e[:, 1:] |= levels[:, 1:] != levels[:, :-1]
    e[:, :-1] |= levels[:, 1:] != levels[:, :-1]
    e[1:, :] |= levels[1:, :] != levels[:-1, :]
    e[:-1, :] |= levels[1:, :] != levels[:-1, :]
    return ndimage.distance_transform_edt(~e) / scale


def populations(cell):
    """[(name, kind, boolean mask over the canvas)] for a cell, deep-mask restricted."""
    spec, m, s = cell.bg_spec, cell.mask, cell.scale
    kind = spec['kind']
    B = cell.B if cell.B.ndim == 2 else G.luma(cell.B * 255) / 255
    out = []
    if kind == 'solid':
        out.append(('deep', 'uniform', m))
    elif kind == 'checkerboard':
        pitch = spec['cell']
        core = min(4.0, pitch / 4.0)
        dist = _edges_distance(np.round(B * 255).astype(int), s)
        la, lb = G.luma(np.array(spec['a'], float)), G.luma(np.array(spec['b'], float))
        dark_is_a = la < lb
        is_a = np.abs(B * 255 - la) < np.abs(B * 255 - lb)
        knee_a = dark_is_a if cell.scheme == 'light' else not dark_is_a
        lab, n = ndimage.label(np.ones_like(is_a) & (dist >= core))
        # squares: connected components of the core set (each checker square's core is one component)
        pk, pf = np.zeros_like(m), np.zeros_like(m)
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            reg = lab[sl] == i
            full = np.zeros_like(m)
            full[sl] = reg
            if not (full & ~m).any() and full.sum() >= MIN_PX:
                side_a = bool(is_a[full].mean() > 0.5)
                knee = side_a == knee_a
                out.append((f'sq{i}:{"knee" if knee else "far"}', 'checker-square', full))
                (pk if knee else pf)[full] = True
        if pk.any():
            out.append(('knee-cores', 'checker-pooled', pk))
        if pf.any():
            out.append(('far-cores', 'checker-pooled', pf))
    elif kind == 'impulse':
        lev = np.round(B * 255).astype(int)
        fg = G.luma(np.array(spec['foreground'], float))
        is_fg = np.abs(B * 255 - fg) < 0.5
        lab, n = ndimage.label(is_fg)
        dist_out = ndimage.distance_transform_edt(~is_fg) / s
        dist_in = ndimage.distance_transform_edt(is_fg) / s
        size = spec['size']
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            sq = lab == i
            core = sq & (dist_in >= min(1.0, size / 4.0) + 0.5 / s)
            if (core & m).sum() >= 1 and not (sq & ~m).any():
                out.append((f'p{i}:core', 'patch-core', core & m))
                # this patch's rings: distance to its own edge, nearer to it than to any other patch
                d_own = ndimage.distance_transform_edt(~sq) / s
                own = d_own <= dist_out + 1e-9
                for a, b in zip(PATCH_RINGS[:-1], PATCH_RINGS[1:]):
                    ring = own & ~is_fg & (d_own > a) & (d_own <= b) & m
                    if ring.sum() >= MIN_PX:
                        out.append((f'p{i}:ring{a:g}-{b:g}', 'patch-ring', ring))
        if not out:
            out.append(('deep', 'uniform-like', m))
    elif kind == 'split':
        ys, xs = np.mgrid[0:m.shape[0], 0:m.shape[1]]
        coord = ((xs if spec['axis'] == 'x' else ys) + 0.5) / s - spec['position']
        for a, b in zip(STEP_BINS[:-1], STEP_BINS[1:]):
            r = m & (coord > a) & (coord <= b)
            if r.sum() >= MIN_PX:
                out.append((f'bin{a:g}..{b:g}', 'step-bin', r))
        for nm, r in (('plateau-lo', m & (coord < -PLATEAU_PT)), ('plateau-hi', m & (coord > PLATEAU_PT))):
            if r.sum() >= MIN_PX:
                out.append((nm, 'step-plateau', r))
    else:
        out.append(('deep', 'other', m))
    return out


def statistics(cell, img, pops=None):
    """{name: median} per population (per channel for RGB images: name|c)."""
    pops = pops if pops is not None else populations(cell)
    res = {}
    for name, kind, r in pops:
        v = img[r]
        if img.ndim == 3:
            for c in range(img.shape[2]):
                res[f'{name}|{"RGB"[c]}'] = float(np.nanmedian(v[:, c]))
        else:
            res[name] = float(np.nanmedian(v))
    return res


def stats_from_masked(cell, values, pops=None):
    """Region statistics from values given on cell.mask (the forward engine's output layout)."""
    shape = cell.d.shape + ((values.shape[1],) if values.ndim == 2 else ())
    img = np.full(shape, np.nan)
    img[cell.mask] = values
    return statistics(cell, img, pops)
