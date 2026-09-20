#!/usr/bin/env python3
"""W30 G0 (c) — the structure cut: how much of the backdrop's own structure each
tier passes through the body, per pitch, per scheme, per tier, per span.

    python3 structure-cut.py > structure-cut.txt

The tracker's entry "the two tiers miss the backdrop's structure in opposite
directions" names this read as the precondition for chartering a scale-selective
scatter: `interiorStdDevDelta` is already in the matrix, so the cut is of
committed evidence rather than a capture (X2, X5).

**The quantity.** `material.interiorStdDevNative` and `…Web` are the standard
deviation of the body's own luminance over the component's interior, native and
vitrea, in the metric's units. The ratio W/N is what the operator has to move:
above 1 vitrea passes MORE of the backdrop's structure through the body than
Apple does, below 1 it passes less. `interiorStdDevBackdrop` is printed beside
them where it exists, because the two ratios to it are each tier's own
transmission and the ratio between them is free of Apple.

**Which rows.** The generation partition is `adopted-thresholds.test.ts`'s
`atAShippedDocument`, reproduced here on the same rule — the `capturePath` names
a profile document and a 12-hex content hash, and the row counts only if that
hash is the hash of the file on disk. The macOS 26.5 rows come through the same
gate, which is what makes the two materials comparable rather than merely
adjacent in one file.

**The discriminator the charter asks for.** A positive mix of two Gaussians is
monotone in frequency and its transfer is INDEPENDENT OF CONTRAST, because it is
linear. The bed carries `checkerboard` and `checkerboard-lc16` at the SAME 16 px
pitch and different contrast, and `hc-text` at three pitches beside the
checkerboard's five. So:

  - a ratio that varies with pitch and NOT with contrast at one pitch is
    consistent with a fixed non-monotone kernel — candidate (i), a second heavy
    tap at its own width with a signed weight;
  - a ratio that varies with CONTRAST at one pitch cannot come from any linear
    kernel applied to every source, and asks for a mix keyed on the source's own
    measured statistics — candidate (ii).

§5 runs that comparison.

**Two units, and §7 now prints both** (review closure, W30 Decision Log 3 (e)).
`interiorMean` is linear-light RELATIVE LUMINANCE, and §7 differenced it and
multiplied by 255 — which is a linear-luminance figure on a 0–255 scale, not the
8-bit code difference W25 G2's `fit-level.txt` states `resid` in. W25 encodes
each side to sRGB FIRST and differences the codes. Both columns are printed
side by side: the linear one is what the original cut recorded and is left
exactly as it read, the sRGB one is the quantity comparable to W25's `lever`
and `gain`.
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent

MATRIX = PACKAGE / "results/matrix.json"
DELTA = PACKAGE / "results/2026-09-19-w29-g3b-shadow-recede/native-delta.json"
PROFILES = PACKAGE / "profiles"
SCENES = ROOT / "apps/reference-apple/scenes.json"

CAPTURE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")

# Pitch in CSS px where the backdrop has one, ordered fine to coarse. `photo`
# and the solids have no single pitch and are printed after the ladder.
PITCH = {
    "checkerboard-4": 4,
    "checkerboard-8": 8,
    "checkerboard": 16,
    "checkerboard-lc16": 16,
    "checkerboard-32": 32,
    "checkerboard-64": 64,
    "hc-text-7": 7,
    "hc-text": 14,
    "hc-text-28": 28,
}
ORDER = ["checkerboard-4", "hc-text-7", "checkerboard-8", "hc-text", "checkerboard",
         "checkerboard-lc16", "hc-text-28", "checkerboard-32", "checkerboard-64",
         "photo", "light-solid", "mid-chroma-solid", "mid-dark-solid", "dark-solid", "impulse"]

TIER = {"texture": "webgpu", "dom": "css"}


def shipped_hashes() -> dict[str, str]:
    return {
        f"packages/calibration/profiles/{p.name}":
            hashlib.sha256(p.read_bytes()).hexdigest()[:12]
        for p in sorted(PROFILES.glob("*.json"))
    }


def spans_of(components: dict) -> dict[str, int]:
    out = {}
    for name, spec in components.items():
        kind = spec["kind"]
        if kind in ("capsule", "rrect"):
            out[name] = min(spec["size"])
        elif kind == "stack":
            out[name] = min(spec["base"]["size"])
        elif kind == "group":
            out[name] = min(min(item["size"]) for item in spec["items"])
    return out


def value(block: dict | None, name: str):
    entry = (block or {}).get(name)
    return entry["value"] if isinstance(entry, dict) else None


def median(values: list[float]) -> float:
    return sorted(values)[len(values) // 2]


def encode(value: float) -> float:
    """Linear-light relative luminance to an sRGB-encoded signal, W25's own curve.

    `results/2026-09-09-w25-thick-span-composite/g2/fit.py` encodes each side and
    then differences, which is what makes its `resid`, `lever` and `gain` 8-bit
    CODES. §7 below prints that beside the linear figure it originally recorded.
    """
    value = min(1.0, max(0.0, value))
    return value * 12.92 if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055


def bed_of(key: str) -> str:
    if key.startswith("apple-macos-26.5-"):
        return "26.5 " + key.removeprefix("apple-macos-26.5-").replace("-standard", "")
    return "27 " + key.removeprefix("apple-macos-27.0-").removesuffix("-glass0.5").replace(
        "-standard", "")


def main() -> int:
    hashes = shipped_hashes()
    span_of = spans_of(json.loads(SCENES.read_text())["components"])
    matrix = json.loads(MATRIX.read_text())

    rows = []
    # Two counts, not one. `generation` is every row of a generation that is at a
    # shipped document; `rows` is the subset that carries an interior-structure
    # reading. The two differ — a cell whose native spread is absent or zero
    # measures no structure — and §1b names which of them each figure is, because
    # a row count stated without that qualification reads as the generation's
    # (review closure, W30 Decision Log 3 (e)).
    generation: dict[tuple[str, str | None], int] = defaultdict(int)
    for cellular in matrix["cells"]:
        clause = CAPTURE.search(cellular["key"]["web"]["capturePath"])
        if clause is None or hashes.get(clause.group(1)) != clause.group(2):
            continue
        os_of = "26.5" if "26.5" in cellular["key"]["profileKey"] else "27"
        generation[(os_of, cellular.get("fixtureSet"))] += 1
        material = cellular.get("material")
        native = value(material, "interiorStdDevNative")
        web = value(material, "interiorStdDevWeb")
        if native is None or web is None or native <= 0:
            continue
        scene = cellular["key"]["sceneId"]
        parts = scene.split("__")
        if len(parts) < 2:
            continue
        rows.append({
            "bed": bed_of(cellular["key"]["profileKey"]),
            "profile": cellular["key"]["profileKey"],
            "os": "26.5" if "26.5" in cellular["key"]["profileKey"] else "27",
            "tier": TIER.get(cellular["tier"], cellular["tier"]),
            "pose": "inactive" if cellular.get("state") == "inactive"
                    or scene.endswith("__inactive") else "active",
            "set": cellular.get("fixtureSet"),
            "scene": scene,
            "backdrop": parts[0],
            "component": parts[1],
            "span": span_of.get(parts[1]),
            "tinted": "-tint-" in scene,
            "native": native,
            "web": web,
            "backdropSd": value(material, "interiorStdDevBackdrop"),
            "ratio": web / native,
            "interiorMeanNative": value(material, "interiorMeanNative"),
            "interiorMeanWeb": value(material, "interiorMeanWeb"),
        })

    print("W30 G0 (c) — the structure cut: interiorStdDev, vitrea against Apple, per pitch")
    print("=" * 112)
    print()
    print(f"Source: results/matrix.json, {len(rows)} rows at a shipped document with both")
    print("        interiorStdDev readings; the generation partition is atAShippedDocument's.")
    print("Ratio:  interiorStdDevWeb / interiorStdDevNative. >1 vitrea passes MORE of the")
    print("        backdrop's structure through the body than Apple does; <1 it passes less.")
    print()

    beds = sorted({r["bed"] for r in rows})
    print("§0. The partition")
    print("-" * 112)
    for bed in beds:
        for tier in ("webgpu", "css"):
            sel = [r for r in rows if r["bed"] == bed and r["tier"] == tier]
            if sel:
                act = sum(1 for r in sel if r["pose"] == "active")
                print(f"  {bed:<36}{tier:<8}{len(sel):>5} rows  ({act} active, {len(sel)-act} inactive)")
    print()

    def table(title: str, keep, beds_shown, spans=(44, 96, 128, 160)):
        print(title)
        print("-" * 112)
        for bed in beds_shown:
            for tier in ("webgpu", "css"):
                sel = [r for r in rows if r["bed"] == bed and r["tier"] == tier and keep(r)]
                if not sel:
                    continue
                print(f"  {bed} — {tier}")
                print(f"    {'backdrop':<20}{'pitch':>6}" +
                      "".join(f"{('span ' + str(s)):>26}" for s in spans))
                print(f"    {'':<20}{'':>6}" + "".join(f"{'N':>8}{'W':>8}{'W/N':>10}"
                                                       for _ in spans))
                for backdrop in ORDER:
                    line = f"    {backdrop:<20}{PITCH.get(backdrop, ''):>6}"
                    seen = False
                    for span in spans:
                        picked = [r for r in sel
                                  if r["backdrop"] == backdrop and r["span"] == span]
                        if not picked:
                            line += f"{'—':>26}"
                            continue
                        seen = True
                        line += (f"{median([r['native'] for r in picked]):>8.3f}"
                                 f"{median([r['web'] for r in picked]):>8.3f}"
                                 f"{median([r['ratio'] for r in picked]):>10.3f}")
                    if seen:
                        print(line)
                print()

    table("§1. macOS 27, ACTIVE — the bed the operator is fitted on",
          lambda r: r["os"] == "27" and r["pose"] == "active" and not r["tinted"],
          [b for b in beds if b.startswith("27 ")])

    print("§1b. The pitch ladder has NO macOS 27 web row in the committed matrix")
    print("-" * 112)
    SETS = ("calibration", "validation", "holdout", "probe")
    metric = defaultdict(int)
    for row in rows:
        metric[(row["os"], row["set"])] += 1
    print("  Every count here is COMPUTED from the file, and each is given twice: the")
    print("  generation's own rows at a shipped document, and the subset of them that")
    print("  carries an interior-structure reading (both interiorStdDev readings present,")
    print("  native > 0). Every per-pitch figure below is read on the second.")
    print()
    print(f"    {'generation':<14}" + "".join(f"{s:>26}" for s in SETS) + f"{'total':>16}")
    print(f"    {'':<14}" + "".join(f"{'rows':>13}{'w/ metric':>13}" for _ in SETS)
          + f"{'rows':>8}{'metric':>8}")
    for os_of in ("27", "26.5"):
        line = f"    {('macOS ' + os_of):<14}"
        for fixture_set in SETS:
            line += f"{generation[(os_of, fixture_set)]:>13}{metric[(os_of, fixture_set)]:>13}"
        line += (f"{sum(v for (o, _), v in generation.items() if o == os_of):>8}"
                 f"{sum(v for (o, _), v in metric.items() if o == os_of):>8}")
        print(line)
    print()
    print("  The canonical read is calibration + validation, then holdout. The pitch ladder is")
    print("  entirely `probe`, and probe has never been read at a macOS 27 document — the")
    print("  macOS 27 generation carries **zero probe rows**, against the macOS 26.5")
    print("  generation's own probe rows above. §5.153 §6's per-pitch figures were read off")
    print("  G3's SCRATCH matrices, which were never committed.")
    print()
    print("  So the macOS 27 per-pitch table does not exist in committed evidence and X2 says")
    print("  G0 does not capture one. What does exist is two halves that together say what the")
    print("  operator's shape has to be:")
    print("    §1c — vitrea's own transmission across the WHOLE ladder, at the macOS 26.5")
    print("          material, where the ladder was read (662 probe rows);")
    print("    §1d — Apple's own structure across the whole ladder on BOTH materials, from")
    print("          `native-delta.json`'s `readings.interiorStdDev`, which is native-only and")
    print("          therefore complete.")
    print()

    table("§1c. macOS 26.5, ACTIVE, the full pitch ladder — vitrea's own transmission curve",
          lambda r: r["os"] == "26.5" and r["pose"] == "active" and not r["tinted"],
          [b for b in beds if b.startswith("26.5 ")])

    print("§1d. Apple's own structure per pitch, macOS 26.5 against macOS 27")
    print("-" * 112)
    print("  `native-delta.json`'s `readings.interiorStdDev` is the [26.5, 27] pair of the")
    print("  reference's own body standard deviation on one cell. The backdrop raster is")
    print("  byte-identical across the two operating systems (W29 G1 Part B, 896 comparisons,")
    print("  zero disagreements), so the ratio 27/26.5 is Apple's own change in how much")
    print("  structure the material passes, per pitch, free of vitrea entirely — and it is the")
    print("  one quantity the whole ladder carries on both materials.")
    print()
    delta_rows = []
    for row in json.loads(DELTA.read_text())["rows"]:
        pair = (row.get("readings") or {}).get("interiorStdDev")
        if pair is None or row["pose"] != "active" or pair[0] in (None, 0):
            continue
        delta_rows.append({
            "bed": row["profileKey27"].removeprefix("apple-macos-27.0-")
                   .removesuffix("-glass0.5").replace("-standard", ""),
            "backdrop": row["background"],
            "span": span_of.get(row["component"]),
            "tinted": "-tint-" in row["sceneId"],
            "sd26": pair[0],
            "sd27": pair[1],
            "ratio": pair[1] / pair[0],
        })
    for bed in sorted({r["bed"] for r in delta_rows}):
        sel = [r for r in delta_rows if r["bed"] == bed and not r["tinted"]]
        if not sel:
            continue
        print(f"  {bed}")
        print(f"    {'backdrop':<20}{'pitch':>6}" +
              "".join(f"{('span ' + str(s)):>26}" for s in (44, 96, 128, 160)))
        print(f"    {'':<20}{'':>6}" +
              "".join(f"{'sd 26.5':>9}{'sd 27':>8}{'27/26.5':>9}" for _ in (44, 96, 128, 160)))
        for backdrop in ORDER:
            line = f"    {backdrop:<20}{PITCH.get(backdrop, ''):>6}"
            seen = False
            for span in (44, 96, 128, 160):
                picked = [r for r in sel if r["backdrop"] == backdrop and r["span"] == span]
                if not picked:
                    line += f"{'—':>26}"
                    continue
                seen = True
                line += (f"{median([r['sd26'] for r in picked]):>9.4f}"
                         f"{median([r['sd27'] for r in picked]):>8.4f}"
                         f"{median([r['ratio'] for r in picked]):>9.3f}")
            if seen:
                print(line)
        print()

    table("§2. macOS 27, INACTIVE — the receded pose, reported and fitted to nothing",
          lambda r: r["os"] == "27" and r["pose"] == "inactive" and not r["tinted"],
          [b for b in beds if b.startswith("27 ")])

    table("§3. macOS 26.5, INACTIVE — the frozen material's receded pose, for comparison",
          lambda r: r["os"] == "26.5" and r["pose"] == "inactive" and not r["tinted"],
          [b for b in beds if b.startswith("26.5 ")])

    print("§4. The scale comparison: 1x against 2x, macOS 27, active, WebGPU")
    print("-" * 112)
    print("  One scene id present on both scales of one scheme. `ratio` is W/N on each bed;")
    print("  the last column is the 2x ratio over the 1x one — a scatter that is right at one")
    print("  scale and wrong at the other shows here and nowhere else.")
    print()
    for scheme in ("light", "dark"):
        for tier in ("webgpu", "css"):
            one = {r["scene"]: r for r in rows if r["bed"] == f"27 1x-{scheme}"
                   and r["tier"] == tier and r["pose"] == "active" and not r["tinted"]}
            two = {r["scene"]: r for r in rows if r["bed"] == f"27 2x-{scheme}"
                   and r["tier"] == tier and r["pose"] == "active" and not r["tinted"]}
            # The scene id is the last key, so the order is a property of the data
            # rather than of the set's iteration order — which is hash-randomised
            # per process and made two runs of this cut differ in line order while
            # every figure agreed (review closure, W30 Decision Log 3 (e)).
            shared = sorted(set(one) & set(two),
                            key=lambda s: (PITCH.get(one[s]["backdrop"], 999),
                                           one[s]["span"] or 0, s))
            if not shared:
                continue
            print(f"  {scheme} — {tier}, {len(shared)} scenes")
            print(f"    {'scene':<44}{'pitch':>6}{'ratio 1x':>10}{'ratio 2x':>10}{'2x/1x':>9}")
            for scene in shared:
                a, b = one[scene], two[scene]
                print(f"    {scene:<44}{PITCH.get(a['backdrop'], ''):>6}"
                      f"{a['ratio']:>10.3f}{b['ratio']:>10.3f}{b['ratio'] / a['ratio']:>9.3f}")
            ratios = [two[s]["ratio"] / one[s]["ratio"] for s in shared]
            print(f"    2x/1x over {len(ratios)} scenes: median {median(ratios):.3f}, "
                  f"min {min(ratios):.3f}, max {max(ratios):.3f}")
            print()

    print("§5. The discriminator: same pitch, different contrast")
    print("-" * 112)
    print("  `checkerboard` and `checkerboard-lc16` are both a 16 px pitch. A LINEAR kernel —")
    print("  which a positive or signed mix of Gaussians is — has a transfer that does not")
    print("  depend on the backdrop's contrast, so candidate (i) predicts the SAME W/N ratio")
    print("  on the two. A mix keyed on the source's measured variance or edge density —")
    print("  candidate (ii) — does not, because the two sources have different statistics at")
    print("  the same scale.")
    print()
    print("  It can only be run on the macOS 26.5 generation: `checkerboard-lc16` is a probe")
    print("  fixture and the macOS 27 generation carries no probe row (§1b). `Tw` and `Tn` are")
    print("  each side's own transmission, sd(rendered) / sd(backdrop), which is what divides")
    print("  the other side out — `Tw`'s ratio is vitrea's contrast dependence alone.")
    print()
    print(f"  {'bed':<20}{'tier':<8}{'span':>5}{'ckbd W/N':>10}{'lc16 W/N':>10}{'ratio':>8}"
          f"{'ckbd Tw':>9}{'lc16 Tw':>9}{'ratio':>8}{'ckbd Tn':>9}{'lc16 Tn':>9}{'ratio':>8}")
    for bed in [b for b in beds if b.startswith("26.5 ")]:
        for tier in ("webgpu", "css"):
            for span in (44, 96, 128, 160):
                a = [r for r in rows if r["bed"] == bed and r["tier"] == tier and r["span"] == span
                     and r["backdrop"] == "checkerboard" and r["pose"] == "active"
                     and not r["tinted"]]
                b2 = [r for r in rows if r["bed"] == bed and r["tier"] == tier and r["span"] == span
                      and r["backdrop"] == "checkerboard-lc16" and r["pose"] == "active"
                      and not r["tinted"]]
                if not a or not b2:
                    continue
                ra = median([r["ratio"] for r in a])
                rb = median([r["ratio"] for r in b2])

                def transmission(picked: list[dict], side: str) -> float:
                    usable = [r[side] / r["backdropSd"] for r in picked if r["backdropSd"]]
                    return median(usable) if usable else float("nan")

                twa, twb = transmission(a, "web"), transmission(b2, "web")
                tna, tnb = transmission(a, "native"), transmission(b2, "native")
                print(f"  {bed:<20}{tier:<8}{span:>5}{ra:>10.3f}{rb:>10.3f}{rb / ra:>8.3f}"
                      f"{twa:>9.3f}{twb:>9.3f}{twb / twa:>8.3f}"
                      f"{tna:>9.3f}{tnb:>9.3f}{tnb / tna:>8.3f}")
    print()

    print("§6. The gated 16 px checkerboard cell, per §5.154 §9 (c) — recomputed, not copied")
    print("-" * 112)
    print("  The cell the tracker and the ledger both state the residual on:")
    print("  `checkerboard__rrect-md__rest`, active, macOS 27, at the shipped documents.")
    print()
    print(f"  {'bed':<20}{'tier':<8}{'native sd':>11}{'vitrea sd':>11}{'W/N':>8}")
    coherence = {}
    for bed in [b for b in beds if b.startswith("27 ")]:
        for tier in ("webgpu", "css"):
            sel = [r for r in rows if r["bed"] == bed and r["tier"] == tier
                   and r["scene"] == "checkerboard__rrect-md__rest"]
            if not sel:
                continue
            r = sel[0]
            coherence[f"{bed}|{tier}"] = {"native": r["native"], "web": r["web"],
                                          "ratio": r["ratio"], "profile": r["profile"]}
            print(f"  {bed:<20}{tier:<8}{r['native']:>11.4f}{r['web']:>11.4f}{r['ratio']:>8.4f}")
    print()

    print("§7. `sizeToneLevelFar`'s sign on the macOS 27 ladder, read the way W25 read it")
    print("-" * 112)
    print("  W25 G2's `fit-level.txt`: `resid` is native − web at the baseline, in 8-bit codes")
    print("  over the body; the constant is an OFFSET on the interior level reached at")
    print("  `sizeScatterSpanMax` and EXACTLY 0 at and below span 96, so the quantity it has")
    print("  to explain is `resid(160) − resid(96)` on one backdrop. A positive difference")
    print("  asks for a positive constant. W25 declined it because the per-row gains ran")
    print("  −1.13…+0.24 with the two grids disagreeing in sign.")
    print()
    print("  TWO UNITS, both printed (review closure, W30 Decision Log 3 (e)). `interiorMean`")
    print("  is linear-light relative luminance. The `linear x255` columns difference it and")
    print("  scale by 255, which is what this cut first recorded and is left untouched; the")
    print("  `sRGB code` columns encode each side to sRGB FIRST and difference the codes,")
    print("  which is W25's own `resid` and the only unit comparable to W25's `lever` and")
    print("  `gain`. The verdict is read on the sRGB columns and does not change: the sign is")
    print("  stable per scheme and the magnitude is not.")
    print()
    for bed in [b for b in beds if b.startswith("27 ")]:
        for tier in ("webgpu",):
            lines = []
            for backdrop in ORDER:
                at = {}
                for span in (96, 160):
                    sel = [r for r in rows if r["bed"] == bed and r["tier"] == tier
                           and r["backdrop"] == backdrop and r["span"] == span
                           and r["pose"] == "active" and not r["tinted"]
                           and r["interiorMeanNative"] is not None]
                    if sel:
                        at[span] = (
                            median([(r["interiorMeanNative"] - r["interiorMeanWeb"]) * 255
                                    for r in sel]),
                            median([(encode(r["interiorMeanNative"])
                                     - encode(r["interiorMeanWeb"])) * 255 for r in sel]),
                        )
                if 96 in at and 160 in at:
                    lines.append((backdrop, at[96], at[160]))
            if not lines:
                continue
            linear_unit = "linear x255 (as first cut)"
            srgb_unit = "sRGB code (W25's own unit)"
            print(f"  {bed} — {tier}")
            print(f"    {'':<20}{linear_unit:>35}{srgb_unit:>37}")
            print(f"    {'backdrop':<20}{'resid(96)':>11}{'resid(160)':>12}{'Δ':>12}"
                  f"{'resid(96)':>13}{'resid(160)':>12}{'Δ':>12}")
            for backdrop, a, b2 in lines:
                print(f"    {backdrop:<20}{a[0]:>11.2f}{b2[0]:>12.2f}{b2[0] - a[0]:>+12.2f}"
                      f"{a[1]:>13.2f}{b2[1]:>12.2f}{b2[1] - a[1]:>+12.2f}")
            for unit, index in ((linear_unit, 0), (srgb_unit, 1)):
                deltas = [b2[index] - a[index] for _, a, b2 in lines]
                positive = sum(1 for d in deltas if d > 0)
                print(f"    {unit}: n={len(deltas)}  median Δ {median(deltas):+.2f}  "
                      f"range {min(deltas):+.2f}…{max(deltas):+.2f}  "
                      f"positive on {positive}/{len(deltas)}")
            print()

    (HERE / "structure-cut.json").write_text(json.dumps({
        "source": "results/matrix.json at atAShippedDocument",
        "quantity": "interiorStdDevWeb / interiorStdDevNative",
        "coherenceCell": coherence,
        "rows": rows,
    }, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
