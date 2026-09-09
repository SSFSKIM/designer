"""W25 G3 — the three fits, each off the rows that identify it, with its condition beside it.

WHAT THIS READS. `read-<rung>.json` written by `g3-read.py` for the inert baseline `r0` and for one
lever rung per mechanism. Nothing else; it writes tables on stdout and touches no fixture, scene,
matrix or capture.

THE METHOD, AND WHY IT IS A RENDERED LEVER RATHER THAN A MODEL. Every implied value here is

    implied = c_rung · (native − web_at_0) / (web_at_c_rung − web_at_0)

so the renderer supplies the derivative of the quantity the reader measures with respect to the
constant, and no analytic model of the optics enters the fit. That is G2's method (`fit.py`) and
the W23 lesson it comes from: the condition — how far the rendered quantity actually moves per unit
of the constant — is stated before the value is, and a row whose lever is at or near zero is
reported as unidentified rather than averaged in.

THE ROWS ARE NAMED PER MECHANISM and the reasons are in each section below. Every fit prints its
rows, the lever on each, the implied value, the residual at the joint value and the rows NOT fitted
that check it.

Usage:  g3-fit.py share|level|field --rung <lever rung> --value <the constant at that rung>
"""

import argparse
import json
import math
import os
import statistics
import sys

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w25/g3"


def load(rung):
    return json.load(open(os.path.join(SCRATCH, rung, f"read-{rung}.json")))


def index(rows, key):
    out = {}
    for r in rows:
        out[key(r)] = r
    return out


def encode(v):
    v = max(v, 0.0)
    return v * 12.92 if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def fmt(v, n=4):
    return "—" if v is None or not math.isfinite(v) else f"{v:+.{n}f}"


# --------------------------------------------------------------------------- the heavy share

def fit_share(base, rung, value):
    """The heavy share's thick-end lift, on reader A's own share.

    THE ROWS. Every `impulse` probe row at 1x on which reader A identifies a two-component kernel on
    BOTH sides — which is the whole of what "the row identifies the share" can mean, since a fit
    that has collapsed to one Gaussian has no share to compare. A row is refused when either side
    reads a share of 0.00 with its heavy component at the profile's own half-window (the signature
    of a single Gaussian, G0 §1), which is what the collapsed cells and the dark scheme's own
    collapse return. The 2x rows are read and printed but are not fitted: `sizeScatterFloor2x` is 1,
    so `kDeep` is saturated before the lift is added and the 2x constant is arithmetically inert —
    the rung measures that rather than assuming it (Decision Log 4 (e)).
    """
    b = index([r for r in base["widths"] if r["reader"] == "A"],
              lambda r: (r["profile"], r["scene"], r["src"]))
    g = index([r for r in rung["widths"] if r["reader"] == "A"],
              lambda r: (r["profile"], r["scene"], r["src"]))
    print(f"the heavy share — reader A on the impulse rows, lever rung at lift {value}\n")
    print(f"{'profile':9} {'scene':26} {'span':>5} {'nat':>6} {'web0':>6} {'web1':>6} "
          f"{'lever':>7} {'implied':>8}  verdict")
    implied, levers = [], []
    for (profile, scene, src) in sorted(b):
        if src != "web":
            continue
        n = b.get((profile, scene, "native"))
        w0 = b[(profile, scene, "web")]
        w1 = g.get((profile, scene, "web"))
        if not (n and w1):
            continue
        degenerate = (n["heavyShare"] < 0.01 or w0["heavyShare"] < 0.005 <= 0)
        lever = (w1["heavyShare"] - w0["heavyShare"]) / value
        row_implied = None
        verdict = ""
        if n["heavyShare"] < 0.01:
            verdict = "refused: the reference reads one Gaussian here (collapsed)"
        elif abs(lever) < 0.05:
            verdict = "refused: the rendered lever is below 0.05 share per unit lift"
        elif profile.startswith("2x"):
            verdict = "read, not fitted: the 2x floor saturates kDeep (Decision Log 4 (e))"
            levers.append((profile, lever))
        else:
            row_implied = (n["heavyShare"] - w0["heavyShare"]) / max(lever, 1e-9)
            implied.append(row_implied)
            levers.append((profile, lever))
            verdict = "FITTED"
        print(f"{profile:9} {scene:26} {n['span']:5.0f} {n['heavyShare']:6.3f} "
              f"{w0['heavyShare']:6.3f} {w1['heavyShare']:6.3f} {lever:7.3f} "
              f"{fmt(row_implied, 3):>8}  {verdict}")
    if implied:
        print(f"\nrows fitted           {len(implied)}")
        print(f"implied lift          median {statistics.median(implied):.3f}  "
              f"mean {statistics.fmean(implied):.3f}  "
              f"spread {min(implied):.3f} … {max(implied):.3f}")
        print(f"condition             lever {min(l for _, l in levers):.3f} … "
              f"{max(l for _, l in levers):.3f} share per unit lift; "
              f"{'well conditioned' if min(abs(l) for _, l in levers) > 0.1 else 'WEAK'}")
    return implied


def share_check(base, rung, value):
    """The check off the fitted rows: the single-width readers over the coarse checkerboards.

    A share is not a width, and G0 §2c is why this check exists and why it can disagree: a
    single-Gaussian reader at one pitch is a true reading of a DIFFERENT PART of a two-component
    kernel. It is printed as `mean |log(web/native)|` over the thick coarse-checkerboard rows that
    are inside both readers' validated bounds, at the baseline and at the rung, so the direction is
    visible rather than argued.
    """
    # The reference side is the same fixture at every rung and is always taken from the baseline
    # read, so a rung captured `--web-only` is compared against the same native rows the baseline
    # was.
    native = index([r for r in base["widths"] if r["src"] == "native"],
                   lambda r: (r["profile"], r["scene"], r["reader"]))

    def objective(doc, profiles):
        vals = []
        for r in doc["widths"]:
            if r["src"] != "web" or r["span"] < 96:
                continue
            if r["backdrop"] not in ("checkerboard-32", "checkerboard-64"):
                continue
            if r["profile"] not in profiles:
                continue
            n = native.get((r["profile"], r["scene"], r["reader"]))
            if not n or n["sigmaDev"] <= 0 or r["sigmaDev"] <= 0:
                continue
            vals.append(abs(math.log(r["sigmaDev"] / n["sigmaDev"])))
        return statistics.fmean(vals), len(vals)
    print("\nthe check off the fitted rows — the coarse checkerboards' single-width readers")
    for label, profiles in (("1x", ("1x-light", "1x-dark")), ("2x", ("2x-light", "2x-dark"))):
        b, nb = objective(base, profiles)
        g, ng = objective(rung, profiles)
        print(f"  {label}  mean |log(web/native)| over {nb} rows: {b:.4f} at lift 0 "
              f"-> {g:.4f} at lift {value}   ({'WORSE' if g > b else 'better'})")


# --------------------------------------------------------------------------- the level term

def fit_level(base, rung, value_light, value_dark, wide=False):
    """The level term above the knee, SCHEME-SIGNED, on the body levels of the probe rows.

    THE ROWS. Every untinted probe row of a scheme, read in 8-bit display codes, split by span:
    above the knee (span > 96) the term has a rendered lever and is fitted; at and below it the term
    is exactly zero by the shape of its own span curve and the rows are CONTROLS — a rendered lever
    there that is not zero would mean the mechanism reaches the bed the rest of the material was
    fitted on, and would stop the fit.

    The declared row set is the wave's: the three flat solids and the checkerboards at spans 80,
    96, 128 and 160. `--all-backdrops` widens it to every untinted probe backdrop and is printed
    beside the declared fit rather than instead of it, so the value's dependence on the row set is
    visible rather than chosen.

    The `impulse` rows are excluded from the fit and printed apart. Their bodies sit two orders of
    magnitude below every other backdrop's (0.005 against 0.05–0.7 linear) and their residual is
    −39 to −43 codes at every span, above and below the knee alike, so they carry a standing
    deficit that is not this term's and would dominate a code-weighted mean.
    """
    SOLIDS = ("dark-solid", "mid-dark-solid", "light-solid")

    def declared(row):
        return (row["backdrop"] in SOLIDS or row["backdrop"].startswith("checkerboard")) \
            and row["span"] in (80.0, 96.0, 128.0, 160.0)

    b = index(base["levels"], lambda r: (r["profile"], r["scene"], r["src"]))
    g = index(rung["levels"], lambda r: (r["profile"], r["scene"], r["src"]))
    out = {}
    for scheme, value in (("light", value_light), ("dark", value_dark)):
        print(f"\nthe level term, {scheme} scheme — lever rung at sizeToneLevelFar {value}\n")
        print(f"{'profile':9} {'scene':36} {'span':>5} {'resid':>7} {'lever':>8} {'implied':>8}")
        implied, weights, levers, controls = [], [], [], []
        for key in sorted(b, key=lambda k: (b[k]["span"], k[0], k[1])):
            profile, scene, src = key
            if src != "web" or not profile.endswith(scheme):
                continue
            n = b.get((profile, scene, "native"))
            w0, w1 = b[key], g.get(key)
            if not (n and w1):
                continue
            resid = 255 * (encode(n["body"]) - encode(w0["body"]))
            lever = 255 * (encode(w1["body"]) - encode(w0["body"])) / value
            if not (wide or declared(n)):
                continue
            if n["span"] <= 96:
                controls.append((profile, scene, n["span"], lever))
                continue
            if scene.startswith("impulse"):
                print(f"{profile:9} {scene:36} {n['span']:5.0f} {resid:7.2f} {lever:8.2f} "
                      f"{'—':>8}  excluded: the impulse rows' standing deficit")
                continue
            if abs(lever) < 1.0:
                print(f"{profile:9} {scene:36} {n['span']:5.0f} {resid:7.2f} {lever:8.2f} "
                      f"{'—':>8}  unidentified: lever under 1 code per unit")
                continue
            row = resid / lever
            implied.append(row)
            weights.append(abs(lever))
            levers.append(lever)
            print(f"{profile:9} {scene:36} {n['span']:5.0f} {resid:7.2f} {lever:8.2f} {row:8.4f}")
        if implied:
            joint = sum(i * w for i, w in zip(implied, weights)) / sum(weights)
            before = math.sqrt(statistics.fmean([(i * l) ** 2 for i, l in zip(implied, levers)]))
            after = math.sqrt(statistics.fmean(
                [((i - joint) * l) ** 2 for i, l in zip(implied, levers)]))
            print(f"\nrows fitted           {len(implied)}")
            print(f"lever-weighted value  {joint:+.4f}   median {statistics.median(implied):+.4f}")
            print(f"condition             lever {min(levers):+.2f} … {max(levers):+.2f} "
                  f"codes per unit over {len(levers)} rows")
            print(f"residual RMS          {before:.3f} -> {after:.3f} codes")
            out[scheme] = joint
        worst = max((abs(l) for *_x, l in controls), default=0.0)
        print(f"controls (span <= 96) {len(controls)} rows, worst rendered lever "
              f"{worst:.4f} codes per unit")
    return out


# --------------------------------------------------------------------------- the along-side field

def fit_field(base, rung, value):
    """The along-side slope, on the four straight sides of the thick solid cells.

    THE ROWS. Every straight side of a thick (span > 96) cell over a flat solid, at both scales in
    both schemes, on which the rendered lever is not zero. The solids are where the term is
    separable at all: on a structured backdrop the same reader correlates 0.85–0.96 with the
    backdrop under the body, which is the lens (G0 §4). A side whose reader returns a zero-length
    profile — the displaced cell's clipped top and bottom — has no lever and is refused by the same
    rule as any other unidentified row.
    """
    b = index(base["sides"], lambda r: (r["profile"], r["scene"], r["side"], r["src"]))
    g = index(rung["sides"], lambda r: (r["profile"], r["scene"], r["side"], r["src"]))
    print(f"the along-side field — lever rung at rimAlongSideSlope {value}\n")
    print(f"{'profile':9} {'scene':30} {'side':6} {'span':>5} {'nat':>10} {'web0':>10} "
          f"{'web1':>10} {'implied':>8}")
    implied, weights = [], []
    for key in sorted(b):
        profile, scene, side, src = key
        if src != "web":
            continue
        n = b.get((profile, scene, side, "native"))
        w0, w1 = b[key], g.get(key)
        if not (n and w1) or n["span"] <= 96:
            continue
        lever = (w1["slopePerCss"] - w0["slopePerCss"]) / value
        if abs(lever) < 1e-6:
            continue
        row = (n["slopePerCss"] - w0["slopePerCss"]) / lever
        implied.append(row)
        weights.append(abs(lever))
        print(f"{profile:9} {scene:30} {side:6} {n['span']:5.0f} {n['slopePerCss']:10.6f} "
              f"{w0['slopePerCss']:10.6f} {w1['slopePerCss']:10.6f} {row:8.3f}")
    if implied:
        joint = sum(i * w for i, w in zip(implied, weights)) / sum(weights)
        q = statistics.quantiles(implied, n=4)
        print(f"\nrows fitted           {len(implied)}")
        print(f"implied slope         median {statistics.median(implied):.3f}  "
              f"lever-weighted {joint:.3f}  quartiles {q[0]:.3f} … {q[2]:.3f}")
        print(f"condition             lever {min(weights):.2e} … {max(weights):.2e} "
              f"luma per CSS px per unit slope")
    return implied


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("share", "level", "field"))
    ap.add_argument("--base", default="r0")
    ap.add_argument("--rung", required=True)
    ap.add_argument("--value", type=float, default=1.0)
    ap.add_argument("--value-dark", type=float, default=None)
    ap.add_argument("--all-backdrops", action="store_true")
    args = ap.parse_args(argv)
    base, rung = load(args.base), load(args.rung)
    if args.mode == "share":
        fit_share(base, rung, args.value)
        share_check(base, rung, args.value)
    elif args.mode == "level":
        fit_level(base, rung, args.value,
                  args.value if args.value_dark is None else args.value_dark,
                  wide=args.all_backdrops)
    else:
        fit_field(base, rung, args.value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
