#!/usr/bin/env bash
#
# W32 G1 — the pitch ladder this wave's reads name, in ONE place.
#
# W31 G3's `canonical-read.sh` carried the 45-scene list inline; this wave's
# rounds, its pre-fit bed and its canonical read must all name the SAME list or
# the round the fit converged on is not the bed the read landed, so the list is
# sourced by all three rather than copied into each.
#
# **The 45**: the seven ladder backdrops' whole scene set, every one declared
# `probe` in `apps/reference-apple/scenes.json`. Named here so the selection is
# legible and so `--set probe` cannot widen to the other 91 probe rows.
#
# **The ten Decision Log 1 (b) adds** — the probe INACTIVE scenes whose native
# fixtures have been on disk since the macOS 27 capture and which the web side
# has never been read for: four on `rrect-ml` (span 128, where the matrix
# carries no inactive row at all) and six on `rrect-lg` (span 160, beside the
# three checkerboard rungs already in the 45). `mid-light-solid` on either
# component has no fixture and is not named. This is a READ-SET decision: no
# scene changes set, the split does not move and the holdout is not touched.
#
# The charter counts NINE because `impulse__rrect-ml__inactive` has no shadow to
# read; it is named anyway, so that absence is a reading this wave records rather
# than a row it quietly never asked for.
#
# `check-ladder-fixtures.py` beside this file asserts, per profile directory,
# that every scene the profile DECLARES has its native fixture — the four
# standard profiles declare all ten and the two accessibility profiles declare
# three (`checkerboard__rrect-ml__inactive`, `light-solid__rrect-ml__inactive`,
# `hc-text__rrect-lg__inactive`). A declared scene with no fixture is a red.

LADDER_45="checkerboard-4__capsule-button__rest,checkerboard-4__capsule-button__rest-tint-orange,checkerboard-4__rrect-lg__rest,checkerboard-4__rrect-md__inactive,checkerboard-4__rrect-md__rest,checkerboard-4__rrect-ml__rest,checkerboard-4__rrect-sm__rest,checkerboard-8__capsule-button__rest,checkerboard-8__capsule-button__rest-tint-orange,checkerboard-8__rrect-lg__inactive,checkerboard-8__rrect-lg__rest,checkerboard-8__rrect-md__inactive,checkerboard-8__rrect-md__rest,checkerboard-8__rrect-ml__rest,checkerboard-8__rrect-sm__rest,checkerboard-32__capsule-button__rest,checkerboard-32__capsule-button__rest-tint-orange,checkerboard-32__rrect-lg__inactive,checkerboard-32__rrect-lg__rest,checkerboard-32__rrect-md__rest,checkerboard-32__rrect-ml__rest,checkerboard-32__rrect-sm__rest,checkerboard-64__capsule-button__rest,checkerboard-64__capsule-button__rest-tint-orange,checkerboard-64__rrect-lg__inactive,checkerboard-64__rrect-lg__rest,checkerboard-64__rrect-md__inactive,checkerboard-64__rrect-md__rest,checkerboard-64__rrect-ml__rest,checkerboard-64__rrect-sm__rest,checkerboard-lc16__capsule-button__inactive,checkerboard-lc16__capsule-button__rest,checkerboard-lc16__rrect-lg__rest,checkerboard-lc16__rrect-md__inactive,checkerboard-lc16__rrect-md__rest,checkerboard-lc16__rrect-ml__rest,checkerboard-lc16__rrect-sm__rest,hc-text-7__rrect-lg__rest,hc-text-7__rrect-md__inactive,hc-text-7__rrect-md__rest,hc-text-7__rrect-sm__rest,hc-text-28__rrect-lg__rest,hc-text-28__rrect-md__inactive,hc-text-28__rrect-md__rest,hc-text-28__rrect-sm__rest"

LADDER_W32="checkerboard__rrect-ml__inactive,impulse__rrect-ml__inactive,light-solid__rrect-ml__inactive,photo__rrect-ml__inactive,impulse__rrect-lg__inactive,dark-solid__rrect-lg__inactive,mid-dark-solid__rrect-lg__inactive,light-solid__rrect-lg__inactive,hc-text__rrect-lg__inactive,mid-chroma-solid__rrect-lg__inactive"

LADDER="$LADDER_45,$LADDER_W32"
