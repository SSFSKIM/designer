"""W26 G0 deliverable 3 — what the share law's lift does once the width is right.

W25 G3 declined the heavy share's thick lift because the one check off its fitted rows ran the
other way: the coarse checkerboards' single-width objective, `mean |log(web/native)|` over readers
B and C on `checkerboard-32` / `-64` at spans >= 96, went 0.2373 -> 0.3402 at lift 0.45 at 1x
(claims §5.116 §2). Its measured cause was the width — a share is a MIX, and mixing more of a
component that is 13.4 device px wide toward a reference whose own is 19.5 adds structure the
reference does not have.

So this reads the same objective, W25 G3's `share_check` restated, over four rungs:

  r0        the 0.14.0 material                       (width 13.4, lift 0)
  s45only   W25's own declined rung                   (width 13.4, lift 0.45)
  w195      the width alone at the reference's own    (width 19.5 / 11.3, lift 0)
  w195s45   both                                      (width 19.5 / 11.3, lift 0.45)

The question is whether the objective's DIRECTION under the lift changes sign once the width is
right. Reader A's triple is printed beside it, because the share is what reader A reads and the
objective is the check off it.

Writes `share-at-width.txt`.
"""

import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g0"
IMPULSE = ["impulse__rrect-md__rest", "impulse__rrect-ml__rest", "impulse__rrect-lg__rest"]
RUNGS = [("r0", "0.14.0: width 13.4, lift 0"),
         ("s45only", "W25's declined rung: width 13.4, lift 0.45"),
         ("w195", "the width alone: 19.5 / 11.3 device px, lift 0"),
         ("w195s45", "both: width 19.5 / 11.3, lift 0.45")]


def load(rung):
    return json.load(open(os.path.join(SCRATCH, rung, f"read-{rung}.json")))["widths"]


def objective(rows, native, profiles):
    """W25 G3 `g3-fit.py`'s `share_check`, restated: the coarse checkerboards' single-width readers."""
    vals = []
    for r in rows:
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
    return (statistics.fmean(vals) if vals else float("nan")), len(vals)


def main():
    out = []
    e = out.append
    e("W26 G0 deliverable 3 — the share law's lift at the reference's own width")
    e("=" * 100)
    e("")
    e("The objective is W25 G3's `share_check`, restated: mean |log(web / native)| over readers B")
    e("and C on `checkerboard-32` and `-64` at spans >= 96. LOWER IS BETTER. The reference side is")
    e("the same fixture at every rung and is taken from the baseline read, so the four rungs are")
    e("compared against one native.")
    e("")
    base = load("r0")
    native = {(r["profile"], r["scene"], r["reader"]): r for r in base if r["src"] == "native"}

    e(f"  {'rung':10} {'what':46} {'1x':>9} {'2x':>9}")
    scores = {}
    for rung, label in RUNGS:
        rows = load(rung)
        one, n1 = objective(rows, native, ("1x-light",))
        two, n2 = objective(rows, native, ("2x-light",))
        scores[rung] = (one, two)
        e(f"  {rung:10} {label:46} {one:9.4f} {two:9.4f}")
    e(f"  (over {n1} rows at 1x and {n2} at 2x, light standard only — W25's own count of 24 is the")
    e("   same rows in both schemes, and this child captured the light bed.)")
    e("")
    e("  THE LIFT'S DIRECTION, at each width:")
    for width, a, b in (("at the 0.14.0 width", "r0", "s45only"),
                        ("at the reference's width", "w195", "w195s45")):
        for i, tag in ((0, "1x"), (1, "2x")):
            before, after = scores[a][i], scores[b][i]
            verdict = "WORSE" if after > before else "better"
            e(f"    {width:26} {tag}  {before:.4f} -> {after:.4f} at lift 0.45   {verdict}")
    e("")
    e("  The width alone, against the 0.14.0 material:")
    for i, tag in ((0, "1x"), (1, "2x")):
        e(f"    {tag}  {scores['r0'][i]:.4f} -> {scores['w195'][i]:.4f}   "
          f"{'WORSE' if scores['w195'][i] > scores['r0'][i] else 'better'}")
    e("")
    e("READER A's TRIPLE on the impulse rows, so the share the objective is checking is visible.")
    e("")
    e(f"  {'rung':10} {'profile':9} {'scene':26} {'sharp':>7} {'heavy':>8} {'share':>7}")
    for rung, _ in [("r0", None)] + [(r, None) for r, _ in RUNGS[1:]]:
        rows = load(rung)
        for r in sorted(rows, key=lambda r: (r["profile"], r["scene"])):
            if r["reader"] != "A" or r["scene"] not in IMPULSE:
                continue
            if r["src"] == "native" and rung != "r0":
                continue
            tag = rung if r["src"] == "web" else "native"
            e(f"  {tag:10} {r['profile']:9} {r['scene']:26} {r['sharpDev']:7.3f} "
              f"{r['heavyDev']:8.3f} {r['heavyShare']:7.3f}")
        e("")
    text = "\n".join(out)
    print(text)
    open(os.path.join(HERE, "share-at-width.txt"), "w").write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
