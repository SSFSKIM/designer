"""W42 G0 instrument: the fitter (charter clause 6: least squares and minimax, equal weight per cell; a family
with width parameters is non-linear, so its search is a bounded deterministic multistart, stated LOCAL).

The parameters of a fit are split in two:
- the OUTER parameters (widths, scales, supports) move blurs, so each evaluation re-renders every cell; they
  are searched by bounded Powell from a declared start list, the best local optimum kept;
- lam is INNER and per endpoint: it acts after the blurs, so for fixed outer parameters it is a cheap 1-D
  golden-section search on cached maps.

A LAYOUT says which outer parameter is shared across which endpoints, which is how the three nested levels of
k are declared: `k@global` (one k for all four endpoints), `k@endpoint` (LT-1k) and `k_n@endpoint` +
`k_w@endpoint` (LT-2k), with `k@scheme` (the rival "k shared across poses") between the first two.
"""
import numpy as np
from scipy import optimize

import forward as F
import regions as R

LAM_BOUNDS = (-0.5, 1.6)


def cell_param(layout_values, name_scope, ep):
    """The value a cell of endpoint `ep` reads for an outer parameter declared at a scope."""
    name, scope = name_scope
    key = {'global': 'all', 'scheme': ep.split('-')[0], 'pose': ep.split('-')[1], 'endpoint': ep}[scope]
    return layout_values[(name, key)]


class Problem:
    """cells: list of forward.Cell with .y set (observed codes on a canvas image); fam: forward.Family;
    layout: [(param, scope)] for the outer parameters; bounds: {param: (lo, hi)}; fixed: {param: value}
    applied to every cell (e.g. lam for a lam-fixed fit)."""

    def __init__(self, cells, fam, layout, bounds, fixed=None, lam_free=True, trust='none'):
        self.cells, self.fam, self.layout, self.bounds = cells, fam, layout, bounds
        self.fixed = dict(fixed or {})
        self.lam_free = lam_free and 'lam' not in self.fixed
        self.keys = []
        for name, scope in layout:
            groups = sorted({{'global': 'all', 'scheme': c.ep.split('-')[0], 'pose': c.ep.split('-')[1],
                              'endpoint': c.ep}[scope] for c in cells})
            self.keys += [((name, g), (name, scope)) for g in groups]
        # Where T is not measured (memo C's stand-in above input 128-140 in dark at spans >= 96) a pixel may be
        # left out, but never by its OBSERVED code: selecting on the response truncates the knee side and
        # biases lam (a dark lam read 1.6 at the bound against a truth of 0.9 that way). trust='none' fits
        # every pixel in output space, where a flat T simply carries little weight; trust='model' keeps the
        # pixels whose PREDICTED input is trusted, re-selected at every evaluation. The synthetic proofs use
        # 'none': the stand-in T is a known function everywhere. A cell with no usable pixel is excluded and
        # named.
        self.trust = trust
        self.obs, kept, self.excluded = [], [], []
        for c in cells:
            y = c.y[c.mask]
            ok = np.isfinite(y) if y.ndim == 1 else np.isfinite(y).all(-1)
            if trust == 'observed':
                ok &= c.T.trusted(y if y.ndim == 1 else y.mean(-1))
            if ok.sum() == 0:
                self.excluded.append(c.id)
                continue
            kept.append(c)
            self.obs.append((y, ok))
        self.cells = cells = kept
        self.eps = sorted({c.ep for c in cells})

    def params_for(self, x, c):
        vals = {k: v for (k, _), v in zip(self.keys, x)}
        p = dict(self.fixed)
        for name, scope in self.layout:
            p[name] = cell_param(vals, (name, scope), c.ep)
        return F.expand(self.fam, p)

    def _maps(self, x):
        return [F.maps(c, self.fam, self.params_for(x, c)) if self.fam.order != 'blurlast' else None
                for c in self.cells]

    def _cell_mse(self, c, mp, obs, lam, x):
        y, ok = obs
        if self.fam.order == 'blurlast':
            p = self.params_for(x, c)
            p['lam'] = lam
            pred = F.render(c, self.fam, p)
        else:
            pred = F.compose(c, self.fam, mp, lam)
        if self.trust == 'model' and c.T.trust_below is not None:
            ok = ok & (c.T.inv(pred if pred.ndim == 1 else pred.mean(-1)) < c.T.trust_below)
            if not ok.any():
                return 0.0
        e = (pred - y)[ok]
        return float(np.mean(e ** 2))

    def inner(self, x, mps=None):
        """Per endpoint lam (golden section) for fixed outer x; returns (lams, per-cell mse list)."""
        mps = mps if mps is not None else self._maps(x)
        lams, mses = {}, [None] * len(self.cells)
        for ep in self.eps:
            idx = [i for i, c in enumerate(self.cells) if c.ep == ep]
            if not self.lam_free:
                lam = self.fixed['lam']
            else:
                f = lambda lam: sum(self._cell_mse(self.cells[i], mps[i], self.obs[i], lam, x) for i in idx)
                lam = golden(f, *LAM_BOUNDS, tol=2e-4)
            lams[ep] = lam
            for i in idx:
                mses[i] = self._cell_mse(self.cells[i], mps[i], self.obs[i], lam, x)
        return lams, mses

    def objective(self, x):
        _, mses = self.inner(x)
        return float(np.mean(mses))

    def fit(self, starts, xtol=1e-4, ftol=1e-9, maxfev=400):
        """Bounded deterministic multistart (LOCAL): Powell from each declared start, best kept."""
        lo = np.array([self.bounds[k[1][0]][0] for k in self.keys])
        hi = np.array([self.bounds[k[1][0]][1] for k in self.keys])
        best = None
        for s0 in starts:
            x0 = np.array([s0[k[1][0]] if isinstance(s0, dict) else s0 for k in self.keys], float)
            x0 = np.clip(x0, lo, hi)
            if len(x0) == 1:
                r = optimize.minimize_scalar(lambda v: self.objective(np.array([v])), bounds=(lo[0], hi[0]),
                                             method='bounded', options=dict(xatol=xtol, maxiter=maxfev))
                x, fun = np.array([r.x]), r.fun
                # bounded Brent is local: confirm against the start's neighbourhood
            else:
                r = optimize.minimize(self.objective, x0, method='Powell', bounds=list(zip(lo, hi)),
                                      options=dict(xtol=xtol, ftol=ftol, maxfev=maxfev))
                x, fun = r.x, r.fun
            if best is None or fun < best[1]:
                best = (x, fun)
        x = best[0]
        lams, mses = self.inner(x)
        rms = np.sqrt(np.array(mses))
        return dict(x={f'{k[0][0]}@{k[0][1]}': float(v) for k, v in zip(self.keys, x)}, lam=lams,
                    pooled=float(np.sqrt(np.mean(mses))), per_cell={f'{c.ep}|{c.id}': float(r) for c, r in zip(self.cells, rms)},
                    max_cell=float(rms.max()), xvec=x)

    def predictions(self, x, lams):
        out = []
        for c in self.cells:
            p = self.params_for(x, c)
            p['lam'] = lams[c.ep]
            out.append(F.render(c, self.fam, p))
        return out


def golden(f, a, b, tol=1e-4, it=80):
    g = (np.sqrt(5) - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(it):
        if abs(b - a) < tol:
            break
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = f(d)
    return (a + b) / 2


def region_misfit(cells, preds, truths):
    """Max |region statistic of prediction - region statistic of truth| over every cell and population."""
    worst, where = 0.0, None
    for c, p, t in zip(cells, preds, truths):
        pops = R.populations(c)
        sp, st = R.stats_from_masked(c, p, pops), R.stats_from_masked(c, t, pops)
        for k in st:
            dv = abs(sp[k] - st[k])
            if dv > worst:
                worst, where = dv, f'{c.id}:{k}'
    return worst, where


def interval(problem, x, name_key, lams=None, tol=0.10, span=(0.5, 1.5), n=41):
    """The range of one outer parameter over which the pooled rms stays within +tol codes of its minimum,
    the others held (a profile, not a re-fit): the reader's resolution on that parameter."""
    keys = [f'{k[0][0]}@{k[0][1]}' for k in problem.keys]
    i = keys.index(name_key)
    base = np.sqrt(problem.objective(x))
    lo, hi = problem.bounds[problem.keys[i][1][0]]
    grid = np.linspace(max(lo, x[i] * span[0]), min(hi, x[i] * span[1]), n)
    ok = []
    for v in grid:
        xx = x.copy()
        xx[i] = v
        if np.sqrt(problem.objective(xx)) <= base + tol:
            ok.append(v)
    return (min(ok), max(ok)) if ok else (float('nan'), float('nan'))
