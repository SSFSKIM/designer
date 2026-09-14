#!/bin/sh
# W28 G4, step 2: the inactive pose enters the canonical matrix (claims §5.148).
#
# One `compare` invocation per profile per tier — `--renderer` is one tier and
# `--material-profile` is one document, which is the shape the canonical bed is
# always built in. The scene list is every inactive id the declaration puts in
# `calibration`, `validation` or `probe`; `holdout` and `recorded` are deliberately
# absent and the ledger says why. No split is changed, and no id is named in code:
# the list is generated from `scenes.json` by `inactive-scenes.py` and passed in.
#
# Captures land in the canonical `web-captures/` on this machine, beside the matrix
# they belong to. Every inactive scene is a directory that did not exist there, so
# no active capture is written; `capture-tree.py` records the tree before and after
# to prove it rather than assert it.
#
# The MATRIX goes to scratch, and `merge-matrix.py` folds it into the canonical file
# afterwards under a rule this script cannot enforce for itself: only new keys, and
# not one existing cell's bytes moved (X11).
set -e
here=$(cd "$(dirname "$0")" && pwd)
pkg=$(cd "$here/../.." && pwd)
out=${1:?scratch matrix directory}
captures=${2:?canonical capture root}
scenes=$(python3 "$here/inactive-scenes.py" --csv)

cd "$pkg"
mkdir -p "$out"
for profile in \
  apple-macos-26.5-1x-dark-standard \
  apple-macos-26.5-2x-dark-standard \
  apple-macos-26.5-1x-light-standard \
  apple-macos-26.5-2x-light-standard \
  apple-macos-26.5-1x-light-increased-contrast \
  apple-macos-26.5-1x-light-reduced-transparency
do
  case "$profile" in
    *dark*) doc=profiles/apple-macos-26.5-1x-dark-standard.json ;;
    *)      doc=profiles/apple-macos-26.5-1x-light-standard.json ;;
  esac
  # WebGPU first on every profile: the CSS run reads its texture twin off disk for
  # the coherence axis, so the order is what makes that axis exist at all.
  for renderer in webgpu css; do
    echo "══ $profile / $renderer"
    VITREA_WEB_CAPTURES="$captures" npx tsx cli/compare.ts \
      --profile "$profile" \
      --material-profile "$doc" \
      --renderer "$renderer" \
      --set calibration,validation,probe \
      --scene "$scenes" \
      --out-matrix "$out/inactive-matrix.json" \
      --write-partial
  done
done
