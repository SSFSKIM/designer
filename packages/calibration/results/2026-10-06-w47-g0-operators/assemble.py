#!/usr/bin/env python3.12
"""W47 G0 (g): assemble part 1 (`declaration.json`) and its readable twin (`declaration.md`) from the
committed tools and evidence (charter clause 2; Decision Log 5). W46 G0's `assemble.py`
(`results/2026-10-05-w46-g0-declaration/assemble.py`), ported by copy and re-bound to W47.

What W47 changes:
  - **Clause 2's items.** W46's thirteen, with the manifest W46's by hash through W47's X69 loader, T1 as
    GATED (the owner test's `T1_DARK_*` block), and two more: `operators` (the two operators' leaves,
    laws, identities, grids, units and X68 domains, with the runtime and test files they land in
    pinned) and `diagnostic` (G0 (f)'s committed record and its chosen form).
  - **The parent's readings come through `declaration-inputs.json`.** The targets' predictions, S1's
    predicted direction and the diagnostic's chosen form are the parent's, not a tool's; this script
    REFUSES to write part 1 while that file holds a `TO FILL` anywhere, and part 1 pins the file.
  - **The pins are globbed, not listed.** Every tool, test, transcript and record under this evidence
    root (ladder candidates, logs, scratch and the part files themselves excepted) is pinned in the
    `tools` item, so a file a sibling child commits before the hash is picked up; every test's case
    count is read from its committed transcript (`test_<name>.txt` beside it, "Ran N tests") and
    `declare.py check` re-runs it.
  - **On the assembled tree only.** A working-tree source that is untracked or differs from HEAD
    refuses: part 1 is hashed on committed bytes (Decision Log 5: "hashed on the assembled tree after
    clause 1's landing is committed").

W46 G0's text follows, unchanged.

W46 G0 (e): assemble part 1 (`declaration.json`) and its readable twin (`declaration.md`) from the
committed tools and evidence. Every number an item declares is read here from the file that defines it,
and `declare.py check` re-derives each one independently; this script only writes the declaration's
form. It refuses once part 1 is hashed (the hash fixes the bytes; an amendment re-pins, never rewrites).

    python3.12 -B assemble.py
"""
from __future__ import annotations

import gzip
import json
import re
import subprocess
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
# Where the two operators land (G0 (a), (b)) and the tests that pin them (clause 1); pinned in part 1 at
# the assembled tree's bytes, which is why part 1 is hashed after clause 1's landing is committed.
RUNTIME = ("packages/renderer-webgpu/src/material.ts", "packages/renderer-webgpu/src/wgsl/optics.ts",
           "packages/renderer-webgpu/src/passes.ts", "packages/renderer-webgpu/src/pyramid.ts",
           "packages/platform-web/src/optics.ts", "packages/calibration/test/w31-identity-table.test.ts",
           "packages/renderer-webgpu/test/w31-gate-groups.test.ts",
           "packages/calibration/test/tier-coherence.test.ts")
# Never pinned as a tool: the part files and their records, and what renders write.
NOT_PINNED = {"declaration.json", "declaration.md", "declaration.sha256", "fit-declaration.json",
              "fit-declaration.sha256", "amendments.json", "fit-amendments.json", "census.jsonl", "runs.jsonl"}
NOT_PINNED_DIRS = {"logs", "candidates", "__pycache__"}
SUFFIXES = (".py", ".ts", ".sh", ".json", ".txt", ".gz", ".md")
# The charter's operator statements (Design "Operator 1" and "Operator 2", MARKED; X65, X66, X68).
OPERATOR_TEXT = {
    "operator 1": dict(
        law="farS = smoothstep(sizeSpanMax, sizeScatterSpanMax(dpr), span); alphaBase = clamp(tintAlpha + "
            "rampAtScale(tintAlphaFar1x, tintAlphaFar2x, dpr)·farS, 0, 1); sizedAlpha = alphaBase + "
            "sizeOcclusionGain·sizeK·(1 − alphaBase), per pixel on the WebGPU tier, per surface on the CSS tier "
            "(X65: mirrored)",
        identity="two plain value drops in MATERIAL_IDENTITY_TABLE, each at 0 (no gate leaf)",
        grid={"tintAlphaFar1x": [0, 0.1, 0.2, 0.3, 0.45, 0.6], "tintAlphaFar2x": [0, 0.1, 0.2, 0.3, 0.45, 0.6],
              "optics.regular.tintAlpha": [0.7, 0.8, 0.9], "sizeOcclusionGain": [0.05, 0.2, 0.4, 0.6],
              "sizeScatterSpanMax": [128, 160, 192, 256], "sizeScatterSpanMax2x": [128, 160, 192, 256]},
        units={"tintAlphaFar1x": "alpha per unit of farS", "tintAlphaFar2x": "alpha per unit of farS",
               "optics.regular.tintAlpha": "alpha", "sizeOcclusionGain": "share of (1 − alpha) at sizeK 1",
               "sizeScatterSpanMax": "CSS px (span)", "sizeScatterSpanMax2x": "CSS px (span)"}),
    "operator 2": dict(
        law="receded-only by document (X66): in the form G0 (f) chose — body: bodySample' = bodySample + "
            "sizeFineTapShare·(fineSample − bodySample), fineSample the source blurred at sizeFineTapSigma(dpr) "
            "CSS px; deep: scatterColour' = scatterColour + sizeFineTapShare·(deepFine − scatterColour), deepFine "
            "at √(σdeep² + sizeFineTapSigma(dpr)²); interior = mix(·, ·, kScatter); the CSS tier declines it",
        identity="one gate-group in MATERIAL_IDENTITY_TABLE: gate { sizeFineTapShare: 0 }, gated "
                 "[sizeFineTapSigma, sizeFineTapSigma2x]",
        grid={"sizeFineTapSigma": [1.5, 2, 3, 4, 6], "sizeFineTapSigma2x": [1.5, 2, 3, 4, 6],
              "sizeFineTapShare": [0.25, 0.5, 0.75, 1], "optics.regular.blurSigma": [1.25, 2, 3, 4]},
        units={"sizeFineTapSigma": "CSS px", "sizeFineTapSigma2x": "CSS px", "sizeFineTapShare": "share of the "
               "chosen component", "optics.regular.blurSigma": "device px (receded difference only)"}),
}


class Refused(SystemExit):
    pass


def ev(*names):
    return [f"{R}/{n}" for n in names]


def inputs() -> dict:
    """The parent's readings, refused while any `TO FILL` remains."""
    body = json.loads(D.INPUTS.read_text())
    left = D.placeholders({k: body.get(k) for k in ("targets", "s1", "diagnostic")})
    if left:
        raise Refused(f"assemble REFUSES: {D.INPUTS.name} still holds {D.PLACEHOLDER} at {', '.join(left)}; "
                      "the parent fills the targets' predictions, S1's direction and the diagnostic's form first")
    return body


def tool_files() -> list[Path]:
    out = []
    for p in sorted(HERE.rglob("*")):
        rel = p.relative_to(HERE)
        if (not p.is_file() or p.suffix not in SUFFIXES or p.name in NOT_PINNED
                or set(rel.parts[:-1]) & NOT_PINNED_DIRS or any(x.startswith(".") for x in rel.parts)):
            continue
        out.append(p)
    return out


def tests() -> list[list]:
    """[test module, directory, case count] for every `test_*.py` under the root, the count from its
    committed transcript; a test with no transcript refuses."""
    out, missing = [], []
    for p in tool_files():
        if not re.fullmatch(r"test_[a-z0-9_]+\.py", p.name):
            continue
        txt = p.with_suffix(".txt")
        m = re.search(r"^Ran (\d+) tests?", txt.read_text(), flags=re.M) if txt.exists() else None
        if m is None:
            missing.append(str(p.relative_to(HERE)))
            continue
        out.append([p.stem, str(p.parent.relative_to(HERE)) or ".", int(m.group(1))])
    if missing:
        raise Refused(f"assemble REFUSES: no committed transcript (\"Ran N tests\") beside {missing}")
    return out


def uncommitted(paths: list[str]) -> list[str]:
    """Working-tree sources that are untracked or differ from HEAD."""
    wt = [p for p in paths if "@" not in p]
    out = subprocess.run(["git", "-C", str(W.ROOT), "status", "--porcelain", "--", *wt], capture_output=True,
                         text=True, check=True).stdout
    return [ln[3:] for ln in out.splitlines() if ln.strip()]


def build(given: dict) -> tuple[dict, str]:
    B, T1, RULE, REF = D.cuts()
    m = REF.load_manifest()
    held = REF.referee_cells(m)
    pop = T1.population([W.DARK_025[0]])
    population = dict(cells=len(pop), **{s: sum(1 for _, sid in pop if T1.stratum(sid) == s) for s in "FTCP"},
                      **{part: sum(1 for _, sid in pop if T1.partition(W.DARK_025[0], sid, held) == part)
                         for part in ("gate", "holdout", "referee")})
    lists = REF.lists(m)
    reh = json.loads((HERE / "rehearsal/rehearsal.json").read_text())
    rehearsal = {}
    for x in reh["rows"]:
        t = json.loads(gzip.open(W.ROOT / x["source"]).read())["T1"]
        r = RULE.evaluate(t["cells"], t["missing"])
        rehearsal[x["label"]] = [r["verdict"]] + [[p["partition"]["unchanged"]["total"], len(p["awayBeyondB"]),
                                                   len(p["awayBeyondCeiling"])] for p in r["profiles"].values()]
    draft = json.loads(W.DRAFT.read_text())
    families = {}
    for mv in draft["moves"]:
        for f in mv["families"].values():
            for key, spec in f["leaves"].items():
                families.setdefault(spec["target"], []).append(f"{spec['slot']} {key}")
    protocol = json.loads(W.LADDER_PROTOCOL.read_text())
    rungs = 1 + sum(len(D.protocol_rungs(lad)) for lad in protocol["ladders"])
    cells = json.loads(W.LADDER_CELLS.read_text())
    index = json.loads((W.CAL / "results/generations/index.json").read_text())
    d0219 = index["files"]["d0219cd684bf.json"]
    ident = json.loads((HERE / "level/identity/identity.json").read_text())
    stage_reh = json.loads((HERE / "stage/rehearsal/rehearsal.json").read_text())
    bar = json.loads(W.BAR_PATH.read_text())
    diag = given["diagnostic"]
    record_path = HERE / diag["record"]
    record = json.loads(record_path.read_text())
    operators = {}
    for name, leaves in D.OPERATORS.items():
        slots = [s for s in W.MOVING_SLOTS if all(k in W.ADMITTED[s] for k in leaves)]
        operators[name] = dict(leaves=list(leaves), slots=slots,
                               domains={s: {k: D.domains_json(W.DOMAINS[s][k]) for k in leaves if k in W.DOMAINS[s]}
                                        for s in W.MOVING_SLOTS},
                               **OPERATOR_TEXT[name])
    files = tool_files()
    extra = lambda key: list(given[key].get("sources") or [])  # noqa: E731

    items = [
        dict(id="documents", title="the starting point is four document snapshots (X62)", clause="clause 2; X62",
             source=ev("bindings.py", "test_bindings.py", "test_bindings.txt") +
             [f"{R}/documents/{W.DOCUMENT_SHA[s][:12]}.json" for s in W.SLOTS],
             declared=dict(files={s: W.DOCUMENT_SHA[s][:12] for s in W.SLOTS}, digests=W.DOCUMENT_DIGEST,
                           commit=W.SNAPSHOT_COMMIT),
             statement="The dark and light 0.25 document bodies, each verified against its hash and its bytes at "
                       "the charter's merge c1f9bf84c. Every W47 tool builds from these and refuses the live "
                       "profiles/ as a start."),
        dict(id="t1", title="T1 as gated, its shared arithmetic, and its dark population", clause="clause 2; Decision Log 1",
             source=[f"{SHARED_R}/2026-10-03-w44-g1-refit/cuts/t1.py", f"{SHARED_R}/2026-10-03-w44-g1-refit/cuts/readings.py",
                     f"{SHARED_R}/2026-10-03-w44-g1-refit/cuts/test_t1.py", OWNER],
             declared=dict(populationPerDarkProfile=population, strata={k: list(v) for k, v in T1.STRATA.items()},
                           ratioClause=T1.RATIO_CLAUSE, equalTolerance=T1.EQUAL, ownerTest=OWNER,
                           ownerNeedles=['const T1_DARK_GATED_PROFILES = [\n  "apple-macos-27.0-1x-dark-standard-glass0.25",\n'
                                         '  "apple-macos-27.0-2x-dark-standard-glass0.25",',
                                         'const T1_DARK_REFERENCE = { active: "d0219cd684bf", receded: "f0b36a71772a" } as const;',
                                         'sha256: "0eb8ef7712adc0f7de53290190ab1b5d903d61806cc2039de0e99fb78de4c2cf"']),
             statement="T1 is GATED on the dark 0.25 profiles since W46 G2 against d0219cd684bf (§5.210); its statistic, "
                       "bar and arithmetic unchanged (W44 G1's t1.py by path, pinned). G2 re-baselines it in W45's "
                       "five-part order with the separate dark authorised list."),
        dict(id="bar", title="the bar: 0.5 code on every dark cell", clause="clause 2; Decision Log 1",
             source=[f"{SHARED_R}/2026-10-03-w44-g0-declaration/bar/t1-bar.json"],
             declared=dict(darkCells=sum(1 for x in bar["table"] if x["profile"] in W.DARK_025),
                           maxSeparation=bar["maxSeparation"]),
             statement="W44 G0's measurement: 77 cells per dark scale, the seven runs pixel-identical, bar = half a code."),
        dict(id="manifest", title="W46's referee manifest, by hash (X69)", clause="clause 4; X69; Decision Log 1",
             source=ev("referees/referees.py", "referees/test_referees.py", "referees/test_referees.txt",
                       "ladders/cells.json") +
             [f"{SHARED_R}/2026-10-05-w46-g0-declaration/referees/referees.json",
              f"{SHARED_R}/2026-10-05-w46-g0-declaration/referees/plan.py",
              f"{SHARED_R}/2026-10-05-w46-g0-declaration/ladders/cells.json"],
             declared=dict(schema=W.REFEREE_SCHEMA, scenes=m["scenes"], profiles=m["profiles"], sha256=m["sha256"],
                           pregateProbe=dict(count=lists["pregateProbe"]["count"],
                                             listSha256=D.sha(",".join(lists["pregateProbe"]["scenes"]).encode())),
                           exposure=dict(count=lists["exposure"]["count"],
                                         listSha256=D.sha(",".join(lists["exposure"]["scenes"]).encode()))),
             statement="w46-referees-1 loaded by its SHA-256 and never re-derived from W47's ladders; W46's adapter, "
                       "given only W46's frozen ladder list, still reproduces it; W47's membership, disjointness and "
                       "withholding checks hold. Six referee and seven holdout scenes per dark scale are withheld."),
        dict(id="rule", title="the landing rule, its synthetic cases and its rehearsal", clause="clause 3; Decision Log 1",
             source=sorted({str(p.relative_to(W.ROOT)) for p in files if p.parent.name == "rehearsal"} |
                           set(ev("cuts/rule.py", "cuts/test_rule.py", "cuts/test_rule.txt")) |
                           {x["source"] for x in reh["rows"]}),
             declared=dict(constants=dict(budgetCount=RULE.BUDGET_COUNT, budgetCeilingB=RULE.BUDGET_CEILING_B,
                                          gatingMinCells=RULE.GATING_MIN_CELLS),
                           targets={t: [f"{s} {p}" for s, p in g] for t, g in RULE.TARGETS.items()},
                           reference=RULE.REFERENCE, syntheticCases=19, rehearsal=rehearsal),
             statement="W45's growth-only rule as W46 bound it, verbatim: d0219cd684bf, bar 0.5, per dark profile, the "
                       "verdict the weaker profile's. Rehearsed on d0219cd684bf against itself and on W46's point A by "
                       "its committed gate cut (§5.209 §4's verdict reproduced); the gated groups per scale the charter's."),
        dict(id="tools", title="W47's tools, their red cases and their tests on d0219cd684bf", clause="clause 2",
             source=sorted({str(p.relative_to(W.ROOT)) for p in files} | {f"{R}/census-gate.py", f"{R}/with-gpu.sh"}),
             declared=dict(tests=tests(), stageRehearsal=[stage_reh["verdict"], stage_reh["rows"],
                                                          stage_reh["capturesIdentical"]]),
             statement="Each tool a port of W46's re-bound to W47 and refusing W44's, W45's and W46's bindings, tested: "
                       "the cuts port reproduces its reference cut; the stage rehearsal of the shipped dark documents "
                       "reproduces the published rows; X60's evidence reads IDENTICAL."),
        dict(id="level", title="the level check (X61) and its rendered test", clause="G0 (e); X61",
             source=sorted(str(p.relative_to(W.ROOT)) for p in files if "level" in p.relative_to(HERE).parts[:1]) +
             [str(p.relative_to(W.ROOT)) for p in sorted((HERE / "level/candidates/control").glob("candidate.json"))],
             declared=dict(identity=[ident["verdict"], ident["cells"], ident["pixelAndMeasurementIdentical"],
                                     ident["readsNoChange"]], projection=ident["projection"]),
             statement="A check, not a solver, knowing operator 1's per-pixel alpha. The shipped rung reproduces "
                       "d0219cd684bf on every ladder (i) cell as pixel and measurement identity and reads no change."),
        dict(id="operators", title="the two operators: laws, identities, grids, units, X68 domains",
             clause="clause 1; Design \"Operator 1\", \"Operator 2\"; X65, X66, X68; Decision Logs 2, 3",
             source=list(RUNTIME) + ev("bindings.py"),
             declared=operators,
             statement="Operator 1 grades tintAlpha per pixel on the far curve (two plain value drops, mirrored by the "
                       "CSS tier); operator 2 is the receded fine term in the form the diagnostic chose (one gate-group, "
                       "declined by the CSS tier). Their domains are the declaration's (X68), refused by the builder."),
        dict(id="diagnostic", title="the depth-split diagnostic and operator 2's form", clause="G0 (f); Decision Log 3 (v1.1)",
             source=sorted({str(record_path.relative_to(W.ROOT))} | set(extra("diagnostic")) | {f"{R}/{D.INPUTS.name}"}),
             declared=dict(record=str(record_path.relative_to(W.ROOT)), chosenForm=diag["chosenForm"],
                           population=sorted([x["cell"], x["scale"]] for x in record.get("cells") or [])),
             statement=diag["statement"]),
        dict(id="targets", title="the three targets, their families and the predictions", clause="Decision Log 4",
             source=sorted({f"{R}/{D.INPUTS.name}"} | set(extra("targets"))),
             declared=dict(given=given["targets"], families={k: sorted(v) for k, v in families.items()}),
             statement=given["targets"]["statement"]),
        dict(id="ladders", title="the ladders' protocol, cells and decisions", clause="clause 5; Design \"The ladders\"; X69, X70",
             source=sorted(str(p.relative_to(W.ROOT)) for p in files if p.relative_to(HERE).parts[0] == "ladders"),
             declared=dict(rungs=rungs, levers=D.lever_ids(protocol),
                           cellsPerLadder={k: [len(v["rest"]), len(v["inactive"])] for k, v in cells["ladders"].items()}),
             statement="Four ladders in candidate mode from the snapshots, both scales, the listed cells only, X69 "
                       "disjoint from the referees and X70's three-way check at every rung; the bars of clause 5 and "
                       "the decisions name-unfitted, name-target, body-width-first, narrow, strike and name-1x-gap "
                       "(and the outcomes fit and stop), as protocol.json names them."),
        dict(id="startingPoint", title="the starting point, by hash", clause="Design \"The moves\"; X62",
             source=[f"{SHARED_R}/generations/index.json"],
             declared=dict(generation="d0219cd684bf", generationFileSha12=d0219["sha256"][:12],
                           documents={x["path"].split("/")[-1]: x["sha256"] for x in d0219["documents"]},
                           digests={s: W.DOCUMENT_DIGEST[s] for s in W.MOVING_SLOTS}),
             statement="One space, one starting point: d0219cd684bf, the snapshots of its two documents."),
        dict(id="references", title="the references, by hash", clause="Decision Log 1; X52, X60",
             source=[f"{SHARED_R}/generations/index.json"],
             declared=dict(files={n: index["files"][f"{n}.json"]["sha256"] for n in
                                  ("d0219cd684bf", "ebc3d9105a4a", "85ad7f7e3e0d", "0eac5b294cc2")}),
             statement="d0219cd684bf is every regression row's and T1's reference; ebc3d9105a4a is what X60 holds the "
                       "light rows to; the two 0.5 generations are frozen (X41)."),
        dict(id="s1", title="S1's predicted direction", clause="Design \"The other rows\"",
             source=sorted({f"{R}/{D.INPUTS.name}"} | set(extra("s1"))),
             declared=dict(given=given["s1"]),
             statement=given["s1"]["sentence"]),
        dict(id="draft", title="the part-2 draft", clause="clause 2; Design \"The moves\"",
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
    body = dict(schema=D.PARTS["protocol"]["schema"], charter=W.CHARTER_PIN,
                what="W47 G0 part 1: the declaration hashed on the assembled tree after clause 1's landing is "
                     "committed and before any ladder render",
                items=[{k: v for k, v in it.items() if k != "statement"} | {"statement": it["statement"]} for it in items],
                sources=dict(sorted(sources.items())))
    md = ["# W47 G0, part 1: the declaration", "",
          f"Charter `{W.CHARTER_PIN}`. Every item below is checked by `declare.py check` against its pinned sources "
          "(`declaration.json`); this twin is its readable form.", ""]
    for it in items:
        md += [f"### {it['id']}", "", f"**{it['title']}** ({it['clause']})", "", str(it["statement"]), "",
               "```json", json.dumps(it["declared"], indent=1, ensure_ascii=False)[:4000], "```", ""]
    return body, "\n".join(md)


def main() -> int:
    if W.PART1_DIGEST.exists():
        raise Refused("assemble REFUSES: part 1 is hashed")
    given = inputs()
    body, md = build(given)
    dirty = uncommitted(list(body["sources"]))
    if dirty:
        raise Refused("assemble REFUSES: part 1 is assembled on committed bytes; untracked or modified: "
                      + ", ".join(dirty))
    W.PART1.write_bytes(D.serialise(body))
    (HERE / "declaration.md").write_text(md)
    print(f"declaration.json: {len(body['items'])} items, {len(body['sources'])} pinned sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
