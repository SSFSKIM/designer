#!/usr/bin/env python3
"""W30 G0, review closure — B3's stop condition, computed rather than quoted.

    python3 departure-stat.py > departure-stat.txt

B3 was declared as "the departure residual held at or better than 0.0007
bed-wide, mean absolute, on non-holdout cells of every profile" (claims §5.156
§5), with 0.0007 taken from §5.154 §3's "0.00681 → 0.00074 on the light standard
bed". The review found that the statistic as written is already exceeded today,
because §5.154 §3's figure was read on G3's SCRATCH matrices, over one bed,
during a fit — and is not reproducible from the committed matrix under any
partition of it. Decision Log 3 (a) restated the stop on the tier and partition
it is actually read on, and this script is what G3 and G4 re-run to read it.

**The quantity.** Per cell, `|shadow.meanDepartureWeb − shadow.meanDepartureNative|`
— the shadow axis's own mean of `backdrop − rendered` over the whole exterior of
the declared region, in linear light, which is the objective §5.154 §3 refitted
the anchors against. The statistic is its arithmetic mean over a row set.

**The partition.** `adopted-thresholds.test.ts`'s `atAShippedDocument`,
reproduced on the same rule as `structure-cut.py` reproduces it — the
`capturePath` names a profile document and a 12-hex content hash, and the row
counts only if that hash is the hash of the file on disk — restricted to the
macOS 27 generation, minus every row whose `fixtureSet` is `holdout` (X4, X5).
No capture is taken and nothing is written outside this directory (X2, X5).

**Why the tier is named in the stop and not left implicit.** The two tiers read
the same axis on the same cells and disagree by a factor of nearly four. The
shadow is the WebGPU tier's to fit — the CSS tier emits one `box-shadow` per
surface derived from the same profile — so the stop is the WebGPU tier's number
and the CSS tier's is recorded beside it, per the tier rule (Decision Log 23 of
2026-09-05). Both are printed here, per profile and pooled, so the restatement
is checkable and so that a later read can say which half moved.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent

MATRIX = PACKAGE / "results/matrix.json"
PROFILES = PACKAGE / "profiles"

CAPTURE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")

TIER = {"texture": "webgpu", "dom": "css"}
GENERATION = "apple-macos-27.0-"


def shipped_hashes() -> dict[str, str]:
    return {
        f"packages/calibration/profiles/{p.name}":
            hashlib.sha256(p.read_bytes()).hexdigest()[:12]
        for p in sorted(PROFILES.glob("*.json"))
    }


def departure(cell: dict) -> float | None:
    shadow = cell.get("shadow") or {}
    web = shadow.get("meanDepartureWeb")
    native = shadow.get("meanDepartureNative")
    if not isinstance(web, dict) or not isinstance(native, dict):
        return None
    return abs(web["value"] - native["value"])


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def main() -> int:
    hashes = shipped_hashes()
    rows = []
    for cell in json.loads(MATRIX.read_text())["cells"]:
        clause = CAPTURE.search(cell["key"]["web"]["capturePath"])
        if clause is None or hashes.get(clause.group(1)) != clause.group(2):
            continue
        if not cell["key"]["profileKey"].startswith(GENERATION):
            continue
        value = departure(cell)
        if value is None:
            continue
        rows.append({
            "profile": cell["key"]["profileKey"],
            "tier": TIER.get(cell["tier"], cell["tier"]),
            "set": cell.get("fixtureSet"),
            "scene": cell["key"]["sceneId"],
            "departure": value,
        })

    print("W30 G0 review closure — B3's departure statistic, as Decision Log 3 (a) restates it")
    print("=" * 100)
    print()
    print("  |meanDepartureWeb - meanDepartureNative|, arithmetic mean, over the macOS 27")
    print("  generation of results/matrix.json at the shipped documents (atAShippedDocument),")
    print(f"  {len(rows)} rows in all. The stop is the WEBGPU line of the 'all six' block.")
    print()

    def block(title: str, keep) -> None:
        print(title)
        print("-" * 100)
        print(f"  {'row set':<12}{'n':>6}{'mean |Δ|':>12}{'max |Δ|':>12}   worst cell")
        for tier in ("webgpu", "css", "both"):
            sel = [r for r in rows if keep(r) and (tier == "both" or r["tier"] == tier)]
            if not sel:
                continue
            values = [r["departure"] for r in sel]
            worst = max(sel, key=lambda r: r["departure"])
            print(f"  {tier:<12}{len(sel):>6}{mean(values):>12.5f}{max(values):>12.5f}   "
                  f"{worst['scene']} ({worst['tier']})")
        print()

    block("All six declared profiles, NON-HOLDOUT — the stop condition",
          lambda r: r["set"] != "holdout")
    block("All six declared profiles, holdout only — reported, never fitted",
          lambda r: r["set"] == "holdout")

    print("Per profile, non-holdout")
    print("-" * 100)
    print(f"  {'profile':<62}{'tier':<8}{'n':>5}{'mean |Δ|':>12}")
    for profile in sorted({r["profile"] for r in rows}):
        for tier in ("webgpu", "css", "both"):
            sel = [r for r in rows if r["profile"] == profile and r["set"] != "holdout"
                   and (tier == "both" or r["tier"] == tier)]
            if not sel:
                continue
            print(f"  {profile:<62}{tier:<8}{len(sel):>5}"
                  f"{mean([r['departure'] for r in sel]):>12.5f}")
    print()

    print("The two light standard beds pooled, non-holdout — the bed §5.154 §3 names")
    print("-" * 100)
    for tier in ("webgpu", "css", "both"):
        sel = [r for r in rows if "light-standard" in r["profile"] and r["set"] != "holdout"
               and (tier == "both" or r["tier"] == tier)]
        print(f"  {tier:<12}{len(sel):>5}{mean([r['departure'] for r in sel]):>12.5f}")
    print()

    print("§5.154 §3's 0.00074 is not reproducible from the committed matrix")
    print("-" * 100)
    print("  Every partition of the 1x-light-standard bed this file can express, so that the")
    print("  correction beside §5.154 §3 says what was checked rather than that it was checked:")
    print()
    one = [r for r in rows if r["profile"] == f"{GENERATION}1x-light-standard-glass0.5"]
    partitions = (
        ("all rows", lambda r: True),
        ("non-holdout", lambda r: r["set"] != "holdout"),
        ("calibration", lambda r: r["set"] == "calibration"),
        ("validation", lambda r: r["set"] == "validation"),
        ("holdout", lambda r: r["set"] == "holdout"),
        ("active only", lambda r: not r["scene"].endswith("__inactive")),
        ("non-holdout active", lambda r: r["set"] != "holdout"
         and not r["scene"].endswith("__inactive")),
        ("calibration active", lambda r: r["set"] == "calibration"
         and not r["scene"].endswith("__inactive")),
    )
    print(f"  {'partition':<22}{'webgpu':>20}{'css':>20}{'both':>20}")
    for name, keep in partitions:
        line = f"  {name:<22}"
        for tier in ("webgpu", "css", "both"):
            sel = [r for r in one if keep(r) and (tier == "both" or r["tier"] == tier)]
            cell = (f"{mean([r['departure'] for r in sel]):.5f} (n {len(sel)})" if sel else "—")
            line += f"{cell:>20}"
        print(line)
    print()
    print("  None of them is 0.00074. That figure is the fit's own residual on G3's scratch")
    print("  matrices at the moment it was chosen; the committed bed is a different read.")

    (HERE / "departure-stat.json").write_text(json.dumps({
        "source": "results/matrix.json at atAShippedDocument, macOS 27 generation",
        "quantity": "abs(shadow.meanDepartureWeb - shadow.meanDepartureNative)",
        "stop": {
            "statistic": "arithmetic mean over the non-holdout cells of all six profiles",
            "tier": "webgpu",
            "today": mean([r["departure"] for r in rows
                           if r["set"] != "holdout" and r["tier"] == "webgpu"]),
            "n": sum(1 for r in rows if r["set"] != "holdout" and r["tier"] == "webgpu"),
        },
        "rows": rows,
    }, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
