"""W43 G2: the per-law verdict rule, declared with the bar and rehearsed before any pair is read.

Charter clause 7 asks for a verdict *moved / not moved* per law (silhouette, contour, interior level,
tone by backdrop, scatter, chroma, rim band, highlight, exterior shadow, tint shade, the recede)
against the declared bar. This file IS that rule; ``bar-declaration.md`` states it in prose and pins
this file's SHA-256, so the rule cannot move after the hash.

    python3.12 -B verdicts.py <slider-delta.json> [--recede <slider-recede-delta.json>] [--out <txt>]
    python3.12 -B verdicts.py <native-delta.json> --w29 --standard-only [--recede <recede-delta.json>] --out <txt>

The second form reads W29's 26.5-against-27 rows, as a rehearsal on a delta whose verdicts are on
record (§5.151); its signed readings are then 27 − 26.5.

THE RULE, per law and per pose:

1. A cell moves on a metric when the pair's value exceeds the row's verdict bar (the row's
   ``moved``; the bar is the larger of the two sides' three-level bounds, ``bar-declaration.md``).
2. A law is read on its PRIMARY metric, over its declared population, with every ``rrect-lg`` cell
   held out as its own stratum (memo F: the rrect-lg backdrop capture scale is 0.5 at x = 0.25
   against 0.25 at x = 0.5, a declared-tree step and not a material constant; §5.198 §7).
3. MOVED when the primary moved on at least half of the measured cells in at least one pose.
   NOT MOVED when it moved on no cell in either pose: the bar separates nothing.
   MINORITY otherwise: the law did not move as a law, and the cells that did are named.
4. Every verdict is printed with its magnitude, because the bar is W29's bed minimum on cells that
   were unanimous on both sides and a "moved" there means "differs at all": the moved count, the
   median |delta|, its p90, the median signed change and up/down counts, the median delta/bar.
5. The secondary metrics of each law are printed beside it and never change its verdict.
6. With ``--null``, each primary metric is printed beside the largest value the CANONICAL bridge
   null reached on it (G1a's 0.5 captures through the side bundle against their 0.5 fixtures,
   ``rehearsal/null-pairs-measured.json``): the size of the bundle-and-night term the bar does not
   contain, on the cells the bridges cover. Moved cells whose value is no larger are counted as
   "within the null". Descriptive; it never changes a verdict.
7. Attribution reads, descriptive and never a verdict: for the geometry, the healthy population
   (both silhouettes within 2x of each other, §5.151 §4); for the rim and the highlight, the
   uniform-backdrop subset (a uniform backdrop gives a uniform body change, so a reading taken
   relative to the body is the edge's own change there); for every law, the radial difference
   profile's bands where the rows carry it.

Medians are the upper middle order statistic of an even count, as ``native-delta tables`` takes them.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

STRUCTURED = re.compile(r"^(checkerboard|hc-text|photo|impulse)")
SINGLE_BOX = {"capsule-button", "rrect-sm", "rrect-md", "rrect-ml", "rrect-lg", "rrect-48", "rrect-64", "rrect-80"}
HELD_OUT_STRATUM = "rrect-lg"

# The law, its primary metric, its secondary metrics and its population.
LAWS = [
    ("silhouette", "silhouetteIoUComplement", ["silhouetteAreaDeltaPx"], "all"),
    ("contour", "contourDistanceMeanPx", ["contourDistanceP95Px", "cornerCurvatureDeltaPerPx"], "all"),
    ("interior level", "bodyLevelDelta", ["interiorMeanDelta"], "all"),
    ("tone by backdrop", "transferSlopeDelta", ["transferOffsetDelta"], "all"),
    ("scatter", "interiorStdDevDelta", [], "structured"),
    ("chroma", "tintChromaDelta", [], "untinted"),
    (
        "rim band",
        "rimContourDeltaMax",
        ["rimLocalDeltaMax", "rimRow0DeltaMax", "rimPeakDelta", "rimPeakDepthDeltaPx", "rimFwhmDeltaPx"],
        "all",
    ),
    (
        "highlight",
        "highlightBinDeltaMax",
        ["highlightBinDeltaMean", "highlightIntegralDeltaMax", "highlightRatioDelta", "highlightPeakAngleDeltaDeg"],
        "all",
    ),
    (
        "exterior shadow",
        "shadowProfileRmsDelta",
        [
            "shadowMeanDepartureDelta",
            "shadowStrengthPeakDelta",
            "shadowStrengthPeakDistanceDeltaPx",
            "shadowFalloffSigmaDeltaPx",
            "shadowFalloffAmplitudeDelta",
            "shadowFalloffLengthDeltaPx",
            "shadowExtentAboveDeltaPx",
            "shadowExtentBelowDeltaPx",
            "shadowExtentLeftDeltaPx",
            "shadowExtentRightDeltaPx",
            "shadowOffsetXDeltaPx",
            "shadowOffsetYDeltaPx",
            "shadowCentroidOffsetXDeltaPx",
            "shadowCentroidOffsetYDeltaPx",
            "shadowAffineSlopeDeltaMax",
            "shadowAffineInterceptDeltaMax",
        ],
        "all",
    ),
    ("tint shade", "tintDeltaLDelta", ["tintChromaDelta", "tintHueShiftDeltaDeg"], "tinted"),
]
RECEDE_PRIMARY = "bodyLevel"
RECEDE_SECONDARY = [
    "rimContourMean",
    "rimLocalMean",
    "highlightPeak",
    "highlightFloor",
    "highlightRatio",
    "interiorMean",
    "interiorStdDev",
    "tintDeltaL",
    "tintChroma",
]
WHOLE_CELL = [
    "ssimComplement",
    "ssimBandComplement",
    "ssimInteriorComplement",
    "ssimOutsideComplement",
    "oklabDeltaEMean",
    "oklabDeltaEP95",
    "oklabDeltaEBodyMean",
    "edgeWeightedMean",
]

# The signed reading behind a metric, as the native delta's SIGNED_OF names it.
SIGNED_OF = {
    "interiorMeanDelta": "interiorMean",
    "interiorStdDevDelta": "interiorStdDev",
    "bodyLevelDelta": "bodyLevel",
    "transferSlopeDelta": "transferSlope",
    "transferOffsetDelta": "transferOffset",
    "rimContourDeltaMax": "rimContourMeanSide",
    "rimPeakDelta": "rimPeak",
    "rimPeakDepthDeltaPx": "rimPeakDepthPx",
    "rimFwhmDeltaPx": "rimFwhmPx",
    "highlightRatioDelta": "highlightRatio",
    "cornerCurvatureDeltaPerPx": "cornerCurvaturePerPx",
    "tintDeltaLDelta": "tintDeltaL",
    "tintChromaDelta": "tintChroma",
    "shadowMeanDepartureDelta": "shadowMeanDeparture",
    "shadowStrengthPeakDelta": "shadowStrengthPeak",
    "shadowExtentBelowDeltaPx": "shadowExtentBelowPx",
    "shadowFalloffSigmaDeltaPx": "shadowFalloffSigmaPx",
    "shadowFalloffAmplitudeDelta": "shadowFalloffAmplitude",
    "shadowFalloffLengthDeltaPx": "shadowFalloffLengthPx",
    "shadowOffsetYDeltaPx": "shadowOffsetYPx",
}


def median(values: list[float]) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def quantile(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


def fmt(value: float) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    if math.isinf(value):
        return "inf"
    return f"{value:.3e}"


def normalise(rows: list[dict], w29: bool) -> list[dict]:
    """W29's rows name their sides by OS; the rule reads both shapes the same way."""
    if not w29:
        return rows
    out = []
    for row in rows:
        row = dict(row)
        row["profileKey"] = row.pop("profileKey27")
        row["counterpartProfileKey"] = row.pop("profileKey26")
        out.append(row)
    return out


def in_population(row: dict, population: str) -> bool:
    tinted = "-tint-" in row["sceneId"]
    if population == "all":
        return True
    if population == "structured":
        return bool(STRUCTURED.match(row["background"]))
    if population == "untinted":
        return not tinted
    if population == "tinted":
        return tinted
    raise ValueError(population)


def signed(row: dict, metric: str) -> float | None:
    name = SIGNED_OF.get(metric)
    if name is None:
        return None
    pair = (row.get("readings") or {}).get(name)
    if not isinstance(pair, list) or len(pair) != 2 or None in pair:
        return None
    return pair[1] - pair[0]


def tally(rows: list[dict], metric: str) -> dict:
    values, ratios, signs = [], [], []
    moved = up = down = 0
    for row in rows:
        value = (row.get("metrics") or {}).get(metric)
        bound = (row.get("bar") or {}).get(metric)
        if value is None or bound is None:
            continue
        values.append(value)
        ratios.append(math.inf if bound == 0 and value > 0 else (0.0 if bound == 0 else value / bound))
        is_moved = (row.get("moved") or {}).get(metric) is True
        moved += is_moved
        s = signed(row, metric)
        if s is not None:
            signs.append(s)
            if is_moved:
                up += s > 0
                down += s < 0
    return {
        "measured": len(values),
        "moved": moved,
        "share": (moved / len(values)) if values else math.nan,
        "medianAbs": median(values),
        "p90Abs": quantile(values, 0.9),
        "medianSigned": median(signs) if signs else None,
        "up": up,
        "down": down,
        "medianRatio": median(ratios),
    }


def verdict_of(per_pose: dict[str, dict]) -> str:
    measured = [t for t in per_pose.values() if t["measured"] > 0]
    if not measured:
        return "UNMEASURED"
    if any(t["share"] >= 0.5 for t in measured):
        return "MOVED"
    if all(t["moved"] == 0 for t in measured):
        return "NOT MOVED"
    return "MINORITY"


def line(label: str, t: dict) -> str:
    return (
        f"    {label:<34} {t['moved']:>4}/{t['measured']:<4} share {t['share']:.3f}  "
        f"med|d| {fmt(t['medianAbs'])}  p90 {fmt(t['p90Abs'])}  "
        f"med signed {fmt(t['medianSigned']) if t['medianSigned'] is not None else '—'}  "
        f"up/down {t['up']}/{t['down']}  med d/bar {fmt(t['medianRatio'])}"
    )


def recede_tally(rows: list[dict], name: str) -> dict:
    values, ratios = [], []
    moved = up = down = 0
    for row in rows:
        d = row["deltaOfRecede"].get(name)
        bound = row["bar"].get(name)
        if d is None or bound is None:
            continue
        values.append(d)
        ratios.append(math.inf if bound == 0 and d != 0 else (0.0 if bound == 0 else abs(d) / bound))
        if row["moved"].get(name) is True:
            moved += 1
            up += d > 0
            down += d < 0
    return {
        "measured": len(values),
        "moved": moved,
        "share": (moved / len(values)) if values else math.nan,
        "medianAbs": median([abs(v) for v in values]),
        "p90Abs": quantile([abs(v) for v in values], 0.9),
        "medianSigned": median(values),
        "up": up,
        "down": down,
        "medianRatio": median(ratios),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("delta")
    parser.add_argument("--recede")
    parser.add_argument("--w29", action="store_true")
    parser.add_argument("--standard-only", action="store_true")
    parser.add_argument("--null")
    parser.add_argument("--out")
    parser.add_argument("--json")
    args = parser.parse_args()

    rows = normalise(json.loads(Path(args.delta).read_text())["rows"], args.w29)
    if args.standard_only:
        rows = [r for r in rows if "-standard" in r["profileKey"]]
    null_max: dict[str, float] = {}
    if args.null:
        for row in json.loads(Path(args.null).read_text())["rows"]:
            if not row["label"].startswith("canonical:"):
                continue
            for metric, value in row["metrics"].items():
                if value is not None:
                    null_max[metric] = max(null_max.get(metric, 0.0), value)
    out: list[str] = []
    record: dict = {"source": args.delta, "laws": {}, "strata": {}, "nullMax": null_max}
    say = out.append
    say(f"# Per-law verdicts under the declared rule (verdicts.py), over {args.delta}")
    say("")
    say(f"{len(rows)} pair rows; {sum(1 for r in rows if r['component'] == HELD_OUT_STRATUM)} in the held-out "
        f"{HELD_OUT_STRATUM} stratum; poses {dict(Counter(r['pose'] for r in rows))}")
    say("")

    verdict_rows = [r for r in rows if r["component"] != HELD_OUT_STRATUM]
    stratum_rows = [r for r in rows if r["component"] == HELD_OUT_STRATUM]
    for law, primary, secondary, population in LAWS:
        say(f"## {law}  (primary {primary}; population {population}; {HELD_OUT_STRATUM} held out)")
        per_pose = {}
        for pose in ("active", "inactive"):
            subset = [r for r in verdict_rows if r["pose"] == pose and in_population(r, population)]
            per_pose[pose] = tally(subset, primary)
        verdict = verdict_of(per_pose)
        say(f"  VERDICT: {verdict}")
        for pose, t in per_pose.items():
            say(line(f"{primary} [{pose}]", t))
        if args.null:
            ceiling = null_max.get(primary)
            for pose in ("active", "inactive"):
                subset = [r for r in verdict_rows if r["pose"] == pose and in_population(r, population)]
                moved_values = [r["metrics"][primary] for r in subset if (r.get("moved") or {}).get(primary)]
                within = sum(1 for v in moved_values if ceiling is not None and v <= ceiling)
                per_pose[pose]["withinNull"] = within
                say(f"    canonical bridge null's largest {primary}: {fmt(ceiling) if ceiling is not None else '— (never measured)'}; "
                    f"moved cells [{pose}] no larger than it: {within} of {len(moved_values)}")
        for metric in secondary:
            for pose in ("active", "inactive"):
                subset = [r for r in verdict_rows if r["pose"] == pose and in_population(r, population)]
                t = tally(subset, metric)
                if t["measured"]:
                    say(line(f"{metric} [{pose}]", t))
        stratum = {
            pose: tally([r for r in stratum_rows if r["pose"] == pose and in_population(r, population)], primary)
            for pose in ("active", "inactive")
        }
        for pose, t in stratum.items():
            if t["measured"]:
                say(line(f"{HELD_OUT_STRATUM} stratum [{pose}]", t))
        record["laws"][law] = {"verdict": verdict, "primary": primary, "perPose": per_pose, "rrectLg": stratum}
        say("")

    recede_path = args.recede
    if recede_path:
        recede = json.loads(Path(recede_path).read_text())["rows"]
        if args.w29:
            for row in recede:
                row["profileKey"] = row.pop("profileKey27")
        recede = [r for r in recede if not args.standard_only or "-standard" in r["profileKey"]]
        for row in recede:
            row["component"] = row["activeSceneId"].split("__")[1]
        held = [r for r in recede if r["component"] != HELD_OUT_STRATUM]
        t = recede_tally(held, RECEDE_PRIMARY)
        verdict = "UNMEASURED" if t["measured"] == 0 else (
            "MOVED" if t["share"] >= 0.5 else "NOT MOVED" if t["moved"] == 0 else "MINORITY"
        )
        say(f"## the recede  (primary {RECEDE_PRIMARY} difference of differences; {HELD_OUT_STRATUM} held out)")
        say(f"  VERDICT: {verdict}")
        say(line(f"{RECEDE_PRIMARY}", t))
        for name in RECEDE_SECONDARY:
            s = recede_tally(held, name)
            if s["measured"]:
                say(line(name, s))
        s = recede_tally([r for r in recede if r["component"] == HELD_OUT_STRATUM], RECEDE_PRIMARY)
        if s["measured"]:
            say(line(f"{HELD_OUT_STRATUM} stratum", s))
        record["laws"]["the recede"] = {"verdict": verdict, "primary": RECEDE_PRIMARY, "all": t, "rrectLg": s}
        say("")

    say("## The whole cell, as context (no verdict)")
    for metric in WHOLE_CELL:
        for pose in ("active", "inactive"):
            t = tally([r for r in verdict_rows if r["pose"] == pose], metric)
            if t["measured"]:
                say(line(f"{metric} [{pose}]", t))
    say("")

    # ---- attribution reads, descriptive -------------------------------------------------
    say("## Attribution reads (descriptive; never a verdict)")
    say("")
    healthy, unhealthy = [], []
    for r in verdict_rows:
        areas = (r.get("readings") or {}).get("silhouetteAreaPx")
        if not areas or min(areas) == 0:
            continue
        (healthy if max(areas) <= 2 * min(areas) else unhealthy).append(r)
    say(f"Geometry, healthy population (both silhouettes within 2x): {len(healthy)} cells; "
        f"one under half the other: {len(unhealthy)}")
    for metric in ("silhouetteIoUComplement", "contourDistanceMeanPx", "silhouetteAreaDeltaPx", "cornerCurvatureDeltaPerPx"):
        t = tally(healthy, metric)
        if t["measured"]:
            say(line(f"healthy {metric}", t))
    small = Counter()
    for r in unhealthy:
        a, b = r["readings"]["silhouetteAreaPx"]
        small[(r["background"], "reference small" if a < b else "subject small")] += 1
    for (background, side), n in sorted(small.items(), key=lambda kv: -kv[1]):
        say(f"    unhealthy: {background:<20} {side:<16} {n}")
    say("")
    say("Implied corner radius per single-box component, median 1/kappa (reference -> subject), healthy cells:")
    by_component = defaultdict(list)
    for r in healthy:
        k = (r.get("readings") or {}).get("cornerCurvaturePerPx")
        if k and None not in k and k[0] > 0 and k[1] > 0:
            by_component[r["component"]].append(k)
    for component, pairs in sorted(by_component.items()):
        before = median([p[0] for p in pairs])
        after = median([p[1] for p in pairs])
        say(f"    {component:<16} {len(pairs):>4} cells  {1 / before:7.2f} -> {1 / after:7.2f} px")
    say("")
    uniform = [r for r in verdict_rows if not STRUCTURED.match(r["background"])]
    say(f"Rim and highlight on uniform backdrops only ({len(uniform)} cells):")
    for metric in ("rimContourDeltaMax", "rimLocalDeltaMax", "highlightBinDeltaMax", "highlightRatioDelta", "bodyLevelDelta"):
        for pose in ("active", "inactive"):
            t = tally([r for r in uniform if r["pose"] == pose], metric)
            if t["measured"]:
                say(line(f"uniform {metric} [{pose}]", t))
    say("")
    if any("radial" in r for r in rows):
        say("Radial difference profile, per band (cells with any differing pixel / cells; median of the")
        say("per-cell mean |code|; max |code|; median per-cell mean signed linear luminance):")
        for stratum_name, subset in (("held-in", verdict_rows), (HELD_OUT_STRATUM, stratum_rows)):
            for pose in ("active", "inactive"):
                bands = defaultdict(list)
                for r in subset:
                    if r["pose"] != pose:
                        continue
                    for band in r.get("radial", []):
                        bands[band["band"]].append(band)
                if not bands:
                    continue
                say(f"  {stratum_name} [{pose}]")
                for name in ("deep", "shoulder", "edge", "near-exterior", "exterior", "far"):
                    items = bands.get(name, [])
                    if not items:
                        continue
                    differing = sum(1 for b in items if b["differing"] > 0)
                    say(
                        f"    {name:<14} {differing:>4}/{len(items):<4} "
                        f"med mean|code| {median([b['meanAbsCode'] for b in items]):8.3f}  "
                        f"max|code| {max(b['maxAbsCode'] for b in items):5.0f}  "
                        f"med signed lum {median([b['meanSignedLuminance'] for b in items]):+.5f}"
                    )
        say("")

    text = "\n".join(out) + "\n"
    if args.out:
        Path(args.out).write_text(text)
    if args.json:
        Path(args.json).write_text(json.dumps(record, indent=1, default=str) + "\n")
    print(text)


if __name__ == "__main__":
    main()
