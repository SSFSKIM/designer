#!/bin/bash
# W24 G2 — the goldens: the attribution, the regeneration, and the isolation proof's new hashes.
#
# Four steps, in the foreground throughout. A golden run detached with `nohup … & disown` loses
# Playwright's `webServer`, which is a child of the test process (W24 Decision Log 2 (h)); the suite
# takes about ten seconds and there is nothing to detach for.
#
#   (1) the attribution — `g2-golden-attribution.spec.ts`, copied into the suite for the length of
#       one run, which renders every scene at the landed constants and at each mechanism declined
#       and says where the delta landed. It is EVIDENCE and not a suite member: committing it would
#       pin a scratch constant into CI.
#   (2) the suite as it stands, whose failures name every golden the two mechanisms moved.
#   (3) the regeneration, behind (1) and (2), and the isolation proof re-run so its own pinned
#       hashes are read at the landed material.
#   (4) the suite again, which must now be green.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
OUT="$HERE/goldens-attribution.txt"
SPEC="$WORKTREE/packages/renderer-webgpu/e2e/golden/w24-g2-attribution.spec.ts"
cd "$WORKTREE/packages/renderer-webgpu"
{
  echo "W24 G2 — the goldens at the landed constants"
  echo "HEAD $(git -C "$WORKTREE" rev-parse --short HEAD)"
  echo
  echo "=============================================================================="
  echo "(1) THE ATTRIBUTION — where each mechanism's delta lands, per scene"
  echo "=============================================================================="
  cp "$HERE/g2-golden-attribution.spec.ts" "$SPEC"
  npx playwright test w24-g2-attribution --reporter=line 2>&1
  rm -f "$SPEC"
  echo
  echo "=============================================================================="
  echo "(2) THE SUITE BEFORE REGENERATION — which goldens moved"
  echo "=============================================================================="
  npx playwright test --grep @golden --reporter=line 2>&1
} > "$OUT" 2>&1
echo "-> $OUT"
