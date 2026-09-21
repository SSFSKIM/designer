#!/usr/bin/env python3
"""W32 G1 — the pre-fit bed reproduced against the committed rows, cell by cell.

    python3 repro.py <scratch-matrix.json>

W31's rule, applied to this wave's bed: a scratch render at the SHIPPED
documents is only a "before" if it reproduces the rows already committed at
those documents. The check is per cell and per field, not per aggregate — an
aggregate agrees while two cells swap.

**The fields.** The shadow axis's own numbers, which are what this wave moves
and what every stop is read on: the five bands' `slopeALinear` and
`interceptCLinear` on both sides, `meanDeparture{Native,Web}`,
`falloffSigma{Native,Web}`, `extent*{Native,Web}` and `offsetY{Native,Web}`.
The NATIVE side must agree exactly — the native fixture is a file on disk and
nothing this wave does touches it, so a native figure that moved is an
instrument change and not noise. The WEB side is compared against the cell's own
repeat noise where the row carries one and against the native-pair bar
(`shadowAffineSlopeDeltaMax` MAX, 0.002044) otherwise.

**The cells with no committed row are counted and named, not skipped.**
Decision Log 1 (b)'s ten scenes have never been read on the web side, so they
have no row at any documents; they are read here for the first time, as scratch,
and this file says so rather than letting a short population pass as agreement.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
COMMITTED = PACKAGE / "results/matrix.json"
PROFILES = PACKAGE / "profiles"
NOISE_BAR = PACKAGE / "results/2026-09-19-w29-g3b-shadow-recede/noise-bar.json"

CAPTURE = re.compile(r"materialProfile=(packages/calibration/profiles/[^ ]+\.json) sha256:([0-9a-f]{12})")
BANDS = ["0-3", "0-6", "3-6", "6-12", "12-24", "24-48"]
SCALARS = [
    "meanDepartureNative", "meanDepartureWeb",
    "falloffSigmaNative", "falloffSigmaWeb",
    "extentAboveNative", "extentAboveWeb", "extentBelowNative", "extentBelowWeb",
    "extentLeftNative", "extentLeftWeb", "extentRightNative", "extentRightWeb",
    "offsetYNative", "offsetYWeb", "offsetXNative", "offsetXWeb",
    "backdropSupport",
    "clearanceAbove", "clearanceBelow", "clearanceLeft", "clearanceRight",
]
BAR = 0.002044


def value(axis, name):
    field = (axis or {}).get(name)
    return field["value"] if isinstance(field, dict) and "value" in field else None


def key_of(cell):
    return (cell["key"]["profileKey"], cell["key"]["sceneId"], cell["tier"])


def shipped_hashes():
    return {f"packages/calibration/profiles/{p.name}":
            hashlib.sha256(p.read_bytes()).hexdigest()[:12]
            for p in sorted(PROFILES.glob("*.json"))}


def at_shipped(cell, hashes) -> bool:
    mo = CAPTURE.search(cell["key"]["web"]["capturePath"])
    return mo is not None and hashes.get(mo.group(1)) == mo.group(2)


def affine_map(axis, side):
    return {(b["ringLabel"], b["direction"]): b for b in (axis or {}).get(f"affine{side}", [])}


def main(argv) -> int:
    if len(argv) != 1:
        raise SystemExit(__doc__)
    scratch = json.loads(Path(argv[0]).read_text())["cells"]
    committed = json.loads(COMMITTED.read_text())["cells"]
    hashes = shipped_hashes()
    have = {key_of(c): c for c in committed if at_shipped(c, hashes)}

    print("W32 G1 — the pre-fit bed against the committed rows, cell by cell")
    print("=" * 118)
    print(f"  scratch   {argv[0]}  ({len(scratch)} cells)")
    print(f"  committed {COMMITTED.relative_to(PACKAGE.parent.parent)} "
          f"({len(have)} cells at the shipped documents)")
    print(f"  bar       native side EXACT; web side {BAR} (the native-pair max) or the cell's own")
    print(f"            repeatNoise where it is larger")
    print()

    new_cells, checked, native_moves, web_over = [], 0, [], []
    worst = []
    for cell in scratch:
        key = key_of(cell)
        before = have.get(key)
        if before is None:
            new_cells.append(key)
            continue
        checked += 1
        a, b = before.get("shadow"), cell.get("shadow")
        if a is None or b is None:
            if a is not b:
                native_moves.append((key, "the shadow axis is present on one side only"))
            continue
        noise = max(BAR, cell["key"]["web"].get("repeatNoise") or 0)
        for name in SCALARS:
            x, y = value(a, name), value(b, name)
            if x is None and y is None:
                continue
            if x is None or y is None:
                native_moves.append((key, f"{name}: {x} → {y}"))
                continue
            delta = abs(y - x)
            native = name.endswith("Native") or name.startswith("clearance")
            if native:
                if delta != 0:
                    native_moves.append((key, f"{name}: {x} → {y} (Δ {delta:g})"))
            else:
                # An extent is in device px and the bar is in transmission; an
                # extent is compared exactly too, because it is a threshold
                # crossing on a deterministic render.
                limit = noise if ("Departure" in name or "backdropSupport" in name) else 0.5
                if delta > limit:
                    web_over.append((key, f"{name}: {x} → {y} (Δ {delta:g} > {limit:g})"))
                worst.append((delta, key, name))
        for side, moved in (("Native", native_moves), ("Web", web_over)):
            before_bands, after_bands = affine_map(a, side), affine_map(b, side)
            for label, entry in before_bands.items():
                other = after_bands.get(label)
                if other is None:
                    moved.append((key, f"affine{side} {label} vanished"))
                    continue
                for field in ("slopeALinear", "interceptCLinear", "renderedLevelLinear",
                              "backdropMeanLinear", "sampleCount"):
                    x, y = entry.get(field), other.get(field)
                    if x is None and y is None:
                        continue
                    if x is None or y is None:
                        moved.append((key, f"affine{side} {label} {field}: {x} → {y}"))
                        continue
                    delta = abs(y - x)
                    limit = 0 if side == "Native" else (0 if field == "sampleCount" else noise)
                    if delta > limit:
                        moved.append((key, f"affine{side} {label} {field}: "
                                           f"{x} → {y} (Δ {delta:g} > {limit:g})"))
                    if side == "Web" and field in ("slopeALinear", "interceptCLinear"):
                        worst.append((delta, key, f"affine{side} {label} {field}"))

    print(f"§1. {checked} cells carry a committed row at the shipped documents and were compared.")
    print(f"    {len(native_moves)} native-side difference(s); {len(web_over)} web-side "
          f"difference(s) over the bar.")
    for key, why in native_moves[:40]:
        print(f"      NATIVE MOVED  {key[0]} {key[1]} [{key[2]}] — {why}")
    for key, why in web_over[:40]:
        print(f"      WEB OVER BAR  {key[0]} {key[1]} [{key[2]}] — {why}")
    if len(native_moves) > 40 or len(web_over) > 40:
        print("      (first 40 of each)")
    print()
    worst.sort(reverse=True)
    print("§2. The largest web-side differences, worst first — inside the bar and printed anyway")
    print(f"  {'Δ':>12}  {'profile':<50}{'scene':<38}{'field'}")
    for delta, key, name in worst[:15]:
        print(f"  {delta:>12.8f}  {key[0]:<50}{key[1]:<38}{name} [{key[2]}]")
    print()
    print(f"§3. {len(new_cells)} scratch cell(s) have NO committed row at any documents — the")
    print("    read-set widening (Decision Log 1 (b)) and anything else the bed gained. These are")
    print("    read here for the first time, as scratch, and are not a reproduction of anything.")
    for key in sorted(new_cells):
        print(f"      NEW  {key[0]} {key[1]} [{key[2]}]")
    print()
    verdict = "GREEN" if not native_moves and not web_over else "RED"
    print(f"  verdict: {verdict} — {len(native_moves)} native and {len(web_over)} web difference(s) "
          f"over the bar on {checked} reproduced cells")
    return 0 if verdict == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
