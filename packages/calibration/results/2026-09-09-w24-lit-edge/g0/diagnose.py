"""W24 G0 (a) — the angular instrument's geometry diagnostic, over every read it wrote.

Three ways this reader can be reading something that is not the rim, and one number each per cell:

- **TRUNCATED** — the fraction of a bin's samples whose peak sat at the far end of the search
  window. The window is 4 CSS px inside the declared contour; a peak that has run to the end has
  not been bounded and the bin is a lower limit, not a reading.
- **OUTSIDE** — the fraction whose peak sat outside the declared contour. The window reaches 1 CSS
  px out so that a rim drawn a fraction of a pixel proud of the declared edge is still caught; over
  a backdrop brighter than the body that same reach reads the BACKDROP, and the bin is then a
  reading of the scene and not of the material.
- **CLIP** — the fraction whose peak pixel is white in all three channels. A clipped reference bin
  cannot say how much brighter it wanted to be.

Beside them the samples per bin (the fit's weight) and the mean depth at which the peak was found,
which is where the reader says the rim actually is.

Usage: diagnose.py <reads-dir>
"""

import json
import os
import sys

import numpy as np

COMPASS = ("N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW")


def main() -> int:
    reads = sys.argv[1]
    for fname in sorted(os.listdir(reads)):
        if not fname.endswith(".json") or fname.startswith("contour-"):
            continue
        d = json.load(open(os.path.join(reads, fname)))
        if d.get("tier") == "css":
            continue
        print(f"\n===== {fname}")
        worst = {"truncated": 0.0, "outside": 0.0, "clip": 0.0}
        for r in d["rows"]:
            for tag in ("native", "web"):
                if tag not in r:
                    continue
                v = r[tag]
                trunc = np.asarray([0.0 if x is None else x for x in v["truncatedFraction"]])
                out = np.asarray([0.0 if x is None else x for x in v["outsideFraction"]])
                clip = np.asarray([0.0 if x is None else x for x in v["clipFraction"]])
                flags = []
                for k in range(len(COMPASS)):
                    marks = []
                    if trunc[k] > 0.05:
                        marks.append(f"trunc {trunc[k]:.2f}")
                    if out[k] > 0.20:
                        marks.append(f"outside {out[k]:.2f}")
                    if clip[k] > 0.02:
                        marks.append(f"clip {clip[k]:.2f}")
                    if marks:
                        flags.append(f"{COMPASS[k]}({'; '.join(marks)})")
                worst["truncated"] = max(worst["truncated"], float(trunc.max()))
                worst["outside"] = max(worst["outside"], float(out.max()))
                worst["clip"] = max(worst["clip"], float(clip.max()))
                print(f"  {r['scene']:42s} {tag:6s} points {v['points']:5d}  "
                      f"min/max samples per bin {min(v['counts']):5d}/{max(v['counts']):5d}  "
                      f"mean peak depth {v['meanPeakDepthCssPx']:+.2f} CSS px"
                      + ("  " + " ".join(flags) if flags else ""))
        print(f"  -- worst over this bed: truncated {worst['truncated']:.2f}, "
              f"outside {worst['outside']:.2f}, clip {worst['clip']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
