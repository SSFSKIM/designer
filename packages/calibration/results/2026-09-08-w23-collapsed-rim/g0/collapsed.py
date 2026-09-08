"""W23 G0 (c) — the collapsed cells: the rim they keep, the schemes' byte identity, the body.

Three questions, one script, so the wave's X4 rests on one reading:

1. **Which cells are collapsed, and what rim does the reference keep on them?** A cell is collapsed
   here when VITREA collapses it — the landed GPU capture's contour rim is 0 on every side, which is
   `present = 0` seen from the pixels — and, on the probe beds where no current capture exists, when
   the reference's body sits within one code of its own backdrop under a dark backdrop. Both are
   stated per cell rather than assumed from a name.
2. **Is the collapsed rim the DARK material's rim on the same backdrop?** The comparison the spec's
   binding shape rests on: `dark-solid__rrect-md` in the dark scheme is the same backdrop
   uncollapsed, and W21's probe grid adds `mid-dark-solid` and `light-solid` at three sizes.
3. **Are the two schemes' fixtures the same bytes?** Not on the two cells the parent read but on
   EVERY scene both standard profiles declare, at both scales, so X4's "one appearance in both
   schemes" is a property of the bed and not of two cells.

Usage: collapsed.py [--out <file>]
"""

import argparse
import hashlib
import json
import math
import os

REPO = "/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-aa0ee5ea92534c3fd"
MAIN = "/Users/new/Developer/GitHub/designer"
HERE = os.path.dirname(os.path.abspath(__file__))
SIDES = ("top", "bottom", "left", "right")

CANONICAL = {
    "light-1x": "canonical-apple-macos-26.5-1x-light-standard-webgpu.json",
    "light-2x": "canonical-apple-macos-26.5-2x-light-standard-webgpu.json",
    "dark-1x": "canonical-apple-macos-26.5-1x-dark-standard-webgpu.json",
    "dark-2x": "canonical-apple-macos-26.5-2x-dark-standard-webgpu.json",
    "probe21-dark": "probe-w21-dark.json",
    "probe9-light": "probe-w9-light.json",
}


def load(name):
    return json.load(open(os.path.join(HERE, "reads", CANONICAL[name])))


def digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16] if os.path.exists(path) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say("W23 G0 (c) — the collapsed cells: the rim the reference keeps, the schemes' byte")
    say("identity, and the body's level against its own backdrop")
    say()
    say("The instrument is `read-contour.py` (X1): the excess over the cell's own local base")
    say("summed over the first two CSS px inside each side's contour, linear, per CSS px. `rimN` is")
    say("the reference's, `rimW` the landed GPU capture's (matrix 3587400, the 0.11.0 bed).")
    say()

    say("== 1. the cells vitrea collapses — the landed capture's contour rim is 0 on every side")
    say(f"{'bed':13s} {'scene':40s} {'bodyN':>7s} {'bodyW':>7s} {'rimN T/B':>17s} "
        f"{'rimW T/B':>17s}")
    collapsed_rows = []
    for bed in ("light-1x", "light-2x", "dark-1x", "dark-2x"):
        data = load(bed)
        for row in data["rows"]:
            if row.get("tint") or "rimWeb" not in row:
                continue
            web = [v for v in row["rimWeb"] if not math.isnan(v)]
            if not web or max(abs(v) for v in web) > 0.0005:
                continue
            collapsed_rows.append((bed, row))
            say(f"{bed:13s} {row['scene']:40s} {row['bodyNative']:7.4f} {row['bodyWeb']:7.4f} "
                f"{row['rimLocalNative'][0]:+8.4f} {row['rimLocalNative'][1]:+8.4f} "
                f"{row['rimLocalWeb'][0]:+8.4f} {row['rimLocalWeb'][1]:+8.4f}")
    say()
    say("and the probe beds' cells whose reference body sits within one code of its own dark")
    say("backdrop — the same appearance, read where no current capture exists:")
    for bed in ("probe21-dark", "probe9-light"):
        data = load(bed)
        for row in data["rows"]:
            if row.get("tint") or not row["scene"].startswith("dark-solid"):
                continue
            if abs(row["bodyNative"] - 0.0110) > 0.0008:
                continue
            collapsed_rows.append((bed, row))
            say(f"{bed:13s} {row['scene']:40s} {row['bodyNative']:7.4f} {'-':>7s} "
                f"{row['rimLocalNative'][0]:+8.4f} {row['rimLocalNative'][1]:+8.4f}")

    say()
    say("== 2. the collapsed rim against the DARK material's rim on the same backdrop")
    say()
    say("The uncollapsed dark rows over the same and neighbouring backdrops, for the comparison:")
    say(f"{'bed':13s} {'scene':40s} {'bodyN':>7s} {'rimN mean':>10s}")
    dark_ref = []
    for bed in ("dark-1x", "dark-2x", "probe21-dark"):
        data = load(bed)
        for row in data["rows"]:
            if row.get("tint"):
                continue
            if not row["scene"].split("__")[0] in ("dark-solid", "mid-dark-solid", "light-solid"):
                continue
            vals = [v for v in row["rimLocalNative"] if not math.isnan(v)]
            mean = sum(vals) / len(vals)
            if abs(row["bodyNative"] - 0.0110) <= 0.0008:
                continue
            dark_ref.append((bed, row["scene"], row["bodyNative"], mean))
            say(f"{bed:13s} {row['scene']:40s} {row['bodyNative']:7.4f} {mean:10.4f}")

    vals = []
    for _bed, row in collapsed_rows:
        vals.extend(v for v in row["rimLocalNative"] if not math.isnan(v))
    say()
    say(f"the collapsed rim over {len(collapsed_rows)} cells / {len(vals)} sides: "
        f"mean {sum(vals) / len(vals):.4f}, min {min(vals):.4f}, max {max(vals):.4f}, "
        f"spread {max(vals) - min(vals):.4f}")
    same = [m for _b, s, _y, m in dark_ref if s.startswith("dark-solid")]
    if same:
        say(f"the DARK material's own rim over the same backdrop (`dark-solid`, uncollapsed): "
            f"mean {sum(same) / len(same):.4f}, min {min(same):.4f}, max {max(same):.4f}")
        say(f"difference: {sum(vals) / len(vals) - sum(same) / len(same):+.4f} linear per CSS px")

    say()
    say("== 3. the two schemes' fixtures, every scene both standard profiles declare")
    spec = json.load(open(os.path.join(REPO, "apps/reference-apple/scenes.json")))
    declared = {}
    for profile in spec["profiles"]:
        declared[profile["key"]] = profile["scenes"]
    all_ids = [s["id"] for s in spec["scenes"]]
    for scale in ("1x", "2x"):
        light_key = f"apple-macos-26.5-{scale}-light-standard"
        dark_key = f"apple-macos-26.5-{scale}-dark-standard"
        dark_scenes = declared[dark_key]
        shared = [s for s in all_ids if s in dark_scenes]
        say()
        say(f"-- {scale}: {len(shared)} scenes declared by both profiles")
        say(f"{'scene':44s} {'identical':>10s}  light sha        dark sha")
        identical = 0
        for sid in shared:
            lp = os.path.join(MAIN, "apps/reference-apple/fixtures", light_key, f"{sid}.png")
            dp = os.path.join(MAIN, "apps/reference-apple/fixtures", dark_key, f"{sid}.png")
            ld, dd = digest(lp), digest(dp)
            if ld is None or dd is None:
                say(f"{sid:44s} {'missing':>10s}")
                continue
            same_bytes = ld == dd
            identical += 1 if same_bytes else 0
            say(f"{sid:44s} {('YES' if same_bytes else 'no'):>10s}  {ld}  {dd}")
        say(f"   {identical} of {len(shared)} byte-identical")

    say()
    say("== 4. the collapsed body against its own backdrop, in codes")
    say(f"{'bed':13s} {'scene':40s} {'bodyN':>8s} {'bodyW':>8s} {'backdrop':>9s} "
        f"{'N-bg codes':>11s}")
    for bed, row in collapsed_rows:
        base = row["baseNative"][0]
        say(f"{bed:13s} {row['scene']:40s} {row['bodyNative']:8.5f} "
            + (f"{row['bodyWeb']:8.5f} " if "bodyWeb" in row else f"{'-':>8s} ")
            + f"{base:9.5f}")

    if args.out:
        with open(args.out, "w") as fh:
            fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
