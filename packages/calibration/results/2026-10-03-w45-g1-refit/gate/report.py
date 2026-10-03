#!/usr/bin/env python3.12
"""W45 G1 step 6 (and 7): the GATE REPORT's tables, read off one cut of the light stage (charter
clause 6; Design "The landing rule"; claims §5.206). Reads only; never re-derives a verdict: the
landing verdict, the groups and the budget are W45's `cuts/rule.py` as `cuts.py` recorded it in the
cut's T1 block, and every other adopted row is the cut's own section.

    python3.12 -B report.py --cut CUT.json [--x48 X48.json] --json OUT.json --text OUT.txt

What it lays out, per tier and pose:
- the landing rule on the WebGPU 2x light scope (gate partition before the exposure; the referees
  and the holdout added at it): the verdict and why; the F aggregate (both poses pooled) against
  c05's; every stratum x pose group's A against c05's A + tau, gated or reported; every cell
  `away` with g > B (a T cell's on T1-low) with its growth in B, the count against three and the
  ceiling against 3B;
- the T cells' two bands (T1-fine for fidelity and change, T1-low for away), at both scales;
- the CSS tier's T1 residual per stratum x scale x pose against c05's (read, never gated);
- every other adopted row's verdict per tier, and each miss by cell against its bound;
- X48's verdict when given.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

LIGHT2 = "apple-macos-27.0-2x-light-standard-glass0.25"


def r4(x):
    return None if x is None else round(x, 4)


def rule_block(t1: dict) -> dict:
    rule = t1["rule"]
    groups = {k: dict(cells=g["cells"], gateCells=g["gateCells"], A=r4(g["A"]), c05A=r4(g["referenceA"]),
                      tau=r4(g["tau"]), bound=r4(g["referenceA"] + g["tau"]), gated=g["gated"], holds=g["holds"])
              for k, g in rule["groups"].items()}
    return dict(scope=rule["scope"], verdict=rule["verdict"], why=rule["why"], read=rule["read"], cells=rule["cells"],
                unmeasured=rule["unmeasured"], partition={k: v["total"] for k, v in rule["partition"].items()},
                fAggregate=r4(rule["fAggregate"]), fAggregateC05=r4(rule["fAggregateReference"]),
                fHalved=rule["fHalved"], fNotWithin=rule["fNotWithin"], groups=groups,
                awayBeyondB=[dict(scene=a["scene"], growthInB=round(a["growthInB"], 3)) for a in rule["awayBeyondB"]],
                count=len(rule["awayBeyondB"]), beyondCeiling=[a["scene"] for a in rule["awayBeyondCeiling"]],
                budgetHolds=rule["budgetHolds"])


def per_cell(t1: dict, tier: str, profile: str) -> list[dict]:
    return [c for c in t1["cells"] if c["tier"] == tier and c["profile"] == profile]


def t_cells(t1: dict) -> list[dict]:
    out = []
    for c in t1["cells"]:
        if c["tier"] != "webgpu" or c["scheme"] != "light" or c["stratum"] != "T" or "bands" not in c:
            continue
        f, lo = c["bands"]["fine"], c["bands"]["low"]
        out.append(dict(scene=c["scene"], scale=c["scale"], partition=c["partition"],
                        fine=dict(n=r4(f["native"]), c05=r4(f["reference"]), k=r4(f["candidate"]),
                                  fidelity=f["fidelity"], change=f["change"]),
                        low=dict(n=r4(lo["native"]), c05=r4(lo["reference"]), k=r4(lo["candidate"]),
                                 change=lo["change"], growthInB=round(lo["growth"] / lo["B"], 3))))
    return sorted(out, key=lambda x: (x["scale"], x["scene"]))


def css_residual(t1: dict) -> list[dict]:
    """The CSS tier's T1 per stratum x scale x pose (light 0.25): median |log| against c05's, and
    the change partition by error growth, read and never gated."""
    import math
    import statistics
    groups = defaultdict(list)
    for c in t1["cells"]:
        if c["tier"] == "css" and c["scheme"] == "light" and c["partition"] in ("gate", "referee", "holdout"):
            groups[(c["stratum"], c["scale"], c["pose"])].append(c)
    out = []
    for (s, scale, pose), cells in sorted(groups.items()):
        eps = [c["code"] for c in cells]
        lk = statistics.median(abs(math.log((c["candidate"] + e) / (c["native"] + e))) for c, e in zip(cells, eps))
        lc = statistics.median(abs(math.log((c["reference"] + e) / (c["native"] + e))) for c, e in zip(cells, eps))
        away = sorted(((c["scene"], round(c["growth"] / c["B"], 2)) for c in cells
                       if abs(c["candidate"] - c["reference"]) > c["bar"] and c["growth"] > c["B"]), key=lambda x: -x[1])
        out.append(dict(group=f"{s} {scale}x {pose}", cells=len(cells), A=r4(lk), c05A=r4(lc),
                        within=sum(c["fidelity"] == "within" for c in cells),
                        withinC05=None, awayBeyondB=away))
    return out


def adopted(cut: dict) -> dict:
    out = {}
    for key, t in cut["tables"].items():
        if "light" not in key:
            continue
        out[f"tables {key}"] = dict(verdict=t["verdict"], misses=[
            dict(cell=f"{m.get('set', '')} {m.get('scene', m.get('cell'))}", metric=m.get("metric"),
                 value=m.get("measured"), bound=m.get("bound"), status=m.get("status")) for m in t["misses"]])
    for row in ("M1", "M2", "C1", "L1", "X1", "E2", "S1"):
        for tier, sec in cut[row].items():
            entry = dict(verdict=sec["verdict"])
            if row == "M1":
                entry["cellMisses"] = sec["cellMisses"]
                entry["beds"] = sec["beds"]
            elif row == "M2":
                entry.update(failures=sec["failures"], named=sec["named"], worstAbsDelta=sec["worstAbsDelta"])
            elif row == "C1":
                entry["perBedSpan"] = {k: dict(statistic=r4(b["statistic"]), verdict=b["verdict"],
                                               c05=r4((b.get("prefit") or {}).get("statistic")))
                                       for k, b in sec["perBedSpan"].items() if "light" in k}
            elif row == "L1":
                entry.update(absoluteMisses=sec["absoluteMisses"], growthMisses=sec["growthMisses"],
                             maxError=sec["maxError"], maxGrowth=sec["maxGrowth"], unmeasured=sec["unmeasured"])
            elif row == "X1":
                entry.update(failing=[f for f in sec["failing"] if "light" in str(f)], cells=sec["cells"])
            elif row == "E2":
                entry.update(failing=sec["failing"], meanChange=sec["meanChange"],
                             namedMissCells=sec["namedMissCells"])
            elif row == "S1":
                entry.update(pooledMedianRatio=sec["pooledMedianRatio"], wrongSign=sec["wrongSign"],
                             perProfileMedian=sec["perProfileMedian"])
            out[f"{row} {tier}"] = entry
    return out


def text(rep: dict) -> str:
    L = []
    r = rep["rule"]
    L.append(f"LANDING RULE ({r['scope']})")
    L.append(f"  verdict: {r['verdict']}")
    for w in r["why"]:
        L.append(f"    why: {w}")
    L.append(f"  {r['read']} of {r['cells']} cells read; unmeasured {len(r['unmeasured'])}; partition {r['partition']}")
    L.append(f"  F aggregate {r['fAggregate']} against c05's {r['fAggregateC05']} (half {r4(r['fAggregateC05'] / 2)}; "
             f"halved {r['fHalved']}); F not within: {len(r['fNotWithin'])} {r['fNotWithin']}")
    L.append("  groups (A against c05's A + tau):")
    for k, g in r["groups"].items():
        L.append(f"    {k:<12} n={g['cells']:<3} gate={g['gateCells']:<3} A {g['A']} c05 {g['c05A']} + tau {g['tau']} = "
                 f"{g['bound']}  {'GATED' if g['gated'] else 'reported'} {'holds' if g['holds'] else 'OVER'}")
    L.append(f"  away with g > B: {r['count']} (at most 3); beyond 3B: {len(r['beyondCeiling'])}; budget "
             f"{'holds' if r['budgetHolds'] else 'FAILS'}")
    for a in r["awayBeyondB"]:
        L.append(f"    {a['scene']:<44} {a['growthInB']} B")
    L.append("T CELLS (fidelity and change on T1-fine; away on T1-low)")
    for t in rep["tCells"]:
        f, lo = t["fine"], t["low"]
        L.append(f"  {t['scale']}x {t['scene']:<28} {t['partition']:<8} fine n {f['n']} c05 {f['c05']} k {f['k']} "
                 f"{f['fidelity']}/{f['change']}; low n {lo['n']} c05 {lo['c05']} k {lo['k']} {lo['change']} "
                 f"g {lo['growthInB']} B")
    L.append("CSS T1 RESIDUAL (light; read, never gated)")
    for g in rep["cssResidual"]:
        L.append(f"  {g['group']:<18} n={g['cells']:<3} A {g['A']} c05 {g['c05A']}; within {g['within']}; away > B "
                 f"{len(g['awayBeyondB'])} {g['awayBeyondB'][:6]}")
    L.append("OTHER ADOPTED ROWS")
    for k, v in rep["adopted"].items():
        extra = {kk: vv for kk, vv in v.items() if kk != "verdict" and vv not in ([], None, {})}
        L.append(f"  {k:<62} {v['verdict']}")
        for kk, vv in extra.items():
            s = json.dumps(vv)
            L.append(f"      {kk}: {s[:600]}{'…' if len(s) > 600 else ''}")
    if rep.get("x48"):
        L.append(f"X48: {rep['x48']}")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cut", type=Path, required=True)
    ap.add_argument("--x48", type=Path)
    ap.add_argument("--json", type=Path, required=True)
    ap.add_argument("--text", type=Path, required=True)
    args = ap.parse_args()
    import gzip
    raw = gzip.open(args.cut).read() if args.cut.suffix == ".gz" else args.cut.read_bytes()
    cut = json.loads(raw)
    t1 = cut["T1"]
    rep = dict(cut=str(args.cut), bed=cut["bed"], reference=cut["reference"].get("label"),
               rule=rule_block(t1), tCells=t_cells(t1), cssResidual=css_residual(t1), adopted=adopted(cut))
    if args.x48:
        x = json.loads(args.x48.read_text())
        rep["x48"] = {k: v for k, v in x.items() if k in ("verdict", "rows", "identical", "differ", "captures",
                                                          "capturesIdentical", "capturesDiffer", "summary")}
    args.json.write_text(json.dumps(rep, indent=1) + "\n")
    args.text.write_text(text(rep))
    print(text(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
