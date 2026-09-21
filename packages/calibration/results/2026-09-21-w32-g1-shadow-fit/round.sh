#!/usr/bin/env bash
#
# W32 G1 — one fit round: four candidate documents, six profiles, one table.
#
#   ./round.sh <label> <constants.json> [<previous-label>]
#
# W31 G3's `round.sh` in shape, with the two differences this wave's subject
# forces. The candidate is a TRIPLE per scheme — the two lengths and the σ law —
# rather than one retention, so it arrives as a constants file built by
# `build-shadow.py`'s idiom rather than as four numbers on the command line; and
# the bed is the whole fit bed (`render-bed.sh`) rather than
# `calibration,validation`, because the thin spans and the ladder's rungs are in
# the fit now.
#
# Each round writes CANDIDATE documents into the scratch tree — never beside the
# committed ones — renders the six macOS 27 profiles on the WebGPU tier, cuts the
# round's own matrix with G0's reader, and prints every stop plus the objective
# and both anchor solves. A round that breaks a stop is recorded and not shipped.
#
# `--at-documents any` on the cut is not a relaxation: a candidate document by
# construction has a content hash no file under `profiles/` carries, so the
# shipped-hash partition would drop every row of the round. The documents the
# rows actually name are printed in the cut's §0 either way.
set -euo pipefail
cd "$(dirname "$0")/../.."

HERE=results/2026-09-21-w32-g1-shadow-fit
LABEL="${1:?usage: round.sh <label> <constants.json> [<previous-label>]}"
CONSTANTS="${2:?}"
PREVIOUS="${3:-}"
SCRATCH="${VITREA_G1_SCRATCH:-/tmp/w32-g1-fit}"
DOCS="$SCRATCH/$LABEL/documents"
ROUND="$HERE/rounds/$LABEL"
mkdir -p "$DOCS" "$ROUND"

cp "$CONSTANTS" "$ROUND/constants.json"
python3 "$HERE/build-shadow.py" "$ROUND/constants.json" "$DOCS" | tee "$ROUND/documents.txt"

VITREA_G1_SCRATCH="$SCRATCH" "$HERE/render-bed.sh" "$LABEL" \
  "$DOCS/apple-macos-27.0-1x-light-standard-glass0.5.json" \
  "$DOCS/apple-macos-27.0-1x-light-standard-glass0.5-receded.json" \
  "$DOCS/apple-macos-27.0-1x-dark-standard-glass0.5.json" \
  "$DOCS/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json"

MATRIX="$SCRATCH/$LABEL/matrix.json"
python3 "$HERE/exterior-cut.py" --matrix "$MATRIX" --at-documents any --out "$ROUND" \
  > "$ROUND/exterior-cut.txt"
# `departure-stat.py` writes its JSON beside itself, which for a round is this
# gate's own directory; it is moved into the round's so the ten rounds do not
# each overwrite the last one's evidence.
python3 "$HERE/departure-stat.py" "$MATRIX" --any-document > "$ROUND/departure-stat.txt"
mv "$HERE/departure-stat.json" "$ROUND/departure-stat.json"

VITREA_W32_G1_CUT="$ROUND/exterior-cut.json" \
  python3 "$HERE/c1-forms.py" > "$ROUND/c1-forms.txt"
VITREA_W32_G1_CUT="$ROUND/exterior-cut.json" \
VITREA_W32_G1_CUT_HOLDOUT="$ROUND/exterior-cut.json" \
VITREA_W32_G1_MATRIX="$MATRIX" \
VITREA_W32_G1_DEPARTURE="$ROUND/departure-stat.json" \
  python3 "$HERE/stops.py" > "$ROUND/stops.txt"

if [ -n "$PREVIOUS" ]; then
  python3 "$HERE/anchor-solve.py" "$ROUND/exterior-cut.json" \
    --constants "$ROUND/constants.json" \
    --against "$HERE/rounds/$PREVIOUS/exterior-cut.json" --label "$LABEL" \
    > "$ROUND/anchor-solve.txt"
else
  python3 "$HERE/anchor-solve.py" "$ROUND/exterior-cut.json" \
    --constants "$ROUND/constants.json" --label "$LABEL" > "$ROUND/anchor-solve.txt"
fi

echo "round $LABEL: $ROUND"
sed -n '1,40p' "$ROUND/anchor-solve.txt"
