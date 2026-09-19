"""W29 G2 — the four things `law-tables.txt` flags that a table cannot answer.

Run from `packages/calibration`:

    python3 results/2026-09-19-w29-g2-native-delta/read-checks.py

1. The backdrops behind each tone-response band, so the band boundaries name real scenes.
2. `rrect-64`'s curvature on 26.5, which the component table reports at kappa 338.9 — an
   implied corner radius of zero, which no declaration carries. Instrument or bed?
3. The hue reading, which is meaningless at near-zero chroma by `tintResponse`'s own
   documentation: the chroma the hue was read at, tinted and untinted apart.
4. The recede's `silhouetteAreaPx` row, whose difference of differences is 171 px on ten
   cells where every other reading is in the third decimal.
5. The population check 2 and 4 both turn out to be about: cells whose 26.5 silhouette is
   nearly empty because the 26.5 material sat within the extractor's 0.02 linear threshold
   of its own backdrop, and whose 27 silhouette is full. The shape axis is level-driven
   there (tech-debt-tracker, "the shape axis mis-segments a glowing interior over a
   near-tone backdrop"), so the geometry law has to be re-read with those cells named and
   set aside.
6. The level and tone laws read PER BACKDROP and mask-free. `interiorMean` is masked by
   the 26.5 silhouette, which is exactly what check 5 shows is unreliable where the 26.5
   material sat at its backdrop's level; `bodyLevel` — the declared box eroded six CSS px —
   needs no mask and is the honest reading there. The transfer fit's r-squared is printed
   beside its slope, because an affine fit against a photo backdrop is not the same claim
   as one against a checkerboard.
"""
import json, pathlib, statistics, sys

HERE = pathlib.Path(__file__).resolve().parent
rows = json.loads((HERE / "native-delta.json").read_text())["rows"]
recede = json.loads((HERE / "recede-delta.json").read_text())["rows"]
out = []


def say(line=""):
    out.append(line)


say("# 1. The backdrops behind each tone-response band")
say()
levels = {}
for r in rows:
    levels.setdefault(r["background"], r["backdropEncodedMean"])
for name, mean in sorted(levels.items(), key=lambda kv: kv[1]):
    say(f"  {mean:7.4f}  {name}")
say()

say("# 2. rrect-64's corner curvature")
say()
for r in rows:
    if r["component"] != "rrect-64":
        continue
    k = r["readings"]["cornerCurvaturePerPx"]
    if k is None:
        say(f"  {r['sceneId']}  curvature ABSENT: {'; '.join(r['notes'])}")
        continue
    say(
        f"  {r['profileKey27'].replace('apple-macos-27.0-','').replace('-glass0.5','')}/"
        f"{r['sceneId']}  kappa 26.5 {k[0]:.5f}  27 {k[1]:.5f}  "
        f"area 26.5 {r['readings']['silhouetteAreaPx'][0]}  27 {r['readings']['silhouetteAreaPx'][1]}  "
        f"IoU complement {r['metrics']['silhouetteIoUComplement']:.6f}"
    )
say()
say("  The same component's neighbours, for scale:")
for component in ("rrect-48", "rrect-80"):
    for r in rows:
        if r["component"] != component:
            continue
        k = r["readings"]["cornerCurvaturePerPx"]
        if k is None:
            say(f"  {component} {r['sceneId']}  curvature ABSENT")
            continue
        say(
            f"  {component} {r['sceneId']}  kappa 26.5 {k[0]:.5f}  27 {k[1]:.5f}  "
            f"area 26.5 {r['readings']['silhouetteAreaPx'][0]}  27 {r['readings']['silhouetteAreaPx'][1]}"
        )
say()

say("# 3. The chroma the hue shift was read at")
say()
for label, subset in (
    ("tinted", [r for r in rows if "-tint-" in r["sceneId"]]),
    ("untinted", [r for r in rows if "-tint-" not in r["sceneId"]]),
):
    chroma = [
        c
        for r in subset
        if r["readings"]["tintChroma"] is not None
        for c in r["readings"]["tintChroma"]
    ]
    hue = [
        r["metrics"]["tintHueShiftDeltaDeg"]
        for r in subset
        if r["metrics"]["tintHueShiftDeltaDeg"] is not None
    ]
    say(
        f"  {label:9s} n={len(subset):4d}  median interior chroma {statistics.median(chroma):.6f}  "
        f"median |hue shift delta| {statistics.median(hue):.3f} deg"
    )
say()
say("  Cells whose interior chroma is under 0.01 on BOTH beds — where a hue is not defined:")
weak = [
    r
    for r in rows
    if r["readings"]["tintChroma"] is not None
    and max(r["readings"]["tintChroma"]) < 0.01
    and r["metrics"]["tintHueShiftDeltaDeg"] is not None
]
strong = [
    r
    for r in rows
    if r["readings"]["tintChroma"] is not None
    and min(r["readings"]["tintChroma"]) >= 0.01
    and r["metrics"]["tintHueShiftDeltaDeg"] is not None
]
for label, subset in (("chroma < 0.01", weak), ("chroma >= 0.01", strong)):
    if not subset:
        continue
    hue = [r["metrics"]["tintHueShiftDeltaDeg"] for r in subset]
    moved = sum(1 for r in subset if r["moved"].get("tintHueShiftDeltaDeg"))
    say(
        f"  {label:16s} n={len(subset):4d}  moved {moved:4d}  median |hue shift delta| "
        f"{statistics.median(hue):.3f} deg"
    )
say()

say("# 4. The recede's silhouette-area row")
say()
for r in recede:
    value = r["deltaOfRecede"].get("silhouetteAreaPx")
    if value is None:
        continue
    say(
        f"  {r['profileKey27'].replace('apple-macos-27.0-','').replace('-glass0.5','')}/"
        f"{r['inactiveSceneId']}  recede 26.5 {r['recede26']['silhouetteAreaPx']:8.1f}  "
        f"27 {r['recede27']['silhouetteAreaPx']:8.1f}  difference {value:8.1f}  "
        f"bar {r['bar'].get('silhouetteAreaPx', float('nan')):.1f}"
    )
say()

say("# 5. The cells whose silhouette is level-driven, and the geometry law without them")
say()
DEGENERATE = 0.5  # of the other bed's area; below this the extraction, not the shape, moved
sick, healthy = [], []
for r in rows:
    pair = r["readings"]["silhouetteAreaPx"]
    small, large = min(pair), max(pair)
    (sick if large > 0 and small < DEGENERATE * large else healthy).append(r)
say(f"  {len(sick)} of {len(rows)} cells have one bed's silhouette under half the other's.")
say("  Their backdrops, and which bed is the small one:")
tally = {}
for r in sick:
    a26, a27 = r["readings"]["silhouetteAreaPx"]
    key = (r["background"], "26.5 small" if a26 < a27 else "27 small")
    tally[key] = tally.get(key, 0) + 1
for (bg, which), n in sorted(tally.items(), key=lambda kv: -kv[1]):
    say(f"    {bg:20s} {which:11s} {n:4d}")
say()
say("  The geometry law, healthy cells only (both silhouettes within 2x of each other):")
for metric in ("silhouetteIoUComplement", "contourDistanceMeanPx", "silhouetteAreaDeltaPx", "cornerCurvatureDeltaPerPx"):
    usable = [r for r in healthy if r["metrics"].get(metric) is not None and metric in r["bar"]]
    if not usable:
        continue
    moved = sum(1 for r in usable if r["moved"].get(metric))
    values = sorted(r["metrics"][metric] for r in usable)
    ratios = sorted(r["metrics"][metric] / r["bar"][metric] for r in usable if r["bar"][metric] > 0)
    worst = max(usable, key=lambda r: r["metrics"][metric])
    say(
        f"    {metric:28s} moved {moved:4d}/{len(usable):4d}  median {statistics.median(values):.4e}  "
        f"median delta/bar {(statistics.median(ratios) if ratios else float('nan')):9.2f}  "
        f"worst {worst['metrics'][metric]:.4e} on {worst['sceneId']}"
    )
say()
say("  And the interior level on the cells the extractor lost, which is what moved there:")
lost = [r for r in sick if r["readings"]["silhouetteAreaPx"][0] < r["readings"]["silhouetteAreaPx"][1]]
if lost:
    lift = sorted(r["readings"]["interiorMean"][1] - r["readings"]["interiorMean"][0] for r in lost if r["readings"]["interiorMean"])
    say(f"    {len(lost)} cells, median 27-minus-26.5 interior level {statistics.median(lift):+.5f} linear")

say("# 6. The level and tone laws per backdrop AND per pose, mask-free where it matters")
say()
say(
    "  Split by pose, and reported as percentiles of the PER-CELL signed difference rather"
)
say(
    "  than as each bed's own median: over `impulse` active the two beds' medians are 0.007"
)
say(
    "  and 0.234 while the median per-cell difference is +0.008, because the cell at one"
)
say(
    "  bed's median is not the cell at the other's. The difference is the measurement and"
)
say(
    "  each bed's median is only context. `bodyLevel` is the declared box eroded six"
)
say("  CSS px and needs no silhouette, which is what makes it usable where check 5 is not.")
say()
for pose in ("active", "inactive"):
    say(f"  ## pose: {pose}")
    say(
        f"  {'backdrop':18s} {'level':>7s} {'n':>4s} {'dBody p10':>10s} {'p50':>9s} "
        f"{'p90':>9s} {'up/down':>9s} {'slope 26.5':>11s} {'27':>8s} {'r2 26.5':>8s} {'r2 27':>7s}"
    )
    for name, mean in sorted(levels.items(), key=lambda kv: kv[1]):
        subset = [r for r in rows if r["background"] == name and r["pose"] == pose]
        bodies = [r["readings"]["bodyLevel"] for r in subset if r["readings"]["bodyLevel"]]
        if not bodies:
            continue
        signed = sorted(b[1] - b[0] for b in bodies)
        up = sum(1 for b in bodies if b[1] > b[0])
        slopes = [r["readings"]["transferSlope"] for r in subset if r["readings"]["transferSlope"]]
        r2s = [r["readings"]["transferR2"] for r in subset if r["readings"]["transferR2"]]
        slope26 = statistics.median(s0 for s0, _ in slopes) if slopes else float("nan")
        slope27 = statistics.median(s1 for _, s1 in slopes) if slopes else float("nan")
        r226 = statistics.median(s0 for s0, _ in r2s) if r2s else float("nan")
        r227 = statistics.median(s1 for _, s1 in r2s) if r2s else float("nan")
        pick = lambda q: signed[min(len(signed) - 1, int(q * len(signed)))]
        say(
            f"  {name:18s} {mean:7.4f} {len(bodies):4d} "
            f"{pick(0.10):+10.5f} {pick(0.50):+9.5f} {pick(0.90):+9.5f} {up:4d}/{len(bodies) - up:<4d} "
            f"{slope26:11.4f} {slope27:8.4f} {r226:8.3f} {r227:7.3f}"
        )
    say()
say("  The body level over the whole bed, per pose:")
for pose in ("active", "inactive"):
    bodies = [r["readings"]["bodyLevel"] for r in rows if r["pose"] == pose and r["readings"]["bodyLevel"]]
    signed = sorted(b[1] - b[0] for b in bodies)
    up = sum(1 for b in bodies if b[1] > b[0])
    say(
        f"    {pose:9s} n={len(bodies):4d}  median signed {statistics.median(signed):+.5f}  "
        f"up/down {up}/{len(bodies) - up}  p05 {signed[len(signed)//20]:+.5f}  p95 {signed[-max(1,len(signed)//20)]:+.5f}"
    )
say()

text = "\n".join(out) + "\n"
(HERE / "read-checks.txt").write_text(text)
sys.stdout.write(text)
