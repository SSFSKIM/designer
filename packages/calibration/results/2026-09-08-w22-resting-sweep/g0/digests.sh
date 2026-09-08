#!/bin/bash
# W22 G0 — the sha256 of every capture this gate produced, so a later gate can reproduce them.
#
# The digest is of the PNG on disk, which is what the readers opened. Both the shipped-constants
# captures (`after/`) and the candidate renders (`fit/`, `probe/`) are listed, because the fit's
# rendered points are evidence too: a fit is only reproducible if the points it was fitted on are.
#
# Usage: `bash digests.sh > digests.txt`
set -eu
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0
echo "# W22 G0 — capture digests, $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "# scratch root $T"
for ROOT in "$T/after" "$T/fit" "$T/probe"; do
  [ -d "$ROOT" ] || continue
  echo
  echo "## $(basename "$ROOT")"
  find "$ROOT" -name '*.png' | sort | while read -r PNG; do
    printf '%s  %s\n' "$(shasum -a 256 "$PNG" | cut -c1-16)" "${PNG#"$T/"}"
  done
done
