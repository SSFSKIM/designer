#!/usr/bin/env python3.12
"""Prove the W40 migration against the BEFORE snapshot without mutating the matrix."""
import collections
import json
import pathlib
import sys

from snapshot import HERE, RESULTS, digest, key, slices
from matrix_store import load_current_rows, legacy_envelope_digest

EXPECTED = "7df96c9246bc9b964fd6e173e742f49dcf493ccb360f7df505a0157240eaf0de"


def main():
    before = json.loads((HERE / "snapshot.json").read_bytes())
    index = json.loads((RESULTS / "generations/index.json").read_bytes())
    if before["matrixSha256"] != EXPECTED:
        raise ValueError("pre-migration witness has unexpected source digest")
    spans = {}
    owner = {}
    profile_groups = collections.defaultdict(lambda: collections.Counter())
    for path in [RESULTS / "matrix.json", *(RESULTS / "generations" / filename
                                            for filename in index["files"]
                                            if index["files"][filename]["status"] == "current")]:
        raw = path.read_bytes()
        offsets, _, _, _ = slices(raw)
        for a, b in offsets:
            piece = raw[a:b]
            row = json.loads(piece)
            identity = key(row)
            if identity in spans:
                raise ValueError(f"duplicate authoritative row in {path} and {owner[identity]}")
            spans[identity] = digest(piece)
            owner[identity] = path.relative_to(RESULTS).as_posix()
            profile_groups[row["key"]["profileKey"]][owner[identity]] += 1
    expected = {item["key"]: item["sha256"] for item in before["rows"]}
    if len(expected) != before["rowCount"] or spans != expected:
        missing = sorted(expected.keys() - spans.keys())
        extra = sorted(spans.keys() - expected.keys())
        altered = sorted(k for k in spans.keys() & expected.keys() if spans[k] != expected[k])
        raise ValueError(f"snapshot mismatch: missing={len(missing)}, extra={len(extra)}, altered={len(altered)}")
    frozen = sum(n for profile, files in profile_groups.items() for file, n in files.items()
                 if profile.startswith("apple-macos-26.5-") and file == "matrix.json")
    moved = sum(n for profile, files in profile_groups.items() for file, n in files.items()
                if profile.startswith("apple-macos-27.0-") and file.startswith("generations/"))
    if frozen != 1107 or moved != 786:
        raise ValueError(f"layout mismatch: frozen={frozen}, moved={moved}")
    if any(profile.startswith("apple-macos-27.0-") and "matrix.json" in files or
           profile.startswith("apple-macos-26.5-") and any(f != "matrix.json" for f in files)
           for profile, files in profile_groups.items()):
        raise ValueError("a row appears in the wrong authority")
    rows = load_current_rows()
    keys = [key(row) for row in rows]
    if keys != [row["key"] for row in before["rows"]]:
        raise ValueError("union serialized key order differs")
    envelope = legacy_envelope_digest(rows)
    if envelope != EXPECTED:
        raise ValueError(f"legacy envelope digest differs: {envelope}")
    files = {}
    for path in [RESULTS / "matrix.json", *(RESULTS / "generations" / filename for filename in index["files"])]:
        raw = path.read_bytes()
        files[path.relative_to(RESULTS).as_posix()] = {"bytes": len(raw), "sha256": digest(raw)}
    output = {
        "schemaVersion": 1, "sourceSha256": before["matrixSha256"],
        "sourceBytes": before["matrixBytes"], "sourceRows": before["rowCount"],
        "serializedKeyOrderSha256": before["keyOrderSha256"],
        "rawSlicesMatched": len(spans), "rawSlicesAltered": 0,
        "missingKeys": 0, "extraKeys": 0, "duplicateAuthoritativeKeys": 0,
        "frozenRows": frozen, "macos27Rows": moved,
        "currentProfiles": {profile: dict(sorted(files.items())) for profile, files in sorted(profile_groups.items())},
        "legacyEnvelopeSha256": envelope, "files": files,
        "demoBeforeCellCount": before["demoReduction"]["matrixCellCount"],
        "demoBeforeProjectedCells": len(before["demoReduction"]["cells"]),
        "archiveIndexUntouched": digest((RESULTS / "superseded/index.json").read_bytes()),
        "result": "all source keys, ordered raw row slices and whole envelope match"
    }
    output_path = HERE / "equality.json"
    blob = (json.dumps(output, indent=2) + "\n").encode()
    if output_path.exists() and output_path.read_bytes() != blob:
        raise ValueError("existing equality witness differs; refusing overwrite")
    output_path.write_bytes(blob)
    print(f"{len(spans)} row slices identical; {frozen} frozen, {moved} indexed; legacy {envelope}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"equality proof failed: {error}", file=sys.stderr)
        raise SystemExit(1)
