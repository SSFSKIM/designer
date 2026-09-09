"""W26 G1b — the row assembly reader E is run on, shared by the control and the reference.

ONE SURFACE, ONE SCALE, MANY BACKDROPS. A row is one (backdrop, surface, scale) capture reduced to
the pixels of a depth band and the same band's basis columns. `assemble` builds every row a
component has and hands them to `w26blib.joint_profile`, which fits ONE kernel across all of them.

THE DEPTH BAND, and why it is not simply "the interior". `wgsl/optics.ts`'s share is a function of
depth and its ramp reaches 80 device px at dpr 1, which is further than `rrect-md`'s half-span. A
kernel fitted over a whole interior is therefore a depth average whatever the reader believes, so
the band is stated, the known share's spread inside it is reported with every control, and the
same band is used on the reference. The band's inner edge also clears the rim, the inner shadow
and the lens's displacement, none of which is a convolution of the backdrop.

WHAT IS EXCLUDED, and why. The solid backdrops carry no structure for a kernel to act on and
constrain only the offset. `photo` is not neutral, so reducing it to luma with ONE gain is an
approximation the synthetic backdrops do not need; it is fitted but its residual is reported
separately and `--no-photo` drops it, which is how its influence is measured rather than assumed.
"""

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w26blib as E  # noqa: E402
import w25lib as L  # noqa: E402

# The thick untinted probe rows of one surface. Order is the order they are reported in.
BACKDROPS = ("impulse", "checkerboard-64", "checkerboard-32", "checkerboard",
             "checkerboard-8", "checkerboard-4", "hc-text", "photo")
NEUTRAL = tuple(b for b in BACKDROPS if b != "photo")


def depth_mask(cell, scale, shape, lo_css, hi_css):
    """Pixels whose depth inside the contour lies in [lo, hi] CSS px."""
    if cell.kind in ("stack", "group"):
        raise ValueError("reader E reads single-box surfaces only")
    d = L.signed_distance(cell.box, cell.radius, scale, shape, cell.kind)
    depth = -d
    return (depth >= lo_css) & (depth <= hi_css)


def load_row(path, backdrop, cell, scale, band, nodes, pad="edge", bg_override=None):
    if not os.path.exists(path):
        return None
    shape = (int(200 * scale), int(320 * scale))
    lum = L.luma_of(path)
    if lum.shape != shape:
        return None
    mask = depth_mask(cell, scale, shape, band[0], band[1])
    if mask.sum() < 500:
        return None
    bg = L.background_for(backdrop, scale, shape) if bg_override is None else bg_override
    cols = E.basis_columns(bg, nodes, pad=pad)
    return {"name": backdrop, "A": cols[:, mask], "y": lum[mask].astype(np.float64),
            "mask": mask, "bg": bg, "level": float(lum[mask].mean()),
            "amp": float(np.percentile(lum[mask], 98) - np.percentile(lum[mask], 2))}


def assemble(source, profile, scale, comp, band, nodes, comps, backdrops=BACKDROPS,
             pad="edge", root=None):
    """Every available row of one surface at one scale. `source` is 'native' or 'web'."""
    cell = L.Cell(comp, comps)
    rows = []
    for backdrop in backdrops:
        sid = f"{backdrop}__{comp}__rest"
        if source == "native":
            path = L.native_path(profile, sid)
        else:
            path = (L.web_path(profile, sid, "webgpu") if root is None
                    else os.path.join(root, profile, sid, f"{sid}__webgpu.png"))
        row = load_row(path, backdrop, cell, scale, band, nodes, pad=pad)
        if row is not None:
            rows.append(row)
    return cell, rows


def summarise(nodes, c, chain_profiles=None, freqs=None):
    """Reader E's answer, reduced to the statistics the wave asks a width question in."""
    w = E.widths_of_profile(nodes, c)
    s_mtf, rel_mtf, *_ = E.sigma_matching_mtf(nodes, c)
    two = E.fit_two_gaussians(nodes, c)
    out = {"sigmaHwhm": w["sigmaHwhm"], "sigmaRms": w["sigmaRms"],
           "sigmaMtf": s_mtf, "sigmaMtfRel": rel_mtf, "two": two}
    if freqs is not None:
        out["mtf"] = E.mtf_of_profile(nodes, c, freqs).tolist()
    if chain_profiles:
        out["mech"] = E.fit_vitrea_mechanism(nodes, c, chain_profiles)
    return out


def rel_mtf_error(nodes, c, ref_c, band=E.MTF_BAND, n=25):
    f = E.band_freqs(n, band)
    a = E.mtf_of_profile(nodes, c, f)
    b = E.mtf_of_profile(nodes, ref_c, f)
    return float(np.sqrt(np.mean((a / np.clip(np.abs(b), 1e-9, None) - 1.0) ** 2))), \
        float(np.max(np.abs(a / np.clip(np.abs(b), 1e-9, None) - 1.0))), f, a, b


def fmt_profile(nodes, c, cols=9):
    """The radial profile as text, normalised to its own peak."""
    peak = max(float(np.max(c)), 1e-300)
    out = []
    for i in range(0, nodes.size, cols):
        out.append("   " + "  ".join(f"{nodes[j]:5.1f}:{c[j] / peak:6.4f}"
                                     for j in range(i, min(i + cols, nodes.size))))
    return out
