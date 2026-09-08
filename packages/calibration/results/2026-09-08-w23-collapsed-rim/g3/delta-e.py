"""W23 G3 — clause 5's headline: the OKLab ΔE mean per profile, per set, PER TIER.

W22 G1's script on this wave's document. A cell's identity carries the tier, so a mean grouped by
profile and set alone would fold the two tiers together; clause 5 is stated on the GPU tier — the
fidelity target (wave Decision Log 23) — so the two are split here, and the CSS tier is printed
beside it because this wave's law reaches it through `optics.ts`'s mirror and its captures move.

    delta-e.py --before <matrix.json> --after <matrix.json> [--out <file>]
"""

import argparse
import json

TIERS = {"texture": "webgpu", "dom": "css"}


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
        return entry.get("value")
    return entry


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

    before = {identity(c): c for c in json.load(open(args.before))["cells"]}
    after = {identity(c): c for c in json.load(open(args.after))["cells"]}

    emit("W23 G3 — OKLab ΔE mean, per profile, per set, per tier, before → after")
    emit("=" * 100)
    emit("before = the canonical matrix at the 0.11.0 landing (the W22 bed); after = the dry run.")
    emit("Clause 5 is stated on the GPU tier; the CSS tier is beside it.")
    emit("")
    emit(
        f"  {'profile':46s} {'tier':7s} {'set':12s} {'cells':>6s} {'before':>10s} {'after':>10s} "
        f"{'delta':>10s}"
    )
    groups = {}
    for ident, cell in after.items():
        base = before.get(ident)
        if base is None:
            continue
        a, b = delta_e(cell), delta_e(base)
        if a is None or b is None:
            continue
        groups.setdefault((ident[0], TIERS[ident[2]], cell["fixtureSet"]), []).append((b, a))
    for key in sorted(groups):
        pairs = groups[key]
        was = sum(p[0] for p in pairs) / len(pairs)
        now = sum(p[1] for p in pairs) / len(pairs)
        emit(
            f"  {key[0]:46s} {key[1]:7s} {key[2]:12s} {len(pairs):6d} {was:10.5f} {now:10.5f} "
            f"{now - was:+10.5f}"
        )

    emit()
    emit("  worse anywhere? (a positive delta is worse)")
    worse = [(k, v) for k, v in groups.items()
             if sum(p[1] for p in v) / len(v) > sum(p[0] for p in v) / len(v) + 1e-9]
    if not worse:
        emit("    no profile / tier / set group is worse.")
    for key, pairs in sorted(worse):
        was = sum(p[0] for p in pairs) / len(pairs)
        now = sum(p[1] for p in pairs) / len(pairs)
        emit(f"    {key[0]} / {key[1]} / {key[2]}: {was:.5f} → {now:.5f} ({now - was:+.5f})")

    if args.out is not None:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
