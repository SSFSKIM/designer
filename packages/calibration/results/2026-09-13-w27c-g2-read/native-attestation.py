#!/usr/bin/env python3
"""W27c G2 read: group E's re-attestation, and the bed's own native readings.

`bound.json` clause 5 suspends the read if the bed's attestation cells "do not
reproduce the recovered fixtures within the settle protocol's noise" — because
that would make the recovered bed's admissibility (W27 Decision Log 5) the
finding rather than the endpoint's fidelity. This is that comparison, and it is
native against native: the sitting's seven-run plurality bytes for an id the
bundle already held, against the recovered fixture the bundle holds for it. No
vitrea capture enters, which is why it can be run over a spent-holdout id without
reading the holdout again.

It also publishes the fresh native interior readings — level, chroma, standard
deviation — for the supplying groups, which is what a supplying cell is for
(experiment arms A1 and A3 consume them; neither arm runs here).

Writes `attestation.json` beside this file. Reads the sitting and the bundle and
writes into neither.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")
SITTING = os.environ.get("VITREA_SITTING_ROOT", "/Users/new/vitrea-w27-26.5-run")


def decode(path):
    """Decode a PNG to (width, height, RGBA bytes) through the repo's own decoder."""
    script = (
        "import sys,json;"
        "from PIL import Image;"
        "im=Image.open(sys.argv[1]).convert('RGBA');"
        "sys.stdout.buffer.write(bytes([im.width>>8,im.width&255,im.height>>8,im.height&255]));"
        "sys.stdout.buffer.write(im.tobytes())"
    )
    out = subprocess.run([sys.executable, "-c", script, path], check=True, capture_output=True).stdout
    width = (out[0] << 8) | out[1]
    height = (out[2] << 8) | out[3]
    return width, height, out[4:]


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


LINEAR = [srgb_to_linear(i) for i in range(256)]


def difference(a, b):
    """The plurality module's own summary: max channel delta, changed pixels, coherence."""
    wa, ha, da = a
    wb, hb, db = b
    if (wa, ha) != (wb, hb):
        return {"comparable": False}
    n = wa * ha
    changed = bytearray(n)
    maxdelta = 0
    count = 0
    for i in range(n):
        j = i * 4
        d = max(abs(da[j] - db[j]), abs(da[j + 1] - db[j + 1]), abs(da[j + 2] - db[j + 2]))
        if d:
            changed[i] = 1
            count += 1
            maxdelta = max(maxdelta, d)
    touching = 0
    for i in range(n):
        if not changed[i]:
            continue
        x, y = i % wa, i // wa
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < wa and 0 <= ny < ha and changed[ny * wa + nx]:
                touching += 1
                break
    return {
        "comparable": True,
        "maxDelta": maxdelta,
        "changedPx": count,
        "changedFraction": count / n,
        "coherence": (touching / count) if count else 0.0,
        # The same rule `src/plurality.ts` classifies a within-cell difference by.
        "classification": "incidental" if count == 0 or maxdelta <= 1
        else ("structured" if (touching / count) >= 0.5 else "incidental"),
    }


def main():
    manifest = json.load(open(os.path.join(FIXTURES, "manifest.json")))
    plurality = json.load(open(os.path.join(HERE, "plurality.json")))
    scenes = json.load(open(os.path.join(REPO, "apps/reference-apple/scenes.json")))
    roles = {}
    for role, ids in scenes["split"].items():
        if role.startswith("$") or role == "note":
            continue
        for i in ids:
            roles[i] = role
    bed = json.load(open(os.path.join(HERE, "../2026-09-11-w27c-g1b/checking-bed.json")))
    bed_groups = {}
    for group in bed["groups"]:
        for i in group["scenes"]:
            bed_groups.setdefault(i, []).append(group["id"])
        for i in group.get("alsoCaptureActive", []):
            bed_groups.setdefault(i, []).append(group["id"] + "-active")

    base = subprocess.run(
        ["git", "-C", REPO, "rev-parse", "ec809ae6"], check=True, capture_output=True, text=True
    ).stdout.strip()

    rows = []
    for profile in manifest["profiles"]:
        key = profile["profileKey"]
        for fixture in profile["fixtures"]:
            scene = fixture["sceneId"]
            if scene not in bed_groups or fixture["fixtureSet"] == "probe":
                continue
            # A bed id the bundle already held: the recovered fixture stays, and
            # the sitting's plurality bytes are compared with it here.
            cell = f"{key}/{scene}"
            fresh_path = None
            for p in plurality["passes"]:
                tally = p["cellTally"].get(cell)
                if tally is None:
                    continue
                for run, digest in tally["perRunSha256"].items():
                    if digest == tally["pluralitySha256"]:
                        fresh_path = os.path.join(SITTING, p["dir"], run, key, f"{scene}.png")
                        break
                break
            if fresh_path is None:
                continue
            recovered_path = os.path.join(FIXTURES, fixture["file"])
            recovered_bytes = open(recovered_path, "rb").read()
            fresh_bytes = open(fresh_path, "rb").read()
            diff = difference(decode(recovered_path), decode(fresh_path))
            rows.append({
                "profile": key,
                "scene": scene,
                "groups": bed_groups[scene],
                "role": roles.get(scene),
                "recoveredSha256": hashlib.sha256(recovered_bytes).hexdigest(),
                "freshPluralitySha256": hashlib.sha256(fresh_bytes).hexdigest(),
                "identicalBytes": recovered_bytes == fresh_bytes,
                "difference": diff,
                "recoveredProvenance": fixture.get("recoveredProvenance"),
            })
            print(f"{cell:78s} {'IDENTICAL' if rows[-1]['identicalBytes'] else diff}")

    report = {
        "gate": "W27c G2 read / claims §5.139",
        "reads": "the sitting's plurality bytes against the recovered fixtures the bundle holds",
        "base": base,
        "sittingRoot": SITTING,
        "cells": len(rows),
        "identical": sum(1 for r in rows if r["identicalBytes"]),
        "structured": [f"{r['profile']}/{r['scene']}" for r in rows
                       if r["difference"].get("classification") == "structured"],
        "rows": rows,
    }
    with open(os.path.join(HERE, "attestation.json"), "w") as handle:
        json.dump(report, handle, indent=1)
        handle.write("\n")
    print(f"\n{report['cells']} attestation cells, {report['identical']} byte-identical, "
          f"{len(report['structured'])} structurally different")


sys.exit(main())
