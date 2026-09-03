"""W12 instrument: recover the lens displacement field D(u) along a straight edge of a
rounded rectangle from a checkerboard capture, without assuming its shape.

Along a line normal to a straight edge (a pixel column for the top/bottom edge, a pixel
row for the left/right edge), the checkerboard is separable: P(x, y) = ½(1 − sx(x)·sy(y))
with sx, sy ±1 square waves. A 2-D Gaussian blur of P is therefore ½(1 − (g∗sx)(x)·(g∗sy)(y)),
so along a fixed column the blurred plate is a 1-D blurred square wave scaled by the
per-line CROSS FACTOR e(σ) = (g∗sx)(x). That reduction is exact for both blur orders as
long as the warp is along the normal and depends only on the depth u, which is the
straight-edge case. Units: CSS px throughout (device px / scale).

Model per line, blur-before  : Y(u) = a + t·½(1 − Σ_c w_c e_c(σ_c) Q_c(s(u)))
              blur-after    : Y(u) = a + t·½(1 − Σ_c w_c e_c(σ_c) (g_σc ∗ q∘s)(u))
with s(u) = u + D(u), two body components (sharp σ1 free with weight 1−k, heavy σ2 = 10
CSS px with weight k — W11c's interior law), the pixel integrated over its footprint,
and D a clamped cubic B-spline on knots every 2 px from 0 to 28, pinned to 0 (value,
slope, curvature) at 28, with a second-difference penalty λ.
"""
import sys
sys.path.insert(0, '/Users/new/.claude/jobs/5c70e47f/tmp')
import json
import numpy as np
from scipy.interpolate import BSpline
from scipy.optimize import least_squares
from scipy.special import erf
from w11lib import COMP, SPAN, CANVAS, load_rgb, luma_lin, native_path, web_path, probe_path, plate_path

CX, CY = CANVAS[0] / 2, CANVAS[1] / 2
SIGMA_HEAVY = 10.0
KNOT_STEP = 2.0
KNOT_END = 28.0
FINE = 8  # fine-grid samples per CSS px


def lens_depth_px(comp, thickness=8.0, gain_max=2.6, span_min=32, span_max=96):
    """The renderer's lensDepthPx: thickness × (1 + (gainMax − 1)·smoothstep(span)) clamped to span/2."""
    span = SPAN[comp]
    t = min(max((span - span_min) / (span_max - span_min), 0.0), 1.0)
    st = t * t * (3 - 2 * t)
    return min(thickness * (1 + (gain_max - 1) * st), span * 0.5)


def landed_law(u, comp, refraction_gain=1.6):
    """vitrea's displacement at depth u (CSS px): L·gain·(1 − u/L)², zero from L inward."""
    L = lens_depth_px(comp)
    d = np.clip(np.asarray(u, dtype=float) / L, 0, 1)
    return L * refraction_gain * (1 - d) ** 2


# ---------------------------------------------------------------- geometry & lines

def contour(comp):
    w, h, r = COMP[comp]
    return dict(x0=CX - w / 2, x1=CX + w / 2, y0=CY - h / 2, y1=CY + h / 2, r=r)


def cell_index(coord, pitch, axis):
    """Checker cell index along an axis at a continuous CSS coordinate (AppKit-flipped rows)."""
    if axis == 'x':
        return np.floor(np.asarray(coord) / pitch).astype(int)
    return np.floor((CANVAS[1] - np.asarray(coord)) / pitch).astype(int)


def square_wave(coord, pitch, axis):
    """+1 on even cells, −1 on odd, along one axis."""
    return np.where(cell_index(coord, pitch, axis) % 2 == 0, 1.0, -1.0)


def plate_value(x, y, pitch):
    """The checkerboard's linear luminance at continuous (x, y): 0 where ix+iy even."""
    return 0.5 * (1 - square_wave(x, pitch, 'x') * square_wave(y, pitch, 'y'))


def cross_factor(coord, pitch, sigma, axis):
    """(g_σ ∗ sw)(coord): the blurred ±1 square wave at a fixed cross coordinate (exact, erf)."""
    coord = float(coord)
    if sigma < 1e-3:
        return float(square_wave(coord, pitch, axis))
    # boundaries within ±6σ
    if axis == 'x':
        k0 = int(np.floor((coord - 6 * sigma) / pitch)) - 1
        k1 = int(np.ceil((coord + 6 * sigma) / pitch)) + 1
        total = 0.0
        for k in range(k0, k1 + 1):
            lo, hi = k * pitch, (k + 1) * pitch
            sign = 1.0 if k % 2 == 0 else -1.0
            total += sign * 0.5 * (erf((hi - coord) / (sigma * np.sqrt(2))) - erf((lo - coord) / (sigma * np.sqrt(2))))
        return total
    # y axis: cell k covers y in (H − (k+1)p, H − kp]
    H = CANVAS[1]
    k0 = int(np.floor((H - coord - 6 * sigma) / pitch)) - 1
    k1 = int(np.ceil((H - coord + 6 * sigma) / pitch)) + 1
    total = 0.0
    for k in range(k0, k1 + 1):
        lo, hi = H - (k + 1) * pitch, H - k * pitch
        sign = 1.0 if k % 2 == 0 else -1.0
        total += sign * 0.5 * (erf((hi - coord) / (sigma * np.sqrt(2))) - erf((lo - coord) / (sigma * np.sqrt(2))))
    return total


class EdgeLines:
    """The pixel lines normal to one straight edge of a cell, with everything the model needs."""

    def __init__(self, Y, comp, edge, pitch, scale, u_min=-4.0, u_max=40.0, margin=4.0, half_width=None):
        self.comp, self.edge, self.pitch, self.scale = comp, edge, pitch, scale
        c = contour(comp)
        H, W = Y.shape
        half_width = pitch / 4 if half_width is None else half_width
        if edge in ('top', 'bottom'):
            lo, hi = c['x0'] + c['r'] + margin, c['x1'] - c['r'] - margin
            cols = np.arange(W)
            xs = (cols + 0.5) / scale
            centres = (np.floor(xs / pitch) + 0.5) * pitch
            keep = (xs >= lo) & (xs <= hi) & (np.abs(xs - centres) <= half_width)
            self.cross = xs[keep]
            self.cross_axis, self.along_axis = 'x', 'y'
            rows = np.arange(H)
            ys = (rows + 0.5) / scale
            if edge == 'top':
                u = ys - c['y0']; self.src = lambda s: c['y0'] + s
            else:
                u = c['y1'] - ys; self.src = lambda s: c['y1'] - s
            sel = (u >= u_min) & (u <= u_max)
            self.u = u[sel]
            self.Y = Y[np.ix_(rows[sel], cols[keep])].T  # lines × pixels
        else:
            lo, hi = c['y0'] + c['r'] + margin, c['y1'] - c['r'] - margin
            rows = np.arange(H)
            ys = (rows + 0.5) / scale
            # cell centres along y: cell k covers (H − (k+1)p, H − kp]
            k = np.floor((CANVAS[1] - ys) / pitch)
            centres = CANVAS[1] - (k + 0.5) * pitch
            keep = (ys >= lo) & (ys <= hi) & (np.abs(ys - centres) <= half_width)
            self.cross = ys[keep]
            self.cross_axis, self.along_axis = 'y', 'x'
            cols = np.arange(W)
            xs = (cols + 0.5) / scale
            if edge == 'left':
                u = xs - c['x0']; self.src = lambda s: c['x0'] + s
            else:
                u = c['x1'] - xs; self.src = lambda s: c['x1'] - s
            sel = (u >= u_min) & (u <= u_max)
            self.u = u[sel]
            self.Y = Y[np.ix_(rows[keep], cols[sel])]
        order = np.argsort(self.u)
        self.u = self.u[order]; self.Y = self.Y[:, order]
        self.n_lines = len(self.cross)
        self.pix = 1.0 / scale
        # fine grid over the padded u range (padding for blur-after and for the pixel footprint)
        pad = 3 * SIGMA_HEAVY + 2
        self.fine_u = np.arange(self.u.min() - 0.5 * self.pix - pad, self.u.max() + 0.5 * self.pix + pad, 1.0 / FINE)
        # per-pixel footprint indices on the fine grid
        self.foot = [np.where((self.fine_u >= ui - 0.5 * self.pix - 1e-9) & (self.fine_u < ui + 0.5 * self.pix - 1e-9))[0] for ui in self.u]
        self.foot_len = np.array([len(f) for f in self.foot])
        assert self.foot_len.min() >= FINE // scale - 1, self.foot_len
        # the along-line square wave in SOURCE coordinate, and the sharp plate self-test
        self.q = lambda s: square_wave(self.src(s), pitch, self.along_axis)
        self.cross_wave = square_wave(self.cross, pitch, self.cross_axis)  # per line, sharp

    def cross_factors(self, sigma):
        return np.array([cross_factor(cv, self.pitch, sigma, self.cross_axis) for cv in self.cross])

    def sharp_plate(self, u):
        """P along every line at depth u (lines × u), the sharp reference for self-tests."""
        return 0.5 * (1 - self.cross_wave[:, None] * self.q(np.asarray(u))[None, :])


# ---------------------------------------------------------------- spline basis

def spline_basis(u):
    """Design matrix of the clamped cubic B-spline on knots 0,2,…,28 for depths u (clipped to [0, 28]);
    returns (B, n_free) with the last three coefficients pinned to zero (D = D' = D'' = 0 at 28)."""
    inner = np.arange(0, KNOT_END + 1e-9, KNOT_STEP)
    t = np.concatenate([[0, 0, 0], inner, [KNOT_END, KNOT_END, KNOT_END]])
    uu = np.clip(np.asarray(u, dtype=float), 0, KNOT_END - 1e-9)
    M = BSpline.design_matrix(uu, t, 3).toarray()
    return M[:, :-3], M.shape[1] - 3


def second_difference(n):
    """Second differences over the free coefficients plus the three pinned zeros, so the penalty also
    holds the curve smoothly to zero at the last knot."""
    full = n + 3
    P = np.zeros((full - 2, full))
    for i in range(full - 2):
        P[i, i], P[i, i + 1], P[i, i + 2] = 1, -2, 1
    return P[:, :n]  # pinned columns dropped (they multiply zeros)


def fit_spline_to_curve(u, D, lam=1e-3):
    """Least-squares spline coefficients for a given curve (used for restarts)."""
    B, n = spline_basis(u)
    P = second_difference(n)
    A = np.vstack([B, lam * P]); b = np.concatenate([D, np.zeros(P.shape[0])])
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    return c


# ---------------------------------------------------------------- the model

class LineModel:
    def __init__(self, lines: EdgeLines, order='before', heavy=True, u_fit=(1.0, 40.0), lam=0.01):
        self.L = lines; self.order = order; self.heavy = heavy; self.lam = lam
        self.B, self.n = spline_basis(np.maximum(lines.fine_u, 0.0))
        self.P = second_difference(self.n)
        self.fit_mask = (lines.u >= u_fit[0]) & (lines.u <= u_fit[1])
        # blur kernels on the fine grid are built per σ
        self._q_cache = {}

    # parameter vector: [a, t, k, sigma1, c_1..c_n]
    def unpack(self, p):
        a, t, k, s1 = p[0], p[1], p[2], p[3]
        c = p[4:]
        return a, t, k, s1, c

    def D_of(self, c):
        return self.B @ c

    def _gauss(self, sigma):
        r = int(np.ceil(4 * sigma * FINE))
        x = np.arange(-r, r + 1) / FINE
        g = np.exp(-x * x / (2 * sigma * sigma)); return g / g.sum()

    def component(self, sigma, s, wave_sharp):
        """The blurred along-line wave for one component, on the fine grid (fine,)."""
        if self.order == 'before':
            # blur the source square wave on a fine source grid, then sample at s
            smin, smax = s.min() - 5 * sigma - 1, s.max() + 5 * sigma + 1
            sg = np.arange(smin, smax, 1.0 / FINE)
            qg = self.L.q(sg)
            Qg = np.convolve(qg, self._gauss(sigma), mode='same')
            return np.interp(s, sg, Qg)
        # blur-after: warp the sharp wave onto the screen grid, then blur along u
        return np.convolve(wave_sharp, self._gauss(sigma), mode='same')

    def predict(self, p, return_fine=False):
        a, t, k, s1, c = self.unpack(p)
        D = self.D_of(c)
        s = self.L.fine_u + D
        wave_sharp = self.L.q(s)
        comps = [(1 - k if self.heavy else 1.0, s1)]
        if self.heavy:
            comps.append((k, SIGMA_HEAVY))
        fine = np.zeros((self.L.n_lines, len(self.L.fine_u)))
        for w, sigma in comps:
            if w <= 0:
                continue
            Q = self.component(sigma, s, wave_sharp)
            e = self.L.cross_factors(sigma)
            fine += w * e[:, None] * Q[None, :]
        fine = a + t * 0.5 * (1 - fine)
        if return_fine:
            return fine
        out = np.empty((self.L.n_lines, len(self.L.u)))
        for j, f in enumerate(self.L.foot):
            out[:, j] = fine[:, f].mean(axis=1)
        return out

    def residuals(self, p):
        pred = self.predict(p)
        r = (pred - self.L.Y)[:, self.fit_mask].ravel() / np.sqrt(self.L.n_lines)
        pen = self.lam * (self.P @ p[4:])
        return np.concatenate([r, pen])

    def rms(self, p):
        pred = self.predict(p)
        r = (pred - self.L.Y)[:, self.fit_mask]
        return float(np.sqrt(np.mean(r * r)))

    def rms_by_u(self, p):
        pred = self.predict(p)
        r = (pred - self.L.Y)
        return self.L.u, np.sqrt(np.mean(r * r, axis=0))

    def bounds(self):
        lo = [-0.5, 0.0, 0.0, 0.3] + [-15.0] * self.n
        hi = [1.5, 2.0, 1.0, 8.0] + [80.0] * self.n
        if not self.heavy:
            lo[2], hi[2] = 0.0, 1e-9
        return np.array(lo), np.array(hi)

    def fit(self, D_inits, a=0.5, t=0.4, k=0.3, s1=1.5, verbose=False):
        best = None
        lo, hi = self.bounds()
        for D0 in D_inits:
            c0 = fit_spline_to_curve(np.maximum(self.L.fine_u, 0.0), D0(np.maximum(self.L.fine_u, 0.0)))
            c0 = np.clip(c0, lo[4:] + 1e-6, hi[4:] - 1e-6)
            p0 = np.concatenate([[a, t, min(max(k, 1e-6), 1 - 1e-6) if self.heavy else 0.0, s1], c0])
            p0 = np.clip(p0, lo + 1e-9, hi - 1e-9)
            res = least_squares(self.residuals, p0, bounds=(lo, hi), method='trf', x_scale='jac', max_nfev=400)
            r = self.rms(res.x)
            if verbose:
                print(f'   restart rms {r:.5f} a {res.x[0]:.3f} t {res.x[1]:.3f} k {res.x[2]:.2f} σ {res.x[3]:.2f}')
            if best is None or r < best[0]:
                best = (r, res.x)
        return best[1], best[0]

    def constraint(self, p):
        """How strongly the data constrain D at each depth: t·|∂model/∂s| averaged over lines (per CSS px)."""
        a, t, k, s1, c = self.unpack(p)
        eps = 0.25
        p1 = p.copy(); p1[4:] = c
        f0 = self.predict(p)
        # shift D by eps everywhere via a tiny change of the spline: approximate with finite difference on s
        D = self.D_of(c) + eps
        # rebuild prediction with shifted s
        saved = self.D_of
        self.D_of = lambda cc: D
        f1 = self.predict(p)
        self.D_of = saved
        return self.L.u, np.mean(np.abs(f1 - f0), axis=0) / eps


# ---------------------------------------------------------------- parametric forms

def quadratic_form(u, S, L):
    d = np.clip(np.asarray(u, dtype=float) / L, 0, 1)
    return S * (1 - d) ** 2


def bevel_form(u, L, T, n, q=1.0):
    """Physical bevel: tilt sin φ = (1 − u/L)^q for u < L (circular when q = 1); remaining depth
    h = max(0, T − L + L cos φ); Snell at index n; D = h·tan(φ − asin(sin φ / n))."""
    u = np.asarray(u, dtype=float)
    x = np.clip(1 - u / L, 0, 1)
    sphi = np.clip(x ** q, 0, 1 - 1e-9)
    phi = np.arcsin(sphi)
    theta = np.arcsin(sphi / n)
    h = np.maximum(0.0, T - L + L * np.cos(phi))
    return np.where(u < L, h * np.tan(phi - theta), 0.0)


def fit_form_to_curve(u, D, form, p0, bounds, weights=None):
    w = np.ones_like(D) if weights is None else weights
    def res(p):
        return (form(u, *p) - D) * np.sqrt(w)
    r = least_squares(res, p0, bounds=bounds, method='trf')
    return r.x, float(np.sqrt(np.mean(res(r.x) ** 2 / np.maximum(w, 1e-9))))


class ParamModel(LineModel):
    """The same pixel model with D given by a parametric form instead of the spline."""

    def __init__(self, lines, form, n_form, order='before', heavy=True, u_fit=(1.0, 40.0)):
        super().__init__(lines, order=order, heavy=heavy, u_fit=u_fit, lam=0.0)
        self.form = form; self.n_form = n_form
        self.uf = np.maximum(lines.fine_u, 0.0)

    def unpack(self, p):
        return p[0], p[1], p[2], p[3], p[4:]

    def D_of(self, c):
        return self.form(self.uf, *c)

    def residuals(self, p):
        pred = self.predict(p)
        return (pred - self.L.Y)[:, self.fit_mask].ravel() / np.sqrt(self.L.n_lines)

    def fit_param(self, form_inits, form_bounds, a=0.5, t=0.4, k=0.3, s1=1.5):
        best = None
        lo = np.array([-0.5, 0.0, 0.0, 0.3] + list(form_bounds[0]))
        hi = np.array([1.5, 2.0, 1.0, 8.0] + list(form_bounds[1]))
        if not self.heavy:
            lo[2], hi[2] = 0.0, 1e-9
        for f0 in form_inits:
            p0 = np.clip(np.array([a, t, k if self.heavy else 0.0, s1] + list(f0)), lo + 1e-9, hi - 1e-9)
            res = least_squares(self.residuals, p0, bounds=(lo, hi), method='trf', x_scale='jac', max_nfev=300)
            r = self.rms(res.x)
            if best is None or r < best[0]:
                best = (r, res.x)
        return best[1], best[0]


# ---------------------------------------------------------------- captures

def load_luma(path):
    return luma_lin(load_rgb(path))


def scale_of(Y):
    return Y.shape[1] // CANVAS[0]


PROBE_RASTERS = '/Users/new/.claude/jobs/5c70e47f/tmp/w9-probe-fixtures/backgrounds'


def raster_path(pitch, scale):
    """The committed raster the capture was taken over: canonical for pitch 16, the W9 probe's otherwise (1x only)."""
    if pitch == 16:
        return plate_path('checkerboard', scale)
    assert scale == 1, 'the probe bed is 1x only'
    return f'{PROBE_RASTERS}/checkerboard-{pitch}@1x.png'


def self_test(Y, comp, edge, pitch, scale):
    """The analytic plate must equal the raster the capture was taken over, along the lines used."""
    L = EdgeLines(Y, comp, edge, pitch, scale)
    RL = EdgeLines(load_luma(raster_path(pitch, scale)), comp, edge, pitch, scale)
    return L, float(np.abs(RL.Y - L.sharp_plate(L.u)).max())


EDGES = ('top', 'bottom', 'left', 'right')


def to_jsonable(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, dict):
        return {k: to_jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_jsonable(v) for v in o]
    return o


# ---------------------------------------------------------------- joint fits across edges / cells

class JointModel:
    """One D (spline or parametric form) shared by several line sets, each with its own (a, t, k, σ1).
    The straight edges of one cell have different checker phases along the normal (the boundaries
    sit at different source depths), so pooling them is what constrains D through the fold."""

    def __init__(self, models):
        self.models = models
        self.m0 = models[0]
        self.param = isinstance(self.m0, ParamModel)
        self.n_c = self.m0.n_form if self.param else self.m0.n
        self.M = len(models)

    def split(self, p):
        per = p[:4 * self.M].reshape(self.M, 4)
        return per, p[4 * self.M:]

    def residuals(self, p):
        per, c = self.split(p)
        parts = []
        for m, q in zip(self.models, per):
            pv = np.concatenate([q, c])
            pred = m.predict(pv)
            parts.append((pred - m.L.Y)[:, m.fit_mask].ravel() / np.sqrt(m.L.n_lines * self.M))
        if not self.param:
            parts.append(self.m0.lam * (self.m0.P @ c))
        return np.concatenate(parts)

    def rms(self, p):
        per, c = self.split(p)
        return [m.rms(np.concatenate([q, c])) for m, q in zip(self.models, per)]

    def D(self, p, u):
        per, c = self.split(p)
        if self.param:
            return self.m0.form(np.asarray(u, dtype=float), *c)
        B, _ = spline_basis(np.maximum(np.asarray(u, dtype=float), 0.0))
        return B @ c

    def bounds(self, form_bounds=None):
        lo, hi = [], []
        for m in self.models:
            l, h = m.bounds()[0][:4], m.bounds()[1][:4]
            lo += list(l); hi += list(h)
        if self.param:
            lo += list(form_bounds[0]); hi += list(form_bounds[1])
        else:
            lo += [-15.0] * self.n_c; hi += [80.0] * self.n_c
        return np.array(lo), np.array(hi)

    def fit(self, inits, per_init=(0.5, 0.4, 0.3, 1.5), form_bounds=None, max_nfev=400):
        """inits: callables u→D (spline) or parameter tuples (param). Returns (p, per-model rms)."""
        lo, hi = self.bounds(form_bounds)
        best = None
        for init in inits:
            if self.param:
                c0 = np.array(init, dtype=float)
            else:
                uf = np.maximum(self.m0.L.fine_u, 0.0)
                c0 = fit_spline_to_curve(uf, init(uf))
            q0 = []
            for m in self.models:
                a, t, k, s1 = per_init
                q0 += [a, t, (k if m.heavy else 0.0), s1]
            p0 = np.clip(np.concatenate([q0, c0]), lo + 1e-9, hi - 1e-9)
            res = least_squares(self.residuals, p0, bounds=(lo, hi), method='trf', x_scale='jac', max_nfev=max_nfev)
            r = float(np.sqrt(np.mean(np.concatenate([np.atleast_1d(v) ** 2 for v in self.rms(res.x)]))))
            if best is None or r < best[0]:
                best = (r, res.x)
        return best[1], self.rms(best[1])

    def bootstrap(self, p_hat, u_eval, reps=8, seed=0):
        """Refit D with each model's lines resampled with replacement; returns D samples (reps × len(u_eval))."""
        rng = np.random.default_rng(seed)
        out = []
        saved = [(m.L.Y, m.L.cross, m.L.cross_wave) for m in self.models]
        for r in range(reps):
            for m, (Y, cross, cw) in zip(self.models, saved):
                idx = rng.integers(0, len(cross), len(cross))
                m.L.Y, m.L.cross, m.L.cross_wave = Y[idx], cross[idx], cw[idx]
            lo, hi = self.bounds()
            res = least_squares(self.residuals, np.clip(p_hat, lo + 1e-9, hi - 1e-9), bounds=(lo, hi), method='trf', x_scale='jac', max_nfev=150)
            out.append(self.D(res.x, u_eval))
        for m, (Y, cross, cw) in zip(self.models, saved):
            m.L.Y, m.L.cross, m.L.cross_wave = Y, cross, cw
        return np.array(out)

    def constraint(self, p, u_eval, eps=0.25):
        """Σ over models of the mean |∂Y/∂s| at each depth — where it is ~0, D is the prior's."""
        per, c = self.split(p)
        total = np.zeros(len(u_eval))
        for m, q in zip(self.models, per):
            pv = np.concatenate([q, c])
            f0 = m.predict(pv)
            saved = m.D_of
            Dfix = saved(c) + eps
            m.D_of = lambda cc, Dfix=Dfix: Dfix
            f1 = m.predict(pv)
            m.D_of = saved
            g = np.mean(np.abs(f1 - f0), axis=0) / eps
            total += np.interp(u_eval, m.L.u, g)
        return total


def edge_models(Y, comp, pitch, scale, order, edges=EDGES, heavy=True, lam=0.01, u_fit=(1.0, 40.0), **kw):
    return [LineModel(EdgeLines(Y, comp, e, pitch, scale, **kw), order=order, heavy=heavy, lam=lam, u_fit=u_fit) for e in edges]


def edge_param_models(Y, comp, pitch, scale, order, form, n_form, edges=EDGES, heavy=True, u_fit=(1.0, 40.0), **kw):
    return [ParamModel(EdgeLines(Y, comp, e, pitch, scale, **kw), form, n_form, order=order, heavy=heavy, u_fit=u_fit) for e in edges]


def fit_fixed_D(joint, c, per_init=(0.5, 0.4, 0.3, 1.5), u_fit=None, form_bounds=None):
    """Refit only the per-model (a, t, k, σ1) with D's coefficients held; optional fit window override."""
    masks = [m.fit_mask for m in joint.models]
    if u_fit is not None:
        for m in joint.models:
            m.fit_mask = (m.L.u >= u_fit[0]) & (m.L.u <= u_fit[1])
    fb = form_bounds if form_bounds is not None else ([-1e9] * len(c), [1e9] * len(c))
    lo, hi = joint.bounds(fb) if joint.param else joint.bounds()
    lo, hi = lo[:4 * joint.M], hi[:4 * joint.M]

    def res(q):
        parts = []
        for m, qq in zip(joint.models, q.reshape(joint.M, 4)):
            pred = m.predict(np.concatenate([qq, c]))
            parts.append((pred - m.L.Y)[:, m.fit_mask].ravel() / np.sqrt(m.L.n_lines * joint.M))
        return np.concatenate(parts)
    q0 = []
    for m in joint.models:
        a, t, k, s1 = per_init
        q0 += [a, t, (k if m.heavy else 0.0), s1]
    r = least_squares(res, np.clip(np.array(q0), lo + 1e-9, hi - 1e-9), bounds=(lo, hi), method='trf', x_scale='jac', max_nfev=200)
    p = np.concatenate([r.x, c])
    rms = joint.rms(p)
    for m, mk in zip(joint.models, masks):
        m.fit_mask = mk
    return p, rms


QUAD_INITS = [(33.0, 20.8), (20.0, 15.0), (45.0, 25.0)]
QUAD_BOUNDS = ([0.0, 4.0], [80.0, 40.0])
BEVEL_INITS = [(20.0, 30.0, 1.5), (15.0, 25.0, 1.4), (25.0, 45.0, 1.7), (20.0, 20.0, 1.5)]
BEVEL_BOUNDS = ([4.0, 0.0, 1.05], [40.0, 80.0, 2.5])
SUPER_INITS = [(20.0, 30.0, 1.5, 1.0), (20.0, 30.0, 1.5, 1.6), (20.0, 30.0, 1.5, 0.7), (15.0, 25.0, 1.4, 1.2)]
SUPER_BOUNDS = ([4.0, 0.0, 1.05, 0.3], [40.0, 80.0, 2.5, 3.0])
FORMS = {
    'quadratic': (quadratic_form, 2, QUAD_INITS, QUAD_BOUNDS),
    'bevel': (lambda u, L, T, n: bevel_form(u, L, T, n, 1.0), 3, BEVEL_INITS, BEVEL_BOUNDS),
    'superbevel': (bevel_form, 4, SUPER_INITS, SUPER_BOUNDS),
}


# ---------------------------------------------------------------- coordinator additions (2026-09-03)
# A two-term profile (Apple's private glassBackground CAFilter exposes inner and outer refraction
# amounts over their own heights), and a depth-varying sharp share (the same filter ramps the blur
# mix by distance from the edge).

def p_quad(x):
    return np.clip(1 - np.asarray(x, dtype=float), 0, 1) ** 2


def p_smooth(x):
    x = np.clip(np.asarray(x, dtype=float), 0, 1)
    return 1 - x * x * (3 - 2 * x)


def two_term_form(u, A_in, H_in, A_out, H_out, profile=p_quad):
    u = np.asarray(u, dtype=float)
    return A_in * profile(u / H_in) - A_out * profile(u / H_out)


TWO_INITS = [(33.0, 20.8, 0.0, 6.0), (40.0, 12.5, 10.0, 6.25), (30.0, 16.0, 5.0, 4.0), (36.0, 22.0, 8.0, 3.0)]
TWO_BOUNDS = ([0.0, 2.0, 0.0, 0.5], [80.0, 40.0, 40.0, 20.0])
FORMS['two-quad'] = (lambda u, A, H, B, G: two_term_form(u, A, H, B, G, p_quad), 4, TWO_INITS, TWO_BOUNDS)
FORMS['two-smooth'] = (lambda u, A, H, B, G: two_term_form(u, A, H, B, G, p_smooth), 4, TWO_INITS, TWO_BOUNDS)

LineModel.n_per = 4
ParamModel.n_per = 4


class RampLineModel(LineModel):
    """Blur-before with the sharp share varying by depth: k(u) = k_deep + (k_edge − k_deep)·max(0, 1 − u/U_ramp).
    Per-line-set parameters (a, t, k_deep, σ1, k_edge, U_ramp)."""
    n_per = 6

    def unpack(self, p):
        return p[0], p[1], p[2], p[3], p[6:]

    def predict(self, p, return_fine=False):
        a, t, k_deep, s1 = p[0], p[1], p[2], p[3]
        k_edge, U = p[4], p[5]
        c = p[6:]
        D = self.D_of(c)
        uf = np.maximum(self.L.fine_u, 0.0)
        k = k_deep + (k_edge - k_deep) * np.clip(1 - uf / max(U, 1e-3), 0, 1)
        s = self.L.fine_u + D
        wave_sharp = self.L.q(s)
        Q1 = self.component(s1, s, wave_sharp); e1 = self.L.cross_factors(s1)
        Q2 = self.component(SIGMA_HEAVY, s, wave_sharp); e2 = self.L.cross_factors(SIGMA_HEAVY)
        fine = (1 - k)[None, :] * e1[:, None] * Q1[None, :] + k[None, :] * e2[:, None] * Q2[None, :]
        fine = a + t * 0.5 * (1 - fine)
        if return_fine:
            return fine
        out = np.empty((self.L.n_lines, len(self.L.u)))
        for j, f in enumerate(self.L.foot):
            out[:, j] = fine[:, f].mean(axis=1)
        return out

    def residuals(self, p):
        pred = self.predict(p)
        r = (pred - self.L.Y)[:, self.fit_mask].ravel() / np.sqrt(self.L.n_lines)
        pen = self.lam * (self.P @ p[6:])
        return np.concatenate([r, pen])

    def bounds(self):
        lo = [-0.5, 0.0, 0.0, 0.3, 0.0, 1.0] + [-15.0] * self.n
        hi = [1.5, 2.0, 1.0, 8.0, 1.0, 40.0] + [80.0] * self.n
        return np.array(lo), np.array(hi)


def _split(self, p):
    n = self.m0.n_per
    per = p[:n * self.M].reshape(self.M, n)
    return per, p[n * self.M:]


def _bounds(self, form_bounds=None):
    lo, hi = [], []
    for m in self.models:
        l, h = m.bounds()
        lo += list(l[:m.n_per]); hi += list(h[:m.n_per])
    if self.param:
        lo += list(form_bounds[0]); hi += list(form_bounds[1])
    else:
        lo += [-15.0] * self.n_c; hi += [80.0] * self.n_c
    return np.array(lo), np.array(hi)


def _fit(self, inits, per_init=(0.5, 0.4, 0.3, 1.5), form_bounds=None, max_nfev=400):
    lo, hi = self.bounds(form_bounds)
    best = None
    for init in inits:
        if self.param:
            c0 = np.array(init, dtype=float)
        else:
            uf = np.maximum(self.m0.L.fine_u, 0.0)
            c0 = fit_spline_to_curve(uf, init(uf))
        q0 = []
        for m in self.models:
            a, t, k, s1 = per_init[:4]
            q = [a, t, (k if m.heavy else 0.0), s1]
            if m.n_per == 6:
                q += [k, 8.0]
            q0 += q
        p0 = np.clip(np.concatenate([q0, c0]), lo + 1e-9, hi - 1e-9)
        res = least_squares(self.residuals, p0, bounds=(lo, hi), method='trf', x_scale='jac', max_nfev=max_nfev)
        r = float(np.sqrt(np.mean(np.concatenate([np.atleast_1d(v) ** 2 for v in self.rms(res.x)]))))
        if best is None or r < best[0]:
            best = (r, res.x)
    return best[1], self.rms(best[1])


JointModel.split = _split
JointModel.bounds = _bounds
JointModel.fit = _fit


def edge_ramp_models(Y, comp, pitch, scale, edges=EDGES, lam=0.01, u_fit=(1.0, 40.0), **kw):
    return [RampLineModel(EdgeLines(Y, comp, e, pitch, scale, **kw), order='before', heavy=True, lam=lam, u_fit=u_fit) for e in edges]


class DarkLineModel(LineModel):
    """Blur-before with a multiplicative darkening near the contour: Y = τ(u)·(a + t·B(s)),
    τ(u) = 1 − δ·exp(−(u − u_d)²/(2 w²)). Per-line-set parameters (a, t, k, σ1, δ, u_d, w)."""
    n_per = 7

    def unpack(self, p):
        return p[0], p[1], p[2], p[3], p[7:]

    def predict(self, p, return_fine=False):
        a, t, k, s1 = p[0], p[1], p[2], p[3]
        delta, ud, wd = p[4], p[5], p[6]
        c = p[7:]
        D = self.D_of(c)
        s = self.L.fine_u + D
        wave_sharp = self.L.q(s)
        Q1 = self.component(s1, s, wave_sharp); e1 = self.L.cross_factors(s1)
        fine = (1 - k) * e1[:, None] * Q1[None, :]
        if self.heavy and k > 0:
            Q2 = self.component(SIGMA_HEAVY, s, wave_sharp); e2 = self.L.cross_factors(SIGMA_HEAVY)
            fine = fine + k * e2[:, None] * Q2[None, :]
        uf = self.L.fine_u
        tau = 1 - delta * np.exp(-(uf - ud) ** 2 / (2 * max(wd, 1e-3) ** 2))
        fine = tau[None, :] * (a + t * 0.5 * (1 - fine))
        if return_fine:
            return fine
        out = np.empty((self.L.n_lines, len(self.L.u)))
        for j, f in enumerate(self.L.foot):
            out[:, j] = fine[:, f].mean(axis=1)
        return out

    def residuals(self, p):
        pred = self.predict(p)
        r = (pred - self.L.Y)[:, self.fit_mask].ravel() / np.sqrt(self.L.n_lines)
        pen = self.lam * (self.P @ p[7:])
        return np.concatenate([r, pen])

    def bounds(self):
        lo = [-0.5, 0.0, 0.0, 0.3, 0.0, 0.5, 0.3] + [-15.0] * self.n
        hi = [1.5, 2.0, 1.0, 8.0, 0.8, 6.0, 3.0] + [80.0] * self.n
        return np.array(lo), np.array(hi)


def _fit2(self, inits, per_init=(0.5, 0.4, 0.3, 1.5), form_bounds=None, max_nfev=400):
    lo, hi = self.bounds(form_bounds)
    best = None
    for init in inits:
        if self.param:
            c0 = np.array(init, dtype=float)
        else:
            uf = np.maximum(self.m0.L.fine_u, 0.0)
            c0 = fit_spline_to_curve(uf, init(uf))
        q0 = []
        for m in self.models:
            a, t, k, s1 = per_init[:4]
            q = [a, t, (k if m.heavy else 0.0), s1]
            if m.n_per == 6:
                q += [k, 8.0]
            elif m.n_per == 7:
                q += [0.2, 2.0, 1.0]
            q0 += q
        p0 = np.clip(np.concatenate([q0, c0]), lo + 1e-9, hi - 1e-9)
        res = least_squares(self.residuals, p0, bounds=(lo, hi), method='trf', x_scale='jac', max_nfev=max_nfev)
        r = float(np.sqrt(np.mean(np.concatenate([np.atleast_1d(v) ** 2 for v in self.rms(res.x)]))))
        if best is None or r < best[0]:
            best = (r, res.x)
    return best[1], self.rms(best[1])


JointModel.fit = _fit2


def edge_dark_models(Y, comp, pitch, scale, edges=EDGES, lam=0.01, u_fit=(1.0, 40.0), **kw):
    return [DarkLineModel(EdgeLines(Y, comp, e, pitch, scale, **kw), order='before', heavy=True, lam=lam, u_fit=u_fit) for e in edges]


def power_form(u, S, L, p):
    d = np.clip(np.asarray(u, dtype=float) / L, 0, 1)
    return S * (1 - d) ** p


POWER_INITS = [(44.0, 19.5, 2.5), (33.0, 20.8, 2.0), (50.0, 18.0, 3.0), (40.0, 22.0, 2.2)]
POWER_BOUNDS = ([0.0, 4.0, 0.5], [120.0, 40.0, 6.0])
FORMS['power'] = (power_form, 3, POWER_INITS, POWER_BOUNDS)
