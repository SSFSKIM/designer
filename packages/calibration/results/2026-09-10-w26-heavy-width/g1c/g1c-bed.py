"""W26 G1c — X5 and the per-span OKLab ΔE at every rung, from the rungs' own scratch matrices.

X5 IS THE LADDER'S STOP AND IS CHECKED AT EVERY RUNG, not at the candidate. A thin cell moved by
more than 0.001 of OKLab ΔE stops the ladder, because the thin end of the size law is where every
earlier wave's constants were fitted and this wave's mechanism has no business there. `sizeThick`
is exactly 0 at `sizeSpanMin`, so the expectation is exact inertness and a violation is a bug
rather than a cost.

THE PER-SPAN ΔE IS TAKEN WITH BOTH DOCUMENTS PATCHED (W26 Decision Log 4 (c)), which is what the
rung script does, so the dark columns here are the candidate's and not the inert material
re-rendered. That distinction cost W26 G1 a whole table.

A rung's matrix is written with `--write-partial` and therefore APPENDS beside older rows; the
newest row per key is the one read.

    g1c-bed.py [--rungs c0,d8,...] [--baseline c0] [--out FILE]
"""

import argparse
import collections
import json
import os
import sys

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c"
HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = "/Users/new/Developer/GitHub/designer/apps/reference-apple/scenes.json"
# X5's rows: every probe cell whose component's shorter side is at or under 44 CSS px.
THIN_SPAN = 44.0
BOUND = 0.001


def spans():
    doc = json.load(open(SCENES))
    out = {}
    for name, c in doc["components"].items():
        if c["kind"] in ("rrect", "capsule"):
            out[name] = float(min(c["size"]))
    return out


def newest(path):
    if not os.path.exists(path):
        return {}
    cells = json.load(open(path))["cells"]
    out = {}
    for cell in cells:
        k = cell["key"]
        out[(cell["tier"], k["profileKey"], k["sceneId"])] = cell
    return out


def delta_e(cell):
    """`perceptual.oklabDeltaEMean` — the bed's own perceptual metric, in OKLab units."""
    v = cell.get("perceptual", {}).get("oklabDeltaEMean")
    if isinstance(v, dict):
        v = v.get("value")
    return float(v) if isinstance(v, (int, float)) else None


def component_of(scene_id):
    parts = scene_id.split("__")
    return parts[1] if len(parts) > 1 else None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", default="c0,d8,d9,d10,d11,x98,x910")
    ap.add_argument("--baseline", default="c0")
    ap.add_argument("--out", default=os.path.join(HERE, "bed.txt"))
    args = ap.parse_args(argv)
    span = spans()
    rungs = args.rungs.split(",")
    mats = {r: newest(os.path.join(SCRATCH, r, "rung.json")) for r in rungs}
    base = mats.get(args.baseline, {})
    lines = []
    e = lines.append
    e("W26 G1c — X5 and the per-span OKLab ΔE at every rung, both documents patched")
    e("=" * 100)
    e("")
    e(f"Baseline `{args.baseline}` is the 0.14.0 control: `sizeHeavyTapSigma` 13.418 at dpr 1, which")
    e("draws the clamped chain tap the bed was frozen with, and 0 at dpr 2, which declines the heavy")
    e("texture entirely. Its captures are byte-identical to the canonical ones (`bytes.txt`), so a")
    e("move against it is a move against 0.14.0.")
    e("")

    e("### X5 — every probe cell of span ≤ 44 CSS px, against the 0.001 bound")
    e("")
    e(f"  {'rung':>5} {'cells':>6} {'worst move':>11} {'scene':>44} {'2nd':>11}")
    for rung in rungs:
        if rung == args.baseline:
            continue
        moves = []
        for key, cell in mats[rung].items():
            comp = component_of(key[2])
            if comp not in span or span[comp] > THIN_SPAN:
                continue
            b = base.get(key)
            if b is None:
                continue
            a, c = delta_e(cell), delta_e(b)
            if a is None or c is None:
                continue
            moves.append((abs(a - c), key[2], key[1]))
        if not moves:
            e(f"  {rung:>5}      0   (no thin cells in this rung's rows)")
            continue
        moves.sort(reverse=True)
        second = moves[1][0] if len(moves) > 1 else 0.0
        flag = "" if moves[0][0] <= BOUND else "   X5 VIOLATED"
        e(f"  {rung:>5} {len(moves):6d} {moves[0][0]:11.5f} {moves[0][1]:>44} {second:11.5f}{flag}")
    e("")

    e("### The per-span OKLab ΔE, per profile, against the baseline")
    e("")
    for profile in sorted({k[1] for k in base}):
        e(f"   {profile}")
        by = collections.defaultdict(list)
        for key, cell in base.items():
            if key[1] != profile:
                continue
            comp = component_of(key[2])
            if comp not in span:
                continue
            by[span[comp]].append(key)
        header = f"      {'span':>5} {'cells':>5} {'baseline':>9}"
        for rung in rungs:
            if rung != args.baseline:
                header += f" {rung:>9}{'worse':>7}"
        e(header)
        for sp in sorted(by):
            keys = by[sp]
            b = [delta_e(base[k]) for k in keys]
            b = [x for x in b if x is not None]
            if not b:
                continue
            row = f"      {sp:5.0f} {len(b):5d} {sum(b) / len(b):9.5f}"
            for rung in rungs:
                if rung == args.baseline:
                    continue
                vals, worse = [], 0
                for k in keys:
                    cell = mats[rung].get(k)
                    if cell is None:
                        continue
                    a, c = delta_e(cell), delta_e(base[k])
                    if a is None or c is None:
                        continue
                    vals.append(a)
                    worse += 1 if a > c + 1e-9 else 0
                row += (f" {sum(vals) / len(vals):9.5f}{worse:4d}/{len(vals):<2d}"
                        if vals else " " * 16)
            e(row)
        e("")
    text = "\n".join(lines)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
