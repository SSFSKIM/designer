#!/bin/bash
# W24 G2 — every reading of the dry run, in one place, after the bed is captured.
#
# Nothing here touches the GPU: the captures are on disk and this is all instrument work. It runs in
# the order the evidence is argued — both beds read on both instruments, then the clauses that need
# the angular reader, then the impulse instrument's clause 2, then the stops, then the matrix's own
# headline, then the byte identity and the digests G3 refers to, then the gate over the scratch
# matrix — so a table that contradicts an earlier one is visible in the file's own order.
#
# `SETS` is a parameter: it is `calibration,validation` on the first pass and gains the holdout only
# after the holdout column has been captured (X3).
#
# Usage: `bash g2-evidence.sh [sets]`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN=/Users/new/Developer/GitHub/designer
T=/Users/new/.claude/jobs/5c70e47f/tmp/w24/g2
AFTER="$T/web-captures"
BEFORE="$MAIN/packages/calibration/web-captures"
MATRIX="$T/g2-dryrun.json"
BED="$MAIN/packages/calibration/results/matrix.json"
SETS="${1:-calibration,validation}"

echo "== reading both beds on both instruments ($SETS) =="
bash "$HERE/read-canonical.sh" "$AFTER" "$BEFORE" "$SETS"
echo "== clauses 1 and 3 =="
"$PY" "$HERE/g2-clauses.py" "$HERE/canonical-reads" --out "$HERE/g2-clauses.txt" > /dev/null
echo "== clause 2, on the impulse instrument =="
bash "$HERE/run-impulse.sh" "$AFTER" "$BEFORE" > "$HERE/impulse-read.txt" 2>&1 || true
echo "== stops S1, S2, S7, S11 =="
"$PY" "$HERE/stops.py" --reads "$HERE/canonical-reads" --before "$BED" --after "$MATRIX" \
  --out "$HERE/stops.txt" > /dev/null
echo "== clause 4's headline, the OKLab dE mean per profile, set and tier =="
"$PY" "$HERE/delta-e.py" --before "$BED" --after "$MATRIX" --out "$HERE/delta-e.txt" > /dev/null
echo "== every capture against the canonical bed, byte for byte (S10) =="
"$PY" "$HERE/byte-identity.py" --before "$BEFORE" --after "$AFTER" \
  --out "$HERE/byte-identity.txt" > /dev/null
echo "== the digests G3 reproduces =="
"$PY" "$HERE/g2-digests.py" "$AFTER" "$MATRIX" > "$HERE/g2-digests.txt"
echo "== the gate over the scratch matrix =="
cd "$HERE/../../.."
VITREA_MATRIX_PATH="$MATRIX" npx vitest run test/adopted-thresholds.test.ts \
  > "$HERE/g2-gate.txt" 2>&1 || true
echo "-> $HERE"
