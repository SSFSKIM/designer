"""W23 G3 — stop S10: no UNTINTED capture moves.

The mechanism gates the rim's colour by the pixel's own tint strength, so it reaches painted pixels
and nothing else — and that is a claim about bytes, not about a metric. Every capture of the bed is
compared against G1's dry run, which is the same configuration in every respect but this constant,
and the verdict is per cell: an untinted cell that moved is S10, and a tinted cell that did not is
a mechanism that did not reach it.

    untinted-identity.py --before <captures dir> --after <captures dir> [--out <file>]
"""

import argparse
import hashlib
import os


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def walk(root):
    found = {}
    for base, _dirs, files in os.walk(root):
        for name in files:
            if not name.endswith(".png"):
                continue
            path = os.path.join(base, name)
            found[os.path.relpath(path, root)] = path
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    before, after = walk(args.before), walk(args.after)
    emit("W23 G3 — S10: every capture against G1's dry run, split by whether the cell is painted")
    emit("=" * 104)
    emit("before = G1's dry run (the same configuration but for `rimTintChroma`); after = G3's.")
    emit("An UNTINTED capture that moved is S10. A TINTED capture that did not is a mechanism that")
    emit("did not reach the cell it was written for.")

    groups = {}
    for name, path in sorted(after.items()):
        was = before.get(name)
        tinted = "tint" in name
        tier = "css" if "__css" in name else "webgpu"
        if was is None:
            groups.setdefault((tinted, tier, "only in G3"), []).append(name)
            continue
        moved = digest(was) != digest(path)
        groups.setdefault((tinted, tier, "moved" if moved else "identical"), []).append(name)
    for tinted in (False, True):
        for tier in ("webgpu", "css"):
            for verdict in ("moved", "identical", "only in G3"):
                names = groups.get((tinted, tier, verdict))
                if not names:
                    continue
                emit()
                emit(
                    f"=== {'TINTED' if tinted else 'UNTINTED'} / {tier}: {len(names)} {verdict} ==="
                )
                for name in names[:400]:
                    emit(f"  {name}")
    untinted_moved = sum(
        len(v) for (tinted, _t, verdict), v in groups.items() if not tinted and verdict == "moved"
    )
    tinted_still = sum(
        len(v) for (tinted, _t, verdict), v in groups.items() if tinted and verdict == "identical"
    )
    emit()
    emit(f"UNTINTED captures that moved (S10 wants 0): {untinted_moved}")
    emit(f"TINTED captures that did not move: {tinted_still}")
    if args.out:
        open(args.out, "w").write("\n".join(lines) + "\n")


main()
