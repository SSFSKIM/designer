#!/usr/bin/env python3
"""W27e G1 — the browser proof, read against the tolerance declared before it.

`operator-probe/results.json` is the reading. This scores it against
declaration §3: every channel of every case must agree with the closed-form
arithmetic to within 1 code value of 255, and the maximum observed difference is
what gets published as the operator's tolerance.

What that tolerance bounds is the analytic operator against the browser's
composite of it. It is not a bound between vitrea and macOS.

Three verdicts come out of the same reading:

  A. the declared path (`feColorMatrix` at sRGB, source-over) against the closed
     form, per scheme, per ink, per ground;
  B. the CPU fold against the declared path — the `css-backdrop` tier's only
     available route, and whether it loses anything;
  C. the alternative reading (the scheme's plus blend) against the declared one,
     which is the size of the disagreement no native pixel can arbitrate.

The closed form is evaluated here, not read out of `results.json`. `run.mjs`
wrote an `expected` block, but it built every model from `reading.filtered`,
which `probe.js` computed inside the browser under test — so it was not the
independent check its comment claimed. This file re-derives the filtered ink
from the matrices the run recorded and publishes the disagreement against the
page's own arithmetic rather than assuming it away.

Writes `verdict.json` beside itself.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
READING = json.load(open(os.path.join(HERE, "operator-probe", "results.json")))
OUT = os.path.join(HERE, "verdict.json")
BOUND = READING["declaredTolerance"]["bound"]
MATRICES = READING["matrices"]

bench = [r for r in READING["cases"]["bench"]["readings"].values() if r["kind"] == "bench"]
by_key = {(r["scheme"], r["arm"], r["ink"], r["groundIndex"]): r for r in bench}


def diff(mean, expected):
    return max(abs(m - e) for m, e in zip(mean, expected))


def number(value):
    """A whole value prints without a decimal point, as `JSON.stringify`'s did.

    The expected colours used to be read straight out of `results.json`, where
    they had been written by JavaScript; computing them here would otherwise
    rewrite every `0` in the file as `0.0` and bury the changes that matter.
    """
    return int(value) if float(value).is_integer() else value


def hex_channels(value):
    n = value.lstrip("#")
    return [int(n[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def clamp01(value):
    return 0.0 if value < 0.0 else (1.0 if value > 1.0 else value)


def apply_matrix(rgba, matrix):
    """Apple's matrix on non-premultiplied encoded sRGB, `inputClamp` = 1.

    Four rows of five columns in row order. `feColorMatrix` and `CAColorMatrix`
    both operate on non-premultiplied channels, which is what antialiased glyph
    edges need, and the clamp is a plain [0, 1] clamp on the encoded channel
    after the matrix.
    """
    out = []
    for row in range(4):
        total = matrix[row * 5 + 4]
        for col in range(4):
            total += matrix[row * 5 + col] * rgba[col]
        out.append(clamp01(total))
    return out


def painted_ink(reading):
    """The colour the cell actually hands the compositor, which differs by arm.

    `probe.js` paints `over` and `plusblend` with the raw ink under a `filter`
    and `fold` with the matrix already applied on the CPU, so all three show the
    compositor the FILTERED ink. `blendonly` carries no `filter` at all — it is
    the documented AppKit vibrancy blend without any matrix, kept for scale — so
    it shows the RAW ink, and a model built on the filtered ink scores it
    against a colour that was never painted.
    """
    ink = hex_channels(reading["inkColor"]) + [reading["inkAlpha"]]
    if reading["arm"] == "blendonly":
        return ink
    return apply_matrix(ink, MATRICES[reading["scheme"]])


def expectations(reading):
    """The closed form and the two composites, on the ink that cell paints."""
    source = painted_ink(reading)
    ground = hex_channels(reading["ground"])
    a = source[3]
    source_over = [a * source[i] + (1 - a) * ground[i] for i in range(3)]
    # The alternative reading's blends, on the opaque grounds this bench paints
    # (αb = 1 throughout). `plus-lighter` is the CSS Compositing 2 form,
    # Co = αs·Cs + αb·Cb clamped to 1. `plus-darker` is NOT taken from that
    # spec: its §9.1.14 text is the broken Apple-derived one
    # (w3c/fxtf-drafts#447), and Apple's own two published formulas disagree
    # with each other. The form below is the one measured against Safari in that
    # issue and endorsed by the CSSWG for the spec —
    # co = min(1, αs + αb) − min(1, αs(1 − Cs) + αb(1 − Cb)) — evaluated at
    # αb = 1, where it reduces to the expression written here.
    plus_lighter = [clamp01(a * source[i] + ground[i]) for i in range(3)]
    plus_darker = [clamp01(1 - (a * (1 - source[i]) + (1 - ground[i]))) for i in range(3)]
    scale = lambda channels: [number(round(c * 255 * 100) / 100) for c in channels]
    return {"sourceOver": scale(source_over), "plusLighter": scale(plus_lighter),
            "plusDarker": scale(plus_darker)}


EXPECTED = {r["id"]: expectations(r) for r in bench}

# How far this file's evaluation of Apple's twenty numbers sits from the page's.
# The two are the same arithmetic run in two languages on two float widths, so
# the figure is the independence check's own error bar: it says how much of the
# agreement reported below could be an artefact of trusting the browser's
# `filtered` rather than the matrix. Published, not asserted.
recompute_worst = {"maxAbsDiffUnitInterval": -1.0}
for r in bench:
    ink = hex_channels(r["inkColor"]) + [r["inkAlpha"]]
    independent = apply_matrix(ink, MATRICES[r["scheme"]])
    d = max(abs(i - p) for i, p in zip(independent, r["filtered"]))
    if d > recompute_worst["maxAbsDiffUnitInterval"]:
        recompute_worst = {"maxAbsDiffUnitInterval": d, "maxAbsDiffCodeValues": d * 255,
                           "cell": r["id"], "independent": independent, "page": r["filtered"]}
independent_check = {
    "what": "this file's evaluation of `matrices` against the `filtered` ink `probe.js` "
            "computed in the page, over every bench cell",
    "why": "the closed form scored below is only independent of the engine under test if the "
           "filtered ink is re-derived outside it; this is how far the two derivations sit apart",
    "n": len(bench),
    "usedForScoring": "the independent value",
    "maxAbsDiffUnitInterval": recompute_worst["maxAbsDiffUnitInterval"],
    "maxAbsDiffCodeValues": recompute_worst["maxAbsDiffCodeValues"],
    "worst": {k: recompute_worst[k] for k in ("cell", "independent", "page")},
}


# -- A. the declared path against the closed form --------------------------
#
# Every arm is scored against the operator the engine actually performed on the
# ink that arm actually painted. That is one model per arm per scheme, because
# `plus-darker` is not expressible in this engine: a light-scheme cell that asks
# for it computes to `normal`, so what it performed is source-over. `plusblend`
# is nevertheless scored against `plusDarker` in light — it is the arm whose
# whole purpose is to size the refuted reading, and the distance from the model
# the engine could not run is the number that sizes it. `blendonly` has no such
# purpose: it carries no matrix, so scoring it against a model it neither
# painted nor performed measured nothing at all.
MODELS = {
    "over": {"light": "sourceOver", "dark": "sourceOver"},
    "fold": {"light": "sourceOver", "dark": "sourceOver"},
    "plusblend": {"light": "plusDarker", "dark": "plusLighter"},
    "blendonly": {"light": "sourceOver", "dark": "plusLighter"},
}
NOTES = {
    "plusblend": "not an arm the declared bound applies to; it is the size of the refuted "
                 "reading. In light the engine rejected `plus-darker` and computed `normal`, "
                 "so the reading is of the source-over fallback against the model named above, "
                 "which is the disagreement itself and not an error",
    "blendonly": "not an arm the declared bound applies to, and not an arm that carries the "
                 "operator: it paints the RAW ink with no matrix, so it is scored against the "
                 "raw ink under the blend the engine performed — `plus-lighter` in dark, where "
                 "the blend is supported, and source-over in light, where it is not. Its "
                 "agreement corroborates the engine's plus-lighter against closed form on an "
                 "unfiltered source; it says nothing about Apple's matrix",
}
arm_scores = {}
for arm in ("over", "fold", "plusblend", "blendonly"):
    rows = [r for r in bench if r["arm"] == arm]
    model = MODELS[arm]
    worst = {"value": -1.0}
    for r in rows:
        key = model[r["scheme"]]
        d = diff(r["mean"], EXPECTED[r["id"]][key])
        if d > worst["value"]:
            worst = {"value": round(d, 4), "cell": r["id"], "mean": r["mean"],
                     "expected": EXPECTED[r["id"]][key], "model": key}
    # The declared bound applies to the two arms the declaration named — the
    # operator's own path and its CPU fold. The two alternative-reading arms are
    # not bound by it and must not carry a field that reads as a failed bound.
    declared = arm in ("over", "fold")
    arm_scores[arm] = {
        "n": len(rows),
        "model": "sourceOver" if declared else model,
        "scoredAgainstInk": "raw (this arm paints no matrix)" if arm == "blendonly"
                            else "filtered (the matrix, recomputed outside the engine)",
        "maxAbsDiffCodeValues": worst["value"],
        "worst": worst,
        "computedBlends": sorted({r["computedBlend"] for r in rows}),
    }
    if declared:
        arm_scores[arm]["withinDeclaredBound"] = worst["value"] <= BOUND
    else:
        arm_scores[arm]["note"] = NOTES[arm]
        arm_scores[arm]["perScheme"] = {
            scheme: {
                "model": model[scheme],
                "maxAbsDiffCodeValues": max(
                    round(diff(r["mean"], EXPECTED[r["id"]][model[scheme]]), 4)
                    for r in rows if r["scheme"] == scheme),
            }
            for scheme in ("light", "dark")
        }

# -- B. the fold against the declared path ---------------------------------
fold_rows = []
for (scheme, arm, ink, gi), r in by_key.items():
    if arm != "over":
        continue
    f = by_key[(scheme, "fold", ink, gi)]
    fold_rows.append({
        "id": r["id"], "scheme": scheme, "ink": ink, "ground": r["ground"],
        "over": r["mean"], "fold": f["mean"], "absDiff": round(diff(r["mean"], f["mean"]), 4),
    })
fold_max = max(fold_rows, key=lambda x: x["absDiff"])

# -- C. the alternative reading against the declared one -------------------
#
# The engine can only carry HALF of this arm. `mix-blend-mode: plus-lighter` is
# supported and `plus-darker` is not — the run asks `CSS.supports` rather than
# inferring it, because a rejected value computes to `normal` and a light-scheme
# reading taken through a silently-dropped blend would look like two readings
# agreeing when they were never compared. So the dark half is measured in the
# browser and the light half is stated from the closed form, marked as such.
SUPPORT = READING["blendSupport"]
BLEND_SUPPORTED = {"light": SUPPORT["mix-blend-mode: plus-darker"],
                   "dark": SUPPORT["mix-blend-mode: plus-lighter"]}
MODEL = {"light": "plusDarker", "dark": "plusLighter"}

alt_rows = []
for (scheme, arm, ink, gi), r in by_key.items():
    if arm != "over":
        continue
    p = by_key[(scheme, "plusblend", ink, gi)]
    measured = BLEND_SUPPORTED[scheme]
    alternative = p["mean"] if measured else EXPECTED[p["id"]][MODEL[scheme]]
    alt_rows.append({
        "id": r["id"], "scheme": scheme, "ink": ink, "ground": r["ground"],
        "declared": r["mean"], "alternative": alternative,
        "alternativeSource": "browser" if measured else "closed form (engine cannot express it)",
        "absDiff": round(diff(r["mean"], alternative), 4),
    })
alt_max = max(alt_rows, key=lambda x: x["absDiff"])
alt_by_scheme = {}
for scheme in ("light", "dark"):
    rows = [a for a in alt_rows if a["scheme"] == scheme]
    top = max(rows, key=lambda x: x["absDiff"])
    alt_by_scheme[scheme] = {
        "n": len(rows), "blendExpressibleInThisEngine": BLEND_SUPPORTED[scheme],
        "maxAbsDiffCodeValues": top["absDiff"], "worst": top,
    }
# The ink Apple actually feeds the operator: pure black in light, pure white in
# dark. Where the readings agree there, the semantics question has no
# consequence for anything Apple ships; where they do not, it does — and the
# dark row is where the matrix's alpha 0.95 decides it, because that coefficient
# is a visible 5 % pull-back under the declared reading and inert under the
# alternative, which saturates to white whatever the alpha.
apple_ink = {"light": "black-100", "dark": "white-100"}
apple_rows = [a for a in alt_rows if a["ink"] == apple_ink[a["scheme"]]]
apple_max = max(apple_rows, key=lambda x: x["absDiff"])

# -- The glass arm ---------------------------------------------------------
glass = {}
for name, case in READING["cases"].items():
    if name == "bench":
        continue
    readings = case["readings"]
    row = {"tier": case["tier"], "scheme": case["scheme"],
           "samplingBackend": case["state"]["samplingBackend"],
           "bareMaterial": readings["bare-material"]["mean"],
           "bareMaterialSdMax": readings["bare-material"]["sdMax"]}
    if "glass-over" in readings:
        over, fold = readings["glass-over"], readings["glass-fold"]
        row |= {
            "over": over["mean"], "overSdMax": over["sdMax"],
            "fold": fold["mean"], "foldSdMax": fold["sdMax"],
            "overVsFold": round(diff(over["mean"], fold["mean"]), 4),
        }
    if "glass-plusblend" in readings:
        alt = readings["glass-plusblend"]
        row |= {"plusblend": alt["mean"], "plusblendSdMax": alt["sdMax"],
                "plusblendComputedBlend": alt["computedBlend"]}
    glass[name] = row

declared_arms = ("over", "fold")
verdict = {
    "declaredTolerance": READING["declaredTolerance"],
    "engine": READING["engine"],
    "adapter": READING["adapter"],
    "independentClosedFormVsPageFiltered": independent_check,
    "A_declaredPathAgainstClosedForm": {a: arm_scores[a] for a in declared_arms},
    "A_measuredTolerance": max(arm_scores[a]["maxAbsDiffCodeValues"] for a in declared_arms),
    "A_passes": all(arm_scores[a]["withinDeclaredBound"] for a in declared_arms),
    "B_foldAgainstDeclaredPath": {
        "n": len(fold_rows), "maxAbsDiffCodeValues": fold_max["absDiff"], "worst": fold_max,
    },
    "C_alternativeReading": {
        "blendSupport": SUPPORT,
        "arms": {a: arm_scores[a] for a in ("plusblend", "blendonly")},
        "againstDeclared": {"n": len(alt_rows), "maxAbsDiffCodeValues": alt_max["absDiff"],
                            "worst": alt_max, "perScheme": alt_by_scheme},
        "atAppleOwnInk": {"n": len(apple_rows), "inks": apple_ink,
                          "maxAbsDiffCodeValues": apple_max["absDiff"], "worst": apple_max},
    },
    "glass": glass,
    "rows": {"fold": fold_rows, "alternative": alt_rows},
}
json.dump(verdict, open(OUT, "w"), indent=1, sort_keys=True)
json.dump({k: v for k, v in verdict.items() if k != "rows"}, sys.stdout, indent=1, sort_keys=True)
print()
