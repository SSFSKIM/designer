#!/usr/bin/env bash
# X6's machine read, one line, appended to machine.txt before and after every
# browser run this gate takes. RT and IC must both be 0 and the appearance
# slider 0.5; the script refuses rather than records a run taken at anything
# else, because a recorded run at the wrong machine state is worse than no run.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
label="${1:-unlabelled}"
rt=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)
ic=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)
glass=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)
head=$(git -C "$here" rev-parse --short HEAD)
line=$(printf '%s  %-34s machine: %s/%s RT=%s IC=%s NSGlassTintAmount=%s head=%s' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$label" \
  "$(sw_vers -productVersion)" "$(sw_vers -buildVersion)" "$rt" "$ic" "$glass" "$head")
echo "$line" | tee -a "$here/machine.txt"
[ "$rt" = "0" ] || { echo "record-machine: reduceTransparency is $rt" >&2; exit 1; }
[ "$ic" = "0" ] || { echo "record-machine: increaseContrast is $ic" >&2; exit 1; }
[ "$glass" = "0.5" ] || { echo "record-machine: NSGlassTintAmount is $glass" >&2; exit 1; }
