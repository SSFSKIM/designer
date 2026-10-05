#!/usr/bin/env python3.12
"""W46 G0 (e): assemble part 1 (`declaration.json`) and its readable twin (`declaration.md`) from the
committed tools and evidence. Every number an item declares is read here from the file that defines it,
and `declare.py check` re-derives each one independently; this script only writes the declaration's
form. It refuses once part 1 is hashed (the hash fixes the bytes; an amendment re-pins, never rewrites).

    python3.12 -B assemble.py
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402
import declare as D  # noqa: E402

R = HERE.relative_to(W.ROOT).as_posix()
SHARED_R = "packages/calibration/results"
OWNER = f"packages/calibration/test/adopted-thresholds.test.ts@{W.CHARTER_COMMIT}"
CHARTER = f"{W.CHARTER_PATH}@{W.CHARTER_COMMIT}"
TESTS = [("test_bindings", ".", 9), ("test_cuts_refusals", "cuts", 11), ("test_build_candidate", "fit", 11),
         ("test_fit", "fit", 35), ("test_seal", "seal", 10), ("test_stage", "stage", 7), ("test_x60", "stage", 11),
         ("test_sheets", "sheets", 7), ("test_declare", ".", 19)]


def ev(*names):
    return [f"{R}/{n}" for n in names]


def main() -> int:
    if W.PART1_DIGEST.exists():
        raise SystemExit("assemble REFUSES: part 1 is hashed")
    B, T1, RULE, plan = D.cuts()
    held = plan.referee_cells(plan.load_manifest())
    pop = T1.population([W.DARK_025[0]])
    population = dict(cells=len(pop), **{s: sum(1 for _, sid in pop if T1.stratum(sid) == s) for s in "FTCP"},
                      **{part: sum(1 for _, sid in pop if T1.partition(W.DARK_025[0], sid, held) == part)
                         for part in ("gate", "holdout", "referee")})
    m = plan.load_manifest()
    lists = plan.lists(m)
    reh = json.loads((HERE / "rehearsal/rehearsal.json").read_text())
    rehearsal = {}
    for x in reh["rows"]:
        t = json.loads(gzip.open(W.ROOT / x["source"]).read())["T1"]
        r = RULE.evaluate(t["cells"], t["missing"])
        rehearsal[x["label"]] = [r["verdict"]] + [[p["partition"]["unchanged"]["total"], len(p["awayBeyondB"]),
                                                   len(p["awayBeyondCeiling"])] for p in r["profiles"].values()]
    pred = json.loads((HERE / "targets/predictions.json").read_text())
    draft = json.loads(W.DRAFT.read_text())
    families = {}
    for mv in draft["moves"]:
        for f in mv["families"].values():
            for key, spec in f["leaves"].items():
                families.setdefault(spec["target"], []).append(f"{spec['slot']} {key}")
    protocol = json.loads((HERE / "ladders/protocol.json").read_text())
    levers = [lv["id"] for lad in protocol["ladders"] for lv in lad.get("arms", []) + lad.get("levers", [])]
    cells = json.loads(W.LADDER_CELLS.read_text())
    index = json.loads((W.CAL / "results/generations/index.json").read_text())
    d0219 = index["files"]["d0219cd684bf.json"]
    ident = json.loads((HERE / "level/identity/identity.json").read_text())
    stage_reh = json.loads((HERE / "stage/rehearsal/rehearsal.json").read_text())
    bar = json.loads(W.BAR_PATH.read_text())

    tool_files = []
    for d in ("cuts", "fit", "seal", "stage", "sheets", "level", "referees", "ladders", "rehearsal", "targets"):
        for p in sorted((HERE / d).glob("*")):
            if p.is_file() and p.suffix in (".py", ".ts", ".json", ".txt", ".gz") and p.name not in ("runs.jsonl",):
                tool_files.append(p)
    items = [
        dict(id="documents", title="the starting point is four document snapshots (X62)", clause="clause 1; X62",
             source=ev("bindings.py", "test_bindings.py", "test_bindings.txt") + [f"{R}/documents/{W.DOCUMENT_SHA[s][:12]}.json" for s in W.SLOTS],
             declared=dict(files={s: W.DOCUMENT_SHA[s][:12] for s in W.SLOTS}, digests=W.DOCUMENT_DIGEST,
                           commit=W.SNAPSHOT_COMMIT),
             statement="The dark and light 0.25 document bodies, each verified against its twelve-hex hash and its bytes at "
                       "b36c9990. Every W46 tool builds from these and refuses the live profiles/ as a start."),
        dict(id="t1", title="T1 as adopted, its shared arithmetic, and its dark population", clause="Decision Log 3",
             source=[f"{SHARED_R}/2026-10-03-w44-g1-refit/cuts/t1.py", f"{SHARED_R}/2026-10-03-w44-g1-refit/cuts/readings.py",
                     f"{SHARED_R}/2026-10-03-w44-g1-refit/cuts/test_t1.py", OWNER],
             declared=dict(populationPerDarkProfile=population, strata={k: list(v) for k, v in T1.STRATA.items()},
                           ratioClause=T1.RATIO_CLAUSE, equalTolerance=T1.EQUAL, ownerTest=OWNER,
                           ownerNeedles=['const T1_READ_PROFILES = [\n  "apple-macos-27.0-1x-dark-standard-glass0.25",\n'
                                         '  "apple-macos-27.0-2x-dark-standard-glass0.25",',
                                         'const T1_REFERENCE = { active: "ebc3d9105a4a", receded: "12712d534b78" } as const;']),
             statement="T1's statistic, bar and arithmetic unchanged (W44 G1's t1.py by path, pinned). The owner test reads "
                       "the dark 0.25 profiles and gates none of them today; G2 adopts them in W45's five-part order."),
        dict(id="bar", title="the bar: 0.5 code on every dark cell", clause="Decision Log 3",
             source=[f"{SHARED_R}/2026-10-03-w44-g0-declaration/bar/t1-bar.json"],
             declared=dict(darkCells=sum(1 for x in bar["table"] if x["profile"] in W.DARK_025),
                           maxSeparation=bar["maxSeparation"]),
             statement="W44 G0's measurement: 77 cells per dark scale, the seven runs pixel-identical, bar = half a code."),
        dict(id="manifest", title="the referee manifest and the planner adapter", clause="clause 3; Decision Log 2",
             source=ev("referees/plan.py", "referees/referees.json", "referees/test_plan.py", "referees/test_plan.txt",
                       "ladders/cells.json"),
             declared=dict(schema="w46-referees-1", scenes=m["scenes"], profiles=m["profiles"], sha256=m["sha256"],
                           pregateProbe=dict(count=lists["pregateProbe"]["count"],
                                             listSha256=D.sha(",".join(lists["pregateProbe"]["scenes"]).encode())),
                           exposure=dict(count=lists["exposure"]["count"],
                                         listSha256=D.sha(",".join(lists["exposure"]["scenes"]).encode())),
                           tests=14, fitMembers={"P rest": 4, "P inactive": 5, "C rest": 28, "F inactive": 2,
                                                 "F rest": 10, "T rest": 3, "C inactive": 14, "T inactive": 0}),
             statement="Six probe scenes per dark scale chosen by the charter's deterministic rule, re-derived by the adapter, "
                       "which refuses any other manifest, a ladder cell, a light profile or W44's schema. 66 of 72 non-holdout "
                       "T1 cells per scale remain to fit."),
        dict(id="rule", title="the landing rule, its synthetic cases and its rehearsal", clause="clause 2; Decision Log 3",
             source=ev("cuts/rule.py", "cuts/test_rule.py", "cuts/test_rule.txt", "rehearsal/rehearse.py",
                       "rehearsal/rehearsal.json", "rehearsal/rehearsal.txt", "rehearsal/d0219-cuts.json.gz",
                       "rehearsal/prefit-cuts.json.gz", "rehearsal/c02-cuts.json.gz"),
             declared=dict(constants=dict(budgetCount=RULE.BUDGET_COUNT, budgetCeilingB=RULE.BUDGET_CEILING_B,
                                          gatingMinCells=RULE.GATING_MIN_CELLS),
                           targets={t: [f"{s} {p}" for s, p in g] for t, g in RULE.TARGETS.items()},
                           reference=RULE.REFERENCE, syntheticCases=19, rehearsal=rehearsal),
             statement="W45's growth-only rule bound to d0219cd684bf, evaluated per dark profile, the verdict the weaker "
                       "profile's. Rehearsed on d0219cd684bf against itself (every gate cell unchanged), W43 G3's pre-fit "
                       "render (504c5348…, every cell unchanged too: the dark 0.5 documents differ in two tone ordinates "
                       "only) and W43's c02 (partial: UNMEASURED). The gated groups per scale are the charter's."),
        dict(id="tools", title="W46's tools, their red cases and their tests on d0219cd684bf", clause="clause 1",
             source=sorted({str(p.relative_to(W.ROOT)) for p in tool_files
                            if p.parent.name in ("cuts", "fit", "seal", "stage", "sheets")} |
                           {f"{R}/stage/rehearsal/rehearsal.json", f"{R}/stage/x60/evidence-g0.json",
                            f"{R}/rehearsal/port-proof.py", f"{R}/rehearsal/port-proof.txt", f"{R}/census-gate.py",
                            f"{R}/with-gpu.sh", f"{R}/declare.py", f"{R}/assemble.py",
                            f"{R}/test_declare.py", f"{R}/test_declare.txt"}),
             declared=dict(tests=TESTS, stageRehearsal=[stage_reh["verdict"], stage_reh["rows"], stage_reh["capturesIdentical"]]),
             statement="Each tool a parameterised port refusing W44's and W45's bindings, tested: the cuts port equals W45's "
                       "landing cut on every dark non-referee entry; the stage rehearsal of the shipped dark documents "
                       "reproduces the published rows (132 rows, 264 captures byte-identical); X60's evidence reads IDENTICAL."),
        dict(id="level", title="the level check (X61) and its rendered test", clause="X61; G0 (d)",
             source=ev("level/arith.ts", "level/level.py", "level/test_level.py", "level/test_level.txt",
                       "level/identity.py", "level/identity/identity.json", "level/candidates/control/candidate.json"),
             declared=dict(tests=11, identity=[ident["verdict"], ident["cells"], ident["pixelAndMeasurementIdentical"],
                                               ident["readsNoChange"]], projection=ident["projection"]),
             statement="A check, not a solver: L1 through the cuts' own cut_l1, the level rows, every excess attributed to "
                       "the stand-down the runtime's own arithmetic predicts. The shipped rung reproduces d0219cd684bf on "
                       "every ladder (i) cell as pixel and measurement identity and reads no change."),
        dict(id="targets", title="the three targets, their families and the predictions", clause="Decision Log 4",
             source=ev("targets/predict.py", "targets/predictions.json", "targets/predictions.txt"),
             declared=dict(predictedAggregates={k: dict(A=[round(x, 3) for x in v["A"].values()], halvedAt=v["halvedAt"])
                                                for k, v in pred["transmission"]["targets"].items()},
                           families={k: sorted(v) for k, v in families.items()}),
             statement="P (both poses) by the transmission, C rest by the rest scatter, F inactive by the receded scatter. "
                       "Predicted from the rows: the transmission alone halves P's aggregate near a = 0.7 at rest and 0.7 "
                       "receded, and moves C rest toward Apple at 0.8 and past it below; it moves F inactive away (it only "
                       "adds structure); the receded photo reaches ×1 near a′ 0.51–0.60, below the receded checker's clamp "
                       "(≈ 0.64), so P inactive is predicted not closable by the transmission at held ordinates."),
        dict(id="ladders", title="the ladders' protocol, cells and decisions", clause="clause 4; Design \"The ladders\"",
             source=ev("ladders/protocol.json", "ladders/cells.json", "ladders/ladder.py", "ladders/read.py",
                       "ladders/test_read.py", "ladders/test_read.txt"),
             declared=dict(rungs=1 + sum(len(lv["values"]) for lad in protocol["ladders"]
                                         for lv in lad.get("arms", []) + lad.get("levers", [])),
                           levers=levers, cellsPerLadder={k: [len(v["rest"]), len(v["inactive"])]
                                                          for k, v in cells["ladders"].items()}),
             statement="Three ladders, one leaf per rung from the snapshots, both scales, the listed cells only; the "
                       "control identical to d0219cd684bf or the ladders stop; the bars of clause 4 and the decisions "
                       "strike, narrow and name-target (X63)."),
        dict(id="startingPoint", title="the starting point, by hash", clause="Design \"The moves\"; X62",
             source=[f"{SHARED_R}/generations/index.json"],
             declared=dict(generation="d0219cd684bf", generationFileSha12=d0219["sha256"][:12],
                           documents={x["path"].split("/")[-1]: x["sha256"] for x in d0219["documents"]},
                           digests={s: W.DOCUMENT_DIGEST[s] for s in W.MOVING_SLOTS}),
             statement="One space, one starting point: d0219cd684bf, the snapshots of its two documents."),
        dict(id="references", title="the references, by hash", clause="Decision Logs 3, 5; X60",
             source=[f"{SHARED_R}/generations/index.json"],
             declared=dict(files={n: index["files"][f"{n}.json"]["sha256"] for n in
                                  ("d0219cd684bf", "ebc3d9105a4a", "85ad7f7e3e0d", "0eac5b294cc2")}),
             statement="d0219cd684bf is every regression row's and T1's reference; ebc3d9105a4a is what X60 holds the "
                       "light rows to; the two 0.5 generations are frozen (X41)."),
        dict(id="s1", title="S1's predicted direction", clause="Decision Log 5",
             source=ev("targets/predictions.json"),
             declared=dict(predictedMedians={p: {k: round(v["median"], 3) for k, v in x.items()}
                                             for p, x in pred["s1"]["perProfile"].items()},
                           sentence=pred["s1"]["sentence"]),
             statement="At held ordinates the level moves only where the clamp bites, so S1's dark medians (0.31 today) are "
                       "predicted unmoved down to a = 0.8, to rise slightly at 0.7 and far above 1 below it, through the "
                       "clamped thick cells. S1 is read and not gated; after a dark 0.25 refit with dark 0.5 frozen it reads "
                       "the refit's change plus the slider's."),
        dict(id="draft", title="the part-2 draft", clause="clause 1; Design \"The moves\"",
             source=ev("fit-declaration-draft.json"),
             declared=dict(stages=[mv["id"] for mv in draft["moves"]],
                           searchedLeaves=sum(len(f["leaves"]) for mv in draft["moves"] for f in mv["families"].values()),
                           targets=list(RULE.TARGETS)),
             statement="Two stages in the fit driver's shape, the tie rule, scale-separable rendering, the selection rule "
                       "and the landing rule; part 2 is this body changed only by the ladders' decisions."),
    ]
    sources = {}
    for it in items:
        for s in it["source"]:
            sources[s] = D.sha(D.source_bytes(s))
    sources[f"{R}/fit-declaration-draft.json"] = D.sha(W.DRAFT.read_bytes())
    sources[CHARTER] = D.sha(D.source_bytes(CHARTER))
    items[0]["source"].append(CHARTER)
    body = dict(schema="w46-declaration-1", charter=W.CHARTER_PIN,
                what="W46 G0 part 1: the declaration hashed before any ladder render, on the assembled tree",
                items=[{k: v for k, v in it.items() if k != "statement"} | {"statement": it["statement"]} for it in items],
                sources=dict(sorted(sources.items())))
    W.PART1.write_bytes(D.serialise(body))
    md = ["# W46 G0, part 1: the declaration", "",
          f"Charter `{W.CHARTER_PIN}`. Every item below is checked by `declare.py check` against its pinned sources "
          "(`declaration.json`); this twin is its readable form.", ""]
    for it in items:
        md += [f"### {it['id']}", "", f"**{it['title']}** ({it['clause']})", "", it["statement"], "",
               "```json", json.dumps(it["declared"], indent=1, ensure_ascii=False)[:4000], "```", ""]
    (HERE / "declaration.md").write_text("\n".join(md))
    print(f"declaration.json: {len(items)} items, {len(sources)} pinned sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
