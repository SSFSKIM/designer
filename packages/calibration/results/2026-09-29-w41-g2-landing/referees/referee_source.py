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
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parent.parent
RESULTS = CAL / "results"
sys.path.insert(0, str(RESULTS / "2026-09-26-w40-g0-generations"))
import matrix_store as store  # noqa: E402

CANONICAL_CAPTURES = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
HOLDOUT = "holdout"


@dataclass
class Source:
    rows: list
    label: str
    stage: dict | None

    @property
    def described(self):
        """What an output records about its rows: the label, and in stage mode every pair."""
        return self.label if self.stage is None else dict(label=self.label, **self.stage)

    @property
    def legacy_sha256(self) -> str:
        """The whole-matrix witness: the legacy schema-5 envelope over the raw row bytes."""
        return store.legacy_envelope_digest(self.rows)


def add_source_arguments(parser) -> None:
    parser.add_argument("--stage", type=Path, default=None,
                        help="read a scratch union: the current union with the stage's declared "
                             "profiles replaced by its matrix.json rows")
    parser.add_argument("--partial", action="store_true",
                        help="admit a stage missing declared non-holdout cells inside a (profile, "
                             "tier) pair it holds (a scratch look, never a cut to adopt)")


def add_capture_arguments(parser) -> None:
    parser.add_argument("--captures", type=Path, action="append", default=None,
                        help="a web capture root; repeatable, each cell is read from the root "
                             f"whose metadata names its capturePath (default {CANONICAL_CAPTURES})")


def load(args) -> Source:
    if args.stage is None:
        rows = store.load_current_rows(matrix_path=str(RESULTS / "matrix.json"))
        return Source(rows, "current union: results/matrix.json + results/generations/index.json",
                      None)
    return _stage(Path(args.stage).resolve(), args.partial)


def _live(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:12]


def _pair(row) -> tuple[str, str]:
    return row["key"]["profileKey"], row["key"]["web"]["renderer"]


def _stage(stage: Path, partial: bool) -> Source:
    membership = json.loads((stage / "membership.json").read_text())
    if membership.get("schemaVersion") != 1 or not membership.get("cells"):
        raise SystemExit(f"{stage}: not a W40 stage membership")
    profiles = set(membership["profiles"])
    active, receded = membership["active"], membership.get("receded")
    # A referee reads the generation that would ship; a stage declared at documents that are
    # no longer the files on disk is a different generation from the one a merge would land.
    for document in [active] + ([receded] if receded else []):
        if _live(document["path"]) != document["sha256"]:
            raise SystemExit(f"{stage}: declared {document['path']} sha256:{document['sha256']} "
                             f"is not the file on disk ({_live(document['path'])})")
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
    unread = sorted({(m[0], m[1]) for m in declared} - set(replaced))
    # Inside a pair the stage holds, a declared non-holdout cell with no row would shrink a
    # cut's population in silence; holdout is read once after the freeze and no cut reads it.
    missing = sorted(m for m in declared - seen if (m[0], m[1]) in replaced)
    gated = [m for m in missing if m[2] != HOLDOUT]
    if gated and not partial:
        raise SystemExit(f"{stage}: {len(gated)} declared non-holdout cell(s) of a pair it holds "
                         f"have no row (first {gated[0]}); fill it or pass --partial")
    current = store.load_current_rows(matrix_path=str(RESULTS / "matrix.json"))
    union = [r for r in current if _pair(r) not in replaced] + staged
    union.sort(key=store.key)
    keys = [store.key(r) for r in union]
    if len(set(keys)) != len(keys):
        raise SystemExit(f"{stage}: a staged key collides with a current row")

    def generations(rows):
        return sorted({" / ".join(f"{kind}={path} sha256:{sha}" for kind, path, sha in
                                  store.documents(r)) for r in rows})
    status = dict(
        stage=str(stage),
        stageMatrixSha256=hashlib.sha256((stage / "matrix.json").read_bytes()).hexdigest(),
        declaredProfiles=sorted(profiles),
        declaredDocuments=dict(active=active, receded=receded),
        replaced=[dict(profile=p, renderer=t,
                       stageRows=sum(_pair(r) == (p, t) for r in staged),
                       currentRowsDropped=sum(_pair(r) == (p, t) for r in current),
                       holdoutAbsentFromStage=sum(m[2] == HOLDOUT for m in missing
                                                  if (m[0], m[1]) == (p, t)))
                  for p, t in replaced],
        keptFromCurrentUnion=[dict(profile=p, renderer=t,
                                   rows=sum(_pair(r) == (p, t) for r in current),
                                   generations=generations([r for r in current
                                                            if _pair(r) == (p, t)]))
                              for p, t in unread],
        declaredCells=len(declared), stageRows=len(seen),
        missingNonHoldoutInReplacedPairs=len(gated), partial=bool(gated))
    label = (f"scratch union: current union with {len(replaced)} (profile, tier) pair(s) "
             f"replaced by {stage / 'matrix.json'}; {len(unread)} declared pair(s) absent from "
             "the stage keep their current rows")
    print(f"# {label}", file=sys.stderr)
    for entry in status["replaced"]:
        print(f"#   replaced {entry['profile']} {entry['renderer']}: {entry['stageRows']} stage "
              f"rows for {entry['currentRowsDropped']} current ({entry['holdoutAbsentFromStage']} "
              "holdout not yet read)", file=sys.stderr)
    for entry in status["keptFromCurrentUnion"]:
        print(f"#   kept     {entry['profile']} {entry['renderer']}: {entry['rows']} current rows "
              f"at {entry['generations']}", file=sys.stderr)
    return Source(union, label, status)


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
