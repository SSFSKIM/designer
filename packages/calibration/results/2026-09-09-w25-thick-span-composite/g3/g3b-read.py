"""W25 G3b — one joint rung read by BOTH of the wave's rim instruments.

WHAT THIS READS. The reference fixtures of the four standard profiles, read-only, and ONE rung's
GPU captures under the g3b scratch root that `g3b-ladder.sh` wrote. It writes one JSON into that
rung's own directory and touches nothing else (X2).

TWO READERS, because the confound G3's dry run measured is exactly a confound BETWEEN them:

  * **the angular reader** (W24 G0's `read-angular.py`, imported and called in-process rather than
    restated, at that file's own defaults) — the rim's peak excess over the body along the inward
    normal at 720+ points of the declared boundary, binned into sixteen bins of 22.5° by the
    normal's ANGLE. It sees the corner ARCS, which is where `rimLitExponent` and
    `rimAlongSideSlope` overlap.
  * **the along-side reader** (W25 G0's `along-side.py`) — the same quantity indexed by POSITION on
    the straight part of a side, where the exponent's factor is exactly 1 by the `√2` normalisation
    and the field is the only term acting.

Neither reader alone can separate the pair: the angular one cannot see a position and the
along-side one cannot see an arc. Read together on the same rung they can, which is the whole
reason W25 Decision Log 6 re-opened the exponent instead of re-fitting the slope under it.

THE ROWS are the untinted FLAT-SOLID rows of the four standard profiles that are not holdout — the
five canonical calibration cells and the probe cells `g3b-ladder.sh` renders. Two exclusions, both
stated rather than silent: the bed's one holdout solid,
`mid-dark-solid__capsule-button__rest`, is never opened (X3); and `dark-solid__rrect-md-clear20`
is left out of the ANGULAR half because W24's reader places a component at the canvas centre and
that cell is displaced 32 points down — its along-side rows, where this file supplies the box, are
kept.

UNITS: bins and ranges in linear Rec.709 luma; slopes in luma per CSS px.

Usage: g3b-read.py --rung p115s000
"""

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
G0_W24 = os.path.join(HERE, "..", "..", "2026-09-09-w24-lit-edge", "g0")
G0_W25 = os.path.join(HERE, "..", "g0")
sys.path.insert(0, G0_W25)
import w25lib as L  # noqa: E402


def _load(name, directory, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(directory, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ANGULAR = _load("w24_read_angular", G0_W24, "read-angular.py")
ALONG = _load("w25_along_side", G0_W25, "along-side.py")

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3b"
PROFILES = ("1x-light", "2x-light", "1x-dark", "2x-dark")
SOLIDS = ("light-solid", "dark-solid", "mid-dark-solid")
# `read-angular.py`'s own CLI defaults, restated where they are used rather than re-chosen.
ERODE, OUTSIDE, DEPTH, STEP, SPACING, MIN_POINTS = 6.0, 1.0, 4.0, 0.25, 0.25, 720


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rung", required=True)
    ap.add_argument("--scratch", default=SCRATCH)
    args = ap.parse_args(argv)
    root = os.path.join(args.scratch, args.rung)

    matrix = json.load(open(L.SCENES))
    comps = matrix["components"]
    canvas = matrix["canvas"]
    holdout = set(matrix["split"]["holdout"])

    rows = []
    for pkey in PROFILES:
        profile, scale, _scheme = L.PROFILES[pkey]
        declared = None
        for entry in matrix["profiles"]:
            if entry["key"] == profile:
                declared = entry.get("scenes")
        for scene in matrix["scenes"]:
            sid = scene["id"]
            if scene.get("background") not in SOLIDS or "tint" in scene:
                continue
            if scene.get("state") != "rest" or sid in holdout:
                continue
            if isinstance(declared, list) and sid not in declared:
                continue
            native = L.native_path(profile, sid)
            web = os.path.join(root, profile, sid, f"{sid}__webgpu.png")
            if not (os.path.exists(native) and os.path.exists(web)):
                continue
            component = scene["component"]
            offset = comps[component].get("offset")
            cell = L.Cell(component, comps)
            if offset and cell.kind not in ("stack", "group"):
                cell.box = L.place(comps[component]["size"], offset)
            geom = ANGULAR.component_geometry(comps, component)
            row = {"profile": pkey, "scheme": _scheme, "scale": scale, "scene": sid,
                   "backdrop": scene["background"], "component": component,
                   "span": float(cell.short), "displaced": bool(offset)}
            for tag, path in (("native", native), ("web", web)):
                entry = {}
                if geom is not None and not offset:
                    read = ANGULAR.read_one(path, canvas, geom, ERODE, OUTSIDE, DEPTH, STEP,
                                            SPACING, MIN_POINTS)
                    entry["bins"] = read["bins"]
                    entry["body"] = read["body"]
                lum = L.luma_of(path)
                sides = {}
                if cell.kind not in ("stack", "group"):
                    for side in ("top", "bottom", "left", "right"):
                        u, excess, _b, _l = ALONG.side_profiles(
                            lum, cell.box, cell.radius, cell.kind, scale, side)
                        summary = ALONG.summarise(u, excess)
                        if summary is not None:
                            sides[side] = {"range": summary["range"], "mean": summary["mean"],
                                           "slopePerCss": summary["slopePerCss"]}
                entry["sides"] = sides
                row[tag] = entry
            rows.append(row)
            print(f"  {pkey:9} {sid:40} read", file=sys.stderr)

    path = os.path.join(root, f"read-{args.rung}.json")
    json.dump({"rung": args.rung, "rows": rows}, open(path, "w"), indent=1)
    print(f"{len(rows)} rows -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
