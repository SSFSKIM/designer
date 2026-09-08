#!/bin/bash
# W22 G3 — the per-pane read of the fix's own captures, web only, no fixture opened.
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
CAPTURES=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g3/stacked
PROFILES="$WORKTREE/packages/calibration/profiles"

mkdir -p "$HERE/stack-reads"
for PROFILE in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
               apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard; do
  case "$PROFILE" in
    *dark*) DOC="$PROFILES/apple-macos-26.5-1x-dark-standard.json" ;;
    *)      DOC="$PROFILES/apple-macos-26.5-1x-light-standard.json" ;;
  esac
  for TIER in webgpu css; do
    OUT="$HERE/stack-reads/$PROFILE-$TIER"
    "$PY" "$HERE/read-stack-web.py" --captures "$CAPTURES" --scenes "$SCENES" \
      --profile "$PROFILE" --profile-doc "$DOC" --tier "$TIER" --json "$OUT.json" > "$OUT.txt"
    cat "$OUT.txt"
  done
done
