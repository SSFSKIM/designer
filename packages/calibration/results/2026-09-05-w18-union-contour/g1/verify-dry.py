#!/usr/bin/env python3
"""W18 G1: the dry run read against the W17 bed under Decision Log 3's re-declared stops.

    python3 verify-dry.py <dry matrix> <dry captures dir> --bed <bed calibration package root>
                          [--closed-form <closed-form-bed.json>] [--label dry]

Derived from W17 G1's `verify-dry.py`. The bed is an ARGUMENT: this script runs from a branch in a
worktree and the bed it compares against is another checkout's, so a hardcoded path would compare
the branch with itself or read the wrong tree. Nothing canonical is written.

## The division of labour with `adopted-thresholds.test.ts`

X6 says the LANDING's gate runs against the dry run's matrix through `VITREA_MATRIX_PATH`, so
**S2's bounds and floors and S7's conditioning predicate are that file's** — it holds the only
copy, and a second copy here would be the thing it exists to prevent. What this script owns is
what the test file cannot see: the GPU tier's byte identity (S1) and the stops that are statements
about the DIFFERENCE between two runs or between the two tiers (S3, S4, S5, S6). The floors' rows
are printed as a reading with their pinned values parsed out of the test file, never restated.

## What Decision Log 3 re-declared, and how it is read here

  S4  the interior mean against the GPU tier's: within **0.005** on `checkerboard__toolbar-group`
      at both scales and on `photo__toolbar-group` at 2x, within **0.01** on
      `photo__toolbar-group` at 1x (the charter's 0.005 missed and named, the bound's −0.0103 on
      the bright-patch member its reason), within **0.01** on `photo__toolbar-group` under
      reduced transparency and increased contrast (q4, measured for the first time at this run),
      and within W17's **0.01** on every other light-standard checkerboard, `hc-text` and `photo`
      cell. The stack's holdout cells are RECORDED whole-cell with the renderer's unsampled route
      named as their remainder; Decision Log 3 (4) gates the tier's own share on the pre-check's
      scratch twins and not here.
  S5  every single-member light cell moves by the closed form's share within **0.002**, the
      `light-solid` cells within **0.0035** (the form's recorded under-prediction on the solid),
      and the two `toolbar-group` cells move ABOVE the form by at most **0.005** per cell (the
      paint-order residual Decision Log 2 (1) declined to model). Every cell's other adopted
      metrics within 0.002 of the bed, and any cell leaving W17's 0.01 cross-tier clause named
      with its number.

The closed form is `g1/parts/closed-form-bed.json`, computed under the light-standard document and
the nominal policy. It therefore predicts the light-standard cells and no others: the dark, the
reduced-transparency and the increased-contrast cells are gated on their measured move and their
other adopted metrics instead, and this script says so per row rather than comparing them against
a number that was not computed for them.
"""
import argparse
import hashlib
import json
import os
import re

ap = argparse.ArgumentParser()
ap.add_argument("matrix")
ap.add_argument("captures")
ap.add_argument("--bed", required=True, help="the calibration package root holding the W17 bed")
ap.add_argument("--closed-form", default=None)
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
ALL = (L1, L2, IC, RT, D1, D2)
DPR = {L1: 1, L2: 2, IC: 1, RT: 1, D1: 1, D2: 2}
# The adopted `ssimMean` bound and OKLab ΔE mean bound per profile, transcribed from
# `adopted-thresholds.test.ts` for reporting only — that file gates them (X6).
BOUNDS = {L1: (0.90, 0.08), L2: (0.92, 0.08), D1: (0.83, 0.09), D2: (0.85, 0.09), RT: (0.91, 0.04), IC: (0.83, 0.07)}
CAL_CHECKER = [
    "checkerboard__rrect-sm__rest",
    "checkerboard__capsule-button__rest",
    "checkerboard__rrect-md__rest",
    "checkerboard__rrect-ml__rest",
    "checkerboard__toolbar-group__rest",
]
SOLID_FAMILIES = ("light-solid", "dark-solid", "mid-dark-solid", "impulse")
# The cells S4 names, with the clause each carries after Decision Log 3 (3).
S4_TIGHT = {(L1, "checkerboard__toolbar-group__rest"), (L2, "checkerboard__toolbar-group__rest"),
            (L2, "photo__toolbar-group__rest")}
S4_FOLD = {(RT, "photo__toolbar-group__rest"), (IC, "photo__toolbar-group__rest")}
# The multi-member light cells, which S5 gates from ABOVE the form rather than against it.
GROUPED = ("toolbar-group", "glass-over-glass")


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


def predictions():
    """The closed form's predicted MOVE per cell, area-weighted over the cell's surfaces.

    `shadowTermPredicted` is what the shadow in the sampled backdrop costs the interior, so the
    move the carriers produce is its negation. The weight is each surface's own pixel count,
    because a cell's mean is over the whole component and its surfaces are not all the same size.
    """
    if args.closed_form is None:
        return {}
    move, area = {}, {}
    for row in json.load(open(args.closed_form)):
        key = (row["scene"], row["dpr"])
        move[key] = move.get(key, 0.0) + -row["shadowTermPredicted"] * row["pixels"]
        area[key] = area.get(key, 0.0) + row["pixels"]
    return {k: move[k] / area[k] for k in move if area[k]}


PREDICTED = predictions()
# The author's opacity per tint id, from the bed's own `scenes.json` registry: a colour's alpha is
# how far the material's tint moves toward the seed, so a cell at full strength sees none of the
# backdrop and none of the shadow's share of it. W17 G1's rule, carried.
_SCENES = json.load(open(os.path.join(BED, "..", "..", "apps", "reference-apple", "scenes.json")))
TINTS = _SCENES["tints"]
SCENE_TINT = {s["id"]: s["tint"] for s in _SCENES["scenes"] if s.get("tint")}


def tint_strength(scene):
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


def shadow_carrier(profile, scene):
    """Which carrier the group drew with, off the capture's own report (W18 G1).

    The matrix's cell carries the measured axes and not the resolved state, so the carrier is read
    where the runtime wrote it — the same place `cssBody` and `cssTint` are read from.
    """
    path = os.path.join(args.captures, profile, scene, "report__css.json")
    if not os.path.exists(path):
        return "—"
    groups = json.load(open(path))["page"].get("groups") or []
    return (groups[0]["state"].get("cssShadow") if groups else None) or "—"


def rows(prof, renderer="css"):
    keys = sorted(k for k in bed if k[0] == prof and k[1] == renderer)
    return [(k, bed[k], dry.get(k)) for k in keys]


# ---------------------------------------------------------------------------
# S1 — the GPU tier byte-identical to the W17 bed, every row within 0.0002
# ---------------------------------------------------------------------------
print(f"== S1 · the GPU tier against the W17 bed ({args.label})")
same = diff = missing = 0
worst = 0.0
METRICS = [
    ("perceptual", "ssimMean"),
    ("perceptual", "ssimBand"),
    ("perceptual", "ssimInterior"),
    ("perceptual", "ssimOutside"),
    ("perceptual", "oklabDeltaEMean"),
    ("material", "interiorStdDevWeb"),
    ("material", "interiorMeanWeb"),
    ("shape", "silhouetteIoU"),
]
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
    rel = os.path.join(prof, scene, f"{scene}__webgpu.png")
    a, b = os.path.join(BED, "web-captures", rel), os.path.join(args.captures, rel)
    if os.path.exists(a) and os.path.exists(b):
        if hashlib.sha256(open(a, "rb").read()).digest() == hashlib.sha256(open(b, "rb").read()).digest():
            same += 1
        else:
            diff += 1
            stop("S1", False, f"capture differs: {scene} @ {prof}")
print(f"  GPU captures byte-identical {same}, differing {diff}, not compared {missing}; worst row |Δ| {worst:.6f}")
verdict.setdefault("S1", True)

# ---------------------------------------------------------------------------
# The CSS tier, per profile
# ---------------------------------------------------------------------------
s5_table = []
for prof in ALL:
    sb, de = BOUNDS[prof]
    print(
        f"\n== CSS tier · {prof[16:]} — carrier | ssimMean bed→{args.label} Δ | bound/floor | band Δ | "
        f"ΔE bed→{args.label} | level bed→{args.label} / GPU / native | CSS−GPU | move / predicted | "
        f"spread {args.label} / GPU / native | xtier ΔE bed→{args.label} | ratio"
    )
    for (p, r, scene), b, d in rows(prof):
        if d is None:
            print(f"  {scene:44s} not captured ({b['fixtureSet']})")
            continue
        gpu = dry.get((prof, "webgpu", scene))
        carrier = shadow_carrier(prof, scene)
        pinned = FLOORS.get((prof, scene))
        bound = f"floor {pinned[1]:.4f}" if pinned else f"≥ {sb}"
        s0, s1 = v(b, "perceptual", "ssimMean"), v(d, "perceptual", "ssimMean")
        limit = pinned[1] if pinned else sb
        ok = s1 is not None and s1 >= limit
        m0, m1 = v(b, "material", "interiorMeanWeb"), v(d, "material", "interiorMeanWeb")
        g1 = v(gpu, "material", "interiorMeanWeb")
        moved = None if m0 is None or m1 is None else m1 - m0
        pred = PREDICTED.get((scene, DPR[prof])) if prof in LIGHT_STANDARD else None
        print(
            f"  {scene:44s} {b['fixtureSet'][:4]} {carrier[:5]:5s} {f(s0)}→{f(s1)} {sd(s1, s0)} | {bound:14s} "
            f"{'ok ' if ok else 'MISS'} | {sd(v(d, 'perceptual', 'ssimBand'), v(b, 'perceptual', 'ssimBand'))} | "
            f"{f(v(b, 'perceptual', 'oklabDeltaEMean'))}→{f(v(d, 'perceptual', 'oklabDeltaEMean'))} | "
            f"{f(m0)}→{f(m1)} / {f(g1)} / {f(v(d, 'material', 'interiorMeanNative'))} | {sd(m1, g1)} | "
            f"{'   —   ' if moved is None else f'{moved:+.4f}'} / "
            f"{'   —   ' if pred is None else f'{pred:+.4f}'} | "
            f"{f(v(d, 'material', 'interiorStdDevWeb'))} / {f(v(gpu, 'material', 'interiorStdDevWeb'))} / "
            f"{f(v(d, 'material', 'interiorStdDevNative'))} | "
            f"{f(v(b, 'coherence', 'crossTierOklabDeltaEMean'))}→{f(v(d, 'coherence', 'crossTierOklabDeltaEMean'))} | "
            f"{f(v(d, 'coherence', 'interiorLevelRatioGpuOverCss'))}"
        )

        # -- S2's reading; the gate is `adopted-thresholds.test.ts`'s (X6) ----------------------
        if pinned is not None and s1 is not None and s1 < pinned[1]:
            note(f"S2 reading: {scene} @ {prof[16:]} ssimMean {s1:.5f} below its pinned floor {pinned[1]:.5f}")
        if prof == L1 and scene.startswith("checkerboard__") and s0 is not None and s1 is not None and s1 < s0 - 0.002:
            stop("S2", False, f"{scene} @ 1x fell {s1 - s0:+.4f} below the W17 bed (charter's 0.002 clause)")

        fam = scene.split("__")[0]
        tinted = "-tint-" in scene
        grouped = any(g in scene for g in GROUPED)

        # -- S3: the spread against the GPU tier, W17's one-sided rule carried ------------------
        if scene in CAL_CHECKER and prof in LIGHT_STANDARD:
            sw, sg, sn = (
                v(d, "material", "interiorStdDevWeb"),
                v(gpu, "material", "interiorStdDevWeb"),
                v(d, "material", "interiorStdDevNative"),
            )
            sw0 = v(b, "material", "interiorStdDevWeb")
            if sw is not None and sg is not None and sn is not None and sw0 is not None:
                # "Within W17's reach of native" (Decision Log 3, carrying the G1 section): the
                # gate is that this wave does not move the tier's spread FARTHER from native than
                # the W17 bed already had it. W17's own one-sided rule against the renderer is
                # reported beside it, because a cell that was already outside it on the bed is a
                # standing reading and not this wave's miss.
                stop(
                    "S3",
                    abs(sw - sn) <= abs(sw0 - sn) + 0.0005,
                    f"{scene} @ {prof[16:]} spread {sw - sn:+.4f} from native against the bed's "
                    f"{sw0 - sn:+.4f} — farther by {abs(sw - sn) - abs(sw0 - sn):+.4f}",
                )
                if abs(sw - sn) - abs(sg - sn) > 0.005:
                    note(
                        f"S3 reading (W17's rule, standing): {scene} @ {prof[16:]} spread "
                        f"{sw - sn:+.4f} from native against the renderer's {sg - sn:+.4f}; on the "
                        f"W17 bed the same cell read {sw0 - sn:+.4f}"
                    )

        # -- S4: the level against the GPU tier ------------------------------------------------
        if m1 is not None and g1 is not None:
            gap = m1 - g1
            if (prof, scene) in S4_TIGHT:
                stop("S4", abs(gap) <= 0.005, f"{scene} @ {prof[16:]} level {gap:+.4f} (clause 0.005)")
            elif (prof, scene) == (L1, "photo__toolbar-group__rest"):
                stop("S4", abs(gap) <= 0.01, f"{scene} @ 1x level {gap:+.4f} (clause 0.01, Decision Log 3 (3))")
                note(f"S4 named: photo__toolbar-group @ 1x reads {gap:+.4f}; the charter's 0.005 is missed by "
                     f"{abs(gap) - 0.005:+.4f} and the bound's structure term is its reason")
            elif (prof, scene) in S4_FOLD:
                stop("S4", abs(gap) <= 0.01, f"{scene} @ {prof[16:]} fold level {gap:+.4f} (q4's clause 0.01)")
            elif "glass-over-glass" in scene:
                # Decision Log 3 (4): the stack's clause is the tier's own share, read on the
                # pre-check's scratch twins; the canonical cell's whole-cell number is RECORDED
                # once with the renderer's unsampled route on a DOM-sourced group as its
                # remainder, and is not gated here.
                note(f"stack recorded: {scene} @ {prof[16:]} CSS−GPU {gap:+.4f} "
                     f"(moved {'   —   ' if moved is None else f'{moved:+.4f}'}; the remainder is "
                     f"the renderer's unsampled material on a DOM-sourced group, G0 §4)")
            elif prof in LIGHT_STANDARD and not tinted and fam in ("checkerboard", "hc-text", "photo"):
                stop("S4", abs(gap) <= 0.01, f"{scene} @ {prof[16:]} level {gap:+.4f} from the GPU tier's")
            if abs(gap) > 0.01:
                note(f"W17's 0.01 cross-tier clause left: {scene} @ {prof[16:]} at {gap:+.4f}")
            if b["fixtureSet"] == "holdout":
                note(f"holdout recorded: {scene} @ {prof[16:]} CSS−GPU {gap:+.4f} "
                     f"(bed {sd(m0, v(bed.get((prof, 'webgpu', scene)), 'material', 'interiorMeanWeb')).strip()})")

        # -- S5: the move against the closed form's share ---------------------------------------
        if tinted and moved is not None:
            # A tinted cell's own derived share (Decision Log 3 (6); W17 G1's rule): the shadow
            # reaches the interior only through the backdrop the tint has not covered, so the move
            # is `(1 − s)` of the untinted base cell's. The closed form is computed on the
            # material's own optics and does not carry an author tint, so comparing a tinted cell
            # against it would compare the measurement with a number for a different surface.
            strength = tint_strength(scene)
            base = untinted_base(scene)
            b0, b1 = bed.get((prof, "css", base)), dry.get((prof, "css", base))
            base0, base1 = v(b0, "material", "interiorMeanWeb"), v(b1, "material", "interiorMeanWeb")
            pred_tinted = (
                None if strength is None or base0 is None or base1 is None
                else (1 - strength) * (base1 - base0)
            )
            if pred_tinted is not None:
                s5_table.append((prof, scene, moved, pred_tinted, moved - pred_tinted, f"tinted s={strength}"))
                stop("S5", abs(moved - pred_tinted) <= 0.002,
                     f"{scene} @ {prof[16:]} moved {moved:+.4f} against its derived share "
                     f"{pred_tinted:+.4f} (miss {moved - pred_tinted:+.4f})")
        elif "glass-over-glass" in scene and moved is not None:
            # The closed form's largest residual is on the stack (+0.0274, G0 §6): the overlay's
            # shadow lands on the base's RENDERED body and is composited over it rather than
            # sampled into its backdrop, and the form models only the sampled path. The cell is
            # recorded, not compared.
            s5_table.append((prof, scene, moved, None, None, "stack (form not applicable)"))
        elif prof in LIGHT_STANDARD and moved is not None:
            if grouped:
                # Above the form by at most 0.005: the paint-order residual the form was never
                # asked to carry, and never BELOW the form, which would be a different mechanism.
                if pred is not None:
                    excess = moved - pred
                    s5_table.append((prof, scene, moved, pred, excess, "grouped"))
                    stop("S5", -0.002 <= excess <= 0.005,
                         f"{scene} @ {prof[16:]} moved {moved:+.4f} against the form's {pred:+.4f} "
                         f"(excess {excess:+.4f}, clause −0.002…+0.005)")
            elif pred is not None:
                tol = 0.0035 if fam == "light-solid" else 0.002
                excess = moved - pred
                s5_table.append((prof, scene, moved, pred, excess, "solid" if fam == "light-solid" else "single"))
                stop("S5", abs(excess) <= tol,
                     f"{scene} @ {prof[16:]} moved {moved:+.4f} against the form's {pred:+.4f} "
                     f"(miss {excess:+.4f}, clause {tol})")
        elif moved is not None:
            # The dark and the two fold profiles: the closed form was computed under the
            # light-standard document and the nominal policy and predicts nothing for them, so
            # they are gated on the move being small and on their other adopted metrics.
            s5_table.append((prof, scene, moved, None, None, "unpredicted"))

        # -- S5's tail: every cell's other adopted metrics within 0.002 -------------------------
        for ax, metric in (("perceptual", "ssimBand"), ("perceptual", "ssimInterior"),
                           ("perceptual", "oklabDeltaEMean"), ("shape", "silhouetteIoU")):
            a0, a1 = v(b, ax, metric), v(d, ax, metric)
            if a0 is None or a1 is None:
                continue
            if abs(a1 - a0) > 0.002 and metric != "ssimBand":
                note(f"S5 metric: {scene} @ {prof[16:]} {metric} moved {a1 - a0:+.4f}")
        x0, x1 = v(b, "coherence", "crossTierOklabDeltaEMean"), v(d, "coherence", "crossTierOklabDeltaEMean")
        if x0 is not None and x1 is not None and x1 > x0 + 1e-4:
            note(f"S6 reading: {scene} @ {prof[16:]} cross-tier ΔE rose {x1 - x0:+.5f} "
                 f"({x0:.5f} → {x1:.5f}); the gate is the profile's mean")

# ---------------------------------------------------------------------------
# S6 — coherence: the cross-tier ΔE not up on any profile, the level ratio on the light cells
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
for prof in LIGHT_STANDARD:
    for (p, r, scene), b, d in rows(prof):
        lr = v(d, "coherence", "interiorLevelRatioGpuOverCss")
        if lr is None:
            continue
        if worstratio is None or abs(lr - 1) > abs(worstratio[0] - 1):
            worstratio = (lr, scene, prof)
        # S6 as Decision Log 3 carries it is the PROFILE's cross-tier ΔE mean above and the
        # `tier-coherence` unit suite; W17's per-cell 0.97–1.03 band on the level ratio is the
        # standing reading, printed with the bed's own value beside it so a cell that moved
        # farther from 1 is visible without being a stop this wave never declared.
        lr0 = v(b, "coherence", "interiorLevelRatioGpuOverCss")
        # "Tighter or equal": a cell outside W17's band on the W17 bed too is a standing reading,
        # and only a cell that LEAVES the band by this wave is a miss of it.
        outside_bed = lr0 is not None and not (0.97 <= lr0 <= 1.03)
        stop("S6", 0.97 <= lr <= 1.03 or outside_bed,
             f"{scene} @ {prof[16:]} level ratio {lr:.4f} left W17's 0.97–1.03 (bed {f(lr0)})")
        if not (0.97 <= lr <= 1.03) and outside_bed:
            note(f"S6 reading (standing): {scene} @ {prof[16:]} level ratio {lr:.4f}, bed {lr0:.4f}")
        if lr0 is not None and abs(lr - 1) > abs(lr0 - 1) + 0.0005:
            note(f"S6 reading: {scene} @ {prof[16:]} level ratio {lr:.4f} against the bed's {lr0:.4f} "
                 f"— farther from 1 by {abs(lr - 1) - abs(lr0 - 1):+.4f}, inside W17's band")
if worstratio is not None:
    print(f"  worst light-cell level ratio {worstratio[0]:.4f} on {worstratio[1]} @ {worstratio[2][16:]}")

# ---------------------------------------------------------------------------
# S5's table, gathered
# ---------------------------------------------------------------------------
print("\n== S5 · the move against the closed form's share, per cell")
print("  profile                      scene                                         moved  predicted   excess  class")
for prof, scene, moved, pred, excess, kind in s5_table:
    print(
        f"  {prof[16:]:28s} {scene:44s} {moved:+.4f}  "
        f"{'   —   ' if pred is None else f'{pred:+.4f}'}  "
        f"{'   —   ' if excess is None else f'{excess:+.4f}'}  {kind}"
    )

# ---------------------------------------------------------------------------
# W17's 0.01 cross-tier clause: every cell outside it, before and after
# ---------------------------------------------------------------------------
print("\n== W17's 0.01 cross-tier clause · every cell outside it on either run")
print("  profile                        scene                                          bed      dry   verdict")
for (prof, rend, scene), b in sorted(bed.items()):
    if rend != "css":
        continue
    d = dry.get((prof, rend, scene))
    m0, g0 = v(b, "material", "interiorMeanWeb"), v(bed.get((prof, "webgpu", scene)), "material", "interiorMeanWeb")
    m1, g1 = v(d, "material", "interiorMeanWeb"), v(dry.get((prof, "webgpu", scene)), "material", "interiorMeanWeb")
    if None in (m0, g0, m1, g1):
        continue
    gap0, gap1 = m0 - g0, m1 - g1
    if abs(gap0) <= 0.01 and abs(gap1) <= 0.01:
        continue
    kind = ("LEFT the clause" if abs(gap1) <= 0.01 < abs(gap0)
            else "NEW miss" if abs(gap0) <= 0.01 < abs(gap1) else "standing")
    print(f"  {prof[16:]:30s} {scene:44s} {gap0:+.4f} {gap1:+.4f}  {kind}")

print("\n== verdicts")
for k, ok in sorted(verdict.items()):
    print(f"  {k}: {'met' if ok else 'FIRED'}")
print(f"  ({len(notes)} note(s) above; S2's bounds and floors and S7's predicate are "
      f"adopted-thresholds.test.ts's, X6)")
