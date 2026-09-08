"""W22 G3 — the nested pane read on VITREA'S OWN capture, with no native fixture opened.

Both `glass-over-glass` cells are holdout and the wave's one holdout read belongs to G1 (X5), so
this gate may not put the reference beside vitrea. What it can do is the check the design named:
read the two panes off vitrea's capture and ask whether the OVERLAY's body is what the shipped
response law gives at the BASE pane's own measured output. That is a statement about vitrea against
vitrea's material, and it needs no reference at all.

The instrument is G0's, imported and not re-implemented: `read_stack`, `place` and the masks come
from `../g0/read-stack.py` by path, so the geometry, the erosion, the dilated cut-out and the peak
statistic are the same ten quantities X3 validated by injection (worst recovery error 0.000625).
Only the driver is new — G0's `main` requires a fixture to key its loop on, and this one keys on the
capture. The response law is `../g0/predict-overlay.py`'s, imported the same way.

Usage:

    read-stack-web.py --captures <dir> --scenes <scenes.json> --profile <key> --tier webgpu \
                      --profile-doc <profile json> [--json <out>]
"""

import argparse
import importlib.util
import json
import os
import sys

import numpy as np


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


HERE = os.path.dirname(os.path.abspath(__file__))
G0 = os.path.join(HERE, "..", "g0")
stack = load("w22_g0_read_stack", os.path.join(G0, "read-stack.py"))
predict = load("w22_g0_predict_overlay", os.path.join(G0, "predict-overlay.py"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", required=True)
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--profile-doc", required=True)
    ap.add_argument("--tier", default="webgpu")
    ap.add_argument("--component", default="glass-over-glass")
    ap.add_argument("--erode", type=float, default=6.0)
    ap.add_argument("--band", type=float, default=3.0)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    spec = json.load(open(args.scenes))
    canvas = spec["canvas"]
    component = spec["components"][args.component]
    base_box = stack.place(component["base"], canvas)
    over_box = stack.place(component["over"], canvas)

    patch = json.load(open(args.profile_doc))["patch"]
    xs = patch["backdropToneAnchorX"]
    thin = patch["backdropToneResponseThin"]
    thick = patch["backdropToneResponseThick"]

    declared = None
    for p in spec["profiles"]:
        if p["key"] == args.profile:
            declared = p.get("scenes")

    rows = []
    for scene in spec["scenes"]:
        if scene["component"] != args.component:
            continue
        sid = scene["id"]
        if isinstance(declared, list) and sid not in declared:
            continue
        png = os.path.join(args.captures, args.profile, sid, f"{sid}__{args.tier}.png")
        if not os.path.exists(png):
            continue
        lum = stack.luma_of(png)
        row = stack.read_stack(lum, base_box, over_box, canvas, args.erode, args.band)
        # The overlay is 120 x 56 CSS px, under `sizeSpanMin` on its short side, so it is a THIN
        # surface and the law is read on the thin row; the thick row is the bound in the other
        # direction and is printed beside it.
        x = predict.encode(row["baseBody"])
        row["scene"] = sid
        row["lawInput"] = x
        row["lawThin"] = predict.response(x, 0.0, xs, thin, thick)
        row["lawThick"] = predict.response(x, 1.0, xs, thin, thick)
        row["overMinusLawThin"] = row["overBody"] - row["lawThin"]
        rows.append(row)

    print(f"== {args.profile} / {args.tier}   (web only; no fixture opened)")
    head = (f"{'scene':44s} {'base':>8s} {'over':>8s} {'excess':>8s} {'lawIn':>7s} "
            f"{'lawThin':>8s} {'lawThick':>9s} {'over-law':>9s} {'overSd':>7s}")
    print(head)
    for r in rows:
        print(f"{r['scene']:44s} {r['baseBody']:8.4f} {r['overBody']:8.4f} {r['excess']:+8.4f} "
              f"{r['lawInput']:7.4f} {r['lawThin']:8.4f} {r['lawThick']:9.4f} "
              f"{r['overMinusLawThin']:+9.4f} {r['overSd']:7.4f}")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"profile": args.profile, "tier": args.tier,
                       "captures": os.path.abspath(args.captures),
                       "placement": {"base": base_box, "over": over_box},
                       "rows": rows}, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
