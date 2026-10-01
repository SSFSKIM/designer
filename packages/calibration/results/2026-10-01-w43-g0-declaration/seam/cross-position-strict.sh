#!/usr/bin/env bash
# W43 G0 (f): one real stamped strict-mode cross-position row, and the refusal without the flag.
#
# No 0.25 fixture exists before G1a, so this builds a SCRATCH one: the shipped 0.5 light 1x
# photo__rrect-md__rest fixture filed under the key apple-macos-27.0-1x-light-standard-glass0.25,
# in a scratch fixture tree (VITREA_FIXTURES) beside a symlink to the committed backgrounds. The
# shipped 0.5 document is then read against it through strict mode: refused without
# --cross-position, stamped with it. Output: cross-position-strict.txt beside this file.
#
#   bash packages/calibration/results/2026-10-01-w43-g0-declaration/seam/cross-position-strict.sh
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PKG="$(cd "$HERE/../../.." && pwd)"
ROOT="$(cd "$PKG/../.." && pwd)"
WORK=/tmp/w43-g0-cross-strict
rm -rf "$WORK" && mkdir -p "$WORK/fixtures/apple-macos-27.0-1x-light-standard-glass0.25"
ln -s "$ROOT/apps/reference-apple/fixtures/backgrounds" "$WORK/fixtures/backgrounds"
cp "$ROOT/apps/reference-apple/fixtures/apple-macos-27.0-1x-light-standard-glass0.5/photo__rrect-md__rest.png" \
   "$WORK/fixtures/apple-macos-27.0-1x-light-standard-glass0.25/"
python3 - "$ROOT/apps/reference-apple/fixtures/manifest.json" "$WORK/fixtures/manifest.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
p = next(x for x in m["profiles"] if x["profileKey"] == "apple-macos-27.0-1x-light-standard-glass0.5")
p = json.loads(json.dumps(p))
p["profileKey"] = "apple-macos-27.0-1x-light-standard-glass0.25"
p["fixtures"] = [f for f in p["fixtures"] if f["sceneId"] == "photo__rrect-md__rest"]
for f in p["fixtures"]:
    f["file"] = f["file"].replace("-glass0.5/", "-glass0.25/")
m["profiles"] = [p]
m["bedProvenance"] = []
json.dump(m, open(sys.argv[2], "w"), indent=2)
EOF

ARGS=(--material-profile profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
      --profile apple-macos-27.0-1x-light-standard-glass0.25 --scene photo__rrect-md__rest
      --out-matrix "$WORK/matrix.json")
OUT="$HERE/cross-position-strict.txt"
{
  echo "W43 G0 (f) strict-mode cross-position, end to end, $(date -u +%FT%TZ)"
  echo "scratch fixture: the shipped 0.5 light 1x photo__rrect-md__rest PNG filed under -glass0.25"
  echo
  echo "\$ VITREA_FIXTURES=$WORK/fixtures VITREA_WEB_CAPTURES=$WORK/captures npx tsx cli/compare.ts ${ARGS[*]}"
  (cd "$PKG" && VITREA_FIXTURES="$WORK/fixtures" VITREA_WEB_CAPTURES="$WORK/captures" \
    npx tsx cli/compare.ts "${ARGS[@]}" > "$WORK/refused.log" 2>&1)
  status=$?
  tail -1 "$WORK/refused.log"
  echo "exit $status (matrix: $([ -e "$WORK/matrix.json" ] && echo written || echo not written); captures: $([ -e "$WORK/captures" ] && echo taken || echo none))"
  echo
  echo "\$ ... the same, with --cross-position"
  (cd "$PKG" && VITREA_FIXTURES="$WORK/fixtures" VITREA_WEB_CAPTURES="$WORK/captures" \
    npx tsx cli/compare.ts "${ARGS[@]}" --cross-position > "$WORK/compare.log" 2>&1)
  echo "exit $?"
  grep -E "CROSS-POSITION|adapter" "$WORK/compare.log"
  python3 - "$WORK/matrix.json" <<'EOF'
import json, sys
k = json.load(open(sys.argv[1]))["cells"][0]["key"]
print("row profileKey", k["profileKey"])
print("row renderer", k["web"]["renderer"], "adapter", k["web"]["gpuAdapter"])
print("row capturePath", k["web"]["capturePath"])
EOF
} > "$OUT"
cat "$OUT"
