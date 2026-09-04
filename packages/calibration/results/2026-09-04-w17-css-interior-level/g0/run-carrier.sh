#!/bin/bash
# W17 G0 (d) — the carrier's capture.
#
# The CSS tier on the two light-standard profiles, calibration and validation only, under the
# committed profile documents, with the temporary `feComponentTransfer` carrier built into
# `platform-web` (`src/w17-carrier.ts` plus the two call sites, uncommitted and reverted before
# anything is committed). The GPU tier is captured into the same scratch matrix first so the
# cross-tier coherence rows compute and the comparison is against this run's own GPU capture rather
# than against a remembered number.
#
# Usage: `bash run-carrier.sh <tag>` — `baseline` before the patch is built, `carrier` after.
set -u
TAG=${1:-carrier}
W=/Users/new/Developer/GitHub/designer/packages/calibration
T=/Users/new/.claude/jobs/5c70e47f/tmp/w17/g0

if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi

cd "$W" || exit 1
unset VITREA_SCENES VITREA_FIXTURES
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json

run() {
  local profile=$1 renderer=$2
  echo "=== $(date +%H:%M:%S) $TAG / $profile / $renderer ==="
  VITREA_WEB_CAPTURES="$T/captures/$TAG" npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$LIGHT" --renderer "$renderer" --set calibration,validation \
    --write-partial --out-matrix "$T/matrices/$TAG.json" >> "$T/logs/$TAG.log" 2>&1
  echo "    exit=$?"
}

for profile in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard; do
  run "$profile" webgpu
  run "$profile" css
done
echo "DONE $TAG $(date +%H:%M:%S)"
