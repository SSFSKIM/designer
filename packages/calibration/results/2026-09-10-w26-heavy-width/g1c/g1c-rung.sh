#!/bin/bash
# W26 G1c — one rung: a candidate material rendered over this child's rows, GPU tier, to SCRATCH.
#
# G1's `g1-rung.sh` with two changes, both of them rulings rather than taste.
#
#   * **BOTH documents are patched, always.** W26 Decision Log 4 (c): the dark profile is a
#     difference document resolved over `DEFAULT_MATERIAL_PROFILE`, not over the light patch, so a
#     rung that writes the light document alone renders the dark scheme at the CODE defaults — which
#     for this wave's constants is inert. A landing edits the default and therefore reaches the dark
#     bed, so a rung that does not is not a rehearsal of one. `g1c-ladder.sh` passes `both:`.
#
#   * **The reader's row set is HOLDOUT-FREE.** Three of the eight backdrops G1b read on each
#     surface are holdout scenes — `checkerboard__rrect-lg`, `hc-text__rrect-md`,
#     `photo__rrect-lg` — and G1b was a spike that fitted nothing. G1c FITS two constants, so
#     `reader` names only calibration, validation and probe rows and the holdout is left for the
#     declaring child's one dry run (X3).
#
#   g1c-rung.sh <rung> <light-doc.json> <dark-doc.json> [reader|probe|bed] [1x|2x|both]
#
# One capture process at a time (X4), and `g1c-guard.sh` refuses to start while another is running
# or while :5189 is held. Everything under `--out-matrix` and `VITREA_WEB_CAPTURES` in scratch (X2):
# the canonical matrix, `web-captures/`, `fixtures/` and `scenes.json` are never written. A DONE
# marker is written last so a waiter has one file to watch.
#
# WHERE THE CAPTURE RUNS, and why it is not this worktree. A worktree carries no `node_modules`,
# and installing a second copy of the workspace to render from would be a second toolchain rather
# than the same one. The run is therefore taken in the shared checkout — and `g1c-same.sh` proves
# before every rung that every source the capture depends on (the renderer, the pyramid, the passes,
# the optics shader, the harness's `compare.ts`, the two committed profile documents and
# `scenes.json`) is byte-identical between the two, so it is a run of THIS branch's code. Nothing is
# written there: the documents are read from scratch and both outputs are redirected to scratch.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HERE/g1c-same.sh" || { echo "sources differ from the checkout — refusing" >&2; exit 1; }
"$HERE/g1c-guard.sh" || exit 1
cd /Users/new/Developer/GitHub/designer
unset VITREA_SCENES VITREA_FIXTURES VITREA_MATRIX_PATH
RUNG=${1:?rung}
LIGHT=${2:?light document}
DARK=${3:?dark document}
ROWS=${4:-reader}
SCALES=${5:-both}
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c/$RUNG
mkdir -p "$T"
export VITREA_WEB_CAPTURES="$T/web-captures"
MATRIX="$T/rung.json"
rm -f "$T/DONE" "$MATRIX"
LOG="$T/runs.log"
: > "$LOG"

# The family reader's rows: `impulse`, the four checkerboard pitches, `hc-text` and `photo` over
# `rrect-md` and `rrect-lg`, minus every holdout scene. Seven rows on `-md`, six on `-lg`; the dark
# fixtures carry a subset and the run drops what has no fixture.
READER_SCENES=\
impulse__rrect-md__rest,impulse__rrect-lg__rest,\
checkerboard-64__rrect-md__rest,checkerboard-64__rrect-lg__rest,\
checkerboard-32__rrect-md__rest,checkerboard-32__rrect-lg__rest,\
checkerboard__rrect-md__rest,\
checkerboard-8__rrect-md__rest,checkerboard-8__rrect-lg__rest,\
checkerboard-4__rrect-md__rest,checkerboard-4__rrect-lg__rest,\
hc-text__rrect-lg__rest,photo__rrect-md__rest

cd packages/calibration
echo "=== $(date +%H:%M:%S) rung=$RUNG rows=$ROWS scales=$SCALES ==="
echo "=== light $(shasum -a 256 "$LIGHT" | cut -c1-12)  dark $(shasum -a 256 "$DARK" | cut -c1-12) ==="
run() {
  echo "=== $(date +%H:%M:%S) $1 ==="
  case "$ROWS" in
    probe)
      npx tsx cli/compare.ts --profile "$1" --material-profile "$2" --renderer webgpu \
        --set probe --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1 ;;
    bed)
      # BOTH tiers. `adopted-thresholds.test.ts` asserts over the whole frozen bed and counts its
      # partitions, and the bed carries a `texture` row and a `css` row for every cell; a matrix
      # holding only the WebGPU half fails the gate on absence rather than on any measurement.
      for renderer in webgpu css; do
        npx tsx cli/compare.ts --profile "$1" --material-profile "$2" --renderer "$renderer" \
          --set calibration,validation --alpha --write-partial --out-matrix "$MATRIX" \
          >> "$LOG" 2>&1
      done ;;
    *)
      npx tsx cli/compare.ts --profile "$1" --material-profile "$2" --renderer webgpu \
        --set probe,validation,calibration --scene "$READER_SCENES" \
        --alpha --write-partial --out-matrix "$MATRIX" >> "$LOG" 2>&1 ;;
  esac
  echo "    exit=$?"
}
case "$SCALES" in
  1x|both) run apple-macos-26.5-1x-light-standard "$LIGHT" ;;
esac
case "$SCALES" in
  2x|both) run apple-macos-26.5-2x-light-standard "$LIGHT" ;;
esac
case "$SCALES" in
  1x|both) run apple-macos-26.5-1x-dark-standard "$DARK" ;;
esac
case "$SCALES" in
  2x|both) run apple-macos-26.5-2x-dark-standard "$DARK" ;;
esac
if [ "$ROWS" = "bed" ]; then
  run apple-macos-26.5-1x-light-reduced-transparency "$LIGHT"
  run apple-macos-26.5-1x-light-increased-contrast "$LIGHT"
fi
echo "RUNG $RUNG DONE $(date +%H:%M:%S)"
touch "$T/DONE"
