#!/bin/zsh
# W48 G1 step 7: the exposure, read 8, once: the seven holdout scenes and the six referees per scale, both
# tiers, into the re-freeze's dark stage. A pass the census refused is relaunched under stage.py's rule.
set -u
cd ${0:A:h}
export W48_G1_ROUND=dl9
for tier in webgpu css; do
  python3.12 -B run.py dark exposure $tier && continue
  for try in 1 2 3 4 5 6; do
    until python3.12 -B -c "import sys; sys.path.insert(0, '../../2026-10-06-w48-g0-declaration'); import inherit; sys.exit(0 if inherit.W.census().observe()['passes'] else 1)"; do sleep 120; done
    python3.12 -B run.py dark exposure $tier --relaunch-after-stop "census refused (attempt $try)" && break
  done || exit 1
done
echo EXPOSURE-DONE
