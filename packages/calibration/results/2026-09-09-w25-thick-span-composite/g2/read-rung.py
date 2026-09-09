"""W25 G2 — one rung read: the three widths, the body levels and the along-side rim, native | web.

WHAT THIS READS. The reference fixtures (`apps/reference-apple/fixtures/<profile>/`) and the two
probe grids' native captures, both read-only; and ONE RUNG's web captures under the scratch root,
which `ladder.sh` wrote and nothing else reads. It writes a single JSON into the scratch rung's own
directory. Nothing under `fixtures/`, `scenes.json`, `results/matrix.json` or the canonical
`web-captures/` is touched — X2.

THE INSTRUMENTS ARE G0's, unchanged. `w25lib.py`'s reader A (the dot's two-component PSF), reader B
(the edge spread) and reader C (the whole-region sigma match) are imported, not restated, and so is
`along-side.py`'s position reader; W25 X1 makes G0's three readers the wave's only width
instrument, and a rung that measured itself with a fourth would not be comparable with G0's table.

THE FOUR BEDS a rung carries, and where each one's NATIVE side comes from:
  w9          the W9 light probe grid   → results/2026-09-02-w9-probe/apple-…-1x-light-standard
  w21         the W21 dark probe grid   → results/2026-09-06-w21-dark-scheme/probe/apple-…-1x-dark
  canon-light the canonical 1x light bed → apps/reference-apple/fixtures/apple-…-1x-light-standard
  canon-dark  the canonical 1x dark bed  → apps/reference-apple/fixtures/apple-…-1x-dark-standard

TWO CELLS ARE REFUSED on the dark grid: `dark-solid__rrect-sm__rest` and
`light-solid__rrect-sm__rest`, whose files W25 G0 showed to be byte-identical to the W9 LIGHT grid's
captures of the same scenes and which W25 Decision Log 3 (d) withdrew as dark readings. They are
skipped here by name rather than filtered later, so no fit can reach them.

UNITS. Sigmas in DEVICE px (the grids and the canonical 1x bed are all scale 1, so device and CSS px
coincide on every row this file reads). Levels in linear Rec.709 luma; `codes` is the same
difference through the sRGB OETF. Along-side slopes in luma per CSS px.

Usage: read-rung.py --rung r0 [--scratch DIR] [--out DIR]
"""

import argparse
import importlib.util
import json
import os
import sys

import numpy as np

G0 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "g0")
sys.path.insert(0, G0)
import w25lib as L  # noqa: E402


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(G0, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ALONG = _load("w25_along_side", "along-side.py")

SCRATCH_DEFAULT = "/Users/new/.claude/jobs/5c70e47f/tmp/w25/g2"
WITHDRAWN = {("w21", "dark-solid__rrect-sm__rest"), ("w21", "light-solid__rrect-sm__rest")}
STRUCTURED = {"checkerboard", "checkerboard-4", "checkerboard-8", "checkerboard-16",
              "checkerboard-32", "checkerboard-64", "checkerboard-lc16", "hc-text", "hc-text-7",
              "hc-text-28", "photo", "impulse"}
FLAT = {"light-solid", "dark-solid", "mid-dark-solid"}
EDGE = {"checkerboard", "checkerboard-32", "checkerboard-64", "checkerboard-lc16", "hc-text"}

BEDS = {
    "w9": {
        "native": os.path.join(L.RESULTS, "2026-09-02-w9-probe",
                               "apple-macos-26.5-1x-light-standard"),
        "scenes": os.path.join(L.REPO, "apps", "reference-apple", "scenes-w9-probe.json"),
        "background": "probe", "scheme": "light",
    },
    "w21": {
        "native": os.path.join(L.RESULTS, "2026-09-06-w21-dark-scheme", "probe",
                               "apple-macos-26.5-1x-dark-standard"),
        "scenes": os.path.join(L.REPO, "apps", "reference-apple", "scenes-w21-probe.json"),
        "background": "probe", "scheme": "dark",
    },
    "canon-light": {
        "native": os.path.join(L.FIXTURES, "apple-macos-26.5-1x-light-standard"),
        "scenes": L.SCENES, "background": "canonical", "scheme": "light",
    },
    "canon-dark": {
        "native": os.path.join(L.FIXTURES, "apple-macos-26.5-1x-dark-standard"),
        "scenes": L.SCENES, "background": "canonical", "scheme": "dark",
    },
}


def read_widths(lum, bg, cell, backdrop, ref_key):
    """G0 `widths.py`'s `read_widths` at scale 1, each reader only where its backdrop answers."""
    out = {}
    mask = cell.body_mask(1.0, lum.shape, 6.0)
    if backdrop == "impulse":
        rows = L.read_psf_cell(lum, bg, cell, 1.0, half_css=30.0)
        if rows:
            out["A"] = {
                "sigmaDev": float(np.median([r["sigmaEquivDev"] for r in rows])),
                "sharpDev": float(np.median([r["sharpSigmaDev"] for r in rows])),
                "heavyDev": float(np.median([r["heavySigmaDev"] for r in rows])),
                "heavyShare": float(np.median([r["heavyShare"] for r in rows])),
                "residual": float(np.median([r["rmsRel"] for r in rows])),
                "n": len(rows),
            }
    if backdrop in EDGE:
        b = L.read_edge_spread(lum, bg, mask, 1.0, sigma_ceiling_dev=64.0)
        if b["n"]:
            out["B"] = {"sigmaDev": b["sigmaDev"], "residual": b["residual"], "n": b["n"]}
    if backdrop in STRUCTURED:
        c = L.sigma_match(lum, bg, mask, top=64.0, ref_key=ref_key)
        out["C"] = {"sigmaDev": c["sigmaDev"], "residual": c["rmsRel"], "gain": c.get("gain"),
                    "sd": c["sd"], "atCeiling": c["atCeiling"]}
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rung", required=True)
    ap.add_argument("--scratch", default=SCRATCH_DEFAULT)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    root = os.path.join(args.scratch, args.rung)
    widths, levels, sides = [], [], []

    tasks = []
    for bed, spec in BEDS.items():
        webdir = os.path.join(root, bed)
        if not os.path.isdir(webdir):
            continue
        matrix = json.load(open(spec["scenes"]))
        comps = matrix["components"]
        holdout = set(matrix.get("split", {}).get("holdout", []))
        for scene in matrix["scenes"]:
            sid = scene["id"]
            if scene.get("state") != "rest" or "tint" in scene:
                continue
            if (bed, sid) in WITHDRAWN:
                continue
            native = os.path.join(spec["native"], f"{sid}.png")
            web = os.path.join(webdir, sid, f"{sid}__webgpu.png")
            if not (os.path.exists(native) and os.path.exists(web)):
                continue
            tasks.append((scene["background"], bed, sid, scene["component"], comps,
                          sid in holdout, native, web, spec))

    # Ordered by (backdrop, bed): reader C's blurred-reference cache holds one backdrop at a time.
    for backdrop, bed, sid, component, comps, is_holdout, native, web, spec in sorted(
            tasks, key=lambda t: (t[0], t[1], t[2])):
        shape = (200, 320)
        bg = (L.background_for(backdrop, 1.0, shape) if spec["background"] == "canonical"
              else L.probe_background(backdrop, 1.0, shape))
        cell = L.Cell(component, comps)
        mask = cell.body_mask(1.0, shape, 6.0)
        for tag, path in (("native", native), ("web", web)):
            lum = L.luma_of(path)
            if lum.shape != shape:
                continue
            levels.append({
                "bed": bed, "scheme": spec["scheme"], "scene": sid, "backdrop": backdrop,
                "component": component, "holdout": is_holdout, "src": tag,
                "span": float(cell.short), "body": float(lum[mask].mean()),
                "sd": float(lum[mask].std()), "n": int(mask.sum()),
            })
            if backdrop not in FLAT:
                for reader, v in read_widths(lum, bg, cell, backdrop,
                                             (spec["background"], backdrop)).items():
                    widths.append({
                        "bed": bed, "scheme": spec["scheme"], "scene": sid, "backdrop": backdrop,
                        "component": component, "holdout": is_holdout, "src": tag,
                        "span": float(cell.short), "reader": reader, **v,
                    })
            if backdrop in FLAT and cell.kind not in ("stack", "group"):
                for side in ("top", "bottom", "left", "right"):
                    u, excess, _body, _len = ALONG.side_profiles(
                        lum, cell.box, cell.radius, cell.kind, 1.0, side)
                    s = ALONG.summarise(u, excess)
                    if s is None:
                        continue
                    sides.append({
                        "bed": bed, "scheme": spec["scheme"], "scene": sid, "backdrop": backdrop,
                        "component": component, "holdout": is_holdout, "src": tag,
                        "span": float(cell.short), "side": side,
                        "mean": s["mean"], "range": s["range"], "slopePerCss": s["slopePerCss"],
                        "lengthCss": s["lengthCss"],
                    })
        print(f"  {bed:12} {sid:44} read", file=sys.stderr)

    out = args.out or root
    path = os.path.join(out, f"rung-{args.rung}.json")
    json.dump({"rung": args.rung, "widths": widths, "levels": levels, "sides": sides},
              open(path, "w"), indent=1)
    print(f"{len(widths)} width rows, {len(levels)} level rows, {len(sides)} side rows -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
