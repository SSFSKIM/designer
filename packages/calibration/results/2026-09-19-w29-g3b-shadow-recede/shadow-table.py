#!/usr/bin/env python3
"""W29 G3b — the shadow axis of a fit label's matrices, native beside web.

    python3 shadow-table.py <label> [<label> ...] [--with-holdout]

The renders themselves are G3's `fit.py render`, unchanged and invoked as it
stands: one candidate document, one `compare` run into `$VITREA_G3_SCRATCH`,
with the same three refusals (another capture process, an accessibility toggle
that is not 0, a slider that is not 0.5). This is the reader G3's `fit.py table`
is for the material axis — the shadow axis has its own block in a cell and its
own absences, so it needs its own column set and not a `--metric` flag on a
table whose native/web pairs are named `<metric>Native` / `<metric>Web` under
`material`.

Absences are printed as `—` and never as zero: over `dark-solid` and `impulse`
there is no light to remove and the whole normalised block is absent, which is
the honest reading of a shadow over black and not a shadow of strength nothing.

**The holdout drop moved out of this file (W30 G0 (f), claims §5.156 §4).** It
used to live here, and it was the only place it lived — which is the tracker's
"the fit loop's holdout drop lives in one reader, and the other reader has
none". It is now `fit.py`'s `cells()`, the single function every reader built on
that file takes its rows from, so a wave that writes a new reader inherits the
guarantee instead of having to be told. This file reads through it and prints
the drop `cells()` reports; the behaviour is unchanged and the guarantee is one
function wider.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# `fit.py` is W29 G3's, one evidence directory along: `render` is invoked from
# there unchanged, so the reader that goes with it belongs there too.
sys.path.insert(0, str(HERE.parent / "2026-09-19-w29-g3-refit"))
from fit import cells as fit_cells  # noqa: E402

SCRATCH = Path(os.environ.get("VITREA_G3_SCRATCH", "/tmp/g3scratch"))

# Departure and the fitted pair are what a refit moves; the reach and the
# offset are what says whether the geometry moved with them.
COLUMNS = [
    ("meanDeparture", 5),
    ("falloffAmplitude", 4),
    ("falloffSigma", 2),
    ("strengthPeak", 4),
    ("extentBelow", 1),
    ("extentAbove", 1),
    ("offsetY", 1),
]


def at(block: dict, name: str) -> float | None:
    entry = block.get(name)
    return entry["value"] if isinstance(entry, dict) else None


def rows(matrix: Path, with_holdout: bool = False) -> list[dict]:
    out = []
    for cell in fit_cells(matrix, with_holdout):
        shadow = cell.get("shadow")
        if shadow is None:
            continue
        row = {
            "profile": cell["key"]["profileKey"],
            "renderer": cell["key"]["web"]["renderer"],
            "scene": cell["key"]["sceneId"],
            "set": cell.get("fixtureSet"),
            "support": at(shadow, "backdropSupport"),
        }
        for name, _ in COLUMNS:
            row[f"{name}N"] = at(shadow, f"{name}Native")
            row[f"{name}W"] = at(shadow, f"{name}Web")
        out.append(row)
    return out


def show(value: float | None, digits: int, width: int) -> str:
    return f"{'—':>{width}}" if value is None else f"{value:>{width}.{digits}f}"


def main(labels: list[str], with_holdout: bool = False) -> int:
    #
    # THE FIT NEVER READS A HOLDOUT ROW — and since W30 G0 (f) that is `fit.py`'s
    # `cells()` and not this file's own filter. The drop belongs to whatever
    # reads a fit label's matrices, not to one wave's script: a round whose
    # scene list names a holdout id still captures it, and what is guaranteed is
    # that no number off that capture reaches a human or a table, through any
    # reader built on that function. `cells()` prints what it dropped.
    #
    collected: list[dict] = []
    for label in labels:
        run = SCRATCH / "fit-log" / label
        for matrix in sorted(run.glob("*.json")):
            collected += rows(matrix, with_holdout)
    collected.sort(key=lambda r: (r["profile"], r["renderer"], r["scene"]))

    header = f"{'profile':<48}{'r':<4}{'scene':<42}"
    for name, _ in COLUMNS:
        header += f"{name + '·N':>13}{name + '·W':>13}{'Δ':>11}"
    print(header)
    for r in collected:
        line = f"{r['profile']:<48}{r['renderer'][:3]:<4}{r['scene']:<42}"
        for name, digits in COLUMNS:
            native, web = r[f"{name}N"], r[f"{name}W"]
            line += show(native, digits, 13) + show(web, digits, 13)
            line += (
                f"{'—':>11}"
                if native is None or web is None
                else f"{web - native:>+11.{digits}f}"
            )
        print(line)

    for name, digits in COLUMNS:
        pairs = [
            (r[f"{name}W"] - r[f"{name}N"], r)
            for r in collected
            if r[f"{name}N"] is not None and r[f"{name}W"] is not None
        ]
        if not pairs:
            print(f"\n{name}: no cell resolved both sides")
            continue
        mean_abs = sum(abs(d) for d, _ in pairs) / len(pairs)
        signed = sum(d for d, _ in pairs) / len(pairs)
        worst = max(pairs, key=lambda p: abs(p[0]))
        print(
            f"\n{name}: mean |Δ| {mean_abs:.{digits + 1}f}, signed mean {signed:+.{digits + 1}f}, "
            f"over {len(pairs)} cells; worst {worst[1]['profile']} {worst[1]['renderer']} "
            f"{worst[1]['scene']} {worst[0]:+.{digits + 1}f}"
        )
    return 0


if __name__ == "__main__":
    LABELS = [a for a in sys.argv[1:] if a != "--with-holdout"]
    if not LABELS:
        raise SystemExit(__doc__)
    raise SystemExit(main(LABELS, "--with-holdout" in sys.argv[1:]))
