#!/usr/bin/env python3
"""W30 G0 (b) — the shadow cut: Apple's macOS 27 falloff σ per span, read off
committed evidence and nothing else.

    python3 shadow-cut.py > shadow-cut.txt

**The source, and the arithmetic.** `results/2026-09-19-w29-g3b-shadow-recede/
native-delta.json` carries, per pair row, `readings.shadowFalloffSigmaPx` as a
two-element [26.5, 27] pair in DEVICE px. Claims §5.154 §4's correction states
the recipe exactly: take element [1] — the macOS 27 reading — and divide by the
row's own `scale`. That is the only transformation applied here. Nothing is
recomputed from a capture and no capture is taken (X2, X5).

**The casting span** is the declared component's SHORTER side, read from
`apps/reference-apple/scenes.json` rather than tabulated here — the same
quantity `sizeThickness` and `outer_shadow_thick` take, and the same one the
spans 32/44/96/128/130/160 of §5.154 §4's table are. A stack's span is its
BASE's shorter side and a group's is its members' (they are equal here); §4 of
the output says what that means for the instrument.

**The statistic** is the upper middle order statistic — `sorted[n // 2]` — which
is `law-tables.txt`'s own convention and therefore what §5.154 §4's medians are.
It is reported with the per-cell minimum and maximum and the count, because a
ratio acceptance against a median whose cells disagree by 9x is unfalsifiable
and the charter's Grounding says so.

**Non-converged fits are excluded by a stated rule, not by name.**
`metrics/shadow.ts` fits the blurred-edge model over ring means with the edge
pinned to the declared contour and the scale searched to twice the profile's own
reach; over a coarse backdrop the ring means oscillate with the backdrop's own
pitch and the search runs away into the interior of that interval. The rule is
`sigma_css > span`: a shadow whose fitted blur is wider than the surface casting
it has no edge left in the window, and the quantity is then a reading of the
backdrop rather than of the material. It is applied before any statistic and
every excluded cell is named in §0 of the output, so the rule can be checked
against what it removed.
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent

DELTA = PACKAGE / "results/2026-09-19-w29-g3b-shadow-recede/native-delta.json"
SCENES = ROOT / "apps/reference-apple/scenes.json"
MATRIX = PACKAGE / "results/matrix.json"

SPANS = [32, 44, 96, 128, 130, 160]

# The backdrop classes the charter asks the σ to be cut by, with the
# checkerboard's own pitch in CSS px where it has one. `checkerboard` is the
# 16 px bed pitch; `checkerboard-lc16` is the same pitch at low contrast.
BACKDROP_CLASS = {
    "checkerboard-4": ("checker", "4 px"),
    "checkerboard-8": ("checker", "8 px"),
    "checkerboard": ("checker", "16 px"),
    "checkerboard-lc16": ("checker", "16 px lc"),
    "checkerboard-32": ("checker", "32 px"),
    "checkerboard-64": ("checker", "64 px"),
    "photo": ("photo", "photo"),
    "light-solid": ("solid", "light"),
    "dark-solid": ("solid", "dark"),
    "mid-dark-solid": ("solid", "mid-dark"),
    "mid-chroma-solid": ("solid", "mid-chroma"),
    "hc-text-7": ("hc-text", "7 px"),
    "hc-text": ("hc-text", "14 px"),
    "hc-text-28": ("hc-text", "28 px"),
    "impulse": ("impulse", "impulse"),
}


def spans_of(components: dict) -> dict[str, int]:
    out = {}
    for name, spec in components.items():
        kind = spec["kind"]
        if kind in ("capsule", "rrect"):
            out[name] = min(spec["size"])
        elif kind == "stack":
            out[name] = min(spec["base"]["size"])
        elif kind == "group":
            out[name] = min(min(item["size"]) for item in spec["items"])
    return out


def bed_of(profile_key: str) -> str:
    """`<scale> <scheme/a11y>` — the bed label §5.154 §4's table uses."""
    rest = profile_key.removeprefix("apple-macos-27.0-").removesuffix("-glass0.5")
    scale, _, tail = rest.partition("-")
    return f"{scale} {tail.replace('-standard', '')}"


def median(values: list[float]) -> float:
    """The upper middle order statistic — `law-tables.txt`'s convention."""
    return sorted(values)[len(values) // 2]


def cell(values: list[float], width: int = 22) -> str:
    if not values:
        return f"{'—':>{width}}"
    return f"{median(values):>7.2f} [{min(values):5.2f}–{max(values):6.2f}] ({len(values):>2})".rjust(width)


def main() -> int:
    scenes = json.loads(SCENES.read_text())
    span_of = spans_of(scenes["components"])
    delta = json.loads(DELTA.read_text())

    rows = []
    excluded = []
    for row in delta["rows"]:
        pair = (row.get("readings") or {}).get("shadowFalloffSigmaPx")
        if pair is None or row["pose"] != "active":
            continue
        span = span_of.get(row["component"])
        if span is None:
            continue
        sigma = pair[1] / row["scale"]
        amplitude = ((row.get("readings") or {}).get("shadowFalloffAmplitude") or [None, None])[1]
        record = {
            "amplitude27": amplitude,
            "bed": bed_of(row["profileKey27"]),
            "profile": row["profileKey27"],
            "scene": row["sceneId"],
            "set": row["fixtureSet"],
            "gated": row["fixtureSet"] != "probe",
            "backdrop": row["background"],
            "component": row["component"],
            "span": span,
            "scale": row["scale"],
            "sigmaCss": sigma,
            "sigma265Css": pair[0] / row["scale"],
        }
        (excluded if sigma > span else rows).append(record)

    print("W30 G0 (b) — the shadow cut: macOS 27's falloff σ per span, per scale, per scheme")
    print("=" * 108)
    print()
    print("Source: results/2026-09-19-w29-g3b-shadow-recede/native-delta.json,")
    print("        readings.shadowFalloffSigmaPx[1] / row scale — claims §5.154 §4's correction.")
    print("Spans:  the declared component's shorter side, from apps/reference-apple/scenes.json.")
    print("        " + "  ".join(f"{k}={v}" for k, v in sorted(span_of.items(), key=lambda kv: kv[1])))
    print("Cells:  ACTIVE pose only. Every figure is `median [min–max] (n)`, median = sorted[n//2],")
    print("        the upper middle order statistic law-tables.txt uses and §5.154 §4's medians are.")
    print()

    print("§0. The non-converged fits, excluded by the rule σ_css > span")
    print("-" * 108)
    print(f"  {len(rows)} cells kept, {len(excluded)} excluded of {len(rows) + len(excluded)} active")
    print("  cells that resolve a σ at all. Every exclusion, named:")
    for record in sorted(excluded, key=lambda r: -r["sigmaCss"]):
        print(f"    σ {record['sigmaCss']:8.2f} CSS px at span {record['span']:3}  "
              f"{record['bed']:<36} {record['scene']:<50} {record['set']}")
    print()
    print("  These are §5.154 §4's own two populations — the 74.3 readings are the four")
    print("  `checkerboard-64__capsule-button` cells (a 64 px pitch under a 44 px caster: the")
    print("  ring means oscillate with the backdrop and the search leaves the material), and")
    print("  157.7 is `hc-text__rrect-sm__rest` on 1x light. Both are probe rows; no gated cell")
    print("  is excluded by the rule at any span, which is worth stating because it means the")
    print("  rule costs the acceptance nothing.")
    print()

    beds = sorted({r["bed"] for r in rows}, key=lambda b: (b.split()[1], b.split()[0]))

    for title, keep in (
        ("§1. The gated sets (calibration + validation + holdout + recorded)", lambda r: r["gated"]),
        ("§2. The probe ladder", lambda r: not r["gated"]),
        ("§3. Both, pooled — the bed as §5.154 §4 read it", lambda r: True),
    ):
        print(title)
        print("-" * 108)
        header = f"  {'bed':<36}" + "".join(f"{s:>22}" for s in SPANS)
        print(header)
        for bed in beds:
            line = f"  {bed:<36}"
            for span in SPANS:
                values = [r["sigmaCss"] for r in rows
                          if r["bed"] == bed and r["span"] == span and keep(r)]
                line += cell(values)
            print(line)
        print()

    print("§4. Per backdrop class, pooled over the gated sets and the probe ladder together")
    print("-" * 108)
    classes = []
    for _, (family, label) in BACKDROP_CLASS.items():
        if (family, label) not in classes:
            classes.append((family, label))
    for bed in beds:
        print(f"  {bed}")
        print(f"    {'backdrop':<16}" + "".join(f"{s:>22}" for s in SPANS))
        for family, label in classes:
            names = [n for n, v in BACKDROP_CLASS.items() if v == (family, label)]
            line = f"    {family + ' ' + label:<16}"
            any_value = False
            for span in SPANS:
                values = [r["sigmaCss"] for r in rows
                          if r["bed"] == bed and r["span"] == span and r["backdrop"] in names]
                any_value = any_value or bool(values)
                line += cell(values)
            if any_value:
                print(line)
        print()

    print("§4b. The instrument on a mixed-span composite")
    print("-" * 108)
    print("  `metrics/shadow.ts` returns ONE (amplitude, σ) pair per cell, fitted over ring")
    print("  means of the whole exterior with the shadow's edge pinned to the DECLARED")
    print("  contour — the union of the component's placed shapes. The charter asks what that")
    print("  means where the component has more than one span. The bed carries two such")
    print("  components and they turn out to be different cases, neither of them a mixture:")
    print()
    composite = {"toolbar-group": [], "glass-over-glass": []}
    for row in delta["rows"]:
        if row["pose"] != "active" or row["component"] not in composite:
            continue
        pair = (row.get("readings") or {}).get("shadowFalloffSigmaPx")
        composite[row["component"]].append((bed_of(row["profileKey27"]), row["sceneId"],
                                            None if pair is None else pair[1] / row["scale"],
                                            row["fixtureSet"]))
    for name, entries in composite.items():
        resolved = [e for e in entries if e[2] is not None]
        print(f"  {name}: {len(entries)} active rows, {len(resolved)} resolve a σ")
        for bed, scene, sigma, fset in sorted(entries):
            shown = "—  (no width; neither family converged)" if sigma is None else f"{sigma:.3f}"
            print(f"    {bed:<36}{scene:<40}{shown:<40}{fset}")
        print()
    print("  `toolbar-group` is three 44x44 capsules at 12 px spacing, so its members do not")
    print("  differ in span at all — and the instrument returns NO width on any of its seven")
    print("  rows, on either bed, in either family. The silhouette is fenestrated: the 12 px")
    print("  gaps are exterior to the declared region and interior to the shadow field, so the")
    print("  near rings average pixels occluded by two neighbours with pixels occluded by one,")
    print("  and the monotone profile the blurred-edge model needs does not exist. The cell")
    print("  still carries a departure and a strength peak. **The σ law is not read on it.**")
    print()
    print("  `glass-over-glass` is a 220x130 base with a 120x56 overlay at offset (0, −8).")
    print("  Half-extents put the overlay inside x ±60 of ±110 and y −36…+20 of ±65, so it is")
    print("  WHOLLY INTERIOR to the base and never reaches the measured exterior. The reading")
    print("  is the base's alone and it is a clean span-130 reading, not a compromise between")
    print("  130 and 56 — which is why its six cells sit within 13.25…13.74 of the rrect-ml")
    print("  span-128 column rather than between the span-56 and span-130 values. **The σ law")
    print("  IS read on it, at span 130 — and every one of those six cells is holdout.**")
    print()

    print("§5. The thin-regime hypothesis, on every cell pair that carries it")
    print("-" * 108)
    print("  §5.154 §4 states it as: below span 96 the σ is 'nearly constant in DEVICE px',")
    print("  read off 1.84 at 1x light against 3.92 at 2x light at span 44, 'a ratio of 2.13 —")
    print("  the device pixel ratio'. The two halves of that sentence are different")
    print("  hypotheses and the bed can separate them, so both are printed:")
    print()
    print("    H_css  σ is scale-invariant in CSS px      → σ_css(2x) / σ_css(1x) = 1.00")
    print("    H_dev  σ is scale-invariant in DEVICE px   → σ_css(2x) / σ_css(1x) = 0.50")
    print()
    print("  A pair is one scene id present on BOTH the 1x and the 2x bed of one scheme.")
    print()
    for scheme in ("light", "dark"):
        one = {(r["scene"]): r for r in rows if r["bed"] == f"1x {scheme}"}
        two = {(r["scene"]): r for r in rows if r["bed"] == f"2x {scheme}"}
        shared = sorted(set(one) & set(two), key=lambda s: (one[s]["span"], s))
        print(f"  {scheme} — {len(shared)} cell pairs")
        print(f"    {'span':>5} {'scene':<48}{'σ 1x':>9}{'σ 2x':>9}{'ratio':>8}"
              f"{'σdev 1x':>9}{'σdev 2x':>9}{'set':>13}")
        for scene in shared:
            a, b = one[scene], two[scene]
            print(f"    {a['span']:>5} {scene:<48}{a['sigmaCss']:>9.2f}{b['sigmaCss']:>9.2f}"
                  f"{b['sigmaCss'] / a['sigmaCss']:>8.2f}"
                  f"{a['sigmaCss']:>9.2f}{b['sigmaCss'] * 2:>9.2f}"
                  f"{('' if a['set'] == b['set'] else a['set'] + '/') + b['set']:>13}")
        for band, lo, hi in (("thin (spans 32–44)", 0, 95), ("thick (spans 96–160)", 96, 999)):
            ratios = [two[s]["sigmaCss"] / one[s]["sigmaCss"]
                      for s in shared if lo <= one[s]["span"] <= hi]
            if ratios:
                print(f"    {band:<24} n={len(ratios):<3} ratio median {median(ratios):.3f}  "
                      f"min {min(ratios):.3f}  max {max(ratios):.3f}  "
                      f"mean {statistics.fmean(ratios):.3f}")
        print()

    print("§5b. The fit's own valley: the amplitude beside the σ")
    print("-" * 108)
    print("  `metrics/shadow.ts` fits (amplitude, σ) jointly with the edge pinned to the declared")
    print("  contour, and its own header says the two trade along a valley. The product")
    print("  amplitude × σ is the profile's first moment — the energy the tail carries — and it")
    print("  is what survives the trade. If the product is scale-invariant where the two factors")
    print("  are not, the thin regime's σ is a position on the valley rather than a width.")
    print()
    print(f"  {'bed':<16}" + "".join(f"{('span ' + str(s)):>26}" for s in SPANS))
    print(f"  {'':<16}" + "".join(f"{'a':>8}{'σ':>8}{'a·σ':>10}" for _ in SPANS))
    for bed in beds:
        line = f"  {bed:<16}"
        for span in SPANS:
            picked = [r for r in rows
                      if r["bed"] == bed and r["span"] == span and r["amplitude27"] is not None]
            if not picked:
                line += f"{'—':>26}"
                continue
            a = median([r["amplitude27"] for r in picked])
            s = median([r["sigmaCss"] for r in picked])
            line += f"{a:>8.4f}{s:>8.2f}{a * s:>10.3f}"
        print(line)
    print()
    print("  The plain against the TINTED cell, at one span and one scene, on the light bed —")
    print("  the same geometry, the same backdrop, an author tint the material's blur cannot")
    print("  depend on:")
    print()
    print(f"    {'scene':<48}{'bed':<10}{'a':>9}{'σ':>8}{'a·σ':>9}")
    for scene in ("checkerboard__capsule-button__rest",
                  "checkerboard__capsule-button__rest-tint-orange",
                  "light-solid__capsule-button__rest",
                  "light-solid__capsule-button__rest-tint-orange",
                  "checkerboard__rrect-md__rest",
                  "checkerboard__rrect-md__rest-tint-orange"):
        for bed in ("1x light", "2x light"):
            picked = [r for r in rows if r["bed"] == bed and r["scene"] == scene]
            if not picked or picked[0]["amplitude27"] is None:
                continue
            r = picked[0]
            print(f"    {scene:<48}{bed:<10}{r['amplitude27']:>9.4f}{r['sigmaCss']:>8.2f}"
                  f"{r['amplitude27'] * r['sigmaCss']:>9.3f}")
    print()

    print("§6. The thick regime's line, checked on this bed")
    print("-" * 108)
    print("  §5.154 §4 as corrected: σ_css ≈ 0.133 · (span − 30) over spans 96–160.")
    print()
    print(f"  {'bed':<36}" + "".join(f"{s:>12}" for s in (96, 128, 130, 160))
          + f"{'slope':>10}{'zero at':>10}{'max resid':>11}")
    for bed in beds:
        line = f"  {bed:<36}"
        xs, ys = [], []
        for span in (96, 128, 130, 160):
            values = [r["sigmaCss"] for r in rows if r["bed"] == bed and r["span"] == span]
            line += f"{median(values):>12.2f}" if values else f"{'—':>12}"
            if values:
                xs.append(span)
                ys.append(median(values))
        if len(xs) >= 2:
            n = len(xs)
            mx, my = statistics.fmean(xs), statistics.fmean(ys)
            sxx = sum((x - mx) ** 2 for x in xs)
            slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
            intercept = my - slope * mx
            resid = max(abs(y - (slope * x + intercept)) for x, y in zip(xs, ys))
            line += f"{slope:>10.4f}{-intercept / slope:>10.1f}{resid:>11.3f}"
        print(line)
    print()

    print("§7. What 0.19.0 draws, against what the reference shows")
    print("-" * 108)
    print("  The shipped `sigmaPx` is 11.0 CSS px in both macOS 27 standard documents, one")
    print("  uniform for every span. The ratio below is 11.0 / (the bed's median native σ).")
    print()
    print(f"  {'bed':<36}" + "".join(f"{s:>12}" for s in SPANS))
    for bed in beds:
        line = f"  {bed:<36}"
        for span in SPANS:
            values = [r["sigmaCss"] for r in rows if r["bed"] == bed and r["span"] == span]
            line += f"{11.0 / median(values):>11.2f}x" if values else f"{'—':>12}"
        print(line)
    print()

    print("§8. The roster: which cells a σ acceptance can be fitted on, and which are checks")
    print("-" * 108)
    print("  X4 and the charter's clause 3: the σ law is fitted on NON-HOLDOUT cells and the")
    print("  holdout cells' native σ is reported beside it as a check, never fitted to.")
    print("  Non-holdout here means calibration + validation + recorded + probe; the ladder is")
    print("  entirely probe and probe is gated by nothing, which is what makes it fittable.")
    print()
    print(f"  {'bed':<36}" + "".join(f"{('span ' + str(s)):>18}" for s in SPANS))
    print(f"  {'':<36}" + "".join(f"{'fit':>8}{'check':>10}" for _ in SPANS))
    for bed in beds:
        line = f"  {bed:<36}"
        for span in SPANS:
            picked = [r for r in rows if r["bed"] == bed and r["span"] == span]
            fit = [r for r in picked if r["set"] != "holdout"]
            check = [r for r in picked if r["set"] == "holdout"]
            line += f"{len(fit):>8}{len(check):>10}"
        print(line)
    print()
    print("  The holdout cells the σ law will be CHECKED against, named — every one of them:")
    for r in sorted((r for r in rows if r["set"] == "holdout"),
                    key=lambda r: (r["span"], r["bed"], r["scene"])):
        print(f"    span {r['span']:>3}  {r['bed']:<36}{r['scene']:<48}σ {r['sigmaCss']:6.2f}")
    print()

    out = {
        "source": "results/2026-09-19-w29-g3b-shadow-recede/native-delta.json",
        "statistic": "upper middle order statistic of sigma_css = shadowFalloffSigmaPx[1] / scale",
        "exclusionRule": "sigma_css > span (the fit has no edge left in the window)",
        "excluded": excluded,
        "cells": rows,
    }
    (HERE / "shadow-cut.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
