"""A Python replica of the calibration harness's silhouette extractor and the
three shape metrics built on it, for the W26 G2 extractor spike.

Read-only against every canonical input. The replica is validated cell by cell
against the committed `results/matrix.json` before any conclusion is drawn from
it (`validate.py`); nothing here is a second definition of the instrument, it is
a transcription of `packages/calibration/src/{silhouette,component-region}.ts`
and `src/metrics/shape.ts` so the rule can be scanned over parameters the TS
harness exposes only through a full capture run.
"""

from __future__ import annotations

import json
import math
import os

import numpy as np
from PIL import Image
from scipy import ndimage

REPO = "/Users/new/Developer/GitHub/designer"
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")
CAPTURES = os.path.join(REPO, "packages/calibration/web-captures")
SCENES = json.load(open(os.path.join(REPO, "apps/reference-apple/scenes.json")))
MANIFEST = json.load(open(os.path.join(FIXTURES, "manifest.json")))

DEFAULT_THRESHOLD = 0.02
DEFAULT_CHROMA = 0.03

_i = np.arange(256) / 255.0
SRGB_TO_LINEAR = np.where(_i <= 0.04045, _i / 12.92, ((_i + 0.055) / 1.055) ** 2.4)


def load(path):
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)


def linear(img):
    return SRGB_TO_LINEAR[img[:, :, :3].astype(np.int32)]


def luma(img):
    lin = linear(img)
    return 0.2126 * lin[:, :, 0] + 0.7152 * lin[:, :, 1] + 0.0722 * lin[:, :, 2]


def oklab_ab(img):
    lin = linear(img)
    r, g, b = lin[:, :, 0], lin[:, :, 1], lin[:, :, 2]
    l = np.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = np.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = np.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    a = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s
    return a, bb


# ---------------------------------------------------------------- geometry


def _radius(spec):
    if spec["kind"] == "capsule":
        return min(spec["size"]) / 2
    if spec["kind"] == "rrect":
        return spec.get("radius", 0)
    raise ValueError(spec["kind"])


def _place(spec, canvas, left=None, top=None):
    w, h = spec["size"]
    ox, oy = spec.get("offset", [0, 0])
    return {
        "left": round((canvas["width"] - w) / 2) + ox if left is None else left,
        "top": round((canvas["height"] - h) / 2) + oy if top is None else top,
        "width": w,
        "height": h,
        "radius": _radius(spec),
    }


def place_component(component, canvas):
    if component.get("kind") == "group":
        items = component["items"]
        spacing = component["spacing"]
        total = sum(i["size"][0] for i in items) + spacing * (len(items) - 1)
        height = max(i["size"][1] for i in items)
        top = round((canvas["height"] - height) / 2)
        left = round((canvas["width"] - total) / 2)
        out = []
        for item in items:
            out.append(_place(item, canvas, left, top + round((height - item["size"][1]) / 2)))
            left += item["size"][0] + spacing
        return out
    if component.get("kind") == "stack":
        return [_place(component["base"], canvas), _place(component["over"], canvas)]
    return [_place(component, canvas)]


def component_region(component, canvas, scale, width, height, margin_px=0.0):
    """`componentRegion` — the declared geometry rasterised by pixel-centre
    containment, plus the exact signed distance field."""
    placed = place_component(component, canvas)
    ys, xs = np.mgrid[0:height, 0:width]
    px = xs + 0.5
    py = ys + 0.5
    nearest = np.full((height, width), np.inf)
    for shape in placed:
        cx = (shape["left"] + shape["width"] / 2) * scale
        cy = (shape["top"] + shape["height"] / 2) * scale
        hw = (shape["width"] / 2) * scale
        hh = (shape["height"] / 2) * scale
        r = shape["radius"] * scale
        qx = np.abs(px - cx) - (hw - r)
        qy = np.abs(py - cy) - (hh - r)
        d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
        nearest = np.minimum(nearest, d)
    return (nearest <= margin_px).astype(np.uint8), nearest


# ---------------------------------------------------------------- extraction


def extract_luminance_delta(image, background, region, threshold=DEFAULT_THRESHOLD,
                            chroma=DEFAULT_CHROMA):
    """`extractSilhouette` under the luminance-delta rule, chroma arm included."""
    own = luma(image)
    base = luma(background)
    mask = (np.abs(own - base) >= threshold)
    if chroma is not None:
        rgb = image[:, :, :3].astype(np.int32)
        brgb = background[:, :, :3].astype(np.int32)
        neutral = ((rgb[:, :, 0] == rgb[:, :, 1]) & (rgb[:, :, 1] == rgb[:, :, 2])
                   & (brgb[:, :, 0] == brgb[:, :, 1]) & (brgb[:, :, 1] == brgb[:, :, 2]))
        pa, pb = oklab_ab(image)
        qa, qb = oklab_ab(background)
        chroma_hit = (np.hypot(pa - qa, pb - qb) >= chroma) & (~neutral)
        mask = mask | chroma_hit
    return (mask & (region != 0)).astype(np.uint8)


def extract_alpha(image, region, threshold=0.5):
    return ((image[:, :, 3] >= threshold * 255) & (region != 0)).astype(np.uint8)


# ---------------------------------------------------------------- topology

_CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool)
_BOX = np.ones((3, 3), dtype=bool)


def fill_holes(mask):
    """`fillSilhouetteHoles`: 4-connected flood of the background from the image
    border; anything unreached is enclosed."""
    free = mask == 0
    seed = np.zeros_like(free)
    seed[0, :] = free[0, :]
    seed[-1, :] = free[-1, :]
    seed[:, 0] = free[:, 0]
    seed[:, -1] = free[:, -1]
    outside = ndimage.binary_propagation(seed, mask=free, structure=_CROSS)
    return (mask.astype(bool) | ~outside).astype(np.uint8)


def hole_count(mask, region):
    """`silhouetteHoleCount`: 4-connected runs of region pixels the mask excludes
    that reach neither the image border nor the region's edge."""
    excluded = (region != 0) & (mask == 0)
    labels, n = ndimage.label(excluded, structure=_CROSS)
    if n == 0:
        return 0
    outside_region = (region == 0)
    touch = ndimage.binary_dilation(outside_region, structure=_CROSS) & excluded
    border = np.zeros(excluded.shape, dtype=bool)
    border[0, :] = border[-1, :] = True
    border[:, 0] = border[:, -1] = True
    open_seed = excluded & (touch | border)
    open_labels = set(np.unique(labels[open_seed]).tolist())
    open_labels.discard(0)
    return int(n - len(open_labels))


def body_count(mask):
    filled = fill_holes(mask)
    _, n = ndimage.label(filled, structure=_BOX)
    return int(n)


def boundary_mask(mask):
    m = mask.astype(bool)
    inside = np.zeros_like(m)
    inside[1:-1, 1:-1] = (m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1]
                          & m[1:-1, :-2] & m[1:-1, 2:])
    return (m & ~inside).astype(np.uint8)


def iou(a, b):
    a = a.astype(bool)
    b = b.astype(bool)
    inter = np.count_nonzero(a & b)
    union = np.count_nonzero(a | b)
    return inter / union


def _p95(sorted_vals):
    rank = 0.95 * (len(sorted_vals) - 1)
    lo = math.floor(rank)
    hi = math.ceil(rank)
    return float(sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (rank - lo))


def contour_distance(a, b):
    ba = boundary_mask(fill_holes(a))
    bb = boundary_mask(fill_holes(b))
    da = ndimage.distance_transform_edt(ba == 0)
    db = ndimage.distance_transform_edt(bb == 0)
    samples = np.concatenate([db[ba != 0], da[bb != 0]])
    s = np.sort(samples)
    return {
        "maxPx": float(s[-1]),
        "p95Px": _p95(s),
        "meanPx": float(s.mean()),
        "rmsPx": float(np.sqrt((s ** 2).mean())),
        "sampleCount": int(s.size),
    }


# ---------------------------------------------------------------- cell wiring


def scene(scene_id):
    for s in SCENES["scenes"]:
        if s["id"] == scene_id:
            return s
    raise KeyError(scene_id)


def profile_scale(profile_key):
    return 2 if "-2x-" in profile_key else 1


def background_path(scene_id, scale):
    bg = scene(scene_id)["background"]
    files = MANIFEST["backgrounds"]
    return os.path.join(FIXTURES, files.get(f"{bg}@{scale}x", files.get(bg)))


def native_path(profile_key, scene_id):
    return os.path.join(FIXTURES, profile_key, f"{scene_id}.png")


def web_path(profile_key, scene_id, renderer, root=CAPTURES, alpha=False):
    suffix = "__alpha" if alpha else ""
    return os.path.join(root, profile_key, scene_id, f"{scene_id}__{renderer}{suffix}.png")


def cell_inputs(profile_key, scene_id, renderer, root=CAPTURES, margin_px=0.0):
    scale = profile_scale(profile_key)
    native = load(native_path(profile_key, scene_id))
    web = load(web_path(profile_key, scene_id, renderer, root))
    bg = load(background_path(scene_id, scale))
    h, w = native.shape[:2]
    component = SCENES["components"][scene(scene_id)["component"]]
    region, sdist = component_region(component, SCENES["canvas"], scale, w, h, margin_px)
    return native, web, bg, region, sdist
