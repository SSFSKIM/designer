"""W42 G0 instrument: what the family proofs (proof1_families.py, proof2_separation.py) share: the truth and
start configurations of every declared family, the cells each family's parameters are read from, and the
survival-resolution measure.

The cells each family is fitted on are the bed families the charter says answer it (Design, "The rival
families", column "answered by"; "What existing cells cannot identify"). Fitting a subset is conservative for
separation: adding cells can only raise the best misfit a wrong family can reach, so a pair separated on the
subset is separated on the whole bed, and a pair unresolved on the subset is re-read on the whole bed before
it is reported unresolved.
"""
import os

import numpy as np

import bed
import families as FA
import fitting as Fi
import forward as F
import regions as R

LETTERS = {
    'LT': ('B', "B'", 'C', 'D'), 'LT-2k': ("B'", 'C'), 'free-sn': ("B'", 'C'), 'R1': ('B',),
    'W-shape': ('B', 'C', 'D'), 'W-canvas': ('B', 'C', 'D'), 'W-tails': ('B', 'C', 'D'), 'K2': ('B', 'C', 'D'),
    'C-linear': ('B', "B'", 'D'), 'knee-luma': ('E',), 'LT+bleed': ("B'", 'C', 'D'),
    'LT+bleed-own': ("B'", 'C', 'D'), 'LT+bleed-lit-pre': ("B'", 'C', 'D'), 'LT+bleed-lit-post': ("B'", 'C', 'D'),
    'LT+bleed-lit-own-pre': ("B'", 'C', 'D'), 'LT+bleed-lit-own-post': ("B'", 'C', 'D'), 'edge-swap': ('D', 'C'),
    'null-mix': ("B'", 'C'), 'null-texel': ("B'", 'C'), 'null-dev': ("B'", 'C'), 'null-R2': ('B', "B'"),
    'null-boxfloor': ("B'",),
}
EXTRA_BOUNDS = {name: dict(extra) for name, (_, extra, *_rest) in FA.FAMILIES.items()}


def truth(name, ep, k=None, lam=None):
    """The parameter dict a family is rendered at in the proofs."""
    pose = ep.split('-')[1]
    p = {'k': FA.TRUTH_K[ep] if k is None else k, 'lam': FA.TRUTH_LAM[ep] if lam is None else lam}
    ex = FA.TRUTH_EXTRA.get(name, {})
    if name == 'free-sn':
        for s, v in ex[pose].items():
            p[f'sn_{pose}_{s}'] = v
    else:
        p.update(ex)
    if name == 'LT-2k':
        p.pop('k')
    return p


def layout_for(name, ep, level='k@endpoint'):
    pose = ep.split('-')[1]
    if name == 'LT-2k':
        lay = list(FA.LAYOUTS['k2@endpoint'])
    elif name == 'free-sn':
        lay = FA.free_layout(pose)
    else:
        lay = list(FA.LAYOUTS[level])
    lay += [(pn, 'endpoint') for pn, _ in EXTRA_BOUNDS[name].items()]
    return lay


def bounds_for(name):
    b = {'k': FA.K_BOUNDS, 'k_n': FA.K_BOUNDS, 'k_w': FA.K_BOUNDS}
    if name == 'null-dev':
        # in device px the same widths need about twice the scale at 2x (k 4.0-4.2 for memo E's readings), so
        # the shared bound would cap the null short of its best fit and inflate its misfit (the first run did)
        b['k'] = (0.8, 9.0)
    for pose in ('rest', 'inactive'):
        for s in FA.FREE_SPANS:
            b[f'sn_{pose}_{s}'] = (0.0, 14.0)
    b.update(EXTRA_BOUNDS[name])
    return b


def starts_for(name, ep, n_outer):
    """Declared starts: the plausible centre of each outer parameter; a second start for searches of at
    most two outer parameters (the search is LOCAL, and this is its multistart). No start sits on a proof truth
    (families.TRUTH_*): until the review of b151aff4 W-tails' s2 (40), the bleed's k_b (2.0) and free-sn's
    receded ordinates at 128 and 160 (6.5, 7.5) did, so those recoveries began at the answer."""
    pose = ep.split('-')[1]
    base = {'k': 2.0, 'k_n': 2.0, 'k_w': 2.0, 'mu': 8.0, 's2': 28.0, 'a': 0.15, 'sk': 10.0, 'k_b': 1.6}
    for s, v in zip(FA.FREE_SPANS, (1.0, 2.0, 3.0, 4.5, 5.5) if pose == 'rest' else (3.5, 4.2, 4.8, 5.8, 6.8)):
        base[f'sn_{pose}_{s}'] = v
    alt = dict(base, k=2.6, k_n=1.5, k_w=2.6, mu=0.0, s2=60.0, a=0.35, sk=20.0, k_b=2.5)
    return [base] if n_outer > 2 else [base, alt]


# The active mask's kernel support: 'n' (the revised ruling 3's primary, refraction after the blur; every family
# fitter) unless W42_KERNEL names 'w' (the fallback mask of the rival order, 53.6 pt; its record). Read from the
# environment so that spawned pool workers, which re-import this module, see the caller's choice.
KERNEL = os.environ.get('W42_KERNEL', 'n')


def cells_for(name, ep, scales=(2,), rgb=False, kernel=None):
    out = []
    for s in scales:
        out += bed.cells(ep, s, letters=LETTERS[name], rgb=rgb, kernel=kernel or KERNEL)
    return out


def render_truth(cells, fam, p, seed=0):
    """Quantised synthetic captures (in place on each cell) and the exact renders, per cell."""
    exact = []
    for i, c in enumerate(cells):
        exact.append(F.render(c, fam, F.expand(fam, p)))
        F.synth(c, fam, p, seed=seed + i)
    return exact


def trusted_stats(cell, st, trust='none'):
    """Region statistics scored in the separation proof. With the fits' trust='none' (the stand-in T is known
    everywhere) every statistic counts; with 'model' the statistics whose truth level lies where T is not
    measured are dropped."""
    tb = cell.T.trust_below
    if trust == 'none' or tb is None:
        return st
    return {k: v for k, v in st.items() if cell.T.inv(v) < tb}


def stats_list(cells, preds):
    return [trusted_stats(c, R.stats_from_masked(c, v, R.populations(c))) for c, v in zip(cells, preds)]


def survival_misfit(cells, preds, truth_stats):
    worst, where = 0.0, None
    for c, v, st in zip(cells, preds, truth_stats):
        sp = R.stats_from_masked(c, v, R.populations(c))
        for k, tv in st.items():
            d = abs(sp[k] - tv)
            if d > worst:
                worst, where = d, f'{c.id}:{k}'
    return worst, where


def minimax_refine(prob, x0, lams0, truth_stats, maxfev=120):
    """Refine a least-squares optimum by minimax on the region statistics of the truth's exact render: the
    outer parameters and every endpoint's lam searched together (Nelder-Mead from the LS point, bounded by
    clipping). Returns (x, lams, s, where)."""
    from scipy import optimize
    eps = prob.eps
    lo = np.array([prob.bounds[k[1][0]][0] for k in prob.keys] + [Fi.LAM_BOUNDS[0]] * len(eps))
    hi = np.array([prob.bounds[k[1][0]][1] for k in prob.keys] + [Fi.LAM_BOUNDS[1]] * len(eps))
    n = len(prob.keys)
    pops = [R.populations(c) for c in prob.cells]

    def f(z):
        z = np.clip(z, lo, hi)
        x, lams = z[:n], dict(zip(eps, z[n:]))
        worst = 0.0
        for c, st, pp in zip(prob.cells, truth_stats, pops):
            p = prob.params_for(x, c)
            p['lam'] = lams[c.ep]
            sp = R.stats_from_masked(c, F.render(c, prob.fam, p), pp)
            worst = max([worst] + [abs(sp[k] - v) for k, v in st.items()])
        return worst
    z0 = np.concatenate([x0, [lams0[e] for e in eps]])
    step = np.maximum(0.02 * np.abs(z0), 0.02)
    simplex = [z0] + [z0 + np.eye(len(z0))[i] * step[i] for i in range(len(z0))]
    r = optimize.minimize(f, z0, method='Nelder-Mead',
                          options=dict(maxfev=maxfev, xatol=1e-4, fatol=1e-3, initial_simplex=simplex))
    z = np.clip(r.x, lo, hi)
    x, lams = z[:n], dict(zip(eps, z[n:]))
    preds = []
    for c in prob.cells:
        p = prob.params_for(x, c)
        p['lam'] = lams[c.ep]
        preds.append(F.render(c, prob.fam, p))
    s, where = survival_misfit(prob.cells, preds, truth_stats)
    return x, lams, s, where


def verdict(s):
    return 'DISTINGUISHED' if s > 1.5 else ('UNRESOLVED' if s < 0.5 else 'MARGINAL')
