#!/bin/bash
# W22 G3 — vitrea's own captures at the fix, entirely to scratch, and with no native fixture opened.
#
# `capture-web.ts` and NOT `compare.ts`, which is the whole point: the two `glass-over-glass` cells
# are HOLDOUT, the wave's one holdout read belongs to G1 (X5), and `compare.ts` would diff them
# against the reference. `capture-web` renders vitrea's side and writes the PNG; it never opens
# `apps/reference-apple/fixtures` and writes no matrix, so nothing here spends the holdout read.
# The flags below are copied from `compare.ts`'s own invocation (`captureFor`), so a capture taken
# here is the same file `compare.ts` would have produced for the same cell.
#
# Two runs:
#
#   stacked/ — the two nested-pane cells on both tiers, at all four standard profiles. Read by
#              `read-stack-web.py` against the response law, never against a fixture.
#   bed/     — the calibration+validation scenes, webgpu, `--alpha`, the flags G0's `g0-capture.sh`
#              used, so every non-stacked capture can be compared byte for byte against G0's.
#
# The GPU is shared: everything is serialised in one process and a DONE marker is the only thing
# anything waits on.
set -u
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/agent-ac98f964c1299c688
unset VITREA_SCENES VITREA_FIXTURES VITREA_WEB_CAPTURES
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g3
LISTS="$T/scene-lists.json"
rm -f "$T/DONE"
LOG="$T/g3-captures.log"
: > "$LOG"
cd packages/calibration
LIGHT=profiles/apple-macos-26.5-1x-light-standard.json
DARK=profiles/apple-macos-26.5-1x-dark-standard.json

scenes() { node -e 'const j=require(process.argv[1]);process.stdout.write(j[process.argv[2]][process.argv[3]].join(" "))' "$LISTS" "$1" "$2"; }

run() {
  local profile=$1 doc=$2 scale=$3 scheme=$4 renderer=$5 set=$6 out=$7
  local list; list=$(scenes "$profile" "$set")
  [ -z "$list" ] && return 0
  echo "=== $(date +%H:%M:%S) $profile / $renderer / $set ($(echo "$list" | wc -w | tr -d ' ') scenes) ==="
  # shellcheck disable=SC2086
  npx tsx scripts/capture-web.ts $list --renderer "$renderer" --color-scheme "$scheme" \
    --scale "$scale" --out "$out/$profile" --material-profile "$doc" \
    ${8:-} >> "$LOG" 2>&1
  echo "    exit=$?"
}

for SPEC in "apple-macos-26.5-1x-light-standard $LIGHT 1 light" \
            "apple-macos-26.5-2x-light-standard $LIGHT 2 light" \
            "apple-macos-26.5-1x-dark-standard $DARK 1 dark" \
            "apple-macos-26.5-2x-dark-standard $DARK 2 dark"; do
  set -- $SPEC
  run "$1" "$2" "$3" "$4" webgpu gog "$T/stacked"
  run "$1" "$2" "$3" "$4" css    gog "$T/stacked"
  run "$1" "$2" "$3" "$4" webgpu bed "$T/bed" --alpha
done
echo "ALL RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE"
