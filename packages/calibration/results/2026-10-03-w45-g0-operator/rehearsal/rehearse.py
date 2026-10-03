#!/usr/bin/env python3.12
"""W45 G0 (d): the rehearsal of the landing rule (charter clause 3; Decision Log 3; X55).

Nothing is rendered. The rule (`../cuts/rule.py`) is evaluated, at the gate scope (WebGPU, 2x light,
both poses, F ∪ T ∪ C ∪ P less the referees), on:
  - W44's three COMPLETE 94-cell maps (`m1c-0.5-5`, `m2-t0.8`, `m3-t0.1`, the joint point), from
    their committed cuts (`results/2026-10-03-w44-g1-refit/fit/candidates/<label>/cuts.json.gz`,
    each against the published c05 generation, X52);
  - c05 against itself (`c05-cuts.json.gz`, W45's port on the published generation);
  - W43's pre-fit render against c05 (`prefit-cuts.json.gz`, W45's port on
    `~/vitrea-w43/g3-scratch/prefit/matrix.json` at sha256 504c5348…);
  - W44's 97 PARTIAL candidates (move populations only): UNMEASURED is preserved — each carries
    per-cell diagnostics and never a landing verdict;
and it records the synthetic cases' result (`../cuts/test_rule.txt`). Every verdict is committed
(`rehearsal.json`, `rehearsal.txt`); the count and the ceiling are the rule's constants and are
not moved by anything read here (X55).

    python3.12 -B rehearse.py   (refuses to overwrite its outputs)
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402
sys.path.insert(1, str(B.W44_G1 / "cuts"))
import rule  # noqa: E402

CANDIDATES = B.W44_G1 / "fit" / "candidates"
COMPLETE = ("m1c-0.5-5", "m2-t0.8", "m3-t0.1")
JOINT = "m3-t0.1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    return json.loads(gzip.open(path).read())


def row(label: str, kind: str, r: dict, source: Path) -> dict:
    return dict(
        label=label, kind=kind, source=str(source.relative_to(B.ROOT)), sourceSha256=sha(source),
        verdict=r["verdict"], read=r["read"], cells=r["cells"], unmeasured=len(r["unmeasured"]),
        partition={k: v["total"] for k, v in r["partition"].items()},
        fAggregate=r["fAggregate"], fAggregateReference=r["fAggregateReference"], fHalved=r["fHalved"],
        fNotWithin=len(r["fNotWithin"]),
        groups={k: dict(A=g["A"], referenceA=g["referenceA"], tau=g["tau"], gated=g["gated"],
                        holds=g["holds"], cells=g["cells"]) for k, g in r["groups"].items()},
        gatedAggregateFailures=r["gatedAggregateFailures"],
        reportedAggregateOver=r["reportedAggregateOver"],
        awayBeyondB=r["awayBeyondB"], awayBeyondCeiling=r["awayBeyondCeiling"],
        budgetHolds=r["budgetHolds"], why=r["why"])


def main() -> int:
    out_json, out_txt = HERE / "rehearsal.json", HERE / "rehearsal.txt"
    if out_json.exists() or out_txt.exists():
        raise SystemExit("rehearse: the rehearsal is committed evidence and is not overwritten")
    rows = []
    for label, path in (("c05 (against itself)", HERE / "c05-cuts.json.gz"),
                        ("pre-fit (W43, against c05)", HERE / "prefit-cuts.json.gz")):
        t = read(path)["T1"]
        rows.append(row(label, "render", rule.evaluate(t["cells"], t["missing"]), path))
    partial = []
    for folder in sorted(CANDIDATES.iterdir()):
        path = folder / "cuts.json.gz"
        if not path.exists():
            continue
        t = read(path)["T1"]
        r = rule.evaluate(t["cells"], t["missing"])
        complete = not r["unmeasured"] and r["read"] == r["cells"]
        if folder.name in COMPLETE:
            if not complete:
                raise SystemExit(f"rehearse: {folder.name} is declared complete and has "
                                 f"{len(r['unmeasured'])} UNMEASURED members")
            rows.append(row(folder.name + (" (W44's joint point)" if folder.name == JOINT else ""),
                            "complete W44 map", r, path))
        else:
            if complete:
                raise SystemExit(f"rehearse: {folder.name} reads complete and is not declared so")
            if not r["verdict"].startswith("UNMEASURED"):
                raise SystemExit(f"rehearse: {folder.name} is partial and its verdict is {r['verdict']}")
            partial.append(dict(
                label=folder.name, source=str(path.relative_to(B.ROOT)), sourceSha256=sha(path),
                verdict=r["verdict"], read=r["read"], unmeasured=len(r["unmeasured"]),
                diagnostics=dict(partition={k: v["total"] for k, v in r["partition"].items()},
                                 awayBeyondBAmongRead=[a["scene"] for a in r["awayBeyondB"]],
                                 awayBeyondCeilingAmongRead=[a["scene"] for a in r["awayBeyondCeiling"]])))
    synthetic = (EVIDENCE / "cuts" / "test_rule.txt").read_text().strip().splitlines()[-1]
    joint = next(x for x in rows if x["label"].startswith(JOINT))
    result = dict(
        schema="w45-rehearsal-1",
        what="W45 G0 (d): the landing rule (Decision Log 3) on W44's three complete maps, c05, the "
             "pre-fit render and W44's partial candidates; nothing rendered",
        rule=dict(path=str((EVIDENCE / "cuts" / "rule.py").relative_to(B.ROOT)),
                  sha256=sha(EVIDENCE / "cuts" / "rule.py"),
                  constants=dict(budgetCount=rule.BUDGET_COUNT, budgetCeilingB=rule.BUDGET_CEILING_B,
                                 gatingMinCells=rule.GATING_MIN_CELLS)),
        rows=rows, partial=partial, partialCount=len(partial),
        synthetic=dict(path=str((EVIDENCE / "cuts" / "test_rule.txt").relative_to(B.ROOT)),
                       result=synthetic),
        joint=dict(verdict=joint["verdict"], awayBeyondB=len(joint["awayBeyondB"]),
                   awayBeyondCeiling=len(joint["awayBeyondCeiling"]),
                   failsOnCount=len(joint["awayBeyondB"]) > rule.BUDGET_COUNT,
                   failsOnCeiling=bool(joint["awayBeyondCeiling"])))
    lines = [f"W45 G0 (d): the rehearsal (rule sha256 {result['rule']['sha256'][:12]}; count "
             f"{rule.BUDGET_COUNT}, ceiling {rule.BUDGET_CEILING_B:g} B, gated at {rule.GATING_MIN_CELLS} cells)", ""]
    for x in rows:
        lines.append(f"{x['label']:<34} {x['verdict']}")
        lines.append(f"    partition {x['partition']}; F aggregate {x['fAggregate']:.4f} against "
                     f"{x['fAggregateReference']:.4f} (halved {x['fHalved']}), {x['fNotWithin']} F not within")
        lines.append(f"    budget: {len(x['awayBeyondB'])} away beyond B, {len(x['awayBeyondCeiling'])} beyond 3 B"
                     f" -> {'holds' if x['budgetHolds'] else 'FAILS'}")
        for a in x["awayBeyondB"]:
            lines.append(f"      {a['scene']:<46} {a['growthInB']:.2f} B")
        for k, g in x["groups"].items():
            flag = "" if g["holds"] else (" WORSE BEYOND τ (gated)" if g["gated"] else " over τ (reported)")
            lines.append(f"    {k:<12} n={g['cells']:<3} A {g['A']:.4f} c05 {g['referenceA']:.4f} τ {g['tau']:.4f}{flag}")
        for w in x["why"]:
            lines.append(f"    why: {w}")
        lines.append("")
    lines.append(f"W44's partial candidates: {len(partial)}, every one UNMEASURED (move populations only; "
                 "diagnostics in the JSON, never a landing verdict)")
    lines.append(f"synthetic cases (cuts/test_rule.py): {synthetic}")
    lines.append(f"the joint point: {joint['verdict']}; fails on the count "
                 f"({len(joint['awayBeyondB'])} > {rule.BUDGET_COUNT}): {result['joint']['failsOnCount']}; "
                 f"on the ceiling ({len(joint['awayBeyondCeiling'])} beyond 3 B): {result['joint']['failsOnCeiling']}")
    with out_json.open("x") as f:
        json.dump(result, f, indent=1)
        f.write("\n")
    with out_txt.open("x") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
