"""W47 G0 (c): W46 G0's bed loader (`results/2026-10-05-w46-g0-declaration/cuts/bed.py`), ported by copy
for W47 (charter clause 2; X60, X62, X69); W46's committed copy is untouched and never imported.

What the port changes, and nothing else:
  - **W47's bindings** (`../bindings.py`): W47's charter pin, evidence root, scratch and stages; W44's,
    W45's and W46's evidence directories and scratch refused as a bed (`refuse_other_wave`).
  - **The referee manifest is W46's, loaded by hash (X69).** `referee_plan` is W47's loader
    (`referees/referees.py`, `bindings.referees()`): `w46-referees-1` at its pinned SHA-256, the
    derivation pinned against W46's frozen ladder list only, W47's membership and disjointness checks.
    The withheld dark cells are unchanged: W46's six referee scenes and the seven holdout scenes per
    dark scale.
  - Every other clause (the light withheld cells refused for good; the sealed bed's X60 check; a
    candidate never naming a live document) is W46's, unchanged, with the reference generations
    `d0219cd684bf` (dark) and `ebc3d9105a4a` (light).

W46 G0's text follows, unchanged; where it says W46 it is W47.

W46 G0 (a): W45 G0's bed loader (`results/2026-10-03-w45-g0-operator/cuts/bed.py`), ported for W46
(charter clause 1; X60, X62); W45's and W44's committed copies are untouched and never imported.

What the port changes, and nothing else:
  - **W46's bindings** (`../bindings.py`). The shared inputs (the bar, W44 G1's `t1.py` and
    `readings.py`, W44 G0's interior port, W40's `matrix_store`) are pinned there and checked at
    import. `G0` STILL names W44 G0's directory, because the shared `t1.py` reads the bar through
    `bed.G0`; W46's own evidence root is `EVIDENCE`.
  - **W46's referee manifest.** The withheld dark cells are `referees/referees.json` read through
    W46's planner adapter (schema `w46-referees-1`, the two dark 0.25 profiles), not W44's.
  - **The light withheld cells are refused for good.** On the light 0.25 profiles the 20 canonical
    holdout scenes and W44's six referee scenes per scale are spent at the current light bytes (read
    7) and never re-rendered (Design "The populations per phase"; X60). A light row of either is
    refused by every bed, `with_holdout` included: W46's exposure is the DARK one. W44's manifest is
    read as data (its file pinned in `bindings.SHARED`); its planner is not imported.
  - **W44's and W45's renders are not a W46 bed.** A matrix or candidate under either wave's
    evidence directory or scratch refuses (`refuse_other_wave`). Their committed CUTS are read as
    rehearsal inputs where the charter names them; their beds never are.
  - **The sealed bed (X60).** A W46 stage row names its scheme's two live `-glass0.25` documents at
    their live hash. For the LIGHT scheme those live bytes must be the light snapshots' (the light
    material never moves, X60); a light row naming any other bytes refuses.
  - **A candidate never names a live profile document as an endpoint** (X62).

W45 G0's text follows, unchanged; where it says W45 it is W46, where it says c05 the reference
generations are `d0219cd684bf` (dark) and `ebc3d9105a4a` (light).

W45 G0 (b): W44 G1's bed loader (`results/2026-10-03-w44-g1-refit/cuts/bed.py`), ported for W45
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

The W44 and W43 texts are in W45's copy and are not repeated here; what they establish holds:
`load()` refuses a referee row for any bed but a sealed one read `with_holdout` (the exposure), and
a holdout row likewise; a `prefit` bed (W43's cross-position render of the shipped 0.5 documents on
the 0.25 cells) drops its referee rows unread; `load_published` reads one immutable generation by
its active document hash, checked against `generations/index.json`, every set admitted (recorded
rows render nothing). A bed may be PARTIAL (`--write-partial`): `Bed.missing` names every declared
non-holdout scene with no row, per (profile, tier), and the cuts draw their populations from
`scenes.json`, never from the bed.
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
sys.path.insert(0, str(EVIDENCE))
import bindings as W  # noqa: E402

CAL = W.CAL
ROOT = W.ROOT
RESULTS = W.RESULTS
G0 = W.W44_G0            # the shared t1.py reads the bar through `bed.G0` (W44 G0's directory)
W44_G1 = W.W44_G1
SCENES_PATH = ROOT / "apps/reference-apple/scenes.json"

W.require_shared()


def refuse_other_wave(path, what: str) -> None:
    W.refuse_other_wave_path(path, what)


sys.path.insert(0, str(W.MATRIX_STORE.parent))
import matrix_store  # noqa: E402

referee_plan = W.referees()      # W47's loader under X69: w46-referees-1 by hash

PROFILES = W.DARK_025 + W.LIGHT_025
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


def light_withheld() -> set[tuple[str, str]]:
    """The light 0.25 cells spent at the current light bytes: the canonical holdout and W44's six
    referee scenes on each light profile (read 7). No W46 (or W47) bed carries one, ever (X60)."""
    w44 = json.loads((W.W44_G0 / "referees/referees.json").read_bytes())
    out = {(p, s) for p in w44["profiles"] for s in w44["scenes"]}
    out |= {(p, s) for p in W.LIGHT_025 for s in SCENES.declared(p) if SCENES.role[s] == "holdout"}
    return out


LIGHT_WITHHELD = frozenset(light_withheld())


def shipped_05() -> dict[str, str]:
    """The four shipped macOS 27 0.5 standard documents, path as rows name them -> live sha12,
    each checked at its X41-frozen hash."""
    out = {}
    for scheme in ("light", "dark"):
        for suffix in ("", "-receded"):
            key = f"apple-macos-27.0-1x-{scheme}-standard-glass0.5{suffix}"
            path = W.twin_path(key)
            out[str(path.relative_to(ROOT))] = sha256(path)[:12]
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
        refuse_other_wave(file, "--candidate-document")
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
            W.refuse_live_profile(path, f"--candidate-document {rel}: {slot}")
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
    refereeRowsDropped: int = 0                   # a prefit bed's withheld rows, never read

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
            return "sealed: the -glass0.25 documents under profiles/, strict shipped mode (a stage read)"
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
    """The four live -glass0.25 documents, path as rows name it -> live sha12."""
    out = {}
    for scheme in ("light", "dark"):
        for suffix in ("", "-receded"):
            rel = f"packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.25{suffix}.json"
            out[rel] = sha256(ROOT / rel)[:12]
    return out


def _admit_sealed(row: dict, sealed: dict) -> str | None:
    """A stage row: strict shipped mode at the (macOS 27.0, glass 0.25) pair, naming the scheme's
    two live documents at their live hash, with no cross-position stamp and no candidate; a light
    row's documents must be the light snapshots' bytes (X60)."""
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
        if scheme == "light":
            slot = f"{'active' if suffix == '' else 'receded'}.light"
            if sealed[rel] != W.DOCUMENT_SHA[slot][:12]:
                return f"{rel} is {sealed[rel]}, not the light snapshot {W.DOCUMENT_SHA[slot][:12]} (X60)"
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
    """`with_holdout` admits the DARK holdout and referee rows, for a SEALED bed only: the stage's
    one exposure (clause 7). A light withheld row is refused by every bed (X60)."""
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
        refuse_other_wave(file, "--bed")
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
            if kind == "prefit" and ((profile, sid) in held or (profile, sid) in LIGHT_WITHHELD):
                # W43's pre-fit render predates both manifests and carries every probe row; W46 (and W47)
                # reads it only in G0's rehearsal, and never its withheld rows.
                dropped += 1
                continue
            if (profile, sid) in LIGHT_WITHHELD:
                raise SystemExit(f"{where}: a light holdout or W44 referee cell, spent at the current light "
                                 "bytes (read 7) and never re-read (X60)")
            if (profile, sid) in held and not with_holdout:
                raise SystemExit(f"{where}: a referee cell (referees.json sha256 "
                                 f"{manifest['sha256'][:12]}); a {kind} bed never carries one, and a "
                                 "stage carries one only at the exposure (W47 clause 4, X69)")
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
    """One published generation, by its ACTIVE document's twelve-hex hash (W44 G0; X52), checked
    against `generations/index.json`; every set admitted (recorded rows render nothing)."""
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
    return Bed(f"published:{active}", rows,
               [dict(path=str((GENERATIONS / name).relative_to(ROOT)), sha256=entry["sha256"],
                     rows=len(rows), skippedNonStandard=skipped, documents=documents)])


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
