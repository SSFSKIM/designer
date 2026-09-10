"""W26 G2 — X5 and the per-span OKLab ΔE over the probe set, ON BOTH TIERS.

W26 G1c's `g1c-bed.py` with one change, and the change is the reason this file exists rather than
being a second call of that one. G1c read X5 on the GPU tier alone, and it was right to: a scratch
rung patches the profile DOCUMENTS and leaves the code where it is, so the CSS tier's own arithmetic
could not move at any rung. A LANDING moves the code, and this one moves the CSS tier's heavy layer
from `blurSigma × gain` through the mip chain's effective ratio to the profile's own width —
13.800 → 9.000 CSS px at dpr 1 at every span, thin spans included. So X5 has a second half this
wave, and a thin CSS cell is now something that can move.

The control per tier is stated rather than assumed:

  * the GPU tier's is G1c's `c0p` rung, the 0.14.0 material captured on this machine;
  * the CSS tier's is `c0css`, captured by THIS child at the 0.14.0 code before the landing edit,
    because no earlier rung has one — G1c never needed it.

S14 is the same two matrices read with a different bound (0.002 against the control on any probe
row) and it is printed here beside X5 rather than in the canonical bed's stop file, because the
probe set is where this wave's constants were fitted and a fit that had bought its own rows at the
expense of the rest would show here first.

    g2-probe.py --before-gpu <matrix> --before-css <matrix> --after <matrix> [--out FILE]
"""

import argparse
import collections
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SCENES = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..",
                                      "apps", "reference-apple", "scenes.json"))
TIERS = {"texture": "webgpu", "dom": "css"}
THIN_SPAN = 44.0
X5_BOUND = 0.001
S14_BOUND = 0.002
# The thick spans the fit was read on, and the ones claims §5.122 §5c tables.
THICK_SPANS = (96.0, 128.0, 160.0)


def spans():
    """Component id → shorter side in CSS px, out of `scenes.json` and never out of a name."""
    doc = json.load(open(SCENES))
    out = {}
    for name, spec in doc["components"].items():
        # Only the shapes that HAVE one span: a group or a stack has no single shorter side, and
        # X5's bound is stated on a surface's span rather than on a composition's extent.
        if spec.get("kind") in ("rrect", "capsule"):
            out[name] = float(min(spec["size"]))
    return out


def identity(cell):
    return (
        cell["key"]["profileKey"],
        cell["key"]["sceneId"],
        cell["tier"],
        cell["key"]["web"]["renderer"],
    )


def delta_e(cell):
    entry = (cell.get("perceptual") or {}).get("oklabDeltaEMean")
    if isinstance(entry, dict):
        entry = entry.get("value")
    if entry is None or (isinstance(entry, float) and math.isnan(entry)):
        return None
    return float(entry)


def newest(path):
    """A matrix written with `--write-partial` APPENDS, so the newest row per key is the reading."""
    cells = {}
    for cell in json.load(open(path))["cells"]:
        cells[identity(cell)] = cell
    return cells


def component_of(scene_id, table):
    """`<background>__<component>__<state>`; the component is the middle field."""
    parts = scene_id.split("__")
    return table.get(parts[1]) if len(parts) >= 2 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before-gpu", required=True)
    ap.add_argument("--before-css", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "probe.txt"))
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    table = spans()
    before = {}
    before.update(newest(args.before_gpu))
    before.update(newest(args.before_css))
    after = newest(args.after)

    emit("W26 G2 — the probe set at the candidate, against the 0.14.0 control, on both tiers")
    emit("=" * 104)
    emit(f"  control: GPU {args.before_gpu}")
    emit(f"           CSS {args.before_css}")
    emit(f"  candidate: {args.after}")
    emit(f"  cells: control {len(before)}, candidate {len(after)}, "
         f"paired {len(set(before) & set(after))}")

    # ------------------------------------------------------------------ X5, per tier
    emit()
    emit(f"=== X5 / S12 — every probe cell of span at or below {THIN_SPAN:.0f} CSS px "
         f"(bound {X5_BOUND}) ===")
    worst = {"texture": (0.0, None), "dom": (0.0, None)}
    counted = collections.Counter()
    fired = []
    for ident, cell in sorted(after.items()):
        base = before.get(ident)
        if base is None:
            continue
        span = component_of(ident[1], table)
        if span is None or span > THIN_SPAN:
            continue
        a, b = delta_e(cell), delta_e(base)
        if a is None or b is None:
            continue
        counted[ident[2]] += 1
        move = abs(a - b)
        if move > worst[ident[2]][0]:
            worst[ident[2]] = (move, ident)
        if move > X5_BOUND:
            fired.append((ident, b, a))
    for tier, (value, ident) in worst.items():
        where = f"{ident[0]} / {ident[1]}" if ident else "—"
        emit(f"  {TIERS[tier]:7s} {counted[tier]:4d} thin cells   worst move {value:.5f}   {where}")
    emit(f"  cells firing: {len(fired)}")
    for ident, b, a in fired:
        emit(f"    FIRES {ident[0]:46s} {ident[1]:40s} {TIERS[ident[2]]:7s} {b:.5f} → {a:.5f}")

    # ------------------------------------------------------------------ S14, per tier
    emit()
    emit(f"=== S14 — any probe row worse by more than {S14_BOUND} ΔE than at the control ===")
    rows = []
    worst14 = 0.0
    for ident, cell in sorted(after.items()):
        base = before.get(ident)
        if base is None:
            continue
        a, b = delta_e(cell), delta_e(base)
        if a is None or b is None:
            continue
        d = a - b
        worst14 = max(worst14, d)
        if d > S14_BOUND:
            rows.append((ident, b, a, d))
    emit(f"  worst rise over {len(set(before) & set(after))} paired rows: {worst14:+.5f}")
    emit(f"  rows firing: {len(rows)}")
    for ident, b, a, d in rows:
        emit(f"    FIRES {ident[0]:46s} {ident[1]:40s} {TIERS[ident[2]]:7s} "
             f"{b:.5f} → {a:.5f}  {d:+.5f}")

    # ------------------------------------------------------------------ the per-span table
    emit()
    emit("=== the per-span OKLab ΔE, mean over the span's untinted probe cells, per tier ===")
    emit("  claims §5.122 §5c's table, re-read on the landing rather than on a scratch rung, and")
    emit("  with the CSS tier beside the GPU one for the first time.")
    emit(f"  {'profile':46s} {'tier':7s} " +
         "  ".join(f"{'span ' + str(int(s)):>18s}" for s in THICK_SPANS))
    groups = collections.defaultdict(lambda: collections.defaultdict(list))
    for ident, cell in after.items():
        base = before.get(ident)
        if base is None or "tint" in ident[1]:
            continue
        span = component_of(ident[1], table)
        if span not in THICK_SPANS:
            continue
        a, b = delta_e(cell), delta_e(base)
        if a is None or b is None:
            continue
        groups[(ident[0], ident[2])][span].append((b, a))
    for key in sorted(groups):
        cells = groups[key]
        row = f"  {key[0]:46s} {TIERS[key[1]]:7s} "
        for span in THICK_SPANS:
            pairs = cells.get(span, [])
            if not pairs:
                row += f"{'—':>18s}  "
                continue
            b = sum(p[0] for p in pairs) / len(pairs)
            a = sum(p[1] for p in pairs) / len(pairs)
            mark = "*" if a > b else " "
            row += f"{b:8.5f}→{a:8.5f}{mark}"
        emit(row)
    emit("  * = worse at the candidate than at the control.")

    with open(args.out, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
