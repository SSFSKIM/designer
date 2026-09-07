"""W21 G1 fit 2 — `optics.regular.tintAlpha` on the passthrough rows.

## The rows, and why they are the rows

W21 Decision Log 2 (c) and contract X1. `pass` is the body's own standard deviation over the
backdrop's standard deviation under the same declared footprint — the fraction of the structure on
offer that the material let through, which is exactly the quantity a lerp's alpha sets. The fit runs
on the CHECKERBOARD PITCH SWEEP at fixed component: `rrect-sm`, `rrect-md` and `rrect-lg` over
`checkerboard-4`, `checkerboard` (pitch 16), `checkerboard-32` and `checkerboard-64`. A pitch sweep
at one component is a modulation-transfer curve, so it separates the alpha — which scales the whole
curve — from the blur, which changes its shape with pitch; claims §5.89 §4 reports the shortfall as
roughly constant in `pass` rather than growing with pitch, so it is the amplitude that is wrong.

Excluded, each for a stated reason rather than by convenience:

  * `checkerboard-64__rrect-sm` — its footprint lies inside one white checker, so the backdrop
    offers no structure (`bgSd` 0.0000) and `pass` is undefined;
  * `checkerboard-64__rrect-lg` — the grid carries no such cell;
  * `hc-text__rrect-sm` — 4-of-7 between the material's two appearances, too close to call
    (Decision Log 2 (c) puts it in no fit). The other `hc-text` rows are a second backdrop family
    rather than a pitch sweep and are REPORTED beside the fit, not fitted on;
  * `checkerboard-lc16` — the equal-mean partner. It is the CHECK, not a fit row: it holds the
    encoded mean of `checkerboard` while offering 0.568 of its structure, so a constant fitted on
    the sweep has to land it without being told about it.

## The objective, and the constraint on it, both declared before the number

Objective: the mean over the fit rows of |ln(pass_web / pass_native)| — a ratio objective, because
`pass` runs from 0.014 to 0.134 across the sweep and an absolute objective would be a fit to the
largest pitch alone. The wave's target is a factor of 1.5, and ln(1.5) = 0.405, so the objective is
directly comparable to it.

Constraint: the BODY has to stay where the response law put it. Under the solve the level belongs to
the law and not to the alpha (W21 Design; claims §5.34), and that separation is the only reason the
alpha is free to carry the passthrough at all — but the separation holds only while the solve has
headroom to hold the level, and G0 measured the dark remainder running DOWNWARD into the black clamp
(claims §5.88 §3). So the alpha is swept and the body is read at every point.

The constraint is stated on the separation rather than on the clause, and the difference matters. A
clause-shaped constraint ("the body still within 0.010") would put the answer exactly where the
solve has begun to lose the level and has not yet lost enough of it to fail — a cliff edge, chosen
on the probe grid and applied to a canonical bed whose cells sit somewhere else on the same curve.
The measured boundary is the plateau: above `PLATEAU_ALPHA` the body is flat in the alpha to 0.0002,
which is the separation the design assumed, and the admissible range is where the body is within the
reader's own recovery bound (0.0028, claims §5.88 §1) of that plateau. Both readings are reported —
the unconstrained minimiser, the clause-constrained one and the separation-constrained one — so the
cost of taking the safe side of the cliff is on the page rather than in the choice.

The constraint is evaluated on the THICK rows (`rrect-md`, `rrect-lg`). The thin rows carry the
appearance term Decision Log 2 (a) defers by name, and their body error is a residual of that term
rather than of the alpha; they are reported and never constrain.

The sweep is rendered rather than modelled. A lerp's `k·(1 − alpha)` is exact only where the solve
is not clamping, which is the very thing being tested, so between rendered points this interpolates
linearly in alpha and never extrapolates past the ends.

    fit-alpha.py <tintAlpha>=<read.json> ... [--confirm <tintAlpha>=<read.json>] [--out <file>]
"""

import argparse
import json
import math

COMPONENTS = ("rrect-sm", "rrect-md", "rrect-lg")
PITCHES = (("checkerboard-4", 4), ("checkerboard", 16), ("checkerboard-32", 32),
           ("checkerboard-64", 64))
EQUAL_MEAN = ("checkerboard", "checkerboard-lc16")
BESIDE = ("hc-text-7", "hc-text", "hc-text-28")
THICK = ("rrect-md", "rrect-lg")
BODY_CLAUSE = 0.010
PLATEAU_ALPHA = 0.92
RECOVERY_BOUND = 0.0028


def load(path):
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def passes(row, which):
    return None if row["backdropSd"] <= 1e-6 else row[f"sd{which}"] / row["backdropSd"]


def interpolate(xs, ys, x):
    """Linear in alpha between rendered points; clamped to the swept ends, never extrapolated."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for index in range(1, len(xs)):
        if x <= xs[index]:
            span = xs[index] - xs[index - 1]
            t = (x - xs[index - 1]) / span
            return ys[index - 1] + t * (ys[index] - ys[index - 1])
    return ys[-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reads", nargs="+", help="<tintAlpha>=<read.json>")
    parser.add_argument("--confirm", default=None, help="<tintAlpha>=<read.json>")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    points = sorted((float(a), load(p)) for a, p in (e.split("=", 1) for e in args.reads))
    alphas = [alpha for alpha, _rows in points]
    native = points[0][1]

    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    def columns(label_width, first):
        return f"{first:{label_width}s}" + "".join(f" {'a=' + format(a, '.2f'):>8s}" for a in alphas)

    say("W21 G1 fit 2 — optics.regular.tintAlpha, on the checkerboard pitch sweep's passthrough")
    say()
    say("pass = body sd / backdrop sd under the declared footprint. specularGain 0 and rimAlpha at")
    say("the fit-1 value on every candidate, so the only thing moving between columns is the alpha.")
    say()
    say(columns(37, f"{'component':10s} {'background':18s} {'native':>7s}"))
    fit_rows = []
    for component in COMPONENTS:
        for background, _pitch in PITCHES:
            scene = f"{background}__{component}__rest"
            row = native.get(scene)
            if row is None:
                continue
            reference = passes(row, "Native")
            if reference is None:
                say(f"{component:10s} {background:18s} {'—':>7s}   (no structure under the "
                    f"footprint; excluded)")
                continue
            series = [passes(rows[scene], "Web") for _a, rows in points]
            say(f"{component:10s} {background:18s} {reference:7.4f}" +
                "".join(f" {value:8.4f}" for value in series))
            fit_rows.append((scene, component, background, reference, series))
    say(f"{len(fit_rows)} fit rows")

    # The body, on the same rows and the same candidates: the constraint, read rather than assumed.
    body_rows = []
    for component in COMPONENTS:
        for background, _pitch in PITCHES:
            scene = f"{background}__{component}__rest"
            row = native.get(scene)
            if row is None:
                continue
            body_rows.append((scene, row["bodyNative"],
                              [rows[scene]["bodyWeb"] for _a, rows in points]))

    say()
    say("The body beside the sd — the constraint. Under the solve the level should not move with")
    say("the alpha; where it does, the solve has run out of headroom (the black clamp, §5.88 §3).")
    say(columns(37, f"{'component':10s} {'background':18s} {'native':>7s}"))
    for scene, reference, series in body_rows:
        background, component, _rest = scene.split("__")
        say(f"{component:10s} {background:18s} {reference:7.4f}" +
            "".join(f" {value:8.4f}" for value in series))
    say(f"{'':29s} {'mean |Δ|':>7s}" +
        "".join(f" {sum(abs(s[index] - r) for _n, r, s in body_rows) / len(body_rows):8.4f}"
                for index in range(len(alphas))))
    say(f"{'':29s} {'worst':>7s}" +
        "".join(f" {max(abs(s[index] - r) for _n, r, s in body_rows):8.4f}"
                for index in range(len(alphas))))

    thick_rows = [entry for entry in body_rows if entry[0].split("__")[1] in THICK]
    plateau = {
        scene: interpolate(alphas, series, PLATEAU_ALPHA) for scene, _reference, series in thick_rows
    }

    say()
    say("The two curves against alpha, on a grid interpolated between the rendered points.")
    say(f"`worst |Δbody|` is against the reference on the thick rows (the wave's clause 3, "
        f"{BODY_CLAUSE:.3f}); `drift` is the same rows against their own value on the clamp-free")
    say(f"plateau at alpha {PLATEAU_ALPHA} (the separation, {RECOVERY_BOUND:.4f} — the reader's "
        f"recovery bound).")
    say(f"{'alpha':>7s} {'|ln ratio|':>11s} {'factor':>8s} {'worst |Δbody|':>14s} {'clause':>7s} "
        f"{'drift':>8s} {'separated':>10s}")
    grid = []
    step = 0.0025
    alpha = alphas[0]
    while alpha <= alphas[-1] + 1e-9:
        objective = sum(
            abs(math.log(interpolate(alphas, series, alpha) / reference))
            for _s, _c, _b, reference, series in fit_rows
        ) / len(fit_rows)
        worst = max(
            abs(interpolate(alphas, series, alpha) - reference)
            for _s, reference, series in thick_rows
        )
        drift = max(
            abs(interpolate(alphas, series, alpha) - plateau[scene])
            for scene, _reference, series in thick_rows
        )
        grid.append((alpha, objective, worst, drift))
        alpha += step
    for alpha, objective, worst, drift in grid:
        if abs(alpha * 200 - round(alpha * 200)) < 1e-6:  # print every 0.005
            say(f"{alpha:7.3f} {objective:11.4f} {math.exp(objective):8.3f} {worst:14.4f} "
                f"{'met' if worst <= BODY_CLAUSE else 'MISSED':>7s} {drift:8.4f} "
                f"{'yes' if drift <= RECOVERY_BOUND else 'no':>10s}")
    free = min(grid, key=lambda entry: entry[1])
    say(f"unconstrained minimiser: alpha {free[0]:.4f}, factor {math.exp(free[1]):.3f}, "
        f"worst |Δbody| {free[2]:.4f}, drift {free[3]:.4f}")
    for name, admissible in (
        ("the clause", [entry for entry in grid if entry[2] <= BODY_CLAUSE]),
        ("the separation", [entry for entry in grid if entry[3] <= RECOVERY_BOUND]),
    ):
        if not admissible:
            say(f"constrained by {name}: no swept alpha qualifies")
            continue
        bound = min(admissible, key=lambda entry: entry[1])
        say(f"constrained by {name}: the range opens at alpha "
            f"{min(entry[0] for entry in admissible):.4f}; the objective's minimiser inside it is "
            f"alpha {bound[0]:.4f} at factor {math.exp(bound[1]):.3f} "
            f"(worst |Δbody| {bound[2]:.4f}, drift {bound[3]:.4f})")

    say()
    say("Per row at each rendered alpha, the factor against the reference (the shape of what one")
    say("constant can and cannot close):")
    say(columns(37, f"{'component':10s} {'background':18s} {'native':>7s}"))
    for _scene, component, background, reference, series in fit_rows:
        say(f"{component:10s} {background:18s} {reference:7.4f}" +
            "".join(f" {max(value / reference, reference / value):8.3f}" for value in series))

    say()
    say("The equal-mean pair, the check the fit is not told about: `checkerboard` and")
    say("`checkerboard-lc16` hold the same encoded mean and differ in structure by 0.568.")
    say(columns(41, f"{'component':10s} {'background':22s} {'native':>7s}"))
    for component in COMPONENTS:
        for background in EQUAL_MEAN:
            scene = f"{background}__{component}__rest"
            row = native.get(scene)
            if row is None:
                continue
            say(f"{component:10s} {background:22s} {passes(row, 'Native'):7.4f}" +
                "".join(f" {passes(rows[scene], 'Web'):8.4f}" for _a, rows in points))

    say()
    say("Reported beside the fit, never fitted on — the text backdrops. `hc-text__rrect-sm` is the")
    say("4-of-7 cell Decision Log 2 (c) keeps out of every fit and is marked.")
    say(columns(37, f"{'component':10s} {'background':18s} {'native':>7s}"))
    for component in COMPONENTS:
        for background in BESIDE:
            scene = f"{background}__{component}__rest"
            row = native.get(scene)
            if row is None:
                continue
            mark = "  (bistable, in no fit)" if scene == "hc-text__rrect-sm__rest" else ""
            say(f"{component:10s} {background:18s} {passes(row, 'Native'):7.4f}" +
                "".join(f" {passes(rows[scene], 'Web'):8.4f}" for _a, rows in points) + mark)

    if args.confirm is not None:
        alpha, path = args.confirm.split("=", 1)
        rows = load(path)
        say()
        say(f"Confirmation — rendered at tintAlpha {alpha}, against the reference:")
        say(f"{'component':10s} {'background':18s} {'native':>8s} {'web':>8s} {'factor':>8s} "
            f"{'≤ 1.5':>7s} {'body Δ':>8s}")
        factors = []
        for scene, component, background, reference, _series in fit_rows:
            web = passes(rows[scene], "Web")
            factor = max(web / reference, reference / web)
            factors.append(factor)
            delta = rows[scene]["bodyWeb"] - rows[scene]["bodyNative"]
            say(f"{component:10s} {background:18s} {reference:8.4f} {web:8.4f} {factor:8.3f} "
                f"{'yes' if factor <= 1.5 else 'NO':>7s} {delta:+8.4f}")
        say(f"rows inside a factor of 1.5: {sum(1 for f in factors if f <= 1.5)} / {len(factors)}; "
            f"worst {max(factors):.3f}; geometric mean "
            f"{math.exp(sum(math.log(f) for f in factors) / len(factors)):.3f}")

    if args.out is not None:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")
        print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
