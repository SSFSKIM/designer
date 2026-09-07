"""W21 G1 fit 1 — `optics.regular.rimAlpha` on the six solid cells' rim excess, per side.

## The rows, and why they are the rows

W21 Decision Log 2 (b) and contract X1. The rim is fitted on the probe's two dark solids crossed
with three sizes — `dark-solid` and `mid-dark-solid` at `rrect-sm`, `-md` and `-lg`. Over a solid
backdrop the rim band carries no backdrop structure, so a side's peak minus that capture's own body
IS the rim's amplitude and nothing else; over a structured backdrop the same subtraction mixes the
rim with whatever checker or glyph the band happens to cover. Two rows of three cells, one
constant. The reference's excess is 0.0131–0.0187 over `dark-solid` and 0.0342–0.0387 over
`mid-dark-solid` (claims §5.89 §5 quotes the same rows to two decimals).

## The instrument's one exclusion, declared before the number

The fit runs on the TOP, BOTTOM and RIGHT sides and not on the left. The reason is a measurement,
not a convenience: at `specularGain` 0 vitrea's left edge still reads 0.12–0.15 above its other
three sides on every solid, and the pair of renders `sweep0-rim002` / `sweep0-rim018` — the same
documents with `sweepGain` 0 and nothing else — collapses left onto right to the fourth decimal
while leaving top, bottom and right byte-identical. The highlight pass's specular sweep is a
Gaussian band centred at the driver's `sweep` channel, which at rest is 0, and 0 radians in the
gradient's angular coordinate is the left edge; so a resting surface carries a stationary shimmer
there. That term is not `specularGain`, it is not in the dark patch's reach without also removing
the dark scheme's shimmer animation, and a renderer-side fix would move the light captures this
gate binds byte-identical (X3, S4). It is therefore REPORTED, not fitted, and the left side is
carried as a recorded column throughout.

Top, bottom and right are unaffected by the sweep to four decimals, so a constant fitted on them is
a constant fitted at the landed configuration.

## The objective, declared before the number

The mean over the eighteen rows (six cells x three sides) of |excess_web − excess_native|. Per side
rather than per cell because `specularGain` 0 makes the sides one quantity and the reference agrees
to 0.001–0.004 across them: a per-cell mean would hide a side that missed.

The renderer adds the rim as `colour = (colour·bodyAlpha + rim) / (bodyAlpha + rim)` with
`rim = rimWeight · (rimAlpha + specular)` (`wgsl/optics.ts`), so at `specularGain` 0 the excess is
linear in `rimAlpha` up to the body's own composite. Two rendered points therefore determine the
line per row and a third confirms it against the reference directly.

    fit-rim.py <rimAlpha>=<read.json> ... [--confirm <rimAlpha>=<read.json>]
                [--sweep-off <label>=<read.json> ...] [--out <file>]
"""

import argparse
import json
import os

SOLIDS = [
    f"{background}__rrect-{size}__rest"
    for background in ("dark-solid", "mid-dark-solid")
    for size in ("sm", "md", "lg")
]
SIDES = ("top", "bottom", "left", "right")
FITTED_SIDES = (0, 1, 3)


def load(path):
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def excess(row, which):
    body = row[f"body{which}"]
    return [peak - body for peak in row[f"rim{which}"]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reads", nargs="+", help="<rimAlpha>=<read.json>")
    parser.add_argument("--confirm", default=None, help="<rimAlpha>=<read.json>")
    parser.add_argument("--sweep-off", nargs="*", default=[],
                        help="<label>=<sweep-on read.json>,<sweep-off read.json>")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    points = sorted((float(a), load(p)) for a, p in (e.split("=", 1) for e in args.reads))
    native = points[0][1]

    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say("W21 G1 fit 1 — optics.regular.rimAlpha, on the six solid cells' rim excess per side")
    say()
    say("Every number is (side peak − that capture's own body) under the declared geometry: the")
    say("rim band is the declared box's outer 3 CSS px and a side's peak is the largest row or")
    say("column mean inside it (the wave's instrument, X2). specularGain 0 throughout.")
    say()
    header = f"{'scene':32s} {'side':7s} {'native':>8s}"
    for alpha, _rows in points:
        header += f" {'a=' + format(alpha, '.2f'):>8s}"
    header += f"  {'fitted':>7s}"
    say(header)
    for scene in SOLIDS:
        native_excess = excess(native[scene], "Native")
        for index, side in enumerate(SIDES):
            row = f"{scene:32s} {side:7s} {native_excess[index]:8.4f}"
            for _alpha, rows in points:
                row += f" {excess(rows[scene], 'Web')[index]:8.4f}"
            row += f"  {'yes' if index in FITTED_SIDES else 'no (sweep)':>7s}"
            say(row)

    say()
    say("The line excess(rimAlpha) = m·rimAlpha + c per fitted row, and the rimAlpha that row")
    say("alone would choose. S5's test: a constant whose rows do not separate it is declined, so")
    say("what has to be legible here is whether the per-row answers agree.")
    say(f"{'scene':32s} {'side':7s} {'m':>8s} {'c':>8s} {'target':>8s} {'rimAlpha*':>10s}")
    rows_model = []
    for scene in SOLIDS:
        native_excess = excess(native[scene], "Native")
        for index in FITTED_SIDES:
            xs = [alpha for alpha, _r in points]
            ys = [excess(rows[scene], "Web")[index] for _a, rows in points]
            slope = (ys[-1] - ys[0]) / (xs[-1] - xs[0])
            intercept = ys[0] - slope * xs[0]
            target = native_excess[index]
            want = (target - intercept) / slope if slope != 0 else float("nan")
            rows_model.append((scene, SIDES[index], slope, intercept, target))
            say(f"{scene:32s} {SIDES[index]:7s} {slope:8.4f} {intercept:8.4f} {target:8.4f} "
                f"{want:10.4f}")

    live = [entry for entry in rows_model if entry[2] != 0]
    dead = sorted({entry[0] for entry in rows_model if entry[2] == 0})
    say()
    if dead:
        say("Cells whose rim the constant cannot reach because vitrea's collapse folds the rim out "
            f"(recorded, not fitted; Decision Log 2 (b) defers the collapsed rim): {', '.join(dead)}")
    best, best_error = 0.0, None
    alpha = 0.0
    while alpha <= 0.40 + 1e-9:
        error = sum(abs(m * alpha + c - t) for _s, _d, m, c, t in live) / len(live)
        if best_error is None or error < best_error:
            best, best_error = alpha, error
        alpha += 0.0001
    say(f"The pooled minimiser over the {len(live)} live rows: rimAlpha = {best:.4f}, "
        f"mean |Δexcess| {best_error:.4f}")
    wants = sorted((t - c) / m for _s, _d, m, c, t in live)
    say(f"the per-row answers span {wants[0]:.4f} to {wants[-1]:.4f}, median {wants[len(wants) // 2]:.4f}")

    if args.sweep_off:
        say()
        say("The recorded term — the highlight pass's stationary specular sweep, isolated. The same")
        say("documents with sweepGain 0 and nothing else, so the difference is that term alone:")
        say(f"{'scene':32s} {'side':7s} {'sweep on':>9s} {'sweep off':>10s} {'Δ':>9s}")
        for entry in args.sweep_off:
            label, paths = entry.split("=", 1)
            on_path, off_path = paths.split(",", 1)
            on, off = load(on_path), load(off_path)
            say(f"  [{label}]")
            for scene in SOLIDS:
                for index, side in enumerate(SIDES):
                    a = excess(on[scene], "Web")[index]
                    b = excess(off[scene], "Web")[index]
                    say(f"{scene:32s} {side:7s} {a:9.4f} {b:10.4f} {b - a:+9.4f}")

    if args.confirm is not None:
        alpha, path = args.confirm.split("=", 1)
        rows = load(path)
        say()
        say(f"Confirmation — rendered at rimAlpha {alpha} with specularGain 0, against the reference:")
        say(f"{'scene':32s} {'side':7s} {'native':>8s} {'web':>8s} {'Δ':>9s} {'clause 4':>9s}")
        errors, worst = [], 0.0
        for scene in SOLIDS:
            native_excess = excess(native[scene], "Native")
            web_excess = excess(rows[scene], "Web")
            for index, side in enumerate(SIDES):
                delta = web_excess[index] - native_excess[index]
                if index in FITTED_SIDES:
                    errors.append(abs(delta))
                    worst = max(worst, abs(delta))
                say(f"{scene:32s} {side:7s} {native_excess[index]:8.4f} {web_excess[index]:8.4f} "
                    f"{delta:+9.4f} {'MET' if abs(delta) <= 0.03 else 'MISSED':>9s}")
        say(f"mean |Δexcess| over the {len(errors)} fitted rows: {sum(errors) / len(errors):.4f}; "
            f"worst {worst:.4f}")
        say()
        say("Flatness — max side minus min side, the reference's against vitrea's, over the three")
        say("fitted sides and over all four (clause 4 asks for the reference's flatness within 0.03):")
        say(f"{'scene':32s} {'nat T/B/R':>10s} {'web T/B/R':>10s} {'nat all':>8s} {'web all':>8s}")
        for scene in SOLIDS:
            native_excess = excess(native[scene], "Native")
            web_excess = excess(rows[scene], "Web")
            three_n = [native_excess[i] for i in FITTED_SIDES]
            three_w = [web_excess[i] for i in FITTED_SIDES]
            say(f"{scene:32s} {max(three_n) - min(three_n):10.4f} {max(three_w) - min(three_w):10.4f} "
                f"{max(native_excess) - min(native_excess):8.4f} "
                f"{max(web_excess) - min(web_excess):8.4f}")
        say()
        say("Recorded, not fitted — the `light-solid` cells under the same constant. The reference's")
        say("own horizontal-against-vertical split lives here (claims §5.89 §5) and no dark")
        say("canonical cell shows it:")
        say(f"{'scene':32s} {'side':7s} {'native':>8s} {'web':>8s} {'Δ':>9s}")
        for scene in sorted(s for s in rows if s.startswith("light-solid__")):
            if "bodyWeb" not in rows[scene]:
                continue
            native_excess = excess(native[scene], "Native")
            web_excess = excess(rows[scene], "Web")
            for index, side in enumerate(SIDES):
                say(f"{scene:32s} {side:7s} {native_excess[index]:8.4f} {web_excess[index]:8.4f} "
                    f"{web_excess[index] - native_excess[index]:+9.4f}")

    if args.out is not None:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")
        print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
