#!/bin/bash
# One accessibility pass pair of the W29 27 bed: <increased-contrast|reduced-transparency>.
# Runs the active then the inactive pass for that mode, each rehearsed dry first with its
# presented count checked. The machine must already be in the mode (the user's hand); the
# sitting script refuses otherwise. Display must be at mode 69 (1x).
set -uo pipefail
MODE="${1:?increased-contrast|reduced-transparency}"
case "$MODE" in increased-contrast) EA=10; EI=22;; reduced-transparency) EA=9; EI=21;; *) echo bad mode; exit 64;; esac
REPO=/Users/new/Developer/GitHub/designer
R=$REPO/packages/calibration/results/2026-09-18-w29-g1-bed
export VITREA_SCENES=$REPO/apps/reference-apple/scenes.json
log(){ echo "[$(date -u +%FT%TZ)] $*"; }
pass(){ # pose expected
  log "DRY $1 1x $MODE"
  local out; out=$(DRY=1 "$R/run-sitting-27.sh" "$1" 1 "$MODE" 2>&1); rc=$?
  echo "$out" | tail -4
  local n; n=$(echo "$out" | grep -o 'cells presented: [0-9]*' | grep -o '[0-9]*$')
  if [ $rc -ne 0 ] || [ "${n:-0}" != "$2" ]; then log "STOP: dry $1 $MODE presented '${n:-none}' (expected $2), rc=$rc"; exit 10; fi
  log "REAL $1 1x $MODE"
  "$R/run-sitting-27.sh" "$1" 1 "$MODE"; rc=$?
  if [ $rc -ne 0 ]; then log "STOP: real $1 $MODE exit $rc"; exit $rc; fi
  log "DONE $1 1x $MODE"
}
log "start $MODE; slider=$(defaults read -g NSGlassTintAmount) rt=$(defaults read com.apple.universalaccess reduceTransparency) ic=$(defaults read com.apple.universalaccess increaseContrast) borders=$(defaults read com.apple.Accessibility ButtonShapesEnabled) $(displayplacer list | grep 'current mode' | grep -o 'mode [0-9]*')"
pass active $EA
pass inactive $EI
log "BOTH $MODE PASSES DONE"
