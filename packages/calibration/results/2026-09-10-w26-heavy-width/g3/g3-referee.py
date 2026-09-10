"""W26 G3 — the referee over the canonical rebuild.

A landing writes the committed evidence, so the question it has to answer is not "did the run
succeed" but "are the bytes it wrote the bytes the wave declared". This wave has TWO declarations
pointing in opposite directions and the referee is built around that:

  * the LIGHT scheme takes the heavy width, so its GPU rows must reproduce **G2b's declared
    digests** (`g2/g2b-digests.txt`) and must NOT reproduce the canonical 0.14.0 bed;
  * the DARK scheme declines it (Decision Log 10 (c)), so its GPU rows must reproduce the
    **canonical 0.14.0 bytes** and must NOT reproduce G2b's, whose dark column was captured at the
    inherited 9 / 9;
  * the CSS tier is byte-identical to 0.14.0 on both schemes (Decision Log 7 (f)), so every dom
    capture must reproduce the canonical bytes.

Each of the three is checked in BOTH directions. An identity that held because the whole capture
path had drifted, or a difference that was really a flake, looks like a pass from one side only.

It also checks the bed's SHAPE against the 0.14.0 bed (every (profile, tier, set) count) and the
corrected `silhouetteIoU` column against `g3a/recompute-rows.json` on the cells whose captures did
not move — which is the check that the rebuild carries G3a's instrument rather than merely running
after it.

    g3-referee.py --before <dir> --after <dir> --before-matrix <json> --after-matrix <json>
                  --g2b <g2b-digests.txt> --recompute <recompute-rows.json>
"""

import argparse
import hashlib
import json
import os
from collections import Counter, defaultdict

TIER_OF = {"__webgpu": "texture", "__css": "dom"}


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree(root):
    out = {}
    for base, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith(".png"):
                full = os.path.join(base, name)
                out[os.path.relpath(full, root)] = full
    return out


def read_digests(path):
    out = {}
    for line in open(path):
        parts = line.split(None, 1)
        if len(parts) == 2 and len(parts[0]) == 64 and all(c in "0123456789abcdef" for c in parts[0]):
            out[parts[1].strip()] = parts[0]
    return out


def is_dark(rel):
    return "-dark-standard/" in rel


def is_css(rel):
    return "__css" in rel


def delta(a, b):
    try:
        import numpy as np
        from PIL import Image
    except Exception:
        return None
    ia = np.asarray(Image.open(a).convert("RGBA"), dtype=np.int16)
    ib = np.asarray(Image.open(b).convert("RGBA"), dtype=np.int16)
    if ia.shape != ib.shape:
        return f"shape {ia.shape} vs {ib.shape}"
    d = np.abs(ia - ib)
    return f"max {int(d.max())} code(s) over {int((d.max(axis=2) > 0).sum())} px of {ia.shape[0] * ia.shape[1]}"


def compare(label, landed, expect, expectation, before_root=None):
    """One column: how many of `landed` match `expect`, and the movers named."""
    same, movers, absent = 0, [], []
    for rel in sorted(landed):
        if rel not in expect:
            absent.append(rel)
            continue
        got = digest(landed[rel])
        if got == expect[rel]:
            same += 1
        else:
            movers.append((rel, expect[rel], got))
    total = same + len(movers)
    verdict = "PASS" if (expectation == "identical" and not movers) or (
        expectation == "different" and same == 0) else "LOOK"
    print(f"\n--- {label}")
    print(f"    expectation      {expectation}")
    print(f"    compared         {total}")
    print(f"    identical        {same}")
    print(f"    different        {len(movers)}")
    print(f"    not in reference {len(absent)}")
    print(f"    verdict          {verdict}")
    if expectation == "identical":
        for rel, was, now in movers:
            line = f"      MOVED {rel}\n            declared {was}\n            landed   {now}"
            if before_root is not None:
                other = os.path.join(before_root, rel)
                if os.path.exists(other):
                    line += f"\n            delta    {delta(other, landed[rel])}"
            print(line)
    elif same:
        for rel in sorted(landed):
            if rel in expect and digest(landed[rel]) == expect[rel]:
                print(f"      UNMOVED {rel}")
    return total, same, len(movers)


def cells(path):
    out = {}
    for cell in json.load(open(path))["cells"]:
        key = (cell["tier"], cell["fixtureSet"], cell["key"]["sceneId"], cell["key"]["profileKey"])
        out[" / ".join(key)] = cell
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--before-matrix", required=True)
    ap.add_argument("--after-matrix", required=True)
    ap.add_argument("--g2b", required=True)
    ap.add_argument("--recompute", required=True)
    args = ap.parse_args()

    before_tree = tree(args.before)
    after_tree = tree(args.after)
    canonical = {rel: digest(path) for rel, path in before_tree.items()}
    g2b = read_digests(args.g2b)

    print("W26 G3 — the referee over the canonical rebuild")
    print("=" * 100)
    print(f"before (the 0.14.0 bed)  {args.before}  {len(before_tree)} captures")
    print(f"after  (the landed bed)  {args.after}  {len(after_tree)} captures")
    print(f"G2b's declared digests   {args.g2b}  {len(g2b)} captures")

    # ---------------------------------------------------------------- the three columns
    light_gpu = {r: p for r, p in after_tree.items()
                 if not is_css(r) and not is_dark(r) and "__alpha" not in r}
    dark_gpu = {r: p for r, p in after_tree.items() if not is_css(r) and is_dark(r)}
    css = {r: p for r, p in after_tree.items() if is_css(r)}

    print("\n" + "=" * 100)
    print("1. THE LIGHT SCHEME TAKES THE WIDTH — its GPU rows are G2b's, not the canonical bed's")
    compare("light GPU  vs G2b's declared digests", light_gpu, g2b, "identical", args.before)
    compare("light GPU  vs the canonical 0.14.0 bed", light_gpu, canonical, "different")

    print("\n" + "=" * 100)
    print("2. THE DARK SCHEME DECLINES IT — its GPU rows are the canonical bed's, not G2b's")
    compare("dark GPU   vs the canonical 0.14.0 bed", dark_gpu, canonical, "identical", args.before)
    compare("dark GPU   vs G2b's declared digests", {r: p for r, p in dark_gpu.items()
                                                     if "__alpha" not in r},
            g2b, "different")

    print("\n" + "=" * 100)
    print("3. THE CSS TIER IS UNMOVED ON BOTH SCHEMES")
    compare("every CSS capture vs the canonical 0.14.0 bed", css, canonical, "identical", args.before)

    # ---------------------------------------------------------------- the bed's shape
    before_cells, after_cells = cells(args.before_matrix), cells(args.after_matrix)
    print("\n" + "=" * 100)
    print("4. THE BED'S SHAPE")
    shape_b = Counter((c["key"]["profileKey"], c["tier"], c["fixtureSet"]) for c in before_cells.values())
    shape_a = Counter((c["key"]["profileKey"], c["tier"], c["fixtureSet"]) for c in after_cells.values())
    print(f"    cells before {len(before_cells)}   cells after {len(after_cells)}")
    moved = [k for k in sorted(set(shape_b) | set(shape_a)) if shape_b[k] != shape_a[k]]
    print(f"    (profile, tier, set) partitions that differ: {len(moved)}")
    for k in moved:
        print(f"      {k}  {shape_b[k]} -> {shape_a[k]}")
    only_before = sorted(set(before_cells) - set(after_cells))
    only_after = sorted(set(after_cells) - set(before_cells))
    print(f"    cells only in the 0.14.0 bed {len(only_before)}, only in the landed bed {len(only_after)}")
    for k in only_before[:10]:
        print(f"      - {k}")
    for k in only_after[:10]:
        print(f"      + {k}")

    # ------------------------------------------- G3a's corrected silhouetteIoU on the unmoved cells
    print("\n" + "=" * 100)
    print("5. G3a's CORRECTED silhouetteIoU, on the cells whose captures did not move")
    print("   (every dark GPU cell and every CSS cell; the light GPU cells drew a different width)")
    recompute = {" / ".join((r["tier"], r["set"], r["scene"], r["profile"])): r
                 for r in json.load(open(args.recompute))}
    checked, agree, disagree = 0, 0, []
    for key, cell in sorted(after_cells.items()):
        row = recompute.get(key)
        if row is None:
            continue
        entry = (cell.get("shape") or {}).get("silhouetteIoU")
        if not isinstance(entry, dict):
            continue
        tier = cell["tier"]
        dark = "-dark-standard" == cell["key"]["profileKey"][-len("-dark-standard"):]
        unmoved = tier == "dom" or dark
        if not unmoved:
            continue
        checked += 1
        if abs(entry["value"] - row["corrected"]) < 5e-6:
            agree += 1
        else:
            disagree.append((key, row["matrix"], row["corrected"], entry["value"]))
    print(f"    cells checked   {checked}")
    print(f"    agree with g3a/recompute-rows.json  {agree}")
    print(f"    DISAGREE                            {len(disagree)}")
    for key, m, c, v in disagree[:40]:
        print(f"      {key}\n        matrix(0.14.0) {m:.5f}  recompute {c:.5f}  landed {v:.5f}")

    # And the shape of the correction on the whole landed bed, for the record.
    still_uncorrected = 0
    for key, cell in after_cells.items():
        row = recompute.get(key)
        entry = (cell.get("shape") or {}).get("silhouetteIoU")
        if row is None or not isinstance(entry, dict):
            continue
        if row["matrix"] != row["corrected"] and abs(entry["value"] - row["matrix"]) < 5e-6:
            still_uncorrected += 1
    print(f"    landed cells still reading the PRE-correction value  {still_uncorrected}")


if __name__ == "__main__":
    main()
