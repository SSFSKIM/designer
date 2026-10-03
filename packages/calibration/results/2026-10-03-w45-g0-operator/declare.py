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


def part_one_record() -> tuple[dict, dict]:
    """(partOnePins, partOneReadAt) as part 2's amendment records them."""
    pins, read_at = {}, {}
    for a in amendments("fit"):
        pins.update(a.get("partOnePins") or {})
        read_at.update(a.get("partOneReadAt") or {})
    return pins, read_at


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
    for key, want in (fit.get("sources") or {}).items():
        try:
            c.eq(f"pin {key}", sha(source_bytes(key)), want)
        except (OSError, subprocess.CalledProcessError) as err:
            c.failures.append(f"pin {key}: unreadable ({err})")
    c.true("fit: ladders/results.json is not one of part 2's pinned sources",
           f"{REL}/ladders/results.json" in (fit.get("sources") or {}))
    try:
        validate_fit(json.loads(DRAFT.read_text()), fit, json.loads(RESULTS.read_text()),
                     json.loads(PROTOCOL.read_text()))
    except Refusal as err:
        c.failures.append(f"fit: {err}")
    return c, fit


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
        return amend("fit", argv[2:])
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
