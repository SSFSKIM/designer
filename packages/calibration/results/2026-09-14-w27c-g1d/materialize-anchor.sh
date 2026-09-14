#!/bin/bash
# Publish Decision Log 18's two seven-run pluralities. Without APPLY=1 this
# materialises into VITREA_FIXTURES, which must name a scratch copy.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
SITTING="${VITREA_SITTING_ROOT:-$HOME/vitrea-w27c-g1d-2026-09-14}"
APPLY_FLAG=""
[ "${APPLY:-0}" = 1 ] && APPLY_FLAG="--apply"

for SCALE in 2 1; do
  args=""
  for run in 1 2 3 4 5 6 7; do
    args="$args --run run-$run=$SITTING/inactive-${SCALE}x/run-$run"
  done
  echo "=== inactive-${SCALE}x"
  # The generated arguments contain no whitespace: the sitting path is fixed by
  # the declaration and each label/path pair is one materialize argument.
  # shellcheck disable=SC2086
  pnpm --dir "$REPO" --filter @vitrea/calibration --fail-if-no-match exec \
    tsx cli/materialize.ts $args --set probe --frequency-settle $APPLY_FLAG
done
