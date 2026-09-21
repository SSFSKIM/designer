#!/bin/sh
# The c9d chain at the 0.21.0 cut (claims §5.165 §5; `c9d-release-checklist.md`).
#
# W30 G4's `chain.sh` in shape, run at the version bump's head rather than after
# it: the nine steps the checklist's "full chain" names, in its order, serially,
# one browser at a time, each browser step preceded by a machine-settings reading
# that REFUSES the run if either accessibility policy is on.
#
# Every step's whole output is kept beside this script under its own name,
# whatever it exits with — a step that fails is a record, not a reason to re-run
# until it is green. `chain-status.v2.txt` is the MACHINE's exit codes; the
# ledger's table is written from it rather than typed beside it.
#
# The two evidence steps the checklist does not list but every gate of this wave
# has run are here too, first and last: `freeze.py verify` (the macOS 26.5 bed,
# 1,818 entries) and `gated-count.py` (the macOS 27 bed, 230 gated cells / 726
# rows, which contract X10 pins at every merge).
set -e
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)
package=$(cd "$here/../.." && pwd)

step() {
  name=$1
  shift
  printf '\n== %s\n' "$name"
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

cd "$package"
step freeze-open python3 results/2026-09-16-w29-freeze/freeze.py verify

cd "$repo"
step build pnpm -r build
step lint pnpm -r lint
step eslint-root npx eslint .
step units pnpm -r test

browser_step goldens pnpm --filter @vitrea/renderer-webgpu test:golden
browser_step gpu pnpm --filter @vitrea/renderer-webgpu test:gpu
browser_step platform-web sh -c 'cd packages/platform-web && npx playwright test'
browser_step react-e2e pnpm --filter @vitreajs/vitrea-react test:e2e
browser_step demo-e2e pnpm --filter demo test:e2e

cd "$package"
step gated-count python3 results/2026-09-21-w31-g4-landing/gated-count.py
step freeze-close python3 results/2026-09-16-w29-freeze/freeze.py verify

cat "$here/chain-status.v2.txt"
