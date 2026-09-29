"""W42 G0 instrument: family C's patch and annulus reader (charter Design, "The instrument").

A single square patch (or each square of an impulse lattice) is read in two ways.

Statistics (clause 6's populations for family C): the patch CORE, the pixels at least min(1, size / 4) pt
inside the square, and the surround ANNULI, rings of distance to the patch's own edge in PATCH_RINGS pt, each
restricted to the reader's pixel mask; plus a finer radial profile (medians in 1-pt rings to 16 pt, then
4-pt rings to 48 pt) that the eye and the halo stop read.

Model read: the local regression of read_local on the pixels within R pt of the patch, with the narrow width
sigma_n (pt, flat over the window), the wide width sigma_w (pt) and W's support searched, lam and w free or
given. The core fixes sigma_n (a bright patch in light, or a dark one in dark, is the far side the knee leaves
linear); the annulus fixes sigma_w and its reach, because there the lighten (darken) lifts the surround toward
W: the halo. Two polarities read together separate the knee from the width. A second Gaussian in W (the
tails rival) is an optional extra read, reported as the rms it buys.

lam is read here only on synthetic renders of a declared family. On real pixels (proof 3, vitrea's impulse
cells) the free-lam read is not identified: on a sparse lattice the hinge column is nearly collinear with C
and W, so any kernel-shape misfit lands in lam (|lam| up to 46 on a system with no knee). The protocol
therefore reads the widths with lam GIVEN, from the per-cell lam reader on the checkers (read_lambda).

sigma_n read here is the narrow blur ON TOP of the capture floor in the native reading (the basis maps carry
the 0.8-device-px floor), and the whole narrow width in the linear reading (vitrea has no floor). At t = 0 in
the active pose LT's sigma_n is 0 and the only width is the floor; a relative bar is undefined there, so the
reader also reports the effective width sqrt((sigma_n s)^2 + F^2) in device px.
"""
import numpy as np
from scipy import ndimage

import geometry as G
import read_local as L

PATCH_RINGS = (0.0, 2.0, 4.0, 8.0, 16.0, 32.0, 48.0)
PROFILE = tuple(np.r_[np.arange(0, 17, 1.0), np.arange(20, 49, 4.0)])
SN_GRID = (0.0, 0.3, 0.7, 1.2, 2.0, 3.0, 4.5, 6.0, 8.0)
SW_GRID = (6.0, 9.0, 12.0, 16.0, 20.0, 26.0, 34.0)
SUPPORTS = (('box', 'clamp', None), ('box', 'norm', None), ('canvas', 'clamp', None))


def patch_masks(cell):
    """Foreground patches of a 'patch' or 'impulse' backdrop: (labels, count, is_fg)."""
    spec = cell.bg_spec
    B = cell.B if cell.B.ndim == 2 else G.luma(cell.B * 255) / 255
    fg = float(np.dot(spec['foreground'], G.W709))
    is_fg = np.abs(B * 255 - fg) < 0.5
    lab, n = ndimage.label(is_fg)
    return lab, n, is_fg


def patch_centres(cell):
    lab, n, _ = patch_masks(cell)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        out.append((i, (ys.mean() + 0.5) / cell.scale, (xs.mean() + 0.5) / cell.scale))
    return out


def reader_mask(cell, R=48.0, d_in=None, which=None):
    """Pixels within R pt of the patch (or of patch label `which`) and at least d_in pt inside the shape
    (default: the cell's deep mask)."""
    lab, n, is_fg = patch_masks(cell)
    src = is_fg if which is None else lab == which
    dist = ndimage.distance_transform_edt(~src) / cell.scale
    inside = cell.mask if d_in is None else cell.d <= -d_in
    return inside & (dist <= R)


def populations(cell, pix):
    """Core and rings per patch whose square lies wholly inside `pix`."""
    lab, n, is_fg = patch_masks(cell)
    s, size = cell.scale, cell.bg_spec['size']
    dist_in = ndimage.distance_transform_edt(is_fg) / s
    dist_out = ndimage.distance_transform_edt(~is_fg) / s
    out = []
    for i in range(1, n + 1):
        sq = lab == i
        if (sq & ~pix).any():
            continue
        core = sq & (dist_in >= min(1.0, size / 4.0) + 0.5 / s) & pix
        if core.sum() == 0:
            continue
        out.append((f'p{i}:core', 'patch-core', core))
        d_own = ndimage.distance_transform_edt(~sq) / s
        own = d_own <= dist_out + 1e-9
        for a, b in zip(PATCH_RINGS[:-1], PATCH_RINGS[1:]):
            ring = own & ~is_fg & (d_own > a) & (d_own <= b) & pix
            if ring.sum() >= 12:
                out.append((f'p{i}:ring{a:g}-{b:g}', 'patch-ring', ring))
    return out


def statistics(cell, img, pix):
    return {nm: float(np.nanmedian(img[r])) for nm, _, r in populations(cell, pix)}


def radial_profile(cell, img, pix, which=None):
    """Median output by distance to the patch edge (negative inside), for the halo stop and the eye."""
    lab, n, is_fg = patch_masks(cell)
    src = is_fg if which is None else lab == which
    s = cell.scale
    dd = ndimage.distance_transform_edt(~src) / s - ndimage.distance_transform_edt(src) / s
    y = L.luma_img(img)
    out = []
    edges = (-8.0,) + PROFILE
    for a, b in zip(edges[:-1], edges[1:]):
        r = pix & (dd > a) & (dd <= b) & np.isfinite(y)
        if r.sum() >= 4:
            out.append((a, b, float(np.median(y[r])), int(r.sum())))
    return out


def _parts(cells_pix, reading, sn, sw, support, edge, mu, kn=None, s2=None, a=0.0):
    parts = []
    for cell, pix in cells_pix:
        key = ('_rp', reading, id(pix))
        if key not in cell._cache:
            b = L.Basis(cell, pix, reading)
            cell._cache[key] = (b, L.observed(cell, pix, reading))
        b, (M, wt, ok) = cell._cache[key]
        C = b.C(kn=kn) if kn is not None else b.C(sn=sn)
        W = b.W(sw, support, edge, mu, s2, a)
        parts.append((M, wt, L.model_ok(cell, reading, ok, C, W), C, W, b.sg))
    return parts


def read(cells_pix, reading='native', sn=None, sw=None, lam=None, w=None, supports=SUPPORTS, kn=None,
         intervals=True):
    """Model read over [(cell, pix)] sharing every coefficient. sn/sw None = searched; lam/w None = free.
    Returns per support the best widths, lam, w, rms and profile intervals, and the ranking."""
    res = {}
    for support, edge, mu in supports:
        free = [n for n, v in (('sn', sn if kn is None else 0.0), ('sw', sw)) if v is None]

        def obj(x, support=support, edge=edge, mu=mu):
            vals = dict(zip(free, x))
            s_n = vals.get('sn', sn)
            s_w = vals.get('sw', sw)
            if (s_n is not None and s_n < 0) or s_w <= 0.5:
                return 1e6
            return L.regress(_parts(cells_pix, reading, s_n, s_w, support, edge, mu, kn), lam, w)['rms']

        if free:
            grid = [[v] for v in (SN_GRID if free[0] == 'sn' else SW_GRID)] if len(free) == 1 else \
                [[a, b] for a in SN_GRID for b in SW_GRID if a < b]
            bounds = [(0.0, 20.0) if n == 'sn' else (1.0, 80.0) for n in free]
            x, v, _ = L.search(obj, grid, bounds)
        else:
            x, v = np.array([]), obj(np.array([]))
        vals = dict(zip(free, x))
        s_n, s_w = vals.get('sn', sn), vals.get('sw', sw)
        r = L.regress(_parts(cells_pix, reading, s_n, s_w, support, edge, mu, kn), lam, w)
        r.update(sn=None if kn is not None else float(s_n), sw=float(s_w), support=support, edge=edge, mu=mu)
        r['_obj'], r['_x'], r['_free'] = obj, x, free
        res[f'{support}/{edge}' + (f'/{mu:g}' if mu is not None else '')] = r
    rank = sorted(res, key=lambda k: res[k]['rms'])
    b = res[rank[0]]
    if intervals and b['_free']:
        for i, n in enumerate(b['_free']):
            b[f'{n}_iv'] = L.profile_interval(b['_obj'], b['_x'], i, n=21)
    for v in res.values():
        for k in ('_obj', '_x', '_free'):
            v.pop(k, None)
    gap = res[rank[1]]['rms'] - res[rank[0]]['rms'] if len(rank) > 1 else float('inf')
    return dict(fits=res, ranking=rank, best=b, call_gap=float(gap))


def read_tails(cells_pix, reading, sn, sw, support, edge, lam=None, w=None,
               s2_grid=(24.0, 32.0, 40.0, 48.0, 64.0), a_grid=(0.1, 0.2, 0.3, 0.4)):
    """The optional tail read: W = (1 - a) G(sw) + a G(s2), sn and sw re-searched around the one-Gaussian read."""
    best = None
    for s2 in s2_grid:
        for a in a_grid:
            def obj(x, s2=s2, a=a):
                if x[0] < 0 or x[1] <= 0.5:
                    return 1e6
                return L.regress(_parts(cells_pix, reading, x[0], x[1], support, edge, None, None, s2, a),
                                 lam, w)['rms']
            x, v, _ = L.search(obj, [[sn, sw]], [(0.0, 20.0), (1.0, 80.0)])
            if best is None or v < best['rms']:
                best = dict(rms=v, sn=float(x[0]), sw=float(x[1]), s2=s2, a=a)
    return best


def effective_dev(cell, sn_pt, reading='native'):
    F_dev = 0.4 * cell.f if reading == 'native' else 0.0
    return float(np.hypot(sn_pt * cell.scale, F_dev))
