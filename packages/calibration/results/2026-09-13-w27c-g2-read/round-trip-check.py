#!/usr/bin/env python3
"""W27c G2 read, step 1: prove the committed bundle survived publication.

`manifest-doctor` answers one question — does the manifest decode and re-encode
through the Swift types without losing a field — and it answers it about the file
as it stands. It cannot answer the question publication actually raises: did any
of the 455 entries the bundle already held MOVE. This does, by diffing every
pre-existing entry and every pre-existing PNG against the commit publication
started from, and it is the check the brief asks for beside the doctor's.

    python3 round-trip-check.py [BASE_COMMIT]      # default HEAD
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")
BASE = sys.argv[1] if len(sys.argv) > 1 else "HEAD"


def git_show(path):
    return subprocess.run(
        ["git", "-C", REPO, "show", f"{BASE}:{path}"],
        check=True, capture_output=True,
    ).stdout


def entries(manifest):
    out = {}
    for profile in manifest["profiles"]:
        for fixture in profile["fixtures"]:
            out[f"{profile['profileKey']}/{fixture['sceneId']}"] = fixture
    return out


def tracked_pngs():
    listing = subprocess.run(
        ["git", "-C", REPO, "ls-tree", "-r", "--name-only", BASE, "apps/reference-apple/fixtures/"],
        check=True, capture_output=True, text=True,
    ).stdout.split()
    return [p for p in listing if p.endswith(".png")]


def main():
    before = entries(json.loads(git_show("apps/reference-apple/fixtures/manifest.json")))
    after_doc = json.load(open(os.path.join(FIXTURES, "manifest.json")))
    after = entries(after_doc)

    lost = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    changed = sorted(k for k in before if k in after and before[k] != after[k])

    png_changed, png_lost = [], []
    for path in tracked_pngs():
        live = os.path.join(REPO, path)
        if not os.path.exists(live):
            png_lost.append(path)
            continue
        was = hashlib.sha256(git_show(path)).hexdigest()
        now = hashlib.sha256(open(live, "rb").read()).hexdigest()
        if was != now:
            png_changed.append(path)

    base_provenance = json.loads(git_show("apps/reference-apple/fixtures/manifest.json"))["bedProvenance"]
    kept = [p for p in base_provenance if p in after_doc["bedProvenance"]]

    report = {
        "gate": "W27c G2 read / claims §5.139",
        "base": subprocess.run(["git", "-C", REPO, "rev-parse", BASE],
                               check=True, capture_output=True, text=True).stdout.strip(),
        "entriesBefore": len(before),
        "entriesAfter": len(after),
        "entriesLost": lost,
        "entriesAdded": len(added),
        "addedCells": added,
        "preExistingEntriesChanged": changed,
        "preExistingPngsChanged": png_changed,
        "preExistingPngsLost": png_lost,
        "bedProvenanceBlocksBefore": len(base_provenance),
        "bedProvenanceBlocksAfter": len(after_doc["bedProvenance"]),
        "bedProvenanceBlocksKept": len(kept),
        "holds": not lost and not changed and not png_changed and not png_lost
                 and len(kept) == len(base_provenance),
    }
    with open(os.path.join(HERE, "round-trip.json"), "w") as handle:
        json.dump(report, handle, indent=1)
        handle.write("\n")
    print(json.dumps({k: v for k, v in report.items() if k != "addedCells"}, indent=1))
    return 0 if report["holds"] else 1


sys.exit(main())
