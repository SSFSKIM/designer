"""W21 G1 — the dry run read against the W20 bed, and contract X3's byte check.

Three readings, one script, because they are one verdict:

  1. **The dark rows**, per cell, both scales, both tiers: the fidelity axes the gate is judged on
     (OKLab ΔE mean and p95, `ssimMean`) and the material axes the wave's own instrument mirrors
     (`interiorMeanNative` / `Web`, `interiorStdDev*`, `rimPeakLuminance*`), each against the W20
     bed's row in the canonical `results/matrix.json`. The W20 bed is the referee this wave froze
     (the spec's Grounding Baseline), so every movement here is signed against it.
  2. **The stops**, evaluated on those rows with numbers: S1 (an untinted dark row worse by more
     than 0.001 ΔE mean or 0.005 `ssimMean`), S2 (a tinted dark cell moved by more than 0.001),
     S4 (a light capture not byte-identical). S3's collapsed-capsule body and clauses 3 and 4 are
     read under the DECLARED geometry by `read.py` and reported by `g1-declared.py`, not here — the
     matrix's `interiorMean` on a dark solid is a rim reading (claims §5.87) and cannot answer them.
  3. **X3**, the inverse contract: every light-profile capture byte-identical to the canonical
     `web-captures/`. The canonical capture tree is gitignored and lives on the capture machine, so
     its path is given rather than assumed.

The canonical matrix appends rather than overwrites, so a cell's row is taken as the NEWEST by
`capturedAt` for its (profile, renderer, scene) key — the same reduction W20 G2's verifier used.

    g1-tables.py <dry-run matrix.json> <dry-run captures dir> <canonical captures dir>
"""

import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
CAL = os.path.join(ROOT, "packages", "calibration")
PREFIX = "apple-macos-26.5-"
DARK = (PREFIX + "1x-dark-standard", PREFIX + "2x-dark-standard")
LIGHT = PREFIX + "1x-light-standard"
S1_DELTA_E = 0.001
S1_SSIM = 0.005
S2 = 0.001


def load(path):
    best = {}
    for cell in json.load(open(path))["cells"]:
        key = (cell["key"]["profileKey"], cell["key"]["web"]["renderer"], cell["key"]["sceneId"])
        if key not in best or cell["capturedAt"] > best[key]["capturedAt"]:
            best[key] = cell
    return best


def value(cell, axis, name):
    if cell is None:
        return None
    entry = (cell.get(axis) or {}).get(name)
    if entry is None:
        return None
    return entry["value"] if isinstance(entry, dict) else entry


def fixture_set(cell):
    for source in (cell, cell.get("key") or {}):
        for name in ("fixtureSet", "set", "split", "partition"):
            if isinstance(source, dict) and name in source:
                return source[name]
    return "?"


def digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    dry_path, dry_captures, canonical_captures = sys.argv[1:4]
    dry = load(dry_path)
    bed = load(os.path.join(CAL, "results", "matrix.json"))
    print(f"dry run: {len(dry)} cells; the canonical W20 bed: {len(bed)} cells")
    print(f"dry-run captures: {dry_captures}")
    print(f"canonical captures: {canonical_captures}")

    for renderer, label in (("webgpu", "GPU tier"), ("css", "CSS tier")):
        print(f"\n=== the dark bed, {label} — the W20 bed → this dry run ===")
        print(f"  {'cell':46s} {'dpr':3s} {'set':11s}  {'ΔE mean':>17s}  {'ΔE p95':>17s}  "
              f"{'ssimMean':>17s}")
        for profile in DARK:
            dpr = "1x" if "1x" in profile else "2x"
            rows = sorted(scene for (p, r, scene) in dry if p == profile and r == renderer)
            for scene in rows:
                cell = dry[(profile, renderer, scene)]
                before = bed.get((profile, renderer, scene))
                line = f"  {scene:46s} {dpr:3s} {fixture_set(cell):11s}"
                for axis, name in (("perceptual", "oklabDeltaEMean"),
                                   ("perceptual", "oklabDeltaEP95"),
                                   ("perceptual", "ssimMean")):
                    a, b = value(before, axis, name), value(cell, axis, name)
                    line += (f"  {'—':>17s}" if a is None or b is None
                             else f"  {a:7.5f} → {b:7.5f}")
                print(line)

        print(f"\n  the material axes, {label} (native | W20 bed → dry run):")
        print(f"  {'cell':46s} {'dpr':3s} {'interiorMean':>26s} {'interiorStdDev':>26s} "
              f"{'rimPeakLuminance':>26s}")
        for profile in DARK:
            dpr = "1x" if "1x" in profile else "2x"
            for scene in sorted(scene for (p, r, scene) in dry if p == profile and r == renderer):
                cell = dry[(profile, renderer, scene)]
                before = bed.get((profile, renderer, scene))
                line = f"  {scene:46s} {dpr:3s}"
                for name in ("interiorMean", "interiorStdDev", "rimPeakLuminance"):
                    native = value(cell, "material", name + "Native")
                    a = value(before, "material", name + "Web")
                    b = value(cell, "material", name + "Web")
                    line += (f" {'—':>26s}" if native is None or b is None
                             else f" {native:7.4f} | {a if a is not None else float('nan'):7.4f} "
                                  f"→ {b:7.4f}")
                print(line)

    print("\n=== the stops, on the matrix's rows ===")
    fired = []
    print(f"  S1 — an untinted dark row worse than the W20 bed by more than {S1_DELTA_E} ΔE mean "
          f"or {S1_SSIM} ssimMean:")
    for (profile, renderer, scene), cell in sorted(dry.items()):
        if profile not in DARK or "tint" in scene:
            continue
        before = bed.get((profile, renderer, scene))
        delta_e = value(cell, "perceptual", "oklabDeltaEMean")
        base_e = value(before, "perceptual", "oklabDeltaEMean")
        ssim = value(cell, "perceptual", "ssimMean")
        base_s = value(before, "perceptual", "ssimMean")
        if base_e is None or delta_e is None:
            continue
        worse_e = delta_e - base_e
        worse_s = (base_s - ssim) if (ssim is not None and base_s is not None) else 0.0
        if worse_e > S1_DELTA_E or worse_s > S1_SSIM:
            fired.append(("S1", profile, renderer, scene, worse_e, worse_s))
            print(f"    FIRES {scene} @ {profile.replace(PREFIX, '')} / {renderer}: "
                  f"ΔE {base_e:.5f} → {delta_e:.5f} ({worse_e:+.5f}), "
                  f"ssim {base_s:.5f} → {ssim:.5f} ({-worse_s:+.5f})")
    if not any(entry[0] == "S1" for entry in fired):
        print("    does not fire on any row")

    print(f"  S2 — a tinted dark cell moved by more than {S2}:")
    for (profile, renderer, scene), cell in sorted(dry.items()):
        if profile not in DARK or "tint" not in scene:
            continue
        before = bed.get((profile, renderer, scene))
        delta_e = value(cell, "perceptual", "oklabDeltaEMean")
        base_e = value(before, "perceptual", "oklabDeltaEMean")
        if base_e is None or delta_e is None:
            continue
        moved = delta_e - base_e
        state = "FIRES" if abs(moved) > S2 else "     "
        if abs(moved) > S2:
            fired.append(("S2", profile, renderer, scene, moved, 0.0))
        print(f"    {state} {scene:46s} @ {profile.replace(PREFIX, ''):18s} / {renderer:6s} "
              f"ΔE {base_e:.5f} → {delta_e:.5f} ({moved:+.5f})")

    print("\n=== X3 — every light-profile capture byte-identical to the canonical bed ===")
    same, differ, missing = 0, 0, 0
    for (profile, renderer, scene), _cell in sorted(dry.items()):
        if profile != LIGHT:
            continue
        relative = os.path.join(profile, scene, f"{scene}__{renderer}.png")
        a = os.path.join(dry_captures, relative)
        b = os.path.join(canonical_captures, relative)
        if not os.path.exists(a) or not os.path.exists(b):
            missing += 1
            print(f"  MISSING {relative}")
            continue
        if digest(a) == digest(b):
            same += 1
        else:
            differ += 1
            fired.append(("S4", profile, renderer, scene, 0.0, 0.0))
            print(f"  DIFFERS {scene} @ {profile.replace(PREFIX, '')} / {renderer}")
    print(f"  byte-identical {same} / {same + differ}; missing {missing}")

    print("\n=== the dark bed's ΔE mean per profile, tier and split, W20 bed → dry run ===")
    print(f"  {'profile':22s} {'tier':7s} {'split':12s} {'n':>3s}  bed → dry run")
    for profile in DARK:
        for renderer in ("webgpu", "css"):
            for split in ("calibration", "validation", "holdout"):
                after, before = [], []
                for (p, r, scene), cell in dry.items():
                    if p != profile or r != renderer or fixture_set(cell) != split:
                        continue
                    x = value(cell, "perceptual", "oklabDeltaEMean")
                    y = value(bed.get((p, r, scene)), "perceptual", "oklabDeltaEMean")
                    if x is None or y is None:
                        continue
                    after.append(x)
                    before.append(y)
                if not after:
                    continue
                print(f"  {profile.replace(PREFIX, ''):22s} {renderer:7s} {split:12s} "
                      f"{len(after):3d}  {sum(before) / len(before):.5f} → "
                      f"{sum(after) / len(after):.5f}")

    print(f"\nstops fired: {len(fired)}")
    for name, profile, renderer, scene, a, b in fired:
        print(f"  {name} {scene} @ {profile.replace(PREFIX, '')} / {renderer} ({a:+.5f}, {b:+.5f})")


if __name__ == "__main__":
    main()
