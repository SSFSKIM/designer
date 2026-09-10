#!/bin/bash
# W26 G2 — the goldens: the attribution, the regeneration, and the isolation proof's new hashes.
#
# W25 G3's script at this wave's two constants. Four steps, in the FOREGROUND throughout: a golden
# run detached with `nohup … & disown` loses Playwright's `webServer`, which is a child of the test
# process (W24 Decision Log 2 (h)), and the suite takes about ten seconds.
#
#   (1) the attribution — `g2-golden-attribution.spec.ts`, copied into the suite for the length of
#       one run, which renders every scene at the landed width and with both anchors declined and
#       says where the delta landed and on which spans. EVIDENCE, not a suite member: committing it
#       would pin a scratch constant into CI.
#   (2) the suite as it stands, whose failures name every golden the width moved.
#   (3) the regeneration, behind (1) and (2), and the isolation proof re-run so its own pinned
#       hashes are read at the landed material.
#   (4) the suite again, which must now be green — 33 of 33.
#
# Steps (3) and (4) run only when this is called with `--regen`, so the attribution can be taken and
# read before any golden byte is rewritten. The GPU guard is the caller's: these run on the same
# adapter as the captures and X4 is one at a time.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
OUT="$HERE/${OUT_NAME:-g2-goldens-attribution.txt}"
SPEC="$WORKTREE/packages/renderer-webgpu/e2e/golden/w26-g2-attribution.spec.ts"
REGEN="${1:-}"
cd "$WORKTREE/packages/renderer-webgpu"
{
  echo "W26 G2 — the goldens at the landed heavy width (sizeHeavyTapSigma 9, sizeHeavyTapSigma2x 9)"
  echo "HEAD $(git -C "$WORKTREE" rev-parse --short HEAD)"
  echo
  echo "=============================================================================="
  echo "(1) THE ATTRIBUTION — where the width's delta lands, per scene"
  echo "=============================================================================="
  cp "$HERE/g2-golden-attribution.spec.ts" "$SPEC"
  npx playwright test w26-g2-attribution --reporter=line 2>&1
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
