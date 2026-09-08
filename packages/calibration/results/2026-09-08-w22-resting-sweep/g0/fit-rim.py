"""W22 G0 (c) — the LIGHT profile's rim, re-read and re-fitted per side with the band gone.

W21 G1's `fit-rim.py` method, moved to the light bed and widened by one question. W21 fitted
`optics.regular.rimAlpha` on the dark patch over three sides and had to EXCLUDE the left, because
the sweep's band sat on it; with the band gone all four sides are fittable, and the question the
light bed adds is which of the three rim constants its rows separate at all.

## The rows, and why they are the rows

The solid backdrops (`light-solid`, `dark-solid`) crossed with the components the light profiles
carry. Over a solid the rim band holds no backdrop structure, so a side's peak minus that capture's
own body IS the rim's amplitude; over a structured backdrop the same subtraction mixes the rim with
whatever the band covers, so the structured cells are printed as context and never fitted.

## The instrument's one geometric caveat, declared before the number

The declared box's rim band is a RECTANGLE's band, and a rounded shape does not fill it. On the
vertical sides (left, right) the band's columns run the box's full height and lose the two corner
arcs to background; on the horizontal sides they run its full width and lose less, because the box
is wider than it is tall. So a side's peak is a mixture of rim and background whose weight differs
between the horizontal and the vertical pair, and the horizontal-against-vertical gap `H-V` is NOT
a light direction — it is that mixture. This script computes each side's covered fraction from the
declared geometry and prints the level the mixture predicts beside the reading, so the artefact is
visible rather than inferred.

What is NOT contaminated, and is therefore what the fit is stated on:

- **`L-R`** — left minus right. The two sides have identical geometry, so the mixture cancels
  exactly. This is the statistic the sweep destroyed and the gate restores.
- **`T-B`** — top minus bottom. Identical geometry likewise. This is the statistic a light
  direction with a vertical component moves, and therefore the one that separates `specularGain`.

## The objective, declared before the number

The mean over the fitted rows of |excess_web - excess_native|, per side, exactly W21's. `rimAlpha`
is additive in the shader (`rim = rimWeight * (rimAlpha + specular)`), so two rendered points fix
the line per row and the per-row answers' spread is S5's test of whether the rows separate it.

    fit-rim.py --native <read.json> <rimAlpha>=<read.json> ... [--baseline <label>=<read.json>]
               [--scenes <scenes.json>] [--out <file>]
"""

import argparse
import json
import math

SIDES = ("top", "bottom", "left", "right")


def load(path):
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def excess(row, which):
    body = row[f"body{which}"]
    return [peak - body for peak in row[f"rim{which}"]]


def covered_fraction(width, height, radius, band, side):
    """The fraction of a side's band that the rounded shape actually fills.

    A band column at horizontal distance `dx` from the box edge meets the shape over the box's full
    height minus the two corner arcs' shortfall, `2 * (radius - sqrt(radius^2 - (radius - dx)^2))`
    where `dx < radius`. Averaged over the band's width. The horizontal sides are the same integral
    with the axes swapped. This is geometry, not a fit: it is what the declared box's band contains
    and what the peak statistic therefore averages over.
    """
    long_side, short_side = (width, height) if side in ("top", "bottom") else (height, width)
    steps = 200
    total = 0.0
    for i in range(steps):
        d = band * (i + 0.5) / steps
        if d < radius:
            shortfall = 2.0 * (radius - math.sqrt(max(radius * radius - (radius - d) ** 2, 0.0)))
        else:
            shortfall = 0.0
        total += max(long_side - shortfall, 0.0) / long_side
    return total / steps


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True, help="any read of the same bed; the native "
                                                        "columns are identical across them")
    parser.add_argument("reads", nargs="+", help="<rimAlpha>=<read.json>, specularGain 0")
    parser.add_argument("--baseline", default=None, help="<label>=<read.json> — the shipped "
                                                         "constants at the gate, for the "
                                                         "specular's own rows")
    parser.add_argument("--scenes", default=None)
    parser.add_argument("--band", type=float, default=3.0)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    points = sorted((float(a), load(p)) for a, p in (e.split("=", 1) for e in args.reads))
    native = load(args.native)
    baseline_label, baseline = (None, None)
    if args.baseline is not None:
        baseline_label, path = args.baseline.split("=", 1)
        baseline = load(path)

    geometry = {}
    if args.scenes:
        spec = json.load(open(args.scenes))
        for scene in spec["scenes"]:
            component = spec["components"][scene["component"]]
            if "size" not in component:
                continue
            width, height = component["size"]
            radius = (component.get("radius") if component["kind"] == "rrect"
                      else min(width, height) / 2)
            geometry[scene["id"]] = {
                side: covered_fraction(width, height, radius, args.band, side) for side in SIDES
            }

    solids = sorted(s for s in native if s.split("__")[0].endswith("solid") and "-tint" not in s)
    others = sorted(s for s in native if s not in solids and "-tint" not in s)

    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say("W22 G0 — optics.regular.rimAlpha / specularGain / lightDirection on the LIGHT profile,")
    say("re-read per side with the resting sweep gone")
    say()
    say("Every number is (side peak - that capture's own body) under the declared geometry: the rim")
    say("band is the declared box's outer 3 CSS px and a side's peak is the largest row or column")
    say("mean inside it (W22 X2). The rendered points carry specularGain 0; the baseline column")
    say("carries the SHIPPED constants (rimAlpha 0.18, specularGain 0.55) at the gate, so the")
    say("difference between it and the a=0.18 point is the specular term and nothing else.")
    say()

    header = f"{'scene':32s} {'side':7s} {'native':>8s}"
    if baseline is not None:
        header += f" {'shipped':>8s}"
    for alpha, _rows in points:
        header += f" {'a=' + format(alpha, '.2f'):>8s}"
    if geometry:
        header += f" {'covered':>8s}"
    say("== the solid rows (fitted)")
    say(header)
    for scene in solids:
        native_excess = excess(native[scene], "Native")
        for index, side in enumerate(SIDES):
            row = f"{scene:32s} {side:7s} {native_excess[index]:8.4f}"
            if baseline is not None:
                row += (f" {excess(baseline[scene], 'Web')[index]:8.4f}"
                        if "bodyWeb" in baseline.get(scene, {}) else "        -")
            for _alpha, rows in points:
                row += (f" {excess(rows[scene], 'Web')[index]:8.4f}"
                        if "bodyWeb" in rows.get(scene, {}) else "        -")
            if geometry and scene in geometry:
                row += f" {geometry[scene][side]:8.3f}"
            say(row)

    say()
    say("== the two contamination-free contrasts")
    say()
    say("L-R cancels the band's corner mixture exactly (identical geometry); T-B likewise. A")
    say("reference whose L-R is zero has no horizontal light; one whose T-B is zero has no vertical")
    say("light, and then the specular term is fitting nothing.")
    columns = ["native"] + ([baseline_label] if baseline is not None else []) + [
        f"a={alpha:.2f}" for alpha, _r in points
    ]
    say(f"{'scene':32s} {'stat':5s} " + " ".join(f"{c:>9s}" for c in columns))
    for scene in solids:
        sources = [("Native", native)] + ([("Web", baseline)] if baseline is not None else []) + [
            ("Web", rows) for _a, rows in points
        ]
        for stat, i, j in (("L-R", 2, 3), ("T-B", 0, 1)):
            cells = []
            for which, rows in sources:
                if scene not in rows or (which == "Web" and "bodyWeb" not in rows[scene]):
                    cells.append("        -")
                    continue
                e = excess(rows[scene], which)
                cells.append(f"{e[i] - e[j]:+9.4f}")
            say(f"{scene:32s} {stat:5s} " + " ".join(cells))

    say()
    say("== the line excess(rimAlpha) = m*rimAlpha + c per row, and the rimAlpha that row alone")
    say("would choose (S5's test: what has to be legible is whether the per-row answers agree)")
    say(f"{'scene':32s} {'side':7s} {'m':>8s} {'c':>8s} {'target':>8s} {'rimAlpha*':>10s}")
    model = []
    for scene in solids:
        native_excess = excess(native[scene], "Native")
        for index, side in enumerate(SIDES):
            if any(scene not in rows or "bodyWeb" not in rows[scene] for _a, rows in points):
                continue
            xs = [alpha for alpha, _r in points]
            ys = [excess(rows[scene], "Web")[index] for _a, rows in points]
            slope = (ys[-1] - ys[0]) / (xs[-1] - xs[0])
            intercept = ys[0] - slope * xs[0]
            target = native_excess[index]
            want = (target - intercept) / slope if slope != 0 else float("nan")
            model.append((scene, side, slope, intercept, target))
            say(f"{scene:32s} {side:7s} {slope:8.4f} {intercept:8.4f} {target:8.4f} {want:10.4f}")

    live = [e for e in model if e[2] != 0]
    dead = sorted({e[0] for e in model if e[2] == 0})
    say()
    if dead:
        say("Rows the constant cannot reach — the rim is folded out of the capture entirely "
            f"(recorded, not fitted): {', '.join(dead)}")
    if live:
        best, best_error = 0.0, None
        alpha = 0.0
        while alpha <= 0.60 + 1e-9:
            error = sum(abs(m * alpha + c - t) for _s, _d, m, c, t in live) / len(live)
            if best_error is None or error < best_error:
                best, best_error = alpha, error
            alpha += 0.0001
        say(f"The pooled minimiser over the {len(live)} live rows: rimAlpha = {best:.4f}, "
            f"mean |d excess| {best_error:.4f}")
        wants = sorted((t - c) / m for _s, _d, m, c, t in live)
        say(f"the per-row answers span {wants[0]:.4f} to {wants[-1]:.4f}, "
            f"median {wants[len(wants) // 2]:.4f}")
        for alpha, _rows in points:
            err = sum(abs(m * alpha + c - t) for _s, _d, m, c, t in live) / len(live)
            say(f"  the objective at the rendered rimAlpha {alpha:.2f}: {err:.4f}")
        if baseline is not None:
            errs = []
            for scene, side, _m, _c, target in live:
                index = SIDES.index(side)
                errs.append(abs(excess(baseline[scene], "Web")[index] - target))
            say(f"  the objective at the SHIPPED constants ({baseline_label}, specularGain 0.55): "
                f"{sum(errs) / len(errs):.4f}")

    say()
    say("== recorded, not fitted — the structured and impulse rows under the same points")
    say(header)
    for scene in others:
        if scene not in native:
            continue
        native_excess = excess(native[scene], "Native")
        for index, side in enumerate(SIDES):
            row = f"{scene:32s} {side:7s} {native_excess[index]:8.4f}"
            if baseline is not None:
                row += (f" {excess(baseline[scene], 'Web')[index]:8.4f}"
                        if "bodyWeb" in baseline.get(scene, {}) else "        -")
            for _alpha, rows in points:
                row += (f" {excess(rows[scene], 'Web')[index]:8.4f}"
                        if "bodyWeb" in rows.get(scene, {}) else "        -")
            if geometry and scene in geometry:
                row += f" {geometry[scene][side]:8.3f}"
            say(row)

    if args.out is not None:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")
        print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
