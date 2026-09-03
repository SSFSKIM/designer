#!/bin/bash
# W12 X1: the canonical rebuild at recomposition (W12 Cross-Child Contracts, X1).
# `main` at the code that ships (ω 0.8, W12 Decision Log 6; G3 held, Decision Log 7):
# build the workspace, keep the previous canonical bed and captures in scratch for the
# X3 scan, remove results/matrix.json, then the twelve per-profile runs to the CANONICAL
# matrix and the CANONICAL web-captures/ (no --out-matrix, no VITREA_WEB_CAPTURES).
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w12/x1
mkdir -p "$T"
LOG="$T/x1-runs.log"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
cd packages/calibration
cp results/matrix.json "$T/matrix-before-x1.json"
rm -rf "$T/web-captures-before-x1"; mv web-captures "$T/web-captures-before-x1"; mkdir -p web-captures
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
