"""W26 G2 — the fourteen thick regression floors, each read at the control and at the candidate.

The gate (`adopted-thresholds.test.ts` through `g2-gate.sh`) is the authority on whether a floor is
breached, and it stops at the first failing assertion per profile — so a wave that moves several
floors on one profile sees one of them in the gate's output. This file is the other half: every
floor read directly off the matrices, whether or not the gate reached it, so that "three fired" and
"seven are under" cannot be the same run described twice.

It also reads the floors whose CELL has fallen out of the shape gate. A floor nothing reaches is not
a floor that held: the gate's own `proves every regression floor stands on a genuinely unmet bound`
case fails on it, and the underlying number is what says whether the cell got better or worse while
the instrument stopped looking.

The control is the canonical committed `results/matrix.json` — the 0.14.0 bed, which is what every
floor was pinned against — and the candidate is this child's own dry run, both columns.

    g2-floors.py [--before matrix.json] [--after bed.json,holdout.json] [--out FILE]
"""

import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TEST = os.path.abspath(os.path.join(HERE, "..", "..", "..", "test", "adopted-thresholds.test.ts"))


def floors():
    """`REGRESSION_FLOORS` read out of the only file that has it, so the two cannot drift."""
    text = open(TEST).read()
    start = text.index("const REGRESSION_FLOORS")
    end = text.index("};", start)
    out = {}
    for line in text[start:end].splitlines():
        line = line.strip()
        if not line.startswith('"'):
            continue
        key = line[1:line.index('":')]
        body = line[line.index("{"):]
        measured = float(body.split("measured:")[1].split(",")[0])
        floor = float(body.split("floor:")[1].split("}")[0])
        out[key] = (measured, floor)
    return out


def newest(paths):
    out = {}
    for path in paths:
        for cell in json.load(open(path))["cells"]:
            key = (cell["tier"], cell["fixtureSet"], cell["key"]["sceneId"],
                   cell["key"]["profileKey"])
            if key not in out or cell["capturedAt"] >= out[key]["capturedAt"]:
                out[key] = cell
    return out


def reading(cell, metric):
    for axis in ("shape", "perceptual"):
        node = (cell.get(axis) or {}).get(metric)
        if node is not None:
            return node["value"] if isinstance(node, dict) else node
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", default=os.path.abspath(
        os.path.join(HERE, "..", "..", "matrix.json")))
    ap.add_argument("--after", required=True, help="comma-separated matrices")
    ap.add_argument("--out", default=os.path.join(HERE, "floors.txt"))
    args = ap.parse_args()

    before = newest([args.before])
    after = newest(args.after.split(","))
    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W26 G2 — the fourteen thick regression floors, control against candidate")
    emit("=" * 118)
    emit(f"  {'tier':8s} {'set':11s} {'scene':38s} {'profile':16s} {'metric':20s} "
         f"{'floor':>8s} {'0.14.0':>9s} {'cand':>9s} {'verdict':>9s}")
    breached = 0
    held = 0
    for key, (pinned, floor) in floors().items():
        name, metric = key.rsplit(" :: ", 1)
        tier, fixture_set, scene, profile = [part.strip() for part in name.split(" / ")]
        ident = (tier, fixture_set, scene, profile)
        b = reading(before[ident], metric) if ident in before else None
        a = reading(after[ident], metric) if ident in after else None
        # The DIRECTION is the metric's, not the table's, and getting it wrong silently turns four
        # breaches into four holds: `ssimMean` and `silhouetteIoU` are similarity measures and
        # their floors are "≥", while `contourDistance*` are errors in pixels and theirs are "≤".
        # `adopted-thresholds.test.ts` carries the comparison beside each bound; this restates it
        # from the metric's own name so that a floor added later cannot be read the wrong way round.
        greater_is_better = metric in ("ssimMean", "silhouetteIoU")
        verdict = "—"
        if a is not None:
            if (a < floor) if greater_is_better else (a > floor):
                verdict = "BREACHED"
                breached += 1
            else:
                verdict = "held"
                held += 1
        fmt = lambda v: f"{v:9.5f}" if isinstance(v, (int, float)) else f"{'—':>9s}"  # noqa: E731
        emit(f"  {tier:8s} {fixture_set:11s} {scene:38s} {profile[-16:]:16s} {metric:20s} "
             f"{floor:8.4f} {fmt(b)} {fmt(a)} {verdict:>9s}")
    emit()
    emit(f"  breached {breached}, held {held}, of {len(floors())}")
    emit("  A floor whose CELL has left the shape gate is still read here and still counted: the")
    emit("  gate's own `every regression floor stands on a genuinely unmet bound` case fails on it,")
    emit("  and a floor nothing reaches is not a floor that held.")

    with open(args.out, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
