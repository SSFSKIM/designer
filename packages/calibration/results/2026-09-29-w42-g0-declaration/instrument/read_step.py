"""W42 G0 instrument: family D's step reader (charter Design, "The instrument"; U3, and U1's far reference).

A step (the `split` kind) under the interior, or just outside the edge, is the backdrop whose response
depends most directly on WHERE W averages: far from the step the plateau reads W's far reference; across
the step the transition's shape reads the narrow and the wide widths; and a step outside the shape reads
only what the support admits (the receded margin is one device px, so a box-limited W never sees a step
8 pt outside the edge while a canvas-wide W does).

Statistics (clause 6's populations for family D, regions.py): the two plateaus and the transition bins of
signed distance to the step, inside the deep mask. For a two-level checker (vitrea's control reads
checker-64 edges) the same bins are taken against the nearest checker edge, signed toward the knee side.

Model read: the local regression of read_local over the deep mask, with W's width searched on each support
and edge mode ('canvas'/clamp, 'box'/clamp, 'box'/norm, 'shape'/norm with its margin mu searched), and the
narrow term either the declared o-law with k_n given or searched, or a width flat in depth (vitrea's form);
lam and w given or free. The supports are RANKED by rms: the support call is the first, and a call is only
made where the first and second differ by more than CALL_MARGIN code.
"""
import numpy as np
from scipy import ndimage

import geometry as G
import read_local as L
import regions as RG

CALL_MARGIN = 0.05
SUPPORTS = (('canvas', 'clamp', None), ('box', 'clamp', None), ('box', 'norm', None))
MU_GRID = (-4.0, 0.0, 4.0, 8.0, 16.0)
SW_GRID = (8.0, 12.0, 16.0, 20.0, 26.0, 34.0)
SN_GRID = (0.0, 1.0, 2.0, 4.0, 6.0, 8.0)
KN_GRID = (1.0, 1.5, 2.0, 2.5, 3.0)
BINS = (-32.0, -16.0, -8.0, -4.0, -2.0, 0.0, 2.0, 4.0, 8.0, 16.0, 32.0)


def signed_distance(cell):
    """Signed distance (pt) to the backdrop's level change: split -> coordinate minus position; checker ->
    distance to the nearest edge, positive on the far side and negative on the knee side."""
    spec, s = cell.bg_spec, cell.scale
    H, W = cell.d.shape
    if spec['kind'] == 'split':
        ys, xs = np.mgrid[0:H, 0:W]
        return ((xs if spec['axis'] == 'x' else ys) + 0.5) / s - spec['position']
    B = cell.B if cell.B.ndim == 2 else G.luma(cell.B * 255) / 255
    lev = np.round(B * 255)
    e = np.zeros(lev.shape, bool)
    e[:, 1:] |= lev[:, 1:] != lev[:, :-1]
    e[:, :-1] |= lev[:, 1:] != lev[:, :-1]
    e[1:, :] |= lev[1:, :] != lev[:-1, :]
    e[:-1, :] |= lev[1:, :] != lev[:-1, :]
    dist = ndimage.distance_transform_edt(~e) / s
    dark = lev < 0.5 * (lev.min() + lev.max())
    knee = dark if cell.scheme == 'light' else ~dark
    return np.where(knee, -dist, dist)


def statistics(cell, img):
    """The declared step populations (regions.py) for a split; the edge bins for a checker."""
    if cell.bg_spec['kind'] == 'split':
        return RG.statistics(cell, img)
    sd = signed_distance(cell)
    y = L.luma_img(img)
    out = {}
    for a, b in zip(BINS[:-1], BINS[1:]):
        r = cell.mask & (sd > a) & (sd <= b) & np.isfinite(y)
        if r.sum() >= 12:
            out[f'edge{a:g}..{b:g}'] = float(np.median(y[r]))
    return out


def _parts(cells_pix, reading, sn, kn, sw, support, edge, mu):
    parts = []
    for cell, pix in cells_pix:
        key = ('_rs', reading, id(pix), id(cell.y))
        if key not in cell._cache:
            cell._cache[key] = (L.Basis(cell, pix, reading), L.observed(cell, pix, reading))
        b, (M, wt, ok) = cell._cache[key]
        C = b.C(kn=kn) if kn is not None else b.C(sn=sn)
        W = b.W(sw, support, edge, mu)
        parts.append((M, wt, L.model_ok(cell, reading, ok, C, W), C, W, b.sg))
    return parts


def read(cells_pix, reading='native', narrow='olaw', sn=None, kn=None, sw=None, lam=None, w=None,
         supports=SUPPORTS, shape=True, intervals=True):
    """Model read over [(cell, pix)] (pix None: the deep mask) sharing every coefficient.
    narrow 'olaw': C = G(k_n 5 o(d)), k_n given (kn) or searched; 'flat': a flat sn given or searched."""
    cells_pix = [(c, c.mask if p is None else p) for c, p in cells_pix]
    opts = list(supports) + ([('shape', 'norm', m) for m in MU_GRID] if shape else [])
    res = {}
    for support, edge, mu in opts:
        nfree = 'kn' if narrow == 'olaw' and kn is None else ('sn' if narrow == 'flat' and sn is None else None)
        free = ([nfree] if nfree else []) + (['sw'] if sw is None else [])

        def obj(x, support=support, edge=edge, mu=mu):
            v = dict(zip(free, x))
            k_n = v.get('kn', kn) if narrow == 'olaw' else None
            s_n = v.get('sn', sn) if narrow == 'flat' else None
            s_w = v.get('sw', sw)
            if (k_n is not None and k_n <= 0) or (s_n is not None and s_n < 0) or s_w <= 0.5:
                return 1e6
            return L.regress(_parts(cells_pix, reading, s_n, k_n, s_w, support, edge, mu), lam, w)['rms']

        grids = {'kn': KN_GRID, 'sn': SN_GRID, 'sw': SW_GRID}
        bnds = {'kn': (0.05, 6.0), 'sn': (0.0, 20.0), 'sw': (1.0, 80.0)}
        if free:
            grid = [[a] for a in grids[free[0]]] if len(free) == 1 else \
                [[a, b] for a in grids[free[0]] for b in grids[free[1]]]
            x, v, _ = L.search(obj, grid, [bnds[n] for n in free])
        else:
            x, v = np.array([]), obj(np.array([]))
        vals = dict(zip(free, x))
        k_n = vals.get('kn', kn) if narrow == 'olaw' else None
        s_n = vals.get('sn', sn) if narrow == 'flat' else None
        s_w = vals.get('sw', sw)
        r = L.regress(_parts(cells_pix, reading, s_n, k_n, s_w, support, edge, mu), lam, w)
        r.update(kn=k_n, sn=s_n, sw=float(s_w), support=support, edge=edge, mu=mu)
        r['region_max'], r['region_where'] = region_misfit(cells_pix, reading, (s_n, k_n, s_w, support, edge, mu),
                                                           lam, w)
        r['_obj'], r['_x'], r['_free'] = obj, x, free
        res[f'{support}/{edge}' + (f'/{mu:g}' if mu is not None else '')] = r
    # the shape support's margin is itself read: keep its best mu as one option in the ranking
    shp = {k: v for k, v in res.items() if k.startswith('shape/')}
    if shp:
        kbest = min(shp, key=lambda k: shp[k]['rms'])
        res = {k: v for k, v in res.items() if not k.startswith('shape/')}
        res['shape/norm'] = dict(shp[kbest], mu_scan={k.split('/')[-1]: v['rms'] for k, v in shp.items()})
    rank = sorted(res, key=lambda k: res[k]['rms'])
    gap = res[rank[1]]['rms'] - res[rank[0]]['rms'] if len(rank) > 1 else float('inf')
    rrank = sorted(res, key=lambda k: res[k]['region_max'])
    b = res[rank[0]]
    if intervals and 'sw' in b['_free']:
        b['sw_iv'] = L.profile_interval(b['_obj'], b['_x'], b['_free'].index('sw'), rel=(0.8, 1.25), n=19)
    for v in res.values():
        for k in ('_obj', '_x', '_free'):
            v.pop(k, None)
    rgap = res[rrank[1]]['region_max'] - res[rrank[0]]['region_max'] if len(rrank) > 1 else float('inf')
    return dict(fits=res, ranking=rank, best=res[rank[0]], call=rank[0] if gap > CALL_MARGIN else None,
                call_gap=float(gap), region_ranking=rrank, region_gap=float(rgap))


def region_misfit(cells_pix, reading, args, lam, w):
    """Max |median(predicted) - median(observed)| over every cell's step (or edge) populations: where a
    support's error concentrates (near the shape's edge) the pooled rms dilutes it and this does not."""
    parts = _parts(cells_pix, reading, *args)
    fit = L.regress(parts, lam, w, predict=True)
    worst, where = 0.0, None
    for (cell, pix), part, Mp in zip(cells_pix, parts, fit['pred']):
        ok = part[2]
        idx = np.flatnonzero(pix)[ok]
        obs = np.full(cell.d.size, np.nan)
        prd = np.full(cell.d.size, np.nan)
        obs[idx] = L.luma_img(cell.y).ravel()[idx]
        prd[idx] = L.to_output(cell, Mp, reading)
        so, sp = statistics(cell, obs.reshape(cell.d.shape)), statistics(cell, prd.reshape(cell.d.shape))
        for k in so:
            if np.isfinite(so[k]) and np.isfinite(sp.get(k, np.nan)) and abs(so[k] - sp[k]) > worst:
                worst, where = abs(so[k] - sp[k]), f'{cell.id}:{k}'
    return float(worst), where
