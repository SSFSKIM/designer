"""W26 G1 — is `sizeHeavyTapSigma` = 13.418 at 1x the width the chain already draws?

The question matters because `heavyTapSigmaAtScale` interpolates LINEARLY between the two anchors
(`rampAtScale`), so a 2x anchor with a 1x anchor of 0 would make the heavy blur vanish at dpr 1 and
be nearly absent at dpr 1.1 — a discontinuity in the material at fractional ratios that nothing
measured. Naming the 1x anchor at `CHAIN_LEVEL_SIGMA[4]` = 13.418 device px instead asks the
mechanism to draw at 1x what the pyramid's clamped tap already draws there, which would keep the
ramp continuous at no cost in pixels AND make the 1x width a stated quantity rather than a property
of the backdrop raster's size (the tracker entry W26 G0 opened).

"At no cost in pixels" is a claim about captures, so this file reads them: every ladder row of the
1x light profile, `r0` against `c1`, as an OKLab dE mean out of each rung's own scratch matrix and
as a raw per-pixel maximum out of the captures themselves.

    g1-inert1x.py [--scratch DIR] [--base r0] [--rung c1]
"""

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w26lib  # noqa: E402,F401  (puts W25 G0's reader library on the path, X1)

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1"


def cells_of(rung, scratch):
    path = os.path.join(scratch, rung, "rung.json")
    if not os.path.exists(path):
        return {}
    out = {}
    for cell in json.load(open(path))["cells"]:
        if cell["tier"] != "texture":
            continue
        entry = (cell.get("perceptual") or {}).get("oklabDeltaEMean")
        value = entry.get("value") if isinstance(entry, dict) else entry
        if value is not None:
            out[(cell["key"]["profileKey"], cell["key"]["sceneId"])] = float(value)
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default=SCRATCH)
    ap.add_argument("--base", default="r0")
    ap.add_argument("--rung", default="c1")
    ap.add_argument("--out", default=os.path.join(HERE, "inert-1x.txt"))
    args = ap.parse_args(argv)

    base, rung = cells_of(args.base, args.scratch), cells_of(args.rung, args.scratch)
    out = [f"W26 G1 — `{args.rung}` against `{args.base}`: what naming the chain's own 1x width costs",
           "=" * 100, ""]
    for pkey in ("apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard"):
        out.append(f"{pkey}")
        out.append(f"  {'scene':>44} {'dE base':>9} {'dE rung':>9} {'move':>9} {'max code':>9}")
        rows = sorted(s for (p, s) in rung if p == pkey)
        worst = 0.0
        for sid in rows:
            b = base.get((pkey, sid))
            r = rung.get((pkey, sid))
            if b is None or r is None:
                continue
            a_png = os.path.join(args.scratch, args.base, "web-captures", pkey, sid,
                                 f"{sid}__webgpu.png")
            b_png = os.path.join(args.scratch, args.rung, "web-captures", pkey, sid,
                                 f"{sid}__webgpu.png")
            code = float("nan")
            if os.path.exists(a_png) and os.path.exists(b_png):
                ia = np.asarray(Image.open(a_png).convert("RGB"), dtype=np.int16)
                ib = np.asarray(Image.open(b_png).convert("RGB"), dtype=np.int16)
                if ia.shape == ib.shape:
                    code = float(np.abs(ia - ib).max())
            worst = max(worst, abs(r - b))
            out.append(f"  {sid:>44} {b:9.5f} {r:9.5f} {abs(r - b):9.5f} {code:9.0f}")
        out.append(f"  worst OKLab dE move on this profile: {worst:.5f}")
        out.append("")
    text = "\n".join(out)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
