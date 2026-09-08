"""W22 G0 (c) — the per-side rim tables on both canonical beds, before and after the gate.

One table per profile. The rows are every cell the declared reader could read (the two composite
components have no single box and are skipped by the reader itself); the SOLID rows —
`light-solid`, `mid-dark-solid`, `dark-solid` — are the ones clause 2 is stated on, and `impulse`
and the structured backdrops are carried as context because a rim band over a structured backdrop
mixes the rim with whatever the band happens to cover.

Every number is linear luminance under the declared geometry (body = the declared box eroded 6 CSS
px; a side's rim peak = the largest row or column mean inside the outer 3 CSS px). Flatness is
`max side - min side` over the four sides, which is the quantity the sweep destroyed: with the band
present vitrea's left side stood 0.12-0.15 above the other three on the dark solids (claims 5.90
4), and the reference's own flatness is what "flat" means on this bed.

Usage: tables.py --reads <dir> --out <dir>
"""

import argparse
import json
import os

SIDES = ("top", "bottom", "left", "right")
SOLIDS = ("light-solid", "mid-dark-solid", "dark-solid")
PROFILES = (
    "apple-macos-26.5-1x-light-standard",
    "apple-macos-26.5-2x-light-standard",
    "apple-macos-26.5-1x-dark-standard",
    "apple-macos-26.5-2x-dark-standard",
)


def load(path):
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def flat(values):
    return max(values) - min(values)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say("W22 G0 (c) — the rim per side on both canonical beds, GPU tier, before and after the gate")
    say()
    say("before = the canonical `web-captures/` at the 0.10.0 landing (the W21 bed, the band")
    say("present); after = this gate's scratch captures at `shimmer` 0 (the band gone). The native")
    say("column is the committed fixtures, identical in both, so the two web columns differ only by")
    say("what vitrea drew. `flatNat` / `flatAft` are max side minus min side over the four sides.")

    for profile in PROFILES:
        before = load(os.path.join(args.reads, f"{profile}-webgpu-before.json"))
        after = load(os.path.join(args.reads, f"{profile}-webgpu-after.json"))
        css = load(os.path.join(args.reads, f"{profile}-css-before.json"))
        say()
        say(f"== {profile}")
        say(f"{'scene':46s} {'side':7s} {'native':>8s} {'before':>8s} {'after':>8s} "
            f"{'d(a-b)':>8s} {'a-native':>9s}")
        for scene in sorted(after):
            row_a, row_b = after[scene], before.get(scene)
            if "rimWeb" not in row_a or row_b is None or "rimWeb" not in row_b:
                continue
            tag = "" if any(scene.startswith(s + "__") for s in SOLIDS) else "   (context)"
            for i, side in enumerate(SIDES):
                say(f"{scene:46s} {side:7s} {row_a['rimNative'][i]:8.4f} "
                    f"{row_b['rimWeb'][i]:8.4f} {row_a['rimWeb'][i]:8.4f} "
                    f"{row_a['rimWeb'][i] - row_b['rimWeb'][i]:+8.4f} "
                    f"{row_a['rimWeb'][i] - row_a['rimNative'][i]:+9.4f}{tag}")
        say()
        say("Flatness and the body, per cell:")
        say(f"{'scene':46s} {'flatNat':>8s} {'flatBef':>8s} {'flatAft':>8s} "
            f"{'bodyNat':>8s} {'bodyBef':>8s} {'bodyAft':>8s} {'L-R nat':>8s} {'L-R aft':>8s}")
        for scene in sorted(after):
            row_a, row_b = after[scene], before.get(scene)
            if "rimWeb" not in row_a or row_b is None or "rimWeb" not in row_b:
                continue
            say(f"{scene:46s} {flat(row_a['rimNative']):8.4f} {flat(row_b['rimWeb']):8.4f} "
                f"{flat(row_a['rimWeb']):8.4f} {row_a['bodyNative']:8.4f} "
                f"{row_b['bodyWeb']:8.4f} {row_a['bodyWeb']:8.4f} "
                f"{row_a['rimNative'][2] - row_a['rimNative'][3]:+8.4f} "
                f"{row_a['rimWeb'][2] - row_a['rimWeb'][3]:+8.4f}")
        say()
        say("The CSS tier's own rim on the same cells (the canonical captures; the CSS tier draws")
        say("no sweep, so this column is the record of what the other tier's rim looks like):")
        say(f"{'scene':46s} {'body':>8s} | rim T/B/L/R")
        for scene in sorted(css):
            if "rimWeb" not in css[scene]:
                continue
            say(f"{scene:46s} {css[scene]['bodyWeb']:8.4f} | "
                + " ".join(f"{v:.4f}" for v in css[scene]["rimWeb"]))

    say()
    say("== the reference's own flatness, gathered — the light bed's verdict")
    say()
    say("Clause 2 asks the reference's per-side rim to be flat within 0.03 before it asks vitrea's")
    say("to match. `T-B` is top minus bottom, `L-R` left minus right, `H-V` the mean of left and")
    say("right minus the mean of top and bottom. A reference with L-R at zero and H-V away from")
    say("zero is lit along one axis and flat along the other; a reference flat on both is flat.")
    say(f"{'profile':38s} {'scene':32s} {'T-B':>8s} {'L-R':>8s} {'H-V':>8s} {'flat':>8s}")
    for profile in PROFILES:
        after = load(os.path.join(args.reads, f"{profile}-webgpu-after.json"))
        for scene in sorted(after):
            if not any(scene.startswith(s + "__") for s in SOLIDS):
                continue
            if "-tint" in scene:
                continue
            rim = after[scene]["rimNative"]
            say(f"{profile:38s} {scene:32s} {rim[0] - rim[1]:+8.4f} {rim[2] - rim[3]:+8.4f} "
                f"{(rim[2] + rim[3]) / 2 - (rim[0] + rim[1]) / 2:+8.4f} {flat(rim):8.4f}")

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "per-side.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
