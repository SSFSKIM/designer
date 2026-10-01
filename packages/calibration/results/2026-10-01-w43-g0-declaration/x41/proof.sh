#!/usr/bin/env bash
# The X41 checker's red and green cases, run on a scratch copy of what it reads so that no
# committed byte is touched. Each case mutates one thing, runs `x41.ts verify`, prints the
# verdict beside the expected one, and restores the copy. Its output is recorded as proof.txt.
#
#   bash packages/calibration/results/2026-10-01-w43-g0-declaration/x41/proof.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../../.." && pwd)"
TSX="$ROOT/packages/calibration/node_modules/.bin/tsx"
SCRATCH="$(mktemp -d /tmp/x41-proof.XXXXXX)"
trap 'rm -rf "$SCRATCH"' EXIT

for d in apps/reference-apple/fixtures packages/calibration/profiles \
         packages/calibration/results/generations packages/platform-web/src \
         packages/calibration/results/2026-10-01-w43-g0-declaration/x41; do
  mkdir -p "$SCRATCH/$(dirname "$d")"
  cp -R "$ROOT/$d" "$SCRATCH/$d"
done
X="$SCRATCH/packages/calibration/results/2026-10-01-w43-g0-declaration/x41/x41.ts"
DOC="$SCRATCH/packages/platform-web/src/material-document.ts"
MAN="$SCRATCH/apps/reference-apple/fixtures/manifest.json"
IDX="$SCRATCH/packages/calibration/results/generations/index.json"

restore() { cp "$ROOT/$1" "$SCRATCH/$1"; }
fails=0
check() { # name expected(pass|fail)
  local got
  if "$TSX" "$X" verify >"$SCRATCH/out.txt" 2>&1; then got=pass; else got=fail; fi
  local mark=ok; [ "$got" = "$2" ] || { mark=WRONG; fails=$((fails + 1)); }
  printf '%-5s expected %-4s got %-4s  %s\n' "$mark" "$2" "$got" "$1"
  [ "$got" = fail ] && grep -E 'MISSING|NEW|PROJECTION|Error' "$SCRATCH/out.txt" | head -3 | sed 's/^/        /'
  return 0
}
py() { python3 - "$@"; }

check "unmodified" pass

# Decision Log 1's ruled readout: the one admitted change.
perl -0pi -e 's|(  name: "apple-macos-27.0-glass0.5",)|$1\n  glassTintAmount: 0.5,|' "$DOC"
check "glassTintAmount: 0.5 added at the document's top level" pass
restore packages/platform-web/src/material-document.ts
perl -0pi -e 's|(  name: "apple-macos-27.0-glass0.5",)|$1\n  glassTintAmount: 0.25,|' "$DOC"
check "glassTintAmount: 0.25 on the 0.5 document" fail
restore packages/platform-web/src/material-document.ts
perl -0pi -e 's|(profileKey: "apple-macos-27.0-1x-light-standard-glass0.5",)|$1\n      glassTintAmount: 0.5,|' "$DOC"
check "glassTintAmount: 0.5 on an endpoint rather than the document" fail
restore packages/platform-web/src/material-document.ts
perl -0pi -e 's|(  platform: "macOS 27.0",)|$1\n  note: "x",|' "$DOC"
check "any other field added to the document" fail
restore packages/platform-web/src/material-document.ts
perl -0pi -e 's|(patch: macos27LightMaterialProfile)|patch: { ...macos27LightMaterialProfile, liftAmplitude: 0.001 }|' "$DOC"
check "one patch leaf moved" fail
restore packages/platform-web/src/material-document.ts
perl -0pi -e 's|MACOS_27_RESOLVED_MATERIAL_SHA256\.recededDark|"0000000000000000"|' "$DOC"
check "one endpoint digest moved" fail
restore packages/platform-web/src/material-document.ts
perl -0pi -e 's|cssTierMapping: macos27CssTierMapping,|cssTierMapping: {},|' "$DOC"
check "the CSS mapping dropped" fail
restore packages/platform-web/src/material-document.ts
perl -0pi -e 's|DEFAULT_MATERIAL_PROFILE_DOCUMENT: GlassMaterialProfileDocument =\n  macos27MaterialProfileDocument;|DEFAULT_MATERIAL_PROFILE_DOCUMENT: GlassMaterialProfileDocument =\n  macos26MaterialProfileDocument;|' "$DOC"
check "the default document re-pointed" fail
restore packages/platform-web/src/material-document.ts

# Bytes.
F="apps/reference-apple/fixtures/apple-macos-27.0-2x-dark-standard-glass0.5/photo__rrect-md__rest.png"
printf '\0' >>"$SCRATCH/$F"
check "one byte appended to a 0.5 fixture" fail
restore "$F"
cp "$SCRATCH/$F" "$SCRATCH/apps/reference-apple/fixtures/apple-macos-27.0-2x-dark-standard-glass0.5/extra.png"
check "a file added to a 0.5 tree" fail
rm "$SCRATCH/apps/reference-apple/fixtures/apple-macos-27.0-2x-dark-standard-glass0.5/extra.png"
mkdir -p "$SCRATCH/apps/reference-apple/fixtures/apple-macos-27.0-2x-dark-standard-glass0.25"
cp "$SCRATCH/$F" "$SCRATCH/apps/reference-apple/fixtures/apple-macos-27.0-2x-dark-standard-glass0.25/"
check "a 0.25 tree added beside the 0.5 trees" pass
rm -r "$SCRATCH/apps/reference-apple/fixtures/apple-macos-27.0-2x-dark-standard-glass0.25"
printf ' ' >>"$SCRATCH/packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json"
check "one byte appended to a 0.5 profile document" fail
restore packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json
cp "$SCRATCH/packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5.json" \
   "$SCRATCH/packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.25.json"
check "a 0.25 profile document added" pass
rm "$SCRATCH/packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.25.json"
printf '\n' >>"$SCRATCH/packages/platform-web/src/macos27-profile.ts"
check "the generated module touched" fail
restore packages/platform-web/src/macos27-profile.ts
printf ' ' >>"$SCRATCH/packages/calibration/results/generations/85ad7f7e3e0d.json"
check "one byte appended to a 0.5 generation file" fail
restore packages/calibration/results/generations/85ad7f7e3e0d.json

# The fixtures manifest, by entry.
py "$MAN" <<'EOF'
import json, sys
p = sys.argv[1]; m = json.load(open(p))
e = json.loads(json.dumps(next(x for x in m["profiles"] if x["profileKey"] == "apple-macos-27.0-2x-light-standard-glass0.5")))
e["profileKey"] = e["profileKey"].replace("glass0.5", "glass0.25")
m["profiles"].append(e)
m["bedProvenance"].append({"profiles": ["apple-macos-27.0-2x-light-standard-glass0.25"], "runs": 7})
open(p, "w").write(json.dumps(m, indent=2) + "\n")
EOF
check "a 0.25 profile entry and its provenance block appended, file re-serialised" pass
restore apps/reference-apple/fixtures/manifest.json
py "$MAN" <<'EOF'
import json, sys
p = sys.argv[1]; m = json.load(open(p))
next(x for x in m["profiles"] if x["profileKey"] == "apple-macos-27.0-1x-dark-standard-glass0.5")["fixtures"].pop()
open(p, "w").write(json.dumps(m, indent=2) + "\n")
EOF
check "a fixture dropped from a 0.5 profile entry" fail
restore apps/reference-apple/fixtures/manifest.json
py "$MAN" <<'EOF'
import json, sys
p = sys.argv[1]; m = json.load(open(p))
m["bedProvenance"].append({"profiles": ["apple-macos-27.0-2x-light-standard-glass0.25", "apple-macos-27.0-2x-light-standard-glass0.5"], "runs": 7})
open(p, "w").write(json.dumps(m, indent=2) + "\n")
EOF
check "a provenance block naming 0.25 and 0.5 together" fail
restore apps/reference-apple/fixtures/manifest.json

# The generation index, by entry.
py "$IDX" <<'EOF'
import json, sys
p = sys.argv[1]; m = json.load(open(p))
m["files"]["aaaaaaaaaaaa.json"] = {"activeDocumentSha256": "aaaaaaaaaaaa", "documents": [{"path": "packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.25.json", "sha256": "aaaaaaaaaaaa"}], "rowCount": 1, "rowsByProfileKey": {"apple-macos-27.0-1x-light-standard-glass0.25": 1}, "bytes": 1, "sha256": "0" * 64, "status": "current"}
m["byDocumentSha256"]["aaaaaaaaaaaa"] = ["aaaaaaaaaaaa.json"]
m["currentByProfile"]["apple-macos-27.0-1x-light-standard-glass0.25"] = "aaaaaaaaaaaa.json"
open(p, "w").write(json.dumps(m, indent=2) + "\n")
EOF
check "a 0.25 generation indexed beside the 0.5 ones" pass
restore packages/calibration/results/generations/index.json
py "$IDX" <<'EOF'
import json, sys
p = sys.argv[1]; m = json.load(open(p))
m["files"]["0eac5b294cc2.json"]["status"] = "retired"
open(p, "w").write(json.dumps(m, indent=2) + "\n")
EOF
check "a 0.5 generation retired" fail
restore packages/calibration/results/generations/index.json
py "$IDX" <<'EOF'
import json, sys
p = sys.argv[1]; m = json.load(open(p))
m["currentByProfile"]["apple-macos-27.0-1x-light-standard-glass0.5"] = "0eac5b294cc2.json"
open(p, "w").write(json.dumps(m, indent=2) + "\n")
EOF
check "a 0.5 profile's current selection re-pointed" fail
restore packages/calibration/results/generations/index.json

check "restored" pass
echo "wrong verdicts: $fails"
[ "$fails" -eq 0 ]
