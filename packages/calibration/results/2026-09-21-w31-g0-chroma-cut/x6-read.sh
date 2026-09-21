#!/bin/bash
# X6, read before every browser run of this child and appended to browser-runs.txt.
# Reduce Transparency and Increase Contrast must both read 0 and the appearance
# slider must read 0.5; Playwright cannot emulate any of the three, so a run at
# the wrong settings would produce plausible numbers of a different material.
set -u
RT=$(defaults read com.apple.universalaccess reduceTransparency 2>/dev/null || echo 0)
IC=$(defaults read com.apple.universalaccess increaseContrast 2>/dev/null || echo 0)
GLASS=$(defaults read -g NSGlassTintAmount 2>/dev/null || echo absent)
printf '%s  %-28s reduceTransparency=%s increaseContrast=%s NSGlassTintAmount=%s  %s/%s head=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${1:-unlabelled}" "$RT" "$IC" "$GLASS" \
  "$(sw_vers -productVersion)" "$(sw_vers -buildVersion)" "$(git rev-parse --short HEAD)"
[ "$RT" = "0" ] || { echo "x6-read: reduceTransparency is $RT" >&2; exit 1; }
[ "$IC" = "0" ] || { echo "x6-read: increaseContrast is $IC" >&2; exit 1; }
[ "$GLASS" = "0.5" ] || { echo "x6-read: NSGlassTintAmount is $GLASS" >&2; exit 1; }
