#!/usr/bin/env python3
"""W32 G0 — the clearance against the reach, per span: which spans the exterior
is fittable on, and what the bed can and cannot see at each (claims §5.166; W32
acceptance clause 1).

    npx tsx reach.ts > reach.txt          # writes reach.json, which this reads
    python3 clearance.py > clearance.txt

Two numbers per span, from two different places, held up to each other.

  * The CLEARANCE is the bed's: the distance from the declared contour to the
    canvas edge on each side, in device px on every row of `matrix.json`
    (`ShadowFieldReport.clearance*`), divided by the row's scale. It is the
    window the instrument measures through.
  * The REACH is the material's: `outerShadowReachPx` at that caster's own
    occlusion, evaluated through the runtime's own functions by `reach.ts`
    beside this file, at the four shipped macOS 27 documents. It is the
    distance at which the composited shadow falls below the renderer's own
    visibility floor — the runtime's statement of where its shadow ends.

Where the reach is larger than the clearance the capture does not contain the
shadow, and the axis says so in its own words at `truncatedSides`: *"rings past
a truncated side's clearance are averaged over an incomplete annulus, which
pulls `falloffSigmaPx` toward the window. Measured on this bed at roughly 8% low
for a σ ≈ 17 px shadow read through a 20 px margin."* That figure is the axis's
and this file quotes it rather than re-deriving it; what this file adds is which
spans it applies to, from the bed's own clearances, and which bands survive.

`truncatedSides` is computed by the metric and NOT written to a row (W32 X7), so
the per-span verdict here is reconstructed from `clearance*` and the extents the
rows DO carry — an extent absent beside a clearance is the axis having withheld
a number it would have had to read off the frame.

Nothing is fitted, adopted or captured; every figure is a cut of committed
evidence and of the shipped documents (X2, X5).
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent

MATRIX = PACKAGE / "results/matrix.json"
SCENES = ROOT / "apps/reference-apple/scenes.json"
REACH = HERE / "reach.json"
CUT = HERE / "exterior-cut.json"

GENERATION = "apple-macos-27.0-"
BANDS = [("3-6", 6), ("6-12", 12), ("12-24", 24), ("24-48", 48)]
SIDES = ["above", "below", "left", "right"]

# The axis's own figure, quoted from `ShadowFieldReport.truncatedSides`.
AXIS_SIGMA_BIAS = "roughly 8 % low for a σ ≈ 17 px shadow read through a 20 px margin"


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


def main() -> int:
    scenes = json.loads(SCENES.read_text())
    span_of = spans_of(scenes["components"])
    reach = json.loads(REACH.read_text())
    cut = json.loads(CUT.read_text())
    rows = cut["rows"]

    light = reach["apple-macos-27.0-1x-light-standard-glass0.5"]
    dark = reach["apple-macos-27.0-1x-dark-standard-glass0.5"]

    print("W32 G0 — the clearance against the reach, per span")
    print("=" * 160)
    print()
    print(f"Canvas:     {scenes['canvas']['width']} x {scenes['canvas']['height']} CSS px "
          f"(`scenes.json`, unchanged — W32 X5)")
    print(f"Clearance:  from the rows of {MATRIX.relative_to(PACKAGE)}, device px / scale")
    print("Reach:      `outerShadowReachPx` at the shipped documents, via `reach.ts` beside this")
    print("            file — the runtime's own function, not a reproduction of its arithmetic")
    print(f"σ bias:     the axis's own, at `truncatedSides`: {AXIS_SIGMA_BIAS}")
    print()

    # ------------------------------------------------------------------
    print("§1. Clearance, reach and the admitted bands, per span")
    print("-" * 160)
    print("  `holds` is the clearance minus the reach on the tighter pair of sides: positive means")
    print("  the capture contains the whole exterior the runtime says it draws, negative means the")
    print("  shadow walks off the frame by that many CSS px on the side it is shortest on.")
    print()
    print(f"  {'span':>5}  {'component':<18}{'above/below':>13}{'left/right':>12}"
          f"{'reach light':>13}{'holds':>8}{'reach dark':>12}{'holds':>8}"
          f"{'admitted (all)':>24}   the bands the frame eats")
    seen = {}
    for row in rows:
        key = (row["span"], row["component"])
        if key not in seen:
            seen[key] = row
    for key in sorted(seen, key=lambda k: (k[0] or 0, k[1])):
        span, component = key
        row = seen[key]
        clearances = row["clearanceCss"]
        vertical, horizontal = clearances["above"], clearances["left"]
        admitted = row["admittedDir"]["all"]
        eaten = [label for label, outer in BANDS if label not in admitted]
        light_reach = light.get(str(span), {}).get("reach")
        dark_reach = dark.get(str(span), {}).get("reach")
        tight = min(clearances[side] for side in SIDES)
        line = (f"  {span:>5}  {component:<18}{f'{vertical:.2f}':>13}{f'{horizontal:.2f}':>12}")
        line += (f"{light_reach:>13.2f}{tight - light_reach:>8.2f}" if light_reach
                 else f"{'—':>13}{'—':>8}")
        line += (f"{dark_reach:>12.2f}{tight - dark_reach:>8.2f}" if dark_reach
                 else f"{'—':>12}{'—':>8}")
        line += f"{'/'.join(admitted) if admitted else '—':>24}   "
        line += ", ".join(eaten) if eaten else "none"
        print(line)
    print()
    print("  Every span the bed carries is read through a frame narrower than the reach the runtime")
    print("  itself declares. That is not new and it is not a defect of the capture: a shadow whose")
    print("  visibility floor is 13 CSS px out at span 32 is invisible long before the frame ends,")
    print("  and the σ bias the axis names applies where the SHADOW is still strong at the edge.")
    print("  What the admitted-band rule does is stop the TRANSMISSION statistic from summing a")
    print("  band the frame only left corners of, which is a separate matter from the σ fit and is")
    print("  enforceable per band where the σ bias can only be caveated per cell.")
    print()

    # ------------------------------------------------------------------
    print("§2. What the rows themselves say about the frame, per span")
    print("-" * 160)
    print("  An extent is absent where the walk reached the canvas edge. Counted on the ACTIVE,")
    print("  non-holdout, WebGPU rows — the population a clause is read on — and on all rows")
    print("  beside it, because the holdout carries most of span 160's gated cells.")
    print()
    print(f"  {'span':>5}  {'population':<26}{'n':>5}"
          + "".join(f"{('nat ' + s):>10}" for s in SIDES)
          + "".join(f"{('web ' + s):>10}" for s in SIDES)
          + f"{'web offY':>10}")
    for span in sorted({r["span"] for r in rows if r["span"] is not None}):
        for label, keep in (
            ("active non-holdout webgpu",
             lambda r: r["state"] != "inactive" and r["set"] != "holdout" and r["tier"] == "webgpu"),
            ("every row at this span", lambda r: True),
        ):
            here = [r for r in rows if r["span"] == span and keep(r)]
            if not here:
                continue
            line = f"  {span:>5}  {label:<26}{len(here):>5}"
            for side in SIDES:
                present = sum(1 for r in here if r["reach"][side]["native"] is not None)
                line += f"{f'{present}/{len(here)}':>10}"
            for side in SIDES:
                present = sum(1 for r in here if r["reach"][side]["web"] is not None)
                line += f"{f'{present}/{len(here)}':>10}"
            present = sum(1 for r in here if r["reach"]["offsetY"]["web"] is not None)
            line += f"{f'{present}/{len(here)}':>10}"
            print(line)
        print()

    # ------------------------------------------------------------------
    print("§3. `rrect-ml`'s declaration in `scenes.json`, read against the rows")
    print("-" * 160)
    declaration = scenes["components"]["rrect-ml"].get("$comment", "")
    print("  The declaration, verbatim:")
    for line in declaration.split(". "):
        if line.strip():
            print(f"    {line.strip().rstrip('.')}.")
    print()
    span_128 = [r for r in rows if r["span"] == 128]
    active_128 = [r for r in span_128 if r["state"] != "inactive" and r["set"] != "holdout"
                  and r["tier"] == "webgpu"]
    below_web = sum(1 for r in span_128 if r["reach"]["below"]["web"] is not None)
    below_native = sum(1 for r in span_128 if r["reach"]["below"]["native"] is not None)
    print(f"  Rows at span 128: {len(span_128)} in the generation, {len(active_128)} active")
    print(f"  non-holdout on the WebGPU tier. `extentBelowWeb` present on {below_web} of "
          f"{len(span_128)}, `extentBelowNative` on {below_native}.")
    print(f"  Clearance above/below {seen[(128, 'rrect-ml')]['clearanceCss']['above']:.2f} CSS px, "
          f"left/right {seen[(128, 'rrect-ml')]['clearanceCss']['left']:.2f}, against a shipped "
          f"reach of {light['128']['reach']:.2f} (light) and {dark['128']['reach']:.2f} (dark).")
    print()
    print("§4. Span 160, the same reading")
    print("-" * 160)
    span_160 = [r for r in rows if r["span"] == 160]
    active_160 = [r for r in span_160 if r["state"] != "inactive" and r["set"] != "holdout"
                  and r["tier"] == "webgpu"]
    print(f"  Rows at span 160: {len(span_160)} in the generation, {len(active_160)} active")
    print("  non-holdout on the WebGPU tier. Extent presence, both sides, over all of them:")
    for side in SIDES:
        native = sum(1 for r in span_160 if r["reach"][side]["native"] is not None)
        web = sum(1 for r in span_160 if r["reach"][side]["web"] is not None)
        print(f"    {side:<8} native {native:>3}/{len(span_160)}   web {web:>3}/{len(span_160)}")
    for field in ("offsetX", "offsetY"):
        native = sum(1 for r in span_160 if r["reach"][field]["native"] is not None)
        web = sum(1 for r in span_160 if r["reach"][field]["web"] is not None)
        print(f"    {field:<8} native {native:>3}/{len(span_160)}   web {web:>3}/{len(span_160)}")
    print()
    print("  The sample counts the outer bands survive on, direction `all`, native side — the")
    print("  corners of the capture at span 160 against a whole annulus at 128 and 96. Read from")
    print(f"  {MATRIX.relative_to(PACKAGE)} directly, because a band's sample count is on the row")
    print("  and not in the cut. Median over the active, non-holdout, WebGPU rows at each span.")
    print()
    counts: dict[tuple[int, str], list[int]] = {}
    by_scale: dict[tuple[int, int, str], list[int]] = {}
    for cell in json.loads(MATRIX.read_text())["cells"]:
        if not cell["key"]["profileKey"].startswith(GENERATION):
            continue
        if cell["tier"] != "texture" or cell.get("fixtureSet") == "holdout":
            continue
        if cell.get("state") == "inactive":
            continue
        shadow = cell.get("shadow")
        if shadow is None:
            continue
        component = cell["key"]["sceneId"].split("__")[1]
        span = span_of.get(component)
        if span is None:
            continue
        for entry in shadow.get("affineNative", []):
            if entry["direction"] != "all":
                continue
            counts.setdefault((span, entry["ringLabel"]), []).append(entry["sampleCount"])
            scale = 2 if "-2x-" in cell["key"]["profileKey"] else 1
            by_scale.setdefault((span, scale, entry["ringLabel"]), []).append(
                entry["sampleCount"])
    import statistics
    print(f"    {'span':>5}" + "".join(f"{b:>12}" for b, _ in BANDS))
    for span in sorted({s for s, _ in counts}):
        line = f"    {span:>5}"
        for band, _ in BANDS:
            here = counts.get((span, band))
            line += f"{statistics.median(here):>12.0f}" if here else f"{'—':>12}"
        print(line)
    print()
    # A sample count is in DEVICE pixels, so the same band on the same scene carries
    # four times as many at 2x as at 1x, and a median over the pooled rows is the
    # median of two disjoint clusters — a number no capture has. The pooled table
    # above is left exactly as it was recorded and the split is printed beside it
    # (W32 G0 review closure, claims §5.166 §10, finding N6).
    print("    The same counts split by SCALE, which is what one capture carries:")
    print(f"    {'span':>5}{'scale':>6}" + "".join(f"{b:>12}" for b, _ in BANDS))
    for span in sorted({s for s, _, _ in by_scale}):
        for scale in (1, 2):
            if not any((span, scale, band) in by_scale for band, _ in BANDS):
                continue
            line = f"    {span:>5}{scale:>6}"
            for band, _ in BANDS:
                here = by_scale.get((span, scale, band))
                line += f"{statistics.median(here):>12.0f}" if here else f"{'—':>12}"
            print(line)
    print()

    # ------------------------------------------------------------------
    print("§5. The σ fit's own residual per span, native side — what the frame did to the fit")
    print("-" * 160)
    print("  `falloffSigmaResidualNative` is the blurred-edge model's own goodness of fit on")
    print("  Apple's render. Read as the median over the active, non-holdout, WebGPU rows at each")
    print("  span. A truncated profile is a SHORT profile, so a low residual at span 160 says the")
    print("  model described the part of the falloff the frame left, not that the frame left all")
    print("  of it — which is why the residual is printed beside the clearance and not instead of")
    print("  it.")
    print()
    import statistics
    residuals: dict[tuple[int, str], list[float]] = {}
    amplitudes: dict[int, list[float]] = {}
    for cell in json.loads(MATRIX.read_text())["cells"]:
        if not cell["key"]["profileKey"].startswith(GENERATION):
            continue
        if cell["tier"] != "texture" or cell.get("fixtureSet") == "holdout":
            continue
        if cell.get("state") == "inactive":
            continue
        shadow = cell.get("shadow")
        if shadow is None:
            continue
        span = span_of.get(cell["key"]["sceneId"].split("__")[1])
        if span is None:
            continue
        for field in ("falloffSigmaResidualNative", "falloffSigmaResidualWeb"):
            if field in shadow:
                residuals.setdefault((span, field), []).append(shadow[field]["value"])
        if "falloffAmplitudeNative" in shadow:
            amplitudes.setdefault(span, []).append(shadow["falloffAmplitudeNative"]["value"])
    print(f"    {'span':>5}{'residual native':>18}{'residual web':>16}{'amplitude native':>20}"
          f"{'clearance':>12}")
    for span in sorted(amplitudes):
        native = residuals.get((span, "falloffSigmaResidualNative"), [])
        web = residuals.get((span, "falloffSigmaResidualWeb"), [])
        clearance = min(seen[(span, c)]["clearanceCss"][s]
                        for (sp, c) in seen if sp == span for s in SIDES)
        print(f"    {span:>5}"
              f"{f'{statistics.median(native):.4f} (n{len(native)})':>18}"
              f"{f'{statistics.median(web):.4f} (n{len(web)})':>16}"
              f"{f'{statistics.median(amplitudes[span]):.4f}':>20}"
              f"{clearance:>12.2f}")
    print()

    # ------------------------------------------------------------------
    print("§6. `rrect-ml`'s declaration: UPHELD, narrowed, with its own two predictions measured")
    print("-" * 160)
    print("  The sentence at issue is *\"The shadow axis on this cell is marginal by construction")
    print("  and must not be used to fit a shadow constant.\"* It is upheld, and a")
    print("  `$comment-w32-g0` is written BESIDE it in `scenes.json` rather than over it — the")
    print("  existing text is committed evidence and this gate corrects nothing in it.")
    print()
    print("  What the rows CONFIRM. The cell is marginal, and the admitted-band rule says in what:")
    print("  the `24-48` band's outer edge is 48 CSS px against 35.5 of vertical clearance and")
    print("  47.5 of horizontal, so it is outside the frame in EVERY direction and carries 53 % of")
    print("  `T`'s weight. Dropping it moves the span-128 statistic from 0.00487–0.00532 to")
    print("  0.00738–0.00889 on the four standard beds — the cell was not reading what the number")
    print("  said it was. And span 128 is one component: a constant fitted on this cell ALONE is")
    print("  fitted on one geometry at one aspect ratio, which is the declaration's own point.")
    print()
    print("  What the rows FALSIFY, and it is the mechanism rather than the verdict. The")
    print("  declaration predicts *\"the truncation guard to withdraw the downward extent here")
    print("  (clearance 35.5 px against that reach)\"*. It did not: `extentBelowNative` is present")
    print("  on 42 of 42 span-128 rows in this generation and `extentBelowWeb` on 39 of 42, and")
    print("  the median native downward extent is 27.00 CSS px inside a 35.50 px clearance. The")
    print("  shipped reach the runtime declares is 32.89 CSS px on the light document and 34.60 on")
    print("  the dark, both INSIDE the clearance — by 2.61 and 0.90 px. The reference's own shadow")
    print("  ends about eight px before the frame does, so there was nothing for the guard to")
    print("  withdraw. The blurred-edge fit says the same: the native σ residual at span 128 is")
    print("  0.0043 against span 96's 0.0069, a fit 38 % TIGHTER than the span the declaration")
    print("  offers as the safe one.")
    print()
    print("  So the declaration is right for a reason it did not give. W32 fits spans 32, 44, 96")
    print("  and 128 JOINTLY (charter Design, \"Which spans fit and which are read\"), which is not")
    print("  what the sentence forbids: no shadow constant is fitted on `rrect-ml` alone, the")
    print("  `24-48` band is not admitted at that span, and the cell's contribution is one span of")
    print("  four in a joint objective. The sentence stands as written and this gate records what")
    print("  it now means.")
    print()
    print("§7. Span 160: what the bed can and cannot see")
    print("-" * 160)
    print("  The canvas is 320 x 200 and `rrect-lg` is 280 x 160, so every span-160 cell has 19.50")
    print("  CSS px of clearance on all four sides against a shipped reach of 42.93 (light) and")
    print("  45.69 (dark): the frame ends at 43 % of the way to where the runtime says its own")
    print("  shadow does. Two bands are outside it — `12-24` by 4.5 px and `24-48` by 28.5 — and")
    print("  the rows show what that leaves: the `24-48` band survives on a median of 3,878 pixels")
    print("  at span 160 against 39,518 at span 128, a tenth, and all of them in the capture's")
    print("  four corners. **Corrected beside, 2026-09-21** (review closure; claims §5.166 §10,")
    print("  finding N6): those two medians are taken over 1x and 2x rows pooled, and a sample")
    print("  count is in DEVICE pixels, so neither is a count any capture carries. Per scale the")
    print("  `24-48` band reads 1,548 at 1x and 6,208 at 2x at span 160, against 15,804 and")
    print("  63,232 at span 128 — §4's second table. The RATIO is a tenth on each scale, so")
    print("  \"a tenth\" stands. Every extent the axis would have reported is withheld on the active")
    print("  non-holdout WebGPU population — 0 of 28 on both sides, in all four directions, and")
    print("  both offsets with them — so at span 160 the bed can see neither side's reach at all.")
    print()
    print("  What it CAN see is the transmission at 3–12 CSS px, on a whole annulus, on both")
    print("  sides: `3-6` and `6-12` carry 6,374 and 13,194 pixels, more than either carries at")
    print("  span 96. (Corrected beside, as above: per scale they are 2,544 and 5,292 at 1x and")
    print("  10,204 and 21,096 at 2x, against 1,520 / 3,212 and 6,048 / 12,848 at span 96 — so")
    print("  \"more than either carries at span 96\" holds on each scale on its own.) That is the")
    print("  reading W32 admits at span 160 and it is a reading of the")
    print("  falloff's INNER twelve px, which is about 0.7 σ of a σ ≈ 17 px shadow. What it cannot")
    print("  see is the outer falloff, the reach, the displacement, or any σ that is not biased")
    print("  toward the window by the axis's own figure — roughly 8 % low. §5.162's span-160 `T`")
    print("  and B1's span-160 native σ of 17.317 are both read through that frame; nothing")
    print("  recorded is wrong and what was missing is this qualification beside it. The fix in")
    print("  kind is a larger canvas, which is a `scenes.json` decision and a native re-capture")
    print("  (W32 X5) — Deferred.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
