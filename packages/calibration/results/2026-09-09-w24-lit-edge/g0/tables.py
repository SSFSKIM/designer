"""W24 G0 (b) — the read reduced to the findings' tables.

One line per cell per tier: the brightest bin's direction and value, the dimmest as a fraction of
it, and the brightest/dimmest ratio, native against web. The full sixteen bins are in
`angular-read.txt`; this is what the tables in `g0-findings.md` are cut from.

Usage: tables.py <reads-dir> [--tier webgpu|dom] [--solid]
"""

import json
import os
import sys

import numpy as np

COMPASS = ("N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW")
SOLID = ("dark-solid", "mid-dark-solid", "light-solid")


def main() -> int:
    reads = sys.argv[1]
    tier = "css" if "--tier=css" in sys.argv else "webgpu"
    solid_only = "--solid" in sys.argv
    for fname in sorted(os.listdir(reads)):
        if not fname.endswith(".json") or fname.startswith("contour-"):
            continue
        d = json.load(open(os.path.join(reads, fname)))
        if d.get("tier") not in (None, tier):
            continue
        print(f"\n== {d['profile']} / {d.get('tier') or 'native only'}")
        print(f"{'scene':44s} {'set':11s} | {'bright':>6s} {'peak':>8s} {'floor':>6s} "
              f"{'ratio':>7s} | {'bright':>6s} {'peak':>8s} {'floor':>6s} {'ratio':>7s}")
        for r in d["rows"]:
            if solid_only and r["background"] not in SOLID:
                continue
            cells = []
            for tag in ("native", "web"):
                if tag not in r:
                    cells.append(f"{'-':>6s} {'-':>8s} {'-':>6s} {'-':>7s}")
                    continue
                b = np.asarray([np.nan if v is None else v for v in r[tag]["bins"]])
                hi, lo = float(np.nanmax(b)), float(np.nanmin(b))
                ratio = hi / lo if lo > 1e-6 else float("inf")
                cells.append(f"{COMPASS[int(np.nanargmax(b))]:>6s} {hi:8.4f} "
                             f"{lo / hi if abs(hi) > 1e-9 else float('nan'):6.3f} "
                             + ("    inf" if not np.isfinite(ratio) else f"{ratio:7.2f}"))
            tint = f" +{r['tint']}" if r.get("tint") else ""
            print(f"{(r['scene'] + tint)[:44]:44s} {r['set']:11s} | {cells[0]} | {cells[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
