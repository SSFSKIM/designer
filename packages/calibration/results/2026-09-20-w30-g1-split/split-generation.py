#!/usr/bin/env python3
"""Split the canonical matrix by generation — W30 G1, Decision Log 1 (d), contract X7.

A cell's key carries the material profile document its capture was driven from, and
that document's twelve-hex content hash, inside its own `capturePath`. A refit moves
the document's bytes, so the next run does not overwrite the rows read at the old
bytes — it APPENDS a second generation beside them. Both generations are evidence and
neither may be rewritten; but only one of them is the bed that ships, and until now
"which one" was answerable only by reading a timestamp or by hashing the documents on
disk at every read.

This script makes it a name. The working file keeps exactly one generation — every row
all of whose documents are on disk at the bytes the row names — and every other row is
moved, byte for byte, into `results/superseded/<document-sha>.json`.

**The rule for `<document-sha>`, and why it is one hash when a generation is several
documents.** A run names up to two documents: the ACTIVE document (`--material-profile`,
which also selects the runtime material the patch is a difference from) and, on a run
that poses its inactive scenes, the RECEDED document (`--receded-profile`), which is by
construction a difference over the active document of its own scheme. A generation is
therefore a set — a light active and its receded, a dark active and its receded — and a
set has no single hash. So the file is named by the hash of the row's own ACTIVE
document, and a receded document never names a file: it travels with the active document
it is a difference from, because it cannot be read apart from it. A light generation and
a dark generation land in two files, which is right — they are two materials, refitted
together but read apart, and the light file is the one a person looking for "the light
bed before the refit" wants.

Finding a superseded row is then a LOOKUP, never a pattern match on a file name:
`results/superseded/index.json` maps every document hash a superseded row names — active
and receded alike — to the file that holds those rows. A reader that has a hash asks the
index; a reader that has none reads the working file, which is the shipped generation by
construction.

**When only the difference document moved.** A refit can seal a new receded document over
an active document that still ships — the unfocused endpoint alone is refitted — and then
a superseded row names a CURRENT active document. The active hash alone would misdescribe
that file, so the generation is named by the whole of what it was read at: a COMPOUND
`<active>-<receded>.json`, with `index.json` mapping both hashes to it. The lookup is
what finds it; the name is never parsed. A hash that would name two different superseded
files is refused rather than silently overwritten in the index.

`--current` takes the hashes that are current and everything else moves; it is repeatable
and takes any number of hashes after each use. It defaults to the twelve-hex SHA-256 of
every file in `packages/calibration/profiles/`, which is exactly what
`test/adopted-thresholds.test.ts`'s `SHIPPED_DOCUMENT_HASHES` derives, so the default run
and the gate cannot disagree about which generation ships.

**What the tool refuses, before it writes a byte.** A row of a frozen macOS 26.5 profile
selected to move (contract X1 is the tool's to hold, not the operator's); a row whose
`capturePath` carries more document hashes than the clause pattern parses, so a third kind
of document would change a row's currency without this script seeing it; a destination
that already exists, a before-manifest that already exists, or an index entry that would
be overwritten. Every check runs over the whole plan first, so a refusal leaves the tree
as it was rather than half split.

`apply` names its own evidence directory and its own claims section — no defaults, because
a second run that inherited G1's would overwrite G1's committed witness and label a new
generation with the old generation's section.

Rows are moved as RAW TEXT slices of the working file rather than re-serialised: a
JSON round-trip through any other printer is not byte-exact (Python's and V8's number
printers disagree on about six kilobytes of this file), and a row that moves must not
change. The retained rows keep their relative order for the same reason the freeze
needs them to: `results/2026-09-16-w29-freeze/freeze.py` labels each 26.5 row with a
positional counter in file order and compares the whole list ordered.

    python3 split-generation.py plan [--current <12hex> ...]
    python3 split-generation.py apply --evidence <dir> --claims <section> [--current <12hex> ...]

`classifier-selftest.py` beside this file exercises `classify` and `destinations` on a
synthetic matrix — a current row, a superseded-active row, a receded-only superseded row
and a row carrying a third document clause — because the shapes the naming rule has to
name are not all in the bed, and a rule nothing exercises is a rule nobody has read.

W30 G4's invocation, the second application of contract X7, in full:

    python3 packages/calibration/results/2026-09-20-w30-g1-split/split-generation.py apply \\
        --evidence packages/calibration/results/2026-09-20-w30-g4-landing/ \\
        --claims "c9a §5.160"
"""
import datetime
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
RESULTS = ROOT / "packages/calibration/results"
MATRIX = RESULTS / "matrix.json"
SUPERSEDED = RESULTS / "superseded"
PROFILES = ROOT / "packages/calibration/profiles"
TODAY = datetime.date.today().isoformat()

# The clause `capture-web` writes into a cell's `capturePath`, once per document the
# run named. `scripts/material-profile-file.ts` builds it; `atAShippedDocument` reads
# it with the same shape.
DOCUMENT_CLAUSE = re.compile(r"(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})")
ACTIVE_CLAUSE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")
HASH_TOKEN = re.compile(r"^[0-9a-f]{12}$")

# The profiles whose rows are frozen evidence (`results/2026-09-16-w29-freeze/`), and
# which contract X1 keeps in the working file whatever a generation split is asked to do.
FROZEN_PREFIX = "apple-macos-26.5-"


def sha12(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def current_hashes() -> dict:
    """`{repo-relative document path: 12-hex}` for every committed profile document."""
    return {
        f"packages/calibration/profiles/{p.name}": sha12(p.read_bytes())
        for p in sorted(PROFILES.glob("*.json"))
    }


def elements(raw: bytes):
    """Every top-level element of the `cells` array, as (start, end) byte offsets.

    A brace walk over the raw text, honouring strings and escapes. Nothing is parsed
    into Python objects on this path, so a slice is the row's own bytes.
    """
    key = raw.index(b'"cells"')
    start = raw.index(b"[", key)
    i = start + 1
    depth = 0
    begin = None
    out = []
    in_string = False
    escaped = False
    while i < len(raw):
        c = raw[i]
        if in_string:
            if escaped:
                escaped = False
            elif c == 0x5C:  # backslash
                escaped = True
            elif c == 0x22:  # quote
                in_string = False
        elif c == 0x22:
            in_string = True
        elif c in (0x7B, 0x5B):  # { [
            if depth == 0:
                begin = i
            depth += 1
        elif c in (0x7D, 0x5D):  # } ]
            if depth == 0:
                # The closing bracket of the `cells` array itself.
                return start, out, i
            depth -= 1
            if depth == 0:
                out.append((begin, i + 1))
        i += 1
    raise ValueError("matrix.json: the cells array never closes")


def canon(obj) -> bytes:
    """One JSON value, serialised so that only its content decides its hash.

    The same construction `freeze.py` hashes a matrix row by, so a row's identity here
    and a row's identity in the freeze are the same quantity.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def classify(raw: bytes, span, current: dict):
    """One row: the documents it names, and whether every one of them is current.

    A row is CURRENT when every document its `capturePath` names is on disk at the
    bytes the row records. One superseded document in the set supersedes the row: a
    reading posed with a receded document nobody ships is not a reading of the shipped
    material, whatever its active document says.

    **Every document hash in the path is parsed, or the row is refused.** The clause
    pattern knows two kinds of document; a run that named a third would write a third
    clause, and a currency judgement that silently ignored it would call a row current
    on the strength of the documents it happens to recognise. So the count of `sha256:`
    occurrences in the path must equal the number of clauses parsed out of it.
    """
    row = json.loads(raw[span[0]:span[1]])
    path = row["key"]["web"]["capturePath"]
    named = DOCUMENT_CLAUSE.findall(path)
    if path.count("sha256:") != len(named):
        raise ValueError(
            f"capturePath carries {path.count('sha256:')} document hashes and "
            f"{len(named)} parse as clauses this script knows: {path}")
    active = ACTIVE_CLAUSE.search(path)
    is_current = bool(named) and all(current.get(doc) == h for doc, h in named)
    return {
        "profileKey": row["key"]["profileKey"],
        "sceneId": row["key"]["sceneId"],
        "tier": row["tier"],
        "fixtureSet": row["fixtureSet"],
        "capturedAt": row["capturedAt"],
        "documents": [{"path": d, "sha256": h} for d, h in named],
        "activeDocument": None if active is None else active.group(1),
        "activeSha256": None if active is None else active.group(2),
        "current": is_current,
        "rowSha256": hashlib.sha256(canon(row)).hexdigest(),
    }


def read():
    raw = MATRIX.read_bytes()
    start, spans, end = elements(raw)
    prefix = raw[: spans[0][0]] if spans else raw[: start + 1]
    suffix = raw[spans[-1][1]:] if spans else raw[start + 1:]
    seps = {raw[spans[i][1]: spans[i + 1][0]] for i in range(len(spans) - 1)}
    if len(seps) > 1:
        raise ValueError(f"matrix.json: {len(seps)} distinct element separators")
    sep = seps.pop() if seps else b",\n    "
    return raw, spans, prefix, sep, suffix


def compose(prefix: bytes, sep: bytes, suffix: bytes, slices) -> bytes:
    return prefix + sep.join(slices) + suffix


def destinations(rows, current: dict):
    """Which rows stay in the working file, and which file each of the others lands in.

    Returns `(keep_idx, dest)`, `dest` mapping a superseded file's stem — its name
    without `.json` — to the indices of the rows it holds, in file order. Raises
    `ValueError` for every shape the naming rule cannot name, over the whole plan and
    before the caller has written anything.
    """
    keep_idx = [i for i, r in enumerate(rows) if r["current"] or not r["documents"]]
    retained = set(keep_idx)
    move_idx = [i for i in range(len(rows)) if i not in retained]

    # Contract X1: the frozen macOS 26.5 bed does not move, and the tool holds that
    # rather than the operator. One mistyped `--current` selects those rows by the
    # hundred, and the append-check that would catch it only reads after `apply` has
    # written the files.
    frozen = [i for i in move_idx if rows[i]["profileKey"].startswith(FROZEN_PREFIX)]
    if frozen:
        keys = sorted({rows[i]["profileKey"] for i in frozen})
        raise ValueError(
            f"X1: {len(frozen)} rows of the frozen macOS 26.5 bed are selected to move "
            f"({', '.join(keys)}); check --current")

    dest = {}
    for i in move_idx:
        h = rows[i]["activeSha256"]
        if h is None:
            # A row naming a receded document and no active one. `capture-web` does not
            # write that shape — and a row naming no document at all is retained above,
            # not moved — but the file name IS the index, so it is refused rather than
            # guessed at. `classifier-selftest.py` holds this case.
            raise ValueError(f"row {i} is superseded but names no active document")
        stale = [d["sha256"] for d in rows[i]["documents"]
                 if current.get(d["path"]) != d["sha256"]]
        # The compound name, for the generation where only a difference document moved:
        # the active document still ships, so its hash alone would name this file after
        # a generation that is current. See the docstring.
        stem = h if h not in current.values() else "-".join([h] + stale)
        dest.setdefault(stem, []).append(i)
    return keep_idx, dest


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "plan"
    argv = sys.argv[2:]
    # `--current` is repeatable AND takes every hash that follows it, which is what its
    # usage line says; a flag whose parsing and whose documentation disagree is how a
    # `--current a b c` run comes to move rows nobody asked it to.
    override = []
    evidence = None
    claims = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--current":
            i += 1
            while i < len(argv) and not argv[i].startswith("--"):
                override.append(argv[i])
                i += 1
            continue
        if a in ("--evidence", "--claims"):
            if i + 1 >= len(argv):
                print(f"{a} takes a value")
                return 2
            if a == "--evidence":
                evidence = pathlib.Path(argv[i + 1]).resolve()
            else:
                claims = argv[i + 1]
            i += 2
            continue
        print(f"unknown argument {a}")
        return 2
    malformed = [h for h in override if not HASH_TOKEN.match(h)]
    if malformed:
        print(f"--current takes twelve-hex document hashes; got {malformed}")
        return 2
    if mode == "apply" and (evidence is None or claims is None):
        print("apply requires --evidence <dir> and --claims <section>; see the docstring "
              "for G4's invocation")
        return 2

    on_disk = current_hashes()
    if override:
        keep = set(override)
        current = {path: h for path, h in on_disk.items() if h in keep}
        missing = keep - set(current.values())
        if missing:
            print(f"--current names {sorted(missing)}, which no committed document has")
            return 1
    else:
        current = on_disk

    raw, spans, prefix, sep, suffix = read()
    rows = []
    for i, s in enumerate(spans):
        try:
            rows.append(classify(raw, s, current))
        except ValueError as refusal:
            print(f"row {i}: {refusal}; refusing")
            return 1

    try:
        keep_idx, dest = destinations(rows, current)
    except ValueError as refusal:
        print(f"{refusal}; refusing")
        return 1
    move_idx = [i for group in dest.values() for i in group]

    print(f"current documents ({len(current)}):")
    for path, h in sorted(current.items()):
        print(f"  {h}  {path}")
    print(f"rows: {len(rows)} total, {len(keep_idx)} retained, {len(move_idx)} moved")
    for stem in sorted(dest):
        by_profile = {}
        for i in dest[stem]:
            by_profile[rows[i]["profileKey"]] = by_profile.get(rows[i]["profileKey"], 0) + 1
        print(f"  superseded/{stem}.json  {len(dest[stem])} rows")
        for pk in sorted(by_profile):
            print(f"      {by_profile[pk]:5d}  {pk}")
    if mode == "plan":
        return 0
    if mode != "apply":
        print(f"usage: {pathlib.Path(__file__).name} plan|apply")
        return 2

    stem_of = {i: stem for stem, group in dest.items() for i in group}
    prior = {}
    if (SUPERSEDED / "index.json").exists():
        prior = json.loads((SUPERSEDED / "index.json").read_text())
    prior_lookup = dict(prior.get("byDocumentSha256", {}))

    # Every destination is checked before a byte is written, so a refusal leaves the
    # tree as it stood rather than half split. Three ways a run would overwrite a
    # record: a superseded file of that name already there, an index entry that would
    # start pointing somewhere else, and — the one a rerun hits — the before-manifest
    # of the run that already happened, which is the append-check's whole witness.
    manifest_path = evidence / "before-manifest.json"
    blocked = []
    if manifest_path.exists():
        blocked.append(
            f"{manifest_path} already exists; it witnesses a split that has already run")
    for stem in sorted(dest):
        out = SUPERSEDED / f"{stem}.json"
        if out.exists():
            blocked.append(f"{out} already exists; a recorded generation is never overwritten")
        for i in dest[stem]:
            for d in rows[i]["documents"]:
                held = prior_lookup.get(d["sha256"])
                if held is not None and held != f"{stem}.json":
                    blocked.append(
                        f"index.json maps document {d['sha256']} to {held}; this run would "
                        f"point it at {stem}.json")
    if blocked:
        for line in sorted(set(blocked)):
            print(line)
        print("refusing; nothing written")
        return 1

    # The before-manifest is written from the file as it stands, before a byte of it
    # moves, so the append-check has a witness that does not depend on the split.
    evidence.mkdir(parents=True, exist_ok=True)
    manifest = {
        "what": "the canonical matrix immediately before the generation split",
        "matrixSha256": hashlib.sha256(raw).hexdigest(),
        "matrixBytes": len(raw),
        "rowCount": len(rows),
        "currentDocuments": [{"path": p, "sha256": h} for p, h in sorted(current.items())],
        "rows": [
            {
                "index": i,
                "rowSha256": r["rowSha256"],
                "profileKey": r["profileKey"],
                "sceneId": r["sceneId"],
                "tier": r["tier"],
                "fixtureSet": r["fixtureSet"],
                "documents": r["documents"],
                "destination": (
                    "results/matrix.json" if i not in stem_of
                    else f"results/superseded/{stem_of[i]}.json"
                ),
            }
            for i, r in enumerate(rows)
        ],
    }
    (evidence / "before-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    SUPERSEDED.mkdir(parents=True, exist_ok=True)
    index = {
        "what": (
            "Every superseded generation of canonical rows, by the document each was "
            "read at. `byDocumentSha256` is the lookup: a twelve-hex document hash — "
            "active or receded — maps to the file holding the rows that name it."
        ),
        "rule": (
            "A file is named by the ACTIVE document's twelve-hex SHA-256. A receded "
            "document never names a file; it is a difference over the active document "
            "of its own scheme and travels with it. Where only the receded document "
            "moved and the active one still ships, the name is the compound "
            "`<active>-<receded>`, because the active hash alone would name this file "
            "after a generation that is current."
        ),
        "files": dict(prior.get("files", {})),
        "byDocumentSha256": dict(prior.get("byDocumentSha256", {})),
    }
    files = index["files"]
    lookup = index["byDocumentSha256"]

    for stem in sorted(dest):
        slices = [raw[spans[i][0]:spans[i][1]] for i in dest[stem]]
        out = SUPERSEDED / f"{stem}.json"
        out.write_bytes(compose(prefix, sep, suffix, slices))
        by_profile = {}
        for i in dest[stem]:
            by_profile[rows[i]["profileKey"]] = by_profile.get(rows[i]["profileKey"], 0) + 1
        named = sorted({(d["path"], d["sha256"]) for i in dest[stem] for d in rows[i]["documents"]})
        captured = sorted(rows[i]["capturedAt"] for i in dest[stem])
        files[f"{stem}.json"] = {
            "activeDocumentSha256": rows[dest[stem][0]]["activeSha256"],
            "documents": [{"path": p, "sha256": s} for p, s in named],
            "readUnderClaims": claims,
            "capturedAt": {"first": captured[0], "last": captured[-1]},
            "supersededOn": TODAY,
            "rowCount": len(dest[stem]),
            "rowsByProfileKey": dict(sorted(by_profile.items())),
            "bytes": out.stat().st_size,
            "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        }
        for _, s in named:
            lookup[s] = f"{stem}.json"
        print(f"wrote {out.relative_to(ROOT)}  {len(dest[stem])} rows  {out.stat().st_size} bytes")

    index["files"] = dict(sorted(files.items()))
    index["byDocumentSha256"] = dict(sorted(lookup.items()))
    (SUPERSEDED / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n")

    MATRIX.write_bytes(compose(prefix, sep, suffix, [raw[spans[i][0]:spans[i][1]] for i in keep_idx]))
    after = MATRIX.read_bytes()
    print(f"wrote {MATRIX.relative_to(ROOT)}  {len(keep_idx)} rows  {len(after)} bytes")
    print(f"matrix sha256 before {manifest['matrixSha256']}")
    print(f"matrix sha256 after  {hashlib.sha256(after).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
