#!/bin/bash
# W19 G0 (c) — both web tiers against the probe bed, to scratch.
#
# The matrix goes under `--out-matrix` and the captures under `VITREA_WEB_CAPTURES`; the canonical
# layout is untouched. `--set recorded` is opt-in twice over — the bed declares every cell `recorded`
# and compare must be asked for that set by name — which is the custody X10 puts on this bed: read by
# the study, fitted by nothing.
#
# Usage: `bash run-probe-compare.sh <scenesJson> <probeDir> <scratchDir>`, from `packages/calibration`.
set -u
SCENES="${1:?usage: run-probe-compare.sh <scenesJson> <probeDir> <scratchDir>}"
PROBE="${2:?}"
T="${3:?}"
mkdir -p "$T"

for R in webgpu css; do
  while pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs|capture-web|VitreaReference' > /dev/null \
     || lsof -i :5189 > /dev/null 2>&1; do
    echo "waiting for the GPU $(date -u +%H:%M:%SZ)"; sleep 20
  done
  echo "=== $R $(date -u +%H:%M:%SZ)"
  VITREA_SCENES="$SCENES" VITREA_FIXTURES="$PROBE" VITREA_WEB_CAPTURES="$T/web-captures" \
    pnpm run compare -- \
    --profile apple-macos-26.5-1x-light-standard \
    --material-profile profiles/apple-macos-26.5-1x-light-standard.json \
    --renderer "$R" --set recorded --out-matrix "$T/matrix-probe.json" --write-partial \
    > "$T/compare-$R.log" 2>&1
  echo "$R exit=$?"
done
echo "COMPARE DONE $(date -u +%H:%M:%SZ)"
