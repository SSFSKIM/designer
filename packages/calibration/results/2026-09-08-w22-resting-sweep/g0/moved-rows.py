"""W22 G0 (d) — the gate's rows that move, and the merged matrix the gate is run over.

Two jobs, one pass over the two matrices:

1. **The moved-rows table.** Every GPU-tier cell this gate recaptured, on the six named rows, W21's
   bed -> the gate: `rimPeakLuminanceWeb`, `rimPeakDistanceWeb`, `rimFwhmWeb`, `ssimMean`,
   `oklabDeltaEMean`, `interiorMeanWeb`. A row that did not move is printed only in the summary
   count, because what the wave has to see is what moved.

2. **The merged matrix.** The canonical matrix with this gate's rows substituted in place, written
   so that `adopted-thresholds.test.ts` can be pointed at it through `VITREA_MATRIX_PATH`. The
   substitution is by CELL IDENTITY — profile, scene, tier — and a cell the gate did not recapture
   keeps its canonical row, which is the honest state of the bed at this gate: the CSS tier draws
   no sweep and is genuinely unmoved, while the HOLDOUT rows are stale by construction, because
   W22 X5 spends the wave's one holdout read at G1 and this gate does not open it. The merged
   matrix is therefore a gate over the calibration and validation columns and is stated as such.

Usage: moved-rows.py --canonical <matrix.json> --after <scratch matrix.json>
                     --merged <out.json> --out <out.txt>
"""

import argparse
import json

ROWS = (
    ("material", "rimPeakLuminanceWeb"),
    ("material", "rimPeakDistanceWeb"),
    ("material", "rimFwhmWeb"),
    ("perceptual", "ssimMean"),
    ("perceptual", "oklabDeltaEMean"),
    ("material", "interiorMeanWeb"),
)


def identity(cell):
    return (cell["key"]["profileKey"], cell["key"]["sceneId"], cell["tier"],
            cell["key"]["web"]["renderer"])


def value(cell, axis, field):
    node = cell.get(axis)
    if not isinstance(node, dict):
        return None
    entry = node.get(field)
    if not isinstance(entry, dict):
        return None
    return entry.get("value")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--merged", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    canonical = json.load(open(args.canonical))
    after = json.load(open(args.after))
    before_by = {identity(c): c for c in canonical["cells"]}
    after_by = {identity(c): c for c in after["cells"]}

    lines = []

    def say(text=""):
        lines.append(text)
        print(text)

    say("W22 G0 (d) — every GPU-tier row that moved when the resting sweep was gated")
    say()
    say("before = the canonical matrix at the 0.10.0 landing (the W21 bed); after = this gate's")
    say("scratch matrix, the same profile documents and the same bed, the sweep gone. Only the")
    say("cells the gate recaptured appear: the four standard profiles, GPU tier, calibration and")
    say("validation. The holdout is not read at this gate (X5).")
    say()
    say(f"{'profile':38s} {'scene':44s} {'row':22s} {'before':>10s} {'after':>10s} {'delta':>10s}")

    moved = 0
    unmoved = 0
    missing = []
    per_row = {}
    for ident, cell in sorted(after_by.items()):
        base = before_by.get(ident)
        if base is None:
            missing.append(ident)
            continue
        for axis, field in ROWS:
            a, b = value(cell, axis, field), value(base, axis, field)
            if a is None and b is None:
                continue
            if a is None or b is None:
                say(f"{ident[0]:38s} {ident[1]:44s} {field:22s} "
                    f"{'absent' if b is None else format(b, '10.6f'):>10s} "
                    f"{'absent' if a is None else format(a, '10.6f'):>10s} "
                    f"{'-> presence':>10s}")
                moved += 1
                continue
            if abs(a - b) < 1e-9:
                unmoved += 1
                continue
            moved += 1
            per_row[field] = per_row.get(field, 0) + 1
            say(f"{ident[0]:38s} {ident[1]:44s} {field:22s} {b:10.6f} {a:10.6f} {a - b:+10.6f}")

    say()
    say(f"{moved} row(s) moved, {unmoved} unmoved, over {len(after_by)} recaptured cells "
        f"x {len(ROWS)} rows.")
    for field, count in sorted(per_row.items()):
        say(f"  {field}: {count}")
    if missing:
        say(f"cells in the gate's matrix with no canonical counterpart: {missing}")

    say()
    say("== the calibration and validation OKLab dE mean per profile, before -> after")
    say(f"{'profile':38s} {'set':12s} {'cells':>6s} {'before':>10s} {'after':>10s} {'delta':>10s}")
    groups = {}
    for ident, cell in after_by.items():
        base = before_by.get(ident)
        if base is None:
            continue
        key = (ident[0], cell["fixtureSet"])
        a, b = value(cell, "perceptual", "oklabDeltaEMean"), value(base, "perceptual",
                                                                  "oklabDeltaEMean")
        if a is None or b is None:
            continue
        groups.setdefault(key, []).append((b, a))
    for key in sorted(groups):
        pairs = groups[key]
        before_mean = sum(p[0] for p in pairs) / len(pairs)
        after_mean = sum(p[1] for p in pairs) / len(pairs)
        say(f"{key[0]:38s} {key[1]:12s} {len(pairs):6d} {before_mean:10.5f} {after_mean:10.5f} "
            f"{after_mean - before_mean:+10.5f}")

    say()
    say("== W22 G1's stops S1 and the rim rows, evaluated on what this gate moved")
    say()
    say("S1 fires on an untinted row worse than the W21 bed by more than 0.001 in oklabDeltaEMean")
    say("or 0.005 in ssimMean. Worse means larger dE or smaller ssim. Every recaptured cell is")
    say("tested; the extremes in each direction are named.")
    worst = {"oklabDeltaEMean": [], "ssimMean": [], "interiorMeanWeb": [],
             "rimPeakLuminanceWeb": []}
    for ident, cell in after_by.items():
        base = before_by.get(ident)
        if base is None:
            continue
        for axis, field in (("perceptual", "oklabDeltaEMean"), ("perceptual", "ssimMean"),
                            ("material", "interiorMeanWeb"), ("material", "rimPeakLuminanceWeb")):
            a, b = value(cell, axis, field), value(base, axis, field)
            if a is None or b is None:
                continue
            worst[field].append((a - b, ident, b, a))
    for field in ("oklabDeltaEMean", "ssimMean", "interiorMeanWeb", "rimPeakLuminanceWeb"):
        entries = sorted(worst[field])
        if not entries:
            continue
        for label, entry in (("most negative", entries[0]), ("most positive", entries[-1])):
            delta, ident, b, a = entry
            say(f"{field:22s} {label:14s} {delta:+10.6f}  {ident[0]} / {ident[1]} "
                f"({b:.6f} -> {a:.6f})")
        fired = [e for e in entries
                 if (field == "oklabDeltaEMean" and e[0] > 0.001)
                 or (field == "ssimMean" and e[0] < -0.005)]
        say(f"{field:22s} S1 would fire on {len(fired)} row(s)"
            + ("" if not fired else ": " + ", ".join(f"{e[1][0]}/{e[1][1]}" for e in fired)))

    merged = json.loads(json.dumps(canonical))
    replaced = 0
    for index, cell in enumerate(merged["cells"]):
        replacement = after_by.get(identity(cell))
        if replacement is not None:
            merged["cells"][index] = replacement
            replaced += 1
    merged["$comment-w22-g0"] = [
        "W22 G0 MERGED MATRIX — scratch only, never committed.",
        "The canonical matrix at the 0.10.0 landing with this gate's GPU-tier calibration and",
        f"validation rows substituted in place ({replaced} of {len(merged['cells'])} cells).",
        "The CSS rows are canonical and genuinely unmoved (the CSS tier draws no sweep); the",
        "HOLDOUT rows are canonical and STALE, because W22 X5 spends the wave's one holdout read",
        "at G1 and this gate does not open it.",
    ]
    with open(args.merged, "w") as fh:
        json.dump(merged, fh, indent=2)
    say()
    say(f"merged matrix: {replaced} of {len(merged['cells'])} cells substituted -> {args.merged}")

    with open(args.out, "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
