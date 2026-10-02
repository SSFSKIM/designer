#!/usr/bin/env python3.12
"""W43 G3 (i): one Newton step on the tone rows, from a render's residuals (Decision Log 7 items 1, 3).

The body's level on a uniform backdrop is the response law's ordinate at that backdrop's anchor
(material.ts, `backdropToneResponseThin` / `…Thick`: "the reference's settled interior levels at
those anchors"), so the level residual on a knot's own cells moves that ordinate one for one.
This reads a render's CALIBRATION rows only (validation is the transfer; holdout is never read),
untinted, and per (document, row, knot):

  residual = mean over the knot's cells of (interiorMeanWeb − interiorMeanNative), both scales
  step     = − damp × residual

  knots    impulse (anchor 0), dark-solid (1), photo (2), light-solid (3), the ANCHORS held
  rows     thin: capsule-button (span 44) and rrect-sm (32); thick: rrect-md, -ml, -lg
  black    the light black ordinates (thin = thick, as W36 declared them) take knot 0's thin step

Light documents move both rows and the black branch (item 1); dark documents move the thick row
only (item 3). A knot with no calibration cell in a row keeps its value. The new spec carries every
other override of the spec it starts from unchanged.

    python3.12 -B propose.py --from LABEL --spec-in specs/cNN.json --label cMM [--damp 1]
                             [--schemes light,dark] [--note TEXT]
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit as F  # noqa: E402
import bed as B  # noqa: E402

KNOT = {"impulse": 0, "dark-solid": 1, "photo": 2, "light-solid": 3}
ROW = {"capsule-button": "thin", "rrect-sm": "thin", "rrect-md": "thick", "rrect-ml": "thick",
       "rrect-lg": "thick"}


def current(spec: dict, slot: str, leaf: str):
    over = spec.get("overrides", {}).get(slot, {})
    if leaf in over:
        return over[leaf]
    pose, scheme = slot.split(".")
    doc = json.loads((B.CAL / "profiles" / f"apple-macos-27.0-1x-{scheme}-standard-glass0.5"
                      f"{'-receded' if pose == 'receded' else ''}.json").read_text())
    return doc["patch"][leaf]


def residuals(label: str) -> dict:
    out = defaultdict(list)
    for r in F.load_bed(label, "webgpu", {"calibration"}):
        bg, comp, pose = r["key"]["sceneId"].split("__")
        if "-tint-" in pose or pose not in ("rest", "inactive") or bg not in KNOT or comp not in ROW:
            continue
        n, w = B.value(r, "material", "interiorMeanNative"), B.value(r, "material", "interiorMeanWeb")
        if n is None or w is None:
            continue
        slot = f"{'receded' if pose == 'inactive' else 'active'}.{B.scheme_of(r['key']['profileKey'])}"
        out[(slot, ROW[comp], KNOT[bg])].append(w - n)
    return {k: st.mean(v) for k, v in out.items()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="source", required=True)
    ap.add_argument("--spec-in", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--damp", type=float, default=1.0)
    ap.add_argument("--schemes", default="light,dark")
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    spec = json.loads(Path(args.spec_in).read_text())
    res = residuals(args.source)
    new = json.loads(json.dumps(spec))
    new["label"] = args.label
    steps = {}
    for scheme in args.schemes.split(","):
        for pose in ("active", "receded"):
            slot = f"{pose}.{scheme}"
            over = new.setdefault("overrides", {}).setdefault(slot, {})
            rows = ("thin", "thick") if scheme == "light" else ("thick",)
            for row in rows:
                leaf = f"backdropToneResponse{row.capitalize()}"
                values = list(current(new, slot, leaf))
                for knot in range(4):
                    r = res.get((slot, row, knot))
                    if r is None:
                        continue
                    step = -args.damp * r
                    values[knot] = round(values[knot] + step, 4)
                    steps[f"{slot} {row} knot{knot}"] = dict(residual=round(r, 5), step=round(step, 5))
                over[leaf] = values
            if scheme == "light" and (slot, "thin", 0) in res:
                step = -args.damp * res[(slot, "thin", 0)]
                for leaf in ("backdropToneBlackThin", "backdropToneBlackThick"):
                    over[leaf] = round(current(new, slot, leaf) + step, 6)
                steps[f"{slot} black"] = dict(residual=round(res[(slot, "thin", 0)], 5), step=round(step, 5))
    new["note"] = (args.note or f"tone Newton step from {args.source} (damp {args.damp}), "
                   f"over {Path(args.spec_in).name}")
    new["toneStep"] = dict(source=args.source, damp=args.damp, steps=steps)
    out = HERE / "specs" / f"{args.label}.json"
    with out.open("x") as f:
        f.write(json.dumps(new, indent=1) + "\n")
    print(json.dumps(steps, indent=1))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
