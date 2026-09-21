#!/bin/sh
# The PARENT's final chain at the 0.21.0 head after the G4 review closure (05d2d5a7), the same
# steps as chain.sh, writing chain-parent-final-* beside the gate's own logs (never over them).
#
# W30 G4's `chain.sh` in shape, run at the version bump's head rather than after
# it: the nine steps the checklist's "full chain" names, in its order, serially,
# one browser at a time, each browser step preceded by a machine-settings reading
# that REFUSES the run if either accessibility policy is on.
#
# Every step's whole output is kept beside this script under its own name,
# whatever it exits with — a step that fails is a record, not a reason to re-run
# until it is green. `chain-parent-final-status.txt` is the MACHINE's exit codes; the
# ledger's table is written from it rather than typed beside it.
#
# The two evidence steps the checklist does not list but every gate of this wave
# has run are here too, first and last: `freeze.py verify` (the macOS 26.5 bed,
# 1,818 entries) and `gated-count.py` (the macOS 27 bed, 230 gated cells / 726
# rows, which contract X10 pins at every merge).
#
# **2026-09-21, W31 G4 review closure (claims §5.165 §9, finding N10).** Every
# `pnpm --filter` step below now passes `--fail-if-no-match`, which `CLAUDE.md`
# mandates and which this script did not have: a filter that matches nothing exits
# 0 and runs nothing, so a renamed package would have written an empty log, a
# green exit code into `chain-parent-final-status.txt`, and a row in the ledger's table
# saying a suite passed that never ran. The committed logs beside this script are
# NOT affected and are not re-run — each names its suite and its per-file counts,
# so the record shows the suites did run. The flag is here for the next chain.
set -e
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)
package=$(cd "$here/../.." && pwd)

step() {
  name=$1
  shift
  printf '\n== %s\n' "$name"
  set +e
  "$@" > "$here/chain-parent-final-$name.txt" 2>&1
  status=$?
  set -e
  printf '%s exit=%s\n' "$name" "$status"
  echo "$name exit=$status" >> "$here/chain-parent-final-status.txt"
}

browser_step() {
  sh "$here/record-machine.sh" "$1"
  step "$@"
}

: > "$here/chain-parent-final-status.txt"

cd "$package"
step freeze-open python3 results/2026-09-16-w29-freeze/freeze.py verify

cd "$repo"
step build pnpm -r build
step lint pnpm -r lint
step eslint-root npx eslint .
step units pnpm -r test

browser_step goldens pnpm --filter @vitrea/renderer-webgpu --fail-if-no-match test:golden
browser_step gpu pnpm --filter @vitrea/renderer-webgpu --fail-if-no-match test:gpu
browser_step platform-web sh -c 'cd packages/platform-web && npx playwright test'
browser_step react-e2e pnpm --filter @vitreajs/vitrea-react --fail-if-no-match test:e2e
browser_step demo-e2e pnpm --filter demo --fail-if-no-match test:e2e

cd "$package"
step gated-count python3 results/2026-09-21-w31-g4-landing/gated-count.py
step freeze-close python3 results/2026-09-16-w29-freeze/freeze.py verify

cat "$here/chain-parent-final-status.txt"
