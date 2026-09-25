#!/usr/bin/env python3.12
"""Exercise the indexed-read witness only on disposable synthetic results trees."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

CHECKER = pathlib.Path(__file__).with_name("append-check.py")
OLD = "111111111111.json"
NEW = "222222222222.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def envelope(rows):
    return b'{\n  "schemaVersion": 5,\n  "cells": [\n    ' + b',\n    '.join(rows) + b'\n  ]\n}\n'


def row(scene, doc):
    return {"key": {"profileKey": "apple-macos-27.0-1x-light-standard-glass0.5", "sceneId": scene,
                    "web": {"engine": "chromium", "engineVersion": "1", "renderer": "webgpu",
                            "samplingBackend": "css-backdrop", "gpuAdapter": "a", "colorSpace": "srgb",
                            "capturePath": f"materialProfile=profile.json sha256:{doc}"}}, "result": scene}


def invoke(*args):
    return subprocess.run([sys.executable, str(CHECKER), *map(str, args)], text=True,
                          capture_output=True)


def fixture(root):
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    results = root / "results"
    generations = results / "generations"
    archive = results / "superseded"
    generations.mkdir(parents=True)
    archive.mkdir()
    (archive / "index.json").write_bytes(b'{"history": 1}\n')
    (archive / "old.json").write_bytes(envelope([b'{"old":true}']))
    (results / "matrix.json").write_bytes(envelope([b'{"frozen":true}']))
    old_blob = envelope([json.dumps(row("old", "111111111111"), indent=2).encode()])
    (generations / OLD).write_bytes(old_blob)
    index = {"schemaVersion": 1, "files": {OLD: {"status": "current", "rowCount": 1,
              "bytes": len(old_blob), "sha256": sha(old_blob)}}, "currentByProfile": {},
             "byDocumentSha256": {"111111111111": [OLD]}}
    (generations / "index.json").write_text(json.dumps(index) + "\n")
    stage = root / "stage.json"
    stage_rows = [json.dumps(row(scene, "222222222222"), indent=2, ensure_ascii=False).encode()
                  for scene in ("alpha", "beta")]
    stage.write_bytes(envelope(stage_rows))
    witness = root / "before.json"
    assert invoke("snapshot", results, witness).returncode == 0
    published = envelope(stage_rows)
    (generations / NEW).write_bytes(published)
    index["files"][OLD]["status"] = "retired"
    index["byDocumentSha256"]["222222222222"] = [NEW]
    index["files"][NEW] = {"status": "current", "rowCount": 2,
                            "bytes": len(published), "sha256": sha(published)}
    (generations / "index.json").write_text(json.dumps(index) + "\n")
    return results, witness, stage


def check(label, change, reason):
    with tempfile.TemporaryDirectory(prefix="w40-append-check-") as temporary:
        results, witness, stage = fixture(pathlib.Path(temporary))
        change(results, stage)
        result = invoke("verify", results, witness, stage, NEW)
        if reason is None:
            assert result.returncode == 0, (label, result.stderr, result.stdout)
        else:
            assert result.returncode != 0 and reason in result.stderr, (label, result.stderr, result.stdout)
        print(f"{label}: {'PASS' if reason is None else 'REFUSED'}")
        if reason is None:
            print(result.stdout, end="")


def main():
    check("unaltered append", lambda _r, _s: None, None)
    check("frozen mutation", lambda r, _s: (r / "matrix.json").write_bytes(b"changed"), "frozen")
    check("previous generation mutation", lambda r, _s: (r / "generations" / OLD).write_bytes(b"changed"), "generation")
    check("previous generation removal", lambda r, _s: (r / "generations" / OLD).unlink(), "generation")
    check("archive mutation", lambda r, _s: (r / "superseded" / "old.json").write_bytes(b"changed"), "archive")
    check("archive addition", lambda r, _s: (r / "superseded" / "new.json").write_bytes(b"new"), "archive")
    check("archive removal", lambda r, _s: (r / "superseded" / "old.json").unlink(), "archive")
    def reserialize(r, _s):
        path = r / "generations" / NEW
        blob = envelope([json.dumps(row(scene, "222222222222"), separators=(",", ":")).encode()
                         for scene in ("alpha", "beta")])
        path.write_bytes(blob)
        index_path = r / "generations" / "index.json"
        index = json.loads(index_path.read_bytes())
        index["files"][NEW].update(bytes=len(blob), sha256=sha(blob))
        index_path.write_text(json.dumps(index) + "\n")
    check("JSON-equivalent reserialization", reserialize, "raw stage")
    def missing(r, _s):
        path = r / "generations" / NEW
        blob = envelope([json.dumps(row("alpha", "222222222222"), indent=2).encode()])
        path.write_bytes(blob)
        index_path = r / "generations" / "index.json"
        index = json.loads(index_path.read_bytes())
        index["files"][NEW].update(bytes=len(blob), sha256=sha(blob), rowCount=1)
        index_path.write_text(json.dumps(index) + "\n")
    check("missing staged row", missing, "stage")
    def extra(r, _s):
        path = r / "generations" / NEW
        rows = [json.dumps(row(scene, "222222222222"), indent=2).encode()
                for scene in ("alpha", "beta", "gamma")]
        blob = envelope(rows)
        path.write_bytes(blob)
        index_path = r / "generations" / "index.json"
        index = json.loads(index_path.read_bytes())
        index["files"][NEW].update(bytes=len(blob), sha256=sha(blob), rowCount=3)
        index_path.write_text(json.dumps(index) + "\n")
    check("extra published row", extra, "stage")
    def unindexed(r, _s):
        index_path = r / "generations" / "index.json"
        index = json.loads(index_path.read_bytes())
        del index["files"][NEW]
        index_path.write_text(json.dumps(index) + "\n")
    check("unindexed publication", unindexed, "index")
    def repoint_alias(r, _s):
        path = r / "generations/index.json"
        index = json.loads(path.read_bytes())
        index["byDocumentSha256"]["111111111111"] = [NEW]
        path.write_text(json.dumps(index) + "\n")
    check("historical alias repoint", repoint_alias, "alias")
    def rewrite_old_metadata(r, _s):
        path = r / "generations/index.json"
        index = json.loads(path.read_bytes())
        index["files"][OLD]["rowCount"] = 2
        path.write_text(json.dumps(index) + "\n")
    check("historical index metadata rewrite", rewrite_old_metadata, "index entry")
    with tempfile.TemporaryDirectory(prefix="w40-append-check-") as temporary:
        results, witness, stage = fixture(pathlib.Path(temporary))
        first = witness.read_bytes()
        second = invoke("snapshot", results, witness)
        assert second.returncode != 0 and witness.read_bytes() == first
        print("snapshot overwrite: REFUSED")


if __name__ == "__main__":
    main()
