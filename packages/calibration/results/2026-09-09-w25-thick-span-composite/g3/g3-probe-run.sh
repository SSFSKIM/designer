#!/bin/bash
# W25 G3 — the probe set captured on the web, both tiers, the four standard profiles, to SCRATCH.
#
# The probe set (`scenes.json`'s `split.probe`, declared by G1 under Decision Log 3 (e)) is the
# fitting ground for every constant this wave declares: 52 scenes at both scales in both schemes,
# with the coarse checkerboards and the impulse rows that identify the kernel's triple and the
# `dark-solid` span sweep that identifies the level above the knee. It is not a gated set — the
# gate's counts, predicate and floors ignore it by name — so nothing captured here moves a bound.
#
# The material is whatever the working tree carries. Called at the inert defaults it is this
# wave's baseline (all three W25 constants at 0); called at a ladder rung it is that rung's
# material, which the caller patched into the profile documents beforehand. The tag names the
# output directory so no two rungs ever share a matrix or a capture.
#
#   g3-probe-run.sh <tag>
#
# One capture process at a time (X4); everything to scratch through `--out-matrix` and
# `VITREA_WEB_CAPTURES` (X2). The GPU tier runs before the CSS tier so every dom cell's coherence
# axis is measured against a GPU capture already on disk, which is the canonical rebuild's order.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
TAG=${1:?tag}
T=/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3/$TAG
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/probe.json"
rm -f "$T/DONE" "$MATRIX"
LOG="$T/runs.log"
: > "$LOG"
cd packages/calibration
echo "=== $(date +%H:%M:%S) tag=$TAG HEAD $(git rev-parse --short HEAD) ==="
echo "=== light document $(shasum -a 256 profiles/apple-macos-26.5-1x-light-standard.json | cut -c1-12) ==="
echo "=== dark  document $(shasum -a 256 profiles/apple-macos-26.5-1x-dark-standard.json | cut -c1-12) ==="
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json
run() {
  echo "=== $(date +%H:%M:%S) $1 / $3 / probe ==="
  npx tsx cli/compare.ts --profile "$1" --material-profile "$2" --renderer "$3" \
    --set probe --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
}
for RENDERER in webgpu css; do
  run apple-macos-26.5-1x-light-standard "$LIGHT" "$RENDERER"
  run apple-macos-26.5-2x-light-standard "$LIGHT" "$RENDERER"
  run apple-macos-26.5-1x-dark-standard  "$DARK"  "$RENDERER"
  run apple-macos-26.5-2x-dark-standard  "$DARK"  "$RENDERER"
done
echo "PROBE RUNS DONE $TAG $(date +%H:%M:%S)"
touch "$T/DONE"
