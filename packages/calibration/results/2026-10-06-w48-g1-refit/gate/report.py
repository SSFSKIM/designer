#!/usr/bin/env python3.12
"""W48 G1 step 6: the GATE REPORT's tables, read off the strict-mode stage's cut (`cuts/cut.py`). Reads only;
re-derives no verdict: the hashed rule's verdict, groups and budget are W47's `cuts/rule.py` as `cuts.py`
recorded them; every other row is the cut's own section. W46 G1's `gate/report.py`, ported: the input is
the sealed stage's cut (W48 G1 froze before its gate, the brief's step order and charter clause 7), and
the targets are W48's (Decision Log 5): P pooled with P rest and P inactive beside it, C rest, F inactive,
each halving read per profile; the CSS tier's T1 residual (Decision Log 6) and S1 dark beside.

    python3.12 -B report.py CUT_NAME [--out gate-report]
"""
from __future__ import annotations

import gzip
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DARK = ("apple-macos-27.0-1x-dark-standard-glass0.25", "apple-macos-27.0-2x-dark-standard-glass0.25")
ROWS = ("M1", "M2", "C1", "L1", "X1", "E2", "S1")


def r4(x):
    return None if x is None else round(x, 4)


def profile_block(p: dict) -> dict:
    g = p["groups"]
    halve = lambda k: None if k not in g else dict(A=r4(g[k]["A"]), ref=r4(g[k]["referenceA"]),  # noqa: E731
                                                   halved=g[k]["A"] <= 0.5 * g[k]["referenceA"], cells=g[k]["cells"])
    return dict(
        verdict=p["verdict"], why=p["why"], read=p["read"],
        hashedTargets={t: None if v is None else dict(A=r4(v["A"]), ref=r4(v["referenceA"]), halved=v["halved"],
                                                       cells=v["cells"]) for t, v in p["targets"].items()},
        beside=dict(**{"P rest": halve("P rest"), "P inactive": halve("P inactive"),
                       "C inactive": halve("C inactive"), "F rest": halve("F rest")}),
        groups={k: dict(A=r4(v["A"]), ref=r4(v["referenceA"]), tau=r4(v["tau"]), bound=r4(v["referenceA"] + v["tau"]),
                        gated=v["gated"], holds=v["holds"], cells=v["cells"]) for k, v in g.items()},
        partition={k: v["total"] for k, v in p["partition"].items()},
        awayBeyondB=[dict(scene=a["scene"], growthInB=round(a["growthInB"], 2)) for a in p["awayBeyondB"]],
        beyondCeiling=[a["scene"] for a in p["awayBeyondCeiling"]], budgetHolds=p["budgetHolds"],
        targetNotWithin={k: len(v) for k, v in p["targetNotWithin"].items()})


def css_residual(t1: dict) -> dict:
    out = {}
    for c in t1["cells"]:
        if c["tier"] != "css" or c["profile"] not in DARK or c["partition"] != "gate":
            continue
        key = f"{c['scale']}x {c['stratum']} {c['pose']}"
        out.setdefault(key, []).append(c)
    return {k: dict(cells=len(v), medianRatio=r4(statistics.median(c["ratio"] for c in v if c["ratio"] is not None)),
                    referenceMedianRatio=r4(statistics.median(c["referenceRatio"] for c in v
                                                              if c["referenceRatio"] is not None)),
                    away=sum(1 for c in v if c["change"] == "away"), toward=sum(1 for c in v if c["change"] == "toward"))
            for k, v in sorted(out.items())}


def rows(cut: dict) -> dict:
    out = {k: v for k, v in cut["summary"].items()}
    l1 = cut["L1"]["webgpu"]
    dark = lambda c: c["cell"].split("/")[0] in DARK  # noqa: E731
    out["L1 webgpu misses"] = [dict(cell=c["cell"], error=r4(c["error"]), growth=r4(c["growth"]))
                               for c in l1["absoluteMisses"] + l1["growthMisses"] if dark(c)]
    out["L1 webgpu max"] = dict(error=r4(l1["maxError"]), growth=r4(l1["maxGrowth"]))
    m2 = cut["M2"]["webgpu"]
    out["M2 webgpu failures"] = m2["failures"]
    out["M2 webgpu misses"] = m2["misses"]
    out["X1 webgpu failing"] = cut["X1"]["webgpu"]["failing"] if isinstance(cut["X1"], dict) else cut["X1"]
    out["E2 webgpu failing"] = cut["E2"]["webgpu"]["failing"] if isinstance(cut["E2"], dict) else cut["E2"]
    out["C1 webgpu"] = cut["C1"]["webgpu"]["perBedSpan"]
    out["S1 per profile median"] = {k: v for k, v in cut["S1"]["webgpu"]["perProfileMedian"].items()}
    return out


def main(argv) -> int:
    name = argv[1]
    out = HERE / (argv[argv.index("--out") + 1] if "--out" in argv else "gate-report")
    reference = json.load(gzip.open(HERE.parent / "references" / "d0219-cuts.json.gz"))
    cut = json.load(gzip.open(HERE.parent / "cuts" / f"{name}.json.gz"))
    report = dict(what="W48 G1 step 6: the gate report on the sealed strict-mode stage (non-withheld cells)",
                  cut=name, reference=dict(rule={p: profile_block(v) for p, v in reference["T1"]["rule"]["profiles"].items()},
                                           cssT1=css_residual(reference["T1"])),
                  rule={p: profile_block(v) for p, v in cut["T1"]["rule"]["profiles"].items()},
                  ruleVerdict=cut["T1"]["rule"]["verdict"], rows=rows(cut), cssT1=css_residual(cut["T1"]))
    Path(f"{out}.json").write_text(json.dumps(report, indent=1) + "\n")
    lines = [f"== {name}\nhashed rule: {report['ruleVerdict']}"]
    for prof, b in report["rule"].items():
        lines.append(f"  {prof.split('-')[3]}: {b['verdict']}; budget {'holds' if b['budgetHolds'] else 'FAILS'} "
                     f"({len(b['awayBeyondB'])} away > B, {len(b['beyondCeiling'])} > 3B); partition {b['partition']}")
        for t, v in b["hashedTargets"].items():
            lines.append(f"    target {t:<10} A {v['A']} ref {v['ref']} halved {v['halved']} ({v['cells']} cells)")
        for t, v in b["beside"].items():
            if v:
                lines.append(f"    beside {t:<12} A {v['A']} ref {v['ref']} halved {v['halved']} ({v['cells']})")
        for k, v in b["groups"].items():
            lines.append(f"    group {k:<12} A {v['A']} <= {v['bound']} (ref {v['ref']} + tau {v['tau']}) "
                         f"{'gated' if v['gated'] else 'reported'} {'holds' if v['holds'] else 'FAILS'}")
        for a in b["awayBeyondB"]:
            lines.append(f"    away beyond B: {a['scene']} {a['growthInB']} B")
    lines.append("  rows:")
    for k, v in report["rows"].items():
        if isinstance(v, str):
            lines.append(f"    {k:<62} {v}")
    lines.append(f"    L1 max {report['rows']['L1 webgpu max']}; misses {report['rows']['L1 webgpu misses']}")
    lines.append(f"    M2 failures {report['rows']['M2 webgpu failures']}")
    lines.append(f"    S1 medians {report['rows']['S1 per profile median']}")
    lines.append("  CSS T1 (gate cells, median web/native; reference's beside):")
    for k, v in report["cssT1"].items():
        ref = report["reference"]["cssT1"].get(k, {})
        lines.append(f"    {k:<20} n={v['cells']:<3} x{v['medianRatio']} (d0219 x{ref.get('medianRatio')}) "
                     f"away {v['away']} toward {v['toward']}")
    Path(f"{out}.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
