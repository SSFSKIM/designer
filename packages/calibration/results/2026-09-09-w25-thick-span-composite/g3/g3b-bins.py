"""W25 G3b — the per-bin table the ruling asks for, on one cell, at named materials.

The sixteen compass bins of W24's angular reader on a named row, printed as reference | material |
material | … with each material's error beside it. One cell at a time, because the point of the
table is to be read rather than summed: it is where the confound between `rimLitExponent` and
`rimAlongSideSlope` is visible — both peak at NW and SE, the null is at NE and SW, and the straight
sides are N, E, S and W where the exponent's factor is exactly 1.

    g3b-bins.py --profile 1x-light --scene dark-solid__rrect-md__rest p115s000 p045s030 …
"""

import argparse
import json
import math
import os
import sys

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3b"
COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def bins_of(rung, profile, scene, scratch):
    path = os.path.join(scratch, rung, f"read-{rung}.json")
    for row in json.load(open(path))["rows"]:
        if row["profile"] == profile and row["scene"] == scene:
            return row["native"].get("bins"), row["web"].get("bins")
    return None, None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("rungs", nargs="+")
    ap.add_argument("--profile", default="1x-light")
    ap.add_argument("--scene", default="dark-solid__rrect-md__rest")
    ap.add_argument("--scratch", default=SCRATCH)
    args = ap.parse_args(argv)

    native = None
    columns = []
    for rung in args.rungs:
        nat, web = bins_of(rung, args.profile, args.scene, args.scratch)
        if web is None:
            print(f"  {rung}: not read", file=sys.stderr)
            continue
        native = nat
        columns.append((rung, web))
    if native is None:
        raise SystemExit("no rung carries this row")

    scale = max(abs(v) for v in native if v is not None and math.isfinite(v))
    print(f"W25 G3b — the angular bins on {args.profile} / {args.scene}")
    print(f"normaliser: the reference's brightest bin, {scale:.5f} linear luma")
    print()
    header = f"{'bin':5} {'reference':>10}"
    for rung, _ in columns:
        header += f" {rung:>10} {'error':>8}"
    print(header)
    for index, name in enumerate(COMPASS):
        ref = native[index]
        line = f"{name:5} {ref:10.5f}"
        for _rung, web in columns:
            line += f" {web[index]:10.5f} {abs(web[index] - ref):8.5f}"
        print(line)
    line = f"{'mean':5} {'':>10}"
    for _rung, web in columns:
        errs = [abs(w - n) for n, w in zip(native, web)]
        line += f" {'':>10} {sum(errs) / len(errs):8.5f}"
    print(line)
    line = f"{'norm':5} {'':>10}"
    for _rung, web in columns:
        errs = [abs(w - n) for n, w in zip(native, web)]
        line += f" {'':>10} {sum(errs) / len(errs) / scale:8.5f}"
    print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
