#!/bin/bash
# W21 G2b — the read, to SCRATCH (Part 3). The CSS tier's conversion moved; nothing else did.
#
# The scratch matrix starts as a COPY of the canonical one and the scratch capture tree starts as a
# copy of the canonical `web-captures/`, so each run below REPLACES its own rows and leaves the rest
# of the bed exactly as G2 landed it — which is the "canonical matrix with the dark CSS rows
# replaced" the gate has to be run against. It also means the cross-tier coherence axis is measured
# against GPU captures already on disk without re-rendering them.
#
# What runs, and why each:
#   * webgpu / 1x dark — the GPU tier is untouched by construction and this is the proof: its
#     digests must equal `g1/g1-digests.txt`.
#   * css / 1x dark and 2x dark — the new frozen configuration of the CSS tier, calibration and
#     validation first, then the holdout column, which is this configuration's FIRST holdout read.
#   * css / the four light profiles — contract X3, which binds every light capture byte-identical.
#
# One capture process at a time on the shared GPU: every run is serialised here.
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w21/g2b
mkdir -p "$T"
LOG="$T/g2b-runs.log"
rm -f "$T/DONE"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
echo "=== dark document $(shasum -a 256 packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json | cut -c1-12) ==="
cd packages/calibration
rm -rf "$T/web-captures"; cp -R web-captures "$T/web-captures"
cp results/matrix.json "$T/matrix.json"
export VITREA_WEB_CAPTURES="$T/web-captures"
: > "$LOG"
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 renderer=$3 sets=$4
  echo "=== $(date +%H:%M:%S) $profile / $renderer / $sets ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer "$renderer" \
    --set "$sets" --alpha --write-partial --out-matrix "$T/matrix.json" >> "$LOG" 2>&1
  echo "    exit=$?"
}
for SETS in calibration,validation holdout; do
  echo "=== $(date +%H:%M:%S) the $SETS column ==="
  run apple-macos-26.5-1x-dark-standard "$DARK" webgpu "$SETS"
  run apple-macos-26.5-1x-dark-standard "$DARK" css "$SETS"
  run apple-macos-26.5-2x-dark-standard "$DARK" css "$SETS"
  run apple-macos-26.5-1x-light-standard "$LIGHT" css "$SETS"
  run apple-macos-26.5-2x-light-standard "$LIGHT" css "$SETS"
  run apple-macos-26.5-1x-light-increased-contrast "$LIGHT" css "$SETS"
  run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" css "$SETS"
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE"
