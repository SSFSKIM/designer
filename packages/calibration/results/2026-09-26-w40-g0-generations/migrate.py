#!/usr/bin/env python3.12
"""W40 G0 one-time migration of the snapshotted schema-5 matrix.

Reuses W30's brace-walk/raw-slice envelope via snapshot.py; no row is reserialized.
Run snapshot.py before invoking this tool. Future publication belongs to G1.
"""
import collections
import hashlib
import json
import pathlib
import sys

from snapshot import ROOT, RESULTS, HERE, digest, documents, key, slices

INDEX = RESULTS / "generations/index.json"
EXPECTED = {"85ad7f7e3e0d": ("30fbe05986ae", 509, 19788488),
            "0eac5b294cc2": ("5cec8c961201", 277, 10630441)}


def main():
    source = RESULTS / "matrix.json"
    witness = json.loads((HERE / "snapshot.json").read_bytes())
    if not (HERE / "demo-before.json").is_file():
        raise ValueError("demo-before.json must exist before migration")
    if INDEX.exists():
        raise ValueError("already migrated: generations/index.json exists")
    raw = source.read_bytes()
    if len(raw) != witness["matrixBytes"] or digest(raw) != witness["matrixSha256"]:
        raise ValueError("source matrix differs from pre-migration snapshot")
    spans, prefix, separator, suffix = slices(raw)
    if len(spans) != witness["rowCount"]:
        raise ValueError("source row count differs")
    groups = collections.defaultdict(list)
    frozen = []
    for i, (start, end) in enumerate(spans):
        slice_ = raw[start:end]
        cell = json.loads(slice_)
        row_witness = witness["rows"][i]
        if (start != row_witness["start"] or end != row_witness["end"] or
                key(cell) != row_witness["key"] or digest(slice_) != row_witness["sha256"]):
            raise ValueError(f"source row {i} differs from snapshot")
        profile = cell["key"]["profileKey"]
        if profile.startswith("apple-macos-26.5-"):
            frozen.append(slice_)
            continue
        if not profile.startswith("apple-macos-27.0-"):
            raise ValueError(f"unknown profile: {profile}")
        clauses = documents(cell)
        active = [h for kind, _, h in clauses if kind == "materialProfile"]
        if len(active) != 1 or active[0] not in EXPECTED:
            raise ValueError(f"unexpected active document in row {i}")
        receded = [h for kind, _, h in clauses if kind == "recededProfile"]
        if receded != [EXPECTED[active[0]][0]]:
            raise ValueError(f"unexpected receded document in row {i}")
        for _, path, sha in clauses:
            if digest((ROOT / path).read_bytes())[:12] != sha:
                raise ValueError(f"row {i} does not name shipped document bytes: {path}")
        groups[active[0]].append((slice_, cell, clauses))
    if len(frozen) != 1107 or set(groups) != set(EXPECTED):
        raise ValueError("migration has unexpected frozen or generation membership")
    compose = lambda values: prefix + separator.join(values) + suffix
    frozen_bytes = compose(frozen)
    if len(frozen_bytes) != 39150416:
        raise ValueError("frozen envelope differs from grounded size")
    files = {}
    aliases = collections.defaultdict(list)
    current = {}
    outputs = {}
    for active in sorted(groups):
        members = groups[active]
        receded, count, length = EXPECTED[active]
        blob = compose([piece for piece, _, _ in members])
        if len(members) != count or len(blob) != length:
            raise ValueError(f"unexpected row count/bytes for {active}")
        filename = f"{active}.json"
        destination = RESULTS / "generations" / filename
        if destination.exists():
            raise ValueError(f"immutable generation destination already exists: {destination}")
        named = sorted({(path, sha) for _, _, docs in members for _, path, sha in docs})
        if {h for _, h in named} != {active, receded} or len(named) != 2:
            raise ValueError(f"incomplete document set for {filename}")
        counts = dict(sorted(collections.Counter(row["key"]["profileKey"] for _, row, _ in members).items()))
        for profile in counts:
            if profile in current:
                raise ValueError(f"profile assigned twice: {profile}")
            current[profile] = filename
        files[filename] = {"activeDocumentSha256": active,
                           "documents": [{"path": p, "sha256": h} for p, h in named],
                           "rowCount": count, "rowsByProfileKey": counts,
                           "bytes": len(blob), "sha256": digest(blob), "status": "current"}
        for _, h in named:
            aliases[h].append(filename)
        outputs[destination] = blob
    index = {"schemaVersion": 1, "files": files,
             "byDocumentSha256": {h: sorted(names) for h, names in sorted(aliases.items())},
             "currentByProfile": dict(sorted(current.items()))}
    if len(current) != 6:
        raise ValueError("six macOS 27 profiles expected")
    # Verify the exact envelope digest over the prospective raw-slice union before writing.
    union = [(key(json.loads(s)), s) for s in frozen]
    for members in groups.values():
        union += [(key(row), s) for s, row, _ in members]
    union.sort(key=lambda pair: pair[0])
    if len({k for k, _ in union}) != witness["rowCount"] or digest(compose([s for _, s in union])) != witness["matrixSha256"]:
        raise ValueError("prospective union does not reconstruct the old matrix")
    (RESULTS / "generations").mkdir(exist_ok=True)
    for path, blob in outputs.items():
        path.write_bytes(blob)
    source.write_bytes(frozen_bytes)
    INDEX.write_text(json.dumps(index, indent=2) + "\n")
    print(f"migrated {len(frozen)} frozen + {sum(len(x) for x in groups.values())} macOS 27 rows")
    for path in [source, *sorted(outputs), INDEX]:
        b = path.read_bytes()
        print(f"{path.relative_to(ROOT)} {len(b)} {digest(b)}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"migration refused: {error}", file=sys.stderr)
        raise SystemExit(1)
