#!/bin/zsh
# W48 G1 step 4 (the re-freeze, W48_G1_ROUND=dl9): the dark strict-mode stage on both tiers, then X60's light strict-mode stage and its
# reading. A dark pass the census refused is relaunched under --relaunch-after-stop (stage.py's rule)
# once the census passes again.
set -u
cd ${0:A:h}
W48_G1_ROUND=dl9 python3.12 -B run.py dark declare || exit 1
for tier in webgpu css; do
  W48_G1_ROUND=dl9 python3.12 -B run.py dark measure $tier && continue
  for try in 1 2 3 4 5 6; do
    until python3.12 -B -c "import sys; sys.path.insert(0, '../../2026-10-06-w48-g0-declaration'); import inherit; sys.exit(0 if inherit.W.census().observe()['passes'] else 1)"; do sleep 120; done
    W48_G1_ROUND=dl9 python3.12 -B run.py dark measure $tier --relaunch-after-stop "census refused (attempt $try)" && break
  done || exit 1
done
W48_G1_ROUND=dl9 python3.12 -B run.py x60 declare || exit 1
W48_G1_ROUND=dl9 python3.12 -B run.py x60 measure webgpu || exit 1
W48_G1_ROUND=dl9 python3.12 -B run.py x60 measure css || exit 1
W48_G1_ROUND=dl9 python3.12 -B run.py x60 read
echo CHAIN-DONE $?
