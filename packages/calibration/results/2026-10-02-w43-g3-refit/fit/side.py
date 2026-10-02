#!/usr/bin/env python3.12
"""W43 G3 (i): several renders' residuals side by side, per class (a fitting aid, not a cut).

For each (scheme, pose, backdrop, span class) over the chosen sets of a scheme's untinted cells:
  lv   mean (interiorMeanWeb − interiorMeanNative), linear
  sl   mean luminanceSlopeWeb / luminanceSlopeNative (the transfer slope; structured backdrops)
  sd   mean interiorStdDevWeb / interiorStdDevNative

    python3.12 -B side.py prefit c01 c01a ... [--sets calibration] [--scheme light] [--renderer webgpu]
"""
from __future__ import annotations

import argparse
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit as F  # noqa: E402
import bed as B  # noqa: E402


def readings(label, renderer, sets, scheme, tinted):
    out = defaultdict(lambda: defaultdict(list))
    for r in F.load_bed(label, renderer, sets):
        if B.scheme_of(r["key"]["profileKey"]) != scheme:
            continue
        bg, comp, pose = r["key"]["sceneId"].split("__")
        if ("-tint-" in pose) != tinted:
            continue
        key = ("inactive" if pose.startswith("inactive") else "rest", bg + (" " + pose.split("-tint-")[1] if tinted else ""),
               F.CLASS.get(comp, comp))
        v = lambda m: B.value(r, "material", m)  # noqa: E731
        if None not in (v("interiorMeanWeb"), v("interiorMeanNative")):
            out[key]["lv"].append(v("interiorMeanWeb") - v("interiorMeanNative"))
        if v("luminanceSlopeNative") and v("luminanceSlopeWeb") is not None:
            out[key]["sl"].append(v("luminanceSlopeWeb") / v("luminanceSlopeNative"))
        if v("interiorStdDevNative") and v("interiorStdDevWeb") is not None:
            out[key]["sd"].append(v("interiorStdDevWeb") / v("interiorStdDevNative"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("labels", nargs="+")
    ap.add_argument("--sets", default="calibration")
    ap.add_argument("--scheme", default="light")
    ap.add_argument("--renderer", default="webgpu")
    ap.add_argument("--tinted", action="store_true")
    args = ap.parse_args()
    sets = set(args.sets.split(","))
    data = {label: readings(label, args.renderer, sets, args.scheme, args.tinted) for label in args.labels}
    keys = sorted(set().union(*[set(d) for d in data.values()]))
    head = f"{'pose':<9}{'backdrop':<24}{'class':<10}" + "".join(f"| {l:^26}" for l in args.labels)
    print(f"# {args.scheme} {args.renderer} {sorted(sets)}: lv = web-native level, sl = slope ratio, sd = stddev ratio")
    print(head)
    for key in keys:
        cells = []
        for label in args.labels:
            d = data[label].get(key, {})
            m = lambda k: st.mean(d[k]) if d.get(k) else None  # noqa: E731
            f = lambda x, s: " " * len(format(0, s)) if x is None else format(x, s)  # noqa: E731
            cells.append(f"| {f(m('lv'), '+.4f')} {f(m('sl'), '5.2f')} {f(m('sd'), '5.2f')}  ")
        print(f"{key[0]:<9}{key[1]:<24}{key[2]:<10}" + "".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
