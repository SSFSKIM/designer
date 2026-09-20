#!/bin/sh
# The c9d chain at the 0.19.0 head (claims §5.155; `c9d-release-checklist.md`).
#
# W28 G4's chain script, unchanged except for this line and the machine reading it
# calls, which gained the macOS 27 appearance slider.
#
# Serial, one browser at a time, every browser step preceded by a machine-settings
# reading that refuses the run if either accessibility policy is on. Each step's whole
# output is kept beside this script under its own name, whatever it exits with — a step
# that fails is a record, not a reason to re-run until it is green.
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
  echo "$name exit=$status" >> "$here/chain-status.txt"
}

browser_step() {
  sh "$here/record-machine.sh" "$1"
  step "$@"
}

: > "$here/chain-status.txt"
cd "$repo"
step build pnpm -r build
step lint pnpm -r lint
step eslint-root npx eslint .
step units pnpm -r test

cd "$repo/packages/renderer-webgpu"
browser_step renderer-goldens pnpm run test:golden
browser_step renderer-gpu pnpm run test:gpu

cd "$repo/packages/platform-web"
browser_step platform-web npx playwright test

cd "$repo"
browser_step react-e2e pnpm --filter @vitreajs/vitrea-react test:e2e
browser_step demo-e2e pnpm --filter demo test:e2e

cat "$here/chain-status.txt"
