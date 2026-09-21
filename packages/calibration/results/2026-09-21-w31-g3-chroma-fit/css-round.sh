#!/usr/bin/env bash
#
# W31 G3 — the CSS tier at the fitted retention, on scratch (Decision Log 2 (b)).
#
#   ./css-round.sh <label> <r-light-active> <r-light-receded> <r-dark-active> <r-dark-receded>
#
# `round.sh` beside this file renders the WebGPU tier, which is the fidelity
# target and what the objective is stated on. This one renders the CSS tier at
# the SAME candidate documents, because Decision Log 2 (b) keeps a derived term
# only if it adds REACH without moving the authored `saturate()` constants, and
# "adds reach" is a measurement on this tier and nowhere else.
#
# **What the comparison is, and why it needs only one run.** On the CSS tier
# `bodyChromaRetention` enters through exactly one path — the gain on
# `saturate()` in `cssOpticsFromSource` — and that gain is exactly 1 at the
# leaf's identity. So "this tier at the fitted retention WITHOUT the derived
# term" is the same pixels as "this tier at retention 0", which the pre-fit bed
# already holds. The before is `pre-fit-matrix.json`'s `dom` rows and the after
# is this run; nothing has to be rendered twice with the term disabled.
#
# Written as its own file rather than as a flag on `round.sh`, because that one
# is committed evidence of the rounds it drove and a committed script is not
# edited to do a second job.
set -euo pipefail
cd "$(dirname "$0")/../.."

HERE=results/2026-09-21-w31-g3-chroma-fit
LABEL="${1:?usage: css-round.sh <label> <rLA> <rLR> <rDA> <rDR>}"
RLA="${2:?}"; RLR="${3:?}"; RDA="${4:?}"; RDR="${5:?}"
SCRATCH="${VITREA_G3_SCRATCH:-/tmp/w31-g3-fit}"
DOCS="$SCRATCH/$LABEL/documents"
mkdir -p "$DOCS"

if pgrep -f 'compare.ts|sweep.ts|capture-web|VitreaReference' > /dev/null; then
  echo "css-round: another calibration capture is running (X6)" >&2
  exit 1
fi
"$HERE/x6-read.sh" "w31-g3-css-$LABEL" | tee -a "$HERE/browser-runs.txt"

make() {
  printf '{"patch":{"bodyChromaRetention":%s}}\n' "$3" > "$DOCS/$(basename "$1").over.json"
  python3 "$HERE/chroma-fit.py" doc "$1" "$2" "$DOCS/$(basename "$1").over.json" > /dev/null
}
L="$DOCS/light.json";  make "$L"  profiles/apple-macos-27.0-1x-light-standard-glass0.5.json "$RLA"
D="$DOCS/dark.json";   make "$D"  profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json  "$RDA"
LR="$DOCS/light-receded.json"
make "$LR" profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json "$RLR"
DR="$DOCS/dark-receded.json"
make "$DR" profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json "$RDR"

SCENES=$(python3 - "$HERE" <<'PY'
import importlib.util as u, sys
s = u.spec_from_file_location("cf", f"{sys.argv[1]}/chroma-fit.py")
m = u.module_from_spec(s); s.loader.exec_module(m)
print(m.BED_SCENES + "," + m.ANCHOR_SCENES)
PY
)

RUN="$SCRATCH/$LABEL"
mkdir -p "$RUN"
for profile in apple-macos-27.0-1x-light-standard-glass0.5 \
               apple-macos-27.0-2x-light-standard-glass0.5 \
               apple-macos-27.0-1x-dark-standard-glass0.5 \
               apple-macos-27.0-2x-dark-standard-glass0.5; do
  case "$profile" in
    *-dark-*) doc="$D"; receded="$DR" ;;
    *)        doc="$L"; receded="$LR" ;;
  esac
  echo "── $LABEL / $profile / css ──"
  VITREA_WEB_CAPTURES="$RUN/web-captures" npx tsx cli/compare.ts \
    --profile "$profile" --material-profile "$doc" --receded-profile "$receded" \
    --renderer css --alpha --write-partial \
    --set calibration,validation --scene "$SCENES" \
    --out-matrix "$RUN/$profile.css.json" > "$RUN/$profile.css.log" 2>&1 || true
  [ -f "$RUN/$profile.css.json" ] || { echo "css-round: $profile wrote no matrix" >&2; exit 1; }
done

echo "── closing machine read ──"
"$HERE/x6-read.sh" "w31-g3-css-$LABEL-close" | tee -a "$HERE/browser-runs.txt"
