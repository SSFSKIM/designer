"""W27f G2: the CSS tier's coherence on DOM-sourced groups — a record, never a target.

Contract X1 binds this gate: every measured claim is on the WebGPU tier, and the
CSS tier's residual is written down. W27f's charter asks for that residual on
the groups this wave is about — the ones whose backdrop is ordinary page content
rather than a registered texture — because until W27f the two tiers drew
demonstrably different materials there and nothing measured the gap.

`packages/calibration/test/tier-coherence.test.ts` cannot supply this. It reads
no files: it is a code-against-code mirror of the renderer's optics and the CSS
tier's derivation, pinned in both directions, and it has no notion of a sampling
backend at all. The matrix's coherence axis cannot supply it either — its "dom"
tier means the CSS *renderer*, not a DOM-sourced backdrop, so a WebGPU group
over page content has no cell in that schema. This file therefore computes the
same two statistics the adopted coherence rows use, over the page-sourced arms,
and writes them as evidence.

The two statistics, and exactly how far each one matches `cli/measure.ts`:

* `crossTierOklabDeltaEMeanWholeCanvas` — mean OKLab distance over the **whole
  canvas** between the two tiers' captures of the same scene and arm. This is
  `measure.ts:591`'s definition exactly: `oklabDeltaE(twin, web).mean`, which
  aggregates over every pixel with no mask. It is a property of the *pair*, not
  of a region, and it is written at the pair level for that reason: an earlier
  form of this file repeated the identical whole-canvas value inside both the
  `declaredFootprint` and the `stackOverlay` block, where a reader had every
  reason to take the second one for an overlay-local distance.
* `interiorLevelRatioGpuOverCss` — the GPU tier's mean interior linear luminance
  over the CSS tier's. **The mask is not the same one `measure.ts` uses.** It
  computes the ratio over `nativeSil` (`measure.ts:465`, `:598`), the silhouette
  *extracted from the native fixture*; this file uses the **declared** eroded
  interior (6 CSS px, visible union), which is the region every other reading in
  this gate is stated over. The reason is not preference: a native silhouette
  exists only where a fixture does, and 11 of the 20 ordinary dark cells have no
  dark fixture, so the adopted row's mask cannot be formed on the majority of
  the bed this gate measures. A declared region exists on every cell.

So the ratio here is a **different statistic from the adopted row's**, not a
comparable one, and the two must not be read against each other. What it does
support is comparison *within itself* — hinted against unhinted, dark against
light, stack against ordinary — because the same mask is used throughout.

The adopted thresholds (≤ 0.05 and 0.8–1.25) are printed beside each reading
**for shape only**. They are not applied, for two independent reasons: they were
adopted over texture-sourced cells of the frozen bed, and applying them here
would make the CSS tier a target on a path where X1 says it is a record; and for
the ratio they are not even stated over the same mask. Nothing in this file
fails, gates, or floors.

    python coherence.py --scratch /tmp/w27f-g2 --out coherence.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent

_spec = importlib.util.spec_from_file_location("w27f_g0", RESULTS / "2026-09-10-w27f-g0-read.py")
g0 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g0)

# The pairs: a WebGPU page arm and the CSS page arm drawn from the same request.
# `css-today` is deliberately absent — it is texture-sourced, and pairing it with
# a page arm would compare two different backdrops and call the difference a
# tier gap.
PAIRS = [("unsampled-hint", "css-hint", "the page at its measured backdrop level"),
         ("unsampled-nohint", "css-nohint", "the page with no hint — unknown tone on both tiers")]

# The shape of the adopted coherence rows, for reference only (X1).
ADOPTED_SHAPE = {"crossTierOklabDeltaEMeanWholeCanvas": "<= 0.05",
                 "interiorLevelRatioGpuOverCss": "0.8 .. 1.25"}

PHASES = {"candidate": "the 20 ordinary page cells", "holdout": "the two stack cells"}


def capture_path(scratch, phase, scheme, arm, scene, tier):
    profile = f"apple-macos-26.5-1x-{scheme}-standard"
    return scratch / phase / scheme / arm / profile / scene / f"{scene}__{tier}.png"


def interior_mask(surfaces, shape, selected):
    """The declared eroded interior, visible union — the G0 reader's own rule."""
    distances = [g0.distance(s, shape) for s in surfaces]
    interior = np.zeros(shape, bool)
    for i in selected:
        visible = np.ones(shape, bool)
        for j in range(i + 1, len(surfaces)):
            if surfaces[j]["plane"] != surfaces[i]["plane"]:
                visible &= distances[j] > 0
        interior |= (distances[i] <= -6) & visible
    return interior


def whole_canvas_delta_e(gpu_lab, css_lab):
    """The adopted row's statistic: mean OKLab distance over every pixel, no mask."""
    return float(np.sqrt(((gpu_lab - css_lab) ** 2).sum(axis=2)).mean())


def region_reading(gpu_lum, css_lum, surfaces, selected):
    """The two tiers' mean interior level over one declared region, and their ratio."""
    mask = interior_mask(surfaces, gpu_lum.shape, selected)
    gpu_level = float(gpu_lum[mask].mean()) if mask.any() else None
    css_level = float(css_lum[mask].mean()) if mask.any() else None
    ratio = None
    if gpu_level is not None and css_level not in (None, 0.0):
        ratio = gpu_level / css_level
    return {
        "gpuInteriorLinearLuminanceMean": None if gpu_level is None else round(gpu_level, 6),
        "cssInteriorLinearLuminanceMean": None if css_level is None else round(css_level, 6),
        "interiorLevelRatioGpuOverCss": None if ratio is None else round(ratio, 6),
        "interiorPixels": int(mask.sum()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scratch", type=Path, default=Path("/tmp/w27f-g2"))
    parser.add_argument("--out", type=Path, default=HERE / "coherence.json")
    args = parser.parse_args()

    geometry = g0.declared_geometry()
    record = {
        "gate": "W27f G2",
        "what": "the CSS tier's coherence on DOM-sourced groups, recorded under contract X1",
        "neverATarget": "These are readings, not bounds. No CSS floor is adopted and no CSS "
                        "target is set; the WebGPU tier is the fidelity target (wave Decision "
                        "Log 2, X1).",
        "adoptedRowShapeForReference": ADOPTED_SHAPE,
        "definitions": {
            "crossTierOklabDeltaEMeanWholeCanvas": "mean OKLab distance over the whole canvas — "
                                                   "exactly cli/measure.ts:591's definition for "
                                                   "the adopted row. Written once per arm pair "
                                                   "because it has no mask: it is not a reading "
                                                   "of the declared footprint or of the overlay.",
            "interiorLevelRatioGpuOverCss": "GPU over CSS mean linear luminance on the DECLARED "
                                            "interior, eroded 6 CSS px, visible union. NOT the "
                                            "adopted row's mask, which is the silhouette "
                                            "extracted from the native fixture "
                                            "(cli/measure.ts:465,598) and cannot be formed on the "
                                            "11 dark ordinary cells with no dark fixture. A "
                                            "different statistic, comparable within itself only.",
        },
        "phases": {},
    }

    for phase, description in PHASES.items():
        reading = json.loads((args.scratch / phase / "reading.json").read_text())
        schemes = {}
        for scheme, scheme_record in reading.get("schemes", {}).items():
            cells = []
            for row in scheme_record.get("rows", []):
                scene = row["scene"]
                surfaces = geometry["scenes"][scene]["surfaces"]
                whole = list(range(len(surfaces)))
                overlay = [i for i, s in enumerate(surfaces) if s["plane"] != "base"]
                entry = {"scene": scene, "pairs": {}}
                for gpu_arm, css_arm, why in PAIRS:
                    gpu_path = capture_path(args.scratch, phase, scheme, gpu_arm, scene, "webgpu")
                    css_path = capture_path(args.scratch, phase, scheme, css_arm, scene, "css")
                    if not (gpu_path.exists() and css_path.exists()):
                        entry["pairs"][f"{gpu_arm} / {css_arm}"] = {
                            "note": "one of the two arms was not captured"}
                        continue
                    gpu_lum, gpu_lab = g0.image(gpu_path)[1:]
                    css_lum, css_lab = g0.image(css_path)[1:]
                    if gpu_lum.shape != css_lum.shape:
                        entry["pairs"][f"{gpu_arm} / {css_arm}"] = {
                            "error": f"different sizes: {gpu_lum.shape} against {css_lum.shape}"}
                        continue
                    pair = {
                        "why": why,
                        "crossTierOklabDeltaEMeanWholeCanvas":
                            round(whole_canvas_delta_e(gpu_lab, css_lab), 6),
                        "declaredFootprint": region_reading(gpu_lum, css_lum, surfaces, whole),
                    }
                    if overlay:
                        pair["stackOverlay"] = region_reading(gpu_lum, css_lum, surfaces, overlay)
                    entry["pairs"][f"{gpu_arm} / {css_arm}"] = pair
                cells.append(entry)
            schemes[scheme] = cells
        record["phases"][phase] = {"what": description, "schemes": schemes}

    args.out.write_text(f"{json.dumps(record, indent=1)}\n")

    for phase, block in record["phases"].items():
        for scheme, cells in block["schemes"].items():
            for gpu_arm, css_arm, _ in PAIRS:
                deltas, ratios = [], []
                for cell in cells:
                    pair = cell["pairs"].get(f"{gpu_arm} / {css_arm}", {})
                    footprint = pair.get("declaredFootprint")
                    if not footprint:
                        continue
                    deltas.append(pair["crossTierOklabDeltaEMeanWholeCanvas"])
                    if footprint["interiorLevelRatioGpuOverCss"] is not None:
                        ratios.append(footprint["interiorLevelRatioGpuOverCss"])
                if not deltas or not ratios:
                    continue
                print(f"{phase:9s} {scheme:5s} {gpu_arm:17s} {len(deltas):2d} cells: "
                      f"cross-tier ΔE {min(deltas):.4f}–{max(deltas):.4f}, "
                      f"GPU/CSS interior ratio {min(ratios):.4f}–{max(ratios):.4f}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
