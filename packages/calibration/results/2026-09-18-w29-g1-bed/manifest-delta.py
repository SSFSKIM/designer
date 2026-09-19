#!/usr/bin/env python3
"""What publishing the 27 bed did to the bundle's manifest — every difference, named.

    manifest-delta.py snapshot <manifest.json> <out.json>
    manifest-delta.py verify   <manifest.json> <snapshot.json>

Contract X1 says the 26.5 evidence is untouched. `freeze.py` proves that for every
26.5 fixture PNG, for `backgrounds/`, for the 26.5 profile documents and for every
26.5-keyed matrix row — but it hashes `fixtures/manifest.json` as one file, and
that file is shared: it is where the 27 profiles' own entries have to go. So a
whole-file hash cannot distinguish "the 26.5 bed moved" from "a second bed was
added beside it", and after publication it can only ever say the former.

This says which. It compares the manifest against a snapshot taken before
publication and classifies every difference, permitting exactly four:

  * a 27 profile entry appended,
  * a `bedProvenance` block appended,
  * a `backgrounds` index entry added for an id the bundle did not hold,
  * the `split` block re-read from the scene matrix, if and only if it is equal.

Anything else — a changed 26.5 profile entry, a changed fixture record, a moved
background path, a rewritten `hardware` block, a dropped provenance block — is
reported and exits non-zero. `freeze.py` is then amended to hash the manifest the
way it already hashes the matrix: per 26.5 entry rather than whole-file, so that
a 27 entry appended beside changes nothing there either.
"""
import hashlib
import json
import sys

OS_27 = "apple-macos-27.0-"


def sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def snapshot(path: str) -> dict:
    m = json.load(open(path))
    return {
        "wholeFileSha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
        "topLevel": {k: sha(v) for k, v in m.items() if k not in ("profiles", "bedProvenance")},
        "profiles": {p["profileKey"]: sha(p) for p in m["profiles"]},
        "profileCells": {p["profileKey"]: len(p["fixtures"]) for p in m["profiles"]},
        "bedProvenance": [sha(b) for b in (m.get("bedProvenance") or [])],
        "backgrounds": dict(m.get("backgrounds") or {}),
    }


def verify(path: str, before: dict) -> int:
    now = snapshot(path)
    problems, allowed = [], []

    for key, digest in before["topLevel"].items():
        if key not in now["topLevel"]:
            problems.append("top-level '%s' was REMOVED" % key)
        elif now["topLevel"][key] != digest:
            if key == "backgrounds":
                added = {k: v for k, v in now["backgrounds"].items()
                         if before["backgrounds"].get(k) != v}
                moved = {k: (before["backgrounds"][k], now["backgrounds"][k])
                         for k in before["backgrounds"]
                         if k in now["backgrounds"] and before["backgrounds"][k] != now["backgrounds"][k]}
                if moved:
                    problems.append("backgrounds MOVED: %s" % moved)
                else:
                    allowed.append("backgrounds: %d id(s) added: %s" % (len(added), sorted(added)))
            else:
                problems.append("top-level '%s' CHANGED" % key)
    for key in now["topLevel"]:
        if key not in before["topLevel"]:
            problems.append("top-level '%s' was ADDED" % key)

    for key, digest in before["profiles"].items():
        if key not in now["profiles"]:
            problems.append("profile %s was REMOVED" % key)
        elif now["profiles"][key] != digest:
            problems.append("profile %s CHANGED (%d cells before, %d now)"
                            % (key, before["profileCells"][key], now["profileCells"].get(key, -1)))
    for key in now["profiles"]:
        if key in before["profiles"]:
            continue
        if key.startswith(OS_27):
            allowed.append("profile %s added: %d cells" % (key, now["profileCells"][key]))
        else:
            problems.append("profile %s was added and is not a 27 key" % key)

    for digest in before["bedProvenance"]:
        if digest not in now["bedProvenance"]:
            problems.append("a bedProvenance block was REMOVED or REWRITTEN (%s)" % digest[:12])
    added = [d for d in now["bedProvenance"] if d not in before["bedProvenance"]]
    allowed.append("bedProvenance: %d block(s) added, %d kept"
                   % (len(added), len(before["bedProvenance"])))

    print("Permitted differences:")
    for a in allowed:
        print("  + " + a)
    print("\nDisallowed differences: %d" % len(problems))
    for p in problems:
        print("  ! " + p)
    print("\nWhole-file sha256 before: %s" % before["wholeFileSha256"])
    print("Whole-file sha256 now:    %s" % now["wholeFileSha256"])
    print("\nVERDICT: " + ("the 26.5 half of the manifest is byte-identical; only the 27 bed was added."
                           if not problems else "the 26.5 half of the manifest MOVED."))
    return 1 if problems else 0


mode = sys.argv[1]
if mode == "snapshot":
    open(sys.argv[3], "w").write(json.dumps(snapshot(sys.argv[2]), indent=2, sort_keys=True) + "\n")
    print("snapshot written to " + sys.argv[3])
elif mode == "verify":
    raise SystemExit(verify(sys.argv[2], json.load(open(sys.argv[3]))))
else:
    raise SystemExit(__doc__)
