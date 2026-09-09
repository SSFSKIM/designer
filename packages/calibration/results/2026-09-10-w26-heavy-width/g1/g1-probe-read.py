"""W26 G1 — the probe set at the candidate against the inert default: the level, the spans, X5.

Three questions the impulse rows cannot answer, all read as a difference between two capture roots
(`p0` the inert default, `pc` the candidate) over the same 52 probe scenes at the four standard
profiles:

  1. **The level above the knee** (`sizeToneLevelFar`, W25's third mechanism, still 0). W25 recorded
     that the offset the probe SOLIDS ask for flips sign across backdrops, which is why it was
     declined. The wave's question is whether the width in place changes that, since a too-narrow
     heavy component reads as a level error on a structured backdrop. Read as the interior-level
     error (web minus native, linear luma) per backdrop per span.
  2. **One width per source, across the spans.** The heavy texture is built before any group is
     drawn, so the span grading the gain carried does not reach the deep sample. The mid-span rows
     (44 -> 96) are where that would show first, and they are read at the candidate against the
     inert default on the OKLab dE the harness already computes.
  3. **X5 over every thin cell** (span <= 44), not the three the ladder carries.

    g1-probe-read.py [--scratch DIR] [--base p0] [--rung pc]
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w26lib  # noqa: E402,F401  (puts W25 G0's reader library on the path, X1)
import w25lib as L  # noqa: E402

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1"
SOLIDS = ("light-solid", "dark-solid", "mid-dark-solid")
PROFILES = ("apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard",
            "apple-macos-26.5-1x-dark-standard", "apple-macos-26.5-2x-dark-standard")


def cells_of(rung, scratch):
    path = os.path.join(scratch, rung, "rung.json")
    if not os.path.exists(path):
        return {}
    out = {}
    for cell in json.load(open(path))["cells"]:
        if cell["tier"] != "texture":
            continue
        entry = (cell.get("perceptual") or {}).get("oklabDeltaEMean")
        value = entry.get("value") if isinstance(entry, dict) else entry
        if value is not None:
            out[(cell["key"]["profileKey"], cell["key"]["sceneId"])] = float(value)
    return out


def scale_of(profile):
    return 2.0 if "-2x-" in profile else 1.0


def interior_level(path, comp, scale, comps):
    if not os.path.exists(path):
        return None
    lum = L.luma_of(path)
    shape = (int(200 * scale), int(320 * scale))
    if lum.shape != shape:
        return None
    return float(lum[L.Cell(comp, comps).body_mask(scale, shape, 8.0)].mean())


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default=SCRATCH)
    ap.add_argument("--base", default="p0")
    ap.add_argument("--rung", default="pc")
    ap.add_argument("--out", default=os.path.join(HERE, "probe-read.txt"))
    args = ap.parse_args(argv)
    comps = L.load_components()
    spec = json.load(open(L.SCENES))
    scenes = {s["id"]: s for s in spec["scenes"]}
    span = {c: float(min(v["size"])) for c, v in comps.items() if "size" in v}

    base, rung = cells_of(args.base, args.scratch), cells_of(args.rung, args.scratch)
    out = ["W26 G1 — the probe set at the candidate against the inert default", "=" * 100, ""]
    e = out.append

    # 1. The level above the knee, on the probe solids.
    e("1. The level above the knee — the interior-level error on the probe SOLIDS")
    e("")
    e("   web minus native, LINEAR luma, over the eroded interior. W25 declined")
    e("   `sizeToneLevelFar` because the sign of what the solids ask for flips across backdrops;")
    e("   the question here is whether the heavy width in place changes that.")
    e("")
    e(f"   {'profile':>44} {'backdrop':>15} {'span':>5} {'base':>9} {'cand':>9} {'move':>9}")
    signs = {}
    for profile in PROFILES:
        sc = scale_of(profile)
        for sid, scene in sorted(scenes.items()):
            if scene["background"] not in SOLIDS:
                continue
            comp = scene["component"]
            if comp not in span:
                continue
            native = L.native_path(profile, sid)
            nb = interior_level(native, comp, sc, comps)
            if nb is None:
                continue
            a = interior_level(os.path.join(args.scratch, args.base, "web-captures", profile, sid,
                                            f"{sid}__webgpu.png"), comp, sc, comps)
            b = interior_level(os.path.join(args.scratch, args.rung, "web-captures", profile, sid,
                                            f"{sid}__webgpu.png"), comp, sc, comps)
            if a is None or b is None:
                continue
            e(f"   {profile:>44} {scene['background']:>15} {span[comp]:5.0f} "
              f"{a - nb:9.5f} {b - nb:9.5f} {b - a:9.5f}")
            if span[comp] >= 96:
                signs.setdefault((profile, scene["background"]), []).append(b - nb)
    e("")
    e("   The sign above the knee (span >= 96), per profile per backdrop, at the CANDIDATE:")
    for key, vals in sorted(signs.items()):
        m = float(np.mean(vals))
        e(f"     {key[0]:>44} {key[1]:>15} mean {m:+9.5f}  ({'raise' if m < 0 else 'lower'})")
    e("")

    # 2. The spans.
    e("2. One width per source, across the spans — OKLab dE mean, base against candidate")
    e("")
    e(f"   {'span':>5} {'n':>4} " + " ".join(f"{p.replace('apple-macos-26.5-', ''):>28}"
                                             for p in PROFILES))
    rows = {}
    for (profile, sid), value in rung.items():
        if (profile, sid) not in base:
            continue
        comp = scenes[sid]["component"]
        if comp not in span:
            continue
        rows.setdefault(span[comp], {}).setdefault(profile, []).append(
            (base[(profile, sid)], value))
    for s in sorted(rows):
        cells = []
        n = 0
        for profile in PROFILES:
            pairs = rows[s].get(profile, [])
            n = max(n, len(pairs))
            if not pairs:
                cells.append(f"{'-':>28}")
                continue
            a = float(np.mean([p[0] for p in pairs]))
            b = float(np.mean([p[1] for p in pairs]))
            worse = sum(1 for x, y in pairs if y > x + 1e-6)
            cells.append(f"{a:8.5f}->{b:8.5f} {worse:2d}/{len(pairs):2d}w")
        e(f"   {s:5.0f} {n:4d} " + " ".join(cells))
    e("")
    e("   `w` counts the cells whose dE against the reference WORSENED at the candidate.")
    e("")

    # 3. X5 over every thin cell.
    e("3. X5 — every probe cell of span <= 44, OKLab dE move against the inert default")
    e("")
    worst = []
    for (profile, sid), value in rung.items():
        if (profile, sid) not in base:
            continue
        comp = scenes[sid]["component"]
        if comp not in span or span[comp] > 44:
            continue
        worst.append((abs(value - base[(profile, sid)]), profile, sid,
                      base[(profile, sid)], value))
    worst.sort(reverse=True)
    e(f"   {len(worst)} thin cells; the ten largest moves:")
    e(f"   {'move':>9} {'base':>9} {'cand':>9}  profile / scene")
    for move, profile, sid, a, b in worst[:10]:
        e(f"   {move:9.5f} {a:9.5f} {b:9.5f}  {profile.replace('apple-macos-26.5-', '')} / {sid}")
    if worst:
        e("")
        e(f"   Worst thin-cell move: {worst[0][0]:.5f} (X5's bound is 0.001).")
    e("")

    text = "\n".join(out)
    print(text)
    open(args.out, "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
