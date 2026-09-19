#!/usr/bin/env python3
"""Prove the freeze amendment loses nothing — W29 G1 Part B, claims §5.150.

`results/2026-09-16-w29-freeze/freeze.py` hashed `fixtures/manifest.json` as one
file. It now hashes it per unit, because the manifest is the file the 27 profiles'
entries have to go in and a whole-file hash cannot tell "the 26.5 bed moved" from
"a second bed was added beside it". An amendment to the instrument that proves X1
has to prove itself, so this checks three claims:

  1. Every line of the recorded list that is not about the manifest is unchanged —
     the 619 fixture PNGs, the 32 background rasters, the three 26.5 profile
     documents and the 1,107 canonical matrix rows.
  2. Every 26.5 unit inside the manifest still hashes to what it hashed to BEFORE
     the 27 bed was published. The before-state is `manifest-before.json`, the
     structural snapshot taken immediately before publication; it carries the same
     canonical digests, so the two are directly comparable.
  3. No 26.5 publication record was dropped or rewritten.

Re-runnable: it reads the committed snapshot rather than the git history, so it
keeps answering after the bed has been committed.
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FREEZE = ROOT / "packages/calibration/results/2026-09-16-w29-freeze"
sys.path.insert(0, str(FREEZE))
import freeze  # noqa: E402

sha, canon = freeze.sha, freeze.canon
before = json.loads((HERE / "manifest-before.json").read_text())
now_lines = list(freeze.entries())
recorded = (FREEZE / "sha256.txt").read_text().splitlines()

is_manifest = lambda line: (line.split("  ", 1)[1].startswith("manifest:")
                            or line.endswith("fixtures/manifest.json"))

# --- 1 -----------------------------------------------------------------------
a = [l for l in recorded if not is_manifest(l)]
b = [l for l in now_lines if not is_manifest(l)]
print("1. lines outside the manifest: recorded %d, now %d — %s"
      % (len(a), len(b), "IDENTICAL" if a == b else "DIFFER"))
for x in sorted(set(a) ^ set(b))[:6]:
    print("   !", x)

# --- 2 and 3 -----------------------------------------------------------------
now = {}
for line in now_lines:
    digest, name = line.split("  ", 1)
    if not name.startswith("manifest:"):
        continue
    now.setdefault(name, []).append(digest)

moved, lost = [], []


def check(name, expected):
    got = now.get(name)
    if got is None:
        lost.append(name)
    elif got != [expected]:
        moved.append(name)


for key, digest in before["topLevel"].items():
    if key == "backgrounds":
        continue
    check("manifest:" + key, digest)
for bid, path in before["backgrounds"].items():
    check("manifest:background:" + bid, sha(canon([bid, path])))
for key, digest in before["profiles"].items():
    if key.startswith("apple-macos-26.5-"):
        check("manifest:profile:" + key, digest)

kept = set(now.get("manifest:bedProvenance:26.5", []))
dropped = [d for d in before["bedProvenance"] if d not in kept]
extra = [d for d in kept if d not in before["bedProvenance"]]

print("\n2. 26.5 units inside the manifest: %d checked, %d moved, %d lost"
      % (len(before["topLevel"]) - 1 + len(before["backgrounds"])
         + sum(1 for k in before["profiles"] if k.startswith("apple-macos-26.5-")),
         len(moved), len(lost)))
for x in moved:
    print("   MOVED:", x)
for x in lost:
    print("   LOST: ", x)

print("\n3. 26.5 publication records: %d before, %d still hashed, dropped %s, unexpected %s"
      % (len(before["bedProvenance"]), len(kept), dropped or "none", extra or "none"))

print("\nThe whole-file hash this replaces, recorded rather than discarded:")
print("   %s  apps/reference-apple/fixtures/manifest.json" % before["wholeFileSha256"])

ok = a == b and not moved and not lost and not dropped and not extra
print("\nVERDICT: " + ("the amendment loses nothing — every unit the whole-file hash covered "
                       "about the 26.5 bed is still hashed, and still unchanged."
                       if ok else "THE AMENDMENT IS NOT SOUND."))
sys.exit(0 if ok else 1)
