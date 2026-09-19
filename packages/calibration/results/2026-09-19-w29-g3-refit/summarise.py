#!/usr/bin/env python3
"""W29 G3 — one candidate's residual, per law, in the quantity the law is stated in.

    python3 summarise.py <label> [profile] [renderer] [--pose rest|inactive]

The fit loop's readout. Each law of Decision Log 4 (a) has a reading in
`cli/measure.ts`'s material axis and this prints the web-minus-native residual of
that reading — the level as `interiorMean`, the rim as its radial peak and its
FWHM, the diffusion as the interior's spread and the luminance transfer's slope
PER BACKDROP (the law is conditioned on the backdrop's spatial scale, so a
bed-wide mean is the one statistic that cannot show it), and the tint's lightness
as `tintDeltaL`. `oklabDeltaEMean` and `ssimMean` come last as checks rather than
terms, on the same doctrine `scripts/sweep.ts` states for them.
"""
from __future__ import annotations

import collections
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit  # noqa: E402

LAWS = [
    ("level        interiorMean", "interiorMeanNative", "interiorMeanWeb"),
    ("rim          peak", "rimPeakNative", "rimPeakWeb"),
    ("rim          fwhm px", "rimFwhmNative", "rimFwhmWeb"),
    ("diffusion    interiorStdDev", "interiorStdDevNative", "interiorStdDevWeb"),
    ("diffusion    transfer slope", "slopeNative", "slopeWeb"),
    ("tint         deltaL", "tintDeltaLNative", "tintDeltaLWeb"),
]


def stats(rows: list[dict], native: str, web: str) -> str:
    pairs = [(r[web] - r[native]) for r in rows if r[native] is not None and r[web] is not None]
    if not pairs:
        return "no cell carries it"
    return (
        f"n={len(pairs):<4} mean {statistics.mean(pairs):+.4f}"
        f"  median {statistics.median(pairs):+.4f}"
        f"  mean|Δ| {statistics.mean(map(abs, pairs)):.4f}"
        f"  worst {max(pairs, key=abs):+.4f}"
    )


def main() -> int:
    label = sys.argv[1]
    pose = "rest"
    if "--pose" in sys.argv:
        pose = sys.argv[sys.argv.index("--pose") + 1]
    run = fit.SCRATCH / "fit-log" / label
    rows: list[dict] = []
    for matrix in sorted(run.glob("*.json")):
        rows += fit.readings(matrix)
    rows = [r for r in rows if r["state"] == pose]
    untinted = [r for r in rows if "tint" not in r["scene"]]
    tinted = [r for r in rows if "tint" in r["scene"]]

    print(f"{label} / pose {pose}: {len(rows)} cells ({len(tinted)} tinted)")
    for name, native, web in LAWS:
        pool = tinted if name.startswith("tint") else untinted
        print(f"  {name:<28} {stats(pool, native, web)}")

    print("  diffusion by backdrop (interiorStdDev, web − native):")
    by = collections.defaultdict(list)
    for r in untinted:
        if r["interiorStdDevNative"] is not None and r["interiorStdDevWeb"] is not None:
            by[r["backdrop"]].append(r["interiorStdDevWeb"] - r["interiorStdDevNative"])
    for key in sorted(by, key=lambda k: fit.BACKDROP_ENCODED_MEAN.get(k, 0)):
        print(f"    {key:<20} {statistics.mean(by[key]):+.4f}  (n={len(by[key])})")

    for check in ("deMean", "deP95", "ssim"):
        values = [r[check] for r in rows if r[check] is not None]
        if values:
            print(f"  check {check:<10} mean {statistics.mean(values):.5f}  "
                  f"worst {max(values) if check != 'ssim' else min(values):.5f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
