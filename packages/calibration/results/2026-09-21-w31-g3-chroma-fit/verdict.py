#!/usr/bin/env python3
"""W31 G3 — the verdict: every declared row, before and after, in one file.

    python3 verdict.py > verdict.txt

W30 G3's `results/2026-09-20-w30-g3-operators/verdict.py`, copied rather than
reused on that directory's own convention, with this wave's declarations in it.

Run BEFORE the split script moves the superseded generation out, because that is
the interval in which `results/matrix.json` holds both generations and the
before and the after are one read of one file rather than two reads of two.

**How "before" and "after" are told apart, without naming a hash.** Every cell's
`capturePath` carries the material profile documents it was captured at and the
first twelve hex of each document's own bytes. The four macOS 27 documents moved
twice in this branch — once when the digest rule landed and once when the chroma
retention was fitted into them — so a row captured at any earlier bytes names a
hash no file on disk has. "After" is the rows every one of whose documents is
current, which is exactly `atAShippedDocument`'s rule; "before" is the rest.
Nothing is transcribed and the pair cannot be swapped.

What it prints, in the order the declaration asks for it (claims §5.161 §4, §7
and `results/2026-09-21-w31-g0-chroma-cut/bounds-declaration.md`):

  (d) the four rows this wave CLAIMS — `photo__rrect-lg__rest :: oklabDeltaEP95`
      on both dark profiles and both tiers, every one of them a holdout row,
      claimed on a reachability floor of 0.0677-0.0730 against bounds of
      0.17-0.19;
  (e) the recede's worst cell, REPORTED and not claimed;
  (f) the rows declared EXPECTED UNMOVED — the shadow's, the scatter's, the
      structure and the rim — where a move is a warning and not a result, and
      the tinted cells, which are unmoved BY CONSTRUCTION at full strength
      because the tint's shade law reads a luminance the retention preserves;
  the chroma statistic itself, per profile per tier, so the operator's own
  reading is beside the rows it was supposed to move;
  then every row that moved by more than a declared row's own move, so a change
  nobody predicted is as visible as the ones that were.

The bounds themselves are never transcribed here: `test/adopted-thresholds.test.ts`
is the only copy the rule allows, and the pass/fail verdict against them is that
file's own run, recorded beside this one.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
MATRIX = PACKAGE / "results/matrix.json"
CAPTURE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")
TIER = {"texture": "webgpu", "dom": "css"}

# The rows the declaration names, each with what it is declared as. The bound is
# quoted from the declaration for legibility and is asserted nowhere here.
CLAIMED = [
    ("texture", "holdout", "photo__rrect-lg__rest",
     "apple-macos-27.0-1x-dark-standard-glass0.5", "oklabDeltaEP95", "≤ 0.17",
     "the body's chroma retention, WebGPU tier — floor 0.06971"),
    ("texture", "holdout", "photo__rrect-lg__rest",
     "apple-macos-27.0-2x-dark-standard-glass0.5", "oklabDeltaEP95", "≤ 0.17",
     "the body's chroma retention, WebGPU tier — floor 0.06772"),
    ("dom", "holdout", "photo__rrect-lg__rest",
     "apple-macos-27.0-1x-dark-standard-glass0.5", "oklabDeltaEP95", "≤ 0.18",
     "the retention through the CSS tier's saturate() gain — floor 0.07300"),
    ("dom", "holdout", "photo__rrect-lg__rest",
     "apple-macos-27.0-2x-dark-standard-glass0.5", "oklabDeltaEP95", "≤ 0.19",
     "the retention through the CSS tier's saturate() gain — floor 0.07065"),
]

EXPECTED_UNMOVED = [
    # The shadow's exterior — the retention acts inside the body composite and
    # reaches no exterior pixel, so a move here is a warning (§5.161 §7 (f)).
    ("texture", "calibration", "photo__rrect-md__rest",
     "apple-macos-27.0-1x-dark-standard-glass0.5", "meanDepartureWeb", "B3 0.00035"),
    ("texture", "calibration", "checkerboard__rrect-md__rest",
     "apple-macos-27.0-1x-light-standard-glass0.5", "meanDepartureWeb", "B3 0.00035"),
    ("texture", "calibration", "photo__rrect-md__rest",
     "apple-macos-27.0-1x-dark-standard-glass0.5", "falloffSigmaWeb", "the σ law"),
    # The structure — the stop is 2 % of the pre-fit value on any bed cell.
    ("texture", "calibration", "photo__rrect-md__rest",
     "apple-macos-27.0-1x-dark-standard-glass0.5", "interiorStdDevWeb", "±2 %"),
    ("texture", "calibration", "photo__capsule-button__rest",
     "apple-macos-27.0-1x-dark-standard-glass0.5", "interiorStdDevWeb", "±2 %"),
    ("texture", "calibration", "photo__rrect-md__rest",
     "apple-macos-27.0-1x-light-standard-glass0.5", "interiorStdDevWeb", "±2 %"),
    # The rim — its amplitude law reads a luminance the retention preserves.
    ("texture", "calibration", "photo__rrect-md__rest",
     "apple-macos-27.0-1x-dark-standard-glass0.5", "rimPeakLuminanceWeb", "the rim"),
    ("texture", "calibration", "photo__rrect-md__rest",
     "apple-macos-27.0-1x-light-standard-glass0.5", "rimPeakLuminanceWeb", "the rim"),
    # The tinted cells — unmoved BY CONSTRUCTION at s = 1, half the body's
    # change at `-tint-orange-half`, which is why both are here.
    ("texture", "calibration", "photo__capsule-button__rest-tint-orange",
     "apple-macos-27.0-1x-dark-standard-glass0.5", "tintDeltaLWeb", "s = 1"),
    ("texture", "calibration", "photo__capsule-button__rest-tint-orange",
     "apple-macos-27.0-1x-light-standard-glass0.5", "tintDeltaLWeb", "s = 1"),
    ("texture", "calibration", "photo__capsule-button__rest-tint-orange-half",
     "apple-macos-27.0-1x-dark-standard-glass0.5", "tintDeltaLWeb", "s = 0.5"),
    ("texture", "calibration", "photo__capsule-button__rest-tint-orange-half",
     "apple-macos-27.0-1x-light-standard-glass0.5", "tintDeltaLWeb", "s = 0.5"),
]

REPORTED = [
    ("texture", "apple-macos-27.0-1x-dark-standard-glass0.5",
     "photo__rrect-lg__inactive", "interiorStdDev",
     "the recede's worst cell (W29 §5.154 §8) — reported, not claimed"),
    ("texture", "apple-macos-27.0-2x-dark-standard-glass0.5",
     "photo__rrect-lg__inactive", "interiorStdDev",
     "the recede's worst cell at 2x — reported, not claimed"),
]

METRICS = [
    ("perceptual", "ssimMean"), ("perceptual", "ssimOutside"),
    ("perceptual", "oklabDeltaEMean"), ("perceptual", "oklabDeltaEP95"),
    ("material", "interiorMeanNative"), ("material", "interiorMeanWeb"),
    ("material", "interiorStdDevNative"), ("material", "interiorStdDevWeb"),
    ("material", "rimPeakLuminanceWeb"), ("material", "tintDeltaLWeb"),
    ("material", "chromaStructureRatioWeb"), ("material", "rawChromaRatioWeb"),
    ("shadow", "meanDepartureNative"), ("shadow", "meanDepartureWeb"),
    ("shadow", "falloffSigmaNative"), ("shadow", "falloffSigmaWeb"),
]


def value(cell: dict, block: str, metric: str) -> float | None:
    entry = (cell.get(block) or {}).get(metric)
    return entry["value"] if isinstance(entry, dict) else None


def main() -> int:
    hashes = {f"packages/calibration/profiles/{p.name}":
              hashlib.sha256(p.read_bytes()).hexdigest()[:12]
              for p in sorted((PACKAGE / "profiles").glob("*.json"))}
    before: dict[tuple, dict] = {}
    after: dict[tuple, dict] = {}
    for cell in json.loads(MATRIX.read_text())["cells"]:
        if not cell["key"]["profileKey"].startswith("apple-macos-27.0-"):
            continue
        clauses = CAPTURE.findall(cell["key"]["web"]["capturePath"])
        current = bool(clauses) and all(hashes.get(path) == sha for path, sha in clauses)
        key = (cell["tier"], cell.get("fixtureSet"), cell["key"]["sceneId"],
               cell["key"]["profileKey"])
        (after if current else before)[key] = cell

    print("W31 G3 — the verdict, before and after, from one read of results/matrix.json")
    print("=" * 108)
    print(f"  rows at the documents on disk (AFTER)      {len(after)}")
    print(f"  rows at the superseded documents (BEFORE)  {len(before)}")
    print(f"  keys present in both                       {len(set(before) & set(after))}")
    print()

    def show(title: str, rows, lever_column: bool) -> None:
        print(title)
        print("-" * 108)
        head = (f"  {'tier':<9}{'set':<12}{'scene':<40}{'metric':<18}"
                f"{'bound':>9}{'before':>11}{'after':>11}{'Δ':>11}")
        print(head)
        for entry in rows:
            tier, fixture_set, scene, profile, metric, bound = entry[:6]
            lever = entry[6] if lever_column and len(entry) > 6 else ""
            key = (tier, fixture_set, scene, profile)
            block = "perceptual" if metric.startswith(("ssim", "oklab")) else "material"
            was = value(before[key], block, metric) if key in before else None
            now = value(after[key], block, metric) if key in after else None
            print(f"  {TIER.get(tier, tier):<9}{fixture_set:<12}{scene:<40}{metric:<18}"
                  f"{bound:>9}"
                  f"{('—' if was is None else f'{was:.5f}'):>11}"
                  f"{('—' if now is None else f'{now:.5f}'):>11}"
                  f"{('—' if was is None or now is None else f'{now - was:+.5f}'):>11}")
            print(f"    {profile}" + (f"   lever: {lever}" if lever else ""))
        print()

    show("(d) The four rows this wave CLAIMS — every one a holdout row", CLAIMED, True)
    show("(f) The rows declared EXPECTED UNMOVED — a move is a warning, not a result",
         EXPECTED_UNMOVED, False)

    # The operator's own statistic, per profile per tier, beside the rows it was
    # supposed to move. Medians over the untinted `photo` cells of the declared
    # bed, which is where §5.161 §7 (b) states the tolerance.
    print("The chroma statistic itself — R = chromaStructureRatioWeb / …Native, "
          "median over the untinted photo cells")
    print("-" * 108)
    print(f"  {'tier':<9}{'profile':<52}{'pose':<10}{'n':>4}{'before':>11}{'after':>11}{'Δ':>11}")
    import statistics as _stats
    for tier in ("texture", "dom"):
        for profile in sorted({k[3] for k in set(before) | set(after)}):
            for pose in ("rest", "inactive"):
                def medians(table):
                    vals = []
                    for k, cell in table.items():
                        if k[0] != tier or k[3] != profile:
                            continue
                        scene = k[2]
                        if not scene.startswith("photo__") or "-tint-" in scene:
                            continue
                        if not scene.endswith(f"__{pose}"):
                            continue
                        n = value(cell, "material", "chromaStructureRatioNative")
                        w = value(cell, "material", "chromaStructureRatioWeb")
                        if n and w:
                            vals.append(w / n)
                    return vals
                was_vals, now_vals = medians(before), medians(after)
                if not now_vals:
                    continue
                was = _stats.median(was_vals) if was_vals else None
                now = _stats.median(now_vals)
                print(f"  {TIER.get(tier, tier):<9}{profile:<52}"
                      f"{('active' if pose == 'rest' else 'inactive'):<10}{len(now_vals):>4}"
                      f"{('—' if was is None else f'{was:.4f}'):>11}{now:>11.4f}"
                      f"{('—' if was is None else f'{now - was:+.4f}'):>11}")
    print()

    print("(d) The reported-not-claimed residual — the matrix instrument "
          "(the sheets' is read by eye)")
    print("-" * 108)
    for tier, profile, scene, _, note in REPORTED:
        key = (tier, "calibration", scene, profile)
        if key not in after:
            key = next((k for k in after if k[0] == tier and k[2] == scene and k[3] == profile),
                       None)
        if key is None:
            print(f"  {scene} at {profile}: no row")
            continue
        for label, table in (("before", before), ("after", after)):
            cell = table.get(key)
            if cell is None:
                continue
            native = value(cell, "material", "interiorStdDevNative")
            web = value(cell, "material", "interiorStdDevWeb")
            if native and web:
                print(f"  {label:<8}{scene:<40}native {native:.4f}  web {web:.4f}  "
                      f"ratio {web / native:.4f}   {note}")
    print()

    print("Every row that moved most, by metric — so a change nobody declared is as visible")
    print("-" * 108)
    moves: list[tuple[float, str]] = []
    for key in sorted(set(before) & set(after)):
        for block, metric in METRICS:
            was = value(before[key], block, metric)
            now = value(after[key], block, metric)
            if was is None or now is None:
                continue
            if metric.endswith("Native"):
                # A native reading is the fixture's and cannot move; a move here
                # is a measurement fault, not a result, so it is printed first.
                if abs(now - was) > 1e-9:
                    moves.append((1e6 + abs(now - was),
                                  f"NATIVE MOVED  {TIER.get(key[0], key[0])} {key[1]} {key[2]} "
                                  f"{key[3]} :: {metric} {was:.5f} -> {now:.5f}"))
                continue
            moves.append((abs(now - was),
                          f"{TIER.get(key[0], key[0]):<8}{key[1]:<12}{key[2]:<40}"
                          f"{metric:<22}{was:>10.5f}{now:>10.5f}{now - was:>+10.5f}  {key[3]}"))
    for _, line in sorted(moves, reverse=True)[:40]:
        print(f"  {line}")
    print()
    print(f"  {sum(1 for value_, _ in moves if value_ > 1e6)} native readings moved "
          "(any number here but 0 is a fault, not a result)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
