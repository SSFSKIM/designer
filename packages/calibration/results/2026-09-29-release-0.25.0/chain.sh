#!/bin/sh
# The 0.25.0 release chain: W36 G2's ordered chain (0.24.0), adapted.
#
# Same steps, same order, serially. What changed, and why:
# - digests: the six shipped material digests are computed after the build and
#   compared with the expected literals, the documents' own fields and the
#   runtime's endpoints (this release claims no material moved).
# - goldens-bytes: after test:golden, the golden PNGs are compared byte for byte
#   with v0.24.0 and HEAD.
# - gated-count reads the current union through W40's matrix_store, because
#   results/matrix.json holds only the frozen macOS 26.5 rows since W40 G0.
# - X6 is WAITED for rather than refused on idle (run-browser.py).
# - Every browser suite, not only the demo, checks its server port at launch. The
#   ordinary configs reuse an existing server, and the main checkout is shared
#   with other sessions, so a held port would test someone else's code: a held
#   port runs the same suite on an isolated port with no reuse.
# - The chain HALTS at the first non-zero step. A failure is diagnosed before
#   anything else runs (a failure caused by the release's frame-loop change stops
#   the chain for good). Re-invoking skips every step whose log already exists,
#   so a resume never re-runs a recorded step, green or red.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)
package=$(cd "$here/../.." && pwd)
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
  if [ "$2" -ne 0 ]; then
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
browser() {
  name=$1; shift
  done_already "$name" && return 0
  set +e
  python3 "$here/run-browser.py" "chain-$name" "$@"
  status=$?
  set -e
  record "$name" "$status"
}
# Who holds a suite's port at launch, appended to ports.txt; exit 0 when it is held.
held() {
  echo "== $1 port $2 at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$here/ports.txt"
  if lsof -nP -iTCP:"$2" -sTCP:LISTEN >> "$here/ports.txt" 2>&1; then
    for pid in $(lsof -t -iTCP:"$2" -sTCP:LISTEN); do
      ps -o pid=,command= -p "$pid" >> "$here/ports.txt" 2>&1 || true
      lsof -a -d cwd -p "$pid" >> "$here/ports.txt" 2>&1 || true
    done
    echo "HELD: this suite runs on its isolated port, no reuse" >> "$here/ports.txt"
    return 0
  fi
  echo "free: ordinary config" >> "$here/ports.txt"
  return 1
}

cd "$package"
step freeze-open python3 results/2026-09-16-w29-freeze/freeze.py verify
step capture-tree pnpm exec tsx scripts/check-capture-tree.ts
cd "$repo"
step build pnpm -r build
cd "$package"
step digests pnpm exec tsx "$here/digests.ts"
cd "$repo"
step lint pnpm -r lint
step eslint-root pnpm exec eslint .
step units pnpm -r test

if ! done_already goldens && held goldens 5189; then
  export VITREA_GOLDEN_SERVER_PORT=5199
fi
browser goldens pnpm --filter @vitrea/renderer-webgpu --fail-if-no-match test:golden
step goldens-bytes python3 "$here/goldens-bytes.py"
if ! done_already gpu && held gpu 5189; then
  export VITREA_GOLDEN_SERVER_PORT=5199
fi
browser gpu pnpm --filter @vitrea/renderer-webgpu --fail-if-no-match test:gpu
unset VITREA_GOLDEN_SERVER_PORT || true

if ! done_already platform-web && held platform-web 5188; then
  browser platform-web pnpm --filter @vitreajs/vitrea-web --fail-if-no-match exec playwright test \
    --config "$here/isolated-platform-web.config.ts"
else
  browser platform-web pnpm --filter @vitreajs/vitrea-web --fail-if-no-match exec playwright test
fi
if ! done_already react-e2e && held react-e2e 5176; then
  browser react-e2e pnpm --filter @vitreajs/vitrea-react --fail-if-no-match exec playwright test \
    --config "$here/isolated-react.config.ts"
else
  browser react-e2e pnpm --filter @vitreajs/vitrea-react --fail-if-no-match test:e2e
fi
if ! done_already demo-e2e && held demo-e2e 5177; then
  browser demo-e2e pnpm --filter demo --fail-if-no-match exec playwright test \
    --config "$here/isolated-demo.config.ts"
else
  browser demo-e2e pnpm --filter demo --fail-if-no-match test:e2e
fi

cd "$package"
step gated-count python3.12 "$here/gated-count.py"
step freeze-close python3 results/2026-09-16-w29-freeze/freeze.py verify
echo "chain complete" | tee -a "$here/chain-invocations.txt"
cat "$here/chain-status.txt"
