#!/bin/bash
# W26 G1c — the fourteen thick regression floors and every adopted bound, per rung.
#
# `adopted-thresholds.test.ts` is the ONLY copy of the adopted bounds, the floors and the
# conditioning predicate, and it reads whichever matrix `VITREA_MATRIX_PATH` names (X6). It asserts
# over the WHOLE frozen bed — counts, partitions and a "every floor is reached by a gated row"
# guard — so a matrix carrying only a rung's rows fails on absence rather than on measurement.
# `g1-gate.py` (G1's, unedited) assembles the input: the rung's own calibration and validation
# cells beside the CANONICAL holdout cells, which are the frozen bed's own and are evidence about
# nothing in this rung. X3 keeps the holdout for the declaring child's one dry run.
#
#   g1c-gate.sh <rung-with-suffix> [<rung> ...]
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c
cd /Users/new/Developer/GitHub/designer/packages/calibration
for rung in "$@"; do
  echo "=== gate $rung ==="
  $PY "$HERE/../g1/g1-gate.py" --bed "$T/$rung/rung.json" --out "$T/$rung/gate.json" \
    || { echo "    assemble failed"; continue; }
  VITREA_MATRIX_PATH="$T/$rung/gate.json" npx vitest run test/adopted-thresholds.test.ts \
    > "$T/$rung/gate.log" 2>&1
  echo "    vitest exit=$?"
  grep -E "Tests +[0-9]+|Test Files|✓|×|FAIL" "$T/$rung/gate.log" | tail -12
done
