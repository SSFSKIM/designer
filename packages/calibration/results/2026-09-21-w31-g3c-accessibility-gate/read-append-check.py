#!/usr/bin/env python3
"""W31 G3c — the READ's append-check: the canonical read appended and rewrote nothing.

    python3 read-append-check.py snapshot           # before the read
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
  counts add up        per profile key: before + appended == after, both read off
                       the file and the snapshot rather than off a plan
  dark 27 untouched    no row of a macOS 27 DARK profile was appended, and every
                       one the snapshot recorded is still there at its own bytes —
                       this gate moved the two LIGHT documents only (X10)

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


def rows() -> list[tuple[str, str, str]]:
    """(digest, profileKey, capturePath) per row, in file order."""
    raw = MATRIX.read_bytes()
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


def snapshot() -> int:
    if SNAPSHOT.exists():
        raise SystemExit(f"{SNAPSHOT.name} already exists; it witnesses a read that has run")
    current = rows()
    SNAPSHOT.write_text(
        json.dumps(
            {
                "$comment": [
                    "results/matrix.json as it stood BEFORE W31 G3c's canonical read",
                    "(claims §5.164 §13). Written once, never rewritten.",
                ],
                "matrixSha256": hashlib.sha256(MATRIX.read_bytes()).hexdigest(),
                "matrixBytes": MATRIX.stat().st_size,
                "rows": [{"sha256": d, "profileKey": p} for d, p, _ in current],
            },
            indent=2,
        )
        + "\n"
    )
    print(f"snapshot: {len(current)} rows, {MATRIX.stat().st_size} bytes -> {SNAPSHOT.name}")
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

    # The clause this gate adds: the macOS 27 DARK bed is not in the read at all.
    # Its two documents did not move, its rows are not superseded, and a row
    # appended under one of its keys would mean the read captured a profile it
    # had no reason to and would leave two generations of a live cell behind.
    DARK27 = lambda key: "-27.0-" in key and "-dark-" in key
    dark_appended = [p for _, p in appended if DARK27(p)]
    dark_before = {r["sha256"] for r in before if DARK27(r["profileKey"])}
    dark_after = {d for d, p, _ in after if DARK27(p)}
    dark_intact = dark_before == dark_after
    if dark_appended:
        failures.append(
            f"{len(dark_appended)} appended row(s) are macOS 27 DARK rows — this gate moved "
            f"the two LIGHT documents only (X10)"
        )
    if not dark_intact:
        failures.append(
            f"the macOS 27 dark rows are not the snapshot's: {len(dark_before)} before, "
            f"{len(dark_after)} after"
        )

    verdict = lambda ok: "PASS" if ok else "FAIL"
    print(f"rows preserved       {verdict(not missing and not duplicated)}")
    print(f"byte-identical       {verdict(not missing and not duplicated)}")
    print(f"order unchanged      {verdict(ordered)}")
    print(f"26.5 first, intact   {verdict(frozen_first)}")
    print(f"counts add up        {verdict(not any('counts' in f for f in failures))}")
    print(f"no 26.5 row appended {verdict(not frozen_appended)}")
    print(f"dark 27 untouched    {verdict(not dark_appended and dark_intact)}")
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
                    "dark27Untouched": not dark_appended and dark_intact,
                    "dark27Rows": len(dark_after),
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
        return snapshot()
    if verb == "verify":
        out = pathlib.Path(argv[argv.index("--json") + 1]) if "--json" in argv else None
        return verify(out)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
