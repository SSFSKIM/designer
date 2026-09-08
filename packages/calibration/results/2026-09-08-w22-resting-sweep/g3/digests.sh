#!/bin/bash
set -eu
T=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g3
echo "# W22 G3 — capture digests, $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "# scratch root $T"
for ROOT in "$T/stacked" "$T/bed"; do
  [ -d "$ROOT" ] || continue
  echo
  echo "## $(basename "$ROOT")"
  find "$ROOT" -name '*.png' | sort | while read -r PNG; do
    printf '%s  %s\n' "$(shasum -a 256 "$PNG" | cut -c1-16)" "${PNG#"$T/"}"
  done
done
