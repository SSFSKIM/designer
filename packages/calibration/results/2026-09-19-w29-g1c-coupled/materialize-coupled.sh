#!/bin/bash
# Publish the coupled increased-contrast profile from its banked runs —
# W29 G1c Part B, Decision Log 4 (b), claims §5.152 §B.
#
#   materialize-coupled.sh [--apply]
#
# The sibling of `../2026-09-18-w29-g1-bed/materialize-27.sh` and the same shape:
# one invocation per pass, seven runs each, `--frequency-settle` as Decision Log
# 1 (iii) implies and the 26.5 bed was frozen under, nothing written without
# `--apply`. Two passes rather than eight, because this sitting is one profile in
# two poses whose cells are disjoint — each pass appends its own cells and its own
# provenance block.
#
# What it refuses is the point of the second sitting: `src/run-provenance.ts`
# reads each run's attested `increaseContrast` and `reduceTransparency` and
# refuses before a PNG is opened if they disagree with the state the key names.
# The manifest cannot make that judgement — its `a11yMode` is
# `SystemAccessibility.current`, which reads `increased-contrast` in both states.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG="$(cd "$HERE/../.." && pwd)"
REPO="$(cd "$PKG/../.." && pwd)"
T="${VITREA_SITTING_DIR:-$HOME/vitrea-w29-27-run}"
APPLY="${1:-}"
[ -n "$APPLY" ] && [ "$APPLY" != "--apply" ] && { echo "usage: $0 [--apply]" >&2; exit 64; }

# The canonical declaration, for the roles a published cell carries — read as it
# stands now rather than from the manifest the capture wrote, because a role is a
# property of the declaration and moving a scene between sets cannot move a pixel.
export VITREA_SCENES="$REPO/apps/reference-apple/scenes.json"

PASSES="increased-contrast-coupled-active-1x increased-contrast-coupled-inactive-1x"

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
