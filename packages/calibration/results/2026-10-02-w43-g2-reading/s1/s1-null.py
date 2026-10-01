"""W43 G2 (f): S1 rehearsed on the perfect-endpoint null, before any vitrea render at 0.25 exists.

Charter, Design "Referees" (S1) and Decision Log 5 (c). S1 as chartered: on every non-holdout
standard cell where Apple's 0.25-to-0.5 change in interior level exceeds its bar, vitrea's change has
the same sign, and the median ratio of vitrea's change to Apple's lies in [0.8, 1.2].

THE NULL. Put Apple's own 0.25 capture in vitrea's 0.25 place. With the shipped 0.5 render's error
e = vitrea@0.5 − Apple@0.5 read off the current generation's rows, vitrea's change becomes
V = Apple@0.25 − vitrea@0.5 = dA − e, and its ratio to Apple's change dA = Apple@0.25 − Apple@0.5 is
1 − e/dA. Wherever that ratio is negative the sign clause fails an endpoint that matches Apple
exactly; wherever it leaves [0.8, 1.2] the cell pulls the median away. This maps those cells.

THE ANTI-NULL, beside it: a 0.25 endpoint that did not move at all (vitrea@0.25 = vitrea@0.5,
V = 0) must FAIL any S1 worth adopting. A restatement is read on both.

Two level readings, both under the declared geometry of the native delta:
- ``interiorMean``: the mean linear luminance under each capture's OWN extracted silhouette, which
  is what the matrix rows carry (``interiorMeanNative`` / ``interiorMeanWeb``) and so what G3's S1 read
  off rows would use. The 0.5 side's value is checked equal to the row's ``interiorMeanNative``.
- ``bodyLevel``: the declared box eroded 6 CSS px, mask-free (W21's body; §5.151 §4). vitrea's 0.5
  value is read off the canonical capture tree (read-only; ``check-capture-tree`` exit 0 at this
  read), with this script's reader checked equal to the native delta's on the 0.5 fixtures.

Apple's change is barred per cell by the reading's two-sided run-to-run spread: the larger of the
0.25 side's (zero everywhere) and the 0.5 side's (W29's, with its bed-minimum fallback), as
``bar-declaration.md`` declares for the recede's inputs.

    python3.12 -B s1-null.py [--tree <web-captures dir>]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
RESULTS = EVIDENCE.parent
REPO = RESULTS.parents[2]
sys.path.insert(0, str(RESULTS / "2026-09-26-w40-g0-generations"))
import matrix_store  # noqa: E402

PROFILES = [
    "apple-macos-27.0-1x-light-standard-glass0.25",
    "apple-macos-27.0-2x-light-standard-glass0.25",
    "apple-macos-27.0-1x-dark-standard-glass0.25",
    "apple-macos-27.0-2x-dark-standard-glass0.25",
]
NON_HOLDOUT = {"calibration", "validation", "recorded", "probe"}
TIERS = ("webgpu", "css")
READINGS = ("interiorMean", "bodyLevel")
ERODE_CSS_PX = 6


def srgb_to_linear(byte: np.ndarray) -> np.ndarray:
    c = byte / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def body_level(path: Path, box: tuple[float, float, float, float], scale: int) -> float:
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    lum = 0.2126 * srgb_to_linear(rgb[..., 0]) + 0.7152 * srgb_to_linear(rgb[..., 1]) + 0.0722 * srgb_to_linear(rgb[..., 2])
    x0, y0, x1, y1 = box
    e = ERODE_CSS_PX * scale
    h, w = lum.shape
    yc = np.arange(h) + 0.5
    xc = np.arange(w) + 0.5
    ys = (yc >= y0 + e) & (yc < y1 - e)
    xs = (xc >= x0 + e) & (xc < x1 - e)
    return float(lum[np.ix_(ys, xs)].mean())


def declared_box(scenes: dict, scene_id: str, scale: int):
    scene = next(s for s in scenes["scenes"] if s["id"] == scene_id)
    component = scenes["components"][scene["component"]]
    if "size" not in component:
        return None
    w, h = component["size"]
    cx, cy = scenes["canvas"]["width"] / 2, scenes["canvas"]["height"] / 2
    return ((cx - w / 2) * scale, (cy - h / 2) * scale, (cx + w / 2) * scale, (cy + h / 2) * scale)


def median(values):
    if not values:
        return math.nan
    s = sorted(values)
    return s[len(s) // 2]


def reading_bound(cell, name, floor):
    if cell is None:
        return None
    own = cell["readingSpread"].get(name)
    if own is None:
        return None
    if own > 0:
        return own
    return 0.0 if floor is None else floor


def floor_of(bar, name):
    values = [c["readingSpread"].get(name, 0) for c in bar["cells"]]
    values = [v for v in values if v > 0]
    return min(values) if values else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", default="/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
    args = parser.parse_args()
    tree = Path(args.tree)
    delta = json.loads((EVIDENCE / "delta" / "slider-delta.json").read_text())
    by_cell = {(r["profileKey"], r["sceneId"]): r for r in delta["rows"]}
    subject_bar = json.loads((EVIDENCE / "bar" / "noise-bar-0.25.json").read_text())
    reference_bar = json.loads((RESULTS / "2026-09-19-w29-g3b-shadow-recede" / "noise-bar.json").read_text())
    sub_cells = {(c["profileKey"], c["sceneId"]): c for c in subject_bar["cells"]}
    ref_cells = {(c["profileKey"], c["sceneId"]): c for c in reference_bar["cells"]}
    floors = {
        name: (floor_of(subject_bar, name), floor_of(reference_bar, name)) for name in READINGS
    }
    scenes = json.loads((REPO / "apps" / "reference-apple" / "scenes.json").read_text())

    cells: list[dict] = []
    checks = Counter()
    worst_row_check = 0.0
    worst_body_check = 0.0
    for profile in PROFILES:
        ref_profile = profile.replace("-glass0.25", "-glass0.5")
        scale = 2 if "-2x-" in profile else 1
        rows = {}
        for row in matrix_store.load_current_profile(ref_profile):
            rows[(row["key"]["web"]["renderer"], row["key"]["sceneId"])] = row
        for (key, scene), delta_row in sorted(by_cell.items()):
            if key != profile or delta_row["fixtureSet"] not in NON_HOLDOUT:
                continue
            box = declared_box(scenes, scene, scale)
            apple05 = delta_row["captureReadings"]["reference"]
            apple25 = delta_row["captureReadings"]["subject"]
            for tier in TIERS:
                row = rows.get((tier, scene))
                entry = {
                    "profileKey": profile,
                    "sceneId": scene,
                    "fixtureSet": delta_row["fixtureSet"],
                    "background": delta_row["background"],
                    "component": delta_row["component"],
                    "pose": delta_row["pose"],
                    "tier": tier,
                    "row": row is not None,
                    "readings": {},
                }
                for name in READINGS:
                    a05, a25 = apple05.get(name), apple25.get(name)
                    if a05 is None or a25 is None:
                        entry["readings"][name] = {"status": "UNMEASURED: no Apple reading"}
                        continue
                    if row is None:
                        entry["readings"][name] = {"status": "UNMEASURED: no 0.5 row on this tier"}
                        continue
                    if name == "interiorMean":
                        native = row["material"]["interiorMeanNative"]["value"]
                        web = row["material"]["interiorMeanWeb"]["value"]
                        worst_row_check = max(worst_row_check, abs(native - a05))
                        checks["interiorMean row checked"] += 1
                        v05 = web
                    else:
                        if box is None:
                            entry["readings"][name] = {"status": "UNMEASURED: composite, no declared box"}
                            continue
                        capture = tree / ref_profile / scene / f"{scene}__{tier}.png"
                        if not capture.exists():
                            entry["readings"][name] = {"status": "UNMEASURED: no capture in the tree"}
                            continue
                        v05 = body_level(capture, box, scale)
                        fixture_check = body_level(
                            REPO / "apps" / "reference-apple" / "fixtures" / ref_profile / f"{scene}.png", box, scale
                        )
                        worst_body_check = max(worst_body_check, abs(fixture_check - a05))
                        checks["bodyLevel reader checked"] += 1
                    sub_floor, ref_floor = floors[name]
                    sb = reading_bound(sub_cells.get((profile, scene)), name, sub_floor)
                    rb = reading_bound(ref_cells.get((ref_profile, scene)), name, ref_floor)
                    bar = max(b for b in (sb, rb, 0.0) if b is not None)
                    dA = a25 - a05
                    e = v05 - a05
                    entry["readings"][name] = {
                        "status": "measured",
                        "apple05": a05,
                        "apple25": a25,
                        "vitrea05": v05,
                        "dA": dA,
                        "e": e,
                        "bar": bar,
                        "appleMoved": abs(dA) > bar,
                        "nullChange": dA - e,
                        "nullRatio": (dA - e) / dA if dA != 0 else None,
                    }
                cells.append(entry)

    out: list[str] = []
    say = out.append
    say("# S1 on the perfect-endpoint null (W43 G2 (f); charter Design 'Referees', Decision Log 5 (c))")
    say("")
    say("No vitrea render at 0.25 exists or was made. vitrea@0.5 is the current generation (rows:")
    say("matrix_store.load_current_profile; captures: the canonical tree, read-only).")
    say(f"Reader checks: interiorMeanNative of the row against the native delta's own-silhouette reading of")
    say(f"the 0.5 fixture, worst |difference| {worst_row_check:.3e} over {checks['interiorMean row checked']} row reads;")
    say(f"this script's bodyLevel on the 0.5 fixture against the native delta's, worst {worst_body_check:.3e}")
    say(f"over {checks['bodyLevel reader checked']} reads.")
    say("")

    def population(tier, name, profile=None):
        out_ = []
        for c in cells:
            if c["tier"] != tier or (profile is not None and c["profileKey"] != profile):
                continue
            r = c["readings"].get(name, {})
            if r.get("status") != "measured" or not r["appleMoved"]:
                continue
            out_.append((c, r))
        return out_

    def read(subset, label):
        ratios = [r["nullRatio"] for _, r in subset]
        wrong = [(c, r) for c, r in subset if r["nullRatio"] < 0]
        outside = [(c, r) for c, r in subset if not (0.8 <= r["nullRatio"] <= 1.2)]
        med = median(ratios)
        anti_med = 0.0 if subset else math.nan
        passes_null = (not wrong) and (0.8 <= med <= 1.2) if subset else None
        say(
            f"  {label:<44} cells {len(subset):>4}  wrong sign {len(wrong):>4}  outside [0.8,1.2] {len(outside):>4}  "
            f"median ratio {med:7.3f}  perfect endpoint passes S1: {passes_null}  unmoved endpoint "
            f"(ratio 0, sign undefined) passes: {False if subset else None}"
        )
        return {"cells": len(subset), "wrongSign": len(wrong), "outsideBand": len(outside), "medianRatio": med,
                "perfectEndpointPasses": passes_null}

    record: dict = {"asChartered": {}, "restated": {}, "cells": cells}
    for name in READINGS:
        say(f"## S1 as chartered, on {name}")
        say("")
        for tier in TIERS:
            say(f"### tier {tier}")
            record["asChartered"][f"{name}/{tier}"] = {}
            record["asChartered"][f"{name}/{tier}"]["all"] = read(population(tier, name), "all four profiles")
            for profile in PROFILES:
                short = profile.replace("apple-macos-27.0-", "").replace("-standard-glass0.25", "")
                record["asChartered"][f"{name}/{tier}"][short] = read(population(tier, name, profile), short)
            unmeasured = Counter(
                c["readings"][name]["status"] for c in cells if c["tier"] == tier and c["readings"][name]["status"] != "measured"
            )
            not_moved = sum(
                1 for c in cells if c["tier"] == tier and c["readings"][name].get("status") == "measured"
                and not c["readings"][name]["appleMoved"]
            )
            say(f"  not in the population: Apple's change within its bar {not_moved}; " + ", ".join(
                f"{k} {v}" for k, v in unmeasured.items()))
            say("")
        say("")

    # Where the wrong-sign cells sit: the map, by profile, backdrop and pose.
    say("## The map: where a perfect 0.25 endpoint fails S1's sign clause (interiorMean, webgpu)")
    say("")
    wrong = [(c, r) for c, r in population("webgpu", "interiorMean") if r["nullRatio"] < 0]
    by = Counter((c["profileKey"].replace("apple-macos-27.0-", "").replace("-standard-glass0.25", ""),
                  c["background"], c["pose"]) for c, _ in wrong)
    for (profile, background, pose), n in sorted(by.items()):
        say(f"  {profile:<10} {background:<20} {pose:<9} {n}")
    say("")
    say("Each wrong-sign cell: Apple's change dA, the shipped 0.5 error e, and e/dA (> 1 is wrong sign):")
    for c, r in sorted(wrong, key=lambda cr: -cr[1]["e"] / cr[1]["dA"]):
        say(f"  {c['profileKey'].replace('apple-macos-27.0-', '').replace('-standard-glass0.25', ''):<10} "
            f"{c['sceneId']:<52} dA {r['dA']:+.4f}  e {r['e']:+.4f}  e/dA {r['e'] / r['dA']:+.2f}")
    say("")

    say("The map's other half: cells whose null ratio leaves [0.8, 1.2] (interiorMean, webgpu), by profile,")
    say("backdrop and pose, with the median |dA| (linear) of those cells beside the median |dA| of the rest:")
    outside = [(c, r) for c, r in population("webgpu", "interiorMean") if not (0.8 <= r["nullRatio"] <= 1.2)]
    inside = [(c, r) for c, r in population("webgpu", "interiorMean") if 0.8 <= r["nullRatio"] <= 1.2]
    by_out = Counter((c["profileKey"].replace("apple-macos-27.0-", "").replace("-standard-glass0.25", ""),
                      c["background"], c["pose"]) for c, _ in outside)
    for (profile, background, pose), n in sorted(by_out.items()):
        say(f"  {profile:<10} {background:<20} {pose:<9} {n}")
    say(f"  median |dA| outside the band {median([abs(r['dA']) for _, r in outside]):.4f}; inside "
        f"{median([abs(r['dA']) for _, r in inside]):.4f}; wrong-sign cells {median([abs(r['dA']) for _, r in wrong]):.4f}")
    say(f"  median |e| outside the band {median([abs(r['e']) for _, r in outside]):.4f}; inside "
        f"{median([abs(r['e']) for _, r in inside]):.4f}")
    say("")

    # Restatements, each read on both nulls.
    say("## Restatements, each read on the perfect-endpoint null and on the unmoved-endpoint anti-null")
    say("")
    say("R0  as chartered.")
    say("R1  over the cells where the shipped 0.5 render is within a fifth of Apple's change of Apple (|e| <= 0.2|dA|).")
    say("R2  over the cells where Apple's change exceeds the shipped 0.5 error (|dA| > |e|): sign on every cell, the")
    say("    median ratio clause over the same cells.")
    say("R3  as R2 for the sign; the ratio clause replaced by the pooled ratio sum(V)/sum(dA) over the population,")
    say("    in [0.8, 1.2].")
    say("R4  as R2, but the endpoint's change is judged against Apple's change measured FROM vitrea's own 0.5")
    say("    render: the 0.25 endpoint's error must not exceed the 0.5 endpoint's, |V − dA| <= |e| + bar, per cell.")
    say("")

    def restated(tier, name, which):
        subset = population(tier, name)
        if which == "R1":
            subset = [(c, r) for c, r in subset if abs(r["e"]) <= 0.2 * abs(r["dA"])]
        if which in ("R2", "R3", "R4"):
            subset = [(c, r) for c, r in subset if abs(r["dA"]) > abs(r["e"])]
        if not subset:
            return {"cells": 0}
        v_null = [r["nullChange"] for _, r in subset]
        dAs = [r["dA"] for _, r in subset]
        sign_null = all(v * d > 0 for v, d in zip(v_null, dAs))
        ratio_null = median([v / d for v, d in zip(v_null, dAs)])
        pooled_null = sum(v_null) / sum(dAs) if sum(dAs) else math.nan
        if which == "R3":
            passes_null = sign_null and 0.8 <= pooled_null <= 1.2
            passes_anti = False  # V = 0: the sign clause cannot hold
        elif which == "R4":
            passes_null = all(abs(v - d) <= abs(r["e"]) + r["bar"] + 1e-12 for v, d, (_, r) in zip(v_null, dAs, subset))
            # the anti-null endpoint has V = 0, so |V - dA| = |dA| > |e| on every R2 cell: it fails
            passes_anti = all(abs(0 - d) <= abs(r["e"]) + r["bar"] for d, (_, r) in zip(dAs, subset))
        else:
            passes_null = sign_null and 0.8 <= ratio_null <= 1.2
            passes_anti = False
        return {
            "cells": len(subset),
            "signHoldsOnNull": sign_null,
            "medianRatioNull": ratio_null,
            "pooledRatioNull": pooled_null,
            "perfectEndpointPasses": passes_null,
            "unmovedEndpointPasses": passes_anti,
        }

    for name in READINGS:
        for tier in TIERS:
            measured = len(population(tier, name))
            say(f"### {name}, tier {tier} ({measured} cells where Apple's change exceeds its bar)")
            for which in ("R0", "R1", "R2", "R3", "R4"):
                res = restated(tier, name, which)
                record["restated"][f"{name}/{tier}/{which}"] = res
                if res["cells"] == 0:
                    say(f"  {which}: no cells")
                    continue
                say(
                    f"  {which}: cells {res['cells']:>4} ({res['cells'] / measured:.0%})  sign on null {res['signHoldsOnNull']}  "
                    f"median ratio {res['medianRatioNull']:.3f}  pooled {res['pooledRatioNull']:.3f}  "
                    f"perfect endpoint passes {res['perfectEndpointPasses']}  unmoved endpoint passes {res['unmovedEndpointPasses']}"
                )
            say("")
    say("## The charter's example, literally: cells where the shipped 0.5 render is within the bar of Apple")
    say("")
    for name in READINGS:
        for tier in TIERS:
            pop = population(tier, name)
            within = sum(1 for _, r in pop if abs(r["e"]) <= r["bar"])
            say(f"  {name:<12} {tier:<6} {within} of {len(pop)} cells: |e| <= the two-sided bar (of order 1e-9 to 1e-5)")
    say("  The bar is the run-to-run spread, so this population is empty or nearly so; R1 is its workable")
    say("  relative form and R2 the one that keeps half the cells.")
    say("")
    say("## R2 per profile (the recommended restatement), perfect-endpoint null")
    say("")
    for name in READINGS:
        for tier in TIERS:
            for profile in PROFILES:
                short = profile.replace("apple-macos-27.0-", "").replace("-standard-glass0.25", "")
                subset = [(c, r) for c, r in population(tier, name, profile) if abs(r["dA"]) > abs(r["e"])]
                if not subset:
                    say(f"  {name:<12} {tier:<6} {short:<9} no cells")
                    continue
                ratios = [r["nullRatio"] for _, r in subset]
                say(f"  {name:<12} {tier:<6} {short:<9} cells {len(subset):>3} of {len(population(tier, name, profile)):>3}  "
                    f"median ratio {median(ratios):.3f}  perfect endpoint passes {0.8 <= median(ratios) <= 1.2}")
    say("")

    r2 = []
    for c in cells:
        for name in READINGS:
            r = c["readings"][name]
            if r.get("status") == "measured" and r["appleMoved"] and abs(r["dA"]) > abs(r["e"]):
                r2.append({"reading": name, "tier": c["tier"], "profileKey": c["profileKey"], "sceneId": c["sceneId"],
                           "fixtureSet": c["fixtureSet"], "dA": r["dA"], "e": r["e"], "bar": r["bar"]})
    (HERE / "r2-population.json").write_text(json.dumps({
        "rule": "R2: the non-holdout standard 0.25 cells where Apple's change dA exceeds its two-sided bar "
                "and |dA| > |e|, e = vitrea@0.5 - Apple@0.5 from the current generation (frozen by X41), "
                "per reading and tier; computable before any vitrea render at 0.25 and fixed by it",
        "cells": r2,
    }, indent=1) + "\n")
    (HERE / "s1-null.txt").write_text("\n".join(out) + "\n")
    (HERE / "s1-null.json").write_text(json.dumps(record, indent=1) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
