#!/usr/bin/env python3
"""W17 G1: the dry run read against the W16 bed under the charter's G1 stops, as W17 Decision
Log 3 re-declares S3 and S5. Derived from W16 G1's `verify-dry.py`.

    python3 verify-dry.py <dry matrix> <dry captures dir> [--label cfg2]

The canonical matrix and captures are the MAIN checkout's (the W16 bed, `1130104`); the dry run's
are the scratch matrix and captures this branch's build wrote. Nothing canonical is read for
writing and nothing canonical is written.

## The division of labour with `adopted-thresholds.test.ts`

Contract X6 says the LANDING's own gate runs against the dry run's matrix, and since W17 G1 it
can: `VITREA_MATRIX_PATH` points it at a scratch file. So **S2 and S7's conditioning predicate are
that file's**, not this one's — it holds the only copy of the bounds, the floors and the predicate,
and a second copy here would be the thing it exists to prevent. What this script owns is
everything the test file cannot see: the GPU tier's byte identity (S1), and the four stops that
are statements about the DIFFERENCE between two runs or between the two tiers (S3, S4, S5, S6).
The floors' rows are printed here as a reading, with their pinned values parsed out of the test
file rather than restated.

## What Decision Log 3 re-declared, and how it is read here

  S3  the tier's interior spread within 0.005 of the GPU TIER's own spread on every calibration
      span at both scales. The distance to native is printed beside it on every cell, and the
      as-written verdict (±0.01 at 1x, ±0.015 at 2x against native) is computed and reported too,
      so the record carries both readings rather than the one that passes.
  S5  every solid and author-tinted cell's interior mean within 0.01 of the GPU tier's; the
      tinted cells' move predicted per cell as `(1 − s)` of the untinted base cell's change and
      printed beside the measurement; their cross-tier ΔE not rising; their `ssimMean` inside its
      bound or floor (the test file's verdict, echoed here); and the dark-scheme cells that were
      within 0.015 of the GPU tier moving by no more than 0.005.

S4 keeps its own clause — the interior mean within 0.01 of the GPU tier's on every light-standard
checkerboard, `hc-text` and `photo` cell at both scales. Its "and the dark and solid cells moving
≤ 0.005" tail is superseded by S5's re-declaration, which reads the same cells against the
renderer instead, and is reported under S5.
"""
import argparse
import hashlib
import json
import os
import re

MAIN = "/Users/new/Developer/GitHub/designer/packages/calibration"
ap = argparse.ArgumentParser()
ap.add_argument("matrix")
ap.add_argument("captures")
ap.add_argument("--label", default="dry")
args = ap.parse_args()


def load(path):
    """`(profile, renderer, scene) -> cell`, the most recently captured row winning."""
    best = {}
    for c in json.load(open(path))["cells"]:
        k = (c["key"]["profileKey"], c["key"]["web"]["renderer"], c["key"]["sceneId"])
        if k not in best or c["capturedAt"] > best[k]["capturedAt"]:
            best[k] = c
    return best


bed = load(os.path.join(MAIN, "results", "matrix.json"))
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
# The adopted `ssimMean` bound and OKLab ΔE mean bound per profile, transcribed from
# `adopted-thresholds.test.ts` for reporting only — that file gates them (X6).
BOUNDS = {L1: (0.90, 0.08), L2: (0.92, 0.08), D1: (0.83, 0.09), D2: (0.85, 0.09), RT: (0.91, 0.04), IC: (0.83, 0.07)}
# The calibration spans S3 reads, as W16 G1's referee named them.
CAL_CHECKER = [
    "checkerboard__rrect-sm__rest",
    "checkerboard__capsule-button__rest",
    "checkerboard__rrect-md__rest",
    "checkerboard__rrect-ml__rest",
    "checkerboard__toolbar-group__rest",
]
SOLID_FAMILIES = ("light-solid", "dark-solid", "mid-dark-solid", "impulse")
# The author's opacity per tint id, from `apps/reference-apple/scenes.json`'s registry: a colour's
# alpha is how far the material's tint moves toward the seed, and an absent alpha is full strength.
REFERENCE = os.path.join(MAIN, "..", "..", "apps", "reference-apple")
TINTS = json.load(open(os.path.join(REFERENCE, "scenes.json")))["tints"]
SCENE_TINT = {
    s["id"]: s["tint"] for s in json.load(open(os.path.join(REFERENCE, "scenes.json")))["scenes"] if s.get("tint")
}


def tint_strength(scene):
    tint = SCENE_TINT.get(scene)
    return None if tint is None else TINTS[tint].get("alpha", 1.0)


def untinted_base(scene):
    """`checkerboard__capsule-button__rest-tint-orange` -> `checkerboard__capsule-button__rest`."""
    return scene.split("-tint-")[0]


def floors():
    """The pinned `ssimMean` floors, parsed out of the landing's own gate rather than restated."""
    source = open(os.path.join(MAIN, "test", "adopted-thresholds.test.ts")).read()
    out = {}
    for key, measured, floor in re.findall(
        r'"(dom / \w+ / [\w-]+ / [\w.-]+) :: ssimMean":\s*\{\s*measured:\s*([\d.]+),\s*floor:\s*([\d.]+)', source
    ):
        _, _, scene, profile = key.split(" / ")
        out[(profile, scene)] = (float(measured), float(floor))
    return out


FLOORS = floors()
verdict = {}
notes = []


def stop(name, ok, note=""):
    verdict[name] = verdict.get(name, True) and ok
    if not ok:
        print(f"  STOP {name}: {note}")


def note(text):
    notes.append(text)
    print(f"  note: {text}")


def tint_form(profile, scene):
    """Which tint form the group drew, off the capture's own report (Decision Log 4 (c)).

    The matrix's cell carries the measured axes and not the resolved state, so the form is read
    where the runtime wrote it — the same place `cssBody` is read from.
    """
    path = os.path.join(args.captures, profile, scene, "report__css.json")
    if not os.path.exists(path):
        return "—"
    groups = json.load(open(path))["page"].get("groups") or []
    return (groups[0]["state"].get("cssTint") if groups else None) or "—"


def rows(prof, renderer="css"):
    keys = sorted(k for k in bed if k[0] == prof and k[1] == renderer)
    return [(k, bed[k], dry.get(k)) for k in keys]


# ---------------------------------------------------------------------------
# S1 — the GPU tier byte-identical to the bed, every row within 0.0002
# ---------------------------------------------------------------------------
print(f"== S1 · the GPU tier against the W16 bed ({args.label})")
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
    a, b = os.path.join(MAIN, "web-captures", rel), os.path.join(args.captures, rel)
    if os.path.exists(a) and os.path.exists(b):
        if hashlib.sha256(open(a, "rb").read()).digest() == hashlib.sha256(open(b, "rb").read()).digest():
            same += 1
        else:
            diff += 1
            stop("S1", False, f"capture differs: {scene} @ {prof}")
print(f"  GPU captures byte-identical {same}, differing {diff}, not captured {missing}; worst row |Δ| {worst:.6f}")
verdict.setdefault("S1", True)

# ---------------------------------------------------------------------------
# The CSS tier, per profile: the rows, and S2's floors as a reading
# ---------------------------------------------------------------------------
for prof in ALL:
    sb, de = BOUNDS[prof]
    print(
        f"\n== CSS tier · {prof[16:]} — ssimMean bed→{args.label} Δ | bound/floor | band Δ | ΔE bed→{args.label} | "
        f"level bed→{args.label} / GPU / native | CSS−GPU | spread {args.label} / GPU / native | xtier ΔE bed→{args.label} | ratio"
    )
    for (p, r, scene), b, d in rows(prof):
        if d is None:
            print(f"  {scene:44s} not captured ({b['fixtureSet']})")
            continue
        gpu = dry.get((prof, "webgpu", scene))
        form = tint_form(prof, scene)
        pinned = FLOORS.get((prof, scene))
        bound = f"floor {pinned[1]:.4f}" if pinned else f"≥ {sb}"
        s0, s1 = v(b, "perceptual", "ssimMean"), v(d, "perceptual", "ssimMean")
        limit = pinned[1] if pinned else sb
        ok = s1 is not None and s1 >= limit
        m1, g1 = v(d, "material", "interiorMeanWeb"), v(gpu, "material", "interiorMeanWeb")
        print(
            f"  {scene:44s} {b['fixtureSet'][:4]} {form[:3]} {f(s0)}→{f(s1)} {sd(s1, s0)} | {bound:14s} {'ok ' if ok else 'MISS'} | "
            f"{sd(v(d, 'perceptual', 'ssimBand'), v(b, 'perceptual', 'ssimBand'))} | "
            f"{f(v(b, 'perceptual', 'oklabDeltaEMean'))}→{f(v(d, 'perceptual', 'oklabDeltaEMean'))} | "
            f"{f(v(b, 'material', 'interiorMeanWeb'))}→{f(m1)} / {f(g1)} / {f(v(d, 'material', 'interiorMeanNative'))} | "
            f"{sd(m1, g1)} | "
            f"{f(v(d, 'material', 'interiorStdDevWeb'))} / {f(v(gpu, 'material', 'interiorStdDevWeb'))} / "
            f"{f(v(d, 'material', 'interiorStdDevNative'))} | "
            f"{f(v(b, 'coherence', 'crossTierOklabDeltaEMean'))}→{f(v(d, 'coherence', 'crossTierOklabDeltaEMean'))} | "
            f"{f(v(d, 'coherence', 'interiorLevelRatioGpuOverCss'))}"
        )
        # S2 is `adopted-thresholds.test.ts`'s to gate (X6). What is reported here is the reading
        # it will gate: a floor's row below its pin, and the charter's own extra clause that no 1x
        # checkerboard row falls more than 0.002 below the W16 bed.
        if pinned is not None and s1 is not None and s1 < pinned[1]:
            note(f"S2 reading: {scene} @ {prof[16:]} ssimMean {s1:.5f} below its pinned floor {pinned[1]:.5f}")
        if prof == L1 and scene.startswith("checkerboard__") and s0 is not None and s1 is not None and s1 < s0 - 0.002:
            stop("S2", False, f"{scene} @ 1x fell {s1 - s0:+.4f} below the W16 bed (charter's 0.002 clause)")

        fam = scene.split("__")[0]
        tinted = "-tint-" in scene
        # -- S3: the spread against the GPU tier (Decision Log 3), with both readings ------------
        if scene in CAL_CHECKER and prof in LIGHT_STANDARD:
            sw, sg, sn = (
                v(d, "material", "interiorStdDevWeb"),
                v(gpu, "material", "interiorStdDevWeb"),
                v(d, "material", "interiorStdDevNative"),
            )
            # S3 is ONE-SIDED since Decision Log 4 (d): it fires only where the tier's spread is
            # FARTHER from native than the renderer's by more than 0.005. A tier whose spread sits
            # above the renderer's because it is nearer native is a recorded finding, not a miss.
            if sw is not None and sg is not None and sn is not None:
                stop(
                    "S3",
                    abs(sw - sn) - abs(sg - sn) <= 0.005,
                    f"{scene} @ {prof[16:]} spread {sw - sn:+.4f} from native against the "
                    f"renderer's {sg - sn:+.4f} — farther by {abs(sw - sn) - abs(sg - sn):+.4f}",
                )
            if sw is not None and sn is not None and sg is not None:
                tol = 0.01 if prof == L1 else 0.015
                if abs(sw - sn) > tol:
                    note(
                        f"S3 as written: {scene} @ {prof[16:]} spread {sw - sn:+.4f} against native, "
                        f"beyond ±{tol} (the GPU tier is {sg - sn:+.4f} on the same cell)"
                    )
        # -- S4: the level against the GPU tier on the light cells -------------------------------
        if prof in LIGHT_STANDARD and not tinted and fam in ("checkerboard", "hc-text", "photo"):
            if m1 is not None and g1 is not None:
                stop("S4", abs(m1 - g1) <= 0.01, f"{scene} @ {prof[16:]} level {m1 - g1:+.4f} from the GPU tier's")
        # -- S5: the solids and the author-tinted cells against the renderer (Decision Log 3) ----
        if fam in SOLID_FAMILIES or tinted:
            if m1 is not None and g1 is not None:
                stop("S5", abs(m1 - g1) <= 0.01, f"{scene} @ {prof[16:]} level {m1 - g1:+.4f} from the GPU tier's")
            x0, x1 = v(b, "coherence", "crossTierOklabDeltaEMean"), v(d, "coherence", "crossTierOklabDeltaEMean")
            if x0 is not None and x1 is not None:
                # A tolerance rather than a strict comparison: the axis is reported to five
                # decimals and a "rise" of +0.00000 is the print, not the measurement.
                stop("S5", x1 <= x0 + 1e-4, f"{scene} @ {prof[16:]} cross-tier ΔE rose {x1 - x0:+.5f}")
            if s1 is not None:
                stop("S5", s1 >= limit, f"{scene} @ {prof[16:]} ssimMean {s1:.4f} below {limit:.4f}")
        if tinted:
            s = tint_strength(scene)
            base = untinted_base(scene)
            b0, b1 = bed.get((prof, "css", base)), dry.get((prof, "css", base))
            base0 = v(b0, "material", "interiorMeanWeb") if b0 is not None else None
            base1 = v(b1, "material", "interiorMeanWeb") if b1 is not None else None
            predicted = None if s is None or base0 is None or base1 is None else (1 - s) * (base1 - base0)
            m0 = v(b, "material", "interiorMeanWeb")
            if m1 is not None and m0 is not None:
                print(
                    f"      tinted: s={s}  moved {m1 - m0:+.4f}  predicted "
                    f"{'   —   ' if predicted is None else f'{predicted:+.4f}'}"
                    f"{'' if predicted is None else f'  residual {m1 - m0 - predicted:+.4f}'}"
                )
        # -- the dark-scheme cells that were within 0.015 of the GPU tier ------------------------
        if prof in (D1, D2):
            gbed = bed.get((prof, "webgpu", scene))
            m0, gm0 = v(b, "material", "interiorMeanWeb"), v(gbed, "material", "interiorMeanWeb")
            if m0 is not None and gm0 is not None and abs(m0 - gm0) <= 0.015 and m1 is not None:
                stop("S5", abs(m1 - m0) <= 0.005, f"{scene} @ {prof[16:]} dark cell moved {m1 - m0:+.4f} (> 0.005)")

# ---------------------------------------------------------------------------
# S6 — coherence: the cross-tier ΔE down on every profile, the level ratio on the light cells
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
        stop("S6", 0.97 <= lr <= 1.03, f"{scene} @ {prof[16:]} level ratio {lr:.4f} outside 0.97–1.03")
if worstratio is not None:
    print(f"  worst light-cell level ratio {worstratio[0]:.4f} on {worstratio[1]} @ {worstratio[2][16:]}")

# ---------------------------------------------------------------------------
# S7 — the two reduced-transparency capsule cells' conditioning
# ---------------------------------------------------------------------------
print(f"\n== S7 · the reduced-transparency capsule cells")
for scene in ("checkerboard__capsule-button__rest", "hc-text__capsule-button__rest"):
    d = dry.get((RT, "css", scene))
    b = bed.get((RT, "css", scene))
    if d is None:
        print(f"  {scene:44s} not captured")
        continue
    area_w = v(d, "shape", "silhouetteAreaWeb")
    area_r = v(d, "shape", "componentRegionArea")
    bodies = v(d, "shape", "silhouetteBodiesWeb")
    ratio = None if not area_r else area_w / area_r
    print(
        f"  {scene:44s} areaWeb/region {'—' if ratio is None else f'{ratio:.4f}'}  bodies {bodies}  "
        f"level bed {f(v(b, 'material', 'interiorMeanWeb'))} → {f(v(d, 'material', 'interiorMeanWeb'))}  "
        f"GPU {f(v(dry.get((RT, 'webgpu', scene)), 'material', 'interiorMeanWeb'))}"
    )
    stop("S7", ratio is not None and ratio >= 0.95 and bodies == 1, f"{scene} does not condition")

print("\n== verdicts")
for k, ok in sorted(verdict.items()):
    print(f"  {k}: {'met' if ok else 'FIRED'}")
print(f"  ({len(notes)} note(s) above; S2 and the conditioning predicate are adopted-thresholds.test.ts's, X6)")
