#!/bin/sh
# W33's ordered chain, widened to W36's four-fact X6 preflight (§5.180 clause 8).
# Every attempted suite keeps its first result, including a React timing red.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)
package=$(cd "$here/../.." && pwd)
export VITREA_WEB_CAPTURES=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures
[ -d "$VITREA_WEB_CAPTURES" ] || { echo 'UNMEASURED: canonical tree absent'; exit 1; }
[ ! -e "$here/chain-status.txt" ] || { echo 'Chain already attempted'; exit 1; }
step() {
  name=$1; shift
  set +e
  "$@" > "$here/chain-$name.txt" 2>&1
  status=$?
  set -e
  echo "$name exit=$status" | tee -a "$here/chain-status.txt"
}
browser() {
  name=$1; shift
  set +e
  python3 "$here/run-browser.py" "chain-$name" "$@"
  status=$?
  set -e
  echo "$name exit=$status" | tee -a "$here/chain-status.txt"
}
cd "$package"
step freeze-open python3 results/2026-09-16-w29-freeze/freeze.py verify
step capture-tree pnpm exec tsx scripts/check-capture-tree.ts
cd "$repo"
step build pnpm -r build
step lint pnpm -r lint
step eslint-root pnpm exec eslint .
step units pnpm -r test
browser goldens pnpm --filter @vitrea/renderer-webgpu --fail-if-no-match test:golden
browser gpu pnpm --filter @vitrea/renderer-webgpu --fail-if-no-match test:gpu
browser platform-web pnpm --filter @vitreajs/vitrea-web --fail-if-no-match exec playwright test
browser react-e2e pnpm --filter @vitreajs/vitrea-react --fail-if-no-match test:e2e
# A pre-existing demo on the normal port must not be reused across worktrees.
if lsof -nP -iTCP:5177 -sTCP:LISTEN > "$here/demo-port.txt" 2>&1; then
  echo 'Port 5177 held; isolated 5197, normal tests and launch policy, no reuse.' >> "$here/demo-port.txt"
  browser demo-e2e pnpm --filter demo --fail-if-no-match exec playwright test --config "$here/demo-isolated.config.ts"
else
  echo 'Port 5177 free at launch; ordinary demo config.' >> "$here/demo-port.txt"
  browser demo-e2e pnpm --filter demo --fail-if-no-match test:e2e
fi
cd "$package"
step gated-count python3 "$here/gated-count.py"
step freeze-close python3 results/2026-09-16-w29-freeze/freeze.py verify
cat "$here/chain-status.txt"
