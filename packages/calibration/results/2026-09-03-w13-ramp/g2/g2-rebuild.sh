#!/bin/bash
# W13 G2: the canonical rebuild at the landing (W13 Decision Log 8, user-decided; claims
# §5.68 §6). `main` at the code that ships (the depth ramp's fourth form on both tiers, the
# body's widths in CSS px at every scale): build the workspace, keep the previous canonical
# bed and captures in scratch (they are the W14 bed the landing document compares against),
# remove results/matrix.json, then the twelve per-profile runs to the CANONICAL matrix and the
# CANONICAL web-captures/ (no --out-matrix, no VITREA_WEB_CAPTURES). Derived from W14's
# g2-rebuild.sh, which derived from W12's x1-rebuild.sh.
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w13/g2
mkdir -p "$T"
LOG="$T/g2-runs.log"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
cd packages/calibration
cp results/matrix.json "$T/matrix-before-w13.json"
rm -rf "$T/web-captures-before-w13"; mv web-captures "$T/web-captures-before-w13"; mkdir -p web-captures
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
