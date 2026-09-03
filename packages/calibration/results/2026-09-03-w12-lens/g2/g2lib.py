"""W12 G2 dry run: a 2-D band renderer and the scores that rank lens forms against the native captures.

Model: Y(q) = a + t · B(q − D⃗(q)), blur-before, B = (1−k)·G_σs(P) + k·G_10(P) on the raster plate in
linear luminance, (σs, k, a, t) fitted on the NATIVE deep interior of the same cell and scale.
Units: CSS px for every law; the arrays are device px (× scale).
"""
import sys
sys.path.insert(0, '/Users/new/.claude/jobs/5c70e47f/tmp'); sys.path.insert(0, '/Users/new/.claude/jobs/5c70e47f/tmp/w12')
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.signal import find_peaks
from w12b_lib import (COMP, SPAN, CANVAS, PROF, lens_depth, geometry, capture, plate_luma, lstsq_at,
                      to_png, side_by_side)
from w11lib import ssim_map, lin_to_srgb, luma_lin, load_rgb

PROBE_BG = '/Users/new/.claude/jobs/5c70e47f/tmp/w9-probe-fixtures/backgrounds'
SIGMA_HEAVY = 10.0
BAND_TOP = 28.0      # scoring window 0.5 < u ≤ 28 CSS px, the same pixels for every form
CLEAR = 4.0          # straight-edge windows keep this many px clear of the corner arcs
SS_LO, SS_HI = 2.0, None  # dry-run replacement window: 2 ≤ u ≤ L' + 4 (W11c's)


def plate_for(backdrop, scale):
    if backdrop.startswith('checkerboard-'):
        assert scale == 1
        return luma_lin(load_rgb(f'{PROBE_BG}/{backdrop}@1x.png'))
    return plate_luma(backdrop, scale)


class Cell:
    """One native cell with its geometry, plate, body fit and scoring masks."""

    def __init__(self, comp, backdrop, scale, side='native'):
        self.comp, self.backdrop, self.scale = comp, backdrop, scale
        scene = f'{backdrop}__{comp}__rest'
        self.scene = scene
        if backdrop.startswith('checkerboard-'):
            self.Y = capture('probe', scene, 1)
        else:
            self.Y = capture(side, scene, scale)
        self.P = plate_for(backdrop, scale)
        u, nx, ny, xs, ys = geometry(comp, scale)
        self.u, self.nx, self.ny = u, nx, ny
        self.xs, self.ys = xs + 0.5, ys + 0.5          # pixel centres, device px
        w, h, r = COMP[comp]
        self.w, self.h, self.r = w, h, r
        self.cx, self.cy = CANVAS[0] / 2 * scale, CANVAS[1] / 2 * scale
        self.a, self.b = w / 2 * scale, h / 2 * scale   # ellipse half-extents, device px
        self.L = lens_depth(comp)
        px, py = self.xs - self.cx, self.ys - self.cy
        self.px, self.py = px, py
        # ellipse gradient direction (outward), unit
        ex, ey = px / self.a ** 2, py / self.b ** 2
        en = np.sqrt(ex * ex + ey * ey) + 1e-12
        self.ex, self.ey = ex / en, ey / en
        # tangent (any orientation)
        self.tx, self.ty = -ny, nx
        inside = u > 0
        self.inside = inside
        s = scale
        straight_tb = np.abs(px) <= (w / 2 - r - CLEAR) * s
        straight_lr = np.abs(py) <= (h / 2 - r - CLEAR) * s
        self.band = inside & (u > 0.5) & (u <= BAND_TOP)
        self.edge_mask = self.band & (straight_tb | straight_lr)
        # corner boxes: (2r+8)-px squares covering each corner arc
        x0, x1 = self.cx - w / 2 * s, self.cx + w / 2 * s
        y0, y1 = self.cy - h / 2 * s, self.cy + h / 2 * s
        e = (2 * r + 8) * s
        self.corners = {}
        for name, (bx, by) in {'tl': (x0 - 4 * s, y0 - 4 * s), 'tr': (x1 - e + 4 * s, y0 - 4 * s),
                               'bl': (x0 - 4 * s, y1 - e + 4 * s), 'br': (x1 - e + 4 * s, y1 - e + 4 * s)}.items():
            box = (self.xs >= bx) & (self.xs < bx + e) & (self.ys >= by) & (self.ys < by + e)
            self.corners[name] = (box, box & self.band)
        self._blur_cache = {}
        self.fit_body()

    # ---- body ---------------------------------------------------------------------------------
    def blur(self, sigma_css):
        key = round(sigma_css, 3)
        if key not in self._blur_cache:
            self._blur_cache[key] = gaussian_filter(self.P, sigma_css * self.scale, mode='nearest') \
                if sigma_css > 0 else self.P
        return self._blur_cache[key]

    def body(self, sigma_s, k):
        return (1 - k) * self.blur(sigma_s) + k * self.blur(SIGMA_HEAVY)

    def deep_mask(self):
        w, h, r = COMP[self.comp]
        inset = max(min(r, h / 4), 0.0)
        if h / 2 > BAND_TOP + 6:
            inset = BAND_TOP + 2
        return self.u > inset

    def fit_body(self):
        """(σs, k, a, t) on the native deep interior. At pitch 16 k is not identifiable and is fixed
        at the pitch-32/64 reading (0.45 for spans ≥ 96, 0.35 below); at pitch 32 it is fitted."""
        m = self.deep_mask()
        y = self.Y[m]
        if self.backdrop.startswith('checkerboard-'):
            ks = np.linspace(0, 0.9, 19)
        else:
            ks = [0.45 if SPAN[self.comp] >= 96 else 0.35]
        sig_grid = [1.0, 1.25, 1.45, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0]
        best = None
        for sg in sig_grid:
            for k in ks:
                a, t, rms, r2 = lstsq_at(y, self.body(sg, k)[m])
                if best is None or rms < best[2]:
                    best = (sg, k, rms, a, t, r2)
        self.sigma_s, self.k, self.body_rms, self.a_lvl, self.t_lvl, self.body_r2 = best
        self.B = self.body(self.sigma_s, self.k)

    # ---- forms ----------------------------------------------------------------------------------
    def profile(self, G, E, p):
        Lp = E * self.L
        d = np.clip(self.u / Lp, 0, 1)
        return G * self.L * (1 - d) ** p * self.scale      # device px

    def displacement(self, form, params):
        """Outward displacement vector field (device px); the sample is q − D⃗."""
        u, nx, ny = self.u, self.nx, self.ny
        if form == 'F0':
            prof = 1.6 * self.L * np.clip(1 - np.clip(u / self.L, 0, 1), 0, 1) ** 2 * self.scale
            return prof * nx, prof * ny
        G, E, p = params['G'], params['E'], params['p']
        prof = self.profile(G, E, p)
        if form == 'F1':
            return prof * nx, prof * ny
        ex, ey = self.ex, self.ey
        if form == 'F2m':
            return prof * ex, prof * ey
        if form == 'F2n':
            en = ex * nx + ey * ny
            en = np.where(np.abs(en) < 0.2, np.sign(en) * 0.2 + (en == 0) * 0.2, en)
            return prof * ex / en, prof * ey / en
        if form in ('F2bm', 'F2bn'):
            beta = params['beta']
            dx, dy = nx + beta * ex, ny + beta * ey
            dn = np.sqrt(dx * dx + dy * dy) + 1e-12
            dx, dy = dx / dn, dy / dn
            if form == 'F2bm':
                return prof * dx, prof * dy
            en = dx * nx + dy * ny
            en = np.maximum(en, 0.2)
            return prof * dx / en, prof * dy / en
        if form == 'F3':
            g0, Lt = params['g0'], params['Lt']
            g = g0 * np.clip(1 - np.clip(u / Lt, 0, 1), 0, 1) ** 2
            # tangential pull toward the centre: (p − c)·t̂ along t̂
            pt = self.px * self.tx + self.py * self.ty
            return prof * nx + g * pt * self.tx, prof * ny + g * pt * self.ty
        raise ValueError(form)

    def render(self, form, params, mask=None):
        m = self.inside if mask is None else mask
        Dx, Dy = self.displacement(form, params)
        sx = self.xs[m] - 0.5 - Dx[m]
        sy = self.ys[m] - 0.5 - Dy[m]
        out = np.full_like(self.Y, np.nan)
        out[m] = self.a_lvl + self.t_lvl * map_coordinates(self.B, [sy, sx], order=1, mode='nearest')
        return out

    # ---- scores ----------------------------------------------------------------------------------
    def rms(self, model, mask):
        r = model[mask] - self.Y[mask]
        return float(np.sqrt(np.mean(r * r)))

    def edge_rms(self, form, params):
        model = self.render(form, params, self.edge_mask)
        return self.rms(model, self.edge_mask)

    def corner_rms(self, form, params):
        model = self.render(form, params, self.band)
        return {n: self.rms(model, bm) for n, (box, bm) in self.corners.items()}

    def dryrun_ssim(self, form, params, vitrea_Y, Lp=None):
        """Whole-crop SSIM (encoded luma) of vitrea's capture with 2 ≤ u ≤ L'+4 replaced by the model."""
        if Lp is None:
            Lp = (params['E'] * self.L) if form != 'F0' else self.L
        rep = self.inside & (self.u >= SS_LO) & (self.u <= Lp + 4)
        model = self.render(form, params, rep)
        dry = vitrea_Y.copy()
        dry[rep] = model[rep]
        return ssim_of(dry, self.Y), ssim_of(vitrea_Y, self.Y)

    def edge_period(self, form, params, u_row=2.5):
        """Peak spacing (CSS px) along the top edge at depth u_row in the model, straight section."""
        model = self.render(form, params, self.inside)
        s = self.scale
        y = int(round((self.cy / s - self.h / 2 + u_row) * s))
        xa = int(round((self.cx / s - self.w / 2 + self.r) * s))
        xb = int(round((self.cx / s + self.w / 2 - self.r) * s))
        row = model[y, xa:xb]
        row = np.nan_to_num(row - np.nanmean(row))
        pk, _ = find_peaks(row, distance=10 * s)
        pos = np.array(pk) / s + xa / s
        return pos, np.diff(pos)


def ssim_of(a_lin, b_lin):
    m = ssim_map(lin_to_srgb(np.clip(a_lin, 0, 1)), lin_to_srgb(np.clip(b_lin, 0, 1)))
    return float(m.mean())


def displacement_tau(cell, params):
    """F2t: normal component = profile; tangential = τ · profile · tanφ (the ellipse's tilt)."""
    G, E, p, tau = params['G'], params['E'], params['p'], params['tau']
    prof = cell.profile(G, E, p)
    nx, ny, ex, ey = cell.nx, cell.ny, cell.ex, cell.ey
    en = np.maximum(ex * nx + ey * ny, 0.2)
    tanphi_x = ex / en - nx
    tanphi_y = ey / en - ny
    return prof * nx + tau * prof * tanphi_x, prof * ny + tau * prof * tanphi_y


_orig_displacement = Cell.displacement


def _displacement(self, form, params):
    if form == 'F2t':
        return displacement_tau(self, params)
    return _orig_displacement(self, form, params)


Cell.displacement = _displacement
