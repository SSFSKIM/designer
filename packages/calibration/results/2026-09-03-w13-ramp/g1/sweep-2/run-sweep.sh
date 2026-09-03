#!/bin/bash
set -u
NAME=$1; PROFILE=$2; A1=$3; A2=$4
T=/Users/new/.claude/jobs/5c70e47f/tmp/w13/sweep-2
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/w13-g1/packages/calibration
unset VITREA_SCENES VITREA_FIXTURES
export VITREA_WEB_CAPTURES="$T/web-captures-$NAME"
rm -rf "$VITREA_WEB_CAPTURES" sweep-work; mkdir -p "$VITREA_WEB_CAPTURES"
npx tsx scripts/sweep.ts --axis "$A1" --axis "$A2" --base "$T/g1-sweep-2-base.json" \
  --profile "$PROFILE" --renderer webgpu > "$T/$NAME.out" 2> "$T/$NAME.err"
echo "exit=$?"
mkdir -p "$T/points-$NAME"; cp sweep-work/*.json "$T/points-$NAME/"
rm -rf "$VITREA_WEB_CAPTURES"
tail -40 "$T/$NAME.out"
