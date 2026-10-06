#!/bin/zsh
# W48 G0 (b): W47's with-gpu.sh copied (charter clause 2) because it hard-codes its lock and runs the
# census-gate.py beside itself; the lock is W48's /tmp/w48-gpu.lock and the census W48's copy. Nothing else
# changes; W47's text follows.
#
# W47 G0: run one browser launch under the GPU lock, the classifying web census and the browser pin.
#
#   results/2026-10-06-w48-g0-declaration/with-gpu.sh <label> <command> [args...]
#
# W46's with-gpu.sh, ported (W45's before it): W47's workers share one adapter, and the census (§5.201 §21) REFUSES
# while another Playwright-launched Chromium is up, so launches are serialised by a lock directory
# (`mkdir` is atomic) held for the census and the launch together and released on every exit. The
# census and the pin are read by `census-gate.py`, which appends to `census.jsonl`; a refusal releases
# the lock and exits 1 without launching. The command's own exit code is returned.
LOCK=/tmp/w48-gpu.lock
HERE=${0:A:h}
label=$1; shift
until mkdir $LOCK 2>/dev/null; do sleep 3; done
trap 'rmdir $LOCK 2>/dev/null' EXIT INT TERM HUP
python3.12 -B $HERE/census-gate.py "$label" || exit 1
"$@"
