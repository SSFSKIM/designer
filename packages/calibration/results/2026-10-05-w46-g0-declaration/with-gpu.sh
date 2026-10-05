#!/bin/zsh
# W46 G0: run one browser launch under the GPU lock, the classifying web census and the browser pin.
#
#   results/2026-10-05-w46-g0-declaration/with-gpu.sh <label> <command> [args...]
#
# W45's with-gpu.sh, ported: W46's workers share one adapter, and the census (§5.201 §21) REFUSES
# while another Playwright-launched Chromium is up, so launches are serialised by a lock directory
# (`mkdir` is atomic) held for the census and the launch together and released on every exit. The
# census and the pin are read by `census-gate.py`, which appends to `census.jsonl`; a refusal releases
# the lock and exits 1 without launching. The command's own exit code is returned.
LOCK=/tmp/w46-gpu.lock
HERE=${0:A:h}
label=$1; shift
until mkdir $LOCK 2>/dev/null; do sleep 3; done
trap 'rmdir $LOCK 2>/dev/null' EXIT INT TERM HUP
python3.12 -B $HERE/census-gate.py "$label" || exit 1
"$@"
