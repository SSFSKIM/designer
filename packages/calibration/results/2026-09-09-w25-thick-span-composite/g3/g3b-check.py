"""W25 G3b — the check off the fitted rows, and the per-row verdict on the fitted ones.

Two tables, both of W24's angular bin ERROR against the reference — the quantity the joint fit
minimises — read where the fit did not look:

  * **the checkerboard cells** (`g3b-check.sh`'s rows), which carry the rim over structure and are
    the rows a fit made on flat solids could most easily have bought at the expense of;
  * **the fitted solid rows themselves**, per row, before and after, because the ruling's condition
    is not an aggregate: *the thick solids must improve or the pair does not land*.

`--before` and `--after` are two rendered materials' capture roots, each laid out
`<root>/<profile>/<scene>/<scene>__webgpu.png`. The reference side is the committed fixtures in
both columns, so a column's difference is the material and nothing else.

    g3b-check.py --before <root> --after <root> [--thick-span 96]
"""

import argparse
import importlib.util
import json
import math
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
PROFILES = ("1x-light", "2x-light", "1x-dark", "2x-dark")
ERODE, OUTSIDE, DEPTH, STEP, SPACING, MIN_POINTS = 6.0, 1.0, 4.0, 0.25, 0.25, 720


def bin_error(native, web):
    """Mean |web − native| over the sixteen bins, divided by the row's own brightest native bin."""
    scale = max((abs(v) for v in native if v is not None and math.isfinite(v)), default=0.0)
    if scale <= 1e-6:
        return None
    deltas = [abs(w - n) for n, w in zip(native, web)
              if n is not None and w is not None and math.isfinite(n) and math.isfinite(w)]
    return (sum(deltas) / len(deltas) / scale) if deltas else None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--thick-span", type=float, default=96.0)
    args = ap.parse_args(argv)

    matrix = json.load(open(L.SCENES))
    comps, canvas = matrix["components"], matrix["canvas"]
    scenes = {s["id"]: s for s in matrix["scenes"]}

    print("W25 G3b — the angular bin error against the reference, 0.13.0 material -> the pair")
    print("=" * 108)
    print(f"{'profile':9} {'scene':40} {'backdrop':16} {'span':>5} {'before':>9} {'after':>9} "
          f"{'Δ':>9}")
    improved = worsened = 0
    thick_worse = []
    for pkey in PROFILES:
        profile, scale, _scheme = L.PROFILES[pkey]
        for sid, scene in scenes.items():
            before = os.path.join(args.before, profile, sid, f"{sid}__webgpu.png")
            after = os.path.join(args.after, profile, sid, f"{sid}__webgpu.png")
            native = L.native_path(profile, sid)
            if not (os.path.exists(before) and os.path.exists(after) and os.path.exists(native)):
                continue
            component = scene["component"]
            if comps[component].get("offset"):
                continue
            geom = ANGULAR.component_geometry(comps, component)
            if geom is None:
                continue
            nat = ANGULAR.read_one(native, canvas, geom, ERODE, OUTSIDE, DEPTH, STEP, SPACING,
                                   MIN_POINTS)["bins"]
            eb = bin_error(nat, ANGULAR.read_one(before, canvas, geom, ERODE, OUTSIDE, DEPTH,
                                                 STEP, SPACING, MIN_POINTS)["bins"])
            ea = bin_error(nat, ANGULAR.read_one(after, canvas, geom, ERODE, OUTSIDE, DEPTH,
                                                 STEP, SPACING, MIN_POINTS)["bins"])
            if eb is None or ea is None:
                continue
            span = float(min(comps[component]["size"])) if "size" in comps[component] else 0.0
            if ea < eb:
                improved += 1
            elif ea > eb:
                worsened += 1
                if span >= args.thick_span:
                    thick_worse.append((pkey, sid, eb, ea))
            print(f"{pkey:9} {sid:40} {scene['background']:16} {span:5.0f} {eb:9.5f} {ea:9.5f} "
                  f"{ea - eb:+9.5f}")
    print()
    print(f"rows improved: {improved}   worsened: {worsened}")
    print(f"THICK rows (span >= {args.thick_span:g}) that worsened: {len(thick_worse)}")
    for pkey, sid, eb, ea in thick_worse:
        print(f"  {pkey:9} {sid:40} {eb:.5f} -> {ea:.5f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
