#!/usr/bin/env python3
"""W29 G3 — write the two macOS 27 profile documents from the fit's own numbers.

    python3 build-documents.py

Each 27 document is the corresponding 26.5 document's patch with this child's
fitted constants merged over it, plus its own provenance. It is written by a
script rather than by hand because a patch that "names every fitted constant" has
to inherit the whole named set from the document it supersedes, and a hand-copied
set of eighty keys is a set with a typo in it. `seal.ts` then resolves each patch
through the renderer and writes its `resolvedMaterialSha256`; nothing here
computes a digest.

The overrides below are the ONLY numbers this child chose. Every other key in the
document is the 26.5 value, unchanged and still named, which is what makes the
document readable as a difference.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROFILES = HERE.parent.parent / "profiles"

FIT = HERE / "fitted-constants.json"


def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for key, value in over.items():
        out[key] = deep_merge(out[key], value) if isinstance(value, dict) and isinstance(out.get(key), dict) else value
    return out


def build(source: str, target: str, spec: dict) -> None:
    base = json.loads((PROFILES / f"{source}.json").read_text())
    document: dict = {
        "$comment": spec["comment"],
        "profileKey": target,
        "schemaVersion": 1,
        "recordedAt": "2026-09-19",
        "recordedBy": "W29 G3",
        "colorSpace": "srgb",
        "supersedesDefaultsOf": "@vitrea/renderer-webgpu DEFAULT_MATERIAL_PROFILE",
        "supersedes": source,
        "resolvedMaterialSha256": "PENDING — written by seal.ts",
        "measurement": spec["measurement"],
        "patch": deep_merge(base["patch"], spec["patch"]),
        "entries": spec["entries"],
    }
    mapping = deep_merge(base.get("cssTierMapping", {}), spec.get("cssTierMapping", {}))
    if mapping:
        document["cssTierMapping"] = mapping
    (PROFILES / f"{target}.json").write_text(json.dumps(document, indent=2) + "\n")
    print(f"wrote {target}.json")


spec = json.loads(FIT.read_text())
for entry in spec["documents"]:
    build(entry["supersedes"], entry["profileKey"], entry)
