#!/usr/bin/env python3
"""W31 G3c — the verdict, REGENERABLE after the split (claims §5.164 §13).

    python3 verdict.py > verdict-closure.txt

W31 G3's `results/2026-09-21-w31-g3-chroma-fit/verdict.py` with the review's
finding N14 fixed, COPIED rather than edited on that directory's own convention:
nothing under `results/` is edited after commit, and G3's `verdict.txt` is the
reading it took. Three fixes, each of them a thing that file could not say:

**It can be run after the split.** G3's copy required the interval between the
read and the split, when `results/matrix.json` held both generations — run a
minute later it reported 726 rows after and **0** before, and every "before"
column as an em-dash, with no complaint. The superseded generation is not gone:
it is in `results/superseded/`, named by the ACTIVE document whose rows it
holds, with `index.json` mapping every document hash to its file. This copy
reads the working file AND every superseded file that index names, so the
verdict is regenerable from the committed tree at any later date. That is the
difference between a table and a reading.

**The shadow block is read from the shadow block.** G3's `show()` chose between
`perceptual` and `material` by the metric's name, so the three declared
EXPECTED-UNMOVED rows that live under `shadow` — `meanDepartureWeb` twice and
`falloffSigmaWeb` — printed "—" in all three columns. Three of the thirteen rows
of the table whose whole purpose is that a move there is a warning were blank,
and blank read as "unmoved". The block is resolved by where the metric actually
lives now, and a metric in no block is an ERROR rather than an em-dash.

**A declared row that does not exist says so.** One EXPECTED_UNMOVED entry named
`photo__capsule-button__rest-tint-orange-half` on a DARK profile, and that cell
exists on the two light standard profiles only (`scenes.json`). It printed
"—" beside twelve real readings. The entry is corrected to the light profile's
sibling pose, and every row the declaration names and the bed does not carry is
now printed as **ROW ABSENT** and counted in a line at the end.

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
SUPERSEDED = PACKAGE / "results/superseded"
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
    # 2026-09-21, W31 G3c (claims §5.164 §13, finding N14): the first of these
    # named the DARK profile, which carries no `-tint-orange-half` cell at all —
    # `scenes.json` declares the two half-strength scenes on the light standard
    # profiles only. It printed three em-dashes among twelve real readings. The
    # entry is the light profile's other POSE, which is the comparison the row
    # was for: half the body's change at both ends of the pose axis.
    ("texture", "calibration", "photo__capsule-button__inactive-tint-orange-half",
     "apple-macos-27.0-1x-light-standard-glass0.5", "tintDeltaLWeb", "s = 0.5"),
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


BLOCKS = ("perceptual", "material", "shadow", "coherence", "shape")


def block_of(cell: dict, metric: str) -> str | None:
    """Where this metric lives on THIS cell — asked, not guessed (finding N14).

    G3's copy inferred the block from the metric's name and had no branch for
    `shadow`, so every declared shadow row read as an em-dash. A metric present
    in no block returns None and the caller prints ROW ABSENT rather than a
    dash that reads as "unmoved".
    """
    for block in BLOCKS:
        if isinstance((cell.get(block) or {}).get(metric), dict):
            return block
    return None


def value(cell: dict, block: str | None, metric: str) -> float | None:
    if block is None:
        return None
    entry = (cell.get(block) or {}).get(metric)
    return entry["value"] if isinstance(entry, dict) else None


def main() -> int:
    hashes = {f"packages/calibration/profiles/{p.name}":
              hashlib.sha256(p.read_bytes()).hexdigest()[:12]
              for p in sorted((PACKAGE / "profiles").glob("*.json"))}
    # The working file plus every superseded generation `index.json` names. The
    # index is the tree's own map and is read rather than a glob, so a file
    # sitting in that directory unrecorded is not silently read as evidence.
    # The working file plus every superseded generation `index.json` names. The
    # index is the tree's own map and is read rather than a glob, so a file
    # sitting in that directory unrecorded is not silently read as evidence.
    #
    # **In `capturedAt` order, oldest first**, because more than one superseded
    # generation can hold the same cell key and the "before" column means the
    # generation this gate superseded — the most recent one — and not whichever
    # file happened to sort last by content hash. The working file is read
    # first and only supplies "after" rows, so the order below decides nothing
    # about it.
    sources = [MATRIX]
    index = SUPERSEDED / "index.json"
    if index.exists():
        named = json.loads(index.read_text())["files"]
        for name in sorted(named, key=lambda k: named[k]["capturedAt"]["last"]):
            path = SUPERSEDED / name
            if not path.exists():
                raise SystemExit(f"verdict: index.json names {name}, which is not on disk")
            sources.append(path)

    before: dict[tuple, dict] = {}
    after: dict[tuple, dict] = {}
    cells = []
    for path in sources:
        cells += json.loads(path.read_text())["cells"]
    for cell in cells:
        if not cell["key"]["profileKey"].startswith("apple-macos-27.0-"):
            continue
        clauses = CAPTURE.findall(cell["key"]["web"]["capturePath"])
        current = bool(clauses) and all(hashes.get(path) == sha for path, sha in clauses)
        key = (cell["tier"], cell.get("fixtureSet"), cell["key"]["sceneId"],
               cell["key"]["profileKey"])
        (after if current else before)[key] = cell

    print("W31 G3c — the verdict, before and after, regenerable after the split")
    print("=" * 108)
    for path in sources:
        print(f"  read  {path.relative_to(PACKAGE)}")
    print(f"  rows at the documents on disk (AFTER)      {len(after)}")
    print(f"  rows at the superseded documents (BEFORE)  {len(before)}")
    print(f"  keys present in both                       {len(set(before) & set(after))}")
    print()
    absent: list[str] = []

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
            if key not in before and key not in after:
                absent.append(f"{TIER.get(tier, tier)} {fixture_set} {scene} {profile} :: {metric}")
                print(f"  {TIER.get(tier, tier):<9}{fixture_set:<12}{scene:<40}{metric:<18}"
                      f"{bound:>9}{'ROW ABSENT':>33}")
                print(f"    {profile}   <- the bed carries no such cell")
                continue
            sample = after.get(key) or before[key]
            block = block_of(sample, metric)
            if block is None:
                absent.append(
                    f"{TIER.get(tier, tier)} {fixture_set} {scene} {profile} :: {metric} "
                    f"(no block carries it)")
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
            native = value(cell, block_of(cell, "interiorStdDevNative"), "interiorStdDevNative")
            web = value(cell, block_of(cell, "interiorStdDevWeb"), "interiorStdDevWeb")
            if native and web:
                print(f"  {label:<8}{scene:<40}native {native:.4f}  web {web:.4f}  "
                      f"ratio {web / native:.4f}   {note}")
    print()

    print("Every row that moved most, by metric — so a change nobody declared is as visible")
    print("-" * 108)
    moves: list[tuple[float, str]] = []
    for key in sorted(set(before) & set(after)):
        for _declared_block, metric in METRICS:
            was = value(before[key], block_of(before[key], metric), metric)
            now = value(after[key], block_of(after[key], metric), metric)
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
    print()
    print(f"  {len(absent)} declared row(s) the bed does not carry or no block holds "
          "(0 is what a correct declaration reads)")
    for line in absent:
        print(f"    ROW ABSENT  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
