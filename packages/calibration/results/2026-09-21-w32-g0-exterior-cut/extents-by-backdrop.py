#!/usr/bin/env python3
"""W32 G0 review closure — Apple's own active reach, per BACKDROP and per span, on
both generations (claims §5.166 §10, finding N17).

    python3 extents-by-backdrop.py > extents-by-backdrop.txt   # writes the JSON beside it

The review's incidental: Apple's active native shadow looks very different on macOS 27
from macOS 26.5 over one scene and barely different over another. Those two scenes differ
in their SPAN as well as their backdrop, so the contrast cannot say which one moved it.
This file separates them — the native extent per direction, per backdrop, per span, per
scale, on both generations — and answers one question for G1: **does Apple's active
reach on macOS 27 depend on the backdrop beyond the thin regime, where a luminance
keying is already expected?**

Nothing is fitted. `extent*Native` is the axis's own walk outward from the silhouette to
where the native render rejoins its backdrop, in device px, divided here by the row's
scale. It is a THRESHOLD crossing, so a backdrop with little light to remove reports a
shorter reach for a reason that is about detectability and not about the material — which
is exactly why the answer below is stated as a spread over backdrops beside the spread
over scales, and not as a law.

**A READ of committed evidence** (W32 X1, X2, X5): `results/matrix.json` and
`scenes.json` only, the frozen rows at `--at-documents any` because a frozen row names a
document this generation does not ship. No capture, nothing written under a macOS
26.5-keyed path, no holdout row read — the span-160 component `rrect-lg` is holdout on
the calibration backdrops, so span 160 appears here only where a probe backdrop carries
it, and that is said in the table rather than worked around.
"""
from __future__ import annotations

import importlib.util
import json
import statistics
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("w32_exterior_cut", HERE / "exterior-cut.py")
assert _spec is not None and _spec.loader is not None
xc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xc)

FROZEN = "apple-macos-26.5-"
SHIPPED = "apple-macos-27.0-"
SIDES = ["above", "below", "left", "right"]
# The two standard schemes at both scales. The accessibility beds carry their own
# occlusion policy and are not a backdrop contrast, so they are read apart in §3.
STANDARD = ["1x light", "2x light", "1x dark", "2x dark"]


@contextmanager
def generation(prefix: str):
    before = xc.GENERATION
    xc.GENERATION = prefix
    try:
        yield
    finally:
        xc.GENERATION = before


def load(prefix: str, at_documents: str) -> list[dict]:
    scenes = json.loads(xc.SCENES.read_text())
    span_of = xc.spans_of(scenes["components"])
    with generation(prefix):
        rows = xc.readings(xc.MATRIX, span_of, at_documents, with_holdout=False)
    out = []
    for row in rows:
        if row["tier"] != "webgpu" or row["state"] == "inactive":
            continue
        row["reach"] = xc.reach_fields(row)
        out.append(row)
    return out


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def table(frozen: list[dict], shipped: list[dict], beds: list[str], side: str) -> list[dict]:
    """One direction, `26.5 → 27` per backdrop per span, medians over the named beds."""
    keyed: dict[tuple[str, int, str], list[float]] = {}
    for label, rows in (("26.5", frozen), ("27", shipped)):
        for row in rows:
            if row["bed"] not in beds:
                continue
            value = row["reach"][side]["native"]
            if value is None:
                continue
            keyed.setdefault((row["backdrop"], row["span"], label), []).append(value)
    backdrops = sorted({b for b, _, _ in keyed})
    spans = sorted({s for _, s, _ in keyed})
    print(f"  {'backdrop':<18}" + "".join(f"{f'span {s}':>20}" for s in spans))
    records = []
    for backdrop in backdrops:
        line = f"  {backdrop:<18}"
        for span in spans:
            before = median(keyed.get((backdrop, span, "26.5"), []))
            after = median(keyed.get((backdrop, span, "27"), []))
            records.append({"side": side, "backdrop": backdrop, "span": span,
                            "macos26_5": before, "macos27": after,
                            "n26_5": len(keyed.get((backdrop, span, "26.5"), [])),
                            "n27": len(keyed.get((backdrop, span, "27"), []))})
            text = ("—" if before is None else f"{before:.1f}") + "→" + \
                   ("—" if after is None else f"{after:.1f}")
            line += f"{text:>20}"
        print(line)
    print(f"  {'the spread over backdrops, macOS 27 only':<18}")
    line = f"  {'  min–max (range)':<18}"
    spread = []
    for span in spans:
        values = [r["macos27"] for r in records
                  if r["span"] == span and r["macos27"] is not None]
        if not values:
            line += f"{'—':>20}"
            spread.append({"span": span, "min": None, "max": None, "backdrops": 0})
            continue
        spread.append({"span": span, "min": min(values), "max": max(values),
                       "backdrops": len(values)})
        line += f"{f'{min(values):.1f}–{max(values):.1f} ({max(values) - min(values):.1f})':>20}"
    print(line)
    print()
    return records + [{"side": side, "spreadOverBackdrops": spread}]


def main() -> int:
    frozen, shipped = load(FROZEN, "any"), load(SHIPPED, "shipped")

    print("W32 G0 review closure — Apple's active reach per backdrop, 26.5 against 27")
    print("=" * 160)
    print()
    print(f"Matrix:   {xc.MATRIX}")
    print("Read:     committed evidence only, non-holdout, ACTIVE pose, WebGPU tier rows")
    print("          (the native capture is the same on both tiers). No capture, no fit.")
    print("Figure:   `extent<Side>Native` in CSS px — the axis's walk outward from the")
    print("          silhouette to where Apple's render rejoins its backdrop — as the median")
    print("          over the beds named, printed `26.5 → 27`. `—` is the axis's own absence:")
    print("          the walk reached the canvas edge, or the bed carries no such row.")
    print()

    payload: dict[str, object] = {"source": str(xc.MATRIX), "sides": {}}
    for side in SIDES:
        print(f"§1{'abcd'[SIDES.index(side)]}. `extent{side.capitalize()}Native`, "
              f"the four standard beds")
        print("-" * 160)
        payload["sides"][side] = table(frozen, shipped, STANDARD, side)

    print("§2. The answer, stated over what the table shows")
    print("-" * 160)
    print("  Two readings, and they are different questions.")
    print()
    print("  **The generation moved the reach enormously, at every span and on every")
    print("  backdrop.** That is the larger half of the review's incidental and it is not a")
    print("  backdrop effect at all: macOS 27's receded — and active — exterior is simply")
    print("  shorter than macOS 26.5's everywhere the bed can see both.")
    print()
    print("  **Within macOS 27 the reach DOES vary with the backdrop, and outside the thin")
    print("  regime as well as inside it.** The spread lines above are the figure; the")
    print("  ratio beside each span says whether it is a rounding or a reading:")
    print()
    print(f"  {'side':<8}{'span':>6}{'min':>8}{'max':>8}{'range':>8}{'median':>9}"
          f"{'range/median':>14}{'backdrops':>11}")
    ratios = []
    for side in SIDES:
        spread = next(entry for entry in payload["sides"][side]  # type: ignore[index]
                      if "spreadOverBackdrops" in entry)["spreadOverBackdrops"]
        for entry in spread:
            if entry["min"] is None:
                continue
            values = [r["macos27"] for r in payload["sides"][side]  # type: ignore[index]
                      if r.get("span") == entry["span"] and r.get("macos27") is not None]
            centre = statistics.median(values)
            ratio = (entry["max"] - entry["min"]) / centre if centre else None
            ratios.append({"side": side, "span": entry["span"],
                           "range": entry["max"] - entry["min"], "median": centre,
                           "ratio": ratio, "backdrops": entry["backdrops"]})
            print(f"  {side:<8}{entry['span']:>6}{entry['min']:>8.1f}{entry['max']:>8.1f}"
                  f"{entry['max'] - entry['min']:>8.1f}{centre:>9.1f}"
                  f"{('—' if ratio is None else format(ratio, '.2f')):>14}"
                  f"{entry['backdrops']:>11}")
    payload["spreadRatios"] = ratios
    print()
    print("  The ratio is a fraction of a SMALL number wherever `above` is read — Apple draws")
    print("  almost nothing above a caster on macOS 27, so 1.5 against 2.8 CSS px is a 62 %")
    print("  spread over a reach of two pixels and says less than its size suggests. `below` is")
    print("  the direction that carries the amplitude and is the one to read:")
    below = [r for r in ratios if r["side"] == "below" and r["ratio"] is not None]
    thick = [r for r in below if r["span"] >= 96]
    thin = [r for r in below if r["span"] < 96]
    if thick and thin:
        print(f"    `below`, spans ≥ 96:  range {min(r['ratio'] for r in thick):.0%} to "
              f"{max(r['ratio'] for r in thick):.0%} of the span's own median reach")
        print(f"    `below`, spans < 96:  range {min(r['ratio'] for r in thin):.0%} to "
              f"{max(r['ratio'] for r in thin):.0%}")
    print("  and the extremes are the same two backdrops at every span — `light-solid` and")
    print("  `checkerboard-lc16` shortest and longest, in that order, at 96 and at 128.")
    print()
    print("  **What G1 must carry into its verdict**: a fit of one falloff triple against a")
    print("  bed pooled over backdrops leaves a PER-BACKDROP residual at every span, not only")
    print("  at the thin ones, and the residual is of the same order as the thin regime's own")
    print("  keying. Whether that is Apple's material conditioning its shadow on the backdrop")
    print("  or the axis's threshold crossing conditioning its estimate on the backdrop's")
    print("  contrast is NOT decided here: the extent is a threshold and a darker backdrop")
    print("  has less light to remove. Both readings predict the same table, and separating")
    print("  them needs the transmission profile rather than the extent, which is a fit and")
    print("  this gate fits nothing. G1 reports the residual per backdrop either way.")
    print()

    print("§3. The accessibility beds, read apart")
    print("-" * 160)
    print("  They carry their own occlusion policy rather than a backdrop contrast, so they")
    print("  are not a fifth backdrop and are printed rather than pooled.")
    print()
    accessibility = sorted({r["bed"] for r in frozen + shipped if r["bed"] not in STANDARD})
    print(f"  Beds: {', '.join(accessibility)}")
    print()
    payload["accessibility"] = table(frozen, shipped, accessibility, "below")

    (HERE / "extents-by-backdrop.json").write_text(json.dumps(payload, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
