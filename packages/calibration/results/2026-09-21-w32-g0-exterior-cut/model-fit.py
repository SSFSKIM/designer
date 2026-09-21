#!/usr/bin/env python3
"""W32 G0 — the renderer's own falloff model, fitted to BOTH sides' per-band
per-direction transmission, with its conditioning: what Apple's outset reads,
and how far the instrument's model is from the shader (claims §5.166; W32
acceptance clause 1, and §5.162 §9's open finding N-10).

    python3 model-fit.py > model-fit.txt        # writes model-fit.json beside it

Runs in about ten minutes on the committed matrix. Pure standard library, like
every other reader under `results/`: an evidence script that needed a wheel
installed would not reproduce.

## The model, and whose it is

The shader's exterior (`packages/renderer-webgpu/src/wgsl/optics.ts`,
`outer_shadow`) is the group's own signed-distance field translated down by
`offsetPx`, outset by `spreadPx` and blurred by a Gaussian of standard deviation
`sigmaPx`, composited as an alpha on pure black. Written as a transmission of
the backdrop at a point `p`:

    a(p)  =  1 − α · Ψ( (d(p_x, p_y − offset) − spread) / σ )

with `d` the exact signed distance to the DECLARED contour — the same analytic
field `component-region.ts` builds and the same one the shadow axis cuts its
bands from — and `Ψ(z) = 1 − Φ(z)`, the falloff the shader writes as
`outer_shadow_falloff`. Four free parameters: `α`, `σ`, `spread`, `offset`.

**This is the linear-light form**, and one of this gate's readings is that it is
not the shape vitrea draws. The shader composites its alpha in the canvas's
compositing space — `alpha = 1 − (1 − occ)^(1/2.4)` and the multiply happens
there — so in LINEAR light, which is the space the affine pair is fitted in,
vitrea's transmission is

    a_encoded(p)  =  ( 1 − A · Ψ(…) ) ^ 2.4

which agrees with the linear form at `Ψ = 0` and at `Ψ = 1` and differs in
between. Both are fitted on the web side and the difference between them is
reported: if the encoded form returns the shipped triple and the linear one does
not, the gap is the INSTRUMENT'S model error and not a disagreement about the
material, and G1 must fit the encoded form or carry the bias.

## What is fitted against what

The observations are the axis's own `slopeALinear` per band per direction,
`0-3` excluded (it holds the body's own edge, §5.62) and the pooled direction
`all` excluded (it is the four sectors again, not a fifth observation), over the
bands this gate's admitted-band rule allows at that cell's clearance. That is
16 observations at spans 32, 44 and 96, 12 at span 128 and 8 at span 160,
against four free parameters.

The model's prediction for a band is the MEAN of `a(p)` over that band's pixels
in that direction. That is the right functional for a slope: with `rendered =
a(p)·bg(p)`, the least-squares slope over a band is
`cov(bg, a·bg) / var(bg)`, which equals `E[a]` exactly when `a` and `bg` are
independent across the band's pixels — and they are, because `a` is a function
of the distance from the contour and `bg` is the scene's backdrop, which knows
nothing about where the component is. Stated rather than assumed: the assumption
is checkable and its failure would show as a systematic residual on the
structured backdrops and not on `photo`, which §3 prints per scene.

`α` is solved in closed form at every step rather than searched, because the
model is linear in it: `α = Σ(1 − a_obs)·Ψ̄ / Σ Ψ̄²` over the observations. The
search is therefore three-dimensional and a Nelder–Mead simplex is enough.

## The geometry, and the one approximation in it

The distance field, the placement and the direction sectors are reproduced from
`component-region.ts` and `metrics/shadow.ts` term for term — `place()` centres
the declared box on the 320×200 canvas at the row's scale,
`roundedRectSignedDistance` is the same formula, and `directionOf` normalises by
the component's own half-extents so the sector boundaries are the bounding box's
diagonals. The bands are cut from the UNSHIFTED distance, as the axis cuts them;
only the model's argument is shifted.

The approximation: each (band, direction) group's pixels are subsampled to at
most `SAMPLES_PER_GROUP` points, RANK-STRATIFIED by their unshifted distance, so
the subsample carries the group's distance distribution exactly rather than a
scanline slice of it. §1 prints the check that motivated the number — the same
fit run against every pixel of one cell, against the subsample.

**Nothing is fitted into a document and nothing is captured.** Every number is a
cut of `results/matrix.json`, of `scenes.json`'s geometry and of the shipped
documents read for their leaves (W32 X2, X5).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent

MATRIX = PACKAGE / "results/matrix.json"
SCENES = ROOT / "apps/reference-apple/scenes.json"
PROFILES = PACKAGE / "profiles"
NOISE_BAR = PACKAGE / "results/2026-09-19-w29-g3b-shadow-recede/noise-bar.json"

GENERATION = "apple-macos-27.0-"
SHAPE_BANDS = [("3-6", 3.0, 6.0), ("6-12", 6.0, 12.0),
               ("12-24", 12.0, 24.0), ("24-48", 24.0, 48.0)]
SIDES = ["above", "below", "left", "right"]
CLEARANCE = {"above": "clearanceAbove", "below": "clearanceBelow",
             "left": "clearanceLeft", "right": "clearanceRight"}

SAMPLES_PER_GROUP = 600

# The distance histogram's bin, and the quantum the offset is cached at, CSS px.
DISTANCE_BIN_CSS_PX = 0.2
OFFSET_QUANTUM_CSS_PX = 0.05
SPANS = [32, 44, 96, 128, 160]
STANDARD_BEDS = ["1x light", "2x light", "1x dark", "2x dark"]

# The compositing-space exponent the shader converts its occlusion through
# (`outer_shadow`: `1 - pow(1 - occ, 1 / 2.4)`).
ENCODING_EXPONENT = 2.4

# The spread values the conditioning sweep holds σ against, CSS px.
SPREAD_SWEEP = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 3.1, 4.0, 5.0, 6.0]

# vitrea's shipped outset, the value every macOS 27 document carries (the two
# dark documents inherit it from the macOS 26.5 default).
SHIPPED_SPREAD = 3.10
SHIPPED_OFFSET = 7.95


# ---------------------------------------------------------------------------
# The shader's own falloff, and the geometry the axis cuts its bands from
# ---------------------------------------------------------------------------

def falloff(signed_distance: float, sigma: float) -> float:
    """`outer_shadow_falloff` in `wgsl/optics.ts`, term for term.

    `0.5 · (1 + tanh(0.7978845608028654 · (x + 0.044715 x³)))` with
    `x = −signedDistance / σ` — the tanh approximation of the Gaussian CDF the
    shader uses, reproduced rather than replaced by `math.erf`, because the
    quantity being fitted is what the shader draws and the two differ in the
    fourth decimal at the shoulders.
    """
    x = -signed_distance / max(sigma, 1e-4)
    t = 0.7978845608028654 * (x + 0.044715 * x * x * x)
    t = max(-20.0, min(20.0, t))
    return 0.5 * (1.0 + math.tanh(t))


def rounded_rect_distance(x: float, y: float, cx: float, cy: float,
                          hw: float, hh: float, radius: float) -> float:
    """`roundedRectSignedDistance` in `component-region.ts`, term for term."""
    qx = abs(x - cx) - (hw - radius)
    qy = abs(y - cy) - (hh - radius)
    return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - radius


def direction_of(nx: float, ny: float) -> str:
    """`directionOf` in `metrics/shadow.ts`, on already-normalised coordinates."""
    if abs(nx) >= abs(ny):
        return "left" if nx < 0 else "right"
    return "above" if ny < 0 else "below"


class Geometry:
    """One component at one scale: the sample points, grouped by band and sector.

    Built once per `(component, scale)` and shared by every cell that names it,
    which is what makes a per-cell fit affordable in the standard library.
    """

    def __init__(self, spec: dict, canvas: dict, scale: int, admitted: dict[str, list[str]]):
        width_px = round(canvas["width"] * scale)
        height_px = round(canvas["height"] * scale)
        w, h = spec["size"]
        radius = (min(w, h) / 2) if spec["kind"] == "capsule" else spec.get("radius", 0)
        left = round((canvas["width"] - w) / 2)
        top = round((canvas["height"] - h) / 2)
        self.cx = (left + w / 2) * scale
        self.cy = (top + h / 2) * scale
        self.hw = (w / 2) * scale
        self.hh = (h / 2) * scale
        self.radius = radius * scale
        self.scale = scale

        groups: dict[tuple[str, str], list[tuple[float, float, float]]] = {}
        for py in range(height_px):
            fy = py + 0.5
            ny = (fy - self.cy) / self.hh
            for px in range(width_px):
                fx = px + 0.5
                distance = rounded_rect_distance(fx, fy, self.cx, self.cy,
                                                 self.hw, self.hh, self.radius)
                if distance <= 0:
                    continue
                css = distance / scale
                if css >= 48.0:
                    continue
                nx = (fx - self.cx) / self.hw
                direction = direction_of(nx, ny)
                for label, inner, outer in SHAPE_BANDS:
                    if inner <= css < outer and label in admitted[direction]:
                        groups.setdefault((label, direction), []).append((fx, fy, css))
                        break

        # Rank-stratified subsample: sort each group by its own unshifted
        # distance and take every m-th, so the subsample's distance histogram is
        # the group's, not a scanline slice of it.
        self.groups: dict[tuple[str, str], list[tuple[float, float]]] = {}
        self.full: dict[tuple[str, str], list[tuple[float, float]]] = {}
        for key, points in groups.items():
            points.sort(key=lambda p: p[2])
            self.full[key] = [(p[0], p[1]) for p in points]
            step = max(1, len(points) // SAMPLES_PER_GROUP)
            self.groups[key] = [(p[0], p[1]) for p in points[::step]]
        self._histograms: dict[tuple[int, bool], dict[tuple[str, str], list[tuple[float, float]]]] = {}

    def histogram(self, offset: float, full: bool = False):
        """The shifted distances of one group, binned — the whole of the speed.

        `Ψ((d − spread)/σ)` depends on a point only through its SHIFTED distance,
        so a group's mean is a weighted sum over the distinct distances rather
        than over its pixels. The distances are binned at `DISTANCE_BIN_CSS_PX`
        and the offset is quantised at `OFFSET_QUANTUM_CSS_PX`, both far below
        anything the bed can resolve, and the histogram is cached per quantised
        offset: a simplex step that only moves σ or the spread then costs one
        pass over about sixty bins per group instead of one pass over ten
        thousand pixels. The discretisation error is second order in the bin
        width against a function whose scale is σ ≥ 1 CSS px.
        """
        key = (round(offset / OFFSET_QUANTUM_CSS_PX), full)
        got = self._histograms.get(key)
        if got is not None:
            return got
        quantised = key[0] * OFFSET_QUANTUM_CSS_PX
        shift = quantised * self.scale
        source = self.full if full else self.groups
        built: dict[tuple[str, str], list[tuple[float, float]]] = {}
        for group, points in source.items():
            bins: dict[int, int] = {}
            for fx, fy in points:
                distance = rounded_rect_distance(fx, fy - shift, self.cx, self.cy,
                                                 self.hw, self.hh, self.radius)
                index = round((distance / self.scale) / DISTANCE_BIN_CSS_PX)
                bins[index] = bins.get(index, 0) + 1
            total = len(points)
            built[group] = [(index * DISTANCE_BIN_CSS_PX, count / total)
                            for index, count in bins.items()]
        if len(self._histograms) > 400:
            self._histograms.clear()
        self._histograms[key] = built
        return built

    def band_means(self, sigma: float, spread: float, offset: float,
                   full: bool = False) -> dict[tuple[str, str], float]:
        """`Ψ̄` per band and direction at one (σ, spread, offset)."""
        out = {}
        for group, bins in self.histogram(offset, full).items():
            total = 0.0
            for distance, weight in bins:
                total += weight * falloff(distance - spread, sigma)
            out[group] = total
        return out


# ---------------------------------------------------------------------------
# The fit
# ---------------------------------------------------------------------------

def solve_alpha(observations: dict[tuple[str, str], float],
                means: dict[tuple[str, str], float]) -> float:
    """The closed-form amplitude: the model is linear in it."""
    numerator = denominator = 0.0
    for key, observed in observations.items():
        psi = means.get(key)
        if psi is None:
            continue
        numerator += (1.0 - observed) * psi
        denominator += psi * psi
    if denominator <= 0:
        return 0.0
    return max(0.0, min(1.0, numerator / denominator))


def residual_of(observations: dict[tuple[str, str], float],
                means: dict[tuple[str, str], float], alpha: float,
                encoded: bool) -> float:
    total = 0.0
    count = 0
    for key, observed in observations.items():
        psi = means.get(key)
        if psi is None:
            continue
        if encoded:
            model = max(0.0, 1.0 - alpha * psi) ** ENCODING_EXPONENT
        else:
            model = 1.0 - alpha * psi
        total += (observed - model) ** 2
        count += 1
    return math.sqrt(total / count) if count else float("nan")


def objective(geometry: Geometry, observations: dict[tuple[str, str], float],
              encoded: bool):
    cache: dict[tuple[int, int, int], tuple[float, float]] = {}

    def evaluate(point: list[float]) -> float:
        sigma, spread, offset = point
        if not (0.2 <= sigma <= 80 and -8 <= spread <= 30 and -10 <= offset <= 40):
            return 1e6
        key = (round(sigma * 2000), round(spread * 2000), round(offset * 2000))
        hit = cache.get(key)
        if hit is None:
            means = geometry.band_means(sigma, spread, offset)
            if encoded:
                alpha = solve_alpha_encoded(observations, means)
            else:
                alpha = solve_alpha(observations, means)
            hit = (alpha, residual_of(observations, means, alpha, encoded))
            cache[key] = hit
        return hit[1]

    return evaluate, cache


def solve_alpha_encoded(observations: dict[tuple[str, str], float],
                        means: dict[tuple[str, str], float]) -> float:
    """The amplitude of the ENCODED form, by golden section on [0, 1].

    The encoded model is not linear in `A`, so there is no closed form; one
    dimension bisected inside the three-dimensional search is still cheap, and
    the objective is unimodal in `A` because every term is monotone in it.
    """
    low, high = 0.0, 1.0
    phi = (math.sqrt(5.0) - 1.0) / 2.0
    b = high - phi * (high - low)
    c = low + phi * (high - low)
    fb = residual_of(observations, means, b, True)
    fc = residual_of(observations, means, c, True)
    for _ in range(40):
        if fb < fc:
            high, c, fc = c, b, fb
            b = high - phi * (high - low)
            fb = residual_of(observations, means, b, True)
        else:
            low, b, fb = b, c, fc
            c = low + phi * (high - low)
            fc = residual_of(observations, means, c, True)
    return (low + high) / 2.0


def nelder_mead(evaluate, start: list[float], step: list[float],
                iterations: int = 220) -> tuple[list[float], float]:
    """A compact simplex, because the search is three-dimensional and unbounded
    optimisers are not in the standard library."""
    simplex = [list(start)]
    for index in range(len(start)):
        point = list(start)
        point[index] += step[index]
        simplex.append(point)
    scores = [evaluate(p) for p in simplex]
    for _ in range(iterations):
        order = sorted(range(len(simplex)), key=lambda i: scores[i])
        simplex = [simplex[i] for i in order]
        scores = [scores[i] for i in order]
        best, worst = simplex[0], simplex[-1]
        centroid = [sum(p[i] for p in simplex[:-1]) / (len(simplex) - 1)
                    for i in range(len(start))]
        if max(abs(worst[i] - best[i]) for i in range(len(start))) < 1e-4:
            break
        reflected = [centroid[i] + (centroid[i] - worst[i]) for i in range(len(start))]
        score = evaluate(reflected)
        if score < scores[0]:
            expanded = [centroid[i] + 2 * (centroid[i] - worst[i]) for i in range(len(start))]
            expanded_score = evaluate(expanded)
            simplex[-1], scores[-1] = ((expanded, expanded_score)
                                       if expanded_score < score else (reflected, score))
        elif score < scores[-2]:
            simplex[-1], scores[-1] = reflected, score
        else:
            contracted = [centroid[i] + 0.5 * (worst[i] - centroid[i])
                          for i in range(len(start))]
            contracted_score = evaluate(contracted)
            if contracted_score < scores[-1]:
                simplex[-1], scores[-1] = contracted, contracted_score
            else:
                for index in range(1, len(simplex)):
                    simplex[index] = [best[i] + 0.5 * (simplex[index][i] - best[i])
                                      for i in range(len(start))]
                    scores[index] = evaluate(simplex[index])
    order = sorted(range(len(simplex)), key=lambda i: scores[i])
    return simplex[order[0]], scores[order[0]]


def fit(geometry: Geometry, observations: dict[tuple[str, str], float],
        start: list[float], encoded: bool = False) -> dict:
    evaluate, _ = objective(geometry, observations, encoded)
    point, residual = nelder_mead(evaluate, start, [2.0, 1.0, 2.0])
    sigma, spread, offset = point
    means = geometry.band_means(sigma, spread, offset)
    alpha = solve_alpha_encoded(observations, means) if encoded else solve_alpha(observations, means)
    return {"sigma": sigma, "spread": spread, "offset": offset, "alpha": alpha,
            "residual": residual, "n": len(observations)}


def one_sided(geometry: Geometry, observations: dict[tuple[str, str], float],
              two_sided: dict) -> dict | None:
    """One direction's own offset, with σ and the spread HELD at the cell's fit.

    Returns `noShadow` where every observation in the direction is exactly
    1.000000: there the amplitude solves to zero, the objective is flat in every
    parameter, and a printed triple would be the starting point wearing the
    look of a measurement.
    """
    if len(observations) < 2:
        return None
    if all(value == 1.0 for value in observations.values()):
        return {"offset": float("nan"), "alpha": 0.0, "residual": 0.0, "noShadow": True}
    sigma, spread = two_sided["sigma"], two_sided["spread"]
    best = None
    for offset in [x * 0.25 for x in range(-8, 101)]:
        means = geometry.band_means(sigma, spread, offset)
        alpha = solve_alpha(observations, means)
        residual = residual_of(observations, means, alpha, False)
        if best is None or residual < best["residual"]:
            best = {"offset": offset, "alpha": alpha, "residual": residual,
                    "noShadow": False}
    return best


def fit_at_spread(geometry: Geometry, observations: dict[tuple[str, str], float],
                  spread: float, start: list[float], encoded: bool = False) -> dict:
    """The profile likelihood's inner fit: σ and the amplitude, spread HELD."""
    evaluate, _ = objective(geometry, observations, encoded)

    def two(point: list[float]) -> float:
        return evaluate([point[0], spread, point[1]])

    point, residual = nelder_mead(two, [start[0], start[2]], [2.0, 2.0], iterations=140)
    sigma, offset = point
    means = geometry.band_means(sigma, spread, offset)
    alpha = solve_alpha_encoded(observations, means) if encoded else solve_alpha(observations, means)
    return {"sigma": sigma, "spread": spread, "offset": offset, "alpha": alpha,
            "residual": residual}


# ---------------------------------------------------------------------------
# The bed
# ---------------------------------------------------------------------------

def spans_of(components: dict) -> dict[str, int]:
    out = {}
    for name, spec in components.items():
        kind = spec["kind"]
        if kind in ("capsule", "rrect"):
            out[name] = min(spec["size"])
        elif kind == "stack":
            out[name] = min(spec["base"]["size"])
        elif kind == "group":
            out[name] = min(min(item["size"]) for item in spec["items"])
    return out


def law_sigma(leaves: dict, span: int) -> float:
    return leaves["sigmaPx"] + max(
        leaves["sigmaThinOffsetPx"],
        leaves["sigmaSlopePerSpan"] * (span - leaves["sigmaSpanRefPx"]),
    )


def median(values: list[float]) -> float:
    return sorted(values)[len(values) // 2]


def main() -> int:
    scenes = json.loads(SCENES.read_text())
    canvas = scenes["canvas"]
    span_of = spans_of(scenes["components"])
    documents = {
        scheme: json.loads(
            (PROFILES / f"apple-macos-27.0-1x-{scheme}-standard-glass0.5.json").read_text()
        )["patch"]["outerShadow"]
        for scheme in ("light", "dark")
    }
    bar_document = json.loads(NOISE_BAR.read_text())
    bars = {(c["profileKey"], c["sceneId"]):
            c["pairwise"].get("shadowAffineSlopeDeltaMax", {}).get("max")
            for c in bar_document["cells"]}
    bar_floor = bar_document["bedMinimumNonZeroBar"]["shadowAffineSlopeDeltaMax"]
    bar_max = 0.002044  # the MAX over 432 cells, the charter's named thin-regime bar

    print("W32 G0 — the renderer's own falloff model, fitted to both sides")
    print("=" * 160)
    print()
    print(f"Matrix:    {MATRIX}")
    print(f"Model:     a(p) = 1 - alpha * Psi((d(p_x, p_y - offset) - spread) / sigma), linear light")
    print(f"Encoded:   a(p) = (1 - A * Psi(...)) ** {ENCODING_EXPONENT}, the shader's own composite")
    print(f"Samples:   <= {SAMPLES_PER_GROUP} rank-stratified points per band per direction")
    print("Nothing is fitted into a document and nothing is captured.")
    print()

    # ------------------------------------------------------------------
    rows = []
    for cell in json.loads(MATRIX.read_text())["cells"]:
        key = cell["key"]
        profile = key["profileKey"]
        if not profile.startswith(GENERATION):
            continue
        if cell["tier"] != "texture" or cell.get("fixtureSet") == "holdout":
            continue
        if cell.get("state") == "inactive":
            continue
        shadow = cell.get("shadow")
        if shadow is None:
            continue
        scene = key["sceneId"]
        component = scene.split("__")[1]
        span = span_of.get(component)
        if span not in SPANS:
            continue
        # The model's geometry is ONE rounded rect. `toolbar-group` at span 44 is
        # three of them in a row and `glass-over-glass` is a stack, so the
        # sectors `directionOf` cuts are not the sectors of a single silhouette
        # there; those components are counted and not fitted.
        if scenes["components"][component]["kind"] not in ("rrect", "capsule"):
            continue
        rest = profile.removeprefix(GENERATION).removesuffix("-glass0.5")
        scale_token, _, tail = rest.partition("-")
        bed = f"{scale_token} {tail.replace('-standard', '')}"
        if bed not in STANDARD_BEDS:
            continue
        scale = int(scale_token.removesuffix("x"))
        admitted = {}
        for direction in SIDES:
            limit = shadow[CLEARANCE[direction]]["value"] / scale
            admitted[direction] = [label for label, _, outer in SHAPE_BANDS if outer <= limit]
        observed = {}
        for side in ("Native", "Web"):
            got = {}
            for entry in shadow.get(f"affine{side}", []):
                direction = entry["direction"]
                if direction == "all" or entry["ringLabel"] not in dict(
                        (b, None) for b, _, _ in SHAPE_BANDS):
                    continue
                if entry["ringLabel"] not in admitted[direction]:
                    continue
                if entry.get("slopeALinear") is None:
                    continue
                got[(entry["ringLabel"], direction)] = entry["slopeALinear"]
            observed[side] = got
        expected = sum(len(admitted[d]) for d in SIDES)
        if len(observed["Native"]) != expected or len(observed["Web"]) != expected:
            continue
        rows.append({
            "profile": profile, "scene": scene, "component": component, "span": span,
            "scale": scale, "bed": bed,
            "scheme": "dark" if "-dark-" in profile else "light",
            "set": cell.get("fixtureSet"),
            "admitted": admitted, "observed": observed,
            "bar": bars.get((profile, scene)) or bar_floor,
        })

    print(f"§0. The bed: {len(rows)} active, non-holdout, WebGPU cells on the four standard beds")
    print("-" * 160)
    print("  A cell is fitted only where BOTH sides identify every band the cell's own clearance")
    print("  admits, in all four directions — the admitted-band rule applied to the fit's own")
    print("  design matrix, so every cell at a span is fitted on the same observations.")
    print(f"  {'bed':<38}" + "".join(f"{('span ' + str(s)):>10}" for s in SPANS))
    for bed in STANDARD_BEDS:
        line = f"  {bed:<38}"
        for span in SPANS:
            line += f"{sum(1 for r in rows if r['bed'] == bed and r['span'] == span):>10}"
        print(line)
    print()

    geometries: dict[tuple[str, int, str], Geometry] = {}

    def geometry_for(row: dict) -> Geometry:
        key = (row["component"], row["scale"],
               "|".join(f"{d}:{','.join(row['admitted'][d])}" for d in SIDES))
        got = geometries.get(key)
        if got is None:
            got = Geometry(scenes["components"][row["component"]], canvas,
                           row["scale"], row["admitted"])
            geometries[key] = got
        return got

    # ------------------------------------------------------------------
    print("§1. The subsample, checked against every pixel")
    print("-" * 160)
    print("  One cell per span, fitted twice: once on the rank-stratified subsample the rest of")
    print("  this file uses and once on EVERY exterior pixel of the band. A difference in the")
    print("  fitted triple larger than the fit's own residual would make the subsample the")
    print("  finding rather than the material.")
    print()
    print(f"  {'span':>5}{'scene':<34}{'σ sub':>9}{'σ full':>9}{'spread sub':>12}"
          f"{'spread full':>13}{'offset sub':>12}{'offset full':>13}{'resid sub':>11}")
    for span in SPANS:
        picked = [r for r in rows if r["span"] == span and r["bed"] == "1x light"]
        if not picked:
            continue
        row = picked[0]
        geometry = geometry_for(row)
        observations = row["observed"]["Native"]
        sub = fit(geometry, observations, [max(2.0, span * 0.12), 3.0, 8.0])

        class FullGeometry:
            def __init__(self, inner: Geometry):
                self.inner = inner

            def band_means(self, sigma, spread, offset, full=False):
                return self.inner.band_means(sigma, spread, offset, full=True)

        whole = fit(FullGeometry(geometry), observations, [max(2.0, span * 0.12), 3.0, 8.0])
        print(f"  {span:>5}{row['scene']:<34}{sub['sigma']:>9.3f}{whole['sigma']:>9.3f}"
              f"{sub['spread']:>12.3f}{whole['spread']:>13.3f}"
              f"{sub['offset']:>12.3f}{whole['offset']:>13.3f}{sub['residual']:>11.6f}")
    print()

    # ------------------------------------------------------------------
    print("§2. The per-cell fits, both sides")
    print("-" * 160)
    print("  `native` is Apple's render and its `spread` is **Apple's own outset** — §5.162 §9's")
    print("  finding N-10, which no wave had measured. `web` is vitrea's own render through the")
    print("  same instrument and the same model: it SHOULD return the shipped σ(span), spread 3.10")
    print("  and offset 7.95, and the size of its miss is the model's own error.")
    print()
    for row in rows:
        geometry = geometry_for(row)
        start = [max(2.0, row["span"] * 0.12), 3.0, 8.0]
        row["fitNative"] = fit(geometry, row["observed"]["Native"], start)
        row["fitWeb"] = fit(geometry, row["observed"]["Web"], start)
        row["fitWebEncoded"] = fit(geometry, row["observed"]["Web"], start, encoded=True)
        for direction in ("below", "above"):
            for side in ("Native", "Web"):
                one = {k: v for k, v in row["observed"][side].items() if k[1] == direction}
                row[f"fit{side}{direction.capitalize()}"] = one_sided(
                    geometry, one, row[f"fit{side}"])

    print(f"  {'bed':<12}{'span':>5}{'n':>4}{'law σ':>9}"
          f"{'σ nat':>9}{'spread nat':>12}{'offset nat':>12}{'α nat':>8}{'resid':>10}"
          f"{'σ web':>9}{'spread web':>12}{'offset web':>12}{'α web':>8}{'resid':>10}"
          f"{'bar':>10}")
    summary = {}
    for bed in STANDARD_BEDS:
        for span in SPANS:
            here = [r for r in rows if r["bed"] == bed and r["span"] == span]
            if not here:
                continue
            scheme = here[0]["scheme"]
            law = law_sigma(documents[scheme], span)
            entry = {
                "n": len(here),
                "lawSigma": law,
                "native": {k: median([r["fitNative"][k] for r in here])
                           for k in ("sigma", "spread", "offset", "alpha", "residual")},
                "web": {k: median([r["fitWeb"][k] for r in here])
                        for k in ("sigma", "spread", "offset", "alpha", "residual")},
                "webEncoded": {k: median([r["fitWebEncoded"][k] for r in here])
                               for k in ("sigma", "spread", "offset", "alpha", "residual")},
                "bar": median([r["bar"] for r in here]),
            }
            summary[f"{bed} span {span}"] = entry
            print(f"  {bed:<12}{span:>5}{len(here):>4}{law:>9.3f}"
                  f"{entry['native']['sigma']:>9.3f}{entry['native']['spread']:>12.3f}"
                  f"{entry['native']['offset']:>12.3f}{entry['native']['alpha']:>8.4f}"
                  f"{entry['native']['residual']:>10.6f}"
                  f"{entry['web']['sigma']:>9.3f}{entry['web']['spread']:>12.3f}"
                  f"{entry['web']['offset']:>12.3f}{entry['web']['alpha']:>8.4f}"
                  f"{entry['web']['residual']:>10.6f}"
                  f"{entry['bar']:>10.6f}")
    print()
    print("  The same web-side cells under the ENCODED model, which is the shape the shader")
    print("  actually composites. The shipped triple is σ(span) from the law, spread 3.100 and")
    print("  offset 7.950 on every macOS 27 bed (both dark documents inherit the two lengths).")
    print()
    print(f"  {'bed':<12}{'span':>5}{'shipped σ':>11}{'σ web enc':>11}{'Δσ':>9}"
          f"{'spread enc':>12}{'Δspread':>10}{'offset enc':>12}{'Δoffset':>10}{'resid':>10}"
          f"{'resid linear':>14}")
    for bed in STANDARD_BEDS:
        for span in SPANS:
            entry = summary.get(f"{bed} span {span}")
            if entry is None:
                continue
            encoded = entry["webEncoded"]
            print(f"  {bed:<12}{span:>5}{entry['lawSigma']:>11.3f}{encoded['sigma']:>11.3f}"
                  f"{encoded['sigma'] - entry['lawSigma']:>9.3f}"
                  f"{encoded['spread']:>12.3f}{encoded['spread'] - 3.10:>10.3f}"
                  f"{encoded['offset']:>12.3f}{encoded['offset'] - 7.95:>10.3f}"
                  f"{encoded['residual']:>10.6f}{entry['web']['residual']:>14.6f}")
    print()

    # ------------------------------------------------------------------
    print("§3. One sided: which direction carries the offset, with σ and the spread held")
    print("-" * 160)
    print("  A three-observation fit of four free parameters is exactly determined and says")
    print("  nothing, so the one-sided read holds σ and the spread at the cell's own two-sided")
    print("  values and re-fits the OFFSET and the amplitude on one direction at a time. That is")
    print("  two free parameters against three observations and it answers the question the")
    print("  direction resolution exists for: a shift moves `below` outward and `above` inward,")
    print("  so the two offsets disagreeing is the displacement and the two agreeing is a width.")
    print()
    print("  `no shadow` means every observation in that direction is exactly 1.000000 — the band")
    print("  removed no light, on that side, at every distance. Where it appears the offset is")
    print("  identified ONE-SIDEDLY, which is clause 1's condition: the fit still separates a")
    print("  shift from a widening on `below`'s own three bands, but the CHECK on that separation")
    print("  — the opposite side moving the other way — is unavailable.")
    print()
    print(f"  {'bed':<12}{'span':>5}{'side':<8}{'offset below':>14}{'offset above':>14}"
          f"{'below − above':>15}{'α below':>10}{'α above':>10}")
    one_sided_summary = {}
    for bed in STANDARD_BEDS:
        for span in SPANS:
            here = [r for r in rows if r["bed"] == bed and r["span"] == span]
            if not here:
                continue
            for side in ("Native", "Web"):
                below = [r[f"fit{side}Below"] for r in here if r[f"fit{side}Below"]]
                above = [r[f"fit{side}Above"] for r in here if r[f"fit{side}Above"]]
                line = f"  {bed:<12}{span:>5}{side.lower():<8}"
                entry = {}
                for label, got in (("below", below), ("above", above)):
                    if not got:
                        entry[label] = None
                    else:
                        entry[label] = {
                            "offset": median([g["offset"] for g in got]),
                            "alpha": median([g["alpha"] for g in got]),
                            "noShadow": all(g["noShadow"] for g in got),
                        }
                for label in ("below", "above"):
                    got = entry[label]
                    line += (f"{'no shadow':>14}" if got is None or got["noShadow"]
                             else f"{got[chr(111)+chr(102)+chr(102)+chr(115)+chr(101)+chr(116)]:>14.3f}")
                if (entry["below"] and entry["above"]
                        and not entry["below"]["noShadow"] and not entry["above"]["noShadow"]):
                    line += f"{entry['below']['offset'] - entry['above']['offset']:>15.3f}"
                else:
                    line += f"{'—':>15}"
                for label in ("below", "above"):
                    got = entry[label]
                    line += (f"{'—':>10}" if got is None or got["noShadow"]
                             else f"{got['alpha']:>10.4f}")
                one_sided_summary[f"{bed} span {span} {side.lower()}"] = entry
                print(line)
        print()
    print()

    print("§4. The conditioning: the profile likelihood of σ against the spread")
    print("-" * 160)
    print("  Per bed and per span, on the MEDIAN observation vector of that bed and span. The")
    print("  spread is HELD at each value of the sweep and σ, the offset and the amplitude are")
    print("  re-fitted; the residual is the profile.")
    print()
    print("  **What counts as separation.** Not the native-pair bar: the bar is the noise on ONE")
    print("  band's `a` (6e-6 to 1.3e-4 on these cells) and the residual is an RMS over eight to")
    print("  sixteen bands at 5e-4 to 2e-3 — a hundred times the bar — so the model's own misfit")
    print("  dominates the capture's noise and a residual difference above the bar says nothing")
    print("  about identifiability. The interval reported is the ordinary one-sigma contour of a")
    print("  least-squares fit: the spreads whose profile residual is within")
    print("  `sqrt(1 + 1/(n − p)) − 1` of the minimum, with `n` the observations and `p` the four")
    print("  free parameters. The bar is printed beside it and is not the criterion.")
    print()
    print(f"  {'bed':<12}{'span':>5}{'side':<8}{'n':>4}{'best spread':>13}{'1σ interval':>20}"
          f"{'σ at best':>11}{'offset':>9}{'resid':>10}{'3.10 inside?':>14}{'bar':>11}")
    conditioning = {}
    profiles = {}
    for bed in STANDARD_BEDS:
        for span in SPANS:
            here = [r for r in rows if r["bed"] == bed and r["span"] == span]
            if not here:
                continue
            geometry = geometry_for(here[0])
            bar = median([r["bar"] for r in here])
            for side in ("Native", "Web"):
                keys = set(here[0]["observed"][side])
                pooled = {k: median([r["observed"][side][k] for r in here]) for k in keys}
                profile = [fit_at_spread(geometry, pooled, spread,
                                         [max(2.0, span * 0.12), 3.0, 8.0])
                           for spread in SPREAD_SWEEP]
                best = min(profile, key=lambda g: g["residual"])
                n, p_free = len(pooled), 4
                threshold = best["residual"] * (math.sqrt(1.0 + 1.0 / max(n - p_free, 1)) - 1.0)
                inside = [g["spread"] for g in profile
                          if g["residual"] - best["residual"] <= threshold]
                low, high = (min(inside), max(inside)) if inside else (
                    best["spread"], best["spread"])
                shipped_inside = low <= SHIPPED_SPREAD <= high
                conditioning[f"{bed} span {span} {side.lower()}"] = {
                    "bar": bar, "n": n, "threshold": threshold,
                    "bestSpread": best["spread"], "interval": [low, high],
                    "sigmaAtBest": best["sigma"], "offsetAtBest": best["offset"],
                    "residual": best["residual"],
                    "shippedSpreadInside": shipped_inside,
                    "flatWithinBar": all(g["residual"] - best["residual"] < bar
                                         for g in profile),
                }
                profiles[f"{bed} span {span} {side.lower()}"] = profile
                print(f"  {bed:<12}{span:>5}{side.lower():<8}{n:>4}{best['spread']:>13.2f}"
                      f"{f'[{low:.2f}, {high:.2f}]':>20}{best['sigma']:>11.3f}"
                      f"{best['offset']:>9.3f}{best['residual']:>10.6f}"
                      f"{('INSIDE' if shipped_inside else 'excluded'):>14}{bar:>11.6f}")
        print()
    print()
    print("  The profiles themselves, residual against held spread:")
    print()
    for label, profile in profiles.items():
        print(f"  {label}")
        print(f"    {'spread':>8}" + "".join(f"{g['spread']:>9.2f}" for g in profile))
        print(f"    {'σ':>8}" + "".join(f"{g['sigma']:>9.3f}" for g in profile))
        print(f"    {'offset':>8}" + "".join(f"{g['offset']:>9.3f}" for g in profile))
        print(f"    {'resid':>8}" + "".join(f"{g['residual']:>9.6f}" for g in profile))
        print()
    print()

    print("§5. Apple's own outset, which is §5.162 §9's finding N-10 answered")
    print("-" * 160)
    print("  The native side's fitted spread per bed and span, with the one-sigma interval from")
    print("  §4 and the model's own error from the web side beside it: the web fit of vitrea's")
    print("  own render SHOULD return 3.100, and what it returns instead is the bias this")
    print("  instrument's model carries at that span.")
    print()
    print(f"  {'bed':<12}{'span':>5}{'Apple spread':>14}{'1σ interval':>20}"
          f"{'web spread':>12}{'model error':>13}{'Apple offset':>14}{'web offset':>12}"
          f"{'model error':>13}")
    outset = {}
    for bed in STANDARD_BEDS:
        for span in SPANS:
            entry = summary.get(f"{bed} span {span}")
            if entry is None:
                continue
            cond = conditioning.get(f"{bed} span {span} native", {})
            low, high = cond.get("interval", [float("nan")] * 2)
            record = {
                "appleSpread": entry["native"]["spread"],
                "interval": [low, high],
                "webSpread": entry["web"]["spread"],
                "spreadModelError": entry["web"]["spread"] - SHIPPED_SPREAD,
                "appleOffset": entry["native"]["offset"],
                "webOffset": entry["web"]["offset"],
                "offsetModelError": entry["web"]["offset"] - SHIPPED_OFFSET,
            }
            outset[f"{bed} span {span}"] = record
            print(f"  {bed:<12}{span:>5}{record['appleSpread']:>14.3f}"
                  f"{f'[{low:.2f}, {high:.2f}]':>20}"
                  f"{record['webSpread']:>12.3f}{record['spreadModelError']:>13.3f}"
                  f"{record['appleOffset']:>14.3f}{record['webOffset']:>12.3f}"
                  f"{record['offsetModelError']:>13.3f}")
    print()

    (HERE / "model-fit.json").write_text(json.dumps({
        "model": "a = 1 - alpha * Psi((d(x, y - offset) - spread) / sigma), linear light",
        "encoded": f"a = (1 - A * Psi(...)) ** {ENCODING_EXPONENT}",
        "samplesPerGroup": SAMPLES_PER_GROUP,
        "spreadSweep": SPREAD_SWEEP,
        "thinRegimeBarMax": bar_max,
        "summary": summary,
        "conditioning": conditioning,
        "oneSided": one_sided_summary,
        "appleOutset": outset,
        "cells": [{k: v for k, v in row.items() if k not in ("observed",)} | {
            "observed": {side: {f"{b}|{d}": v for (b, d), v in row["observed"][side].items()}
                         for side in ("Native", "Web")},
        } for row in rows],
    }, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
