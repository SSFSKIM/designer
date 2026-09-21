#!/usr/bin/env python3
"""W32 G1 — the verdict: every stop, before and after, on the same statistics.

    python3 verdict.py --before <dir> --after <dir> [--label-before ...] [--label-after ...]

Each directory holds a `stops.json`, a `c1-forms.json` and an `exterior-cut.json`
written by this gate's copies of G0's readers, so the two sides of every row are
the same function of two different beds and no number is transcribed between
them. The bounds are G0's and this file states none of its own.

**What a before and an after are, said once.** The BEFORE is the pre-fit bed —
the six profiles rendered on scratch at the SHIPPED documents, reproduced
against the committed rows cell by cell (`pre-fit/repro.txt`). The AFTER is the
canonical read at the SEALED documents, which is the bed the rows this merge
appends were measured on. They are two renders of the same bed at two materials,
which is what makes a difference between them attributable to the material.

A miss is printed as a miss. Nothing here is widened, re-fitted or excused.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

C1_BOUND = 0.0042          # Decision Log 1 (c), RULED: form (ii), per span
C1_SPANS = [96, 128, 160]
B3_BOUND = 0.00035
THIN_BAR = 0.002044
STANDARD_BEDS = ["1x light", "2x light", "1x dark", "2x dark"]


def load(directory: Path) -> dict:
    out = {}
    for name in ("stops", "c1-forms", "exterior-cut"):
        path = directory / f"{name}.json"
        out[name] = json.loads(path.read_text()) if path.exists() else None
    return out


def fmt(value, places=5, width=0):
    text = "—" if value is None else f"{value:.{places}f}"
    return text.rjust(width) if width else text


def arrow(before, after, places=5):
    if before is None or after is None:
        return f"{fmt(before, places)} → {fmt(after, places)}"
    return f"{fmt(before, places)} → {fmt(after, places)}  ({after - before:+.{places}f})"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--label-before", default="before (shipped documents)")
    parser.add_argument("--label-after", default="after (sealed documents)")
    args = parser.parse_args()

    before, after = load(Path(args.before)), load(Path(args.after))

    print("W32 G1 — the verdict (claims §5.168)")
    print("=" * 128)
    print(f"  before  {args.before}   {args.label_before}")
    print(f"  after   {args.after}   {args.label_after}")
    print()
    for side, payload in (("before", before), ("after", after)):
        docs = (payload["exterior-cut"] or {}).get("documents", [])
        print(f"  {side} documents:")
        for line in docs:
            print(f"    {line}")
    print()

    # ------------------------------------------------------------------ C1
    print("§1. C1 — Decision Log 1 (c) as RULED: form (ii), per-span `T` over the admitted bands,")
    print(f"    ≤ {C1_BOUND} at spans 96, 128 and 160. Form (i) beside it, as §5.162 left it.")
    print("-" * 128)
    print(f"  {'bed':<12}{'span':>5}   {'form (ii) before → after':<34}"
          f"{'verdict':<22}{'n':>4}  {'min–max after'}")
    fails = []
    for bed in STANDARD_BEDS:
        for span in C1_SPANS:
            key = f"{bed} span {span}"
            b = ((before["c1-forms"] or {}).get("forms", {}).get("ii", {})
                 .get("readings", {}).get(key) or {})
            a = ((after["c1-forms"] or {}).get("forms", {}).get("ii", {})
                 .get("readings", {}).get(key) or {})
            bv, av = b.get("value"), a.get("value")
            # `n`, `min` and `max` come from form (i)'s block, which carries them:
            # form (ii) IS form (i)'s value read against a per-span bound, over the
            # same cells, so the population figures are one block's (claims §5.166
            # §5). And the `bound` inside either block is `c1-forms.py` re-deriving
            # the CHARTER'S RULE on the generation in front of it — not C1's
            # adopted 0.0042, which is Decision Log 1 (c)'s and is the constant at
            # the head of this file.
            a = {**((after["c1-forms"] or {}).get("forms", {}).get("i", {})
                    .get("readings", {}).get(key) or {}), **a, "value": av}
            verdict = "—"
            if av is not None:
                verdict = "PASS" if av <= C1_BOUND else f"FAIL by {av / C1_BOUND - 1:+.0%}"
                if av > C1_BOUND:
                    fails.append((bed, span, av))
            span_range = (f"{a.get('min', float('nan')):.5f}–{a.get('max', float('nan')):.5f}"
                          if a else "—")
            print(f"  {bed:<12}{span:>5}   {arrow(bv, av):<34}{verdict:<22}"
                  f"{a.get('n', 0):>4}  {span_range}")
    print()
    print("  form (i), the one bound across the thick spans (≤ 0.0045), recorded beside:")
    for bed in STANDARD_BEDS:
        row = f"  {bed:<12}"
        for span in C1_SPANS:
            key = f"{bed} span {span}"
            b = ((before["c1-forms"] or {}).get("forms", {}).get("i", {})
                 .get("readings", {}).get(key) or {}).get("value")
            a = ((after["c1-forms"] or {}).get("forms", {}).get("i", {})
                 .get("readings", {}).get(key) or {}).get("value")
            row += f"  {span}: {fmt(b)} → {fmt(a)}"
        print(row)
    print()

    # ------------------------------------------------- candidate (i), the headline
    print("§2. Candidate (i) — the wave's headline number: the RENDERED σ against the NATIVE σ,")
    print("    declared with the bound 'inside B1's own ±5 % window of the native σ'.")
    print("-" * 128)
    print(f"  {'bed':<12}{'span':>5}   {'σ native':>10}{'σ web before':>14}{'σ web after':>13}"
          f"{'(i) before':>12}{'(i) after':>11}   {'window':<22}{'verdict'}")
    for bed in STANDARD_BEDS:
        for span in C1_SPANS:
            key = f"{bed} span {span}"
            b = (before["stops"] or {}).get("candidateI", {}).get(key) or {}
            a = (after["stops"] or {}).get("candidateI", {}).get(key) or {}
            window = a.get("window") or b.get("window") or [None, None]
            verdict = "—" if not a else ("INSIDE" if a.get("inside") else "OUTSIDE")
            print(f"  {bed:<12}{span:>5}   {fmt(a.get('nativeSigmaCss'), 3, 10)}"
                  f"{fmt(b.get('renderedSigmaCss'), 3, 14)}{fmt(a.get('renderedSigmaCss'), 3, 13)}"
                  f"{fmt(b.get('relativeError'), 3, 12)}{fmt(a.get('relativeError'), 3, 11)}   "
                  f"{('[' + fmt(window[0], 3) + ', ' + fmt(window[1], 3) + ']'):<22}{verdict}")
    print()

    # ------------------------------------------------------------------ B3
    print("§3. B3 — the departure residual over the WHOLE exterior, the stop's own population")
    print("-" * 128)
    for side, payload in ((args.label_before, before), (args.label_after, after)):
        stop = (payload["stops"] or {}).get("b3", {}).get("stop", {})
        wide = (payload["stops"] or {}).get("b3", {}).get("nonHoldoutIncludingProbe", {})
        value = stop.get("value")
        verdict = "—" if value is None else ("MET" if value <= B3_BOUND else "BROKEN")
        print(f"  {side:<34}{fmt(value, 5, 10)}  ≤ {B3_BOUND}  {verdict}   n={stop.get('n')}")
        print(f"  {'':<34}{'every non-holdout row, probe included:':<40}"
              f"mean {fmt(wide.get('mean'))}  max {fmt(wide.get('max'))}  "
              f"worst {wide.get('worst')}")
    print()
    print("  the window-restricted departure beside it, which is what the anchors were solved on:")
    print(f"  {'bed / span':<24}{'|Δ| whole before':>18}{'after':>12}"
          f"{'|Δ| window before':>20}{'after':>12}")
    keys = sorted(((before["stops"] or {}).get("b3", {}).get("windowDeparture") or {}).keys())
    for key in keys:
        b = (before["stops"] or {}).get("b3", {}).get("windowDeparture", {}).get(key) or {}
        a = (after["stops"] or {}).get("b3", {}).get("windowDeparture", {}).get(key) or {}
        print(f"  {key:<24}{fmt(b.get('wholeAbsDelta'), 5, 18)}{fmt(a.get('wholeAbsDelta'), 5, 12)}"
              f"{fmt(b.get('windowAbsDelta'), 5, 20)}{fmt(a.get('windowAbsDelta'), 5, 12)}")
    print()

    # ------------------------------------------------------------- the thin stop
    print("§4. The thin regime, per cell — no inner band's |Δa| worse than today's by more than")
    print(f"    the bar {THIN_BAR}; the order statistic per bed no worse than today's.")
    print("-" * 128)
    b_cells = (before["stops"] or {}).get("thinRegime", {}).get("perCell") or {}
    a_cells = (after["stops"] or {}).get("thinRegime", {}).get("perCell") or {}
    rows = []
    for key, a in a_cells.items():
        b = b_cells.get(key)
        if b is None:
            continue
        for band in ("3-6", "6-12"):
            bv, av = b.get(band), a.get(band)
            if bv is None or av is None:
                continue
            rows.append((abs(av) - abs(bv), abs(bv), abs(av), band, a.get("bed"), key))
    rows.sort(reverse=True)
    broken = [r for r in rows if r[0] > THIN_BAR]
    print(f"  {len(rows)} (cell, band) readings compared; {len(broken)} worse than the bar.")
    print(f"  {'Δ|Δa|':>11}{'before':>10}{'after':>10}  {'band':<7}{'bed':<12}cell")
    for delta, bv, av, band, bed, key in rows[:10]:
        print(f"  {delta:>+11.5f}{bv:>10.5f}{av:>10.5f}  {band:<7}{str(bed):<12}{key}")
    if broken:
        print("  BROKEN, every one:")
        for delta, bv, av, band, bed, key in broken:
            print(f"  {delta:>+11.5f}{bv:>10.5f}{av:>10.5f}  {band:<7}{str(bed):<12}{key}")
    print("  ... worst first; the whole table is in the two `stops.txt` §3 beside this file.")
    print()
    print("  the order statistic per bed, before → after (median and max of |Δa|, both bands):")
    b_bed = (before["stops"] or {}).get("thinRegime", {}).get("perBed") or {}
    a_bed = (after["stops"] or {}).get("thinRegime", {}).get("perBed") or {}
    worse = []
    for key in sorted(set(b_bed) | set(a_bed)):
        line = f"    {key:<44}"
        for band in ("3-6", "6-12"):
            b = (b_bed.get(key) or {}).get(band) or {}
            a = (a_bed.get(key) or {}).get(band) or {}
            line += (f"  {band} med {fmt(b.get('median'))} → {fmt(a.get('median'))}"
                     f"  max {fmt(b.get('max'))} → {fmt(a.get('max'))}")
            if (b.get("median") is not None and a.get("median") is not None
                    and a["median"] > b["median"]):
                worse.append(f"{key} {band}")
        print(line)
    print(f"  order statistics that got WORSE: {len(worse)}"
          + ("" if not worse else " — " + ", ".join(worse)))
    print()
    print("  the worst cell of the whole population, before and after:")
    for side, payload in ((args.label_before, before), (args.label_after, after)):
        worst = (payload["stops"] or {}).get("thinRegime", {}).get("worstCell")
        scenes = (payload["stops"] or {}).get("thinRegime", {}).get("worstCellScenes")
        print(f"    {side:<34}{worst}   {scenes}")
    print()

    # ----------------------------------------------------- M1 / M2 and the unmoved
    print("§5. The rows expected UNMOVED — a fit that moves one of these is a warning (X3)")
    print("-" * 128)
    print("  M1 and M2 as `stops.py` reads them, which is out of W31 G4's COMMITTED cut — one")
    print("  number that does not move with a round. `chroma-recheck.py` beside this file")
    print("  re-derives both from each matrix over the same population, which is the reading")
    print("  that has a before and an after; `adopted-thresholds.test.ts` is the authority.")
    for name, fields in (("m1", ("median", "min", "max", "outsideCell")),
                         ("m2", ("median", "max"))):
        print(f"  {name.upper()}:")
        for profile in sorted((after["stops"] or {}).get(name, {})):
            b = (before["stops"] or {}).get(name, {}).get(profile) or {}
            a = (after["stops"] or {}).get(name, {}).get(profile) or {}
            line = f"    {profile:<52}"
            for field in fields:
                line += f"  {field} {fmt(b.get(field))} → {fmt(a.get(field))}"
            print(line)
    print()
    print("  the structure, tint and rim readings, per bed — the values a shadow fit must leave:")
    moved = 0
    for bed in STANDARD_BEDS:
        b = (before["stops"] or {}).get("unmoved", {}).get(bed) or {}
        a = (after["stops"] or {}).get("unmoved", {}).get(bed) or {}
        for field in sorted(set(b) | set(a)):
            bv = (b.get(field) or {}).get("median")
            av = (a.get(field) or {}).get("median")
            if bv is None and av is None:
                continue
            delta = None if (bv is None or av is None) else av - bv
            flag = "" if (delta is not None and abs(delta) < 1e-9) else "   MOVED"
            if flag:
                moved += 1
            print(f"    {bed:<12}{field:<26}{fmt(bv)} → {fmt(av)}"
                  f"{'' if delta is None else f'  ({delta:+.5f})'}{flag}")
    print(f"  readings that moved: {moved}")
    print()

    # ------------------------------------------------------------------ the recede
    print("§6. The recede — Decision Log 2's stand-down, read on the inactive pose")
    print("-" * 128)
    b_rec = (before["stops"] or {}).get("recede") or {}
    a_rec = (after["stops"] or {}).get("recede") or {}
    for key in sorted(set(b_rec) | set(a_rec)):
        b, a = b_rec.get(key) or {}, a_rec.get(key) or {}
        if not isinstance(b, dict) or not isinstance(a, dict):
            continue
        fields = [f for f in sorted(set(b) | set(a))
                  if isinstance(b.get(f), (int, float)) or isinstance(a.get(f), (int, float))]
        if not fields:
            continue
        print(f"  {key}")
        for field in fields:
            print(f"      {field:<16}{fmt(b.get(field), 6)} → {fmt(a.get(field), 6)}")
    print()

    # ------------------------------------------------------------- the missed rows
    print("§7. `MISSED_27_ROWS` — the five + three, before and after; nothing is claimed")
    print("-" * 128)
    b_missed = (before["stops"] or {}).get("missedRows") or {}
    a_missed = (after["stops"] or {}).get("missedRows") or {}
    for key in sorted(set(b_missed) | set(a_missed)):
        b, a = b_missed.get(key), a_missed.get(key)
        if isinstance(b, dict) or isinstance(a, dict):
            b, a = b or {}, a or {}
            fields = [f for f in sorted(set(b) | set(a))
                      if isinstance(b.get(f), (int, float)) or isinstance(a.get(f), (int, float))]
            print(f"  {key}")
            for field in fields:
                print(f"      {field:<20}{fmt(b.get(field), 5)} → {fmt(a.get(field), 5)}")
        else:
            print(f"  {key:<60}{b} → {a}")
    print()

    print("§8. The verdict in one line")
    print("-" * 128)
    if fails:
        print(f"  C1 form (ii) FAILS on {len(fails)} of 12 bed × span rows:")
        for bed, span, value in fails:
            print(f"      {bed} span {span}: {value:.5f} against {C1_BOUND}")
    else:
        print(f"  C1 form (ii) PASSES on all 12 bed × span rows at ≤ {C1_BOUND}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
