#!/bin/sh
# The c9d chain at the 0.20.0 head, re-run by the W30 G4 review closure (claims
# §5.160 §9; `c9d-release-checklist.md`).
#
# W29 G4's chain script, unchanged in shape. It exists here because the landing's
# `chain-status.txt` was hand-typed and two of the checklist's nine steps had no
# committed output at all: root `npx eslint .`, which the landing's table omits,
# and the demo Playwright suite, whose row reads "(run before the cut)". Those two
# take their canonical names — `chain-eslint-root.txt` and `chain-demo-e2e.txt` —
# and the three steps the landing already recorded are re-run under `.v2` names so
# no committed log is overwritten. The status file is `chain-status.v2.txt`, the
# MACHINE's exit codes beside the hand-typed table rather than over it.
#
# Serial, one browser at a time, the browser step preceded by a machine-settings
# reading that refuses the run if either accessibility policy is on. Each step's
# whole output is kept beside this script under its own name, whatever it exits
# with — a step that fails is a record, not a reason to re-run until it is green.
#
# The version does not move and no changeset is added: this closure changes
# comments, tests, guards, records and prose only.
set -e
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)

step() {
  name=$1
  shift
  printf '\n══ %s\n' "$name"
  set +e
  "$@" > "$here/chain-$name.txt" 2>&1
  status=$?
  set -e
  printf '%s exit=%s\n' "$name" "$status"
  echo "$name exit=$status" >> "$here/chain-status.v2.txt"
}

browser_step() {
  sh "$here/record-machine.sh" "$1"
  step "$@"
}

: > "$here/chain-status.v2.txt"
cd "$repo"
step build.v2 pnpm -r build
step lint.v2 pnpm -r lint
step eslint-root npx eslint .
step units.v2 pnpm -r test

browser_step demo-e2e pnpm --filter demo test:e2e

cat "$here/chain-status.v2.txt"
