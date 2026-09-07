#!/bin/bash
# W21 G1 — the dry run on the CANONICAL bed at the frozen constants, to SCRATCH (contract X6).
#
# What is frozen: the dark profile document re-recorded by this gate — the six measured anchors at
# `backdropToneResponseStrength` 1, `specularGain` 0, `rimAlpha` 0.082, `tintAlpha` 0.90,
# `resolvedMaterialSha256` d86f480c0e136627. Nothing below may be re-run at a different document
# without the holdout read being void: this is the wave's ONE holdout read, and G2 reproduces these
# captures byte for byte from the main checkout.
#
# The order matters. Calibration and validation first on both tiers and both scales, then the
# holdout, so that a stop firing on the calibration rows can stop the gate before the holdout is
# opened at all. The two dark profiles share one document (the 2x profile is the same material at a
# different device-pixel ratio), which is why `--profile` moves and `--material-profile` does not.
#
# The light profile rides at the end for contract X3's inverse: the light document is untouched, so
# every light capture must come back byte-identical to the canonical `web-captures/` on the capture
# machine. It is a check that nothing in the renderer's defaults moved under this gate's edits, not
# a fidelity read, and `g1-verify.py` is what compares the bytes.
#
# The GPU is shared: one capture process at a time, and this script serialises every run.
set -u
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a5adcfa2901ee0ebe
unset VITREA_SCENES VITREA_FIXTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w21/g1/dryrun
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/g1-dryrun.json"
rm -f "$MATRIX" "$T/DONE"
LOG="$T/g1-runs.log"
: > "$LOG"
echo "=== $(date +%H:%M:%S) build ==="
pnpm -r build > "$T/build.log" 2>&1 || { echo "BUILD FAILED"; exit 1; }
echo "=== $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD) ==="
cd packages/calibration
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  local profile=$1 doc=$2 renderer=$3 sets=$4
  echo "=== $(date +%H:%M:%S) $profile / $renderer / $sets ==="
  npx tsx cli/compare.ts --profile "$profile" --material-profile "$doc" --renderer "$renderer" \
    --set "$sets" --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
}
for RENDERER in webgpu css; do
  run apple-macos-26.5-1x-dark-standard "$DARK" "$RENDERER" calibration,validation
  run apple-macos-26.5-2x-dark-standard "$DARK" "$RENDERER" calibration,validation
done
echo "=== $(date +%H:%M:%S) the holdout, once, at the frozen constants (X6) ==="
for RENDERER in webgpu css; do
  run apple-macos-26.5-1x-dark-standard "$DARK" "$RENDERER" holdout
  run apple-macos-26.5-2x-dark-standard "$DARK" "$RENDERER" holdout
done
echo "=== $(date +%H:%M:%S) the light profile, for X3's byte check ==="
for RENDERER in webgpu css; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$RENDERER" calibration,validation
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE"
