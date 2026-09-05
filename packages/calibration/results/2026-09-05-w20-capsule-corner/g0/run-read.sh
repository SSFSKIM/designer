#!/bin/bash
# W20 G0 — build the candidate contours and read them against the materialised probe bed.
#
# Two steps, both pure computation over committed evidence: `candidates.ts` emits the four candidate
# constructions from the geometry package itself (so whatever wins is a policy G1 can adopt by name),
# and `read-contours.py` reads Apple's own contour off the probe captures and scores them.
#
# Usage: `bash run-read.sh <probeDir> <outDir>`
set -eu
PROBE="${1:?usage: run-read.sh <probeDir> <outDir>}"
OUT="${2:?}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python

mkdir -p "$OUT"
( cd "$WORKTREE" && pnpm --filter @vitrea/calibration exec tsx \
    results/2026-09-05-w20-capsule-corner/g0/candidates.ts ) > "$OUT/candidates.json"
"$PY" "$HERE/read-contours.py" --probe "$PROBE" --candidates "$OUT/candidates.json" --out "$OUT"
"$PY" "$HERE/tables.py" "$OUT/contours.json" > "$OUT/tables.md"
echo "READ DONE -> $OUT"
