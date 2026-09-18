#!/bin/bash
# Where macOS 27's Show Borders is not — the reproducible form of a null field.
#
#   showborders-search.sh
#
# `machine.json` records `accessibility.showBorders: null`, and a null that nobody
# can reproduce is indistinguishable from a field somebody forgot to fill in. This
# is the search behind it: the accessibility domain's whole top-level key list, the
# global domain filtered to anything that could be it, and the 27 SDK's
# accessibility header. A later run that finds a key here turns the null into a
# reading; until then the attestation is the absence, not the setting.
set -uo pipefail

echo "== com.apple.universalaccess, every top-level key =="
python3 - <<'PY'
import plistlib, pathlib, subprocess
p = pathlib.Path.home() / "Library/Preferences/com.apple.universalaccess.plist"
raw = subprocess.run(["plutil", "-convert", "xml1", "-o", "-", str(p)],
                     capture_output=True).stdout
d = plistlib.loads(raw)
for k in sorted(d):
    v = d[k]
    kind = type(v).__name__
    print(f"  {k} ({kind})" if kind in ("dict", "list", "bytes") else f"  {k} = {v!r}")
print(f"  -- {len(d)} keys")
PY

echo
echo "== NSGlobalDomain, anything border/glass/tint/contrast/transparency shaped =="
defaults read -g 2>/dev/null | grep -iE 'border|glass|tint|contrast|transparen' | sed 's/^/  /'

echo
echo "== MacOSX27.sdk: accessibilityDisplayShould* =="
grep -n "accessibilityDisplayShould" \
  /Library/Developer/CommandLineTools/SDKs/MacOSX27.sdk/System/Library/Frameworks/AppKit.framework/Headers/NSAccessibility.h \
  | sed 's/^/  /'

echo
echo "== MacOSX27.sdk AppKit headers: showBorders / windowBorder =="
grep -rn -iE "showBorders|windowBorder|showWindowBorder" \
  /Library/Developer/CommandLineTools/SDKs/MacOSX27.sdk/System/Library/Frameworks/AppKit.framework/Headers/ \
  | sed 's/^/  /'
echo "  (no matches above means none)"
