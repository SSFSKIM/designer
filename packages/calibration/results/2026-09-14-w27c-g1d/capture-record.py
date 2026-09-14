#!/usr/bin/env python3
"""Record and verify Decision Log 18's two seven-run native sittings."""
from collections import Counter
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
SITTING = os.environ.get("VITREA_SITTING_ROOT", "/Users/new/vitrea-w27c-g1d-2026-09-14")
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")
EXPECTED_SCENES = [
    "mid-light-solid__capsule-button__inactive",
    "mid-light-solid__rrect-sm__inactive",
    "mid-light-solid__rrect-ml__inactive",
    "mid-light-solid__rrect-lg__inactive",
]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fixtures(manifest):
    return [
        (profile["profileKey"], fixture)
        for profile in manifest["profiles"] for fixture in profile["fixtures"]
    ]


def main():
    published_manifest = os.path.join(FIXTURES, "manifest.json")
    published = {
        f"{profile}/{fixture['sceneId']}": fixture
        for profile, fixture in fixtures(json.load(open(published_manifest)))
    } if os.path.exists(published_manifest) else {}
    report = {
        "gate": "W27c G1d / claims §5.143 / W27 Decision Log 18",
        "sittingRoot": SITTING,
        "runsPerPass": 7,
        "passes": [],
    }
    ok = True
    for scale in (2, 1):
        name = f"inactive-{scale}x"
        profile = f"apple-macos-26.5-{scale}x-dark-standard"
        root = os.path.join(SITTING, name)
        per_run = []
        cell_hashes = {scene: [] for scene in EXPECTED_SCENES}
        for number in range(1, 8):
            run = f"run-{number}"
            run_root = os.path.join(root, run)
            manifest_path = os.path.join(run_root, "manifest.json")
            manifest = json.load(open(manifest_path))
            rows = fixtures(manifest)
            attested = []
            low_idle = []
            for row_profile, fixture in rows:
                presentation = fixture.get("presentation") or {}
                passed = (
                    row_profile == profile
                    and fixture["sceneId"] in EXPECTED_SCENES
                    and fixture.get("presentedActive") is False
                    and fixture.get("deterministic") is True
                    and fixture.get("materialRendered") is True
                    and presentation.get("declaredPose") == "inactive"
                    and presentation.get("observedPose") == "inactive"
                    and presentation.get("isKeyWindow") is False
                    and presentation.get("appIsActive") is False
                    and presentation.get("windowCanBecomeKey") is False
                    and presentation.get("activationPolicy") == "accessory"
                )
                if passed:
                    attested.append(fixture["sceneId"])
                if fixture.get("hidIdleSeconds", 45) < 45:
                    low_idle.append({
                        "scene": fixture["sceneId"],
                        "hidIdleSeconds": fixture["hidIdleSeconds"],
                    })
                path = os.path.join(run_root, fixture["file"])
                if row_profile == profile and fixture["sceneId"] in cell_hashes:
                    cell_hashes[fixture["sceneId"]].append(sha(path))
            times = sorted(fixture["capturedAt"] for _, fixture in rows)
            item = {
                "run": run,
                "manifestSha256": sha(manifest_path),
                "cells": len(rows),
                "attested": len(attested),
                "firstCapture": times[0] if times else None,
                "lastCapture": times[-1] if times else None,
                "minHidIdleSeconds": min((f.get("hidIdleSeconds", 0) for _, f in rows), default=None),
                "cellsUnder45SecondsIdle": low_idle,
                "osVersion": manifest["hardware"]["osVersion"],
                "osBuild": manifest["hardware"]["osBuild"],
                "requestedScale": manifest["profiles"][0]["display"]["requestedScale"],
                "actualBackingScale": manifest["profiles"][0]["display"]["actualBackingScale"],
            }
            item["holds"] = len(rows) == 4 and len(attested) == 4
            ok = ok and item["holds"]
            per_run.append(item)

        tally = {}
        for scene, hashes in cell_hashes.items():
            counts = Counter(hashes)
            digest, count = counts.most_common(1)[0]
            cell = f"{profile}/{scene}"
            pub = published.get(cell)
            published_sha = sha(os.path.join(FIXTURES, pub["file"])) if pub else None
            tally[cell] = {
                "runs": len(hashes),
                "distinctByteStates": len(counts),
                "agreementHistogram": dict(Counter(counts.values())),
                "pluralityRuns": count,
                "pluralitySha256": digest,
                "perRunSha256": dict(zip((f"run-{n}" for n in range(1, 8)), hashes)),
                "publishedSha256": published_sha,
                "publishedMatchesPlurality": published_sha == digest,
            }
            ok = ok and len(hashes) == 7 and count >= 4 and published_sha == digest
        report["passes"].append({
            "pass": name,
            "profile": profile,
            "runs": per_run,
            "cellTally": tally,
        })
    report["holds"] = ok
    with open(os.path.join(HERE, "capture-record.json"), "w") as handle:
        json.dump(report, handle, indent=1)
        handle.write("\n")
    for capture_pass in report["passes"]:
        print(capture_pass["pass"])
        for run in capture_pass["runs"]:
            print(f"  {run['run']}: {run['attested']}/{run['cells']} attested, "
                  f"min idle {run['minHidIdleSeconds']:.1f}s, {run['manifestSha256']}")
        for cell, tally in capture_pass["cellTally"].items():
            print(f"  {cell}: plurality {tally['pluralityRuns']}/7, "
                  f"published={tally['publishedMatchesPlurality']}")
    print("holds:", ok)
    return 0 if ok else 1


sys.exit(main())
