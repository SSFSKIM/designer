#!/bin/bash
# Every AssertionError the gate raised, per rung, one line each — so a bound failure cannot hide
# behind a census failure.
set -u
T=/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c
for r in c0b d8b d9b d10b d11b x98b x910b; do
  echo "=== $r"
  grep -h "AssertionError" "$T/$r/gate.log" 2>/dev/null | cut -c1-190 | sed 's/^/    /'
done
