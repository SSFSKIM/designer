"""W22 G1 (3d) — the nested pane per pane, native | before | after, at the corrected input.

G0's `stack-tables.py` with the column G0 could not take. Both `glass-over-glass` cells are HOLDOUT
and X5 reserves the wave's one holdout read for this gate, so G0's table had a native column and the
canonical W21 capture and nothing else; this one adds the reading at the frozen configuration —
W22 G3's backdrop-stack fix (claims §5.95) plus this gate's `specularGain`.

The quantity the eye named is the EXCESS — the overlay pane's body minus its base pane's — and its
SIGN: Apple's overlay is darker than its base in the dark scheme and lighter in the light scheme, so
the excess changes sign with the scheme on the reference and the question is whether it does on
vitrea. G3 verified the level against the response law's answer without opening a fixture; this is
the first time the panes are read against the reference itself.

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


def load(reads, profile, tier, when):
    path = os.path.join(reads, f"{profile}-{tier}-{when}.json")
    if not os.path.exists(path):
        return {}
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say("W22 G1 — the nested pane read per pane, both beds, both tiers, both scales")
    say("=" * 118)
    say("base = the base's declared box eroded 6 CSS px with the overlay's box dilated 6 px cut")
    say("out; over = the overlay's declared box eroded 6 CSS px; excess = over − base.")
    say("native is the committed fixture; before is the canonical `web-captures/` at the 0.10.0")
    say("landing; after is this gate's dry run — the FIRST reading of these holdout cells against")
    say("the reference at the corrected input.")
    say()
    say(f"{'profile':38s} {'tier':7s} {'scene':36s} {'column':7s} {'base':>8s} {'over':>8s} "
        f"{'excess':>9s} {'baseSd':>8s} {'overSd':>8s} {'blurSig':>8s}")
    for profile in PROFILES:
        for tier in ("webgpu", "css"):
            before = load(args.reads, profile, tier, "before")
            after = load(args.reads, profile, tier, "after")
            for scene in sorted(after):
                columns = [("native", after[scene].get("native"))]
                if scene in before and before[scene].get("web") is not None:
                    columns.append(("before", before[scene]["web"]))
                if after[scene].get("web") is not None:
                    columns.append(("after", after[scene]["web"]))
                for label, d in columns:
                    if d is None:
                        continue
                    say(f"{profile:38s} {tier:7s} {scene:36s} {label:7s} "
                        f"{d['baseBody']:8.4f} {d['overBody']:8.4f} {d['excess']:+9.4f} "
                        f"{d['baseSd']:8.4f} {d['overSd']:8.4f} "
                        f"{d.get('baseBlurSigmaMatchPx', float('nan')):8.2f}")

    say()
    say("== the eight sides, per pane, native against the after column")
    say(f"{'profile':38s} {'tier':7s} {'scene':36s} {'column':7s} {'pane':5s} | rim T/B/L/R")
    for profile in PROFILES:
        for tier in ("webgpu", "css"):
            after = load(args.reads, profile, tier, "after")
            for scene in sorted(after):
                for label in ("native", "web"):
                    d = after[scene].get(label)
                    if d is None:
                        continue
                    name = "native" if label == "native" else "after"
                    for pane, key in (("base", "baseRim"), ("over", "overRim")):
                        say(f"{profile:38s} {tier:7s} {scene:36s} {name:7s} {pane:5s} | "
                            + " ".join(f"{v:.4f}" for v in d[key]))

    say()
    say("== the excess's sign, which is the whole of the eye's finding")
    say(f"{'profile':38s} {'tier':7s} {'scene':36s} {'native':>9s} {'before':>9s} {'after':>9s} "
        f"{'sign now':>9s}")
    for profile in PROFILES:
        for tier in ("webgpu", "css"):
            before = load(args.reads, profile, tier, "before")
            after = load(args.reads, profile, tier, "after")
            for scene in sorted(after):
                if after[scene].get("web") is None:
                    continue
                n = after[scene]["native"]["excess"]
                w = after[scene]["web"]["excess"]
                was = (
                    before[scene]["web"]["excess"]
                    if scene in before and before[scene].get("web") is not None
                    else float("nan")
                )
                agree = "yes" if (n >= 0) == (w >= 0) else "INVERTED"
                say(f"{profile:38s} {tier:7s} {scene:36s} {n:+9.4f} {was:+9.4f} {w:+9.4f} "
                    f"{agree:>9s}")

    with open(args.out, "w") as handle:
        handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
