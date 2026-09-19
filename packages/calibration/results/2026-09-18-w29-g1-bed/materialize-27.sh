#!/bin/bash
# Publish the macOS 27 bed from the banked runs — W29 G1 Part B, claims §5.150.
#
#   materialize-27.sh [--apply]
#
# One invocation per pass, seven runs each, in the order the sitting ran them.
# A pass is the unit because it is the unit the runs were taken in: `materialize`
# decides the published byte-state per cell ACROSS the runs of one configuration,
# and a profile is captured by two passes (one per pose) whose cells are disjoint,
# so each pass appends its own cells and its own provenance block to the bed.
#
# `--frequency-settle` is the mode W29 Decision Log 1 (iii) implies and the 26.5
# bed was frozen under (Decision Log 21): a cell that holds more than one settled
# byte-state is published at its MAJORITY and marked `frequencySettled`, with the
# observed frequencies beside it, so a reader can see it was decided by counting
# rather than by agreement. A tie is still refused — frequency cannot settle what
# has no majority — and a refusal is the finding rather than an error to repair.
#
# Without `--apply` nothing is written and every cell's resolution is printed.
# Run it that way first: the dry pass is the only place a refusal can be read
# before the bundle has changed.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG="$(cd "$HERE/../.." && pwd)"
REPO="$(cd "$PKG/../.." && pwd)"
T="${VITREA_SITTING_DIR:-$HOME/vitrea-w29-27-run}"
APPLY="${1:-}"
[ -n "$APPLY" ] && [ "$APPLY" != "--apply" ] && { echo "usage: $0 [--apply]" >&2; exit 64; }

# The canonical declaration, for the roles a published cell carries. `materialize`
# reads the role from the DECLARATION as it stands now rather than from the
# manifest the capture wrote, because a role is a property of the declaration and
# moving a scene between sets cannot change a pixel.
export VITREA_SCENES="$REPO/apps/reference-apple/scenes.json"

PASSES="standard-active-2x standard-inactive-2x standard-active-1x standard-inactive-1x
        increased-contrast-active-1x increased-contrast-inactive-1x
        reduced-transparency-active-1x reduced-transparency-inactive-1x"

for P in $PASSES; do
  RUNS=""
  for N in 1 2 3 4 5 6 7; do
    D="$T/$P/run-$N"
    [ -f "$D/manifest.json" ] || { echo "REFUSED: $P run-$N has no manifest.json" >&2; exit 1; }
    RUNS="$RUNS --run r$N=$D"
  done
  echo "================================================================"
  echo "== $P"
  echo "================================================================"
  # shellcheck disable=SC2086  # the run list is built as a string for bash 3.2
  (cd "$PKG" && npx tsx cli/materialize.ts $RUNS --frequency-settle $APPLY)
done
