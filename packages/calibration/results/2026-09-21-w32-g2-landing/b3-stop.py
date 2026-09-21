#!/usr/bin/env python3
"""W32 G2 — B3 as re-stated, read as a STOP (Decision Log 3 (a), ruled; claims §5.169 §2).

    python3 b3-stop.py [<label>=<exterior-cut.json> ...]

W32 G1's `b3-window.py` generalised into a reader with a BAR. That file computed
the window-restricted statistic beside the whole-exterior one as a decomposition
and said in as many words that "the number has no bar"; Decision Log 3 (a) gave
it one, so this file prints the statistic, the bound and PASS/FAIL and exits
nonzero on a fail. With no argument it reads this gate's own `exterior-cut.json`,
which is the cut taken at the shipped documents over the committed matrix.

## What B3 is now

**The shadow's departure residual over the ADMITTED BANDS**, both poses, WebGPU
tier, calibration + validation over all six macOS 27 profiles — 166 cells, 85
active and 81 inactive — as the arithmetic mean of
`|window departure web − window departure native|` per cell. The aggregation,
the tier, the sets and the population are W30 Decision Log 3 (a)'s and do not
move; what the re-statement changes is the PIXEL SET, from the whole exterior to
the bands 3–48 CSS px admitted on each cell in each direction by W32 G0's
clearance rule.

**Why it had to change** (claims §5.168 §7; Decision Log 3): over the whole
exterior B3 pools the `0-3` band, where two things live that are not the shadow
— vitrea's body over-filling its declared contour by 3.5–4 CSS px on the active
pose (§5.62) and, on the inactive pose, the one-device-pixel rim stroke that is
Apple's entire receded exterior (§5.166 §7). Those two errors had been
CANCELLING the exterior's own, so the wave that fitted the exterior broke the
stop by removing one side of a cancellation. The arithmetic says it was
unattainable: after Decision Log 2's stand-down the inactive half alone
contributes 81 × 0.00080 / 166 = 0.000390, already above the old 0.00035, with a
perfect active half.

## Where the bound comes from, and the choice inside the rule

W32 clause 2's rule: **the form's reading on the generation the stop is
re-derived from, rounded UP to two significant figures** — the promise "no worse
than the bed reads today". `round_up_2sf` below is W32 G0's `c1-forms.py`'s own
function, copied byte for byte, so C1 and B3 are rounded by one implementation.

Clause 2 states the rule as *"the worst standard BED's span-96 order statistic"*
because C1 is stated per bed and per span. **B3 is not**: W30 declared it as ONE
pooled arithmetic mean over its whole population, and the re-statement changes
the pixel set and nothing else, so the form has exactly one value on the
generation and "the worst" selects it trivially. Taking the rule's other reading
— the worst STANDARD bed — would give 0.000036 from 2x light and would be a
bound derived over four profiles for a stop read over six, with the two
accessibility beds (which hold the largest per-bed readings, 0.00023 and
0.00019) inside the statistic and outside its bound. That is a different
population, not a stricter bound, so the pooled reading is what is taken; the
per-bed table below is printed so the pooled number cannot hide a bed.

**It is a stop and not an adopted row** — read by script at every fit gate, in
W30's sense — so it lives here rather than in `adopted-thresholds.test.ts`, and
`departure-stat.py` beside it goes on reading the superseded whole-exterior form
at the same generation, because a superseded statement's last reading is kept
and not deleted.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent

SETS = ("calibration", "validation")

#: Decision Log 3 (a), derived by W32 clause 2's rule from the bed at W32 G1's
#: read: the statistic reads 0.0000559626 there and rounds up to this. Written as
#: a literal so the bar cannot drift with the file it is read against, and
#: re-derived by `--derive` from whatever cut is named.
B3_BOUND = 5.6e-05


def round_up_2sf(value: float) -> float:
    """Two significant figures, ALWAYS upward — W32 G0's `c1-forms.py`'s own."""
    if value <= 0:
        return 0.0
    exponent = math.floor(math.log10(value)) - 1
    step = 10.0 ** exponent
    return math.ceil(value / step) * step


def cells_of(path: Path) -> list[dict]:
    """The stop's population: WebGPU, calibration + validation, both poses."""
    return [
        row for row in json.loads(path.read_text())["rows"]
        if row["tier"] == "webgpu" and row["set"] in SETS
        and row["departure"]["native"] is not None
        and row["departure"]["window"]["native"] is not None
    ]


def window(rows: list[dict]) -> float:
    return mean(abs(row["departure"]["window"]["difference"]) for row in rows)


def whole(rows: list[dict]) -> float:
    return mean(abs(row["departure"]["web"] - row["departure"]["native"]) for row in rows)


def main(argv: list[str]) -> int:
    derive = "--derive" in argv
    specs = [a for a in argv if not a.startswith("--")]
    if not specs:
        specs = [f"shipped={HERE / 'exterior-cut.json'}"]

    print("W32 G2 — B3 as re-stated: the departure residual over the ADMITTED BANDS")
    print("=" * 104)
    print("  Decision Log 3 (a), ruled by the user 2026-09-22. The statistic, the aggregation,")
    print("  the tier and the sets are W30 Decision Log 3 (a)'s; the pixel set is W32 G0's")
    print(f"  admitted bands. The bound is {B3_BOUND:.6f}, W32 clause 2's rule applied to the")
    print("  bed at W32 G1's read. The whole-exterior form is printed beside it as the")
    print("  superseded statement's last reading, and is not a bound.")
    print()

    failed = False
    for spec in specs:
        label, _, path = spec.partition("=")
        rows = cells_of(Path(path))
        statistic = window(rows)
        verdict = "PASS" if statistic <= B3_BOUND else "FAIL"
        failed = failed or verdict == "FAIL"
        margin = (B3_BOUND - statistic) / B3_BOUND * 100
        print(f"── {label}  ({len(rows)} cells)")
        print(f"   B3 (admitted bands)   {statistic:.8f}   bound {B3_BOUND:.6f}   "
              f"{verdict}, {margin:.2f}% of the bound unused")
        print(f"   the superseded form   {whole(rows):.8f}   over the WHOLE exterior, "
              "recorded and not bounded")
        if derive:
            print(f"   the rule on THIS cut  {round_up_2sf(statistic):.6f}   "
                  "(what clause 2 would set the bound to here)")
        print()
        print(f"   {'population':<40}{'n':>5}{'B3':>14}{'whole exterior':>17}")
        for name, keep in (("pooled — the stop", lambda r: True),
                           ("active", lambda r: r["state"] != "inactive"),
                           ("inactive", lambda r: r["state"] == "inactive")):
            here = [r for r in rows if keep(r)]
            if here:
                print(f"   {name:<40}{len(here):>5}{window(here):>14.8f}{whole(here):>17.8f}")
        print()
        print(f"   {'per bed — printed so the pooled number hides none':<40}"
              f"{'n':>5}{'B3':>14}{'whole exterior':>17}")
        for bed in sorted({r["bed"] for r in rows}):
            here = [r for r in rows if r["bed"] == bed]
            print(f"   {bed:<40}{len(here):>5}{window(here):>14.8f}{whole(here):>17.8f}")
        print()

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
