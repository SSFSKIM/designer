#!/bin/bash
# W20 G2: the canonical rebuild at the landing (W20 Decision Log 3 — landed on the parent's
# recommendation under the user's standing instruction; claims §5.85). `main` at the code that
# ships (the Apple corner reference keeping the requested radius and compressing the shoulder, so
# every capsule and circle is a stadium on the render path; the CSS tier untouched, byte-identical
# by contract X3's inverse): build the workspace, keep the previous canonical bed and its captures
# in scratch (they are the W19 bed the landing document compares against), remove
# results/matrix.json, then the twelve per-profile runs to the CANONICAL matrix and the CANONICAL
# web-captures/ (no --out-matrix, no VITREA_WEB_CAPTURES). `--alpha` takes the declaration-
# conformance capture on every cell (W20 Decision Log 2 ruling 2: the canonical matrix carries the
# rows from this landing on). The GPU tier runs first so every dom cell's coherence axis is
# measured against a capture already on disk. Derived from W19's g2-rebuild.sh.
set -u
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w20/g2
mkdir -p "$T"
LOG="$T/g2-runs.log"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
cd packages/calibration
cp results/matrix.json "$T/matrix-before-w20.json"
rm -rf "$T/web-captures-before-w20"; mv web-captures "$T/web-captures-before-w20"; mkdir -p web-captures
rm -f results/matrix.json
: > "$LOG"
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 renderer=$3
  echo "=== $(date +%H:%M:%S) $profile / $renderer ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer "$renderer" \
    --set calibration,validation,holdout --alpha --write-partial >> "$LOG" 2>&1
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
touch "$T/DONE"
