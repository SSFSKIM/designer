"""W44 G0: the two hashed parts of the declaration (charter clause 1; X50). W43 G0's pattern
(`results/2026-10-01-w43-g0-declaration/declare.py`), not its code.

Part 1, the mechanism-check protocol, and the part-2 DRAFT (`fit-declaration-draft.json`, pinned
as one of part 1's sources, so the one hash covers both), before any ladder render:

    python3.12 -B declare.py check     # exit 0 consistent (pending items reported), 1 on a mismatch
    python3.12 -B declare.py hash      # refuses (exit 2) while an item is pending or once hashed
    python3.12 -B declare.py amend --reason TEXT --cause COMMIT PIN [PIN ...]

Part 2, the fit declaration (`fit-declaration.json`), after the ladders and before any fit render:

    python3.12 -B declare.py check-fit # the validated diff against the draft (below)
    python3.12 -B declare.py hash-fit  # refuses before part 1 is hashed, on any invalid change, once hashed
    python3.12 -B declare.py amend-fit --reason TEXT --cause COMMIT   # the one content amendment (below)

`declaration.json` declares each item once, points at its source files and pins every source by
SHA-256 (a path suffixed `@<commit>` is read at that commit: the charter). `check` re-reads every
pin and re-derives what each item states as a number or a list from the files that define it:
T1's population and constants and its tests; the bar and the port's proof; the rehearsal's
readings; the referee lists and their red cases; the ledger witness; the ladder protocol (every
fixed cell declared on both light profiles and neither a referee nor holdout, every leaf one its
slot's 0.5 document names, every rung inside its domain, no heavy width below the chain's level-1
width, the control candidate at c05's four digests); the regression references against the
generation index; and the draft (every grid inside its domain, every leaf owned by a ladder, the
rehearsed numbers against the rehearsal). `declaration.md` carries every item, in order.

**Part 2 is a validated diff.** `fit-declaration.json` is the draft's body plus a `changes` list.
`check-fit` applies those changes to the draft, each only if the ladder results
(`ladders/results.json`) support it, and the result must equal part 2's body exactly. A change is
one of the protocol's enumerated decisions and nothing else:
  strike        remove a draft leaf whose ladder the results strike (flat, or moved a 1x capture),
                and the family with it when its last leaf goes;
  strikeFamily  remove family C when the results strike L3 (its 1x inert setting not proven);
  inert         replace C's PENDING inert setting with L3's citation; the value stays 0;
  narrow        replace a grid by a non-empty subset of itself inside its ladder's non-flat range.
Anything else — a changed prediction, a widened or shifted grid, a new leaf, a strike the ladder
did not make — is refused (`test_declare.py` holds the red cases).

**Amendments**, W43's rule: an amendment re-pins named moved sources and changes nothing else; it is
refused unless the part is hashed, its chain verifies, every named pin moved and no other did, and
no render evidence exists for it: part 1's once ANY ladder render exists (`ladders/runs.jsonl`
records a launch, or the ladder scratch holds a matrix), part 2's once any fit render exists
(G1's evidence directory or its scratch).

**Part 2's one amendment (W44 G1 step 0; charter v1.3, Decision Log 7, `ea487a17`).** Decision Log
7 rules five items before any fit render, executed as ONE amendment of part 2 that changes its
CONTENT, not only its pins, so `amend-fit` is this verb and not part 1's:

    python3.12 -B declare.py amend-fit --reason TEXT --cause COMMIT

It writes `fit-amendments.json` (part 2's amendment record, beside part 1's `amendments.json`) with
the superseded hash, the reason, the cause, and the content diff: a list of operations, each an
`add` or a `replace` at one path of part 2's body, each citing the ruling (1-5) it executes, with
its `from` and `to`. `RULINGS` below is the only place a ruling's paths are stated, and
`validate_ops` refuses an operation outside its ruling's paths, an unknown ruling, a removal, a
path touched twice, and a ruling with no operation, so the diff carries exactly the five rulings
and nothing else (`test_amend_fit.py`). The rulings' own pins (G1's T1 readers and the builder
with their red cases) are added as `sources` entries under the ruling they implement, so
`check-fit` verifies their bytes and runs their tests. `amend-fit` refuses once any fit render
exists (`fit_evidence`: a launch in G1's `fit/runs.jsonl`, or a matrix or capture under the fit
scratch; G1's evidence directory existing is not a render) and refuses a second amendment.

`check-fit` then verifies the chain by reverting the operations, which must rebuild the superseded
part 2 byte for byte, and validates that rebuilt body as the draft's diff exactly as before.

This file is one of part 1's pinned sources and the amendment had to move it. Part 1 cannot be
amended (its ladders exist), so `fit-amendments.json` records that move as `partOnePins`
{path: {from, to}}, and part 1's `check` accepts a pin of `PART_ONE_REPINNABLE` (this file
alone) exactly when the record names its pinned hash as `from` and its bytes as `to`. Part 1's
declaration and its hash do not move.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REL = HERE.relative_to(ROOT).as_posix()
CHARTER_PIN = "docs/doperpowers/specs/2026-10-03-w44-texture-at-0-25.md@0ee27ae2"
sys.path.insert(0, str(HERE / "cuts"))
sys.path.insert(0, str(HERE / "referees"))

PARTS = {
    "protocol": dict(declaration=HERE / "declaration.json", twin=HERE / "declaration.md",
                     digest=HERE / "declaration.sha256", amendments=HERE / "amendments.json",
                     schema="w44-declaration-1"),
    "fit": dict(declaration=HERE / "fit-declaration.json", twin=None,
                digest=HERE / "fit-declaration.sha256", amendments=HERE / "fit-amendments.json",
                schema="w44-fit-declaration-1"),
}
DRAFT = HERE / "fit-declaration-draft.json"
PROTOCOL = HERE / "ladders" / "protocol.json"
RESULTS = HERE / "ladders" / "results.json"
LADDER_RUNS = HERE / "ladders" / "runs.jsonl"
LADDER_SCRATCH = Path.home() / "vitrea-w44" / "g0-ladders"
FIT_EVIDENCE = [ROOT / "packages/calibration/results/2026-10-03-w44-g1-refit",
                Path.home() / "vitrea-w44" / "g1-scratch"]
G1 = FIT_EVIDENCE[0]
G1_REL = G1.relative_to(ROOT).as_posix()
G1_SCRATCH = FIT_EVIDENCE[1]
PART_ONE_REPINNABLE = (f"{REL}/declare.py",)
AMENDMENT_TESTS = (f"{REL}/test_amend_fit.py",)
CHARTER_PATH = "docs/doperpowers/specs/2026-10-03-w44-texture-at-0-25.md"
CHAIN_LEVEL_1 = 1.542
LIGHT_025 = ("apple-macos-27.0-1x-light-standard-glass0.25", "apple-macos-27.0-2x-light-standard-glass0.25")

sha = lambda data: hashlib.sha256(data).hexdigest()  # noqa: E731


def source_bytes(key):
    if "@" in key:
        path, commit = key.rsplit("@", 1)
        return subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"], check=True,
                              capture_output=True).stdout
    return (ROOT / key).read_bytes()


def ev(rel):
    return HERE / rel


class Check:
    def __init__(self):
        self.failures = []

    def eq(self, what, got, want):
        if got != want:
            self.failures.append(f"{what}: found {got!r}, declared {want!r}")

    def true(self, what, ok):
        if not ok:
            self.failures.append(what)


def run(*argv, cwd=None):
    r = subprocess.run([sys.executable, "-B", *map(str, argv)], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout + r.stderr


def r4(x):
    return None if x is None else round(x, 4)


# ---------------------------------------------------------------------------------------------
# Part 1
# ---------------------------------------------------------------------------------------------
def structure(c, d):
    items = d["items"]
    ids = [it["id"] for it in items]
    c.eq("item ids are unique", len(set(ids)), len(ids))
    used = set()
    for it in items:
        for key in ("id", "title", "clause", "source"):
            c.true(f"{it.get('id')}: no '{key}'", key in it)
        c.true(f"{it['id']}: an item either declares its reading or is pending, never both or neither",
               ("declared" in it) != ("pending" in it))
        if "pending" in it:
            c.true(f"{it['id']}: a pending item names what it waits on", bool(it["pending"].get("on")))
        for s in it["source"]:
            c.true(f"{it['id']}: source {s} is not pinned", s in d["sources"])
            used.add(s)
    for s in d["sources"]:
        c.true(f"sources: {s} is pinned but no item points at it", s in used)
    repins = part_one_repins()
    for key, want in d["sources"].items():
        try:
            got = sha(source_bytes(key))
        except (OSError, subprocess.CalledProcessError) as err:
            c.failures.append(f"pin {key}: unreadable ({err})")
            continue
        if got != want and accepted_repin(key, want, got, repins):
            continue
        c.eq(f"pin {key}", got, want)
    return {it["id"]: it for it in items}


def part_one_repins() -> dict:
    """Part 1 pins part 2's amendment moved, as `fit-amendments.json` records them."""
    out = {}
    for a in amendments("fit"):
        out.update(a.get("partOnePins") or {})
    return out


def accepted_repin(key, pinned, now, repins) -> bool:
    """A moved part-1 pin is accepted only for `PART_ONE_REPINNABLE` and only when part 2's
    amendment record names exactly that move, from the pinned hash to the bytes on disk."""
    move = repins.get(key)
    return key in PART_ONE_REPINNABLE and bool(move) and move.get("from") == pinned and move.get("to") == now


def twin(c, items, path):
    text = path.read_text()
    heads = re.findall(r"^### (\S+)", text, flags=re.M)
    c.eq(f"{path.name}: its item headings, in order", heads, list(items))
    sections = dict(zip(heads, re.split(r"^### \S+.*$", text, flags=re.M)[1:]))
    for it in items.values():
        body = sections.get(it["id"], "")
        if "pending" in it:
            c.true(f"{path.name}, {it['id']}: not marked PENDING ({it['pending']['on']})",
                   f"PENDING ({it['pending']['on']})" in body)
        else:
            c.true(f"{path.name}, {it['id']}: a declared item is marked PENDING", "PENDING" not in body)


def check_t1(c, it):
    import bed as B
    import plan
    import t1
    d = it["declared"]
    held = plan.referee_cells(plan.load_manifest())
    for p in LIGHT_025:
        pop = t1.population([p])
        got = dict(cells=len(pop))
        for s in ("F", "C", "P"):
            got[s] = sum(1 for _, sid in pop if t1.stratum(sid) == s)
        for part in ("gate", "holdout", "referee"):
            got[part] = sum(1 for _, sid in pop if t1.partition(p, sid, held) == part)
        c.eq(f"t1: population of {p}", got, d["populationPerLightProfile"])
    c.eq("t1: strata", {k: list(v) for k, v in t1.STRATA.items()}, d["strata"])
    c.eq("t1: ratio clause", t1.RATIO_CLAUSE, d["ratioClause"])
    c.eq("t1: g = 0 tolerance", t1.EQUAL, d["equalTolerance"])
    c.eq("t1: change states", sorted(t1.CHANGE), sorted(d["changePrecedence"]))
    c.eq("t1: gated profiles", list(t1.GATED_PROFILES), d["gated"]["profiles"])
    c.eq("t1: gated tier", t1.GATED_TIER, d["gated"]["tier"])
    rc, out = run("-m", "unittest", "test_t1", cwd=HERE / "cuts")
    c.true(f"t1: test_t1 does not pass ({out.strip().splitlines()[-1] if out.strip() else rc})", rc == 0)
    del B


def check_bar(c, it):
    d = it["declared"]
    bar = json.loads(ev("bar/t1-bar.json").read_text())
    proof = json.loads(ev("port/proof.json").read_text())
    c.eq("bar: cells", bar["cells"], d["cells"])
    c.eq("bar: gated cells", sum(1 for x in bar["table"] if x["gated"]), d["gatedCells"])
    c.eq("bar: range in codes", [r4(x) for x in bar["barCodesRange"]], d["barCodes"])
    c.eq("bar: largest separation", bar["maxSeparation"], d["maxSeparation"])
    c.eq("bar: read, not gated", bar["readNotGated"], d["readNotGated"])
    c.eq("bar: archive inventory", bar["archive"]["inventorySha256"], d["archiveInventory"])
    c.eq("bar: its tools are the pinned files", bar["tools"],
         {n: sha(p.read_bytes()) for n, p in (("t1-bar.py", ev("bar/t1-bar.py")),
                                               ("interior.py", ev("port/interior.py")),
                                               ("prove.py", ev("port/prove.py")))})
    c.eq("port: rows compared", proof["rowsCompared"], d["proof"]["rows"])
    c.true(f"port: worst {proof['worstAbsDiff']} not below {d['proof']['tolerance']}",
           proof["worstAbsDiff"] < d["proof"]["tolerance"] and not proof["misses"])
    c.eq("port: its tools are the pinned files", proof["port"],
         {n: sha(ev(f"port/{n}").read_bytes()) for n in ("interior.py", "prove.py")})


def check_rehearsal(c, it):
    d = it["declared"]
    r = json.loads(ev("rehearsal/rehearsal-r2.json").read_text())
    c.eq("rehearsal: baseline reproduced", (r["baseline"]["reproduced"], r["baseline"]["cellsChecked"]),
         (True, d["baselineCells"]))
    c.eq("rehearsal: baseline file", r["baseline"]["baselineSha256"], sha(ev("rehearsal/c05-baseline.json").read_bytes()))
    f = r["findings"]
    c.eq("rehearsal: (i)", ([r4(x) for x in f["i"]["range"]], f["i"]["holds"]), (d["findings"]["i"]["range"], True))
    c.eq("rehearsal: (ii)", (r4(f["ii"]["median"]), f["ii"]["holds"], sorted(f["ii"]["namedUnder"])),
         (d["findings"]["ii"]["median"], True, sorted(d["findings"]["ii"]["namedUnder"])))
    c.eq("rehearsal: (iii)", (r4(f["iii"]["median"]), f["iii"]["holds"], sorted(f["iii"]["named"]),
                              sorted(f["iii"]["subsetCellsUnder2"])),
         (d["findings"]["iii"]["median"], True, sorted(d["findings"]["iii"]["named"]),
          sorted(d["findings"]["iii"]["subsetCellsUnder2"])))
    c.eq("rehearsal: the stop", (round(r["stop"]["minimumSeparationInBars"], 1), r["stop"]["passes"]),
         (d["stopMinimumBars"], True))
    c.eq("rehearsal: the anchors (T1-deep native/web, T1 ratio)",
         [[a["scene"], a["position"], round(a["t1Deep"]["native"], 2), round(a["t1Deep"]["web"], 2),
           round(a["t1"]["ratio"], 2)] for a in r["anchors"]], d["anchors"])
    for name in ("c05", "prefit"):
        g = r["landing"][name]
        c.eq(f"rehearsal: landing on {name}",
             [g["verdict"], r4(g["fAggregate"]), r4(g["fAggregateReference"]), len(g["fNotWithin"]),
              len(g["awayBeyondB"]), len(g["overshoot"])], d["landing"][name])
    s = r["selection"]
    c.eq("rehearsal: selection", [r4(s["c05"]), r4(s["prefit"]), r4(s["tie"]), s["lands"]], d["selection"])
    c.eq("rehearsal: its tools", {k: v for k, v in r["sources"]["tools"].items()},
         {n: sha(p.read_bytes()) for n, p in (("rehearse.py", ev("rehearsal/rehearse.py")),
                                               ("t1.py", ev("cuts/t1.py")), ("bed.py", ev("cuts/bed.py")),
                                               ("readings.py", ev("cuts/readings.py")),
                                               ("cuts.py", ev("cuts/cuts.py")))})


def check_readings(c, it):
    d = it["declared"]
    r = json.loads(ev("rehearsal/rehearsal-r2.json").read_text())
    photo2 = [x for x in r["readings"]["c05"]["cells"] if x["scale"] == 2 and x["scene"].startswith("photo__")
              and x["pose"] == "inactive" and "-tint-" not in x["scene"] and "pressed" not in x["scene"]
              and "glass-over-glass" not in x["scene"]]
    lat = [x["ratio"]["lattice"] for x in photo2]
    t1r = [x["t1Ratio"] for x in photo2]
    c.eq("readings: the 2x inactive single-shape photo cells, T1-lattice range",
         [round(min(lat), 2), round(max(lat), 2)], d["latticeIsolation"]["latticeRange"])
    c.eq("readings: the same cells, T1 range", [round(min(t1r), 2), round(max(t1r), 2)],
         d["latticeIsolation"]["t1Range"])
    import readings as R
    c.eq("readings: constants", [R.DEEP_INSET_CSS, R.FINE_SIGMA_DEVICE, R.ERODE_CSS, list(R.LATTICE_CSS)],
         d["constants"])


def check_referees(c, it):
    import plan
    d = it["declared"]
    m = plan.load_manifest()
    lists = plan.lists(m)
    c.eq("referees: scenes", m["scenes"], d["scenes"])
    c.eq("referees: profiles", m["profiles"], d["profiles"])
    for name in ("pregateProbe", "exposure"):
        got = lists[name]
        c.eq(f"referees: {name} count", got["count"], d[name]["count"])
        c.eq(f"referees: {name} list", sha(",".join(got["scenes"]).encode()), d[name]["listSha256"])
    rc, out = run("-m", "unittest", "test_plan", cwd=HERE / "referees")
    c.true(f"referees: test_plan does not pass ({out.strip().splitlines()[-1] if out.strip() else rc})", rc == 0)


def check_witness(c, it):
    text = (ROOT / "packages/calibration/results/holdout-configuration/configuration.py").read_text()
    for needle in it["declared"]["mentions"]:
        c.true(f"ledgerWitness: configuration.py does not carry {needle!r}", needle in text)


def check_ladders(c, it):
    import plan
    import t1
    d = it["declared"]
    p = json.loads(PROTOCOL.read_text())
    m = plan.load_manifest()
    held = plan.referee_cells(m)
    scenes = plan.load_scenes()
    cells = p["fixedCells"]["scenes"]
    c.eq("ladders: fixed cells", len(cells), d["fixedCells"])
    for sid in cells:
        for prof in LIGHT_025:
            c.true(f"ladders: {prof} does not declare {sid}", sid in scenes["declared"][prof])
            c.true(f"ladders: {sid} is a referee", (prof, sid) not in held)
        c.true(f"ladders: {sid} is {scenes['role'].get(sid)}", scenes["role"].get(sid) not in ("holdout", None))
        c.true(f"ladders: {sid} is not in a set the ladder renders",
               scenes["role"][sid] in p["fixedCells"]["sets"].split(","))
    strata = {t1.stratum(s) for s in cells}
    c.eq("ladders: strata covered", sorted(strata), ["C", "F", "P"])
    twins = {}
    for slot in ("active.light", "receded.light"):
        pose = slot.split(".")[0]
        doc = json.loads((ROOT / f"packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5"
                          f"{'-receded' if pose == 'receded' else ''}.json").read_text())
        twins[slot] = doc["patch"]
    rungs = 0
    for lad in p["ladders"]:
        for leaf in lad["leaves"] + list(lad.get("fixed", {})):
            c.true(f"ladders: {lad['id']} {leaf} is not a leaf the {lad['slot']} 0.5 document names (X44)",
                   leaf in twins[lad["slot"]])
        for base, values in lad["readAt"].items():
            c.true(f"ladders: {lad['id']} reads at an undeclared base {base}", base in p["bases"])
            for v in values:
                rungs += 1
                pairs = zip(lad["leaves"], v) if isinstance(v, list) else [(lad["leaves"][0], v)]
                for leaf, x in pairs:
                    dom = lad["domain"][leaf] if isinstance(lad["domain"], dict) else lad["domain"]
                    c.true(f"ladders: {lad['id']} rung {v} outside {leaf}'s domain {dom}", dom[0] <= x <= dom[1])
                    if leaf in ("sizeHeavyTapSigma2x",):
                        c.true(f"ladders: {lad['id']} rung {x} below the chain's level-1 width", x >= CHAIN_LEVEL_1)
    c.eq("ladders: rungs (bases apart)", rungs, d["rungs"])
    c.eq("ladders: ids", [lad["id"] for lad in p["ladders"]], d["ids"])
    c.eq("ladders: decisions", p["decisions"], d["decisions"])
    ctrl = json.loads((HERE / "ladders/candidates/c05-control/candidate.json").read_text())
    for slot, entry in ctrl["endpoints"].items():
        doc = json.loads((HERE / "ladders/candidates/c05-control" / entry["path"]).read_text())
        pose, scheme = slot.split(".")
        shipped = json.loads((ROOT / f"packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.25"
                              f"{'-receded' if pose == 'receded' else ''}.json").read_text())
        c.eq(f"ladders: c05-control {slot} digest", doc["resolvedMaterialSha256"], shipped["resolvedMaterialSha256"])
        c.eq(f"ladders: c05-control {slot} patch", doc["patch"], shipped["patch"])


def check_references(c, it):
    index = json.loads((ROOT / "packages/calibration/results/generations/index.json").read_text())
    for scheme, entry in it["declared"]["generations"].items():
        f = index["files"].get(f"{entry['active']}.json")
        c.true(f"references: no generation {entry['active']}", f is not None)
        if f:
            c.eq(f"references: {scheme} file sha256", f["sha256"], entry["sha256"])
            c.eq(f"references: {scheme} current", index["currentByProfile"].get(
                f"apple-macos-27.0-2x-{scheme}-standard-glass0.25"), f"{entry['active']}.json")


def draft_leaves(draft):
    """(move id, family, leaf key, spec) for every searched leaf of the draft."""
    for move in draft["moves"]:
        for fam, body in move["families"].items():
            for leaf, spec in body.get("leaves", {}).items():
                yield move["id"], fam, leaf, spec


def ladder_of(protocol, slot, leaf):
    for lad in protocol["ladders"]:
        if lad["slot"] == slot and (leaf == "+".join(lad["leaves"]) or leaf in lad["leaves"]):
            return lad["id"]
    return None


def check_draft(c, it):
    d = it["declared"]
    draft = json.loads(DRAFT.read_text())
    protocol = json.loads(PROTOCOL.read_text())
    c.eq("draft: schema", draft["schema"], PARTS["fit"]["schema"])
    c.eq("draft: moves", [m["id"] for m in draft["moves"]], d["moves"])
    c.eq("draft: references", draft["references"]["c05"], {"light": "6d18c059eb42", "dark": "d0219cd684bf"})
    count = 0
    for mid, fam, leaf, spec in draft_leaves(draft):
        count += 1
        grid, dom = spec["grid"], spec["domain"]
        c.true(f"draft: {mid}/{fam}/{leaf} grid not sorted and distinct", grid == sorted(set(grid)))
        c.true(f"draft: {mid}/{fam}/{leaf} grid {grid} outside its domain {dom}",
               all(dom[0] <= x <= dom[1] for x in grid) and not (spec.get("domainOpenAt") in grid))
        c.true(f"draft: {mid}/{fam}/{leaf} has no unit", bool(spec.get("unit")))
        c.true(f"draft: {mid}/{fam}/{leaf} has no ladder that can strike or narrow it",
               ladder_of(protocol, spec["slot"], leaf) is not None)
        if leaf == "sizeHeavyTapSigma2x":
            c.true(f"draft: {mid}/{fam} heavy width below the chain's level-1 width", min(grid) >= CHAIN_LEVEL_1)
    c.eq("draft: searched leaves", count, d["searchedLeaves"])
    for move in draft["moves"]:
        for fam, body in move["families"].items():
            c.true(f"draft: {move['id']}/{fam} has no prediction", bool(body.get("prediction")))
    reh = json.loads(ev("rehearsal/rehearsal-r2.json").read_text())
    got = draft["rehearsed"]
    for name in ("c05", "prefit"):
        g = reh["landing"][name]
        c.eq(f"draft: rehearsed {name} landing", got[name]["landing"], g["verdict"])
        c.eq(f"draft: rehearsed {name} F aggregate", got[name]["fAggregate"], r4(g["fAggregate"]))
        c.eq(f"draft: rehearsed {name} away beyond B", got[name]["awayBeyondB"], len(g["awayBeyondB"]))
        c.eq(f"draft: rehearsed {name} selection", got[name]["selectionMetric"], r4(reh["selection"][name]))
    c.eq("draft: rehearsed tie", got["selectionTie"], r4(reh["selection"]["tie"]))
    c.eq("draft: rehearsed choice", got["selectionBetweenThem"], reh["selection"]["lands"])
    c.eq("draft: permitted changes against the protocol's decisions", len(draft["permittedChanges"]), 3)
    rc, out = run("-m", "unittest", "test_declare", cwd=HERE)
    c.true(f"draft: test_declare (the part-2 validator's red cases) does not pass "
           f"({out.strip().splitlines()[-1] if out.strip() else rc})", rc == 0)


CHECKS = {"t1": check_t1, "bar": check_bar, "rehearsal": check_rehearsal, "readings": check_readings,
          "referees": check_referees, "ledgerWitness": check_witness, "ladders": check_ladders,
          "references": check_references, "draft": check_draft}


def serialise(d):
    return (json.dumps(d, indent=2, ensure_ascii=False) + "\n").encode()


def digest_lines(part):
    path = PARTS[part]["digest"]
    return [ln.split()[0] for ln in path.read_text().splitlines() if ln.strip()] if path.exists() else []


def amendments(part):
    path = PARTS[part]["amendments"]
    return json.loads(path.read_text())["amendments"] if path.exists() else []


def chain(c, part, d):
    lines, record, raw = digest_lines(part), amendments(part), PARTS[part]["declaration"].read_bytes()
    if not lines:
        c.true(f"chain ({part}): amendments exist but the part was never hashed", not record)
        return
    c.true(f"chain ({part}): the declaration is not in its own serialised form", serialise(d) == raw)
    c.eq(f"chain ({part}): digest lines against amendments", len(lines), 1 + len(record))
    c.eq(f"chain ({part}): the last line names the current file", lines[-1], sha(raw))
    state = json.loads(raw)
    for i in range(len(record) - 1, -1, -1):
        a = record[i]
        c.eq(f"chain ({part}): amendment {i + 1} names the hash it made", a.get("declarationSha256"), lines[i + 1])
        c.eq(f"chain ({part}): amendment {i + 1} names the hash it supersedes", a.get("supersedes"), lines[i])
        c.true(f"chain ({part}): amendment {i + 1} states a reason and a cause", bool(a.get("reason")) and bool(a.get("cause")))
        for path, move in (a.get("pins") or {}).items():
            c.eq(f"chain ({part}): amendment {i + 1} pin {path}", state["sources"].get(path), move.get("to"))
            state["sources"][path] = move.get("from")
        if a.get("ops"):
            try:
                state = revert_ops(state, a["ops"])
            except Refusal as err:
                c.failures.append(f"chain ({part}): amendment {i + 1}'s operations do not revert: {err}")
        c.eq(f"chain ({part}): the declaration before amendment {i + 1} rebuilt", sha(serialise(state)), lines[i])


def check_protocol():
    c = Check()
    d = json.loads(PARTS["protocol"]["declaration"].read_text())
    c.eq("schema", d.get("schema"), PARTS["protocol"]["schema"])
    c.eq("charter", d.get("charter"), CHARTER_PIN)
    chain(c, "protocol", d)
    items = structure(c, d)
    twin(c, items, PARTS["protocol"]["twin"])
    for iid, it in items.items():
        if "declared" in it and iid in CHECKS:
            try:
                CHECKS[iid](c, it)
            except Exception as err:  # a check that cannot run is a mismatch, never a pass
                c.failures.append(f"{iid}: the check raised {type(err).__name__}: {err}")
    c.true("draft: fit-declaration-draft.json is not one of part 1's pinned sources",
           f"{REL}/fit-declaration-draft.json" in d["sources"])
    return c, d, items


# ---------------------------------------------------------------------------------------------
# Part 2: the validated diff
# ---------------------------------------------------------------------------------------------
class Refusal(Exception):
    pass


def apply_changes(draft, changes, results, protocol):
    """The draft with `changes` applied, each only where the ladder results support it."""
    body = json.loads(json.dumps(draft))
    moves = {m["id"]: m for m in body["moves"]}
    ladders = results.get("ladders", {})
    for ch in changes:
        kind = ch.get("kind")
        lad = ladders.get(ch.get("ladder"))
        if lad is None:
            raise Refusal(f"{ch}: cites no ladder in the results")
        if kind in ("strike", "narrow"):
            move = moves.get(ch.get("move"))
            fam = move and move["families"].get(ch.get("family"))
            spec = fam and fam.get("leaves", {}).get(ch.get("leaf"))
            if spec is None:
                raise Refusal(f"{ch}: names no leaf of the draft")
            if ladder_of(protocol, spec["slot"], ch["leaf"]) != ch["ladder"]:
                raise Refusal(f"{ch}: {ch['ladder']} is not {ch['leaf']}'s ladder")
            if kind == "strike":
                if not lad.get("struck"):
                    raise Refusal(f"{ch}: {ch['ladder']} did not strike its leaf")
                del fam["leaves"][ch["leaf"]]
                if not fam["leaves"]:
                    del move["families"][ch["family"]]
                    if ch["family"] in move.get("familyOrder", []):
                        move["familyOrder"].remove(ch["family"])
            else:
                grid = ch.get("grid")
                rng = (lad.get("nonFlatRange") or {}).get(ch["leaf"])
                if not grid or not isinstance(grid, list) or rng is None:
                    raise Refusal(f"{ch}: a narrowing names a grid and its ladder a non-flat range")
                if not set(grid) <= set(spec["grid"]) or grid != sorted(set(grid)):
                    raise Refusal(f"{ch}: {grid} is not a subset of the draft grid {spec['grid']}")
                if not all(rng[0] <= x <= rng[1] for x in grid):
                    raise Refusal(f"{ch}: {grid} leaves {ch['ladder']}'s non-flat range {rng}")
                spec["grid"] = grid
        elif kind == "strikeFamily":
            if ch["ladder"] != "L3" or ch.get("family") != "C" or not lad.get("struck"):
                raise Refusal(f"{ch}: only family C is struck whole, and only when L3 is struck")
            move = moves["move1"]
            move["families"].pop("C", None)
            move["familyOrder"].remove("C")
        elif kind == "inert":
            if ch["ladder"] != "L3" or not lad.get("inert1x"):
                raise Refusal(f"{ch}: C's inert setting is fixed only by L3 proving it")
            fixed = moves["move1"]["families"]["C"]["fixed"]["sizeHeavySecondSigma"]
            if fixed["value"] != 0:
                raise Refusal(f"{ch}: the inert setting is 0, the only one offered")
            fixed["inert"] = ("proven by L3: every 1x capture of every rung pixel-identical to "
                              "c05-control's (ladders/results.json)")
        else:
            raise Refusal(f"{ch}: not one of the protocol's decisions (strike, strikeFamily, inert, narrow)")
    return body


def validate_fit(draft, fit, results, protocol):
    """Raise Refusal unless `fit` is the draft changed only by its own permitted `changes`."""
    if fit.get("schema") != draft["schema"]:
        raise Refusal("part 2's schema is not the draft's")
    changes = fit.get("changes")
    if not isinstance(changes, list):
        raise Refusal("part 2 lists its changes against the draft (`changes`), even when there are none")
    expected = apply_changes(draft, changes, results, protocol)
    for key in ("status",):
        expected.pop(key, None)
    got = {k: v for k, v in fit.items() if k not in ("status", "changes", "sources", "fromDraft")}
    if json.dumps(got, sort_keys=True) != json.dumps(expected, sort_keys=True):
        diff = [k for k in set(got) | set(expected) if got.get(k) != expected.get(k)]
        raise Refusal(f"part 2 differs from the draft beyond its permitted changes, in: {sorted(diff)}")


# ---------------------------------------------------------------------------------------------
# Part 2's one amendment: Decision Log 7's five rulings as a content diff
# ---------------------------------------------------------------------------------------------
def _src(rel):
    return ("sources", f"{G1_REL}/{rel}")


RULINGS = {
    1: dict(title="the receded light document may name sizeHeavySecondShare as a difference over its "
                  "active document (X44 narrowed by one difference); move 3 gains it as a fifth leaf",
            paths=[("moves", 2, "families", "receded", "leaves", "sizeHeavySecondShare"),
                   ("moves", 2, "families", "receded", "predictionDecisionLog7"),
                   ("moves", 2, "inherits"),
                   _src("fit/build-candidate.ts"), _src("fit/test_build_candidate.py")]),
    2: dict(title="the photo cells leave move 1's within clause (still in the regression budget)",
            paths=[("moves", 0, "withinClause")]),
    3: dict(title="hc-text-7 is a fourth stratum T, out of F, read on two bands: fidelity and change "
                  "on T1-fine, the away veto on T1-low, T1 recorded; the full close does not require a "
                  "T cell within",
            paths=[("strata",), ("textStratum",),
                   ("moves", 0, "cells"), ("moves", 1, "cells"), ("moves", 2, "cells"),
                   ("moves", 1, "withinClause"), ("moves", 2, "withinClause"),
                   ("landingRule", "scope"), ("landingRule", "fullClose"), ("landingRule", "improvement"),
                   ("landingRule", "regressionBudget"),
                   _src("cuts/t1.py"), _src("cuts/test_t1.py"), _src("cuts/readings.py")]),
    4: dict(title="fourteen fit scenes per scale among the fine backdrops, not thirteen",
            paths=[("fitCells",)]),
    5: dict(title="a candidate's identity to c05 is patch-and-digest (the glass0.250 key); byte "
                  "identity is the sealed documents'",
            paths=[("candidateIdentity",)]),
}
OP_KINDS = ("add", "replace")


def _walk(body, path):
    node = body
    for part in path[:-1]:
        try:
            node = node[part]
        except (KeyError, IndexError, TypeError):
            raise Refusal(f"{list(path)}: no such parent in part 2")
    return node, path[-1]


def _present(node, key):
    return (key < len(node)) if isinstance(node, list) else (key in node)


def apply_ops(body, ops):
    """`body` with the operations applied, each checked against what it states it replaces."""
    out = json.loads(json.dumps(body))
    for op in ops:
        node, key = _walk(out, tuple(op["path"]))
        if op["kind"] == "add":
            if _present(node, key):
                raise Refusal(f"{op['path']}: an add over an existing value")
        elif op["kind"] == "replace":
            if not _present(node, key) or node[key] != op["from"]:
                raise Refusal(f"{op['path']}: the replaced value is not the operation's `from`")
        else:
            raise Refusal(f"{op['path']}: {op['kind']!r} is not an add or a replace")
        node[key] = op["to"]
    return out


def revert_ops(body, ops):
    """`body` with the operations undone, in reverse; each must find its `to` in place."""
    out = json.loads(json.dumps(body))
    for op in reversed(ops):
        node, key = _walk(out, tuple(op["path"]))
        if not _present(node, key) or node[key] != op["to"]:
            raise Refusal(f"{op['path']}: the amended value is not the operation's `to`")
        if op["kind"] == "add":
            del node[key]
        elif op["kind"] == "replace":
            node[key] = op["from"]
        else:
            raise Refusal(f"{op['path']}: {op['kind']!r} is not an add or a replace")
    return out


def validate_ops(ops):
    """Refuse unless `ops` carries exactly the five rulings: every operation an add or a replace at
    one of its ruling's paths, no path touched twice, and every ruling executed."""
    if not isinstance(ops, list) or not ops:
        raise Refusal("the amendment carries no operations")
    seen, rulings = set(), set()
    for op in ops:
        r, kind, path = op.get("ruling"), op.get("kind"), tuple(op.get("path") or ())
        if r not in RULINGS:
            raise Refusal(f"{list(path)}: cites ruling {r!r}, not one of Decision Log 7's five")
        if kind not in OP_KINDS:
            raise Refusal(f"{list(path)}: {kind!r} is not an add or a replace (nothing is removed)")
        if path not in [tuple(x) for x in RULINGS[r]["paths"]]:
            raise Refusal(f"{list(path)}: not a path ruling {r} changes")
        if path in seen:
            raise Refusal(f"{list(path)}: touched twice")
        if kind == "add" and "from" in op:
            raise Refusal(f"{list(path)}: an add states no `from`")
        if kind == "replace" and "from" not in op:
            raise Refusal(f"{list(path)}: a replace states its `from`")
        seen.add(path)
        rulings.add(r)
    missing = sorted(set(RULINGS) - rulings)
    if missing:
        raise Refusal(f"rulings {missing} carry no operation; the amendment is all five or nothing")


def amendment_one(fit):
    """Decision Log 7's five rulings as operations on part 2's body `fit` (G1 step 0)."""
    moves = fit["moves"]
    ops = []

    def op(ruling, path, to):
        node, key = _walk(fit, tuple(path))
        entry = dict(ruling=ruling, kind="replace" if _present(node, key) else "add", path=list(path))
        if entry["kind"] == "replace":
            entry["from"] = node[key]
        entry["to"] = to
        ops.append(entry)

    # 1. The receded share, a fifth leaf of move 3.
    op(1, ("moves", 2, "families", "receded", "leaves", "sizeHeavySecondShare"), {
        "slot": "receded.light",
        "unit": "signed fraction, named in the receded light document as a difference over its active document "
                "(one leaf for both scales; the 1x width is inherited at 0, so the plan declines at dpr 1)",
        "domain": [0, 1],
        "domainRelativeTo": "the active light document's sizeHeavySecondShare at the joint point: the receded "
                            "share is in [0, the active share]",
        "grid": [0, 0.25, 0.5, 0.75, 1.0],
        "gridUnit": "fraction of the active share (0 switches the second tap off in the receded pose; 1 is the "
                    "inherited value). When the active share is 0 the grid is the one point 0.",
        "inherited": "sizeScatterFloor2x, sizeScatterRampReach2xPx and the second tap's widths "
                     "(sizeHeavySecondSigma, sizeHeavySecondSigma2x) stay inherited from the active document",
        "why": "G0's ladders: the receded document inherits the second tap's share and width and no receded leaf "
               "can take them off; at C 0.5 x 3 CSS px the receded checkerboard-8 mid cell went 1.01 -> 2.56 and "
               "the receded pitch-16 cells read 2.33-3.59 (claims 5.202 section 7; charter Decision Log 7 item 1)"})
    op(1, ("moves", 2, "families", "receded", "predictionDecisionLog7"),
       "under family C the receded share lands at or near 0 (charter v1.3, Design, move 3)")
    op(1, ("moves", 2, "inherits"),
       "the receded document names exactly its 0.5 twin's keys (X44) and, by Decision Log 7 item 1, "
       "sizeHeavySecondShare as a difference over its active document; sizeScatterFloor2x, the reach and the "
       "second tap's widths come from the active document as moves 1 and 2 leave them")
    # 2. Move 1's within clause without the photo.
    op(2, ("moves", 0, "withinClause"),
       "every F cell of `cells` within, AND every pitch-16 (`checkerboard`) cell of `cells` within (T1 output 1); "
       "the photo cells of `cells` are read, out of the clause and still in the regression budget (Decision Log "
       "7 item 2: no family moves them, 0.62-0.70 across A, B and C on the ladders; W43's named tone gap)")
    # 3. The text stratum.
    op(3, ("strata",), {"F": ["checkerboard-4", "checkerboard-8"], "T": ["hc-text-7"],
                        "C": ["checkerboard", "checkerboard-lc16", "checkerboard-32", "checkerboard-64",
                              "hc-text", "hc-text-28", "impulse"],
                        "P": ["photo"]})
    op(3, ("textStratum",), {
        "backdrops": ["hc-text-7"],
        "bands": ["fine", "low"],
        "reads": {"fidelity": "fine", "change": "fine", "overshoot": "fine", "away": "low"},
        "fine": "T1-fine: the SD of L - G(L, sigma 4 device px), linear luminance, over the native silhouette "
                "eroded 4 CSS px",
        "low": "T1-low: the SD of G(L, sigma 4 device px) over the same support",
        "sigmaDevicePx": 4.0,
        "erodeCssPx": 4,
        "outputs": "T1's three outputs per cell on each band, at the cell's own bar and code (the seven runs are "
                   "pixel-identical, so every statistic's separation is 0 and the bar is 0.5 code)",
        "t1": "recorded on every T cell, read by no clause",
        "fullClose": "does not require a T cell within",
        "selectionStrata": ["F", "C", "P"],
        "selection": "T is outside F u C u P: the selection metric and every move objective do not read it",
        "implementation": f"{G1_REL}/cuts/t1.py and readings.py, pinned below with test_t1.py",
        "why": "T1 reads the hc-text-7 cells under (0.79-0.89 on c05) while the fine band reads them x1.9-8.5 "
               "over, and every lever that removes fine structure takes T1 further under (charter Decision Log "
               "7 item 3)"})
    for i, m in enumerate(moves):
        op(3, ("moves", i, "cells"), m["cells"].replace(
            "F u C u P", "F u T u C u P (T read on its two bands and never required within; the move objective "
                         "reads F u C u P)"))
    for i in (1, 2):
        op(3, ("moves", i, "withinClause"), "every F, C and P cell of `cells` within (T1 output 1); a T cell is "
                                             "read on its bands and not required within")
    lr = fit["landingRule"]
    op(3, ("landingRule", "scope"), lr["scope"].replace(
        "F u C u P less the referees", "F u T u C u P less the referees").replace(
        "(t1.landing)", "(t1.landing); a T cell's fidelity and change on T1-fine, its away on T1-low"))
    op(3, ("landingRule", "fullClose"), lr["fullClose"].replace(
        "every F cell within; no cell away with g > B; no cell overshoot;",
        "every F cell within (no T cell is required within); no cell away with g > B (a T cell's on T1-low); "
        "no cell overshoot (a T cell's on T1-fine);"))
    op(3, ("landingRule", "improvement"), lr["improvement"].replace(
        "no cell away with g > B; no cell overshoot;",
        "no cell away with g > B (a T cell's on T1-low); no cell overshoot (a T cell's on T1-fine);"))
    op(3, ("landingRule", "regressionBudget"), lr["regressionBudget"] +
       "; a T cell's budget reads T1-low's error growth (away with g <= B a named regression, g > B a failure)")
    # 4. The fit set's count.
    op(4, ("fitCells",), fit["fitCells"] +
       "; among the fine backdrops (checkerboard-4, checkerboard-8, hc-text-7) that is 14 fit scenes per scale: "
       "their 19 scenes per scale less the five fine referees (F 11 of 15, T 3 of 4; Decision Log 7 item 4)")
    # 5. The candidate identity clause.
    op(5, ("candidateIdentity",),
       "a candidate's dark endpoints are patch- and digest-identical to c05's dark documents, and its light "
       "endpoints are c05's on every leaf but the declared 2x leaves of the moves (and, in the receded light "
       "document, sizeHeavySecondShare), so its 1x-reaching leaves are c05's; a candidate carries the "
       "glass0.250 key because candidate mode refuses a shipped key, so the identity is patch-and-digest, and "
       "byte identity is the sealed documents' at the freeze (charter clause 5; Decision Log 7 item 5)")
    # The rulings' pinned implementations, under the ruling each implements.
    for ruling, rel in ((1, "fit/build-candidate.ts"), (1, "fit/test_build_candidate.py"),
                        (3, "cuts/t1.py"), (3, "cuts/test_t1.py"), (3, "cuts/readings.py")):
        op(ruling, _src(rel), sha((G1 / rel).read_bytes()))
    return ops


def check_fit():
    c = Check()
    path = PARTS["fit"]["declaration"]
    if not path.exists():
        c.failures.append("fit-declaration.json does not exist")
        return c, None
    fit = json.loads(path.read_text())
    chain(c, "fit", fit)
    c.true("part 2: part 1 is not hashed", bool(digest_lines("protocol")))
    for key, want in (fit.get("sources") or {}).items():
        try:
            c.eq(f"pin {key}", sha(source_bytes(key)), want)
        except (OSError, subprocess.CalledProcessError) as err:
            c.failures.append(f"pin {key}: unreadable ({err})")
    c.true("part 2 pins the draft, the protocol and the ladder results",
           {f"{REL}/fit-declaration-draft.json", f"{REL}/ladders/protocol.json", f"{REL}/ladders/results.json"}
           <= set(fit.get("sources") or {}))
    c.eq("part 2: fromDraft names the draft's hash", fit.get("fromDraft"), sha(DRAFT.read_bytes()))
    body = fit
    record = amendments("fit")
    if record:
        body = check_amendment(c, fit, record)
    try:
        validate_fit(json.loads(DRAFT.read_text()), body, json.loads(RESULTS.read_text()),
                     json.loads(PROTOCOL.read_text()))
    except (Refusal, OSError, KeyError, ValueError) as err:
        c.failures.append(f"part 2 is not a valid diff against the draft: {err}")
    return c, fit


def check_amendment(c, fit, record):
    """Part 2's one amendment: its operations are exactly the five rulings, the charter at its
    cause carries Decision Log 7, its part-1 re-pins are this file's alone, its validator tests and
    the rulings' pinned tests pass. Returns part 2's body with the operations reverted (the
    superseded body), or `fit` unchanged when they cannot be reverted (a failure is recorded)."""
    c.eq("amendment: part 2 is amended at most once", len(record), 1)
    a = record[0]
    ops = a.get("ops") or []
    try:
        validate_ops(ops)
    except Refusal as err:
        c.failures.append(f"amendment: {err}")
    try:
        charter = source_bytes(f"{CHARTER_PATH}@{a.get('cause')}").decode()
        c.true(f"amendment: the charter at its cause {a.get('cause')} carries no Decision Log 7",
               "### Decision Log 7" in charter)
    except (subprocess.CalledProcessError, OSError) as err:
        c.failures.append(f"amendment: the cause {a.get('cause')} is not readable ({err})")
    for key in a.get("partOnePins") or {}:
        c.true(f"amendment: re-pins part 1's {key}, which is not re-pinnable", key in PART_ONE_REPINNABLE)
    for key, want in (a.get("validatorTests") or {}).items():
        try:
            c.eq(f"amendment: validator test {key}", sha(source_bytes(key)), want)
        except OSError as err:
            c.failures.append(f"amendment: validator test {key} unreadable ({err})")
    c.eq("amendment: its validator tests", sorted(a.get("validatorTests") or {}), sorted(AMENDMENT_TESTS))
    for name, folder, module in (("the amendment validator", HERE, "test_amend_fit"),
                                 ("G1's T1 readers (ruling 3)", G1 / "cuts", "test_t1"),
                                 ("G1's builder guard (ruling 1)", G1 / "fit", "test_build_candidate")):
        rc, out = run("-m", "unittest", module, cwd=folder)
        c.true(f"amendment: {name}' tests do not pass ({out.strip().splitlines()[-1] if out.strip() else rc})",
               rc == 0)
    check_text_stratum(c, fit)
    try:
        return revert_ops(fit, ops)
    except Refusal as err:
        c.failures.append(f"amendment: its operations do not revert: {err}")
        return fit


def check_text_stratum(c, fit):
    """Ruling 3's declared constants against G1's pinned readers."""
    declared = fit.get("textStratum") or {}
    got = subprocess.run([sys.executable, "-B", "-c",
                          "import json, t1, readings as R; print(json.dumps(dict(strata={k: list(v) for k, v in "
                          "t1.STRATA.items()}, bands=list(t1.BANDS), reads=t1.T_READS, sigma=R.FINE_SIGMA_DEVICE, "
                          "erode=R.ERODE_CSS, selection=list(t1.SELECTION_STRATA))))"],
                         capture_output=True, text=True, cwd=G1 / "cuts")
    if got.returncode:
        c.failures.append(f"amendment: G1's t1.py does not import ({got.stderr.strip()[-300:]})")
        return
    impl = json.loads(got.stdout)
    c.eq("amendment: the strata against G1's t1.py", impl["strata"], fit.get("strata"))
    c.eq("amendment: T's bands and reads against G1's t1.py", [impl["bands"], impl["reads"]],
         [declared.get("bands"), declared.get("reads")])
    c.eq("amendment: T's support against G1's readings.py", [impl["sigma"], impl["erode"]],
         [declared.get("sigmaDevicePx"), declared.get("erodeCssPx")])
    c.eq("amendment: the selection strata against G1's t1.py", impl["selection"], declared.get("selectionStrata"))


# ---------------------------------------------------------------------------------------------
def ladder_evidence():
    found = []
    if LADDER_RUNS.exists() and any('"started"' in ln for ln in LADDER_RUNS.read_text().splitlines()):
        found.append(str(LADDER_RUNS.relative_to(ROOT)))
    if LADDER_SCRATCH.exists():
        found += [str(p) for p in sorted(LADDER_SCRATCH.rglob("matrix.json"))][:3]
    return found


def fit_evidence():
    """Any fit RENDER (the brief's `capture_evidence` for fit renders): a launch recorded in G1's
    `fit/runs.jsonl`, or a matrix or a capture under the fit scratch. G1's evidence directory
    existing is not a render: step 0 writes its T1 readers and builder there before any render."""
    found = []
    runs = G1 / "fit" / "runs.jsonl"
    if runs.exists() and any('"started"' in ln for ln in runs.read_text().splitlines()):
        found.append(str(runs.relative_to(ROOT)))
    if G1_SCRATCH.exists():
        found += [str(p) for p in sorted(G1_SCRATCH.rglob("matrix.json"))][:3]
        found += [str(p) for p in sorted(G1_SCRATCH.rglob("*.png"))][:1]
    return found


def amend_fit(argv):
    """Part 2's one amendment (G1 step 0): Decision Log 7's five rulings as a content diff."""
    import argparse
    ap = argparse.ArgumentParser(prog="declare.py amend-fit")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--cause", required=True, help="the charter commit that rules the amendment")
    args = ap.parse_args(argv)
    lines = digest_lines("fit")
    if not lines:
        print("amend-fit REFUSES: part 2 is not hashed; before the hash it is simply edited and re-checked")
        return 2
    evidence = fit_evidence()
    if evidence:
        print(f"amend-fit REFUSES: a fit render exists ({', '.join(evidence[:4])}); part 2 is fixed (X50)")
        return 2
    if amendments("fit"):
        print("amend-fit REFUSES: part 2 was amended once already (X50: each part amended at most once)")
        return 2
    c, fit = check_fit()
    if c.failures:
        print("amend-fit REFUSES: check-fit fails before the amendment:")
        for f in c.failures:
            print("  MISMATCH", f)
        return 2
    c1, d1, _ = check_protocol()
    moved = {k: sha(source_bytes(k)) for k in PART_ONE_REPINNABLE if sha(source_bytes(k)) != d1["sources"][k]}
    other = [f for f in c1.failures if not any(f.startswith(f"pin {k}:") for k in moved)]
    if other:
        print("amend-fit REFUSES: part 1's check fails outside its re-pinnable sources:")
        for f in other:
            print("  MISMATCH", f)
        return 2
    try:
        charter = source_bytes(f"{CHARTER_PATH}@{args.cause}").decode()
    except subprocess.CalledProcessError:
        print(f"amend-fit REFUSES: no charter at {args.cause}")
        return 2
    if "### Decision Log 7" not in charter:
        print(f"amend-fit REFUSES: the charter at {args.cause} carries no Decision Log 7")
        return 2
    ops = amendment_one(fit)
    try:
        validate_ops(ops)
        amended = apply_ops(fit, ops)
    except Refusal as err:
        print(f"amend-fit REFUSES: {err}")
        return 2
    path = PARTS["fit"]["declaration"]
    raw = serialise(amended)
    entry = {"n": 1, "supersedes": lines[-1], "declarationSha256": sha(raw), "reason": args.reason,
             "cause": args.cause, "charter": f"{CHARTER_PATH}@{args.cause}",
             "rulings": {str(k): v["title"] for k, v in RULINGS.items()}, "ops": ops, "pins": {},
             "partOnePins": {k: {"from": d1["sources"][k], "to": v} for k, v in moved.items()},
             "validatorTests": {k: sha(source_bytes(k)) for k in AMENDMENT_TESTS},
             "renderEvidenceAtAmendment": "none (fit_evidence: G1's fit/runs.jsonl launches, the fit scratch's "
                                          "matrices and captures)"}
    PARTS["fit"]["amendments"].write_text(json.dumps({"schema": "w44-fit-amendments-1", "amendments": [entry]},
                                                     indent=2, ensure_ascii=False) + "\n")
    path.write_bytes(raw)
    with PARTS["fit"]["digest"].open("a") as f:
        f.write(f"{entry['declarationSha256']}  {path.name}\n")
    after, _ = check_fit()
    after1, _, _ = check_protocol()
    for f in after.failures + after1.failures:
        print("  MISMATCH", f)
    if after.failures or after1.failures:
        print("amend-fit: written, but a check fails; inspect before committing")
        return 1
    print(f"amended: {path.name} sha256 {entry['declarationSha256']} supersedes {lines[-1]}; check and "
          "check-fit consistent; commit fit-declaration.json, fit-amendments.json and fit-declaration.sha256")
    return 0


def amend(part, argv):
    import argparse
    ap = argparse.ArgumentParser(prog=f"declare.py amend{'-fit' if part == 'fit' else ''}")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--cause", required=True)
    ap.add_argument("pins", nargs="+")
    args = ap.parse_args(argv)
    lines = digest_lines(part)
    if not lines:
        print("amend REFUSES: the part is not hashed; before the hash it is simply edited and re-checked")
        return 2
    evidence = ladder_evidence() if part == "protocol" else fit_evidence()
    if evidence:
        print(f"amend REFUSES: render evidence exists for this part ({', '.join(evidence[:4])}); "
              "a render after the hash fixes it (X50)")
        return 2
    record = amendments(part)
    if record:
        print("amend REFUSES: this part was amended once already (X50: each part amended at most once)")
        return 2
    path = PARTS[part]["declaration"]
    d = json.loads(path.read_text())
    unknown = [p for p in args.pins if p not in d["sources"] or "@" in p]
    if unknown:
        print(f"amend REFUSES: not a pinned working-tree source: {unknown}")
        return 2
    c = check_protocol()[0] if part == "protocol" else check_fit()[0]
    named = {f"pin {p}" for p in args.pins}
    other = [f for f in c.failures if not any(f.startswith(n + ":") for n in named)]
    if other:
        print("amend REFUSES: the check fails outside the named pins:")
        for f in other:
            print("  MISMATCH", f)
        return 2
    moves = {}
    for p in args.pins:
        now = sha(source_bytes(p))
        if now == d["sources"][p]:
            print(f"amend REFUSES: {p} has not moved")
            return 2
        moves[p] = {"from": d["sources"][p], "to": now}
        d["sources"][p] = now
    raw = serialise(d)
    entry = {"n": 1, "supersedes": lines[-1], "declarationSha256": sha(raw), "reason": args.reason,
             "cause": args.cause, "pins": moves,
             "renderEvidenceAtAmendment": "none (" + ("ladders/runs.jsonl, the ladder scratch" if part == "protocol"
                                                       else "G1's evidence directory and scratch") + ")"}
    PARTS[part]["amendments"].write_text(json.dumps({"schema": f"w44-{part}-amendments-1",
                                                     "amendments": [entry]}, indent=2) + "\n")
    path.write_bytes(raw)
    with PARTS[part]["digest"].open("a") as f:
        f.write(f"{entry['declarationSha256']}  {path.name}\n")
    print(f"amended: {path.name} sha256 {entry['declarationSha256']} supersedes {lines[-1]}")
    return 0


def report(c, waiting, what):
    for f in c.failures:
        print("  MISMATCH", f)
    for it in waiting:
        print(f"  PENDING ({it['pending']['on']}) {it['id']}: {it['pending'].get('note', '')}")
    if c.failures:
        print(f"{what}: {len(c.failures)} mismatch(es)")
        return 1
    print(f"{what}: consistent" + (f"; {len(waiting)} item(s) pending" if waiting else ""))
    return 0


def main(argv):
    verb = argv[1] if len(argv) > 1 else ""
    if verb == "amend":
        return amend("protocol", argv[2:])
    if verb == "amend-fit":
        return amend_fit(argv[2:])
    if verb in ("check", "hash"):
        c, d, items = check_protocol()
        waiting = [it for it in items.values() if "pending" in it]
        print(f"W44 G0 part 1: {len(items)} items, {len(d['sources'])} pinned sources")
        rc = report(c, waiting, "check")
        if verb == "check" or rc:
            return rc
        if waiting:
            print("hash REFUSES: " + ", ".join(it["id"] for it in waiting) + " pending")
            return 2
        if PARTS["protocol"]["digest"].exists():
            print("hash REFUSES: part 1 is hashed already; this tool never overwrites a hash")
            return 2
        if ladder_evidence():
            print("hash REFUSES: a ladder render exists; part 1 is hashed before any (X50)")
            return 2
        digest = sha(PARTS["protocol"]["declaration"].read_bytes())
        with PARTS["protocol"]["digest"].open("x") as f:
            f.write(f"{digest}  declaration.json\n")
        print(f"declaration.json sha256 {digest}; commit it with declaration.sha256 before any ladder render")
        return 0
    if verb in ("check-fit", "hash-fit"):
        c, fit = check_fit()
        print("W44 G0 part 2: the fit declaration as a validated diff against the draft")
        rc = report(c, [], "check-fit")
        if verb == "check-fit" or rc:
            return rc
        if PARTS["fit"]["digest"].exists():
            print("hash-fit REFUSES: part 2 is hashed already")
            return 2
        if fit_evidence():
            print("hash-fit REFUSES: a fit render exists; part 2 is hashed before any (X50)")
            return 2
        digest = sha(PARTS["fit"]["declaration"].read_bytes())
        with PARTS["fit"]["digest"].open("x") as f:
            f.write(f"{digest}  fit-declaration.json\n")
        print(f"fit-declaration.json sha256 {digest}; commit it before any fit render")
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
