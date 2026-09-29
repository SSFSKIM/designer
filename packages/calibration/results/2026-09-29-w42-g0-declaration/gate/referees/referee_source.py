"""W41 G2 — where the referee cuts read their rows, references and captures from (c9a §5.193).

W36's cut scripts read `results/matrix.json` as the working file and `results/superseded/`
by hand. Since W40 (§5.189–§5.190) that pathname holds only the frozen macOS 26.5 rows and
the current macOS 27 rows are a union selected by `results/generations/index.json`. This
module is the one place the ported scripts take rows from, through W40's Python adapter:

  (default)    the CURRENT UNION, `matrix_store.load_current_rows` with the canonical matrix
               path passed explicitly, so a `VITREA_MATRIX_PATH` left in the environment cannot
               turn a canonical cut into a scratch one;
  --stage DIR  a SCRATCH UNION: the current union with every (profile, tier) pair the stage
               HAS rows for replaced by those rows. A pair the stage declared but holds no row
               for keeps its current rows, and the output says so: a stage the landing filled
               only in part (W41 G2's read, X6-refused on the accessibility profiles and the
               CSS tier, holds only the two light standard profiles' WebGPU rows) is still a
               readable referee for every cut that reads those rows. Once a stage holds every
               declared pair this is the union `matrix publish DIR` would leave; rows keep their
               raw bytes, so its legacy-envelope digest is the one the published union carries.

References are generations named by their (active, receded) document pair and resolved by
`matrix_store.load_generation`, which refuses an ambiguous alias; no file is named by hand.

Captures: a cut that opens web PNGs takes one or more `--captures` roots. Each cell is read
from the root whose `cell__webgpu.json` names the row's exact `capturePath` — both document
hashes included — so a stage read written to its own tree and the canonical tree holding the
unchanged scheme can be read together, and a capture of another generation is refused
rather than read.

W42 G0 (charter clause 10; Design, "The instrument (G0)"): the candidate-admission mode.
W41's guards admitted a row only at a document that is the file on disk, and a candidate is
rendered with a scratch document at its own repo-relative path, so every referee refused or
dropped it. Two arguments, shared by every script through `load`:

  --candidate PATH[=SHA12]  (repeatable) a scratch material-profile document, named as the rows
               name it (repo-relative; an absolute path is shown repo-relative as capture-web
               shows it). Its SHA-256 is taken from its bytes; a given SHA12 that differs
               refuses, and a PATH under packages/calibration/profiles/ is the shipped file,
               not a candidate. A row is ADMITTED at (path, sha12) when path is a shipped
               document at its live hash or a declared candidate at its hash; every guard reads
               `Source.admitted`, and a declared PATH at any other hash still refuses. A
               candidate is read only through a stage that declares it, so a candidate no
               stage names refuses. Outputs are stamped: JSON gains `admission` and its
               `atDocuments` reads `candidate`; stdout's first line is `# CANDIDATE`. With no
               --candidate nothing is stamped and every output keeps the verbatim port's bytes.
  --stage DIR  now repeatable: a W40 stage holds one active/receded pair, so a candidate that
               covers both schemes is two stages. Each is validated on its own, their replaced
               (profile, tier) pairs must not overlap, the union replaces all of them, and a
               read of more than one stage records every stage's status under `stages`.

The shipped set is `packages/calibration/profiles/*.json` at its live hash, the owner test's
own `SHIPPED_DOCUMENT_HASHES`. W41's `_stage` (and black-cut's and e2-regression's per-row
checks) asked only whether the named path's file hashes to the named digest, which a scratch
document at its own path satisfies; here a document outside that directory is admitted only
by declaration.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[3]
ROOT = CAL.parent.parent
RESULTS = CAL / "results"
sys.path.insert(0, str(RESULTS / "2026-09-26-w40-g0-generations"))
import matrix_store as store  # noqa: E402

CANONICAL_CAPTURES = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
HOLDOUT = "holdout"
SHIPPED = "packages/calibration/profiles/"


@dataclass
class Source:
    rows: list
    label: str
    stage: dict | None
    admitted: dict
    candidates: tuple = ()

    @property
    def described(self):
        """What an output records about its rows: the label, and in stage mode every pair."""
        return self.label if self.stage is None else dict(label=self.label, **self.stage)

    @property
    def stamp(self) -> dict:
        """What a JSON output gains in candidate mode, placed after its `source`; base: nothing."""
        if not self.candidates:
            return {}
        return {"admission": dict(mode="candidate", documents=[
            dict(path=path, sha256=sha, sha12=sha[:12]) for path, sha in self.candidates])}

    @property
    def at_documents(self) -> str:
        return "candidate" if self.candidates else "shipped"

    def banner(self) -> None:
        """Candidate mode: the first line of stdout. Base mode prints nothing."""
        if self.candidates:
            print("# CANDIDATE admission: rows admitted at the shipped documents and at "
                  + ", ".join(f"{path} sha256:{sha[:12]}" for path, sha in self.candidates)
                  + " (declared scratch documents; not a shipped cut)")

    @property
    def legacy_sha256(self) -> str:
        """The whole-matrix witness: the legacy schema-5 envelope over the raw row bytes."""
        return store.legacy_envelope_digest(self.rows)


def add_source_arguments(parser) -> None:
    parser.add_argument("--stage", type=Path, action="append", default=None,
                        help="read a scratch union: the current union with the stage's declared "
                             "profiles replaced by its matrix.json rows; repeatable, one stage "
                             "per active/receded pair, their replaced pairs disjoint")
    parser.add_argument("--partial", action="store_true",
                        help="admit a stage missing declared non-holdout cells inside a (profile, "
                             "tier) pair it holds (a scratch look, never a cut to adopt)")
    parser.add_argument("--candidate", action="append", default=None, metavar="PATH[=SHA12]",
                        help="admit rows naming this scratch material-profile document at the "
                             "SHA-256 of its bytes (repo-relative as rows name it, or absolute); "
                             "repeatable; every output is stamped candidate")


def add_capture_arguments(parser) -> None:
    parser.add_argument("--captures", type=Path, action="append", default=None,
                        help="a web capture root; repeatable, each cell is read from the root "
                             f"whose metadata names its capturePath (default {CANONICAL_CAPTURES})")


def load(args) -> Source:
    candidates = _candidates(args.candidate)
    admitted = {**shipped_documents(), **{path: sha[:12] for path, sha in candidates}}
    if not args.stage:
        if candidates:
            raise SystemExit("--candidate needs --stage: the current union names no candidate "
                             "document, and a candidate is read only through the stage that "
                             "renders it")
        rows = store.load_current_rows(matrix_path=str(RESULTS / "matrix.json"))
        return Source(rows, "current union: results/matrix.json + results/generations/index.json",
                      None, admitted)
    return _stages([Path(stage).resolve() for stage in args.stage], args.partial, admitted,
                   candidates)


def shipped_documents() -> dict[str, str]:
    """`packages/calibration/profiles/*.json` at twelve hex of their live SHA-256, by the
    construction the owner test's `SHIPPED_DOCUMENT_HASHES` and every cut's guard use."""
    return {f"{SHIPPED}{path.name}": hashlib.sha256(path.read_bytes()).hexdigest()[:12]
            for path in sorted((CAL / "profiles").glob("*.json"))}


def _named(given: str) -> str:
    """A document path as a row names it: capture-web's `materialProfileLabel` shows a path
    inside the repository relative to it and one outside it absolute."""
    if os.path.isabs(given):
        shown = os.path.relpath(os.path.normpath(given), ROOT)
        return os.path.normpath(given) if shown.startswith("..") else shown
    shown = os.path.normpath(given)
    if shown.startswith(".."):
        raise SystemExit(f"--candidate {given}: a relative path is repo-relative; a document "
                         "outside the repository is named by its absolute path")
    return shown


def _candidates(specs) -> list[tuple[str, str]]:
    """Each declared candidate as (path as rows name it, full SHA-256 of its bytes)."""
    out = []
    for spec in specs or []:
        given, want = spec, None
        head, sep, tail = spec.rpartition("=")
        if sep:
            if not re.fullmatch(r"[0-9a-f]{12}", tail):
                raise SystemExit(f"--candidate {spec!r} is not PATH[=SHA12]")
            given, want = head, tail
        path = _named(given)
        file = ROOT / path
        if path.startswith(SHIPPED) or (CAL / "profiles").resolve() in file.resolve().parents:
            raise SystemExit(f"--candidate {path}: a document under {SHIPPED} is the shipped "
                             "file, not a candidate; render a candidate from a scratch copy")
        if not file.is_file():
            raise SystemExit(f"--candidate {path}: no such file ({file})")
        if any(path == seen for seen, _ in out):
            raise SystemExit(f"--candidate {path}: declared twice")
        sha = hashlib.sha256(file.read_bytes()).hexdigest()
        if want is not None and sha[:12] != want:
            raise SystemExit(f"--candidate {path}: the file hashes to sha256:{sha[:12]}, not the "
                             f"declared {want}")
        out.append((path, sha))
    return out


def _unadmitted(path: str, sha: str, admitted: dict, candidates) -> str:
    """Why (path, sha) is not admitted, naming the mismatch."""
    if any(path == declared for declared, _ in candidates):
        return (f"{path} sha256:{sha} is not the declared candidate's bytes "
                f"(sha256:{admitted[path]} on disk): the stage names another generation of it")
    if path in admitted:
        return f"declared {path} sha256:{sha} is not the file on disk ({admitted[path]})"
    return (f"{path} sha256:{sha} is neither a shipped document ({SHIPPED}) nor a declared "
            "--candidate")


def _pair(row) -> tuple[str, str]:
    return row["key"]["profileKey"], row["key"]["web"]["renderer"]


def _stages(stages: list[Path], partial: bool, admitted: dict, candidates) -> Source:
    read = [_stage(stage, partial, admitted, candidates) for stage in stages]
    owner: dict[tuple[str, str], Path] = {}
    for entry in read:
        for pair in entry["replaced"]:
            if pair in owner:
                raise SystemExit(f"{entry['stage']}: replaces {pair}, which {owner[pair]} "
                                 "replaces too; each (profile, tier) pair comes from one stage")
            owner[pair] = entry["stage"]
    named = {document["path"] for entry in read for document in entry["documents"]}
    for path, _ in candidates:
        if path not in named:
            raise SystemExit(f"--candidate {path} is declared by no --stage; a candidate is read "
                             "only through the stage that renders it")
    replaced_all = set(owner)
    current = store.load_current_rows(matrix_path=str(RESULTS / "matrix.json"))
    union = [r for r in current if _pair(r) not in replaced_all]
    for entry in read:
        union += entry["staged"]
    union.sort(key=store.key)
    keys = [store.key(r) for r in union]
    if len(set(keys)) != len(keys):
        raise SystemExit(f"{', '.join(map(str, stages))}: a staged key collides with a current "
                         "row")
    statuses = [_status(entry, current, replaced_all) for entry in read]
    unread = sorted({(e["profile"], e["renderer"]) for status in statuses
                     for e in status["keptFromCurrentUnion"]})
    label = (f"scratch union: current union with {len(replaced_all)} (profile, tier) pair(s) "
             f"replaced by {' + '.join(str(stage / 'matrix.json') for stage in stages)}; "
             f"{len(unread)} declared pair(s) absent from the "
             f"{'stage' if len(stages) == 1 else 'stages'} keep their current rows")
    print(f"# {label}", file=sys.stderr)
    for status in statuses:
        if len(stages) > 1:
            print(f"#  stage {status['stage']}", file=sys.stderr)
        for entry in status["replaced"]:
            print(f"#   replaced {entry['profile']} {entry['renderer']}: {entry['stageRows']} "
                  f"stage rows for {entry['currentRowsDropped']} current "
                  f"({entry['holdoutAbsentFromStage']} holdout not yet read)", file=sys.stderr)
        for entry in status["keptFromCurrentUnion"]:
            print(f"#   kept     {entry['profile']} {entry['renderer']}: {entry['rows']} current "
                  f"rows at {entry['generations']}", file=sys.stderr)
    return Source(union, label, statuses[0] if len(stages) == 1 else dict(stages=statuses),
                  admitted, tuple(candidates))


def _stage(stage: Path, partial: bool, admitted: dict, candidates) -> dict:
    """One stage validated on its own: its declaration, its rows and its coverage."""
    membership = json.loads((stage / "membership.json").read_text())
    if membership.get("schemaVersion") != 1 or not membership.get("cells"):
        raise SystemExit(f"{stage}: not a W40 stage membership")
    profiles = set(membership["profiles"])
    active, receded = membership["active"], membership.get("receded")
    # A referee reads the generation that would ship, or a declared candidate: a stage
    # declared at documents that are no longer the files on disk is a different generation
    # from the one a merge would land, and a scratch document nobody declared is not read.
    for document in [active] + ([receded] if receded else []):
        if admitted.get(document["path"]) != document["sha256"]:
            raise SystemExit(f"{stage}: "
                             + _unadmitted(document["path"], document["sha256"], admitted,
                                           candidates))
    expected = {"materialProfile": (active["path"], active["sha256"]),
                "recededProfile": (receded["path"], receded["sha256"]) if receded else None}
    staged = list(store.load_current_rows(matrix_path=str(stage / "matrix.json")))
    declared = {(c["profileKey"], c["renderer"], c["fixtureSet"], c["sceneId"])
                for c in membership["cells"]}
    seen = set()
    for row in staged:
        member = (row["key"]["profileKey"], row["key"]["web"]["renderer"], row["fixtureSet"],
                  row["key"]["sceneId"])
        if member not in declared:
            raise SystemExit(f"{stage}: row outside the declared membership: {member}")
        if member in seen:
            raise SystemExit(f"{stage}: two rows for one declared member: {member}")
        seen.add(member)
        named = {kind: (path, sha) for kind, path, sha in store.documents(row)}
        if named.get("materialProfile") != expected["materialProfile"] or \
                named.get("recededProfile") != expected["recededProfile"]:
            raise SystemExit(f"{stage}: {member} names documents other than the declaration's")
    replaced = sorted({_pair(r) for r in staged})
    # Inside a pair the stage holds, a declared non-holdout cell with no row would shrink a
    # cut's population in silence; holdout is read once after the freeze and no cut reads it.
    missing = sorted(m for m in declared - seen if (m[0], m[1]) in replaced)
    gated = [m for m in missing if m[2] != HOLDOUT]
    if gated and not partial:
        raise SystemExit(f"{stage}: {len(gated)} declared non-holdout cell(s) of a pair it holds "
                         f"have no row (first {gated[0]}); fill it or pass --partial")
    return dict(stage=stage, profiles=profiles, active=active, receded=receded,
                documents=[active] + ([receded] if receded else []), staged=staged,
                declared=declared, seen=seen, replaced=replaced, missing=missing, gated=gated)


def _status(entry: dict, current: list, replaced_all: set) -> dict:
    """What an output records about one stage: W41's status, byte for byte for one stage."""
    stage, staged, declared = entry["stage"], entry["staged"], entry["declared"]
    missing, gated = entry["missing"], entry["gated"]
    # A declared pair no stage holds keeps its current rows.
    unread = sorted({(m[0], m[1]) for m in declared} - replaced_all)

    def generations(rows):
        return sorted({" / ".join(f"{kind}={path} sha256:{sha}" for kind, path, sha in
                                  store.documents(r)) for r in rows})
    return dict(
        stage=str(stage),
        stageMatrixSha256=hashlib.sha256((stage / "matrix.json").read_bytes()).hexdigest(),
        declaredProfiles=sorted(entry["profiles"]),
        declaredDocuments=dict(active=entry["active"], receded=entry["receded"]),
        replaced=[dict(profile=p, renderer=t,
                       stageRows=sum(_pair(r) == (p, t) for r in staged),
                       currentRowsDropped=sum(_pair(r) == (p, t) for r in current),
                       holdoutAbsentFromStage=sum(m[2] == HOLDOUT for m in missing
                                                  if (m[0], m[1]) == (p, t)))
                  for p, t in entry["replaced"]],
        keptFromCurrentUnion=[dict(profile=p, renderer=t,
                                   rows=sum(_pair(r) == (p, t) for r in current),
                                   generations=generations([r for r in current
                                                            if _pair(r) == (p, t)]))
                              for p, t in unread],
        declaredCells=len(declared), stageRows=len(entry["seen"]),
        missingNonHoldoutInReplacedPairs=len(gated), partial=bool(gated))


def generation(active: str, receded: str | None) -> tuple[list, str]:
    """A named generation's rows and the file that owns them, through the store's resolver."""
    rows = store.load_generation(active, receded)
    owners = []
    for subdir, name in store.owners_for_document(active):
        index = json.loads((RESULTS / subdir / "index.json").read_text())
        entry = index["files"][name]
        secondary = next((d["sha256"] for d in entry["documents"]
                          if d["sha256"] != entry["activeDocumentSha256"]), None)
        if entry["activeDocumentSha256"] == active and secondary == receded:
            owners.append(name)
    if len(owners) != 1:
        raise SystemExit(f"generation ({active}, {receded}) has owners {owners}")
    return list(rows), owners[0]


class Captures:
    """Web capture roots, each cell read from the one whose metadata names the row's generation."""

    def __init__(self, roots):
        sys.path.insert(0, str(RESULTS / "2026-09-23-w34-g0-contour-bed"))
        from w35_readers import WebReader
        self.roots = [Path(r).resolve() for r in (roots or [CANONICAL_CAPTURES])]
        self.readers = [WebReader.canonical(root) for root in self.roots]

    def select(self, cell: str, row: dict):
        """The reader whose `cell__webgpu.json` names this row's capturePath.

        Raises FileNotFoundError when no root holds the cell, and ValueError when a root holds
        it at another generation and none at this one — a stale tree is never read in place.
        """
        others = []
        for root, reader in zip(self.roots, self.readers):
            try:
                meta = json.loads(reader.read(cell, "metadata"))
            except FileNotFoundError:
                continue
            if meta.get("capturePath") == row["key"]["web"]["capturePath"]:
                return reader
            others.append(str(root))
        if others:
            raise ValueError(f"{cell}: capture metadata under {others} names another generation")
        raise FileNotFoundError(f"{cell}: no capture root holds this cell")
