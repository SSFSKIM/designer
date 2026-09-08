"""W22 G0 (e2) — the nested pane, gathered: per pane, per tier, per scheme, per scale.

`read-stack.py` writes one file per profile and tier; this is the one table the finding is read
off. The quantity the eye named is the EXCESS — the overlay pane's body minus its base pane's —
and its SIGN: Apple's overlay is darker than its base in the dark scheme and lighter in the light
scheme, so the excess changes sign with the scheme on the reference and the question is whether it
does on vitrea.

Usage: stack-tables.py --reads <dir> --out <file>
"""

import argparse
import json
import os

PROFILES = (
    "apple-macos-26.5-1x-light-standard",
    "apple-macos-26.5-2x-light-standard",
    "apple-macos-26.5-1x-dark-standard",
    "apple-macos-26.5-2x-dark-standard",
)
SIDES = ("top", "bottom", "left", "right")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say("W22 G0 (e2) — the nested pane read per pane, both beds, both tiers, both scales")
    say()
    say("base = the base's declared box eroded 6 CSS px with the overlay's box dilated 6 px cut")
    say("out; over = the overlay's declared box eroded 6 CSS px; excess = over - base. The web")
    say("column is the CANONICAL `web-captures/` at the 0.10.0 landing: both `glass-over-glass`")
    say("cells are HOLDOUT, W22 X5 spends the wave's one holdout read at G1, and this gate")
    say("therefore takes no new capture of them. Nothing here is an 'after' reading.")
    say()
    say(f"{'profile':38s} {'tier':7s} {'scene':36s} {'which':7s} {'base':>8s} {'over':>8s} "
        f"{'excess':>9s} {'baseSd':>8s} {'overSd':>8s} {'blurSig':>8s}")
    for profile in PROFILES:
        for tier in ("webgpu", "css"):
            path = os.path.join(args.reads, f"{profile}-{tier}.json")
            if not os.path.exists(path):
                continue
            for row in json.load(open(path))["rows"]:
                for which in ("native", "web"):
                    d = row.get(which)
                    if d is None:
                        continue
                    say(f"{profile:38s} {tier:7s} {row['scene']:36s} {which:7s} "
                        f"{d['baseBody']:8.4f} {d['overBody']:8.4f} {d['excess']:+9.4f} "
                        f"{d['baseSd']:8.4f} {d['overSd']:8.4f} "
                        f"{d.get('baseBlurSigmaMatchPx', float('nan')):8.2f}")

    say()
    say("== the eight sides, per pane")
    say(f"{'profile':38s} {'tier':7s} {'scene':36s} {'which':7s} {'pane':5s} | rim T/B/L/R")
    for profile in PROFILES:
        for tier in ("webgpu", "css"):
            path = os.path.join(args.reads, f"{profile}-{tier}.json")
            if not os.path.exists(path):
                continue
            for row in json.load(open(path))["rows"]:
                for which in ("native", "web"):
                    d = row.get(which)
                    if d is None:
                        continue
                    for pane, key in (("base", "baseRim"), ("over", "overRim")):
                        say(f"{profile:38s} {tier:7s} {row['scene']:36s} {which:7s} {pane:5s} | "
                            + " ".join(f"{v:.4f}" for v in d[key]))

    say()
    say("== the excess's sign, which is the whole of the eye's finding")
    say(f"{'profile':38s} {'tier':7s} {'scene':36s} {'native':>9s} {'web':>9s} {'agree?':>8s}")
    for profile in PROFILES:
        for tier in ("webgpu", "css"):
            path = os.path.join(args.reads, f"{profile}-{tier}.json")
            if not os.path.exists(path):
                continue
            for row in json.load(open(path))["rows"]:
                if "web" not in row:
                    continue
                n, w = row["native"]["excess"], row["web"]["excess"]
                agree = "yes" if (n >= 0) == (w >= 0) else "INVERTED"
                say(f"{profile:38s} {tier:7s} {row['scene']:36s} {n:+9.4f} {w:+9.4f} {agree:>8s}")

    with open(args.out, "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
