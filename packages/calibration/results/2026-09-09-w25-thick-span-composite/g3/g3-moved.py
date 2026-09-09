"""W25 G3 — what moved between two rungs: byte identity, and OKLab ΔE per cell.

Two questions with one answer each, and both are stops.

**Which captures moved at all** (W24 G2's S10 and this wave's inertness claims). A capture that is
byte-identical between two materials is a cell the change could not reach; a capture that moved is
one it did. The 2x share is the case this exists for: `sizeScatterFloor2x` is 1, so `kDeep` is
saturated before the lift is added and the constant should be arithmetically inert at that ratio —
which is a byte-identity claim and is measured here rather than argued (Decision Log 4 (e)).

**Which cells moved by how much** (X5 and S14). The matrices the two rungs wrote carry
`oklabDeltaEMean` per cell; the thin rows (span at or below 44) are printed first with their own
bound, because a thin cell moved by more than 0.001 ΔE stops the ladder whatever else improved.

    g3-moved.py <rung-a> <rung-b> [--thin-span 44]
"""

import argparse
import hashlib
import json
import os
import sys

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3"
SCENES = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "..", "..", "..", "..",
                                      "apps", "reference-apple", "scenes.json"))


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def captures(rung):
    root = os.path.join(SCRATCH, rung, "web-captures")
    out = {}
    for profile in sorted(os.listdir(root)):
        pdir = os.path.join(root, profile)
        if not os.path.isdir(pdir):
            continue
        for scene in sorted(os.listdir(pdir)):
            sdir = os.path.join(pdir, scene)
            if not os.path.isdir(sdir):
                continue
            for name in sorted(os.listdir(sdir)):
                if name.endswith(".png"):
                    out[(profile, scene, name)] = digest(os.path.join(sdir, name))
    return out


def deltas(rung):
    path = os.path.join(SCRATCH, rung, "probe.json")
    out = {}
    for cell in json.load(open(path))["cells"]:
        key = (cell["key"]["profileKey"], cell["key"]["web"]["renderer"], cell["key"]["sceneId"])
        value = cell.get("perceptual", {}).get("oklabDeltaEMean")
        if isinstance(value, dict):
            value = value.get("value")
        if isinstance(value, (int, float)):
            out[key] = value
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--thin-span", type=float, default=44.0)
    args = ap.parse_args(argv)

    scenes = json.load(open(SCENES))
    comps = scenes["components"]
    span = {}
    for scene in scenes["scenes"]:
        spec = comps[scene["component"]]
        if spec["kind"] == "stack":
            span[scene["id"]] = min(spec["base"]["size"])
        elif spec["kind"] == "group":
            span[scene["id"]] = min(spec["items"][0]["size"])
        else:
            span[scene["id"]] = min(spec["size"])

    a, b = captures(args.a), captures(args.b)
    shared = sorted(set(a) & set(b))
    moved = [k for k in shared if a[k] != b[k]]
    print(f"captures compared      {len(shared)}  ({len(a)} in {args.a}, {len(b)} in {args.b})")
    print(f"byte-identical         {len(shared) - len(moved)}")
    print(f"moved                  {len(moved)}")
    by_profile = {}
    for profile, scene, name in moved:
        by_profile.setdefault(profile, []).append(scene)
    for profile in sorted(set(p for p, _s, _n in shared)):
        n = len(by_profile.get(profile, []))
        total = len([1 for p, _s, _n in shared if p == profile])
        print(f"  {profile:44} {n:3} of {total:3} moved")

    da, db = deltas(args.a), deltas(args.b)
    common = sorted(set(da) & set(db))
    print(f"\nΔE cells compared      {len(common)}")
    thin = [(k, db[k] - da[k]) for k in common if span.get(k[2], 0) <= args.thin_span]
    thick = [(k, db[k] - da[k]) for k in common if span.get(k[2], 0) > args.thin_span]
    for label, rows, bound in (("thin (span <= %g), X5" % args.thin_span, thin, 0.001),
                               ("thick", thick, 0.002)):
        if not rows:
            continue
        worst = max(rows, key=lambda kv: kv[1])
        best = min(rows, key=lambda kv: kv[1])
        over = [kv for kv in rows if kv[1] > bound]
        print(f"\n{label}: {len(rows)} cells, bound {bound}")
        print(f"  worst rise   {worst[1]:+.6f}  {worst[0][0]} / {worst[0][1]} / {worst[0][2]}")
        print(f"  best fall    {best[1]:+.6f}  {best[0][0]} / {best[0][1]} / {best[0][2]}")
        print(f"  over bound   {len(over)}")
        for k, v in sorted(over, key=lambda kv: -kv[1])[:12]:
            print(f"    {v:+.6f}  {k[0]} / {k[1]} / {k[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
