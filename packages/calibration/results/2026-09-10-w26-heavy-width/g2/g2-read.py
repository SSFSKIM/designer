"""W26 G2 — S15, read on the instrument of record: the family reader, control against candidate.

THE INSTRUMENT IS NOT RE-DERIVED HERE. `g1c-read.py` is imported whole and its `read_cell` is
called; that file in turn imports G1b's `w26blib.py` and `w26brows.py` unedited (W26 Decision Log 5
(a)). The only thing this file adds is WHERE the captures come from: the control column is W26
G1c's `c0` rung, the candidate column is this child's own dry run, and the two live under different
scratch roots, so `SCRATCH` is set per column rather than being a constant.

S15, as the parent re-stated it at Decision Log 4 (a) and assigned it at 6 (f): **the heavy σ on any
fitted row, or any row whose reference two-component fit is conditioned (a sharp component under 4
device px), further from the reference's than at 0.14.0.** The objective per cell is
|log(read / reference)|, a ratio because a width is a scale, and the stop is per cell rather than on
the mean — a mean cannot fire.

**Two of the six cells are expected to fire and the declaration said so before the run.** Both are
at dpr 2 on `rrect-md`, the two cells the 0.14.0 material already had nearly right at that scale,
and the cause is measured rather than guessed: the reference's 2x readings spread 20.4 % across the
two spans and one width per source cannot serve both (claims §5.122 §3). What this file is for is
that the firing be a number in a table rather than a sentence in a document.

The reference column is re-read here rather than quoted from G1c, on the same holdout-free rows, so
that a dry run whose captures differ from a rung's would show as a moved reference rather than as a
silently better fit.

    g2-read.py [--control-root DIR --control-rung c0] [--candidate-root DIR --candidate-rung cand]
               [--out FILE]
"""

import argparse
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
G1C = os.path.abspath(os.path.join(HERE, "..", "g1c"))
G1B = os.path.abspath(os.path.join(HERE, "..", "g1b"))
sys.path.insert(0, G1B)

_spec = importlib.util.spec_from_file_location("g1cread", os.path.join(G1C, "g1c-read.py"))
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

# The sharp component under which the reference's own two-component fit is CONDITIONED, per
# Decision Log 4 (a). Above it the reader has split one wide kernel in half and the "heavy" it
# reports is not a component — which is exactly what the reference's 2x `-lg` row does.
CONDITIONED_SHARP = 4.0
# The reader's own two arguments, built exactly as `g1c-read.py`'s `main` builds them: the radial
# node positions the family is expressed on, and `scenes.json`'s components.
NODES = R.E.radial_nodes(R.EXTENT, R.NODES)
COMPS = R.L.load_components()


def read(source, cell, root_rung, lam):
    surface, scale, scheme = cell
    out, rows, _ = R.read_cell(source, surface, scale, scheme, NODES, COMPS, lam, rung=root_rung)
    return out, rows


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lam", type=float, default=0.003)
    ap.add_argument("--control-root", default="/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c")
    ap.add_argument("--control-rung", default="c0")
    ap.add_argument("--candidate-root", default="/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2")
    ap.add_argument("--candidate-rung", default="cand")
    ap.add_argument("--out", default=os.path.join(HERE, "s15.txt"))
    args = ap.parse_args(argv)

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text, flush=True)

    emit("W26 G2 — S15 on the family reader: the control, the candidate and the reference")
    emit("=" * 112)
    emit(f"  control   {args.control_root}/{args.control_rung}/web-captures")
    emit(f"  candidate {args.candidate_root}/{args.candidate_rung}/web-captures")
    emit()
    emit(f"  {'surface':10s} {'dpr':>3s} {'scheme':6s} {'ref σ':>8s} {'sharp':>7s} "
         f"{'0.14.0':>8s} {'cand':>8s} {'|log| c0':>9s} {'|log| d9':>9s} {'S15':>8s}")

    fired = []
    obj_before = []
    obj_after = []
    for cell in R.CELLS:
        surface, scale, scheme = cell

        R.SCRATCH = args.candidate_root
        native, _ = read("native", cell, None, args.lam)
        if native is None:
            emit(f"  {surface:10s} {int(scale):3d} {scheme:6s}   (no reference rows)")
            continue
        # The two-Gaussian read of the SAME pixels, for the conditioning statistic alone. A sharp
        # component at or above 4 device px means the two-component fit has split one wide kernel,
        # so the row is conditioned and S15 applies to it whether or not it was fitted.
        two = R.two_gauss_read(native["rows"], NODES)
        sharp = two["sharp"] if two else float("nan")

        R.SCRATCH = args.control_root
        control, _ = read("web", cell, args.control_rung, args.lam)
        R.SCRATCH = args.candidate_root
        candidate, _ = read("web", cell, args.candidate_rung, args.lam)
        if control is None or candidate is None:
            emit(f"  {surface:10s} {int(scale):3d} {scheme:6s}   (missing a web column)")
            continue

        ref = native["sigma"]
        before = abs(math.log(control["sigma"] / ref))
        after = abs(math.log(candidate["sigma"] / ref))
        obj_before.append(before)
        obj_after.append(after)
        conditioned = not (sharp >= CONDITIONED_SHARP)
        verdict = "FIRES" if (conditioned and after > before) else "clear"
        if verdict == "FIRES":
            fired.append((cell, before, after))
        emit(f"  {surface:10s} {int(scale):3d} {scheme:6s} {ref:8.3f} {sharp:7.2f} "
             f"{control['sigma']:8.3f} {candidate['sigma']:8.3f} {before:9.4f} {after:9.4f} "
             f"{verdict:>8s}")

    if obj_before:
        emit()
        emit(f"  MEAN |log(read / reference)| over {len(obj_before)} cells: "
             f"{sum(obj_before) / len(obj_before):.4f} → {sum(obj_after) / len(obj_after):.4f}")
    emit(f"  cells firing S15: {len(fired)}")
    emit()
    emit("  A cell whose reference sharp component is at or above 4 device px is UNCONDITIONED and")
    emit("  S15 does not apply to it (Decision Log 4 (a)); its objective is still printed, because a")
    emit("  stop that does not fire on a row is not the same thing as a row nobody read.")

    with open(args.out, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"\n-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
