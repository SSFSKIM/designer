#!/bin/bash
# Every pair the SDK-gating pixel arm needs — W29 G1 (4), claims §5.150.
#
# Each arm's own run-to-run spread first, then the arms against each other. A
# difference between two bundles means nothing until the same cell's difference
# from itself is on the page beside it; the harness's own determinism check makes
# a repeat capture byte-stable within a run, so a byte difference BETWEEN runs of
# one configuration already IS the spread rather than noise below it.
#
# The side arm's `active-r3` is excluded, and its exclusion is the arm's own
# finding: it lost the presentation pose on 5 of its 8 cells at 1–5 s of HID idle
# (`audit.txt`), which is the failure plan.md §7 names — a run that loses the pose
# mid-pass reads against its neighbours like a material difference. So the side
# arm's spread is one pair and the cross-arm comparison is taken at r1 and r2.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG="$(cd "$HERE/../.." && pwd)"
S="$HOME/vitrea-w29-g0-scratch/sdk-pixel"
OUT="$HOME/vitrea-w29-g0-scratch/sdk-pixel/pairs"
mkdir -p "$OUT"

pair() {
  local a="$1" b="$2" la="$3" lb="$4" name="$5"
  echo "== $name"
  (cd "$PKG" && npx tsx results/2026-09-18-w29-g0-preflight/native-pair.ts \
    --a "$a" --b "$b" --label-a "$la" --label-b "$lb" --out "$OUT/$name.json")
}

pair "$S/harness/active-r1" "$S/harness/active-r2" h-r1 h-r2 harness-r1-r2
pair "$S/harness/active-r1" "$S/harness/active-r3" h-r1 h-r3 harness-r1-r3
pair "$S/harness/active-r2" "$S/harness/active-r3" h-r2 h-r3 harness-r2-r3
pair "$S/side-sdk27/active-r1" "$S/side-sdk27/active-r2" s-r1 s-r2 side-r1-r2
pair "$S/harness/active-r1" "$S/side-sdk27/active-r1" harness side27 cross-r1
pair "$S/harness/active-r2" "$S/side-sdk27/active-r2" harness side27 cross-r2
echo "→ $OUT"
