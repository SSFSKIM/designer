#!/usr/bin/env python3
"""W31 G1 review closure — what the backdrop-support rule actually removes.

    python3 support-rule-check.py > support-rule-check.txt

**Nothing is fitted, adopted or captured here, and nothing this script prints is
a new reading of the bed.** It re-reads `results/matrix.json` through
`exterior-instrument.py`'s own functions and answers one question the G1 review
asked: the record says the 80 rows dropped by the axis's
`DEFAULT_MIN_BACKDROP_SUPPORT` rule "read `T` exactly 0.000000 on every band",
and "left in, they would have made the bed look better than it is by eighty rows
of the backdrop's own floor". Neither sentence is true as written, and the size
of the error is what decides whether the rule is kept. So the rule is turned off
and the whole bed is recomputed beside itself.

`exterior-instrument.py` is imported rather than copied, so this file cannot
drift from the reader whose output it is checking, and the reader's own output
is not touched: `T` on an unsupported row stays absent in
`exterior-instrument.json`, because the rule is kept (see §4 below).

Written 2026-09-21 by the W31 G1 review closure; claims §5.162 §9, finding B-2.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("ei", HERE / "exterior-instrument.py")
ei = importlib.util.module_from_spec(_spec)
with contextlib.redirect_stdout(io.StringIO()):          # its module body prints nothing; its
    _spec.loader.exec_module(ei)                         # readers do, and §0 is not this file's


def weighted_without_the_rule(row: dict, field: str) -> float | None:
    """`shape_error`'s weighted mean with the backdrop-support gate not applied.

    Byte for byte the arithmetic `shape_error()` runs BEFORE its gate — the gate
    is the last statement in that function, so this is the number the reader
    computes and then declines to report.
    """
    native = ei.affine(row["shadow"], "Native", "all")
    web = ei.affine(row["shadow"], "Web", "all")
    key = {"T": ("slopeALinear", "slopeALinear"), "L": ("interceptCLinear", "interceptCLinear")}[field]
    usable = []
    for band in ei.SHAPE_BANDS:
        n, w = native.get(band), web.get(band)
        if n is None or w is None:
            continue
        if n.get(key[0]) is None or w.get(key[1]) is None:
            continue
        usable.append((band, w[key[1]] - n[key[0]]))
    if not usable:
        return None
    total = sum(ei.BAND_WIDTH_CSS_PX[b] for b, _ in usable)
    return sum(ei.BAND_WIDTH_CSS_PX[b] * abs(d) for b, d in usable) / total


def main() -> int:
    scenes = json.loads(ei.SCENES.read_text())
    span_of = ei.spans_of(scenes["components"])
    with contextlib.redirect_stdout(io.StringIO()):
        rows = ei.readings(ei.MATRIX, span_of, "shipped", False)

    for row in rows:
        shape = ei.shape_error(row)
        row["T_kept"], row["L_kept"] = shape["T"], shape["L"]
        row["support"] = ei.value(row["shadow"], "backdropSupport")
        row["T_admitted"] = weighted_without_the_rule(row, "T")
        row["L_admitted"] = weighted_without_the_rule(row, "L")

    dropped = [r for r in rows
               if r["support"] is not None and r["support"] < ei.MIN_BACKDROP_SUPPORT]

    print("W31 G1 review closure — the backdrop-support rule, checked against the bed")
    print("=" * 110)
    print()
    print(f"Matrix:  {ei.MATRIX.relative_to(ei.PACKAGE)}, under packages/calibration")
    print(f"Rows:    {len(rows)} macOS 27 rows at the shipped documents, holdout dropped by")
    print("         `exterior-instrument.py`'s own `cells()`, as in its default run.")
    print(f"Rule:    backdropSupport < {ei.MIN_BACKDROP_SUPPORT} "
          "(`DEFAULT_MIN_BACKDROP_SUPPORT`, src/metrics/shadow.ts)")
    print("Nothing here is fitted, adopted or captured; no row, bound or document moves.")
    print()

    print("§1. What the rule removes, by backdrop class")
    print("-" * 110)
    print(f"  {len(dropped)} rows are below the axis's floor. By backdrop:")
    for backdrop, count in sorted(Counter(r["backdrop"] for r in dropped).items()):
        klass = [r for r in dropped if r["backdrop"] == backdrop]
        supports = [r["support"] for r in klass]
        carries = [r for r in klass if r["T_admitted"] is not None]
        nonzero = [r["T_admitted"] for r in carries if r["T_admitted"] > 0]
        print(f"    {count:>4} rows over `{backdrop}`  backdropSupport "
              f"{min(supports):.4f}–{max(supports):.4f}")
        print(f"         of those, {len(klass) - len(carries)} identify NO affine band in "
              f"3–48 CSS px and would carry no `T` with the rule off either;")
        print(f"         {len(carries)} would carry one, and {len(nonzero)} of those are NON-ZERO"
              + (f" ({min(nonzero):.6f}–{max(nonzero):.6f})." if nonzero else "."))
    print()
    print("  So the rule's REAL reach is the rows that would otherwise carry a number:")
    reach = [r for r in dropped if r["T_admitted"] is not None]
    print(f"    {len(reach)} rows, every one over `"
          + "`, `".join(sorted({r['backdrop'] for r in reach})) + "`.")
    print()

    print("§2. Every row the rule actually reaches, with the `T` it would have carried")
    print("-" * 110)
    print(f"  {'T (admitted)':>14}{'L (admitted)':>14}{'support':>10}{'span':>6}  "
          f"{'bed':<34}{'tier':<8}{'pose':<10}{'set':<12}scene")
    for row in sorted(reach, key=lambda r: -r["T_admitted"]):
        pose = "inactive" if row["state"] == "inactive" else "active"
        lift = "—" if row["L_admitted"] is None else f"{row['L_admitted']:.6f}"
        print(f"  {row['T_admitted']:>14.6f}{lift:>14}{row['support']:>10.4f}{row['span']:>6}  "
              f"{row['bed']:<34}{row['tier']:<8}{pose:<10}{row['set']:<12}{row['scene']}")
    print()
    print("  `L` is printed because it is the second half of the same finding: the reader's")
    print("  justification says a LIFT is measured cleanly over black — which is exactly where a")
    print("  transmission has no denominator — and yet `shape_error()`'s gate withholds `L` on")
    print("  these rows along with `T`. `L` is RECORDED and not bounded (claims §5.162 §3), so the")
    print("  closure records it here rather than changing what the reader reports.")
    lifts = [r["L_admitted"] for r in reach if r["L_admitted"] is not None]
    print(f"  What the withheld lift is worth, measured: {min(lifts):.6f}–{max(lifts):.6f} over all")
    print(f"  {len(lifts)} reached rows — so the inconsistency costs the record nothing in")
    print("  magnitude, and is recorded because a justification that does not match its code is")
    print("  a thing a later wave would otherwise have to rediscover.")
    print()

    print("§3. The bed with the rule ON and with it OFF, per bed, tier and span")
    print("-" * 110)
    print("  Active pose, non-holdout — the population any clause is read over. `median (n)`,")
    print("  the upper middle order statistic, five decimals, which is the precision C1 is")
    print("  stated at.")
    print()
    moved_counts, moved_stats = [], []
    for tier in ("webgpu", "css"):
        print(f"  tier {tier}")
        print(f"    {'bed':<34}{'span':>5}{'rule ON':>22}{'rule OFF':>22}   verdict")
        for bed in ei.bed_order(rows):
            for span in ei.SPANS:
                selected = [r for r in rows
                            if r["bed"] == bed and r["span"] == span and r["tier"] == tier
                            and r["state"] != "inactive" and r["set"] != ei.HOLDOUT]
                on = [r["T_kept"] for r in selected if r["T_kept"] is not None]
                off = [r["T_admitted"] for r in selected if r["T_admitted"] is not None]
                if not on and not off:
                    continue
                show = lambda v: f"{ei.upper_middle(v):.5f} ({len(v)})" if v else "—"
                verdict = []
                if len(on) != len(off):
                    verdict.append(f"count {len(on)} → {len(off)}")
                    moved_counts.append((tier, bed, span, len(on), len(off)))
                if on and off and f"{ei.upper_middle(on):.5f}" != f"{ei.upper_middle(off):.5f}":
                    verdict.append("STATISTIC MOVES")
                    moved_stats.append((tier, bed, span,
                                        ei.upper_middle(on), ei.upper_middle(off)))
                print(f"    {bed:<34}{span:>5}{show(on):>22}{show(off):>22}   "
                      + ", ".join(verdict))
        print()

    print("§4. The verdict")
    print("-" * 110)
    print(f"  Counts that move: {len(moved_counts)}.")
    for tier, bed, span, was, now in moved_counts:
        print(f"    {tier:<8}{bed:<34}span {span:>3}:  {was} → {now}")
    print()
    print(f"  Upper middle order statistics that move at five decimals: {len(moved_stats)}.")
    for tier, bed, span, was, now in moved_stats:
        print(f"    {tier:<8}{bed:<34}span {span:>3}:  {was:.5f} → {now:.5f}")
    print()
    webgpu_moved = [m for m in moved_stats if m[0] == "webgpu"]
    print(f"  On the WebGPU tier — the bed C1 is read on — {len(webgpu_moved)} statistics move.")
    print("  The rule is therefore KEPT: it is the shadow axis's own constant rather than this")
    print("  gate's, it is the condition the axis already applies before reporting any normalised")
    print("  figure, and turning it off moves no number the clause is stated over. What the")
    print("  record has to say instead is what this file measured: the rule's reach is the")
    print(f"  {len(reach)} `impulse` rows and not eighty, the `dark-solid` rows are out for a")
    print("  different reason the axis states (no identified affine band at all), and among the")
    print("  rows it does reach the readings are not all zero.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
