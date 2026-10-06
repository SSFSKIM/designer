#!/usr/bin/env python3.12
"""W48 G2: T1 on the published DARK 0.25 generation `b2d074d2df24`, derived against the superseded
`d0219cd684bf` by W44 G1's `cuts/t1.py` arithmetic and W45's growth-only partition (W47's `cuts/rule.py`,
W45's rule bound to the dark profiles, inherited by path under W48's bindings), so the owner test's
TypeScript port has a referee to agree with at the landing (charter clause 10's five parts, X59; claims
§5.214). W45 G2's `derive.py` (`results/2026-10-03-w45-g2-landing/t1/derive.py`), ported for the dark
profiles; W46 G2's dark `derive.py` is its generation's and stays as it is.

Reads the two generations' rows through W47's `bed.load_published` (each file checked against
`generations/index.json`) and the T cells' two bands from BOTH dark fixtures, each keyed by its
generation and capture path, as the owner test reads them: the new generation's
(`t-bands-b2d074d2df24.json`, beside this file) and the reference's
(`2026-10-05-w46-g2-landing/t1/t-bands-d0219cd684bf.json`). For every T1 cell of the two dark 0.25
profiles, WebGPU, every set (W46's referees labelled by `w46-referees-1`, never selected):
  - fidelity on the new generation (a T cell on T1-fine), the `MISSED_27_ROWS` derivation;
  - change against `d0219cd684bf` on both forms: W44's classifier and the growth-only partition (a T
    cell's on T1-low), with g / B.

Writes, never over an existing file:
  t1-derivation.json      every cell's inputs and outputs, and the counts per profile and stratum
  missed-27-rows.ts.txt   the MISSED_27_ROWS dark T1 entries at the new generation, in the owner's shape
  witness-iii.txt         part (iii): clause (b) on both forms against d0219cd684bf with the dark list
                          empty, the growth-only count and ceiling, and every regression by name

    python3.12 -B derive.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
sys.path.insert(0, str(CAL / "results" / "2026-10-06-w48-g0-declaration"))
import inherit  # noqa: E402

C = inherit.tool("cuts/cuts.py")
B, t1, rule = C.B, C.T1, C.RULE

GENERATION = "b2d074d2df24"
REFERENCE = "d0219cd684bf"
FIXTURES = {GENERATION: HERE / "t-bands-b2d074d2df24.json",
            REFERENCE: CAL / "results" / "2026-10-05-w46-g2-landing" / "t1" / "t-bands-d0219cd684bf.json"}
PROFILES = list(B.W.DARK_025)
METRIC = {"F": "t1InteriorStdDev", "C": "t1InteriorStdDev", "P": "t1InteriorStdDev", "T": "t1FineStdDev"}
CEILING_B = rule.BUDGET_CEILING_B


def rows_of(generation: str) -> dict:
    return {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r
            for r in B.load_published(generation).rows}


def bands_of() -> dict:
    """(profile, renderer, scene, capturePath) -> entry, over both fixtures; each fixture must name
    its own generation, and no key may come from two."""
    out = {}
    for generation, path in FIXTURES.items():
        body = json.loads(path.read_text())
        if body["generation"] != generation:
            raise SystemExit(f"{path}: names generation {body['generation']}, not {generation}")
        for e in body["entries"]:
            key = (e["profile"], e["renderer"], e["scene"], e["capturePath"])
            if key in out or f"sha256:{generation}" not in e["capturePath"]:
                raise SystemExit(f"{path}: {e['scene']} is duplicated or names another generation")
            out[key] = e
    return out


def main() -> int:
    outputs = [HERE / n for n in ("t1-derivation.json", "missed-27-rows.ts.txt", "witness-iii.txt")]
    for path in outputs:
        if path.exists():
            raise SystemExit(f"{path} exists; the derivation is written once")
    rows, ref_rows, bands = rows_of(GENERATION), rows_of(REFERENCE), bands_of()
    bars = t1.load_bars()
    held = C.REFEREES
    cells, no_row = [], []
    for profile, sid in t1.population(PROFILES):
        key = (profile, "webgpu", sid)
        row, ref = rows.get(key), ref_rows.get(key)
        if row is None or ref is None:
            no_row.append(f"{profile} {sid}")
            continue
        st = t1.stratum(sid)
        entry = bars[(profile, sid)]
        bar, code = entry["bar"], entry["code"]
        assert abs(code - t1.code_step(B.value(row, "material", "interiorMeanNative"))) < 1e-12
        if st == "T":
            here = bands[(profile, "webgpu", sid, row["key"]["web"]["capturePath"])]
            there = bands[(profile, "webgpu", sid, ref["key"]["web"]["capturePath"])]
            n, k, c = here["bands"]["fine"]["native"], here["bands"]["fine"]["web"], there["bands"]["fine"]["web"]
            ln, lk, lc = here["bands"]["low"]["native"], here["bands"]["low"]["web"], there["bands"]["low"]["web"]
        else:
            n = B.value(row, "material", "interiorStdDevNative")
            k = B.value(row, "material", "interiorStdDevWeb")
            c = B.value(ref, "material", "interiorStdDevWeb")
            assert n == B.value(ref, "material", "interiorStdDevNative")
            ln, lk, lc = n, k, c
        fidelity = t1.classify(n, c, k, bar, code)
        regression = t1.classify(ln, lc, lk, bar, code)
        growth = rule.growth_change(ln, lc, lk, bar)
        cells.append(dict(
            profile=profile, scene=sid, set=row["fixtureSet"], stratum=st,
            partition=t1.partition(profile, sid, held), metric=METRIC[st], native=n, web=k, reference=c,
            ratio=None if n == 0 else k / n, bar=bar, code=code, B=fidelity["B"], fidelity=fidelity["fidelity"],
            change=fidelity["change"], regression=dict(native=ln, reference=lc, web=lk,
                                                       w44=regression["change"], growthOnly=growth,
                                                       growth=regression["growth"],
                                                       growthInB=regression["growth"] / regression["B"])))
    misses = [c for c in cells if c["fidelity"] == "miss"]
    counts = Counter((c["profile"], c["stratum"], c["fidelity"]) for c in cells)
    lines = []
    for c in sorted(misses, key=lambda c: (c["profile"], c["metric"], c["set"], c["scene"])):
        key = f"texture / {c['set']} / {c['scene']} / {c['profile']} :: {c['metric']}"
        # A native SD of exactly 0 (2x `impulse__capsule-button__inactive`, whose mask is the uniform dot) has
        # no finite ratio: the owner test's web / native reads Infinity, recorded as such (W46 G2).
        ratio = "Infinity" if c["ratio"] is None else f"{c['ratio']:.5f}"
        lines.append(f'  "{key}": {{ measured: {ratio}, bound: "|Δ| ≤ {c["B"]:.5f} or 10 %", '
                     f'native: {c["native"]:.5f} }},')
    (HERE / "missed-27-rows.ts.txt").write_text("\n".join(lines) + "\n")

    def trips(c, form):
        r = c["regression"]
        return r["growthInB"] > 1 and (r["w44"] == "away" if form == "w44" else r["growthOnly"] == "away")

    witness = ["W48 G2 part (iii): T1 clause (b) against the superseded dark reference d0219cd684bf /",
               "f0b36a71772a on the published dark generation b2d074d2df24 / 29da6a888a23, with BOTH dark band",
               "fixtures present and T1_DARK_AUTHORISED_REGRESSIONS empty (claims §5.214; X59). A T cell's",
               "regression reads T1-low. g / B is error growth over B = max(1 code, 2 bar).", ""]
    summary = {}
    for profile in PROFILES:
        here = [c for c in cells if c["profile"] == profile]
        for form in ("w44", "growth"):
            tripped = sorted((c for c in here if trips(c, form)), key=lambda c: -c["regression"]["growthInB"])
            beyond = [c for c in tripped if c["regression"]["growthInB"] > CEILING_B]
            summary[f"{profile} {form}"] = dict(count=len(tripped), beyondCeiling=len(beyond),
                                                cells=[(c["scene"], round(c["regression"]["growthInB"], 4))
                                                       for c in tripped])
            witness.append(f"{profile}, {'W44 form' if form == 'w44' else 'growth-only'}: "
                           f"{len(tripped)} away beyond B, {len(beyond)} beyond {CEILING_B:g} B")
            for c in tripped:
                r = c["regression"]
                witness.append(f"  {c['scene']:<46} {c['partition']:<8} n {r['native']:.4f} d0219 {r['reference']:.4f} "
                               f"W48 {r['web']:.4f}  g {r['growthInB']:.4f} B ({r['w44']} / {r['growthOnly']})")
        partition = Counter(c["regression"]["growthOnly"] for c in here)
        w44 = Counter(c["regression"]["w44"] for c in here)
        witness.append(f"  partition: W44 {dict(sorted(w44.items()))}; growth-only {dict(sorted(partition.items()))}")
        witness.append("")
    (HERE / "witness-iii.txt").write_text("\n".join(witness) + "\n")
    (HERE / "t1-derivation.json").write_text(json.dumps(dict(
        what="W48 G2: T1 on the published dark 0.25 generation b2d074d2df24 against d0219cd684bf, "
             "WebGPU, every set, by W44 G1's t1.py and W45's growth-only partition (W47's rule.py)",
        generation=GENERATION, reference=REFERENCE,
        fixtures={g: str(p.relative_to(CAL)) for g, p in FIXTURES.items()},
        cells=cells, noRow=no_row, witness=summary,
        counts={f"{p} {s} {f}": n for (p, s, f), n in sorted(counts.items())}), indent=1) + "\n")
    for p in PROFILES:
        print(p, {s: (counts[(p, s, 'miss')], counts[(p, s, 'miss')] + counts[(p, s, 'within')]) for s in "FTCP"})
    print(len(cells), "cells,", len(misses), "misses,", len(no_row), "no row")
    print("\n".join(witness))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
