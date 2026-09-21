#!/usr/bin/env python3
"""W32 G2 — M2's per-wave move and the cumulative drift beside it (Decision Log 4; §5.169 §3).

    python3 m2-rebaseline.py > m2-rebaseline.txt

Decision Log 4 re-points M2's reference at the generation the adopting gate read
and asks the ledger to carry **the per-wave move of every gated cell against the
previous reference, with the cumulative-from-W31-pre-fit column beside it, so the
drift stays readable while the bound reads one wave's change**. This file is that
table. It gates nothing: `adopted-thresholds.test.ts` reads `chroma-cut.json` and
re-derives every figure in it from the matrix, and this is a record beside it.

Three generations of the same 26 cells, each resolved through
`results/superseded/index.json` by the ACTIVE document it was read at, never by a
path typed here:

  * **W31 pre-fit** — `d0c389d70456` (light) / `880ab1e31450` (dark), the macOS 27
    bed before any chroma retention was fitted into it. W31 G4's reference.
  * **W32's reference** — `49490eb9ff7a` (light) / `b5714a866288` (dark), the rows
    W32 G1's read superseded. This gate's reference under Decision Log 4.
  * **the working file** — `results/matrix.json`, read at the shipped documents.

The per-wave column is what M2 now bounds at 2 %. The cumulative column is not
bounded by anything and is here so a slow walk would be visible: that is the cost
the ruling names in its own words.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent

PROFILES = {
    "apple-macos-27.0-1x-light-standard-glass0.5": "light",
    "apple-macos-27.0-2x-light-standard-glass0.5": "light",
    "apple-macos-27.0-1x-dark-standard-glass0.5": "dark",
    "apple-macos-27.0-2x-dark-standard-glass0.5": "dark",
}

GENERATIONS = {
    "w31-pre-fit": {"light": "d0c389d70456", "dark": "880ab1e31450"},
    "w32-reference": {"light": "49490eb9ff7a", "dark": "b5714a866288"},
}


def interior_std_dev(cells: list[dict], document: str) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    for cell in cells:
        profile = cell["key"]["profileKey"]
        if profile not in PROFILES:
            continue
        if cell["key"]["web"]["renderer"] != "webgpu":
            continue
        if cell.get("fixtureSet") not in ("calibration", "validation"):
            continue
        scene = cell["key"]["sceneId"]
        if not scene.startswith("photo__") or "-tint-" in scene:
            continue
        if document and f"sha256:{document}" not in cell["key"]["web"]["capturePath"]:
            continue
        entry = (cell.get("material") or {}).get("interiorStdDevWeb")
        if isinstance(entry, dict):
            out[(profile, scene)] = entry["value"]
    return out


def main() -> int:
    index = json.loads((PACKAGE / "results" / "superseded" / "index.json").read_text())
    generations: dict[str, dict[tuple[str, str], float]] = {}
    for name, documents in GENERATIONS.items():
        merged: dict[tuple[str, str], float] = {}
        for _scheme, document in documents.items():
            named = index["byDocumentSha256"].get(document)
            if named is None:
                raise SystemExit(f"m2-rebaseline: {document} is in no superseded file")
            cells = json.loads(
                (PACKAGE / "results" / "superseded" / named).read_text()
            )["cells"]
            merged.update(interior_std_dev(cells, document))
        generations[name] = merged

    now = interior_std_dev(
        json.loads((PACKAGE / "results" / "matrix.json").read_text())["cells"], ""
    )
    cut = json.loads((HERE / "chroma-cut.json").read_text())

    print("W32 G2 — M2's reference re-baselined: the per-wave move and the drift beside it")
    print("=" * 108)
    print("  Decision Log 4, ruled by the user 2026-09-22. `interiorStdDevWeb` on the 26 gated")
    print("  cells, at three generations. The per-wave column is what M2 bounds at 2 %; the")
    print("  cumulative column is bounded by nothing and is what would show a slow walk.")
    print()
    print(f"  {'profile':<46}{'scene':<32}{'pre-fit':>11}{'W32 ref':>11}"
          f"{'now':>11}{'per wave':>11}{'cumulative':>12}")
    worst_wave = ("", 0.0)
    worst_cumulative = ("", 0.0)
    for cell in sorted(cut["cells"], key=lambda c: (c["profile"], c["scene"])):
        key = (cell["profile"], cell["scene"])
        pre = generations["w31-pre-fit"][key]
        ref = generations["w32-reference"][key]
        value = now[key]
        if abs(ref - cell["interiorStdDevWebReference"]) > 1e-12:
            raise SystemExit(f"m2-rebaseline: {key} disagrees with the cut's reference")
        wave = (value - ref) / ref
        cumulative = (value - pre) / pre
        if abs(wave) > abs(worst_wave[1]):
            worst_wave = (f"{cell['profile']} {cell['scene']}", wave)
        if abs(cumulative) > abs(worst_cumulative[1]):
            worst_cumulative = (f"{cell['profile']} {cell['scene']}", cumulative)
        print(f"  {cell['profile']:<46}{cell['scene']:<32}{pre:>11.7f}{ref:>11.7f}"
              f"{value:>11.7f}{wave * 100:>10.3f}%{cumulative * 100:>11.3f}%")
    print()
    print(f"  worst per-wave     {worst_wave[1] * 100:>8.3f}%   {worst_wave[0]}")
    print(f"  worst cumulative   {worst_cumulative[1] * 100:>8.3f}%   {worst_cumulative[0]}")
    print(f"  M2's bound          {2.0:>8.3f}%   on the per-wave column alone")
    print()
    print("  The cell W32 G1 recorded MISSED — photo__rrect-sm__inactive on 1x light — reads")
    print("  2.775 % cumulative and is the worst cumulative here; against this gate's own")
    print("  reference it reads the per-wave figure in its row, which is what retires the")
    print("  entry. The 2.775 % is kept in the record and is not rewritten.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
