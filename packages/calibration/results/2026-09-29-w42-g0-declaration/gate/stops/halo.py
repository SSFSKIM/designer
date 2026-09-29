"""W42 G0 gate: Stop H, the impulse halo/annulus statistic (charter clause 10; stopH).

The impulse backdrop is black with fifteen 4 x 4 CSS px white dots on a 64 CSS px lattice, so
the body's response around each dot is its spatial kernel seen directly. Per admitted dot, on
Rec.709 luma of encoded codes and in CSS px from the dot's backdrop centroid:

    peak    = mean(core, r < 2)          - median(floor ring, 8 <= r < 10)
    annulus = mean(annulus, 2 <= r < 8)  - median(floor ring)

and per cell the median over admitted dots. A dot is admitted only if its whole r < 10 disc is
inside the shape at depth >= 2 CSS px and its centroid lies past the lens extent, so the ring is
centred on an undisplaced dot (the declaration's admission and the evidence for it).

Run through `stops.py`; `python3.12 -B halo.py` prints the admission per shape and scale.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
from scipy import ndimage

import stops_common as common

DECL = common.DECLARATION["stopH"]
RINGS = dict(core=(0.0, 2.0), annulus=(2.0, 8.0), floor=(8.0, 10.0))
RIM_DEPTH = 2.0
LENS = dict(gain=1.337, height_per_span=0.25, height_max=20.0)
RES = float(DECL["resolution"]["res"])
STATISTICS = ("peak", "annulus")


def population() -> list[tuple[str, str]]:
    return common.declared_population("stopH", "impulse", untinted_only=False)


@lru_cache(maxsize=None)
def dots(scale: int) -> list[tuple[float, float]]:
    """Backdrop dot centroids in CSS px, refused unless they are the declared lattice."""
    backdrop = common.rgb(common.FIXTURES / "backgrounds" / f"impulse@{scale}x.png")
    white = backdrop[..., 1] > 127
    labels, n = ndimage.label(white, structure=np.ones((3, 3)))
    centres = ndimage.center_of_mass(white, labels, range(1, n + 1))
    found = sorted((float((x + 0.5) / scale), float((y + 0.5) / scale)) for y, x in centres)
    expected = sorted((32.0 + 64 * i, 40.0 + 64 * j) for i in range(5) for j in range(3))
    if len(found) != 15 or np.max(np.abs(np.array(found) - np.array(expected))) > 1e-9:
        raise common.Refused(f"impulse@{scale}x.png: dots {found} are not the declared lattice")
    return found


def lens_extent(component: str) -> float:
    span = common.short_side(component)
    extent = LENS["gain"] * min(LENS["height_per_span"] * span, LENS["height_max"])
    declared = DECL["admission"]["lensExtentCssPx"].get(component)
    if declared is not None and abs(extent - declared) > 5e-4:
        raise common.Refused(f"{component}: lens extent {extent} is not the declared {declared}")
    return extent


@lru_cache(maxsize=None)
def admitted(component: str, scale: int) -> list[tuple[float, float]]:
    """The dots the declaration admits on a shape, derived from geometry alone."""
    depth = common.depth_map(component, scale)
    xs, ys = common.pixel_grid(scale)
    extent = lens_extent(component)
    out = []
    for cx, cy in dots(scale):
        disc = np.hypot(xs - cx, ys - cy) < RINGS["floor"][1]
        centre_depth = -float(common.sdf_at(component, np.array(cx), np.array(cy)))
        if depth[disc].min() >= RIM_DEPTH and centre_depth >= extent:
            out.append((cx, cy))
    declared = [tuple(map(float, d)) for d in DECL["admission"]["admittedDots"].get(component, [])]
    if out != declared:
        raise common.Refused(f"{component} {scale}x: geometry admits {out}, the declaration "
                             f"lists {declared}")
    return tuple(out)


def ring_masks(scale: int, centre: tuple[float, float]) -> dict[str, np.ndarray]:
    xs, ys = common.pixel_grid(scale)
    r = np.hypot(xs - centre[0], ys - centre[1])
    return {name: (r >= lo) & (r < hi) for name, (lo, hi) in RINGS.items()}


def luma(image: np.ndarray) -> np.ndarray:
    return image @ common.W709


def dot_statistics(image: np.ndarray, masks: dict[str, np.ndarray]) -> dict[str, float]:
    y = luma(image)
    floor = float(np.median(y[masks["floor"]]))
    return dict(peak=float(y[masks["core"]].mean()) - floor,
                annulus=float(y[masks["annulus"]].mean()) - floor,
                floor=floor)


def cell_statistics(image: np.ndarray, component: str, scale: int) -> dict:
    """Per-dot readings and the cell's medians; no admitted dot leaves every statistic None."""
    per_dot = []
    for centre in admitted(component, scale):
        reading = dot_statistics(image, ring_masks(scale, centre))
        per_dot.append(dict(dot=list(centre), **reading))
    cell = {s: (float(np.median([d[s] for d in per_dot])) if per_dot else None)
            for s in STATISTICS}
    return dict(cell=cell, dots=per_dot)


def read(trees: common.Trees) -> dict:
    """Stop H over its declared population: native, shipped and candidate per cell."""
    cells = []
    for profile, scene in population():
        scheme, scale = common.PROFILES[profile]
        _backdrop, component, state = common.parse_scene(scene)
        nat = cell_statistics(common.native(profile, scene), component, scale)
        ship = cell_statistics(trees.shipped(profile, scene).image, component, scale)
        candidate = trees.candidate(profile, scene)
        cand = cell_statistics(candidate.image, component, scale) if candidate else None
        statistics = {
            s: common.judge(nat["cell"][s], ship["cell"][s],
                            cand["cell"][s] if cand else None, RES)
            for s in STATISTICS}
        cells.append(dict(
            profile=profile, scene=scene, set=common.ROLE[scene], scheme=scheme, scale=scale,
            pose=common.pose_of(scene), tinted="-tint-" in state,
            candidateCapture=None if candidate is None else dict(
                pngSha256=candidate.png_sha256, metaSha256=candidate.meta_sha256),
            dots=dict(native=nat["dots"], shipped=ship["dots"],
                      candidate=cand["dots"] if cand else None),
            statistics=statistics,
            verdict=common.combine([v["verdict"] for v in statistics.values()])))
    verdicts = [c["verdict"] for c in cells]
    return dict(name=DECL["name"], units=DECL["units"], resolution=RES, cells=cells,
                counts=common.counts(verdicts), verdict=common.combine(verdicts))


if __name__ == "__main__":
    for component in sorted(DECL["admission"]["admittedDots"]):
        for scale in (1, 2):
            print(f"{component} {scale}x: lens extent {lens_extent(component):.3f} CSS px, "
                  f"admitted {admitted(component, scale)}")
