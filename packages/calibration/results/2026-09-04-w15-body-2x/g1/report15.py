"""The W15 G1 sweep reader (W13 sweep-4's, re-pointed at the W13 bed and the 2x profile): the
rows this wave turns on, per point, keyed by the point's OWN profile rather than by grid order.
Usage: python3 report15.py <sweep name> <axis key> [<axis key> ...]   (the 2x light profile)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tab import rows

BASE = "/Users/new/Developer/GitHub/designer/packages/calibration/results/matrix.json"  # the W13 bed
T = "/Users/new/.claude/jobs/5c70e47f/tmp/w15/g1"
CHECKER = ["checkerboard__rrect-sm__rest", "checkerboard__capsule-button__rest",
           "checkerboard__rrect-md__rest", "checkerboard__rrect-ml__rest",
           "checkerboard__toolbar-group__rest"]
SCORED = CHECKER + ["photo__rrect-md__rest"]
SHORT = {"checkerboard__rrect-sm__rest": "sm", "checkerboard__capsule-button__rest": "caps",
         "checkerboard__rrect-md__rest": "md", "checkerboard__rrect-ml__rest": "ml",
         "checkerboard__toolbar-group__rest": "tb", "photo__rrect-md__rest": "pho-md"}


def num(v):
    f = float(v)
    return str(int(f)) if f == int(f) else ("%g" % f)


def points(name, profileKey, axes):
    """axes: the profile keys swept, in the order sweep.ts was given them."""
    objs = {}
    for line in open(f"{T}/{name}.out"):
        m = re.match(r"^(\S+=\S+(?:\s+\S+=\S+)*)\s{2,}([\d.]+)\s", line)
        if m:
            objs[m.group(1).strip()] = float(m.group(2))
    out = []
    d = f"{T}/points-{name}"
    for f in sorted(os.listdir(d)):
        m = re.match(r"^matrix-(\d+)\.json$", f)
        if not m:
            continue
        i = m.group(1)
        pp = f"{d}/profile-{i}.json"
        patch = json.load(open(pp))["patch"] if os.path.exists(pp) else {}
        lbl = " ".join(f"{a}={num(patch[a])}" for a in axes if a in patch)
        out.append((lbl, objs.get(lbl), rows(f"{d}/{f}", profileKey),
                    tuple(patch.get(a) for a in axes)))
    out.sort(key=lambda x: x[3])
    return out


def tables(name, profileKey, axes, W=78):
    base = rows(BASE, profileKey)
    pts = points(name, profileKey, axes)
    f = lambda x: "  —   " if x is None else f"{x:.4f}"
    scored = []
    for lbl, o, r, key in pts:
        d = {s: r[s]["ssimBand"] - base[s]["ssimBand"] for s in CHECKER}
        rise = sum(d.values()) / len(CHECKER)
        worst = min(d.values())
        s1 = min(r[s]["ssimMean"] - base[s]["ssimMean"] for s in SCORED)
        s4 = all(v > 0 for v in d.values())
        dsd = max(abs(r[s]["isdW"] - base[s]["isdN"]) for s in CHECKER)
        scored.append((lbl, o, r, rise, worst, s1, s4, dsd, d))
    print(f"\n## {name}  ({profileKey})   {len(pts)} points\n")
    for title, key in (("ranked by mean ssimBand rise over the 5 checkerboard cells",
                        lambda x: -x[3]),
                       ("ranked by the WORST cell's ssimBand rise (S4's own reading)",
                        lambda x: -x[4])):
        print(f"### {title}\n")
        print("point".ljust(W) + "obj".rjust(9) + "bandRise".rjust(10) + "worstCell".rjust(11)
              + "minDssimMean".rjust(14) + "S1".rjust(6) + "S4".rjust(6) + "maxDisd".rjust(10))
        for lbl, o, r, rise, worst, s1, s4, dsd, _ in sorted(scored, key=key):
            print(lbl.ljust(W) + (("—" if o is None else f"{o:.5f}")).rjust(9)
                  + f"{rise:+.4f}".rjust(10) + f"{worst:+.4f}".rjust(11) + f"{s1:+.4f}".rjust(14)
                  + ("PASS" if s1 >= -0.002 else "FAIL").rjust(6)
                  + ("PASS" if s4 else "FAIL").rjust(6) + f"{dsd:.4f}".rjust(10))
        print()
    order = sorted(scored, key=lambda x: -x[4])
    print("### per-cell ssimBand delta against the W13 bed, worst-cell order\n")
    print("point".ljust(W) + "".join(SHORT[s].rjust(9) for s in CHECKER))
    for lbl, o, r, rise, worst, s1, s4, dsd, d in order:
        print(lbl.ljust(W) + "".join(f"{d[s]:+.4f}".rjust(9) for s in CHECKER))
    seq = [("main(W13 bed)", None, base)] + [(l, o, r) for l, o, r, _, _, _, _, _, _ in order]
    for metric in ["isdW", "ssimBand", "ssimInterior", "ssimMean", "ssimOutside"]:
        print(f"\n### {metric}\n")
        print("point".ljust(W) + "obj".rjust(9) + "".join(SHORT[s].rjust(9) for s in SCORED))
        for lbl, o, r in seq:
            print(lbl.ljust(W) + (("—" if o is None else f"{o:.5f}")).rjust(9)
                  + "".join(f(r.get(s, {}).get(metric)).rjust(9) for s in SCORED))
        if metric == "isdW":
            print("NATIVE".ljust(W) + "".rjust(9)
                  + "".join(f(base.get(s, {}).get("isdN")).rjust(9) for s in SCORED))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    tables(sys.argv[1], "apple-macos-26.5-2x-light-standard", sys.argv[2:])
