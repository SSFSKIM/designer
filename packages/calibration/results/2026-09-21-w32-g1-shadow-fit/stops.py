#!/usr/bin/env python3
"""W32 G0 — every stop the wave declares, read on the current generation today
(claims §5.166; W32 acceptance clause 2).

    python3 stops.py > stops.txt                # writes stops.json beside it

The before-readings G1 compares each round against. Nothing here is fitted,
adopted or captured; every figure is a cut of `results/matrix.json`, of this
gate's own `exterior-cut.json`, of W29 G3b's noise bar and of W31 G4's committed
chroma cut (X2, X5).

The stops, in the charter's order (clause 2):

  * **B1 at the shipped bytes** — `shadow-law.py --at-shipped` beside this file,
    whose windows this file quotes rather than recomputes.
  * **candidate (i)**, the rendered σ against the native σ on the WebGPU tier at
    spans 96 and 128, against the bound "inside B1's own ±5 % window of the
    native σ" — the sentence W31 G1 found false, declared here as a one-wave
    reading with today's value per bed.
  * **B3's departure residual** ≤ 0.00035 on the WebGPU tier over the whole
    exterior, with the WINDOW-RESTRICTED departure beside it, which is the
    quantity W32 clause 3 re-solves the anchors on.
  * **the thin regime, per cell**: on every active non-holdout WebGPU cell at
    spans 32 and 44, the inner bands' `|Δa|` against the native pair's MAX bar
    0.002044 over 432 cells (`results/2026-09-19-w29-g3b-shadow-recede/
    noise-bar.json`). **Every** such cell, which since the W32 G0 review closure
    means the accessibility beds too (claims §5.166 §10, finding N1): the stop
    names them and §3 tabulated only the four standard beds, so nine span-44
    cells the stop binds had no "today" to compare a round against — and they
    hold the population's worst `|Δa|` at the `3-6` band. The four standard beds'
    own figures are unchanged beside them, because the table is per bed.
  * **M1 and M2**, from W31 G4's committed `chroma-cut.json` — the cut they were
    adopted on and the one `adopted-thresholds.test.ts` points `CHROMA_CUT` at,
    which that test re-derives from `results/matrix.json` cell by cell. A second
    implementation of the cut's own population filter here would be a second
    thing to keep true, so this file quotes and says so.
  * **the structure, tint and rim rows expected unmoved**, as today's values per
    bed rather than as bounds: the bounds live in `adopted-thresholds.test.ts`
    and a second copy here would be the staleness that file's own doc comment
    warns about.
  * **the recede**, and **the seven `MISSED_27_ROWS`**.
"""
from __future__ import annotations

import json
import statistics
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
ROOT = PACKAGE.parent.parent

MATRIX = _env("VITREA_W32_G1_MATRIX", PACKAGE / "results/matrix.json")
CUT = _env("VITREA_W32_G1_CUT", HERE / "exterior-cut.json")
CUT_HOLDOUT = _env("VITREA_W32_G1_CUT_HOLDOUT", HERE / "exterior-cut-with-holdout.json")
DEPARTURE = _env("VITREA_W32_G1_DEPARTURE", HERE / "departure-stat.json")
NOISE_BAR = PACKAGE / "results/2026-09-19-w29-g3b-shadow-recede/noise-bar.json"
CHROMA_CUT = PACKAGE / "results/2026-09-21-w31-g4-landing/chroma-cut.json"

STANDARD_BEDS = ["1x light", "2x light", "1x dark", "2x dark"]
# The thin stop is declared over EVERY active non-holdout WebGPU cell at spans 32
# and 44, so its own table is read over every bed the cut carries rather than over
# the four standard ones. Computed from the cut instead of listed, so a bed that
# joins the fixture set joins the stop (review closure, finding N1).
def thin_beds(rows: list[dict]) -> list[str]:
    extra = sorted({r["bed"] for r in rows if r["bed"] not in STANDARD_BEDS})
    return STANDARD_BEDS + extra

THIN_SPANS = [32, 44]
THIN_BANDS = ["3-6", "6-12"]
THIN_BAR = 0.002044          # the MAX over 432 cells, the charter's named bar
B3_BOUND = 0.00035
B1_TOLERANCE = 0.05

CHROMA_BEDS = {
    "apple-macos-27.0-1x-light-standard-glass0.5": "light",
    "apple-macos-27.0-2x-light-standard-glass0.5": "light",
    "apple-macos-27.0-1x-dark-standard-glass0.5": "dark",
    "apple-macos-27.0-2x-dark-standard-glass0.5": "dark",
}
CHROMA_MEDIAN = (0.80, 1.20)
CHROMA_CELL = (0.60, 1.40)
CHROMA_STRUCTURE_TOLERANCE = 0.02

# The material axis's own structure, tint and rim readings. Values, not bounds:
# `adopted-thresholds.test.ts` holds the bounds and a copy here would be the
# staleness its own doc comment warns about.
# Each entry is `(metric, axis, scenes)`. The tint readings are taken over the
# TINTED scenes only: `tintChromaDeltaWeb` is zero by construction on an untinted
# surface, so a median over the whole bed reports the untinted majority and would
# not move if every tinted cell did.
UNMOVED_METRICS = [
    ("interiorStdDevWeb", "structure", "all"),
    ("interiorStdDevNative", "structure", "all"),
    ("tintChromaDeltaWeb", "tint", "tinted"),
    ("tintChromaDeltaNative", "tint", "tinted"),
    ("tintHueShiftWeb", "tint", "tinted"),
    ("rimPeakLuminanceWeb", "rim", "all"),
    ("rimFwhmWeb", "rim", "all"),
]


def upper_middle(values: list[float]) -> float:
    return sorted(values)[len(values) // 2]


def main() -> int:
    cut = json.loads(CUT.read_text())
    rows = cut["rows"]
    holdout_rows = json.loads(CUT_HOLDOUT.read_text())["rows"]
    departure = json.loads(DEPARTURE.read_text())
    matrix = json.loads(MATRIX.read_text())["cells"]
    bar_document = json.loads(NOISE_BAR.read_text())
    chroma = json.loads(CHROMA_CUT.read_text())

    print("W32 G0 — the stops, read today on the current generation")
    print("=" * 160)
    print()
    print(f"Cut:        {CUT.name}  (atDocuments={cut['atDocuments']}, "
          f"withHoldout={cut['withHoldout']})")
    print(f"Documents:  {', '.join(cut['documents'])}")
    print()

    payload: dict = {"documents": cut["documents"]}

    # ------------------------------------------------------------------
    print("§1. Candidate (i): the rendered σ against the native σ, WebGPU tier")
    print("-" * 160)
    print("  The wave's headline number, read at the verdict. The bound declared for it is")
    print("  'inside B1's own ±5 % window of the native σ' — which is the sentence W31 G1 found")
    print("  false (§5.162 §2: the law's σ is inside that window on 25 of 25 rows and the")
    print("  RENDERED σ is outside it on 24 of 25). Today's reading per bed, so the verdict has a")
    print("  before.")
    print()
    print(f"  {'bed':<12}{'span':>5}{'n':>4}{'native σ':>11}{'rendered σ':>12}"
          f"{'σ_web − σ_nat':>15}{'(i)':>9}{'±5 % window':>22}{'verdict':>10}")
    candidate_i = {}
    for bed in STANDARD_BEDS:
        for span in (96, 128, 160):
            here = [r for r in rows
                    if r["bed"] == bed and r["span"] == span and r["tier"] == "webgpu"
                    and r["state"] != "inactive" and r["set"] != "holdout"
                    and r["sigmaRelativeError"] is not None]
            if not here:
                continue
            native = upper_middle([r["sigmaNativeCss"] for r in here])
            rendered = upper_middle([r["sigmaWebCss"] for r in here])
            error = upper_middle([r["sigmaRelativeError"] for r in here])
            low, high = native * (1 - B1_TOLERANCE), native * (1 + B1_TOLERANCE)
            inside = low <= rendered <= high
            candidate_i[f"{bed} span {span}"] = {
                "n": len(here), "nativeSigmaCss": native, "renderedSigmaCss": rendered,
                "relativeError": error, "window": [low, high], "inside": inside,
            }
            print(f"  {bed:<12}{span:>5}{len(here):>4}{native:>11.3f}{rendered:>12.3f}"
                  f"{rendered - native:>15.3f}{error:>9.3f}"
                  f"{f'[{low:.3f}, {high:.3f}]':>22}"
                  f"{('INSIDE' if inside else 'OUTSIDE'):>10}")
    payload["candidateI"] = candidate_i
    print()

    # ------------------------------------------------------------------
    print("§2. B3's departure residual, and the window-restricted departure beside it")
    print("-" * 160)
    print(f"  B3: |meanDepartureWeb − meanDepartureNative| ≤ {B3_BOUND} on the WebGPU tier, the")
    print("  arithmetic mean over the calibration + validation cells of all six profiles — the")
    print("  population the bound was read over. `departure-stat.py` in this directory is the")
    print("  reading; the figures below are its own JSON.")
    print()
    stop = departure["stop"]
    wide = departure["nonHoldoutIncludingProbe"]
    print(f"  the stop, WebGPU, calibration + validation:      {stop['value']:.5f} "
          f"over {stop['n']} rows   {'MET' if stop['value'] <= B3_BOUND else 'BROKEN'} "
          f"against {B3_BOUND}")
    print(f"  every non-holdout row, probe included, WebGPU:   {wide['mean']:.5f} "
          f"over {wide['n']} rows   (recorded, not the stop)")
    print()
    print("  The window-restricted departure — the SAME functional over the admitted bands only,")
    print("  which is what W32 clause 3 re-solves the six occlusion anchors on. The difference")
    print("  between the two is the change of objective G1 measures at its first round, and it is")
    print("  large: the `0-3` band the window excludes holds the body's own over-fill.")
    print()
    print(f"  {'bed':<12}{'span':>5}{'n':>4}{'whole |Δ|':>12}{'window |Δ|':>13}"
          f"{'ratio':>8}{'whole nat':>12}{'window nat':>13}{'whole web':>12}{'window web':>13}")
    window_departure = {}
    for bed in STANDARD_BEDS:
        for span in (32, 44, 96, 128, 160):
            here = [r for r in rows
                    if r["bed"] == bed and r["span"] == span and r["tier"] == "webgpu"
                    and r["state"] != "inactive" and r["set"] != "holdout"
                    and r["departure"]["window"]["native"] is not None]
            if not here:
                continue
            whole = upper_middle([abs(r["departure"]["web"] - r["departure"]["native"])
                                  for r in here])
            window = upper_middle([abs(r["departure"]["window"]["difference"]) for r in here])
            record = {
                "n": len(here), "wholeAbsDelta": whole, "windowAbsDelta": window,
                "wholeNative": upper_middle([r["departure"]["native"] for r in here]),
                "windowNative": upper_middle([r["departure"]["window"]["native"] for r in here]),
                "wholeWeb": upper_middle([r["departure"]["web"] for r in here]),
                "windowWeb": upper_middle([r["departure"]["window"]["web"] for r in here]),
            }
            window_departure[f"{bed} span {span}"] = record
            print(f"  {bed:<12}{span:>5}{len(here):>4}{whole:>12.5f}{window:>13.5f}"
                  f"{(window / whole if whole else float('nan')):>8.2f}"
                  f"{record['wholeNative']:>12.5f}{record['windowNative']:>13.5f}"
                  f"{record['wholeWeb']:>12.5f}{record['windowWeb']:>13.5f}")
    payload["b3"] = {"bound": B3_BOUND, "stop": stop, "nonHoldoutIncludingProbe": wide,
                     "windowDeparture": window_departure}
    print()

    # ------------------------------------------------------------------
    print("§3. The thin regime, per cell — the table G1 compares against")
    print("-" * 160)
    print(f"  Every ACTIVE, non-holdout, WebGPU cell at spans 32 and 44, with `|Δa|` at the two")
    print(f"  bands the shadow reaches there, direction `all`. The bar is {THIN_BAR} — the MAX of")
    print("  `shadowAffineSlopeDeltaMax` over the 432 cells of W29 G3b's native-pair noise bar,")
    print("  which is the charter's named number. The stop is per cell: no cell's `|Δa|` at")
    print("  either band worse than today's by more than the bar, and the order statistic per bed")
    print("  no worse than today's.")
    print()
    print("  EVERY bed, which since the review closure includes the accessibility beds (claims")
    print("  §5.166 §10, finding N1). They were outside this table and inside the stop, and they")
    print("  carry the population's worst reading; the standard beds' own rows are unchanged.")
    print()
    print(f"  {'bed':<38}{'span':>5}{'set':<12}{'scene':<44}"
          + "".join(f"{('|Δa| ' + b):>12}" for b in THIN_BANDS))
    thin = {}
    for bed in thin_beds(rows):
        for span in THIN_SPANS:
            here = sorted([r for r in rows
                           if r["bed"] == bed and r["span"] == span and r["tier"] == "webgpu"
                           and r["state"] != "inactive" and r["set"] != "holdout"
                           and r["T"] is not None],
                          key=lambda r: r["scene"])
            if not here:
                continue
            for row in here:
                values = []
                for band in THIN_BANDS:
                    entry = row["perBand"]["all"].get(band)
                    values.append(None if entry is None or entry["deltaA"] is None
                                  else abs(entry["deltaA"]))
                thin[f"{row['tier']} / {row['set']} / {row['scene']} / {row['profile']}"] = {
                    "bed": bed, "span": span,
                    **{band: value for band, value in zip(THIN_BANDS, values)},
                }
                print(f"  {bed:<38}{span:>5}{row['set']:<12}{row['scene']:<44}"
                      + "".join(f"{'—':>12}" if v is None else f"{v:>12.5f}" for v in values))
            print()
    print("  The order statistic per bed and span, which is the second half of the stop:")
    print(f"  {'bed':<38}{'span':>5}{'n':>4}"
          + "".join(f"{('median ' + b):>16}{('max ' + b):>14}" for b in THIN_BANDS))
    thin_statistic = {}
    for bed in thin_beds(rows):
        for span in THIN_SPANS:
            here = [r for r in rows
                    if r["bed"] == bed and r["span"] == span and r["tier"] == "webgpu"
                    and r["state"] != "inactive" and r["set"] != "holdout" and r["T"] is not None]
            if not here:
                continue
            line = f"  {bed:<38}{span:>5}{len(here):>4}"
            record = {}
            for band in THIN_BANDS:
                values = [abs(r["perBand"]["all"][band]["deltaA"]) for r in here
                          if band in r["perBand"]["all"]
                          and r["perBand"]["all"][band]["deltaA"] is not None]
                if not values:
                    line += f"{'—':>16}{'—':>14}"
                    continue
                record[band] = {"median": upper_middle(values), "max": max(values),
                                "n": len(values)}
                line += f"{upper_middle(values):>16.5f}{max(values):>14.5f}"
            thin_statistic[f"{bed} span {span}"] = record
            print(line)
    print()
    print("  The worst cell over the WHOLE population, which is the figure a round is read")
    print("  against first and which no per-bed row carries:")
    worst = None
    population = [r for r in rows
                  if r["span"] in THIN_SPANS and r["tier"] == "webgpu"
                  and r["state"] != "inactive" and r["set"] != "holdout"
                  and r["T"] is not None]
    for row in population:
        for band in THIN_BANDS:
            entry = row["perBand"]["all"].get(band)
            if entry is None or entry["deltaA"] is None:
                continue
            value = abs(entry["deltaA"])
            if worst is None or value > worst["value"]:
                worst = {"value": value, "bed": row["bed"], "span": row["span"],
                         "band": band, "scene": row["scene"], "set": row["set"]}
    # Every cell that reads the worst value, on any bed: the figure is a tie across
    # two accessibility beds and naming one of them would under-report the stop.
    ties = [f"{r['bed']} span {r['span']}  {r['scene']}" for r in population
            if worst is not None
            and (r["perBand"]["all"].get(worst["band"]) or {}).get("deltaA") is not None
            and abs(r["perBand"]["all"][worst["band"]]["deltaA"]) == worst["value"]]
    print(f"    population {len(population)} cells over {len(thin_beds(rows))} beds")
    if worst is not None:
        print(f"    worst |Δa| {worst['value']:.5f} at band {worst['band']}, "
              f"read on {len(set(ties))} cells:")
        for scene in sorted(set(ties)):
            print(f"      {scene}")
    payload["thinRegime"] = {"bar": THIN_BAR, "perCell": thin, "perBed": thin_statistic,
                             "population": len(population), "beds": thin_beds(rows),
                             "worstCell": worst, "worstCellScenes": sorted(set(ties))}
    print()

    # ------------------------------------------------------------------
    print("§4. M1 and M2 today, from the cut they were adopted on")
    print("-" * 160)
    print("  M1: the median `R = chromaStructureRatioWeb / chromaStructureRatioNative` of every")
    print(f"  bed inside [{CHROMA_MEDIAN[0]}, {CHROMA_MEDIAN[1]}], and every cell inside "
          f"[{CHROMA_CELL[0]}, {CHROMA_CELL[1]}] or named in `MISSED_27_ROWS`.")
    print("  M2: `interiorStdDevWeb` within 2 % of the pre-fit generation's, which W31 G4's cut")
    print("  carries as `structureDeltaFraction` (the pre-fit generation lives under")
    print("  `results/superseded/` and is read by name there).")
    print()
    print("  Read from W31 G4's committed `chroma-cut.json`, which is the cut M1 and M2 were")
    print("  adopted on and the one `adopted-thresholds.test.ts` points `CHROMA_CUT` at. This")
    print("  file does not re-derive `R` from the matrix: the cut's own population is a filtered")
    print("  one (nine cells per light bed, four per dark) and a second implementation of that")
    print("  filter here would be a second thing to keep true. What proves the cut still matches")
    print("  the matrix is the test itself — it re-reads every cell's")
    print("  `chromaStructureRatio{Native,Web}` from `results/matrix.json` and asserts the cut's")
    print("  figures to twelve places — and it is green today (`chain.txt`).")
    print()
    by_profile: dict[str, list[float]] = {}
    structure: dict[str, list[float]] = {}
    for entry in chroma["cells"]:
        by_profile.setdefault(entry["profile"], []).append(entry["R"])
        structure.setdefault(entry["profile"], []).append(
            abs(entry["structureDeltaFraction"]))
    print(f"  {'profile':<62}{'n':>5}{'median R':>11}{'min':>9}{'max':>9}"
          f"{'outside cell':>14}{'verdict':>10}")
    m1 = {}
    for profile in sorted(by_profile):
        values = by_profile[profile]
        median = statistics.median(values)
        over = sum(1 for v in values if not CHROMA_CELL[0] <= v <= CHROMA_CELL[1])
        inside = CHROMA_MEDIAN[0] <= median <= CHROMA_MEDIAN[1]
        m1[profile] = {"n": len(values), "median": median, "min": min(values),
                       "max": max(values), "outsideCell": over, "medianInside": inside}
        print(f"  {profile:<62}{len(values):>5}{median:>11.5f}{min(values):>9.5f}"
              f"{max(values):>9.5f}{over:>14}{('MET' if inside else 'BROKEN'):>10}")
    print()
    print("  The cells outside [0.60, 1.40] are M1's three excused misses, all `photo__rrect-sm`")
    print("  at span 32, named in `MISSED_27_ROWS` at adoption (§5.165 §1).")
    print()
    print("  M2, from the same cut: `|interiorStdDevWeb / pre-fit − 1|` per bed, against 2 %.")
    print(f"  {'profile':<62}{'n':>5}{'median':>11}{'max':>11}{'verdict':>10}")
    m2 = {}
    for profile in sorted(structure):
        values = structure[profile]
        m2[profile] = {"n": len(values), "median": statistics.median(values),
                       "max": max(values), "met": max(values) <= CHROMA_STRUCTURE_TOLERANCE}
        print(f"  {profile:<62}{len(values):>5}{statistics.median(values):>11.5f}"
              f"{max(values):>11.5f}"
              f"{('MET' if m2[profile]['met'] else 'BROKEN'):>10}")
    payload["m2"] = m2
    payload["m1"] = m1
    print()

    # ------------------------------------------------------------------
    print("§5. The structure, tint and rim readings expected unmoved — today's VALUES per bed")
    print("-" * 160)
    print("  The bounds live in `adopted-thresholds.test.ts` and are not copied here, for that")
    print("  file's own reason: a number retyped is a number that goes stale silently. What a")
    print("  before-reading needs is the value, and these are the values a shadow fit must leave")
    print("  where it found them. Active, non-holdout, WebGPU tier; median over the bed.")
    print()
    print(f"  {'bed':<12}{'scenes':<10}"
          + "".join(f"{name[:17]:>19}" for name, _, _ in UNMOVED_METRICS))
    unmoved = {}
    for bed in STANDARD_BEDS:
        scale, scheme = bed.split()
        key = (f"apple-macos-27.0-{scale}-{scheme}-standard-glass0.5")
        here = [c for c in matrix
                if c["key"]["profileKey"] == key and c["tier"] == "texture"
                and c.get("fixtureSet") != "holdout" and c.get("state") != "inactive"]
        if not here:
            continue
        line = f"  {bed:<12}{'all/tinted':<10}"
        record = {}
        for name, _, scope in UNMOVED_METRICS:
            selected = [c for c in here
                        if scope == "all" or "tint" in c["key"]["sceneId"]]
            values = [c["material"][name]["value"] for c in selected
                      if (c.get("material") or {}).get(name) is not None]
            if not values:
                line += f"{'—':>19}"
                continue
            record[name] = {"median": statistics.median(values), "n": len(values),
                            "scope": scope}
            line += f"{statistics.median(values):>19.5f}"
        unmoved[bed] = record
        print(line)
    payload["unmoved"] = unmoved
    print()

    # ------------------------------------------------------------------
    print("§6. The recede's declared reading")
    print("-" * 160)
    print("  The inactive `T_dir` per bed and span over the admitted bands, and what the recede's")
    print("  anchor solve is judged on: the inactive DEPARTURE RATIO per regime. The reading that")
    print("  governs both is §12c of `exterior-cut.txt` — on every inactive cell of this bed")
    print("  Apple's receded window removes NO light from 3 CSS px outward, so the ratio's")
    print("  denominator is zero and the recede is not the active shadow at a lower alpha.")
    print()
    print(f"  {'bed':<12}{'span':>5}{'n':>4}{'T all':>10}{'T above':>10}{'T below':>10}"
          f"{'T left':>10}{'T right':>10}{'win nat':>11}{'win web':>11}{'nat flat':>11}")
    recede = {}
    for bed in STANDARD_BEDS:
        for span in (32, 44, 96, 128, 160):
            here = [r for r in rows
                    if r["bed"] == bed and r["span"] == span and r["tier"] == "webgpu"
                    and r["state"] == "inactive" and r["set"] != "holdout"
                    and r["T"] is not None]
            if not here:
                continue
            record = {"n": len(here)}
            line = f"  {bed:<12}{span:>5}{len(here):>4}"
            for direction in ("all", "above", "below", "left", "right"):
                values = [r["Tdir"][direction] for r in here
                          if r["Tdir"][direction] is not None]
                record[direction] = upper_middle(values) if values else None
                line += f"{'—':>10}" if not values else f"{upper_middle(values):>10.5f}"
            with_window = [r for r in here if r["departure"]["window"]["native"] is not None]
            native_window = [r["departure"]["window"]["native"] for r in with_window]
            web_window = [r["departure"]["window"]["web"] for r in with_window]
            flat = sum(1 for v in native_window if v == 0)
            record["windowNative"] = upper_middle(native_window) if native_window else None
            record["windowWeb"] = upper_middle(web_window) if web_window else None
            record["nativeFlat"] = f"{flat}/{len(with_window)}"
            line += (f"{upper_middle(native_window):>11.6f}{upper_middle(web_window):>11.6f}"
                     f"{record['nativeFlat']:>11}") if native_window else f"{'—':>33}"
            recede[f"{bed} span {span}"] = record
            print(line)
    payload["recede"] = recede
    print()

    # ------------------------------------------------------------------
    print("§7. `MISSED_27_ROWS` today, decomposed for what the shadow can reach")
    print("-" * 160)
    print("  **The list is not §5.162 §4's seven.** That section read the seven rows the list held")
    print("  at W31 G1; two of them — `photo__rrect-lg__rest :: oklabDeltaEP95` on the WebGPU tier,")
    print("  1x and 2x dark — CLEARED at W31 G3 (0.21531 → 0.14655 and 0.21341 → 0.14505) and are")
    print("  no longer in it, and M1's three chroma rows joined it at W31 G4. Today it is FIVE")
    print("  `dom`-tier rows plus THREE chroma rows, which is what the charter's Grounding says")
    print("  and what this gate decomposes. The two cleared rows are read beside, for continuity")
    print("  with §5.162 §4 and because they are the same scene at the same span.")
    print()
    print("  Read under `--with-holdout`: all five shadow rows are holdout rows and a committed")
    print("  row re-read is not a new read of the bed (§5.162 §4). The chroma rows are validation")
    print("  rows and need no flag. Nothing is CLAIMED through this wave.")
    print()
    print("  `share` is the fraction of the cell's SSIM windows that lie OUTSIDE the silhouette,")
    print("  and `reach` is the most the metric could move if the exterior became perfect —")
    print("  `share × (1 − ssimOutside)`. Where `reach` is below the gap the row is NOT reachable")
    print("  through the shadow at all, however well the exterior is fitted.")
    print()
    print("  **What `reach` assumes, said beside it** (W32 G0 review closure, claims §5.166 §10,")
    print("  finding N13). It counts the `ssimOutside` windows only, so it treats every `ssimBand`")
    print("  window as UNIMPROVABLE. On `checkerboard__rrect-lg__rest` that is 18,556 windows —")
    print("  31.8 % of the cell, at `ssimBand` 0.7874, the worst of the three regions — against a")
    print("  verdict whose margin is 0.00059. The band region holds the silhouette's own edge and")
    print("  the `0-3` band with it, and every form of C1 EXCLUDES `0-3`, so a NOT-reachable")
    print("  verdict here reads \"not reachable by the exterior this wave fits\" and not \"not")
    print("  reachable by any shadow work\". The margin is printed so the thinness is visible.")
    print()
    missed = [
        ("dom", "apple-macos-27.0-1x-light-standard-glass0.5",
         "checkerboard__glass-over-glass__rest", "ssimMean", 0.89531, 0.9, "≥", "current"),
        ("dom", "apple-macos-27.0-1x-light-standard-glass0.5",
         "checkerboard__rrect-lg__rest", "ssimMean", 0.88423, 0.9, "≥", "current"),
        ("dom", "apple-macos-27.0-1x-dark-standard-glass0.5",
         "photo__rrect-lg__rest", "oklabDeltaEP95", 0.20095, 0.18, "≤", "current"),
        ("dom", "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
         "photo__rrect-lg__rest", "ssimOutside", 0.82695, 0.83, "≥", "current"),
        ("dom", "apple-macos-27.0-2x-dark-standard-glass0.5",
         "photo__rrect-lg__rest", "oklabDeltaEP95", 0.19474, 0.19, "≤", "current"),
        ("texture", "apple-macos-27.0-1x-dark-standard-glass0.5",
         "photo__rrect-lg__rest", "oklabDeltaEP95", 0.21531, 0.17, "≤", "cleared at W31 G3"),
        ("texture", "apple-macos-27.0-2x-dark-standard-glass0.5",
         "photo__rrect-lg__rest", "oklabDeltaEP95", 0.21341, 0.17, "≤", "cleared at W31 G3"),
    ]
    chroma_rows = [
        ("texture", "apple-macos-27.0-1x-light-standard-glass0.5",
         "photo__rrect-sm__inactive", "chromaStructureRatioR", 1.51552, 1.40, "≤"),
        ("texture", "apple-macos-27.0-2x-light-standard-glass0.5",
         "photo__rrect-sm__inactive", "chromaStructureRatioR", 1.44690, 1.40, "≤"),
        ("texture", "apple-macos-27.0-2x-light-standard-glass0.5",
         "photo__rrect-sm__rest", "chromaStructureRatioR", 1.44173, 1.40, "≤"),
    ]
    tier_of = {"texture": "webgpu", "dom": "css"}
    index = {(r["tier"], r["profile"], r["scene"]): r for r in holdout_rows}
    matrix_index = {(c["tier"], c["key"]["profileKey"], c["key"]["sceneId"]): c
                    for c in matrix}
    print(f"  {'tier':<8}{'scene':<38}{'bed':<34}{'metric':<16}{'measured':>10}"
          f"{'bound':>9}{'gap':>9}{'today':>10}{'share':>8}{'reach':>9}{'(i)':>8}"
          f"{'T all':>9}   verdict")
    missed_out = {}
    for tier, profile, scene, metric, measured, bound, sense, status in missed:
        row = index.get((tier_of[tier], profile, scene))
        cell = matrix_index.get((tier, profile, scene))
        if row is None or cell is None:
            continue
        perceptual = cell["perceptual"]
        today = perceptual[metric]["value"]
        gap = (bound - measured) if sense == "≥" else (measured - bound)
        windows = {name: perceptual[f"ssim{name}Windows"]["value"]
                   for name in ("Outside", "Interior", "Band")}
        share = windows["Outside"] / sum(windows.values())
        outside = perceptual["ssimOutside"]["value"]
        if metric == "ssimMean":
            reach = share * (1.0 - outside)
            verdict = ("reachable if the exterior closes "
                       f"{gap / reach * 100:.0f} % of its own residual"
                       if reach >= gap else "NOT through the shadow")
        elif metric == "ssimOutside":
            reach = 1.0 - outside
            verdict = ("reachable — the metric IS the exterior; "
                       f"{gap / reach * 100:.0f} % of its residual")
        else:
            reach = float("nan")
            verdict = ("undecidable from the committed fields — the axis carries no "
                       "exterior-restricted ΔE")
        error = row["sigmaRelativeError"]
        missed_out[f"{tier} / {scene} / {profile} :: {metric}"] = {
            "status": status, "measured": measured, "bound": bound, "gap": gap,
            "today": today, "outsideWindowShare": share, "ssimOutside": outside,
            "reach": reach, "candidateI": error, "Tdir": row["Tdir"],
            "span": row["span"], "verdict": verdict,
        }
        print(f"  {tier:<8}{scene:<38}{row['bed']:<34}{metric:<16}{measured:>10.5f}"
              f"{f'{sense} {bound}':>9}{gap:>9.5f}{today:>10.5f}{share:>8.3f}"
              f"{('—' if reach != reach else f'{reach:.5f}'):>9}"
              f"{('—' if error is None else f'{error:.3f}'):>8}"
              f"{row['Tdir']['all']:>9.5f}   {verdict}"
              + ("" if status == "current" else f"   [{status}]"))
    print()
    print("  M1's three chroma rows, which the shadow does not touch:")
    print(f"  {'tier':<8}{'scene':<38}{'bed':<34}{'metric':<22}{'measured':>10}"
          f"{'bound':>9}   verdict")
    for tier, profile, scene, metric, measured, bound, sense in chroma_rows:
        bed = profile.removeprefix("apple-macos-27.0-").removesuffix("-glass0.5")
        missed_out[f"{tier} / {scene} / {profile} :: {metric}"] = {
            "status": "current", "measured": measured, "bound": bound,
            "verdict": "not through the shadow — a body-composite ratio",
        }
        print(f"  {tier:<8}{scene:<38}{bed:<34}{metric:<22}{measured:>10.5f}"
              f"{f'{sense} {bound}':>9}   not through the shadow — `R` is a ratio of the "
              f"BODY's chroma to its structure and the exterior is outside the silhouette")
    payload["missedRows"] = missed_out
    print()

    (HERE / "stops.json").write_text(json.dumps(payload, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
