"""W48 G0 (b)-(e): the two hashed parts of W48's declaration (charter `2026-10-06-w48-dark-operators-fit.md`,
Parent-Level Acceptance clauses 2-4; G0 (a)-(e); Decision Logs 2, 3; X71-X73). A NEW file under W48's evidence
root: W47's `declare.py` (`results/2026-10-06-w47-g0-operators/declare.py`), ported by copy; W47's pinned
copy and its spent amendment are not touched and are never run by W48 (X73).

    python3.12 -B declare.py check | hash
    python3.12 -B declare.py amend --reason TEXT --cause COMMIT [--ruling "Decision Log N"
        --charter-commit C --ops OPS.json] PIN [PIN ...]
    python3.12 -B declare.py check-fit | hash-fit
    python3.12 -B declare.py amend-fit --reason TEXT --cause COMMIT [--ruling "Decision Log N"
        --charter-commit C --ops OPS.json] [--part-one SRC ...] PIN [PIN ...]

**What W48 changes, and nothing else:**
- **Bindings.** `bindings.py` is W48's (charter pin `78d0211e0`, this root, `~/vitrea-w48`, schemas `w48-*`);
  W44's-W47's charters, schemas, part hashes and evidence or scratch paths are refused before anything is
  checked. W47's tools are inherited BY PATH under W48's bindings (`inherit.py`), pinned byte-identical in
  `bindings.INHERITED`; their tests run under W48's bindings through `tools/run_inherited.py`.
- **Part 1's items are clause 2's list for this wave**: `documents` (X62 at THIS charter's merge, equal to
  W47's), `t1`, `bar`, `manifest`, `rule` (and its W48 rehearsal), `tools`, `level` (re-bound; the shipped
  rung's identity re-proven from W47's committed record), `operators` (W47's bytes: W47's part 1 by hash and
  the runtime byte-identical to this charter's merge, clause 1), `evidence` (X71: the archive's digest, its
  manifest, the replay record and W47's readings by hash), `targets` (Decision Log 5's predictions),
  `ladders` (the corrected protocol, Decision Log 3, and the verdict reader with its tests), `startingPoint`,
  `references`, `s1` and `draft` (the narrowed part-2 draft, Decision Log 4).
- **The decision kinds are Decision Log 3's** (`ladders/protocol.json`): the changes `name-unfitted`,
  `name-target`, `narrow`, `strike` and **`hold`**, the outcomes `fit` and `stop`. There is NO precedence
  kind (`body-width-first` is gone): when the tap and the receded body width both meet bar (b), both stay
  stage-2 members (X72). `name-1x-gap` is gone with ladder (ii)'s leaves (Decision Log 4). `hold` fixes a
  non-operator leaf the draft marks `holdable` at one of its declared values, on a parent's ruling named by
  its charter Decision Log, without a flat rung: the leaf leaves the search and joins its family's `fixed`.
- **`check-fit` validates part 2 against `ladders/verdicts.json`** (X73; Decision Log 3 (e)), the corrected
  reading, never W47's `results.json` bars: an operator not separating at both scales is named unfitted, the
  body width is struck unless a body-width rung meets, a one-scale rung the parent did not rule off the grid
  stops part 2, the values Decision Logs 3 (f) and 4 put off the grid stay off it. `verdicts.json` must name
  part 1's current hash and the reader and evidence part 1 pins; part 2 pins it.
- **The order (clause 2; X73).** `hash` refuses once `verdicts.json` exists (a verdict computed before part 1's
  hash voids the declaration) or any fit render exists; `hash-fit` refuses before `verdicts.json` exists and
  after any fit render. Part 1's one amendment after the verdicts is additive content only (W47 Decision Log
  8's form, carried); part 2's refuses after any fit render.
- **An empty ops list is refused** by `amend` and `amend-fit` and on read (Decision Log 3 (g)).

W47's text follows, unchanged; where it says W47 it is W48, where it says the ladders' results it is the
verdicts.

W47 G0 (g): the two hashed parts of the declaration (charter `2026-10-06-w47-span-graded-dark-
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
WAVE = "w48"
PARTS = {
    "protocol": dict(declaration=W.PART1, twin=HERE / "declaration.md", digest=W.PART1_DIGEST,
                     amendments=HERE / "amendments.json", schema="w48-declaration-1"),
    "fit": dict(declaration=W.PART2, twin=None, digest=W.PART2_DIGEST, amendments=HERE / "fit-amendments.json",
                schema="w48-fit-declaration-1"),
}
DRAFT = W.DRAFT
INPUTS = HERE / "declaration-inputs.json"
PROTOCOL = W.LADDER_PROTOCOL
VERDICTS = W.VERDICTS
READER = W.LADDERS / "verdicts.py"
FIT_RUNS = W.G1_FIT / "runs.jsonl"
OTHER_SCHEMAS = ("w44-", "w45-", "w46-", "w47-")
RUN_INHERITED = HERE / "tools" / "run_inherited.py"
PLACEHOLDER = "TO FILL"
AMENDMENT_FIELDS = {"n", "supersedes", "declarationSha256", "reason", "cause", "pins", "renderEvidenceAtAmendment"}
# The content form (W46 Decision Log 9's, made general): the ruling verbatim, its charter, the content
# diff; part 2 adds the part-1 moves its tools made.
CONTENT_FIELDS = {"charter", "ruling", "ops"}
FIT_AMENDMENT_FIELDS = AMENDMENT_FIELDS | CONTENT_FIELDS | {"partOnePins"}
PROTOCOL_AMENDMENT_FIELDS = AMENDMENT_FIELDS | CONTENT_FIELDS
OPS_FORBIDDEN_ROOTS = ("schema", "charter", "sources", "changes", "fromDraft")
# The record of an amendment made after the verdicts begins with this (W47 Decision Log 8's form; see `amend`).
POST_RENDER_EVIDENCE = "after the verdicts read, additive only: "
# W48's own tools part 2's one amendment may re-pin (W47's inherited tools are W47's bytes and never move).
PART_ONE_REPINNABLE = tuple(f"{REL}/{p}" for p in (
    "declare.py", "test_declare.py", "test_declare.txt", "fit/build-candidate.ts", "seal/seal.ts",
    "seal/test_seal.py", "seal/test_seal.txt"))
CLAUSE_THREE = ("test_a_halving_every_target_with_three_cells_at_2b_passes", "test_b_four_cells_at_2b_fails",
                "test_c_one_cell_at_3_1b_fails", "test_d_a_gated_aggregate_worse_beyond_its_tolerance_fails",
                "test_e_every_cell_unchanged_is_neither", "test_f_a_group_of_two_gate_cells_is_reported_not_gated")
# Decision Log 3's decisions, as `ladders/protocol.json` names them: the CHANGES part 2 may list against the
# draft (each re-validated by `check-fit` against `verdicts.json`), and the two OUTCOMES that change nothing
# (`fit`) or write no part 2 (`stop`). No precedence kind (X72); `hold` beside `strike`.
CHANGE_KINDS = ("name-unfitted", "name-target", "narrow", "strike", "hold")
OUTCOMES = ("fit", "stop")
DECISIONS = CHANGE_KINDS
OPERATORS = {"operator 1": W.OPERATOR_1, "operator 2": W.OPERATOR_2}
# Clause 1: the operators are W47's bytes. These runtime files (and the identity-table tests) are held
# byte-identical to THIS charter's merge, and to the bytes W47's part 1 pinned where it pinned them.
RUNTIME = ("packages/renderer-webgpu/src/material.ts", "packages/renderer-webgpu/src/wgsl/optics.ts",
           "packages/renderer-webgpu/src/pyramid.ts", "packages/renderer-webgpu/src/renderer.ts",
           "packages/renderer-webgpu/src/passes.ts", "packages/platform-web/src/optics.ts",
           "packages/platform-web/src/css-tier.ts", "packages/calibration/test/w31-identity-table.test.ts",
           "packages/renderer-webgpu/test/w31-gate-groups.test.ts",
           "packages/calibration/test/tier-coherence.test.ts")
W47_REL = W.W47_G0.relative_to(ROOT).as_posix()

sha = lambda data: hashlib.sha256(data).hexdigest()  # noqa: E731


class Refusal(Exception):
    pass


def bindings() -> None:
    for path in (HERE, W.FIT_SCRATCH, W.G1, VERDICTS, FIT_RUNS):
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
                    raise Refusal(f"{part['digest'].name} carries a W44-W47 part hash {ln.split()[0][:12]}")


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


def run_inherited(rel: str):
    """One W47 test module (path under W47's root) run under W48's bindings (`tools/run_inherited.py`)."""
    return run(RUN_INHERITED, rel, cwd=HERE)


def last_line(out: str) -> str:
    lines = [ln for ln in out.strip().splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def ev(rel: str) -> Path:
    return HERE / rel


def cuts():
    """(bed, t1, rule, referees): W47's cuts and X69 loader, inherited by path under W48's bindings."""
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
    for slot in W.SLOTS:
        name = f"{W.DOCUMENT_SHA[slot][:12]}.json"
        c.eq(f"documents: {name} equals W47's snapshot byte for byte (no 0.25 document moved since c1f9bf84c)",
             sha((W.DOCUMENTS / name).read_bytes()), sha((W.W47_G0 / "documents" / name).read_bytes()))


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
    rc, out = run_inherited("cuts/test_rule.py")
    c.true(f"rule: W47's test_rule under W48's bindings does not pass ({last_line(out) or rc})", rc == 0)
    c.true(f"rule: test_rule runs fewer than {d['syntheticCases']} cases", ran_at_least(out, d["syntheticCases"]))
    for name in CLAUSE_THREE:
        c.true(f"rule: the case {name} does not run and pass", re.search(rf"^{name} .* ok$", out, re.M) is not None)
    reh = json.loads(ev("rehearsal/rehearsal.json").read_text())
    c.eq("rule: the rehearsal's rule file is W47's rule.py", reh["rule"]["sha256"], sha((W.CUTS_SOURCE / "rule.py").read_bytes()))
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
    """W48's own tests (each re-run; its case count at least its committed transcript's), W47's inherited tests
    re-run under W48's bindings (`tools/run_inherited.py`), the inherited pins, X60 by evidence."""
    d = it["declared"]
    for test, cwd, count in d["tests"]:
        rc, out = run("-m", "unittest", test, cwd=HERE / cwd)
        c.true(f"tools: {cwd}/{test} does not pass ({last_line(out) or rc})", rc == 0)
        c.true(f"tools: {cwd}/{test} runs fewer than {count} cases", ran_at_least(out, count))
    for rel, count in d["inheritedTests"]:
        rc, out = run_inherited(rel)
        c.true(f"tools: W47's {rel} under W48's bindings does not pass ({last_line(out) or rc})", rc == 0)
        c.true(f"tools: W47's {rel} runs fewer than {count} cases", ran_at_least(out, count))
    c.eq("tools: the inherited W47 tools are their pinned bytes", W.verify_inherited(), [])
    c.eq("tools: the inherited set", sorted(str(p.relative_to(ROOT)) for p in W.INHERITED), sorted(d["inherited"]))
    x60 = json.loads(ev("stage/x60/evidence-g0.json").read_text())
    c.eq("tools: X60 by evidence", x60["verdict"], "IDENTICAL")


def check_level(c, it):
    """The level check is W47's `level/level.py`, inherited by path; the shipped rung's identity is W47's committed
    record, re-proven against the archive's reference subset (`level/identity-reproof.json`)."""
    d = it["declared"]
    ident = json.loads((W.W47_G0 / "level/identity/identity.json").read_text())
    c.eq("level: W47's shipped-rung identity", (ident["verdict"], ident["cells"], ident["pixelAndMeasurementIdentical"],
                                                 ident["readsNoChange"]), tuple(d["identity"]))
    c.eq("level: the projection", ident["projection"], d["projection"])
    proof = json.loads(ev("level/identity-reproof.json").read_text())
    c.eq("level: the re-proof's verdict", proof.get("verdict"), d["reproof"])
    c.true("level: the re-proof did not reproduce W47's identity against the archive (review P2)",
           proof.get("verdict") == "REPRODUCED" and proof.get("failures") == [] and proof.get("pngsChecked", 0) > 0
           and proof.get("inventory", {}).get("sha256") == sha(ev("archive/inventory.json").read_bytes()))


def domains_json(parts) -> list:
    return [list(p[:1]) + ([list(p[1])] if p[0] == "set" else list(p[1:])) for p in parts]


def identity_table(material: str) -> str:
    m = re.search(r"export const MATERIAL_IDENTITY_TABLE\b.*?\n\];", material, flags=re.S)
    return m.group(0) if m else ""


def check_operators(c, it):
    """Clause 1: the operators are W47's bytes. W47's part 1 by its current hash and its `operators` item verbatim;
    every runtime file byte-identical to THIS charter's merge (and to W47's part-1 pin where it pinned one);
    each leaf's default its identity 0, in `MATERIAL_IDENTITY_TABLE`, named by the W31 tests; the X68 domains
    `bindings.DOMAINS`' (carried)."""
    d = it["declared"]
    lines = [ln.split()[0] for ln in (W.W47_G0 / "declaration.sha256").read_text().splitlines() if ln.strip()]
    c.eq("operators: W47's part 1, current hash", lines[-1], d["w47PartOne"]["sha256"])
    w47 = json.loads((W.W47_G0 / "declaration.json").read_bytes())
    c.eq("operators: W47's part 1 is its hashed bytes", sha((W.W47_G0 / "declaration.json").read_bytes()), lines[-1])
    w47_ops = next(x for x in w47["items"] if x["id"] == "operators")["declared"]
    c.eq("operators: W47's operators item, verbatim", w47_ops, d["w47Operators"])
    for path, want in d["runtime"].items():
        now = sha((ROOT / path).read_bytes())
        c.eq(f"operators: {path} is this charter's merge's bytes", now, sha(git_show(path, W.CHARTER_COMMIT)))
        c.eq(f"operators: {path} is the pinned bytes", now, want)
        if path in w47["sources"]:
            c.eq(f"operators: {path} is the bytes W47's part 1 pinned", now, w47["sources"][path])
    c.eq("operators: the runtime files", sorted(d["runtime"]), sorted(RUNTIME))
    material = (ROOT / "packages/renderer-webgpu/src/material.ts").read_text()
    table = identity_table(material)
    identity_test = (ROOT / "packages/calibration/test/w31-identity-table.test.ts").read_text()
    for name, leaves in OPERATORS.items():
        c.eq(f"operators: {name}'s leaves", w47_ops[name]["leaves"], list(leaves))
        for leaf in leaves:
            c.true(f"operators: {leaf}'s default is not its identity 0", f"\n  {leaf}: 0,\n" in material)
            c.true(f"operators: {leaf} is not in MATERIAL_IDENTITY_TABLE", leaf in table)
            c.true(f"operators: w31-identity-table.test.ts does not name {leaf}", leaf in identity_test)
            for slot in W.MOVING_SLOTS:
                parts = W.DOMAINS[slot].get(leaf)
                if parts is not None:
                    c.eq(f"operators: {slot} {leaf}'s X68 domain (carried)", domains_json(parts),
                         w47_ops[name]["domains"][slot][leaf])
    c.true("operators: operator 2's gate-group is not in the table (gate sizeFineTapShare: 0)",
           re.search(r"gate:\s*\{\s*sizeFineTapShare:\s*0\s*\}", table) is not None)
    c.true("operators: X66 — the active admits an operator-2 leaf",
           not set(W.OPERATOR_2) & set(W.ADMITTED["active.dark"]))


def check_evidence(c, it):
    """X71: W47's ladder evidence as the archive of record and the replay that reproduced it, then pinned: the
    archive record and inventory, the replay record (every output equal, the control 142 of 142, the tree
    unchanged, every denial fired), `ladders/evidence.json`'s pins of W47's files at their bytes."""
    d = it["declared"]
    arch = json.loads(ev("archive/archive.json").read_text())
    inv = ev("archive/inventory.json")
    c.eq("evidence: the inventory's digest", sha(inv.read_bytes()), d["inventorySha256"])
    c.eq("evidence: the archive record's inventory", arch["inventory"]["sha256"], d["inventorySha256"])
    c.eq("evidence: the asset", [arch["asset"]["name"], arch["asset"]["sha256"], arch["asset"]["bytes"]],
         [d["asset"], d["sha256"], d["bytes"]])
    c.eq("evidence: GitHub's digest", arch["asset"]["githubDigest"], f"sha256:{d['sha256']}")
    c.eq("evidence: the release", [arch["release"]["tag"], arch["release"]["latest"]], [d["release"], False])
    inventory = json.loads(inv.read_text())
    c.eq("evidence: entries per section", {k: len(inventory[k]) for k in ("ladders", "drive", "reference")},
         d["entries"])
    rep = json.loads(ev("replay/record/replay.json").read_text())
    c.true("evidence: the replay does not reproduce W47's readings", rep["allEqual"] is True)
    c.true("evidence: a denial did not fire", all(x["refused"] for x in rep["negativeControl"]))
    c.eq("evidence: the replay's control identity", [rep["counts"]["identityIdentical"], rep["counts"]["identityCells"]],
         [142, 142])
    c.eq("evidence: the replay read the archive by its inventory", rep["archive"]["before"]["inventorySha256"],
         d["inventorySha256"])
    c.true("evidence: the archive tree moved during the replay", rep["archive"]["unchanged"] is True)
    for e in rep["equality"]:
        if "replaySha256" in e:
            c.eq(f"evidence: the replay's {e['file']} is W47's committed file",
                 e["replaySha256"], sha((W.W47_G0 / "ladders" / e["file"]).read_bytes()))
            c.eq(f"evidence: replay/record/{e['file']} is the recorded output",
                 sha(ev(f"replay/record/{e['file']}").read_bytes()), e["replaySha256"])
    c.eq("evidence: the replay's capture record", sha(ev("replay/record/captures.json").read_bytes()), rep["capturesSha256"])
    pins = json.loads(W.LADDER_EVIDENCE.read_text())
    for path, want in pins["w47"].items():
        c.eq(f"evidence: {path} is its pinned bytes", sha((ROOT / path).read_bytes()), want)
    c.eq("evidence: W47's part-1 hashes", [pins["w47PartOne"]["superseded"], pins["w47PartOne"]["current"]],
         d["w47PartOne"])
    c.eq("evidence: the pins name the archive", pins["archive"]["sha256"], d["sha256"])
    c.eq("evidence: the pins name the replay record", pins["replay"]["recordSha256"],
         sha(ev("replay/record/replay.json").read_bytes()))


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


def w47_protocol() -> dict:
    """W47's hashed protocol: the rungs W47 rendered (X71), read by path."""
    return json.loads((W.W47_G0 / "ladders" / "protocol.json").read_text())


def charter_rulings() -> dict:
    """Decision Log 3's items (a)-(g), verbatim (whitespace folded), from the charter at its merge."""
    text = git_show(W.CHARTER_PATH, W.CHARTER_COMMIT).decode()
    dl3 = decision_log(text, "Decision Log 3")
    return {f"decision-log-3-{m.group(1)}": " ".join(m.group(2).split())
            for m in re.finditer(r"^- \(([a-g])\) (.*?)(?=^- \(|^\*Why)", dl3, flags=re.M | re.S)}


def check_ladders(c, it):
    """The corrected protocol (Decision Log 3; X72) and the verdict reader: the decision kinds (`hold` in, no
    precedence kind), each ladder W47's rungs exactly, the evidence pins, the levers partitioning W47's
    ladder (i) and (iii) rungs, the off-grid values inside the rungs that moved them, the bars' numbers, the
    rulings verbatim from the charter, the expectations, X69's disjointness."""
    B, T1, _, R = cuts()
    d = it["declared"]
    p = json.loads(PROTOCOL.read_text())
    w47 = w47_protocol()
    c.eq("ladders: protocol schema", p.get("schema"), "w48-ladder-protocol-1")
    c.eq("ladders: protocol charter", p.get("charter"), W.CHARTER_PIN)
    c.eq("ladders: the protocol's decisions", sorted(p.get("decisions", {})), sorted(CHANGE_KINDS + OUTCOMES))
    c.eq("ladders: the protocol's change kinds", (p.get("decisionKinds") or {}).get("changes"), list(CHANGE_KINDS))
    c.eq("ladders: the protocol's outcomes", (p.get("decisionKinds") or {}).get("outcomes"), list(OUTCOMES))
    c.true("ladders: a precedence kind survives (Decision Log 3 (c))",
           "body-width-first" not in p.get("decisions", {}) and "body-width-first" not in CHANGE_KINDS)
    for lid, kinds in p["decides"].items():
        c.true(f"ladders: ({lid}) decides outside the change kinds", set(kinds) <= set(CHANGE_KINDS))
    w47_rungs = {lad["id"]: [r["label"] for r in lad["rungs"]] for lad in w47["ladders"]}
    c.eq("ladders: each ladder's rungs are W47's, none added or removed (X71)",
         {k: v["rungs"] for k, v in p["ladders"].items()}, w47_rungs)
    ev_ = p["evidence"]
    for key in ("pins", "rungs", "results", "reread", "cells"):
        c.eq(f"ladders: the protocol's {key} pin", sha((ROOT / ev_[key]["path"]).read_bytes()), ev_[key]["sha256"])
    c.eq("ladders: the evidence pins are bindings'", ROOT / ev_["pins"]["path"], W.LADDER_EVIDENCE)
    c.eq("ladders: the cells are bindings'", ROOT / ev_["cells"]["path"], W.LADDER_CELLS)
    lev = p["levers"]
    c.eq("ladders: the levers partition W47's ladder (i) and (iii) rungs",
         sorted(lev["operator 1"]) + sorted(lev["operator 2"] + lev["body width"]),
         sorted(w47_rungs["i"]) + sorted(w47_rungs["iii"]))
    c.true("ladders: a body-width lever moves no blurSigma",
           all("optics.regular.blurSigma" in r["overrides"].get("receded.dark", {})
               for lad in w47["ladders"] for r in lad["rungs"] if r["label"] in lev["body width"]))
    over = {r["label"]: r["overrides"] for lad in w47["ladders"] for r in lad["rungs"]}
    for kind in ("oneScale", "metNowhere"):
        for x in p["offGrid"][kind]:
            for slot, leaves in x["values"].items():
                for leaf, v in leaves.items():
                    c.eq(f"ladders: offGrid {x['rung']} {leaf} is what that rung moved",
                         over.get(x["rung"], {}).get(slot, {}).get(leaf), v)
    c.eq("ladders: the bars", p["bars"], d["bars"])
    c.eq("ladders: the separation rule", p["separation"], d["separation"])
    c.eq("ladders: the off-grid values", p["offGrid"], d["offGrid"])
    c.eq("ladders: the expectations (the charter's clause 3 Bar)", p["expected"], d["expected"])
    c.eq("ladders: the rulings are Decision Log 3's items, verbatim", p["rulings"], charter_rulings())
    c.eq("ladders: the item states the rulings", d["parentRulings"], p["rulings"])
    c.eq("ladders: the reader", sha(READER.read_bytes()), d["readerSha256"])
    try:
        R.check_disjoint(R.load_manifest(), R.load_ladder_cells())
    except W.Refusal as err:
        c.failures.append(f"ladders: X69 disjointness: {err}")
    cells = json.loads(W.LADDER_CELLS.read_text())
    for sid in cells["union"]:
        c.true(f"ladders: {sid} is a holdout scene", B.SCENES.role[sid] != "holdout")


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


SPAN_LAW = ("optics.regular.tintAlpha", "tintAlphaFar1x", "tintAlphaFar2x", "sizeScatterSpanMax",
            "sizeScatterSpanMax2x", "sizeOcclusionGain")
FINE_TERM = ("optics.regular.tintAlpha", "sizeFineTapSigma", "sizeFineTapSigma2x", "sizeFineTapShare",
             "optics.regular.blurSigma")
SECOND_TAP = ("sizeHeavySecondShare", "sizeHeavySecondSigma", "sizeHeavySecondSigma2x", "sizeHeavySecondShareFar2x")
HOLDABLE = ("sizeOcclusionGain", "sizeScatterSpanMax", "sizeScatterSpanMax2x")   # Decision Log 3 (d)


def off_grid(protocol: dict) -> dict:
    """(slot, leaf) -> the values Decision Logs 3 (f) and 4 put off the grid."""
    out = {}
    for kind in ("oneScale", "metNowhere"):
        for x in protocol["offGrid"][kind]:
            for slot, leaves in x["values"].items():
                for leaf, v in leaves.items():
                    out.setdefault((slot, leaf), set()).add(v)
    return out


def grid_failures(body: dict, protocol: dict) -> list[str]:
    """No searched grid carries a value Decision Logs 3 (f) and 4 put off the grid."""
    out, off = [], off_grid(protocol)
    for m in body["moves"]:
        for fam, fb in m["families"].items():
            for key, spec in fb["leaves"].items():
                bad = sorted(set(spec["grid"]) & off.get((spec["slot"], key), set()))
                if bad:
                    out.append(f"{m['id']}/{fam}/{key}: grid carries {bad}, off the grid (Decision Logs 3 (f), 4)")
    return out


def draft_failures(draft: dict, protocol: dict, targets) -> list[str]:
    """The draft's shape (clause 2; Design "The moves", MARKED; Decision Logs 3, 4): every searched leaf a dark
    slot's, admitted by X64 ∪ X67 or named by its snapshot, its grid sorted, distinct and inside both its
    declared domain and its X68 domain, a unit and one of the rule's targets; its `ladder` one of W47's ladders
    (or none) and its `rungs` W47's rungs that move it in its slot; no ladder-(ii) conditional leaf and no
    second tap in stage 1 (ladder (ii) met no rung); `holdable` only on the leaves Decision Log 3 (d) names, at
    values on the leaf's grid; no off-grid value; the span law and the stage-2 factorial each one group; a
    family's `fixed` values admitted and inside X68; nothing named before the verdicts."""
    out = []
    w47 = w47_protocol()
    ladders = {lad["id"] for lad in w47["ladders"]}
    by_rung = rung_leaves(w47)
    rung_ladder = {r["id"]: lad["id"] for lad in w47["ladders"] for r in protocol_rungs(lad)}
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
                    out.append(f"draft: {sid} names a ladder W47's protocol does not declare ({lad})")
                for r in rungs:
                    if (key, spec["slot"]) not in by_rung.get(r, set()):
                        out.append(f"draft: {sid} cites rung {r}, which does not move it in {spec['slot']}")
                if lad is not None and not any(rung_ladder.get(r) == lad for r in rungs):
                    out.append(f"draft: {sid} names ladder ({lad}) and none of its rungs")
                if spec.get("conditional") is not None:
                    out.append(f"draft: {sid} is conditional on {spec['conditional']!r}; ladder (ii) met no rung "
                               "and no W48 leaf is conditional (Decision Log 4)")
                if spec.get("operator") is not None and key not in OPERATORS.get(spec["operator"], ()):
                    out.append(f"draft: {sid} is tagged {spec['operator']} and is not one of its leaves")
                if "holdable" in spec:
                    if key not in HOLDABLE or any(key in v for v in OPERATORS.values()):
                        out.append(f"draft: {sid} is holdable and is not a leaf Decision Log 3 (d) names")
                    elif not spec["holdable"].get("values") or not set(spec["holdable"]["values"]) <= set(grid):
                        out.append(f"draft: {sid} holdable values {spec['holdable'].get('values')} are not on its grid")
            for leaf, fx in body.get("fixed", {}).items():
                if fx["slot"] not in W.MOVING_SLOTS or not admitted_leaf(fx["slot"], leaf):
                    out.append(f"draft: {m['id']}/{fam} fixes {fx['slot']} {leaf}, not a leaf it may name")
                elif not W.in_domain(fx["slot"], leaf, fx["value"]):
                    out.append(f"draft: {m['id']}/{fam} fixes {leaf}={fx['value']} outside its X68 domain")
            for g in body.get("factorialGroups", []):
                if not set(g["keys"]) <= set(body["leaves"]):
                    out.append(f"draft: {m['id']}/{fam} factorial group names a leaf it does not search")
    out += [f"draft: {x}" for x in grid_failures(draft, protocol)]
    stages = {m["id"]: m for m in draft["moves"]}
    if set(stages) != {"stage1", "stage2"}:
        out.append(f"draft: the moves are {sorted(stages)}, not stage1 and stage2")
        return out
    if stages["stage2"].get("materialise") != "receded.dark" or stages["stage2"].get("materialiseX64") is not None:
        out.append("draft: stage 2 does not materialise the receded X64 ∪ X67 keys (materialise: receded.dark)")
    if stages["stage1"].get("materialise") is not None or stages["stage1"].get("materialiseX64") is not None:
        out.append("draft: stage 1 materialises a slot; only stage 2's base is materialised")
    for sid, keys in (("stage1", SPAN_LAW), ("stage2", FINE_TERM)):
        groups = [set(g["keys"]) for fb in stages[sid]["families"].values() for g in fb.get("factorialGroups", [])]
        if set(keys) not in groups:
            out.append(f"draft: {sid} does not search {sorted(keys)} as ONE factorial (Design \"The moves\", MARKED)")
    s1 = {k for fb in stages["stage1"]["families"].values() for k in list(fb["leaves"]) + list(fb.get("fixed", {}))}
    if s1 & set(SECOND_TAP):
        out.append(f"draft: stage 1 carries the second tap {sorted(s1 & set(SECOND_TAP))}; ladder (ii) met no rung")
    if draft.get("notFitted") != []:
        out.append("draft: a target or operator is named not fitted before the verdicts")
    if draft.get("namedGaps", []) != []:
        out.append("draft: a gap is named before the verdicts")
    return out


def check_draft(c, it):
    d = it["declared"]
    draft = json.loads(DRAFT.read_text())
    protocol = json.loads(PROTOCOL.read_text())
    c.eq("draft: schema", draft["schema"], PARTS["fit"]["schema"])
    c.eq("draft: charter", draft["charter"], W.CHARTER_PIN)
    c.eq("draft: stages", [m["id"] for m in draft["moves"]], d["stages"])
    c.eq("draft: references", {k: draft["references"][k] for k in ("dark", "light")}, W.REFERENCE)
    c.true("draft: the landing rule is not W47's cuts/rule.py",
           draft["landingRule"]["implementation"].startswith("cuts/rule.py"))
    c.failures += draft_failures(draft, protocol, d["targets"])
    count = sum(len(f["leaves"]) for m in draft["moves"] for f in m["families"].values())
    c.eq("draft: searched leaves", count, d["searchedLeaves"])
    c.eq("draft: the stage sizes", draft.get("stageSizes"), d["stageSizes"])
    c.eq("draft: narrowed from W47's draft at its bytes", draft["fromW47"]["sha256"],
         sha((W.W47_G0 / "fit-declaration-draft.json").read_bytes()))


CHECKS = {"documents": check_documents, "t1": check_t1, "bar": check_bar, "manifest": check_manifest,
          "rule": check_rule, "tools": check_tools, "level": check_level, "operators": check_operators,
          "evidence": check_evidence, "targets": check_targets, "ladders": check_ladders,
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
    if not a["ops"]:
        out.append(f"{name}: amendment {i} carries an empty ops list; an amendment is spent on content, never on "
                   "nothing (Decision Log 3 (g))")
    if not str(a["charter"]).startswith(f"{W.CHARTER_PATH}@"):
        out.append(f"{name}: amendment {i} names a charter other than W48's ({a['charter']})")
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
                out.append(f"{path.name}: amendment {i} was made over the verdicts and is not part 1's "
                           "content form (W47 Decision Log 8's form, carried)")
            elif any(op.get("op") != "add" for op in a["ops"]):
                out.append(f"{path.name}: amendment {i} was made over the verdicts and replaces a hashed value; "
                           "only an add is admitted after them (W47 Decision Log 8's form, carried)")
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
    """The parent's rulings part 1 states: protocol.json's `rulings` are Decision Log 3's items verbatim
    (`check_ladders`), and the `ladders` item states them as the protocol records them."""
    out, rulings = [], protocol.get("rulings") or {}
    if (items.get("ladders", {}).get("declared") or {}).get("parentRulings") != rulings:
        out.append("rulings: item ladders does not state Decision Log 3's rulings as protocol.json records them")
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


def body_width_leaves(body):
    """The receded body width, wherever the body searches it."""
    return [(m, f, k) for m in body["moves"] for f, fb in m["families"].items() for k, spec in fb["leaves"].items()
            if k == "optics.regular.blurSigma" and spec["slot"] == "receded.dark"]


def all_leaves(body):
    return [(m, f, k, spec) for m in body["moves"] for f, fb in m["families"].items()
            for k, spec in fb["leaves"].items()]


def rungs_flat(verdicts, rungs) -> bool:
    """A leaf's rungs read flat: every one read and none moved a cell beyond its bar (`verdicts.json` `flat`,
    read from W47's results.json by key)."""
    flat = verdicts.get("flat") or {}
    return bool(rungs) and all(r in flat for r in rungs) and all(flat[r] for r in rungs)


def passing_alphas(verdicts, shipped: float) -> set:
    """The transmission's passing rungs: the snapshot's value and every ladder (i) base rung (`i-a<value>`) at
    which L1 passes (`verdicts.json` `ladders.i.passingL1`)."""
    out = {shipped}
    for lab in (verdicts.get("ladders", {}).get("i", {}).get("passingL1") or []):
        m = re.fullmatch(r"i-a([0-9.]+)", lab)
        if m:
            out.add(float(m.group(1)))
    return out


def shipped_alpha(slot: str) -> float:
    return W.document(slot)["patch"]["optics"]["regular"]["tintAlpha"]


def hold_ruling(ch) -> str:
    """The parent's ruling a `hold` cites: the charter's `### Decision Log N` section at the commit named, which
    must name the held leaf; refused otherwise."""
    heading, commit = ch.get("ruling"), ch.get("charterCommit")
    if not (heading and commit):
        raise Refusal(f"{ch}: a hold names the parent's ruling (`ruling`, `charterCommit`; Decision Log 3 (d))")
    try:
        text = decision_log(git_show(W.CHARTER_PATH, commit).decode(), heading)
    except (Refusal, subprocess.CalledProcessError) as err:
        raise Refusal(f"{ch}: the charter at {commit} records no `### {heading}` ({err})") from None
    if ch.get("leaf") not in text:
        raise Refusal(f"{ch}: {heading} does not name {ch.get('leaf')}")
    return text


def apply_changes(draft, changes, verdicts, protocol):
    """The draft with `changes` applied, each only where the verdicts (`ladders/verdicts.json`, Decision Log 3's
    reading) support it and the protocol lets the cited ladder make that kind of decision (`decides`)."""
    body = json.loads(json.dumps(draft))
    body.setdefault("namedGaps", [])
    decides = {lid: set(kinds) for lid, kinds in protocol["decides"].items()}
    ops = verdicts.get("operators") or {}
    for ch in changes:
        kind = ch.get("kind")
        if kind not in CHANGE_KINDS:
            raise Refusal(f"{ch}: not one of the protocol's decisions {CHANGE_KINDS}")
        lad = ch.get("ladder")
        if lad not in decides or kind not in decides[lad]:
            raise Refusal(f"{ch}: a {kind} cites a ladder the protocol does not let decide it ({lad})")
        if kind == "name-target":
            target = ch.get("target")
            if not ch.get("operatorShape") or not ch.get("reading"):
                raise Refusal(f"{ch}: a named target cites its ladder, its reading and the operator's shape (X63)")
            levers = {"F inactive": ops.get("operator 2", {}).get("separates") or ops.get("operator 2", {}).get("bodyWidthMeets"),
                      "C rest": ops.get("operator 1", {}).get("separates"), "P": ops.get("operator 1", {}).get("separates")}
            if levers.get(target):
                raise Refusal(f"{ch}: the verdicts read a lever for {target}")
            for move, fam, key, spec in all_leaves(body):
                if spec["target"] == target:
                    drop_leaf(move, fam, key)
            body["notFitted"].append(dict(target=target, ladder=lad, reading=ch["reading"],
                                          operatorShape=ch["operatorShape"]))
            continue
        if kind == "name-unfitted":
            op = ch.get("operator")
            got = ops.get(op)
            if op not in OPERATORS or got is None:
                raise Refusal(f"{ch}: the verdicts carry no reading of {op}")
            if not ch.get("reading"):
                raise Refusal(f"{ch}: a named operator states its reading (X63)")
            if got["separates"]:
                raise Refusal(f"{ch}: the verdicts read {op} as separating at both scales; it is fitted, not named")
            for move, fam, key in operator_leaves(body, op):
                drop_leaf(move, fam, key)
            body["notFitted"].append(dict(operator=op, ladder=lad, reading=ch["reading"]))
            continue
        move, fam, spec = find_leaf(body, ch.get("move"), ch.get("family"), ch.get("leaf"))
        if spec is None:
            raise Refusal(f"{ch}: names no leaf of the draft")
        if kind == "strike":
            if ch["leaf"] == "optics.regular.blurSigma" and spec["slot"] == "receded.dark":
                if lad != "iii" or ops.get("operator 2", {}).get("bodyWidthMeets"):
                    raise Refusal(f"{ch}: a body-width rung meets bar (b) at both scales; the body width is a member")
            elif lad != spec.get("ladder"):
                raise Refusal(f"{ch}: {ch.get('leaf')} is read on ladder ({spec.get('ladder')}), not ({lad})")
            elif not rungs_flat(verdicts, spec.get("rungs")):
                raise Refusal(f"{ch}: its rungs {spec.get('rungs')} did not read flat")
            drop_leaf(move, ch["family"], ch["leaf"])
            continue
        if kind == "hold":
            if any(ch["leaf"] in v for v in OPERATORS.values()):
                raise Refusal(f"{ch}: an operator leaf is fitted or named, never held (Decision Log 3 (d))")
            if ch.get("value") not in (spec.get("holdable") or {}).get("values", []):
                raise Refusal(f"{ch}: {ch.get('value')} is not a value the draft declares {ch['leaf']} holdable at")
            if lad != spec.get("ladder"):
                raise Refusal(f"{ch}: {ch['leaf']} is read on ladder ({spec.get('ladder')}), not ({lad})")
            text = hold_ruling(ch)
            family = move["families"][ch["family"]]
            slot = spec["slot"]
            drop_leaf(move, ch["family"], ch["leaf"])
            fixed = move["families"].setdefault(ch["family"], family).setdefault("fixed", {})
            fixed[ch["leaf"]] = dict(slot=slot, value=ch["value"], heldBy=f"{ch['ruling']} @ {ch['charterCommit']}",
                                     rulingSha256=sha(text.encode()))
            continue
        # narrow: the active transmission on ladder (i) only (W46's and W47's narrowing; other grids are the fit's)
        if ch["leaf"] != "optics.regular.tintAlpha" or spec.get("ladder") != "i" or lad != "i":
            raise Refusal(f"{ch}: the protocol narrows only the active transmission, on ladder (i)")
        grid = ch.get("grid")
        if not grid or not isinstance(grid, list) or len(set(grid)) != len(grid) or not set(grid) <= set(spec["grid"]):
            raise Refusal(f"{ch}: {grid} is not a non-empty subset of the draft grid {spec['grid']}")
        allowed = passing_alphas(verdicts, shipped_alpha(spec["slot"]))
        if not set(grid) <= allowed:
            raise Refusal(f"{ch}: {grid} leaves the transmission's passing rungs {sorted(allowed)}")
        spec["grid"] = [x for x in spec["grid"] if x in grid]
    return body


def mandatory_failures(body, verdicts, protocol) -> list[str]:
    """What the verdicts REQUIRE of part 2 (Decision Log 3; X72, X73), read on the resulting body whatever its
    `changes` say: no unruled one-scale rung; no part 2 at all when neither operator separates; every operator not
    separating at both scales named with none of its leaves retained; the body width retained only where a
    body-width rung meets (and then beside the tap: no precedence); no grid value Decision Logs 3 (f) and 4 put
    off the grid; the active transmission inside its passing rungs; no retained leaf whose rungs read flat; no
    leaf of a target named not fitted; no hold of an operator leaf."""
    out = []
    ops = verdicts.get("operators") or {}
    if not ops:
        return ["the verdicts carry no operator reading"]
    unruled = (verdicts.get("oneScale") or {}).get("unruled") or []
    if unruled:
        out.append(f"rungs meeting at one scale only that no ruling put off the grid ({unruled}): the parent rules "
                   "before part 2 (W47's one-scale rule, Decision Log 3 (f))")
    for lid in ("i", "iii"):
        if not (verdicts.get("ladders") or {}).get(lid, {}).get("complete"):
            out.append(f"ladder ({lid}) is incomplete in the verdicts: an unread rung decides nothing")
    op1 = bool(ops.get("operator 1", {}).get("separates"))
    op2 = ops.get("operator 2", {})
    tap, width = bool(op2.get("separates")), bool(op2.get("bodyWidthMeets"))
    if not op1 and not (tap or width):
        out.append("neither operator separates: the wave closes at G0 with the finding and part 2 is not hashed (stop)")
    named = {x["operator"]: x for x in body.get("notFitted", []) if "operator" in x}
    want = ({"operator 1"} if not op1 else set()) | ({"operator 2"} if not tap else set())
    for op in sorted(want - set(named)):
        out.append(f"{op} does not separate at both scales and is not named in notFitted (X63)")
    for op in sorted(set(named) - want):
        out.append(f"{op} is named not fitted, and the verdicts read it as separating at both scales")
    for op in sorted(want | set(named)):
        for move, fam, key in operator_leaves(body, op):
            out.append(f"{move['id']}/{fam}/{key}: a leaf of {op}, which is not fitted")
    retained_width = body_width_leaves(body)
    if retained_width and not width:
        out.append("the receded body width is searched and no body-width rung meets bar (b) at both scales (strike it)")
    if width and not retained_width:
        out.append("a body-width rung meets bar (b) at both scales and the body width is not searched (no precedence, "
                   "Decision Log 3 (c))")
    if tap and not operator_leaves(body, "operator 2"):
        out.append("the tap separates at both scales and its leaves are not searched (no precedence, Decision Log 3 (c))")
    out += grid_failures(body, protocol)
    named_targets = {x["target"] for x in body.get("notFitted", []) if "target" in x}
    for move, fam, key, spec in all_leaves(body):
        where = f"{move['id']}/{fam}/{key}"
        if spec["target"] in named_targets:
            out.append(f"{where}: a leaf of target {spec['target']}, which is named not fitted (X63)")
        if spec.get("ladder") is not None and rungs_flat(verdicts, spec.get("rungs")):
            out.append(f"{where}: its rungs {spec['rungs']} read flat and the leaf is retained")
        if key == "optics.regular.tintAlpha" and spec.get("ladder") == "i":
            allowed = passing_alphas(verdicts, shipped_alpha(spec["slot"]))
            if not set(spec["grid"]) <= allowed:
                out.append(f"{where}: grid {spec['grid']} leaves the transmission's passing rungs {sorted(allowed)}")
    for m in body["moves"]:
        for fam, fb in m["families"].items():
            for leaf in fb.get("fixed", {}):
                if any(leaf in v for v in OPERATORS.values()) and "heldBy" in fb["fixed"][leaf]:
                    out.append(f"{m['id']}/{fam}: operator leaf {leaf} is held")
    return out


def verdict_failures(verdicts: dict, part1: dict, digest: str) -> list[str]:
    """`verdicts.json` must be the pinned reader's reading of the pinned evidence after part 1's CURRENT hash."""
    out = []
    if verdicts.get("schema") != "w48-verdicts-1":
        out.append(f"verdicts.json: schema {verdicts.get('schema')!r}")
    if verdicts.get("declarationSha256") != digest:
        out.append("verdicts.json does not name part 1's current hash")
    names = {"reader": f"{REL}/ladders/verdicts.py", "protocol": f"{REL}/ladders/protocol.json",
             "evidence": f"{REL}/ladders/evidence.json"}
    protocol = json.loads(PROTOCOL.read_text())
    names |= {k: protocol["evidence"][k]["path"] for k in ("results", "reread", "rungs")}
    for key, rel in names.items():
        pinned = part1["sources"].get(rel)
        if pinned is None or (verdicts.get("inputs") or {}).get(key) != pinned:
            out.append(f"verdicts.json read {key} at bytes part 1 does not pin ({rel})")
    return out


def validate_fit(draft, fit, verdicts, protocol, record=None):
    """The verdicts' validated diff and required outcomes on part 2 with its amendment's ops reverted (the hashed
    part 2 a ruling amends)."""
    record = record or []
    ops = [op for a in record for op in (a.get("ops") or [])]
    if ops:
        fit = revert_ops(fit, ops)
    if fit.get("schema") != draft["schema"]:
        raise Refusal("part 2's schema is not the draft's")
    changes = fit.get("changes")
    if not isinstance(changes, list):
        raise Refusal("part 2 lists its changes against the draft (`changes`), even when there are none")
    expected = apply_changes(draft, changes, verdicts, protocol)
    expected.pop("status", None)
    got = {k: v for k, v in fit.items() if k not in ("status", "changes", "sources", "fromDraft")}
    got.setdefault("namedGaps", [])
    if json.dumps(got, sort_keys=True) != json.dumps(expected, sort_keys=True):
        diff = [k for k in set(got) | set(expected) if got.get(k) != expected.get(k)]
        raise Refusal(f"part 2 differs from the draft beyond its permitted changes, in: {sorted(diff)}")
    required = mandatory_failures(expected, verdicts, protocol)
    if required:
        raise Refusal("part 2 omits what the verdicts require: " + "; ".join(required))


def check_fit():
    c = Check()
    if not PARTS["protocol"]["digest"].exists():
        c.failures.append("part 1 is not hashed; part 2 is checked only after it")
        return c, None
    if not VERDICTS.exists():
        c.failures.append("ladders/verdicts.json does not exist; part 2 is validated only against the verdicts (X73)")
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
    c.eq("fit: names the verdicts' hash", (fit.get("fromDraft") or {}).get("verdictsSha256"), sha(VERDICTS.read_bytes()))
    chain(c, "fit", fit)
    for key, want in (fit.get("sources") or {}).items():
        try:
            c.eq(f"pin {key}", sha(source_bytes(key)), want)
        except (OSError, subprocess.CalledProcessError) as err:
            c.failures.append(f"pin {key}: unreadable ({err})")
    c.true("fit: ladders/verdicts.json is not one of part 2's pinned sources",
           f"{REL}/ladders/verdicts.json" in (fit.get("sources") or {}))
    verdicts = json.loads(VERDICTS.read_text())
    c.failures += verdict_failures(verdicts, json.loads(PARTS["protocol"]["declaration"].read_text()),
                                   part1[-1] if part1 else None)
    try:
        validate_fit(json.loads(DRAFT.read_text()), fit, verdicts, json.loads(PROTOCOL.read_text()),
                     amendments("fit"))
    except Refusal as err:
        c.failures.append(f"fit: {err}")
    return c, fit


# ---------------------------------------------------------------------------------------------
# Evidence, amendments, the verbs
# ---------------------------------------------------------------------------------------------
def verdict_evidence():
    """X73: the verdicts exist only after part 1's hash; their presence is part 1's post-reading evidence."""
    return [str(VERDICTS)] if VERDICTS.exists() else []


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
    if args.ops:
        try:
            given = json.loads(Path(args.ops).read_text())
        except (OSError, ValueError) as err:
            print(f"amend REFUSES: --ops is unreadable ({err})")
            return 2
        if not isinstance(given, list) or not given:
            print("amend REFUSES: the ops list is empty (or not a list); an amendment is spent on content, never on "
                  "nothing (Decision Log 3 (g))")
            return 2
    lines = digest_lines(part)
    if not lines:
        print("amend REFUSES: the part is not hashed; before the hash it is simply edited and re-checked")
        return 2
    evidence = (verdict_evidence() + fit_evidence()) if part == "protocol" else fit_evidence()
    if evidence and not (part == "protocol" and args.ops):
        print(f"amend REFUSES: post-reading evidence exists for this part ({', '.join(evidence[:4])}); after the "
              "verdicts only a ruling's additive content amendment of part 1 is admitted (W47 Decision Log 8's form)")
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
            if not isinstance(ops, list) or not ops:
                raise Refusal("the ops list is empty (or not a list); an amendment is spent on content, never on "
                              "nothing (Decision Log 3 (g))")
            if evidence and any(op.get("op") != "add" for op in ops):
                raise Refusal("after the verdicts an amendment of part 1 only adds beside the hashed body; "
                              "an op that replaces a value is refused (W47 Decision Log 8's form)")
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
                 "none (" + ("ladders/verdicts.json, G1's fit runs and scratch" if part == "protocol"
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
        print(f"W48 G0 part 1: {len(items)} items, {len(d['sources'])} pinned sources")
        rc = report(c, waiting, "check")
        if verb == "check" or rc:
            return rc
        if waiting:
            print("hash REFUSES: " + ", ".join(it["id"] for it in waiting) + " pending")
            return 2
        if PARTS["protocol"]["digest"].exists():
            print("hash REFUSES: part 1 is hashed already; this tool never overwrites a hash")
            return 2
        if verdict_evidence() or fit_evidence():
            print("hash REFUSES: the verdicts or a fit render exist; part 1 is hashed before either (X73; clause 2: "
                  "a verdict computed before part 1's hash voids the declaration)")
            return 2
        digest = sha(PARTS["protocol"]["declaration"].read_bytes())
        with PARTS["protocol"]["digest"].open("x") as f:
            f.write(f"{digest}  declaration.json\n")
        print(f"declaration.json sha256 {digest}; commit it with declaration.sha256 before the verdicts are read")
        return 0
    if verb in ("check-fit", "hash-fit"):
        c, fit = check_fit()
        print("W48 G0 part 2: the fit declaration as a validated diff against the draft, read on the verdicts")
        rc = report(c, [], "check-fit")
        if verb == "check-fit" or rc:
            return rc
        if PARTS["fit"]["digest"].exists():
            print("hash-fit REFUSES: part 2 is hashed already")
            return 2
        if fit_evidence():
            print("hash-fit REFUSES: a fit render exists; part 2 is hashed before any")
            return 2
        if not verdict_evidence():
            print("hash-fit REFUSES: ladders/verdicts.json does not exist; part 2 is hashed only after it (X73)")
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
