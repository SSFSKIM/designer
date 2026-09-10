#!/bin/bash
# W26 G2 — the fourteen thick regression floors, every adopted bound and the conditioning
# predicate's census, over the dry run's own matrix.
#
# `adopted-thresholds.test.ts` is the ONLY copy of the bounds, the floors and the predicate, and it
# reads whichever matrix `VITREA_MATRIX_PATH` names (X6). It asserts over the WHOLE frozen bed, so
# the input has to be a whole bed.
#
# Run TWICE, and the two runs are different claims:
#
#   calval   the dry run's calibration and validation cells beside the CANONICAL holdout cells,
#            assembled by G1's `g1-gate.py` unedited. The holdout rows there are the 0.14.0 bed's
#            own and are evidence about the frozen bed and not about the candidate — which is what
#            lets the floors be read before X3's one holdout read is spent.
#   whole    the dry run's own calibration, validation AND holdout cells, once the holdout column
#            has been captured. This is the gate on the candidate, entire.
#
#   g2-gate.sh calval|whole
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2/cand
MODE=${1:?calval|whole}
cd "$HERE/../../../../../packages/calibration"

if [ "$MODE" = calval ]; then
  $PY "$HERE/../g1/g1-gate.py" --bed "$T/bed.json" --out "$T/gate-calval.json"
  MATRIX="$T/gate-calval.json"
else
  # The dry run's three columns in one matrix, newest row per key. `--write-partial` APPENDS, so a
  # naive concatenation would hand the gate every cell twice and it would fail 25 of 37 cases on
  # the duplication alone before a measurement was read (W25 G3b's own gate did exactly that).
  $PY - "$T/bed.json" "$T/holdout.json" "$T/gate-whole.json" <<'PY'
import json, sys
out = {}
schema = None
for path in sys.argv[1:3]:
    doc = json.load(open(path))
    schema = doc.get("schemaVersion", schema)
    for cell in doc["cells"]:
        key = (cell["key"]["profileKey"], cell["key"]["sceneId"], cell["tier"],
               cell["key"]["web"]["renderer"])
        prior = out.get(key)
        if prior is None or cell["capturedAt"] >= prior["capturedAt"]:
            out[key] = cell
json.dump({"schemaVersion": schema, "cells": list(out.values())}, open(sys.argv[3], "w"))
print(f"assembled {len(out)} cells -> {sys.argv[3]}")
PY
  MATRIX="$T/gate-whole.json"
fi

VITREA_MATRIX_PATH="$MATRIX" npx vitest run test/adopted-thresholds.test.ts \
  > "$HERE/gate-$MODE.txt" 2>&1 || true
grep -E "Tests +[0-9]+|Test Files|✓|×|FAIL|expected" "$HERE/gate-$MODE.txt" | tail -30
echo "-> $HERE/gate-$MODE.txt"
