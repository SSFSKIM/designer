#!/bin/bash
# W17 G1: the whole-bed dry run, in the order the evidence needs.
#
# The GPU tier goes first in every configuration because a dom cell's coherence axis is measured
# against the webgpu capture already on disk. The two configurations are two BUILDS of this branch
# — configuration 1 stands the transfer down with a one-line local edit so the ordering fix and the
# inner shadow can be read alone — so this script is run once per build with the matching tag:
#
#   bash launch-dry.sh cfg1     # after building with the transfer stood down
#   bash launch-dry.sh cfg2     # after building the branch as committed
#   bash launch-dry.sh holdout  # contract X8, on the frozen configuration 2, once
set -u
TAG=$1
G=/Users/new/Developer/GitHub/designer/.claude/worktrees/w17-g1/packages/calibration/results/2026-09-04-w17-css-interior-level/g1
if [ "$TAG" = "holdout" ]; then
  bash "$G/run-dry.sh" cfg2 webgpu holdout
  bash "$G/run-dry.sh" cfg2 css holdout
else
  bash "$G/run-dry.sh" "$TAG" webgpu calibration,validation
  bash "$G/run-dry.sh" "$TAG" css calibration,validation
fi
echo "ALL DONE $TAG $(date +%H:%M:%S)"
