import sys; sys.path.insert(0, '/Users/new/.claude/jobs/5c70e47f/tmp')
from w11lib import *
import numpy as np, itertools, json
from scipy.ndimage import gaussian_filter, map_coordinates
def sdf_rrect(W, H, cx, cy, w, h, r):
    ys, xs = np.mgrid[0:H, 0:W]
    px = np.abs(xs + 0.5 - cx) - (w / 2 - r); py = np.abs(ys + 0.5 - cy) - (h / 2 - r)
    d = np.sqrt(np.maximum(px, 0) ** 2 + np.maximum(py, 0) ** 2) + np.minimum(np.maximum(px, py), 0) - r
    gy, gx = np.gradient(d); nrm = np.sqrt(gx * gx + gy * gy) + 1e-9
    return d, gx / nrm, gy / nrm
def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0); return t * t * (3 - 2 * t)
def kscatter(span): return 0.4 + 0.6 * smoothstep(32, 256, span)
SB, SH = 1.25, 10.0
U0, U1 = 3, 24
class Cell:
    def __init__(self, Y, P, comp, scale=1):
        W, H = 320 * scale, 200 * scale; w, h, r = COMP[comp]
        self.Y, self.P, self.scale = Y, P, scale
        d, nx, ny = sdf_rrect(W, H, 160 * scale, 100 * scale, w * scale, h * scale, r * scale); self.u = -d / scale
        ys, xs = np.mgrid[0:H, 0:W]; self.xs, self.ys, self.nx, self.ny = xs, ys, nx, ny
        self.Gb = gaussian_filter(P, SB * scale, mode='nearest'); self.Gh = gaussian_filter(P, SH * scale, mode='nearest')
        self.k = kscatter(SPAN[comp])
        deep = self.u > U1 + 2
        X = (1 - self.k) * self.Gb + self.k * self.Gh
        A = np.stack([np.ones(deep.sum()), X[deep]], 1); coef, *_ = np.linalg.lstsq(A, Y[deep], rcond=None)
        self.a, self.t = coef[0], coef[1]
        self.band = (self.u >= U0) & (self.u <= U1)
        self.ub = self.u[self.band]; self.yb = Y[self.band]
        self._cache = {}
    def samples(self, L, p, S):
        key = (L, p, S)
        if key not in self._cache:
            prof = np.clip(1 - self.ub / L, 0, 1) ** p; D = S * prof * self.scale
            sx = self.xs[self.band] - self.nx[self.band] * D; sy = self.ys[self.band] - self.ny[self.band] * D
            self._cache[key] = (prof, map_coordinates(self.Gb, [sy, sx], order=1, mode='nearest'), map_coordinates(self.Gh, [sy, sx], order=1, mode='nearest'))
        return self._cache[key]
    def model(self, L, p, S, c, delta):
        prof, gb, gh = self.samples(L, p, S)
        kB = self.k + (1 - self.k) * c * prof
        return self.a * (1 - delta * prof) + self.t * ((1 - kB) * gb + kB * gh)
    def rms(self, *args):
        r = self.yb - self.model(*args); return float(np.sqrt(np.mean(r * r)))
    def full_model(self, L, p, S, c, delta):
        """the model on the whole canvas (band pixels replaced), for the SSIM dry run"""
        out = self.Y.copy(); out[self.band] = self.model(L, p, S, c, delta); return out
