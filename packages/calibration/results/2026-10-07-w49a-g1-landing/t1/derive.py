#!/usr/bin/env python3.12
"""X59 (ii)/(iii): witness W49a against b2d074 AND d0219 before editing the authorised list.

Uses the same W44 arithmetic and W45 growth-only partition as W48. Reports every comparison
against both references and separately the explicit DL2/DL9 per-cell reference partition.
Writes dark MISSED_27_ROWS entries independently of the reference selection. Refuses an incomplete
stage, absent bands, duplicate captures or output overwrite. This reads recorded pixels only.

  python3.12 -B derive.py --stage STAGE
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w49_inputs as I

C = I.cuts()
B, T1, RULE = C.B, C.T1, C.RULE
FIXTURES = {
    I.GENERATION: (HERE / f"t-bands-{I.GENERATION}.json", I.PAIR),
    "b2d074d2df24": (I.RESULTS / "2026-10-06-w48-g2-landing/t1/t-bands-b2d074d2df24.json",
                       I.REFERENCES["b2d074d2df24"]),
    "d0219cd684bf": (I.RESULTS / "2026-10-05-w46-g2-landing/t1/t-bands-d0219cd684bf.json",
                       I.REFERENCES["d0219cd684bf"]),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=Path, required=True)
    args = ap.parse_args()
    outputs = [HERE / n for n in ("t1-derivation.json", "witness-iii.txt", "missed-27-rows.ts.txt")]
    if any(p.exists() for p in outputs):
        raise SystemExit("derivation output exists; evidence is written once")
    rows = {I.row_key(r): r for r in I.stage_rows(args.stage)}
    references = {g: {I.row_key(r): r for r in I.published(g, pair)} for g, pair in I.REFERENCES.items()}
    bands = {}
    for path, pair in FIXTURES.values():
        found = I.band_fixture(path, pair)
        if bands.keys() & found.keys():
            raise ValueError("two fixtures name the same capture")
        bands.update(found)
    bars = T1.load_bars()
    cells = []
    for profile, sid in T1.population(B.W.DARK_025):
        key = profile, "webgpu", sid
        row = rows[key]
        st = T1.stratum(sid)
        bar, code = bars[(profile, sid)]["bar"], bars[(profile, sid)]["code"]
        if abs(code - T1.code_step(B.value(row, "material", "interiorMeanNative"))) >= 1e-12:
            raise ValueError(f"{key}: native mean disagrees with declared code step")
        n = B.value(row, "material", "interiorStdDevNative")
        k = B.value(row, "material", "interiorStdDevWeb")
        low_n, low_k = n, k
        if st == "T":
            here = bands[(*key, row["key"]["web"]["capturePath"])]["bands"]
            n, k = here["fine"]["native"], here["fine"]["web"]
            low_n, low_k = here["low"]["native"], here["low"]["web"]
        fidelity = T1.classify(n, n, k, bar, code)
        comparisons = {}
        for g, ref_rows in references.items():
            ref = ref_rows[key]
            if st == "T":
                there = bands[(*key, ref["key"]["web"]["capturePath"])]["bands"]
                if there["fine"]["native"] != n or there["low"]["native"] != low_n:
                    raise ValueError(f"{key}: native band changed between generations")
                c = there["low"]["web"]
            else:
                if B.value(ref, "material", "interiorStdDevNative") != n:
                    raise ValueError(f"{key}: native SD changed between generations")
                c = B.value(ref, "material", "interiorStdDevWeb")
            reading = T1.classify(low_n, c, low_k, bar, code)
            comparisons[g] = dict(native=low_n, reference=c, web=low_k, w44=reading["change"],
                                  growthOnly=RULE.growth_change(low_n, c, low_k, bar),
                                  growth=reading["growth"], growthInB=reading["growth"] / reading["B"])
        cells.append(dict(profile=profile, scene=sid, set=row["fixtureSet"], stratum=st,
                          partition=T1.partition(profile, sid, C.REFEREES),
                          metric="t1FineStdDev" if st == "T" else "t1InteriorStdDev",
                          native=n, web=k, ratio=None if n == 0 else k / n,
                          bar=bar, code=code, B=fidelity["B"], fidelity=fidelity["fidelity"],
                          selectedReference=I.selected_reference(profile, sid), comparisons=comparisons))
    if len(cells) != 154:
        raise ValueError(f"expected 154 dark T1 cells, found {len(cells)}")
    witness = [f"W49a X59 (iii): {I.GENERATION}, both historical references and DL2/DL9's per-cell selection.",
               "All three band fixtures present; no authorisation suppresses a failure in this witness.", ""]
    summary = {}
    for profile in B.W.DARK_025:
        for reference in (*I.REFERENCES, "selected"):
            for form in ("w44", "growthOnly"):
                tripped = []
                for cell in cells:
                    if cell["profile"] != profile:
                        continue
                    g = cell["selectedReference"] if reference == "selected" else reference
                    r = cell["comparisons"][g]
                    if r[form] == "away" and r["growthInB"] > 1:
                        tripped.append(dict(scene=cell["scene"], reference=g, growthInB=r["growthInB"]))
                summary[f"{profile} {reference} {form}"] = tripped
                witness.append(f"{profile} against {reference}, {form}: {len(tripped)} beyond B")
                witness += [f"  {c['scene']:<48} {c['reference']} {c['growthInB']:.8f} B" for c in tripped]
    misses = sorted((c for c in cells if c["fidelity"] == "miss"),
                    key=lambda c: (c["profile"], c["metric"], c["set"], c["scene"]))
    lines = []
    for c in misses:
        key = f"texture / {c['set']} / {c['scene']} / {c['profile']} :: {c['metric']}"
        ratio = "Infinity" if c["ratio"] is None else f"{c['ratio']:.5f}"
        lines.append(f'  "{key}": {{ measured: {ratio}, bound: "|Δ| ≤ {c["B"]:.5f} or 10 %", '
                     f'native: {c["native"]:.5f} }},')
    body = dict(generation=I.GENERATION, pair=I.PAIR, references=I.REFERENCES,
                fixtures={g: str(p.relative_to(I.CAL)) for g, (p, _) in FIXTURES.items()},
                cells=cells, witness=summary,
                counts=dict(Counter(f"{c['profile']} {c['stratum']} {c['fidelity']}" for c in cells)))
    for path, text in zip(outputs, (json.dumps(body, indent=1) + "\n", "\n".join(witness) + "\n",
                                    "\n".join(lines) + "\n")):
        with path.open("x") as f:
            f.write(text)
    print("\n".join(witness))
    print(f"{len(cells)} cells, {len(misses)} misses")


if __name__ == "__main__":
    main()
