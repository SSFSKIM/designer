#!/bin/bash
# Launch one W27c G1d native pass detached so the wrapper command line does not
# trip the sitting script's shared-process guard.
set -euo pipefail
SCALE="${1:?scale}"
ROOT=/Users/new/vitrea-w27c-g1d-2026-09-14
WORKTREE=/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a411f423c61b68604
GRANTED=/Users/new/Developer/GitHub/designer/apps/reference-apple/build
RUNNER="$WORKTREE/packages/calibration/results/2026-09-11-w27-26.5-run/run-sitting.sh"
EVIDENCE="$WORKTREE/packages/calibration/results/2026-09-14-w27c-g1d"
LOG="$ROOT/inactive-${SCALE}x.pass.log"
PID="$ROOT/inactive-${SCALE}x.pass.pid"

[ "$(defaults read com.apple.universalaccess increaseContrast)" = 0 ]
[ "$(defaults read com.apple.universalaccess reduceTransparency)" = 0 ]
mkdir -p "$ROOT"
printf 'launch %s inactive %sx; increaseContrast=0 reduceTransparency=0\n' \
  "$(date -u +%FT%TZ)" "$SCALE" >> "$ROOT/launches.log"
nohup env \
  VITREA_APP="$GRANTED/VitreaReference.app" \
  VITREA_HARNESS="$GRANTED/harness" \
  VITREA_SCENES="$WORKTREE/apps/reference-apple/scenes.json" \
  VITREA_BED_FILE="$EVIDENCE/bed-inactive.txt" \
  VITREA_SITTING_DIR="$ROOT" \
  caffeinate -dimsu "$RUNNER" inactive "$SCALE" 1 7 > "$LOG" 2>&1 < /dev/null &
echo $! > "$PID"
disown -a 2>/dev/null || true
printf 'pid %s log %s\n' "$(cat "$PID")" "$LOG"
