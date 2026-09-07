#!/bin/bash
# W21 G2 — the LANDED canonical dark bed read under the declared geometry (contract X2).
#
# G1's `read-canonical.sh`, re-pointed: the "after" column is now the canonical `web-captures/` on
# this machine rather than a scratch dry run, and the "before" column is the W20 bed's captures kept
# in scratch by `g2-rebuild.sh`. The native side is the canonical fixtures in both columns, so the
# two differ only by what vitrea drew.
#
# The point is referee item (iv): `g1-clauses.py` over this directory must print what
# `g1-clauses.txt` printed. The matrix cannot answer clauses 3 and 4 on this scheme — over the dark
# solids the native silhouette is the rim ring in fragments (claims §5.87) — so this read, not the
# matrix, is what the clauses were judged on and what the landing has to reproduce.
#
# Usage: bash g2-read-canonical.sh <landed captures dir> <W20 bed captures dir>
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../../../.." && pwd)"
SCENES="$ROOT/apps/reference-apple/scenes.json"
FIXTURES="$ROOT/apps/reference-apple/fixtures"
AFTER="${1:?usage: g2-read-canonical.sh <landedCaptures> <w20BedCaptures>}"
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
