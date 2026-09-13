#!/bin/bash
# W27c G1c: the frozen re-read (claims §5.141).
#
# Runs AFTER `declare.ts` freezes the fitted endpoint. Three passes and nothing
# canonical written:
#
#   1. the whole checking set on the WebGPU tier — the bound's own population,
#      which also carries this child's four holdout cells, so the holdout is read
#      exactly once and on the frozen document;
#   2. the same population on the CSS tier, for the record only. X1: the CSS tier
#      derives and never gates, and its rows are not scored by anything;
#   3. the bound of claims §5.134 §6, clause by clause, per profile.
#
# The driver refuses the run if either of the machine's own accessibility
# settings is on and records both readings in each matrix.
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT="${OUT:-/tmp/w27c-g1c-frozen}"
RUN=(npx tsx results/2026-09-13-w27c-g1c-fit/g1c-run.ts --out "$OUT")

"${RUN[@]}" --label checking --renderer webgpu
"${RUN[@]}" --label checking-css --renderer css
python3 results/2026-09-13-w27c-g1c-fit/score-bound.py "$OUT/checking.json"
python3 results/2026-09-13-w27c-g1c-fit/sheet.py "$OUT/checking.json"
