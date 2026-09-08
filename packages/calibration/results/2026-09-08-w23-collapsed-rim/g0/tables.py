"""W23 G0 (b) — the whole read, as tables: both canonical beds, both probe beds, per side.

One file, so the wave's grounding is in one place. Every number is `read-contour.py`'s (X1): the
excess over the cell's own base summed over the first two CSS px inside a side's contour, linear
Rec.709 luminance, per CSS px, on the straight span with the continuous corner excluded.

Two excesses are printed and they answer different questions. `rim` is the excess over the eroded
BODY — the definition the wave binds and the one the parent's grounding table used. `rimL` is the
excess over the side's OWN neighbouring rows. Over a solid backdrop they agree; over a structured
one the body is not the level under that side's contour, and `rimL` is the one a law may be fitted
on. Both are printed on every row so the difference between them is never hidden inside a verdict.

Usage: tables.py [--out <file>]
"""

import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SIDES = ("top", "bottom", "left", "right")

BEDS = [
    ("light 1x", "canonical-apple-macos-26.5-1x-light-standard"),
    ("light 2x", "canonical-apple-macos-26.5-2x-light-standard"),
    ("dark 1x", "canonical-apple-macos-26.5-1x-dark-standard"),
    ("dark 2x", "canonical-apple-macos-26.5-2x-dark-standard"),
    ("reduced-transparency 1x", "canonical-apple-macos-26.5-1x-light-reduced-transparency"),
    ("increased-contrast 1x", "canonical-apple-macos-26.5-1x-light-increased-contrast"),
]


def fmt(v, width=8, places=4):
    return f"{'-':>{width}}" if v is None or math.isnan(v) else f"{v:+{width}.{places}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say("W23 G0 (b) — the rim read at the contour on every bed, per side")
    say()
    say("native fixtures: apps/reference-apple/fixtures (committed)")
    say("web captures:    packages/calibration/web-captures — the LANDED 0.11.0 bed, matrix 3587400")
    say("instrument:      g0/read-contour.py; body = declared box eroded 6 CSS px; depth 2 CSS px;")
    say("                 straight span with the corner excluded at 1.6x the declared radius")
    say("units:           linear Rec.709 luminance per CSS px")
    say()
    say("A capsule's left and right sides have no straight span (the ends are semicircles) and are")
    say("printed as `-` rather than as a number read across an arc. `toolbar-group` and")
    say("`glass-over-glass` have no single declared box and are skipped entirely.")
    say()

    for label, stem in BEDS:
        for tier in ("webgpu", "css"):
            path = os.path.join(HERE, "reads", f"{stem}-{tier}.json")
            if not os.path.exists(path):
                continue
            data = json.load(open(path))
            say("=" * 118)
            say(f"== {label}, {tier} tier — {data['profile']}")
            say("=" * 118)
            say(f"{'scene':44s} {'set':6s} {'bodyN':>7s} {'bodyW':>7s} | "
                f"{'rim native T/B/L/R':^35s} | {'rim web T/B/L/R':^35s} | {'clipN':>5s} "
                f"{'clipW':>5s}")
            for row in data["rows"]:
                tint = " (tinted)" if row.get("tint") else ""
                web_body = f"{row['bodyWeb']:7.4f}" if "bodyWeb" in row else "      -"
                nat = " ".join(fmt(v) for v in row["rimNative"])
                web = (" ".join(fmt(v) for v in row["rimWeb"]) if "rimWeb" in row else " " * 35)
                clip_n = max(v for v in row["clipNative"] if not math.isnan(v))
                clip_w = (max(v for v in row["clipWeb"] if not math.isnan(v))
                          if "clipWeb" in row else float("nan"))
                say(f"{row['scene'] + tint:44s} {row['set'][:6]:6s} {row['bodyNative']:7.4f} "
                    f"{web_body} | {nat} | {web} | {clip_n:5.2f} "
                    + (f"{clip_w:5.2f}" if not math.isnan(clip_w) else "    -"))
            say()
            say("the same rows against each side's OWN base (`rimL`), which is what a structured")
            say("backdrop's contour has to be read against:")
            say(f"{'scene':44s} {'baseN T/B/L/R':^35s} | {'rimL native':^35s} | "
                f"{'rimL web':^35s}")
            for row in data["rows"]:
                base = " ".join(fmt(v, 8, 4) for v in row["baseNative"])
                nat = " ".join(fmt(v) for v in row["rimLocalNative"])
                web = (" ".join(fmt(v) for v in row["rimLocalWeb"]) if "rimLocalWeb" in row
                       else " " * 35)
                say(f"{row['scene']:44s} {base} | {nat} | {web}")
            say()

    for label, stem in (("W21 probe — the DARK reference on the solid grid", "probe-w21-dark"),
                        ("W9 probe — the LIGHT reference on the same grid", "probe-w9-light")):
        path = os.path.join(HERE, "reads", f"{stem}.json")
        data = json.load(open(path))
        say("=" * 118)
        say(f"== {label} — {data['profile']}")
        if stem == "probe-w9-light":
            say("   the web column is W9-ERA and the material has moved many times since; it is")
            say("   context only, and no fit in this gate reads it. The native column is the law's")
            say("   fitting ground.")
        say("=" * 118)
        say(f"{'scene':44s} {'set':6s} {'bodyN':>7s} | {'rim native T/B/L/R':^35s} | "
            f"{'rimL native T/B/L/R':^35s} | {'clipN':>5s}")
        for row in data["rows"]:
            tint = " (tinted)" if row.get("tint") else ""
            nat = " ".join(fmt(v) for v in row["rimNative"])
            loc = " ".join(fmt(v) for v in row["rimLocalNative"])
            clip_n = max(v for v in row["clipNative"] if not math.isnan(v))
            say(f"{row['scene'] + tint:44s} {row['set'][:6]:6s} {row['bodyNative']:7.4f} | "
                f"{nat} | {loc} | {clip_n:5.2f}")
        say()

    if args.out:
        with open(args.out, "w") as fh:
            fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
