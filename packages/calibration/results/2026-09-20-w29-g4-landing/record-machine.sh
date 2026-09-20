#!/bin/sh
# Append one machine-settings reading to `browser-runs.txt`, labelled with the run
# it precedes. A nonzero reading exits nonzero so the caller cannot launch under an
# accessibility policy Playwright would not record.
set -e
here=$(dirname "$0")
rt=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)
ic=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)
# The slider joins the reading at W29: `NSGlassTintAmount` did not exist on macOS
# 26.5 and it drives the native material with no GUI, so a bed and a browser run
# taken at different positions are taken under different appearances. It is read
# here rather than refused on, because no browser suite renders the native
# material — what it makes is a record of the machine each run was taken on.
glass=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)
printf '%s  %-26s reduceTransparency=%s increaseContrast=%s NSGlassTintAmount=%s\n' \
  "$(date -u +%FT%TZ)" "$1" "$rt" "$ic" "$glass" >> "$here/browser-runs.txt"
tail -n 1 "$here/browser-runs.txt"
[ "$rt" = "0" ] && [ "$ic" = "0" ]
