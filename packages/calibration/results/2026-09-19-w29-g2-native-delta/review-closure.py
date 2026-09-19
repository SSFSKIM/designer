"""W29 G2 — the ten recomputations the gate's independent review asked for (2026-09-19).

Run from `packages/calibration`:

    python3 results/2026-09-19-w29-g2-native-delta/review-closure.py

Every figure the review closure writes into claims §5.151 and into the charter's Decision
Log 4 is computed here, from the committed rows, and none is copied from the review. The
median is the instrument's own — the upper middle element for an even count, exactly as
`native-delta.ts`'s `median` — so that a figure written beside one of the instrument's can
be compared with it; where a percentile is used it is nearest-rank and says so.

The ten, in the review's numbering:

 1. The recede's population. The first cut barred a recede reading only where BOTH 27 cells
    had a non-zero spread of their own, which left 158 of 231 rows with no bar at all and
    read §8's medians off 18–70 rows while 219 pairs were measurable. Reported here on both
    populations, and the instrument is fixed so the barred population becomes the full one.
 2. The increased-contrast rows inside the bed-wide numbers. §9 says no reading on that
    profile is a statement about the material, so every bed-wide median is reported again
    with its 32 rows removed.
 4. The bounds. Decision Log 4 (c) quotes a median against tables that bound the per-cell
    worst case, so the p90 and the max are reported per profile per bounded metric, beside
    the 26.5 texture table's allowance for that profile.
 5. The corner's up/down over the healthy cells rather than over all moved cells.
 7. The 55-cell breakdown, which prints to 53 without its two singletons.
 8. The highlight ratio's two ends, so a difference of ratios is not fitted to.
 9. The brightest bin's angular shift over the moved cells rather than over all cells.
10. The chroma population: the cells that cross 0.01 on one bed only.

Items 3 and 6 need no computation here — 3 is an attestation the fixtures either carry or
do not (checked against `fixtures/manifest.json` below), and 6 is already in
`read-checks.txt` check 6 and is transcribed into the ledger rather than recomputed.

## Amended 2026-09-19 by the G1c Part B review closure (claims §5.152 §B, §5.151 §12)

Item 4's allowances were **transcribed** from `test/adopted-thresholds.test.ts` into a
dictionary here, and three of the forty-eight texture-tier numbers were transcribed wrong
(`2x-light-standard` ssimMean, `1x-light-reduced-transparency` ssimOutside,
`1x-light-increased-contrast` ssimOutside — a fourth, `2x-light-standard` ssimOutside, was
found by the same audit). The dictionary is now **read from the test file** by
`adopted_allowances.read_allowances()` beside this script — which the G1c closure imports
too, so there is one reader and not two — the allowance column cannot drift again, and
the dom tier is reported beside the texture tier as Decision Log 4 (c) says it is. The
original transcription is kept verbatim as `TRANSCRIBED_2026_09_19` and item 11 prints it
against the file row by row: the first run's numbers are not rewritten, the corrected ones
are printed beside them. The original output stands as `review-closure.v1.txt`.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CALIBRATION = HERE.parents[1]
REFERENCE = CALIBRATION.parents[1] / "apps" / "reference-apple"

sys.path.insert(0, str(HERE))
from adopted_allowances import read_allowances  # noqa: E402  (after HERE is known)

rows = json.loads((HERE / "native-delta.json").read_text())["rows"]
recede_v1 = json.loads((HERE / "recede-delta.v1.json").read_text())["rows"]
recede_v2 = json.loads((HERE / "recede-delta.json").read_text())["rows"]

out = []


def say(line=""):
    out.append(line)


def median(values):
    """The instrument's median: the upper middle element for an even count."""
    if not values:
        return float("nan")
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def percentile(values, q):
    """Nearest-rank, so the figure is always one of the bed's own readings."""
    if not values:
        return float("nan")
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, -(-int(round(q * len(ordered) * 100)) // 100) - 1))
    return ordered[index]


def short(profile_key):
    return profile_key.replace("apple-macos-27.0-", "").replace("-glass0.5", "")


def is_ic(row):
    return "increased-contrast" in row["profileKey27"]


# ---------------------------------------------------------------------------
say("# W29 G2 — the review closure's recomputations (2026-09-19)")
say()
say("Medians are the instrument's (upper middle of an even count); percentiles are nearest-rank.")
say()

say("# 1. The recede on its full measurable population")
say()
say("Per reading: the barred population the ledger's §8 table was read on, then every row that")
say("carries the reading at all. 'v2 barred' is the same instrument after the bed-minimum")
say("fallback is applied to the recede rows as it always was to the pair rows.")
say()
say(
    f"  {'reading':18s} {'v1 bar':>7s} {'26.5':>10s} {'27':>10s} {'diff':>10s}   "
    f"{'meas':>5s} {'26.5':>10s} {'27':>10s} {'diff':>10s}   {'v2 moved/meas':>14s}"
)
readings = [name for name in json.loads((HERE / "recede-delta.json").read_text())["readings"]]
for name in readings:
    barred = [r for r in recede_v1 if name in r["bar"]]
    measurable = [r for r in recede_v1 if name in r["deltaOfRecede"]]
    v2 = [r for r in recede_v2 if name in r["bar"]]
    v2_moved = sum(1 for r in v2 if r["moved"].get(name) is True)
    pull = lambda subset, field: [r[field][name] for r in subset]
    say(
        f"  {name:18s} {len(barred):>7d} "
        f"{median(pull(barred, 'recede26')):>10.5f} {median(pull(barred, 'recede27')):>10.5f} "
        f"{median(pull(barred, 'deltaOfRecede')):>10.5f}   "
        f"{len(measurable):>5d} {median(pull(measurable, 'recede26')):>10.5f} "
        f"{median(pull(measurable, 'recede27')):>10.5f} "
        f"{median(pull(measurable, 'deltaOfRecede')):>10.5f}   "
        f"{f'{v2_moved}/{len(v2)}':>14s}"
    )
say()
say(f"  rows with no bar at all: v1 {sum(1 for r in recede_v1 if not r['bar'])} of {len(recede_v1)}, "
    f"v2 {sum(1 for r in recede_v2 if not r['bar'])} of {len(recede_v2)}")
sources = {}
for r in recede_v2:
    for name, source in r.get("barSource", {}).items():
        sources[source] = sources.get(source, 0) + 1
say(f"  v2 bar sources over all barred readings: {sources}")
say()

# ---------------------------------------------------------------------------
say("# 2. The bed-wide medians with the increased-contrast rows removed")
say()
ic_rows = [r for r in rows if is_ic(r)]
say(f"  {len(ic_rows)} increased-contrast rows of {len(rows)} "
    f"({sum(1 for r in ic_rows if r['pose'] == 'active')} active, "
    f"{sum(1 for r in ic_rows if r['pose'] == 'inactive')} inactive).")
say()
METRICS_2 = [
    "rimContourDeltaMax",
    "rimLocalDeltaMax",
    "rimPeakDelta",
    "rimFwhmDeltaPx",
    "highlightBinDeltaMax",
    "highlightBinDeltaMean",
    "highlightRatioDelta",
    "interiorMeanDelta",
    "bodyLevelDelta",
    "interiorStdDevDelta",
    "transferSlopeDelta",
    "transferOffsetDelta",
    "ssimComplement",
    "ssimBandComplement",
    "ssimInteriorComplement",
    "oklabDeltaEMean",
    "oklabDeltaEBodyMean",
    "edgeWeightedMean",
]
for pose in ("active", "inactive"):
    say(f"  ## pose: {pose}")
    say(f"  {'metric':26s} {'bed n':>6s} {'bed median':>12s} {'ex-IC n':>8s} {'ex-IC median':>13s}")
    for metric in METRICS_2:
        bed = [r["metrics"][metric] for r in rows
               if r["pose"] == pose and r["metrics"].get(metric) is not None and metric in r["bar"]]
        exic = [r["metrics"][metric] for r in rows
                if r["pose"] == pose and not is_ic(r)
                and r["metrics"].get(metric) is not None and metric in r["bar"]]
        say(f"  {metric:26s} {len(bed):>6d} {median(bed):>12.4e} {len(exic):>8d} {median(exic):>13.4e}")
    say()
say("  The rim's worst cell by delta/bar, with and without the increased-contrast rows:")
for pose in ("active", "inactive"):
    for label, subset in (("bed", rows), ("ex-IC", [r for r in rows if not is_ic(r)])):
        usable = [r for r in subset if r["pose"] == pose
                  and r["metrics"].get("rimContourDeltaMax") is not None
                  and r["bar"].get("rimContourDeltaMax")]
        worst = max(usable, key=lambda r: r["metrics"]["rimContourDeltaMax"] / r["bar"]["rimContourDeltaMax"])
        say(f"    rimContourDeltaMax {pose:9s} {label:6s} "
            f"{short(worst['profileKey27'])}/{worst['sceneId']}  "
            f"delta {worst['metrics']['rimContourDeltaMax']:.4f}  "
            f"delta/bar {worst['metrics']['rimContourDeltaMax'] / worst['bar']['rimContourDeltaMax']:.3e}")
say()

# ---------------------------------------------------------------------------
say("# 3. The reduced-transparency attestation, as the manifest carries it")
say()
manifest = json.loads((REFERENCE / "fixtures" / "manifest.json").read_text())
for profile in manifest["profiles"]:
    key = profile["profileKey"]
    if "reduced-transparency" not in key and "increased-contrast" not in key:
        continue
    attestation = profile.get("attestation")
    caveats = profile.get("caveats") or []
    say(f"  {key}")
    say(f"    a11yMode:    {profile.get('a11yMode')}")
    say(f"    attestation: {json.dumps(attestation) if attestation is not None else 'ABSENT'}")
    for caveat in caveats:
        say(f"    caveat:      {caveat}")
say()

# ---------------------------------------------------------------------------
say("# 4. The bounded metrics per profile, worst case beside the median")
say()
say("The adopted tables in test/adopted-thresholds.test.ts bound the PER-CELL value, so the")
say("native-to-native distribution is reported at its p90 and its max as well as its median.")
say("'allowance' is the 26.5 texture-tier row for the profile of the same name and 'dom' the")
say("dom-tier row beside it; a '>=' row is")
say("restated as the complement the native-delta metric measures, so every row reads 'lower is")
say("closer'. The allowance bounds vitrea against Apple, not Apple against Apple: it is here as")
say("the scale Decision Log 4 (c) reasons on, not as a bound anything is failing.")
say("Both columns are PARSED from the test file (2026-09-19 amendment, item 11); the dash marks")
say("a metric the dom table of that profile does not carry.")
say()
# The 26.5 texture-tier tables as the first run TRANSCRIBED them. Kept because a recorded
# number is corrected beside and never over: item 11 prints this against the file.
TRANSCRIBED_2026_09_19 = {
    "1x-light-standard": {
        "silhouetteIoUComplement": 1 - 0.82, "contourDistanceMeanPx": 2.5, "contourDistanceP95Px": 5.0,
        "ssimComplement": 1 - 0.88, "oklabDeltaEMean": 0.07, "oklabDeltaEP95": 0.17,
        "edgeWeightedMean": 0.11, "ssimOutsideComplement": 1 - 0.84,
    },
    "2x-light-standard": {
        "silhouetteIoUComplement": 1 - 0.85, "contourDistanceMeanPx": 5.0, "contourDistanceP95Px": 10.0,
        "ssimComplement": 1 - 0.89, "oklabDeltaEMean": 0.07, "oklabDeltaEP95": 0.17,
        "edgeWeightedMean": 0.12, "ssimOutsideComplement": 1 - 0.86,
    },
    "1x-dark-standard": {
        "silhouetteIoUComplement": 1 - 0.93, "contourDistanceMeanPx": 0.5, "contourDistanceP95Px": 1.5,
        "ssimComplement": 1 - 0.87, "oklabDeltaEMean": 0.09, "oklabDeltaEP95": 0.17,
        "edgeWeightedMean": 0.04, "ssimOutsideComplement": 1 - 0.83,
    },
    "2x-dark-standard": {
        "silhouetteIoUComplement": 1 - 0.93, "contourDistanceMeanPx": 1.0, "contourDistanceP95Px": 1.5,
        "ssimComplement": 1 - 0.88, "oklabDeltaEMean": 0.09, "oklabDeltaEP95": 0.17,
        "edgeWeightedMean": 0.04, "ssimOutsideComplement": 1 - 0.86,
    },
    "1x-light-reduced-transparency": {
        "silhouetteIoUComplement": 1 - 0.87, "contourDistanceMeanPx": 1.5, "contourDistanceP95Px": 3.5,
        "ssimComplement": 1 - 0.95, "oklabDeltaEMean": 0.04, "oklabDeltaEP95": 0.08,
        "edgeWeightedMean": 0.10, "ssimOutsideComplement": 1 - 0.93,
    },
    "1x-light-increased-contrast": {
        "silhouetteIoUComplement": 1 - 0.85, "contourDistanceMeanPx": 1.8, "contourDistanceP95Px": 11.5,
        "ssimComplement": 1 - 0.86, "oklabDeltaEMean": 0.06, "oklabDeltaEP95": 0.10,
        "edgeWeightedMean": 0.17, "ssimOutsideComplement": 1 - 0.80,
    },
}
BOUNDED = [
    "silhouetteIoUComplement", "contourDistanceMeanPx", "contourDistanceP95Px", "ssimComplement",
    "oklabDeltaEMean", "oklabDeltaEP95", "edgeWeightedMean", "ssimOutsideComplement",
]

TABLES, TABLE_NAMES = read_allowances()
ALLOWANCE = {name: tiers["texture"] for name, tiers in TABLES.items()}
DOM_ALLOWANCE = {name: tiers["dom"] for name, tiers in TABLES.items()}
say("The '(healthy)' columns drop the §4 cells whose two silhouettes differ by more than 2x, where")
say("the shape metrics are reading the extractor's threshold rather than a shape (claims §5.151 §4).")
say()


def healthy_row(r):
    pair = r["readings"]["silhouetteAreaPx"]
    small, large = min(pair), max(pair)
    return not (large > 0 and small < 0.5 * large)


for key in sorted({short(r["profileKey27"]) for r in rows}):
    subset = [r for r in rows if short(r["profileKey27"]) == key]
    fit = [r for r in subset if healthy_row(r)]
    say(f"  ## {key}  (n = {len(subset)} pairs, {len(fit)} of them healthy)"
        f"   tables: {TABLE_NAMES[key]['texture']}, {TABLE_NAMES[key]['dom']}")
    say(f"  {'metric':26s} {'n':>4s} {'median':>9s} {'p90':>9s} {'max':>9s} "
        f"{'p90 (healthy)':>14s} {'max (healthy)':>14s} {'allowance':>10s} {'p90/allow':>10s} "
        f"{'dom':>10s}")
    for metric in BOUNDED:
        values = [r["metrics"][metric] for r in subset if r["metrics"].get(metric) is not None]
        clean = [r["metrics"][metric] for r in fit if r["metrics"].get(metric) is not None]
        if not values:
            continue
        allow = ALLOWANCE[key][metric]
        dom = DOM_ALLOWANCE[key].get(metric)
        p90 = percentile(values, 0.90)
        say(f"  {metric:26s} {len(values):>4d} {median(values):>9.4f} {p90:>9.4f} "
            f"{max(values):>9.4f} {percentile(clean, 0.90):>14.4f} "
            f"{(max(clean) if clean else float('nan')):>14.4f} {allow:>10.4f} {p90 / allow:>10.2f} "
            f"{('—' if dom is None else f'{dom:.4f}'):>10s}")
    say()

# ---------------------------------------------------------------------------
say("# 5. The corner's direction over the healthy cells")
say()
DEGENERATE = 0.5
healthy, sick = [], []
for r in rows:
    pair = r["readings"]["silhouetteAreaPx"]
    small, large = min(pair), max(pair)
    (sick if large > 0 and small < DEGENERATE * large else healthy).append(r)
for label, subset, pose in (
    ("all rows, active, moved only", rows, "active"),
    ("all rows, inactive, moved only", rows, "inactive"),
    ("healthy rows, active, moved only", healthy, "active"),
    ("healthy rows, inactive, moved only", healthy, "inactive"),
):
    usable = [r for r in subset if r["pose"] == pose and r["readings"].get("cornerCurvaturePerPx")]
    moved = [r for r in usable if r["moved"].get("cornerCurvatureDeltaPerPx") is True]
    up = sum(1 for r in moved if r["readings"]["cornerCurvaturePerPx"][1] > r["readings"]["cornerCurvaturePerPx"][0])
    down = sum(1 for r in moved if r["readings"]["cornerCurvaturePerPx"][1] < r["readings"]["cornerCurvaturePerPx"][0])
    say(f"  {label:36s} n={len(usable):4d}  moved {len(moved):4d}  up/down {up}/{down}")
signed_all, signed_healthy = [], []
for label, subset, store in (("all", rows, signed_all), ("healthy", healthy, signed_healthy)):
    for r in subset:
        pair = r["readings"].get("cornerCurvaturePerPx")
        if pair:
            store.append(pair[1] - pair[0])
for label, store in (("all rows", signed_all), ("healthy rows", signed_healthy)):
    up = sum(1 for d in store if d > 0)
    down = sum(1 for d in store if d < 0)
    say(f"  {label:36s} n={len(store):4d}  up/down/tie {up}/{down}/{len(store) - up - down}  "
        f"median signed {median(store):+.3e}")
say()

# ---------------------------------------------------------------------------
say("# 7. The 55 cells whose 26.5 silhouette is the small one, by backdrop")
say()
tally = {}
for r in sick:
    a26, a27 = r["readings"]["silhouetteAreaPx"]
    if a26 < a27:
        tally[r["background"]] = tally.get(r["background"], 0) + 1
for name, count in sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])):
    say(f"    {name:20s} {count:4d}")
say(f"    {'total':20s} {sum(tally.values()):4d}")
say()

# ---------------------------------------------------------------------------
say("# 8. The highlight ratio's two ends")
say()
for pose in ("active", "inactive"):
    usable = [r for r in rows if r["pose"] == pose and r["readings"].get("highlightRatio")
              and "highlightRatioDelta" in r["bar"]]
    r26 = [r["readings"]["highlightRatio"][0] for r in usable]
    r27 = [r["readings"]["highlightRatio"][1] for r in usable]
    bins = [r["readings"]["highlightBins"] for r in usable if r["readings"].get("highlightBins")]
    floors = [[min(bins26), min(bins27)] for bins26, bins27 in bins]
    peaks = [[max(bins26), max(bins27)] for bins26, bins27 in bins]
    say(f"  {pose}: n={len(usable)}")
    say(f"    ratio  26.5 median {median(r26):8.3f}  27 median {median(r27):8.3f}  "
        f"26.5 max {max(r26):10.3f}  27 max {max(r27):10.3f}")
    say(f"    cells with a 27 ratio over 100: {sum(1 for v in r27 if v > 100)}; over 26.5: "
        f"{sum(1 for v in r26 if v > 100)}")
    say(f"    dimmest bin  26.5 median {median([f[0] for f in floors]):.4f}  "
        f"27 median {median([f[1] for f in floors]):.4f}")
    say(f"    brightest bin 26.5 median {median([p[0] for p in peaks]):.4f}  "
        f"27 median {median([p[1] for p in peaks]):.4f}")
say()

# ---------------------------------------------------------------------------
say("# 9. The brightest bin's angular shift, over all cells and over the moved ones")
say()
for pose in ("active", "inactive"):
    usable = [r for r in rows if r["pose"] == pose
              and r["metrics"].get("highlightPeakAngleDeltaDeg") is not None
              and "highlightPeakAngleDeltaDeg" in r["bar"]]
    moved = [r for r in usable if r["moved"].get("highlightPeakAngleDeltaDeg") is True]
    say(f"  {pose}: all n={len(usable)} median {median([r['metrics']['highlightPeakAngleDeltaDeg'] for r in usable]):.1f} deg;  "
        f"moved n={len(moved)} median {median([r['metrics']['highlightPeakAngleDeltaDeg'] for r in moved]):.1f} deg;  "
        f"moved max {max(r['metrics']['highlightPeakAngleDeltaDeg'] for r in moved):.1f} deg")
say()

# ---------------------------------------------------------------------------
say("# 10. The chroma population the hue was read on")
say()
with_hue = [r for r in rows if r["readings"].get("tintChroma") and r["metrics"].get("tintHueShiftDeltaDeg") is not None]
weak = [r for r in with_hue if max(r["readings"]["tintChroma"]) < 0.01]
strong = [r for r in with_hue if min(r["readings"]["tintChroma"]) >= 0.01]
crossing = [r for r in with_hue if r not in weak and r not in strong]
for label, subset in (("chroma < 0.01 on both beds", weak), ("chroma >= 0.01 on both beds", strong),
                      ("crossing 0.01 between beds", crossing)):
    hue = [r["metrics"]["tintHueShiftDeltaDeg"] for r in subset]
    say(f"  {label:30s} n={len(subset):4d}  median |hue shift| {median(hue):7.2f} deg")
say(f"  {'measurable population':30s} n={len(with_hue):4d}")
say()

# ---------------------------------------------------------------------------
say("# 11. The allowances audited against the test file (added 2026-09-19 by the G1c review closure)")
say()
say("Every texture-tier allowance the first run transcribed, beside the row the test file")
say("actually carries. 'file' is what read_allowances() parses now and what section 4 above")
say("uses; 'transcribed' is what the 2026-09-19 first run wrote and what review-closure.v1.txt")
say("and the tables copied from it were read against. A MISMATCH line is a number a decision may")
say("have cited: claims §5.151 §12 and the charter's Decision Log 4 (c) carry the correction.")
say()
mismatches = 0
for key in sorted(TRANSCRIBED_2026_09_19):
    for metric in BOUNDED:
        was = TRANSCRIBED_2026_09_19[key][metric]
        now = ALLOWANCE[key][metric]
        mark = "        " if abs(now - was) < 1e-12 else "MISMATCH"
        if mark == "MISMATCH":
            mismatches += 1
            say(f"  {mark} {key:32s} {metric:26s} transcribed {was:.4f}  file {now:.4f}")
say(f"  {mismatches} of {len(TRANSCRIBED_2026_09_19) * len(BOUNDED)} texture-tier rows differ; "
    f"the rest agree exactly.")
say()
say("The dom tier was never transcribed here at all, so it has nothing to differ from; it is")
say("parsed and printed beside the texture column in section 4 from now on.")
say()

text = "\n".join(out) + "\n"
(HERE / "review-closure.txt").write_text(text)
sys.stdout.write(text)
