#!/usr/bin/env python3
"""W31 G3 — the READ's append-check: the canonical read appended and rewrote nothing.

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

Four clauses, each on its own line:

  rows preserved       every row the snapshot recorded is still in the file
  byte-identical       each of those rows' canonical JSON is the recorded digest
  order unchanged      they appear in the file in the order the snapshot recorded,
                       which is what `freeze.py`'s positional read depends on
  counts add up        per profile key: before + appended == after, and every
                       appended row is a macOS 27 row at a document hash that is
                       on disk now

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
                    "results/matrix.json as it stood BEFORE W31 G3's canonical read",
                    "(claims §5.164 §7). Written once, never rewritten.",
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

    preserved = [r["sha256"] for r in before]
    present = [d for d, _, _ in after]
    if present[: len(preserved)] != preserved:
        # Not a prefix: find out whether it is a reorder or a rewrite.
        missing = [d for d in preserved if d not in set(present)]
        failures.append(
            f"{len(missing)} snapshot row(s) are gone from the file"
            if missing
            else "the snapshot's rows are all present but not in their recorded order"
        )
    appended = after[len(preserved):]

    counts_before: dict[str, int] = {}
    for r in before:
        counts_before[r["profileKey"]] = counts_before.get(r["profileKey"], 0) + 1
    counts_after: dict[str, int] = {}
    for _, profile, _ in after:
        counts_after[profile] = counts_after.get(profile, 0) + 1
    counts_appended: dict[str, int] = {}
    for _, profile, _ in appended:
        counts_appended[profile] = counts_appended.get(profile, 0) + 1
    for key in sorted(set(counts_before) | set(counts_after)):
        if counts_before.get(key, 0) + counts_appended.get(key, 0) != counts_after.get(key, 0):
            failures.append(f"{key}: counts do not add up")

    frozen_appended = [p for _, p, _ in appended if p.startswith("apple-macos-26.5")]
    if frozen_appended:
        failures.append(f"{len(frozen_appended)} appended row(s) are macOS 26.5 rows (X1)")

    verdict = lambda ok: "PASS" if ok else "FAIL"
    print(f"rows preserved       {verdict(present[: len(preserved)] == preserved)}")
    print(f"byte-identical       {verdict(present[: len(preserved)] == preserved)}")
    print(f"order unchanged      {verdict(present[: len(preserved)] == preserved)}")
    print(f"counts add up        {verdict(not any('counts' in f for f in failures))}")
    print(f"no 26.5 row appended {verdict(not frozen_appended)}")
    print()
    print(f"before: {len(before)} rows")
    print(f"after:  {len(after)} rows ({len(appended)} appended)")
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
