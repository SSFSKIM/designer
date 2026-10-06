#!/usr/bin/env python3.12
"""W48 G0 (c): assemble part 1 (`declaration.json`) and its readable twin (`declaration.md`) from the committed
tools and evidence (charter clause 2; Decision Logs 2-5; X71-X73). W47's `assemble.py`
(`results/2026-10-06-w47-g0-operators/assemble.py`) is the pattern; this is W48's own file.

    python3.12 -B assemble.py

Every number an item declares is read here from the file that defines it, and `declare.py check` re-derives
each one independently; this script only writes the declaration's form. It refuses once part 1 is hashed,
once `ladders/verdicts.json` exists (X73: part 1 is hashed before any verdict), while
`declaration-inputs.json` holds a `TO FILL`, and on a working tree whose sources are untracked or modified
(part 1 is hashed on committed bytes, "on the ASSEMBLED tree", G0 (c)).

The items are clause 2's for this wave: `documents`, `t1`, `bar`, `manifest`, `rule`, `tools`, `level`,
`operators` (W47's bytes, by W47's part 1), `evidence` (X71), `targets`, `ladders` (the corrected protocol and
the verdict reader), `startingPoint`, `references`, `s1`, `draft`. The pins are globbed: every tool, test,
transcript and record under this root (the part files and their records excepted), and every W47 file W48
inherits or reads (`bindings.INHERITED`, `ladders/evidence.json`).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inherit  # noqa: E402,F401  (W48's bindings first, before any W47 tool)
import bindings as W  # noqa: E402

D = inherit.own("declare.py", "w48_declare")
R = HERE.relative_to(W.ROOT).as_posix()
SHARED_R = "packages/calibration/results"
OWNER = f"packages/calibration/test/adopted-thresholds.test.ts@{W.CHARTER_COMMIT}"
CHARTER = f"{W.CHARTER_PATH}@{W.CHARTER_COMMIT}"
NOT_PINNED = {"declaration.json", "declaration.md", "declaration.sha256", "fit-declaration.json",
              "fit-declaration.sha256", "amendments.json", "fit-amendments.json", "census.jsonl", "runs.jsonl",
              "verdicts.json", "verdicts.txt"}
NOT_PINNED_DIRS = {"logs", "candidates", "__pycache__"}
SUFFIXES = (".py", ".ts", ".sh", ".json", ".txt", ".gz", ".md")


class Refused(SystemExit):
    pass


def rel(p: Path) -> str:
    return str(Path(p).relative_to(W.ROOT))


def ev(*names):
    return [f"{R}/{n}" for n in names]


def inputs() -> dict:
    body = json.loads(D.INPUTS.read_text())
    left = D.placeholders({k: body.get(k) for k in ("targets", "s1")})
    if left:
        raise Refused(f"assemble REFUSES: {D.INPUTS.name} still holds {D.PLACEHOLDER} at {', '.join(left)}")
    return body


def tool_files() -> list[Path]:
    out = []
    for p in sorted(HERE.rglob("*")):
        r = p.relative_to(HERE)
        if (not p.is_file() or p.suffix not in SUFFIXES or p.name in NOT_PINNED
                or set(r.parts[:-1]) & NOT_PINNED_DIRS or any(x.startswith(".") for x in r.parts)):
            continue
        out.append(p)
    return out


def ran(txt: Path) -> int | None:
    m = re.search(r"^Ran (\d+) tests?", txt.read_text(), flags=re.M) if txt.exists() else None
    return int(m.group(1)) if m else None


def tests() -> list[list]:
    """[module, directory, count] for every W48 `test_*.py`, the count from its committed transcript."""
    out, missing = [], []
    for p in tool_files():
        if not re.fullmatch(r"test_[a-z0-9_]+\.py", p.name):
            continue
        n = ran(p.with_suffix(".txt"))
        if n is None:
            missing.append(rel(p))
            continue
        out.append([p.stem, str(p.parent.relative_to(HERE)) or ".", n])
    if missing:
        raise Refused(f"assemble REFUSES: no committed transcript (\"Ran N tests\") beside {missing}")
    return out


def inherited_tests() -> list[list]:
    """[W47-relative test path, count] for every inherited W47 test run under W48's bindings, from its committed
    transcript `tools/inherited/<dir>__<test>.txt`."""
    out = []
    for txt in sorted((HERE / "tools" / "inherited").glob("*__test_*.txt")):
        d, t = txt.stem.split("__", 1)
        n = ran(txt)
        if n is None:
            raise Refused(f"assemble REFUSES: {rel(txt)} has no \"Ran N tests\"")
        out.append([f"{d}/{t}.py" if d != "." else f"{t}.py", n])
    return out


def uncommitted(paths: list[str]) -> list[str]:
    wt = [p for p in paths if "@" not in p]
    got = subprocess.run(["git", "-C", str(W.ROOT), "status", "--porcelain", "--", *wt], capture_output=True,
                         text=True, check=True).stdout
    return [ln[3:] for ln in got.splitlines() if ln.strip()]


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
    import gzip  # noqa: PLC0415
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
    index = json.loads((W.CAL / "results/generations/index.json").read_text())
    d0219 = index["files"]["d0219cd684bf.json"]
    ident = json.loads((W.W47_G0 / "level/identity/identity.json").read_text())
    proof = json.loads((HERE / "level/identity-reproof.json").read_text())
    bar = json.loads(W.BAR_PATH.read_text())
    arch = json.loads((HERE / "archive/archive.json").read_text())
    inventory = json.loads((HERE / "archive/inventory.json").read_text())
    pins = json.loads(W.LADDER_EVIDENCE.read_text())
    w47_lines = [ln.split()[0] for ln in (W.W47_G0 / "declaration.sha256").read_text().splitlines() if ln.strip()]
    w47_part1 = json.loads((W.W47_G0 / "declaration.json").read_text())
    w47_ops = next(x for x in w47_part1["items"] if x["id"] == "operators")["declared"]
    files = tool_files()
    inherited = sorted(rel(p) for p in W.INHERITED)
    w47_read = sorted(set(pins["w47"]) | {rel(W.W47_G0 / "declaration.sha256"), rel(W.W47_G0 / "declaration.json"),
                                          rel(W.W47_G0 / "level/identity/identity.json")})
    ev_paths = protocol["evidence"]
    mine = lambda *dirs: sorted(rel(p) for p in files if p.relative_to(HERE).parts[0] in dirs)  # noqa: E731

    items = [
        dict(id="documents", title="the starting point is four document snapshots (X62), at this charter's merge",
             clause="clause 2; X62",
             source=ev("bindings.py", "inherit.py", "test_bindings.py", "test_bindings.txt") +
             [f"{R}/documents/{W.DOCUMENT_SHA[s][:12]}.json" for s in W.SLOTS] +
             [rel(W.W47_G0 / "documents" / f"{W.DOCUMENT_SHA[s][:12]}.json") for s in W.SLOTS],
             declared=dict(files={s: W.DOCUMENT_SHA[s][:12] for s in W.SLOTS}, digests=W.DOCUMENT_DIGEST,
                           commit=W.SNAPSHOT_COMMIT),
             statement="The dark and light 0.25 document bodies at the charter's merge 78d0211e0, each verified "
                       "against its hash and its bytes there, and equal to W47's snapshots byte for byte (no 0.25 "
                       "document moved since c1f9bf84c). Every W48 tool builds from these and refuses the live "
                       "profiles/ as a start."),
        dict(id="t1", title="T1 as gated, its shared arithmetic, and its dark population",
             clause="clause 2; Decision Log 1",
             source=[f"{SHARED_R}/2026-10-03-w44-g1-refit/cuts/t1.py", f"{SHARED_R}/2026-10-03-w44-g1-refit/cuts/readings.py",
                     f"{SHARED_R}/2026-10-03-w44-g1-refit/cuts/test_t1.py", OWNER],
             declared=dict(populationPerDarkProfile=population, strata={k: list(v) for k, v in T1.STRATA.items()},
                           ratioClause=T1.RATIO_CLAUSE, equalTolerance=T1.EQUAL, ownerTest=OWNER,
                           ownerNeedles=['const T1_DARK_GATED_PROFILES = [\n  "apple-macos-27.0-1x-dark-standard-glass0.25",\n'
                                         '  "apple-macos-27.0-2x-dark-standard-glass0.25",',
                                         'const T1_DARK_REFERENCE = { active: "d0219cd684bf", receded: "f0b36a71772a" } as const;',
                                         'sha256: "0eb8ef7712adc0f7de53290190ab1b5d903d61806cc2039de0e99fb78de4c2cf"']),
             statement="T1 is GATED on the dark 0.25 profiles since W46 G2 against d0219cd684bf (§5.210); its "
                       "statistic, bar and arithmetic unchanged (W44 G1's t1.py by path, pinned). G2 re-baselines it "
                       "in the five-part order with the separate dark authorised list."),
        dict(id="bar", title="the bar: 0.5 code on every dark cell", clause="clause 2; Decision Log 1",
             source=[f"{SHARED_R}/2026-10-03-w44-g0-declaration/bar/t1-bar.json"],
             declared=dict(darkCells=sum(1 for x in bar["table"] if x["profile"] in W.DARK_025),
                           maxSeparation=bar["maxSeparation"]),
             statement="W44 G0's measurement: 77 cells per dark scale, the seven runs pixel-identical, bar = half a code."),
        dict(id="manifest", title="W46's referee manifest, by hash (X69)", clause="clause 5; X69; Decision Log 1",
             source=sorted(set(mine("referees")) | {rel(W.W47_G0 / "referees/referees.py"), rel(W.LADDER_CELLS)} |
                           {f"{SHARED_R}/2026-10-05-w46-g0-declaration/referees/referees.json",
                            f"{SHARED_R}/2026-10-05-w46-g0-declaration/referees/plan.py",
                            f"{SHARED_R}/2026-10-05-w46-g0-declaration/ladders/cells.json"}),
             declared=dict(schema=W.REFEREE_SCHEMA, scenes=m["scenes"], profiles=m["profiles"], sha256=m["sha256"],
                           pregateProbe=dict(count=lists["pregateProbe"]["count"],
                                             listSha256=D.sha(",".join(lists["pregateProbe"]["scenes"]).encode())),
                           exposure=dict(count=lists["exposure"]["count"],
                                         listSha256=D.sha(",".join(lists["exposure"]["scenes"]).encode()))),
             statement="w46-referees-1 loaded by its SHA-256 through W47's X69 loader (inherited by path); W46's "
                       "adapter, given only W46's frozen ladder list, still reproduces it; the six referee and seven "
                       "holdout scenes per dark scale are withheld from every fit, stage, gate read and sheet."),
        dict(id="rule", title="the landing rule, its synthetic cases and its rehearsal", clause="clause 4; Decision Log 1",
             source=sorted(set(mine("rehearsal")) | {rel(W.CUTS_SOURCE / "rule.py"), f"{R}/tools/inherited/cuts__test_rule.txt"} |
                           {x["source"] for x in reh["rows"]}),
             declared=dict(constants=dict(budgetCount=RULE.BUDGET_COUNT, budgetCeilingB=RULE.BUDGET_CEILING_B,
                                          gatingMinCells=RULE.GATING_MIN_CELLS),
                           targets={t: [f"{s} {p}" for s, p in g] for t, g in RULE.TARGETS.items()},
                           reference=RULE.REFERENCE, syntheticCases=19, rehearsal=rehearsal),
             statement="W45's growth-only rule as W46 and W47 bound it, W47's cuts/rule.py inherited by path: "
                       "d0219cd684bf, bar 0.5, per dark profile, the verdict the weaker profile's. Rehearsed under "
                       "W48's bindings on d0219cd684bf against itself and on W46's point A by its committed gate cut "
                       "(§5.209 §4 and §5.211 §6 reproduced); the gated groups per scale the charter's."),
        dict(id="tools", title="W48's tools, W47's inherited by path, their tests on d0219cd684bf", clause="clause 2",
             source=sorted({rel(p) for p in files} | set(inherited)),
             declared=dict(tests=tests(), inheritedTests=inherited_tests(), inherited=inherited),
             statement="W48's own tools (bindings, inherit, the archive and replay, the census and launcher copies, "
                       "the builder and seal copies, declare and assemble, the verdict reader) with their tests; W47's "
                       "cuts, fit, stage, sheets, referees, level and ladder reader inherited BY PATH under W48's "
                       "bindings, pinned byte-identical, their tests re-run under W48's bindings; X60 by evidence."),
        dict(id="level", title="the level check (X61), re-bound; the shipped rung's identity re-proven",
             clause="G0 (b); X61",
             source=sorted(set(mine("level")) | {rel(W.W47_G0 / "level/identity/identity.json"),
                                                 rel(W.W47_G0 / "level/level.py"), rel(W.W47_G0 / "level/arith.ts")}),
             declared=dict(identity=[ident["verdict"], ident["cells"], ident["pixelAndMeasurementIdentical"],
                                     ident["readsNoChange"]], projection=ident["projection"], reproof=proof["verdict"]),
             statement="W47's level check, inherited by path, knowing operator 1's per-pixel alpha. The shipped rung's "
                       "identity is W47's committed record (130 of 130, reads no change), re-proven against the "
                       "archive's d0219cd684bf reference subset; its unexplained excesses are read beside L1, ungated."),
        dict(id="operators", title="the two operators are W47's bytes (clause 1)", clause="clause 1; X65, X66, X68",
             source=list(D.RUNTIME) + [rel(W.W47_G0 / "declaration.json"), rel(W.W47_G0 / "declaration.sha256")],
             declared=dict(w47PartOne=dict(sha256=w47_lines[-1], supersedes=w47_lines[0]), w47Operators=w47_ops,
                           runtime={p: D.sha((W.ROOT / p).read_bytes()) for p in D.RUNTIME}),
             statement="Operator 1 (tintAlphaFar1x / 2x) and operator 2 (sizeFineTapShare with its two widths, the body "
                       "form) as W47's part 1 states them (2d4a2c7f…, its operators item verbatim), landed inert on main "
                       "at 429d0a78; every runtime file and identity-table test byte-identical to this charter's merge. "
                       "Any runtime byte that moves before G1's freeze closes the child."),
        dict(id="evidence", title="W47's ladder evidence, archived, replayed and pinned (X71)",
             clause="G0 (a); X71; Decision Log 2",
             source=sorted(set(mine("archive", "replay")) | {rel(W.LADDER_EVIDENCE)} | set(pins["w47"])),
             declared=dict(release=arch["release"]["tag"], asset=arch["asset"]["name"], sha256=arch["asset"]["sha256"],
                           bytes=arch["asset"]["bytes"], inventorySha256=arch["inventory"]["sha256"],
                           entries={k: len(inventory[k]) for k in ("ladders", "drive", "reference")},
                           w47PartOne=[pins["w47PartOne"]["superseded"], pins["w47PartOne"]["current"]]),
             statement="The ladder tree, the drive's logs and the canonical d0219cd684bf reference subset as release "
                       "w47-ladders-archive by SHA-256; W47's read.py and reread.py replayed read-only from the fetched "
                       "archive with the raw root and the live canonical tree denied, equal to W47's committed readings "
                       "byte for byte, the control 142 of 142; W47's readings, protocol, diagnostic, both part-1 hashes "
                       "and amendment record pinned. The verdicts are read from these files by key."),
        dict(id="targets", title="the three targets, their families and the predictions", clause="Decision Log 5",
             source=sorted({f"{R}/{D.INPUTS.name}"} | set(given["targets"].get("sources") or [])),
             declared=dict(given=given["targets"], families={k: sorted(v) for k, v in families.items()}),
             statement=given["targets"]["statement"]),
        dict(id="ladders", title="the corrected protocol (Decision Log 3) and the verdict reader",
             clause="clause 3; Decision Log 3; X72, X73",
             source=sorted(set(mine("ladders")) | {ev_paths[k]["path"] for k in ("rungs", "results", "reread", "cells")}),
             declared=dict(bars=protocol["bars"], separation=protocol["separation"], offGrid=protocol["offGrid"],
                           expected=protocol["expected"], parentRulings=protocol["rulings"],
                           readerSha256=D.sha(D.READER.read_bytes())),
             statement="W47's rungs, read by key from its re-read and results (no ladder rendered), under Decision "
                       "Log 3's bars: (a) operator 1 the landing rule's partition with `unchanged` admitted on "
                       "over-Apple cells; (b) operator 2 on T1-fine, R >= 0.5, the whole band beside; (c) the joint, "
                       "deciding only name-target; no precedence kind, `hold` beside `strike`; the sigma 2 and share 0.5 "
                       "one-scale rungs off the grid. The verdicts are written by ladders/verdicts.py after this hash."),
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
        dict(id="s1", title="S1's predicted direction", clause="Decision Log 5",
             source=[f"{R}/{D.INPUTS.name}"], declared=dict(given=given["s1"]), statement=given["s1"]["sentence"]),
        dict(id="draft", title="the part-2 draft, narrowed (Decision Log 4)", clause="clause 2; Design \"The moves\"",
             source=ev("fit-declaration-draft.json") + [rel(W.W47_G0 / "fit-declaration-draft.json")],
             declared=dict(stages=[mv["id"] for mv in draft["moves"]],
                           searchedLeaves=sum(len(f["leaves"]) for mv in draft["moves"] for f in mv["families"].values()),
                           targets=list(RULE.TARGETS), stageSizes=draft["stageSizes"]),
             statement="W47's draft narrowed by the ladders as Design \"The moves\" states: stage 1 the span law at 432 "
                       "points (72 renders per scale; 108 / 18 with the gain held), the second tap off, then W46's rest "
                       "scatter; stage 2 the receded transmission x the fine term x the body width at 114 points (42 per "
                       "scale), then W46's receded scatter. Part 2 is this body changed only by the decisions the "
                       "verdicts support."),
    ]
    sources = {}
    for it in items:
        for s in it["source"]:
            sources[s] = D.sha(D.source_bytes(s))
    sources[CHARTER] = D.sha(D.source_bytes(CHARTER))
    items[0]["source"].append(CHARTER)
    body = dict(schema=D.PARTS["protocol"]["schema"], charter=W.CHARTER_PIN,
                what="W48 G0 part 1: the declaration hashed on the assembled tree after the evidence was archived, "
                     "replayed and pinned (a) and the tools, the reader and the draft were committed (b), before any "
                     "verdict exists",
                items=[{k: v for k, v in it.items() if k != "statement"} | {"statement": it["statement"]} for it in items],
                sources=dict(sorted(sources.items())))
    md = ["# W48 G0, part 1: the declaration", "",
          f"Charter `{W.CHARTER_PIN}`. Every item below is checked by `declare.py check` against its pinned sources "
          "(`declaration.json`); this twin is its readable form.", ""]
    for it in items:
        md += [f"### {it['id']}", "", f"**{it['title']}** ({it['clause']})", "", str(it["statement"]), "",
               "```json", json.dumps(it["declared"], indent=1, ensure_ascii=False)[:4000], "```", ""]
    return body, "\n".join(md)


def main() -> int:
    if W.PART1_DIGEST.exists():
        raise Refused("assemble REFUSES: part 1 is hashed")
    if W.VERDICTS.exists():
        raise Refused("assemble REFUSES: ladders/verdicts.json exists; part 1 is assembled and hashed before any "
                      "verdict (X73)")
    given = inputs()
    body, md = build(given)
    dirty = uncommitted(list(body["sources"]))
    if dirty:
        raise Refused("assemble REFUSES: part 1 is assembled on committed bytes; untracked or modified: "
                      + ", ".join(dirty[:20]))
    W.PART1.write_bytes(D.serialise(body))
    (HERE / "declaration.md").write_text(md)
    print(f"declaration.json: {len(body['items'])} items, {len(body['sources'])} pinned sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
