#!/bin/bash
# W21 G0 — every reading in this gate, in one place, so the findings are reproducible from the
# committed bed and the scratch captures by running one script.
#
# The order matters only in that the tables are written from the reads. Nothing here captures
# anything and nothing here touches a canonical path: the native side is `probe/`, the web side is
# whatever `run-web.sh` left in scratch, and every output lands beside this script.
#
# The attested runs are named on the command line rather than globbed. A disqualified run is
# disqualified whole — W9's rule and W20's — so its cells must not reach the run-to-run sigma even
# when the run happened to attest some of them; naming the kept runs is what makes that true by
# construction instead of by a filter that could be relaxed later.
#
# The probe's holdout column is left out of every reading (`read.py --sets` defaults to
# calibration, validation and recorded): the wave's one holdout read is the canonical bed's, at G1.
#
# Usage: `bash run-read.sh <webRoot|-> <keptRunDir>...`
set -u
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes-w21-probe.json"
PROBE="$HERE/../probe"
WEB="${1:--}"
shift || true

"$PY" "$HERE/read.py" --scenes "$SCENES" --fixtures "$PROBE" ${*:+--runs "$@"} \
  --json "$HERE/probe-read.json" > "$HERE/probe-read.txt"

WEB_ARGS=()
for LABEL in web0 web1 candidate candidate-footprint; do
  CAP="$WEB/$LABEL/web-captures"
  [ "$WEB" != "-" ] && [ -d "$CAP" ] || continue
  "$PY" "$HERE/read.py" --scenes "$SCENES" --fixtures "$PROBE" --captures "$CAP" --tier webgpu \
    --json "$HERE/probe-read-$LABEL.json" > "$HERE/probe-read-$LABEL.txt"
  WEB_ARGS+=(--web "$LABEL=$HERE/probe-read-$LABEL.json")
done

"$PY" "$HERE/tables.py" --native "$HERE/probe-read.json" ${WEB_ARGS[@]+"${WEB_ARGS[@]}"} --out "$HERE"

if [ -f "$HERE/probe-read-web0.json" ] && [ -f "$HERE/probe-read-web1.json" ]; then
  "$PY" "$HERE/endpoints.py" --native "$HERE/probe-read.json" \
    --web0 "$HERE/probe-read-web0.json" --web1 "$HERE/probe-read-web1.json" \
    --out "$HERE/endpoints.txt"
fi
echo "READS DONE $(date -u +%H:%M:%SZ)"
