"""W42 G0 instrument: the two-sided LINEAR control body for proof 1 (charter clause 2: "A two-sided control
reads the mirror statistic at vitrea's level ... A known-space control shows the reader cannot manufacture a
knee").

A vitrea-like body, rendered on the same declared cells as every family: the backdrop decoded to linear light,
blurred by two Gaussians on the canvas (clamp-to-edge), mixed two-sidedly at a share k, made affine and
encoded, then quantised as every synthetic render is:

    body = (1 - k) G(sn) * lin(B) + k G(sw) * lin(B),   y = round(enc(a + b body) + U(-0.5, 0.5))

It has no knee (lam = 0 by construction) and its space is linear, so a correct reader in the linear space
reads lam = 0 and s1/gain = 0, and the ENCODED reading of it shows what a wrong space manufactures. The
widths and share default to vitrea's shipped light-active 2x rrect-md body (memo B: sharp 1.58 dev, deep
about 20 dev, share 0.99) or any value the proof names.
"""
import numpy as np
from scipy import ndimage

import geometry as G
from tone import srgb_to_lin, lin_to_srgb


def render(cell, sn_pt, sw_pt, k, a=0.22, b=0.70, seed=0, noise=0.5):
    B = cell.B if cell.B.ndim == 2 else G.luma(cell.B * 255) / 255
    L = srgb_to_lin(255 * B)
    g = lambda s: ndimage.gaussian_filter(L, s * cell.scale, mode='nearest', truncate=4) if s > 0 else L
    body = (1 - k) * g(sn_pt) + k * g(sw_pt)
    y = lin_to_srgb(a + b * body)
    rng = np.random.default_rng(seed)
    yq = np.clip(np.round(y + rng.uniform(-noise, noise, y.shape)), 0, 255)
    img = np.full(cell.d.shape, np.nan)
    img[cell.mask] = yq[cell.mask]
    cell.y = img
    cell._rm = {}
    return img
