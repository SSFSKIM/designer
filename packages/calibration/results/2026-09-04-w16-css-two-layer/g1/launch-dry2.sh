#!/bin/bash
cd /Users/new/Developer/GitHub/designer/.claude/worktrees/w16-g1
echo "=== build $(date +%H:%M:%S) HEAD $(git rev-parse --short HEAD)"
pnpm -r build > $T/build-dry2.log 2>&1 || { echo "BUILD FAILED"; exit 1; }
bash /Users/new/Developer/GitHub/designer/.claude/worktrees/w16-g1/packages/calibration/results/2026-09-04-w16-css-two-layer/g1/run-dry.sh dry2 webgpu calibration,validation,holdout
bash /Users/new/Developer/GitHub/designer/.claude/worktrees/w16-g1/packages/calibration/results/2026-09-04-w16-css-two-layer/g1/run-dry.sh dry2 css calibration,validation
bash /Users/new/Developer/GitHub/designer/.claude/worktrees/w16-g1/packages/calibration/results/2026-09-04-w16-css-two-layer/g1/run-dry.sh dry2 css holdout
echo "ALL DRY2 DONE $(date +%H:%M:%S)"
