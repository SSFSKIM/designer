"""W25 G2 — the row table the three fits are conditioned on: span, backdrop level, and lever inputs.

WHAT THIS READS. The backdrop rasters only — `apps/reference-apple/fixtures/backgrounds/` for the
canonical bed and the W21 probe's `backgrounds/` for the two grids — plus `scenes.json` and the two
probe scene matrices for the geometry. No capture, no fixture, no matrix. Read-only throughout.

WHY IT EXISTS. The W23 lesson is that the condition of a fit is checked before the fit, and the
condition of all three of W25's mechanisms is a function of two numbers per row: the surface's SPAN,
which is what `sizeThickness` and the above-knee curve read, and the BACKDROP's own linear mean,
which is what the tone response's argument is. This dumps both for every row of the three 1x beds,
and `predict.mjs` beside it turns them into levers through the renderer's own material functions —
so the arithmetic that decides which rows separate a constant is the arithmetic that will draw it.

UNITS. `backdropLinear` is the Rec.709 luma mean over the surface's own border box, in linear light,
which is the quantity `GroupRenderInput.backdropTone` carries and the tone response's argument is
the sRGB encoding of. Spans are the SHORT side in CSS px, `instances.ts:204`'s own rule.

Usage: rows.py [--out rows.json]
"""

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "g0"))
import w25lib as L  # noqa: E402

BEDS = [
    # (bed key, scenes matrix, backdrop loader, scheme)
    ("canon-light", L.SCENES, "canonical", "light"),
    ("canon-dark", L.SCENES, "canonical", "dark"),
    ("w9", os.path.join(L.REPO, "apps", "reference-apple", "scenes-w9-probe.json"), "probe",
     "light"),
    ("w21", os.path.join(L.REPO, "apps", "reference-apple", "scenes-w21-probe.json"), "probe",
     "dark"),
]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="rows.json")
    args = ap.parse_args(argv)

    out = []
    for key, scenes_path, loader, scheme in BEDS:
        matrix = json.load(open(scenes_path))
        comps = matrix["components"]
        holdout = set(matrix.get("split", {}).get("holdout", []))
        shape = (200, 320)
        cache = {}
        for scene in matrix["scenes"]:
            if scene.get("state") != "rest" or "tint" in scene:
                continue
            component = scene["component"]
            if component not in comps:
                continue
            backdrop = scene["background"]
            if backdrop not in cache:
                cache[backdrop] = (L.background_for(backdrop, 1.0, shape) if loader == "canonical"
                                   else L.probe_background(backdrop, 1.0, shape))
            bg = cache[backdrop]
            cell = L.Cell(component, comps)
            boxes = ([("base", *cell.base)] if cell.kind == "stack"
                     else [(f"m{i}", *m) for i, m in enumerate(cell.members)] if cell.kind == "group"
                     else [("", cell.box, cell.radius, cell.kind)])
            for label, box, radius, kind in boxes:
                mask = L.rrect_mask(box, radius, 1.0, shape, 0.0, kind)
                out.append({
                    "bed": key,
                    "scheme": scheme,
                    "scene": scene["id"],
                    "sub": label,
                    "backdrop": backdrop,
                    "component": component,
                    "holdout": scene["id"] in holdout,
                    "spanCss": float(min(box["width"], box["height"])),
                    "widthCss": float(box["width"]),
                    "heightCss": float(box["height"]),
                    "radiusCss": float(radius),
                    "kind": kind,
                    "backdropLinear": float(np.mean(bg[mask])),
                    "pitchCss": L.backdrop_pitch_css(backdrop),
                })
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"{len(out)} rows -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
