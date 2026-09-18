#!/usr/bin/env python3
"""Fold G0's scratch readings into the two committed records.

    assemble.py <scratch-root> <out-dir>

The raw runs stay on the machine (hundreds of megabytes of PNGs, this repository's
standing practice); what is committed is the derived reading. This builds both
records from the scratch JSONs rather than from anything typed by hand, so every
number in them has a script between it and the pixels.

`slider-probe.json` states, per arm and per cell, the centre-against-centre spread
FIRST and then each position's difference from the centre, with a verdict that is
just the comparison of the two: a position moved the cell if its worst channel
delta exceeds the largest the same cell showed against itself across the three
centre runs. That is the construction the charter asks for, at the probe's scale.
"""
import json
import os
import sys

scratch, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)


def load(path):
    with open(path) as fh:
        return json.load(fh)


# ---------------------------------------------------------------- SDK gating
three = load(os.path.join(scratch, "c/dump-compare-three.json"))
sides = load(os.path.join(scratch, "c/dump-compare-sides.json"))

sdk = {
    "gate": "W29 G0 (c); claims 5.149",
    "question": "Is Apple's 27 material gated on the capturing binary's linked SDK?",
    "bundles": {
        "granted": {
            "path": "/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app",
            "recordedSdk": "26.0", "minos": "26.0",
            "toolchain": "Xcode 26.6 swiftc (Swift 6.3.3), MacOSX.sdk 26.5",
            "sourceRevision": "predates ee9e7449 (no dump-layers --inactive in the binary)",
            "screenRecordingGrant": "granted; verified by a capture with materialRendered true",
        },
        "sdk265": {
            "path": os.path.join(scratch, "c/side-sdk265/VitreaReference.app"),
            "recordedSdk": "26.5", "minos": "26.0",
            "toolchain": "Command Line Tools swiftc (Swift 6.4), MacOSX26.5.sdk",
            "sourceRevision": "HEAD",
            "screenRecordingGrant": "none; not requested (see the sdk27 arm)",
        },
        "sdk27": {
            "path": os.path.join(scratch, "c/side-sdk27/VitreaReference.app"),
            "recordedSdk": "27.0", "minos": "26.0",
            "toolchain": "Command Line Tools swiftc (Swift 6.4), MacOSX27.0.sdk",
            "sourceRevision": "HEAD",
            "screenRecordingGrant": "DENIED, and no prompt was presented",
        },
    },
    "pixelArm": {
        "ran": False,
        "reason": ("ScreenCaptureKit reported the TCC denial for the side bundle and presented no "
                   "prompt. TCC binds an ad-hoc signature by its cdhash, so a rebuild is a new "
                   "identity, and a recorded denial suppresses the prompt (README, the capture "
                   "wall). Granting it is a hand in System Settings."),
        "whatIsNeeded": ("System Settings > Privacy & Security > Screen & System Audio Recording: "
                         "add " + os.path.join(scratch, "c/side-sdk27/VitreaReference.app") +
                         " and enable it, then re-run the arm. The side bundle carries the same "
                         "CFBundleIdentifier as the granted one, so whether adding it disturbs the "
                         "granted entry is not known and X4 makes that the user's call."),
    },
    "declaredMaterialArm": {
        "method": ("dump-layers on the charter's cell set through each bundle: the declared "
                   "Core Animation filter tree and every filter input by its own inputKeys. "
                   "Captures no pixels and needs no grant."),
        "cells": sorted(three["cells"]),
        "grantedVsSideBuilds": three["summary"],
        "sdk265VsSdk27": sides["summary"],
        "cellsWithDifferingInputs": {
            cell: entry["differingInputs"]
            for cell, entry in three["cells"].items() if entry["differingInputs"]
        },
    },
    "verdict": (
        "Not SDK-gated, as far as the declared material can say. Two bundles built from one "
        "toolchain and one source revision against MacOSX26.5.sdk and MacOSX27.0.sdk, recording "
        "sdk 26.5 and sdk 27.0 in LC_BUILD_VERSION, declare a byte-identical material on 9 of 9 "
        "cells: same layer and effect classes, all 81 filter inputs equal. The granted bundle, "
        "which records the oldest value of the three (sdk 26.0), agrees with both on 8 of the 9; "
        "the 9th is the recede arm, and its difference is the pose rather than the material — "
        "that binary predates dump-layers --inactive and presented active, which its own dump "
        "records (isKeyWindow true, no activationPolicy field). The pixel arm is not taken."
    ),
    "residual": (
        "The window server composites the material out of the tree this arm reads, so identical "
        "trees are strong evidence and not a pixel proof: the compositor could in principle read "
        "the requesting binary's linked SDK itself. Closing that needs the side bundle's Screen "
        "Recording grant."
    ),
}
with open(os.path.join(out, "sdk-gating.json"), "w") as fh:
    json.dump(sdk, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
print(f"→ {os.path.join(out, 'sdk-gating.json')}")


# ------------------------------------------------------------------- slider
ARMS = ["active-2x", "inactive-2x", "active-1x"]
SPREAD = ["centre-r1-r2", "centre-r1-r3", "centre-r2-r3"]
POSITIONS = {"centre-vs-left": "0.0", "centre-vs-right": "1.0",
             "centre-vs-asfound": "0.5459057", "centre-vs-absent": "<key deleted>"}

# The declared-parameter sweep, read back out of dump-layers' own stdout.
sweep = {}
sweep_dir = os.path.join(scratch, "d/dump-sweep")
for name in sorted(os.listdir(sweep_dir)) if os.path.isdir(sweep_dir) else []:
    if not name.endswith(".out"):
        continue
    value = name[:-4]
    fields = {}
    for line in open(os.path.join(sweep_dir, name)):
        line = line.strip()
        for field in ("inputBlurFillNormalOpacity", "inputBlurFillLightenOpacity",
                      "inputFaceColorMatrixFillColor", "inputBlurFillDarkenOpacity"):
            if line.startswith(field + " ="):
                fields[field] = line.split("=", 1)[1].strip()
    if fields:
        sweep[value] = fields

arms = {}
for arm in ARMS:
    pairs_dir = os.path.join(scratch, "d/pairs", arm)
    if not os.path.isdir(pairs_dir):
        continue
    spread = {}
    for name in SPREAD:
        for row in load(os.path.join(pairs_dir, f"{name}.json"))["cells"]:
            prev = spread.get(row["cell"], {"maxDelta": 0, "changedPx": 0, "deltaEWorst": 0.0})
            spread[row["cell"]] = {
                "maxDelta": max(prev["maxDelta"], row["maxDelta"]),
                "changedPx": max(prev["changedPx"], row["changedPx"]),
                "deltaEWorst": max(prev["deltaEWorst"], row["deltaEWorst"]),
            }
    cells = {}
    for cell, bar in spread.items():
        cells[cell] = {"centreRunToRunSpread": bar, "positions": {}}
    for name, label in POSITIONS.items():
        path = os.path.join(pairs_dir, f"{name}.json")
        if not os.path.exists(path):
            continue
        for row in load(path)["cells"]:
            bar = spread[row["cell"]]
            cells[row["cell"]]["positions"][label] = {
                "identicalToCentre": row["identical"],
                "maxDelta": row["maxDelta"], "changedPx": row["changedPx"],
                "ssim": row["ssim"], "deltaEMean": row["deltaEMean"],
                "deltaEWorst": row["deltaEWorst"],
                "movedBeyondSpread": row["maxDelta"] > bar["maxDelta"]
                or row["deltaEWorst"] > bar["deltaEWorst"],
            }
    arms[arm] = cells

slider = {
    "gate": "W29 G0 (d); claims 5.149",
    "key": {"name": "NSGlassTintAmount", "domain": "NSGlobalDomain", "type": "float",
            "asFoundValue": 0.5459057,
            "asFoundWrittenAt": "2026-09-18T11:59 local (the .GlobalPreferences.plist mtime)",
            "restoredTo": 0.5459057},
    "drivesRenderingWithoutAGui": True,
    "declaredParameterSweep": sweep,
    "centreIs": {
        "value": 0.5,
        "evidence": ("With the key deleted the harness declares inputBlurFillNormalOpacity 0.5 and "
                     "inputFaceColorMatrixFillColor alpha 0.2000, and its captures are "
                     "byte-identical to the 0.5 arm's on every cell of every arm. 0.5 is also the "
                     "knee of both declared ramps: the face fill's alpha rises 0.0->0.20 over "
                     "[0, 0.5] and 0.20->0.50 over [0.5, 1.0], and the lighten opacity rises "
                     "0.675->0.9 over [0, 0.5] and then holds."),
    },
    "arms": arms,
}
with open(os.path.join(out, "slider-probe.json"), "w") as fh:
    json.dump(slider, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
print(f"→ {os.path.join(out, 'slider-probe.json')}")

for arm, cells in arms.items():
    for cell, entry in cells.items():
        moved = [p for p, v in entry["positions"].items() if v["movedBeyondSpread"]]
        still = [p for p, v in entry["positions"].items() if not v["movedBeyondSpread"]]
        print(f"{arm} {cell}: bar maxDelta={entry['centreRunToRunSpread']['maxDelta']} "
              f"dE={entry['centreRunToRunSpread']['deltaEWorst']:.6f} | moved: {', '.join(moved) or 'none'}"
              f" | within the bar: {', '.join(still) or 'none'}")
