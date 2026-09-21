#!/usr/bin/env bash
#
# W31 G0 — the chroma bed's web side, captured as SCRATCH at the shipped
# documents (acceptance clause 1; claims §5.161 §2).
#
#   ./scratch-capture.sh 27      # the six macOS 27 profiles, both tiers
#   ./scratch-capture.sh 26.5    # the six macOS 26.5 trees, re-measured
#
# **Nothing here is canonical and nothing is appended.** `--out-matrix` writes
# into this evidence directory and `VITREA_WEB_CAPTURES` writes into a scratch
# tree outside the repository; `results/matrix.json` and the canonical
# `web-captures/` are not touched by either mode. The rows this produces carry a
# statistic that did not exist when the committed generation was read, and the
# committed generation stays the reading — see `reproduction-check.md`.
#
# Why a re-capture at all: no current-generation capture tree exists on this
# machine (charter Surprises). The canonical `web-captures/` holds the six macOS
# 26.5 trees and nothing else, and every macOS 27 tree was written inside a
# worktree that has since been removed.
#
# **The holdout cells are re-captured, and that is disclosed rather than
# assumed.** `photo__rrect-lg__rest` and `photo__glass-over-glass__rest` are
# holdout scenes and four of the wave's claimed rows are the first of them.
# Decision Log 1 (b) reads the holdout once per frozen configuration, and this
# is the SAME configuration the committed rows were read at — identical document
# bytes, identical renderer sources, no fitted constant moved. So this is not a
# second holdout verdict: the committed rows remain the reading and this run
# exists only to carry the per-pixel chroma statistic and to decompose the four
# missed rows, neither of which the committed rows can be asked for. The
# reproduction check is what makes that claim checkable rather than asserted.
#
# The 26.5 mode is `--skip-capture` over a COPY of the canonical trees. The
# frozen trees are never read in place and never written to: X1 wants no macOS
# 26.5 path to move, and the cheapest way to guarantee that is to not open them
# for writing at all.
set -euo pipefail
cd "$(dirname "$0")/../.."

MODE="${1:?usage: scratch-capture.sh 27|26.5}"
HERE=results/2026-09-21-w31-g0-chroma-cut
SCRATCH=/tmp/w31-g0-captures
MATRIX="$HERE/scratch-matrix.json"

# X6's exclusivity, in two parts rather than one pattern.
#
# **Refused**: another CALIBRATION capture. Two runs of this harness contend for
# the same display, the same dev server and the same GPU, and the second one's
# numbers are not of the material.
#
# **Recorded, not refused**: any other browser automation on the machine. W29
# and W30's scripts folded a bare `playwright` into the refusal pattern, which
# on a shared machine also matches an unrelated `playwright-cli` daemon that no
# capture of this bed will ever touch. Refusing on it makes a foreign session's
# idle browser a hard stop on evidence; ignoring it silently would hide a real
# contender. So it is read, named in `browser-runs.txt`, and left for the
# reproduction check to referee — which is the instrument that would actually
# see contention, cell by cell, against the committed rows.
if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference' > /dev/null; then
  echo "scratch-capture: another calibration capture is running (X6)" >&2
  exit 1
fi
# 2026-09-21, the review closure (claims §5.161 §11, finding N8): this line read
# `pgrep -fc`, which BSD `pgrep` does not have — macOS exits 2 with a usage
# message and `|| true` swallows it, so `$FOREIGN` was empty and the three lines
# this wrote into `browser-runs.txt` carry no count at all. The count was
# therefore never recorded on the run that took the bed; the reproduction check
# refereed the condition instead, cell by cell, and found |Δ| 0 on all 552 macOS
# 27 cells. `browser-runs.txt` is left exactly as the run wrote it.
FOREIGN=$(pgrep -f 'playwright' | wc -l | tr -d ' ')
echo "foreign browser automation processes at start: $FOREIGN" | tee -a "$HERE/browser-runs.txt"
"$HERE/x6-read.sh" "w31-g0-scratch-$MODE" | tee -a "$HERE/browser-runs.txt"

# The chroma bed: every `photo` cell, every `mid-chroma-solid` cell and every
# tinted cell the declaration carries, in the union over all profiles. `compare`
# intersects `--scene` with `--set`, so a profile that declares none of a given
# scene simply plans nothing for it, and the four `recorded` poses drop out
# because `recorded` is never in `--set`.
SCENES="checkerboard-32__capsule-button__rest-tint-orange,checkerboard-4__capsule-button__rest-tint-orange,checkerboard-64__capsule-button__rest-tint-orange,checkerboard-8__capsule-button__rest-tint-orange,checkerboard__capsule-button__inactive-tint-blue,checkerboard__capsule-button__inactive-tint-orange,checkerboard__capsule-button__rest-tint-blue,checkerboard__capsule-button__rest-tint-orange,dark-solid__capsule-button__inactive-tint-blue,dark-solid__capsule-button__inactive-tint-orange,dark-solid__capsule-button__rest-tint-blue,dark-solid__capsule-button__rest-tint-orange,hc-text__capsule-button__inactive-tint-orange,hc-text__capsule-button__rest-tint-orange,impulse__capsule-button__inactive-tint-orange,impulse__capsule-button__rest-tint-orange,light-solid__capsule-button__inactive-tint-orange,light-solid__capsule-button__rest-tint-orange,mid-chroma-solid__capsule-button__inactive,mid-chroma-solid__capsule-button__inactive-tint-orange,mid-chroma-solid__capsule-button__rest,mid-chroma-solid__capsule-button__rest-tint-orange,mid-chroma-solid__rrect-lg__inactive,mid-chroma-solid__rrect-lg__rest,mid-chroma-solid__rrect-md__inactive,mid-chroma-solid__rrect-md__rest,photo__capsule-button__inactive,photo__capsule-button__inactive-tint-blue,photo__capsule-button__inactive-tint-orange,photo__capsule-button__inactive-tint-orange-half,photo__capsule-button__rest,photo__capsule-button__rest-tint-blue,photo__capsule-button__rest-tint-orange,photo__capsule-button__rest-tint-orange-half,photo__glass-over-glass__inactive,photo__glass-over-glass__rest,photo__rrect-lg__inactive,photo__rrect-lg__inactive-tint-orange,photo__rrect-lg__rest,photo__rrect-lg__rest-tint-orange,photo__rrect-md__inactive,photo__rrect-md__inactive-tint-orange,photo__rrect-md__rest,photo__rrect-md__rest-tint-orange,photo__rrect-ml__inactive,photo__rrect-ml__rest,photo__rrect-sm__inactive,photo__rrect-sm__rest,photo__toolbar-group__inactive,photo__toolbar-group__rest"
SETS=calibration,validation,holdout,probe

mkdir -p "$SCRATCH"

if [ "$MODE" = "27" ]; then
  LIGHT=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
  DARK=profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json
  LIGHT_RECEDED=profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json
  DARK_RECEDED=profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json
  PROFILES=(
    apple-macos-27.0-1x-light-standard-glass0.5
    apple-macos-27.0-2x-light-standard-glass0.5
    apple-macos-27.0-1x-dark-standard-glass0.5
    apple-macos-27.0-2x-dark-standard-glass0.5
    apple-macos-27.0-1x-light-reduced-transparency-glass0.5
    apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5
  )
  for profile in "${PROFILES[@]}"; do
    case "$profile" in
      *-dark-*) doc="$DARK"; receded="$DARK_RECEDED" ;;
      *)        doc="$LIGHT"; receded="$LIGHT_RECEDED" ;;
    esac
    for renderer in webgpu css; do
      echo "── $profile / $renderer ──"
      VITREA_WEB_CAPTURES="$SCRATCH" npx tsx cli/compare.ts \
        --profile "$profile" --material-profile "$doc" --receded-profile "$receded" \
        --renderer "$renderer" --alpha --write-partial \
        --set "$SETS" --scene "$SCENES" --out-matrix "$MATRIX"
    done
  done
else
  # A COPY of the frozen trees, so no macOS 26.5 path is opened for writing.
  CANONICAL="${VITREA_CANONICAL_CAPTURES:-$PWD/web-captures}"
  for profile in apple-macos-26.5-1x-light-standard apple-macos-26.5-2x-light-standard \
                 apple-macos-26.5-1x-dark-standard apple-macos-26.5-2x-dark-standard \
                 apple-macos-26.5-1x-light-reduced-transparency \
                 apple-macos-26.5-1x-light-increased-contrast; do
    [ -d "$CANONICAL/$profile" ] || { echo "scratch-capture: no canonical tree for $profile" >&2; exit 1; }
    mkdir -p "$SCRATCH/$profile"
    for cell in "$CANONICAL/$profile"/*; do
      name=$(basename "$cell")
      case "$name" in
        photo__*|mid-chroma-solid__*|*-tint-*) cp -R "$cell" "$SCRATCH/$profile/" ;;
      esac
    done
    for renderer in webgpu css; do
      echo "── $profile / $renderer (re-measure, no capture) ──"
      # `|| true`, and only on this branch. The canonical macOS 26.5 trees hold
      # the cells the macOS 26.5 bed was READ at, which is a subset of the chroma
      # scene list — `mid-chroma-solid`'s `rest` poses and several inactive ones
      # were never captured there. `compare` exits non-zero when a planned cell
      # has no capture under `--skip-capture`, which is right when a run is
      # supposed to produce a bed and wrong here, where the missing cells are a
      # fact about the frozen tree and X6 forbids capturing them. Every one is
      # named in the run log, and a cell with no row simply has no row.
      VITREA_WEB_CAPTURES="$SCRATCH" npx tsx cli/compare.ts \
        --profile "$profile" --renderer "$renderer" --skip-capture --alpha --write-partial \
        --set "$SETS" --scene "$SCENES" --out-matrix "$MATRIX" || true
    done
  done
fi

echo "── closing machine read ──"
"$HERE/x6-read.sh" "w31-g0-scratch-$MODE-close" | tee -a "$HERE/browser-runs.txt"
