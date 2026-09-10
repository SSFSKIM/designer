"""The floor cell at the candidate, under each of the four rules.

`texture / holdout / checkerboard__glass-over-glass__rest /
apple-macos-26.5-2x-dark-standard`, floor 0.9257. The 0.14.0 column is the
canonical committed capture; the candidate column is G2b's scratch capture of the
ruled configuration.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage

import w26extractor as X
from anatomy import CAND_ROOT, PROFILE, SCENE
from blast import holes_of, hysteresis, iou_within

FLOOR = 0.9257


def main():
    native, web0, bg, region, _ = X.cell_inputs(PROFILE, SCENE, "webgpu")
    webc = X.load(X.web_path(PROFILE, SCENE, "webgpu", root=CAND_ROOT))
    n = X.extract_luminance_delta(native, bg, region)
    cols = {"0.14.0": X.extract_luminance_delta(web0, bg, region),
            "candidate": X.extract_luminance_delta(webc, bg, region)}
    hn = hysteresis(native, bg, region)
    hyst = {"0.14.0": hysteresis(web0, bg, region), "candidate": hysteresis(webc, bg, region)}

    print(f"texture / holdout / {SCENE} / {PROFILE}   floor {FLOOR}")
    print()
    print(f"{'rule':<12}{'0.14.0':>10}{'candidate':>12}{'Δ':>10}   verdict at the candidate")
    for rule in ("base", "fill", "drop", "hyst"):
        vals = {}
        for label, w in cols.items():
            if rule == "base":
                vals[label] = X.iou(n, w)
            elif rule == "fill":
                vals[label] = X.iou(X.fill_holes(n), X.fill_holes(w))
            elif rule == "drop":
                pop = (region != 0) & ~(holes_of(n, region) | holes_of(w, region))
                vals[label] = iou_within(n, w, pop)
            else:
                vals[label] = X.iou(hn, hyst[label])
        d = vals["candidate"] - vals["0.14.0"]
        verdict = "OVER the floor" if vals["candidate"] >= FLOOR else "UNDER the floor"
        print(f"{rule:<12}{vals['0.14.0']:>10.5f}{vals['candidate']:>12.5f}{d:>+10.5f}   {verdict}")

    print()
    print("The population `drop` removes, per column (region pixels the extractor")
    print("cannot decide because one side's material coincides with its backdrop):")
    for label, w in cols.items():
        hn_px = int(holes_of(n, region).sum())
        hw_px = int(holes_of(w, region).sum())
        both = int((holes_of(n, region) | holes_of(w, region)).sum())
        print(f"  {label:<10} native holes {hn_px:>6} px, web holes {hw_px:>6} px, "
              f"union {both:>6} px of {int(region.sum())} ({both / region.sum():.2%})")


if __name__ == "__main__":
    main()
