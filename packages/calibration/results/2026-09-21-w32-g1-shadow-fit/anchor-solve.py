#!/usr/bin/env python3
"""W32 G1 — the fit's objective and the anchors, read off one round's cut.

    python3 anchor-solve.py <round>/exterior-cut.json [--constants <candidate.json>] \
        [--against <previous>/exterior-cut.json]

`results/2026-09-20-w30-g3-operators/anchor-solve.py` with its OBJECTIVE
changed, plus the two things W30 had no need of: the admitted-band fit objective
this wave's lengths are searched against, and the linearity check printed as a
number rather than described.

## What changed, exactly

**W30 solved the anchors on `meanDeparture{Native,Web}` — the mean of
`backdrop − rendered` over the WHOLE exterior of the declared region.** W32
clause 3 solves them on the departure restricted to the **admitted bands of
direction `all`**, 3–48 CSS px outside the declared contour, because the `0-3`
band holds the body's own over-fill: vitrea's GPU capsule spills 3.5–4 CSS px
past its declared contour against Apple's ≤ 1 (§5.62), and at span 160 that band
reads `Δa` +0.090 to +0.157 — an order of magnitude above the shadow bands and
of the opposite sign. An anchor solved through it is solved through the rim.

**How the window-restricted departure is computed, per regime.** It is not an
approximation of the whole-exterior figure and is not derived from it. Each
affine band entry on a row carries `sampleCount`, `backdropMeanLinear` and
`renderedLevelLinear` on BOTH sides over the SAME pixels — the bands are cut
from the scene's own distance field, so the two sides' counts agree — and the
per-cell window departure is the sample-count-weighted mean of
`backdropMeanLinear − renderedLevelLinear` over the admitted bands, per side.
A mean of means weighted by their counts is the mean of the union, so the
quantity is exact over the window's pixels rather than an estimate of it. That
is `exterior-cut.py`'s `window_departure`, which this file reads out of the cut
rather than recomputing (`row["departure"]["window"]`). The REGIME then groups
cells exactly as W30's `regime()` did — the occlusion law's own grouping, thin
below span 44 split by backdrop class and thick by span — and the regime's
departure is the MEAN over its cells, per side, as W30 took it. So the change of
objective is a change of the pixel set the mean is taken over and of nothing
else: same grouping, same closed form, same ratio.

    anchor_wanted = anchor_rendered · (departure_native / departure_web)

**Both solves are printed every round**, window and whole, because §5.166 §6
measures them as different objectives rather than a restriction of one another:
the restricted difference is larger on every bed at every span, by 1.69× to
50.66×, and on 1x light the two disagree in SIGN. B3 is stated over the whole
exterior and stays the stop; where the window solve would break B3 the anchors
that keep B3 ship and the window residual is recorded (charter clause 3).

**The inactive rows are a separate block and are never solved here.** W32
Decision Log 2 ruled the receded documents' amplitude to 0 as a declared
reading; the native window departure is exactly 0.000000 on every one of them,
so the ratio has a zero denominator and there is nothing to solve. The block
reports what vitrea still draws there, which is the reading the stand-down is
confirmed by.

## The fit objective

Per scheme, over that scheme's two STANDARD beds, WebGPU tier, active,
non-holdout, cells whose identified band set equals their span's admitted set:

    objective(scheme) = mean over spans {32, 44, 96, 128} of
                        upperMiddle({ T_all(cell) at that span })

— the upper middle order statistic per span (W30 G0's statistic, and C1's), then
**equal weight per span**, four spans. Span 160 is read and printed at every
round and is never in the objective, because a fit that prefers the triple that
fits inside a 19.5 px frame is a fit of the frame (charter, "Which spans fit and
which are read"). The two accessibility beds are read every round as a check and
are not in the objective: their six anchors are overwritten by the
reduced-transparency fold, so a fit driven by them would be fitting a material
this wave does not move (X3).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("w32_cut", HERE / "exterior-cut.py")
_cut = importlib.util.module_from_spec(_spec)
sys.modules["w32_cut"] = _cut
_spec.loader.exec_module(_cut)

DARK_BACKDROPS = {"impulse", "dark-solid"}
BRIGHT_BACKDROPS = {"light-solid"}

ANCHOR = {
    "thinDark": "thinOcclusionDark",
    "thinMid": "thinOcclusionMid",
    "thinBright": "thinOcclusionBright",
    "thick96": "thickOcclusionAt96",
    "thick128": "thickOcclusionAt128",
    "thick160": "thickOcclusionAt160",
}
ORDER = ["thinDark", "thinMid", "thinBright", "thick96", "thick128", "span130", "thick160"]

OBJECTIVE_SPANS = [32, 44, 96, 128]
READ_ONLY_SPANS = [160]
STANDARD_BEDS = {"light": ["1x light", "2x light"], "dark": ["1x dark", "2x dark"]}
BAR = 0.002044


def regime(span, backdrop: str):
    """W30 G3's `regime()`, verbatim — the occlusion law's own grouping."""
    if span is None:
        return None
    if span <= 44:
        if backdrop in DARK_BACKDROPS:
            return "thinDark"
        if backdrop in BRIGHT_BACKDROPS:
            return "thinBright"
        return "thinMid"
    if span <= 96:
        return "thick96"
    if span <= 128:
        return "thick128"
    if span < 160:
        return "span130"
    return "thick160"


def upper_middle(values):
    return sorted(values)[len(values) // 2] if values else None


def full_set(row) -> bool:
    return tuple(row["bandsUsed"]) == tuple(row["admitted"]) and row["T"] is not None


def fit_rows(rows, scheme):
    return [r for r in rows
            if r["tier"] == "webgpu" and r["state"] != "inactive" and r["set"] != "holdout"
            and r["bed"] in STANDARD_BEDS[scheme] and full_set(r)]


def objective(rows, scheme):
    """The number the lengths are searched against, and its parts."""
    per_span = {}
    for span in OBJECTIVE_SPANS:
        values = [r["T"] for r in fit_rows(rows, scheme) if r["span"] == span]
        per_span[span] = (upper_middle(values), len(values))
    usable = [v for v, _ in per_span.values() if v is not None]
    return (sum(usable) / len(usable) if usable else None), per_span


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cut", help="a round's exterior-cut.json")
    parser.add_argument("--constants", help="the candidate documents' constants, for anchor_wanted")
    parser.add_argument("--against", help="the previous round's exterior-cut.json, for the deltas")
    parser.add_argument("--label", default="")
    args = parser.parse_args()

    payload = json.loads(Path(args.cut).read_text())
    rows = payload["rows"]
    for row in rows:
        row["regime"] = regime(row["span"], row["backdrop"])
    constants = json.loads(Path(args.constants).read_text()) if args.constants else None
    previous = None
    if args.against:
        previous = json.loads(Path(args.against).read_text())
        for row in previous["rows"]:
            row["regime"] = regime(row["span"], row["backdrop"])

    label = args.label or Path(args.cut).parent.name
    print(f"W32 G1 — round `{label}`: the objective, the anchors and the linearity")
    print("=" * 120)
    print(f"  cut          {args.cut}")
    print(f"  documents    {', '.join(payload['documents'])}")
    print(f"  rows         {len(rows)} macOS 27 rows carry the shadow axis")
    print(f"  bar          {BAR} (the native-pair `shadowAffineSlopeDeltaMax` MAX over 432 cells)")
    print()

    # ---------------------------------------------------------------- objective
    print("§1. The fit objective — per span the upper middle `T`, equal weight per span")
    print("-" * 120)
    print(f"  {'scheme':<8}{'obj':>10}   " + "".join(f"{f'span {s}':>16}" for s in OBJECTIVE_SPANS)
          + f"{'span 160 (read)':>18}")
    objectives = {}
    for scheme in ("light", "dark"):
        value, per_span = objective(rows, scheme)
        objectives[scheme] = (value, per_span)
        read160 = [r["T"] for r in fit_rows(rows, scheme) if r["span"] == 160]
        cell160 = upper_middle(read160)
        line = f"  {scheme:<8}{('—' if value is None else f'{value:.5f}'):>10}   "
        for span in OBJECTIVE_SPANS:
            v, n = per_span[span]
            line += f"{('—' if v is None else f'{v:.5f}') + f' ({n})':>16}"
        line += f"{('—' if cell160 is None else f'{cell160:.5f}') + f' ({len(read160)})':>18}"
        print(line)
    if previous:
        print()
        print("  against the previous round:")
        for scheme in ("light", "dark"):
            now, now_spans = objectives[scheme]
            was, was_spans = objective(previous["rows"], scheme)
            delta = None if (now is None or was is None) else now - was
            print(f"    {scheme:<8}{('—' if was is None else f'{was:.5f}'):>10} → "
                  f"{('—' if now is None else f'{now:.5f}'):>9}   "
                  f"Δ {('—' if delta is None else f'{delta:+.5f}'):>10}   "
                  f"{'converged (|Δ| < bar)' if delta is not None and abs(delta) < BAR else ''}")
    print()

    # ---------------------------------------------------------------- per bed
    print("§2. `T` per bed per span — every bed the round carries, the objective's and the rest")
    print("-" * 120)
    beds = sorted({r["bed"] for r in rows})
    spans = sorted({r["span"] for r in rows if r["span"] is not None})
    print(f"  {'bed':<38}" + "".join(f"{f'{s}':>14}" for s in spans))
    for bed in beds:
        line = f"  {bed:<38}"
        for span in spans:
            values = [r["T"] for r in rows
                      if r["bed"] == bed and r["span"] == span and r["tier"] == "webgpu"
                      and r["state"] != "inactive" and r["set"] != "holdout" and full_set(r)]
            v = upper_middle(values)
            line += f"{('—' if v is None else f'{v:.5f}') + f'({len(values)})':>14}"
        print(line)
    print()

    # ---------------------------------------------------------------- anchors
    for scheme in ("light", "dark"):
        print(f"§3{'ab'[scheme == 'dark']}. The {scheme} document's anchors — the WINDOW solve "
              f"(3–48 CSS px) beside the WHOLE-exterior one")
        print("-" * 120)
        print(f"  {'regime':<12}{'n':>4}{'win N':>11}{'win W':>11}{'N/W':>9}"
              f"{'anchor now':>12}{'wanted (win)':>14}"
              f"{'whole N':>11}{'whole W':>11}{'N/W':>9}{'wanted (whole)':>16}")
        for name in ORDER:
            sel = [r for r in rows
                   if r["scheme"] == scheme and r["regime"] == name
                   and r["state"] != "inactive" and r["tier"] == "webgpu"
                   and r["set"] != "holdout" and r["bed"] in STANDARD_BEDS[scheme]]
            win = [r for r in sel if r["departure"]["window"]["native"] is not None]
            whole = [r for r in sel if r["departure"]["native"] is not None]
            if not win and not whole:
                continue
            leaf = ANCHOR.get(name)
            now = (constants or {}).get(scheme, {}).get(leaf) if leaf else None
            wn = sum(r["departure"]["window"]["native"] for r in win) / len(win) if win else None
            ww = sum(r["departure"]["window"]["web"] for r in win) / len(win) if win else None
            hn = sum(r["departure"]["native"] for r in whole) / len(whole) if whole else None
            hw = sum(r["departure"]["web"] for r in whole) / len(whole) if whole else None
            want_w = (now * wn / ww) if (now is not None and ww) else None
            want_h = (now * hn / hw) if (now is not None and hw) else None
            fmt = lambda v, p=5: "—" if v is None else f"{v:.{p}f}"
            print(f"  {name:<12}{len(sel):>4}{fmt(wn):>11}{fmt(ww):>11}"
                  f"{(fmt(wn / ww, 3) if ww else '—'):>9}"
                  f"{fmt(now, 4):>12}{fmt(want_w, 4):>14}"
                  f"{fmt(hn):>11}{fmt(hw):>11}{(fmt(hn / hw, 3) if hw else '—'):>9}"
                  f"{fmt(want_h, 4):>16}")
        print()

    # ------------------------------------------------------- linearity check
    if previous and constants:
        print("§4. The linearity check — the ratio a round at a MOVED anchor returns")
        print("-" * 120)
        print("  At a fixed geometry the departure is very nearly linear in the composited alpha,")
        print("  so a round rendered at the anchor the previous round WANTED should return a")
        print("  window ratio of 1.000. The distance from 1.000 is the non-linearity, in the")
        print("  quantity the solve is taken in. |Δratio| < the bar is the convergence test's")
        print("  anchor half (charter clause 3).")
        print()
        print(f"  {'scheme':<8}{'regime':<12}{'ratio was':>12}{'ratio now':>12}{'Δ':>12}{'':>8}")
        for scheme in ("light", "dark"):
            for name in ORDER:
                def ratio(source):
                    sel = [r for r in source
                           if r["scheme"] == scheme and r["regime"] == name
                           and r["state"] != "inactive" and r["tier"] == "webgpu"
                           and r["set"] != "holdout" and r["bed"] in STANDARD_BEDS[scheme]
                           and r["departure"]["window"]["native"] is not None]
                    if not sel:
                        return None
                    n = sum(r["departure"]["window"]["native"] for r in sel) / len(sel)
                    w = sum(r["departure"]["window"]["web"] for r in sel) / len(sel)
                    return (n / w) if w else None
                was, now = ratio(previous["rows"]), ratio(rows)
                if was is None or now is None:
                    continue
                delta = now - was
                print(f"  {scheme:<8}{name:<12}{was:>12.4f}{now:>12.4f}{delta:>+12.4f}"
                      f"{('  < bar' if abs(delta) < BAR else ''):>8}")
        print()

    # ---------------------------------------------------------------- inactive
    print("§5. The inactive pose — Decision Log 2's stand-down, read not solved")
    print("-" * 120)
    print("  The native window departure is exactly 0.000000 on this bed (claims §5.166 §7), so")
    print("  the ratio has a zero denominator and there is no anchor to solve. What is printed is")
    print("  what vitrea still draws in the window, which is what the stand-down is confirmed by.")
    print()
    print(f"  {'bed':<38}{'span':>6}{'n':>4}{'win N':>11}{'win W':>11}{'whole N':>11}{'whole W':>11}"
          f"{'T':>10}")
    for bed in beds:
        for span in spans:
            sel = [r for r in rows
                   if r["bed"] == bed and r["span"] == span and r["tier"] == "webgpu"
                   and r["state"] == "inactive" and r["set"] != "holdout"]
            win = [r for r in sel if r["departure"]["window"]["native"] is not None]
            if not win:
                continue
            ts = [r["T"] for r in sel if r["T"] is not None]
            print(f"  {bed:<38}{span:>6}{len(sel):>4}"
                  f"{sum(r['departure']['window']['native'] for r in win) / len(win):>11.6f}"
                  f"{sum(r['departure']['window']['web'] for r in win) / len(win):>11.6f}"
                  f"{sum(r['departure']['native'] for r in win) / len(win):>11.6f}"
                  f"{sum(r['departure']['web'] for r in win) / len(win):>11.6f}"
                  f"{(upper_middle(ts) if ts else float('nan')):>10.5f}")
    print()

    # ------------------------------------------------------ per backdrop
    print("§6. The per-backdrop residual — `T_dir` and the extent excess per backdrop")
    print("-" * 120)
    print("  §5.166 §10's finding N17: Apple's ACTIVE reach on macOS 27 depends on the backdrop")
    print("  outside the thin regime (16.0–18.5 CSS px at span 96 over twelve backdrops, 25.0–28.8")
    print("  at 128), so a fit of one triple against a bed pooled over backdrops leaves a")
    print("  per-backdrop residual at every span. It is REPORTED, never fitted.")
    print()
    print(f"  {'span':>5}  {'backdrop':<22}{'n':>4}{'T':>10}{'ext N':>9}{'ext W':>9}{'W − N':>9}")
    for span in spans:
        for backdrop in sorted({r["backdrop"] for r in rows if r["span"] == span}):
            sel = [r for r in rows
                   if r["span"] == span and r["backdrop"] == backdrop and r["tier"] == "webgpu"
                   and r["state"] != "inactive" and r["set"] != "holdout" and full_set(r)]
            if not sel:
                continue
            ts = [r["T"] for r in sel]
            en = [r["reach"]["below"]["native"] for r in sel
                  if r["reach"]["below"]["native"] is not None]
            ew = [r["reach"]["below"]["web"] for r in sel
                  if r["reach"]["below"]["web"] is not None]
            mn = upper_middle(en) if en else None
            mw = upper_middle(ew) if ew else None
            fmt = lambda v: "—" if v is None else f"{v:.2f}"
            print(f"  {span:>5}  {backdrop:<22}{len(sel):>4}{upper_middle(ts):>10.5f}"
                  f"{fmt(mn):>9}{fmt(mw):>9}"
                  f"{(fmt(mw - mn) if (mn is not None and mw is not None) else '—'):>9}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
