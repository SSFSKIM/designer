#!/bin/bash
# W26 G1 §7 — the candidate over the probe set in the DARK scheme, patched into BOTH documents.
#
# WHY THIS RUN EXISTS. G1's `pc` rung wrote the candidate's constants into the LIGHT document only
# (`g0-candidate.py`'s `light:` scope), and the dark document is a difference document resolved over
# `DEFAULT_MATERIAL_PROFILE` rather than over the light patch — `tuned-profiles.test.ts` resolves
# both as `withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, doc.patch)`. A constant the dark patch
# does not name therefore comes from the CODE default, which for this wave's constants is 0. So
# every dark cell in `probe-read.txt` was rendered with the mechanism OFF: that table's dark columns
# are the inert material re-rendered, not the candidate.
#
# It matters beyond the table. A landed constant reaches the dark scheme because LANDING edits
# `DEFAULT_MATERIAL_PROFILE` — which is exactly what "the dark document's resolved material moves
# with it" means in W15's and W25's own entries — so G2's declaration WILL reach the dark bed, and
# the dark bed has to be measured before it does. This run measures it.
#
# `both:` writes each constant into both documents, which reproduces at capture time what a landing
# reproduces at declaration time. Dark profiles only: the light half is already `pc`.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
G0="$HERE/../g0"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1
NAME=${1:-pcd}
shift || true
$PY "$G0/g0-candidate.py" "$T/$NAME/doc" \
  both:sizeHeavyTapSigma=13.418 both:sizeHeavyTapSigma2x=10.3 \
  both:sizeScatterHeavyShareThick1x=0.25 "$@" > /dev/null

cd "$HERE/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
D=$T/$NAME
export VITREA_WEB_CAPTURES="$D/web-captures"
rm -f "$D/DONE" "$D/rung.json"
cd packages/calibration
for profile in apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard; do
  echo "=== $(date +%H:%M:%S) $profile ==="
  npx tsx cli/compare.ts --profile "$profile" \
    --material-profile "$D/doc/apple-macos-26.5-1x-dark-standard.json" \
    --renderer webgpu --set probe --alpha --write-partial \
    --out-matrix "$D/rung.json" >> "$D/runs.log" 2>&1
  echo "    exit=$?"
done
touch "$D/DONE"
