#!/usr/bin/env bash
#
# W32 G1 — render the fit's bed once, at a named set of four documents.
#
#   ./render-bed.sh <label> <light> <light-receded> <dark> <dark-receded>
#
# W31 G3's `round.sh` and `scratch-capture.sh` fused into the one thing both of
# them are: a scratch render of a declared bed at four declared documents,
# writing into a scratch capture tree and a scratch matrix and touching neither
# canonical output. The pre-fit bed calls it at the SHIPPED documents and every
# round calls it at that round's candidates (`round.sh`).
#
# **The bed** (charter, "The fit's bed, counted"): the six macOS 27 profiles on
# the WebGPU tier over `calibration,validation`, plus the pitch ladder as probe
# rows on the four standard profiles — 45 scenes as W31 G3's `canonical-read.sh`
# named them, **widened by the ten Decision Log 1 (b) names** (nine of which
# carry a shadow; `impulse__rrect-ml__inactive` has none and is read anyway so
# its absence is a reading rather than a gap). 346 committed rows before the
# widening, counted from `results/matrix.json` at the shipped documents.
#
# The receded documents are passed with `--receded-profile`, so every `inactive`
# cell draws the round's own recede composed over the round's own active
# document — which is the material a root hands the renderer when the window
# loses focus, and the only way the recede's stand-down (Decision Log 2) can be
# read at all.
#
# **X6, in the two parts W31 G3's review closure left them in.** Another
# CALIBRATION capture is a refusal; any other browser automation is counted,
# named in `browser-runs.txt` and left for the reproduction check to referee.
# The machine is read before the run and after it.
set -euo pipefail
cd "$(dirname "$0")/../.."

HERE=results/2026-09-21-w32-g1-shadow-fit
LABEL="${1:?usage: render-bed.sh <label> <light> <light-receded> <dark> <dark-receded>}"
LIGHT="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
LIGHT_RECEDED="$(cd "$(dirname "$3")" && pwd)/$(basename "$3")"
DARK="$(cd "$(dirname "$4")" && pwd)/$(basename "$4")"
DARK_RECEDED="$(cd "$(dirname "$5")" && pwd)/$(basename "$5")"

SCRATCH="${VITREA_G1_SCRATCH:-/tmp/w32-g1-fit}"
CAPTURES="$SCRATCH/$LABEL/captures"
MATRIX="$SCRATCH/$LABEL/matrix.json"
mkdir -p "$CAPTURES"

if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference' > /dev/null; then
  echo "render-bed: another calibration capture is running (X6)" >&2
  exit 1
fi
FOREIGN=$( { pgrep -f 'playwright' || true; } | wc -l | tr -d ' ')
echo "foreign browser automation processes at start: $FOREIGN" | tee -a "$HERE/browser-runs.txt"
"$HERE/x6-read.sh" "w32-g1-$LABEL" | tee -a "$HERE/browser-runs.txt"

PROFILES=(
  apple-macos-27.0-1x-light-standard-glass0.5
  apple-macos-27.0-2x-light-standard-glass0.5
  apple-macos-27.0-1x-dark-standard-glass0.5
  apple-macos-27.0-2x-dark-standard-glass0.5
  apple-macos-27.0-1x-light-reduced-transparency-glass0.5
  apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5
)

# shellcheck source=ladder.sh
. "$HERE/ladder.sh"

run() {
  local profile="$1" doc="$2" receded="$3"
  shift 3
  echo "── $LABEL / $profile / webgpu / $* ──"
  VITREA_WEB_CAPTURES="$CAPTURES" npx tsx cli/compare.ts \
    --profile "$profile" \
    --material-profile "$doc" \
    --receded-profile "$receded" \
    --renderer webgpu \
    --alpha \
    --write-partial \
    --out-matrix "$MATRIX" \
    "$@"
}

for profile in "${PROFILES[@]}"; do
  case "$profile" in
    *-dark-*) doc="$DARK"; receded="$DARK_RECEDED" ;;
    *)        doc="$LIGHT"; receded="$LIGHT_RECEDED" ;;
  esac
  run "$profile" "$doc" "$receded" --set calibration,validation
done
for profile in "${PROFILES[@]:0:4}"; do
  case "$profile" in
    *-dark-*) doc="$DARK"; receded="$DARK_RECEDED" ;;
    *)        doc="$LIGHT"; receded="$LIGHT_RECEDED" ;;
  esac
  run "$profile" "$doc" "$receded" --set probe --scene "$LADDER"
done

echo "── closing machine read ──"
"$HERE/x6-read.sh" "w32-g1-$LABEL-close" | tee -a "$HERE/browser-runs.txt"
echo "matrix: $MATRIX"
