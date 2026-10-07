#!/usr/bin/env python3.12
"""W49a G0: part 1's numeric predictions for P2, from committed readings only (renders nothing).

Family R moves one thing: the receded dark 0.25 base alpha above the knee, alphaBase = 0.8 + far · farS(span),
with farS(160) = 1 (rrect-lg) and farS(128) = 0.5 (rrect-ml), 0 at span <= 96. Each reachable cell's T1 is
predicted by a straight line in alphaBase through two committed readings of the same receded scatter family:
`b2d074d2df24` (alphaBase 1.0 on rrect-lg, 0.9 on rrect-ml; W48's exposure cut) and W46's point A (alphaBase
0.8 at every span, no far delta; W46's gate cut). Point A sits over the d0219 active and lacks b2d074's second
heavy tap, so these are first-order predictions, stated before any render to be checked against it (DL6), not
readings. A withheld cell (referee, holdout), absent from point A's gate cut, is predicted on rrect-lg by the line through
b2d074 (1.0) and d0219cd684bf (0.89 flat), the grounding's "moves as checkerboard-64__rrect-lg__inactive does",
and on glass-over-glass (where b2d074 already transmits) as proportional to the transmission 1 - alphaBase.

Growth is W45's arithmetic, |k - n| - |c - n|, in the cell's own B from the exposure cut, against d0219 (DL2
(a), (b)) and against b2d074 (DL2 (c)).

    python3.12 -B predict.py > predict.txt          (also writes predict.json beside this file)
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parents[1]
EXPOSURE = RES / "2026-10-06-w48-g1-refit/cuts/cut-025-w48-dl9-exposure.json.gz"
POINT_A = RES / ("2026-10-05-w46-g1-refit/gate/"
                 "d-s2-rta0.8-rs214-rfa0.5-rh10.25-re20.04-rk10.15-rk20.04-rn10.4-rn20.4-rg0/cut.json.gz")
DARK = ("apple-macos-27.0-1x-dark-standard-glass0.25", "apple-macos-27.0-2x-dark-standard-glass0.25")
FAR = (-0.1, 0.0, 0.05, 0.09, 0.1, 0.15)
def _farS(span: float) -> float:
    t = min(max((span - 96) / (160 - 96), 0.0), 1.0)
    return t * t * (3 - 2 * t)


# The surfaces R reaches: rrect-lg (160) and rrect-ml (128), and glass-over-glass's base (130; its 56 px member
# is below the knee, so this first-order farS is the base's and over-states the cell's mean).
FARS = {"rrect-lg": _farS(160), "rrect-ml": _farS(128), "glass-over-glass": _farS(130)}
REPAIR = ("checkerboard-64__rrect-lg__inactive", "checkerboard-32__rrect-lg__inactive", "photo__rrect-lg__inactive")
FLATTERED = ("hc-text__rrect-lg__inactive", "impulse__rrect-lg__inactive", "checkerboard-8__rrect-lg__inactive")


def cells(path):
    return {(c["scale"], c["scene"]): c for c in json.load(gzip.open(path))["T1"]["cells"]
            if c["profile"] in DARK and c["tier"] == "webgpu"}


def main() -> None:
    exposure, point_a = cells(EXPOSURE), cells(POINT_A)
    rows = []
    for (scale, scene), c in sorted(exposure.items()):
        shape = scene.split("__")[1]
        if c["pose"] != "inactive" or shape not in FARS:
            continue
        n, d0219, b2d074, B = c["native"], c["reference"], c["candidate"], c["B"]
        a_b = 0.8 + 0.2 * FARS[shape]
        a = point_a.get((scale, scene))
        if a:
            anchor = (0.8, a["candidate"], "point A")
        elif shape == "rrect-lg":
            anchor = (0.89, d0219, "d0219")
        else:
            # b2d074 transmits here (alphaBase < 1) and the two generations' scatters differ, so a line through
            # d0219 at nearly the same alpha would read the scatter difference as a slope: T1 is taken as
            # proportional to the transmission 1 - alphaBase instead.
            anchor = (0.0, b2d074 / (1 - a_b), "proportional to 1 - alphaBase")
        slope = (anchor[1] - b2d074) / (anchor[0] - a_b)
        role = "repair" if scene in REPAIR else "flattered" if scene in FLATTERED else "other"
        per = {}
        for v in FAR:
            alpha = min(max(0.8 + v * FARS[shape], 0.0), 1.0)
            k = max(b2d074 + slope * (alpha - a_b), 0.0)
            per[str(v)] = dict(alphaBase=round(alpha, 4), t1=k,
                               growthVsD0219B=(abs(k - n) - abs(d0219 - n)) / B,
                               growthVsB2d074B=(abs(k - n) - abs(b2d074 - n)) / B)
        rows.append(dict(scale=scale, scene=scene, partition=c["partition"], role=role, native=n, d0219=d0219,
                         b2d074=b2d074, B=B, anchor=anchor[2], predicted=per))
    (HERE / "predict.json").write_text(json.dumps(dict(far=FAR, rows=rows), indent=1) + "\n")
    print("P2 predictions (first order; growth in B: vs d0219 for repair/flattered cells, vs b2d074 otherwise)")
    print(f"{'cell':52} {'part':8} {'role':9} " + " ".join(f"{v:>7}" for v in FAR))
    for r in rows:
        key = "growthVsB2d074B" if r["role"] == "other" else "growthVsD0219B"
        print(f"{r['scale']}x {r['scene']:49} {r['partition']:8} {r['role']:9} "
              + " ".join(f"{r['predicted'][str(v)][key]:+7.2f}" for v in FAR) + f"   ({r['anchor']})")
    print("\nDL2 per value and scale (predicted): repair (gate cell) <= B, flattered <= B, others <= B vs b2d074")
    for scale in (1, 2):
        for v in FAR:
            mine = [r for r in rows if r["scale"] == scale and r["partition"] == "gate"]
            fails = [f"{r['scene']} {r['predicted'][str(v)]['growthVsB2d074B' if r['role'] == 'other' else 'growthVsD0219B']:+.2f}B"
                     for r in mine
                     if r["predicted"][str(v)]["growthVsB2d074B" if r["role"] == "other" else "growthVsD0219B"] > 1]
            print(f"  {scale}x far {v:+.2f}: {'passes' if not fails else 'fails: ' + '; '.join(fails)}")


if __name__ == "__main__":
    main()
