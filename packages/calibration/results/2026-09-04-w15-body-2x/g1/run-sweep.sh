#!/bin/bash
# W15 G1: one runtime sweep at 2x on the G1 branch (claims §5.69; the charter's binding rule
# that the renderer is the fitting instrument). Usage:
#
#   bash results/2026-09-04-w15-body-2x/g1/run-sweep.sh <name> [--base <patch.json>] \
#        --axis <path>=v1,v2,... [--axis ...]
#
# Runs `scripts/sweep.ts` from the G1 worktree at --profile apple-macos-26.5-2x-light-standard on
# the calibration set (sweep.ts cannot name the holdout), writes the ranked table to
# $T/<name>.out and archives every point's profile and matrix to $T/points-<name>/ so the reader
# (report15.py) keys each row by the point's OWN patch rather than by grid order. The GPU is
# shared: refuse to start while another capture is running.
set -u
NAME=$1; shift
T=/Users/new/.claude/jobs/5c70e47f/tmp/w15/g1
W=/Users/new/Developer/GitHub/designer/.claude/worktrees/w15-g1/packages/calibration
mkdir -p "$T"
if pgrep -f 'compare.ts|sweep.ts' > /dev/null || lsof -i :5189 > /dev/null 2>&1; then
  echo "GPU busy: another capture is running"; exit 2
fi
cd "$W"
rm -rf sweep-work; mkdir -p sweep-work
echo "=== $(date +%H:%M:%S) sweep $NAME: $* ==="
npx tsx scripts/sweep.ts --profile apple-macos-26.5-2x-light-standard --renderer webgpu "$@" \
  > "$T/$NAME.out" 2> "$T/$NAME.err"
echo "    exit=$?"
rm -rf "$T/points-$NAME"; cp -R sweep-work "$T/points-$NAME"
echo "=== $(date +%H:%M:%S) done: $(ls "$T/points-$NAME" | grep -c '^matrix-') points archived ==="
tail -n +1 "$T/$NAME.out" | sed -n '/^point/,$p' | head -40
