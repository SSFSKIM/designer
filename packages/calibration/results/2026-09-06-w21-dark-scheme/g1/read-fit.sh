#!/bin/bash
# W21 G1 — read one fit candidate's probe-grid capture with the wave's instrument.
#
# G0's `run-read.sh` reduced to the one job this gate repeats: the reference is already read (G0's
# `probe-read.json`, which this gate does not re-derive), so a candidate needs only its own web
# column beside the same native bed. The holdout column stays unread — `read.py`'s `--sets` default
# is calibration, validation and recorded, and the wave's one holdout read is the canonical bed's.
#
# Usage: `bash read-fit.sh <capturesRoot> <label> [<label> ...]`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes-w21-probe.json"
PROBE="$HERE/../probe"
ROOT="${1:?usage: read-fit.sh <capturesRoot> <label>...}"
shift

mkdir -p "$HERE/fit-reads"
for LABEL in "$@"; do
  "$PY" "$HERE/../g0/read.py" --scenes "$SCENES" --fixtures "$PROBE" \
    --captures "$ROOT/$LABEL/web-captures" --tier webgpu \
    --json "$HERE/fit-reads/$LABEL.json" > "$HERE/fit-reads/$LABEL.txt"
  echo "read $LABEL -> fit-reads/$LABEL.json"
done
