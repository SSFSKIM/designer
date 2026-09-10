#!/bin/bash
# W26 G3 step 2 — the dark scheme's GPU rows at the landed documents, to SCRATCH, before anything
# canonical is touched (W26 Decision Log 10 (d)).
#
# The claim under test is the one the dark document now makes about itself: naming
# sizeHeavyTapSigma 0 / sizeHeavyTapSigma2x 0 is EXACTLY 0.14.0's dark draw and not approximately
# it. `resolvedMaterialSha256` returning to 874be66ea501621b — G1's fingerprint, taken when the
# constants existed at 0 — is the arithmetic half; this is the rendered half, and it is taken
# BEFORE the rebuild so that a failure costs nothing but a scratch directory.
#
# Every dark GPU row: both scales, calibration + validation, holdout and probe. `--out-matrix` and
# VITREA_WEB_CAPTURES send all of it to scratch (the canonical matrix, web-captures/, the fixtures
# and scenes.json are never written). The holdout is captured here because these bytes are compared
# against the canonical bed's own and NOT read as a fresh measurement of the candidate — the dark
# scheme is unmoved this wave, so there is no candidate on it to read.
#
# The flags are the canonical rebuild's — `--alpha --write-partial` — because the point is byte
# identity with captures taken under them.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/g3-guard.sh" || exit 1
cd "$HERE/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g3/darkproof
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
rm -f "$T/DONE"; rm -rf "$T/web-captures"
LOG="$T/runs.log"; : > "$LOG"
cd packages/calibration
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) $(git status --short | wc -l | tr -d ' ') dirty ==="
echo "=== dark document $(shasum -a 256 $DARK | cut -c1-16) ==="
run() {
  echo "=== $(date +%H:%M:%S) $1 / webgpu / $2 ==="
  npx tsx cli/compare.ts --profile "$1" --material-profile "$DARK" --renderer webgpu \
    --set "$2" --alpha --write-partial --out-matrix "$T/$2.json" >> "$LOG" 2>&1
  echo "    exit=$?"
}
for SETS in calibration,validation holdout probe; do
  run apple-macos-26.5-1x-dark-standard "$SETS"
  run apple-macos-26.5-2x-dark-standard "$SETS"
done
echo "DARK PROOF DONE $(date +%H:%M:%S)"
touch "$T/DONE"
