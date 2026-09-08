#!/bin/bash
# W24 G1 — the scratch material-profile documents the ladder renders at.
#
# The leaf writer is W22 G0's `make-candidates.mjs`, unchanged and called by path: it is a generic
# override over a SHIPPED document, which is what makes each rendered point attributable to the one
# leaf whose name it carries. `resolvedMaterialSha256` stays the shipped document's and is STALE in
# every copy, on W21's rule — a fabricated hash beside a changed patch is worse than an honest
# stale one that says so. Nothing here is ever committed to `profiles/`.
#
# ONE document serves both scales — `profiles/` holds only the 1x light and 1x dark documents and
# the 2x profile keys are captured against the same file — so the two scales are two ANCHORS in one
# document (`collapseTransmission` and `collapseTransmission2x`), exactly as the body's second
# scale is carried. A candidate therefore names both.
#
# Usage: `bash make-candidates.sh probe` or `bash make-candidates.sh fit <c1x> <c2x>`.
set -eu
WORKTREE=/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-aa8a0b1f92b46418f
P="$WORKTREE/packages/calibration/profiles"
MK="$WORKTREE/packages/calibration/results/2026-09-08-w22-resting-sweep/g0/make-candidates.mjs"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w24/g1
C="$T/candidates"
PHASE="${1:-probe}"
mkdir -p "$C"

if [ "$PHASE" = probe ]; then
  # The control: the shipped document with the new leaf pinned at its inert value, so the c = 0
  # capture is a rendered claim of byte identity rather than an argument about the arithmetic.
  node "$MK" "$P/apple-macos-26.5-1x-light-standard.json" "$C" \
    light-c0:collapseTransmission=0 light-c0:collapseTransmission2x=0
  # One non-zero rung per profile. 0.10 is chosen only to be large enough to read cleanly against
  # the 8-bit floor at these levels and small enough not to clip; the constant is LINEAR here, so
  # the rung's value does not bias the fit.
  node "$MK" "$P/apple-macos-26.5-1x-light-standard.json" "$C" \
    light-probe:collapseTransmission=0.1 light-probe:collapseTransmission2x=0.1
  node "$MK" "$P/apple-macos-26.5-1x-dark-standard.json" "$C" \
    dark-probe:collapseTransmission=0.1 dark-probe:collapseTransmission2x=0.1
else
  C1X="${2:?the 1x constant}"
  C2X="${3:?the 2x constant}"
  node "$MK" "$P/apple-macos-26.5-1x-light-standard.json" "$C" \
    "light-fit:collapseTransmission=$C1X" "light-fit:collapseTransmission2x=$C2X"
  node "$MK" "$P/apple-macos-26.5-1x-dark-standard.json" "$C" \
    "dark-fit:collapseTransmission=$C1X" "dark-fit:collapseTransmission2x=$C2X"
fi
ls -1 "$C"
