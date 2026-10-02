"""W44 G0 (b): the driver's interior statistic, ported to Python (charter clause 4).

What `cli/measure.ts` writes as `material.interiorStdDev{Native,Web}` and `interiorMean{...}`:

  1. `componentRegion` (`src/component-region.ts`): the scene's declared component placed on the
     declared canvas (left = round((W - w) / 2) + offset x, a group laid out from its members and
     spacing, a stack as base and over), each shape a rounded rect (a capsule's radius half its
     short side), the exact signed distance taken at PIXEL CENTRES at the profile's scale, and
     the region = every pixel at distance <= the margin (0 device px, the default).
  2. `extractSilhouette` luminance-delta (`src/silhouette.ts`), bounded to that region: a pixel is
     inside when |Y(image) - Y(background)| >= 0.02 in linear-light Rec.709 luminance, or, where
     that says no and the pixel or its background is not neutral, when the OKLab a/b distance
     between them is >= 0.03 (`DEFAULT_SILHOUETTE_THRESHOLD`, `DEFAULT_SILHOUETTE_CHROMA_THRESHOLD`).
  3. The interior is the NATIVE silhouette, for both sides ("one mask for both sides, and it is
     the NATIVE silhouette").
  4. `interiorLevel` (`src/metrics/material.ts`): over the mask, the linear luminance's mean and
     the population SD by the one-pass identity `max(0, E[Y^2] - E[Y]^2)`, as the driver takes it.

JavaScript's `Math.round` rounds half up, so placement uses `floor(x + 0.5)`. PNGs are decoded to
8-bit RGB as `pngjs` hands them over (no gamma or ICC applied by either side).
"""
from __future__ import annotations

import io
import math
from pathlib import Path

import numpy as np
from PIL import Image

LUMA = (0.2126, 0.7152, 0.0722)
THRESHOLD = 0.02
CHROMA_THRESHOLD = 0.03
SRGB_TO_LINEAR = np.array([(i / 255) / 12.92 if i / 255 <= 0.04045 else ((i / 255 + 0.055) / 1.055) ** 2.4
                           for i in range(256)], dtype=np.float64)


def js_round(x: float) -> int:
    return math.floor(x + 0.5)


def decode(raw: bytes) -> np.ndarray:
    return np.asarray(Image.open(io.BytesIO(raw)).convert("RGB"))


def read(path: Path) -> np.ndarray:
    return decode(Path(path).read_bytes())


def luminance(rgb: np.ndarray) -> np.ndarray:
    lin = SRGB_TO_LINEAR[rgb]
    return LUMA[0] * lin[..., 0] + LUMA[1] * lin[..., 1] + LUMA[2] * lin[..., 2]


def oklab_ab(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lin = SRGB_TO_LINEAR[rgb]
    r, g, b = lin[..., 0], lin[..., 1], lin[..., 2]
    l_ = np.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m_ = np.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s_ = np.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    a = 1.9779984951 * l_ - 2.428592205 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.808675766 * s_
    return a, bb


def _radius(shape: dict) -> float:
    if shape["kind"] in ("capsule", "capsule-circular"):
        return min(shape["size"]) / 2
    if shape["kind"] == "rrect":
        return shape.get("radius", 0)
    raise ValueError(f"no geometry for a {shape['kind']}")


def _place(shape: dict, canvas: dict, left=None, top=None) -> dict:
    w, h = shape["size"]
    ox, oy = shape.get("offset", [0, 0])
    return dict(left=left if left is not None else js_round((canvas["width"] - w) / 2) + ox,
                top=top if top is not None else js_round((canvas["height"] - h) / 2) + oy,
                width=w, height=h, radius=_radius(shape))


def place_component(component: dict, canvas: dict) -> list[dict]:
    if component["kind"] == "group":
        items = component["items"]
        total = sum(i["size"][0] for i in items) + component["spacing"] * (len(items) - 1)
        height = max(i["size"][1] for i in items)
        top = js_round((canvas["height"] - height) / 2)
        left = js_round((canvas["width"] - total) / 2)
        out = []
        for item in items:
            out.append(_place(item, canvas, left, top + js_round((height - item["size"][1]) / 2)))
            left += item["size"][0] + component["spacing"]
        return out
    if component["kind"] == "stack":
        return [_place(component["base"], canvas), _place(component["over"], canvas)]
    return [_place(component, canvas)]


def signed_distance(component: dict, canvas: dict, scale: int, shape: tuple[int, int]) -> np.ndarray:
    """Exact signed distance to the declared contour at pixel centres, device px, negative inside;
    the nearest of the placed shapes (`componentRegion`)."""
    height, width = shape
    if width != js_round(canvas["width"] * scale) or height != js_round(canvas["height"] * scale):
        raise ValueError(f"a {width}x{height} capture is not the declared canvas at {scale}x")
    y, x = np.indices((height, width), dtype=np.float64)
    px, py = x + 0.5, y + 0.5
    nearest = np.full((height, width), np.inf)
    for s in place_component(component, canvas):
        cx, cy = (s["left"] + s["width"] / 2) * scale, (s["top"] + s["height"] / 2) * scale
        hw, hh, r = s["width"] / 2 * scale, s["height"] / 2 * scale, s["radius"] * scale
        qx = np.abs(px - cx) - (hw - r)
        qy = np.abs(py - cy) - (hh - r)
        d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
        nearest = np.minimum(nearest, d)
    return nearest


def region(component: dict, canvas: dict, scale: int, shape, margin_px: float = 0) -> np.ndarray:
    return signed_distance(component, canvas, scale, shape) <= margin_px


def silhouette(image: np.ndarray, background: np.ndarray, bounded: np.ndarray) -> np.ndarray:
    """`extractSilhouette` luminance-delta with the chroma arm, bounded to `bounded`."""
    own, base = luminance(image), luminance(background)
    lum = np.abs(own - base) >= THRESHOLD
    neutral = ((image[..., 0] == image[..., 1]) & (image[..., 1] == image[..., 2]) &
               (background[..., 0] == background[..., 1]) & (background[..., 1] == background[..., 2]))
    a1, b1 = oklab_ab(image)
    a2, b2 = oklab_ab(background)
    chroma = (~neutral) & (np.sqrt((a1 - a2) ** 2 + (b1 - b2) ** 2) >= CHROMA_THRESHOLD)
    return bounded & (lum | chroma)


def level(image: np.ndarray, mask: np.ndarray) -> dict:
    """`interiorLevel`: mean and population SD by the driver's one-pass identity."""
    values = luminance(image)[mask]
    if values.size == 0:
        raise ValueError("the interior mask selected no pixels")
    count = values.size
    total = float(np.sum(values))
    squares = float(np.sum(values * values))
    mean = total / count
    return dict(mean=mean, stdDev=math.sqrt(max(0.0, squares / count - mean * mean)), count=count)


def native_interior(native: np.ndarray, background: np.ndarray, component: dict, canvas: dict,
                    scale: int) -> np.ndarray:
    return silhouette(native, background, region(component, canvas, scale, native.shape[:2]))


def code_step(mean: float) -> float:
    """One code at a cell (T1): the linear step of one encoded sRGB code at the linear level `mean`,
    the derivative of the sRGB decode at that level times 1/255 (about 0.0035 at linear 0.2 and
    0.0066 at 0.6). Below the decode's linear segment it is the segment's own 1/(255 * 12.92)."""
    if mean <= 0.0031308:
        return 1 / (255 * 12.92)
    encoded = 1.055 * mean ** (1 / 2.4) - 0.055
    return 2.4 / 1.055 * ((encoded + 0.055) / 1.055) ** 1.4 / 255
