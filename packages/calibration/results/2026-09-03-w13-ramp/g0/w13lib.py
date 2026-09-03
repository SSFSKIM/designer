"""W13 G0 instrument: one heavy share k per depth window, read through a FIXED lens.

The W12 G0 instrument (`../../2026-09-03-w12-lens/g1/w12lib.py`) recovered the lens
displacement D(u) along a straight edge with one body mix per line set. This wave asks the
opposite question with the lens held: D(u) is pinned at `main`'s landed law (W12 G2's power
form with the reference's span laws and `lensOvalization` 0.8, claims 5.51), and the body's
mix is free **per depth window** — u bins of 4 CSS px from the contour to the centre.

The model, per line normal to a straight edge, is W12 G0's with the window index added:

    Y(p) = a + t/2 · (1 − Σ_c w_c(u) · S_c(x_src) · S_c(y_src))

with (x_src, y_src) the point the shader samples — the screen point displaced by −D·dir,
dir the landed direction field (the rounded rect's normal blended toward the inscribed
oval by ω) — S_c the component's kernel convolved with the checkerboard's ±1 square wave
along one axis (the plate is separable, so a separable blur of it is the product of two
1-D blurred waves), and w_sharp + w_heavy = 1 with w_heavy = k(u) constant inside a window.
The pixel is integrated over its footprint on a fine grid before the window weights are
applied, so a pixel straddling a window boundary carries both.

Written as t_s(u) = −t/2·(1 − k) and t_h(u) = −t/2·k the model is **linear** in its
unknowns given the two widths: one intercept per line set and two shared coefficients per
window. That is the whole instrument — an ordinary least-squares solve on normal equations,
no optimiser, no restarts. It also buys a free diagnostic the W12 form could not give: the
per-window total transmission t(u) = −2(t_s + t_h) is fitted rather than assumed, so a
transmission that itself changes with depth shows up as a non-constant t(u) instead of
hiding inside k(u).

Depth is the rounded rect's SDF depth, not the distance from the edge: a sample is used
only where THIS edge is the nearest feature (depth == distance to this edge), which is what
makes the straight-edge reduction exact and what limits the deep windows to the lines near
the edge's midpoint.

Units are CSS px throughout; a capture at scale s has s device px per CSS px. Everything
here is analysis of committed rasters. No constant under `packages/*/src` is read at
runtime — the material's numbers are transcribed below with their source — and nothing is
captured.
"""
import os
import sys

import numpy as np

W12 = '/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-03-w12-lens/g1'
G3 = '/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-03-w12-lens/g3'
for p in (W12, G3):
    if p not in sys.path:
        sys.path.insert(0, p)

import g3lib  # noqa: E402  (the probe beds, the plates, the two-component kernel fits)
import w11lib  # noqa: E402  (colour, geometry, the compare's SSIM replica)

ROOT = '/Users/new/Developer/GitHub/designer'
OUT = f'{ROOT}/packages/calibration/results/2026-09-03-w13-ramp/g0'
WEB = f'{ROOT}/packages/calibration/web-captures'
FIX = f'{ROOT}/apps/reference-apple/fixtures'

CANVAS = g3lib.CANVAS
COMP = g3lib.COMP
SPAN = g3lib.SPAN
PITCH = g3lib.PITCH
CX, CY = CANVAS[0] / 2, CANVAS[1] / 2
FINE = 8  # fine-grid samples per CSS px

# ---------------------------------------------------------------- the landed material
# Transcribed from packages/renderer-webgpu/src/material.ts DEFAULT_MATERIAL_PROFILE on
# `main` (the W12 close, ω 0.8) and packages/renderer-webgpu/src/wgsl/optics.ts. Nothing
# below is fitted here; the lens is fixed by the wave's first binding rule.
BLUR_SIGMA = 1.25             # sharp σ, CSS px
SIZE_SCATTER_GAIN_MAX = 8.0   # heavy σ = BLUR_SIGMA × this = 10 CSS px
SIZE_SCATTER_FLOOR = 0.4
SIZE_SCATTER_SPAN_MAX = 256.0
SIZE_SPAN_MIN = 32.0
LENS_REFRACTION_GAIN = 0.745
LENS_HEIGHT_PER_SPAN = 0.25
LENS_HEIGHT_MAX = 20.0
LENS_AMOUNT_PER_SPAN = 0.8
LENS_AMOUNT_MAX = 60.0
LENS_THICKNESS_REFERENCE = 8.0
LENS_EXTENT_GAIN = 1.337
LENS_PROFILE_EXPONENT = 3.69
LENS_OVALIZATION = 0.8
LENS_OVALIZATION_SPAN_MIN = 64.0
LENS_OVALIZATION_SPAN_MAX = 72.0
THICKNESS = 8.0               # the host default and what the bed was captured at


def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def vitrea_k(span):
    """`scatterThickness(span, fold=1)`: the uniform heavy share `main` renders at."""
    return SIZE_SCATTER_FLOOR + (1 - SIZE_SCATTER_FLOOR) * smoothstep(
        SIZE_SPAN_MIN, SIZE_SCATTER_SPAN_MAX, span)


def lens_depth_px(span, thickness=THICKNESS):
    scale = thickness / LENS_THICKNESS_REFERENCE
    base = min(LENS_HEIGHT_PER_SPAN * span, LENS_HEIGHT_MAX)
    return min(max(base * scale, 0.0), span * 0.5)


def lens_magnitude_px(span, thickness=THICKNESS):
    scale = thickness / LENS_THICKNESS_REFERENCE
    unclamped = min(LENS_HEIGHT_PER_SPAN * span, LENS_HEIGHT_MAX) * scale
    amount = min(LENS_AMOUNT_PER_SPAN * span, LENS_AMOUNT_MAX) * scale
    depth = lens_depth_px(span, thickness)
    return LENS_REFRACTION_GAIN * amount * (depth / unclamped if unclamped > 1e-6 else 0.0)


def lens_extent_px(span, thickness=THICKNESS):
    return LENS_EXTENT_GAIN * lens_depth_px(span, thickness)


def landed_D(depth, span, thickness=THICKNESS):
    """`main`'s displacement at SDF depth (CSS px): S · max(0, 1 − depth/L′)^p."""
    extent = lens_extent_px(span, thickness)
    if extent <= 1e-6:
        return np.zeros_like(np.asarray(depth, dtype=float))
    t = np.maximum(1.0 - np.maximum(np.asarray(depth, dtype=float), 0.0) / extent, 0.0)
    return lens_magnitude_px(span, thickness) * t ** LENS_PROFILE_EXPONENT


def omega_of(span):
    return LENS_OVALIZATION * smoothstep(LENS_OVALIZATION_SPAN_MIN, LENS_OVALIZATION_SPAN_MAX, span)


# ---------------------------------------------------------------- geometry


def rrect_sdf(px, py, comp):
    """Signed distance to the component's contour (negative inside), CSS px, at continuous points."""
    w, h, r = COMP[comp]
    qx = np.abs(px - CX) - (w / 2 - r)
    qy = np.abs(py - CY) - (h / 2 - r)
    return (np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2)
            + np.minimum(np.maximum(qx, qy), 0) - r)


def rrect_normal(px, py, comp):
    """The outward unit gradient of the SDF (the field pass's normal), by central difference."""
    e = 1e-3
    gx = rrect_sdf(px + e, py, comp) - rrect_sdf(px - e, py, comp)
    gy = rrect_sdf(px, py + e, comp) - rrect_sdf(px, py - e, comp)
    n = np.hypot(gx, gy)
    n = np.where(n > 1e-9, n, 1.0)
    return gx / n, gy / n


def lens_direction(px, py, comp):
    """The optics pass's displacement direction: the normal blended toward the inscribed oval."""
    w, h, _ = COMP[comp]
    a, b = w / 2, h / 2
    omega = omega_of(SPAN[comp])
    nx, ny = rrect_normal(px, py, comp)
    relx, rely = px - CX, py - CY
    unit_r = np.maximum(np.hypot(relx / a, rely / b), 1e-6)
    s = min(a, b) / unit_r
    gx = (1 - omega) * nx + omega * (relx / (a * a)) * s
    gy = (1 - omega) * ny + omega * (rely / (b * b)) * s
    ln = np.hypot(gx, gy)
    ok = ln > 1e-9
    return np.where(ok, gx / np.where(ok, ln, 1), nx), np.where(ok, gy / np.where(ok, ln, 1), ny)


# ---------------------------------------------------------------- kernels on the plate


def square_wave_x(x, pitch):
    return np.where(np.floor(np.asarray(x, dtype=float) / pitch).astype(int) % 2 == 0, 1.0, -1.0)


def square_wave_y(y, pitch):
    """AppKit-flipped rows: cell k covers y in (H − (k+1)p, H − kp]."""
    return np.where(np.floor((CANVAS[1] - np.asarray(y, dtype=float)) / pitch).astype(int) % 2 == 0,
                    1.0, -1.0)


def _kernel(kind, width, step):
    """A normalised 1-D kernel on a grid of spacing `step` CSS px. Gaussian σ, or box width."""
    if kind == 'gauss':
        if width <= 1e-6:
            return np.array([1.0])
        r = int(np.ceil(4 * width / step))
        x = np.arange(-r, r + 1) * step
        g = np.exp(-x * x / (2 * width * width))
        return g / g.sum()
    if kind == 'box':
        n = max(int(round(width / step)), 1)
        return np.ones(n) / n
    raise ValueError(kind)


class Wave1D:
    """The ±1 square wave along one axis, convolved with one kernel, on a dense grid.

    Sampled by interpolation: the model needs it at hundreds of thousands of scattered
    source coordinates, and one dense grid per (axis, pitch, kernel) is the cheap way there.
    """

    def __init__(self, axis, pitch, kind, width, lo, hi, step=1.0 / FINE):
        pad = 6 * (width if kind == 'gauss' else width) + 4
        self.grid = np.arange(lo - pad, hi + pad, step)
        raw = square_wave_x(self.grid, pitch) if axis == 'x' else square_wave_y(self.grid, pitch)
        k = _kernel(kind, width, step)
        self.vals = raw if len(k) == 1 else np.convolve(raw, k, mode='same')
        # `same` leaks the unpadded ends; the pad keeps the used range clear of them.
        self.lo, self.hi = lo, hi

    def __call__(self, x):
        return np.interp(x, self.grid, self.vals)


# ---------------------------------------------------------------- one edge's line set

_raster_cache = {}


def blurred_raster(backdrop, scale, kind, width):
    """A committed backdrop raster blurred by one component's kernel, in device px."""
    key = (backdrop, scale, kind, round(float(width), 5))
    if key not in _raster_cache:
        from scipy.ndimage import gaussian_filter, uniform_filter
        P = g3lib.plate(backdrop, scale)
        if kind == 'gauss':
            _raster_cache[key] = (gaussian_filter(P, width * scale, mode='nearest')
                                  if width > 1e-6 else P)
        elif kind == 'box':
            n = max(int(round(width * scale)), 1)
            _raster_cache[key] = uniform_filter(P, n, mode='nearest') if n > 1 else P
        else:
            raise ValueError(kind)
    return _raster_cache[key]


EDGES = ('top', 'bottom', 'left', 'right')


class EdgeSet:
    """The pixel lines normal to one straight edge, with the fixed lens already applied.

    Everything the design matrix needs that does not depend on the two widths is computed
    once here: the source coordinates (x_src, y_src) at every fine sample, the SDF depth,
    and the validity mask (this edge is the nearest feature, and the whole pixel footprint
    is valid).
    """

    def __init__(self, Y, comp, edge, pitch, scale, u_max=None, u_fit_min=2.0,
                 corner_margin=4.0, max_lines=48, thickness=THICKNESS, backdrop=None):
        self.comp, self.edge, self.pitch, self.scale = comp, edge, pitch, scale
        self.backdrop = backdrop  # None: the analytic checkerboard at `pitch`
        w, h, r = COMP[comp]
        span = SPAN[comp]
        x0, x1, y0, y1 = CX - w / 2, CX + w / 2, CY - h / 2, CY + h / 2
        u_max = span / 2 if u_max is None else u_max
        H, W = Y.shape
        # a checkerboard's lines are taken at the cell centres, where the cross factor is
        # near ±1 and the line carries the most contrast; any other backdrop takes them all.
        half_width = pitch / 4 if backdrop is None else 1e9

        if edge in ('top', 'bottom'):
            lo, hi = x0 + r + corner_margin, x1 - r - corner_margin
            cols = np.arange(W)
            xs = (cols + 0.5) / scale
            centres = (np.floor(xs / pitch) + 0.5) * pitch
            keep = (xs >= lo) & (xs <= hi) & (np.abs(xs - centres) <= half_width)
            rows = np.arange(H)
            ys = (rows + 0.5) / scale
            u = ys - y0 if edge == 'top' else y1 - ys
            sel = (u >= u_fit_min) & (u <= u_max)
            self.cross = xs[keep]
            self.u = np.sort(u[sel])
            order = np.argsort(u[sel])
            self.Y = Y[np.ix_(rows[sel], cols[keep])].T[:, order]
        else:
            lo, hi = y0 + r + corner_margin, y1 - r - corner_margin
            rows = np.arange(H)
            ys = (rows + 0.5) / scale
            k = np.floor((CANVAS[1] - ys) / pitch)
            centres = CANVAS[1] - (k + 0.5) * pitch
            keep = (ys >= lo) & (ys <= hi) & (np.abs(ys - centres) <= half_width)
            cols = np.arange(W)
            xs = (cols + 0.5) / scale
            u = xs - x0 if edge == 'left' else x1 - xs
            sel = (u >= u_fit_min) & (u <= u_max)
            self.cross = ys[keep]
            self.u = np.sort(u[sel])
            order = np.argsort(u[sel])
            self.Y = Y[np.ix_(rows[keep], cols[sel])][:, order]

        if len(self.cross) > max_lines:  # a uniform stride: adjacent lines are near-replicas
            idx = np.linspace(0, len(self.cross) - 1, max_lines).round().astype(int)
            self.cross, self.Y = self.cross[idx], self.Y[idx]
        self.n_lines = len(self.cross)
        self.pix = 1.0 / scale

        # the fine grid along the normal, and the footprint of every pixel on it
        self.fine_u = np.arange(self.u.min() - 0.5 * self.pix,
                                self.u.max() + 0.5 * self.pix + 1e-9, 1.0 / FINE)
        self.foot = [np.where((self.fine_u >= ui - 0.5 * self.pix - 1e-9)
                              & (self.fine_u < ui + 0.5 * self.pix - 1e-9))[0] for ui in self.u]
        assert min(len(f) for f in self.foot) >= 1

        # screen points (lines × fine), the SDF depth, the landed lens, the source point
        C = self.cross[:, None]
        U = self.fine_u[None, :]
        if edge == 'top':
            px, py = np.broadcast_to(C, (self.n_lines, len(self.fine_u))).copy(), y0 + U
        elif edge == 'bottom':
            px, py = np.broadcast_to(C, (self.n_lines, len(self.fine_u))).copy(), y1 - U
        elif edge == 'left':
            px, py = x0 + U + 0 * C, np.broadcast_to(C, (self.n_lines, len(self.fine_u))).copy()
        else:
            px, py = x1 - U + 0 * C, np.broadcast_to(C, (self.n_lines, len(self.fine_u))).copy()
        px, py = np.broadcast_arrays(px, py)
        px, py = np.array(px, dtype=float), np.array(py, dtype=float)
        self.depth = -rrect_sdf(px, py, comp)
        # this edge is the nearest feature exactly where the SDF depth equals the distance
        # to it; elsewhere the normal is another edge's and the reduction does not hold.
        self.valid_fine = (self.depth > 0) & (self.depth >= np.broadcast_to(U, px.shape) - 1e-6)
        D = landed_D(self.depth, span, thickness)
        dx, dy = lens_direction(px, py, comp)
        self.x_src = px - dx * D
        self.y_src = py - dy * D
        self.D = D
        # a pixel is used only where every fine sample under it is valid
        self.valid_pix = np.stack([self.valid_fine[:, f].all(axis=1) for f in self.foot], axis=1)

    def integrate(self, fine):
        """Footprint-average a fine-grid field (lines × fine) onto the pixel grid."""
        out = np.empty((self.n_lines, len(self.u)))
        for j, f in enumerate(self.foot):
            out[:, j] = fine[:, f].mean(axis=1)
        return out

    def structure(self, kind, width):
        """One component's blurred backdrop, in linear luminance, at the source point.

        A checkerboard is separable, so the blurred plate is ½(1 − Sx(x)·Sy(y)) with each S
        the ±1 square wave convolved with the component's 1-D kernel — exact, and evaluated
        by interpolation on a dense 1-D grid. Any other backdrop is blurred as a raster at
        device resolution and read with cubic interpolation at the source point; that path
        carries the raster's own interpolation error and is used only where the frequency
        diversity it brings is what makes the fit identifiable (see `g0-instrument.md` §2).
        """
        if self.backdrop is None:
            wx = Wave1D('x', self.pitch, kind, width, float(self.x_src.min()), float(self.x_src.max()))
            wy = Wave1D('y', self.pitch, kind, width, float(self.y_src.min()), float(self.y_src.max()))
            return 0.5 * (1 - wx(self.x_src) * wy(self.y_src))
        from scipy.ndimage import map_coordinates
        P = blurred_raster(self.backdrop, self.scale, kind, width)
        return map_coordinates(P, [self.y_src * self.scale - 0.5, self.x_src * self.scale - 0.5],
                               order=3, mode='nearest')


def plate_self_test(comp, pitch, scale, edge='top'):
    """The analytic plate must equal the committed raster along the lines used (w12lib's check)."""
    backdrop = [b for b, p in PITCH.items() if p == pitch and b != 'checkerboard-lc16'][0]
    R = g3lib.plate(backdrop, scale)
    L = EdgeSet(R, comp, edge, pitch, scale, u_fit_min=-4.0, u_max=SPAN[comp] / 2)
    # rebuild the raster's own value at the pixel centres from the analytic square waves
    C = L.cross[:, None]
    U = L.u[None, :]
    w, h, r = COMP[comp]
    y0, y1, x0, x1 = CY - h / 2, CY + h / 2, CX - w / 2, CX + w / 2
    if edge == 'top':
        px, py = np.broadcast_to(C, (L.n_lines, len(L.u))), y0 + U
    elif edge == 'bottom':
        px, py = np.broadcast_to(C, (L.n_lines, len(L.u))), y1 - U
    elif edge == 'left':
        px, py = x0 + U + 0 * C, np.broadcast_to(C, (L.n_lines, len(L.u)))
    else:
        px, py = x1 - U + 0 * C, np.broadcast_to(C, (L.n_lines, len(L.u)))
    if L.Y.size == 0:
        return float('nan')  # no straight-edge line at this pitch on this component
    model = 0.5 * (1 - square_wave_x(px, pitch) * square_wave_y(py, pitch))
    return float(np.abs(model - L.Y).max())


# ---------------------------------------------------------------- the windowed fit


def windows_for(span, step=4.0):
    """The depth windows: bins of `step` CSS px from the contour to span/2."""
    edges = np.arange(0.0, span / 2 + 1e-9, step)
    if edges[-1] < span / 2 - 1e-9:
        edges = np.append(edges, span / 2)
    return [(float(edges[i]), float(edges[i + 1])) for i in range(len(edges) - 1)]


class WindowFit:
    """One heavy share per depth window over a pool of line sets, at fixed widths.

    Two modes, because the two are identified by different things:

    - **`t` shared** (the instrument). Per line set a level `a` and a transmission `t`; per
      window one share `k`, shared by every set. The model is bilinear — linear in (a, t)
      given k, linear in k given (a, t) — and is solved by alternating least squares from a
      flat start. This is the mode that must be used when only one pitch is available: with
      `t` free per window as well, a uniform scaling of `t` trades almost exactly against a
      uniform shift of `k` (the heavy component at pitch 16 keeps only ≈ 15% of its
      contrast, so its column is nearly antiparallel to the sharp one), and the solve wanders
      — see `g0-instrument.md` §2.
    - **`t` free per window** (the diagnostic). Two coefficients per window, ordinary least
      squares, no constraint that the transmission is the same at every depth. Identified
      only when several pitches are pooled, where the two components' contrast ratios differ
      strongly enough to separate them; used to ask whether the reference's transmission is
      itself a function of depth rather than assuming it is not.
    """

    def __init__(self, sets, windows):
        self.sets, self.windows = sets, windows
        self.W = len(windows)
        self.M = len(sets)

    # ---- shared precomputation: the window occupancy and the two components' integrals
    def prepare(self, sharp, heavy):
        prep = []
        for s in self.sets:
            A = s.structure(*sharp)
            B = s.structure(*heavy)
            PA, dP, occ = [], [], []
            for (lo, hi) in self.windows:
                inw = ((s.depth >= lo) & (s.depth < hi)).astype(float)
                pa = s.integrate(inw * A)[s.valid_pix]
                pb = s.integrate(inw * B)[s.valid_pix]
                PA.append(pa)
                dP.append(pb - pa)
                occ.append(s.integrate(inw)[s.valid_pix])
            prep.append(dict(PA_tot=np.sum(PA, axis=0), dP=np.stack(dP, axis=1),
                             PA=np.stack(PA, axis=1), occ=np.stack(occ, axis=1),
                             y=s.Y[s.valid_pix]))
        return prep

    def solve_shared_t(self, sharp, heavy, iters=60, k0=0.5, prep=None, t_fixed=None,
                       bounds=(0.0, 1.0), t_min=0.0):
        """Alternating least squares: (a_i, t_i) per set, k_w per window shared.

        `t_fixed` pins the transmission (one number, or one per set) instead of fitting it —
        the only way to read k's LEVEL from a capture that offers a single spatial frequency,
        where t and a uniform shift of k trade against each other almost exactly.
        """
        prep = self.prepare(sharp, heavy) if prep is None else prep
        k = np.full(self.W, float(k0))
        at = [(0.45, 0.4)] * self.M
        if t_fixed is not None and np.isscalar(t_fixed):
            t_fixed = [float(t_fixed)] * self.M
        for _ in range(iters):
            # (a_i, t_i) given k
            at = []
            for i, p in enumerate(prep):
                X = p['PA_tot'] + p['dP'] @ k
                if t_fixed is None:
                    Xm = np.stack([np.ones_like(X), X], axis=1)
                    c, *_ = np.linalg.lstsq(Xm, p['y'], rcond=None)
                    t = max(float(c[1]), t_min)
                    a = float(c[0]) if t == float(c[1]) else float(np.mean(p['y'] - t * X))
                    at.append((a, t))
                else:
                    t = float(t_fixed[i])
                    at.append((float(np.mean(p['y'] - t * X)), t))
            # k given (a_i, t_i)
            XtX = np.zeros((self.W, self.W))
            Xty = np.zeros(self.W)
            for p, (a, t) in zip(prep, at):
                Z = t * p['dP']
                r = p['y'] - a - t * p['PA_tot']
                XtX += Z.T @ Z
                Xty += Z.T @ r
            if bounds is None:
                k_new = np.linalg.solve(XtX + 1e-10 * np.eye(self.W), Xty)
            else:
                # k is a mix weight; outside [0, 1] the model is extrapolating (a negative
                # sharp weight sharpens rather than mixes), so the bound is kept and the
                # windows that reach it are reported as reaching it.
                from scipy.optimize import lsq_linear
                Lch = np.linalg.cholesky(XtX + 1e-9 * np.eye(self.W))
                k_new = lsq_linear(Lch.T, np.linalg.solve(Lch, Xty), bounds=bounds).x
            if np.max(np.abs(k_new - k)) < 1e-9:
                k = k_new
                break
            k = k_new
        # residual (overall and per window), and the covariance of k conditional on (a, t)
        sse, n = 0.0, 0
        w_sse, w_n = np.zeros(self.W), np.zeros(self.W)
        for p, (a, t) in zip(prep, at):
            pred = a + t * (p['PA_tot'] + p['dP'] @ k)
            r = p['y'] - pred
            sse += float(r @ r)
            n += len(r)
            # a pixel is charged to the window that owns most of its footprint
            own = np.argmax(p['occ'], axis=1)
            np.add.at(w_sse, own, r * r)
            np.add.at(w_n, own, 1.0)
        dof = max(n - (self.W + 2 * self.M), 1)
        cov = (sse / dof) * np.linalg.inv(XtX + 1e-10 * np.eye(self.W))
        return dict(mode='shared-t', k=k, se_k=np.sqrt(np.clip(np.diag(cov), 0, None)),
                    at=at, rms=float(np.sqrt(sse / n)), n=n, sse=sse,
                    rms_by_window=np.sqrt(w_sse / np.maximum(w_n, 1)), n_by_window=w_n)

    def solve_free_t(self, sharp, heavy, prep=None):
        """Per-window (t_sharp, t_heavy) free: ordinary least squares, per-set intercepts."""
        prep = self.prepare(sharp, heavy) if prep is None else prep
        n_col = self.M + 2 * self.W
        XtX = np.zeros((n_col, n_col))
        Xty = np.zeros(n_col)
        yty, n = 0.0, 0
        for i, p in enumerate(prep):
            cols = np.empty((len(p['y']), 2 * self.W))
            cols[:, 0::2] = p['PA']
            cols[:, 1::2] = p['PA'] + p['dP']
            sh = slice(self.M, n_col)
            XtX[sh, sh] += cols.T @ cols
            XtX[i, sh] += cols.sum(axis=0)
            XtX[sh, i] += cols.sum(axis=0)
            XtX[i, i] += len(p['y'])
            Xty[sh] += cols.T @ p['y']
            Xty[i] += p['y'].sum()
            yty += float(p['y'] @ p['y'])
            n += len(p['y'])
        coef = np.linalg.solve(XtX + 1e-10 * np.eye(n_col), Xty)
        sse = float(yty - 2 * coef @ Xty + coef @ XtX @ coef)
        dof = max(n - n_col, 1)
        cov = (sse / dof) * np.linalg.inv(XtX + 1e-10 * np.eye(n_col))
        ts = coef[self.M:][0::2]
        th = coef[self.M:][1::2]
        t = ts + th
        k = np.where(np.abs(t) > 1e-9, th / np.where(np.abs(t) > 1e-9, t, 1), np.nan)
        se = []
        for w in range(self.W):
            i_s, i_h = self.M + 2 * w, self.M + 2 * w + 1
            if abs(t[w]) < 1e-9:
                se.append(float('nan'))
                continue
            g = np.array([-th[w] / t[w] ** 2, ts[w] / t[w] ** 2])
            C = cov[np.ix_([i_s, i_h], [i_s, i_h])]
            se.append(float(np.sqrt(max(g @ C @ g, 0.0))))
        return dict(mode='free-t', k=k, se_k=np.array(se), t=t, t_sharp=ts, t_heavy=th,
                    rms=float(np.sqrt(max(sse, 0.0) / n)), n=n, sse=sse)

    def rows(self, res):
        out = []
        for w, (lo, hi) in enumerate(self.windows):
            r = dict(u0=lo, u1=hi, u_mid=0.5 * (lo + hi), k=float(res['k'][w]),
                     se_k=float(res['se_k'][w]), s=float(1 - res['k'][w]))
            if 't' in res:
                r.update(t=float(res['t'][w]))
            out.append(r)
        return out


def forward(s, sharp, heavy, a, t, k_of_depth):
    """The model's own prediction on one line set — used to seed the estimator's self-test."""
    A = s.structure(*sharp)
    B = s.structure(*heavy)
    k = k_of_depth(s.depth)
    return s.integrate(a + t * ((1 - k) * A + k * B))


def build_sets(loader, comp, scale, backdrops, edges=EDGES, **kw):
    """One EdgeSet per (backdrop, edge). `loader(backdrop)` returns the linear-luminance capture.

    `backdrops` are scene backdrop names (`checkerboard-32`, `photo`, …); the checkerboard
    family takes the analytic separable path, everything else the raster path.
    """
    sets, tags = [], []
    for b in backdrops:
        Y = loader(b)
        pitch = PITCH.get(b, 16)
        raster = None if (b in PITCH and b != 'checkerboard-lc16') else b
        for e in edges:
            st = EdgeSet(Y, comp, e, pitch, scale, backdrop=raster, **kw)
            # a capsule has no straight vertical edge, and a coarse pitch can leave an edge
            # with no cell centre inside its straight part; such a set carries nothing.
            if st.n_lines == 0 or not st.valid_pix.any():
                continue
            sets.append(st)
            tags.append(f'{b}-{e}')
    return sets, tags


# ---------------------------------------------------------------- captures


def probe_loader(comp, scale):
    def load(backdrop):
        return g3lib.capture(f'{backdrop}__{comp}__rest', scale)
    return load


def native_loader(comp, scale, profile=None):
    profile = profile or f'apple-macos-26.5-{scale}x-light-standard'

    def load(backdrop):
        return w11lib.luma_lin(w11lib.load_rgb(f'{FIX}/{profile}/{backdrop}__{comp}__rest.png'))
    return load


def web_loader(comp, scale, profile=None, renderer='webgpu', root=WEB):
    profile = profile or f'apple-macos-26.5-{scale}x-light-standard'

    def load(backdrop):
        scene = f'{backdrop}__{comp}__rest'
        return w11lib.luma_lin(w11lib.load_rgb(f'{root}/{profile}/{scene}/{scene}__{renderer}.png'))
    return load


# ---------------------------------------------------------------- the two candidate ramps


def h1_sharp(u, span):
    """The layer tree's ramp (claims 5.50 2): s = 0.5·max(0, 1 − u/(span/2))."""
    return 0.5 * np.maximum(0.0, 1.0 - np.asarray(u, dtype=float) / (span / 2))


def h2_sharp(u, span, s0, rho, floor):
    """A ramp with a free start, reach and floor: s = s0·max(0, 1 − u/(ρ·span/2)) + floor."""
    return s0 * np.maximum(0.0, 1.0 - np.asarray(u, dtype=float) / max(rho * span / 2, 1e-6)) + floor


def to_jsonable(o):
    return g3lib.to_jsonable(o)


def write_part(name, obj):
    import json
    os.makedirs(f'{OUT}/parts', exist_ok=True)
    with open(f'{OUT}/parts/{name}.json', 'w') as f:
        json.dump(to_jsonable(obj), f, indent=1, sort_keys=True)
    print(f'[wrote] {OUT}/parts/{name}.json')
