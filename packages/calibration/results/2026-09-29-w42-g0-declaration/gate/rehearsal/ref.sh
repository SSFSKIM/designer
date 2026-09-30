#!/bin/bash
# usage: ref.sh LIGHT_STAGE DARK_STAGE LIGHT_VARIANT DARK_VARIANT TREES(colon-separated) OUT
set -e
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
LS=$1; DS=$2; LV=$3; DV=$4; TREES=$5; OUT=$6
R=packages/calibration/results/2026-09-29-w42-g0-declaration/gate/rehearsal/documents
SRC=(--stage "$LS" --stage "$DS"
  --candidate $R/$LV/apple-macos-27.0-1x-light-standard-glass0.5.json
  --candidate $R/$LV/apple-macos-27.0-1x-light-standard-glass0.5-receded.json
  --candidate $R/$DV/apple-macos-27.0-1x-dark-standard-glass0.5.json
  --candidate $R/$DV/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json)
CAP=()
IFS=':' read -ra TS <<< "$TREES"
for t in "${TS[@]}"; do CAP+=(--captures "$t"); done
CAP+=(--captures /Users/new/Developer/GitHub/designer/packages/calibration/web-captures)
# The referees beside this script, in whatever checkout holds it (the candidate paths above are
# repo-relative, and the referees resolve them against their own checkout's root).
cd "$(dirname "${BASH_SOURCE[0]}")/../referees"
mkdir -p "$OUT"; rm -f "$OUT"/l1-cut.json "$OUT"/chroma-cut.json "$OUT"/black-cut.json "$OUT"/e2-regression*.json* "$OUT"/exterior-cut.json "$OUT"/m2-rebaseline.json
python3.12 -B l1-cut.py "${SRC[@]}" --out "$OUT/l1-cut.json" > "$OUT/l1-cut.txt" 2>&1
python3.12 -B chroma-cut.py "${SRC[@]}" --out "$OUT/chroma-cut.json" > "$OUT/chroma-cut.txt" 2>&1
python3.12 -B m2-rebaseline.py --cut "$OUT/chroma-cut.json" --out "$OUT/m2-rebaseline.json" > "$OUT/m2-rebaseline.txt" 2>&1 || true
python3.12 -B exterior-cut.py "${SRC[@]}" --out "$OUT" > "$OUT/exterior-cut.txt" 2>"$OUT/exterior-cut.err"
python3.12 -B black-cut.py "${SRC[@]}" "${CAP[@]}" --out "$OUT/black-cut.json" > "$OUT/black-cut.txt" 2>&1 || echo "black-cut exit $?" >> "$OUT/black-cut.txt"
python3.12 -B e2-regression.py "${SRC[@]}" "${CAP[@]}" --out "$OUT/e2-regression.json" --bins "$OUT/e2-regression-bins.json.gz" > "$OUT/e2-regression.txt" 2>&1 || echo "e2 exit $?" >> "$OUT/e2-regression.txt"
echo done
