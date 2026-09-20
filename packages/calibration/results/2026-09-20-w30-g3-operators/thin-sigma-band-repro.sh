#!/usr/bin/env bash
set -euo pipefail
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a555fafb289fa2069/packages/calibration
for tag in "$@"; do
  out=/tmp/w30g3scratch/alpha-$tag
  rm -rf "$out"; mkdir -p "$out"
  VITREA_WEB_CAPTURES="$out" npx tsx cli/compare.ts \
    --profile apple-macos-27.0-1x-light-standard-glass0.5 \
    --material-profile "/tmp/w30g3scratch/docs-$tag/apple-macos-27.0-1x-light-standard-glass0.5.json" \
    --receded-profile "/tmp/w30g3scratch/docs-$tag/apple-macos-27.0-1x-light-standard-glass0.5-receded.json" \
    --renderer webgpu --set calibration --scene checkerboard__capsule-button__rest \
    --alpha --write-partial --out-matrix "$out/matrix.json" > "$out/log.txt" 2>&1 || true
  echo "$tag done"
done
