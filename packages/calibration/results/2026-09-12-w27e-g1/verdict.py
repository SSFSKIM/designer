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

Writes `verdict.json` beside itself.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
READING = json.load(open(os.path.join(HERE, "operator-probe", "results.json")))
OUT = os.path.join(HERE, "verdict.json")
BOUND = READING["declaredTolerance"]["bound"]

bench = [r for r in READING["cases"]["bench"]["readings"].values() if r["kind"] == "bench"]
by_key = {(r["scheme"], r["arm"], r["ink"], r["groundIndex"]): r for r in bench}


def diff(mean, expected):
    return max(abs(m - e) for m, e in zip(mean, expected))


# -- A. the declared path against the closed form --------------------------
arm_scores = {}
for arm in ("over", "fold", "plusblend", "blendonly"):
    rows = [r for r in bench if r["arm"] == arm]
    if arm in ("over", "fold"):
        model = "sourceOver"
    else:
        model = {"light": "plusDarker", "dark": "plusLighter"}
    worst = {"value": -1.0}
    for r in rows:
        key = model if isinstance(model, str) else model[r["scheme"]]
        d = diff(r["mean"], r["expected"][key])
        if d > worst["value"]:
            worst = {"value": round(d, 4), "cell": r["id"], "mean": r["mean"],
                     "expected": r["expected"][key], "model": key}
    arm_scores[arm] = {
        "n": len(rows),
        "model": model if isinstance(model, str) else model,
        "maxAbsDiffCodeValues": worst["value"],
        "worst": worst,
        "withinDeclaredBound": worst["value"] <= BOUND,
        "computedBlends": sorted({r["computedBlend"] for r in rows}),
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
    alternative = p["mean"] if measured else r["expected"][MODEL[scheme]]
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
