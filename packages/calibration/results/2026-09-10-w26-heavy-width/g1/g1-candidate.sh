#!/bin/bash
# W26 G1 — the recommended candidate, captured over everything the recommendation has to answer for.
#
# The candidate (see `g1-findings.md` for each constant's fit, condition and decline):
#   sizeHeavyTapSigma            13.418   the width the chain already draws at dpr 1, NAMED
#   sizeHeavyTapSigma2x          10.3     fitted on the one conditioned 2x reference row
#   sizeScatterHeavyShareThick1x 0.25     fitted on the three 1x impulse rows' share
#   sizeScatterFloor2x           1        UNCHANGED — declined on X5 and on a flat objective
#
# Three runs, in this order:
#   t103  the ladder rows at sigma2x 10.3 alone, so the width's own fit has its own rung;
#   pc    the whole probe set at the candidate, for the level above the knee, the mid-span rows
#         and X5's full sweep against `p0`;
#   bedc  the frozen bed (calibration + validation) at the candidate on both tiers and all six
#         profiles, which is what `adopted-thresholds.test.ts` needs to re-read the fourteen thick
#         floors through `VITREA_MATRIX_PATH`.
#
# One capture process at a time (X4); scratch only (X2).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
G0="$HERE/../g0"
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1
CAND="light:sizeHeavyTapSigma=13.418 light:sizeHeavyTapSigma2x=10.3 \
light:sizeScatterHeavyShareThick1x=0.25"

$PY "$G0/g0-candidate.py" "$T/t103/doc" light:sizeHeavyTapSigma=10.3 \
  light:sizeHeavyTapSigma2x=10.3 > /dev/null
"$HERE/g1-rung.sh" t103 "$T/t103/doc/apple-macos-26.5-1x-light-standard.json" \
  "$T/t103/doc/apple-macos-26.5-1x-dark-standard.json" ladder both

$PY "$G0/g0-candidate.py" "$T/pc/doc" $CAND > /dev/null
"$HERE/g1-rung.sh" pc "$T/pc/doc/apple-macos-26.5-1x-light-standard.json" \
  "$T/pc/doc/apple-macos-26.5-1x-dark-standard.json" probe both

# The bed, both tiers, all six profiles — the floors' own rows.
cd "$HERE/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
BED=$T/bedc
mkdir -p "$BED"
export VITREA_WEB_CAPTURES="$BED/web-captures"
rm -f "$BED/bed.json" "$BED/DONE"
cd packages/calibration
for profile in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
               apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard \
               apple-macos-26.5-1x-light-reduced-transparency \
               apple-macos-26.5-1x-light-increased-contrast; do
  case "$profile" in
    *dark*) DOC=$T/pc/doc/apple-macos-26.5-1x-dark-standard.json ;;
    *)      DOC=$T/pc/doc/apple-macos-26.5-1x-light-standard.json ;;
  esac
  for renderer in webgpu css; do
    echo "=== $(date +%H:%M:%S) $profile $renderer ==="
    npx tsx cli/compare.ts --profile "$profile" --material-profile "$DOC" \
      --renderer "$renderer" --set calibration,validation --alpha --write-partial \
      --out-matrix "$BED/bed.json" >> "$BED/runs.log" 2>&1
    echo "    exit=$?"
  done
done
touch "$BED/DONE"
touch "$T/CANDIDATE-DONE"
