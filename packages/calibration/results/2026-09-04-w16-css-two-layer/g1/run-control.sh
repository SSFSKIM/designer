#!/bin/bash
# W16 G1: the `blur()` control — the same branch with the Chromium conformance row's
# `referenceFilterInBackdrop` turned off for the run, so the only difference between the
# `control` matrix and the `dry` one is the blur's colour space (claims §5.71 §2, W16 Decision
# Log 2 question 0). The edit is local to the run and reverted after it; the light-standard
# profiles at both scales, calibration + validation, CSS tier only.
set -u
W=/Users/new/Developer/GitHub/designer/.claude/worktrees/w16-g1
T=/Users/new/.claude/jobs/5c70e47f/tmp/w16/dry
TABLE=$W/packages/platform-web/src/probe/conformance-table.ts
cd "$W"
if pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy"; exit 2
fi
grep -c "referenceFilterInBackdrop: true," "$TABLE"
sed -i '' 's/referenceFilterInBackdrop: true,/referenceFilterInBackdrop: false, \/\/ CONTROL RUN/' "$TABLE"
pnpm --filter @vitreajs/vitrea-web build > "$T/control-build.log" 2>&1 || { echo "BUILD FAILED"; git checkout -- "$TABLE"; exit 1; }
cd packages/calibration; unset VITREA_SCENES VITREA_FIXTURES
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
for profile in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard; do
  echo "=== $(date +%H:%M:%S) $profile / css / control ==="
  VITREA_WEB_CAPTURES="$T/web-captures-control" npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$LIGHT" --renderer css --set calibration,validation --write-partial \
    --out-matrix "$T/matrix-control.json" >> "$T/runs-control.log" 2>&1
  echo "    exit=$?"
done
cd "$W"; git checkout -- "$TABLE"; git status --short | wc -l
pnpm --filter @vitreajs/vitrea-web build > "$T/control-rebuild.log" 2>&1 && echo "reverted and rebuilt"
echo "CONTROL DONE $(date +%H:%M:%S)"
