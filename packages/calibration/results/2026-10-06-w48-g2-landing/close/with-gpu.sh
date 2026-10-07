#!/bin/zsh
# W48 G2: one browser launch under the GPU lock, the classifying web census and the browser pin, for the
# landing's c9d chain. G1's with-gpu.sh with G2's census log (census-gate.py beside this file) and the
# same lock (/tmp/w48-gpu.lock). A census refusal is retried with backoff (60 s doubling to 600 s, at
# most 12 tries) with the lock released while waiting; no other session's browser is ever touched.
# The command's own exit code is returned; a census that never passes exits 3.
LOCK=/tmp/w48-gpu.lock
HERE=${0:A:h}
label=$1; shift
wait=60
for try in {1..12}; do
  until mkdir $LOCK 2>/dev/null; do sleep 3; done
  trap 'rmdir $LOCK 2>/dev/null' EXIT INT TERM HUP
  if python3.12 -B $HERE/census-gate.py "$label"; then
    "$@"
    exit $?
  fi
  rmdir $LOCK 2>/dev/null
  trap - EXIT INT TERM HUP
  echo "census refused ($label, try $try); retrying in ${wait}s" >&2
  sleep $wait
  wait=$(( wait * 2 > 600 ? 600 : wait * 2 ))
done
exit 3
