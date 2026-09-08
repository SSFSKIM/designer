#!/bin/bash
# W23 G3 — every reading of the dry run, in one place, after the bed is captured.
#
# G1's `g1-evidence.sh` with this gate's own reader (the hue columns) and two readings G1 had no
# need of: the chromaticity table the wave's new clause is stated on, and stop S10's byte identity
# against G1's dry run, which is the same configuration in every respect but the painted rim.
#
# Nothing here touches the GPU: the captures are on disk and this is all instrument work.
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN=/Users/new/Developer/GitHub/designer
T=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g3/dryrun
G1=/Users/new/.claude/jobs/5c70e47f/tmp/w23/g1/dryrun
AFTER="$T/web-captures"
BEFORE="$MAIN/packages/calibration/web-captures"
MATRIX="$T/g3-dryrun.json"
BED="$MAIN/packages/calibration/results/matrix.json"

echo "== reading both beds on both instruments =="
bash "$HERE/read-canonical.sh" "$AFTER" "$BEFORE"
echo "== the hue clause: the tinted rows' contour-row colour, landed / G1 / G3 =="
bash "$HERE/read-chroma.sh" g3 "$AFTER"
"$PY" "$HERE/chroma-table.py" --label landed --label g1 --label g3 --out "$HERE/chroma-after.txt" \
  > /dev/null
"$PY" "$HERE/chroma-table.py" --label landed --label g1 --label g3 --tier css \
  --out "$HERE/chroma-after-css.txt" > /dev/null
echo "== clauses 1-4 =="
"$PY" "$HERE/g3-clauses.py" "$HERE/canonical-reads" --out "$HERE/g3-clauses.txt" > /dev/null
echo "== stops S1, S2, S7 =="
"$PY" "$HERE/stops.py" --reads "$HERE/canonical-reads" --before "$BED" --after "$MATRIX" \
  --out "$HERE/stops.txt" > /dev/null
echo "== stop S9: the tinted rows' luminance rim against the landed bed =="
"$PY" "$HERE/tinted-rows.py" --landed landed --after g3 --out "$HERE/tinted-rows.txt" > /dev/null
echo "== stop S10: no untinted capture moves, against G1's dry run =="
"$PY" "$HERE/untinted-identity.py" --before "$G1/web-captures" --after "$AFTER" \
  --out "$HERE/untinted-identity.txt" > /dev/null
echo "== clause 5's headline, the OKLab dE mean per profile, set and tier =="
"$PY" "$HERE/delta-e.py" --before "$BED" --after "$MATRIX" --out "$HERE/delta-e.txt" > /dev/null
echo "== every capture against the canonical bed, byte for byte =="
"$PY" "$HERE/byte-identity.py" --before "$BEFORE" --after "$AFTER" \
  --out "$HERE/byte-identity.txt" > /dev/null
echo "== the digests G2 reproduces =="
"$PY" "$HERE/g3-digests.py" "$AFTER" "$MATRIX" > "$HERE/g3-digests.txt"
echo "== the gate over the scratch matrix =="
cd "$HERE/../../.."
VITREA_MATRIX_PATH="$MATRIX" npx vitest run test/adopted-thresholds.test.ts \
  > "$HERE/g3-gate.txt" 2>&1 || true
echo "-> $HERE"
