#!/usr/bin/env python3
"""W19 G1: the whole-bed dry run read against the W18 bed under Decision Log 3's stops.

    python3 verify-dry.py <dry matrix> <dry captures dir> --bed <bed calibration package root>
                          [--moved <dir of moved-<profile>.json>] [--predict <dir>] [--label dry]

W18 G1's script with its stops re-aimed. The bed is an ARGUMENT for the reason it was there: this
runs from a branch in a worktree and the bed it compares against is the main checkout's, so a
hardcoded path would compare the branch with itself. Nothing canonical is written.

## The division of labour

X6 says the LANDING's gate runs `adopted-thresholds.test.ts` against this matrix through
`VITREA_MATRIX_PATH`, so **S2's bounds and floors and S7's conditioning predicate are that file's**
and are not restated here; the floors' rows are printed as a reading with their pinned values
parsed out of it. What this script owns is what that file cannot see: the GPU tier's byte identity
(S1) and the stops that are statements about a DIFFERENCE — between the two runs, or between the
two tiers (S3, S4, S5, S6).

The pixel half of S3 is `moved.ts`'s, run per profile before this script and read from JSON here,
because classifying a differing pixel against the declared component region eroded by two device
pixels needs the harness's own region rasteriser and not a second copy of it.

## What Decision Log 3 declared, and how it is read

  S1  every GPU row within 0.0002 of the W18 bed and every GPU capture byte-identical to it.
  S3  every UNTINTED CSS capture byte-identical to the W18 bed's; every FULL-STRENGTH tinted cell
      within 0.0005 in the interior mean with its differing pixels confined to the contour ring
      (none in the region eroded by two device pixels), per cell.
  S4  the bed's twelve tinted scenes. On the light-standard profiles, `CSS − GPU` within 0.005.
      On the fold profiles, ruling (1): `(CSS − GPU)_tinted − (1 − s)·(CSS − GPU)_untinted` within
      0.01 — the fold's own algebra, since a tinted surface sees `(1 − s)` of whatever the
      untinted material's gap to the renderer is and `s` of a layer both tiers agree on. On the
      dark-scheme profiles the tinted cells must be byte-identical, which is the encoded form's
      untouchedness proved by bytes rather than asserted.
  S5  the `orange-half` cells against `predFold + c`, within 0.005, with the clamp share beside
      them to four places; a miss is carried by name with the alpha-dependence attribution
      (pre-check §5) and the clause is not loosened. The clamp-share stop reads "under 0.1 % of
      masked channel samples".
  S6  the cross-tier OKLab ΔE mean and the level ratio, per profile, down or flat.
"""
import argparse
import hashlib
import json
import os
import re

ap = argparse.ArgumentParser()
ap.add_argument("matrix")
ap.add_argument("captures")
ap.add_argument("--bed", required=True, help="the calibration package root holding the W18 bed")
ap.add_argument("--moved", default=None, help="a directory of moved-<profileKey>.json (S3's pixels)")
ap.add_argument("--predict", default=None, help="a directory of predict-<profileKey>.json (S5)")
ap.add_argument("--label", default="dry")
args = ap.parse_args()
BED = args.bed


def load(path):
    """`(profile, renderer, scene) -> cell`, the most recently captured row winning."""
    best = {}
    for c in json.load(open(path))["cells"]:
        k = (c["key"]["profileKey"], c["key"]["web"]["renderer"], c["key"]["sceneId"])
        if k not in best or c["capturedAt"] > best[k]["capturedAt"]:
            best[k] = c
    return best


bed = load(os.path.join(BED, "results", "matrix.json"))
dry = load(args.matrix)


def v(c, ax, k):
    if c is None:
        return None
    x = (c.get(ax) or {}).get(k)
    return None if x is None else (x["value"] if isinstance(x, dict) else x)


f = lambda x: "   —  " if x is None else f"{x:.4f}"
sd = lambda a, b: "   —   " if a is None or b is None else f"{a - b:+.4f}"

P = "apple-macos-26.5-"
L1, L2, D1, D2 = P + "1x-light-standard", P + "2x-light-standard", P + "1x-dark-standard", P + "2x-dark-standard"
IC, RT = P + "1x-light-increased-contrast", P + "1x-light-reduced-transparency"
LIGHT_STANDARD = (L1, L2)
DARK = (D1, D2)
FOLD = (IC, RT)
ALL = (L1, L2, IC, RT, D1, D2)
BOUNDS = {L1: (0.90, 0.08), L2: (0.92, 0.08), D1: (0.83, 0.09), D2: (0.85, 0.09), RT: (0.91, 0.04), IC: (0.83, 0.07)}

_SCENES = json.load(open(os.path.join(BED, "..", "..", "apps", "reference-apple", "scenes.json")))
TINTS = _SCENES["tints"]
SCENE_TINT = {s["id"]: s["tint"] for s in _SCENES["scenes"] if s.get("tint")}


def strength_of(scene):
    tint = SCENE_TINT.get(scene)
    return None if tint is None else TINTS[tint].get("alpha", 1.0)


def untinted_base(scene):
    """`checkerboard__capsule-button__rest-tint-orange` -> `checkerboard__capsule-button__rest`."""
    return scene.split("-tint-")[0]


verdict = {}
notes = []


def stop(name, ok, note_text=""):
    verdict[name] = verdict.get(name, True) and ok
    if not ok:
        print(f"  STOP {name}: {note_text}")


def note(text):
    notes.append(text)
    print(f"  note: {text}")


def floors():
    """The pinned `ssimMean` floors, parsed out of the landing's own gate rather than restated."""
    source = open(os.path.join(BED, "test", "adopted-thresholds.test.ts")).read()
    out = {}
    for key, measured, floor in re.findall(
        r'"(dom / \w+ / [\w-]+ / [\w.-]+) :: ssimMean":\s*\{\s*measured:\s*([\d.]+),\s*floor:\s*([\d.]+)', source
    ):
        _, _, scene, profile = key.split(" / ")
        out[(profile, scene)] = (float(measured), float(floor))
    return out


FLOORS = floors()


def rows(prof, renderer="css"):
    keys = sorted(k for k in bed if k[0] == prof and k[1] == renderer)
    return [(k, bed[k], dry.get(k)) for k in keys]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).digest()


def capture_pair(prof, scene, tier):
    rel = os.path.join(prof, scene, f"{scene}__{tier}.png")
    return os.path.join(BED, "web-captures", rel), os.path.join(args.captures, rel)


# ---------------------------------------------------------------------------
# S1 — the GPU tier byte-identical to the W18 bed, every row within 0.0002
# ---------------------------------------------------------------------------
print(f"== S1 · the GPU tier against the W18 bed ({args.label})")
METRICS = [
    ("perceptual", "ssimMean"), ("perceptual", "ssimBand"), ("perceptual", "ssimInterior"),
    ("perceptual", "ssimOutside"), ("perceptual", "oklabDeltaEMean"),
    ("material", "interiorStdDevWeb"), ("material", "interiorMeanWeb"), ("shape", "silhouetteIoU"),
]
same = diff = missing = 0
worst = 0.0
for (prof, rend, scene), c in sorted(bed.items()):
    if rend != "webgpu":
        continue
    d = dry.get((prof, rend, scene))
    if d is None:
        missing += 1
        continue
    for ax, m in METRICS:
        a, b = v(d, ax, m), v(c, ax, m)
        if a is None or b is None:
            continue
        worst = max(worst, abs(a - b))
        if abs(a - b) > 0.0002:
            stop("S1", False, f"{m} {scene} @ {prof}: {a:.5f} vs bed {b:.5f}")
    a, b = capture_pair(prof, scene, "webgpu")
    if os.path.exists(a) and os.path.exists(b):
        if sha(a) == sha(b):
            same += 1
        else:
            diff += 1
            stop("S1", False, f"capture differs: {scene} @ {prof}")
print(f"  GPU captures byte-identical {same}, differing {diff}, rows not compared {missing}; "
      f"worst row |Δ| {worst:.6f}")
verdict.setdefault("S1", True)

# ---------------------------------------------------------------------------
# S3 — the CSS captures: untinted byte-identical, full strength on the contour ring only
# ---------------------------------------------------------------------------
print(f"\n== S3 · the CSS captures against the W18 bed")
untinted_same = untinted_diff = 0
for (prof, rend, scene), c in sorted(bed.items()):
    if rend != "css" or "-tint-" in scene:
        continue
    a, b = capture_pair(prof, scene, "css")
    if not (os.path.exists(a) and os.path.exists(b)):
        continue
    if sha(a) == sha(b):
        untinted_same += 1
    else:
        untinted_diff += 1
        stop("S3", False, f"untinted capture moved: {scene} @ {prof[16:]}")
print(f"  untinted CSS captures byte-identical {untinted_same}, differing {untinted_diff}")

moved_rows = {}
if args.moved is not None:
    for prof in ALL:
        path = os.path.join(args.moved, f"moved-{prof}.json")
        if not os.path.exists(path):
            continue
        for row in json.load(open(path)):
            if "identical" in row:
                moved_rows[(prof, row["scene"])] = row

print("  full-strength tinted cells (and the dark scheme's, which must be byte-identical):")
print("    profile                        scene                                          state")
for prof in ALL:
    for (p, r, scene), b, d in rows(prof):
        if "-tint-" not in scene:
            continue
        s = strength_of(scene)
        row = moved_rows.get((prof, scene))
        a_path, b_path = capture_pair(prof, scene, "css")
        identical = (os.path.exists(a_path) and os.path.exists(b_path) and sha(a_path) == sha(b_path))
        if prof in DARK:
            state = "BYTE-IDENTICAL" if identical else "MOVED"
            stop("S3", identical, f"dark-scheme tinted capture moved: {scene} @ {prof[16:]} "
                                  f"— the encoded form must be untouched")
        elif s == 1.0:
            if identical:
                state = "BYTE-IDENTICAL"
            elif row is None:
                state = "differs, not classified (no moved-*.json)"
                stop("S3", False, f"{scene} @ {prof[16:]} differs and was not classified")
            else:
                state = (f"differing {row['differingPixels']} px, {row['differingInRegion']} in region, "
                         f"{row['differingInErodedInterior']} in the eroded interior, worst code "
                         f"{row['worstChannelCode']}, interior mean {row['interiorMeanMove']:+.5f}")
                stop("S3", row["differingInErodedInterior"] == 0 and abs(row["interiorMeanMove"]) <= 0.0005,
                     f"{scene} @ {prof[16:]} moved {row['interiorMeanMove']:+.5f} with "
                     f"{row['differingInErodedInterior']} pixels off the contour ring")
        else:
            # The bed's one sub-unit rung. It is not gated by S3 — the whole point of the wave is
            # that it moves — and is printed so the move is on the record beside the cells that
            # must not move.
            move = None if row is None else row["interiorMeanMove"]
            state = f"sub-unit s={s}: interior mean " + ("—" if move is None else f"{move:+.5f}")
        print(f"    {prof[16:]:30s} {scene:44s} {state}")
verdict.setdefault("S3", True)

# ---------------------------------------------------------------------------
# The CSS tier, per profile — the full reading, with S4 and S6 gated inside it
# ---------------------------------------------------------------------------
for prof in ALL:
    sb, de = BOUNDS[prof]
    print(
        f"\n== CSS tier · {prof[16:]} — ssimMean bed→{args.label} Δ | bound/floor | ΔE bed→{args.label} | "
        f"level bed→{args.label} / GPU / native | CSS−GPU | move | xtier ΔE bed→{args.label} | ratio"
    )
    for (p, r, scene), b, d in rows(prof):
        if d is None:
            print(f"  {scene:44s} not captured ({b['fixtureSet']})")
            continue
        gpu = dry.get((prof, "webgpu", scene))
        pinned = FLOORS.get((prof, scene))
        bound = f"floor {pinned[1]:.4f}" if pinned else f"≥ {sb}"
        s0, s1 = v(b, "perceptual", "ssimMean"), v(d, "perceptual", "ssimMean")
        limit = pinned[1] if pinned else sb
        ok = s1 is not None and s1 >= limit
        m0, m1 = v(b, "material", "interiorMeanWeb"), v(d, "material", "interiorMeanWeb")
        g1 = v(gpu, "material", "interiorMeanWeb")
        moved = None if m0 is None or m1 is None else m1 - m0
        print(
            f"  {scene:44s} {b['fixtureSet'][:4]} {f(s0)}→{f(s1)} {sd(s1, s0)} | {bound:14s} "
            f"{'ok ' if ok else 'MISS'} | "
            f"{f(v(b, 'perceptual', 'oklabDeltaEMean'))}→{f(v(d, 'perceptual', 'oklabDeltaEMean'))} | "
            f"{f(m0)}→{f(m1)} / {f(g1)} / {f(v(d, 'material', 'interiorMeanNative'))} | {sd(m1, g1)} | "
            f"{'   —   ' if moved is None else f'{moved:+.4f}'} | "
            f"{f(v(b, 'coherence', 'crossTierOklabDeltaEMean'))}→{f(v(d, 'coherence', 'crossTierOklabDeltaEMean'))} | "
            f"{f(v(d, 'coherence', 'interiorLevelRatioGpuOverCss'))}"
        )
        if pinned is not None and s1 is not None and s1 < pinned[1]:
            note(f"S2 reading: {scene} @ {prof[16:]} ssimMean {s1:.5f} below its pinned floor {pinned[1]:.5f}")

        # -- S4, on the bed's twelve tinted scenes only ----------------------------------------
        if "-tint-" in scene and m1 is not None and g1 is not None:
            gap = m1 - g1
            s = strength_of(scene) or 1.0
            if prof in LIGHT_STANDARD:
                stop("S4", abs(gap) <= 0.005,
                     f"{scene} @ {prof[16:]} CSS−GPU {gap:+.4f} (clause 0.005)")
            elif prof in FOLD:
                base = untinted_base(scene)
                bm = v(dry.get((prof, "css", base)), "material", "interiorMeanWeb")
                bg = v(dry.get((prof, "webgpu", base)), "material", "interiorMeanWeb")
                if bm is None or bg is None:
                    note(f"S4 fold: {scene} @ {prof[16:]} has no untinted control on this profile "
                         f"— CSS−GPU {gap:+.4f} recorded")
                else:
                    residual = gap - (1 - s) * (bm - bg)
                    stop("S4", abs(residual) <= 0.01,
                         f"{scene} @ {prof[16:]} CSS−GPU {gap:+.4f} against (1−s)·untinted "
                         f"{(1 - s) * (bm - bg):+.4f} — residual {residual:+.4f} (Decision Log 3 (1), 0.01)")
                    note(f"S4 fold reading: {scene} @ {prof[16:]} CSS−GPU {gap:+.4f}, "
                         f"(1−s)·untinted {(1 - s) * (bm - bg):+.4f}, residual {residual:+.4f}")
            # the dark profiles' tinted cells are gated by bytes in S3, above.
            if b["fixtureSet"] == "holdout":
                bg0 = v(bed.get((prof, "webgpu", scene)), "material", "interiorMeanWeb")
                note(f"holdout recorded (X8): {scene} @ {prof[16:]} CSS−GPU {gap:+.4f} "
                     f"(bed {sd(m0, bg0).strip()})")

        # -- every cell's other adopted metrics, and a cell leaving W17's 0.01 clause -----------
        for ax, metric in (("perceptual", "ssimInterior"), ("perceptual", "oklabDeltaEMean"),
                           ("shape", "silhouetteIoU")):
            a0, a1 = v(b, ax, metric), v(d, ax, metric)
            if a0 is None or a1 is None:
                continue
            if abs(a1 - a0) > 0.002:
                note(f"metric moved: {scene} @ {prof[16:]} {metric} {a0:.4f} → {a1:.4f} ({a1 - a0:+.4f})")
        if m1 is not None and g1 is not None and abs(m1 - g1) > 0.01:
            note(f"W17's 0.01 cross-tier clause left: {scene} @ {prof[16:]} at {m1 - g1:+.4f}")
verdict.setdefault("S4", True)

# ---------------------------------------------------------------------------
# S5 — the `orange-half` cells against predFold + c
# ---------------------------------------------------------------------------
print("\n== S5 · the bed's sub-unit rungs against predFold + c")
if args.predict is None:
    print("  no --predict directory given; S5 not read")
else:
    for prof in ALL:
        path = os.path.join(args.predict, f"predict-{prof}.json")
        if not os.path.exists(path):
            continue
        by = {r["scene"]: r for r in json.load(open(path)) if "measuredCss" in r}
        for scene, row in sorted(by.items()):
            s = strength_of(scene)
            if s is None or s >= 1.0:
                continue
            # `c` is this cell's own decoration constant, read at `s = 1` on the same backdrop
            # and scale — the same background's full-strength cell (pre-check §5, G0 §4).
            full = by.get(f"{untinted_base(scene)}-tint-orange")
            if full is None:
                note(f"S5: {scene} @ {prof[16:]} has no full-strength twin on this profile")
                continue
            c = full["measuredCss"] - full["predictedFold"]
            miss = row["measuredCss"] - (row["predictedFold"] + c)
            print(f"  {prof[16:]:28s} {scene:44s} measured {row['measuredCss']:.5f}  "
                  f"predFold {row['predictedFold']:.5f}  c {c:+.5f}  miss {miss:+.5f}  "
                  f"clamp today {row['clampedChannelShareToday']*100:.4f}%  "
                  f"clamp fold {row['clampedChannelShareFold']*100:.4f}%")
            # Gated on the light-standard profiles only. `predict.ts` resolves the surface under
            # the NOMINAL policy, so its prediction is a number for a different surface on the two
            # fold profiles — G0's Deferred already names that — and those rows are recorded.
            if prof in LIGHT_STANDARD:
                stop("S5", abs(miss) <= 0.005,
                     f"{scene} @ {prof[16:]} miss {miss:+.5f} against the clause's 0.005 — "
                     f"the decoration constant is α″-dependent (pre-check §5)")
                stop("S5", row["clampedChannelShareFold"] * 100 < 0.1,
                     f"{scene} @ {prof[16:]} clamp share under the fold "
                     f"{row['clampedChannelShareFold']*100:.4f}% is not under 0.1%")
            else:
                note(f"S5 recorded, not gated: {scene} @ {prof[16:]} miss {miss:+.5f} — the "
                     f"prediction resolves under the nominal policy (G0 Deferred)")
verdict.setdefault("S5", True)

# ---------------------------------------------------------------------------
# S6 — coherence: the cross-tier ΔE not up on any profile, the level ratio in band
# ---------------------------------------------------------------------------
print(f"\n== S6 · cross-tier coherence")
for prof in ALL:
    xs = [
        (v(b, "coherence", "crossTierOklabDeltaEMean"), v(d, "coherence", "crossTierOklabDeltaEMean"))
        for (p, r, s), b, d in rows(prof)
        if d is not None and b["fixtureSet"] != "holdout"
    ]
    xs = [(a, c) for a, c in xs if a is not None and c is not None]
    if not xs:
        print(f"  {prof[16:]:28s} no paired cells")
        continue
    m0, m1 = sum(a for a, _ in xs) / len(xs), sum(c for _, c in xs) / len(xs)
    print(f"  {prof[16:]:28s} cross-tier ΔE bed {m0:.5f} → {args.label} {m1:.5f}  ({len(xs)} cells)")
    stop("S6", m1 <= m0 + 1e-9, f"cross-tier ΔE rose @ {prof[16:]}: {m0:.5f} → {m1:.5f}")
worstratio = None
for prof in ALL:
    for (p, r, scene), b, d in rows(prof):
        lr = v(d, "coherence", "interiorLevelRatioGpuOverCss")
        if lr is None:
            continue
        if worstratio is None or abs(lr - 1) > abs(worstratio[0] - 1):
            worstratio = (lr, scene, prof)
        lr0 = v(b, "coherence", "interiorLevelRatioGpuOverCss")
        outside_bed = lr0 is not None and not (0.97 <= lr0 <= 1.03)
        stop("S6", 0.97 <= lr <= 1.03 or outside_bed,
             f"{scene} @ {prof[16:]} level ratio {lr:.4f} left 0.97–1.03 (bed {f(lr0)})")
        if not (0.97 <= lr <= 1.03) and outside_bed:
            note(f"S6 reading (standing): {scene} @ {prof[16:]} level ratio {lr:.4f}, bed {lr0:.4f}")
if worstratio is not None:
    print(f"  worst level ratio {worstratio[0]:.4f} on {worstratio[1]} @ {worstratio[2][16:]}")

# ---------------------------------------------------------------------------
# The tinted cells' ΔE, before and after, in both measures
# ---------------------------------------------------------------------------
print("\n== the bed's tinted cells · ΔE against native and against the GPU tier, bed → dry")
print("  profile                        scene                                        native ΔE          cross-tier ΔE")
for prof in ALL:
    for (p, r, scene), b, d in rows(prof):
        if "-tint-" not in scene or d is None:
            continue
        print(f"  {prof[16:]:30s} {scene:44s} "
              f"{f(v(b, 'perceptual', 'oklabDeltaEMean'))}→{f(v(d, 'perceptual', 'oklabDeltaEMean'))} "
              f"{sd(v(d, 'perceptual', 'oklabDeltaEMean'), v(b, 'perceptual', 'oklabDeltaEMean'))}   "
              f"{f(v(b, 'coherence', 'crossTierOklabDeltaEMean'))}→"
              f"{f(v(d, 'coherence', 'crossTierOklabDeltaEMean'))} "
              f"{sd(v(d, 'coherence', 'crossTierOklabDeltaEMean'), v(b, 'coherence', 'crossTierOklabDeltaEMean'))}")

print("\n== verdicts")
for k, ok in sorted(verdict.items()):
    print(f"  {k}: {'met' if ok else 'FIRED'}")
print(f"  ({len(notes)} note(s) above; S2's bounds and floors and S7's predicate are "
      f"adopted-thresholds.test.ts's, X6)")
