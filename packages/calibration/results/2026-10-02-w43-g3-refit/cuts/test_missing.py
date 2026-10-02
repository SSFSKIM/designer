#!/usr/bin/env python3.12
"""W43 G3 (i) review closure (charter clause 10): the red cases for the review's two P2 findings.

  1. A declared member with no row vanished from every cut but S1, and a (profile, tier) pair
     with no row at all lost its verdict, although the render drivers write ``--write-partial``.
  2. An L1 cell whose pre-fit row carries no web mean passed with its growth clause unread.

Each case builds a scratch bed under /tmp from candidate c05's scratch matrix (or the pre-fit
one), reads the affected cuts with the fixed ``cuts.py`` and with the pre-fix revision
(``PRE_FIX``, read out of git and run over the same ``bed.py``), and asserts:

  (0) the unmodified c05 bed reproduces the verdicts, misses and failing lists ``PRE_FIX``
      committed in ``read/c05-cuts.json``;
  (a) E2 WebGPU without one failing cell's row names it UNMEASURED, no row, and still reads MISS
      (pre-fix: the cell vanished); without every failing cell's row it reads "PASS, N
      UNMEASURED (N no row)" (pre-fix: PASS);
  (b) the (1x light, CSS) pair with no row: ``Bed.missing`` names all its declared scenes, its
      table reads UNMEASURED (pre-fix: its MISS vanished), and every other cut names the pair's
      members UNMEASURED, no row, with no unqualified PASS; (b2) the same for the (2x dark,
      WebGPU) pair on the row-derived gated cuts;
  (c) one pre-fit row's interiorMeanWeb deleted for a WebGPU L1 cell: the cell is UNMEASURED on
      the growth clause and counted against the verdict (pre-fix: MEASURED, the clause unread).

Pure Python: no browser, no capture. ``python3.12 -B test_missing.py`` prints the record
``test_missing.txt`` keeps, and exits 1 on any failed assertion.
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bed as B  # noqa: E402
import cuts as C  # noqa: E402

PRE_FIX = "9e9cfcd2"
SCRATCH = Path.home() / "vitrea-w43" / "g3-scratch"
C05, PREFIT = SCRATCH / "fit" / "c05", SCRATCH / "prefit"
CANDIDATE = str((B.EVIDENCE / "fit" / "candidates" / "c05" / "candidate.json").relative_to(B.ROOT))
TMP = Path("/tmp/w43-g3-test-missing")
TIERS = tuple(B.TIERS)
failures: list[str] = []


def check(ok: bool, what: str) -> None:
    print(f"    {'ok  ' if ok else 'FAIL'} {what}")
    if not ok:
        failures.append(what)


def git_show(path: Path) -> str:
    rel = path.relative_to(B.ROOT)
    return subprocess.run(["git", "-C", str(B.ROOT), "show", f"{PRE_FIX}:{rel}"], check=True,
                          capture_output=True, text=True).stdout


def prefix_cuts():
    """``cuts.py`` as ``PRE_FIX`` had it, importing the current ``bed.py`` as before."""
    module = types.ModuleType("cuts_prefix")
    module.__file__ = str(HERE / "cuts.py")
    exec(compile(git_show(HERE / "cuts.py"), f"{PRE_FIX}:cuts.py", "exec"), module.__dict__)
    return module


def scratch(name: str, source: Path, keep=lambda r: True, edit=lambda r: None) -> Path:
    matrix = json.loads(source.read_text())
    matrix["cells"] = [r for r in matrix["cells"] if keep(r)]
    for r in matrix["cells"]:
        edit(r)
    out = TMP / name / "matrix.json"
    out.parent.mkdir(parents=True)
    out.write_text(json.dumps(matrix))
    return out


def ident(r) -> tuple[str, str, str]:
    return r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]


def fingerprint(r: dict) -> dict:
    return dict(
        summary=r["summary"],
        tables={k: [(m["scene"], m["metric"], m["measured"]) for m in t["misses"]]
                for k, t in r["tables"].items()},
        M1={t: r["M1"][t]["cellMisses"] for t in TIERS},
        M2={t: [(m["cell"], m["verdict"], m["delta"]) for m in r["M2"][t]["misses"]]
            for t in TIERS},
        C1={t: {k: e["statistic"] for k, e in r["C1"][t]["perBedSpan"].items()} for t in TIERS},
        L1={t: ([c["cell"] for c in r["L1"][t]["absoluteMisses"]],
                [c["cell"] for c in r["L1"][t]["growthMisses"]], r["L1"][t]["unmeasured"])
            for t in TIERS},
        X1={t: [c["cell"] for c in r["X1"][t]["failing"]] for t in TIERS},
        E2={t: ([c["cell"] for c in r["E2"][t]["failing"]], r["E2"][t]["namedMissCells"],
                len(r["E2"][t]["namedMissBins"])) for t in TIERS},
        S1={t: (r["S1"][t]["pooledMedianRatio"], [c["cell"] for c in r["S1"][t]["wrongSign"]])
            for t in TIERS})


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    old = prefix_cuts()
    c05_matrix, prefit_matrix = C05 / "matrix.json", PREFIT / "matrix.json"
    prefit = B.load([str(prefit_matrix)], "prefit")
    print(f"W43 G3 (i) review closure: declared populations and L1's growth clause, red cases")
    print(f"pre-fix cuts.py: {PRE_FIX}; bed c05 {CANDIDATE}; scratch beds under {TMP}")

    print("\n(0) the unmodified c05 bed against the verdicts committed at the pre-fix revision")
    out = TMP / "c05-cuts.json"
    with contextlib.redirect_stdout(io.StringIO()):
        C.main(["--bed", str(c05_matrix), "--kind", "candidate", "--candidate-document", CANDIDATE,
                "--captures", str(C05 / "web-captures"), "--prefit", str(prefit_matrix),
                "--prefit-captures", str(PREFIT / "web-captures"), "--out", str(out)])
    now = json.loads(out.read_text())
    then = json.loads(git_show(B.EVIDENCE / "read" / "c05-cuts.json"))
    for k, v in now["summary"].items():
        print(f"  {k:<64} {v}")
    check(fingerprint(now) == fingerprint(then),
          "verdicts, misses, failing and named lists and S1 numbers equal the committed ones")
    check(all(not now[cut][t]["noRow"] for cut in ("M1", "C1", "L1", "X1", "E2", "S1")
              for t in TIERS) and all(not t["noRow"] for t in now["tables"].values()),
          "a complete bed has no member without a row")
    check(now["L1"]["webgpu"]["unmeasured"] == then["L1"]["webgpu"]["unmeasured"]
          and len(then["L1"]["webgpu"]["unmeasured"]) == 4
          and not now["L1"]["webgpu"]["growthUnmeasured"],
          "L1 WebGPU's UNMEASURED are the four reading-level dark cells, none for the growth "
          "clause alone")
    c05 = B.load([str(c05_matrix)], "candidate", CANDIDATE)

    print("\n(a) E2 WebGPU with failing cells' rows removed")
    failing = [c["cell"] for c in now["E2"]["webgpu"]["failing"]]
    for label, gone in (("one failing cell", failing[:1]), ("every failing cell", failing)):
        path = scratch(f"a-{len(gone)}", c05_matrix,
                       keep=lambda r: not (r["key"]["web"]["renderer"] == "webgpu"
                                           and f"{r['key']['profileKey']}/{r['key']['sceneId']}"
                                           in gone))
        bed = B.load([str(path)], "candidate", CANDIDATE)
        args = (bed, C05 / "web-captures", prefit, PREFIT / "web-captures", "webgpu")
        before, after = old.cut_e2(*args), C.cut_e2(*args)
        print(f"  {label} ({len(gone)}): pre-fix {before['verdict']!r} on {before['cells']} cells; "
              f"fixed {after['verdict']!r}, {len(after['noRow'])} no row")
        if len(gone) == 1:
            print(f"    removed {gone[0]}")
        check(not set(gone) & {c["cell"] for c in before["perCell"]},
              "pre-fix: the removed cells vanished from E2")
        check(sorted(after["noRow"]) == sorted(gone),
              "fixed: every removed cell is UNMEASURED, no row")
        if len(gone) == 1:
            check(after["verdict"] == "MISS", "fixed: MISS still wins")
        else:
            check(before["verdict"] == "PASS", "pre-fix: PASS with the failing cells gone")
            check(after["verdict"] == f"PASS, {len(gone)} UNMEASURED ({len(gone)} no row)",
                  "fixed: no unqualified PASS")

    current = B.current_05_rows()
    tables = C.owner_tables()
    for case, (profile, renderer), heavy in (
            ("b", ("apple-macos-27.0-1x-light-standard-glass0.25", "css"), True),
            ("b2", ("apple-macos-27.0-2x-dark-standard-glass0.25", "webgpu"), False)):
        print(f"\n({case}) the whole ({profile}, {renderer}) pair removed")
        path = scratch(case, c05_matrix,
                       keep=lambda r: (r["key"]["profileKey"], r["key"]["web"]["renderer"])
                       != (profile, renderer))
        bed = B.load([str(path)], "candidate", CANDIDATE)
        declared = sorted(s for s in B.SCENES.declared(profile)
                          if B.SCENES.role[s] in B.NON_HOLDOUT)
        check(bed.missing[(profile, renderer)] == declared
              and bed.described()["missingNonHoldout"][f"{profile} {renderer}"] == declared,
              f"Bed.missing names all {len(declared)} declared non-holdout scenes of the pair")
        pair = f"{profile} {renderer}"
        before_t, after_t = old.cut_tables(bed, tables), C.cut_tables(bed, tables)
        print(f"  tables {pair}: committed {then['tables'][pair]['verdict']!r}; pre-fix "
              f"{before_t.get(pair, {}).get('verdict', '(no entry)')!r}; fixed "
              f"{after_t[pair]['verdict']!r}, {len(after_t[pair]['noRow'])} no row")
        check(pair not in before_t, "pre-fix: the pair's table verdict vanished")
        expected = [s for s in B.SCENES.declared(profile) if C.gated_member(s)
                    and B.SCENES.role[s] in B.NON_HOLDOUT]
        check(after_t[pair]["verdict"] == "UNMEASURED" and after_t[pair]["noRow"] == expected,
              "fixed: the pair's table reads UNMEASURED, its gated cells named")
        reads = {
            "M1": lambda m: m.cut_m1_m2(bed, prefit, renderer)["M1"],
            "M2": lambda m: m.cut_m1_m2(bed, prefit, renderer)["M2"],
            "C1": lambda m: m.cut_c1(bed, renderer, {}),
            "L1": lambda m: m.cut_l1(bed, prefit, renderer)}
        rules = {"M1": C.chroma_member, "M2": C.chroma_member, "C1": C.c1_member,
                 "L1": lambda s: B.SCENES.role[s] in ("calibration", "validation")}
        if heavy:
            reads["X1"] = lambda m: m.cut_x1(bed, C05 / "web-captures", renderer)
            reads["E2"] = lambda m: m.cut_e2(bed, C05 / "web-captures", prefit,
                                             PREFIT / "web-captures", renderer)
            rules |= {"X1": C.x1_member, "E2": C.e2_member}
            reads["S1"] = lambda m: m.cut_s1(bed, current)[renderer]
        for cut, read in reads.items():
            before, after = read(old), read(C)
            members = [f"{profile}/{s}" for s in B.SCENES.declared(profile)
                       if B.SCENES.role[s] in B.NON_HOLDOUT and rules[cut](s)] \
                if cut != "S1" else [f"{e['profileKey']}/{e['sceneId']}" for e in json.loads(
                    C.R2_POPULATION.read_text())["cells"] if e["reading"] == "interiorMean"
                    and e["tier"] == renderer and e["profileKey"] == profile]
            print(f"  {cut} {renderer}: committed {then[cut][renderer]['verdict']!r}; pre-fix "
                  f"{before['verdict']!r}; fixed {after['verdict']!r}, "
                  f"{len(after['noRow'])} no row of {len(members)} declared")
            check(set(after["noRow"]) == set(members) and len(after["noRow"]) == len(members),
                  f"fixed: {cut} names every declared member of the pair UNMEASURED, no row")
            check(after["verdict"] != "PASS", f"fixed: {cut} gives no unqualified PASS")

    print("\n(c) one pre-fit row's interiorMeanWeb deleted for a WebGPU L1 cell")
    cell = next(c for c in now["L1"]["webgpu"]["cells"] if c["status"] == "MEASURED")
    profile, sid = cell["cell"].split("/")
    target = (profile, "webgpu", sid)
    path = scratch("c-prefit", prefit_matrix,
                   edit=lambda r: r["material"].pop("interiorMeanWeb")
                   if ident(r) == target else None)
    stripped = B.load([str(path)], "prefit")
    before, after = old.cut_l1(c05, stripped, "webgpu"), C.cut_l1(c05, stripped, "webgpu")
    b_cell = next(c for c in before["cells"] if c["cell"] == cell["cell"])
    a_cell = next(c for c in after["cells"] if c["cell"] == cell["cell"])
    print(f"  cell {cell['cell']} (error {cell['error']:.4f})")
    print(f"  pre-fix: cell {b_cell['status']}, growth {b_cell['growth']}; verdict "
          f"{before['verdict']!r}")
    print(f"  fixed:   cell {a_cell['status']} {a_cell.get('unmeasuredClauses')}; verdict "
          f"{after['verdict']!r}")
    check(b_cell["status"] == "MEASURED" and b_cell["growth"] is None
          and before["verdict"] == now["L1"]["webgpu"]["verdict"],
          "pre-fix: the cell read MEASURED with the growth clause unread, verdict unmoved")
    check(a_cell["status"] == "UNMEASURED" and a_cell["unmeasuredClauses"] == ["growth"]
          and after["growthUnmeasured"] == [cell["cell"]],
          "fixed: the cell is UNMEASURED on the growth clause, and named")
    check(after["verdict"] == "PASS, 5 UNMEASURED (1 growth clause only)",
          "fixed: the verdict counts it")

    print(f"\n{'FAILED: ' + str(len(failures)) if failures else 'all assertions hold'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
