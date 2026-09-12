#!/bin/bash
# W27c G2 read, step 1: publish the sitting's seven-run plurality into the bundle.
#
# One `materialize` invocation per pass, because a pass is one snapshot set: the
# seven runs of one pose at one scale under one accessibility mode, each run a
# whole directory with its own manifest. `--set probe` is the declaration of how
# these rows enter (claims §5.134 §5, §5.136 §6, W27 Decision Log 13): the whole
# checking bed is declared `probe` in `scenes.json`'s split, so a cell whose id
# carries any other role is skipped before its bytes are read. That is what keeps
# the six pre-existing recovered ids the bed re-captures — three calibration and
# three holdout — from being republished over the frozen bed at the probe bar.
# Their fresh bytes are read where they belong, in the group E re-attestation
# (clause 5), and never written.
#
# `--frequency-settle` is the mode the frozen bed was built under (Decision Log
# 21): a cell holding two settled appearances is published at its majority and
# marked, with the frequencies beside it, rather than refused. It is also what
# writes `stateFrequencies`, `observedStates` and `frequencySettled` — three of
# the attestation fields §5.134 §5 asks for, which only materialisation can write
# (§5.136 §7).
#
#   VITREA_FIXTURES=/tmp/scratch-root ./materialize-bed.sh        # dry run into scratch
#   APPLY=1 ./materialize-bed.sh                                  # publish into the bundle
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
SITTING="${VITREA_SITTING_ROOT:-$HOME/vitrea-w27-26.5-run}"
APPLY_FLAG=""
if [ "${APPLY:-0}" = "1" ]; then APPLY_FLAG="--apply"; fi

run_pass() {
  local name="$1" dir="$2"
  local args=()
  for r in 1 2 3 4 5 6 7; do
    args+=(--run "run-$r=$SITTING/$dir/run-$r")
  done
  echo "=== $name ($dir)"
  (cd "$REPO" && pnpm --filter @vitrea/calibration --fail-if-no-match exec \
    tsx cli/materialize.ts "${args[@]}" --set probe --frequency-settle $APPLY_FLAG)
}

run_pass inactive-2x inactive-2x
run_pass active-2x active-2x
run_pass inactive-1x inactive-1x
run_pass active-1x active-1x
run_pass inactive-1x-increase-contrast a11y-increase-contrast/inactive-1x
run_pass inactive-1x-reduce-transparency a11y-reduce-transparency/inactive-1x
