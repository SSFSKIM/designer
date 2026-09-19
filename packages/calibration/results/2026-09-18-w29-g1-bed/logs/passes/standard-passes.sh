#!/bin/bash
# The four standard passes of the W29 27 bed, run back to back (RUNBOOK §3 "Standard first").
# Each pass is rehearsed dry and its presented count checked before the real pass; the display
# is switched to 1x between the 2x and 1x pairs and LEFT at mode 69 at the end, because the
# accessibility passes that follow are 1x. Logs to standard-passes.log beside this script.
set -uo pipefail
REPO=/Users/new/Developer/GitHub/designer
R=$REPO/packages/calibration/results/2026-09-18-w29-g1-bed
export VITREA_SCENES=$REPO/apps/reference-apple/scenes.json
DP="id:7709FD0F-F423-4277-B0C8-7CA94F85723A res:2560x1440 hz:60 color_depth:4 enabled:true origin:(0,0) degree:0"
log(){ echo "[$(date -u +%FT%TZ)] $*"; }
pass(){ # pose scale expected
  log "DRY $1 ${2}x standard"
  local out; out=$(DRY=1 "$R/run-sitting-27.sh" "$1" "$2" standard 2>&1); rc=$?
  echo "$out" | tail -4
  local n; n=$(echo "$out" | grep -o 'cells presented: [0-9]*' | grep -o '[0-9]*$')
  if [ $rc -ne 0 ] || [ "${n:-0}" != "$3" ]; then log "STOP: dry $1 ${2}x presented '${n:-none}' (expected $3), rc=$rc"; exit 10; fi
  log "REAL $1 ${2}x standard"
  "$R/run-sitting-27.sh" "$1" "$2" standard; rc=$?
  if [ $rc -ne 0 ]; then log "STOP: real $1 ${2}x exit $rc"; exit $rc; fi
  log "DONE $1 ${2}x standard"
}
log "start; slider=$(defaults read -g NSGlassTintAmount) rt=$(defaults read com.apple.universalaccess reduceTransparency) ic=$(defaults read com.apple.universalaccess increaseContrast) borders=$(defaults read com.apple.Accessibility ButtonShapesEnabled) $(displayplacer list | grep 'current mode' | grep -o 'mode [0-9]*')"
pass active 2 162
pass inactive 2 119
displayplacer "$DP mode:69"; sleep 5
displayplacer list | grep 'current mode' | grep -q 'mode 69' || { log "STOP: display not at mode 69"; exit 11; }
log "display at mode 69"
pass active 1 162
pass inactive 1 119
log "ALL FOUR STANDARD PASSES DONE; display left at mode 69 for the accessibility passes"
