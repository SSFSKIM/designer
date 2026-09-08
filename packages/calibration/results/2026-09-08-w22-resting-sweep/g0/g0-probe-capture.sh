#!/bin/bash
# W22 G0 (c) — the DARK patch's `rimAlpha` re-read on W21's own rows, with the band gone.
#
# W21 G1 fitted `optics.regular.rimAlpha` to 0.082 on the probe's six solid cells over THREE sides,
# excluding the left because the resting sweep sat on it (claims 5.90 2 and 4). W22 clause 3 asks
# whether that constant moves once the fourth side is readable. Reproducing the fit needs the same
# bed and the same two rendered points, so this renders W21's grid at the gate:
#
#   probe-dark-rim002 / probe-dark-rim018   the shipped dark document at `rimAlpha` 0.02 and 0.18 —
#                                           the two points that fix the line, W21's own pair.
#   probe-dark-rim0082                      the shipped 0.082, the confirmation render.
#
# The bed is the committed probe (`../../2026-09-06-w21-dark-scheme/probe/`) through
# `VITREA_SCENES` / `VITREA_FIXTURES`, so no canonical scene file or fixture is read; every capture
# goes to scratch. `--set calibration,validation` keeps the probe's own holdout column unread.
#
# The GPU is shared: one capture process at a time, and this script serialises every run.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes-w21-probe.json"
PROBE="$(cd "$HERE/../../2026-09-06-w21-dark-scheme/probe" && pwd)"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0/probe
C=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0/candidates
mkdir -p "$T"
rm -f "$T/DONE"
LOG="$T/probe-runs.log"
: > "$LOG"
cd "$WORKTREE/packages/calibration"
node "$HERE/make-candidates.mjs" profiles/apple-macos-26.5-1x-dark-standard.json "$C" \
  "dark-rim002:optics.regular.rimAlpha=0.02" \
  "dark-rim018:optics.regular.rimAlpha=0.18" \
  "dark-rim0082:optics.regular.rimAlpha=0.082"
run() {
  local label=$1
  local out="$T/$label"
  mkdir -p "$out"
  echo "=== $(date +%H:%M:%S) $label on the W21 probe grid ==="
  VITREA_SCENES="$SCENES" VITREA_FIXTURES="$PROBE" VITREA_WEB_CAPTURES="$out/web-captures" \
    npx tsx cli/compare.ts --profile apple-macos-26.5-1x-dark-standard \
    --material-profile "$C/${label#probe-}.json" --renderer webgpu \
    --set calibration,validation --allow-colourless-tints --write-partial \
    --out-matrix "$out/matrix.json" >> "$LOG" 2>&1
  echo "    exit=$?"
}
run probe-dark-rim002
run probe-dark-rim018
run probe-dark-rim0082
echo "ALL PROBE RUNS DONE $(date +%H:%M:%S)"
touch "$T/DONE"
