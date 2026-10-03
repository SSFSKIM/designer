"""W45 G0 (b): W44 G1's bed loader (`results/2026-10-03-w44-g1-refit/cuts/bed.py`), ported for W45
(charter clause 2, X58); W44's committed copies are untouched.

What the port changes, and nothing else:
  - **The shared inputs are read by path and pinned.** The referee manifest and its planner, the
    bar, W44 G1's `t1.py` and `readings.py` (which W45's cuts import from W44 G1's directory) and
    W44 G0's `port/interior.py` (which `readings.py` reads images through)
    stay where W44 committed them — X49's one manifest stays one file — and each must hash to
    `SHARED_PINS` below, checked at import: a moved shared input stops every W45 tool before it
    reads a row. `G0` still names W44 G0's directory because `t1.py` reads the bar through it.
  - **W44's renders are not a W45 bed (X58).** A matrix under W44's scratch (`~/vitrea-w44`) or a
    W44 evidence directory, and a candidate document a W44 directory holds, refuse: W45 reads W44's
    committed CUTS (the rehearsal's complete maps) and never re-cuts W44's beds as its own.

W44 G1's text follows, unchanged.

W44 G1: G0's bed loader (`results/2026-10-03-w44-g0-declaration/cuts/bed.py`), copied; G0's
committed copy, which part 1 pins, is untouched. The one change is where it finds G0's
evidence: the referee manifest and its planner, the bar and the port stay in G0's directory
(`G0` below) and are read from there, never copied, so X49's one manifest stays one file.

G0's text follows, unchanged.

W44 G0 (a), (d): W43 G3 (i)'s bed loader, copied and extended (W43's committed copy is untouched).

What W44 G0 adds, each executing a clause of charter 2026-10-03-w44-texture-at-0-25.md:
  - **The referee manifest's fit and gate consumers (X49; Design "The referees").** `load()`
    refuses a row of any cell `referees/referees.json` holds out, for a candidate bed (the fit
    loader's refusal) and for a sealed stage bed read before the exposure (the gate's absence
    check). Only a sealed bed read `with_holdout`, which is the exposure, admits one. W43's
    pre-fit render (the `prefit` kind) predates the manifest and carries every probe row; its
    referee rows are DROPPED, counted in `refereeRowsDropped`, and never read: W44 reads that
    render only in G0's rehearsal, and its references are the published c05 rows (X52).
  - **Published generations (clause 2's rehearsal; X52's reference render).** `load_published`
    reads one immutable generation file named by its active document hash (``6d18c059eb42``, the
    published c05 light generation; ``85ad7f7e3e0d``, the 0.5 light one; and their dark twins),
    checks the file against `generations/index.json` and every row against the documents the
    index names, and admits every set: these rows are already-published evidence, holdout and
    referees included, and reading their recorded numbers renders nothing.

The W43 text follows, unchanged.

W43 G3 (i): where the 0.25 cuts take their rows from, and what they admit (clause 10, step 1).

W42's referees (``results/2026-09-29-w42-g0-declaration/gate/referees``) read a W40 stage and admit
a candidate as a scratch PROFILE DOCUMENT named in each row's ``materialProfile=`` clause. W43 G0 (f)
replaced that route: a candidate is now a complete DECLARATION drawn in candidate mode, which
``compare`` refuses into a stage, and the pre-fit render is the shipped 0.5 material read under
``--cross-position``, which is refused into a stage too. Both therefore live in ordinary scratch
matrices (``--out-matrix``), and this module is the candidate-admission mode re-instantiated for
them. It admits exactly two kinds of bed, and every output names which:

  prefit     the shipped 0.5 documents drawn on the 0.25 cells: every row stamped
             ``crossPosition=shipped-glass0.5-against-glass0.25`` and naming, as its
             ``materialProfile=`` and ``recededProfile=`` clauses, its scheme's two shipped 0.5
             documents under ``packages/calibration/profiles/`` at their live hash. This is the
             unmoved endpoint, and L1's growth baseline and M2's and E2's reference
             (Decision Log 5 (b), RULED 2026-10-02).
  candidate  one declared candidate document (``--candidate-document PATH[=SHA12]``): every row
             names it as ``materialProfile=candidate candidateDocument=<PATH> declarationSha256=<SHA12>``
             with no cross-position stamp, and the declaration's four endpoint files still hash to
             what it declares. A candidate whose bytes moved after its render refuses.

Refused for both: a row of any profile other than the four ``-glass0.25`` standard keys; a holdout
row, by its label or by the declaration's split (the holdout is never read in this child); a row
of a scene its profile does not declare, or whose ``fixtureSet`` or ``state`` disagrees with
``scenes.json`` (so a cut's population drawn from ``scenes.json`` selects exactly the rows a rule
on the rows' own fields would); two rows for one (profile, tier, scene). Rows keep their raw
bytes; nothing here writes a matrix.

A bed may be PARTIAL: the render drivers write with ``--write-partial``, so a scene, or a whole
(profile, tier) pair, can have no row. ``Bed.missing`` names, for every pair of the four profiles
on both tiers (a pair with no row at all included), the declared non-holdout scenes with no row.
The cuts do not read their populations off the bed: each draws its own from ``scenes.json`` and
reports a declared member with no row as UNMEASURED.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
CAL = EVIDENCE.parents[1]
ROOT = CAL.parent.parent
RESULTS = CAL / "results"
G0 = RESULTS / "2026-10-03-w44-g0-declaration"
W44_G1 = RESULTS / "2026-10-03-w44-g1-refit"
SCENES_PATH = ROOT / "apps/reference-apple/scenes.json"

# The shared, immutable inputs (charter clause 2, X58), by path and pinned byte for byte.
SHARED_PINS = {
    G0 / "referees" / "referees.json": "b1132bd0f01f318b07e1722da3fefaba6eac96679b56efbe2b451ef13bf1b60b",
    G0 / "referees" / "plan.py": "f8ca80bb2153e12b7a3a4edc18b440e8f2c89a75bf0adef30e795c40c8dda8c7",
    G0 / "bar" / "t1-bar.json": "1c3e63ad086b59cc959be67e220ceeb4b6f3d42529d295960f84d7d8fbf0932f",
    W44_G1 / "cuts" / "t1.py": "55f0a96e27b03325d4345f0f541b0b5996c7cd580573bd3e7aeb4c35835355fc",
    W44_G1 / "cuts" / "readings.py": "d4063705869df3933e27a0f329084e4280a472aab2103bb9873b08c5c93d1b5f",
    # readings.py reads its images and silhouettes through W44 G0's proven port.
    G0 / "port" / "interior.py": "8c5193b550b2cd627c88380b41227d6656d4fc04214f336ae8a3bcb7ee0fdd98",
}
for _path, _want in SHARED_PINS.items():
    _got = hashlib.sha256(_path.read_bytes()).hexdigest()
    if _got != _want:
        raise SystemExit(f"W45 bed: the shared input {_path.relative_to(ROOT)} hashes to {_got[:12]}, "
                         f"not its pinned {_want[:12]} (X58)")

# X58: W44's evidence and scratch are never a W45 bed.
W44_PLACES = re.compile(r"(^|/)(2026-10-03-w44-[^/]*|vitrea-w44)(/|$)")


def refuse_w44(path, what: str) -> None:
    if W44_PLACES.search(str(Path(path).resolve())):
        raise SystemExit(f"{what} {path}: W44's evidence or scratch; W45 reads W44's committed cuts, "
                         "never W44's beds as its own (X58)")
sys.path.insert(0, str(RESULTS / "2026-09-26-w40-g0-generations"))
import matrix_store  # noqa: E402
sys.path.insert(0, str(G0 / "referees"))
import plan as referee_plan  # noqa: E402

PROFILES = (
    "apple-macos-27.0-1x-light-standard-glass0.25",
    "apple-macos-27.0-2x-light-standard-glass0.25",
    "apple-macos-27.0-1x-dark-standard-glass0.25",
    "apple-macos-27.0-2x-dark-standard-glass0.25",
)
NON_HOLDOUT = ("calibration", "validation", "recorded", "probe")
TIERS = {"webgpu": "texture", "css": "dom"}
CROSS_STAMP = "crossPosition=shipped-glass0.5-against-glass0.25"
DOC_CLAUSE = re.compile(r"(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})")
CANDIDATE_CLAUSE = re.compile(
    r"materialProfile=candidate candidateDocument=(\S+) declarationSha256=([0-9a-f]{12})")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scheme_of(profile: str) -> str:
    return "dark" if "-dark-" in profile else "light"


def scale_of(profile: str) -> int:
    return 2 if "-2x-" in profile else 1


def counterpart_05(profile: str) -> str:
    """The 0.5 key a 0.25 key's scene list was copied from (scenes.json version 8)."""
    if not profile.endswith("-glass0.25"):
        raise ValueError(f"{profile} is not a -glass0.25 key")
    return profile[: -len("-glass0.25")] + "-glass0.5"


class Scenes:
    def __init__(self) -> None:
        self.raw = SCENES_PATH.read_bytes()
        self.spec = json.loads(self.raw)
        self.by_id = {s["id"]: s for s in self.spec["scenes"]}
        self.role = {sid: role for role in ("calibration", "validation", "holdout", "recorded",
                                             "probe") for sid in self.spec["split"].get(role, [])}
        self.holdout = frozenset(self.spec["split"]["holdout"])
        self.components = self.spec["components"]
        self.canvas = self.spec["canvas"]

    def declared(self, profile: str) -> list[str]:
        entry = next(p for p in self.spec["profiles"] if p["key"] == profile)
        return list(self.by_id) if entry["scenes"] == "all" else list(entry["scenes"])

    def component(self, sid: str) -> dict:
        return self.components[self.by_id[sid]["component"]]

    def span(self, sid: str) -> float | None:
        c = self.component(sid)
        if c["kind"] in ("capsule", "rrect"):
            return min(c["size"])
        if c["kind"] == "stack":
            return min(c["base"]["size"])
        if c["kind"] == "group":
            return min(min(i["size"]) for i in c["items"])
        return None

    def inactive(self, sid: str) -> bool:
        return self.by_id[sid]["state"] == "inactive"


SCENES = Scenes()


def shipped_05() -> dict[str, str]:
    """The four shipped macOS 27 0.5 standard documents, path as rows name them -> live sha12."""
    out = {}
    for scheme in ("light", "dark"):
        for suffix in ("", "-receded"):
            rel = f"packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.5{suffix}.json"
            out[rel] = sha256(ROOT / rel)[:12]
    return out


@dataclass
class Candidate:
    path: str          # as rows name it (repo-relative)
    sha256: str
    declaration: dict
    endpoints: dict    # slot -> (absolute path, sha256)

    @classmethod
    def read(cls, spec: str) -> "Candidate":
        given, want = spec, None
        head, sep, tail = spec.rpartition("=")
        if sep and re.fullmatch(r"[0-9a-f]{12}", tail):
            given, want = head, tail
        file = (ROOT / given) if not Path(given).is_absolute() else Path(given)
        file = file.resolve()
        refuse_w44(file, "--candidate-document")
        rel = str(file.relative_to(ROOT))
        if rel.startswith("packages/calibration/profiles/"):
            raise SystemExit(f"--candidate-document {rel}: a shipped document is read in strict mode")
        digest = sha256(file)
        if want is not None and digest[:12] != want:
            raise SystemExit(f"--candidate-document {rel}: hashes to {digest[:12]}, not the "
                             f"declared {want}")
        declaration = json.loads(file.read_text())
        if declaration.get("kind") != "vitrea-candidate-material-document":
            raise SystemExit(f"--candidate-document {rel}: not a candidate declaration")
        if declaration.get("glassTintAmount") != 0.25:
            raise SystemExit(f"--candidate-document {rel}: declares glass "
                             f"{declaration.get('glassTintAmount')}, and these cuts are the 0.25 cuts")
        endpoints = {}
        for slot, entry in declaration["endpoints"].items():
            path = (file.parent / entry["path"]).resolve()
            actual = sha256(path)
            if actual != entry["sha256"]:
                raise SystemExit(f"--candidate-document {rel}: {slot} declares {entry['sha256'][:12]}, "
                                 f"and {path} hashes to {actual[:12]}")
            endpoints[slot] = (str(path), actual)
        return cls(rel, digest, declaration, endpoints)


@dataclass
class Bed:
    kind: str                 # "prefit" | "candidate" | "sealed" | "published:<active>"
    rows: list
    matrices: list            # [{"path", "sha256", "rows"}]
    candidate: Candidate | None = None
    missing: dict = field(default_factory=dict)   # every (profile, tier) -> [scene ids, no row]
    refereeRowsDropped: int = 0                   # W44: a prefit bed's referee rows, never read

    def described(self) -> dict:
        out = dict(kind=self.kind, matrices=self.matrices, refereeRowsDropped=self.refereeRowsDropped,
                   rows=len(self.rows),
                   pairs={f"{p} {t}": n for (p, t), n in sorted(self.pair_counts().items())},
                   missingNonHoldout={f"{p} {t}": s for (p, t), s in sorted(self.missing.items()) if s})
        if self.candidate is not None:
            out["candidateDocument"] = dict(
                path=self.candidate.path, sha256=self.candidate.sha256,
                name=self.candidate.declaration.get("name"),
                endpoints={slot: dict(path=str(Path(p).relative_to(ROOT)), sha256=s)
                           for slot, (p, s) in sorted(self.candidate.endpoints.items())})
        elif self.kind == "sealed":
            out["documents"] = sealed_025()
        elif self.kind.startswith("published:"):
            out["documents"] = self.matrices[0]["documents"]
        else:
            out["documents"] = shipped_05()
            out["stamp"] = CROSS_STAMP
        return out

    def pair_counts(self) -> dict:
        counts: dict = {}
        for r in self.rows:
            pair = (r["key"]["profileKey"], r["key"]["web"]["renderer"])
            counts[pair] = counts.get(pair, 0) + 1
        return counts

    def by_key(self, renderer: str | None = None) -> dict:
        return {(r["key"]["profileKey"], r["key"]["sceneId"]): r for r in self.rows
                if renderer is None or r["key"]["web"]["renderer"] == renderer}

    @property
    def label(self) -> str:
        if self.kind == "prefit":
            return "prefit: shipped 0.5 documents on the 0.25 cells (" + CROSS_STAMP + ")"
        if self.kind == "sealed":
            return "sealed: the four -glass0.25 documents under profiles/, strict shipped mode (a stage read)"
        if self.kind.startswith("published:"):
            return f"published generation {self.kind.split(':', 1)[1]} (recorded rows; renders nothing)"
        return f"candidate: {self.candidate.path} sha256:{self.candidate.sha256[:12]}"


def _admit_prefit(row: dict, shipped: dict) -> str | None:
    path = row["key"]["web"]["capturePath"]
    if CROSS_STAMP not in path:
        return "no cross-position stamp"
    named = {kind: (p, s) for kind, p, s in DOC_CLAUSE.findall(path)}
    scheme = scheme_of(row["key"]["profileKey"])
    want = {
        "materialProfile": f"packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.5.json",
        "recededProfile": f"packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.5-receded.json",
    }
    for kind, rel in want.items():
        if named.get(kind) != (rel, shipped[rel]):
            return f"{kind} is {named.get(kind)}, not {rel} at {shipped[rel]}"
    return None


def sealed_025() -> dict[str, str]:
    """The four sealed -glass0.25 documents, path as rows name it -> live sha12 (W43 G3 (ii))."""
    out = {}
    for scheme in ("light", "dark"):
        for suffix in ("", "-receded"):
            rel = f"packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.25{suffix}.json"
            out[rel] = sha256(ROOT / rel)[:12]
    return out


def _admit_sealed(row: dict, sealed: dict) -> str | None:
    """A stage row: strict shipped mode at the (macOS 27.0, glass 0.25) pair, naming the scheme's
    two sealed documents at their live hash, with no cross-position stamp and no candidate."""
    path = row["key"]["web"]["capturePath"]
    if "crossPosition=" in path:
        return "a stage row carries a cross-position stamp"
    if CANDIDATE_CLAUSE.search(path):
        return "a stage row names a candidate"
    named = {kind: (p, s) for kind, p, s in DOC_CLAUSE.findall(path)}
    scheme = scheme_of(row["key"]["profileKey"])
    for kind, suffix in (("materialProfile", ""), ("recededProfile", "-receded")):
        rel = f"packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.25{suffix}.json"
        if named.get(kind) != (rel, sealed[rel]):
            return f"{kind} is {named.get(kind)}, not {rel} at {sealed[rel]}"
    return None


def _admit_candidate(row: dict, candidate: Candidate) -> str | None:
    path = row["key"]["web"]["capturePath"]
    if "crossPosition=" in path:
        return "a candidate row carries a cross-position stamp"
    match = CANDIDATE_CLAUSE.search(path)
    if match is None:
        return "names no candidate document"
    if match.group(1) != candidate.path or match.group(2) != candidate.sha256[:12]:
        return (f"names {match.group(1)} sha256:{match.group(2)}, not {candidate.path} "
                f"sha256:{candidate.sha256[:12]}")
    if DOC_CLAUSE.search(path):
        return "names a profile document beside the candidate"
    return None


def load(matrices: list[str], kind: str, candidate: str | None = None,
         with_holdout: bool = False) -> Bed:
    """`with_holdout` admits holdout rows, for a SEALED bed only: the stage's one holdout read
    (charter clause 10 step 6). Every cut's population is declared without the holdout except the
    tables', so only the holdout reader asks for it.

    W44 (X49): a row of a referee cell is refused unless this is that one read (a sealed bed
    `with_holdout`, which W44 calls the exposure); a fit bed carrying one is never admitted."""
    if kind not in ("prefit", "candidate", "sealed"):
        raise SystemExit(f"bed kind {kind!r}")
    if with_holdout and kind != "sealed":
        raise SystemExit("only a sealed stage bed reads the holdout, once, after its gate")
    if (kind == "candidate") != (candidate is not None):
        raise SystemExit("a candidate bed names exactly one --candidate-document; a prefit bed none")
    declared = Candidate.read(candidate) if candidate is not None else None
    shipped = shipped_05()
    sealed = sealed_025() if kind == "sealed" else {}
    lists = {profile: set(SCENES.declared(profile)) for profile in PROFILES}
    manifest = referee_plan.load_manifest()
    held = referee_plan.referee_cells(manifest)
    rows, record, seen, dropped = [], [], set(), 0
    for given in matrices:
        file = Path(given).resolve()
        refuse_w44(file, "--bed")
        raw = file.read_bytes()
        matrix = json.loads(raw)
        if matrix.get("schemaVersion") != 5:
            raise SystemExit(f"{file}: not a schema-5 matrix")
        count = 0
        for row in matrix["cells"]:
            profile, sid = row["key"]["profileKey"], row["key"]["sceneId"]
            renderer = row["key"]["web"]["renderer"]
            where = f"{file.name}: {profile} {renderer} {sid}"
            if profile not in PROFILES:
                raise SystemExit(f"{where}: not one of the four -glass0.25 standard profiles")
            if (profile, sid) in held and kind == "prefit":
                # W43's pre-fit render predates the manifest and carries every probe row; W44
                # reads it only in G0's rehearsal, and never its referee rows (X49).
                dropped += 1
                continue
            if (profile, sid) in held and not with_holdout:
                raise SystemExit(f"{where}: a referee cell (referees.json sha256 "
                                 f"{manifest['sha256'][:12]}); a {kind} bed never carries one, and a "
                                 "stage carries one only at the exposure (W44 X49)")
            if (row.get("fixtureSet") == "holdout" or sid in SCENES.holdout) and not with_holdout:
                raise SystemExit(f"{where}: a holdout row; the holdout is read only by the stage's "
                                 "one holdout reader")
            if row.get("fixtureSet") not in NON_HOLDOUT + (("holdout",) if with_holdout else ()):
                raise SystemExit(f"{where}: fixtureSet {row.get('fixtureSet')!r}")
            if sid not in lists[profile]:
                raise SystemExit(f"{where}: a scene scenes.json does not declare for this profile")
            role, state = SCENES.role[sid], SCENES.by_id[sid]["state"]
            if (row["fixtureSet"], row.get("state")) != (role, state):
                raise SystemExit(f"{where}: fixtureSet/state {row['fixtureSet']}/{row.get('state')}"
                                 f" where scenes.json declares {role}/{state}")
            why = (_admit_prefit(row, shipped) if kind == "prefit"
                   else _admit_sealed(row, sealed) if kind == "sealed"
                   else _admit_candidate(row, declared))
            if why is not None:
                raise SystemExit(f"{where}: not admitted as a {kind} row: {why}")
            ident = (profile, renderer, sid)
            if ident in seen:
                raise SystemExit(f"{where}: two rows for one (profile, tier, scene)")
            seen.add(ident)
            rows.append(row)
            count += 1
        record.append(dict(path=str(file), sha256=hashlib.sha256(raw).hexdigest(), rows=count))
    rows.sort(key=matrix_store.key)
    bed = Bed(kind, rows, record, declared, refereeRowsDropped=dropped)
    for profile in PROFILES:
        for renderer in TIERS:
            have = {r["key"]["sceneId"] for r in rows if r["key"]["profileKey"] == profile
                    and r["key"]["web"]["renderer"] == renderer}
            bed.missing[(profile, renderer)] = sorted(
                sid for sid in SCENES.declared(profile)
                if SCENES.role[sid] in NON_HOLDOUT and sid not in have)
    return bed


GENERATIONS = RESULTS / "generations"
STANDARD = re.compile(r"^apple-macos-27\.0-[12]x-(light|dark)-standard-glass0\.(25|5)$")


def load_published(active: str) -> Bed:
    """One published generation, by its ACTIVE document's twelve-hex hash (W44 G0; X52).

    The file is `generations/<active>.json` exactly as `index.json` records it (file SHA-256,
    current status not required: a retired generation is still its own evidence), read through
    W40's `matrix_store`. Every row must be a macOS 27 STANDARD profile's (the accessibility rows
    a 0.5 generation also carries are left out by name, not silently) and must name, as its
    `materialProfile=` / `recededProfile=` clauses, exactly the documents the index names for
    the file. Every set is admitted, holdout and referees included: a published row is recorded
    evidence, and this reads its numbers and renders nothing. The bed's `kind` is
    ``published:<active>``."""
    index = json.loads((GENERATIONS / "index.json").read_bytes())
    name = f"{active}.json"
    entry = index["files"].get(name)
    if entry is None:
        raise SystemExit(f"published: generations/index.json has no file {name}")
    raw = (GENERATIONS / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
        raise SystemExit(f"published: {name} does not hash to its index entry")
    documents = {d["path"]: d["sha256"] for d in entry["documents"]}
    rows, skipped = [], {}
    for row in matrix_store.load_generation(active):
        profile = row["key"]["profileKey"]
        if not STANDARD.match(profile):
            skipped[profile] = skipped.get(profile, 0) + 1
            continue
        named = {p: h for _, p, h in DOC_CLAUSE.findall(row["key"]["web"]["capturePath"])}
        if named != documents:
            raise SystemExit(f"published {name}: {profile} {row['key']['sceneId']} names {named}, "
                             f"not the index's {documents}")
        rows.append(row)
    rows.sort(key=matrix_store.key)
    bed = Bed(f"published:{active}", rows,
              [dict(path=str((GENERATIONS / name).relative_to(ROOT)), sha256=entry["sha256"],
                    rows=len(rows), skippedNonStandard=skipped, documents=documents)])
    return bed


def current_05_rows() -> dict:
    """The current 0.5 generation's rows of the four standard profiles, keyed by
    (0.5 profile, renderer, scene). X41 freezes these bytes."""
    out = {}
    for profile in PROFILES:
        ref = counterpart_05(profile)
        for row in matrix_store.load_current_profile(ref):
            out[(ref, row["key"]["web"]["renderer"], row["key"]["sceneId"])] = row
    return out


def value(row: dict | None, axis: str, metric: str):
    if row is None:
        return None
    entry = (row.get(axis) or {}).get(metric)
    return entry["value"] if isinstance(entry, dict) else None
