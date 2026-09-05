"""W20 G1: the dry run's three tables — conformance, fidelity, and the rounded rectangles' bytes.

    python3 g1-tables.py <after-matrix.json> <g0-conformance.json> <canonical-matrix.json> \
        <after-captures-dir> <canonical-captures-dir>

(a) conformance, before (G0's bed-wide reading on the same instrument, contract X1) against after,
    on every capsule-button and toolbar-group cell and on the rounded-rectangle cells;
(b) fidelity, before (the canonical W19 bed) against after, on the capsule and toolbar cells;
(c) every rounded-rectangle and glass-over-glass GPU capture, byte for byte against the canonical
    one — sha256 equal, or the differing pixel count and the max code difference.

A cell is keyed by (profileKey, sceneId, renderer) and the GPU tier only. The material profile
document did not change in this wave, so the cell keys match across the three matrices and a row
that fails to pair is a fact worth printing rather than dropping.
"""
import collections
import hashlib
import json
import os
import sys

CAPSULE_COMPONENTS = ("capsule-button", "toolbar-group")
RRECT_COMPONENTS = ("rrect-sm", "rrect-md", "rrect-ml", "rrect-lg", "glass-over-glass")


def component_of(scene_id):
    return scene_id.split("__")[1]


def short(profile):
    return profile.replace("apple-macos-26.5-", "")


def index(path):
    matrix = json.load(open(path))
    out = {}
    for cell in matrix["cells"]:
        key = (cell["key"]["profileKey"], cell["key"]["sceneId"], cell["key"]["web"]["renderer"])
        # A partial run appends; the newest row per key is the one that counts.
        out[key] = cell
    return matrix, out


def axis(cell, axis_name, field):
    block = cell.get(axis_name)
    if block is None:
        return None
    entry = block.get(field)
    return None if entry is None else entry["value"]


def fmt(value, width=8, places=4):
    return "—".rjust(width) if value is None else f"{value:{width}.{places}f}"


def delta(after, before, width=9, places=4):
    if after is None or before is None:
        return "—".rjust(width)
    return f"{after - before:+{width}.{places}f}"


# ---------------------------------------------------------------------------
# (a) conformance
# ---------------------------------------------------------------------------

def conformance(before, after):
    print("\n\n## (a) declaration conformance, GPU tier — G0's instrument, before and after\n")
    header = (f"{'profile':<26} {'scene':<40} "
              f"{'drawn b':>8} {'drawn a':>8} {'declared':>8}  "
              f"{'IoU b':>7} {'IoU a':>7}  {'max b':>6} {'max a':>6}")
    for title, wanted in (("capsule and toolbar cells", CAPSULE_COMPONENTS),
                          ("rounded-rectangle and stack cells", RRECT_COMPONENTS)):
        print(f"\n### {title}\n")
        print(header)
        print("-" * len(header))
        worst_after_max = 0.0
        for key in sorted(after):
            profile, scene, renderer = key
            if renderer != "webgpu" or component_of(scene) not in wanted:
                continue
            b = before.get(key)
            a = after[key]
            if axis(a, "shape", "declaredIoUWeb") is None:
                continue
            drawn_b = axis(b, "shape", "drawnAreaWeb") if b else None
            drawn_a = axis(a, "shape", "drawnAreaWeb")
            declared = axis(a, "shape", "componentRegionArea")
            max_a = axis(a, "shape", "declaredContourMaxWeb")
            worst_after_max = max(worst_after_max, max_a or 0.0)
            print(f"{short(profile):<26} {scene:<40} "
                  f"{fmt(drawn_b, 8, 0)} {fmt(drawn_a, 8, 0)} {fmt(declared, 8, 0)}  "
                  f"{fmt(axis(b, 'shape', 'declaredIoUWeb') if b else None, 7)} "
                  f"{fmt(axis(a, 'shape', 'declaredIoUWeb'), 7)}  "
                  f"{fmt(axis(b, 'shape', 'declaredContourMaxWeb') if b else None, 6, 2)} "
                  f"{fmt(max_a, 6, 2)}")
        print(f"\nworst declaredContourMaxWeb after, over these cells: {worst_after_max:.2f} device px")


# ---------------------------------------------------------------------------
# (b) fidelity
# ---------------------------------------------------------------------------

FIDELITY = (
    ("perceptual", "oklabDeltaEMean", "ΔE mean", -1),
    ("perceptual", "ssimMean", "SSIM mean", +1),
    ("shape", "silhouetteIoU", "silhouette IoU", +1),
    ("material", "rimPeakLuminanceWeb", "rim peak web", 0),
)


def fidelity(before, after):
    print("\n\n## (b) fidelity against Apple, GPU tier — the W19 canonical bed, before and after\n")
    print("`better` is the sign the metric improves in: ΔE down, SSIM up, IoU up. The interior")
    print("mean is read against the NATIVE interior mean beside it, so its own column is the gap.\n")
    header = (f"{'profile':<26} {'scene':<40} "
              f"{'ΔE b':>8} {'ΔE a':>8} {'ΔΔE':>9}  {'SSIM b':>7} {'SSIM a':>7} {'ΔSSIM':>9}  "
              f"{'|int gap| b':>11} {'|int gap| a':>11}  {'rim b':>7} {'rim a':>7}  {'IoU a':>6}")
    print(header)
    print("-" * len(header))
    rows = []
    for key in sorted(after):
        profile, scene, renderer = key
        if renderer != "webgpu" or component_of(scene) not in CAPSULE_COMPONENTS:
            continue
        b = before.get(key)
        a = after[key]
        if b is None:
            print(f"{short(profile):<26} {scene:<40}  NO BEFORE ROW")
            continue
        de_b = axis(b, "perceptual", "oklabDeltaEMean")
        de_a = axis(a, "perceptual", "oklabDeltaEMean")
        ss_b = axis(b, "perceptual", "ssimMean")
        ss_a = axis(a, "perceptual", "ssimMean")
        # The interior gap is absent where the material axis is (the `dark-solid`
        # cells, whose silhouette is empty inside the declared region): absent, not
        # zero, and printed as such rather than paired against nothing.
        def gap(cell):
            web = axis(cell, "material", "interiorMeanWeb")
            native = axis(cell, "material", "interiorMeanNative")
            return None if web is None or native is None else abs(web - native)

        gap_b, gap_a = gap(b), gap(a)
        rows.append((short(profile), scene, de_a - de_b, ss_a - ss_b,
                     None if gap_a is None or gap_b is None else gap_a - gap_b))
        print(f"{short(profile):<26} {scene:<40} "
              f"{fmt(de_b)} {fmt(de_a)} {delta(de_a, de_b)}  "
              f"{fmt(ss_b, 7)} {fmt(ss_a, 7)} {delta(ss_a, ss_b)}  "
              f"{fmt(gap_b, 11)} {fmt(gap_a, 11)}  "
              f"{fmt(axis(b, 'material', 'rimPeakLuminanceWeb'), 7)} "
              f"{fmt(axis(a, 'material', 'rimPeakLuminanceWeb'), 7)}  "
              f"{fmt(axis(a, 'shape', 'silhouetteIoU'), 6, 3)}")
    if rows:
        worse_de = [r for r in rows if r[2] > 0]
        worse_ss = [r for r in rows if r[3] < 0]
        print(f"\n{len(rows)} capsule/toolbar GPU cells.")
        print(f"  ΔE:   {len(rows) - len(worse_de)} improved, {len(worse_de)} worsened; "
              f"best {min(r[2] for r in rows):+.5f} ({min(rows, key=lambda r: r[2])[1]}), "
              f"worst {max(r[2] for r in rows):+.5f} ({max(rows, key=lambda r: r[2])[1]})")
        print(f"  SSIM: {len(rows) - len(worse_ss)} improved, {len(worse_ss)} worsened; "
              f"best {max(r[3] for r in rows):+.5f} ({max(rows, key=lambda r: r[3])[1]}), "
              f"worst {min(r[3] for r in rows):+.5f} ({min(rows, key=lambda r: r[3])[1]})")
        for label, entries in (("ΔE", worse_de), ("SSIM", worse_ss)):
            if entries:
                print(f"  STOP CANDIDATES on {label}:")
                for entry in entries:
                    print(f"    {entry[0]:<26} {entry[1]:<40} {entry[2] if label == 'ΔE' else entry[3]:+.6f}")


# ---------------------------------------------------------------------------
# (c) the rounded rectangles' bytes
# ---------------------------------------------------------------------------

def png_pixels(path):
    from PIL import Image
    import numpy as np
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.int16)


def bytes_table(after_dir, canonical_dir):
    print("\n\n## (c) every rounded-rectangle and glass-over-glass GPU capture, byte for byte\n")
    print("The canonical `web-captures/` is the W19 bed's, on the capture machine. A pair that")
    print("differs is reported with its differing-pixel count and max code difference; the")
    print("tracker's one frame-timing pair moves by a single code between any two runs.\n")
    header = f"{'profile':<26} {'scene':<40} {'sha equal':>9} {'diff px':>9} {'max code':>9}"
    print(header)
    print("-" * len(header))
    moved = []
    missing = []
    for profile in sorted(os.listdir(after_dir)):
        pdir = os.path.join(after_dir, profile)
        if not os.path.isdir(pdir):
            continue
        for scene in sorted(os.listdir(pdir)):
            if component_of(scene) not in RRECT_COMPONENTS:
                continue
            name = f"{scene}__webgpu.png"
            a = os.path.join(pdir, scene, name)
            c = os.path.join(canonical_dir, profile, scene, name)
            if not os.path.exists(a) or not os.path.exists(c):
                missing.append((profile, scene))
                continue
            ha = hashlib.sha256(open(a, "rb").read()).hexdigest()
            hc = hashlib.sha256(open(c, "rb").read()).hexdigest()
            if ha == hc:
                print(f"{short(profile):<26} {scene:<40} {'yes':>9} {0:>9} {0:>9}")
                continue
            import numpy as np
            pa, pc = png_pixels(a), png_pixels(c)
            if pa.shape != pc.shape:
                print(f"{short(profile):<26} {scene:<40} {'NO':>9} {'shape':>9} {'shape':>9}")
                moved.append((profile, scene, -1, -1))
                continue
            diff = np.abs(pa - pc)
            count = int((diff.max(axis=2) > 0).sum())
            worst = int(diff.max())
            print(f"{short(profile):<26} {scene:<40} {'NO':>9} {count:>9} {worst:>9}")
            moved.append((profile, scene, count, worst))
    print(f"\n{len(moved)} capture(s) not byte-identical; {len(missing)} pair(s) missing a side.")
    for entry in moved:
        print(f"  MOVED {short(entry[0]):<26} {entry[1]:<40} {entry[2]} px, max code {entry[3]}")
    for entry in missing:
        print(f"  MISSING {short(entry[0]):<26} {entry[1]}")


def main():
    after_path, before_conf_path, canonical_path, after_dir, canonical_dir = sys.argv[1:6]
    after_matrix, after = index(after_path)
    _, before_conf = index(before_conf_path)
    _, canonical = index(canonical_path)
    print(f"# W20 G1 dry run — the corrected corner over the bed, GPU tier, to scratch\n")
    print(f"after   {after_path}: {len(after_matrix['cells'])} cells")
    print(f"before  conformance {before_conf_path}, fidelity {canonical_path}")
    conformance(before_conf, after)
    fidelity(canonical, after)
    bytes_table(after_dir, canonical_dir)


if __name__ == "__main__":
    main()
