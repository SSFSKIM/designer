#!/usr/bin/env python3.12
"""W47 G0 (d): the rehearsal of the landing rule on this bed (charter clause 3; Design "The landing
rule"; Decision Log 1). Nothing is rendered: every map is an existing render's reading, and the rule is
W47's port (`cuts/rule.py`, W46's binding verbatim).

  - **`d0219cd684bf` against itself.** The published dark generation (with `ebc3d9105a4a`, the light
    one, which the rule does not read) cut by W47's ported cuts against itself, with the canonical
    capture tree (read-only); every dark gate cell must be `unchanged` and the verdict NEITHER.
  - **W46's point A, by its committed evidence.** W46 G1's freeze-free gate cut of point A
    (`results/2026-10-05-w46-g1-refit/gate/<A>/cut.json.gz`, cut by W46's tools from the rendered
    point against `d0219cd684bf`) is READ, not re-cut (its renders are W46's scratch, which W47 never
    reads as a bed): its T1 cells, with their native, reference and candidate readings and the T
    cells' two bands, are evaluated by W47's rule. The cut is checked to name point A's committed
    candidate (`fit/candidates/<A>/candidate.json` there) by hash and `d0219cd684bf` as its
    reference. The verdict must reproduce §5.209 §4: NEITHER, with 16 and 17 cells away beyond B and
    8 and 10 past 3B (1x, 2x). If it does not, the rehearsal stops (exit 1) and the rule is NOT
    adjusted.
  - **W45's synthetic cases**: `cuts/test_rule.txt` (19 cases, unchanged from W46's port).
Per profile the gated and reported groups at the gate are listed against the charter's (per scale:
gated F rest 10, C rest 28, C inactive 14, P rest 4, P inactive 5, T rest 3; F inactive reported with
two gate cells; T inactive none). The count and the ceiling are the rule's constants and are not moved
by anything read here.

    python3.12 -B rehearse.py      (writes rehearsal.json, rehearsal.txt and the d0219 cut beside it;
                                    refuses to overwrite committed evidence)
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
POINT_A = "d-s2-rta0.8-rs214-rfa0.5-rh10.25-re20.04-rk10.15-rk20.04-rn10.4-rn20.4-rg0"
POINT_A_CUT = W.W46_G1 / "gate" / POINT_A / "cut.json.gz"
POINT_A_CANDIDATE = W.W46_G1 / "fit" / "candidates" / POINT_A / "candidate.json"
# §5.209 §4: point A's verdict under the hashed rule, per profile (away beyond B, beyond 3B).
POINT_A_EXPECTED = {W.DARK_025[0]: (16, 8), W.DARK_025[1]: (17, 10)}
CHARTER_GROUPS = {"F rest": (10, True), "T rest": (3, True), "C rest": (28, True), "C inactive": (14, True),
                  "P rest": (4, True), "P inactive": (5, True), "F inactive": (2, False)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(W.ROOT))


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
    out = dict(label=label, kind=kind, source=rel(source), sourceSha256=sha(source),
               verdict=r["verdict"], **extra, profiles={})
    for profile, p in r["profiles"].items():
        out["profiles"][profile] = dict(
            verdict=p["verdict"], read=p["read"], cells=p["cells"], unmeasured=len(p["unmeasured"]),
            partition={k: v["total"] for k, v in p["partition"].items()},
            targets=p["targets"], targetNotWithin={t: len(v) for t, v in p["targetNotWithin"].items()},
            groups={k: dict(A=g["A"], referenceA=g["referenceA"], tau=g["tau"], gated=g["gated"],
                            holds=g["holds"], cells=g["cells"], gateCells=g["gateCells"])
                    for k, g in p["groups"].items()},
            gatedAggregateFailures=p["gatedAggregateFailures"], reportedAggregateOver=p["reportedAggregateOver"],
            awayBeyondB=p["awayBeyondB"], awayBeyondCeiling=p["awayBeyondCeiling"], budgetHolds=p["budgetHolds"],
            why=p["why"],
            perCellChange={c["scene"]: c["change"] for c in p["perCell"]})
    out["pooledTargets"] = r["pooledTargets"]
    return out


def point_a_source() -> dict:
    """The committed gate cut names point A's committed candidate by hash and d0219cd684bf as its
    reference; nothing else is admitted as point A."""
    whole = json.loads(gzip.open(POINT_A_CUT).read())
    declared = whole["bed"]["candidateDocument"]
    if declared["path"] != rel(POINT_A_CANDIDATE) or declared["sha256"] != sha(POINT_A_CANDIDATE):
        raise SystemExit(f"rehearse: {rel(POINT_A_CUT)} does not name point A's committed candidate by hash")
    refs = [m["path"] for m in whole["T1"]["reference"]]
    if not any(W.REFERENCE["dark"] in p for p in refs):
        raise SystemExit(f"rehearse: {rel(POINT_A_CUT)} does not read d0219cd684bf as its reference ({refs})")
    endpoints = {}
    for slot in ("active.dark", "receded.dark"):
        doc = json.loads((POINT_A_CANDIDATE.parent / f"{slot}.json").read_text())
        endpoints[slot] = doc.get("resolvedMaterialSha256")
    return dict(t1=whole["T1"], candidate=rel(POINT_A_CANDIDATE), candidateSha256=sha(POINT_A_CANDIDATE),
                endpointDigests=endpoints, reference=refs)


def main() -> int:
    out_json, out_txt = HERE / "rehearsal.json", HERE / "rehearsal.txt"
    if out_json.exists() or out_txt.exists():
        raise SystemExit("rehearse: the rehearsal is committed evidence and is not overwritten")
    canonical = str(W.CANONICAL_CAPTURES)
    d0219 = cut("d0219", ["--published", W.REFERENCE["dark"], "--published", W.REFERENCE["light"],
                          "--captures", canonical])
    a = point_a_source()
    maps = [
        ("published d0219cd684bf against itself (W47's cuts, canonical captures)", d0219,
         json.loads(gzip.open(d0219).read())["T1"], {}),
        (f"W46's point A ({POINT_A}) against d0219cd684bf, W46 G1's committed gate cut read by W47's rule",
         POINT_A_CUT, a["t1"], dict(candidate=a["candidate"], candidateSha256=a["candidateSha256"],
                                    endpointDigests=a["endpointDigests"], cutReference=a["reference"])),
    ]
    rows = []
    for label, path, t, extra in maps:
        r = RULE.evaluate(t["cells"], t["missing"])
        complete = not r["verdict"].startswith("UNMEASURED")
        rows.append(row(label, "complete map" if complete else "PARTIAL map (diagnostics only)", r, path,
                        dict(extra, complete=complete)))

    checks = {}
    self_row = rows[0]
    checks["d0219 every gate cell unchanged"] = all(
        p["partition"]["toward"] == 0 and p["partition"]["away"] == 0 and p["verdict"].startswith("NEITHER")
        for p in self_row["profiles"].values())
    got_a = {prof: (len(p["awayBeyondB"]), len(p["awayBeyondCeiling"])) for prof, p in rows[1]["profiles"].items()}
    checks["point A reproduces §5.209 §4 (16/8 at 1x, 17/10 at 2x, NEITHER)"] = (
        got_a == POINT_A_EXPECTED and rows[1]["verdict"].startswith("NEITHER"))
    groups_ok = {}
    for profile, p in self_row["profiles"].items():
        got = {k: (g["gateCells"], g["gated"]) for k, g in p["groups"].items()}
        groups_ok[profile] = dict(got=got, charter=CHARTER_GROUPS, equal=got == CHARTER_GROUPS)
    checks["gated and reported groups equal the charter's per scale"] = all(g["equal"] for g in groups_ok.values())
    synthetic = (W.CUTS / "test_rule.txt").read_text().strip().splitlines()
    checks["W45's synthetic cases pass"] = synthetic[-1] == "OK"

    result = dict(
        schema="w47-rehearsal-1",
        what="W47 G0 (d): W45's landing rule as W46 bound it (W47's verbatim port), on d0219cd684bf against "
             "itself and on W46's point A by its committed gate cut, beside W45's synthetic cases; nothing "
             "rendered",
        charter=W.CHARTER_PIN,
        rule=dict(path=rel(W.CUTS / "rule.py"), sha256=sha(W.CUTS / "rule.py"),
                  constants=dict(budgetCount=RULE.BUDGET_COUNT, budgetCeilingB=RULE.BUDGET_CEILING_B,
                                 gatingMinCells=RULE.GATING_MIN_CELLS),
                  targets={t: [f"{s} {p}" for s, p in g] for t, g in RULE.TARGETS.items()}),
        pointAExpected={p: dict(awayBeyondB=v[0], beyond3B=v[1]) for p, v in POINT_A_EXPECTED.items()},
        rows=rows, groupsAgainstCharter=groups_ok,
        synthetic=dict(path=rel(W.CUTS / "test_rule.txt"), sha256=sha(W.CUTS / "test_rule.txt"),
                       result=synthetic[-3:]),
        checks=checks)

    lines = [f"W47 G0 (d): the rehearsal (rule sha256 {result['rule']['sha256'][:12]}; count {RULE.BUDGET_COUNT}, "
             f"ceiling {RULE.BUDGET_CEILING_B:g} B, gated at {RULE.GATING_MIN_CELLS} gate cells; per dark profile; "
             f"bar 0.5 code, reference {RULE.REFERENCE})", ""]
    lines.append("| map | profile | verdict | unchanged / toward / away | away > B | > 3B | P | C rest | F inactive |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for i, x in enumerate(rows):
        name = "d0219cd684bf vs itself" if i == 0 else "W46 point A"
        for profile, p in x["profiles"].items():
            part = p["partition"]
            tg = p["targets"]
            cells = " | ".join(
                "—" if tg[t] is None else f"{tg[t]['A']:.3f} / {tg[t]['referenceA']:.3f}{' (halved)' if tg[t]['halved'] else ''}"
                for t in RULE.TARGETS)
            lines.append(f"| {name} | {profile.split('-')[3]} | {p['verdict'].split(':')[0]} | {part['unchanged']} / "
                         f"{part['toward']} / {part['away']} | {len(p['awayBeyondB'])} | {len(p['awayBeyondCeiling'])} "
                         f"| {cells} |")
    lines.append("")
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
                lines.append(f"    {k:<12} gate {g['gateCells']:<3} read {g['cells']:<3} "
                             f"{'GATED' if g['gated'] else 'reported'} A {g['A']:.4f} ref {g['referenceA']:.4f} "
                             f"τ {g['tau']:.4f}{flag}")
            lines.append(f"    budget: {len(p['awayBeyondB'])} away beyond B, {len(p['awayBeyondCeiling'])} beyond 3 B "
                         f"-> {'holds' if p['budgetHolds'] else 'FAILS'}")
            for a_ in p["awayBeyondB"]:
                lines.append(f"      {a_['scene']:<50} {a_['growthInB']:.2f} B")
            for w in p["why"]:
                lines.append(f"    why: {w}")
        lines.append("")
    for profile, g in groups_ok.items():
        lines.append(f"gated/reported groups at the gate, {profile}: "
                     f"{'EQUAL to the charter' if g['equal'] else 'DIFFER'} ("
                     + ", ".join(f"{k} {v[0]} {'gated' if v[1] else 'reported'}" for k, v in g["got"].items())
                     + "; T inactive has no gate cell)")
    lines.append(f"synthetic cases (cuts/test_rule.py): {synthetic[-3].strip()} {synthetic[-1]}")
    lines.append("")
    for k, v in checks.items():
        lines.append(f"CHECK {'PASS' if v else 'FAIL'}: {k}")
    with out_json.open("x") as f:
        json.dump(result, f, indent=1)
        f.write("\n")
    with out_txt.open("x") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
