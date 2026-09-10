#!/bin/bash
# W26 G1c — the capture runs in the shared checkout, so prove it is running THIS branch's code.
#
# A worktree carries no `node_modules`, and a second install would be a second toolchain rather than
# the same one. So every rung is captured in the shared checkout, and this script is the precondition
# that makes that honest: every source the capture's output depends on — the renderer, the pyramid
# and its plan, the passes, the optics shader, the backdrop shader, the harness's `compare.ts`, the
# two committed profile documents the rung's scratch documents are derived from, and `scenes.json`
# — must be byte-identical between the worktree and the checkout. A single difference refuses the
# run, because a rung captured against different source is evidence about a different material.
set -u
W="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
M=/Users/new/Developer/GitHub/designer
BAD=0
for f in \
  packages/renderer-webgpu/src/pyramid.ts \
  packages/renderer-webgpu/src/pyramid-plan.ts \
  packages/renderer-webgpu/src/renderer.ts \
  packages/renderer-webgpu/src/passes.ts \
  packages/renderer-webgpu/src/material.ts \
  packages/renderer-webgpu/src/wgsl/optics.ts \
  packages/renderer-webgpu/src/wgsl/backdrop.ts \
  packages/calibration/cli/compare.ts \
  packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json \
  packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json \
  apps/reference-apple/scenes.json
do
  a=$(shasum -a 256 "$W/$f" | cut -c1-16)
  b=$(shasum -a 256 "$M/$f" | cut -c1-16)
  if [ "$a" != "$b" ]; then echo "DIFF $f worktree=$a checkout=$b" >&2; BAD=1; fi
done
[ "$BAD" = 0 ] && echo "SAME: every capture-relevant source is byte-identical to the checkout"
exit $BAD
