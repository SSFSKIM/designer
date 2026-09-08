"""W22 G1 (1) — `optics.regular.specularGain` fitted PER CONTRAST on the light bed.

W22 Decision Log 2 (b) is the ruling this script implements: the constant is fitted on `T−B` and
`L−R` per untinted solid cell at both scales, and never on a mean pooled over sides. G0 measured
why (claims §5.94 §3): the pooled objective PREFERS the shipped 0.55 because the specular lifts
`dark-solid__rrect-md`'s top row from −0.061 to +0.062 against a reference of +0.047 while leaving
its bottom at −0.061 against the same +0.047 — it buys one side of a pair by breaking the other, and
a mean over sides cannot see that. The two contrasts can: `T−B` and `L−R` each compare two sides of
identical geometry, so the declared reader's rim/background mixture cancels in them exactly (the
`H−V` gap does not cancel and is a geometric artefact, not a light direction — §5.94 §3).

## The rows

The five untinted solid CALIBRATION cells of the light bed, at both scales:
`light-solid__{capsule-button,rrect-md,rrect-ml}` and `dark-solid__{capsule-button,rrect-md}`.
`mid-dark-solid__capsule-button` is a holdout scene and is NOT a fit row (X5); it is read once at
the dry run and reported there. `dark-solid__capsule-button` collapses — the light material over a
backdrop of its own tone draws no readable rim — and is printed with its slope so that its
non-separation is visible rather than assumed.

## The objective

Per contrast `c ∈ {T−B, L−R}` and per row, `|c_web(g) − c_native|`; the ladder is eight rendered
documents differing from the shipped light document in `optics.regular.specularGain` alone. A row
SEPARATES the constant when its objective varies across the ladder by more than the instrument's
own floor (G0's stack injection put that at 0.000625; the run-to-run σ on this bed is below the
fourth decimal), and the chosen value is the one the separating rows agree on.

    fit-specular.py <reads dir> [--out <file>]
"""

import argparse
import json
import os

SIDES = ("top", "bottom", "left", "right")
# The ladder, in the order the documents were rendered. The label is the candidate document's name.
LADDER = [
    ("spec000", 0.0),
    ("spec0025", 0.025),
    ("spec005", 0.05),
    ("spec010", 0.10),
    ("spec015", 0.15),
    ("spec025", 0.25),
    ("spec040", 0.40),
    ("spec055", 0.55),
]
# The instrument's recovery floor on this geometry, measured by G0's injection test (claims §5.94
# §5). A row whose objective moves by less than this across the whole ladder does not separate the
# constant and is reported as context.
SEPARATION_FLOOR = 0.000625


def contrasts(rim):
    """`T−B` and `L−R` from a four-side rim reading, in the reader's own side order."""
    top, bottom, left, right = rim
    return {"T-B": top - bottom, "L-R": left - right}


def load(reads, gain, scale):
    """The ladder point's reading, keyed by scene — only the rows that HAVE a web capture.

    The reader emits a row for every scene in the requested sets and leaves the web fields absent on
    the ones this ladder did not capture (the ladder renders the five untinted solid cells and no
    others), so the filter here is what keeps the fit's rows the declared rows.
    """
    path = os.path.join(reads, f"light-{scale}-{gain}.json")
    return {
        row["scene"]: row
        for row in json.load(open(path))["rows"]
        if row.get("rimWeb") is not None
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reads")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W22 G1 — `optics.regular.specularGain` on the light profile, fitted per contrast")
    emit("=" * 108)
    emit("The objective is |contrast_web − contrast_native| per row per contrast; never pooled over")
    emit("sides (W22 Decision Log 2 (b)). The ladder is eight documents differing in this constant")
    emit(f"alone. A row separates the constant when its objective moves by more than {SEPARATION_FLOOR}")
    emit("across the ladder — G0's injection floor for this instrument.")

    per_row = {}
    for scale in ("1x", "2x"):
        tables = {gain: load(args.reads, gain, scale) for gain, _ in LADDER}
        scenes = sorted(tables["spec000"])
        for scene in scenes:
            native = contrasts(tables["spec000"][scene]["rimNative"])
            for contrast in ("T-B", "L-R"):
                row = (scale, scene, contrast)
                per_row[row] = {
                    "native": native[contrast],
                    "web": {
                        value: contrasts(tables[gain][scene]["rimWeb"])[contrast]
                        for gain, value in LADDER
                    },
                }

    # The web contrast, and the objective, per row per ladder point.
    for contrast in ("T-B", "L-R"):
        emit()
        emit(f"=== the contrast {contrast}: vitrea's reading at each gain, against the reference ===")
        header = f"  {'dpr':3s} {'cell':38s} {'native':>9s} " + " ".join(
            f"{value:>8.3f}" for _, value in LADDER
        )
        emit(header)
        for (scale, scene, kind), data in sorted(per_row.items()):
            if kind != contrast:
                continue
            emit(
                f"  {scale:3s} {scene[:38]:38s} {data['native']:>9.4f} "
                + " ".join(f"{data['web'][value]:>8.4f}" for _, value in LADDER)
            )
        emit()
        emit(f"=== the objective |Δ{contrast}| per row, and each row's own minimiser ===")
        emit(
            f"  {'dpr':3s} {'cell':38s} " + " ".join(f"{value:>8.3f}" for _, value in LADDER)
            + f" {'span':>8s} {'argmin':>7s} {'separates':>10s}"
        )
        separating = []
        for (scale, scene, kind), data in sorted(per_row.items()):
            if kind != contrast:
                continue
            objective = {
                value: abs(data["web"][value] - data["native"]) for _, value in LADDER
            }
            span = max(objective.values()) - min(objective.values())
            argmin = min(objective, key=lambda v: objective[v])
            separates = span > SEPARATION_FLOOR
            if separates:
                separating.append((scale, scene, argmin, span, objective))
            emit(
                f"  {scale:3s} {scene[:38]:38s} "
                + " ".join(f"{objective[value]:>8.4f}" for _, value in LADDER)
                + f" {span:>8.4f} {argmin:>7.3f} {'yes' if separates else 'no':>10s}"
            )
        emit()
        if separating:
            emit(f"  separating rows on {contrast}: {len(separating)}")
            for scale, scene, argmin, span, _ in separating:
                emit(f"    {scale} {scene:44s} argmin {argmin:.3f}  span {span:.4f}")
            emit(
                f"  the separating rows' minimisers: "
                f"{sorted({f'{a:.3f}' for _, _, a, _, _ in separating})}"
            )
            # The pooled objective OVER SEPARATING ROWS OF THIS CONTRAST ONLY — still per contrast,
            # which is what the ruling asks; the mean is over rows, never over sides.
            pooled = {
                value: sum(o[value] for _, _, _, _, o in separating) / len(separating)
                for _, value in LADDER
            }
            emit(
                "  mean over those rows: "
                + " ".join(f"{value:.3f}={pooled[value]:.4f}" for _, value in LADDER)
            )
            emit(f"  → minimiser on {contrast}: {min(pooled, key=lambda v: pooled[v]):.3f}")
        else:
            emit(f"  no row separates the constant on {contrast}.")

    # The two contrasts together, over every separating row of either — the declaration.
    emit()
    emit("=== the declaration: every separating row of either contrast, one table ===")
    rows = []
    for (scale, scene, kind), data in sorted(per_row.items()):
        objective = {value: abs(data["web"][value] - data["native"]) for _, value in LADDER}
        if max(objective.values()) - min(objective.values()) > SEPARATION_FLOOR:
            rows.append(((scale, scene, kind), objective))
    if rows:
        pooled = {
            value: sum(o[value] for _, o in rows) / len(rows) for _, value in LADDER
        }
        emit(f"  {len(rows)} separating rows; mean objective per ladder point:")
        for _, value in LADDER:
            emit(f"    specularGain {value:>6.3f}   {pooled[value]:.5f}")
        emit(f"  → the fit's answer: specularGain {min(pooled, key=lambda v: pooled[v]):.3f}")

    if args.out is not None:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
