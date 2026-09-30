"""W42 G0 instrument: the region statistics clause 6 gates on, and their populations.

Clause 6 gates a family on region statistics, never on per-cell rms (which is reported beside them). Each
statistic is a MEDIAN of output codes over a declared population of deep-mask pixels, read per channel:

- uniform (family A): the deep median;
- two-level checker (families B, B', E and the checker bridges): one median per checker square over its core
  (the pixels at least `core_pt` = min(4, pitch / 4) pt from every checker edge) inside the deep mask,
  labelled knee side or far side (light: the darker level is the knee side; dark: the brighter; an
  isoluminant pair is labelled a / b), plus the pooled knee-side and far-side core medians;
- single patch (family C, the impulse bridges): for every patch with core pixels in the deep mask, the patch
  core (at least min(1, size / 4) pt inside the square) and the surround annuli, rings of distance to the
  patch's edge in PATCH_RINGS pt, each inside the deep mask;
- step (family D): the two plateaus (beyond PLATEAU_PT from the step) and the transition bins of signed
  distance to the step in STEP_BINS pt, each inside the deep mask;
- anything else (photo, text): the deep median only.

A population with fewer than MIN_PX pixels is not a statistic. Medians of integer codes are themselves
quantised to 0.5 code; that is the statistic's own resolution on a single capture, and proof 2 states it.
"""
import numpy as np
from scipy import ndimage

import geometry as G

MIN_PX = 12
PATCH_RINGS = (0.0, 2.0, 4.0, 8.0, 16.0, 32.0, 48.0)
STEP_BINS = (-48.0, -32.0, -24.0, -16.0, -8.0, -4.0, -2.0, 0.0, 2.0, 4.0, 8.0, 16.0, 24.0, 32.0, 48.0)
PLATEAU_PT = 48.0


def _edges_distance(levels, scale):
    """Distance (pt) from every pixel to the nearest level change of a piecewise-constant backdrop."""
    e = np.zeros(levels.shape, bool)
    e[:, 1:] |= levels[:, 1:] != levels[:, :-1]
    e[:, :-1] |= levels[:, 1:] != levels[:, :-1]
    e[1:, :] |= levels[1:, :] != levels[:-1, :]
    e[:-1, :] |= levels[1:, :] != levels[:-1, :]
    return ndimage.distance_transform_edt(~e) / scale


def populations(cell):
    """[(name, kind, flat pixel indices into the canvas)] for a cell, deep-mask restricted (cached on the cell).
    Indices, not canvas-sized boolean masks: a checker cell carries up to ~300 populations, and as masks they
    held tens of MB per cell, several GB over a whole-bed fit."""
    if getattr(cell, '_pops', None) is None:
        cell._pops = [(nm, kind, np.flatnonzero(r).astype(np.int32)) for nm, kind, r in _populations(cell)]
    return cell._pops


def _populations(cell):
    spec, m, s = cell.bg_spec, cell.mask, cell.scale
    kind = spec['kind']
    raw = G.render_background(spec, s)          # the exact levels (chroma pairs share one luma)
    out = []
    if kind == 'solid':
        out.append(('deep', 'uniform', m))
    elif kind == 'checkerboard':
        pitch = spec['cell']
        core = min(4.0, pitch / 4.0)
        is_a = (raw == np.array(spec['a'])).all(-1)
        dist = _edges_distance(is_a.astype(int), s)
        la, lb = float(np.dot(spec['a'], G.W709)), float(np.dot(spec['b'], G.W709))
        # light: the darker level is the knee side (the lighten lifts it); dark: the brighter. An
        # isoluminant pair has no knee side by luma; its squares are labelled a / b instead.
        side = {True: 'a', False: 'b'} if abs(la - lb) < 1 else None
        knee_a = (la < lb) if cell.scheme == 'light' else (la > lb)
        lab, n = ndimage.label(dist >= core)
        pk, pf = np.zeros_like(m), np.zeros_like(m)
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            full = np.zeros_like(m)
            full[sl] = lab[sl] == i
            full &= m
            if full.sum() >= MIN_PX:
                side_a = bool(is_a[full].mean() > 0.5)
                if side:
                    out.append((f'sq{i}:{side[side_a]}', 'checker-square', full))
                    (pk if side_a else pf)[full] = True
                    continue
                knee = side_a == knee_a
                out.append((f'sq{i}:{"knee" if knee else "far"}', 'checker-square', full))
                (pk if knee else pf)[full] = True
        names = ('a-cores', 'b-cores') if side else ('knee-cores', 'far-cores')
        if pk.any():
            out.append((names[0], 'checker-pooled', pk))
        if pf.any():
            out.append((names[1], 'checker-pooled', pf))
    elif kind in ('impulse', 'patch'):
        is_fg = (raw == np.array(spec['foreground'])).all(-1)
        lab, n = ndimage.label(is_fg)
        dist_out = ndimage.distance_transform_edt(~is_fg) / s
        dist_in = ndimage.distance_transform_edt(is_fg) / s
        size = spec['size']
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            sq = lab == i
            core = sq & (dist_in >= min(1.0, size / 4.0) + 0.5 / s) & m
            if not core.any():
                continue
            if core.sum() >= 1:
                out.append((f'p{i}:core', 'patch-core', core))
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
    flat = img.reshape(-1, img.shape[2]) if img.ndim == 3 else img.reshape(-1)
    for name, kind, r in pops:
        v = flat[r]
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
