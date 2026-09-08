"""W23 G0 (f) — the rim's WIDTH: the profile across the contour, row by row, reference against web.

The amplitude law and the band's shape are two different questions and the two-CSS-px sum answers
only the first. §5.99 read the shape once, on one cell: the reference's rim is one CSS px wide with
an inner shoulder (2x rows 0.744 / 0.629 over a 0.481 body) while vitrea's `rimWidth` 1.5 with a
squared falloff puts 69 % / 25 % of its peak where the reference has 100 % / 56 %. This reads the
same profile on every solid cell of both beds at both scales, as a fraction of the FIRST row's own
excess, so the shape is separated from the amplitude and the two verdicts do not contaminate each
other.

Usage: width.py [--captures <dir>] [--out <file>]
"""

import argparse
import importlib.util
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = "/Users/new/Developer/GitHub/designer"
WORKTREE = "/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-aa0ee5ea92534c3fd"

spec = importlib.util.spec_from_file_location("rc", os.path.join(HERE, "read-contour.py"))
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

CELLS = (
    ("apple-macos-26.5-1x-light-standard", "dark-solid__rrect-md__rest"),
    ("apple-macos-26.5-1x-light-standard", "light-solid__rrect-md__rest"),
    ("apple-macos-26.5-1x-light-standard", "impulse__rrect-md__rest"),
    ("apple-macos-26.5-2x-light-standard", "dark-solid__rrect-md__rest"),
    ("apple-macos-26.5-2x-light-standard", "light-solid__rrect-md__rest"),
    ("apple-macos-26.5-2x-light-standard", "impulse__rrect-md__rest"),
    ("apple-macos-26.5-1x-dark-standard", "dark-solid__rrect-md__rest"),
    ("apple-macos-26.5-2x-dark-standard", "dark-solid__rrect-md__rest"),
    ("apple-macos-26.5-1x-dark-standard", "dark-solid__capsule-button__rest"),
    ("apple-macos-26.5-2x-dark-standard", "dark-solid__capsule-button__rest"),
)
DEPTH = 4.0


def profile_rows(path, canvas, geom, corner=1.6):
    rgb = rc.rgb_of(path)
    lum = rc.luma_of_rgb(rgb)
    scale = lum.shape[1] / canvas["width"]
    _body, sides = rc.contour_read(lum, rgb, canvas, geom, scale, 6.0, DEPTH, corner)
    return scale, sides["top"]["rows"], sides["top"]["base"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", default=f"{MAIN}/packages/calibration/web-captures")
    ap.add_argument("--label", default="landed")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    lines = []

    def say(t=""):
        lines.append(t)
        print(t)

    spec_json = json.load(open(os.path.join(WORKTREE, "apps/reference-apple/scenes.json")))
    canvas = spec_json["canvas"]
    scenes = {s["id"]: s for s in spec_json["scenes"]}

    say("W23 G0 (f) — the rim's profile across the contour, top side, straight span")
    say()
    say(f"Rows are DEVICE pixels inward from the declared box's first pixel, over {DEPTH:.0f} CSS px.")
    say("`excess` is over the side's own base (the rows from 4 to 8 CSS px in). `%peak` is that")
    say("row's excess as a fraction of the FIRST row's, which is the shape with the amplitude")
    say("divided out — the number `rimWidth` and the falloff are read on.")
    say()
    for profile, scene in CELLS:
        geom = rc.component_geometry(spec_json["components"], scenes[scene]["component"])
        nat = os.path.join(MAIN, "apps/reference-apple/fixtures", profile, f"{scene}.png")
        web = os.path.join(args.captures, profile, scene, f"{scene}__webgpu.png")
        if not os.path.exists(nat):
            continue
        scale, nrows, nbase = profile_rows(nat, canvas, geom)
        have_web = os.path.exists(web)
        if have_web:
            _s, wrows, wbase = profile_rows(web, canvas, geom)
        say(f"== {profile}  {scene}   (scale {scale:.0f}x)")
        say(f"   {'row':>4s} {'depth px':>9s} | {'ref lin':>8s} {'excess':>8s} {'%peak':>7s} | "
            + (f"{'web lin':>8s} {'excess':>8s} {'%peak':>7s}" if have_web else ""))
        n0 = nrows[0] - nbase
        w0 = (wrows[0] - wbase) if have_web else float("nan")
        for k, v in enumerate(nrows):
            e = v - nbase
            line = (f"   {k:4d} {(k + 0.5) / scale:9.2f} | {v:8.4f} {e:8.4f} "
                    f"{(e / n0 * 100 if n0 else float('nan')):6.1f}% |")
            if have_web:
                ew = wrows[k] - wbase
                line += (f" {wrows[k]:8.4f} {ew:8.4f} "
                         f"{(ew / w0 * 100 if w0 else float('nan')):6.1f}%")
            say(line)
        say()

    if args.out:
        with open(args.out, "w") as fh:
            fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
