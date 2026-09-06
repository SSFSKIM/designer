#!/bin/bash
# W21 G0 — every reading in this gate, in one place, so the findings are reproducible from the
# committed bed and the scratch captures by running one script.
#
# The order matters only in that the tables are written from the reads. Nothing here captures
# anything and nothing here touches a canonical path: the native side is `probe/`, the web side is
# whatever `run-web.sh` left in scratch, and every output lands beside this script.
#
# Usage: `bash run-read.sh <runRoot> <webRoot>` — `runRoot` holds the attested `run-N` directories
# (for the noise floor), `webRoot` the `web0` / `web1` / `candidate` capture trees. Either may be
# absent; the reads that need it are skipped.
set -u
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes-w21-probe.json"
PROBE="$HERE/../probe"
RUNS="${1:-}"
WEB="${2:-}"

RUN_ARGS=()
if [ -n "$RUNS" ]; then
  for D in "$RUNS"/run-*/; do
    [ -f "$D/manifest.json" ] && RUN_ARGS+=("${D%/}")
  done
fi

# The native probe, read under the declared geometry. The probe's holdout column is left out of
# every reading at G0 (W21: the wave's one holdout read is the canonical bed's, at G1).
"$PY" "$HERE/read.py" --scenes "$SCENES" --fixtures "$PROBE" \
  ${RUN_ARGS[@]+--runs "${RUN_ARGS[@]}"} \
  --json "$HERE/probe-read.json" > "$HERE/probe-read.txt"

WEB_ARGS=()
for LABEL in web0 web1 candidate; do
  CAP="$WEB/$LABEL/web-captures"
  [ -n "$WEB" ] && [ -d "$CAP" ] || continue
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
