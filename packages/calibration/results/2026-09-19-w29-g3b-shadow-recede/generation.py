#!/usr/bin/env python3
"""W29 G3b — the canonical matrix reduced to ONE generation, for a reader that has no idea there are two.

    python3 generation.py <out.json> [--at-sealed | --at <materialProfile sha256 prefix>,...]

A profile document's hash is in the cell's key, so this child's read appended a
second 27 generation beside G3's rather than replacing it — which is the rule
(a recorded number is never rewritten) and is what `append-check.txt` proves.
Every reader that selects rows by profile and tier alone therefore sees both,
and G3's `referee.py` is one of them.

The gate file grew its own drop for this (`atAShippedDocument`, which reads the
documents on disk). `referee.py` is G3's committed instrument and is not edited
here for the reason nothing under `results/` is edited after it is committed, so
the filter lives outside it: this writes the sealed generation to a scratch
matrix and the referee runs over that, unchanged.

The 26.5 rows pass through untouched — they are their own generation, at
documents that have not moved since they were read.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent

SEALED = [
    "f42ddec1cf5a",  # apple-macos-27.0-1x-light-standard-glass0.5.json
    "272d1b0c3e10",  # apple-macos-27.0-1x-dark-standard-glass0.5.json
]
CLAUSE = re.compile(r"materialProfile=\S+ sha256:([0-9a-f]{12})")

out = Path(sys.argv[1])
if "--at" in sys.argv:
    wanted = set(sys.argv[sys.argv.index("--at") + 1].split(","))
else:
    wanted = set(SEALED)

matrix = json.loads((PACKAGE / "results" / "matrix.json").read_text())
kept, dropped = [], 0
for cell in matrix["cells"]:
    if not cell["key"]["profileKey"].startswith("apple-macos-27.0-"):
        kept.append(cell)
        continue
    match = CLAUSE.search(cell["key"]["web"]["capturePath"])
    if match is not None and match.group(1) in wanted:
        kept.append(cell)
    else:
        dropped += 1

out.write_text(json.dumps({"schemaVersion": matrix["schemaVersion"], "cells": kept}))
print(f"{out}: {len(kept)} rows kept, {dropped} 27 rows of a superseded generation dropped")
