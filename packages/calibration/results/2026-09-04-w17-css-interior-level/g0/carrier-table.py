#!/usr/bin/env python3
"""W17 G0 (d) — the carrier's six probe readings, beside the landed bed and this run's own GPU tier.

The question the table answers is the charter's: does an `feComponentTransfer` stage inside the
tier's existing linear-light reference filter, with an intercept and a slope solved from the two
equations plus the derived excess, land the CSS tier's interior mean within 0.01 of the GPU tier's
RENDERED interior — and what does the interior spread and `ssimMean` do while it does.

The GPU column is read from the carrier run's own matrix rather than from the committed one, so a
drift in the adapter or the browser between the two runs cannot be mistaken for the carrier's work;
the GPU tier is untouched by the patch and its captures are checked byte-identical to the canonical
bed separately.

Usage: `python3 carrier-table.py <carrierMatrix> <canonicalMatrix> [outJson]`.
"""

import json
import sys
from pathlib import Path

PROBES = [
    "checkerboard__rrect-md__rest",
    "checkerboard__capsule-button__rest",
    "checkerboard__rrect-ml__rest",
]
PROFILES = ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard"]


def index(path):
    out = {}
    for cell in json.loads(Path(path).read_text())["cells"]:
        out[(cell["key"]["profileKey"], cell["key"]["sceneId"], cell["tier"])] = cell
    return out


def metric(cell, axis, field):
    if cell is None:
        return None
    report = cell.get(axis)
    if report is None:
        return None
    entry = report.get(field)
    return None if entry is None else entry["value"]


def main():
    carrier = index(sys.argv[1])
    canonical = index(sys.argv[2])

    rows = []
    for profile in PROFILES:
        for scene in PROBES:
            css = carrier.get((profile, scene, "dom"))
            gpu = carrier.get((profile, scene, "texture"))
            bed = canonical.get((profile, scene, "dom"))
            if css is None or gpu is None:
                continue
            rows.append(
                {
                    "profileKey": profile,
                    "sceneId": scene,
                    "native": metric(css, "material", "interiorMeanNative"),
                    "gpuRendered": metric(gpu, "material", "interiorMeanWeb"),
                    "cssCarrier": metric(css, "material", "interiorMeanWeb"),
                    "cssBed": metric(bed, "material", "interiorMeanWeb"),
                    "carrierMinusGpu": metric(css, "material", "interiorMeanWeb")
                    - metric(gpu, "material", "interiorMeanWeb"),
                    "bedMinusGpu": None
                    if bed is None
                    else metric(bed, "material", "interiorMeanWeb") - metric(gpu, "material", "interiorMeanWeb"),
                    "spreadNative": metric(css, "material", "interiorStdDevNative"),
                    "spreadCarrier": metric(css, "material", "interiorStdDevWeb"),
                    "spreadBed": metric(bed, "material", "interiorStdDevWeb"),
                    "ssimMeanCarrier": metric(css, "perceptual", "ssimMean"),
                    "ssimMeanBed": metric(bed, "perceptual", "ssimMean"),
                    "ssimBandCarrier": metric(css, "perceptual", "ssimBand"),
                    "ssimBandBed": metric(bed, "perceptual", "ssimBand"),
                    "levelRatioCarrier": metric(css, "coherence", "interiorLevelRatioGpuOverCss"),
                    "levelRatioBed": None if bed is None else metric(bed, "coherence", "interiorLevelRatioGpuOverCss"),
                    "crossTierDeltaECarrier": metric(css, "coherence", "crossTierOklabDeltaEMean"),
                    "crossTierDeltaEBed": None
                    if bed is None
                    else metric(bed, "coherence", "crossTierOklabDeltaEMean"),
                }
            )

    if len(sys.argv) > 3:
        Path(sys.argv[3]).write_text(json.dumps(rows, indent=1) + "\n")

    head = (
        f"{'dpr':>3} {'scene':<36} {'native':>7} {'GPU':>7} {'bed':>7} {'carrier':>8} "
        f"{'car-GPU':>8} {'bed-GPU':>8} {'sprN':>6} {'sprC':>6} {'sprBed':>6} "
        f"{'ssimC':>7} {'ssimBed':>7} {'ratioC':>7} {'ratioBed':>8}"
    )
    print(head)
    for row in rows:
        dpr = "2x" if "2x" in row["profileKey"] else "1x"
        print(
            f"{dpr:>3} {row['sceneId']:<36} {row['native']:7.4f} {row['gpuRendered']:7.4f} "
            f"{row['cssBed']:7.4f} {row['cssCarrier']:8.4f} {row['carrierMinusGpu']:+8.4f} "
            f"{row['bedMinusGpu']:+8.4f} {row['spreadNative']:6.4f} {row['spreadCarrier']:6.4f} "
            f"{row['spreadBed']:6.4f} {row['ssimMeanCarrier']:7.4f} {row['ssimMeanBed']:7.4f} "
            f"{row['levelRatioCarrier']:7.4f} {row['levelRatioBed']:8.4f}"
        )
    worst = max(rows, key=lambda row: abs(row["carrierMinusGpu"]))
    print(
        f"worst |carrier - GPU| {worst['carrierMinusGpu']:+.4f} on "
        f"{worst['profileKey']} {worst['sceneId']}"
    )


if __name__ == "__main__":
    main()
