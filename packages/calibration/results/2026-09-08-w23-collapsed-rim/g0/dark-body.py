"""W23 G0 (e) — the dark thick body over `dark-solid`, read beside the rim, and its constant named.

The wave's Deferred list carries it: `dark-solid__rrect-md__rest` in the dark scheme draws a body of
0.0130 linear against the reference's 0.0153 — three 8-bit codes at that level — and W21 clause 1
was met at a tolerance of 0.010, so nothing has ever had to move it. The question G0 was asked is
whether ONE constant on the dark law separates it, or whether it is carried with its number.

The reading is the whole dark bed's body, native against landed, so that a constant proposed for one
cell is immediately visible on the others: a scalar on the dark tint moves every dark body at once,
and what matters is the sign of that move everywhere else.
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BEDS = ("apple-macos-26.5-1x-dark-standard", "apple-macos-26.5-2x-dark-standard")


def main():
    print("W23 G0 (e) — the dark bed's body, native against the landed GPU capture")
    print()
    print("linear Rec.709 luminance over the declared box eroded 6 CSS px (W21's body). `codes` is")
    print("the difference expressed in 8-bit codes at that level, which is the only honest unit for")
    print("a difference of two thousandths on a near-black surface.")
    print()
    for profile in BEDS:
        data = json.load(open(os.path.join(HERE, "reads", f"canonical-{profile}-webgpu.json")))
        print(f"== {profile}")
        print(f"{'scene':44s} {'set':6s} {'bodyN':>8s} {'bodyW':>8s} {'d':>9s} {'codes':>7s}")
        for row in data["rows"]:
            if "bodyWeb" not in row:
                continue
            n, w = row["bodyNative"], row["bodyWeb"]
            # one code at this level, from the sRGB curve
            e = n ** (1 / 2.4) if n > 0.0031308 else n
            enc = 1.055 * max(n, 0.0) ** (1 / 2.4) - 0.055 if n > 0.0031308 else n * 12.92
            code = enc * 255.0
            hi = ((min(code + 0.5, 255.0) / 255.0 + 0.055) / 1.055) ** 2.4
            lo = max((max(code - 0.5, 0.0) / 255.0 + 0.055) / 1.055, 0.0) ** 2.4
            step = hi - lo if hi > lo else 1e-6
            tint = " (tinted)" if row.get("tint") else ""
            print(f"{row['scene'] + tint:44s} {row['set'][:6]:6s} {n:8.5f} {w:8.5f} "
                  f"{w - n:+9.5f} {(w - n) / step:7.2f}")
        print()


if __name__ == "__main__":
    main()
