#!/bin/bash
# W24 G1 (b) — the kernel behind the FWHM, on the reference and on vitrea, at both scales.
set -eu
G1="$(cd "$(dirname "$0")" && pwd)"
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
R=/Users/new/Developer/GitHub/designer
W="${1:-$R/packages/calibration/web-captures}"
F="$R/apps/reference-apple/fixtures"
$PY "$G1/psf.py" \
  "native capsule=$F/apple-macos-26.5-1x-light-standard/impulse__capsule-button__rest.png:1" \
  "native capsule=$F/apple-macos-26.5-2x-light-standard/impulse__capsule-button__rest.png:2" \
  "native rrect-md=$F/apple-macos-26.5-1x-light-standard/impulse__rrect-md__rest.png:1" \
  "native rrect-md=$F/apple-macos-26.5-2x-light-standard/impulse__rrect-md__rest.png:2" \
  "landed capsule=$W/apple-macos-26.5-1x-light-standard/impulse__capsule-button__rest/impulse__capsule-button__rest__webgpu.png:1" \
  "landed capsule=$W/apple-macos-26.5-2x-light-standard/impulse__capsule-button__rest/impulse__capsule-button__rest__webgpu.png:2" \
  "landed rrect-md=$W/apple-macos-26.5-1x-light-standard/impulse__rrect-md__rest/impulse__rrect-md__rest__webgpu.png:1" \
  "landed rrect-md=$W/apple-macos-26.5-2x-light-standard/impulse__rrect-md__rest/impulse__rrect-md__rest__webgpu.png:2"
