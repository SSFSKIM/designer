#!/usr/bin/env python3.12
"""W46 G2: T1 on the published DARK 0.25 generation `d0219cd684bf`, derived by W44 G1's `cuts/t1.py`
arithmetic (shared by path and pinned, `bindings.SHARED`), the Python referee the owner test's
TypeScript port agrees with (W44 G2's `t1/derive.py`, ported for the dark profiles; claims §5.210).

For every T1 cell of the two dark 0.25 profiles, WebGPU, every set (holdout and referees included,
labelled by W46's manifest, never selected): native n, web k, the bar and code from W44 G0's
`bar/t1-bar.json`, the fidelity (`t1.classify`; a T cell on T1-fine, from `t-bands-d0219cd684bf.json`)
and the change against the reference, which is the same generation, so every cell is `unchanged`.
Writes `t1-derivation.json` and `missed-27-rows.ts.txt`: the MISSED_27_ROWS entries in the owner
test's key and value shape.

    python3.12 -B derive.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
sys.path.insert(0, str(RESULTS / "2026-10-05-w46-g0-declaration"))
import bindings as W  # noqa: E402

B, T1, _ = W.load_cuts()
GENERATION = "d0219cd684bf"
METRIC = {"F": "t1InteriorStdDev", "C": "t1InteriorStdDev", "P": "t1InteriorStdDev", "T": "t1FineStdDev"}


def main() -> int:
    rows = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r
            for r in B.load_published(GENERATION).rows}
    bands = {(e["profile"], e["renderer"], e["scene"]): e
             for e in json.loads((HERE / f"t-bands-{GENERATION}.json").read_text())["entries"]}
    bars = T1.load_bars()
    plan = W.referee_plan()
    held = plan.referee_cells(plan.load_manifest())
    cells, no_row = [], []
    for profile, sid in T1.population(list(W.DARK_025)):
        row = rows.get((profile, "webgpu", sid))
        if row is None:
            no_row.append(f"{profile} {sid}")
            continue
        st = T1.stratum(sid)
        entry = bars[(profile, sid)]
        bar, code = entry["bar"], entry["code"]
        assert abs(code - T1.code_step(B.value(row, "material", "interiorMeanNative"))) < 1e-12
        if st == "T":
            e = bands[(profile, "webgpu", sid)]
            assert e["capturePath"] == row["key"]["web"]["capturePath"]
            n, k = e["bands"]["fine"]["native"], e["bands"]["fine"]["web"]
            ln, lk = e["bands"]["low"]["native"], e["bands"]["low"]["web"]
            low = T1.classify(ln, lk, lk, bar, code)
        else:
            n = B.value(row, "material", "interiorStdDevNative")
            k = B.value(row, "material", "interiorStdDevWeb")
            low = None
        out = T1.classify(n, k, k, bar, code)
        cells.append(dict(profile=profile, scene=sid, set=row["fixtureSet"], stratum=st,
                          partition=T1.partition(profile, sid, held), metric=METRIC[st], native=n, web=k,
                          ratio=None if n == 0 else k / n, bar=bar, code=code, B=out["B"], fidelity=out["fidelity"],
                          change=out["change"], lowChange=None if low is None else low["change"]))
    misses = [c for c in cells if c["fidelity"] == "miss"]
    counts = Counter((c["profile"], c["stratum"], c["fidelity"]) for c in cells)
    lines = []
    for c in sorted(misses, key=lambda c: (c["profile"], c["metric"], c["set"], c["scene"])):
        key = f"texture / {c['set']} / {c['scene']} / {c['profile']} :: {c['metric']}"
        # A native SD of exactly 0 (2x `impulse__capsule-button__inactive`, whose L1 mask is the uniform
        # dot) has no finite ratio: the owner test's web / native reads Infinity, recorded as such.
        ratio = "Infinity" if c["ratio"] is None else f"{c['ratio']:.5f}"
        lines.append(f'  "{key}": {{ measured: {ratio}, bound: "|Δ| ≤ {c["B"]:.5f} or 10 %", '
                     f'native: {c["native"]:.5f} }},')
    (HERE / "missed-27-rows.ts.txt").write_text("\n".join(lines) + "\n")
    (HERE / "t1-derivation.json").write_text(json.dumps(dict(
        what=f"W46 G2: T1 on the published dark 0.25 generation {GENERATION}, WebGPU, every set, by W44 G1's t1.py",
        generation=GENERATION, cells=cells, noRow=no_row,
        counts={f"{p} {s} {f}": n for (p, s, f), n in sorted(counts.items())}), indent=1) + "\n")
    for p in W.DARK_025:
        print(p, {s: (counts[(p, s, 'miss')], counts[(p, s, 'miss')] + counts[(p, s, 'within')]) for s in "FTCP"})
    nonheld = [c for c in cells if c["partition"] == "gate"]
    print(len(cells), "cells,", len(misses), "misses,", len(no_row), "no row;", Counter(c["change"] for c in cells),
          "partition of misses", Counter(c["partition"] for c in misses),
          "| non-holdout (gate + referee):", sum(1 for c in misses if c["partition"] != "holdout"), "of",
          sum(1 for c in cells if c["partition"] != "holdout"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
