#!/bin/bash
# W26 G2c — one diagnostic rung: a patched material rendered over the eye's rows, to SCRATCH.
#
# These are DIAGNOSTICS and not fits. Each rung changes ONE thing against the candidate so that the
# edge→centre gradient the user's eye found can be attributed rather than guessed at, and no rung
# but the candidate is a material anybody proposes to land.
#
# THE ROWS ARE PROBE ROWS ONLY, and that is deliberate: `checkerboard-64__rrect-lg` and `-md` carry
# the effect and are not in the holdout, so the mechanism can be identified without opening
# `checkerboard__glass-over-glass` again. X3's one read of the holdout stays the dry run's; the
# nested pane is read in this child from captures that already exist (the native fixture, the
# canonical 0.14.0 bed and W26 G2's own dry run) and from no new render.
#
#   g2c-rung.sh <rung> <light-doc.json> <dark-doc.json> [profiles...]
#
# One capture process at a time (X4); `g2-guard.sh` refuses to start beside another. Everything to
# scratch through `--out-matrix` and `VITREA_WEB_CAPTURES` (X2): the canonical `results/matrix.json`,
# `web-captures/`, `apps/reference-apple/fixtures/` and `scenes.json` are never written.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/g2-guard.sh" || exit 1
cd "$HERE/../../../../.."
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
RUNG=${1:?rung}
LIGHT=${2:?light document}
DARK=${3:?dark document}
shift 3
PROFILES=${*:-"apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard apple-macos-26.5-1x-light-standard"}
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2c/$RUNG
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/rung.json"
rm -f "$T/DONE" "$MATRIX"
LOG="$T/runs.log"
: > "$LOG"
SCENES=checkerboard-64__rrect-lg__rest,checkerboard-64__rrect-md__rest
cd packages/calibration
echo "=== $(date +%H:%M:%S) rung=$RUNG ==="
echo "=== light $(shasum -a 256 "$LIGHT" | cut -c1-12)  dark $(shasum -a 256 "$DARK" | cut -c1-12) ==="
for P in $PROFILES; do
  case "$P" in *dark*) DOC="$DARK" ;; *) DOC="$LIGHT" ;; esac
  echo "=== $(date +%H:%M:%S) $P ==="
  npx tsx cli/compare.ts --profile "$P" --material-profile "$DOC" --renderer webgpu \
    --set probe --scene "$SCENES" --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1
  echo "    exit=$?"
done
echo "RUNG $RUNG DONE $(date +%H:%M:%S)"
touch "$T/DONE"
