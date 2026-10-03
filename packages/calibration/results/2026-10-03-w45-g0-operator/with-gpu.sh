#!/bin/zsh
# W45 G0: run one browser launch under the GPU lock and the classifying web census.
#
#   results/2026-10-03-w45-g0-operator/with-gpu.sh <label> <command> [args...]
#
# Two W45 workers share one adapter, and the census (§5.201 §21) REFUSES while another
# Playwright-launched Chromium is up, so launches are serialised: the lock is a directory
# (`mkdir` is atomic), held for the census and the launch together and released on every exit.
# The census is read by `census-gate.py`, which appends the observation to `census.jsonl`; a
# refusal releases the lock and exits 1 without launching. The command's own exit code is
# returned.
LOCK=/tmp/w45-gpu.lock
HERE=${0:A:h}
label=$1; shift
until mkdir $LOCK 2>/dev/null; do sleep 3; done
trap 'rmdir $LOCK 2>/dev/null' EXIT INT TERM HUP
python3.12 -B $HERE/census-gate.py "$label" || exit 1
"$@"
