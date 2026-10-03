#!/usr/bin/env python3.12
"""W44 G2: T1 on the published light 0.25 generation, derived by W44 G1's `cuts/t1.py` arithmetic
(the file part 2's amendment pins), so the owner test's TypeScript port has a referee to agree with.

Reads the current light 0.25 generation `6d18c059eb42` (rows) and `t-bands.json` (the T cells'
bands), and for every T1 cell of the two light 0.25 profiles, WebGPU, every set: native n, web k,
the bar and code from G0's `bar/t1-bar.json`, the fidelity (`t1.classify`; a T cell on T1-fine), and
the change against the reference, which is the same generation (so every cell is `unchanged`).
Writes `t1-derivation.json`, and `missed-27-rows.ts.txt`: the MISSED_27_ROWS entries, one per
named miss, in the owner test's key and value shape.

    python3.12 -B derive.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
sys.path.insert(0, str(CAL / "results" / "2026-10-03-w44-g1-refit" / "cuts"))
import bed as B  # noqa: E402
import t1  # noqa: E402

GENERATION = "6d18c059eb42"
METRIC = {"F": "t1InteriorStdDev", "C": "t1InteriorStdDev", "P": "t1InteriorStdDev", "T": "t1FineStdDev"}


def main() -> int:
    rows = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r
            for r in B.load_published(GENERATION).rows}
    bands = {(e["profile"], e["renderer"], e["scene"]): e
             for e in json.loads((HERE / "t-bands.json").read_text())["entries"]}
    bars = t1.load_bars()
    held = B.referee_plan.referee_cells(B.referee_plan.load_manifest())
    cells, no_row = [], []
    for profile, sid in t1.population(t1.GATED_PROFILES):
        row = rows.get((profile, "webgpu", sid))
        if row is None:
            no_row.append(f"{profile} {sid}")
            continue
        st = t1.stratum(sid)
        entry = bars[(profile, sid)]
        bar, code = entry["bar"], entry["code"]
        mean = B.value(row, "material", "interiorMeanNative")
        assert abs(code - t1.code_step(mean)) < 1e-12
        if st == "T":
            e = bands[(profile, "webgpu", sid)]
            assert e["capturePath"] == row["key"]["web"]["capturePath"]
            n, k = e["bands"]["fine"]["native"], e["bands"]["fine"]["web"]
            ln, lk = e["bands"]["low"]["native"], e["bands"]["low"]["web"]
            low = t1.classify(ln, lk, lk, bar, code)
        else:
            n = B.value(row, "material", "interiorStdDevNative")
            k = B.value(row, "material", "interiorStdDevWeb")
            low = None
        out = t1.classify(n, k, k, bar, code)
        cells.append(dict(profile=profile, scene=sid, set=row["fixtureSet"], stratum=st,
                          partition=t1.partition(profile, sid, held), metric=METRIC[st], native=n, web=k,
                          ratio=k / n, bar=bar, code=code, B=out["B"], fidelity=out["fidelity"],
                          change=out["change"], lowChange=None if low is None else low["change"]))
    misses = [c for c in cells if c["fidelity"] == "miss"]
    counts = Counter((c["profile"], c["stratum"], c["fidelity"]) for c in cells)
    lines = []
    for c in sorted(misses, key=lambda c: (c["profile"], c["metric"], c["set"], c["scene"])):
        key = f"texture / {c['set']} / {c['scene']} / {c['profile']} :: {c['metric']}"
        lines.append(f'  "{key}": {{ measured: {c["ratio"]:.5f}, bound: "|Δ| ≤ {c["B"]:.5f} or 10 %", '
                     f'native: {c["native"]:.5f} }},')
    (HERE / "missed-27-rows.ts.txt").write_text("\n".join(lines) + "\n")
    (HERE / "t1-derivation.json").write_text(json.dumps(dict(
        what="W44 G2: T1 on the published light 0.25 generation 6d18c059eb42, WebGPU, every set, by G1's t1.py",
        generation=GENERATION, cells=cells, noRow=no_row,
        counts={f"{p} {s} {f}": n for (p, s, f), n in sorted(counts.items())}), indent=1) + "\n")
    for p in t1.GATED_PROFILES:
        print(p, {s: (counts[(p, s, 'miss')], counts[(p, s, 'miss')] + counts[(p, s, 'within')]) for s in "FTCP"})
    print(len(cells), "cells,", len(misses), "misses,", len(no_row), "no row;",
          Counter(c["change"] for c in cells), Counter(c["partition"] for c in misses))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
