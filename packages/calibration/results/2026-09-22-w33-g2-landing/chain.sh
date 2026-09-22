#!/bin/sh
# W32 G2 chain, copied for 0.23.0 (§5.173, W33 DL4).
# Every exit is retained. No React timing red is rerun. X6 precedes each browser.
set -e
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)
package=$(cd "$here/../.." && pwd)
export VITREA_WEB_CAPTURES="${VITREA_WEB_CAPTURES:-/Users/new/Developer/GitHub/designer/packages/calibration/web-captures}"
[ -d "$VITREA_WEB_CAPTURES" ] || { echo 'UNMEASURED: canonical tree absent'; exit 1; }

step() {
  name=$1
  shift
  printf '\n== %s\n' "$name"
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

cd "$package"
step freeze-open python3 results/2026-09-16-w29-freeze/freeze.py verify
step capture-tree env VITREA_WEB_CAPTURES="${VITREA_WEB_CAPTURES:-$package/web-captures}" \
  npx tsx scripts/check-capture-tree.ts

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
step gated-count python3 results/2026-09-22-w33-g2-landing/gated-count.py
step freeze-close python3 results/2026-09-16-w29-freeze/freeze.py verify

cat "$here/chain-status.txt"
