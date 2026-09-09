#!/bin/bash
# W25 G3 — the goldens: the attribution, the regeneration, and the isolation proof's new hashes.
#
# W24 G2's script, at this wave's one mechanism. Four steps, in the FOREGROUND throughout: a golden
# run detached with `nohup … & disown` loses Playwright's `webServer`, which is a child of the test
# process (W24 Decision Log 2 (h)), and the suite takes about ten seconds.
#
#   (1) the attribution — `g3-golden-attribution.spec.ts`, copied into the suite for the length of
#       one run, which renders every scene at the landed slope and with the field declined and says
#       where the delta landed and on which spans. EVIDENCE, not a suite member: committing it
#       would pin a scratch constant into CI.
#   (2) the suite as it stands, whose failures name every golden the field moved.
#   (3) the regeneration, behind (1) and (2), and the isolation proof re-run so its own pinned
#       hashes are read at the landed material.
#   (4) the suite again, which must now be green.
#
# Steps (3) and (4) run only when this is called with `--regen`, so the attribution can be taken
# and read before any golden byte is rewritten.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
OUT="$HERE/goldens-attribution.txt"
SPEC="$WORKTREE/packages/renderer-webgpu/e2e/golden/w25-g3-attribution.spec.ts"
REGEN="${1:-}"
cd "$WORKTREE/packages/renderer-webgpu"
{
  echo "W25 G3 — the goldens at the landed constant (optics.regular.rimAlongSideSlope 0.45)"
  echo "HEAD $(git -C "$WORKTREE" rev-parse --short HEAD)"
  echo
  echo "=============================================================================="
  echo "(1) THE ATTRIBUTION — where the field's delta lands, per scene"
  echo "=============================================================================="
  cp "$HERE/g3-golden-attribution.spec.ts" "$SPEC"
  npx playwright test w25-g3-attribution --reporter=line 2>&1
  rm -f "$SPEC"
  echo
  echo "=============================================================================="
  echo "(2) THE SUITE BEFORE REGENERATION — which goldens moved"
  echo "=============================================================================="
  npx playwright test --grep @golden --reporter=line 2>&1
  if [ "$REGEN" = "--regen" ]; then
    echo
    echo "=============================================================================="
    echo "(3) THE REGENERATION"
    echo "=============================================================================="
    pnpm run goldens:regen 2>&1
    echo
    echo "=============================================================================="
    echo "(4) THE SUITE AFTER REGENERATION — the new hashes read at the landed material"
    echo "=============================================================================="
    npx playwright test --grep @golden --reporter=line 2>&1
  fi
} > "$OUT" 2>&1
echo "-> $OUT"
