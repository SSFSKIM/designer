#!/bin/bash
# W21 G1 — the canonical dark bed read under the DECLARED geometry (contract X2), before and after.
#
# The wave's clauses 3 and 4 are stated on the body and the rim under the declared geometry, and the
# matrix cannot answer them on this scheme: over the dark solids the native silhouette is the rim
# ring in fragments, so `interiorMean` measures the rim on both sides and `dark-solid__rrect-md` is
# excluded from the gate entirely (claims §5.87). This is the reading the clauses are judged on.
#
# Eight reads: the two dark profiles crossed with the two tiers crossed with BEFORE (the canonical
# `web-captures/` on the capture machine, which is the W20 bed's captures) and AFTER (this gate's
# dry run in scratch). The native side is the canonical fixtures in both cases, so the two columns
# differ only by what vitrea drew.
#
# `--sets` names every split including the holdout: this is the gate the wave's one holdout read is
# spent on (contract X6), and the holdout cells are read here exactly once.
#
# Usage: `bash read-canonical.sh <dry-run captures dir> <canonical captures dir>`
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$WORKTREE/apps/reference-apple/scenes.json"
FIXTURES="$WORKTREE/apps/reference-apple/fixtures"
AFTER="${1:?usage: read-canonical.sh <dryRunCaptures> <canonicalCaptures>}"
BEFORE="${2:?}"

mkdir -p "$HERE/canonical-reads"
for PROFILE in apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard; do
  for TIER in webgpu css; do
    for WHEN in before after; do
      [ "$WHEN" = before ] && CAP="$BEFORE" || CAP="$AFTER"
      OUT="$HERE/canonical-reads/$PROFILE-$TIER-$WHEN"
      "$PY" "$HERE/../g0/read.py" --scenes "$SCENES" --fixtures "$FIXTURES" --profile "$PROFILE" \
        --captures "$CAP" --tier "$TIER" --sets calibration,validation,holdout,recorded \
        --json "$OUT.json" > "$OUT.txt"
      echo "read $PROFILE / $TIER / $WHEN -> canonical-reads/$(basename "$OUT").json"
    done
  done
done
