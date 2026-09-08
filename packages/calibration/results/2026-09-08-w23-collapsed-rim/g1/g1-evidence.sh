#!/bin/bash
# W23 G1 — every reading of the dry run, in one place, after the bed is captured.
#
# Nothing here touches the GPU: the captures are on disk and this is all instrument work. It runs
# in the order the evidence is argued — the two beds read on both instruments, then the clauses,
# then the stops, then the matrix's own headline, then the byte identity and the digests G2 refers
# to — so a table that contradicts an earlier one is visible in the file's own order.
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN=/Users/new/Developer/GitHub/designer
T=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g1/dryrun
AFTER="$T/web-captures"
BEFORE="$MAIN/packages/calibration/web-captures"
MATRIX="$T/g1-dryrun.json"
BED="$MAIN/packages/calibration/results/matrix.json"

echo "== reading both beds on both instruments =="
bash "$HERE/read-canonical.sh" "$AFTER" "$BEFORE"
echo "== clauses 1-4 =="
"$PY" "$HERE/g1-clauses.py" "$HERE/canonical-reads" --out "$HERE/g1-clauses.txt" > /dev/null
echo "== stops S1, S2, S7 =="
"$PY" "$HERE/stops.py" --reads "$HERE/canonical-reads" --before "$BED" --after "$MATRIX" \
  --out "$HERE/stops.txt" > /dev/null
echo "== clause 5's headline, the OKLab dE mean per profile, set and tier =="
"$PY" "$HERE/delta-e.py" --before "$BED" --after "$MATRIX" --out "$HERE/delta-e.txt" > /dev/null
echo "== every capture against the canonical bed, byte for byte =="
"$PY" "$HERE/byte-identity.py" --before "$BEFORE" --after "$AFTER" \
  --out "$HERE/byte-identity.txt" > /dev/null
echo "== the digests G2 reproduces =="
"$PY" "$HERE/g1-digests.py" "$AFTER" "$MATRIX" > "$HERE/g1-digests.txt"
echo "== the gate over the scratch matrix =="
cd "$HERE/../../.."
VITREA_MATRIX_PATH="$MATRIX" npx vitest run test/adopted-thresholds.test.ts \
  > "$HERE/g1-gate.txt" 2>&1 || true
echo "-> $HERE"
