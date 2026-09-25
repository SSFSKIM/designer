#!/usr/bin/env python3.12
"""Witness one indexed generation publication without rewriting any prior evidence.

    python3.12 append-check.py snapshot <results> <witness.json>        # BEFORE read
    python3.12 append-check.py verify <results> <witness.json> <stage/matrix.json> <published filename>  # AFTER publication

Keep the witness outside <results>. The stage is the COMPLETE scratch matrix used for
this one publication; take the snapshot before the read starts, then verify the
published file before landing the read. This checks raw row slices, not parsed JSON
re-encoded by a checker. W30/W36 witnesses still describe their original layouts.
"""
import hashlib
import json
import pathlib
import sys

# G0's splitter-derived slicer and serialized cell key are the same ones used
# to prove that the migration preserved each recorded row's original bytes.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] /
                       "2026-09-26-w40-g0-generations"))
from snapshot import key, slices  # noqa: E402


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(directory):
    """Include archived index and every nested historical file, not just known aliases."""
    require(directory.is_dir(), f"archive directory missing: {directory}")
    return {str(path.relative_to(directory)): digest(path.read_bytes())
            for path in sorted(directory.rglob("*")) if path.is_file()}


def generations(results):
    directory = results / "generations"
    require(directory.is_dir(), f"generation directory missing: {directory}")
    return {path.name: digest(path.read_bytes()) for path in sorted(directory.iterdir())
            if path.is_file() and path.name != "index.json"}


def index_at(results):
    index = json.loads((results / "generations/index.json").read_bytes())
    require(index["schemaVersion"] == 1 and isinstance(index["files"], dict),
            "invalid generation index")
    return index


def read_rows(path):
    raw = path.read_bytes()
    spans, _, _, _ = slices(raw)
    by_key = {}
    for start, end in spans:
        piece = raw[start:end]
        identity = key(json.loads(piece))
        require(identity not in by_key, f"duplicate serialized key in {path}: {identity}")
        by_key[identity] = piece
    return by_key


def snapshot(results, witness):
    require(results.is_dir(), f"results directory missing: {results}")
    require(not witness.exists(), f"witness already exists; refusing overwrite: {witness}")
    require(not witness.is_relative_to(results), "witness must be outside results")
    index = index_at(results)
    previous = generations(results)
    require(set(previous) == set(index["files"]), "generation files differ from index before read")
    recorded = {"schemaVersion": 1, "results": str(results),
                "frozen": digest((results / "matrix.json").read_bytes()),
                "generations": previous, "archive": inventory(results / "superseded"),
                "indexedFiles": index["files"],
                "aliases": index.get("byDocumentSha256", {})}
    with witness.open("xb") as target:
        target.write((json.dumps(recorded, indent=2, sort_keys=True) + "\n").encode())
    print(f"snapshot: frozen + {len(previous)} published generation(s) + "
          f"{len(recorded['archive'])} archive file(s); {witness}")


def verify(results, witness, stage, filename):
    before = json.loads(witness.read_bytes())
    require(before["schemaVersion"] == 1 and before["results"] == str(results),
            "witness belongs to a different results directory or schema")
    require(filename == pathlib.Path(filename).name and filename.endswith(".json") and
            filename != "index.json", "published filename must be a generation basename")
    require(filename not in before["generations"], "published filename existed before read")
    require(digest((results / "matrix.json").read_bytes()) == before["frozen"],
            "frozen matrix bytes changed")
    after_files = generations(results)
    require(set(after_files) == set(before["generations"]) | {filename},
            "generation file set changed beyond the one publication")
    for name, original in before["generations"].items():
        require(after_files[name] == original, f"previously published generation bytes changed: {name}")
    require(inventory(results / "superseded") == before["archive"],
            "archive bytes or file set changed")
    index = index_at(results)
    require(set(index["files"]) == set(after_files), "generation index does not name exactly the files")
    for name, original in before["indexedFiles"].items():
        entry = index["files"][name]
        require({k: v for k, v in entry.items() if k != "status"} ==
                {k: v for k, v in original.items() if k != "status"},
                f"previously published generation index entry changed: {name}")
    for alias, owners in before["aliases"].items():
        prior = owners if isinstance(owners, list) else [owners]
        now = index.get("byDocumentSha256", {}).get(alias, [])
        current = now if isinstance(now, list) else [now]
        require(set(prior) <= set(current), f"previously published document alias changed: {alias}")
    published = results / "generations" / filename
    entry = index["files"][filename]
    raw = published.read_bytes()
    require(entry["status"] == "current" and entry["rowCount"] > 0 and
            entry["rowCount"] == len(read_rows(published)) and
            entry["bytes"] == len(raw) and entry["sha256"] == digest(raw),
            "new generation index metadata does not describe published bytes")
    staged_rows = read_rows(stage)
    published_rows = read_rows(published)
    require(staged_rows and staged_rows.keys() == published_rows.keys(),
            "published rows differ from stage membership (missing or extra key)")
    for identity, original in staged_rows.items():
        require(published_rows[identity] == original,
                f"published row differs from raw stage byte slice: {identity}")
    print(f"PASS frozen bytes unchanged; {len(before['generations'])} prior generation(s) "
          f"byte-identical; archive untouched ({len(before['archive'])} file(s))")
    print(f"PASS {len(staged_rows)} published row(s) exactly match raw stage byte slices by key: {filename}")


def main(argv):
    if len(argv) == 3 and argv[0] == "snapshot":
        snapshot(pathlib.Path(argv[1]).resolve(), pathlib.Path(argv[2]).resolve())
    elif len(argv) == 5 and argv[0] == "verify":
        verify(pathlib.Path(argv[1]).resolve(), pathlib.Path(argv[2]).resolve(),
               pathlib.Path(argv[3]).resolve(), argv[4])
    else:
        raise ValueError(__doc__)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"append-check refused: {error}", file=sys.stderr)
        raise SystemExit(1)
