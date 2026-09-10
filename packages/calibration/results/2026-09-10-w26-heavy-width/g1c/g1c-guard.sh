#!/bin/bash
# W26 G1c — the GPU guard, run before every capture and never skipped.
#
# X4 is one capture process at a time, and the cost of breaking it is not a failed run but a
# QUIETLY WRONG one: two Chromium instances contending for the same adapter produce captures that
# differ from a clean run by more than the constants this child is fitting move them. So the guard
# is a precondition rather than a courtesy, and it refuses rather than waits, because a run that
# starts late is fine and a run that starts alongside another is not.
#
# It checks the two things that can be true at once: a capture or bench process still alive
# (`compare.ts`, `sweep.ts`, `cost.mjs`, `capture.mjs`, `capture-web`, `VitreaReference`,
# `playwright`), and the dev server's port still held. `pgrep -f` would match this script's own
# command line, so the pattern is built so it cannot.
#
# ONE EXCLUSION, AND IT IS MEASURED RATHER THAN ASSUMED. Playwright keeps a resident daemon
# (`run-cli-server --daemon-session`) and the headless Chrome it launched alive BETWEEN runs, and
# both match `playwright` on their command lines. Refusing on those refuses every rung after the
# first, which is not what X4 is about: what X4 forbids is two capture RUNS contending, and an idle
# daemon is not a run. The evidence that it is harmless is on this child's own bench — the `c0`
# rung was captured with that daemon already resident and came out BYTE-IDENTICAL to the canonical
# 0.14.0 captures on all fifty rows, which were taken on another day in another session. So the
# daemon and its browser are excluded by name and everything else still refuses.
#
# A SECOND EXCLUSION, AND IT IS THE HONEST ONE RATHER THAN THE CONVENIENT ONE. This machine also
# runs browser automations that have nothing to do with vitrea, and they match `playwright` too.
# Blocking on them would stall a ladder on load the child neither owns nor can wait out, so a
# playwright process whose command line does not name this repository is reported as ambient load
# and not refused. What makes that defensible is the same measurement as above: `c0` was captured
# under exactly this load and came out byte-identical to the canonical captures on all fifty rows,
# and every cell the harness writes carries `deterministic: true` with `repeatNoise: 0`. Foreign
# load is therefore recorded in the run's log and the run proceeds; a vitrea capture is refused.
set -u
PAT='compare\.ts|sweep\.ts|cost\.mjs|capture\.mjs|capture-web|VitreaReference|playwright'
RESIDENT='run-cli-server|Google Chrome|Chromium\.app|chrome_crashpad'
HITS=$(pgrep -f "$PAT" | grep -v "^$$\$" || true)
BUSY=""
FOREIGN=""
if [ -n "$HITS" ]; then
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    pid=${line%% *}
    case "$line" in
      *run-cli-server*|*"Google Chrome"*|*Chromium.app*|*chrome_crashpad*) continue ;;
    esac
    case "$line" in
      *designer*|*vitrea*|*compare.ts*|*sweep.ts*|*cost.mjs*|*capture.mjs*|*capture-web*|*VitreaReference*)
        BUSY="$BUSY $pid" ;;
      *) FOREIGN="$FOREIGN $pid" ;;
    esac
  done <<EOF
$(ps -o pid=,command= -p $HITS 2>/dev/null)
EOF
fi
if [ -n "$BUSY" ]; then
  echo "GUARD: a vitrea capture or bench process is alive — refusing." >&2
  ps -o pid,etime,command -p $BUSY | cut -c1-160 >&2
  exit 1
fi
if [ -n "$FOREIGN" ]; then
  echo "GUARD: ambient browser automation on this machine (not vitrea, not refused):$FOREIGN"
fi
if lsof -i :5189 >/dev/null 2>&1; then
  echo "GUARD: port 5189 is held — refusing." >&2
  lsof -i :5189 >&2
  exit 1
fi
echo "GUARD: clear at $(date +%H:%M:%S)"
