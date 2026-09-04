#!/usr/bin/env python3
"""W17 G1 — the probe pre-check's table.

Reads a scratch matrix written by `run-probe.sh` and prints the six readings the charter's G1
procedure asks for, per configuration: the CSS tier's interior mean against the GPU tier's
rendered interior on the same run, the interior spread against native, `ssimMean` and `ssimBand`
against the W16 canonical bed, and the cross-tier level ratio.

    python3 tab-probe.py <matrix.json> [<matrix.json> ...]

The canonical bed is read from the main checkout, never written. Where a matrix carries more than
one row for a cell — the CLI appends beside old rows rather than replacing them — the LAST row
wins, which is the run that finished most recently.
"""

import json
import sys

BED = "/Users/new/Developer/GitHub/designer/packages/calibration/results/matrix.json"
PROFILES = ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard"]
SCENES = [
    "checkerboard__rrect-md__rest",
    "checkerboard__capsule-button__rest",
    "checkerboard__rrect-ml__rest",
]


def index(path):
    """`(tier, profile, scene) -> cell`, last row wins."""
    out = {}
    for cell in json.load(open(path))["cells"]:
        out[(cell["tier"], cell["key"]["profileKey"], cell["key"]["sceneId"])] = cell
    return out


def value(cell, axis, field):
    if cell is None:
        return None
    node = (cell.get(axis) or {}).get(field)
    return None if node is None else node["value"]


def fmt(x, digits=4):
    return "  —    " if x is None else f"{x:+.{digits}f}" if digits == 4 else f"{x:.{digits}f}"


def main():
    bed = index(BED)
    for path in sys.argv[1:]:
        run = index(path)
        print(f"\n### {path}\n")
        print(
            "| dpr | cell | native | GPU | CSS | CSS−GPU | spread nat | spread CSS | "
            "ssimMean run/bed | ssimBand run/bed | level ratio GPU/CSS |"
        )
        print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for profile in PROFILES:
            dpr = "2x" if "-2x-" in profile else "1x"
            for scene in SCENES:
                css = run.get(("dom", profile, scene))
                gpu = run.get(("texture", profile, scene))
                bedcss = bed.get(("dom", profile, scene))
                native = value(css, "material", "interiorMeanNative")
                cssmean = value(css, "material", "interiorMeanWeb")
                gpumean = value(gpu, "material", "interiorMeanWeb")
                delta = None if (cssmean is None or gpumean is None) else cssmean - gpumean
                print(
                    f"| {dpr} | `{scene.replace('checkerboard__', '').replace('__rest', '')}` "
                    f"| {fmt(native, 4)[1:]} | {fmt(gpumean, 4)[1:]} | {fmt(cssmean, 4)[1:]} "
                    f"| {fmt(delta)} "
                    f"| {fmt(value(css, 'material', 'interiorStdDevNative'), 4)[1:]} "
                    f"| {fmt(value(css, 'material', 'interiorStdDevWeb'), 4)[1:]} "
                    f"| {fmt(value(css, 'perceptual', 'ssimMean'), 4)[1:]} / "
                    f"{fmt(value(bedcss, 'perceptual', 'ssimMean'), 4)[1:]} "
                    f"| {fmt(value(css, 'perceptual', 'ssimBand'), 4)[1:]} / "
                    f"{fmt(value(bedcss, 'perceptual', 'ssimBand'), 4)[1:]} "
                    f"| {fmt(value(css, 'coherence', 'interiorLevelRatioGpuOverCss'), 4)[1:]} |"
                )
        # The GPU tier is bound unchanged, so its own rows are reported as a difference against
        # the bed rather than as numbers: a non-zero entry here is S1 firing.
        worst = 0.0
        for profile in PROFILES:
            for scene in SCENES:
                a = value(run.get(("texture", profile, scene)), "material", "interiorMeanWeb")
                b = value(bed.get(("texture", profile, scene)), "material", "interiorMeanWeb")
                if a is not None and b is not None:
                    worst = max(worst, abs(a - b))
        print(f"\nGPU tier interior mean, worst |run − bed| over the six cells: {worst:.6f}")
        for profile in PROFILES:
            for scene in SCENES:
                css = run.get(("dom", profile, scene))
                bedcss = bed.get(("dom", profile, scene))
                a = value(css, "coherence", "crossTierOklabDeltaEMean")
                b = value(bedcss, "coherence", "crossTierOklabDeltaEMean")
                if a is None:
                    continue
                print(
                    f"  cross-tier ΔE {profile[-19:]:20s} {scene:36s} "
                    f"run {a:.5f}  bed {'—' if b is None else f'{b:.5f}'}"
                )


if __name__ == "__main__":
    main()
