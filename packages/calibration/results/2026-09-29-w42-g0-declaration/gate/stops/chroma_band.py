"""W42 G0 gate: Stop P, the photo band-pass chroma energy (charter clause 10; stopP).

Per pixel OKLab (a, b) of the encoded image, band-passed by Gaussians normalised to the deep
body (the support IS the region, so neither the lens band nor the exterior enters a band value):

    F = G(1) - G(4),   M = G(4) - G(16)      (sigma in CSS px, times the scale in device px)
    E_band = sqrt(mean over the deep body of (Delta a^2 + Delta b^2))

The bar per band is |E_cand - E_nat| <= |E_ship - E_nat| + res_band, where res_band is the band
energy of a one-code quantisation field at the NATIVE image's colours (the declaration's
resolution rule), frozen in `stops-declaration.json` and recomputed on every run.

    python3.12 -B chroma_band.py --write-resolution   # fill stopP.resolution.perCell (natives only)
    python3.12 -B chroma_band.py                      # print the frozen table beside a recomputation
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache

import numpy as np
from scipy import ndimage

import stops_common as common

DECL = common.DECLARATION["stopP"]
BANDS = dict(F=(1.0, 4.0), M=(4.0, 16.0))
QUANTISATION_VARIANCE = 1.0 / 6.0  # q = u1 - u2, u ~ U(-0.5, 0.5): the difference of two roundings
RELATIVE_RESOLUTION_AGREEMENT = 1e-9

# Ottosson's OKLab; the matrices of memo A's port (metrics.py), proven against the matrix rows.
OK_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                  [0.2119034982, 0.6806995451, 0.1073969566],
                  [0.0883024619, 0.2817188376, 0.6299787005]])
OK_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                  [1.9779984951, -2.4285922050, 0.4505937099],
                  [0.0259040371, 0.7827717662, -0.8086757660]])


def population() -> list[tuple[str, str]]:
    return common.declared_population("stopP", "photo", untinted_only=True)


def to_linear(codes: np.ndarray) -> np.ndarray:
    x = np.asarray(codes, dtype=np.float64) / 255.0
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def oklab(codes: np.ndarray) -> np.ndarray:
    return np.cbrt(to_linear(codes) @ OK_M1.T) @ OK_M2.T


def oklab_ab(codes: np.ndarray) -> np.ndarray:
    return oklab(codes)[..., 1:]


def deep_threshold(component: str) -> float:
    """memo A's D = max(6, min(16, half the maximum depth)), the maximum depth the inradius."""
    value = max(6.0, min(16.0, 0.5 * common.short_side(component) / 2))
    declared = DECL["region"]["deepThresholdCssPx"][component]
    if value != declared:
        raise common.Refused(f"{component}: D = {value} is not the declared {declared}")
    return value


@lru_cache(maxsize=None)
def region(component: str, scale: int) -> np.ndarray:
    return common.depth_map(component, scale) >= deep_threshold(component)


@lru_cache(maxsize=None)
def kernel(sigma_device: float) -> np.ndarray:
    radius = int(np.ceil(4 * sigma_device))
    x = np.arange(-radius, radius + 1, dtype=np.float64)
    k = np.exp(-0.5 * (x / sigma_device) ** 2)
    return k / k.sum()


def separable(field: np.ndarray, k: np.ndarray) -> np.ndarray:
    out = ndimage.correlate1d(field, k, axis=0, mode="constant", cval=0.0)
    return ndimage.correlate1d(out, k, axis=1, mode="constant", cval=0.0)


def masked_blur(field: np.ndarray, mask: np.ndarray, sigma_device: float) -> np.ndarray:
    k = kernel(sigma_device)
    m = mask.astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        return separable(field * m, k) / separable(m, k)


def band_fields(ab: np.ndarray, mask: np.ndarray, scale: int) -> dict[str, np.ndarray]:
    blurs = {}
    for sigma in sorted({s for pair in BANDS.values() for s in pair}):
        blurs[sigma] = np.stack([masked_blur(ab[..., c], mask, sigma * scale)
                                 for c in range(ab.shape[-1])], -1)
    return {name: blurs[lo] - blurs[hi] for name, (lo, hi) in BANDS.items()}


def energies_of_ab(ab: np.ndarray, mask: np.ndarray, scale: int) -> dict[str, float]:
    if not mask.any():
        return {name: None for name in BANDS}
    fields = band_fields(ab, mask, scale)
    return {name: float(np.sqrt((f[mask] ** 2).sum(-1).mean())) for name, f in fields.items()}


def energies(image: np.ndarray, component: str, scale: int) -> dict[str, float]:
    return energies_of_ab(oklab_ab(image), region(component, scale), scale)


# ---------------------------------------------------------------------------------------------
# Resolution: the band energy of the one-code quantisation field at the native's colours.

def secant_jacobian_norm2(codes: np.ndarray) -> np.ndarray:
    """||d(a, b)/d(R, G, B)||_F^2 per pixel, by a +/- 0.5-code secant clipped at the rails."""
    total = np.zeros(codes.shape[:2])
    for channel in range(3):
        step = np.zeros(3)
        step[channel] = 0.5
        hi, lo = np.clip(codes + step, 0, 255), np.clip(codes - step, 0, 255)
        width = (hi - lo)[..., channel]
        slope = (oklab_ab(hi) - oklab_ab(lo)) / width[..., None]
        total += (slope ** 2).sum(-1)
    return total


def band_noise_energy(weight: np.ndarray, mask: np.ndarray, scale: int, band: str) -> float:
    """sqrt(mean_x sum_y h(x, y)^2 weight(y)) for the band's mask-normalised filter h.

    h(x, y) = k_lo(x - y) m(y) / N_lo(x) - k_hi(x - y) m(y) / N_hi(x); the squares and the cross
    term are separable kernels, so the expectation is exact for i.i.d. noise of per-pixel
    variance `weight`.
    """
    lo, hi = (s * scale for s in BANDS[band])
    k_lo, k_hi = kernel(lo), kernel(hi)
    pad = (len(k_hi) - len(k_lo)) // 2
    k_lo_padded = np.pad(k_lo, (pad, pad))
    m = mask.astype(np.float64)
    mw = m * weight
    n_lo, n_hi = separable(m, k_lo), separable(m, k_hi)
    with np.errstate(invalid="ignore", divide="ignore"):
        variance = (separable(mw, k_lo ** 2) / n_lo ** 2
                    - 2 * separable(mw, k_lo_padded * k_hi) / (n_lo * n_hi)
                    + separable(mw, k_hi ** 2) / n_hi ** 2)
    return float(np.sqrt(variance[mask].mean()))


def resolution_of(codes: np.ndarray, mask: np.ndarray, scale: int) -> dict[str, float]:
    weight = QUANTISATION_VARIANCE * secant_jacobian_norm2(codes)
    return {band: band_noise_energy(weight, mask, scale, band) for band in BANDS}


def computed_resolution(profile: str, scene: str, image: np.ndarray | None = None) -> dict:
    _scheme, scale = common.PROFILES[profile]
    component = common.parse_scene(scene)[1]
    image = common.native(profile, scene) if image is None else image
    return resolution_of(image, region(component, scale), scale)


def frozen_resolution(profile: str, scene: str) -> dict[str, float]:
    table = DECL["resolution"]["perCell"]
    if not table:
        raise common.Refused("stopP.resolution.perCell is empty: run "
                             "`chroma_band.py --write-resolution` first")
    return table[f"{profile}/{scene}"]


def checked_resolution(profile: str, scene: str, native_image: np.ndarray) -> dict[str, float]:
    frozen = frozen_resolution(profile, scene)
    now = computed_resolution(profile, scene, native_image)
    for band in BANDS:
        if abs(now[band] - frozen[band]) > RELATIVE_RESOLUTION_AGREEMENT * frozen[band]:
            raise common.Refused(f"{profile}/{scene}: res_{band} recomputes to {now[band]!r}, the "
                                 f"declaration froze {frozen[band]!r}")
    return frozen


# ---------------------------------------------------------------------------------------------

def censored_fraction(image: np.ndarray, mask: np.ndarray) -> float:
    pixels = image[mask]
    return float(((pixels >= 250) | (pixels <= 5)).any(-1).mean())


def read(trees: common.Trees) -> dict:
    """Stop P over its declared population: native, shipped and candidate per cell."""
    cells = []
    for profile, scene in population():
        scheme, scale = common.PROFILES[profile]
        component = common.parse_scene(scene)[1]
        native_image = common.native(profile, scene)
        res = checked_resolution(profile, scene, native_image)
        nat = energies(native_image, component, scale)
        ship = energies(trees.shipped(profile, scene).image, component, scale)
        candidate = trees.candidate(profile, scene)
        cand = energies(candidate.image, component, scale) if candidate else None
        statistics = {band: common.judge(nat[band], ship[band],
                                         cand[band] if cand else None, res[band])
                      for band in BANDS}
        mask = region(component, scale)
        cells.append(dict(
            profile=profile, scene=scene, set=common.ROLE[scene], scheme=scheme, scale=scale,
            pose=common.pose_of(scene), regionPixels=int(mask.sum()),
            deepThresholdCssPx=deep_threshold(component),
            nativeCensoredFraction=censored_fraction(native_image, mask),
            candidateCapture=None if candidate is None else dict(
                pngSha256=candidate.png_sha256, metaSha256=candidate.meta_sha256),
            statistics=statistics,
            verdict=common.combine([v["verdict"] for v in statistics.values()])))
    verdicts = [c["verdict"] for c in cells]
    return dict(name=DECL["name"], units=DECL["units"], cells=cells,
                counts=common.counts(verdicts), verdict=common.combine(verdicts))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write-resolution", action="store_true",
                        help="compute res_band from the natives alone and freeze it in the "
                             "declaration (refused once a table is frozen)")
    args = parser.parse_args()
    table = {f"{p}/{s}": computed_resolution(p, s) for p, s in population()}
    if args.write_resolution:
        declaration = json.loads(common.DECLARATION_PATH.read_text())
        if declaration["stopP"]["resolution"]["perCell"] is not None:
            raise common.Refused("the resolution table is already frozen")
        declaration["stopP"]["resolution"]["perCell"] = table
        common.DECLARATION_PATH.write_text(common.dump_json(declaration))
        print(f"froze res_band for {len(table)} cells into {common.DECLARATION_PATH.name}")
    frozen = DECL["resolution"]["perCell"] or {}
    for key, value in table.items():
        was = frozen.get(key)
        print(f"{key:<85} F {value['F'] * 1e3:.5f}  M {value['M'] * 1e3:.5f}  (x1e-3)"
              + ("" if was is None else
                 f"  frozen F {was['F'] * 1e3:.5f} M {was['M'] * 1e3:.5f}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
