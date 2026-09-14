#!/bin/sh
# Append one machine-settings reading to `browser-runs.txt`, labelled with the run
# it precedes. A nonzero reading exits nonzero so the caller cannot launch under an
# accessibility policy Playwright would not record.
set -e
here=$(dirname "$0")
rt=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)
ic=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)
printf '%s  %-26s reduceTransparency=%s increaseContrast=%s\n' \
  "$(date -u +%FT%TZ)" "$1" "$rt" "$ic" >> "$here/browser-runs.txt"
tail -n 1 "$here/browser-runs.txt"
[ "$rt" = "0" ] && [ "$ic" = "0" ]
