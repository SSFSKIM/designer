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

`--current` takes the hashes that are current and everything else moves. It defaults to
the twelve-hex SHA-256 of every file in `packages/calibration/profiles/`, which is
exactly what `test/adopted-thresholds.test.ts`'s `SHIPPED_DOCUMENT_HASHES` derives, so
the default run and the gate cannot disagree about which generation ships. G4 runs this
again, with no arguments, once its own read has sealed new documents.

Rows are moved as RAW TEXT slices of the working file rather than re-serialised: a
JSON round-trip through any other printer is not byte-exact (Python's and V8's number
printers disagree on about six kilobytes of this file), and a row that moves must not
change. The retained rows keep their relative order for the same reason the freeze
needs them to: `results/2026-09-16-w29-freeze/freeze.py` labels each 26.5 row with a
positional counter in file order and compares the whole list ordered.

    python3 split-generation.py plan
    python3 split-generation.py apply [--current <12hex> ...] [--evidence <dir>]
"""
import datetime
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
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
    """
    row = json.loads(raw[span[0]:span[1]])
    path = row["key"]["web"]["capturePath"]
    named = DOCUMENT_CLAUSE.findall(path)
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


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "plan"
    argv = sys.argv[2:]
    override = [argv[i + 1] for i, a in enumerate(argv) if a == "--current"]
    evidence = HERE
    claims = None
    for i, a in enumerate(argv):
        if a == "--evidence":
            evidence = pathlib.Path(argv[i + 1]).resolve()
        if a == "--claims":
            claims = argv[i + 1]

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
    rows = [classify(raw, s, current) for s in spans]

    keep_idx = [i for i, r in enumerate(rows) if r["current"] or not r["documents"]]
    move_idx = [i for i in range(len(rows)) if i not in set(keep_idx)]

    # The destination, by the rule in the docstring: the row's active document's hash.
    dest = {}
    for i in move_idx:
        h = rows[i]["activeSha256"]
        if h is None:
            print(f"row {i} is superseded but names no active document; refusing")
            return 1
        if h in current.values():
            # Would name a superseded file after a document that still ships. Nothing
            # in the bed produces this today (a generation's documents move together);
            # it is refused rather than guessed at, because the file name is the index.
            print(f"row {i}: active document {h} is current but the row is superseded; refusing")
            return 1
        dest.setdefault(h, []).append(i)

    print(f"current documents ({len(current)}):")
    for path, h in sorted(current.items()):
        print(f"  {h}  {path}")
    print(f"rows: {len(rows)} total, {len(keep_idx)} retained, {len(move_idx)} moved")
    for h in sorted(dest):
        by_profile = {}
        for i in dest[h]:
            by_profile[rows[i]["profileKey"]] = by_profile.get(rows[i]["profileKey"], 0) + 1
        print(f"  superseded/{h}.json  {len(dest[h])} rows")
        for pk in sorted(by_profile):
            print(f"      {by_profile[pk]:5d}  {pk}")
    if mode == "plan":
        return 0
    if mode != "apply":
        print(f"usage: {pathlib.Path(__file__).name} plan|apply")
        return 2

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
                    "results/matrix.json" if i in set(keep_idx)
                    else f"results/superseded/{r['activeSha256']}.json"
                ),
            }
            for i, r in enumerate(rows)
        ],
    }
    (evidence / "before-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    SUPERSEDED.mkdir(parents=True, exist_ok=True)
    prior = {}
    if (SUPERSEDED / "index.json").exists():
        prior = json.loads((SUPERSEDED / "index.json").read_text())
    index = {
        "what": (
            "Every superseded generation of canonical rows, by the document each was "
            "read at. `byDocumentSha256` is the lookup: a twelve-hex document hash — "
            "active or receded — maps to the file holding the rows that name it."
        ),
        "rule": (
            "A file is named by the ACTIVE document's twelve-hex SHA-256. A receded "
            "document never names a file; it is a difference over the active document "
            "of its own scheme and travels with it."
        ),
        "files": dict(prior.get("files", {})),
        "byDocumentSha256": dict(prior.get("byDocumentSha256", {})),
    }
    files = index["files"]
    lookup = index["byDocumentSha256"]

    for h in sorted(dest):
        slices = [raw[spans[i][0]:spans[i][1]] for i in dest[h]]
        out = SUPERSEDED / f"{h}.json"
        if out.exists():
            print(f"{out} already exists; refusing to overwrite a recorded generation")
            return 1
        out.write_bytes(compose(prefix, sep, suffix, slices))
        by_profile = {}
        for i in dest[h]:
            by_profile[rows[i]["profileKey"]] = by_profile.get(rows[i]["profileKey"], 0) + 1
        named = sorted({(d["path"], d["sha256"]) for i in dest[h] for d in rows[i]["documents"]})
        captured = sorted(rows[i]["capturedAt"] for i in dest[h])
        files[f"{h}.json"] = {
            "activeDocumentSha256": h,
            "documents": [{"path": p, "sha256": s} for p, s in named],
            "readUnderClaims": claims,
            "capturedAt": {"first": captured[0], "last": captured[-1]},
            "supersededOn": TODAY,
            "rowCount": len(dest[h]),
            "rowsByProfileKey": dict(sorted(by_profile.items())),
            "bytes": out.stat().st_size,
            "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        }
        for _, s in named:
            lookup[s] = f"{h}.json"
        print(f"wrote {out.relative_to(ROOT)}  {len(dest[h])} rows  {out.stat().st_size} bytes")

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
