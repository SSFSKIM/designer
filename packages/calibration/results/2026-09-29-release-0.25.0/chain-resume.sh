#!/bin/sh
# Resume the 0.25.0 chain after its first platform-web run (platform-web-run1-diagnosis.txt).
#
# That run is kept as the record: 165 Chromium/chromium-gpu passes and 246 Firefox/WebKit
# cases that never launched, because the machine's Playwright cache no longer held the
# firefox-1538 and webkit-2336 builds @playwright/test 1.62.1 needs. The two builds were
# installed (browsers-install.txt) and nothing else changed. This runs the platform-web suite
# once more under its own X6 preflight and port check, as chain-platform-web-run2.txt, then
# hands back to chain.sh, which skips every step already recorded and continues from React.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)
export VITREA_WEB_CAPTURES=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures
echo "resume $(date -u +%Y-%m-%dT%H:%M:%SZ) at $(git -C "$repo" rev-parse HEAD)" >> "$here/chain-invocations.txt"
cd "$repo"
if [ ! -e "$here/chain-platform-web-run2.txt" ]; then
  echo "== platform-web-run2 port 5188 at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$here/ports.txt"
  if lsof -nP -iTCP:5188 -sTCP:LISTEN >> "$here/ports.txt" 2>&1; then
    echo "HELD: isolated port 5198, no reuse" >> "$here/ports.txt"
    config="--config $here/isolated-platform-web.config.ts"
  else
    echo "free: ordinary config" >> "$here/ports.txt"
    config=""
  fi
  set +e
  # shellcheck disable=SC2086
  python3 "$here/run-browser.py" chain-platform-web-run2 \
    pnpm --filter @vitreajs/vitrea-web --fail-if-no-match exec playwright test $config
  status=$?
  set -e
  echo "platform-web-run2 exit=$status" | tee -a "$here/chain-status.txt"
  if [ "$status" -ne 0 ]; then
    echo "HALT after platform-web-run2 (exit $status): diagnose before resuming" \
      | tee -a "$here/chain-status.txt"
    exit "$status"
  fi
fi
exec sh "$here/chain.sh"
