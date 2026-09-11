#!/usr/bin/env python3
"""W27c G1b — the analysis half of the activation measurement gate.

This script reads ONLY committed evidence and writes the gate's machine tables.
It captures nothing, runs no browser, and touches neither the canonical matrix
nor any profile document. In particular it does not re-run `compare` on holdout
membership: the 30-cell holdout of claims §5.130 is spent, and reading its
recorded per-cell numbers out of `holdout.json` is reading the record, which is
what this gate is allowed to do and all it does.

Reproduce with, from the repository root:

    python3 packages/calibration/results/2026-09-11-w27c-g1b/read.py

Outputs are rewritten in place, because every number in them is a pure function
of the committed inputs whose SHA-256s the outputs carry.
"""

from __future__ import annotations

import hashlib
import json
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.dirname(HERE)
CAL = os.path.dirname(RESULTS)
ROOT = os.path.dirname(os.path.dirname(CAL))

G1 = os.path.join(RESULTS, "2026-09-10-w27c-g1-corrected")

SOURCES = {
    "checked": os.path.join(G1, "checked.json"),
    "holdout": os.path.join(G1, "holdout.json"),
    "declaration": os.path.join(RESULTS, "2026-09-10-w27c-g1-corrected-declaration.json"),
    "tables": os.path.join(RESULTS, "2026-09-10-w27c-g1-corrected-tables.json"),
    "recede": os.path.join(RESULTS, "2026-09-10-w27c-g0-recede.json"),
    "scenes": os.path.join(ROOT, "apps", "reference-apple", "scenes.json"),
    "lightProfile": os.path.join(CAL, "profiles", "apple-macos-26.5-1x-light-standard.json"),
    "darkProfile": os.path.join(CAL, "profiles", "apple-macos-26.5-1x-dark-standard.json"),
}


def sha256(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load(name: str):
    with open(SOURCES[name], "rb") as handle:
        return json.load(handle)


def short(profile: str) -> str:
    """`apple-macos-26.5-1x-light-standard` -> `1x-light-standard`."""
    return profile[len("apple-macos-26.5-"):]


def canvas_pixels(profile: str) -> int:
    """The declared 320x200 canvas in device pixels at this profile's scale."""
    return 320 * 200 * (4 if profile.startswith("2x") else 1)


# ---------------------------------------------------------------------------
# 1. Which regimes the inactive fit was given, and which it was not
# ---------------------------------------------------------------------------

def coverage(scenes: dict) -> dict:
    """Every inactive scene's set membership, grouped by background and by
    component, so a family present in no fitting set is visible by counting
    rather than by assertion. The inactive split is the active split mirrored
    through `sourceScene`, which is why the three families the endpoint
    extrapolates into are exactly the three the active bed reserved."""
    member = {}
    for name in ("calibration", "validation", "holdout", "recorded"):
        for scene in scenes["split"].get(name, []):
            if isinstance(scene, str):
                member[scene] = name
    by_id = {scene["id"]: scene for scene in scenes["scenes"]}

    backgrounds = defaultdict(lambda: defaultdict(int))
    components = defaultdict(lambda: defaultdict(int))
    for scene_id, scene in by_id.items():
        if scene.get("state") not in ("inactive", "inactive-pressed"):
            continue
        where = member.get(scene_id, "unassigned")
        backgrounds[scene["background"]][where] += 1
        components[scene["component"]][where] += 1

    def rows(table):
        out = []
        for key in sorted(table):
            counts = dict(table[key])
            fitted = counts.get("calibration", 0) + counts.get("validation", 0)
            out.append({
                "key": key,
                "counts": counts,
                "inFittingSets": fitted,
                "holdoutOnly": fitted == 0 and counts.get("holdout", 0) > 0,
            })
        return out

    spans = {
        name: (min(spec["size"]) if "size" in spec else None)
        for name, spec in scenes["components"].items()
    }
    return {
        "$comment": [
            "Inactive scene membership by background and by component. A family",
            "with inFittingSets 0 was never seen by the fit or its check: no",
            "setting of any declared field was identified on it, so the frozen",
            "endpoint extrapolates there. Three such families exist and they are",
            "exactly where four of the five §5.130 §7 residuals live.",
        ],
        "byBackground": rows(backgrounds),
        "byComponent": rows(components),
        "componentSpanCssPx": spans,
    }


# ---------------------------------------------------------------------------
# 2. The metric decomposition — what the "seven to eight times" is made of
# ---------------------------------------------------------------------------

def decomposition(checked: list, holdout: list) -> dict:
    """`§5.130 §7` compares sets on FULL-CANVAS mean OKLab ΔE. That statistic is
    an area-weighted dilution of the interior error: a capsule's body is 5% of
    the canvas and an rrect-lg's is 61%, and §5.130 §1 says so itself ("The
    full-canvas mean is not an interior bound"). The calibration and validation
    sets have near-equal mean footprint area, so their full-canvas comparison is
    fair; the holdout's mean footprint is 3.7x larger, so its full-canvas
    comparison against calibration is not. Both statistics are reported here,
    per profile, with the footprint area that separates them."""
    rows = checked + holdout
    grouped = defaultdict(list)
    for row in rows:
        grouped[(short(row["profile"]), row["set"])].append(row)

    per_set = {}
    for (profile, which), cells in sorted(grouped.items()):
        per_set.setdefault(profile, {})[which] = {
            "n": len(cells),
            "meanFootprintAreaFraction": statistics.mean(
                cell["body"]["n"] / canvas_pixels(profile) for cell in cells
            ),
            "meanFullCanvasDeltaE": statistics.mean(
                cell["deltaE"]["mean"] for cell in cells
            ),
            "meanBodyDeltaE": statistics.mean(cell["body"]["deltaE"] for cell in cells),
            "maxFullCanvasDeltaE": max(cell["deltaE"]["mean"] for cell in cells),
            "maxBodyDeltaE": max(cell["body"]["deltaE"] for cell in cells),
        }

    for profile, sets in per_set.items():
        base = sets["calibration"]
        for which, stats in sets.items():
            stats["fullCanvasRatioToCalibration"] = (
                stats["meanFullCanvasDeltaE"] / base["meanFullCanvasDeltaE"]
                if base["meanFullCanvasDeltaE"] else None
            )
            stats["bodyRatioToCalibration"] = (
                stats["meanBodyDeltaE"] / base["meanBodyDeltaE"]
            )
            stats["footprintRatioToCalibration"] = (
                stats["meanFootprintAreaFraction"] / base["meanFootprintAreaFraction"]
            )

    return {
        "$comment": [
            "fullCanvasRatioToCalibration on the holdout rows is the 7-8x of",
            "§5.130 §7 and of W27 Decision Log 12. bodyRatioToCalibration is the",
            "same comparison on the declared union eroded 6 CSS px, the mask the",
            "material actually occupies. footprintRatioToCalibration is the",
            "confound: multiply it by bodyRatioToCalibration and the full-canvas",
            "ratio is recovered to within the un-eroded contour band.",
        ],
        "definitions": {
            "meanFullCanvasDeltaE": "equal-cell mean of whole-image mean per-pixel OKLab ΔE (canonical oklabDeltaE, packages/calibration/src/metrics/perceptual.ts)",
            "meanBodyDeltaE": "equal-cell mean of the same distance over the declared union eroded 6 CSS px",
            "meanFootprintAreaFraction": "eroded body device pixels / canvas device pixels at that profile's scale",
        },
        "perProfile": per_set,
    }


# ---------------------------------------------------------------------------
# 3. The adopted active-bed bounds, against which the spent holdout is read
# ---------------------------------------------------------------------------

# Transcribed from `packages/calibration/test/adopted-thresholds.test.ts`, the
# WebGPU ("texture") tier rows only, which is the tier X1 makes the comparison.
# The metric is the same canonical full-canvas `oklabDeltaEMean` the tables above
# use, so the two are directly comparable without any conversion.
ADOPTED_TEXTURE_TIER_DELTA_E_MEAN = {
    "1x-light-standard": 0.07,
    "2x-light-standard": 0.07,
    "1x-dark-standard": 0.09,
    "2x-dark-standard": 0.09,
    "1x-light-increased-contrast": 0.06,
    "1x-light-reduced-transparency": 0.04,
}


def against_adopted(holdout: list) -> dict:
    """The active material's own adopted per-cell ceiling, applied to the spent
    inactive holdout. This is not a new bound; it is the bar `adopted-thresholds`
    already enforces on the WebGPU tier for each profile, and the inactive pose
    ships into the same product."""
    grouped = defaultdict(list)
    for row in holdout:
        grouped[short(row["profile"])].append(row)
    out = {}
    for profile, cells in sorted(grouped.items()):
        worst = max(cells, key=lambda cell: cell["deltaE"]["mean"])
        bound = ADOPTED_TEXTURE_TIER_DELTA_E_MEAN[profile]
        out[profile] = {
            "adoptedTextureTierOklabDeltaEMean": bound,
            "worstHoldoutCell": worst["scene"],
            "worstHoldoutFullCanvasDeltaE": worst["deltaE"]["mean"],
            "holds": worst["deltaE"]["mean"] <= bound,
            "headroomFraction": worst["deltaE"]["mean"] / bound,
        }
    return {
        "$comment": [
            "Transcribed from packages/calibration/test/adopted-thresholds.test.ts",
            "(TEXTURE_TIER_* tables, perceptual/oklabDeltaEMean rows). Every one of",
            "the 30 spent inactive holdout cells is inside its profile's adopted",
            "active-bed ceiling. That is a fact about the record, not an adoption:",
            "no inactive floor is adopted by this gate, and G3 still owns that.",
        ],
        "perProfile": out,
    }


# ---------------------------------------------------------------------------
# 4. The native reference's own span behaviour, from the G0 census
# ---------------------------------------------------------------------------

def native_span_behaviour(recede: dict, scenes: dict) -> dict:
    """Two readings of Apple's own recede against surface span, both from the
    121-cell G0 census (footprint mask, not eroded), which is why they are
    comparable to each other and not to the eroded tables above.

    `chromaBySpan` is the one that decides residuals (c) and (e): the reference's
    inactive material retains MORE of a chromatic backdrop's chroma than its
    active one, and the excess grows with span.

    `structureBySpan` is the one that decides residual (b): the reference's
    inactive material scatters progressively harder as span grows, and the step
    between span 96 and span 160 is the largest in the census."""
    spans = {
        name: (min(spec["size"]) if "size" in spec else None)
        for name, spec in scenes["components"].items()
    }

    chroma = []
    structure = []
    for cell in recede["cells"]:
        if "standard" not in cell["profile"]:
            continue
        active, inactive = cell["active"], cell["inactive"]
        span = spans.get(cell["component"])
        if cell["background"] == "photo" and cell["state"] == "rest":
            chroma.append({
                "profile": short(cell["profile"]),
                "scene": cell["scene"],
                "component": cell["component"],
                "spanCssPx": span,
                "tinted": bool(cell["tinted"]),
                "nativeChromaActive": active["meanOklabChroma"],
                "nativeChromaInactive": inactive["meanOklabChroma"],
                "chromaRetention": (
                    inactive["meanOklabChroma"] / active["meanOklabChroma"]
                    if active["meanOklabChroma"] else None
                ),
                "nativeYActive": active["meanLinear"],
                "nativeYInactive": inactive["meanLinear"],
            })
        if (
            cell["background"] == "checkerboard"
            and cell["state"] == "rest"
            and not cell["tinted"]
        ):
            structure.append({
                "profile": short(cell["profile"]),
                "scene": cell["scene"],
                "component": cell["component"],
                "spanCssPx": span,
                "nativeSdActive": active["stdDevLinear"],
                "nativeSdInactive": inactive["stdDevLinear"],
                "sdRatioInactiveOverActive": (
                    inactive["stdDevLinear"] / active["stdDevLinear"]
                    if active["stdDevLinear"] else None
                ),
            })

    return {
        "$comment": [
            "From results/2026-09-10-w27c-g0-recede.json, the 121-cell native",
            "census. Footprint mask (declared rounded component region, zero",
            "margin), NOT the 6-CSS-px-eroded body of the fit tables.",
        ],
        "chromaBySpan": sorted(chroma, key=lambda r: (r["profile"], r["spanCssPx"] or 0, r["scene"])),
        "structureBySpan": sorted(structure, key=lambda r: (r["profile"], r["spanCssPx"] or 0)),
    }


# ---------------------------------------------------------------------------
# 5. The five residuals, each with the cells that decide it
# ---------------------------------------------------------------------------

def cell(rows: list, profile: str, scene: str) -> dict | None:
    for row in rows:
        if short(row["profile"]) == profile and row["scene"] == scene:
            return {
                "scene": scene,
                "profile": profile,
                "set": row["set"],
                "fullCanvasDeltaE": row["deltaE"]["mean"],
                "bodyDeltaE": row["body"]["deltaE"],
                "bodyWebY": row["body"]["webY"],
                "bodyNativeY": row["body"]["nativeY"],
                "bodyWebSD": row["body"]["webSD"],
                "bodyNativeSD": row["body"]["nativeSD"],
                "bodyPixels": row["body"]["n"],
            }
    return None


def residuals(checked: list, holdout: list, declaration: dict, recede: dict) -> list:
    rows = checked + holdout
    patch = declaration["patch"]

    def native(scene: str, profile: str, pose: str, field: str):
        for entry in recede["cells"]:
            if entry["scene"] == scene and short(entry["profile"]) == profile:
                return entry[pose][field]
        return None

    return [
        {
            "id": "a",
            "name": "the mid-dark-solid capsule the three-anchor response misidentifies",
            "classification": "bed",
            "subtype": "evidence absent, not fixture suspect",
            "expressibleInDeclaredFields": True,
            "field": "backdropToneResponseThin[1] / backdropToneResponseThick[1]",
            "why": [
                "`backdropToneAnchorX` is [0.1104, 0.2706, 0.9505] — the three",
                "SOLID backgrounds' encoded-space means. 0.2706 is 69/255, which is",
                "mid-dark-solid exactly. The middle ordinate of the response is",
                "therefore not a shape parameter fitted through this cell: it IS",
                "this cell's predicted level, and a capsule at span 44 takes",
                "smoothstep(0.09229) = 0.024 of the thick row, so its output is the",
                "thin ordinate to within 0.0006.",
                "The fitted dark thin[1] is 0.089 and the web body reads 0.08866;",
                "the fitted light thin[1] is 0.4 and the web body reads 0.40198.",
                "The field is exactly the right field and it is set to the wrong",
                "number, so this is not model-form.",
                "It is not the fixture either. mid-dark-solid is a uniform 69/255",
                "patch; the 1x and 2x native inactive readings agree to 1e-4 in",
                "both schemes across two independently captured files, and the",
                "active side of the same census reproduces the same agreement.",
                "What is missing is the EVIDENCE the active profile had and the",
                "inactive endpoint did not: the active middle anchors are direct",
                "probe-bed measurements (W9 in light, W21 G0 in dark, the latter",
                "reading `mid-dark-solid encoded mean 0.2706 thin 0.0284 thick",
                "0.0238` off results/2026-09-06-w21-dark-scheme/probe/). The",
                "recovered inactive bed has 37 scenes and no probe grid, and the",
                "one mid-dark cell it does have is holdout. The middle ordinate was",
                "consequently fitted as a shape knob for cells at other abscissas.",
            ],
            "decidingCells": [
                cell(rows, "1x-dark-standard", "mid-dark-solid__capsule-button__inactive"),
                cell(rows, "2x-dark-standard", "mid-dark-solid__capsule-button__inactive"),
                cell(rows, "1x-light-standard", "mid-dark-solid__capsule-button__inactive"),
                cell(rows, "2x-light-standard", "mid-dark-solid__capsule-button__inactive"),
                cell(rows, "1x-dark-standard", "dark-solid__capsule-button__inactive"),
                cell(rows, "1x-light-standard", "light-solid__capsule-button__inactive"),
                cell(rows, "1x-light-standard", "dark-solid__rrect-md__inactive"),
            ],
            "fittedOrdinates": {
                "backdropToneAnchorX": [0.1104, 0.2706, 0.9505],
                "lightInactiveThin": patch["light"]["backdropToneResponseThin"],
                "lightInactiveThick": patch["light"]["backdropToneResponseThick"],
                "darkInactiveThin": patch["dark"]["backdropToneResponseThin"],
                "darkInactiveThick": patch["dark"]["backdropToneResponseThick"],
            },
            "nativeCensusCrossCheck": {
                "$comment": "footprint mask; the inactive fixture's credibility, independent of the fit",
                "1x-dark active Y": native("mid-dark-solid__capsule-button__rest", "1x-dark-standard", "active", "meanLinear"),
                "1x-dark inactive Y": native("mid-dark-solid__capsule-button__rest", "1x-dark-standard", "inactive", "meanLinear"),
                "2x-dark inactive Y": native("mid-dark-solid__capsule-button__rest", "2x-dark-standard", "inactive", "meanLinear"),
                "1x-light active Y": native("mid-dark-solid__capsule-button__rest", "1x-light-standard", "active", "meanLinear"),
                "1x-light inactive Y": native("mid-dark-solid__capsule-button__rest", "1x-light-standard", "inactive", "meanLinear"),
                "2x-light inactive Y": native("mid-dark-solid__capsule-button__rest", "2x-light-standard", "inactive", "meanLinear"),
            },
            "candidateModelForm": None,
            "whatWouldCloseIt": (
                "One uniform mid-dark-solid cell per scheme, per scale, at a thin "
                "and a thick span, captured fresh and read into the middle ordinate "
                "directly. No new field and no new law. It cannot come from the "
                "spent holdout."
            ),
        },
        {
            "id": "b",
            "name": "the light checker rrect-lg's far-span scatter, too structured at a near-native mean",
            "classification": "model-form",
            "subtype": "partly expressible; the declared ramp is not demonstrated to reach it",
            "expressibleInDeclaredFields": False,
            "field": "sizeScatterRampStartFar1x (inherited, unfitted) / sizeScatterRampStartFar2x (set by continuation)",
            "why": [
                "The inactive patch sets sizeScatterRampStartFar2x = 0.04 'by",
                "continuation' with the thick anchor and does not set",
                "sizeScatterRampStartFar1x at all, so 1x keeps the ACTIVE 0.2. The",
                "cell those two fields exist for is rrect-lg, which is holdout — the",
                "active material's own doc comment says so ('The cell the constant",
                "exists for is holdout').",
                "So part of this is the same missing evidence as (a). What makes it",
                "model-form rather than bed is the active bed's own answer: on the",
                "ACTIVE material, where far1x = 0.20 and far2x = 0.21 WERE fitted,",
                "the canonical matrix still reads checkerboard__rrect-lg interior SD",
                "1.206x native at 1x and 1.325x at 2x, against 0.87-1.07x on every",
                "span the bed does anchor. A fitted far anchor buys some authority",
                "and demonstrably does not close span 160 even in the pose it was",
                "fitted for.",
                "The reference's demand is larger inactive than active: native SD",
                "falls 0.06387 (span 96) -> 0.01742 (span 160) on the eroded body at",
                "1x light, a 3.7x step, while web falls 0.06073 -> 0.04695, a 1.29x",
                "step. The inactive/active native SD ratio in the census is 0.76-0.79",
                "at spans 32 and 44, 0.614 at 96 and 0.457 at 160: the recede's own",
                "scatter is a function of span that the ramp's three fixed anchors",
                "are not shaped to carry.",
                "Not metrology: the difference is 0.0295 of linear Y in SD, two",
                "orders above the 8-bit floor, and the cell's mean is within 0.0026",
                "of native so framing is not implicated.",
                "Not bed: the same family's calibration siblings (rrect-sm 32,",
                "capsule 44, rrect-md 96) read web/native SD 1.07, 1.00 and 0.95 at",
                "1x on the SAME recovered fixtures, so the fixtures are not suspect.",
            ],
            "decidingCells": [
                cell(rows, "1x-light-standard", "checkerboard__rrect-lg__inactive"),
                cell(rows, "2x-light-standard", "checkerboard__rrect-lg__inactive"),
                cell(rows, "1x-light-standard", "checkerboard__rrect-md__inactive"),
                cell(rows, "2x-light-standard", "checkerboard__rrect-md__inactive"),
                cell(rows, "1x-light-standard", "checkerboard__capsule-button__inactive"),
                cell(rows, "1x-light-standard", "checkerboard__rrect-sm__inactive"),
            ],
            "activeBedControl": {
                "$comment": "canonical results/matrix.json, WebGPU tier, latest row per key; interiorStdDev web/native",
                "1x-light checkerboard__rrect-lg__rest": {"native": 0.06495, "web": 0.07832, "ratio": 1.206},
                "2x-light checkerboard__rrect-lg__rest": {"native": 0.08096, "web": 0.10727, "ratio": 1.325},
                "1x-light checkerboard__rrect-md__rest": {"native": 0.11307, "web": 0.10967, "ratio": 0.970},
                "1x-light checkerboard__rrect-sm__rest": {"native": 0.15489, "web": 0.16521, "ratio": 1.067},
            },
            "candidateModelForm": (
                "A span-continued scatter law rather than three fixed span anchors: "
                "the heavy share (or the heavy tap's width) as a monotone function of "
                "span that keeps rising past sizeSpanMax, where today sizeThickness "
                "saturates at span 96 and every span above it is described by one far "
                "anchor. Named, not fitted, and not fitted by this gate."
            ),
            "whatWouldCloseIt": (
                "A span ladder on one structured backdrop — spans 32, 44, 96, 128, 160 "
                "— at both scales in both schemes, inactive, so the scatter's span "
                "dependence is measured rather than anchored at three points."
            ),
        },
        {
            "id": "c",
            "name": "the dark photo rrect-lg's colour/spatial miss at near-native mean Y",
            "classification": "model-form",
            "expressibleInDeclaredFields": False,
            "field": "optics.regular.tintAlpha (light inherits the active 0.46; dark 0.9 -> 0.89) against backdropToneResponseThin/Thick",
            "why": [
                "This one is decided against 'bed' by its own calibration siblings.",
                "The dark photo rrect-md at span 96 is a CALIBRATION cell and reads",
                "body ΔE 0.06018 at 1x and 0.05837 at 2x with mean Y within 0.0018",
                "of native — the same failure, at the same magnitude, inside the",
                "fitted set. The holdout's rrect-lg reads 0.06967 / 0.06759. The",
                "holdout did not reveal this; it re-measured it one span up.",
                "",
                "The cause is a missing degree of freedom, and the correction below",
                "is per scheme because the two schemes' alphas are different numbers",
                "moving in different directions. The renderer's body is a LERP,",
                "`mix(backdrop, tint, tintAlpha)`, so that one alpha sets how much of",
                "the backdrop survives — its level AND its chroma together.",
                "In LIGHT the inactive patch does not set the field at all: it",
                "inherits the active 0.46, which §5.130's own table records as",
                "'inherited active 0.46' beside the 0.37 perturbation that was tried",
                "and declined.",
                "In DARK the active profile is already at 0.9 — a difference document",
                "over DEFAULT_MATERIAL_PROFILE, W21 G1's fitted passthrough — and the",
                "inactive patch moves it to 0.89, which is marginally LESS opaque,",
                "not more.",
                "So in neither scheme does the recede reach its level by closing the",
                "lerp. Both reach it through backdropToneResponseThin/Thick, a SCALAR",
                "interior-level target with no chroma channel at all.",
                "That is the model-form gap, stated exactly: the one declared field",
                "that governs chroma transmission is left where the active pose put",
                "it, and the field that does move sets a level. Meanwhile the",
                "reference RAISES its chroma retention as span grows — OKLab C ratio",
                "inactive/active on untinted photo reads 1.07-1.12 at span 96 and",
                "1.23-1.29 at span 160 in BOTH schemes, and 1.01-1.04 at spans 32-44",
                "in LIGHT only (dark has no span-32 rung, and its span-44 capsule",
                "reads 0.94 at 1x and 0.77 at 2x, the latter being the",
                "minority-active pair §5.128 §1 excludes from focus-response",
                "reading). No setting of the declared fields raises chroma",
                "transmission in either scheme, which is why this is model-form and",
                "not a mis-set value.",
            ],
            "decidingCells": [
                cell(rows, "1x-dark-standard", "photo__rrect-lg__inactive"),
                cell(rows, "2x-dark-standard", "photo__rrect-lg__inactive"),
                cell(rows, "1x-dark-standard", "photo__rrect-md__inactive"),
                cell(rows, "2x-dark-standard", "photo__rrect-md__inactive"),
                cell(rows, "1x-dark-standard", "photo__capsule-button__inactive"),
                cell(rows, "1x-light-standard", "photo__rrect-md__inactive"),
                cell(rows, "1x-light-standard", "photo__rrect-lg__inactive"),
            ],
            "candidateModelForm": (
                "A transmission term with a chroma channel: the inactive body as a "
                "neutral-density absorber over a transmitted backdrop (level down, "
                "chroma scaled by its own coefficient that may exceed the level's), "
                "rather than an opaque neutral layer whose alpha sets both at once. "
                "Named, not fitted."
            ),
            "whatWouldCloseIt": (
                "A chromatic-backdrop span ladder in both schemes, inactive, read on "
                "chroma as well as level — the experiment in experiment.json."
            ),
        },
        {
            "id": "d",
            "name": "the light photo stacks — 'the one-plane endpoint does not close stacking'",
            "classification": "metrology",
            "subtype": "the measured plane is not the endpoint's plane, and the runtime has since changed",
            "expressibleInDeclaredFields": None,
            "field": "not applicable — the overlay resolves css-backdrop / analysis: none",
            "why": [
                "The stack cells' recorded `actualGroups` settle this without any new",
                "capture. Their overlay is not a sampled surface: it resolves",
                "configuredSource dom, samplingBackend css-backdrop, refraction",
                "approximate, analysis none, and paints the UNSAMPLED material. In",
                "the light scheme that material is recorded in the holdout rows as",
                "tint [1, 1, 1] at tintAlpha 0.6649600815626966 — the flat white of",
                "claims §5.129 §3, byte-for-byte the ACTIVE value, because the light",
                "inactive patch changes no field that feeds it. The inactive endpoint",
                "does not reach the second plane at all, so these cells cannot be",
                "evidence about it.",
                "This is SIX holdout rows, not the two the residual is named for:",
                "both light photo stacks and all four checkerboard stacks (1x and 2x",
                "light at the same flat white; 1x and 2x dark at tint",
                "[0.05, 0.05, 0.05] / 0.9116188858455282). W27f G1 replaced this path",
                "in BOTH schemes, so the dark stacks are as stale as the light ones.",
                "Twenty-four of the thirty holdout rows are texture-sourced and still",
                "describe today's runtime; six are not.",
                "Second, the rows are stale. holdout.json's own sourceSha256 block",
                "names packages/platform-web/src/optics.ts, packages/platform-web/",
                "src/root.ts and packages/renderer-webgpu/src/wgsl/optics.ts, and all",
                "three differ from main today: W27f G1 (claims §5.131, merged",
                "6ae37c1) replaced exactly that flat with a profile-at-tone",
                "derivation, and it landed AFTER this holdout was captured (§5.130 §6",
                "records integration only through 38d782c). The two profile documents",
                "and receded-profile.ts are unchanged and the goldens did not move,",
                "so the twenty-four texture-sourced holdout rows still describe",
                "today's runtime; these six do not.",
                "Third, what is left after the overlay is set aside is the photo",
                "family's own residual, not a stacking term. The light photo stack's",
                "body underlifts by 0.0329 Y where photo rrect-md underlifts by",
                "0.0308 and photo rrect-lg by 0.0267, and its body ΔE 0.05075 sits",
                "between rrect-md's 0.04771 and rrect-lg's 0.05921.",
                "NO stack-specific excess is quoted. The achromatic control that",
                "would bound it is checkerboard__glass-over-glass__inactive, and it",
                "carries the same replaced overlay as the photo stacks, so it",
                "inherits exactly the staleness that sets those aside. Every stack",
                "scene in the bed is a DOM-overlay scene, so no unaffected row exists",
                "to re-derive it from. The stack-specific term is UNMEASURED at this",
                "gate, not small: A4 on the checking bed is what would measure it.",
            ],
            "decidingCells": [
                cell(rows, "1x-light-standard", "photo__glass-over-glass__inactive"),
                cell(rows, "2x-light-standard", "photo__glass-over-glass__inactive"),
                cell(rows, "1x-light-standard", "checkerboard__glass-over-glass__inactive"),
                cell(rows, "2x-light-standard", "checkerboard__glass-over-glass__inactive"),
                cell(rows, "1x-dark-standard", "checkerboard__glass-over-glass__inactive"),
                cell(rows, "2x-dark-standard", "checkerboard__glass-over-glass__inactive"),
                cell(rows, "1x-light-standard", "photo__rrect-md__inactive"),
                cell(rows, "1x-light-standard", "photo__rrect-lg__inactive"),
            ],
            "staleHoldoutRows": {
                "$comment": "every holdout row carrying a css-backdrop group, i.e. the replaced DOM overlay path",
                "n": 6,
                "rows": [
                    "1x-light-standard checkerboard__glass-over-glass__inactive",
                    "2x-light-standard checkerboard__glass-over-glass__inactive",
                    "1x-light-standard photo__glass-over-glass__inactive",
                    "2x-light-standard photo__glass-over-glass__inactive",
                    "1x-dark-standard checkerboard__glass-over-glass__inactive",
                    "2x-dark-standard checkerboard__glass-over-glass__inactive",
                ],
                "textureSourcedRowsStillCurrent": 24,
            },
            "recordedOverlayState": {
                "light": {"samplingBackend": "css-backdrop", "analysis": "none", "unsampledMaterial": {"tint": [1, 1, 1], "tintAlpha": 0.6649600815626966}},
                "dark": {"samplingBackend": "css-backdrop", "analysis": "none", "unsampledMaterial": {"tint": [0.05, 0.05, 0.05], "tintAlpha": 0.9116188858455282}},
            },
            "candidateModelForm": None,
            "whatWouldCloseIt": (
                "Re-read the stack scenes against the current runtime once W27f G2 "
                "has landed the page material, on the checking bed and not on the "
                "spent holdout — both backdrops and both schemes, since all six rows "
                "are affected. Until then §5.130 §7's sentence about stacking is "
                "withdrawn rather than carried, and no stack-specific excess is "
                "claimed in either direction."
            ),
        },
        {
            "id": "e",
            "name": "full-strength neutral tint removing the photo's background chroma where native keeps it",
            "classification": "model-form",
            "expressibleInDeclaredFields": False,
            "field": "tintChromaScale (0 inactive), tintShadeCollapseRetention (1 inactive), tintShadeStrength",
            "why": [
                "Decided against 'bed' by its own calibration and validation",
                "siblings, and the span trend runs straight through all three sets:",
                "photo capsule tint-orange (span 44, CALIBRATION) body ΔE 0.03483,",
                "photo rrect-md tint-orange (span 96, VALIDATION) 0.05689, photo",
                "rrect-lg tint-orange (span 160, holdout) 0.07055. The same three at",
                "2x read 0.03517 / 0.05667 / 0.07026. The holdout is the third point",
                "on a line the fitted bed already drew.",
                "The G0 census names the model-form error precisely. `tintChromaScale",
                "= 0` was identified on the CHECKERBOARD tinted capsules, where the",
                "backdrop is achromatic and the reference's inactive tinted body",
                "really does read OKLab C 0.000662 (§5.128). Over the photo the same",
                "reference keeps 0.03539 on the capsule and 0.07027 on rrect-lg —",
                "which is as much chroma as the UNTINTED active photo rrect-lg has",
                "(0.07488). So the facet is not 'the author hue is removed'; it is",
                "'the author hue is removed AND the backdrop's chroma is transmitted',",
                "and the second half grows with span exactly as in residual (c).",
                "A full-strength authored layer is opaque in the declared family, so",
                "no value of tintChromaScale, tintShadeStrength, tintShadeDark or",
                "tintShadeLight lets backdrop chroma through it. §5.130 §2 records",
                "that tintChromaScale 'scales the seed's saturation toward its maximum",
                "linear channel before the shade law' — it acts on the seed, and the",
                "backdrop's chroma is lost to the layer's opacity, not to the seed.",
                "The opacity in question is the AUTHOR STRENGTH's, at 1 on these",
                "cells, and it is a different quantity from the body lerp's",
                "optics.regular.tintAlpha that residual (c) is about. On a tinted",
                "cell the two remove the backdrop's chroma in series, which is why",
                "the tinted span ladder runs above the untinted one at every span.",
            ],
            "decidingCells": [
                cell(rows, "1x-light-standard", "photo__capsule-button__inactive-tint-orange"),
                cell(rows, "1x-light-standard", "photo__rrect-md__inactive-tint-orange"),
                cell(rows, "1x-light-standard", "photo__rrect-lg__inactive-tint-orange"),
                cell(rows, "2x-light-standard", "photo__capsule-button__inactive-tint-orange"),
                cell(rows, "2x-light-standard", "photo__rrect-md__inactive-tint-orange"),
                cell(rows, "2x-light-standard", "photo__rrect-lg__inactive-tint-orange"),
                cell(rows, "1x-light-standard", "checkerboard__capsule-button__inactive-tint-orange"),
                cell(rows, "1x-light-standard", "dark-solid__capsule-button__inactive-tint-orange"),
            ],
            "nativeTintedChroma": {
                "$comment": "G0 census, footprint mask, 1x light standard, active -> inactive OKLab C",
                "checkerboard capsule tint-orange": [0.16424, 0.00066],
                "photo capsule tint-orange": [0.16323, 0.03539],
                "photo rrect-md tint-orange": [0.16611, 0.05688],
                "photo rrect-lg tint-orange": [0.16676, 0.07027],
                "photo rrect-lg untinted (for scale)": [0.07488, 0.09654],
            },
            "candidateModelForm": (
                "The same transfer term as (c), with the authored paint applied as an "
                "absorbing filter on the transmitted backdrop rather than as an opaque "
                "shaded layer: the hue goes to neutral and the transmission stays, so "
                "a chromatic backdrop's haze survives a full-strength tint. One term "
                "would then serve (c) and (e). Named, not fitted."
            ),
            "whatWouldCloseIt": (
                "The same chromatic-backdrop span ladder as (c), run tinted and "
                "untinted, so the tint's effect on transmitted chroma is separable "
                "from the body's."
            ),
        },
    ]


# ---------------------------------------------------------------------------

def main() -> None:
    checked = load("checked")["rows"]
    holdout_doc = load("holdout")
    holdout = holdout_doc["rows"]
    scenes = load("scenes")
    recede = load("recede")
    declaration = load("declaration")

    provenance = {
        "gate": "W27c G1b / claims §5.134",
        "declaredIn": "docs/doperpowers/specs/2026-09-10-w27-coverage-wave.md (child W27c, gate G1b; Decision Log 12)",
        "reads": "committed evidence only; no capture, no compare run, no holdout re-read",
        "sources": {
            name: {
                "path": os.path.relpath(path, ROOT),
                "sha256": sha256(path),
            }
            for name, path in sorted(SOURCES.items())
        },
        "spentHoldout": {
            "status": holdout_doc["label"] + " / spent",
            "patchSha256": holdout_doc["patchSha256"],
            "n": len(holdout),
            "$comment": "read from the record; never re-measured, never fitted back",
        },
    }

    out = {
        "coverage.json": {"provenance": provenance, **coverage(scenes)},
        "decomposition.json": {
            "provenance": provenance,
            **decomposition(checked, holdout),
            "againstAdoptedActiveBedBounds": against_adopted(holdout),
            "nativeSpanBehaviour": native_span_behaviour(recede, scenes),
        },
        "classification.json": {
            "provenance": provenance,
            "$comment": [
                "Model-form: no setting of the declared fields can express it.",
                "Bed: the evidence for that cell is absent or suspect.",
                "Metrology: the comparison itself is the limit.",
                "Where a residual's own family has calibration cells that agree with",
                "the holdout cell, that is evidence against 'bed', and it is quoted.",
            ],
            "residuals": residuals(checked, holdout, declaration, recede),
        },
    }

    for name, document in out.items():
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as handle:
            json.dump(document, handle, indent=1, ensure_ascii=False)
            handle.write("\n")
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
