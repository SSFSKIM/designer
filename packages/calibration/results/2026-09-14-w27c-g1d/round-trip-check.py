#!/usr/bin/env python3
"""Prove Decision Log 18 publication added eight cells and rewrote no evidence."""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")
BASE = sys.argv[1] if len(sys.argv) > 1 else "582a145"
SCENES = [
    "mid-light-solid__capsule-button__inactive",
    "mid-light-solid__rrect-sm__inactive",
    "mid-light-solid__rrect-ml__inactive",
    "mid-light-solid__rrect-lg__inactive",
]
EXPECTED = sorted(
    f"apple-macos-26.5-{scale}x-dark-standard/{scene}"
    for scale in (1, 2) for scene in SCENES
)


def git_show(path):
    return subprocess.run(
        ["git", "-C", REPO, "show", f"{BASE}:{path}"],
        check=True, capture_output=True,
    ).stdout


def entries(manifest):
    return {
        f"{profile['profileKey']}/{fixture['sceneId']}": fixture
        for profile in manifest["profiles"] for fixture in profile["fixtures"]
    }


def tracked_pngs():
    listing = subprocess.run(
        ["git", "-C", REPO, "ls-tree", "-r", "--name-only", BASE,
         "apps/reference-apple/fixtures/"],
        check=True, capture_output=True, text=True,
    ).stdout.split()
    return [path for path in listing if path.endswith(".png")]


def main():
    before_doc = json.loads(git_show("apps/reference-apple/fixtures/manifest.json"))
    after_doc = json.load(open(os.path.join(FIXTURES, "manifest.json")))
    before, after = entries(before_doc), entries(after_doc)
    lost = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    changed = sorted(key for key in before if before[key] != after.get(key))

    png_changed, png_lost = [], []
    for path in tracked_pngs():
        live = os.path.join(REPO, path)
        if not os.path.exists(live):
            png_lost.append(path)
            continue
        if hashlib.sha256(git_show(path)).digest() != hashlib.sha256(open(live, "rb").read()).digest():
            png_changed.append(path)

    old_provenance = before_doc.get("bedProvenance", [])
    kept = [block for block in old_provenance if block in after_doc.get("bedProvenance", [])]
    report = {
        "gate": "W27c G1d / claims §5.143 / W27 Decision Log 18",
        "base": subprocess.run(
            ["git", "-C", REPO, "rev-parse", BASE], check=True,
            capture_output=True, text=True,
        ).stdout.strip(),
        "entriesBefore": len(before),
        "entriesAfter": len(after),
        "entriesLost": lost,
        "entriesAdded": len(added),
        "addedCells": added,
        "expectedAddedCells": EXPECTED,
        "preExistingEntriesChanged": changed,
        "preExistingPngsChanged": png_changed,
        "preExistingPngsLost": png_lost,
        "bedProvenanceBlocksBefore": len(old_provenance),
        "bedProvenanceBlocksAfter": len(after_doc.get("bedProvenance", [])),
        "bedProvenanceBlocksKept": len(kept),
    }
    report["holds"] = (
        not lost and not changed and not png_changed and not png_lost
        and added == EXPECTED and len(kept) == len(old_provenance)
    )
    with open(os.path.join(HERE, "round-trip.json"), "w") as handle:
        json.dump(report, handle, indent=1)
        handle.write("\n")
    print(json.dumps(report, indent=1))
    return 0 if report["holds"] else 1


sys.exit(main())
