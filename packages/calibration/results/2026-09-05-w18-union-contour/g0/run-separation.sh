#!/bin/bash
# W18 G0 (a) and (c) — the separation captures.
#
# One scratch scene bed (the lone circle, the canonical capsule, the three-up at 12 and at 40, the
# stack and its two parts, over `checkerboard`, `photo` and `light-solid`) rendered on both tiers at
# both scales. Four runs of `capture-web`, one at a time on a shared adapter.
#
# `compare` is deliberately NOT the driver here. Compare plans its cells from the native manifest,
# and eight of these eighteen scenes have no native fixture and never will on this bed — the study
# is a CSS-tier against GPU-tier difference, which needs no reference. So the driver is the capture
# script alone and the reading is `separation.ts`'s, under the declared component region.
#
# Nothing canonical is written: the scene bed is scratch through `VITREA_SCENES`, the captures land
# under the scratch root through `--out`, and `VITREA_FIXTURES` is left unset so the page fetches
# the committed backgrounds read-only through the dev server's mount.
#
# Usage: `bash run-separation.sh`, from `packages/calibration`.
set -u
W=/Users/new/Developer/GitHub/designer/packages/calibration
T=/Users/new/.claude/jobs/5c70e47f/tmp/w18/g0

if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi

cd "$W" || exit 1
unset VITREA_FIXTURES
export VITREA_SCENES="$T/scenes/w18-web.json"

for tier in webgpu css; do
  for scale in 1 2; do
    echo "=== $(date +%H:%M:%S) $tier @${scale}x ==="
    npx tsx scripts/capture-web.ts --all --renderer "$tier" --scale "$scale" \
      --out "$T/captures/sep-$tier-${scale}x" >> "$T/logs/sep.log" 2>&1
    echo "    exit=$?"
  done
done
echo "DONE $(date +%H:%M:%S)"
