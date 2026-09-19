#!/usr/bin/env python3
"""W29 G1c Part B — the six things the gate's independent review asked for (2026-09-19).

Run from `packages/calibration`:

    python3 results/2026-09-19-w29-g1c-coupled/review-closure.py

Every figure the closure writes into claims §5.152 §B, §5.151 §12 and the charter's
Decision Logs 4 (c) and 5 is computed here from the committed rows, and none is copied from
the review. Two of the six are corrections to numbers this child already recorded, so the
rule is the repository's: the first reading stays and the corrected one is printed beside it.

The six, in the review's numbering:

 1. The SSIM-outside allowance for increased contrast. `read-checks.py` §8 transcribed it as
    ≤ 0.20 from Decision Log 4 (c)'s column, which had itself been transcribed. The row in
    `test/adopted-thresholds.test.ts` is `ssimOutside ≥ 0.69`, so the allowance is ≤ 0.31 and
    the coupled profile's worst cell has headroom rather than a risk.
 2. Whether "inside every material row at its worst cell" is unique to this profile. It is
    not: with the allowances read from the file, `1x-light-reduced-transparency` is inside
    every one of them too.
 3. The allowance audit. Done in G2's closure (`../2026-09-19-w29-g2-native-delta/`, item 11)
    because the dictionary that failed is that child's; both closures now read the tables
    through the one `adopted_allowances` module and neither transcribes.
 4. The tone response, conditioned on its own fit quality. `transferR2` says the linear
    transfer barely explains anything on a near-opaque panel, and `transferOffset` and
    `bodyLevel` are one reading and not two.
 5. The median convention. `native-delta.ts`'s `tables` takes the upper-middle order
    statistic on an even count; `read-checks.py` averages the two middles. Both figures in
    the record are right under their own convention; neither moves, and the convention is
    now named where each is read.
 6. The attested field's name, as the manifest writes it.
"""
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(os.path.dirname(HERE))
G2 = os.path.join(PKG, "results", "2026-09-19-w29-g2-native-delta")
REFERENCE = os.path.join(os.path.dirname(os.path.dirname(PKG)), "apps", "reference-apple")

sys.path.insert(0, G2)
from adopted_allowances import read_allowances  # noqa: E402  (after G2 is known)

COUPLED = "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5"
DECOUPLED = "apple-macos-27.0-1x-light-increased-contrast-glass0.5"

rows = json.load(open(os.path.join(HERE, "delta", "native-delta.json")))["rows"]
g2rows = json.load(open(os.path.join(G2, "native-delta.json")))["rows"]
manifest = json.load(open(os.path.join(REFERENCE, "fixtures", "manifest.json")))

TABLES, TABLE_NAMES = read_allowances()

out = []


def say(line=""):
    out.append(line)


def med_upper(values):
    """`native-delta.ts`'s `median`: the upper middle element of an even count."""
    values = sorted(v for v in values if v is not None)
    return values[len(values) // 2] if values else float("nan")


def med_mean(values):
    """`read-checks.py`'s median: `statistics.median`, which averages the two middles."""
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else float("nan")


def quantile(values, q):
    """`read-checks.py` §8's quantile, kept so a row here lands on that row's number."""
    values = sorted(v for v in values if v is not None)
    if not values:
        return float("nan")
    return values[min(len(values) - 1, max(0, int(round(q * (len(values) - 1)))))]


def healthy(row):
    """§5.151 §4's conditioning: the two silhouettes within 2× of each other."""
    pair = row["readings"].get("silhouetteAreaPx") or [None, None]
    if pair[0] in (None, 0) or pair[1] in (None, 0):
        return False
    return not (pair[0] / pair[1] < 0.5 or pair[1] / pair[0] < 0.5)


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    spread = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return cov / spread


SHAPE = ["silhouetteIoUComplement", "contourDistanceMeanPx", "contourDistanceP95Px"]
MATERIAL = ["ssimComplement", "oklabDeltaEMean", "oklabDeltaEP95", "edgeWeightedMean",
            "ssimOutsideComplement"]
FIRST_READ = {  # read-checks.py §8's transcribed column, kept so the correction reads beside it
    "silhouetteIoUComplement": 0.15, "contourDistanceMeanPx": 1.8, "contourDistanceP95Px": 11.5,
    "ssimComplement": 0.14, "oklabDeltaEMean": 0.06, "oklabDeltaEP95": 0.10,
    "edgeWeightedMean": 0.17, "ssimOutsideComplement": 0.20,
}

say("# W29 G1c Part B — the review closure's recomputations (2026-09-19)")
say()
say("Medians are named at every use: 'upper' is the instrument's (native-delta.ts) and 'mean' is")
say("read-checks.py's. Quantiles are read-checks.py §8's, so a row here lands on that row's number.")
say()

# ---------------------------------------------------------------------------
say("# 1. The allowance the coupled profile is read against, from the test file")
say()
say("Allowances are parsed from test/adopted-thresholds.test.ts through the shared")
say("adopted_allowances module, never transcribed. The three shape rows are over the healthy")
say("cells, the five material rows over all 32 pairs, and the median is read-checks.py's — all")
say("three exactly as §8 reads them, so only the allowance column moves against what it printed.")
say()
allow = TABLES["1x-light-increased-contrast"]["texture"]
dom = TABLES["1x-light-increased-contrast"]["dom"]
say(f"  table: {TABLE_NAMES['1x-light-increased-contrast']['texture']} "
    f"(texture), {TABLE_NAMES['1x-light-increased-contrast']['dom']} (dom)")
say()
say(f"  {'metric':26s} {'n':>4s} {'median':>10s} {'p90':>10s} {'max':>10s} {'allowance':>10s} "
    f"{'first read':>11s} {'dom':>8s}  verdict")
fit = [r for r in rows if healthy(r)]
for metric in SHAPE + MATERIAL:
    pool = fit if metric in SHAPE else rows
    values = [r["metrics"].get(metric) for r in pool if r["metrics"].get(metric) is not None]
    worst, bound = max(values), allow[metric]
    verdict = "MAX OVER" if worst > bound else ("p90 over" if quantile(values, 0.9) > bound else "inside")
    was = FIRST_READ[metric]
    say(f"  {metric:26s} {len(values):>4d} {med_mean(values):>10.4g} "
        f"{quantile(values, 0.9):>10.4g} {worst:>10.4g} {bound:>10.4g} "
        f"{('same' if abs(was - bound) < 1e-12 else f'{was:.4g}'):>11s} "
        f"{dom.get(metric, float('nan')):>8.4g}  {verdict}")
say()
say("The one row that moves is ssimOutsideComplement: the first read had ≤ 0.20 and called the")
say("0.2369 worst cell a named risk; the file's row is ssimOutside ≥ 0.69, so the allowance is")
say("≤ 0.31 and that cell sits at %.3f of it." % (max(
    r["metrics"]["ssimOutsideComplement"] for r in rows
    if r["metrics"].get("ssimOutsideComplement") is not None) / allow["ssimOutsideComplement"]))
say()

# ---------------------------------------------------------------------------
say("# 2. Is 'inside every material row at its worst cell' unique to this profile?")
say()
say("Every profile's five material rows at their worst cell, against that profile's own parsed")
say("texture allowance. The shape rows are excluded, as they are everywhere in this wave: they")
say("are the extractor reading a level and are over on every profile.")
say()
beds = {"1x-light-increased-contrast-coupled": rows}
for r in g2rows:
    beds.setdefault(r["profileKey27"].replace("apple-macos-27.0-", "").replace("-glass0.5", ""),
                    []).append(r)
for name in sorted(beds):
    table = TABLES["1x-light-increased-contrast" if "increased-contrast" in name else name]["texture"]
    over = []
    for metric in MATERIAL:
        values = [r["metrics"].get(metric) for r in beds[name]
                  if r["metrics"].get(metric) is not None]
        if values and max(values) > table[metric]:
            over.append(f"{metric} {max(values):.4g} > {table[metric]:.4g}")
    say(f"  {name:44s} n={len(beds[name]):4d}  "
        f"{'INSIDE EVERY MATERIAL ROW' if not over else 'over: ' + '; '.join(over)}")
say()
say("Two profiles are inside all five, and the second one is only inside since the allowance was")
say("corrected: reduced transparency's ssimOutside row is ≥ 0.84 in the file (≤ 0.16), not the")
say("≤ 0.07 the transcription had, and its worst cell is 0.0926.")
say()

# ---------------------------------------------------------------------------
say("# 3. The allowance audit")
say()
say("In G2's closure, item 11 — the dictionary that failed is that child's, and both closures now")
say("read through adopted_allowances. Four of its forty-eight texture rows differed from the file:")
say("2x-light-standard ssimMean (≤ 0.07, not ≤ 0.11) and ssimOutside (≤ 0.13, not ≤ 0.14),")
say("1x-light-reduced-transparency ssimOutside (≤ 0.16, not ≤ 0.07), 1x-light-increased-contrast")
say("ssimOutside (≤ 0.31, not ≤ 0.20).")
say()

# ---------------------------------------------------------------------------
say("# 4. The tone response, conditioned on its own fit")
say()
r2 = [(r["readings"]["transferR2"][0], r["readings"]["transferR2"][1]) for r in rows
      if r["readings"].get("transferR2")]
say(f"  transferR2 over {len(r2)} cells that carry a transfer:")
say(f"    26.5  median {med_mean([a for a, _ in r2]):.4f} (mean) "
    f"{med_upper([a for a, _ in r2]):.4f} (upper)   max {max(a for a, _ in r2):.4f}   "
    f"below 0.1: {sum(1 for a, _ in r2 if a < 0.1)} of {len(r2)}")
say(f"    27    median {med_mean([b for _, b in r2]):.4f} (mean) "
    f"{med_upper([b for _, b in r2]):.4f} (upper)   max {max(b for _, b in r2):.4f}   "
    f"below 0.1: {sum(1 for _, b in r2 if b < 0.1)} of {len(r2)}")
say()
say("  A slope and an offset fitted through a cloud with no slope in it are a reading of the")
say("  body's own level. The offset says so directly:")
both = [r for r in rows if r["readings"].get("transferOffset") and r["readings"].get("bodyLevel")]
for index, label in ((0, "26.5"), (1, "27")):
    offsets = [r["readings"]["transferOffset"][index] for r in both]
    levels = [r["readings"]["bodyLevel"][index] for r in both]
    say(f"    transferOffset against bodyLevel, {label:4s}  n={len(both)}  "
        f"r = {pearson(offsets, levels):.4f}")
pooled_o = [r["readings"]["transferOffset"][i] for r in both for i in (0, 1)]
pooled_l = [r["readings"]["bodyLevel"][i] for r in both for i in (0, 1)]
say(f"    pooled over both beds                 n={len(pooled_o)}  "
    f"r = {pearson(pooled_o, pooled_l):.4f}")
say()

# ---------------------------------------------------------------------------
say("# 5. The two median conventions, on the corner radii §B §3 cites")
say()
say("Neither figure is wrong and neither moves. `tables` takes the upper middle of an even count")
say("and read-checks.py averages the two middles, so a component carrying an even number of cells")
say("reads differently in the two files. The implied radius is 1/κ.")
say()
say(f"  {'component':22s} {'cells':>5s}  {'κ 26.5 upper':>13s} {'κ 27 upper':>11s} "
    f"{'r upper':>18s}  {'κ 26.5 mean':>12s} {'κ 27 mean':>10s} {'r mean':>18s}")
components = {}
for r in fit:
    pair = r["readings"].get("cornerCurvaturePerPx")
    if pair:
        components.setdefault(r["component"], []).append(pair)
for name in sorted(components):
    pairs = components[name]
    a_up, b_up = med_upper([p[0] for p in pairs]), med_upper([p[1] for p in pairs])
    a_mn, b_mn = med_mean([p[0] for p in pairs]), med_mean([p[1] for p in pairs])
    say(f"  {name:22s} {len(pairs):>5d}  {a_up:>13.5f} {b_up:>11.5f} "
        f"{f'{1 / a_up:.2f} → {1 / b_up:.2f} px':>18s}  {a_mn:>12.5f} {b_mn:>10.5f} "
        f"{f'{1 / a_mn:.2f} → {1 / b_mn:.2f} px':>18s}")
say()
say("`law-tables.txt` prints the 'upper' pair and claims §5.152 §B §3 cites the 'mean' pair. They")
say("can differ only where the cell count is even — capsule-button, rrect-ml and toolbar-group —")
say("and on this bed only rrect-ml actually does, because the other two have equal middles. The")
say("generator now names its convention in the file's header.")
say()

# ---------------------------------------------------------------------------
say("# 6. The attested field, as the manifest writes it")
say()
for profile in manifest["profiles"]:
    if profile.get("profileKey") == COUPLED:
        attestation = profile.get("attestation") or {}
        say("  " + COUPLED)
        for field in ("increaseContrast", "reduceTransparency", "showBorders", "glassTintAmount",
                      "osBuild", "displayplacerMode", "runs"):
            say(f"    {field:20s} {attestation.get(field, 'ABSENT')}")
say()
say("  `showBorders` and `glassTintAmount` are the attestation's field names. ButtonShapesEnabled")
say("  and NSGlassTintAmount are the `defaults` keys they are read from (charter Surprises,")
say("  2026-09-18) and appear in the profile's caveat prose, not in the attested block.")
say()

text = "\n".join(out) + "\n"
open(os.path.join(HERE, "review-closure.txt"), "w").write(text)
sys.stdout.write(text)
