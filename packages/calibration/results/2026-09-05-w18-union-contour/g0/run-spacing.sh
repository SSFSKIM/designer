#!/bin/bash
# W18 G0 (a), M3 — the spacing sweep.
#
# The three canonical circles at eight gaps, on both tiers at both scales. The separation in (a)
# reads a neighbours' term at the declared spacing of 12 that is gone at 40; this resolves the length
# scale between them, which is what tells the mechanisms apart. Three lengths are in play and they
# are different numbers: the renderer's union separation (16, `DEFAULT_GROUP_UNION`), the sampling
# padding the web scene builder floors the merge distance at (24, `DEFAULT_GROUP_SAMPLING`), and the
# CSS tier's own per-host outer shadow (sigma 15.55 CSS px, spread 3.1, offset 7.95 down).
#
# One at a time on a shared adapter; scratch scene bed, scratch capture roots, nothing canonical.
#
# Usage: `bash run-spacing.sh`, from `packages/calibration`.
set -u
W=/Users/new/Developer/GitHub/designer/packages/calibration
T=/Users/new/.claude/jobs/5c70e47f/tmp/w18/g0

if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi

cd "$W" || exit 1
unset VITREA_FIXTURES
export VITREA_SCENES="$T/scenes/w18-spacing.json"

for tier in webgpu css; do
  for scale in 1 2; do
    echo "=== $(date +%H:%M:%S) $tier @${scale}x ==="
    npx tsx scripts/capture-web.ts --all --renderer "$tier" --scale "$scale" \
      --out "$T/captures/spacing-$tier-${scale}x" >> "$T/logs/spacing.log" 2>&1
    echo "    exit=$?"
  done
done
echo "DONE $(date +%H:%M:%S)"
