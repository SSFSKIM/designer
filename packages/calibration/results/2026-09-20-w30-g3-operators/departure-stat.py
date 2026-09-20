#!/usr/bin/env python3
"""W30 G3 — B3's stop condition, read on this child's own matrices.

    python3 departure-stat.py [<matrix.json> ...] > departure-stat.txt

W30 G0's `results/2026-09-20-w30-g0-cut/departure-stat.py` is the definition of
the statistic and this file does not restate it: the partition rule
(`atAShippedDocument` reproduced from the `capturePath`'s own content hash), the
quantity (`|shadow.meanDepartureWeb - shadow.meanDepartureNative|`) and the tier
map are IMPORTED from it. Nothing under that directory is edited — it is
committed evidence, and its `departure-stat.json` is G0's reading. This file
writes its own beside it, under this child's evidence directory.

Two things are added, and each exists because this child's read changes the
population the stop was declared over:

  1. **A like-for-like partition.** B3's 0.00035 was read over the macOS 27
     generation's non-holdout rows, which at G0 were calibration + validation
     and nothing else — the generation carried no probe row at all (claims
     §5.156 §3). This child's canonical read appends the pitch ladder as probe
     rows (Decision Log 2 (a)), which are also non-holdout, so "the non-holdout
     cells of all six profiles" names a different population before and after.
     The stop is read on the population it was declared over — calibration +
     validation — and the probe-inclusive figure is printed beside it, because a
     stop that silently changes its own row set is not a stop.
  2. **Scratch matrices.** A fit round's matrices are read by naming them on the
     command line, with `--any-document` for a candidate document that is by
     construction not one of the shipped bytes. With no argument the committed
     `results/matrix.json` is read through the shipped-hash partition, which is
     what reproduces G0's own figure.

No capture is taken and nothing outside this directory is written (X2, X5).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent

# G0's own definitions, imported rather than restated: the partition, the
# quantity, the tier map and the generation prefix are that gate's.
_spec = importlib.util.spec_from_file_location(
    "g0_departure_stat", HERE.parent / "2026-09-20-w30-g0-cut" / "departure-stat.py"
)
assert _spec is not None and _spec.loader is not None
g0 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g0)

CAPTURE, TIER, GENERATION = g0.CAPTURE, g0.TIER, g0.GENERATION


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def rows_of(paths: list[Path], honour_hashes: bool) -> list[dict]:
    hashes = g0.shipped_hashes()
    out: list[dict] = []
    for path in paths:
        for cell in json.loads(path.read_text())["cells"]:
            if not cell["key"]["profileKey"].startswith(GENERATION):
                continue
            if honour_hashes:
                clause = CAPTURE.search(cell["key"]["web"]["capturePath"])
                if clause is None or hashes.get(clause.group(1)) != clause.group(2):
                    continue
            value = g0.departure(cell)
            if value is None:
                continue
            out.append({
                "profile": cell["key"]["profileKey"],
                "tier": TIER.get(cell["tier"], cell["tier"]),
                "set": cell.get("fixtureSet"),
                "scene": cell["key"]["sceneId"],
                "departure": value,
                "source": path.name,
            })
    return out


def block(title: str, rows: list[dict], keep) -> dict[str, dict]:
    print(title)
    print("-" * 100)
    print(f"  {'row set':<12}{'n':>6}{'mean |d|':>12}{'max |d|':>12}   worst cell")
    got: dict[str, dict] = {}
    for tier in ("webgpu", "css", "both"):
        sel = [r for r in rows if keep(r) and (tier == "both" or r["tier"] == tier)]
        if not sel:
            continue
        values = [r["departure"] for r in sel]
        worst = max(sel, key=lambda r: r["departure"])
        got[tier] = {"n": len(sel), "mean": mean(values), "max": max(values),
                     "worst": worst["scene"]}
        print(f"  {tier:<12}{len(sel):>6}{mean(values):>12.5f}{max(values):>12.5f}   "
              f"{worst['scene']} ({worst['tier']})")
    print()
    return got


def main(argv: list[str]) -> int:
    honour = not any(a == "--any-document" for a in argv)
    paths = [Path(a) for a in argv if not a.startswith("--")]
    if not paths:
        paths = [PACKAGE / "results/matrix.json"]
        honour = True
    rows = rows_of(paths, honour)

    print("W30 G3 — B3's departure statistic, on " + ", ".join(p.name for p in paths))
    print("=" * 100)
    print()
    print("  The quantity, the partition and the tier map are W30 G0's")
    print("  (results/2026-09-20-w30-g0-cut/departure-stat.py), imported and not restated.")
    print(f"  {len(rows)} macOS 27 rows carry the axis"
          + ("" if honour else "  [--any-document: the capturePath hash check is off]"))
    print()

    stop = block("THE STOP — calibration + validation, the population B3's 0.00035 was read over",
                 rows, lambda r: r["set"] in ("calibration", "validation"))
    block("Calibration alone — the partition a fit round renders, so a round is comparable "
          "to the committed bed", rows, lambda r: r["set"] == "calibration")
    wide = block("Every non-holdout row, probe included — the same clause on this child's bed",
                 rows, lambda r: r["set"] != "holdout")
    block("Probe (the pitch ladder) alone — no committed macOS 27 row existed before this child",
          rows, lambda r: r["set"] == "probe")
    block("Holdout only — reported, never fitted",
          rows, lambda r: r["set"] == "holdout")

    print("Per profile, calibration + validation")
    print("-" * 100)
    print(f"  {'profile':<62}{'tier':<8}{'n':>5}{'mean |d|':>12}")
    for profile in sorted({r["profile"] for r in rows}):
        for tier in ("webgpu", "css", "both"):
            sel = [r for r in rows if r["profile"] == profile
                   and r["set"] in ("calibration", "validation")
                   and (tier == "both" or r["tier"] == tier)]
            if not sel:
                continue
            print(f"  {profile:<62}{tier:<8}{len(sel):>5}"
                  f"{mean([r['departure'] for r in sel]):>12.5f}")
    print()

    (HERE / "departure-stat.json").write_text(json.dumps({
        "source": [str(p) for p in paths],
        "quantity": "abs(shadow.meanDepartureWeb - shadow.meanDepartureNative)",
        "definedBy": "results/2026-09-20-w30-g0-cut/departure-stat.py",
        "stop": {
            "statistic": "arithmetic mean over the calibration + validation cells of all "
                         "six profiles, the population B3's 0.00035 was read over",
            "tier": "webgpu",
            "value": stop.get("webgpu", {}).get("mean"),
            "n": stop.get("webgpu", {}).get("n"),
        },
        "nonHoldoutIncludingProbe": wide.get("webgpu"),
        "rows": rows,
    }, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
