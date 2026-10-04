#!/bin/sh
# W45 G2's c9d chain at the landing's head (claims §5.207; docs/doperpowers/specs/c9d-release-checklist.md).
#
# The 0.25.0 chain's steps and order (results/2026-09-29-release-0.25.0/chain.sh), with W45's
# additions: X41 beside the freeze at open, the ten-digest step, and W45's two declaration checks at
# the close. Every browser launch goes through W45's GPU lock and classifying web census
# (results/2026-10-03-w45-g0-operator/with-gpu.sh, appending to that directory's census.jsonl), and
# its suite's port is checked free first, so no suite can reuse another session's server. The chain
# HALTS at the first non-zero gated step; re-invoking skips every step whose log exists. The two
# declaration checks are recorded with their exit codes and never halt: they are expected to fail
# on the tool tests that build from the live light documents (the tracker's W45 entry), and
# close-checks.txt says which check reads what.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
package=$(cd "$here/../../.." && pwd)
repo=$(cd "$package/../.." && pwd)
gpu="$package/results/2026-10-03-w45-g0-operator/with-gpu.sh"
export VITREA_WEB_CAPTURES=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures
[ -d "$VITREA_WEB_CAPTURES" ] || { echo 'UNMEASURED: canonical tree absent'; exit 1; }
echo "invocation $(date -u +%Y-%m-%dT%H:%M:%SZ) at $(git -C "$repo" rev-parse HEAD)" >> "$here/chain-invocations.txt"

done_already() {
  if [ -e "$here/chain-$1.txt" ]; then
    echo "$1 skipped: already recorded" | tee -a "$here/chain-invocations.txt"
    return 0
  fi
  return 1
}
record() {
  echo "$1 exit=$2" | tee -a "$here/chain-status.txt"
  if [ "$2" -ne 0 ] && [ "${3:-gated}" = gated ]; then
    echo "HALT after $1 (exit $2): diagnose before resuming" | tee -a "$here/chain-status.txt"
    exit "$2"
  fi
}
step() {
  name=$1; shift
  done_already "$name" && return 0
  set +e
  "$@" > "$here/chain-$name.txt" 2>&1
  status=$?
  set -e
  record "$name" "$status"
}
recorded() {
  name=$1; shift
  done_already "$name" && return 0
  set +e
  "$@" > "$here/chain-$name.txt" 2>&1
  status=$?
  set -e
  record "$name" "$status" recorded
}
browser() {
  name=$1; port=$2; shift 2
  done_already "$name" && return 0
  if lsof -nP -iTCP:"$port" -sTCP:LISTEN > "$here/chain-$name.port.txt" 2>&1; then
    echo "$name: port $port is held; refusing to reuse another server" | tee -a "$here/chain-status.txt"
    exit 4
  fi
  set +e
  "$gpu" "w45-g2-chain-$name" "$@" > "$here/chain-$name.txt" 2>&1
  status=$?
  set -e
  record "$name" "$status"
}

cd "$package"
step freeze-open python3 results/2026-09-16-w29-freeze/freeze.py verify
step x41-open pnpm exec tsx results/2026-10-01-w43-g0-declaration/x41/x41.ts verify
step capture-tree pnpm exec tsx scripts/check-capture-tree.ts
cd "$repo"
step build pnpm -r build
cd "$package"
step digests pnpm exec tsx "$here/digests.ts"
cd "$repo"
step lint pnpm -r lint
step eslint-root pnpm exec eslint .
step units pnpm -r test
browser goldens 5189 pnpm --filter @vitrea/renderer-webgpu --fail-if-no-match test:golden
browser gpu 5189 pnpm --filter @vitrea/renderer-webgpu --fail-if-no-match test:gpu
browser platform-web 5188 pnpm --filter @vitreajs/vitrea-web --fail-if-no-match exec playwright test
browser react-e2e 5176 pnpm --filter @vitreajs/vitrea-react --fail-if-no-match test:e2e
browser demo-e2e 5177 pnpm --filter demo --fail-if-no-match test:e2e
cd "$package"
recorded declare-check python3.12 -B results/2026-10-03-w45-g0-operator/declare.py check
recorded declare-check-fit python3.12 -B results/2026-10-03-w45-g0-operator/declare.py check-fit
step capture-tree-close pnpm exec tsx scripts/check-capture-tree.ts
step x41-close pnpm exec tsx results/2026-10-01-w43-g0-declaration/x41/x41.ts verify
step freeze-close python3 results/2026-09-16-w29-freeze/freeze.py verify
echo "chain complete $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$here/chain-status.txt"
