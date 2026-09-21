#!/usr/bin/env python3
"""W31 G3 — the holdout rule, enforced by artifact (Decision Log 1 (b) and 2 (e); claims §5.164 §6).

    python3 configuration.py show                       # print the configuration, change nothing
    python3 configuration.py record --claims "c9a §5.164"
    python3 configuration.py record --claims "…" --source-moved-because "<a non-fit reason>"

W31 Decision Log 1 (b), ruled: **a frozen configuration is (the shipped document
bytes, the renderer's material-affecting sources); the holdout is read once per
configuration; no fitted constant may change between two holdout reads of the
same document bytes.** A renderer fix after a read may be re-read once and
disclosed as such; a fit may not.

W30 read the holdout twice at one document set — G3 at the sealed documents and
G3b again after a renderer fix with no constant moved — and its review said a
third read would need a ruling naming "the smallest thing that makes a
configuration new" (§5.159b §10, finding 13). The ruling exists; this file is the
part that cannot be forgotten. It is a committed LOG, not a check that reads the
world: `configuration-log.json` beside it records every holdout read this
material has had, and the refusal is against that record.

## What the configuration is

  * the four macOS 27 profile documents' FILE hashes — the bytes a
    `capturePath` is keyed under, and the thing `atAShippedDocument` reads;
  * a SHA-256 over an enumerated source list, in sorted path order, each file's
    bytes preceded by its repo-relative path: `packages/renderer-webgpu/src/wgsl/`
    (every file), `src/material.ts`, `src/renderer.ts`, `src/passes.ts`, and
    `packages/platform-web/src/{optics,css-tier}.ts`.

The list is the charter's, verbatim (acceptance clause 6), and it is a list
rather than a tree because a hash over everything would move on a comment in a
test and say nothing about the material.

## What it refuses, and what it cannot see

**Refused**: a second `record` at document hashes already in the log, unless the
SOURCE hash has moved *and* `--source-moved-because` names a reason. Both halves
are required: a reason without a moved source is a fit being called a fix, and a
moved source without a reason is a change nobody wrote down.

**Not seen, and named rather than left implicit**: a fit that moves a value out
of a document and into a shader default is a document change AND a source change,
and it is caught as the former — the document hashes move, so the read is a new
configuration and the rule does not apply. That is the ruling's own wording and
not a hole in it.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent
LOG = HERE / "configuration-log.json"

DOCUMENTS = [
    "packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5.json",
    "packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json",
    "packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json",
    "packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json",
]

SOURCE_LIST = [
    "packages/renderer-webgpu/src/wgsl",          # every file in it
    "packages/renderer-webgpu/src/material.ts",
    "packages/renderer-webgpu/src/renderer.ts",
    "packages/renderer-webgpu/src/passes.ts",
    "packages/platform-web/src/optics.ts",
    "packages/platform-web/src/css-tier.ts",
]


def source_files() -> list[Path]:
    out: list[Path] = []
    for entry in SOURCE_LIST:
        path = ROOT / entry
        if path.is_dir():
            out += sorted(p for p in path.rglob("*") if p.is_file())
        elif path.is_file():
            out.append(path)
        else:
            raise SystemExit(f"configuration: {entry} is neither a file nor a directory")
    return sorted(out)


def source_hash() -> tuple[str, list[str]]:
    """One digest over the enumerated sources, path-qualified and order-stable."""
    digest = hashlib.sha256()
    names = []
    for path in source_files():
        rel = str(path.relative_to(ROOT))
        names.append(rel)
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest(), names


def document_hashes() -> dict[str, str]:
    out = {}
    for entry in DOCUMENTS:
        path = ROOT / entry
        out[Path(entry).name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def head() -> str:
    got = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return got.stdout.strip() if got.returncode == 0 else "unknown"


def load_log() -> list[dict]:
    return json.loads(LOG.read_text())["reads"] if LOG.exists() else []


def show() -> dict:
    documents = document_hashes()
    sources, names = source_hash()
    print("== the frozen configuration (W31 Decision Log 1 (b)) ==")
    print(f"  head                {head()}")
    for name, digest in documents.items():
        print(f"  {name:<52} {digest}")
    print(f"  source list         {len(names)} files")
    for name in names:
        print(f"    {name}")
    print(f"  SOURCE SHA-256      {sources}")
    return {"documents": documents, "sourceSha256": sources, "sourceFiles": names}


def record(claims: str, reason: str | None) -> int:
    state = show()
    previous = load_log()
    same_documents = [e for e in previous if e["documents"] == state["documents"]]
    if same_documents:
        prior = same_documents[-1]
        print("\n-- a holdout read already exists at these document hashes --")
        print(f"   {prior['at']}  head {prior['head']}  claims {prior['claims']}")
        if prior["sourceSha256"] == state["sourceSha256"]:
            print("\nREFUSED: identical document bytes AND identical sources. This is the same")
            print("frozen configuration the holdout was already read at (Decision Log 1 (b)).")
            return 1
        if not reason:
            print("\nREFUSED: the sources moved and no reason is named. A second read of the same")
            print("document bytes is allowed only for a NON-FIT reason, named on the command line")
            print("with --source-moved-because and recorded here (Decision Log 1 (b)).")
            return 1
        print(f"\n   the sources moved; reason given: {reason}")
    entry = {
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "head": head(),
        "claims": claims,
        "documents": state["documents"],
        "sourceSha256": state["sourceSha256"],
        "sourceFileCount": len(state["sourceFiles"]),
    }
    if reason:
        entry["sourceMovedBecause"] = reason
    LOG.write_text(
        json.dumps(
            {
                "$comment": [
                    "Every holdout read of the macOS 27 bed, by frozen configuration",
                    "(W31 Decision Log 1 (b); claims §5.164 §6). APPEND-ONLY: a recorded",
                    "read is never rewritten, and `configuration.py record` refuses a",
                    "second entry at document hashes already here unless the source hash",
                    "moved for a named non-fit reason.",
                ],
                "reads": [*previous, entry],
            },
            indent=2,
        )
        + "\n"
    )
    print(f"\nRECORDED — holdout read {len(previous) + 1} at this configuration. {LOG.name} updated.")
    return 0


def main() -> int:
    argv = sys.argv[1:]
    verb = argv[0] if argv else "show"
    if verb == "show":
        show()
        return 0
    if verb == "record":
        claims = argv[argv.index("--claims") + 1] if "--claims" in argv else "unstated"
        reason = (
            argv[argv.index("--source-moved-because") + 1]
            if "--source-moved-because" in argv
            else None
        )
        return record(claims, reason)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
