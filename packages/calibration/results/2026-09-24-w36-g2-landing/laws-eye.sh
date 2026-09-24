#!/bin/sh
# One X6-attested CLI browser session; no calibration capture (§5.180 clause 8).
set -eu
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../../.." && pwd)
cd "$repo"
trap 'playwright-cli -s=w36-g2-eye close > "$here/laws-close-inline.txt" 2>&1' EXIT
playwright-cli -s=w36-g2-eye open 'http://localhost:5197/laws/?renderer=webgpu' \
  --config="$here/laws-browser.json" > "$here/laws-open-inline.txt" 2>&1
playwright-cli -s=w36-g2-eye run-code "$(cat "$here/laws-shot.js")" > "$here/laws-readings-inline.txt" 2>&1
# The CLI can report a browser-side error in an exit-zero response; preserve it and fail loudly.
if grep -q '^### Error' "$here/laws-readings-inline.txt"; then
  cat "$here/laws-readings-inline.txt"
  exit 1
fi
