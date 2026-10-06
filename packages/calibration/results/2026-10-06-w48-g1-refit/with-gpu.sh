#!/bin/zsh
# W48 G1: one browser launch under the GPU lock, the classifying web census and the browser pin.
# G0's with-gpu.sh with G1's census log (census-gate.py beside this file); the same lock
# (/tmp/w48-gpu.lock), so G0's and G1's launches are serialised against each other. The command's own
# exit code is returned. W46 G1's form.
LOCK=/tmp/w48-gpu.lock
HERE=${0:A:h}
label=$1; shift
until mkdir $LOCK 2>/dev/null; do sleep 3; done
trap 'rmdir $LOCK 2>/dev/null' EXIT INT TERM HUP
python3.12 -B $HERE/census-gate.py "$label" || exit 1
"$@"
