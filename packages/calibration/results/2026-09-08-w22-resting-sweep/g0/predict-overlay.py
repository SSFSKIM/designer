"""W22 G0 (e2) — what the shipped dark law would put the overlay pane at, and what it reads.

The nested pane's overlay samples the BASE pane's rendered output (`web/scenes.ts`: the overlay
group is declared `dom`, which on the GPU tier resolves to `samplingBackend: "css-backdrop"`, and
the plane sandwich composites the overlay's proxy after the base plane's optics canvas). So the
overlay's backdrop is a known number — the base pane's own measured body — and the shipped dark
response law can be evaluated at it and compared with what the overlay actually drew. If the law
lands near the reference and the capture does not, the miss is in the INPUT the group was handed,
not in the law.

`backdropToneResponse` is reimplemented here term for term from
`packages/renderer-webgpu/src/material.ts` — the monotone Fritsch-Carlson Hermite spline through
the three anchors, with the thin/thick rows blended by `smoothstep(0, 1, thickness)`. It is
reimplemented rather than imported because this is Python; the two are compared on a cell whose
answer is already in the matrix, printed below as the implementation's own check.

Usage: predict-overlay.py --profile-doc <dark profile json> --reads <stack-reads dir>
"""

import argparse
import json
import math
import os


def encode(v):
    return 12.92 * v if v <= 0.0031308 else 1.055 * max(v, 0.0) ** (1 / 2.4) - 0.055


def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def response(encoded_input, thickness, xs, thin, thick):
    f = smoothstep(0.0, 1.0, thickness)
    ys = [thin[i] + (thick[i] - thin[i]) * f for i in range(3)]
    x = min(xs[2], max(xs[0], encoded_input))
    h0, h1 = xs[1] - xs[0], xs[2] - xs[1]
    d0, d1 = (ys[1] - ys[0]) / h0, (ys[2] - ys[1]) / h1
    m1 = 0.0 if d0 * d1 <= 0 else (2 * d0 * d1) / (d0 + d1)
    seg = 0 if x <= xs[1] else 1
    h = h0 if seg == 0 else h1
    t = (x - (xs[0] if seg == 0 else xs[1])) / h
    y0, y1 = (ys[0], ys[1]) if seg == 0 else (ys[1], ys[2])
    s0, s1 = (d0, m1) if seg == 0 else (m1, d1)
    return (y0 * (1 + 2 * t) * (1 - t) ** 2 + s0 * h * t * (1 - t) ** 2
            + y1 * t * t * (3 - 2 * t) + s1 * h * t * t * (t - 1))


def invert(target, thickness, xs, thin, thick):
    """The encoded backdrop input the law would need to produce `target`. Bisection: the law is
    monotone between monotone anchors, which is the whole point of the Hermite form."""
    lo, hi = xs[0], xs[2]
    if target <= response(lo, thickness, xs, thin, thick):
        return float("nan")
    if target >= response(hi, thickness, xs, thin, thick):
        return float("nan")
    for _ in range(80):
        mid = (lo + hi) / 2
        if response(mid, thickness, xs, thin, thick) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-doc", required=True)
    ap.add_argument("--reads", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    patch = json.load(open(args.profile_doc))["patch"]
    xs = patch["backdropToneAnchorX"]
    thin = patch["backdropToneResponseThin"]
    thick = patch["backdropToneResponseThick"]

    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say("W22 G0 (e2) — the overlay pane against the shipped dark law evaluated at its own backdrop")
    say()
    say(f"anchors (encoded)      {xs}")
    say(f"backdropToneResponseThin  {thin}")
    say(f"backdropToneResponseThick {thick}")
    say()
    say("The overlay is 120 x 56 CSS px, well under sizeSpanMin 32 .. sizeSpanMax 96 on its short")
    say("side, so it is a THIN surface and the law is evaluated on the thin row; the thick row is")
    say("printed beside it as the bound in the other direction. `input` is the encoded mean of the")
    say("overlay's backdrop, which is the base pane's own measured body.")
    say()
    say(f"{'profile':38s} {'base body':>10s} {'input':>8s} {'law thin':>9s} {'law thick':>10s} "
        f"{'native over':>12s} {'web over':>9s}")
    for profile in ("apple-macos-26.5-1x-dark-standard", "apple-macos-26.5-2x-dark-standard"):
        path = os.path.join(args.reads, f"{profile}-webgpu.json")
        if not os.path.exists(path):
            continue
        for row in json.load(open(path))["rows"]:
            if "web" not in row:
                continue
            base = row["web"]["baseBody"]
            x = encode(base)
            say(f"{profile:38s} {base:10.4f} {x:8.4f} "
                f"{response(x, 0.0, xs, thin, thick):9.4f} "
                f"{response(x, 1.0, xs, thin, thick):10.4f} "
                f"{row['native']['overBody']:12.4f} {row['web']['overBody']:9.4f}")
            need = invert(row["web"]["overBody"], 0.0, xs, thin, thick)
            say(f"{'':38s} the encoded input the law would need to produce what the overlay DREW: "
                f"{need:.4f} (linear {((need + 0.055) / 1.055) ** 2.4 if need > 0.04045 else need / 12.92:.4f})")

    if args.out:
        with open(args.out, "w") as fh:
            fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
