"""W18 G0 (d) — the closed forms against the measurement, per cell.

The shadow term's prediction is `closed-form.ts`'s; the measurement it is held to is the CSS tier's
own captures, default minus `no-outer-shadow`, over the SAME per-surface mask the prediction is
averaged on. Both are differences, so the affine's constants, the encode's offset and the reader's
mask all cancel out of the comparison, and what is left is the model of the mechanism.

The ramp's area mean is reported beside it: what `optics.ts` carries for that surface (the extents,
no corners) against the exact co-area value over the rounded rectangle on the device grid.

Usage: `python closed-form-table.py <partsDir>`.
"""

import json
import sys
from pathlib import Path


def main() -> None:
    parts = Path(sys.argv[1])
    forms = json.loads((parts / "closed-form.json").read_text())
    for dpr in (1, 2):
        default = {r["scene"]: r for r in json.loads((parts / f"separation-{dpr}x.json").read_text())
                   if "skipped" not in r}
        declined = {}
        for name in ("attr-no-outer-shadow", "stack-no-outer-shadow"):
            path = parts / f"{name}-{dpr}x.json"
            if not path.exists():
                continue
            for row in json.loads(path.read_text()):
                if "skipped" not in row:
                    declined[row["scene"]] = row
        print(f"=== dpr {dpr}: the shadow the tier samples through its own backdrop ===")
        print(f"{'scene':40s} {'surf':>4s} {'box':>10s} {'predicted':>10s} {'measured':>10s} "
              f"{'residual':>9s} {'rampOptics':>11s} {'rampExact':>10s} {'rampErr':>9s}")
        worst = (0.0, "")
        for form in forms:
            if form["dpr"] != dpr:
                continue
            scene, index = form["scene"], form["surface"]
            if scene not in declined:
                continue
            a = default[scene]["surfaces"][index]["declared"]["css"]
            b = declined[scene]["surfaces"][index]["declared"]["css"]
            measured = a - b
            predicted = form["shadowTermPredicted"]
            residual = predicted - measured
            ramp = form["rampAreaMean"]
            box = f"{form['box'][0]}x{form['box'][1]}"
            print(f"{scene:40s} {index:4d} {box:>10s} {predicted:+10.4f} {measured:+10.4f} "
                  f"{residual:+9.4f} {ramp['opticsCarries']:11.4f} {ramp['exactOverTheBox']:10.4f} "
                  f"{ramp['difference']:+9.4f}")
            if abs(residual) > abs(worst[0]):
                worst = (residual, f"{scene} surface {index}")
        print(f"largest residual {worst[0]:+.4f} on {worst[1]}\n")


if __name__ == "__main__":
    main()
