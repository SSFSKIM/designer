#!/usr/bin/env bash
#
# W31 G3 — one fit round: four candidate documents, four profiles, one table.
#
#   ./round.sh <label> <r-light-active> <r-light-receded> <r-dark-active> <r-dark-receded>
#
# `results/2026-09-20-w30-g3-operators/round.py`'s job in this wave's shape. Each
# round writes CANDIDATE documents into the scratch tree — never beside the
# committed ones — renders the four macOS 27 standard profiles on the WebGPU
# tier over the declared bed, and leaves the matrices for `chroma-fit.py read`.
#
# **The bed is `calibration,validation` and the scenes are named** (X4): the
# holdout is read once, at the canonical read, and `chroma-fit.py`'s own
# `cells()` drops a holdout row even if one arrived.
#
# The receded documents are passed with `--receded-profile`, so the inactive
# pose draws a CANDIDATE recede composed over the CANDIDATE active document —
# which is the material a root hands the renderer when the window loses focus,
# and what `fit.py render` could not express.
set -euo pipefail
cd "$(dirname "$0")/../.."

HERE=results/2026-09-21-w31-g3-chroma-fit
LABEL="${1:?usage: round.sh <label> <rLA> <rLR> <rDA> <rDR>}"
RLA="${2:?}"; RLR="${3:?}"; RDA="${4:?}"; RDR="${5:?}"
SCRATCH="${VITREA_G3_SCRATCH:-/tmp/w31-g3-fit}"
DOCS="$SCRATCH/$LABEL/documents"
mkdir -p "$DOCS"

"$HERE/x6-read.sh" "w31-g3-round-$LABEL" | tee -a "$HERE/browser-runs.txt"

make() {  # <out> <base> <retention>
  printf '{"patch":{"bodyChromaRetention":%s}}\n' "$3" > "$DOCS/$(basename "$1").over.json"
  python3 "$HERE/chroma-fit.py" doc "$1" "$2" "$DOCS/$(basename "$1").over.json" > /dev/null
}
L="$DOCS/light.json";  make "$L"  profiles/apple-macos-27.0-1x-light-standard-glass0.5.json "$RLA"
D="$DOCS/dark.json";   make "$D"  profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json  "$RDA"
LR="$DOCS/light-receded.json"
make "$LR" profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json "$RLR"
DR="$DOCS/dark-receded.json"
make "$DR" profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json "$RDR"

for profile in apple-macos-27.0-1x-light-standard-glass0.5 \
               apple-macos-27.0-2x-light-standard-glass0.5 \
               apple-macos-27.0-1x-dark-standard-glass0.5 \
               apple-macos-27.0-2x-dark-standard-glass0.5; do
  case "$profile" in
    *-dark-*) doc="$D"; receded="$DR" ;;
    *)        doc="$L"; receded="$LR" ;;
  esac
  echo "── $LABEL / $profile ──"
  python3 "$HERE/chroma-fit.py" render "$LABEL" "$profile" "$doc" "$receded" \
    --set calibration,validation \
    --scene "$(python3 -c 'import sys; sys.path.insert(0,"'"$HERE"'"); import importlib.util as u; s=u.spec_from_file_location("cf","'"$HERE"'/chroma-fit.py"); m=u.module_from_spec(s); s.loader.exec_module(m); print(m.BED_SCENES + "," + m.ANCHOR_SCENES)')"
done

echo "── closing machine read ──"
"$HERE/x6-read.sh" "w31-g3-round-$LABEL-close" | tee -a "$HERE/browser-runs.txt"
