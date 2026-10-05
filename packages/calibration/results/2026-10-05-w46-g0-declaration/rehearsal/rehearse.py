#!/usr/bin/env python3.12
"""W46 G0 (c): the rehearsal of the landing rule on this bed (charter clause 2; Decision Log 3). Nothing
is rendered: every map is an existing render, cut by W46's ported cuts against the published
`d0219cd684bf` generation.

  - **`d0219cd684bf` against itself**: the published dark generation (and `ebc3d9105a4a`, the light
    one, which the rule does not read) as the bed; every dark gate cell must be `unchanged`.
  - **W43 G3's dark pre-fit render, by hash**: the shipped 0.5 documents drawn on the 0.25 cells,
    `~/vitrea-w43/g3-scratch/prefit/matrix.json` at sha256 `504c5348…` (its committed record
    `results/2026-10-02-w43-g3-refit/prefit/record.json` names the same), with its captures beside it.
    Its withheld rows are dropped unread by the bed (`refereeRowsDropped`).
  - **W43's dark probe c02, if its map is complete**: `~/vitrea-w43/g3-scratch/fit/c02/matrix.json`
    with its committed declaration. Its dark rows are the calibration and validation scenes only, so its
    map is PARTIAL: the rule reads it UNMEASURED and it is recorded as such, with its read cells'
    diagnostics, never a landing verdict.
And the synthetic cases' result (`../cuts/test_rule.txt`). Per profile the gated and reported groups are
listed after the withholding, against the charter's counts (per scale: gated F rest 10, T rest 3,
C rest 28, C inactive 14, P rest 4, P inactive 5; reported F inactive 2; T inactive none). The count and
the ceiling are the rule's constants and are not moved by anything read here.

    python3.12 -B rehearse.py      (writes the cuts it reads beside it; refuses to overwrite)
"""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
import bindings as W  # noqa: E402

B, T1, RULE = W.load_cuts()
CUTS = W.CUTS / "cuts.py"
PREFIT = Path.home() / "vitrea-w43/g3-scratch/prefit"
PREFIT_SHA = "504c5348638265e6a141308d4f74d98dc6119dfbb9e12e15164fc6e028bdebbb"
C02 = Path.home() / "vitrea-w43/g3-scratch/fit/c02"
C02_CANDIDATE = W.RESULTS / "2026-10-02-w43-g3-refit/fit/candidates/c02/candidate.json"
CHARTER_GROUPS = {"F rest": (10, True), "T rest": (3, True), "C rest": (28, True), "C inactive": (14, True),
                  "P rest": (4, True), "P inactive": (5, True), "F inactive": (2, False)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cut(name: str, argv: list[str]) -> Path:
    out = HERE / f"{name}-cuts.json"
    gz = out.with_suffix(".json.gz")
    if gz.exists():
        return gz
    got = subprocess.run([sys.executable, "-B", str(CUTS), *argv, "--out", str(out),
                          "--text", str(HERE / f"{name}-cuts.txt")], cwd=W.CUTS, capture_output=True, text=True)
    if got.returncode:
        raise SystemExit(f"rehearse: cuts.py on {name} exit {got.returncode}: {got.stderr[-1500:]}")
    with gzip.open(gz, "wt") as f:
        f.write(out.read_text())
    out.unlink()
    return gz


def row(label: str, kind: str, r: dict, source: Path, extra: dict) -> dict:
    out = dict(label=label, kind=kind, source=str(source.relative_to(W.ROOT)), sourceSha256=sha(source),
               verdict=r["verdict"], **extra, profiles={})
    for profile, p in r["profiles"].items():
        out["profiles"][profile] = dict(
            verdict=p["verdict"], read=p["read"], cells=p["cells"], unmeasured=len(p["unmeasured"]),
            partition={k: v["total"] for k, v in p["partition"].items()},
            targets=p["targets"], targetNotWithin={t: len(v) for t, v in p["targetNotWithin"].items()},
            groups={k: dict(A=g["A"], referenceA=g["referenceA"], tau=g["tau"], gated=g["gated"],
                            holds=g["holds"], cells=g["cells"], gateCells=g["gateCells"]) for k, g in p["groups"].items()},
            gatedAggregateFailures=p["gatedAggregateFailures"], reportedAggregateOver=p["reportedAggregateOver"],
            awayBeyondB=p["awayBeyondB"], awayBeyondCeiling=p["awayBeyondCeiling"], budgetHolds=p["budgetHolds"],
            why=p["why"])
    out["pooledTargets"] = r["pooledTargets"]
    return out


def main() -> int:
    out_json, out_txt = HERE / "rehearsal.json", HERE / "rehearsal.txt"
    if out_json.exists() or out_txt.exists():
        raise SystemExit("rehearse: the rehearsal is committed evidence and is not overwritten")
    if sha(PREFIT / "matrix.json") != PREFIT_SHA:
        raise SystemExit("rehearse: W43's pre-fit matrix is not 504c5348…")
    record = json.loads((W.RESULTS / "2026-10-02-w43-g3-refit/prefit/record.json").read_text())
    if record["matrix"]["sha256"] != PREFIT_SHA:
        raise SystemExit("rehearse: W43's committed pre-fit record names another matrix")
    canonical = str(W.CANONICAL_CAPTURES)
    maps = [
        ("d0219", "published d0219cd684bf against itself",
         cut("d0219", ["--published", W.REFERENCE["dark"], "--published", W.REFERENCE["light"],
                       "--captures", canonical]), {}),
        ("prefit", "W43 G3's pre-fit render (504c5348…) against d0219cd684bf",
         cut("prefit", ["--bed", str(PREFIT / "matrix.json"), "--kind", "prefit",
                        "--captures", str(PREFIT / "web-captures")]),
         dict(matrixSha256=PREFIT_SHA, matrix=str(PREFIT / "matrix.json"))),
        ("c02", "W43's dark probe c02 against d0219cd684bf",
         cut("c02", ["--bed", str(C02 / "matrix.json"), "--kind", "candidate",
                     "--candidate-document", str(C02_CANDIDATE.relative_to(W.ROOT)), "--captures", str(C02 / "web-captures")]),
         dict(matrixSha256=sha(C02 / "matrix.json"), matrix=str(C02 / "matrix.json"),
              candidate=str(C02_CANDIDATE.relative_to(W.ROOT)), candidateSha256=sha(C02_CANDIDATE))),
    ]
    rows = []
    for name, label, path, extra in maps:
        t = json.loads(gzip.open(path).read())["T1"]
        r = RULE.evaluate(t["cells"], t["missing"])
        complete = not r["verdict"].startswith("UNMEASURED")
        rows.append(row(label, "complete render" if complete else "PARTIAL render (diagnostics only)", r, path,
                        dict(extra, complete=complete)))
    groups_ok = {}
    for profile, p in rows[0]["profiles"].items():
        got = {k: (g["gateCells"], g["gated"]) for k, g in p["groups"].items()}
        groups_ok[profile] = dict(got=got, charter=CHARTER_GROUPS, equal=got == CHARTER_GROUPS)
    synthetic = (W.CUTS / "test_rule.txt").read_text().strip().splitlines()[-1]
    result = dict(
        schema="w46-rehearsal-1",
        what="W46 G0 (c): W45's landing rule bound to the dark 0.25 profiles, on d0219cd684bf against itself, "
             "W43 G3's pre-fit render and W43's c02 (partial); nothing rendered",
        rule=dict(path=str((W.CUTS / "rule.py").relative_to(W.ROOT)), sha256=sha(W.CUTS / "rule.py"),
                  constants=dict(budgetCount=RULE.BUDGET_COUNT, budgetCeilingB=RULE.BUDGET_CEILING_B,
                                 gatingMinCells=RULE.GATING_MIN_CELLS)),
        rows=rows, groupsAgainstCharter=groups_ok,
        synthetic=dict(path=str((W.CUTS / "test_rule.txt").relative_to(W.ROOT)), result=synthetic))
    lines = [f"W46 G0 (c): the rehearsal (rule sha256 {result['rule']['sha256'][:12]}; count {RULE.BUDGET_COUNT}, "
             f"ceiling {RULE.BUDGET_CEILING_B:g} B, gated at {RULE.GATING_MIN_CELLS} gate cells; per dark profile)", ""]
    for x in rows:
        lines.append(f"{x['label']}: {x['verdict']}  [{x['kind']}]")
        for profile, p in x["profiles"].items():
            lines.append(f"  {profile}: {p['verdict']}; {p['read']} of {p['cells']} read; partition {p['partition']}")
            for t, a in p["targets"].items():
                if a is not None:
                    lines.append(f"    target {t:<11} n={a['cells']:<3} A {a['A']:.4f} ref {a['referenceA']:.4f} "
                                 f"halved {a['halved']}; {p['targetNotWithin'][t]} not within")
            for k, g in p["groups"].items():
                flag = "" if g["holds"] else (" WORSE BEYOND τ (gated)" if g["gated"] else " over τ (reported)")
                lines.append(f"    {k:<12} gate {g['gateCells']:<3} read {g['cells']:<3} {'GATED' if g['gated'] else 'reported'} "
                             f"A {g['A']:.4f} ref {g['referenceA']:.4f} τ {g['tau']:.4f}{flag}")
            lines.append(f"    budget: {len(p['awayBeyondB'])} away beyond B, {len(p['awayBeyondCeiling'])} beyond 3 B "
                         f"-> {'holds' if p['budgetHolds'] else 'FAILS'}")
            for a in p["awayBeyondB"][:12]:
                lines.append(f"      {a['scene']:<46} {a['growthInB']:.2f} B")
            if len(p["awayBeyondB"]) > 12:
                lines.append(f"      ... and {len(p['awayBeyondB']) - 12} more (JSON)")
            for w in p["why"]:
                lines.append(f"    why: {w}")
        lines.append("")
    for profile, g in groups_ok.items():
        lines.append(f"gated/reported groups at the gate, {profile}: {'EQUAL to the charter' if g['equal'] else 'DIFFER'} "
                     f"({', '.join(f'{k} {v[0]} {'gated' if v[1] else 'reported'}' for k, v in g['got'].items())}; "
                     "T inactive has no gate cell)")
    lines.append(f"synthetic cases (cuts/test_rule.py): {synthetic}")
    with out_json.open("x") as f:
        json.dump(result, f, indent=1)
        f.write("\n")
    with out_txt.open("x") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
