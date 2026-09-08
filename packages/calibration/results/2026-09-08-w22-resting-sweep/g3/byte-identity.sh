#!/bin/bash
# W22 G3 — every non-stacked capture against G0's, byte for byte.
set -u
G0=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0/after/web-captures
G3=/Users/new/.claude/jobs/5c70e47f/tmp/w22/g3/bed
same=0; moved=0; missing=0
while read -r png; do
  rel=${png#"$G3"/}
  ref="$G0/$rel"
  if [ ! -f "$ref" ]; then echo "MISSING-IN-G0  $rel"; missing=$((missing+1)); continue; fi
  a=$(shasum -a 256 "$png" | cut -d' ' -f1)
  b=$(shasum -a 256 "$ref" | cut -d' ' -f1)
  if [ "$a" = "$b" ]; then same=$((same+1)); else echo "MOVED  $rel"; echo "   g0 ${b:0:16}  g3 ${a:0:16}"; moved=$((moved+1)); fi
done < <(find "$G3" -name '*.png' | sort)
echo
echo "byte-identical: $same   moved: $moved   not in G0: $missing"
# The other direction: anything G0 captured that this run did not.
while read -r png; do
  rel=${png#"$G0"/}
  [ -f "$G3/$rel" ] || echo "NOT-RECAPTURED  $rel"
done < <(find "$G0" -name '*.png' | sort)
