#!/usr/bin/env python3
"""The holdout rule, enforced by artifact — the CROSS-GATE copy (W31 Decision Log 1 (b) and 2 (e);
claims §5.164 §6, §5.167).

    python3 packages/calibration/results/holdout-configuration/configuration.py show
    python3 …/configuration.py record --claims "c9a §5.168"
    python3 …/configuration.py record --claims "…" --source-moved-because "<a non-fit reason>"

**This is the location every canonical holdout read records to, from W32 onward.** W31 G3 wrote
this script into its own evidence directory and W31 G3c ran that copy in place, which worked and
was not a rule: every script under `results/` is copied per gate by convention, and **a copy
starts with an empty log**, so the next gate that copied rather than reached back would have made
the refusal blind to every read before it — one keeps the rule and one silently retires it, with
nothing saying which (W31 Deferred item 14; tracker, "The holdout configuration log is a
cross-gate ledger living inside one gate's evidence directory"). The ledger is now a directory of
its own, named for what it holds rather than for the gate that first needed it, and it is not
copied.

W31 G3's `configuration.py` and its `configuration-log.json` **stay byte-identical where they
are** at `results/2026-09-21-w31-g3-chroma-fit/` — they are that gate's committed witness and a
committed witness is never edited. This log is SEEDED from theirs, byte for byte, so the record
those two reads made is unbroken across the move: the two entries below `reads` are W31 G3's and
W31 G3c's, at the bytes they wrote them.

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

**The list is narrower than "everything that affects the render", and W32 G0b
measured by how much rather than asserting it either way** (claims §5.167;
`source-list-closure.txt` in that gate's evidence). Following the local import
graph out of the five named TypeScript entry points reaches **50 further files**
the list does not name, and they are not all plumbing: `analysis.ts`,
`silhouette-tone.ts`, `instances.ts`, `backdrop-fit.ts`, `color.ts`, `pyramid.ts`,
`pyramid-plan.ts` and `render-model.ts` on the renderer side, and
`css-tier-layers.ts`, `css-tier-shadow.ts`, `backdrop-tone.ts`, `refraction.ts`,
`tint.ts`, `vibrancy.ts`, `material-document.ts`, `macos27-profile.ts`,
`dark-profile.ts`, `receded-profile.ts`, `window-activation.ts` and
`media-policy.ts` on the web side, each of which can move a capture's pixels at
unmoved document bytes. `renderer-bridge.ts` — asked about by name — holds no
material constant and no material arithmetic (its one conversion, `linearTint`,
is `optics.ts`'s and is on the list), but it decides WHICH material reaches the
renderer: the `setMaterialProfile` forwarding, the `unsampledMaterial` assembly
and the accessibility hand-off. So it is material-affecting in the routing sense
and it is one of fifty, not a special case.

**The list is nevertheless unchanged here, and that is a decision rather than an
oversight.** Widening it changes what a configuration IS, which is W31 Decision
Log 1 (b)'s subject and a ruling to take rather than a copy to make; and it would
break the artifact it is meant to sharpen, because the refusal's second half
compares today's `sourceSha256` against a LOGGED one — a hash under a different
definition is not a different hash, it is an incomparable one, so a widened list
would report "the sources moved" at every read forever and retire the rule more
thoroughly than the fork this move exists to prevent. The honest widening is also
not a handful of names: it is the module closure, which is the "hash over
everything" the paragraph above rejects for cause. What this gate adds instead is
`sourceListSha256` — a digest of the DEFINITION, recorded beside the digest of
the sources — so that a later widening is visible in the record rather than
silent in it, and a reader comparing two `sourceSha256` values can see whether
they were taken over the same list. The fix shape (a declared list checked
against the closure, or a closure hash with a declared ignore list; either is a
ruling) is a tracker entry.

## What it refuses, and what it cannot see

**Refused**: a second `record` at document hashes already in the log, unless the
SOURCE hash is one *no* record at those documents carries *and*
`--source-moved-because` names a reason. Both halves are required: a reason
without a moved source is a fit being called a fix, and a moved source without a
reason is a change nobody wrote down.

**The comparison is against EVERY record at those documents, not the last one**
(W32 G0b review closure, finding NB1; claims §5.167 §8). A configuration is a set
of bytes, not a position in a list: sources that move away and then back land on a
configuration the holdout has already been read at, and reading it a second time
is the thing Decision Log 1 (b) forbids however many reads sit in between. So a
named reason cannot re-open a configuration already read — `--source-moved-because`
admits a read at sources this log has never seen at these documents, and nothing
else. The refusal says so when a reason was given.

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


def source_list_hash() -> str:
    """A digest of the source LIST, not of the sources.

    `sourceSha256` is only comparable across two reads that took it over the same
    enumeration. Recording the enumeration's own digest makes a change of
    definition a visible field rather than an invisible one — see the docstring's
    paragraph on why the list is not widened here.
    """
    digest = hashlib.sha256()
    for entry in SOURCE_LIST:
        digest.update(entry.encode())
        digest.update(b"\0")
    return digest.hexdigest()


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
    print(f"  source LIST SHA-256 {source_list_hash()}   (the enumeration, not the bytes)")
    return {"documents": documents, "sourceSha256": sources, "sourceFiles": names}


def record(claims: str, reason: str | None) -> int:
    state = show()
    previous = load_log()
    same_documents = [e for e in previous if e["documents"] == state["documents"]]
    if same_documents:
        print("\n-- a holdout read already exists at these document hashes --")
        for entry in same_documents:
            print(f"   {entry['at']}  head {entry['head']}  claims {entry['claims']}"
                  f"  sources {entry['sourceSha256'][:12]}…")
        # Against EVERY record at these documents rather than the newest: sources that move
        # away and back land on a configuration already read, and the reads in between do
        # not make it a new one (W32 G0b review closure, NB1; claims §5.167 §8).
        already = [e for e in same_documents if e["sourceSha256"] == state["sourceSha256"]]
        if already:
            first = already[0]
            print("\nREFUSED: identical document bytes AND identical sources. This is the same")
            print("frozen configuration the holdout was already read at (Decision Log 1 (b)) —")
            print(f"{first['at']}, head {first['head']}, claims {first['claims']}.")
            if reason:
                print("\n--source-moved-because names a reason the SOURCES moved. It cannot re-open a")
                print("configuration already read: the sources are back at bytes this log already")
                print("carries a read at, so there is no move for a reason to explain.")
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
        "sourceListSha256": source_list_hash(),
    }
    if reason:
        entry["sourceMovedBecause"] = reason
    LOG.write_text(
        json.dumps(
            {
                "$comment": [
                    "Every holdout read of the macOS 27 bed, by frozen configuration",
                    "(W31 Decision Log 1 (b); claims §5.164 §6, §5.167). APPEND-ONLY: a",
                    "recorded read is never rewritten, and `configuration.py record`",
                    "refuses a second entry at document hashes already here unless the",
                    "source hash moved for a named non-fit reason.",
                    "",
                    "This is the CROSS-GATE ledger at results/holdout-configuration/,",
                    "seeded byte for byte from W31 G3's log at W32 G0b and not copied",
                    "per gate: a copy starts empty, and an empty log refuses nothing.",
                    "The first two reads below are W31 G3's and W31 G3c's, and they",
                    "predate `sourceListSha256`, which W32 G0b added so that a later",
                    "widening of the source list is visible in the record.",
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
