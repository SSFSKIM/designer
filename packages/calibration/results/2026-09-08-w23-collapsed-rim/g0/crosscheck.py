"""W23 G0 (a) (iii) — this reader against the parent's, on the cells the parent read.

`finding/contour-table.txt` is the grounding read (claims §5.99). Its reader averaged the top
edge's rows over a fixed 20-CSS-px window at the cell's horizontal centre; this one averages over
the straight span with the continuous corner excluded, and subtracts the eroded body rather than
the row two px in. The two must agree wherever the backdrop is solid and the row is flat, and the
places they do NOT agree are the places the window happened to sit on structure — which is the
whole reason this reader reads a span.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "..", "finding", "contour-table.txt")
BED = {
    "apple-macos-26.5-1x-light-standard": "canonical-apple-macos-26.5-1x-light-standard-webgpu.json",
    "apple-macos-26.5-2x-light-standard": "canonical-apple-macos-26.5-2x-light-standard-webgpu.json",
    "apple-macos-26.5-1x-dark-standard": "canonical-apple-macos-26.5-1x-dark-standard-webgpu.json",
    "apple-macos-26.5-2x-dark-standard": "canonical-apple-macos-26.5-2x-dark-standard-webgpu.json",
}


def main():
    reads = {}
    for profile, name in BED.items():
        data = json.load(open(os.path.join(HERE, "reads", name)))
        reads[profile] = {r["scene"]: r for r in data["rows"]}

    print("`rim nat` / `rim web` are the parent's numbers; `top` is this reader's TOP side.")
    print("`d` is this reader minus the parent's. One 8-bit code is 0.0059 of linear luminance at")
    print("a body of 0.48 and 0.0007 at a body of 0.011, so the dark bed's agreement is tighter in")
    print("codes than it looks in luminance.")
    print()
    print(f"{'profile':36s} {'scene':38s} {'natP':>8s} {'natT':>8s} {'d':>8s} "
          f"{'webP':>8s} {'webT':>8s} {'d':>8s}")
    worst = (0.0, "")
    for line in open(TABLE):
        parts = line.split()
        if len(parts) < 7 or not parts[0].startswith("apple-macos"):
            continue
        profile, scene = parts[0], parts[1]
        nat_p, web_p = float(parts[4]), float(parts[5])
        row = reads.get(profile, {}).get(scene)
        if row is None:
            print(f"{profile:36s} {scene:38s} {'(not read by this gate)':>40s}")
            continue
        nat_t = row["rimNative"][0]
        web_t = row["rimWeb"][0] if "rimWeb" in row else float("nan")
        d_nat = nat_t - nat_p
        d_web = web_t - web_p
        if abs(d_nat) > abs(worst[0]):
            worst = (d_nat, f"{profile} {scene}")
        print(f"{profile:36s} {scene:38s} {nat_p:8.4f} {nat_t:8.4f} {d_nat:+8.4f} "
              f"{web_p:8.4f} {web_t:8.4f} {d_web:+8.4f}")
    print()
    print(f"the largest disagreement on the native side: {worst[0]:+.4f} ({worst[1]})")
    print()
    print("Where the two agree to a thousandth the backdrop under the parent's centre window was")
    print("the same as under the whole span. Where they do not, the span read is the one to")
    print("believe: the centre window is 20 CSS px of a 120–224 px edge and inherits whatever")
    print("structure sits under it, and on `photo` and `checkerboard` that is most of the")
    print("difference between a rim and a backdrop feature.")


if __name__ == "__main__":
    main()
