#!/bin/bash
# W24 G0 (c) — the golden suite at the defaults, re-run and appended.
#
# `golden-ladder.sh`'s first section ran the suite three times under `nohup ... & disown` and every
# one of those runs was lost to the HARNESS rather than to the material: once to
# `net::ERR_CONNECTION_REFUSED` on four scenes, once to the fixture page never reaching
# `data-vitrea-ready` on thirty of thirty-one, and once to the same. None is a pixel comparison and
# none is rewritten here.
#
# The cause is the detachment and not the suite: Playwright's `webServer` is a child of the test
# process, and a `disown`ed run loses it. Run in the FOREGROUND the same suite passes 31 / 31 in
# nine seconds, twice, at the same commit. So this script runs in the foreground and appends its
# result beside the lost runs, which is the repository's rule for a reading taken again.
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
cd "$WORKTREE/packages/renderer-webgpu"
{
  echo
  echo "=============================================================================="
  echo "(1c) THE SUITE AT THE DEFAULTS, IN THE FOREGROUND — the runs above lost their webServer"
  echo "=============================================================================="
  npx playwright test --grep @golden --reporter=line 2>&1
} >> "$HERE/goldens-attribution.txt"
echo "-> appended"
