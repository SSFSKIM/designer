#!/bin/bash
# W20 G0 — read Apple's own Core Animation layer tree for every probe rung.
#
# `dump-layers` captures nothing and needs no TCC grant, so this is the cheapest evidence available
# and the most direct: if CoreAnimation states the corner radius and corner curve it draws, that is
# a statement from the reference implementation rather than an inference from pixels.
#
# The app is launched from the MAIN checkout's bundle through `open --env`, for the two reasons the
# harness README records: the Screen Recording grant is keyed to that bundle identity, and
# `launchctl setenv` never reaches the GUI session an agent's shell launches into, so the scene bed
# and the output directory have to travel as `open --env`.
#
# Usage: `bash run-dump-layers.sh`, from anywhere.
set -eu

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes-w20-probe.json"
OUT="$HERE/layer-dumps"
MAIN=/Users/new/developer/github/designer/apps/reference-apple/build/VitreaReference.app
LOG=/tmp/w20g0

mkdir -p "$LOG" "$OUT"
IDS="$(python3 -c "
import json, sys
print(','.join(s['id'] for s in json.load(open(sys.argv[1]))['scenes']))
" "$SCENES")"

echo "scenes: $IDS"
open -W --env VITREA_SCENES="$SCENES" --stdout "$LOG/dump.out" --stderr "$LOG/dump.err" \
  "$MAIN" --args dump-layers --settle 8 --out "$OUT" --scenes "$IDS"
echo "DUMP DONE $(date -u +%H:%M:%SZ)"
