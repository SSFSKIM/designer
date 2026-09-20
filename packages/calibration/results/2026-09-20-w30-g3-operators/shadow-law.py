#!/usr/bin/env python3
"""W30 G3 — the sigma law and the six anchors, solved from the native cut.

    python3 shadow-law.py > shadow-law.txt

The evidence is W30 G0's `shadow-cut.json` — the per-cell native sigma_css and
falloff amplitude of the macOS 27 bed, read off
`results/2026-09-19-w29-g3b-shadow-recede/native-delta.json` with the statistic
G0 named (upper middle order statistic, `sigma_css > span` excluded). Nothing
under G0's directory is written; this file reads it.

Three things are computed and each answers a clause of the declaration:

  1. **B1's joint windows per document**, recomputed from the cut rather than
     transcribed from the ledger (claims §5.156 §5 as restated; charter Decision
     Log 3 (c)). A document serves several beds, so the admissible sigma at each
     span is the INTERSECTION of the +-5 % windows of every bed it serves, and
     the law's three free numbers have to land inside all of them at once.
  2. **The sigma law**, fitted jointly across those beds with `sigmaSpanRefPx`
     HELD at 96 and `sigmaPx` refitted as the sigma at span 96. Four objectives
     are computed and the file says which is adopted and why: the absolute least
     squares (which lands the light document OUTSIDE B1's joint window, because
     a squared absolute residual weights a span-160 observation four times a
     span-96 one and B1 is a relative clause), the same restricted to the window,
     the minimax relative error (B1's own currency), and the adopted one — the
     point that maximises the smaller of B1's and B2's normalised slacks with the
     slope held inside the range the served beds measure for themselves. Each is
     reported with its position inside every window in percent, so a pass is
     visible and so is a miss.
  3. **The six occlusion anchors and `liftAmplitude`'s starting point**, from the
     native falloff amplitude per span per bed. The reader's amplitude is the
     model's occlusion at the contour and is sigma-independent by construction
     (claims §5.156 §2), which is what makes it readable BEFORE the candidate is
     rendered; the value it implies is a starting point and the departure the
     rendered rounds measure is what settles it.

The thin regime is not fitted (Decision Log 2 (b)): `sigmaThinOffsetPx` is set
by declaration to put the floor at the thick line evaluated at the thin spans,
and B2's check statistic — the untinted, non-holdout, non-excluded, dpr-1
span-44 median — is printed beside it.

**Two flags, added 2026-09-20 by the W30 G3/G3b review closure (claims §5.159b
§10, findings 5 and 7). Both default OFF, so the bare invocation above is still
the one that produced the committed `shadow-law.txt`** — that file is evidence
and §5.159b §3 reads it by a zero-line `diff`, so a default that moved would
retire a proof rather than add one.

    python3 shadow-law.py --fit-on non-holdout --at-shipped > shadow-law.v2.txt

  * `--fit-on non-holdout` gives the adopted fit — the served beds' own slope
    range and the joint-margin grid — the non-holdout table rather than the
    pooled one, which is what the table's own label promises the fit may see.
    B1's WINDOWS and the printed verdict stay on the pooled medians: that
    population is the clause's, declared at §5.156 §5, and narrowing it would
    change what B1 asserts rather than what the fit is allowed to read. The
    answer does not move past the rounding the seal writes, which is the
    reading §5.159b §10 records.
  * `--at-shipped` prints B1 and B2 a second time at the ROUNDED constants the
    four sealed documents carry, beside the fit's own unrounded pair. A fit is
    adopted at four significant figures and read back at five, and the two
    differ in the third decimal of B1's percentage; the seal's values are the
    ones the material draws, so they are the ones a clause is held to.

A run with either flag writes `shadow-law.v2.json` rather than the committed
`shadow-law.json`, for the same reason.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUT = HERE.parent / "2026-09-20-w30-g0-cut" / "shadow-cut.json"
# The documents the seal writes, whose rounded leaves `--at-shipped` reads. The
# receded documents inherit the σ law rather than restating it (`reach-pad.txt`).
SEALED = {
    "light": HERE.parent.parent / "profiles/apple-macos-27.0-1x-light-standard-glass0.5.json",
    "dark": HERE.parent.parent / "profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json",
}

THICK = (96, 128, 160)
REF = 96.0

# Which beds each shipped document draws. The scale and the accessibility state
# are axes of the capture and of the policy, not of the material document
# (the documents' own `$comment`), so one document is judged jointly on all of
# them — which is what makes B1 two clauses rather than seven.
SERVES = {
    "light": ["1x light", "2x light", "1x light-reduced-transparency",
              "1x light-increased-contrast-coupled"],
    "dark": ["1x dark", "2x dark"],
}
# `1x light-increased-contrast` is the confounded key W29 Decision Log 5 left
# out of the six declared profiles; it is printed and never fitted on.
REPORTED_ONLY = ["1x light-increased-contrast"]


def median(values: list[float]) -> float | None:
    """G0's statistic: the upper middle order statistic, `sorted[n // 2]`."""
    if not values:
        return None
    return sorted(values)[len(values) // 2]


def load() -> list[dict]:
    return json.loads(CUT.read_text())["cells"]


def sigma_table(cells: list[dict], keep) -> dict[tuple[str, int], tuple[float, int]]:
    out: dict[tuple[str, int], tuple[float, int]] = {}
    beds = sorted({c["bed"] for c in cells})
    for bed in beds:
        for span in sorted({c["span"] for c in cells}):
            sel = [c["sigmaCss"] for c in cells
                   if c["bed"] == bed and c["span"] == span and keep(c)]
            got = median(sel)
            if got is not None:
                out[(bed, span)] = (got, len(sel))
    return out


def amplitude_table(cells: list[dict], keep) -> dict[tuple[str, int], tuple[float, int]]:
    out: dict[tuple[str, int], tuple[float, int]] = {}
    for bed in sorted({c["bed"] for c in cells}):
        for span in sorted({c["span"] for c in cells}):
            sel = [c["amplitude27"] for c in cells
                   if c["bed"] == bed and c["span"] == span and keep(c)
                   and c.get("amplitude27") is not None]
            got = median(sel)
            if got is not None:
                out[(bed, span)] = (got, len(sel))
    return out


def window(medians: dict[tuple[str, int], tuple[float, int]], beds: list[str],
           span: int, tolerance: float) -> tuple[float, float] | None:
    lows, highs = [], []
    for bed in beds:
        entry = medians.get((bed, span))
        if entry is None:
            continue
        lows.append(entry[0] * (1 - tolerance))
        highs.append(entry[0] * (1 + tolerance))
    if not lows:
        return None
    return (max(lows), min(highs))


def observations(medians: dict[tuple[str, int], tuple[float, int]],
                 beds: list[str]) -> list[tuple[float, float]]:
    """One observation per served bed per thick span: (span - 96, median sigma).

    Unweighted, deliberately: B1's own windows weight each bed equally — a
    two-cell accessibility bed's window is as binding as a sixteen-cell
    standard one — so the fit is stated in the same currency as the bound it
    has to land inside.
    """
    out = []
    for bed in beds:
        for span in THICK:
            entry = medians.get((bed, span))
            if entry is not None:
                out.append((float(span - REF), entry[0]))
    return out


def sse(points: list[tuple[float, float]], intercept: float, slope: float) -> float:
    return sum((intercept + slope * x - y) ** 2 for x, y in points)


def fit(medians: dict[tuple[str, int], tuple[float, int]], beds: list[str]) -> tuple[float, float]:
    """Unconstrained least squares for (sigma96, slope) over the served beds.

    The law above the knee is `sigma96 + slope * (span - 96)`, linear in both
    unknowns, so the normal equations close in one step. Every bed that carries
    a median at a thick span contributes one observation, which is what makes
    the fit joint rather than a 1x fit checked at 2x afterwards — a 1x-light-only
    fit lands -6.08 % against the 2x-light bed (claims §5.156 §5).
    """
    points = observations(medians, beds)
    n = len(points)
    sx = sum(x for x, _ in points)
    sy = sum(y for _, y in points)
    sxx = sum(x * x for x, _ in points)
    sxy = sum(x * y for x, y in points)
    denominator = n * sxx - sx * sx
    slope = (n * sxy - sx * sy) / denominator
    intercept = (sy - slope * sx) / n
    return intercept, slope


def minimax_fit(medians: dict[tuple[str, int], tuple[float, int]],
                beds: list[str]) -> tuple[float, float, float]:
    """B1's own currency: minimise the worst RELATIVE error. Recorded, not adopted.

    B1 is a relative clause — ±5 % of each served bed's own median — and a least
    squares in absolute CSS px is not that objective. On the light document the
    difference is not cosmetic: the absolute fit is pulled down by the span-160
    observations, which are twice the magnitude of the span-96 ones and so carry
    four times the weight in a squared absolute residual, and it lands **on the
    joint window's lower boundary**, where the clause it is judged by is one
    reading's rounding from failing. Minimising the worst relative error puts it
    where no bed can be traded against another, and the margin that leaves is the
    clause's own headroom rather than an arbitrary nudge inside it.

    Solved by bisection on the worst error `t`: at a fixed `t` each observation
    is a strip `|sigma96 + slope*x - y| <= t*y` in the plane, the admissible set
    is their intersection, and feasibility is decided by scanning `sigma96` and
    intersecting the slope intervals the strips leave. Among the minimisers —
    the problem has a flat direction once only one span's observations bind —
    the tie is broken by least squares, which is why the return is lexicographic
    and not a single objective.

    Returns `(sigma96, slope, worst relative error)`.
    """
    points = observations(medians, beds)

    def feasible(t: float) -> tuple[float, float] | None:
        best: tuple[float, float, float] | None = None
        lo = min(y for _, y in points) * (1 - t) - 1
        hi = max(y for _, y in points) * (1 + t) + 1
        steps = 4000
        for index in range(steps + 1):
            intercept = lo + (hi - lo) * index / steps
            low, high = -1e9, 1e9
            ok = True
            for x, y in points:
                if x == 0:
                    if not (y * (1 - t) - 1e-12 <= intercept <= y * (1 + t) + 1e-12):
                        ok = False
                        break
                    continue
                low = max(low, (y * (1 - t) - intercept) / x)
                high = min(high, (y * (1 + t) - intercept) / x)
            if not ok or low > high:
                continue
            # Least squares in the slope, clamped into what this `t` admits.
            sxx = sum(x * x for x, _ in points)
            sxy = sum(x * (y - intercept) for x, y in points)
            slope = min(max(sxy / sxx, low), high)
            error = sse(points, intercept, slope)
            if best is None or error < best[0]:
                best = (error, intercept, slope)
        return None if best is None else (best[1], best[2])

    low, high = 0.0, 1.0
    answer = feasible(high)
    for _ in range(40):
        middle = (low + high) / 2
        got = feasible(middle)
        if got is None:
            low = middle
        else:
            high = middle
            answer = got
    assert answer is not None
    worst = max(abs(answer[0] + answer[1] * x - y) / y for x, y in points)
    return (answer[0], answer[1], worst)


def bed_slopes(medians: dict[tuple[str, int], tuple[float, int]],
               beds: list[str]) -> dict[str, float]:
    """Each served bed's OWN least-squares slope over its own thick medians.

    §5.156 §2 tabulates these per bed — 0.1283 to 0.1340 across the whole macOS
    27 capture — and they are what says the slope is a measured quantity rather
    than a free one. A joint fit whose slope falls outside the range its own beds
    measure is a fit of the clause and not of the bed, so the range is computed
    here and used as a constraint rather than quoted as a comfort.
    """
    out: dict[str, float] = {}
    for bed in beds:
        xs = [(float(span - REF), medians[(bed, span)][0]) for span in THICK
              if (bed, span) in medians]
        if len(xs) < 2:
            continue
        n = len(xs)
        sx = sum(x for x, _ in xs)
        sy = sum(y for _, y in xs)
        sxx = sum(x * x for x, _ in xs)
        sxy = sum(x * y for x, y in xs)
        out[bed] = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    return out


def joint_margin_fit(medians: dict[tuple[str, int], tuple[float, int]], beds: list[str],
                     thin: dict[str, float],
                     slope_range: tuple[float, float]) -> tuple[float, float, float, float]:
    """The point that leaves the most room in BOTH declared clauses at once.

    B1 (the thick regime, ±5 % per served bed at spans 96/128/160) and B2 (the
    thin regime, a factor of 1.5 at span 44) are clauses on the SAME two numbers:
    σ(44) is `sigmaPx - 52 * slope` and the floor can only raise it, never lower
    it, so a law that sits comfortably inside one sits closer to the edge of the
    other. Minimising the worst relative error over the thick medians alone —
    `minimax_fit` — lands the light document at 4.32 % of B1's 5 % and at 1.49 of
    B2's 1.5; the absolute least squares lands it outside B1 altogether.

    So the adopted point maximises the smaller of the two clauses' normalised
    slacks: `1 - worst/limit` on each, with B1's worst taken as the largest
    |σ/median − 1| over every served bed at every thick span and B2's as the
    largest |ln(σ(44)/median)| / ln 1.5 over the beds whose thin statistic the
    declaration names — **subject to the slope staying inside the range the
    served beds measure for themselves** (`bed_slopes`). That last constraint is
    what keeps this a fit of the bed: σ(96) is pinned to within 0.7 percentage
    points by the beds' own disagreement whatever objective is used, so the only
    real freedom is the slope, and a slope outside 0.128–0.134 would be a fit of
    the clause. Inside that range the objective chooses where in a measured
    interval to sit, which is a choice the data does not make and the clauses do.

    Returns `(sigma96, slope, B1 worst relative error, B2 worst ratio)`.
    """
    points = observations(medians, beds)
    thin_medians = list(thin.values())
    best: tuple[float, float, float, float, float] | None = None
    lo96 = min(y for x, y in points if x == 0) * 0.95
    hi96 = max(y for x, y in points if x == 0) * 1.05
    for i in range(1201):
        intercept = lo96 + (hi96 - lo96) * i / 1200
        for j in range(1201):
            slope = slope_range[0] + (slope_range[1] - slope_range[0]) * j / 1200
            b1 = max(abs(intercept + slope * x - y) / y for x, y in points)
            at44 = intercept + slope * (44 - REF)
            if at44 <= 0:
                continue
            b2 = max(abs(math.log(at44 / y)) for y in thin_medians)
            slack = min(1 - b1 / 0.05, 1 - b2 / math.log(1.5))
            if best is None or slack > best[0]:
                best = (slack, intercept, slope, b1, math.exp(b2))
    assert best is not None
    return (best[1], best[2], best[3], best[4])


def constrained_fit(medians: dict[tuple[str, int], tuple[float, int]], beds: list[str],
                    windows: dict[int, tuple[float, float] | None],
                    ) -> tuple[float, float, bool]:
    """The same least squares, restricted to the points B1 admits.

    B1's joint windows are linear inequalities in (sigma96, slope) — one pair
    per thick span — so the admissible set is a convex polygon and the objective
    is a convex quadratic on it. The unconstrained optimum is returned when it
    is already inside; otherwise the minimum is on the boundary, and the search
    below is exact in the slope and fine in the intercept: for each sigma96 on a
    grid across its own window, the best slope is the one-dimensional least
    squares solution CLAMPED to the interval the other windows leave at that
    sigma96, which is the exact inner optimum because the objective is convex in
    the slope. The grid is 20,001 points over a window at most 0.42 CSS px wide,
    so its resolution is 2e-5 CSS px — four orders below the bound it lands in.

    Returns `(sigma96, slope, feasible)`. `feasible` is False when no point
    satisfies every window at once, which is the shape a B1 miss would take and
    is reported rather than clamped away.
    """
    points = observations(medians, beds)
    unconstrained = fit(medians, beds)

    def inside(intercept: float, slope: float) -> bool:
        for span, bounds in windows.items():
            if bounds is None:
                continue
            value = intercept + slope * (span - REF)
            if not (bounds[0] - 1e-12 <= value <= bounds[1] + 1e-12):
                return False
        return True

    if inside(*unconstrained):
        return (*unconstrained, True)

    at96 = windows.get(96)
    lo, hi = at96 if at96 is not None else (unconstrained[0] - 2.0, unconstrained[0] + 2.0)
    best: tuple[float, float, float] | None = None
    steps = 20_000
    for index in range(steps + 1):
        intercept = lo + (hi - lo) * index / steps
        # The exact inner optimum in the slope, then clamped to what the other
        # windows admit at this intercept.
        sxx = sum(x * x for x, _ in points)
        sxy = sum(x * (y - intercept) for x, y in points)
        slope = sxy / sxx
        low, high = -1e9, 1e9
        for span, bounds in windows.items():
            if bounds is None or span == REF:
                continue
            x = span - REF
            low = max(low, (bounds[0] - intercept) / x)
            high = min(high, (bounds[1] - intercept) / x)
        if low > high:
            continue
        slope = min(max(slope, low), high)
        value = sse(points, intercept, slope)
        if best is None or value < best[0]:
            best = (value, intercept, slope)
    if best is None:
        return (*unconstrained, False)
    return (best[1], best[2], True)


def shipped_law(scheme: str) -> tuple[float, float]:
    """The σ law as the seal rounded it, out of the document's own patch."""
    patch = json.loads(SEALED[scheme].read_text())["patch"]["outerShadow"]
    return (float(patch["sigmaPx"]), float(patch["sigmaSlopePerSpan"]))


def clause_readings(medians: dict[tuple[str, int], tuple[float, int]], beds: list[str],
                    thin: dict[str, float], intercept: float,
                    slope: float) -> tuple[float, float]:
    """B1's worst relative error and B2's worst ratio at one (σ96, slope).

    The same two quantities `joint_margin_fit` optimises, read at a point
    somebody else chose — which is what makes the fit's pair and the seal's pair
    comparable in one currency.
    """
    points = observations(medians, beds)
    b1 = max(abs(intercept + slope * x - y) / y for x, y in points)
    at44 = intercept + slope * (44 - REF)
    b2 = max(max(at44 / y, y / at44) for y in thin.values())
    return (b1, b2)


def main() -> int:
    argv = sys.argv[1:]
    fit_on = "pooled"
    at_shipped = False
    i = 0
    while i < len(argv):
        if argv[i] == "--fit-on" and i + 1 < len(argv) and argv[i + 1] in ("pooled", "non-holdout"):
            fit_on = argv[i + 1]
            i += 2
            continue
        if argv[i] == "--at-shipped":
            at_shipped = True
            i += 1
            continue
        print(f"unknown argument {argv[i]}; see the docstring", file=sys.stderr)
        return 2

    cells = load()
    active_all = lambda c: True
    non_holdout = lambda c: c["set"] != "holdout"

    pooled = sigma_table(cells, active_all)
    fittable = sigma_table(cells, non_holdout)
    amplitudes = amplitude_table(cells, non_holdout)
    amplitudes_pooled = amplitude_table(cells, active_all)
    # What the ADOPTED fit may read. B1's windows and the verdict below stay on
    # `pooled` whichever this is: the clause's population is declared and is not
    # a flag's to narrow.
    fit_medians = pooled if fit_on == "pooled" else fittable

    print("W30 G3 — the sigma law and the anchors, from W30 G0's native cut")
    print("=" * 100)
    print()
    print(f"  source     {CUT.relative_to(HERE.parent.parent)}")
    print("  statistic  upper middle order statistic of sigma_css, active cells, "
          "sigma_css > span excluded")
    print("  law        sigma(span) = sigmaPx + max(sigmaThinOffsetPx, "
          "sigmaSlopePerSpan * (span - 96))")
    if fit_on != "pooled" or at_shipped:
        print()
        print(f"  --fit-on {fit_on:<12} the adopted fit's slope range and grid read the "
              f"{'POOLED' if fit_on == 'pooled' else 'NON-HOLDOUT'} medians; B1's windows "
              "and the verdict are on the pooled medians either way")
        print(f"  --at-shipped {'on' if at_shipped else 'off':<8} "
              "B1 and B2 re-read at the rounded constants the seal wrote")
    print()

    print("1. The native sigma per bed per span — pooled (B1's population) and "
          "non-holdout (the fit's)")
    print("-" * 100)
    spans = sorted({c["span"] for c in cells})
    header = f"  {'bed':<38}" + "".join(f"{s:>16}" for s in spans)
    print(header)
    for bed in sorted({c["bed"] for c in cells}):
        line = f"  {bed:<38}"
        for span in spans:
            entry = pooled.get((bed, span))
            line += f"{'—':>16}" if entry is None else f"{entry[0]:>11.4f} ({entry[1]:>2}){'':>0}"
        print(line)
    print()
    print("  the same, non-holdout only (what the fit may see)")
    for bed in sorted({c["bed"] for c in cells}):
        line = f"  {bed:<38}"
        for span in spans:
            entry = fittable.get((bed, span))
            line += f"{'—':>16}" if entry is None else f"{entry[0]:>11.4f} ({entry[1]:>2})"
        print(line)
    print()

    solutions: dict[str, dict] = {}
    for scheme, beds in SERVES.items():
        print(f"2. The {scheme} document — joint over {', '.join(beds)}")
        print("-" * 100)
        free96, free_slope = fit(pooled, beds)
        windows = {span: window(pooled, beds, span, 0.05) for span in THICK}
        held96, held_slope, held_ok = constrained_fit(pooled, beds, windows)
        sigma96, slope, worst = minimax_fit(pooled, beds)
        points = observations(pooled, beds)
        print(f"  unconstrained least squares, absolute CSS px:   "
              f"sigmaPx {free96:.4f}, slope {free_slope:.5f}, worst relative error "
              f"{max(abs(free96 + free_slope * x - y) / y for x, y in points) * 100:.3f} %")
        print(f"  the same restricted to B1's joint windows:      "
              f"sigmaPx {held96:.4f}, slope {held_slope:.5f}"
              + ("" if held_ok else "   [NO FEASIBLE POINT — B1 cannot be met]"))
        print(f"  MINIMAX relative (B1's own currency, recorded): "
              f"sigmaPx {sigma96:.4f}, slope {slope:.5f}, worst relative error "
              f"{worst * 100:.3f} % against B1's 5 %")
        thin_stat = {}
        for bed in beds:
            sel = [c["sigmaCss"] for c in cells
                   if c["bed"] == bed and c["span"] == 44 and c["set"] != "holdout"
                   and c["scale"] == 1 and "-tint-" not in c["scene"]]
            got = median(sel)
            if got is not None:
                thin_stat[bed] = got
        own = bed_slopes(fit_medians, beds)
        span_of_slopes = (min(own.values()), max(own.values()))
        print("  each served bed's own least-squares slope: "
              + ", ".join(f"{bed} {value:.4f}" for bed, value in own.items()))
        joint96, joint_slope, joint_b1, joint_b2 = joint_margin_fit(
            fit_medians, beds, thin_stat, span_of_slopes)
        print(f"  JOINT MARGIN over B1 and B2, slope inside "
              f"[{span_of_slopes[0]:.4f}, {span_of_slopes[1]:.4f}] — THE FIT THIS CHILD ADOPTS: "
              f"sigmaPx {joint96:.4f}, slope {joint_slope:.5f}; B1 worst "
              f"{joint_b1 * 100:.3f} % of 5 %, B2 worst {joint_b2:.3f} of 1.5")
        print(f"  sum of squares {sse(points, free96, free_slope):.6f} free, "
              f"{sse(points, held96, held_slope):.6f} window-constrained, "
              f"{sse(points, sigma96, slope):.6f} minimax, "
              f"{sse(points, joint96, joint_slope):.6f} joint-margin, over "
              f"{len(points)} bed-span observations")
        if fit_on != "pooled":
            # The fit read the non-holdout medians; the clause is read on the
            # pooled ones, so the pair is printed in the verdict's own currency.
            pooled_b1, pooled_b2 = clause_readings(pooled, beds, thin_stat, joint96, joint_slope)
            print(f"  the same point against B1's POOLED population: B1 worst "
                  f"{pooled_b1 * 100:.3f} % of 5 %, B2 worst {pooled_b2:.3f} of 1.5")
        sigma96, slope = joint96, joint_slope
        for span, bounds in windows.items():
            if bounds is None:
                continue
            print(f"  B1 window at span {span:<4} [{bounds[0]:.4f}, {bounds[1]:.4f}]"
                  f"  (+-{(bounds[1] - bounds[0]) / (bounds[1] + bounds[0]) * 100:.3f} % "
                  f"about its own centre)")
        print()
        print(f"  {'span':<8}{'law':>10}{'window':>26}{'position':>12}   per bed")
        ok = True
        for span in THICK:
            value = sigma96 + slope * (span - REF)
            bounds = windows[span]
            inside = bounds is not None and bounds[0] <= value <= bounds[1]
            ok = ok and (bounds is None or inside)
            where = "—" if bounds is None else ("INSIDE" if inside else "MISSES")
            band = "—" if bounds is None else f"[{bounds[0]:.4f}, {bounds[1]:.4f}]"
            detail = "  ".join(
                f"{bed}: {value / pooled[(bed, span)][0] * 100 - 100:+.2f} %"
                for bed in beds if (bed, span) in pooled)
            print(f"  {span:<8}{value:>10.4f}{band:>26}{where:>12}   {detail}")
        print(f"  => B1 {'MET' if ok else 'MISSED'} on the {scheme} document at "
              f"the three thick spans")
        print()

        # The thin floor, by declaration: the thick line evaluated at span 44.
        floor_span = 44
        line_at_44 = sigma96 + slope * (floor_span - REF)
        offset = line_at_44 - sigma96
        b2 = {}
        for bed in beds + REPORTED_ONLY:
            sel = [c["sigmaCss"] for c in cells
                   if c["bed"] == bed and c["span"] == floor_span and c["set"] != "holdout"
                   and c["scale"] == 1 and "-tint-" not in c["scene"]]
            got = median(sel)
            if got is not None:
                b2[bed] = (got, len(sel))
        print(f"  the floor, by declaration: the thick line at span {floor_span} is "
              f"{line_at_44:.4f}, so sigmaThinOffsetPx = {offset:.4f}")
        print(f"  B2's statistic (untinted, non-holdout, dpr-1, span {floor_span}):")
        for bed, (value, count) in b2.items():
            ratio = line_at_44 / value
            print(f"    {bed:<40}{value:.4f} over {count:>2} cells   "
                  f"law/bed {ratio:.3f}x  {'inside' if 1/1.5 <= ratio <= 1.5 else 'OUTSIDE'} "
                  f"the factor 1.5")
        print(f"    shipped sigmaPx 11.0 against the same statistic: "
              + "  ".join(f"{bed} {11.0 / v[0]:.2f}x" for bed, v in b2.items()))
        knee = REF + offset / slope
        print(f"  the derived knee: {knee:.2f} CSS px "
              f"(sigmaSpanRefPx + sigmaThinOffsetPx / sigmaSlopePerSpan)")
        if at_shipped:
            # The clause at the bytes that draw. The fit is adopted at four
            # significant figures, and the document carries the rounded pair —
            # so B1 and B2 are read there too, on B1's own pooled population.
            ship96, ship_slope = shipped_law(scheme)
            fit_b1, fit_b2 = clause_readings(pooled, beds, thin_stat, sigma96, slope)
            ship_b1, ship_b2 = clause_readings(pooled, beds, thin_stat, ship96, ship_slope)
            ship44 = ship96 + ship_slope * (44 - REF)
            print(f"  AT THE SEALED, ROUNDED CONSTANTS — {SEALED[scheme].name}")
            print(f"    the fit      sigmaPx {sigma96:.5f}, slope {slope:.6f}: "
                  f"B1 worst {fit_b1 * 100:.4f} % of 5 %, B2 worst {fit_b2:.4f} of 1.5")
            print(f"    the document sigmaPx {ship96:.5f}, slope {ship_slope:.6f}: "
                  f"B1 worst {ship_b1 * 100:.4f} % of 5 %, B2 worst {ship_b2:.4f} of 1.5")
            print(f"    the document's own thin line at span 44 is {ship44:.4f} CSS px, "
                  f"sigmaThinOffsetPx {ship44 - ship96:.4f}")
            for span in THICK:
                value = ship96 + ship_slope * (span - REF)
                bounds = windows[span]
                inside = bounds is not None and bounds[0] <= value <= bounds[1]
                print(f"    span {span:<5}{value:>10.4f}   "
                      f"{'INSIDE' if inside else 'MISSES'} its pooled window")
        print()
        solutions[scheme] = {
            "sigmaPx": sigma96,
            "sigmaSlopePerSpan": slope,
            "sigmaSpanRefPx": REF,
            "sigmaThinOffsetPx": offset,
            "knee": knee,
            "b1": {str(span): {"law": sigma96 + slope * (span - REF),
                               "window": windows[span]} for span in THICK},
            "b2": {bed: {"median": v[0], "cells": v[1],
                         "ratio": line_at_44 / v[0]} for bed, v in b2.items()},
        }

    print("3. The native falloff amplitude per bed per span — what the anchors are solved toward")
    print("-" * 100)
    print("  The reader's amplitude is the model's occlusion at the contour and is")
    print("  sigma-INDEPENDENT by construction (the blurred-edge shape is 0.5 at distance")
    print("  zero whatever sigma is), so these are readable before a candidate is rendered.")
    print()
    print(f"  {'bed':<38}" + "".join(f"{s:>16}" for s in spans))
    for bed in sorted({c["bed"] for c in cells}):
        line = f"  {bed:<38}"
        for span in spans:
            entry = amplitudes.get((bed, span))
            line += f"{'—':>16}" if entry is None else f"{entry[0]:>11.4f} ({entry[1]:>2})"
        print(line)
    print()
    print("  pooled (holdout included), for the spans the fit has no cell at")
    for bed in sorted({c["bed"] for c in cells}):
        line = f"  {bed:<38}"
        for span in spans:
            entry = amplitudes_pooled.get((bed, span))
            line += f"{'—':>16}" if entry is None else f"{entry[0]:>11.4f} ({entry[1]:>2})"
        print(line)
    print()

    print("  the thin regime's amplitude by backdrop class, 1x, non-holdout, untinted")
    print(f"  {'bed':<38}{'backdrop':<22}{'span':>6}{'amplitude':>12}{'n':>5}")
    for bed in sorted({c["bed"] for c in cells}):
        for backdrop in sorted({c["backdrop"] for c in cells}):
            sel = [c["amplitude27"] for c in cells
                   if c["bed"] == bed and c["backdrop"] == backdrop and c["span"] in (32, 44)
                   and c["set"] != "holdout" and c["scale"] == 1 and "-tint-" not in c["scene"]
                   and c.get("amplitude27") is not None]
            got = median(sel)
            if got is not None:
                print(f"  {bed:<38}{backdrop:<22}{'32/44':>6}{got:>12.4f}{len(sel):>5}")
    print()

    # A default run rewrites G3's committed artefact and must therefore write
    # exactly what it wrote; a flagged run is a second reading and lands beside.
    default_run = fit_on == "pooled" and not at_shipped
    out = HERE / ("shadow-law.json" if default_run else "shadow-law.v2.json")
    out.write_text(json.dumps({
        "source": str(CUT.relative_to(HERE.parent.parent)),
        **({} if default_run else {"fitOn": fit_on, "atShipped": at_shipped}),
        "serves": SERVES,
        "solutions": solutions,
        "sigmaPooled": {f"{bed}|{span}": value for (bed, span), value in pooled.items()},
        "sigmaNonHoldout": {f"{bed}|{span}": value for (bed, span), value in fittable.items()},
        "amplitudeNonHoldout": {f"{bed}|{span}": value for (bed, span), value in
                                amplitudes.items()},
        "amplitudePooled": {f"{bed}|{span}": value for (bed, span), value in
                            amplitudes_pooled.items()},
    }, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
