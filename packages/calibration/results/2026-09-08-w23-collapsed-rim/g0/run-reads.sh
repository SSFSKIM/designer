#!/bin/bash
# W23 G0 (b) — every bed read at the contour, and W22's band read taken beside it.
#
# Three beds, one reader:
#
#   the canonical bed        six committed profiles, native fixtures against the LANDED captures
#                            (the 0.11.0 bed, matrix 3587400) on both tiers. `--sets` includes the
#                            holdout, because this is a READ of captures already taken at a
#                            configuration whose holdout was spent by W22 G1 — no fit and no ladder
#                            capture in this gate touches a holdout cell (the wave's X3).
#   W21's probe bed          the DARK reference over dark-solid / mid-dark-solid / light-solid at
#                            three sizes, with the W21 captures beside it.
#   W9's probe bed           the same grid under the LIGHT reference. Its web captures are W9-era
#                            and the material has moved many times since, so the web column there
#                            is context only; the NATIVE column is the law's fitting ground.
#
# The band read (W21 `g0/read.py`, the declared box's outer 3 CSS px, one peak per side) runs on
# the canonical bed beside the contour read, so that W22 clause 2 can be re-checked on its own
# instrument (W23 X1) without re-deriving it.
#
# Nothing here writes anything canonical: every output is under this gate's own directory.
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
MAIN=/Users/new/Developer/GitHub/designer
CONTOUR="$HERE/read-contour.py"
BAND="$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme/g0/read.py"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$MAIN/apps/reference-apple/fixtures"
CAPTURES="$MAIN/packages/calibration/web-captures"
W21="$WORKTREE/packages/calibration/results/2026-09-06-w21-dark-scheme"
SCRATCH=/Users/new/.claude/jobs/5c70e47f/tmp

mkdir -p "$HERE/reads"
for PROFILE in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
               apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard \
               apple-macos-26.5-1x-light-reduced-transparency \
               apple-macos-26.5-1x-light-increased-contrast; do
  for TIER in webgpu css; do
    "$PY" "$CONTOUR" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
      --captures "$CAPTURES" --tier "$TIER" --sets calibration,validation,holdout,recorded \
      --json "$HERE/reads/canonical-$PROFILE-$TIER.json" \
      > "$HERE/reads/canonical-$PROFILE-$TIER.txt" 2>/dev/null
    echo "contour $PROFILE / $TIER"
  done
  "$PY" "$BAND" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
    --captures "$CAPTURES" --tier webgpu --sets calibration,validation,holdout,recorded \
    --json "$HERE/reads/band-$PROFILE-webgpu.json" \
    > "$HERE/reads/band-$PROFILE-webgpu.txt" 2>/dev/null
  echo "band    $PROFILE / webgpu"
done

# W21's probe bed: the dark reference on the solid grid, with W21's own captures beside it.
"$PY" "$CONTOUR" --scenes "$WORKTREE/apps/reference-apple/scenes-w21-probe.json" \
  --fixtures "$W21/probe" --profile apple-macos-26.5-1x-dark-standard \
  --sets calibration,validation,holdout,recorded \
  --json "$HERE/reads/probe-w21-dark.json" > "$HERE/reads/probe-w21-dark.txt" 2>/dev/null
echo "contour W21 probe (dark reference)"

# W9's probe bed: the light reference on the same grid. Fixtures and captures live in scratch.
"$PY" "$CONTOUR" --scenes "$WORKTREE/apps/reference-apple/scenes-w9-probe.json" \
  --fixtures "$SCRATCH/w9-probe-fixtures" --profile apple-macos-26.5-1x-light-standard \
  --captures "$SCRATCH/w9-web-captures" --tier webgpu \
  --sets calibration,validation,holdout,recorded \
  --json "$HERE/reads/probe-w9-light.json" > "$HERE/reads/probe-w9-light.txt" 2>/dev/null
echo "contour W9 probe (light reference)"
