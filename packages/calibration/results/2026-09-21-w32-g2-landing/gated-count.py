#!/usr/bin/env python3
"""W31 G3c — the macOS 27 bed's gated-cell count, before and after the read.

    python3 gated-count.py [matrix.json]

`test/adopted-thresholds.test.ts`'s `atAShippedDocument` and `MATRIX` filter,
restated in python so the count claims §5.164 §7 states (230 cells / 726 rows)
can be read from a script rather than from a test's failure message. A row is
AT A SHIPPED DOCUMENT when its `capturePath` names a profile document path and
the first twelve hex of that file's current SHA-256; a GATED cell is such a row
that is not `probe`, not `inactive`, and not one of the inactive scenes the
suite drops. Per profile, and per tier, because a bed empties one profile at a
time when a document's bytes move.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent

CLAUSE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")
INACTIVE = re.compile(r"__inactive")


def shipped(path: str) -> str | None:
    file = ROOT / path
    if not file.is_file():
        return None
    return hashlib.sha256(file.read_bytes()).hexdigest()[:12]


def main() -> int:
    matrix = Path(sys.argv[1]) if len(sys.argv) > 1 else PACKAGE / "results/matrix.json"
    cells = json.loads(matrix.read_text())["cells"]
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

    print(f"== {matrix} ==")
    for os_token in ("26.5", "27"):
        print(f"\n  macOS {os_token}: {total[os_token]} row(s) in the file")
        keys = sorted(k for k in rows if k[0] == os_token)
        for key in keys:
            print(f"    {key[1]:<62} {rows[key]:>5} row(s) at a shipped document, "
                  f"{gated[key]:>4} gated")
        print(f"    {'TOTAL at a shipped document':<62} "
              f"{sum(rows[k] for k in keys):>5} row(s), {sum(gated[k] for k in keys):>4} gated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
