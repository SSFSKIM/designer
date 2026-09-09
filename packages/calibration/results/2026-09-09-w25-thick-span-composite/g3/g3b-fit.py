"""W25 G3b — the JOINT fit of `rimLitExponent` and `rimAlongSideSlope` over a rendered grid.

WHAT THIS READS. `read-<rung>.json` for every rendered point of the (exponent, slope) plane, written
by `g3b-read.py`. Nothing else, and it writes tables on stdout.

WHY A GRID AND NOT A LEVER. Every other fit in this wave used a rendered lever — one rung, one
derivative — because one constant moved one quantity monotonically. These two do not: they multiply
the same rim amplitude, both peak on the same diagonal, and the exponent's factor is a POWER, so
the surface is not separable and a derivative at one point does not locate the minimum of the
other. Every point below is a render; no model of the rim stands between the objective and the
pixels.

THE TWO OBJECTIVES, AND THE ONE SCALE THEY SHARE.

  * **A, the angular error** — mean over rows of the mean over the sixteen bins of
    |web − native|, each row divided by its OWN brightest native bin. That per-row normalisation is
    W24's (`g0-findings.md` §8): without it a light row at 0.19 luma and a dark row at 0.024 would
    weigh eight to one and the fit would be the light bed's.
  * **R, the along-side range error** — mean over the straight sides of
    |range(web) − range(native)|, divided by the SAME per-row scale, so a fraction of A is a
    fraction of R and the weight between them is a pure number rather than a unit conversion.

  J(p, s) = A(p, s) + w · R(p, s)

`w` is set so that the two terms contribute EQUALLY at the 0.13.0 material (p = 1.15, s = 0), which
is a statement about the starting point and not about which reader matters more. The sensitivity of
the argmin to that choice is printed over w/2 … 3w/2 — the ±50 % the ruling asks for — and over the
two single-objective extremes beside it.

THE ROWS are `g3b-read.py`'s: the untinted flat-solid calibration and probe rows of the four
standard profiles, never the holdout. The check off them is `g3b-check.py`, on the checkerboard
cells.

ONE GUARD, and it is the same guard G0 gave reader C: **a row whose normalised angular error at the
0.13.0 material already exceeds 1 is not a rim-shape row and is refused**, with its name printed.
An error above 1 means vitrea's bins differ from the reference's by more than the reference's own
BRIGHTEST bin — the two are not drawing the same material there at all, and no exponent or slope
can be read off the difference. Measured, the refusals are four rows and both causes are on the
ledger already: `light-solid__rrect-sm` in the dark profiles (19.9), which is claims §5.115 §3's
size-keyed scheme adaptation — the reference renders the LIGHT appearance for a small surface over
a bright solid in the dark scheme and vitrea renders the dark material — and
`dark-solid__rrect-64` in the light profiles (3.6–3.9), where the reference has collapsed at span
64 (`g1/sweep-read.txt`) and vitrea has not. Both are body gaps wearing a rim reader's numbers, and
carrying them would have made this fit a fit of the collapse.

Usage:  g3b-fit.py --base p115s000 [--grid <dir>]
"""

import argparse
import json
import math
import os
import re
import sys

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3b"
COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def rung_params(tag):
    """`p115s045` -> (1.15, 0.45). The tag is the grid point and carries its own coordinates."""
    match = re.fullmatch(r"p(\d+)s(\d+)", tag)
    if not match:
        return None
    return float(match.group(1)) / 100.0, float(match.group(2)) / 100.0


def load(directory):
    out = {}
    for tag in sorted(os.listdir(directory)):
        params = rung_params(tag)
        path = os.path.join(directory, tag, f"read-{tag}.json")
        if params is None or not os.path.exists(path):
            continue
        out[tag] = (params, {r["profile"] + "/" + r["scene"]: r
                             for r in json.load(open(path))["rows"]})
    return out


def scale_of(row):
    """The row's own brightest native rim reading — the denominator both objectives share."""
    native = row["native"]
    best = 0.0
    for value in native.get("bins", []) or []:
        if value is not None and math.isfinite(value):
            best = max(best, abs(value))
    for side in (native.get("sides") or {}).values():
        best = max(best, abs(side["mean"]))
    return best if best > 1e-6 else None


def errors(rows):
    """Per row: (angular error, along-side range error, n bins, n sides), each normalised."""
    out = {}
    for key, row in rows.items():
        scale = scale_of(row)
        if scale is None:
            continue
        nat, web = row["native"], row["web"]
        angular, nbins = None, 0
        nb, wb = nat.get("bins"), web.get("bins")
        if isinstance(nb, list) and isinstance(wb, list):
            deltas = [abs(w - n) for n, w in zip(nb, wb)
                      if n is not None and w is not None
                      and math.isfinite(n) and math.isfinite(w)]
            if deltas:
                angular, nbins = sum(deltas) / len(deltas) / scale, len(deltas)
        ranges, nsides = None, 0
        deltas = []
        for side, value in (nat.get("sides") or {}).items():
            other = (web.get("sides") or {}).get(side)
            if other is None:
                continue
            deltas.append(abs(other["range"] - value["range"]))
        if deltas:
            ranges, nsides = sum(deltas) / len(deltas) / scale, len(deltas)
        out[key] = (angular, ranges, nbins, nsides)
    return out


def objective(rows, keep=None):
    per = errors(rows)
    if keep is not None:
        per = {k: v for k, v in per.items() if k in keep}
    a = [v[0] for v in per.values() if v[0] is not None]
    r = [v[1] for v in per.values() if v[1] is not None]
    return (sum(a) / len(a) if a else float("nan"),
            sum(r) / len(r) if r else float("nan"),
            len(a), len(r), sum(v[2] for v in per.values()), sum(v[3] for v in per.values()))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="p115s000")
    ap.add_argument("--grid", default=SCRATCH)
    args = ap.parse_args(argv)

    grid = load(args.grid)
    if args.base not in grid:
        raise SystemExit(f"the base rung {args.base} has not been read")

    # The guard, applied at the base and carried to every rung so the objective is the same rows
    # at every point of the plane.
    base_rows = errors(grid[args.base][1])
    keep, refused = set(), []
    for key, value in base_rows.items():
        if value[0] is not None and value[0] > 1.0:
            refused.append((key, value[0]))
        else:
            keep.add(key)

    table = {tag: (params, objective(rows, keep)) for tag, (params, rows) in grid.items()}
    base_a, base_r = table[args.base][1][0], table[args.base][1][1]
    weight = base_a / base_r if base_r else 1.0

    print("W25 G3b — the joint fit of rimLitExponent and rimAlongSideSlope, on a rendered grid")
    print("=" * 104)
    _a, _r, na, nr, nbins, nsides = table[args.base][1]
    print(f"rows: {na} carry an angular read ({nbins} bins), {nr} carry along-side sides "
          f"({nsides} sides)")
    print(f"the base rung is {args.base} = the 0.13.0 material (exponent 1.15, slope 0)")
    print(f"rows refused by the guard (base angular error above 1): {len(refused)}")
    for key, value in sorted(refused, key=lambda kv: -kv[1]):
        print(f"    {value:8.3f}  {key}")
    print(f"A(base) = {base_a:.5f}   R(base) = {base_r:.5f}   w = A/R = {weight:.4f}")
    print()
    print(f"{'rung':10} {'p':>5} {'s':>5} {'A angular':>10} {'R range':>10} {'J':>10} "
          f"{'ΔJ vs base':>11}")
    base_j = base_a + weight * base_r
    for tag, (params, values) in sorted(table.items(), key=lambda kv: kv[1][0]):
        a, r = values[0], values[1]
        j = a + weight * r
        print(f"{tag:10} {params[0]:5.2f} {params[1]:5.2f} {a:10.5f} {r:10.5f} {j:10.5f} "
              f"{j - base_j:+11.5f}")

    # W25 Decision Log 6's ACCEPTANCE CONDITION, which is not the objective: the thick solids'
    # angular error must be at or under the 0.13.0 bed's. J says which point the two readers jointly
    # prefer; this says whether that point is allowed to land, and the two can disagree.
    spans = {key: row["span"] for key, row in grid[args.base][1].items()}
    base_per = base_rows
    allowed = set()
    print()
    print("the ruling's acceptance condition — the THICK solids (span >= 96) against the 0.13.0 bed")
    print(f"{'rung':10} {'p':>5} {'s':>5} {'thick A':>9} {'thick R':>9} {'rows +':>7} "
          f"{'rows −':>7} {'verdict':>9}")
    for tag, (params, _values) in sorted(grid.items(), key=lambda kv: kv[1][0]):
        per = errors(grid[tag][1])
        up = down = 0
        angular, ranges = [], []
        for key in keep:
            if spans.get(key, 0.0) < 96.0:
                continue
            value, base_value = per.get(key), base_per.get(key)
            if value is None or base_value is None or value[0] is None or base_value[0] is None:
                continue
            angular.append(value[0])
            if value[1] is not None:
                ranges.append(value[1])
            if value[0] < base_value[0]:
                up += 1
            elif value[0] > base_value[0]:
                down += 1
        if not angular:
            continue
        a = sum(angular) / len(angular)
        r = (sum(ranges) / len(ranges)) if ranges else float("nan")
        if tag == args.base:
            verdict = "the bed"
        else:
            verdict = "allowed" if up > down else "REFUSED"
            if verdict == "allowed":
                allowed.add(tag)
        print(f"{tag:10} {params[0]:5.2f} {params[1]:5.2f} {a:9.5f} {r:9.5f} {up:7d} {down:7d} "
              f"{verdict:>9}")

    print()
    print("the minimum, and its sensitivity to the weighting (the ruling asks for ±50 %)")
    print("  `whole grid` is where the two readers jointly point; `allowed only` is where they")
    print("  point among the pairs the acceptance condition lets land, and that is the landing.")
    print(f"{'weight':>12} {'w/w0':>7} {'whole grid':>12} {'p':>5} {'s':>5} {'J':>10}   "
          f"{'allowed only':>12} {'p':>5} {'s':>5} {'J':>10}")
    for factor in (0.0, 0.5, 0.75, 1.0, 1.25, 1.5, 1e6):
        w = weight * factor
        key = lambda kv: kv[1][1][0] + w * kv[1][1][1]  # noqa: E731
        best = min(table.items(), key=key)
        pool = {tag: value for tag, value in table.items() if tag in allowed}
        pick = min(pool.items(), key=key) if pool else None
        label = "angular only" if factor == 0.0 else ("range only" if factor > 1e5 else "")
        line = (f"{w:12.4f} {factor:7.2f} {best[0]:>12} {best[1][0][0]:5.2f} "
                f"{best[1][0][1]:5.2f} {key(best):10.5f}   ")
        line += (f"{pick[0]:>12} {pick[1][0][0]:5.2f} {pick[1][0][1]:5.2f} {key(pick):10.5f}"
                 if pick else f"{'—':>12}")
        print(line + f"  {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
