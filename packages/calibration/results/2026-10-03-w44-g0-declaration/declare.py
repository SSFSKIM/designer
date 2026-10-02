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
    python3.12 -B declare.py amend-fit --reason TEXT --cause COMMIT PIN [PIN ...]

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
    for key, want in d["sources"].items():
        try:
            c.eq(f"pin {key}", sha(source_bytes(key)), want)
        except (OSError, subprocess.CalledProcessError) as err:
            c.failures.append(f"pin {key}: unreadable ({err})")
    return {it["id"]: it for it in items}


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
    try:
        validate_fit(json.loads(DRAFT.read_text()), fit, json.loads(RESULTS.read_text()),
                     json.loads(PROTOCOL.read_text()))
    except (Refusal, OSError, KeyError, ValueError) as err:
        c.failures.append(f"part 2 is not a valid diff against the draft: {err}")
    return c, fit


# ---------------------------------------------------------------------------------------------
def ladder_evidence():
    found = []
    if LADDER_RUNS.exists() and any('"started"' in ln for ln in LADDER_RUNS.read_text().splitlines()):
        found.append(str(LADDER_RUNS.relative_to(ROOT)))
    if LADDER_SCRATCH.exists():
        found += [str(p) for p in sorted(LADDER_SCRATCH.rglob("matrix.json"))][:3]
    return found


def fit_evidence():
    return [str(p) for p in FIT_EVIDENCE if p.exists()]


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
    if verb in ("amend", "amend-fit"):
        return amend("protocol" if verb == "amend" else "fit", argv[2:])
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
