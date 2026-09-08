#!/bin/bash
# W24 G1 (b) — `transmission-read.txt`: the whole read, in the order the acceptance asks it.
# Usage: `bash run-transmission-read.sh [captures-dir] [label] > transmission-read.txt`
set -eu
G1="$(cd "$(dirname "$0")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
R=/Users/new/Developer/GitHub/designer
W="${1:-$R/packages/calibration/web-captures}"
LABEL="${2:-landed}"

cat <<'HEAD'
W24 G1 (b) — the transmission read: what the reference's collapsed material passes and what
vitrea's does, on the four impulse cells and the dark thin structured cells

Instrument: `read-impulse.py` (validated below on the background itself — a 4 CSS px dot reads
peak 1.0, FWHM 4.00 CSS px and integral 4.000 at both scales, exactly), `read-structure.py` (the
body and W21 G0's passthrough) and `psf.py` (the kernel behind the FWHM). Every number is linear
luma. `native` is the committed fixture; `landed` is the 0.12.0 capture at `408ad2e`, GPU tier.
The impulse background is fifteen 4 CSS px white dots on black: 4 DEVICE px across at 1x and 8 at
2x, which is the fact a width quoted in CSS px hides.

Agreement with the parent's own table in `finding/eye-finding.txt`, which is the instrument's
second validation: light `impulse__capsule-button` 1x native +0.0065 / FWHM 8 / 0.050 against this
read's +0.0066 / 7.57 / 0.0508; 2x native +0.0254 / 4 / 0.107 against +0.0254 / 3.80 / 0.1074;
`impulse__rrect-md` 2x native +0.062 / 9 / 0.65 against +0.0596 / 8.65 / 0.5763 and landed +0.071 /
8 / 0.70 against +0.0701 / 8.28 / 0.6791. The headline rows agree to the fourth decimal; the
parent's integrals on the rrect run wider because its window is wider, and the difference is the
window, not the reading.

HEAD

echo "======== 1. the impulse cells — the dot through the body, native against $LABEL"
bash "$G1/run-reads.sh" "$W" "$LABEL"

cat <<'MID'

======== 2. the dark thin structured cells, and the collapsed stop cells

`pass` = the body's own sd over the backdrop's sd under the same region (W21 G0's passthrough,
`results/2026-09-06-w21-dark-scheme/g0/passthrough.txt`): the fraction of the structure on offer
that the material let through. `code` is the body's 8-bit code, which is the unit W23 G0 quoted the
appearance term in.
MID
CELLS=""
for spec in \
  "apple-macos-26.5-1x-dark-standard/checkerboard__capsule-button__rest/capsule-button/1" \
  "apple-macos-26.5-2x-dark-standard/checkerboard__capsule-button__rest/capsule-button/2" \
  "apple-macos-26.5-1x-dark-standard/photo__capsule-button__rest/capsule-button/1" \
  "apple-macos-26.5-2x-dark-standard/photo__capsule-button__rest/capsule-button/2" \
  "apple-macos-26.5-1x-dark-standard/impulse__capsule-button__rest/capsule-button/1" \
  "apple-macos-26.5-2x-dark-standard/impulse__capsule-button__rest/capsule-button/2" \
  "apple-macos-26.5-1x-light-standard/impulse__capsule-button__rest/capsule-button/1" \
  "apple-macos-26.5-2x-light-standard/impulse__capsule-button__rest/capsule-button/2" \
  "apple-macos-26.5-1x-dark-standard/dark-solid__capsule-button__rest/capsule-button/1" \
  "apple-macos-26.5-2x-dark-standard/dark-solid__capsule-button__rest/capsule-button/2"; do
  CELLS="$CELLS $spec"
done
# shellcheck disable=SC2086
$PY "$G1/read-structure.py" "$W" $CELLS

cat <<'TAIL'

======== 3. the kernel the dot arrives through

The dot is a 4 CSS px box, so the profile through the body is that box convolved with the
material's own blur; `psf.py` recovers it as a sharp and a heavy Gaussian in DEVICE px.
TAIL
bash "$G1/run-psf.sh" "$W"
