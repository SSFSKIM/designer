#!/usr/bin/env python3.12
"""The gated-cell count for the 0.25.0 chain, read from the current union.

    python3.12 gated-count.py

W31 G3c's `gated-count.py` (as W36 G2 copied it), with ONE change: its rows come
from W40's `matrix_store.load_current_rows()` instead of `results/matrix.json`.
Since W40 G0 (§5.189) that path holds only the 1,107 frozen macOS 26.5 rows and
the current macOS 27 rows live in `results/generations/`, so reading the file
alone would report the macOS 27 bed as empty. The filter is unchanged: a row is
AT A SHIPPED DOCUMENT when its `capturePath` names a profile document path and
the first twelve hex of that file's current SHA-256; a GATED cell is such a row
that is not `probe`, not `inactive`, and not an `__inactive` scene.
"""
from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "2026-09-26-w40-g0-generations"))
import matrix_store  # noqa: E402

CLAUSE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")
INACTIVE = re.compile(r"__inactive")


def shipped(path: str) -> str | None:
    file = ROOT / path
    if not file.is_file():
        return None
    return hashlib.sha256(file.read_bytes()).hexdigest()[:12]


def main() -> int:
    cells = matrix_store.load_current_rows()
    rows = Counter()
    gated = Counter()
    total = Counter()
    for cell in cells:
        profile = cell["key"]["profileKey"]
        os_token = "27" if "-27.0-" in profile else "26.5"
        total[os_token] += 1
        clause = CLAUSE.search(cell["key"]["web"]["capturePath"])
        if clause is None or shipped(clause.group(1)) != clause.group(2):
            continue
        rows[(os_token, profile)] += 1
        if (
            cell.get("fixtureSet") != "probe"
            and cell.get("state") != "inactive"
            and not INACTIVE.search(cell["key"]["sceneId"])
        ):
            gated[(os_token, profile)] += 1

    print("== the current union (results/matrix.json + results/generations/, matrix_store) ==")
    for os_token in ("26.5", "27"):
        print(f"\n  macOS {os_token}: {total[os_token]} row(s) in the union")
        keys = sorted(k for k in rows if k[0] == os_token)
        for key in keys:
            print(f"    {key[1]:<62} {rows[key]:>5} row(s) at a shipped document, "
                  f"{gated[key]:>4} gated")
        print(f"    {'TOTAL at a shipped document':<62} "
              f"{sum(rows[k] for k in keys):>5} row(s), {sum(gated[k] for k in keys):>4} gated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
