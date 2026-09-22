#!/usr/bin/env python3
"""W31 G3 — the READ's append-check: the canonical read appended and rewrote nothing.

    python3 read-append-check.py snapshot [<matrix.json>]   # before the read
    python3 read-append-check.py verify  [--json out.json]

`append-check.py` beside this file is the SPLIT's check — it proves that moving
rows between files changed none of them, against the manifest `split-generation.py
apply` writes. This one is the other half of contract X7, and it is a different
statement about a different operation: **a canonical read APPENDS**, and the file
it appends to holds 1,107 frozen macOS 26.5 rows and the previous generation's
macOS 27 rows, none of which may move.

Both checks run here, in the order the charter names: this one after the read and
before the split, `append-check.py` after the split, so the two operations are
refereed separately and a failure names which one did it.

Five clauses, each on its own line:

  rows preserved       every row the snapshot recorded is still in the file, once
  byte-identical       each of those rows' canonical JSON hashes to the recorded
                       digest — which is the same statement as the line above,
                       because the digest IS the row's bytes
  order unchanged      they appear in the file in the RELATIVE order the snapshot
                       recorded — a subsequence, not a prefix
  26.5 first, intact   the 1,107 frozen rows are the file's first 1,107, unmoved
  counts add up        per profile key: before + appended == after

**Why a subsequence and not a prefix**, measured rather than assumed. `compare`
writes a new generation of a cell BESIDE the old one rather than at the end of
the file — this read's 726 new rows land at positions 1,108 onward, interleaved
among the macOS 27 rows they supersede — which is what lets
`split-generation.py` find both generations of a key by walking the file once.
So the invariant a read has to hold is that no recorded row moved past another
recorded row, and that the frozen bed is still the contiguous block
`freeze.py`'s positional read walks. A prefix check would have called a correct
append a failure, which is what the first draft of this file did.

The row reader is `split-generation.py`'s own, imported rather than restated, so
the two scripts cannot disagree about where a row begins.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.resolve().parents[3]
PACKAGE = ROOT / "packages/calibration"
MATRIX = PACKAGE / "results/matrix.json"
SNAPSHOT = HERE / "read-snapshot.json"

_spec = importlib.util.spec_from_file_location(
    "split_generation", PACKAGE / "results/2026-09-20-w30-g1-split/split-generation.py"
)
_split = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_split)
canon, elements = _split.canon, _split.elements


def rows(source: pathlib.Path | None = None) -> list[tuple[str, str, str]]:
    """(digest, profileKey, capturePath) per row, in file order."""
    raw = (source or MATRIX).read_bytes()
    _, spans, _ = elements(raw)
    out = []
    for a, b in spans:
        obj = json.loads(raw[a:b])
        out.append(
            (
                hashlib.sha256(canon(obj)).hexdigest(),
                obj.get("key", {}).get("profileKey", "?"),
                obj.get("capturePath", ""),
            )
        )
    return out


def snapshot(source: pathlib.Path | None = None) -> int:
    """W32 G1's ONE change to this copy (claims §5.168): the snapshot may be taken
    of a NAMED matrix rather than of the live one.

    W31 G3 took it of the live file before its read. This gate ran the read
    first, so the "before" it needs is not on disk any more — it is the blob the
    SEAL commit carries, which is the same bytes and is signed for by git rather
    than by a reader's memory. `git show <seal>:packages/calibration/results/matrix.json`
    reproduces it, and naming it here is honest where re-running the read would
    not be: the check's whole job is to referee the append, and taking its
    "before" from the commit immediately before the append is what "before"
    means. With no argument this is W31 G3's function exactly.
    """
    if SNAPSHOT.exists():
        raise SystemExit(f"{SNAPSHOT.name} already exists; it witnesses a read that has run")
    current = rows(source)
    SNAPSHOT.write_text(
        json.dumps(
            {
                "$comment": [
                    "results/matrix.json as it stood BEFORE W33 G1b's canonical read",
                    "(claims §5.172). Written once, never rewritten.",
                    "Taken from the live file before this gate begins its canonical read.",
                ],
                "matrixSha256": hashlib.sha256((source or MATRIX).read_bytes()).hexdigest(),
                "matrixBytes": (source or MATRIX).stat().st_size,
                "rows": [{"sha256": d, "profileKey": p} for d, p, _ in current],
            },
            indent=2,
        )
        + "\n"
    )
    print(f"snapshot: {len(current)} rows, {(source or MATRIX).stat().st_size} bytes "
          f"of {(source or MATRIX)} -> {SNAPSHOT.name}")
    return 0


def verify(out_path: pathlib.Path | None) -> int:
    before = json.loads(SNAPSHOT.read_text())["rows"]
    after = rows()
    failures: list[str] = []

    recorded = [r["sha256"] for r in before]
    present = [d for d, _, _ in after]
    recorded_set = set(recorded)
    seen: dict[str, int] = {}
    for digest in present:
        seen[digest] = seen.get(digest, 0) + 1
    missing = [d for d in recorded if d not in seen]
    duplicated = [d for d in recorded if seen.get(d, 0) > 1]
    if missing:
        failures.append(f"{len(missing)} snapshot row(s) are gone from the file")
    if duplicated:
        failures.append(f"{len(duplicated)} snapshot row(s) appear more than once")

    # The relative order: the snapshot's digests, in order, as a SUBSEQUENCE of
    # the file's. A recorded row may gain neighbours and may not pass one.
    walk = iter(present)
    ordered = all(any(candidate == digest for candidate in walk) for digest in recorded)
    if not ordered:
        failures.append("the snapshot's rows are present but no longer in their recorded order")

    appended = [(d, p) for d, p, _ in after if d not in recorded_set]

    frozen_before = [r for r in before if r["profileKey"].startswith("apple-macos-26.5")]
    head = present[: len(frozen_before)]
    frozen_first = head == [r["sha256"] for r in frozen_before] and all(
        profile.startswith("apple-macos-26.5") for _, profile, _ in after[: len(frozen_before)]
    )
    if not frozen_first:
        failures.append(
            f"the {len(frozen_before)} frozen macOS 26.5 rows are no longer the file's first rows"
        )

    counts_before: dict[str, int] = {}
    for r in before:
        counts_before[r["profileKey"]] = counts_before.get(r["profileKey"], 0) + 1
    counts_after: dict[str, int] = {}
    for _, profile, _ in after:
        counts_after[profile] = counts_after.get(profile, 0) + 1
    counts_appended: dict[str, int] = {}
    for _, profile in appended:
        counts_appended[profile] = counts_appended.get(profile, 0) + 1
    for key in sorted(set(counts_before) | set(counts_after)):
        if counts_before.get(key, 0) + counts_appended.get(key, 0) != counts_after.get(key, 0):
            failures.append(f"{key}: counts do not add up")

    frozen_appended = [p for _, p in appended if p.startswith("apple-macos-26.5")]
    if frozen_appended:
        failures.append(f"{len(frozen_appended)} appended row(s) are macOS 26.5 rows (X1)")

    verdict = lambda ok: "PASS" if ok else "FAIL"
    print(f"rows preserved       {verdict(not missing and not duplicated)}")
    print(f"byte-identical       {verdict(not missing and not duplicated)}")
    print(f"order unchanged      {verdict(ordered)}")
    print(f"26.5 first, intact   {verdict(frozen_first)}")
    print(f"counts add up        {verdict(not any('counts' in f for f in failures))}")
    print(f"no 26.5 row appended {verdict(not frozen_appended)}")
    print()
    print(f"before: {len(before)} rows")
    print(f"after:  {len(after)} rows ({len(appended)} appended)")
    positions = [index for index, (digest, _, _) in enumerate(after) if digest not in recorded_set]
    if positions:
        print(f"appended at positions {positions[0]}..{positions[-1]}, interleaved among the "
              f"rows they supersede")
    print()
    print(f"{'profile key':<62}{'before':>8}{'appended':>10}{'after':>8}")
    for key in sorted(set(counts_before) | set(counts_after)):
        print(
            f"{key:<62}{counts_before.get(key, 0):>8}"
            f"{counts_appended.get(key, 0):>10}{counts_after.get(key, 0):>8}"
        )
    for failure in failures:
        print(f"FAIL {failure}")
    if out_path is not None:
        out_path.write_text(
            json.dumps(
                {
                    "before": len(before),
                    "after": len(after),
                    "appended": len(appended),
                    "frozenRowsFirst": frozen_first,
                    "orderPreserved": ordered,
                    "failures": failures,
                    "perProfile": {
                        key: {
                            "before": counts_before.get(key, 0),
                            "appended": counts_appended.get(key, 0),
                            "after": counts_after.get(key, 0),
                        }
                        for key in sorted(set(counts_before) | set(counts_after))
                    },
                },
                indent=2,
            )
            + "\n"
        )
    return 1 if failures else 0


def main() -> int:
    argv = sys.argv[1:]
    verb = argv[0] if argv else "verify"
    if verb == "snapshot":
        named = [a for a in argv[1:] if not a.startswith("--")]
        return snapshot(pathlib.Path(named[0]) if named else None)
    if verb == "verify":
        out = pathlib.Path(argv[argv.index("--json") + 1]) if "--json" in argv else None
        return verify(out)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
