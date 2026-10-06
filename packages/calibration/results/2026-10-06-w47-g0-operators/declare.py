"""W47 G0 (g): the two hashed parts of the declaration (charter `2026-10-06-w47-span-graded-dark-
transmission.md`, Parent-Level Acceptance clause 2; G0 (g); Decision Log 5). W46 G0's `declare.py`
(`results/2026-10-05-w46-g0-declaration/declare.py`), ported by copy and re-bound to W47; W46's, W45's
and W44's committed copies are untouched and are never run by W47.

    python3.12 -B declare.py check | hash
    python3.12 -B declare.py amend --reason TEXT --cause COMMIT [--ruling "Decision Log N"
        --charter-commit C --ops OPS.json] PIN [PIN ...]
    python3.12 -B declare.py check-fit | hash-fit
    python3.12 -B declare.py amend-fit --reason TEXT --cause COMMIT [--ruling "Decision Log N"
        --charter-commit C --ops OPS.json] [--part-one SRC ...] PIN [PIN ...]

**What W47 changes, and nothing else:**
- **Bindings.** `bindings.py` is W47's: the charter pin `c1f9bf84c`, this evidence root, W47's scratch,
  part files and schemas (`w47-*`). A declaration naming W44's, W45's or W46's charter or schema, a
  digest file carrying any of their eleven part hashes, and a ladder or fit path in their evidence or
  scratch are refused before anything is checked.
- **Part 1's items are clause 2's list.** `documents` (X62 at the charter's merge); `t1` (T1 as GATED on
  the dark 0.25 profiles since W46 G2: the owner test's `T1_DARK_*` block); `bar`; `manifest` (W46's
  `w46-referees-1` loaded BY HASH through W47's X69 loader, its derivation pinned against W46's frozen
  ladder list only, W47's membership and disjointness checks — never re-derived from W47's ladders);
  `rule` (W46's binding verbatim, and its rehearsal record: `d0219cd684bf` against itself and W46's
  point A by its committed gate cut); `tools`; `level`; `operators` (the two operators' laws,
  identities, grids, units and X68 domains, against `bindings.DOMAINS` and the landed runtime);
  `diagnostic` (G0 (f): the depth-split diagnostic's committed record and its chosen form, the
  criterion recomputed); `targets` (the three targets' families from the draft, their predictions
  from the orchestrator's inputs); `ladders` (protocol, cells, permitted decisions; X69 and X70);
  `startingPoint`; `references`; `s1` (the predicted direction); `draft`. The values the parent
  supplies (the predictions, S1's direction, the diagnostic's chosen form) come through
  `declaration-inputs.json`, which `assemble.py` refuses to read while a `TO FILL` remains.
- **Part 2's decisions are clause 5's, in the protocol's words** (`ladders/protocol.json` `decisions`,
  each ladder's `decides`). The CHANGES: `name-unfitted` (an operator whose ladder shows no separation
  is NOT fitted: its leaves leave the body and it is named in `notFitted` with its ladder and its
  reading, X63); `body-width-first` (a receded `optics.regular.blurSigma` rung of ladder (iii) met the bar
  on its own: the tap is named unfitted, its leaves leave, the body width is fitted; Decision Log 3);
  `name-target` (W46's, X63); `name-1x-gap` (ladder (ii) met its bar: the 1x per-span width is named in
  `namedGaps` with its shape; Decision Log 2's declined item; nothing is added); `strike` (a leaf whose
  protocol rungs read flat, or a stage-1 leaf `conditional` on ladder (ii) when ladder (ii) did not meet
  its bar: Design "The moves"); `narrow` (the active transmission to the shipped value and the ladder
  (i) base rungs at which L1 passes). The OUTCOMES, which change nothing: `fit` and `stop`. A draft
  leaf names its `ladder` and the protocol `rungs` that move it; the results are `ladders/read.py`'s
  (`operators`, `ladders`, `rungs`). The REQUIRED outcomes add: every operator the ladders read as not
  separating named and none of its leaves retained, the body width first where it met the bar, the 1x
  gap named exactly when ladder (ii) met its bar, a separation at one scale only ruled by the parent
  first, and no part 2 at all when neither operator separates (the wave closes at G0 with the finding).
- **Every leaf is X67's and X68's.** A draft or protocol leaf is one its dark slot's snapshot names or
  `bindings.ADMITTED` admits (X64 ∪ X67), and every grid value and every numeric rung is inside
  `bindings.DOMAINS` where X68 declares one.
- **The content amendment, kept in W46 Decision Log 9's form and made general.** W46's record carried
  one ruling's text and recomputed its ops from a ruling-specific function. W47's record carries the
  same fields — `ruling`, `charter`, `ops` (each an `add` or a `replace` at one body path with its
  `from` and `to`), and on part 2 `partOnePins` — and validates them on READ against what does not
  depend on the ruling: `ruling` must be, verbatim, the `### Decision Log N` section of the charter at
  the commit `charter` names; the ops must revert the current body to the bytes of the hash it
  supersedes (the chain); no op may touch `schema`, `charter`, `sources`, `changes` or `fromDraft`.
  Part 2's ladders' validated diff and its required outcomes are read on the REVERTED body (the hashed
  part 2 the ruling amends), as W46's were. Either part may carry the content form (Design "If the
  user lifts X41" amends part 1 once); each part is amended at most once, finally, and a further
  `amend` / `amend-fit` refuses.
- **Part 1's one amendment after the ladders (W47 Decision Log 8).** `amend` refused part 1 once any ladder
  render existed. The parent's Decision Log 8 spends part 1's one amendment after the ladders read, to
  re-state the bars beside the hashed ones, so part 1 now admits ONE post-render amendment in the content
  form only, and only ADDITIVE: every op is an `add`, so no hashed value of part 1 is replaced, and a
  ruling can sit beside what the ladders were read against but cannot rewrite it. The record names the
  render evidence it was made over (`renderEvidenceAtAmendment`), and the read-time validation refuses a
  record made over render evidence whose form is pins-only or whose ops replace anything. Part 2's
  `amend-fit` still refuses after any fit render.

W46 G0's text follows, unchanged; where it says W46 it is W47, where it names Decision Log 9's ruling
the record names W47's own ruling by heading.

W46 G0: the two hashed parts of the declaration (charter clause 1; G0 (e)). W45 G0's `declare.py`
(`results/2026-10-03-w45-g0-operator/declare.py`), ported and parameterised for W46; W45's and W44's
committed copies are untouched and are never run by W46.

Part 1 (`declaration.json`, with its readable twin `declaration.md`) and the part-2 DRAFT
(`fit-declaration-draft.json`, pinned as one of part 1's sources, so the one hash covers both), on the
ASSEMBLED tree and before any ladder render:

    python3.12 -B declare.py check     # exit 0 consistent (pending items reported), 1 on a mismatch
    python3.12 -B declare.py hash      # refuses (exit 2) while an item is pending, once hashed, or after a ladder render
    python3.12 -B declare.py amend --reason TEXT --cause COMMIT PIN [PIN ...]

Part 2 (`fit-declaration.json`), after the ladders and before any fit render:

    python3.12 -B declare.py check-fit # the validated diff against the draft
    python3.12 -B declare.py hash-fit  # refuses before part 1 is hashed, on any invalid change, once hashed
    python3.12 -B declare.py amend-fit --reason TEXT --cause COMMIT PIN [PIN ...]

**What W46 binds, and refuses.** The charter pin, the evidence root, the scratch and the part files are
`bindings.py`'s. A declaration naming W44's or W45's charter or schema, a digest file carrying their part
hashes, and a ladder or fit path in their directories or scratch are refused before anything is checked.

**What `check` re-derives**, item by item, from the files that define it (each pinned by SHA-256 in
`sources`; a path suffixed `@<commit>` is read at that commit): the four snapshots (X62); T1 as adopted,
its shared arithmetic and its tests, and its dark population; the bar; W46's referee manifest, its
adapter's lists and the fit-member counts; the rule, its synthetic cases and its rehearsal record (the
verdicts recomputed from the committed cuts, the gated groups the charter's); the tools and their red
cases, the cuts' port proof, the stage rehearsal and X60's evidence; the level check, its tests and its
rendered identity test; the targets, their families and the predictions file; the ladders' protocol (every
rung a one-leaf move the builder admits, inside its domain, on non-withheld cells); the starting point and
the references by hash; S1's prediction; and the draft (every leaf a dark slot's, admitted by X64 or named
by its snapshot, its grid inside its domain, its ladder a protocol lever, the landing rule `cuts/rule.py`).

**Part 2 is a validated diff** (W44's and W45's rule). `fit-declaration.json` is the draft's body plus a
`changes` list; `check-fit` applies each change only where the ladder results (`ladders/results.json`)
support it and the protocol lets the cited ladder make that decision, and the result must equal part 2's
body exactly. The decisions (`ladders/protocol.json`): `strike` (a leaf its lever read flat), `narrow` (a
grid to a subset inside the lever's non-flat range; for `tintAlpha`, the shipped value and the passing
rungs), `name-target` (a target with no lever, recorded in `notFitted` with the operator's shape, and
every draft leaf of that target removed: X63). The changes are also REQUIRED where the ladders require
them (`mandatory_failures`, read on the resulting body whatever `changes` lists): each tintAlpha grid
inside its passing rungs, no flat lever's leaf retained, every leverless target named, and no part 2
at all when no target has a lever.

**Amendments** (W43's and W44's rule): an amendment re-pins named moved sources and changes nothing
else, with ONE exception below; each part is amended at most once; `amend` refuses once ANY ladder render exists, `amend-fit` once
any fit render exists. **The amendment record is validated on READ** (W45's review closure, §5.205 §14
item 3): `check` and `check-fit` refuse a record entry with any field outside the pins-only form, a pin
outside the part's sources, or a chain that does not rebuild the superseded hash.

**Part 2's one amendment is Decision Log 9's, a CONTENT amendment** (W46 G1; the form W44 G1 step 0
and W45 G0 used). The parent ruled on G1's step-0 diagnosis: widen the receded `tintAlpha` grid to
{0.8, 0.89} and have stage 2 report two points, A with no exception and B with
`impulse__capsule-button__inactive`'s L1 miss named. Its record carries, beside the pins:
- `ruling`, the charter's Decision Log 9 verbatim, and `charter`, the charter at the commit that
  records it.
- `ops`, the content diff, each an `add` or a `replace` at one path of part 2's body with its `from`
  and `to`. `check-fit` recomputes them from the body with the ops reverted (`ruling_nine_ops`) and
  requires the recorded ones equal, values included. The ladders' validated diff and their required
  outcomes are read on that reverted body, which is the hashed part 2 the ruling amends.
- `partOnePins`, moves of the part-1 sources the amendment's tools changed. Part 1 cannot be amended
  once a ladder renders, so, as in W45, part 1's check accepts a moved pin only for
  `PART_ONE_REPINNABLE`, only along the move this record names, and only at the bytes the AMENDED
  part 2 pins in its own `sources` (each part-1 move is added there, inside part 2's hash chain, so
  `check-fit` re-hashes it). Part 1's declaration and hash do not move.
The ops re-add stage 2's receded scatter family, which the F inactive `name-target` change had
removed. Point A's clause, "any point where the receded scatter leaves ... dilute the dot enough for
L1 to pass at 0.8", is a search over those leaves. F inactive stays named not fitted, and the leaves
carry the ruling as their target. They add `points`, the two-point protocol `search.py` runs
(`stage_points`).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402

ROOT = W.ROOT
CAL = W.CAL
REL = HERE.relative_to(ROOT).as_posix()
WAVE = "w47"
PARTS = {
    "protocol": dict(declaration=W.PART1, twin=HERE / "declaration.md", digest=W.PART1_DIGEST,
                     amendments=HERE / "amendments.json", schema="w47-declaration-1"),
    "fit": dict(declaration=W.PART2, twin=None, digest=W.PART2_DIGEST, amendments=HERE / "fit-amendments.json",
                schema="w47-fit-declaration-1"),
}
DRAFT = W.DRAFT
INPUTS = HERE / "declaration-inputs.json"
PROTOCOL = W.LADDER_PROTOCOL
RESULTS = W.LADDERS / "results.json"
LADDER_RUNS = W.LADDERS / "runs.jsonl"
FIT_RUNS = W.G1_FIT / "runs.jsonl"
OTHER_SCHEMAS = ("w44-", "w45-", "w46-")
PLACEHOLDER = "TO FILL"
AMENDMENT_FIELDS = {"n", "supersedes", "declarationSha256", "reason", "cause", "pins", "renderEvidenceAtAmendment"}
# The content form (W46 Decision Log 9's, made general): the ruling verbatim, its charter, the content
# diff; part 2 adds the part-1 moves its tools made.
CONTENT_FIELDS = {"charter", "ruling", "ops"}
FIT_AMENDMENT_FIELDS = AMENDMENT_FIELDS | CONTENT_FIELDS | {"partOnePins"}
PROTOCOL_AMENDMENT_FIELDS = AMENDMENT_FIELDS | CONTENT_FIELDS
OPS_FORBIDDEN_ROOTS = ("schema", "charter", "sources", "changes", "fromDraft")
# The record of an amendment made after renders begins with this (Decision Log 8's form; see `amend`).
POST_RENDER_EVIDENCE = "after the ladders read, additive only: "
PART_ONE_REPINNABLE = tuple(f"{REL}/{p}" for p in (
    "declare.py", "test_declare.py", "test_declare.txt", "fit/fit.py", "fit/search.py", "fit/joint.py",
    "fit/test_fit.py", "fit/test_fit.txt", "seal/seal.ts", "seal/test_seal.py", "seal/test_seal.txt"))
CLAUSE_THREE = ("test_a_halving_every_target_with_three_cells_at_2b_passes", "test_b_four_cells_at_2b_fails",
                "test_c_one_cell_at_3_1b_fails", "test_d_a_gated_aggregate_worse_beyond_its_tolerance_fails",
                "test_e_every_cell_unchanged_is_neither", "test_f_a_group_of_two_gate_cells_is_reported_not_gated")
# Clause 5's decisions, as `ladders/protocol.json` names them: the CHANGES part 2 may list against the draft
# (each re-validated by `check-fit`), and the two OUTCOMES that change nothing (`fit`) or write no part 2
# (`stop`).
CHANGE_KINDS = ("name-unfitted", "name-target", "body-width-first", "narrow", "strike", "name-1x-gap")
OUTCOMES = ("fit", "stop")
DECISIONS = CHANGE_KINDS
OPERATORS = {"operator 1": W.OPERATOR_1, "operator 2": W.OPERATOR_2}
FORMS = ("body", "deep")
# Clause 1's evidence, pinned explicitly by part 1's `operators` item (the parent's ruling of 2026-10-06), not
# only through the tools glob: the two by-render recorder specs, the scene fixture they added scenes to (the
# W47 span quadruple and the fine-tap scenes in `e2e/fixtures/scenes.ts`), and each operator's proof records.
# Operator 2's records carry operator 1's names; part 1 refuses to assemble while any file is absent.
PROOF_RECORDS = ("compare.txt", "png-sha256.json", "digests.txt", "suites.txt", "identity.txt", "x60.txt",
                 "readers.txt")
CLAUSE1_EVIDENCE = (("packages/renderer-webgpu/e2e/gpu/w47-alpha-far.spec.ts",
                     "packages/renderer-webgpu/e2e/gpu/w47-fine-tap.spec.ts",
                     "packages/renderer-webgpu/e2e/fixtures/scenes.ts")
                    + tuple(f"{REL}/operator-{n}/{f}" for n in (1, 2) for f in PROOF_RECORDS))


def clause1_missing(paths=None) -> list[str]:
    """The clause-1 evidence files that are not on the tree."""
    return [p for p in (CLAUSE1_EVIDENCE if paths is None else paths) if not (ROOT / p).is_file()]

sha = lambda data: hashlib.sha256(data).hexdigest()  # noqa: E731


class Refusal(Exception):
    pass


def bindings() -> None:
    for path in (HERE, W.LADDER_SCRATCH, W.FIT_SCRATCH, W.G1, RESULTS, LADDER_RUNS, FIT_RUNS):
        try:
            W.refuse_other_wave_path(path, "declare.py")
        except W.Refusal as err:
            raise Refusal(str(err)) from None
    for part in PARTS.values():
        if part["declaration"].exists():
            text = part["declaration"].read_text()
            d = json.loads(text)
            if str(d.get("schema", "")).startswith(OTHER_SCHEMAS):
                raise Refusal(f"{part['declaration'].name} carries another wave's schema {d['schema']}")
            try:
                W.refuse_other_wave_text(text, part["declaration"].name)
            except W.Refusal as err:
                raise Refusal(str(err)) from None
        if part["digest"].exists():
            for ln in part["digest"].read_text().splitlines():
                if ln.strip() and ln.split()[0] in W.OTHER_PART_HASHES:
                    raise Refusal(f"{part['digest'].name} carries a W44, W45 or W46 part hash {ln.split()[0][:12]}")


def git_show(path: str, commit: str) -> bytes:
    return W.git_show(path, commit)


def source_bytes(key: str) -> bytes:
    if "@" in key:
        path, commit = key.rsplit("@", 1)
        return git_show(path, commit)
    return (ROOT / key).read_bytes()


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


def ev(rel: str) -> Path:
    return HERE / rel


def cuts():
    """(bed, t1, rule, referees): W47's cuts, and W47's X69 loader in the planner's place."""
    B, T1, RULE = W.load_cuts()
    return B, T1, RULE, W.referees()


def placeholders(node, path="") -> list[str]:
    """Every path in `node` still holding the `TO FILL` placeholder (assemble refuses while any does)."""
    if isinstance(node, str):
        return [path or "/"] if PLACEHOLDER in node else []
    if isinstance(node, dict):
        return [p for k, v in node.items() for p in placeholders(v, f"{path}/{k}")]
    if isinstance(node, list):
        return [p for i, v in enumerate(node) for p in placeholders(v, f"{path}/{i}")]
    return []


def decision_log(charter: str, heading: str) -> str:
    """The `### <heading> …` section of `charter` (text), verbatim, to the next heading of level 1–3."""
    m = re.search(rf"^### {re.escape(heading)}\b.*?(?=^#{{1,3}} |\Z)", charter, flags=re.M | re.S)
    if m is None:
        raise Refusal(f"the charter records no `### {heading}`")
    return m.group(0).rstrip() + "\n"


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


def check_documents(c, it):
    d = it["declared"]
    c.eq("documents: the snapshots verify (X62)", W.verify_documents(), [])
    c.eq("documents: the slots", {s: W.DOCUMENT_SHA[s][:12] for s in W.SLOTS}, d["files"])
    c.eq("documents: the digests", W.DOCUMENT_DIGEST, d["digests"])
    c.eq("documents: snapshot commit", W.SNAPSHOT_COMMIT, d["commit"])


def check_t1(c, it):
    B, T1, _, R = cuts()
    d = it["declared"]
    held = R.referee_cells(R.load_manifest())
    for p in W.DARK_025:
        pop = T1.population([p])
        got = dict(cells=len(pop))
        for s in ("F", "T", "C", "P"):
            got[s] = sum(1 for _, sid in pop if T1.stratum(sid) == s)
        for part in ("gate", "holdout", "referee"):
            got[part] = sum(1 for _, sid in pop if T1.partition(p, sid, held) == part)
        c.eq(f"t1: population of {p}", got, d["populationPerDarkProfile"])
    c.eq("t1: strata", {k: list(v) for k, v in T1.STRATA.items()}, d["strata"])
    c.eq("t1: ratio clause", T1.RATIO_CLAUSE, d["ratioClause"])
    c.eq("t1: g = 0 tolerance", T1.EQUAL, d["equalTolerance"])
    owner = source_bytes(d["ownerTest"]).decode()
    for needle in d["ownerNeedles"]:
        c.true(f"t1: the owner test does not carry {needle!r}", needle in owner)
    rc, out = run("-m", "unittest", "test_t1", cwd=W.W44_G1 / "cuts")
    c.true(f"t1: W44 G1's test_t1 does not pass ({last_line(out) or rc})", rc == 0)


def check_bar(c, it):
    d = it["declared"]
    bar = json.loads(W.BAR_PATH.read_text())
    dark = [x for x in bar["table"] if x["profile"] in W.DARK_025]
    c.eq("bar: dark cells", len(dark), d["darkCells"])
    c.true("bar: a dark cell's bar is not half its code", all(abs(x["bar"] - 0.5 * x["code"]) < 1e-15 for x in dark))
    c.eq("bar: largest separation", bar["maxSeparation"], d["maxSeparation"])


def check_manifest(c, it):
    """X69: loaded by hash, never re-derived from W47's ladders; the derivation pinned against W46's frozen
    ladder list only; membership and disjointness (the loader's own checks); the whitelists."""
    R = W.referees()
    d = it["declared"]
    m = R.load_manifest()
    lists = R.lists(m)
    c.eq("manifest: schema", json.loads(Path(m["path"]).read_text())["schema"], d["schema"])
    c.eq("manifest: scenes", m["scenes"], d["scenes"])
    c.eq("manifest: profiles", m["profiles"], d["profiles"])
    c.eq("manifest: sha256", m["sha256"], d["sha256"])
    c.eq("manifest: the path is W46's (X69)", Path(m["path"]).resolve(), W.W46_REFEREES.resolve())
    c.eq("manifest: W46's adapter reproduces it from W46's frozen ladder list", R.pin_derivation()["scenes"],
         d["scenes"])
    for name in ("pregateProbe", "exposure"):
        got = lists[name]
        c.eq(f"manifest: {name} count", got["count"], d[name]["count"])
        c.eq(f"manifest: {name} list", sha(",".join(got["scenes"]).encode()), d[name]["listSha256"])


def check_rule(c, it):
    _, _, rule, _ = cuts()
    d = it["declared"]
    c.eq("rule: constants", dict(budgetCount=rule.BUDGET_COUNT, budgetCeilingB=rule.BUDGET_CEILING_B,
                                 gatingMinCells=rule.GATING_MIN_CELLS), d["constants"])
    c.eq("rule: targets", {t: [f"{s} {p}" for s, p in g] for t, g in rule.TARGETS.items()}, d["targets"])
    c.eq("rule: reference", rule.REFERENCE, d["reference"])
    rc, out = run("-m", "unittest", "-v", "test_rule", cwd=W.CUTS)
    c.true(f"rule: test_rule does not pass ({last_line(out) or rc})", rc == 0)
    c.true(f"rule: test_rule runs fewer than {d['syntheticCases']} cases", ran_at_least(out, d["syntheticCases"]))
    for name in CLAUSE_THREE:
        c.true(f"rule: the case {name} does not run and pass", re.search(rf"^{name} .* ok$", out, re.M) is not None)
    reh = json.loads(ev("rehearsal/rehearsal.json").read_text())
    c.eq("rule: the rehearsal's rule file is rule.py", reh["rule"]["sha256"], sha(ev("cuts/rule.py").read_bytes()))
    got = {}
    for x in reh["rows"]:
        src = ROOT / x["source"]
        c.eq(f"rule: {x['label']} source", sha(src.read_bytes()), x["sourceSha256"])
        t = json.loads(gzip.open(src).read())["T1"]
        r = rule.evaluate(t["cells"], t["missing"])
        c.eq(f"rule: {x['label']} verdict recomputed", r["verdict"], x["verdict"])
        got[x["label"]] = [r["verdict"]] + [
            [p["partition"]["unchanged"]["total"], len(p["awayBeyondB"]), len(p["awayBeyondCeiling"])]
            for p in r["profiles"].values()]
    c.eq("rule: the rehearsal's verdicts", got, d["rehearsal"])
    c.true("rule: the gated and reported groups are not the charter's",
           all(g["equal"] for g in reh["groupsAgainstCharter"].values()))


def check_tools(c, it):
    d = it["declared"]
    for test, cwd, count in d["tests"]:
        rc, out = run("-m", "unittest", test, cwd=HERE / cwd)
        c.true(f"tools: {cwd}/{test} does not pass ({last_line(out) or rc})", rc == 0)
        c.true(f"tools: {cwd}/{test} runs fewer than {count} cases", ran_at_least(out, count))
    rc, out = run(ev("rehearsal/port-proof.py"))
    c.true(f"tools: the cuts port does not reproduce its reference cut ({last_line(out) or rc})", rc == 0)
    reh = json.loads(ev("stage/rehearsal/rehearsal.json").read_text())
    c.eq("tools: the stage rehearsal", (reh["verdict"], reh["rows"], reh["capturesIdentical"]),
         tuple(d["stageRehearsal"]))
    x60 = json.loads(ev("stage/x60/evidence-g0.json").read_text())
    c.eq("tools: X60 by evidence", x60["verdict"], "IDENTICAL")


def check_level(c, it):
    d = it["declared"]
    ident = json.loads(ev("level/identity/identity.json").read_text())
    c.eq("level: the shipped rung's identity", (ident["verdict"], ident["cells"], ident["pixelAndMeasurementIdentical"],
                                                ident["readsNoChange"]), tuple(d["identity"]))
    c.eq("level: the projection", ident["projection"], d["projection"])


def domains_json(parts) -> list:
    return [list(p[:1]) + ([list(p[1])] if p[0] == "set" else list(p[1:])) for p in parts]


def identity_table(material: str) -> str:
    m = re.search(r"export const MATERIAL_IDENTITY_TABLE\b.*?\n\];", material, flags=re.S)
    return m.group(0) if m else ""


def check_operators(c, it):
    """The two operators as part 1 states them (charter Design "Operator 1", "Operator 2"; X65, X66, X68):
    their leaves are the bindings', their X68 domains `bindings.DOMAINS`' on every slot that names them,
    every leaf's default in `DEFAULT_MATERIAL_PROFILE` is its identity 0, every leaf is an entry of
    `MATERIAL_IDENTITY_TABLE` (operator 1 two plain value drops; operator 2 one gate-group whose gate is
    the share), and the two W31 tests name them."""
    d = it["declared"]
    material = (ROOT / "packages/renderer-webgpu/src/material.ts").read_text()
    table = identity_table(material)
    c.true("operators: material.ts has no MATERIAL_IDENTITY_TABLE", bool(table))
    identity_test = (ROOT / "packages/calibration/test/w31-identity-table.test.ts").read_text()
    gate_test = (ROOT / "packages/renderer-webgpu/test/w31-gate-groups.test.ts").read_text()
    for name, leaves in OPERATORS.items():
        op = d[name]
        c.eq(f"operators: {name}'s leaves", op["leaves"], list(leaves))
        for leaf in leaves:
            c.true(f"operators: {leaf}'s default is not its identity 0", f"\n  {leaf}: 0,\n" in material)
            c.true(f"operators: {leaf} is not in MATERIAL_IDENTITY_TABLE", leaf in table)
            c.true(f"operators: w31-identity-table.test.ts does not name {leaf}", leaf in identity_test)
            for slot in W.MOVING_SLOTS:
                parts = W.DOMAINS[slot].get(leaf)
                if parts is not None:
                    c.eq(f"operators: {slot} {leaf}'s X68 domain", domains_json(parts), op["domains"][slot][leaf])
            for v in op["grid"].get(leaf, []):
                for slot in op["slots"]:
                    c.true(f"operators: {name} grid value {leaf}={v} outside X68 on {slot}", W.in_domain(slot, leaf, v))
        c.eq(f"operators: {name}'s slots", op["slots"], [s for s in W.MOVING_SLOTS
                                                         if all(k in W.ADMITTED[s] for k in leaves)])
    c.true("operators: operator 2's gate-group is not in the table (gate sizeFineTapShare: 0)",
           re.search(r"gate:\s*\{\s*sizeFineTapShare:\s*0\s*\}", table) is not None)
    c.true("operators: w31-gate-groups.test.ts does not sweep operator 2's gated widths",
           "sizeFineTapSigma" in gate_test)
    c.true("operators: X66 — the active admits an operator-2 leaf",
           not set(W.OPERATOR_2) & set(W.ADMITTED["active.dark"]))
    evidence = d.get("clause1Evidence") or {}
    c.eq("operators: clause 1's evidence pinned (the recorder specs, their scene fixture, both operators' "
         "proof records)", sorted(evidence), sorted(CLAUSE1_EVIDENCE))
    for path in clause1_missing():
        c.failures.append(f"operators: clause 1's evidence {path} is absent")
    for path, want in evidence.items():
        if (ROOT / path).is_file():
            c.eq(f"operators: {path} is the pinned bytes", sha((ROOT / path).read_bytes()), want)


def diagnostic_choice(cells: list[dict]) -> str:
    """Design "The ladders", the depth-split diagnostic's criterion: a form is chosen when it removes at
    least half of `E` on every cell and scale AND more of it than the other on the pooled mean; neither
    form, or a split by scale, is "parent" (operator 2 lands in no form until ruled)."""
    mean = {f: statistics.mean(x["R"][f] for x in cells) for f in FORMS}
    chosen = [f for f in FORMS
              if all(x["R"][f] >= 0.5 for x in cells) and mean[f] > mean[FORMS[1 - FORMS.index(f)]]]
    return chosen[0] if len(chosen) == 1 else "parent"


def check_diagnostic(c, it):
    d = it["declared"]
    rec = json.loads((ROOT / d["record"]).read_text())
    c.true(f"diagnostic: chosen form {d['chosenForm']!r} is neither {FORMS}", d["chosenForm"] in FORMS)
    c.eq("diagnostic: the record's chosen form", rec.get("chosenForm"), d["chosenForm"])
    cells = rec.get("cells") or []
    keys = sorted((x["cell"], x["scale"]) for x in cells)
    c.eq("diagnostic: its population (cell, scale)", keys, sorted(tuple(k) for k in d["population"]))
    if cells:
        c.eq("diagnostic: the criterion recomputed from R", diagnostic_choice(cells), d["chosenForm"])
    held = set(W.referees().load_manifest()["scenes"])
    c.true("diagnostic: a referee was rendered", not {x["cell"] for x in cells} & held)


def check_inputs_block(c, it, key):
    """An item whose reading the parent supplied (`declaration-inputs.json`, pinned): declared as given."""
    inputs = json.loads(INPUTS.read_text())
    c.true(f"{key}: {INPUTS.name} still holds a {PLACEHOLDER}", not placeholders(inputs[key]))
    c.eq(f"{key}: the declared reading is the inputs file's", it["declared"]["given"], inputs[key])


def check_targets(c, it):
    d = it["declared"]
    check_inputs_block(c, it, "targets")
    draft = json.loads(DRAFT.read_text())
    fam = {}
    for m in draft["moves"]:
        for f in m["families"].values():
            for key, spec in f["leaves"].items():
                fam.setdefault(spec["target"], []).append(f"{spec['slot']} {key}")
    c.eq("targets: the families (the draft's leaves by target)", {k: sorted(v) for k, v in fam.items()},
         {k: sorted(v) for k, v in d["families"].items()})


def check_s1(c, it):
    check_inputs_block(c, it, "s1")


def admitted_leaf(slot: str, leaf: str) -> bool:
    """A leaf a dark slot may move: one its snapshot names (a nested path included) or an X64 ∪ X67 key
    (`bindings.ADMITTED`, which carries the nested `optics.regular.blurSigma` on the receded only)."""
    if leaf in W.ADMITTED.get(slot, {}):
        return True
    node = W.document(slot)["patch"]
    for part in leaf.split("."):
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def protocol_rungs(lad: dict) -> list[dict]:
    """A ladder's rungs as (id, lever, ladder, overrides {slot: {leaf: value}}). W47's protocol lists
    each rung explicitly (`rungs[]`, each with its `label`): a rung may move several leaves (ladder (i)'s
    base and far delta, ladder (ii)'s share, width and far share), and its lever is the rung itself. W46's
    one-leaf form (`arms`/`levers`, each `values` with its `slot` and `leaf`) is still read. A value that
    depends on an earlier ladder's reading is `{"select": NAME}` (`ladder.py`), checked when it is
    resolved, never fixed here."""
    out = []
    for lev in lad.get("arms", []) + lad.get("levers", []):
        if "rungs" in lev:
            out += [dict(id=r["id"], lever=lev["id"], ladder=lad["id"], overrides=r["overrides"]) for r in lev["rungs"]]
        else:
            out += [dict(id=f"{lev['id']}-{v}", lever=lev["id"], ladder=lad["id"], overrides={lev["slot"]: {lev["leaf"]: v}},
                         domain=lev.get("domain"), shipped=lev.get("shipped"))
                    for v in lev["values"]]
    for r in lad.get("rungs", []):
        rid = r.get("label", r.get("id"))
        out.append(dict(id=rid, lever=r.get("lever", rid), ladder=lad["id"], overrides=r["overrides"]))
    return out


def lever_ids(protocol: dict) -> list[str]:
    """Every lever the protocol declares, in order: W47's rungs are their own levers (their labels)."""
    return list(dict.fromkeys(r["lever"] for lad in protocol["ladders"] for r in protocol_rungs(lad)))


def rung_leaves(protocol: dict) -> dict[str, set]:
    """rung label -> {(leaf, slot)} it moves (a `{"select": ...}` value moves its leaf too)."""
    return {r["id"]: {(leaf, slot) for slot, leaves in r["overrides"].items() for leaf in leaves}
            for lad in protocol["ladders"] for r in protocol_rungs(lad)}


def check_ladders(c, it):
    B, T1, _, R = cuts()
    d = it["declared"]
    p = json.loads(PROTOCOL.read_text())
    c.eq("ladders: the protocol pins cells.json", p["cells"]["sha256"], sha(W.LADDER_CELLS.read_bytes()))
    c.eq("ladders: the protocol's decisions are clause 5's", sorted(p.get("decisions", {})),
         sorted(CHANGE_KINDS + OUTCOMES))
    c.eq("ladders: the protocol's change kinds", (p.get("decisionKinds") or {}).get("changes"), list(CHANGE_KINDS))
    c.eq("ladders: the protocol's outcomes", (p.get("decisionKinds") or {}).get("outcomes"), list(OUTCOMES))
    cells = json.loads(W.LADDER_CELLS.read_text())
    union = set(cells["union"])
    try:
        R.check_disjoint(R.load_manifest(), R.load_ladder_cells())
    except W.Refusal as err:
        c.failures.append(f"ladders: X69 disjointness: {err}")
    for sid in union:
        c.true(f"ladders: {sid} is a holdout scene", B.SCENES.role[sid] != "holdout")
        for prof in W.DARK_025:
            c.true(f"ladders: {prof} does not declare {sid} (X70)", sid in B.SCENES.declared(prof))
        c.true(f"ladders: {sid} is in no set the ladders render", B.SCENES.role[sid] in p["sets"].split(","))
    c.eq("ladders: the protocol's ladders are cells.json's", [lad["id"] for lad in p["ladders"]], list(cells["ladders"]))
    rungs = 1
    for lad in p["ladders"]:
        for r in protocol_rungs(lad):
            rungs += 1
            for slot, leaves in r["overrides"].items():
                for leaf, v in leaves.items():
                    c.true(f"ladders: {r['id']} {slot} {leaf} is not a leaf the builder admits (X64, X67)",
                           slot in W.MOVING_SLOTS and admitted_leaf(slot, leaf))
                    if isinstance(v, dict):
                        c.true(f"ladders: {r['id']} {leaf} is neither a value nor a declared selection",
                               bool(v.get("select") or v.get("dependsOn")))
                        continue
                    c.true(f"ladders: {r['id']} {slot} {leaf}={v} outside its X68 domain", W.in_domain(slot, leaf, v))
                    if r.get("domain"):
                        lo, hi = r["domain"]
                        c.true(f"ladders: {r['id']} value outside {r['domain']}", lo <= v <= hi)
                    if r.get("shipped") is not None:
                        c.true(f"ladders: {r['id']} repeats its shipped value", v != r["shipped"])
        c.true(f"ladders: {lad['id']} decides outside the protocol's change kinds",
               set(lad.get("decides", ())) <= set(CHANGE_KINDS))
    c.eq("ladders: rungs (the control included)", rungs, d["rungs"])
    c.eq("ladders: lever ids", lever_ids(p), d["levers"])
    c.eq("ladders: cells per ladder", {k: [len(v["rest"]), len(v["inactive"])] for k, v in cells["ladders"].items()},
         d["cellsPerLadder"])


def check_starting_point(c, it):
    d = it["declared"]
    index = json.loads((CAL / "results/generations/index.json").read_text())
    entry = index["files"][f"{d['generation']}.json"]
    c.eq("startingPoint: the generation file", entry["sha256"][:12], d["generationFileSha12"])
    c.eq("startingPoint: the documents it names", {x["path"].split("/")[-1]: x["sha256"] for x in entry["documents"]},
         d["documents"])
    c.eq("startingPoint: the snapshots' digests", {s: W.DOCUMENT_DIGEST[s] for s in W.MOVING_SLOTS}, d["digests"])


def check_references(c, it):
    index = json.loads((CAL / "results/generations/index.json").read_text())
    for name, want in it["declared"]["files"].items():
        f = index["files"].get(f"{name}.json")
        c.true(f"references: no generation {name}", f is not None)
        if f:
            c.eq(f"references: {name} index sha256", f["sha256"], want)
            c.eq(f"references: {name} file sha256", sha((CAL / "results/generations" / f"{name}.json").read_bytes()), want)


def draft_failures(draft: dict, protocol: dict, targets) -> list[str]:
    """The draft's shape (clause 2; Design "The moves"): every searched leaf a dark slot's, admitted by
    X64 ∪ X67 or named by its snapshot, its grid sorted, distinct and inside both its declared domain and
    its X68 domain, a unit and one of the rule's targets; its `ladder` one of the protocol's ladders (or
    none: a leaf no W47 ladder reads), and its `rungs` the protocol rungs that move it in its slot, at
    least one on its ladder; `conditional` only on ladder (ii) (Design "The moves": the second tap is
    crossed into stage 1 only where ladder (ii) meets its bar); a family's `fixed` values admitted and
    inside X68; every factorial group of keys the family searches."""
    out = []
    ladders = {lad["id"] for lad in protocol["ladders"]}
    by_rung = rung_leaves(protocol)
    rung_ladder = {r["id"]: lad["id"] for lad in protocol["ladders"] for r in protocol_rungs(lad)}
    for m in draft["moves"]:
        if m.get("materialise") is not None and m["materialise"] not in W.MOVING_SLOTS:
            out.append(f"draft: {m['id']} materialises {m['materialise']!r}, not a dark slot (X67)")
        for fam, body in m["families"].items():
            for key, spec in body["leaves"].items():
                sid = f"{m['id']}/{fam}/{key}"
                if spec["slot"] not in W.MOVING_SLOTS:
                    out.append(f"draft: {sid} is in a slot that does not move")
                    continue
                if not admitted_leaf(spec["slot"], key):
                    out.append(f"draft: {sid} is not a leaf its slot may name (X64, X67)")
                grid, dom = spec["grid"], spec["domain"]
                if grid != sorted(set(grid)):
                    out.append(f"draft: {sid} grid not sorted and distinct")
                if not all(dom[0] <= x <= dom[1] for x in grid):
                    out.append(f"draft: {sid} grid {grid} outside {dom}")
                if not all(W.in_domain(spec["slot"], key, x) for x in grid):
                    out.append(f"draft: {sid} grid {grid} outside its X68 domain")
                if not (spec.get("unit") and spec.get("target") in targets):
                    out.append(f"draft: {sid} has no unit or target")
                lad, rungs = spec.get("ladder"), spec.get("rungs", [])
                if lad is not None and lad not in ladders:
                    out.append(f"draft: {sid} names a ladder the protocol does not declare ({lad})")
                for r in rungs:
                    if (key, spec["slot"]) not in by_rung.get(r, set()):
                        out.append(f"draft: {sid} cites rung {r}, which does not move it in {spec['slot']}")
                if lad is not None and not any(rung_ladder.get(r) == lad for r in rungs):
                    out.append(f"draft: {sid} names ladder ({lad}) and none of its rungs")
                if spec.get("conditional") not in (None, "ii"):
                    out.append(f"draft: {sid} is conditional on {spec['conditional']!r}; only ladder (ii) gates a leaf")
                if spec.get("operator") is not None and key not in OPERATORS.get(spec["operator"], ()):
                    out.append(f"draft: {sid} is tagged {spec['operator']} and is not one of its leaves")
            for leaf, fx in body.get("fixed", {}).items():
                if fx["slot"] not in W.MOVING_SLOTS or not admitted_leaf(fx["slot"], leaf):
                    out.append(f"draft: {m['id']}/{fam} fixes {fx['slot']} {leaf}, not a leaf it may name")
                elif not W.in_domain(fx["slot"], leaf, fx["value"]):
                    out.append(f"draft: {m['id']}/{fam} fixes {leaf}={fx['value']} outside its X68 domain")
            for g in body.get("factorialGroups", []):
                if not set(g["keys"]) <= set(body["leaves"]):
                    out.append(f"draft: {m['id']}/{fam} factorial group names a leaf it does not search")
    # W46's `materialiseX64` check, generalised to X64 ∪ X67 (the parent's ruling on W47 G0's reading 10):
    # stage 2 is the receded document's, sealed as a difference over the stage-1 active (Design "The
    # moves"), so it starts from a base that states every admitted receded key (X64 and X67) at its
    # inherited value (`materialise: receded.dark`, `fit.materialise`), and stage 1 materialises nothing.
    stages = {m["id"]: m for m in draft["moves"]}
    if set(stages) != {"stage1", "stage2"}:
        out.append(f"draft: the moves are {sorted(stages)}, not stage1 and stage2")
    else:
        if stages["stage2"].get("materialise") != "receded.dark" or stages["stage2"].get("materialiseX64") is not None:
            out.append("draft: stage 2 does not materialise the receded X64 ∪ X67 keys (materialise: receded.dark)")
        if stages["stage1"].get("materialise") is not None or stages["stage1"].get("materialiseX64") is not None:
            out.append("draft: stage 1 materialises a slot; only stage 2's base is materialised")
        # Design "The moves" (MARKED): stage 1's span law is ONE factorial, crossed WITH the 2x second
        # tap where ladder (ii) met its bar, so every ladder-(ii)-conditional leaf is a member of the
        # factorial group that holds the span law's knots, never a family swept after it.
        knots = {"optics.regular.tintAlpha", "tintAlphaFar1x", "tintAlphaFar2x", "sizeOcclusionGain",
                 "sizeScatterSpanMax", "sizeScatterSpanMax2x"}
        crossed = [set(g["keys"]) for fb in stages["stage1"]["families"].values()
                   for g in fb.get("factorialGroups", []) if knots & set(g["keys"])]
        for fam, fb in stages["stage1"]["families"].items():
            for key, spec in fb["leaves"].items():
                if spec.get("conditional") == "ii" and not any(key in g for g in crossed):
                    out.append(f"draft: stage1/{fam}/{key} is conditional on ladder (ii) and not crossed into "
                               "the span law's factorial (Design \"The moves\")")
    if draft.get("notFitted") != []:
        out.append("draft: a target or operator is named not fitted before the ladders")
    if draft.get("namedGaps", []) != []:
        out.append("draft: a gap is named before the ladders")
    return out


def check_draft(c, it):
    d = it["declared"]
    draft = json.loads(DRAFT.read_text())
    protocol = json.loads(PROTOCOL.read_text())
    c.eq("draft: schema", draft["schema"], PARTS["fit"]["schema"])
    c.eq("draft: stages", [m["id"] for m in draft["moves"]], d["stages"])
    c.eq("draft: references", {k: draft["references"][k] for k in ("dark", "light")}, W.REFERENCE)
    c.eq("draft: the landing rule's implementation", draft["landingRule"]["implementation"], "cuts/rule.py (pinned by part 1)")
    c.failures += draft_failures(draft, protocol, d["targets"])
    count = sum(len(f["leaves"]) for m in draft["moves"] for f in m["families"].values())
    c.eq("draft: searched leaves", count, d["searchedLeaves"])


CHECKS = {"documents": check_documents, "t1": check_t1, "bar": check_bar, "manifest": check_manifest,
          "rule": check_rule, "tools": check_tools, "level": check_level, "operators": check_operators,
          "diagnostic": check_diagnostic, "targets": check_targets, "ladders": check_ladders,
          "startingPoint": check_starting_point, "references": check_references, "s1": check_s1,
          "draft": check_draft}


def serialise(d):
    return (json.dumps(d, indent=2, ensure_ascii=False) + "\n").encode()


def digest_lines(part):
    path = PARTS[part]["digest"]
    return [ln.split()[0] for ln in path.read_text().splitlines() if ln.strip()] if path.exists() else []


def amendments(part):
    path = PARTS[part]["amendments"]
    return json.loads(path.read_text())["amendments"] if path.exists() else []


def content_failures(name: str, i: int, a: dict) -> list[str]:
    """The content form validated on READ (W46 Decision Log 9's form, general): the ruling is, verbatim,
    the charter's `### Decision Log N` section at the commit the record names; each op an add or a
    replace at a body path outside the declaration's frame. That the ops are exactly the amendment's
    diff is the chain's (they must revert the body to the hash the amendment supersedes)."""
    out = []
    if not (a.get("ruling") and a.get("charter") and isinstance(a.get("ops"), list)):
        return [f"{name}: amendment {i} carries content without its ruling, charter and ops"]
    if not str(a["charter"]).startswith(f"{W.CHARTER_PATH}@"):
        out.append(f"{name}: amendment {i} names a charter other than W47's ({a['charter']})")
    else:
        heading = a["ruling"].splitlines()[0].removeprefix("### ").split(" —")[0].strip()
        try:
            want = decision_log(git_show(*a["charter"].rsplit("@", 1)).decode(), heading)
        except (Refusal, subprocess.CalledProcessError) as err:
            want = None
            out.append(f"{name}: amendment {i}: the ruling's charter is unreadable or lacks it ({err})")
        if want is not None and a["ruling"] != want:
            out.append(f"{name}: amendment {i}'s ruling is not, verbatim, the charter's `{heading}` at "
                       f"{a['charter'].rsplit('@', 1)[1]}")
    for op in a["ops"]:
        if op.get("op") not in ("add", "replace") or not op.get("path"):
            out.append(f"{name}: amendment {i} op {op.get('op')!r} at {op.get('path')} is not an add or a replace")
        elif op["path"][0] in OPS_FORBIDDEN_ROOTS:
            out.append(f"{name}: amendment {i} op at {op['path']} touches the declaration's frame")
    return out


def amendment_failures(part, d) -> list[str]:
    """The record validated on READ: the pins-only form or the content form, at most one entry, pins of
    the part's sources; on part 2 the part-1 moves only of the re-pinnable sources, from part 1's pin."""
    out = []
    path = PARTS[part]["amendments"]
    if not path.exists():
        return out
    body = json.loads(path.read_text())
    if body.get("schema") != f"{WAVE}-{part}-amendments-1":
        out.append(f"{path.name}: schema {body.get('schema')!r}")
    record = body.get("amendments", [])
    if len(record) > 1:
        out.append(f"{path.name}: {len(record)} amendments; each part is amended at most once")
    allowed = FIT_AMENDMENT_FIELDS if part == "fit" else PROTOCOL_AMENDMENT_FIELDS
    for i, a in enumerate(record, 1):
        extra = sorted(set(a) - allowed)
        if extra:
            out.append(f"{path.name}: amendment {i} carries fields outside the pins-only and content forms: {extra}")
        for key, move in (a.get("pins") or {}).items():
            if key not in d["sources"] or "@" in key:
                out.append(f"{path.name}: amendment {i} re-pins {key}, not a working-tree source of the part")
            if set(move) != {"from", "to"}:
                out.append(f"{path.name}: amendment {i} pin {key} is not a from/to move")
        if set(a) & (CONTENT_FIELDS | {"partOnePins"}):
            out += content_failures(path.name, i, a)
        if str(a.get("renderEvidenceAtAmendment", "")).startswith(POST_RENDER_EVIDENCE):
            if part != "protocol" or not isinstance(a.get("ops"), list) or not a["ops"]:
                out.append(f"{path.name}: amendment {i} was made over render evidence and is not part 1's "
                           "content form (Decision Log 8)")
            elif any(op.get("op") != "add" for op in a["ops"]):
                out.append(f"{path.name}: amendment {i} was made over render evidence and replaces a hashed value; "
                           "only an add is admitted after the ladders (Decision Log 8)")
        if part == "fit" and a.get("partOnePins"):
            part1 = json.loads(PARTS["protocol"]["declaration"].read_text())["sources"]
            for key, move in a["partOnePins"].items():
                if key not in PART_ONE_REPINNABLE or key not in part1:
                    out.append(f"{path.name}: amendment {i} re-pins part-1 source {key}, which no amendment may")
                elif set(move) != {"from", "to"} or move["from"] != part1[key]:
                    out.append(f"{path.name}: amendment {i} part-1 pin {key} does not start at part 1's pin")
    return out


# ---------------------------------------------------------------------------------------------
# The content diff
# ---------------------------------------------------------------------------------------------
def node_at(body, path):
    node = body
    for k in path[:-1]:
        node = node[k]
    return node


def apply_ops(body, ops):
    out = json.loads(json.dumps(body))
    for op in ops:
        if op["path"][0] in OPS_FORBIDDEN_ROOTS:
            raise Refusal(f"op at {op['path']}: the declaration's frame is not amendable content")
        parent, key = node_at(out, op["path"]), op["path"][-1]
        if op["op"] == "add":
            if key in parent:
                raise Refusal(f"add at {op['path']}: the path exists")
            parent[key] = json.loads(json.dumps(op["to"]))
        elif op["op"] == "replace":
            if parent.get(key) != op["from"]:
                raise Refusal(f"replace at {op['path']}: the body does not hold its `from`")
            parent[key] = json.loads(json.dumps(op["to"]))
        else:
            raise Refusal(f"{op['op']}: an amendment op is an add or a replace")
    return out


def revert_ops(body, ops):
    out = json.loads(json.dumps(body))
    for op in reversed(ops):
        parent, key = node_at(out, op["path"]), op["path"][-1]
        if parent.get(key) != op["to"]:
            raise Refusal(f"revert at {op['path']}: the body does not hold the op's `to`")
        if op["op"] == "add":
            del parent[key]
        else:
            parent[key] = json.loads(json.dumps(op["from"]))
    return out


def part_one_moves() -> dict:
    """{part-1 source: move} as part 2's amendment records it (only the re-pinnable sources)."""
    out = {}
    for a in amendments("fit"):
        for key, move in (a.get("partOnePins") or {}).items():
            if key in PART_ONE_REPINNABLE:
                out[key] = move
    return out


def amended_sources() -> dict:
    """The amended part 2's own `sources`: the hashed record of every part-1 move (W46's review P1)."""
    path = PARTS["fit"]["declaration"]
    return json.loads(path.read_text()).get("sources", {}) if path.exists() and amendments("fit") else {}


def accepted_repin(key: str, pinned: str, now: str) -> bool:
    """A moved part-1 pin is accepted only along the move part 2's amendment records AND only at the
    bytes the AMENDED part 2 pins in its own `sources` (inside its hash chain)."""
    move = part_one_moves().get(key)
    return (bool(move) and move.get("from") == pinned and move.get("to") == now
            and amended_sources().get(key) == now)


def chain(c, part, d):
    lines, record, raw = digest_lines(part), amendments(part), PARTS[part]["declaration"].read_bytes()
    c.failures += amendment_failures(part, d)
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
        for path, move in (a.get("partOnePins") or {}).items():
            if path in (a.get("pins") or {}):
                continue
            c.eq(f"chain ({part}): amendment {i + 1} part-1 pin {path} in part 2's sources",
                 state["sources"].get(path), move.get("to"))
            state["sources"].pop(path, None)
        if a.get("ops"):
            try:
                state = revert_ops(state, a["ops"])
            except Refusal as err:
                c.failures.append(f"chain ({part}): amendment {i + 1}: {err}")
        c.eq(f"chain ({part}): the declaration before amendment {i + 1} rebuilt", sha(serialise(state)), lines[i])


def ruling_failures(items: dict, protocol: dict) -> list[str]:
    """The parent's rulings (2026-10-06) that part 1 states: each item's `parentRulings` is the protocol's
    `rulings` text exactly, and each of the four rulings is stated by the item it governs."""
    out, rulings = [], protocol.get("rulings") or {}
    governs = {"target-p-pooled": "rule", "separation-both-scales": "ladders",
               "widened-second-tap-domains": "draft", "stage-1-crossed-factorial": "draft"}
    for rid, iid in governs.items():
        if rid not in rulings:
            out.append(f"rulings: protocol.json does not record {rid!r}")
        elif (items.get(iid, {}).get("declared") or {}).get("parentRulings", {}).get(rid) != rulings[rid]:
            out.append(f"rulings: item {iid} does not state the parent's ruling {rid!r} as protocol.json records it")
    for iid, it in items.items():
        for rid, text in ((it.get("declared") or {}).get("parentRulings") or {}).items():
            if rulings.get(rid) != text:
                out.append(f"rulings: item {iid}'s {rid!r} is not protocol.json's text")
    return out


def check_protocol():
    c = Check()
    d = json.loads(PARTS["protocol"]["declaration"].read_text())
    c.eq("schema", d.get("schema"), PARTS["protocol"]["schema"])
    c.eq("charter", d.get("charter"), W.CHARTER_PIN)
    chain(c, "protocol", d)
    items = structure(c, d)
    twin(c, items, PARTS["protocol"]["twin"])
    for iid, it in items.items():
        if "declared" in it and iid in CHECKS:
            try:
                CHECKS[iid](c, it)
            except Exception as err:  # a check that cannot run is a mismatch, never a pass
                c.failures.append(f"{iid}: the check raised {type(err).__name__}: {err}")
    missing = sorted(set(CHECKS) - set(items))
    c.true(f"items: the declaration lacks {missing}", not missing)
    c.failures += ruling_failures(items, json.loads(PROTOCOL.read_text()))
    c.true("draft: fit-declaration-draft.json is not one of part 1's pinned sources",
           f"{REL}/fit-declaration-draft.json" in d["sources"])
    return c, d, items


# ---------------------------------------------------------------------------------------------
# Part 2: the validated diff
# ---------------------------------------------------------------------------------------------
def find_leaf(body, move_id, family, key):
    move = next((m for m in body["moves"] if m["id"] == move_id), None)
    fam = None if move is None else move["families"].get(family)
    return move, fam, (None if fam is None else fam["leaves"].get(key))


def drop_leaf(move, family, key):
    fam = move["families"][family]
    del fam["leaves"][key]
    for g in fam.get("factorialGroups", []):
        if key in g["keys"]:
            g["keys"].remove(key)
    fam["factorialGroups"] = [g for g in fam.get("factorialGroups", []) if len(g["keys"]) > 1]
    if not fam["factorialGroups"]:
        fam.pop("factorialGroups")
    if not fam["leaves"]:
        del move["families"][family]
        move["familyOrder"].remove(family)


def operator_leaves(body, op):
    """Every (move, family, key) of the body that is one of `op`'s leaves, in any slot."""
    return [(m, f, k) for m in body["moves"] for f, fb in m["families"].items() for k in fb["leaves"]
            if k in OPERATORS[op]]


def all_leaves(body):
    return [(m, f, k, spec) for m in body["moves"] for f, fb in m["families"].items()
            for k, spec in fb["leaves"].items()]


def rungs_flat(results, rungs) -> bool:
    """A leaf's rungs read flat: every one read and no cell of any moved beyond its bar."""
    got = results.get("rungs") or {}
    return bool(rungs) and all(r in got for r in rungs) and not any(
        cell.get("moved") for r in rungs for cell in got[r]["cells"].values())


def passing_alphas(results, shipped: float) -> set:
    """The transmission's passing rungs: the shipped value and every ladder (i) base rung (`i-a<value>`)
    at which L1 passes (`ladders.i.passingL1`)."""
    out = {shipped}
    for lab in (results.get("ladders", {}).get("i", {}).get("passingL1") or []):
        m = re.fullmatch(r"i-a([0-9.]+)", lab)
        if m:
            out.add(float(m.group(1)))
    return out


def shipped_alpha(slot: str) -> float:
    return W.document(slot)["patch"]["optics"]["regular"]["tintAlpha"]


def apply_changes(draft, changes, results, protocol):
    """The draft with `changes` applied, each only where the ladder results (`ladders/read.py`'s
    `results.json`) support it and the protocol lets the cited ladder make that kind of decision (each
    ladder's `decides`; `protocol.json` `decisions`)."""
    body = json.loads(json.dumps(draft))
    body.setdefault("namedGaps", [])
    decides = {lad["id"]: set(lad.get("decides", ())) for lad in protocol["ladders"]}
    ops = results.get("operators") or {}
    if results.get("control", {}).get("verdict") != "IDENTICAL":
        raise Refusal("the ladders' control is not IDENTICAL: no decision is supported")
    for ch in changes:
        kind = ch.get("kind")
        if kind not in CHANGE_KINDS:
            raise Refusal(f"{ch}: not one of the protocol's decisions {CHANGE_KINDS}")
        lad = ch.get("ladder")
        if lad not in decides or kind not in decides[lad]:
            raise Refusal(f"{ch}: a {kind} cites a ladder the protocol lets decide it ({lad})")
        if kind == "name-target":
            target = ch.get("target")
            if (results.get("targets") or {}).get(target, {}).get("lever"):
                raise Refusal(f"{ch}: the ladders read a lever for {target}")
            if not ch.get("operatorShape"):
                raise Refusal(f"{ch}: a named target cites its ladder and states the operator's shape (X63)")
            for move, fam, key, spec in all_leaves(body):
                if spec["target"] == target:
                    drop_leaf(move, fam, key)
            body["notFitted"].append(dict(target=target, ladder=lad, operatorShape=ch["operatorShape"]))
            continue
        if kind in ("name-unfitted", "body-width-first"):
            op = ch.get("operator", "operator 2" if kind == "body-width-first" else None)
            got = ops.get(op)
            if op not in OPERATORS or got is None:
                raise Refusal(f"{ch}: the ladders carry no reading of {op}")
            if not got.get("complete"):
                raise Refusal(f"{ch}: ladder ({lad}) is incomplete; an unread rung decides nothing")
            if not ch.get("reading"):
                raise Refusal(f"{ch}: a named operator states its ladder's reading (X63)")
            if kind == "name-unfitted":
                if got["separates"]:
                    raise Refusal(f"{ch}: the ladders read {op} as separating; it is fitted, not named")
                if got.get("bodyWidthMeets"):
                    raise Refusal(f"{ch}: the receded body width met the bar: body-width-first, not name-unfitted")
                entry = dict(operator=op, ladder=lad, reading=ch["reading"])
            else:
                if op != "operator 2" or not got.get("bodyWidthMeets"):
                    raise Refusal(f"{ch}: no receded optics.regular.blurSigma rung met clause 5 (iii)'s bar on its own")
                entry = dict(operator=op, ladder=lad, reading=ch["reading"], decision=kind,
                             rungs=list(got.get("bodyRungs") or []))
            for move, fam, key in operator_leaves(body, op):
                drop_leaf(move, fam, key)
            body["notFitted"].append(entry)
            continue
        if kind == "name-1x-gap":
            got = ops.get("2x width") or {}
            if not got.get("meets"):
                raise Refusal(f"{ch}: ladder (ii) did not meet its bar; no 1x gap is named from it")
            if not ch.get("operatorShape"):
                raise Refusal(f"{ch}: a named gap states the operator's shape (X63)")
            body["namedGaps"].append(dict(gap="the 1x per-span width", ladder=lad, shape=ch["operatorShape"],
                                          rungs=list(got.get("rungs") or [])))
            continue
        move, fam, spec = find_leaf(body, ch.get("move"), ch.get("family"), ch.get("leaf"))
        if spec is None:
            raise Refusal(f"{ch}: names no leaf of the draft")
        if kind == "strike":
            conditional = spec.get("conditional") == "ii" and lad == "ii"
            if conditional:
                got = ops.get("2x width") or {}
                if got.get("meets") or not got.get("complete"):
                    raise Refusal(f"{ch}: ladder (ii) met its bar (or is incomplete); its leaf is searched")
            elif lad != spec.get("ladder"):
                raise Refusal(f"{ch}: {ch.get('leaf')} is read on ladder ({spec.get('ladder')}), not ({lad})")
            elif not rungs_flat(results, spec.get("rungs")):
                raise Refusal(f"{ch}: its rungs {spec.get('rungs')} did not read flat")
            drop_leaf(move, ch["family"], ch["leaf"])
            continue
        # narrow: the transmission on ladder (i) only (W46's narrowing; the other grids are the fit's)
        if ch["leaf"] != "optics.regular.tintAlpha" or spec.get("ladder") != "i" or lad != "i":
            raise Refusal(f"{ch}: the protocol narrows only the active transmission, on ladder (i)")
        grid = ch.get("grid")
        if not grid or not isinstance(grid, list) or len(set(grid)) != len(grid) or not set(grid) <= set(spec["grid"]):
            raise Refusal(f"{ch}: {grid} is not a non-empty subset of the draft grid {spec['grid']}")
        allowed = passing_alphas(results, shipped_alpha(spec["slot"]))
        if not set(grid) <= allowed:
            raise Refusal(f"{ch}: {grid} leaves the transmission's passing rungs {sorted(allowed)}")
        spec["grid"] = [x for x in spec["grid"] if x in grid]
    return body


def mandatory_failures(body, results) -> list[str]:
    """What the ladders REQUIRE of part 2 (clause 5), read on the resulting body whatever its `changes`
    say: no separation at one scale only left unruled; every operator the ladders read as not separating
    named in `notFitted` with none of its leaves retained (X63), the body width first where its rung met
    the bar on its own (Decision Log 3); no part 2 at all when neither operator separates (`stop`: the
    wave closes at G0 with the finding); ladder (ii)'s conditional leaves gone unless it met its bar, and
    the 1x gap named when it did (Decision Log 2); the active transmission inside its passing rungs; no
    retained leaf whose rungs read flat; no leaf of a target named not fitted."""
    out = []
    ops = results.get("operators") or {}
    lads = results.get("ladders") or {}
    if not ops:
        return ["the ladders' results carry no operator reading"]
    for name in ("operator 1", "operator 2"):
        if ops.get(name, {}).get("oneScaleOnly"):
            out.append(f"{name} meets its bar at one scale only ({ops[name]['oneScaleOnly']}): the parent rules "
                       "before part 2")
    for lad in ("i", "iii"):
        if not lads.get(lad, {}).get("complete"):
            out.append(f"ladder ({lad}) is incomplete: an unread rung decides nothing")
    op1 = bool(ops.get("operator 1", {}).get("separates"))
    op2 = ops.get("operator 2", {})
    if not op1 and not (op2.get("separates") or op2.get("bodyWidthMeets")):
        out.append("neither operator separates: the wave closes at G0 with the finding and part 2 is not "
                   "hashed (clause 5's stop)")
    named = {x["operator"]: x for x in body.get("notFitted", []) if "operator" in x}
    want = set()
    if not op1:
        want.add("operator 1")
    if op2.get("bodyWidthMeets") or not op2.get("separates"):
        want.add("operator 2")
    for op in sorted(want - set(named)):
        out.append(f"{op} shows no separation on its ladder (or its body width met the bar) and is not named in "
                   "notFitted (clause 5; X63)")
    for op in sorted(set(named) - want):
        out.append(f"{op} is named not fitted, and the ladders read it as separating")
    if op2.get("bodyWidthMeets") and named.get("operator 2", {}).get("decision") != "body-width-first":
        out.append("operator 2: the body width met the bar on its own, and part 2 does not record body-width-first")
    for op in sorted(want | set(named)):
        for move, fam, key in operator_leaves(body, op):
            out.append(f"{move['id']}/{fam}/{key}: a leaf of {op}, which is not fitted")
    width = ops.get("2x width") or {}
    gaps = [g for g in body.get("namedGaps", []) if g.get("ladder") == "ii"]
    if width.get("meets") and not gaps:
        out.append("ladder (ii) met its bar and the 1x per-span width gap is not named (Decision Log 2; X63)")
    if not width.get("meets") and gaps:
        out.append("a 1x gap is named and ladder (ii) did not meet its bar")
    named_targets = {x["target"] for x in body.get("notFitted", []) if "target" in x}
    for move, fam, key, spec in all_leaves(body):
        where = f"{move['id']}/{fam}/{key}"
        if spec.get("conditional") == "ii" and not width.get("meets"):
            out.append(f"{where}: crossed into stage 1 only where ladder (ii) meets its bar, which it did not")
        if spec["target"] in named_targets:
            out.append(f"{where}: a leaf of target {spec['target']}, which is named not fitted (X63)")
        if rungs_flat(results, spec.get("rungs")) and spec.get("ladder") is not None:
            out.append(f"{where}: its rungs {spec['rungs']} read flat and the leaf is retained")
        if key == "optics.regular.tintAlpha" and spec.get("ladder") == "i":
            allowed = passing_alphas(results, shipped_alpha(spec["slot"]))
            if not set(spec["grid"]) <= allowed:
                out.append(f"{where}: grid {spec['grid']} leaves the transmission's passing rungs {sorted(allowed)}")
    return out


def validate_fit(draft, fit, results, protocol, record=None):
    """The ladders' validated diff and required outcomes on part 2 with its amendment's ops reverted (the
    hashed part 2 the ruling amends). The ops' own validity is the record's (`content_failures`) and the
    chain's (they revert the body to the superseded hash)."""
    record = record or []
    ops = [op for a in record for op in (a.get("ops") or [])]
    if ops:
        fit = revert_ops(fit, ops)
    if fit.get("schema") != draft["schema"]:
        raise Refusal("part 2's schema is not the draft's")
    changes = fit.get("changes")
    if not isinstance(changes, list):
        raise Refusal("part 2 lists its changes against the draft (`changes`), even when there are none")
    expected = apply_changes(draft, changes, results, protocol)
    expected.pop("status", None)
    got = {k: v for k, v in fit.items() if k not in ("status", "changes", "sources", "fromDraft")}
    got.setdefault("namedGaps", [])
    if json.dumps(got, sort_keys=True) != json.dumps(expected, sort_keys=True):
        diff = [k for k in set(got) | set(expected) if got.get(k) != expected.get(k)]
        raise Refusal(f"part 2 differs from the draft beyond its permitted changes, in: {sorted(diff)}")
    required = mandatory_failures(expected, results)
    if required:
        raise Refusal("part 2 omits what the ladders require: " + "; ".join(required))


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
    c.eq("fit: names part 1's hash", (fit.get("fromDraft") or {}).get("partOneSha256"), part1[-1] if part1 else None)
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
        validate_fit(json.loads(DRAFT.read_text()), fit, json.loads(RESULTS.read_text()), json.loads(PROTOCOL.read_text()),
                     amendments("fit"))
    except Refusal as err:
        c.failures.append(f"fit: {err}")
    return c, fit


# ---------------------------------------------------------------------------------------------
# Render evidence, amendments, the verbs
# ---------------------------------------------------------------------------------------------
def ladder_evidence():
    found = []
    if LADDER_RUNS.exists() and any('"started"' in ln for ln in LADDER_RUNS.read_text().splitlines()):
        found.append(str(LADDER_RUNS))
    if W.LADDER_SCRATCH.exists():
        found += [str(p) for p in sorted(W.LADDER_SCRATCH.rglob("matrix.json"))][:3]
        found += [str(p) for p in sorted(W.LADDER_SCRATCH.rglob("*.png"))][:1]
    return found


def fit_evidence():
    found = []
    if FIT_RUNS.exists() and any('"started"' in ln for ln in FIT_RUNS.read_text().splitlines()):
        found.append(str(FIT_RUNS))
    if W.FIT_SCRATCH.exists():
        found += [str(p) for p in sorted(W.FIT_SCRATCH.rglob("matrix.json"))][:3]
        found += [str(p) for p in sorted(W.FIT_SCRATCH.rglob("*.png"))][:1]
    return found


def amend(part, argv):
    import argparse
    ap = argparse.ArgumentParser(prog=f"declare.py amend{'-fit' if part == 'fit' else ''}")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--cause", required=True)
    ap.add_argument("--ruling", help="the charter's Decision Log heading, e.g. 'Decision Log 8' (content form)")
    ap.add_argument("--charter-commit", help="the commit whose charter records the ruling")
    ap.add_argument("--ops", help="a JSON file: the content diff, a list of add/replace ops on the body")
    if part == "fit":
        ap.add_argument("--part-one", nargs="*", default=[], help="part-1 sources the amendment's tools moved")
    ap.add_argument("pins", nargs="*")
    args = ap.parse_args(argv)
    content_args = (args.ruling, args.charter_commit, args.ops)
    if any(content_args) and not all(content_args):
        print("amend REFUSES: the content form names --ruling, --charter-commit and --ops together")
        return 2
    if not args.pins and not args.ops:
        print("amend REFUSES: an amendment re-pins a moved source or carries a ruling's content")
        return 2
    lines = digest_lines(part)
    if not lines:
        print("amend REFUSES: the part is not hashed; before the hash it is simply edited and re-checked")
        return 2
    evidence = ladder_evidence() if part == "protocol" else fit_evidence()
    if evidence and not (part == "protocol" and args.ops):
        print(f"amend REFUSES: render evidence exists for this part ({', '.join(evidence[:4])}); after the "
              "ladders only a ruling's additive content amendment of part 1 is admitted (Decision Log 8)")
        return 2
    if amendments(part):
        print("amend REFUSES: this part was amended once already (each part is amended at most once, finally)")
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
    content = {}
    if args.ops:
        try:
            ruling = decision_log(git_show(W.CHARTER_PATH, args.charter_commit).decode(), args.ruling)
            ops = json.loads(Path(args.ops).read_text())
            if evidence and any(op.get("op") != "add" for op in ops):
                raise Refusal("after a ladder render an amendment of part 1 only adds beside the hashed body; "
                              "an op that replaces a value is refused (Decision Log 8)")
            d = apply_ops(d, ops)
        except (Refusal, subprocess.CalledProcessError, OSError, KeyError, TypeError) as err:
            print(f"amend REFUSES: {err}")
            return 2
        content = {"charter": f"{W.CHARTER_PATH}@{args.charter_commit}", "ruling": ruling, "ops": ops}
    if part == "fit" and args.part_one:
        part1 = json.loads(PARTS["protocol"]["declaration"].read_text())["sources"]
        one = {}
        for key in args.part_one:
            if key not in PART_ONE_REPINNABLE or key not in part1:
                print(f"amend REFUSES: {key} is not a part-1 source the amendment may re-pin")
                return 2
            now = sha(source_bytes(key))
            if now == part1[key]:
                print(f"amend REFUSES: part-1 source {key} has not moved")
                return 2
            one[key] = {"from": part1[key], "to": now}
        if not content:
            print("amend REFUSES: part-1 moves ride a ruling's content amendment of part 2 (W46 Decision Log 9's form)")
            return 2
        # Every part-1 move is pinned in the amended part 2 too, inside its hash (W46's review P1).
        for key, move in one.items():
            if key in d["sources"] and key not in moves:
                print(f"amend REFUSES: {key} is a part-2 source and must be named as a pin")
                return 2
            d["sources"][key] = move["to"]
        content["partOnePins"] = one
    raw = serialise(d)
    entry = {"n": 1, "supersedes": lines[-1], "declarationSha256": sha(raw), "reason": args.reason,
             "cause": args.cause, **content, "pins": moves,
             "renderEvidenceAtAmendment": (
                 POST_RENDER_EVIDENCE + ", ".join(evidence) if evidence else
                 "none (" + ("ladders/runs.jsonl, the ladder scratch" if part == "protocol"
                             else "G1's fit runs and scratch") + ")")}
    PARTS[part]["amendments"].write_text(json.dumps({"schema": f"{WAVE}-{part}-amendments-1",
                                                     "amendments": [entry]}, indent=2) + "\n")
    path.write_bytes(raw)
    with PARTS[part]["digest"].open("a") as f:
        f.write(f"{entry['declarationSha256']}  {path.name}\n")
    print(f"amended: {path.name} sha256 {entry['declarationSha256']} supersedes {lines[-1]} (final)")
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
        if not PARTS["protocol"]["declaration"].exists():
            print("check: declaration.json does not exist yet (assemble.py writes it)")
            return 1
        c, d, items = check_protocol()
        waiting = [it for it in items.values() if "pending" in it]
        print(f"W47 G0 part 1: {len(items)} items, {len(d['sources'])} pinned sources")
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
        print("W47 G0 part 2: the fit declaration as a validated diff against the draft")
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
