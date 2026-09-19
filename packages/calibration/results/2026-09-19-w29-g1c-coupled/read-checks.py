#!/usr/bin/env python3
"""The seven things the law tables cannot answer about the coupled bed.

W29 G1c Part B, claims §5.152 §B. `delta/law-tables.txt` counts cells that cleared
their bar; each check below is a question about what those counts MEAN that no
count answers on its own. Five of them are G2's own conditioning, applied to this
profile because a reading that joins §5.151 has to be read the way §5.151 is read
(§5.151 §3, §4, §7); the other two exist only here.

    read-checks.py            > read-checks.txt

Reads the committed rows and writes nothing.
"""
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(os.path.dirname(HERE))
G2 = os.path.join(PKG, "results", "2026-09-19-w29-g2-native-delta")

COUPLED = "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5"
DECOUPLED = "apple-macos-27.0-1x-light-increased-contrast-glass0.5"

rows = json.load(open(os.path.join(HERE, "delta", "native-delta.json")))["rows"]
recede = json.load(open(os.path.join(HERE, "delta", "recede-delta.json")))["rows"]
bar = json.load(open(os.path.join(HERE, "delta", "noise-bar.json")))
g2rows = [r for r in json.load(open(os.path.join(G2, "native-delta.json")))["rows"]
          if r["profileKey27"] == DECOUPLED]
g2recede = [r for r in json.load(open(os.path.join(G2, "recede-delta.json")))["rows"]
            if r["profileKey27"] == DECOUPLED]


def med(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else float("nan")


def out(line=""):
    sys.stdout.write(line + "\n")


out("# W29 G1c — what the coupled bed's counts mean")
out()
out("Rows: %d pair, %d recede. The 26.5 counterpart is"
    " apple-macos-26.5-1x-light-increased-contrast on every one of them." % (len(rows), len(recede)))
out()

# ---------------------------------------------------------------------------
out("## 1. The geometry, on the cells whose two silhouettes are comparable")
out()
out("§5.151 §4: where one bed's material sits inside the extractor's 0.02 linear threshold of its")
out("own backdrop and the other's does not, every silhouette-masked statistic is taken over a few")
out("dozen pixels and the shape metrics read a segmentation, not a shape. The same conditioning is")
out("applied here: a cell is HEALTHY when its two silhouettes are within 2x of each other.")
out()
artefacts, healthy = [], []
for r in rows:
    a26 = (r["readings"].get("silhouetteAreaPx") or [None, None])[0]
    a27 = (r["readings"].get("silhouetteAreaPx") or [None, None])[1]
    if a26 is None or a27 is None or a26 == 0 or a27 == 0:
        continue
    (artefacts if (a26 / a27 < 0.5 or a27 / a26 < 0.5) else healthy).append(r)
out("healthy %d, artefact %d of %d cells carrying both areas" %
    (len(healthy), len(artefacts), len(healthy) + len(artefacts)))
for r in artefacts:
    out("  artefact  %-44s 26.5 %8.0f px   27 %8.0f px" %
        (r["sceneId"], r["readings"]["silhouetteAreaPx"][0],
         r["readings"]["silhouetteAreaPx"][1]))
out()
for metric in ["silhouetteIoUComplement", "contourDistanceMeanPx", "silhouetteAreaDeltaPx"]:
    vals = [r["metrics"].get(metric) for r in healthy]
    moved = sum(1 for r in healthy if r["moved"].get(metric))
    out("  healthy  %-26s moved %2d/%2d   median %.6g" %
        (metric, moved, len([v for v in vals if v is not None]), med(vals)))
out()

# ---------------------------------------------------------------------------
out("## 2. The corner, signed and per component")
out()
signed = []
for r in healthy:
    pair = r["readings"].get("cornerCurvaturePerPx") or [None, None]
    k26, k27 = pair[0], pair[1]
    if k26 is None or k27 is None:
        continue
    signed.append((r["sceneId"], r["component"], k26, k27, k27 - k26))
up = sum(1 for s in signed if s[4] > 0)
down = sum(1 for s in signed if s[4] < 0)
tied = sum(1 for s in signed if s[4] == 0)
out("over %d healthy cells carrying a curvature: %d up, %d down, %d exactly tied;"
    " median signed Δκ %.4g /px" % (len(signed), up, down, tied, med([s[4] for s in signed])))
out()
out("  component            cells   median κ 26.5   median κ 27   implied r 26.5→27")
comps = sorted({s[1] for s in signed})
for c in comps:
    group = [s for s in signed if s[1] == c]
    k26, k27 = med([g[2] for g in group]), med([g[3] for g in group])
    out("  %-20s %5d   %13.5f %13.5f   %6.2f → %6.2f px" %
        (c, len(group), k26, k27, 1 / k26 if k26 else float("nan"), 1 / k27 if k27 else float("nan")))
out()

# ---------------------------------------------------------------------------
out("## 3. The tint's hue, conditioned on there being a hue")
out()
out("§5.151 §7: `tintResponse` documents that its hue is meaningless at near-zero chroma, and a")
out("bed read without that condition reports a hue swing that is an artefact of it.")
out()
lo, hi = [], []
for r in rows:
    pair = r["readings"].get("tintChroma") or [None, None]
    c26, c27 = pair[0], pair[1]
    v = r["metrics"].get("tintHueShiftDeltaDeg")
    if c26 is None or c27 is None or v is None:
        continue
    (hi if (c26 >= 0.01 and c27 >= 0.01) else lo).append(v)
out("  chroma ≥ 0.01 on BOTH beds: %d cells, median |Δhue| %.3g°" % (len(hi), med(hi)))
out("  below it on either bed:     %d cells, median |Δhue| %.3g°" % (len(lo), med(lo)))
out("  read without the condition: %d cells, median |Δhue| %.3g°" % (len(lo) + len(hi), med(lo + hi)))
out()

# ---------------------------------------------------------------------------
out("## 4. The coupled bed against the decoupled one, cell for cell")
out()
out("The two 27 profiles declare the same 32 cells and share one 26.5 counterpart, so their rows")
out("differ in exactly one thing: whether Reduce transparency was on when the 27 side was captured.")
out("This is what §5.151 §9 could not have: the confounded reading beside the unconfounded one.")
out()
g2by = {r["sceneId"]: r for r in g2rows}
out("  metric                         coupled moved  decoupled moved   median |Δ| coupled  decoupled   ratio")
METRICS = bar["metrics"]
compare = {}
for m in METRICS:
    cm = [r for r in rows if r["metrics"].get(m) is not None]
    dm = [r for r in g2rows if r["metrics"].get(m) is not None]
    cmoved = sum(1 for r in cm if r["moved"].get(m))
    dmoved = sum(1 for r in dm if r["moved"].get(m))
    cmed = med([r["metrics"][m] for r in cm])
    dmed = med([r["metrics"][m] for r in dm])
    ratio = (dmed / cmed) if (cmed and cmed == cmed and dmed == dmed and cmed != 0) else float("nan")
    compare[m] = (cmoved, len(cm), dmoved, len(dm), cmed, dmed, ratio)
    out("  %-30s %5d/%-5d %8d/%-5d %12.5g %11.5g %7.2f" %
        (m, cmoved, len(cm), dmoved, len(dm), cmed, dmed, ratio))
out()
out("  ratio = the decoupled bed's median distance from 26.5 divided by the coupled bed's. Above 1")
out("  means the decoupled reading is the larger one, and the excess is what the TOGGLE contributes")
out("  to §5.151's numbers on this profile.")
out()

# ---------------------------------------------------------------------------
out("## 5. The signed readings, coupled and decoupled, on the laws the ledger leans on")
out()
READINGS = ["bodyLevel", "interiorMean", "interiorStdDev", "transferSlope", "transferOffset",
            "rimPeak", "rimPeakDepthPx", "rimFwhmPx", "tintDeltaL", "tintChroma"]
out("  reading            26.5   27 coupled   27 decoupled   coupled−26.5   decoupled−26.5")
for name in READINGS:
    b26 = med([(r["readings"].get(name) or [None, None])[0] for r in rows])
    c27 = med([(r["readings"].get(name) or [None, None])[1] for r in rows])
    d27 = med([(r["readings"].get(name) or [None, None])[1] for r in g2rows])
    out("  %-16s %9.5g %11.5g %14.5g %14.5g %16.5g" %
        (name, b26, c27, d27, c27 - b26, d27 - b26))
out()

# ---------------------------------------------------------------------------
out("## 6. Would any verdict differ under a fallback taken over this pass alone?")
out()
out("The bar declaration takes the zero-spread fallback over the whole 27 bed rather than over this")
out("pass's 32 cells (bar-declaration.md §1). The alternative is recorded here rather than argued:")
out("a 32-cell minimum is larger where it is defined and undefined on twelve metrics, where the")
out("rule would then give a bar of exactly zero.")
out()
alt = {}
for m in METRICS:
    vals = [c["pairwise"][m]["max"] for c in bar["cells"]
            if m in c["pairwise"] and c["pairwise"][m]["max"] > 0]
    alt[m] = min(vals) if vals else None
flips = []
for r in rows:
    cell = next(c for c in bar["cells"] if c["sceneId"] == r["sceneId"])
    for m in METRICS:
        value = r["metrics"].get(m)
        if value is None:
            continue
        own = cell["pairwise"].get(m, {}).get("max")
        if own is None:
            continue
        used = r["bar"].get(m)
        altbar = own if own > 0 else (alt[m] if alt[m] is not None else 0.0)
        now = r["moved"].get(m)
        then = value > altbar
        if now != then:
            flips.append((r["sceneId"], m, value, used, altbar, now, then))
out("  verdicts that would differ: %d of %d" %
    (len(flips), sum(1 for r in rows for m in METRICS if r["moved"].get(m) is not None)))
for f in flips[:40]:
    out("    %-40s %-28s Δ=%.4g bar %.4g → %.4g   moved %s → %s" % f)
out()

# ---------------------------------------------------------------------------
out("## 7. The recede, coupled against decoupled")
out()
out("  reading              coupled moved  decoupled moved   median difference coupled  decoupled")
names = sorted({k for r in recede for k in r["deltaOfRecede"]})
for name in names:
    cm = [r for r in recede if r["deltaOfRecede"].get(name) is not None]
    dm = [r for r in g2recede if r["deltaOfRecede"].get(name) is not None]
    out("  %-20s %5d/%-5d %8d/%-5d %20.5g %11.5g" %
        (name,
         sum(1 for r in cm if r["moved"].get(name)), len(cm),
         sum(1 for r in dm if r["moved"].get(name)), len(dm),
         med([r["deltaOfRecede"][name] for r in cm]),
         med([r["deltaOfRecede"][name] for r in dm])))
out()
out("%d coupled recede rows against %d decoupled ones." % (len(recede), len(g2recede)))


# ---------------------------------------------------------------------------
out()
out("## 8. The native-to-native distribution against the 26.5 allowances")
out()
out("The shape of Decision Log 4 (c)'s table, for this profile. It is what a bound proposal has to")
out("be read off: every row of `adopted-thresholds.test.ts` is a PER-CELL bound, so the p90 and the")
out("max decide whether declaring the 26.5 table for this profile is defensible, not the median.")
out("The three shape rows are over the HEALTHY cells of check 1, as that table's are.")
out()
# The 26.5 increased-contrast texture-tier allowances, transcribed from Decision
# Log 4 (c)'s own column for the profile of that name; every row restated so
# that lower is closer.
ALLOWANCE = [
    ("silhouetteIoUComplement", 0.15, True),
    ("contourDistanceMeanPx", 1.8, True),
    ("contourDistanceP95Px", 11.5, True),
    ("ssimComplement", 0.14, False),
    ("oklabDeltaEMean", 0.06, False),
    ("oklabDeltaEP95", 0.10, False),
    ("edgeWeightedMean", 0.17, False),
    ("ssimOutsideComplement", 0.20, False),
]


def quantile(values, q):
    values = sorted(v for v in values if v is not None)
    if not values:
        return float("nan")
    i = min(len(values) - 1, max(0, int(round(q * (len(values) - 1)))))
    return values[i]


out("  metric                       population  median      p90         max         26.5 allowance  over?")
for metric, allow, shape in ALLOWANCE:
    pool = healthy if shape else rows
    vals = [r["metrics"].get(metric) for r in pool]
    vals = [v for v in vals if v is not None]
    m, p90, mx = med(vals), quantile(vals, 0.9), max(vals) if vals else float("nan")
    out("  %-28s %6d  %10.4g  %10.4g  %10.4g  %14.4g  %s" %
        (metric, len(vals), m, p90, mx, allow,
         "MAX OVER" if mx > allow else ("p90 over" if p90 > allow else "")))
out()

# ---------------------------------------------------------------------------
out("## 9. Does this profile move like the rest of the bed?")
out()
out("The five profiles Decision Log 4 (a) declared tables for are the unconfounded ones. The")
out("comparison is per profile and on |Δ| — the quantity the law tables report — because a signed")
out("median pooled over light, dark and reduced transparency cancels populations that §5.151 §2")
out("says moved BOTH ways, and would answer a question nobody asked.")
out()
allrows = json.load(open(os.path.join(G2, "native-delta.json")))["rows"]
UNCONFOUNDED = [
    "apple-macos-27.0-1x-light-standard-glass0.5",
    "apple-macos-27.0-2x-light-standard-glass0.5",
    "apple-macos-27.0-1x-dark-standard-glass0.5",
    "apple-macos-27.0-2x-dark-standard-glass0.5",
    "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
]
SHOWN = ["ssimComplement", "oklabDeltaEMean", "edgeWeightedMean", "interiorMeanDelta",
         "bodyLevelDelta", "interiorStdDevDelta", "transferSlopeDelta", "rimContourDeltaMax",
         "highlightBinDeltaMax", "tintDeltaLDelta"]
header = "  %-28s %9s" % ("metric (median |Δ|)", "coupled")
for key in UNCONFOUNDED:
    header += " %11s" % key.replace("apple-macos-27.0-", "").replace("-glass0.5", "")[:11]
out(header)
for m in SHOWN:
    line = "  %-28s %9.4g" % (m, med([r["metrics"].get(m) for r in rows]))
    for key in UNCONFOUNDED:
        pool = [r for r in allrows if r["profileKey27"] == key]
        line += " %11.4g" % med([r["metrics"].get(m) for r in pool])
    out(line)
out()
out("  And the directions, per profile, as the share of moved cells that read UP on the signed")
out("  reading — a law that moved the same way everywhere reads the same here.")
out()
SIGNED = [("bodyLevelDelta", "bodyLevel"), ("interiorMeanDelta", "interiorMean"),
          ("interiorStdDevDelta", "interiorStdDev"), ("transferSlopeDelta", "transferSlope"),
          ("tintDeltaLDelta", "tintDeltaL")]
out("  %-28s %9s %s" % ("reading (up / moved)", "coupled",
                        " ".join("%11s" % k.replace("apple-macos-27.0-", "").replace("-glass0.5", "")[:11]
                                 for k in UNCONFOUNDED)))
for metric, name in SIGNED:
    def share(pool):
        moved = [r for r in pool if r["moved"].get(metric)
                 and (r["readings"].get(name) or [None, None])[0] is not None]
        if not moved:
            return "—"
        up = sum(1 for r in moved
                 if r["readings"][name][1] > r["readings"][name][0])
        return "%d/%d" % (up, len(moved))
    line = "  %-28s %9s" % (name, share(rows))
    for key in UNCONFOUNDED:
        line += " %11s" % share([r for r in allrows if r["profileKey27"] == key])
    out(line)
out()
out("  %d coupled rows; the five profiles carry %d rows between them." %
    (len(rows), len([r for r in allrows if r["profileKey27"] in UNCONFOUNDED])))
