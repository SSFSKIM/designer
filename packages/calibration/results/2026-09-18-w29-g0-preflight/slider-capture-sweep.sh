#!/bin/bash
# The pixel arm of G0 (d): does moving `NSGlassTintAmount` move the harness's cells?
#
#   slider-capture-sweep.sh <arm> <scale> <pose> <ids> <out-root> <value>[:<runs>] ...
#
# One arm is one scale and one pose; one run is one snapshot at one slider value,
# into its own fixture root with its own manifest — the same shape `run-sitting.sh`
# gives a pass, for the same reason: `materialize` and every reader downstream
# expect one whole snapshot per run with nothing decided yet.
#
# `<value>:<runs>` repeats a value. The centre is repeated so the arm carries its
# own run-to-run spread, which is what turns "these bytes differ" into "these bytes
# differ by more than this cell differs from itself" — the construction the charter
# asks of clause 3's noise bar, taken here at the probe's own small scale.
#
# Raw captures land under `$HOME`, never under `fixtures/`. The value is written
# before the launch and read back into the run directory, because a run whose
# slider position is inferred from the command that launched it attests nothing
# (X2: a value that cannot be read by something that can refuse is not an
# attestation, and this script's read is the weaker stand-in until the harness
# itself carries the field).
set -euo pipefail

ARM="${1:?usage: slider-capture-sweep.sh <arm> <scale> <pose> <ids> <out-root> <value>[:<runs>] ...}"
SCALE="${2:?}"; POSE="${3:?}"; IDS="${4:?}"; OUT="${5:?}"
shift 5

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
SPEC="$REPO/apps/reference-apple/scenes.json"
APP="${VITREA_APP:-/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app}"
HARNESS="$APP/Contents/MacOS/VitreaReference"

case "$OUT" in "$REPO"/*) echo "REFUSED: $OUT is inside the repository." >&2; exit 1;; esac
case "$POSE" in active|inactive) ;; *) echo "REFUSED: pose is active or inactive" >&2; exit 64;; esac

if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference|playwright' >/dev/null; then
  echo "REFUSED: a capture process is already running (the GPU is shared; one at a time)." >&2
  exit 7
fi

POSE_ARG=""
[ "$POSE" = "inactive" ] && POSE_ARG="--inactive"

mkdir -p "$OUT"
for SPEC_ARG in "$@"; do
  V="${SPEC_ARG%%:*}"
  N="${SPEC_ARG#*:}"; [ "$N" = "$SPEC_ARG" ] && N=1
  for R in $(seq 1 "$N"); do
    D="$OUT/$ARM/$V-r$R"
    if [ -e "$D/manifest.json" ]; then echo "$ARM $V r$R: already banked"; continue; fi
    rm -rf "$D"; mkdir -p "$D"

    if [ "$V" = "DELETED" ]; then
      defaults delete -g NSGlassTintAmount 2>/dev/null || true
    else
      defaults write -g NSGlassTintAmount -float "$V"
    fi
    defaults read -g NSGlassTintAmount > "$D/slider.read" 2>/dev/null || echo "<absent>" > "$D/slider.read"
    # Both accessibility reads, per run, as X7 requires of every capture.
    {
      echo "reduceTransparency=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)"
      echo "increaseContrast=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)"
    } > "$D/a11y.read"

    VITREA_SCALE="$SCALE" VITREA_FIXTURES="$D" VITREA_SCENES="$SPEC" \
      "$HARNESS" backgrounds > "$D.backgrounds.out" 2>&1 \
      || { echo "$ARM $V r$R: backgrounds FAILED"; tail -5 "$D.backgrounds.out"; exit 2; }

    START=$(date -u +%s)
    open -W --env VITREA_SCALE="$SCALE" --env VITREA_FIXTURES="$D" --env VITREA_SCENES="$SPEC" \
      --stdout "$D.out" --stderr "$D.err" "$APP" \
      --args capture ${POSE_ARG} --run-label "w29-g0-d-$ARM-$V-r$R" \
      --reset-interstitial 6 --scenes "$IDS"
    END=$(date -u +%s)
    if [ ! -f "$D/manifest.json" ]; then
      echo "$ARM $V r$R: FAILED"; tail -12 "$D.err" "$D.out"; exit 3
    fi
    CELLS=$(grep -c "byte-stable\|repeat " "$D.out" || true)
    echo "$ARM $V r$R: $((END-START))s  slider=$(cat "$D/slider.read")  cells~$CELLS"
    echo "$((END-START))" > "$D/seconds"
  done
done
echo "ARM $ARM DONE $(date -u +%H:%M:%SZ)"
