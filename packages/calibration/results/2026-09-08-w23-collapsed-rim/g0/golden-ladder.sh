#!/bin/bash
# W23 G0 (d) — the goldens run at the defaults and at every ladder point, and the attribution
# written.
#
# Two runs. First the SUITE as it stands, which at the shipped constants must pass byte-identical:
# that is the whole of this gate's claim that three new constants and a re-formed shader line moved
# nothing. Then `golden-ladder.spec.ts`, copied into the suite for the length of one run, which
# renders every golden scene at each ladder constant and reports where the delta landed.
#
# The spec is copied rather than committed to `e2e/golden/`: it is a measurement of this gate's
# candidates, not a regression the suite should carry.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
OUT="$HERE/goldens-attribution.txt"
SPEC="$WORKTREE/packages/renderer-webgpu/e2e/golden/w23-ladder.spec.ts"
cd "$WORKTREE/packages/renderer-webgpu"

{
  echo "W23 G0 — the goldens at the shipped defaults, and the rim law's reach at every ladder point"
  echo
  echo "=============================================================================="
  echo "(1) THE SUITE AT THE DEFAULTS — the attribution for the seam itself"
  echo "=============================================================================="
  echo "Three new profile constants (optics.rimLevelGain, optics.rimEnvGain, rimCollapsed), a"
  echo "re-formed rim line in the optics shader, one more vec4 in the optics uniform, and the CSS"
  echo "mirror's rim seam. All three constants are 0, so every golden must reproduce byte for byte"
  echo "AND the isolation proof's pinned hashes must reproduce from the named pre-C9a profile."
  echo
  npx playwright test --grep @golden --reporter=line 2>&1
  echo
  echo "=============================================================================="
  echo "(2) THE LADDER POINTS — where each constant's delta lands"
  echo "=============================================================================="
  cp "$HERE/golden-ladder.spec.ts" "$SPEC"
  npx playwright test w23-ladder --reporter=line 2>&1
  rm -f "$SPEC"
} > "$OUT" 2>&1
echo "-> $OUT"
