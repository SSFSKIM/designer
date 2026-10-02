"""W44 G0 (a), (c): the readings beside T1, never gated (charter Design "T1", "Readings beside it").

Each reads one cell's native fixture and web capture (the capture checked against its row by
`cuts.capture`) and returns the statistic on each side; a ratio web / native is the reading.

  deep     T1-deep, the eye sheet's statistic: the SD of ENCODED Rec.709 luma, in codes (0-255),
           over the declared region eroded 8 CSS px (signed distance to the declared contour
           <= -8 x scale device px). W43's sheets record no crop of their own (`sheets.py` crops for
           display only: the declared box plus 24 CSS px), so this crop is DECLARED here: on c05 it
           reproduces the anchors `checkerboard-4__rrect-md__{rest,inactive}` 2x light at 2.87 / 9.08
           and 0.29 / 10.49 codes (the sheet's 2.9 / 9.1 and 0.3 / 10.5), and the 0.5 rest pair at
           1.74 / 2.54 (the sheet's 1.7 / 2.6).
  fine     T1-fine: the SD of the residual L - G(L, sigma 4 device px) in linear luminance (an
           unmasked Gaussian, scipy's default reflect border), over the native silhouette eroded
           4 CSS px (Euclidean distance to the silhouette's outside > 4 x scale device px).
  lattice  T1-lattice, the band G0 (c) found isolates the receded 2x photo lattice: the SD of a
           MASKED difference of Gaussians, sigma 1 to 4 CSS px (2-8 device px at 2x, 1-4 at 1x), of
           linear luminance over the native silhouette eroded 4 CSS px; the Gaussians are
           normalised over that eroded mask, so nothing outside the body enters the band.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

import bed as B

sys.path.insert(0, str(B.EVIDENCE / "port"))
import interior as P  # noqa: E402

DEEP_INSET_CSS = 8
FINE_SIGMA_DEVICE = 4.0
ERODE_CSS = 4
LATTICE_CSS = (1.0, 4.0)


def masked_gaussian(L: np.ndarray, mask: np.ndarray, sigma: float) -> np.ndarray:
    num = gaussian_filter(L * mask, sigma)
    den = gaussian_filter(mask.astype(np.float64), sigma)
    return num / np.maximum(den, 1e-12)


def encoded_luma(rgb: np.ndarray) -> np.ndarray:
    a = rgb.astype(np.float64)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def cell_geometry(profile: str, sid: str, native: np.ndarray) -> dict:
    scale = B.scale_of(profile)
    component = B.SCENES.component(sid)
    background = P.read(B.ROOT / "apps/reference-apple/fixtures/backgrounds" /
                        f"{B.SCENES.by_id[sid]['background']}@{scale}x.png")
    silhouette = P.native_interior(native, background, component, B.SCENES.canvas, scale)
    distance = P.signed_distance(component, B.SCENES.canvas, scale, native.shape[:2])
    eroded = distance_transform_edt(silhouette) > ERODE_CSS * scale
    return dict(scale=scale, background=background, silhouette=silhouette, signedDistance=distance,
                deep=distance <= -DEEP_INSET_CSS * scale, eroded=eroded)


def read(profile: str, sid: str, native: np.ndarray, web: np.ndarray, geometry: dict | None = None) -> dict:
    g = geometry or cell_geometry(profile, sid, native)
    out = {}
    for side, img in (("native", native), ("web", web)):
        L = P.luminance(img)
        lo, hi = (s * g["scale"] for s in LATTICE_CSS)
        band = masked_gaussian(L, g["eroded"], lo) - masked_gaussian(L, g["eroded"], hi)
        out[side] = dict(
            deep=float(encoded_luma(img)[g["deep"]].std()) if g["deep"].any() else None,
            fine=float((L - gaussian_filter(L, FINE_SIGMA_DEVICE))[g["eroded"]].std()) if g["eroded"].any() else None,
            lattice=float(band[g["eroded"]].std()) if g["eroded"].any() else None)
    ratios = {}
    for k in ("deep", "fine", "lattice"):
        n, w = out["native"][k], out["web"][k]
        ratios[k] = None if n in (None, 0) or w is None else w / n
    return dict(native=out["native"], web=out["web"], ratio=ratios,
                pixels=dict(deep=int(g["deep"].sum()), eroded=int(g["eroded"].sum())))
