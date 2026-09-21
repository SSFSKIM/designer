#!/usr/bin/env python3
"""W32 G0 — C1 in its three candidate forms, each over the admitted bands, with
the bound of the two non-declared forms fixed by the charter's own rule before
the tables exist (claims §5.166; W32 acceptance clause 2, Decision Log 1 (c)).

    python3 c1-forms.py > c1-forms.txt          # writes c1-forms.json beside it

Reads this gate's own `exterior-cut.json`, which is the cut the tables are taken
from, so the three forms are three readings of ONE population and differ only in
how they are summarised.

## The three forms

  **(i)** `T` as W31 G1 declared it and §5.162 §3 states it — the width-weighted
  mean of the per-band transmission error over 3–48 CSS px, ONE bound 0.0045
  across spans 96, 128 and 160, upper middle order statistic per standard bed,
  active, non-holdout, WebGPU tier. Restricted here to the admitted bands, which
  moves its span-128 and span-160 readings and moves nothing else; both numbers
  are printed.

  **(ii)** the same statistic, bounded PER SPAN — three numbers rather than one.
  §5.162 §9's finding N-9 names it as the first thing adoption should consider.

  **(iii)** the σ-NORMALISED window N-9 names second: bands at fixed multiples
  of the row's own native σ, so every span is read at the same number of falloff
  lengths. The axis's bands are fixed at 3 / 6 / 12 / 24 / 48 CSS px and cannot
  be re-cut without a re-capture, so the σ-bands are integrated out of the fixed
  ones: the per-band `|Δa|` is read as a piecewise-constant profile over
  distance — each band's value on its own interval, which is what a band mean IS
  — and each σ-band's value is that profile's mean over `[m_k σ, m_{k+1} σ)`.
  The multiples are `SIGMA_MULTIPLES` and are proposed from the bed below rather
  than assumed.

## The bound rule, which is the charter's and not this file's

W32 clause 2: *"the bound at every span is the worst standard bed's span-96
order statistic of that form on the current generation, rounded up to two
significant figures"* — the promise "no worse at any span than at span 96
today", which is C1's own justification (§5.162 §3) applied form by form. This
file computes it and prints it as the bound; it cannot choose the number and the
parent chooses only the form.

Nothing is fitted, adopted or captured (W32 X2, X4, X5).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- W32 G1's ONE change to this copy (claims §5.168) ---------------------
# G0 read one cut, in its own directory. G1 reads a cut per ROUND, each in its
# own subdirectory under `rounds/`, plus the pre-fit one under `pre-fit/` and
# the read's under this directory. Rather than copy the file per round, the
# three inputs this reader takes from disk are overridable by environment
# variable; unset, every path is byte-for-byte G0's. Nothing else in this file
# differs from `results/2026-09-21-w32-g0-exterior-cut/`'s copy.
import os as _os
def _env(name: str, default):
    raw = _os.environ.get(name)
    return default if raw is None else Path(raw)
PACKAGE = HERE.parent.parent
CUT = _env("VITREA_W32_G1_CUT", HERE / "exterior-cut.json")

SHAPE_BANDS = [("3-6", 3.0, 6.0), ("6-12", 6.0, 12.0),
               ("12-24", 12.0, 24.0), ("24-48", 24.0, 48.0)]
BAND_WIDTH = {label: outer - inner for label, inner, outer in SHAPE_BANDS}
SIDES = ["above", "below", "left", "right"]

STANDARD_BEDS = ["1x light", "2x light", "1x dark", "2x dark"]
DECLARED_SPANS = [96, 128, 160]
ALL_SPANS = [32, 44, 96, 128, 160]

# W31 G1's declared bound on form (i), unchanged and not re-stated (W32 X4).
C1_DECLARED = 0.0045

# The σ-band edges of form (iii), as multiples of the row's own native σ. The
# innermost is 0.35 because the profile is undefined below 3 CSS px — the `0-3`
# band holds the body's own edge and is excluded from every form — and 0.35 σ is
# 3.08 CSS px at the span-96 bed's own native σ, so the window starts where the
# data does. The outermost is 2.8 because doubling three times from 0.35 keeps
# every σ-band one octave wide, which is what makes them comparable across spans.
SIGMA_MULTIPLES = [0.35, 0.7, 1.4, 2.8]


def upper_middle(values: list[float]) -> float:
    return sorted(values)[len(values) // 2]


def round_up_2sf(value: float) -> float:
    """Two significant figures, ALWAYS upward — the charter's rule."""
    if value <= 0:
        return 0.0
    exponent = math.floor(math.log10(value)) - 1
    step = 10.0 ** exponent
    return math.ceil(value / step) * step


def profile_of(row: dict) -> list[tuple[float, float, float]]:
    """The per-band `|Δa|` as a piecewise-constant profile of distance.

    `(inner, outer, |Δa|)` over the bands this row both ADMITS and identifies in
    direction `all`. It is a profile and not an interpolation: a band's value is
    already the mean of the transmission error over that interval, so reading it
    as constant there is the axis's own statement about the band and not a new
    assumption about the falloff.
    """
    out = []
    for label, inner, outer in SHAPE_BANDS:
        if label not in row["bandsUsed"]:
            continue
        entry = row["perBand"]["all"].get(label)
        if entry is None or entry["deltaA"] is None:
            continue
        out.append((inner, outer, abs(entry["deltaA"])))
    return out


def sigma_window(row: dict, sigma: float | None
                 ) -> tuple[float | None, list[tuple[float, float, float]]]:
    """Form (iii) per row: `T_σ` and the σ-bands it was read over.

    A σ-band is admitted when it lies inside the row's own clearance AND inside
    the distance range the fixed-band profile covers, which starts at 3 CSS px
    because `0-3` is excluded from every form.

    `sigma` is the BED AND SPAN's own median native σ rather than the cell's.
    Taken per cell, the σ-bands move from cell to cell inside one bed and the
    order statistic is then over cells read at different numbers of falloff
    lengths — which is the confound form (iii) exists to remove, reappearing one
    level down. Read at the bed's σ, every cell at a span is read over the same
    σ-bands and the population is the same one forms (i) and (ii) use.
    """
    profile = profile_of(row)
    if sigma is None or not profile:
        return None, []
    lowest = min(inner for inner, _, _ in profile)
    highest = max(outer for _, outer, _ in profile)
    clearance = min(row["clearanceCss"][side] for side in SIDES)
    bands = []
    for index in range(len(SIGMA_MULTIPLES) - 1):
        low = SIGMA_MULTIPLES[index] * sigma
        high = SIGMA_MULTIPLES[index + 1] * sigma
        if low < lowest or high > min(clearance, highest):
            continue
        # The profile's mean over [low, high), which is exactly the width
        # weighting of the fixed bands the σ-band overlaps.
        total = weight = 0.0
        for inner, outer, value in profile:
            overlap = min(outer, high) - max(inner, low)
            if overlap <= 0:
                continue
            total += overlap * value
            weight += overlap
        if weight <= 0:
            continue
        bands.append((low, high, total / weight))
    if not bands:
        return None, []
    numerator = sum((high - low) * value for low, high, value in bands)
    denominator = sum(high - low for low, high, _ in bands)
    return numerator / denominator, bands


def main() -> int:
    cut = json.loads(CUT.read_text())
    rows = [r for r in cut["rows"]
            if r["tier"] == "webgpu" and r["state"] != "inactive" and r["set"] != "holdout"
            and r["bed"] in STANDARD_BEDS]

    print("W32 G0 — C1 in three forms, over the admitted bands")
    print("=" * 160)
    print()
    print(f"Cut:        {CUT.name}  (atDocuments={cut['atDocuments']}, "
          f"withHoldout={cut['withHoldout']})")
    print(f"Documents:  {', '.join(cut['documents'])}")
    print("Population: WebGPU tier, active pose, non-holdout, the four standard macOS 27 beds")
    print("Statistic:  the upper middle order statistic, `sorted[n // 2]` — B1's convention")
    print()
    print("THE BOUND RULE, stated before the tables (W32 clause 2): the bound of forms (ii) and")
    print("(iii) at every span is the WORST standard bed's span-96 order statistic of that form")
    print("on this generation, rounded UP to two significant figures. Form (i)'s bound is W31 G1's")
    print("declared 0.0045 and is not re-stated here (X4).")
    print()

    bed_sigma: dict[tuple[str, int], float] = {}
    for bed in STANDARD_BEDS:
        for span in ALL_SPANS:
            got = [r["sigmaNativeCss"] for r in rows
                   if r["bed"] == bed and r["span"] == span
                   and r.get("sigmaNativeCss") is not None]
            if got:
                bed_sigma[(bed, span)] = upper_middle(got)
    for row in rows:
        row["Tsigma"], row["sigmaBands"] = sigma_window(
            row, bed_sigma.get((row["bed"], row["span"])))

    # ------------------------------------------------------------------
    print("§1. Form (i): `T` as declared, one bound across the thick spans")
    print("-" * 160)
    print("  Printed twice: over the ADMITTED bands, which is this gate's rule, and over W31 G1's")
    print("  own per-cell renormalisation, which is what §5.162 §1 records. They are the same")
    print("  number wherever the clearance holds all four bands and differ at spans 128 and 160,")
    print("  where the band the frame ate was in the sum. Neither is withdrawn.")
    print()
    print(f"  {'bed':<12}" + "".join(f"{('span ' + str(s)):>26}" for s in ALL_SPANS))
    forms: dict[str, dict] = {"i": {}, "ii": {}, "iii": {}}
    for bed in STANDARD_BEDS:
        line = f"  {bed:<12}"
        for span in ALL_SPANS:
            here = [r for r in rows if r["bed"] == bed and r["span"] == span
                    and r["T"] is not None and r["bandsUsed"] == r["admitted"]]
            if not here:
                line += f"{'—':>26}"
                continue
            statistic = upper_middle([r["T"] for r in here])
            forms["i"][(bed, span)] = {
                "value": statistic, "n": len(here),
                "min": min(r["T"] for r in here), "max": max(r["T"] for r in here),
                "bands": list(here[0]["admitted"]),
            }
            line += f"{f'{statistic:.5f} ({len(here)})':>26}"
        print(line)
    print()
    print(f"  Against the declared {C1_DECLARED} at the three spans C1 is stated over:")
    print(f"  {'bed':<12}" + "".join(f"{('span ' + str(s)):>22}" for s in DECLARED_SPANS))
    for bed in STANDARD_BEDS:
        line = f"  {bed:<12}"
        for span in DECLARED_SPANS:
            entry = forms["i"].get((bed, span))
            if entry is None:
                line += f"{'—':>22}"
                continue
            value = entry["value"]
            verdict = "PASS" if value <= C1_DECLARED else "FAIL"
            line += f"{f'{value:.5f} {verdict}':>22}"
        print(line)
    print()

    # ------------------------------------------------------------------
    print("§2. Form (ii): the same statistic, bounded PER SPAN")
    print("-" * 160)
    print("  The values are form (i)'s — the two forms differ in what they are compared against,")
    print("  not in what they measure. The bound is the rule's.")
    print()
    span96 = [forms["i"][(bed, 96)]["value"] for bed in STANDARD_BEDS
              if (bed, 96) in forms["i"]]
    bound_ii = round_up_2sf(max(span96))
    print(f"  The four standard beds at span 96 read "
          f"{', '.join(f'{v:.5f}' for v in sorted(span96))}; the worst is {max(span96):.5f} and")
    print(f"  the bound by the rule is {bound_ii:.4f} at EVERY span.")
    print()
    print(f"  {'bed':<12}" + "".join(f"{('span ' + str(s)):>22}" for s in DECLARED_SPANS))
    for bed in STANDARD_BEDS:
        line = f"  {bed:<12}"
        for span in DECLARED_SPANS:
            entry = forms["i"].get((bed, span))
            if entry is None:
                line += f"{'—':>22}"
                continue
            value = entry["value"]
            verdict = "PASS" if value <= bound_ii else "FAIL"
            forms["ii"][(bed, span)] = {"value": value, "bound": bound_ii,
                                        "pass": verdict == "PASS"}
            line += f"{f'{value:.5f} {verdict}':>22}"
        print(line)
    print()

    # ------------------------------------------------------------------
    print("§3. Form (iii): the σ-normalised window")
    print("-" * 160)
    print(f"  σ-band edges at {SIGMA_MULTIPLES} × the row's own native σ in CSS px. A σ-band is")
    print("  admitted where it lies inside the row's clearance and inside the range the fixed")
    print("  bands cover, which starts at 3 CSS px because `0-3` is excluded from every form.")
    print()
    print("  What the bed leaves, per span. `covers` is the distance range the fixed bands")
    print("  actually reach at that span, in CSS px: a σ-band outside it has no profile to")
    print("  average, and at span 160 that is the binding constraint rather than the clearance —")
    print("  the admitted bands stop at 12 CSS px and the FIRST σ-band ends at 0.7 σ = 12.1, so")
    print("  the form reads nothing there, by a tenth of a pixel.")
    print()
    print("  The clearance measured in the bed's own native σ is the deeper reading: 5.5–5.9 σ at")
    print("  span 96, 2.7 at 128 and 1.1 at 160. \"The same number of falloff lengths at every")
    print("  span\" is not purchasable on this canvas at any choice of multiples.")
    print(f"  {'bed':<12}{'span':>5}{'native σ':>11}{'clearance':>11}{'clearance/σ':>13}"
          f"{'covers':>10}{'σ-bands':>9}   the σ-bands, CSS px")
    for bed in STANDARD_BEDS:
        for span in ALL_SPANS:
            here = [r for r in rows if r["bed"] == bed and r["span"] == span
                    and r["Tsigma"] is not None]
            all_here = [r for r in rows if r["bed"] == bed and r["span"] == span
                        and r.get("sigmaNativeCss") is not None]
            if not all_here:
                continue
            sigma = bed_sigma[(bed, span)]
            clearance = min(all_here[0]["clearanceCss"][side] for side in SIDES)
            if here:
                bands = here[0]["sigmaBands"]
                described = ", ".join(f"[{low:.1f}, {high:.1f})" for low, high, _ in bands)
            else:
                bands, described = [], "none — no σ-band fits inside the clearance"
            covered = profile_of(all_here[0])
            span_of_profile = (f"{min(i for i, _, _ in covered):.0f}–"
                               f"{max(o for _, o, _ in covered):.0f}") if covered else "—"
            print(f"  {bed:<12}{span:>5}{sigma:>11.3f}{clearance:>11.2f}"
                  f"{clearance / sigma:>13.2f}{span_of_profile:>10}{len(bands):>9}   {described}")
    print()
    print(f"  {'bed':<12}" + "".join(f"{('span ' + str(s)):>26}" for s in ALL_SPANS))
    for bed in STANDARD_BEDS:
        line = f"  {bed:<12}"
        for span in ALL_SPANS:
            here = [r for r in rows if r["bed"] == bed and r["span"] == span
                    and r["Tsigma"] is not None]
            if not here:
                line += f"{'—':>26}"
                continue
            counts = {len(r["sigmaBands"]) for r in here}
            statistic = upper_middle([r["Tsigma"] for r in here])
            forms["iii"][(bed, span)] = {
                "value": statistic, "n": len(here),
                "sigmaBandCounts": sorted(counts),
            }
            line += f"{f'{statistic:.5f} ({len(here)})':>26}"
        print(line)
    print()
    sigma96 = [forms["iii"][(bed, 96)]["value"] for bed in STANDARD_BEDS
               if (bed, 96) in forms["iii"]]
    bound_iii = round_up_2sf(max(sigma96)) if sigma96 else float("nan")
    print(f"  The four standard beds at span 96 read "
          f"{', '.join(f'{v:.5f}' for v in sorted(sigma96))}; the worst is {max(sigma96):.5f}")
    print(f"  and the bound by the rule is {bound_iii:.4f} at EVERY span.")
    print()
    print(f"  {'bed':<12}" + "".join(f"{('span ' + str(s)):>22}" for s in DECLARED_SPANS))
    for bed in STANDARD_BEDS:
        line = f"  {bed:<12}"
        for span in DECLARED_SPANS:
            entry = forms["iii"].get((bed, span))
            if entry is None:
                line += f"{'—':>22}"
                continue
            value = entry["value"]
            verdict = "PASS" if value <= bound_iii else "FAIL"
            entry["bound"] = bound_iii
            entry["pass"] = verdict == "PASS"
            line += f"{f'{value:.5f} {verdict}':>22}"
        print(line)
    print()

    # ------------------------------------------------------------------
    print("§4. The composition of the bed each form is read on, per bed per span per pose")
    print("-" * 160)
    print("  `CONTRIBUTING_CELLS` for the adopting gate's guard, counted from the bed rather than")
    print("  transcribed — the reason W30 G4's review gave `CONTRIBUTING_BEDS` (§5.160 §9): a bed")
    print("  that stopped contributing would otherwise leave the clause to the beds that remain")
    print("  instead of failing. §5.162 §9's finding N-6 re-counted the composition; this is that")
    print("  count re-derived on the current generation and under the admitted-band rule.")
    print()
    print(f"  {'bed':<12}{'span':>5}{'cal':>5}{'val':>5}{'probe':>7}{'total':>7}"
          f"{'admitted':>24}   scenes")
    composition: dict[str, dict] = {}
    for bed in STANDARD_BEDS:
        for span in ALL_SPANS:
            here = [r for r in rows if r["bed"] == bed and r["span"] == span
                    and r["T"] is not None and r["bandsUsed"] == r["admitted"]]
            if not here:
                continue
            counts = {klass: sum(1 for r in here if r["set"] == klass)
                      for klass in ("calibration", "validation", "probe")}
            gated = sorted(r["scene"] for r in here
                           if r["set"] in ("calibration", "validation"))
            composition[f"{bed} span {span}"] = {
                **counts, "total": len(here),
                "admitted": list(here[0]["admitted"]), "gatedScenes": gated,
            }
            print(f"  {bed:<12}{span:>5}{counts['calibration']:>5}{counts['validation']:>5}"
                  f"{counts['probe']:>7}{len(here):>7}"
                  f"{'/'.join(here[0]['admitted']):>24}   "
                  f"{', '.join(gated) if gated else 'all probe'}")
    print()

    print("§5. What G0 recommends, and why — the parent rules (Decision Log 1 (c))")
    print("-" * 160)
    print("  **Form (ii), the per-span bound, at 0.0042.**")
    print()
    print("  Form (iii) is withdrawn on measurement, as the v1 charter's depth-normalised form")
    print("  was. It cannot be stated at span 160 on ANY bed — the admitted bands reach 12 CSS px")
    print("  there and the first σ-band ends at 0.7 σ = 12.1 — and span 160 is the span C1 exists")
    print("  for: it is where the residual the eye named is largest and where every non-ladder")
    print("  cell is holdout. It is also unreadable at span 44 on all four beds and at span 32 on")
    print("  two, so the thin regime this wave admits to the fit would carry no shape clause at")
    print("  all. And the reason is not the choice of multiples: the clearance in the bed's own")
    print("  native σ is 5.5–5.9 at span 96, 2.7 at 128 and 1.1 at 160, so no set of multiples")
    print("  buys the same number of falloff lengths at every span on a 320x200 canvas. The form")
    print("  is right in principle and the bed cannot carry it; it becomes available when the")
    print("  canvas does, which is this wave's first Deferred item.")
    print()
    print("  Form (i) is one bound across three spans and §5.162 §9's finding N-9 already records")
    print("  that it is span-confounded. The admitted-band rule makes it worse rather than better:")
    print("  the band SET now differs per span — four bands at 96, three at 128, two at 160 — so")
    print("  one number is a promise about three different statistics. It is kept as the reference")
    print("  reading and is not the clause.")
    print()
    print("  Form (ii) changes nothing about what is measured. It is form (i)'s own value read")
    print("  against a bound stated per span, which is the minimum change that makes the promise")
    print("  true: `no worse at any span than at span 96 today`. It keeps the statistic, the")
    print("  exclusions, the population and the order statistic exactly as W31 G1 declared them,")
    print("  it needs no re-binning and no assumption about the profile between band edges, and")
    print("  it fails today at 128 and 160 on all four beds, by 76–112 % at span 128 and 49–90 %")
    print("  at span 160 —")
    print("  which is the position B1 was in at its own declaration and is what makes it a clause")
    print("  a wave can be judged on rather than a restatement of a residual missed everywhere.")
    print()
    print("  What adopting it costs, stated plainly: the bound is 0.0042 rather than 0.0045, so")
    print("  span 96 passes with 1.7–8.3 % of headroom (2x light 0.00413, 1x light 0.00408, 1x")
    print("  dark 0.00399, 2x dark 0.00385) where form (i) leaves 8–14 %. The rule is the")
    print("  charter's, so this is what the rule produces on this generation and not a number this")
    print("  gate chose; and the thin margin at span 96 is the clause's own statement that span 96")
    print("  is not free either — a fit that buys span 128 by widening span 96 fails.")
    print()

    (HERE / "c1-forms.json").write_text(json.dumps({
        "cut": CUT.name,
        "atDocuments": cut["atDocuments"],
        "withHoldout": cut["withHoldout"],
        "documents": cut["documents"],
        "population": "webgpu tier, active pose, non-holdout, the four standard macOS 27 beds",
        "statistic": "upper middle order statistic, sorted[n // 2]",
        "boundRule": "the worst standard bed's span-96 order statistic of that form on this "
                     "generation, rounded up to two significant figures (W32 clause 2)",
        "sigmaMultiples": SIGMA_MULTIPLES,
        "forms": {
            "i": {"bound": C1_DECLARED, "declaredBy": "W31 G1, claims §5.162 §3",
                  "readings": {f"{bed} span {span}": value
                               for (bed, span), value in forms["i"].items()}},
            "ii": {"bound": bound_ii,
                   "readings": {f"{bed} span {span}": value
                                for (bed, span), value in forms["ii"].items()}},
            "iii": {"bound": bound_iii,
                    "readings": {f"{bed} span {span}": value
                                 for (bed, span), value in forms["iii"].items()}},
        },
        "contributingCells": composition,
    }, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
