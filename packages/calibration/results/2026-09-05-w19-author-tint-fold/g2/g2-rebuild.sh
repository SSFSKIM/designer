#!/bin/bash
# W19 G2: the canonical rebuild at the landing (W19 Decision Log 4 — landed on the parent's
# recommendation under the user's standing instruction; claims §5.81). `main` at the code that
# ships (the author tint folded over the contrast floor on the CSS tier's linear path: the
# transfer table solved on the untinted material, L3 the encoded fold of the author layer over
# the floor overlay; the GPU tier byte-identical by contract X3): build the workspace, keep the
# previous canonical bed and its captures in scratch (they are the W18 bed the landing document
# compares against), remove results/matrix.json, then the twelve per-profile runs to the
# CANONICAL matrix and the CANONICAL web-captures/ (no --out-matrix, no VITREA_WEB_CAPTURES). The
# GPU tier runs first so every dom cell's coherence axis is measured against a capture already
# on disk. Derived from W18's g2-rebuild.sh; the commands are the same.
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w19/g2
mkdir -p "$T"
LOG="$T/g2-runs.log"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
cd packages/calibration
cp results/matrix.json "$T/matrix-before-w19.json"
rm -rf "$T/web-captures-before-w19"; mv web-captures "$T/web-captures-before-w19"; mkdir -p web-captures
rm -f results/matrix.json
: > "$LOG"
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 renderer=$3
  echo "=== $(date +%H:%M:%S) $profile / $renderer ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer "$renderer" \
    --set calibration,validation,holdout --write-partial >> "$LOG" 2>&1
  echo "    exit=$?"
}
for renderer in webgpu css; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$renderer"
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-light-increased-contrast "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT" "$renderer"
  run apple-macos-26.5-1x-dark-standard "$DARK" "$renderer"
  run apple-macos-26.5-2x-dark-standard "$DARK" "$renderer"
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
