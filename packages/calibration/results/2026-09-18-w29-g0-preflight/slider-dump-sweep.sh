#!/bin/bash
# Does `NSGlassTintAmount` reach a `.glassEffect()` surface? The cheap arm.
#
#   slider-dump-sweep.sh <bundle.app> <out-root> <value> [<value> ...]
#
# `dump-layers` reads the material's DECLARED parameters and captures nothing, so
# one arm costs a settle rather than a capture and needs no grant. It answers a
# narrower question than the pixels do — whether the key reaches the filter the
# window server composites from — and it answers it per value, which is what makes
# "the centre maps to X" a reading rather than an assertion.
#
# Every arm relaunches the harness. `defaults` writes through cfprefsd and a
# running application has already read its preferences, so a sweep that reused one
# process would measure the first value it happened to launch under.
#
# The caller restores the key. This script does not, on purpose: a script that
# tidies up after itself would also tidy up after a crash that left the machine on
# a value nobody recorded.
set -euo pipefail

APP="${1:?usage: slider-dump-sweep.sh <bundle.app> <out-root> <value> ...}"
OUT="${2:?usage: slider-dump-sweep.sh <bundle.app> <out-root> <value> ...}"
shift 2

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
SPEC="$REPO/apps/reference-apple/scenes.json"
SCENES=photo__rrect-md__rest
SETTLE="${VITREA_SETTLE:-8}"

mkdir -p "$OUT"
for V in "$@"; do
  if [ "$V" = "DELETED" ]; then
    defaults delete -g NSGlassTintAmount 2>/dev/null || true
  else
    defaults write -g NSGlassTintAmount -float "$V"
  fi
  READ=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo "<absent>")
  echo "arm $V: key reads back $READ"
  open -W --env VITREA_SCENES="$SPEC" \
    --stdout "$OUT/$V.out" --stderr "$OUT/$V.err" "$APP" \
    --args dump-layers --scenes "$SCENES" --scheme light --settle "$SETTLE" \
    --require-key --out "$OUT/$V"
  grep -E "inputBlurFill|inputFaceColorMatrixFillColor|inputFaceOpacity" "$OUT/$V.out" | sed 's/^/    /'
done
