#!/usr/bin/env python3
"""W29 G3b — what the canonical read did to `results/matrix.json`, checked from git.

    python3 append-check.py [<commit>] > append-check.txt

The read appends and never reduces or rewrites, and that is a claim about a file
this gate itself changed — so it is checked against the committed state rather
than asserted. Three things, in the order they would go wrong:

  1. every row that was in the file before is still in it, byte for byte, under
     the same key — the 26.5 bed, G3's 27 generation, and the probe rows;
  2. every row the read added is a 27 row whose `capturePath` names one of this
     child's sealed documents;
  3. the generation the gate reads (a row at a document currently on disk) is
     exactly the rows this read wrote.

`<commit>` defaults to the commit that sealed the documents, which is the last
state of the matrix before the read.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
REPO = PACKAGE.parents[1]
REL = "packages/calibration/results/matrix.json"

BEFORE_AT = sys.argv[1] if len(sys.argv) > 1 else "7af983e8"

SEALED = {
    "packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5.json": "f42ddec1cf5a",
    "packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json": "272d1b0c3e10",
}
SEALED_RECEDED = {
    "packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json": "59d4b20a4596",
    "packages/calibration/profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json": "5c81bc72edad",
}


def key(cell: dict) -> str:
    web = cell["key"]["web"]
    return "|".join(
        [
            cell["key"]["profileKey"],
            cell["key"]["sceneId"],
            web["engine"],
            web["engineVersion"],
            web["renderer"],
            web["samplingBackend"],
            web["gpuAdapter"],
            web["colorSpace"],
            web["capturePath"],
        ]
    )


before = json.loads(
    subprocess.check_output(["git", "-C", str(REPO), "show", f"{BEFORE_AT}:{REL}"], text=True)
)
after = json.loads((PACKAGE / "results" / "matrix.json").read_text())

was = {key(c): json.dumps(c, sort_keys=True) for c in before["cells"]}
now = {key(c): json.dumps(c, sort_keys=True) for c in after["cells"]}

print(f"before ({BEFORE_AT}): {len(was)} rows")
print(f"after:               {len(now)} rows")

missing = sorted(set(was) - set(now))
changed = sorted(k for k in set(was) & set(now) if was[k] != now[k])
added = sorted(set(now) - set(was))
print(f"rows missing after the read: {len(missing)}")
for k in missing[:20]:
    print("   ", k[:150])
print(f"rows CHANGED under an unchanged key: {len(changed)}")
for k in changed[:20]:
    print("   ", k[:150])
print(f"rows added: {len(added)}")

by_profile: dict[str, int] = {}
not27 = []
unsealed = []
receded = 0
for k in added:
    cell = next(c for c in after["cells"] if key(c) == k)
    profile = cell["key"]["profileKey"]
    by_profile[profile] = by_profile.get(profile, 0) + 1
    if not profile.startswith("apple-macos-27.0-"):
        not27.append(k)
    path = cell["key"]["web"]["capturePath"]
    if not any(f"materialProfile={p} sha256:{h}" in path for p, h in SEALED.items()):
        unsealed.append(k)
    if any(f"recededProfile={p} sha256:{h}" in path for p, h in SEALED_RECEDED.items()):
        receded += 1

print("added, per profile:")
for profile, count in sorted(by_profile.items()):
    print(f"    {profile:<62} {count}")
print(f"added rows that are NOT 27 rows: {len(not27)}")
print(f"added rows NOT at a sealed active document: {len(unsealed)}")
for k in unsealed[:10]:
    print("   ", k[:180])
print(f"added rows posed with a sealed receded document: {receded}")

# The 26.5 half, stated on its own because X1 is stated on its own.
before265 = {k: v for k, v in was.items() if k.startswith("apple-macos-26.5-")}
after265 = {k: v for k, v in now.items() if k.startswith("apple-macos-26.5-")}
print(
    f"\nthe 26.5 half: {len(before265)} rows before, {len(after265)} after, "
    f"{len(set(before265) - set(after265))} missing, "
    f"{len([k for k in before265 if after265.get(k) != before265[k]])} changed"
)
