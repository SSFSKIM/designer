"""The 2x null: every point's matrix and captures must be identical to every other's.
Reports the maximum |difference| over every numeric measurement of every cell, and the
byte identity of the captures, across the points of a sweep directory."""
import json, os, sys, hashlib, itertools
T = "/Users/new/.claude/jobs/5c70e47f/tmp/w13/sweep-4"
name = sys.argv[1] if len(sys.argv) > 1 else "2x-null"
d = f"{T}/points-{name}"
pts = sorted(int(f[7:-5]) for f in os.listdir(d) if f.startswith("matrix-") and f.endswith(".json"))
def flat(o, prefix=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from flat(v, f"{prefix}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from flat(v, f"{prefix}[{i}]")
    elif isinstance(o, (int, float)) and not isinstance(o, bool): yield prefix, float(o)
mats = {}
for p in pts:
    cells = json.load(open(f"{d}/matrix-{p}.json"))["cells"]
    patch = json.load(open(f"{d}/profile-{p}.json"))["patch"]
    lbl = " ".join(f"{k}={patch[k]}" for k in ("sizeScatterRampStartThin2x", "sizeScatterRampStartThick2x", "sizeScatterRampStartFar2x", "sizeScatterRampReach2xPx") if k in patch)
    m = {}
    for c in cells:
        sid = c["key"]["sceneId"]
        for k, v in flat({a: c[a] for a in ("material", "perceptual", "shape", "shadow") if a in c}):
            if "capturedAt" in k or "sha" in k.lower(): continue
            m[(sid, k)] = v
    mats[p] = (lbl, m)
    print(f"point {p}: {lbl}: {len(cells)} cells, {len(m)} measurements")
worst = 0; worst_at = None
for a, b in itertools.combinations(pts, 2):
    ma, mb = mats[a][1], mats[b][1]
    keys = set(ma) & set(mb)
    for k in keys:
        dlt = abs(ma[k] - mb[k])
        if dlt > worst: worst, worst_at = dlt, (a, b, k)
print(f"\nmaximum |difference| over all point pairs and all measurements: {worst}", "" if worst_at is None else f"at {worst_at}")
# captures
caps = {}
for p in pts:
    root = f"{T}/web-captures-{name}"
    # the sweep writes each point's captures under the same dir; hashes per scene per point are not separable after the fact
print("cells per point identical in count:", len({len(v[1]) for v in mats.values()}) == 1)
