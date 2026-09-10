"""Blast radius over the committed 0.14.0 bed of four candidate rules for
`silhouetteIoU`, each of which treats the two sides alike.

  base       what ships: IoU over the masks as extracted.
  fill       IoU over HOLE-FILLED masks on both sides — the rule `contourDistance`
             already applies to its boundaries (`shape.ts`, 2026-08-31).
  drop       IoU over the region MINUS every pixel that is inside a hole of either
             mask: the extractor cannot decide those pixels, so they leave the
             population instead of being asserted as coverage.
  hysteresis a pixel is inside if |Δ| >= t, or if |Δ| >= t/2 and it is 4-connected
             to such a pixel — the standard cure for a level fence, applied at
             extraction and therefore to both sides at once.

Only `silhouetteIoU` moves under `fill`, `drop` and (for `hysteresis`, also areas
and hole counts). Every recomputation is checked against the committed matrix
before it is used.
"""

from __future__ import annotations

import json
import os

import numpy as np
from scipy import ndimage

import w26extractor as X

MATRIX = os.path.join(X.REPO, "packages/calibration/results/matrix.json")
_CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool)
GATED_SETS = ("calibration", "validation")

FLOORS = {
    ("dom", "checkerboard__glass-over-glass__rest", "apple-macos-26.5-1x-dark-standard"): 0.9070,
    ("texture", "checkerboard__glass-over-glass__rest", "apple-macos-26.5-2x-dark-standard"): 0.9257,
    ("dom", "checkerboard__glass-over-glass__rest", "apple-macos-26.5-2x-dark-standard"): 0.9038,
}
BOUNDS = {
    ("apple-macos-26.5-1x-light-standard", "texture"): 0.82,
    ("apple-macos-26.5-1x-light-standard", "dom"): 0.85,
    ("apple-macos-26.5-2x-light-standard", "texture"): 0.85,
    ("apple-macos-26.5-2x-light-standard", "dom"): 0.85,
    ("apple-macos-26.5-1x-light-reduced-transparency", "texture"): 0.87,
    ("apple-macos-26.5-1x-light-reduced-transparency", "dom"): 0.89,
    ("apple-macos-26.5-1x-light-increased-contrast", "texture"): 0.85,
    ("apple-macos-26.5-1x-light-increased-contrast", "dom"): 0.80,
    ("apple-macos-26.5-1x-dark-standard", "texture"): 0.93,
    ("apple-macos-26.5-1x-dark-standard", "dom"): 0.93,
    ("apple-macos-26.5-2x-dark-standard", "texture"): 0.93,
    ("apple-macos-26.5-2x-dark-standard", "dom"): 0.93,
}
WELL_CONDITIONED_AREA_RATIO = 0.95


def holes_of(mask, region):
    """The pixels enclosed by a mask's holes, inside the region."""
    return ((X.fill_holes(mask) != 0) & (mask == 0) & (region != 0))


def hysteresis(image, background, region, t=X.DEFAULT_THRESHOLD, chroma=X.DEFAULT_CHROMA):
    strong = X.extract_luminance_delta(image, background, region, t, chroma).astype(bool)
    weak = X.extract_luminance_delta(image, background, region, t / 2, chroma).astype(bool)
    return ndimage.binary_propagation(strong, mask=weak, structure=_CROSS).astype(np.uint8)


def iou_within(a, b, population):
    a = a.astype(bool) & population
    b = b.astype(bool) & population
    return np.count_nonzero(a & b) / np.count_nonzero(a | b)


def measure():
    cells = [c for c in json.load(open(MATRIX))["cells"] if c.get("shape")]
    rows = []
    for c in cells:
        key = c["key"]
        profile, scene_id = key["profileKey"], key["sceneId"]
        native, web, bg, region, _ = X.cell_inputs(profile, scene_id, key["web"]["renderer"])
        n = X.extract_luminance_delta(native, bg, region)
        w = X.extract_luminance_delta(web, bg, region)
        base = X.iou(n, w)
        assert abs(base - c["shape"]["silhouetteIoU"]["value"]) < 1e-9
        undecidable = holes_of(n, region) | holes_of(w, region)
        population = (region != 0) & ~undecidable
        hn = hysteresis(native, bg, region)
        hw = hysteresis(web, bg, region)
        area = c["shape"]["componentRegionArea"]["value"]
        rows.append({
            "tier": c["tier"], "set": c["fixtureSet"], "scene": scene_id, "profile": profile,
            "holesNative": c["shape"]["silhouetteHolesNative"]["value"],
            "holesWeb": c["shape"]["silhouetteHolesWeb"]["value"],
            "conditioned": (c["shape"]["silhouetteAreaNative"]["value"] >= WELL_CONDITIONED_AREA_RATIO * area
                            and c["shape"]["silhouetteAreaWeb"]["value"] >= WELL_CONDITIONED_AREA_RATIO * area),
            "base": base,
            "fill": X.iou(X.fill_holes(n), X.fill_holes(w)),
            "drop": iou_within(n, w, population),
            "hyst": X.iou(hn, hw),
        })
    return rows


def summarise(rows, rule):
    d = np.array([r[rule] - r["base"] for r in rows])
    nz = np.abs(d) > 5e-6
    print(f"  {rule:<11} moves {int(nz.sum()):>4} of {len(rows)} cells   "
          f"Δ min {d.min():+.5f}  max {d.max():+.5f}  "
          f"down {int((d < -5e-6).sum()):>3}  up {int((d > 5e-6).sum()):>3}")


def main():
    rows = measure()
    print("How far each rule moves the committed bed's `silhouetteIoU`:")
    for rule in ("fill", "drop", "hyst"):
        summarise(rows, rule)

    print()
    print("Cells that move DOWN under a rule, and by how much (a rule that only ever")
    print("raises IoU is a rule that has stopped measuring something):")
    for rule in ("fill", "drop", "hyst"):
        down = sorted((r for r in rows if r[rule] - r["base"] < -0.001),
                      key=lambda r: r[rule] - r["base"])
        print(f"  {rule}: {len(down)} cells under -0.001")
        for r in down[:8]:
            print(f"      {r['tier']:<8}{r['set']:<12}{r['profile']:<44}{r['scene']:<40}"
                  f"holes {r['holesNative']:>4}/{r['holesWeb']:<4}"
                  f"{r['base']:>9.5f} -> {r[rule]:<9.5f}{r[rule] - r['base']:+9.5f}"
                  f"{'  [gated+conditioned]' if r['set'] in GATED_SETS and r['conditioned'] else ''}")

    print()
    print("The adopted `silhouetteIoU >=` bounds. Worst WELL-CONDITIONED cell of the")
    print("gated sets (calibration + validation) per profile and tier — the cell the")
    print("bound is actually set against. The conditioning predicate reads areas, which")
    print("`fill` and `drop` do not touch, so membership is identical under both.")
    print(f"{'profile':<46}{'tier':<9}{'bound':>7}{'base':>10}{'fill':>10}{'drop':>10}{'hyst':>10}")
    for (profile, tier), bound in BOUNDS.items():
        sel = [r for r in rows if r["profile"] == profile and r["tier"] == tier
               and r["set"] in GATED_SETS and r["conditioned"]]
        if not sel:
            print(f"{profile:<46}{tier:<9}{bound:>7.2f}   (no well-conditioned gated cell)")
            continue
        vals = {k: min(r[k] for r in sel) for k in ("base", "fill", "drop", "hyst")}
        note = ""
        for k in ("fill", "drop", "hyst"):
            if vals["base"] >= bound > vals[k]:
                note += f"  {k} WOULD BREAK"
        print(f"{profile:<46}{tier:<9}{bound:>7.2f}"
              f"{vals['base']:>10.5f}{vals['fill']:>10.5f}{vals['drop']:>10.5f}"
              f"{vals['hyst']:>10.5f}{note}")

    print()
    print("The three committed `silhouetteIoU` regression floors on the 0.14.0 bed:")
    print(f"{'floor row':<74}{'floor':>8}{'base':>10}{'fill':>10}{'drop':>10}{'hyst':>10}")
    for (tier, scene_id, profile), floor in FLOORS.items():
        for r in rows:
            if (r["tier"], r["scene"], r["profile"]) == (tier, scene_id, profile):
                label = f"{tier} / {r['set']} / {scene_id} / {profile}"
                print(f"{label:<74}{floor:>8.4f}{r['base']:>10.5f}{r['fill']:>10.5f}"
                      f"{r['drop']:>10.5f}{r['hyst']:>10.5f}")

    with open("blast-rows.json", "w") as f:
        json.dump(rows, f, indent=1)
    print()
    print("per-cell rows written to blast-rows.json")


if __name__ == "__main__":
    main()
