"""W45 G0: the two hashed parts of the declaration (charter clause 2; X58). W44 G0's `declare.py`
(`results/2026-10-03-w44-g0-declaration/declare.py`), ported and parameterised for W45; W44's
committed copy is untouched and is never run by W45.

Part 1 (`declaration.json`, with its readable twin `declaration.md`) and the part-2 DRAFT
(`fit-declaration-draft.json`, pinned as one of part 1's sources, so the one hash covers both),
before any ladder render:

    python3.12 -B declare.py check     # exit 0 consistent (pending items reported), 1 on a mismatch
    python3.12 -B declare.py hash      # refuses (exit 2) while an item is pending or once hashed
    python3.12 -B declare.py amend --reason TEXT --cause COMMIT PIN [PIN ...]

Part 2 (`fit-declaration.json`), after the ladders and before any fit render:

    python3.12 -B declare.py check-fit # the validated diff against the draft
    python3.12 -B declare.py hash-fit  # refuses before part 1 is hashed, on any invalid change, once hashed
    python3.12 -B declare.py amend-fit --reason TEXT --cause COMMIT PIN [PIN ...]

**What W45 binds, and refuses (X58).** The wave's charter pin, its evidence root, its scratch and
its part files are the constants below. A declaration naming another charter, a digest file
carrying W44's part hashes, and a ladder or fit evidence path in W44's directories or scratch are
refused before anything is checked (`bindings`; `test_declare.py` holds the red cases).

**What `check` re-derives.** `declaration.json` declares each item once, points at its source files
and pins every source by SHA-256 (a path suffixed `@<commit>` is read at that commit). `check`
re-reads every pin and re-derives what each item states from the files that define it: the
operator's inert landing and its proofs; T1 as adopted (the owner test at W44 G2's merge) with
the shared arithmetic and its tests; the bar; the referee manifest and the planner's two lists;
the landing rule, its synthetic cases and its rehearsal record (the verdicts recomputed); W45's
tools and their red cases; the ladders' protocol (every fixed cell a declared, non-referee,
non-holdout `__rest` cell, a probe cell in the pre-gate whitelist; every leaf one its slot's 0.5
document names or the operator's key; every rung inside its domain; the control and the joint
bases built and digest-identical to c05 and to W44's joint point); the two starting points; the
regression references against the generation index; and the draft.

**Part 2 is a validated diff** (W44's rule). `fit-declaration.json` is the draft's body plus a
`changes` list. `check-fit` applies the changes to the draft, each only where the ladder results
(`ladders/results.json`) support it, and the result must equal part 2's body exactly. A change is
one of the protocol's decisions and nothing else: `strike` (a leaf its ladder read flat), `narrow`
(a grid to a subset inside its ladder's non-flat range), `inert` (the 1x width's PENDING setting,
by X48 on every rung). Anything else is refused.

**Amendments** (W43's and W44's rule): an amendment re-pins named moved sources and changes
nothing else; each part is amended at most once; part 1's `amend` refuses once ANY ladder render
exists, part 2's `amend-fit` once any fit render exists.

**Part 2's second and final amendment** (G1 step 0; the charter's Decision Log 7, ruled at
`86c1b543`). The parent ruled ONE more amendment of part 2, before any fit render, for exactly these
items, and nothing else:

    python3.12 -B declare.py amend-fit --reason TEXT --cause 86c1b543

1. the side branch's three tool fixes (`w45-g0-search-fix`: a content twin never replaces a point's
   overrides; the sweeps refuse a partial objective; both checkers validate the amendment record),
   their moved part-2 pins and part 1's `declare.py` / `test_declare.py` re-recorded;
2. the operator's domain narrowed to [−share, 0] in stage 1 and in the receded difference
   (`domainLowerIsMinus`, checked by the fit driver on every point);
3. the 35-point share × width factorial from c05 as ONE coordinate step (`factorialGroups`);
6. the seal admitting what the builder admits (the receded second-tap widths), and part 2 stating
   the receded second widths inherited unless a point names them.

It is a CONTENT diff (W44 G1 step 0's form): `ops`, each an `add` or a `replace` at one path of part
2's body citing the ruling it executes with its `from` and `to`, and `pins`, each a moved source with
its `from`, `to` and the rulings that moved it. `RULINGS_TWO` is the only place a ruling's paths and
pins are stated; `validate_two` refuses an operation or pin outside its ruling, an unknown ruling, a
path touched twice, a removal and a ruling with nothing executed; `check-fit` recomputes the ops from
the body before the amendment (`amendment_two`) and requires the recorded ones equal, values included
(W44 G1's lesson). The chain reverts both amendments in turn, rebuilding `77f1c392…` and then
`da85de04…` byte for byte, and the draft's validated diff is checked on the body with every
amendment's operations reverted. A part-1 pin moved by both amendments is accepted only along the
chain the records state (`part_one_record`). After it, `amend-fit` refuses for ever: a third
amendment of part 2 has no ruling to cite.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CAL = ROOT / "packages" / "calibration"
REL = HERE.relative_to(ROOT).as_posix()
WAVE = "w45"
CHARTER_PATH = "docs/doperpowers/specs/2026-10-03-w45-span-selective-texture.md"
CHARTER_PIN = f"{CHARTER_PATH}@c152b89b"
W44_G0 = CAL / "results" / "2026-10-03-w44-g0-declaration"
W44_G1 = CAL / "results" / "2026-10-03-w44-g1-refit"
# W44's part hashes (its declaration.sha256 and fit-declaration.sha256 lines): never a W45 part.
W44_PART_HASHES = frozenset({
    *(ln.split()[0] for ln in (W44_G0 / "declaration.sha256").read_text().splitlines() if ln.strip()),
    *(ln.split()[0] for ln in (W44_G0 / "fit-declaration.sha256").read_text().splitlines() if ln.strip()),
})
W44_PLACES = re.compile(r"(^|/)(2026-10-03-w44-[^/]*|vitrea-w44)(/|$)")

PARTS = {
    "protocol": dict(declaration=HERE / "declaration.json", twin=HERE / "declaration.md",
                     digest=HERE / "declaration.sha256", amendments=HERE / "amendments.json",
                     schema="w45-declaration-1"),
    "fit": dict(declaration=HERE / "fit-declaration.json", twin=None,
                digest=HERE / "fit-declaration.sha256", amendments=HERE / "fit-amendments.json",
                schema="w45-fit-declaration-1"),
}
DRAFT = HERE / "fit-declaration-draft.json"
PROTOCOL = HERE / "ladders" / "protocol.json"
RESULTS = HERE / "ladders" / "results.json"
LADDER_RUNS = HERE / "ladders" / "runs.jsonl"
LADDER_SCRATCH = Path.home() / "vitrea-w45" / "g0-ladders"
G1 = CAL / "results" / "2026-10-03-w45-g1-refit"
FIT_RUNS = G1 / "fit" / "runs.jsonl"
FIT_SCRATCH = Path.home() / "vitrea-w45" / "g1-scratch"
LIGHT_025 = ("apple-macos-27.0-1x-light-standard-glass0.25", "apple-macos-27.0-2x-light-standard-glass0.25")
OPERATOR = "sizeHeavySecondShareFar2x"
CHAIN_LEVEL_1 = 1.542
# Part 1 cannot be amended once a ladder renders (it has). W44's rule, extended: part 2's one
# amendment may record moves of THESE part-1 sources (`partOnePins`, from the pinned hash to the
# bytes on disk), and may name part-1 sources that are to be read at a commit rather than live
# (`partOneReadAt`) — the light 0.25 documents, which G1's seal replaces by design. Part 1's
# declaration and its hash do not move; its check accepts exactly what the record names.
PART_ONE_REPINNABLE = tuple(f"{REL}/{p}" for p in ("declare.py", "test_declare.py", "cuts/rule.py",
                                                   "cuts/test_rule.py"))
PART_ONE_READ_AT_ADMISSIBLE = (
    "packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.25.json",
    "packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.25-receded.json",
)
CLAUSE_THREE = ("test_a_halving_f_with_three_cells_at_2b_passes", "test_b_four_cells_at_2b_fails",
                "test_c_one_cell_at_3_1b_fails", "test_d_a_stratum_aggregate_worse_beyond_its_tolerance_fails",
                "test_e_every_cell_unchanged_is_neither", "test_f_a_t_stratum_of_two_cells_is_reported_not_gated")

sha = lambda data: hashlib.sha256(data).hexdigest()  # noqa: E731


class Refusal(Exception):
    pass


def bindings() -> None:
    """X58: W45's tool refuses W44's charter, part hashes, directories and scratch."""
    for path in (HERE, LADDER_SCRATCH, FIT_SCRATCH, G1, RESULTS, LADDER_RUNS, FIT_RUNS):
        if W44_PLACES.search(str(path)):
            raise Refusal(f"{path} is W44's evidence or scratch; W45 declares into its own (X58)")
    for part in PARTS.values():
        if part["declaration"].exists():
            d = json.loads(part["declaration"].read_text())
            if d.get("charter") not in (None, CHARTER_PIN) and "w44" in str(d.get("charter")):
                raise Refusal(f"{part['declaration'].name} names W44's charter {d.get('charter')} (X58)")
            if str(d.get("schema", "")).startswith("w44-"):
                raise Refusal(f"{part['declaration'].name} carries W44's schema {d['schema']} (X58)")
        if part["digest"].exists():
            for ln in part["digest"].read_text().splitlines():
                if ln.strip() and ln.split()[0] in W44_PART_HASHES:
                    raise Refusal(f"{part['digest'].name} carries W44's part hash {ln.split()[0][:12]} (X58)")


def git_show(path: str, commit: str) -> bytes:
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"], check=True,
                          capture_output=True).stdout


def part_one_moves() -> dict:
    """{key: [move, ...]}: every recorded move of a re-pinnable part-1 source, in amendment order."""
    out = {}
    for a in amendments("fit"):
        for k, v in (a.get("partOnePins") or {}).items():
            if k in PART_ONE_REPINNABLE:
                out.setdefault(k, []).append(v)
    return out


def part_one_record() -> tuple[dict, dict]:
    """(partOnePins, partOneReadAt) as part 2's amendments record them, each restricted to the
    sources it may name: an entry outside PART_ONE_REPINNABLE or PART_ONE_READ_AT_ADMISSIBLE never
    re-routes a read or accepts a pin (`part_one_record_failures` reports it). A source moved by more
    than one amendment is recorded as ONE move from its part-1 pin to the last amendment's bytes,
    and only when each later move starts where the earlier one ended; a chain that breaks accepts
    nothing."""
    pins, read_at = {}, {}
    for key, moves in part_one_moves().items():
        if all(moves[i]["from"] == moves[i - 1]["to"] for i in range(1, len(moves))):
            pins[key] = {"from": moves[0]["from"], "to": moves[-1]["to"]}
    for a in amendments("fit"):
        read_at.update({k: v for k, v in (a.get("partOneReadAt") or {}).items()
                        if k in PART_ONE_READ_AT_ADMISSIBLE})
    return pins, read_at


def part_one_record_failures() -> list[str]:
    """The record's entries a checker must refuse: a key outside its admissible set, or a read-at
    commit whose bytes are not the part-1 pin."""
    out = []
    part1 = json.loads(PARTS["protocol"]["declaration"].read_text())["sources"]
    for key, moves in part_one_moves().items():
        for i in range(1, len(moves)):
            if moves[i]["from"] != moves[i - 1]["to"]:
                out.append(f"part 2's amendments re-pin {key} along a chain that breaks: move {i + 1} starts at "
                           f"{str(moves[i]['from'])[:12]}, not where move {i} ended ({str(moves[i - 1]['to'])[:12]})")
    for a in amendments("fit"):
        for key in a.get("partOnePins") or {}:
            if key not in PART_ONE_REPINNABLE:
                out.append(f"part 2's amendment re-pins {key}, which no amendment may re-pin")
        for key, commit in (a.get("partOneReadAt") or {}).items():
            if key not in PART_ONE_READ_AT_ADMISSIBLE:
                out.append(f"part 2's amendment reads {key} at {commit}, and only the light 0.25 documents may be")
            elif key not in part1 or sha(git_show(key, commit)) != part1[key]:
                out.append(f"part 2's amendment reads {key} at {commit}, whose bytes are not part 1's pin")
    return out


def source_bytes(key: str, live: bool = False) -> bytes:
    """A pinned source's bytes: `path@commit` at that commit; a part-1 source part 2's amendment
    names in `partOneReadAt` at the recorded commit (unless `live`); anything else on disk."""
    if "@" in key:
        path, commit = key.rsplit("@", 1)
        return git_show(path, commit)
    if not live:
        commit = part_one_record()[1].get(key)
        if commit is not None:
            return git_show(key, commit)
    return (ROOT / key).read_bytes()


def accepted_repin(key: str, pinned: str, now: str) -> bool:
    """A moved part-1 pin is accepted only for `PART_ONE_REPINNABLE` and only when part 2's
    amendment names exactly that move, from the pinned hash to the bytes on disk."""
    move = part_one_record()[0].get(key)
    return key in PART_ONE_REPINNABLE and bool(move) and move.get("from") == pinned and move.get("to") == now


def ran_at_least(out: str, count: int) -> bool:
    m = re.search(r"^Ran (\d+) tests?", out, flags=re.M)
    return m is not None and int(m.group(1)) >= count


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


def last_line(out: str) -> str:
    lines = [ln for ln in out.strip().splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def r4(x):
    return None if x is None else round(x, 4)


def ev(rel: str) -> Path:
    return HERE / rel


def cuts_modules():
    """W45's cuts directory first, then W44 G1's (its `t1` binds to W45's `bed`)."""
    if str(HERE / "cuts") not in sys.path:
        sys.path.insert(0, str(HERE / "cuts"))
    import bed  # noqa: F401
    if str(W44_G1 / "cuts") not in sys.path:
        sys.path.insert(1, str(W44_G1 / "cuts"))
    if str(W44_G0 / "referees") not in sys.path:
        sys.path.append(str(W44_G0 / "referees"))
    import plan
    import rule
    import t1
    return bed, t1, rule, plan


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
            got = sha(source_bytes(key))
        except (OSError, subprocess.CalledProcessError) as err:
            c.failures.append(f"pin {key}: unreadable ({err})")
            continue
        if got != want and accepted_repin(key, want, got):
            continue
        c.eq(f"pin {key}", got, want)
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


def check_operator(c, it):
    d = it["declared"]
    compare = ev("operator/compare.txt").read_text()
    c.true("operator: compare.txt does not read every identity case byte-identical",
           f"identity cases byte-identical: {d['identityCases']} of {d['identityCases']}" in compare
           and "failures: none" in compare)
    digests = ev("operator/digests.txt").read_text()
    c.true("operator: digests.txt does not read every shipped document unchanged",
           f"{d['documents']} of {d['documents']} documents reproduce their recorded digest" in digests)
    goldens = ev("operator/after/goldens.txt").read_text()
    c.true(f"operator: after/goldens.txt is not {d['goldens']} passed", f"{d['goldens']} passed" in goldens)
    material = source_bytes(d["material"]).decode()
    c.true("operator: DEFAULT_MATERIAL_PROFILE does not hold the leaf at 0",
           f"  {OPERATOR}: 0,\n" in material)
    c.true("operator: MATERIAL_IDENTITY_TABLE carries no plain-drop entry for the leaf",
           f"gate: {{ {OPERATOR}: 0 }},\n    gated: [],\n" in material)
    shader = source_bytes(d["shader"]).decode()
    c.true("operator: the optics pass's graded share is not the declared expression",
           d["shaderExpression"] in shader)
    owner = source_bytes(d["ownerTest"]).decode()
    c.true("operator: the owner test's authorised list is not landed empty",
           "const T1_AUTHORISED_REGRESSIONS: readonly T1AuthorisedRegression[] = [];" in owner)
    for commit in d["commits"]:
        got = subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", commit, "HEAD"])
        c.true(f"operator: {commit} is not an ancestor of HEAD", got.returncode == 0)


def check_t1(c, it):
    _, t1, _, plan = cuts_modules()
    d = it["declared"]
    held = plan.referee_cells(plan.load_manifest())
    for p in LIGHT_025:
        pop = t1.population([p])
        got = dict(cells=len(pop))
        for s in ("F", "T", "C", "P"):
            got[s] = sum(1 for _, sid in pop if t1.stratum(sid) == s)
        for part in ("gate", "holdout", "referee"):
            got[part] = sum(1 for _, sid in pop if t1.partition(p, sid, held) == part)
        c.eq(f"t1: population of {p}", got, d["populationPerLightProfile"])
    c.eq("t1: strata", {k: list(v) for k, v in t1.STRATA.items()}, d["strata"])
    c.eq("t1: ratio clause", t1.RATIO_CLAUSE, d["ratioClause"])
    c.eq("t1: g = 0 tolerance", t1.EQUAL, d["equalTolerance"])
    c.eq("t1: gated profiles", list(t1.GATED_PROFILES), d["gatedProfiles"])
    adopted = source_bytes(d["adoptedOwnerTest"]).decode()
    for needle in d["adoptedNeedles"]:
        c.true(f"t1: the owner test at adoption does not carry {needle!r}", needle in adopted)
    rc, out = run("-m", "unittest", "test_t1", cwd=W44_G1 / "cuts")
    c.true(f"t1: W44 G1's test_t1 does not pass ({last_line(out) or rc})", rc == 0)


def check_bar(c, it):
    d = it["declared"]
    bar = json.loads((W44_G0 / "bar/t1-bar.json").read_text())
    c.eq("bar: cells", bar["cells"], d["cells"])
    c.eq("bar: gated cells", sum(1 for x in bar["table"] if x["gated"]), d["gatedCells"])
    c.true("bar: a cell's bar is not half its code",
           all(abs(x["bar"] - 0.5 * x["code"]) < 1e-15 for x in bar["table"]))
    c.eq("bar: largest separation", bar["maxSeparation"], d["maxSeparation"])


def check_manifest(c, it):
    _, _, _, plan = cuts_modules()
    d = it["declared"]
    m = plan.load_manifest()
    lists = plan.lists(m)
    c.eq("manifest: scenes", m["scenes"], d["scenes"])
    c.eq("manifest: profiles", m["profiles"], d["profiles"])
    for name in ("pregateProbe", "exposure"):
        got = lists[name]
        c.eq(f"manifest: {name} count", got["count"], d[name]["count"])
        c.eq(f"manifest: {name} list", sha(",".join(got["scenes"]).encode()), d[name]["listSha256"])
    rc, out = run("-m", "unittest", "test_plan", cwd=W44_G0 / "referees")
    c.true(f"manifest: test_plan does not pass ({last_line(out) or rc})", rc == 0)


def check_rule(c, it):
    import gzip
    _, _, rule, _ = cuts_modules()
    d = it["declared"]
    c.eq("rule: constants", dict(budgetCount=rule.BUDGET_COUNT, budgetCeilingB=rule.BUDGET_CEILING_B,
                                 gatingMinCells=rule.GATING_MIN_CELLS), d["constants"])
    rc, out = run("-m", "unittest", "-v", "test_rule", cwd=HERE / "cuts")
    c.true(f"rule: test_rule does not pass ({last_line(out) or rc})", rc == 0)
    c.true(f"rule: test_rule runs fewer than {d['syntheticCases']} cases", ran_at_least(out, d["syntheticCases"]))
    for name in CLAUSE_THREE:
        c.true(f"rule: clause 3's case {name} does not run and pass", re.search(rf"^{name} .* ok$", out, re.M) is not None)
    reh = json.loads(ev("rehearsal/rehearsal.json").read_text())
    rule_now = sha(ev("cuts/rule.py").read_bytes())
    rule_from = (part_one_record()[0].get(f"{REL}/cuts/rule.py") or {}).get("from")
    c.true("rule: the rehearsal's rule file is neither the current rule.py nor the one part 2's amendment "
           "re-pinned it from", reh["rule"]["sha256"] in (rule_now, rule_from))
    got = {}
    for x in reh["rows"]:
        src = ROOT / x["source"]
        c.eq(f"rule: {x['label']} source", sha(src.read_bytes()), x["sourceSha256"])
        t = json.loads(gzip.open(src).read())["T1"]
        r = rule.evaluate(t["cells"], t["missing"])
        c.eq(f"rule: {x['label']} verdict recomputed", r["verdict"], x["verdict"])
        got[x["label"]] = [r["verdict"], len(r["awayBeyondB"]), len(r["awayBeyondCeiling"]),
                           sorted(r["gatedAggregateFailures"])]
    c.eq("rule: the rehearsal's verdicts", got, d["rehearsal"])
    c.eq("rule: partial candidates, every one UNMEASURED",
         (reh["partialCount"], all(p["verdict"].startswith("UNMEASURED") for p in reh["partial"])),
         (d["partialUnmeasured"], True))
    c.eq("rule: the joint point fails on count and ceiling",
         (reh["joint"]["failsOnCount"], reh["joint"]["failsOnCeiling"]), (True, True))


def check_tools(c, it):
    d = it["declared"]
    for test, cwd, count in d["tests"]:
        rc, out = run("-m", "unittest", test, cwd=HERE / cwd)
        c.true(f"tools: {cwd}/{test} does not pass ({last_line(out) or rc})", rc == 0)
        c.true(f"tools: {cwd}/{test} runs fewer than {count} cases", ran_at_least(out, count))
    rc, out = run(ev("rehearsal/port-proof.py"))
    c.true(f"tools: the cuts port does not reproduce W44 G1's c05 cut ({last_line(out) or rc})", rc == 0)


def check_ladders(c, it):
    _, t1, _, plan = cuts_modules()
    d = it["declared"]
    p = json.loads(PROTOCOL.read_text())
    m = plan.load_manifest()
    held = plan.referee_cells(m)
    scenes = plan.load_scenes()
    pregate = set(plan.lists(m)["pregateProbe"]["scenes"])
    cells = p["fixedCells"]["scenes"]
    c.eq("ladders: fixed cells", len(cells), d["fixedCells"])
    for sid in cells:
        c.true(f"ladders: {sid} is not a __rest cell", sid.endswith("__rest"))
        for prof in LIGHT_025:
            c.true(f"ladders: {prof} does not declare {sid}", sid in scenes["declared"][prof])
            c.true(f"ladders: {sid} is a referee", (prof, sid) not in held)
        role = scenes["role"].get(sid)
        c.true(f"ladders: {sid} is {role}", role in ("calibration", "probe"))
        if role == "probe":
            c.true(f"ladders: {sid} is a probe scene outside the pre-gate whitelist", sid in pregate)
        c.true(f"ladders: {sid} is not in a set the ladder renders", role in p["fixedCells"]["sets"].split(","))
    twins = {}
    for slot in ("active.light", "receded.light"):
        doc = json.loads((CAL / f"profiles/apple-macos-27.0-1x-light-standard-glass0.5"
                          f"{'-receded' if slot.startswith('receded') else ''}.json").read_text())
        twins[slot] = doc["patch"]
    named = lambda slot, leaf: leaf in twins[slot] or leaf == OPERATOR  # noqa: E731
    for name, base in p["bases"].items():
        for slot, over in base["overrides"].items():
            for leaf in over:
                c.true(f"ladders: base {name} {leaf} is not a leaf {slot} names (X44 as narrowed)", named(slot, leaf))
    rungs = 0
    for lad in p["ladders"]:
        reads = [s for v in lad["reads"].values() for s in (v if isinstance(v, list) else [v])]
        for sid in reads:
            c.true(f"ladders: {lad['id']} reads {sid}, not a fixed cell", sid in cells)
        if lad["id"] == "v":
            for lever in lad["levers"]:
                rungs += 1
                for leaf in lever["set"]:
                    c.true(f"ladders: v {leaf} is not a leaf active.light names", named("active.light", leaf))
            continue
        for leaf in lad["leaves"] + list(lad.get("fixed", {})) + list(lad.get("at", {})):
            c.true(f"ladders: {lad['id']} {leaf} is not a leaf {lad['slot']} names (X44 as narrowed)",
                   named(lad["slot"], leaf))
        if "grid" in lad:
            n = 1
            for leaf, values in lad["grid"].items():
                n *= len(values)
                lo, hi = lad["domain"][leaf]
                c.true(f"ladders: {lad['id']} {leaf} grid outside {lad['domain'][leaf]}",
                       all(lo <= x <= hi for x in values))
                if leaf == "sizeHeavySecondSigma2x":
                    c.true(f"ladders: {lad['id']} width below the chain's level-1 width",
                           all(x >= CHAIN_LEVEL_1 for x in values))
            rungs += n
        else:
            lo, hi = lad["domain"]
            c.true(f"ladders: {lad['id']} values outside {lad['domain']}", all(lo <= x <= hi for x in lad["values"]))
            rungs += len(lad["values"]) * max([1] + [len(v) for v in lad.get("at", {}).values()])
    c.eq("ladders: rungs (as declared, before content dedup)", rungs, d["rungs"])
    c.eq("ladders: ids", [lad["id"] for lad in p["ladders"]], d["ids"])
    c.eq("ladders: decisions", sorted(p["decisions"]), sorted(d["decisions"]))
    c.eq("ladders: the 1x second width is held at 0 on every base",
         all(base["overrides"].get("active.light", {}).get("sizeHeavySecondSigma", 0) == 0
             for base in p["bases"].values()), True)
    for name, label in (("control", "c05-control"), ("J", "base-joint")):
        cand = HERE / "ladders" / "candidates" / label / "candidate.json"
        c.true(f"ladders: base {name} is not built ({cand.relative_to(ROOT)})", cand.exists())
        if not cand.exists():
            continue
        body = json.loads(cand.read_text())
        for slot, entry in body["endpoints"].items():
            doc = json.loads((cand.parent / entry["path"]).read_text())
            want = (d["controlDigests"] if name == "control" else d["jointDigests"])[slot]
            c.eq(f"ladders: base {name} {slot} digest", doc["resolvedMaterialSha256"], want)


def check_starting_points(c, it):
    d = it["declared"]
    for slot, path in d["c05"]["documents"].items():
        doc = json.loads(source_bytes(path))
        c.eq(f"startingPoints: c05 {slot} digest", doc["resolvedMaterialSha256"], d["c05"]["digests"][slot])
    c.eq("startingPoints: the joint point's declaration hash", sha((ROOT / d["joint"]["candidate"]).read_bytes()),
         d["joint"]["declarationSha256"])
    spec = json.loads((ROOT / d["joint"]["candidate"]).parent.joinpath("spec.json").read_text())
    c.eq("startingPoints: the joint point's overrides", spec["overrides"], d["joint"]["overrides"])


def check_references(c, it):
    index = json.loads((CAL / "results/generations/index.json").read_text())
    for scheme, entry in it["declared"]["generations"].items():
        f = index["files"].get(f"{entry['active']}.json")
        c.true(f"references: no generation {entry['active']}", f is not None)
        if f:
            # The index's own record and the immutable file's bytes; whether the generation is still
            # CURRENT is not the claim (G1's publication retires it).
            c.eq(f"references: {scheme} index sha256", f["sha256"], entry["sha256"])
            c.eq(f"references: {scheme} file sha256",
                 sha((CAL / "results/generations" / f"{entry['active']}.json").read_bytes()), entry["sha256"])


def draft_leaves(draft):
    """(stage id, family, leaf key, spec) for every searched leaf of the draft (W44's `moves` shape:
    a stage is a `moves` entry, its families carry the leaves; a tied pair is keyed `a+b`)."""
    for move in draft["moves"]:
        for fam, body in move["families"].items():
            for key, spec in body.get("leaves", {}).items():
                yield move["id"], fam, key, spec


def check_draft(c, it):
    d = it["declared"]
    draft = json.loads(DRAFT.read_text())
    protocol = json.loads(PROTOCOL.read_text())
    ladders = {lad["id"] for lad in protocol["ladders"]}
    c.eq("draft: schema", draft["schema"], PARTS["fit"]["schema"])
    c.eq("draft: stages", [m["id"] for m in draft["moves"]], d["stages"])
    c.eq("draft: references", draft["references"]["c05"], {"light": "6d18c059eb42", "dark": "d0219cd684bf"})
    count = 0
    for mid, fam, key, spec in draft_leaves(draft):
        sid = f"{mid}/{fam}"
        count += 1
        grid, dom = spec["grid"], spec["domain"]
        c.true(f"draft: {sid}/{key} grid not sorted and distinct",
               sorted(set(grid)) == sorted(grid) and len(set(grid)) == len(grid))
        if "domainRelativeTo" not in spec:
            c.true(f"draft: {sid}/{key} grid {grid} outside its domain {dom}", all(dom[0] <= x <= dom[1] for x in grid))
        c.true(f"draft: {sid}/{key} has no unit", bool(spec.get("unit")))
        c.true(f"draft: {sid}/{key} names a ladder the protocol does not declare",
               spec.get("ladder") is None or spec["ladder"] in ladders)
    c.eq("draft: searched leaves", count, d["searchedLeaves"])
    c.eq("draft: the operator's grid (stage 1)",
         next(s for m, _, k, s in draft_leaves(draft) if m == "stage1" and k == OPERATOR)["grid"], d["operatorGrid"])
    c.eq("draft: the span top's grid", next(s for _, _, k, s in draft_leaves(draft)
                                             if k == "sizeScatterSpanMax2x")["grid"], d["spanTopGrid"])
    c.eq("draft: the scopes", {f"{m['id']}/{f}": b.get("scope") or m.get("scope") for m in draft["moves"]
                               for f, b in m["families"].items()}, d["scopes"])
    c.eq("draft: the landing rule's implementation", draft["landingRule"]["implementation"], "cuts/rule.py (pinned by part 1)")


CHECKS = {"operator": check_operator, "t1": check_t1, "bar": check_bar, "manifest": check_manifest,
          "rule": check_rule, "tools": check_tools, "ladders": check_ladders,
          "startingPoints": check_starting_points, "references": check_references, "draft": check_draft}


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
        c.true(f"chain ({part}): amendment {i + 1} states a reason and a cause",
               bool(a.get("reason")) and bool(a.get("cause")))
        for path, move in (a.get("pins") or {}).items():
            c.eq(f"chain ({part}): amendment {i + 1} pin {path}", state["sources"].get(path), move.get("to"))
            state["sources"][path] = move.get("from")
        if a.get("ops"):
            try:
                state = revert_ops(state, a["ops"])
            except Refusal as err:
                c.failures.append(f"chain ({part}): amendment {i + 1}'s operations do not revert: {err}")
                return
        c.eq(f"chain ({part}): the declaration before amendment {i + 1} rebuilt", sha(serialise(state)), lines[i])


def check_protocol():
    c = Check()
    d = json.loads(PARTS["protocol"]["declaration"].read_text())
    c.eq("schema", d.get("schema"), PARTS["protocol"]["schema"])
    c.eq("charter", d.get("charter"), CHARTER_PIN)
    chain(c, "protocol", d)
    c.failures += part_one_record_failures()
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
def leaf_spec(body, move_id, family, key):
    move = next((m for m in body["moves"] if m["id"] == move_id), None)
    fam = None if move is None else move["families"].get(family)
    return None if fam is None else fam.get("leaves", {}).get(key)


def apply_changes(draft, changes, results, protocol):
    """The draft with `changes` applied, each only where the ladder results support it and the
    protocol lets the cited ladder make that kind of decision (`x48` makes only `inert`)."""
    body = json.loads(json.dumps(draft))
    ladders = results.get("ladders", {})
    decides = {lad["id"]: set(lad["decides"]) for lad in protocol["ladders"]}
    decides["x48"] = {"inert"}
    for ch in changes:
        kind = ch.get("kind")
        lad = ladders.get(ch.get("ladder"))
        if lad is None:
            raise Refusal(f"{ch}: cites no ladder in the results")
        if kind not in decides.get(ch.get("ladder"), set()):
            raise Refusal(f"{ch}: the protocol does not let {ch.get('ladder')} decide a {kind}")
        if kind in ("strike", "narrow"):
            spec = leaf_spec(body, ch.get("move"), ch.get("family"), ch.get("leaf"))
            if spec is None:
                raise Refusal(f"{ch}: names no leaf of the draft")
            if spec.get("ladder") != ch["ladder"]:
                raise Refusal(f"{ch}: {ch['ladder']} is not {ch['leaf']}'s ladder")
            if kind == "strike":
                if ch["leaf"] not in (lad.get("struck") or []):
                    raise Refusal(f"{ch}: {ch['ladder']} did not strike {ch['leaf']}")
                move = next(m for m in body["moves"] if m["id"] == ch["move"])
                del move["families"][ch["family"]]["leaves"][ch["leaf"]]
                if not move["families"][ch["family"]]["leaves"]:
                    del move["families"][ch["family"]]
                    move["familyOrder"].remove(ch["family"])
            else:
                grid = ch.get("grid")
                rng = (lad.get("nonFlatRange") or {}).get(ch["leaf"])
                if not grid or not isinstance(grid, list) or rng is None:
                    raise Refusal(f"{ch}: a narrowing names a grid and its ladder a non-flat range")
                if not set(grid) <= set(spec["grid"]) or len(set(grid)) != len(grid):
                    raise Refusal(f"{ch}: {grid} is not a subset of the draft grid {spec['grid']}")
                if not all(min(rng) <= x <= max(rng) for x in grid):
                    raise Refusal(f"{ch}: {grid} leaves {ch['ladder']}'s non-flat range {rng}")
                spec["grid"] = [x for x in spec["grid"] if x in grid]
        elif kind == "inert":
            if not lad.get("inert1x"):
                raise Refusal(f"{ch}: the 1x width's inert setting is fixed only by X48 holding on every rung")
            fixed = body["moves"][0]["families"]["deep"]["fixed"]["sizeHeavySecondSigma"]
            if fixed["value"] != 0:
                raise Refusal(f"{ch}: the inert setting is 0, the only one offered")
            fixed["inert"] = ("proven by the ladders: every rung's 1x captures pixel-identical to "
                              "c05-control's (ladders/results.json, X48)")
        else:
            raise Refusal(f"{ch}: not one of the protocol's decisions (strike, narrow, inert)")
    return body


def validate_fit(draft, fit, results, protocol):
    """Raise Refusal unless `fit` is the draft changed only by its own permitted `changes`."""
    if fit.get("schema") != draft["schema"]:
        raise Refusal("part 2's schema is not the draft's")
    changes = fit.get("changes")
    if not isinstance(changes, list):
        raise Refusal("part 2 lists its changes against the draft (`changes`), even when there are none")
    expected = apply_changes(draft, changes, results, protocol)
    expected.pop("status", None)
    got = {k: v for k, v in fit.items() if k not in ("status", "changes", "sources", "fromDraft")}
    if json.dumps(got, sort_keys=True) != json.dumps(expected, sort_keys=True):
        diff = [k for k in set(got) | set(expected) if got.get(k) != expected.get(k)]
        raise Refusal(f"part 2 differs from the draft beyond its permitted changes, in: {sorted(diff)}")


def check_fit():
    c = Check()
    if not PARTS["protocol"]["digest"].exists():
        c.failures.append("part 1 is not hashed; part 2 is checked only after it")
        return c, None
    fit_path = PARTS["fit"]["declaration"]
    if not fit_path.exists():
        c.failures.append("fit-declaration.json does not exist")
        return c, None
    fit = json.loads(fit_path.read_text())
    c.eq("fit: schema", fit.get("schema"), PARTS["fit"]["schema"])
    part1 = digest_lines("protocol")
    c.eq("fit: names part 1's hash", (fit.get("fromDraft") or {}).get("partOneSha256"), part1[0] if part1 else None)
    c.eq("fit: names the draft's hash", (fit.get("fromDraft") or {}).get("draftSha256"), sha(DRAFT.read_bytes()))
    chain(c, "fit", fit)
    c.failures += part_one_record_failures()
    for key, want in (fit.get("sources") or {}).items():
        try:
            c.eq(f"pin {key}", sha(source_bytes(key)), want)
        except (OSError, subprocess.CalledProcessError) as err:
            c.failures.append(f"pin {key}: unreadable ({err})")
    c.true("fit: ladders/results.json is not one of part 2's pinned sources",
           f"{REL}/ladders/results.json" in (fit.get("sources") or {}))
    record = amendments("fit")
    c.true(f"fit: part 2 carries {len(record)} amendments; the charter rules at most two (Decision Log 7)",
           len(record) <= 2)
    body = fit
    if len(record) >= 2:
        body = check_amendment_two(c, fit, record[1])
    try:
        validate_fit(json.loads(DRAFT.read_text()), body, json.loads(RESULTS.read_text()),
                     json.loads(PROTOCOL.read_text()))
    except Refusal as err:
        c.failures.append(f"fit: {err}")
    return c, fit


# ---------------------------------------------------------------------------------------------
# Part 2's second and final amendment: the charter's Decision Log 7 (G1 step 0)
# ---------------------------------------------------------------------------------------------
RULING_COMMIT = "86c1b543"
_FIT = f"{REL}/fit"
DELTA_ACTIVE = ("moves", 0, "families", "deep", "leaves", OPERATOR)
DELTA_RECEDED = ("moves", 1, "families", "receded", "leaves", OPERATOR)
FACTORIAL = ("moves", 0, "families", "deep", "factorialGroups")
INHERITS = ("moves", 1, "inherits")
RULINGS_TWO = {
    1: dict(title="a second amendment, final: the side branch's three tool fixes (w45-g0-search-fix 50be5c44, "
                  "371d3f1c) re-pinned, and amend-fit accepting this amendment once and then refusing for ever",
            paths=[], pins=[f"{_FIT}/fit.py", f"{_FIT}/search.py", f"{_FIT}/joint.py", f"{_FIT}/finding.py",
                            f"{_FIT}/test_fit.py"],
            partOnePins=[f"{REL}/declare.py", f"{REL}/test_declare.py"]),
    2: dict(title="the grading's domain is the monotone range: sizeHeavySecondShareFar2x in [-share, 0] in stage 1 "
                  "and in the receded difference",
            paths=[DELTA_ACTIVE, DELTA_RECEDED], pins=[f"{_FIT}/fit.py", f"{_FIT}/search.py", f"{_FIT}/test_fit.py"],
            partOnePins=[]),
    3: dict(title="the (share, width) factorial is the permitted full factorial: stage 1 runs the 35-point "
                  "share x width grid from c05 as one coordinate step, through a driver option",
            paths=[FACTORIAL], pins=[f"{_FIT}/search.py", f"{_FIT}/test_fit.py"], partOnePins=[]),
    6: dict(title="the seal admits what the builder admits (the receded second-tap widths), and part 2 declares "
                  "the receded second widths inherited unless a point names them",
            paths=[INHERITS], pins=[f"{REL}/seal/seal.ts", f"{REL}/seal/test_seal.py"], partOnePins=[]),
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


def validate_two(entry):
    """Refuse unless the entry carries exactly Decision Log 7's rulings: every operation an add or a
    replace at one of its ruling's paths, every pin a source one of its rulings moves, no path touched
    twice, and every ruling executed by an operation or a pin."""
    ops, pins, one = entry.get("ops"), entry.get("pins") or {}, entry.get("partOnePins") or {}
    if not isinstance(ops, list) or not ops:
        raise Refusal("the second amendment carries no operations")
    seen, executed = set(), set()
    for op in ops:
        r, kind, path = op.get("ruling"), op.get("kind"), tuple(op.get("path") or ())
        if r not in RULINGS_TWO:
            raise Refusal(f"{list(path)}: cites ruling {r!r}, not one of Decision Log 7's {sorted(RULINGS_TWO)}")
        if kind not in OP_KINDS:
            raise Refusal(f"{list(path)}: {kind!r} is not an add or a replace (nothing is removed)")
        if path not in [tuple(x) for x in RULINGS_TWO[r]["paths"]]:
            raise Refusal(f"{list(path)}: not a path ruling {r} changes")
        if path in seen:
            raise Refusal(f"{list(path)}: touched twice")
        if kind == "add" and "from" in op:
            raise Refusal(f"{list(path)}: an add states no `from`")
        if kind == "replace" and "from" not in op:
            raise Refusal(f"{list(path)}: a replace states its `from`")
        seen.add(path)
        executed.add(r)
    for key, move in pins.items():
        rulings = move.get("rulings") or []
        if not rulings or any(r not in RULINGS_TWO or key not in RULINGS_TWO[r]["pins"] for r in rulings):
            raise Refusal(f"pin {key}: cites rulings {rulings}, and no ruling of Decision Log 7 among them moves it")
        executed.update(rulings)
    for key, move in one.items():
        rulings = move.get("rulings") or []
        if not rulings or any(r not in RULINGS_TWO or key not in RULINGS_TWO[r]["partOnePins"] for r in rulings):
            raise Refusal(f"part-1 pin {key}: cites rulings {rulings}, and no ruling of Decision Log 7 among them moves it")
        executed.update(rulings)
    missing = sorted(set(RULINGS_TWO) - executed)
    if missing:
        raise Refusal(f"rulings {missing} carry nothing; the amendment is all of Decision Log 7's items or nothing")


def amendment_two(fit):
    """Decision Log 7's content rulings (2, 3 and 6) as operations on part 2's body `fit`."""
    ops = []

    def op(ruling, path, to):
        node, key = _walk(fit, tuple(path))
        entry = dict(ruling=ruling, kind="replace" if _present(node, key) else "add", path=list(path))
        if entry["kind"] == "replace":
            entry["from"] = node[key]
        entry["to"] = to
        ops.append(entry)

    active = _walk(fit, DELTA_ACTIVE)
    receded = _walk(fit, DELTA_RECEDED)
    ladder = ("the isolation ladder (i) read checkerboard-8__rrect-lg__rest monotone in the delta down to -0.75 at "
              "share 0.5 and reversed at -1, where share + delta crossed zero and the signed share became an unsharp "
              "mask that adds the c = 16 structure back (claims 5.205 section 8 (i)); the isolation bar is met on "
              "this domain (md byte-identical, the thick cells monotone)")
    op(2, DELTA_ACTIVE, dict(active[0][active[1]], domainLowerIsMinus="sizeHeavySecondShare", jointDomain=(
        "sizeHeavySecondShareFar2x in [-share, 0], share the point's resolved active sizeHeavySecondShare, so the "
        "graded share + delta * farS is never negative at any span; [-1, 0] is the box the grid spans. Checked on "
        "every point whatever it moves (fit.joint_domain_failures): a grid point outside it at the others' "
        "current values is not a candidate, of a delta sweep or of a share sweep holding the delta"),
        why=f"Decision Log 7 item 2, a narrowing to the monotone range: {ladder}"))
    op(2, DELTA_RECEDED, dict(receded[0][receded[1]], domainLowerIsMinus="sizeHeavySecondShare", jointDomain=(
        "the receded delta, resolved, in [-share, 0], share the receded document's resolved sizeHeavySecondShare "
        "(its own difference where the point names one, else the active value); each key the receded document "
        "does not name resolves to the active value, so a receded share below the inherited delta's magnitude "
        "is not a candidate until the receded delta is narrowed with it"),
        why="Decision Log 7 item 2: the receded difference on the same monotone range as stage 1"))
    op(3, FACTORIAL, [{
        "keys": ["sizeHeavySecondShare", "sizeHeavySecondSigma2x"],
        "starts": ["c05"],
        "points": 35,
        "rule": ("on the c05 lineage the share and the width are swept as ONE coordinate step: their 5 x 7 grid in "
                 "full, at the position of the share in the listed order, in place of their two single-leaf sweeps, "
                 "in each pass (search.steps_of); a point outside the joint domain is not a candidate; content twins "
                 "render once and every point keeps its own overrides. From the joint point the coordinate sweep is "
                 "as before"),
        "why": ("Decision Log 7 item 3: from c05 (share 0, width 0) the share and the width gate each other (at share "
                "0 the width is unread, at width 0 the share does nothing), so a coordinate sweep leaves (0, 0) only "
                "through the grid's first width; this is the 'full factorial permitted' of searchProcedure")}])
    op(6, INHERITS, fit["moves"][1]["inherits"] + (
        "; the receded second-tap widths (sizeHeavySecondSigma, sizeHeavySecondSigma2x) are inherited from the "
        "active document unless a point names them, and no point of this part 2 names them (no receded width is a "
        "declared leaf); the seal admits what the builder admits: the receded share, both receded widths and the "
        "operator's key, each as a difference over the active document (Decision Log 7 item 6)"))
    return ops


def amendment_two_failures(fit, entry):
    """(failures, the body before the amendment): its rulings validated, its cause the ruling's
    commit with Decision Log 7 in the charter there, and its operations exactly `amendment_two` on
    the body they revert to, values included. The body is `fit` itself when they do not revert."""
    out = []
    try:
        validate_two(entry)
    except Refusal as err:
        out.append(f"amendment 2: {err}")
    if entry.get("cause") != RULING_COMMIT:
        out.append(f"amendment 2: its cause {entry.get('cause')!r} is not the ruling's commit {RULING_COMMIT}")
    try:
        if "### Decision Log 7" not in git_show(CHARTER_PATH, str(entry.get("cause"))).decode():
            out.append(f"amendment 2: the charter at {entry.get('cause')} carries no Decision Log 7")
    except subprocess.CalledProcessError as err:
        out.append(f"amendment 2: the cause {entry.get('cause')} is not readable ({err})")
    try:
        before = revert_ops(fit, entry.get("ops") or [])
    except Refusal as err:
        return out + [f"amendment 2: its operations do not revert: {err}"], fit
    try:
        if entry.get("ops") != amendment_two(before):
            out.append("amendment 2: the recorded operations are not amendment_two on the body before it "
                       "(values included)")
    except Refusal as err:
        out.append(f"amendment 2: amendment_two does not apply to the body before it: {err}")
    return out, before


def check_amendment_two(c, fit, entry):
    """The second amendment (`amendment_two_failures`), and the tests of what it pins passing (the fit
    driver's and the seal's). Returns part 2's body with BOTH amendments' operations reverted (the
    draft's validated diff is read there), or `fit` when they cannot be reverted."""
    failures, before = amendment_two_failures(fit, entry)
    c.failures += failures
    for name, folder, module in (("the fit driver", HERE / "fit", "test_fit"),
                                 ("the seal", HERE / "seal", "test_seal")):
        rc, out = run("-m", "unittest", module, cwd=folder)
        c.true(f"amendment 2: {name}'s tests do not pass ({last_line(out) or rc})", rc == 0)
    return before


# ---------------------------------------------------------------------------------------------
# Evidence and amendments
# ---------------------------------------------------------------------------------------------
def ladder_evidence():
    found = []
    if LADDER_RUNS.exists() and any('"started"' in ln for ln in LADDER_RUNS.read_text().splitlines()):
        found.append(str(LADDER_RUNS))
    if LADDER_SCRATCH.exists():
        found += [str(p) for p in sorted(LADDER_SCRATCH.rglob("matrix.json"))][:3]
        found += [str(p) for p in sorted(LADDER_SCRATCH.rglob("*.png"))][:1]
    return found


def fit_evidence():
    found = []
    if FIT_RUNS.exists() and any('"started"' in ln for ln in FIT_RUNS.read_text().splitlines()):
        found.append(str(FIT_RUNS))
    if FIT_SCRATCH.exists():
        found += [str(p) for p in sorted(FIT_SCRATCH.rglob("matrix.json"))][:3]
        found += [str(p) for p in sorted(FIT_SCRATCH.rglob("*.png"))][:1]
    return found


def amend(part, argv):
    import argparse
    ap = argparse.ArgumentParser(prog=f"declare.py amend{'-fit' if part == 'fit' else ''}")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--cause", required=True)
    ap.add_argument("pins", nargs="+")
    if part == "fit":
        ap.add_argument("--part-one-pin", action="append", default=[],
                        help="a moved part-1 source in PART_ONE_REPINNABLE, recorded from its pin to its bytes")
        ap.add_argument("--part-one-read-at", action="append", default=[],
                        help="KEY=COMMIT: a part-1 source to be read at COMMIT, whose bytes there are its pin")
    args = ap.parse_args(argv)
    lines = digest_lines(part)
    if not lines:
        print("amend REFUSES: the part is not hashed; before the hash it is simply edited and re-checked")
        return 2
    evidence = ladder_evidence() if part == "protocol" else fit_evidence()
    if evidence:
        print(f"amend REFUSES: render evidence exists for this part ({', '.join(evidence[:4])}); "
              "a render after the hash fixes it")
        return 2
    if amendments(part):
        print("amend REFUSES: this part was amended once already (each part is amended at most once)")
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
                                                       else "G1's fit runs and scratch") + ")"}
    if part == "fit" and (args.part_one_pin or args.part_one_read_at):
        part1 = json.loads(PARTS["protocol"]["declaration"].read_text())["sources"]
        one_pins, read_at = {}, {}
        for key in args.part_one_pin:
            if key not in PART_ONE_REPINNABLE:
                print(f"amend-fit REFUSES: {key} is not a part-1 source part 2's amendment may re-pin")
                return 2
            now = sha(source_bytes(key, live=True))
            if now == part1[key]:
                print(f"amend-fit REFUSES: part-1 source {key} has not moved")
                return 2
            one_pins[key] = {"from": part1[key], "to": now}
        for spec in args.part_one_read_at:
            key, _, commit = spec.rpartition("=")
            if key not in PART_ONE_READ_AT_ADMISSIBLE or key not in part1:
                print(f"amend-fit REFUSES: {key} is not a part-1 source that may be read at a commit")
                return 2
            if sha(git_show(key, commit)) != part1[key]:
                print(f"amend-fit REFUSES: {key} at {commit} is not the bytes part 1 pinned")
                return 2
            read_at[key] = commit
        entry["partOnePins"], entry["partOneReadAt"] = one_pins, read_at
    record = PARTS[part]["amendments"]
    old_raw, old_digest = path.read_bytes(), PARTS[part]["digest"].read_text()
    record.write_text(json.dumps({"schema": f"{WAVE}-{part}-amendments-1", "amendments": [entry]}, indent=2) + "\n")
    path.write_bytes(raw)
    with PARTS[part]["digest"].open("a") as f:
        f.write(f"{entry['declarationSha256']}  {path.name}\n")
    if part == "fit":
        # The record must leave part 1's check whole, or nothing is written.
        c1 = check_protocol()[0]
        if c1.failures:
            record.unlink()
            path.write_bytes(old_raw)
            PARTS[part]["digest"].write_text(old_digest)
            print("amend-fit REFUSES: part 1's check fails with this record:")
            for f in c1.failures:
                print("  MISMATCH", f)
            return 2
    print(f"amended: {path.name} sha256 {entry['declarationSha256']} supersedes {lines[-1]}")
    return 0


def amend_fit(argv):
    """Part 2's amendments: the first (pins only, W43's rule) while none exists; the second and
    final one (Decision Log 7) once, under the ruling's commit; never a third."""
    record = amendments("fit")
    if len(record) == 0:
        return amend("fit", argv)
    if len(record) >= 2:
        print("amend-fit REFUSES: part 2 was amended twice, the second time finally (the charter's Decision Log 7); "
              "it is never amended again")
        return 2
    return amend_fit_two(argv)


def amend_fit_two(argv):
    """The second and final amendment of part 2 (G1 step 0; Decision Log 7)."""
    import argparse
    ap = argparse.ArgumentParser(prog="declare.py amend-fit")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--cause", required=True, help="the charter commit that rules the amendment")
    args = ap.parse_args(argv)
    lines = digest_lines("fit")
    if not lines:
        print("amend-fit REFUSES: part 2 is not hashed")
        return 2
    evidence = fit_evidence()
    if evidence:
        print(f"amend-fit REFUSES: a fit render exists ({', '.join(evidence[:4])}); part 2 is fixed")
        return 2
    if args.cause != RULING_COMMIT:
        print(f"amend-fit REFUSES: the second amendment is ruled at {RULING_COMMIT}, not {args.cause}")
        return 2
    try:
        charter = git_show(CHARTER_PATH, args.cause).decode()
    except subprocess.CalledProcessError:
        print(f"amend-fit REFUSES: no charter at {args.cause}")
        return 2
    if "### Decision Log 7" not in charter:
        print(f"amend-fit REFUSES: the charter at {args.cause} carries no Decision Log 7")
        return 2
    path = PARTS["fit"]["declaration"]
    fit = json.loads(path.read_text())
    # Every moved source must be one a ruling moves; nothing else may fail.
    movable = {k: sorted(r for r, v in RULINGS_TWO.items() if k in v["pins"]) for v in RULINGS_TWO.values()
               for k in v["pins"]}
    moved = {k: sha(source_bytes(k)) for k in fit["sources"] if sha(source_bytes(k)) != fit["sources"][k]}
    stray = sorted(set(moved) - set(movable))
    if stray:
        print(f"amend-fit REFUSES: sources moved that no ruling of Decision Log 7 moves: {stray}")
        return 2
    c, _ = check_fit()
    other = [f for f in c.failures if not any(f.startswith(f"pin {k}:") for k in moved)]
    if other:
        print("amend-fit REFUSES: check-fit fails outside the moved pins:")
        for f in other:
            print("  MISMATCH", f)
        return 2
    part1 = json.loads(PARTS["protocol"]["declaration"].read_text())["sources"]
    composite = part_one_record()[0]
    one_movable = {k: sorted(r for r, v in RULINGS_TWO.items() if k in v["partOnePins"]) for v in RULINGS_TWO.values()
                   for k in v["partOnePins"]}
    one = {}
    for k in PART_ONE_REPINNABLE:
        now = sha(source_bytes(k, live=True))
        last = (composite.get(k) or {}).get("to", part1[k])
        if now != last:
            if k not in one_movable:
                print(f"amend-fit REFUSES: part-1 source {k} moved, and no ruling of Decision Log 7 moves it")
                return 2
            one[k] = {"from": last, "to": now, "rulings": one_movable[k]}
    c1, _, _ = check_protocol()
    other1 = [f for f in c1.failures if not any(f.startswith(f"pin {k}:") for k in one)]
    if other1:
        print("amend-fit REFUSES: part 1's check fails outside the part-1 sources this amendment re-pins:")
        for f in other1:
            print("  MISMATCH", f)
        return 2
    ops = amendment_two(fit)
    pins = {k: {"from": fit["sources"][k], "to": v, "rulings": movable[k]} for k, v in moved.items()}
    entry = {"n": 2, "supersedes": lines[-1], "reason": args.reason, "cause": args.cause,
             "charter": f"{CHARTER_PATH}@{args.cause} (Decision Log 7)",
             "rulings": {str(k): v["title"] for k, v in RULINGS_TWO.items()}, "ops": ops, "pins": pins,
             "partOnePins": one, "partOneReadAt": {},
             "renderEvidenceAtAmendment": "none (G1's fit runs and scratch)"}
    try:
        validate_two(entry)
        amended = apply_ops(fit, ops)
    except Refusal as err:
        print(f"amend-fit REFUSES: {err}")
        return 2
    for k, move in pins.items():
        amended["sources"][k] = move["to"]
    raw = serialise(amended)
    entry = {"n": 2, "supersedes": lines[-1], "declarationSha256": sha(raw),
             **{k: v for k, v in entry.items() if k not in ("n", "supersedes")}}
    record_path, digest_path = PARTS["fit"]["amendments"], PARTS["fit"]["digest"]
    old = {p: p.read_bytes() for p in (record_path, path, digest_path)}
    record = json.loads(old[record_path])
    record["amendments"].append(entry)
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    path.write_bytes(raw)
    with digest_path.open("a") as f:
        f.write(f"{entry['declarationSha256']}  {path.name}\n")
    after, _ = check_fit()
    after1, _, _ = check_protocol()
    if after.failures or after1.failures:
        for p, data in old.items():
            p.write_bytes(data)
        print("amend-fit REFUSES: the checks fail with this amendment written; nothing is kept:")
        for f in after.failures + after1.failures:
            print("  MISMATCH", f)
        return 2
    print(f"amended: {path.name} sha256 {entry['declarationSha256']} supersedes {lines[-1]}; check and check-fit "
          "consistent; part 2 is never amended again")
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
    try:
        bindings()
    except Refusal as err:
        print(f"declare.py REFUSES: {err}")
        return 2
    if verb == "amend":
        return amend("protocol", argv[2:])
    if verb == "amend-fit":
        return amend_fit(argv[2:])
    if verb in ("check", "hash"):
        c, d, items = check_protocol()
        waiting = [it for it in items.values() if "pending" in it]
        print(f"W45 G0 part 1: {len(items)} items, {len(d['sources'])} pinned sources")
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
            print("hash REFUSES: a ladder render exists; part 1 is hashed before any")
            return 2
        digest = sha(PARTS["protocol"]["declaration"].read_bytes())
        with PARTS["protocol"]["digest"].open("x") as f:
            f.write(f"{digest}  declaration.json\n")
        print(f"declaration.json sha256 {digest}; commit it with declaration.sha256 before any ladder render")
        return 0
    if verb in ("check-fit", "hash-fit"):
        c, fit = check_fit()
        print("W45 G0 part 2: the fit declaration as a validated diff against the draft")
        rc = report(c, [], "check-fit")
        if verb == "check-fit" or rc:
            return rc
        if PARTS["fit"]["digest"].exists():
            print("hash-fit REFUSES: part 2 is hashed already")
            return 2
        if fit_evidence():
            print("hash-fit REFUSES: a fit render exists; part 2 is hashed before any")
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
