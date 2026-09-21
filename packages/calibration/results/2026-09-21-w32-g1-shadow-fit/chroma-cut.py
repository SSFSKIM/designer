#!/usr/bin/env python3
"""W31 G4 — the chroma cut the adopted rows read (Decision Log 3 (a); claims §5.165 §1).

    python3 chroma-cut.py [--out chroma-cut.json]

W30 G0's `shadow-cut.json` is what `adopted-thresholds.test.ts`'s B1 reads, and
W31 G1's review closure found the hole in that shape: a cut committed at one gate
is a SNAPSHOT, so a row adopted against it asserts a bound over frozen numbers and
can never fail (claims §5.162 §9). This cut is regenerated at the gate that adopts
it — the ruling's own words — and the hole is closed by construction on the other
side too: the test **re-derives every figure below from `results/matrix.json` and
from the two superseded files named here, and refuses a cut that disagrees with
them**. So the cut is a readable record of what was adopted and never the only
copy of it; a later read that moves a row moves the test whether or not anybody
re-runs this script.

**The statistic** (claims §5.161 §7 (b), fitted at §5.164 §4):
`R = chromaStructureRatioWeb / chromaStructureRatioNative`, web against native on
the same cell and never against 1. Bed: the untinted `photo` cells of the four
macOS 27 standard profiles, both scales, `calibration` + `validation`, on the
**WebGPU tier** (`tier == "texture"`), the two poses separated because they draw
two different documents. The holdout is dropped twice over — by `fixtureSet` and
by the declared split read from `scenes.json` — and `withHoldout` records it.

**The structure reading beside it** is `interiorStdDevWeb` against the PRE-FIT
generation: the rows read at the macOS 27 documents before any retention was
fitted into them, which the split moved to `results/superseded/880ab1e31450.json`
(the dark pair) and `results/superseded/d0c389d70456.json` (the four light
profiles). Those rows carry no chroma field at all — the instrument entered the
schema with this wave (claims §5.164 §4, N15) — and they do carry
`interiorStdDevWeb`, which is the whole point: `R` is scale-free in the deviations
and is therefore equally blind to a body that loses chroma and structure together,
so without this second row `R` is not a sufficient statistic (§5.161 §7 (b)).

The pre-fit generation is resolved through `results/superseded/index.json` rather
than named by hand, and the resolution is asserted: the file a document hash maps
to has to be the one this script read it from.
"""
from __future__ import annotations

import datetime as _datetime
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
REPO = PACKAGE.parent.parent
SCENES = REPO / "apps/reference-apple/scenes.json"

#: The four macOS 27 STANDARD profiles, with the scheme and scale each reads at.
#: The two accessibility profiles are deliberately absent: they inherit the light
#: document and stand the retention down under their occlusion lift (W31 Decision
#: Log 3 (d), claims §5.164 §13), so their `R` is 0.20.0's and is not this row's.
PROFILES = {
    "apple-macos-27.0-1x-light-standard-glass0.5": ("light", 1),
    "apple-macos-27.0-2x-light-standard-glass0.5": ("light", 2),
    "apple-macos-27.0-1x-dark-standard-glass0.5": ("dark", 1),
    "apple-macos-27.0-2x-dark-standard-glass0.5": ("dark", 2),
}

#: The pre-fit generation, by the ACTIVE document each was read at. Named here as
#: hashes and resolved through `superseded/index.json`, so a file renamed or a
#: generation moved again is a refusal rather than a silently different baseline.
PRE_FIT_ACTIVE_DOCUMENTS = {
    "dark": "880ab1e31450",
    "light": "d0c389d70456",
}

MODE = (
    "R = chromaStructureRatioWeb / chromaStructureRatioNative, web against native on the "
    "same cell and never against 1; median per scheme and pose with a two-sided per-cell "
    "clause; structure read as interiorStdDevWeb against the pre-fit generation"
)


def shipped_document_hashes() -> dict[str, str]:
    """`scripts/material-profile-file.ts`'s construction — twelve hex of SHA-256."""
    return {
        f"packages/calibration/profiles/{path.name}": hashlib.sha256(path.read_bytes())
        .hexdigest()[:12]
        for path in sorted((PACKAGE / "profiles").glob("*.json"))
    }


def at_a_shipped_document(cell: dict, shipped: dict[str, str]) -> bool:
    """`adopted-thresholds.test.ts`'s own predicate, restated over every named document.

    The test's version reads the FIRST `materialProfile=` clause; a macOS 27 row
    names a receded document too, and a cut that ignored it would read rows drawn
    by a recede nobody ships. Every named document has to be current here.
    """
    named = re.findall(
        r"(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})",
        cell["key"]["web"]["capturePath"],
    )
    if not named:
        return False
    return all(shipped.get(path) == digest for path, digest in named)


def bed_rows(cells: list[dict], shipped: dict[str, str]) -> dict[tuple[str, str], dict]:
    """The declared bed, keyed by (profileKey, sceneId)."""
    out: dict[tuple[str, str], dict] = {}
    for cell in cells:
        profile = cell["key"]["profileKey"]
        scheme_scale = PROFILES.get(profile)
        if scheme_scale is None:
            continue
        if cell["key"]["web"]["renderer"] != "webgpu":
            continue
        if cell.get("fixtureSet") not in ("calibration", "validation"):
            continue
        scene = cell["key"]["sceneId"]
        backdrop, _component, pose = (scene.split("__") + ["", ""])[:3]
        if backdrop != "photo" or "-tint-" in scene:
            continue
        if not at_a_shipped_document(cell, shipped):
            continue
        material = cell.get("material") or {}
        read = lambda field: (
            material[field]["value"] if isinstance(material.get(field), dict) else None
        )
        scheme, scale = scheme_scale
        out[(profile, scene)] = {
            "profile": profile,
            "scene": scene,
            "set": cell["fixtureSet"],
            "tier": cell["tier"],
            "scheme": scheme,
            "scale": scale,
            "pose": "inactive" if pose.startswith("inactive") else "active",
            "chromaStructureRatioNative": read("chromaStructureRatioNative"),
            "chromaStructureRatioWeb": read("chromaStructureRatioWeb"),
            "interiorStdDevWeb": read("interiorStdDevWeb"),
        }
    return out


def main(argv: list[str]) -> int:
    out_path = HERE / "chroma-cut.json"
    if "--out" in argv:
        out_path = Path(argv[argv.index("--out") + 1])

    shipped = shipped_document_hashes()
    matrix = json.loads((PACKAGE / "results" / "matrix.json").read_text())
    if matrix.get("schemaVersion") != 5:
        raise SystemExit(f"chroma-cut: matrix schema {matrix.get('schemaVersion')}, expected 5")
    current = bed_rows(matrix["cells"], shipped)

    index = json.loads((PACKAGE / "results" / "superseded" / "index.json").read_text())
    pre_fit: dict[tuple[str, str], dict] = {}
    pre_fit_files: dict[str, str] = {}
    for scheme, document in PRE_FIT_ACTIVE_DOCUMENTS.items():
        named = index["byDocumentSha256"].get(document)
        if named is None:
            raise SystemExit(f"chroma-cut: {document} is in no superseded file")
        pre_fit_files[scheme] = named
        path = PACKAGE / "results" / "superseded" / named
        cells = json.loads(path.read_text())["cells"]
        # The pre-fit rows were read at documents that are NOT shipped any more —
        # that is what makes them pre-fit — so the shipped-document guard is not
        # applied to them. What IS asserted is that every one of them names the
        # generation this script says it does.
        for cell in cells:
            profile = cell["key"]["profileKey"]
            if PROFILES.get(profile, (None, None))[0] != scheme:
                continue
            if cell["key"]["web"]["renderer"] != "webgpu":
                continue
            if cell.get("fixtureSet") not in ("calibration", "validation"):
                continue
            scene = cell["key"]["sceneId"]
            backdrop, _component, _pose = (scene.split("__") + ["", ""])[:3]
            if backdrop != "photo" or "-tint-" in scene:
                continue
            if f"sha256:{document}" not in cell["key"]["web"]["capturePath"]:
                raise SystemExit(f"chroma-cut: {named} holds a row not read at {document}")
            material = cell.get("material") or {}
            entry = material.get("interiorStdDevWeb")
            pre_fit[(profile, scene)] = {
                "interiorStdDevWeb": entry["value"] if isinstance(entry, dict) else None,
                "carriesChroma": "chromaStructureRatioWeb" in material,
            }

    holdout = frozenset(json.loads(SCENES.read_text())["split"]["holdout"])

    cells_out = []
    for key in sorted(current):
        row = dict(current[key])
        native = row["chromaStructureRatioNative"]
        web = row["chromaStructureRatioWeb"]
        if native is None or web is None:
            raise SystemExit(f"chroma-cut: {key} carries no chroma field")
        if row["scene"] in holdout:
            raise SystemExit(f"chroma-cut: {key} is a declared holdout scene (X4)")
        before = pre_fit.get(key)
        if before is None or before["interiorStdDevWeb"] is None:
            raise SystemExit(f"chroma-cut: {key} has no pre-fit interiorStdDevWeb")
        if before["carriesChroma"]:
            raise SystemExit(
                f"chroma-cut: {key}'s pre-fit row carries a chroma field — "
                "that generation is not pre-fit"
            )
        row["R"] = web / native
        row["interiorStdDevWebPreFit"] = before["interiorStdDevWeb"]
        row["structureDeltaFraction"] = (
            row["interiorStdDevWeb"] - before["interiorStdDevWeb"]
        ) / before["interiorStdDevWeb"]
        cells_out.append(row)

    beds: dict[str, dict] = {}
    for scheme in ("light", "dark"):
        for pose in ("active", "inactive"):
            group = [c for c in cells_out if c["scheme"] == scheme and c["pose"] == pose]
            if not group:
                continue
            values = [c["R"] for c in group]
            beds[f"{scheme}|{pose}"] = {
                "cells": len(group),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "worstStructureDeltaFraction": max(
                    abs(c["structureDeltaFraction"]) for c in group
                ),
            }

    cut = {
        "what": (
            "W31 G4's chroma cut: the declared bed's R and its structure reading, "
            "regenerated at the gate that adopts them (W31 Decision Log 3 (a))."
        ),
        "mode": MODE,
        "claims": "c9a §5.165 §1; declared at §5.161 §7 (b), fitted at §5.164 §4",
        "generatedAt": _datetime.datetime.now(_datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "atDocuments": "shipped",
        "withHoldout": False,
        "tier": "texture",
        "renderer": "webgpu",
        "sets": ["calibration", "validation"],
        "shippedDocuments": {
            path.split("/")[-1]: digest
            for path, digest in sorted(shipped.items())
            if "apple-macos-27.0-" in path
        },
        "preFitGeneration": {
            scheme: {
                "activeDocumentSha256": PRE_FIT_ACTIVE_DOCUMENTS[scheme],
                "file": pre_fit_files[scheme],
            }
            for scheme in PRE_FIT_ACTIVE_DOCUMENTS
        },
        "beds": beds,
        "cells": cells_out,
    }
    out_path.write_text(json.dumps(cut, indent=2) + "\n")

    print(f"# {cut['what']}")
    print(f"# mode: {MODE}")
    print(f"# at documents: {json.dumps(cut['shippedDocuments'])}")
    print(f"# pre-fit generation: {json.dumps(cut['preFitGeneration'])}")
    print(f"# holdout: {'READ' if cut['withHoldout'] else 'not read'}\n")
    print(f"{'bed':<18}{'n':>4}{'median R':>11}{'min R':>9}{'max R':>9}{'worst |Δsd|':>13}")
    for bed, figures in beds.items():
        print(
            f"{bed:<18}{figures['cells']:>4}{figures['median']:>11.4f}"
            f"{figures['min']:>9.4f}{figures['max']:>9.4f}"
            f"{figures['worstStructureDeltaFraction'] * 100:>12.3f}%"
        )
    print(f"\n{'profile':<52}{'scene':<32}{'set':<12}{'R':>9}{'Δsd':>10}")
    for row in sorted(cells_out, key=lambda c: -c["R"]):
        print(
            f"{row['profile']:<52}{row['scene']:<32}{row['set']:<12}"
            f"{row['R']:>9.4f}{row['structureDeltaFraction'] * 100:>9.3f}%"
        )
    print(f"\n{len(cells_out)} cells -> {out_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
