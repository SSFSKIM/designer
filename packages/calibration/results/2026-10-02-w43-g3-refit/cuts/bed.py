"""W43 G3 (i): where the 0.25 cuts take their rows from, and what they admit (clause 10, step 1).

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
row, by its label or by the declaration's split (the holdout is never read in this child); two rows
for one (profile, tier, scene). Rows keep their raw bytes; nothing here writes a matrix.
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
SCENES_PATH = ROOT / "apps/reference-apple/scenes.json"
sys.path.insert(0, str(RESULTS / "2026-09-26-w40-g0-generations"))
import matrix_store  # noqa: E402

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
    kind: str                 # "prefit" | "candidate"
    rows: list
    matrices: list            # [{"path", "sha256", "rows"}]
    candidate: Candidate | None = None
    missing: dict = field(default_factory=dict)   # (profile, tier) -> [scene ids]

    def described(self) -> dict:
        out = dict(kind=self.kind, matrices=self.matrices,
                   rows=len(self.rows),
                   pairs={f"{p} {t}": n for (p, t), n in sorted(self.pair_counts().items())},
                   missingNonHoldout={f"{p} {t}": s for (p, t), s in sorted(self.missing.items()) if s})
        if self.candidate is not None:
            out["candidateDocument"] = dict(
                path=self.candidate.path, sha256=self.candidate.sha256,
                name=self.candidate.declaration.get("name"),
                endpoints={slot: dict(path=str(Path(p).relative_to(ROOT)), sha256=s)
                           for slot, (p, s) in sorted(self.candidate.endpoints.items())})
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


def load(matrices: list[str], kind: str, candidate: str | None = None) -> Bed:
    if kind not in ("prefit", "candidate"):
        raise SystemExit(f"bed kind {kind!r}")
    if (kind == "candidate") != (candidate is not None):
        raise SystemExit("a candidate bed names exactly one --candidate-document; a prefit bed none")
    declared = Candidate.read(candidate) if candidate is not None else None
    shipped = shipped_05()
    rows, record, seen = [], [], set()
    for given in matrices:
        file = Path(given).resolve()
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
            if row.get("fixtureSet") == "holdout" or sid in SCENES.holdout:
                raise SystemExit(f"{where}: a holdout row; the holdout is never read in G3 (i)")
            if row.get("fixtureSet") not in NON_HOLDOUT:
                raise SystemExit(f"{where}: fixtureSet {row.get('fixtureSet')!r}")
            why = (_admit_prefit(row, shipped) if kind == "prefit"
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
    bed = Bed(kind, rows, record, declared)
    for (profile, renderer) in bed.pair_counts():
        have = {r["key"]["sceneId"] for r in rows
                if r["key"]["profileKey"] == profile and r["key"]["web"]["renderer"] == renderer}
        bed.missing[(profile, renderer)] = sorted(
            sid for sid in SCENES.declared(profile)
            if SCENES.role[sid] in NON_HOLDOUT and sid not in have)
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
