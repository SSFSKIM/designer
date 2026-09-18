#!/bin/bash
# Every pair the slider probe needs, in one pass, per arm.
#
#   pair-all.sh <arm-root> <out-dir>
#
# The three centre-against-centre pairs come first and they are the point: a
# difference between two slider positions means nothing until the same cell's
# difference from itself is on the page beside it. Every other pair is a position
# against the FIRST centre run, so all of them are read against one reference
# rather than against whichever run happened to be next.
#
# `DELETED` is the arm with no key at all, and it is a control rather than a
# position: if the absent key renders as the centre, it says what the system's own
# default is, which is the question the bed's "default position" turns on.
set -euo pipefail

ARM="${1:?usage: pair-all.sh <arm-root> <out-dir>}"
OUT="${2:?usage: pair-all.sh <arm-root> <out-dir>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG="$(cd "$HERE/../.." && pwd)"

mkdir -p "$OUT"
pair() {
  local a="$1" b="$2" name="$3"
  [ -d "$ARM/$a" ] || { echo "skip $name: no $a"; return; }
  [ -d "$ARM/$b" ] || { echo "skip $name: no $b"; return; }
  echo "== $name"
  (cd "$PKG" && npx tsx results/2026-09-18-w29-g0-preflight/native-pair.ts \
    --a "$ARM/$a" --b "$ARM/$b" --label-a "$a" --label-b "$b" \
    --out "$OUT/$name.json") | tail -n +1
}

pair 0.5-r1 0.5-r2 centre-r1-r2
pair 0.5-r1 0.5-r3 centre-r1-r3
pair 0.5-r2 0.5-r3 centre-r2-r3
pair 0.5-r1 0.0-r1 centre-vs-left
pair 0.5-r1 1.0-r1 centre-vs-right
pair 0.5-r1 0.5459057-r1 centre-vs-asfound
pair 0.5-r1 DELETED-r1 centre-vs-absent
