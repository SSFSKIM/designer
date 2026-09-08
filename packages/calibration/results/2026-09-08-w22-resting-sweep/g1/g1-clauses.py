"""W22 G1 (3a) — the parent's clause 2, per side, on both canonical beds.

Clause 2, verbatim from the charter: *on every untinted texture-tier cell over a solid backdrop at
both scales, in both schemes: the left side within 0.03 of the right, and each side's rim-band peak
within 0.03 of the reference's under the declared geometry.* On the dark bed W21 clause 4's two open
cells (`dark-solid__rrect-md`, `mid-dark-solid__capsule-button`, left side) must close.

Read from `read-canonical.sh`'s output — W21's declared-geometry instrument (X2) applied to the
canonical bed's native fixtures against vitrea BEFORE (the canonical `web-captures/` in the main
checkout, the W21 bed at the 0.10.0 landing) and AFTER (this gate's dry run).

Two contrasts are printed beside the per-side terms, and only these two, because they are the only
ones the instrument states cleanly: the declared box's rim band is a RECTANGLE's band and a rounded
shape does not fill it, so a side's peak mixes rim with background at a weight that differs between
the horizontal and the vertical pair — `L−R` and `T−B` compare sides of identical geometry and the
mixture cancels in them exactly (W22 Decision Log 2 (c); claims §5.94 §3).

    g1-clauses.py <canonical-reads dir> [--out <file>]
"""

import argparse
import json
import os

SOLID_BACKGROUNDS = ("dark-solid", "mid-dark-solid", "light-solid", "impulse")
RIM_CLAUSE = 0.03
SIDES = ("top", "bottom", "left", "right")
PROFILES = (
    ("apple-macos-26.5-1x-light-standard", "1x", "light"),
    ("apple-macos-26.5-2x-light-standard", "2x", "light"),
    ("apple-macos-26.5-1x-dark-standard", "1x", "dark"),
    ("apple-macos-26.5-2x-dark-standard", "2x", "dark"),
)
# The two cells W21 clause 4 left open on the left side (claims §5.90 §5), named so the verdict on
# them is a line of this table rather than a claim about it.
W21_OPEN = ("dark-solid__rrect-md__rest", "mid-dark-solid__capsule-button__rest")


def load(directory, profile, tier, when):
    path = os.path.join(directory, f"{profile}-{tier}-{when}.json")
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W22 G1 — clause 2, the rim per side over a solid backdrop, both beds, both scales")
    emit("=" * 118)
    emit("native | before (the canonical W21 bed) | after (this gate's dry run); the clause is 0.03")
    emit("both on |after − native| per side and on |L−R| within itself.")

    for tier in ("webgpu", "css"):
        emit()
        emit(f"=== clause 2 per side, {tier} tier ===")
        emit(
            f"  {'cell':44s} {'scheme':6s} {'dpr':3s} {'side':7s} {'native':>8s} {'before':>8s} "
            f"{'after':>8s} {'Δ after':>9s} {'verdict':>8s}"
        )
        missed = []
        for profile, dpr, scheme in PROFILES:
            before = load(args.directory, profile, tier, "before")
            after = load(args.directory, profile, tier, "after")
            for scene in sorted(after):
                if scene.split("__")[0] not in SOLID_BACKGROUNDS or "tint" in scene:
                    continue
                row, was = after[scene], before.get(scene)
                if row.get("rimWeb") is None:
                    continue
                for index, side in enumerate(SIDES):
                    native = row["rimNative"][index]
                    now = row["rimWeb"][index]
                    then = (
                        was["rimWeb"][index]
                        if was is not None and was.get("rimWeb") is not None
                        else float("nan")
                    )
                    delta = now - native
                    verdict = "met" if abs(delta) <= RIM_CLAUSE else "MISSED"
                    if verdict == "MISSED":
                        missed.append((scheme, dpr, scene, side, native, now, delta))
                    emit(
                        f"  {scene:44s} {scheme:6s} {dpr:3s} {side:7s} {native:8.4f} {then:8.4f} "
                        f"{now:8.4f} {delta:+9.4f} {verdict:>8s}"
                    )
                # The two clean contrasts, native against web, before and after.
                for label, (a, b) in (("L-R", (2, 3)), ("T-B", (0, 1))):
                    native_c = row["rimNative"][a] - row["rimNative"][b]
                    now_c = row["rimWeb"][a] - row["rimWeb"][b]
                    then_c = (
                        was["rimWeb"][a] - was["rimWeb"][b]
                        if was is not None and was.get("rimWeb") is not None
                        else float("nan")
                    )
                    inner = "met" if abs(now_c) <= RIM_CLAUSE else "MISSED"
                    emit(
                        f"  {scene:44s} {scheme:6s} {dpr:3s} {label:7s} {native_c:8.4f} "
                        f"{then_c:8.4f} {now_c:8.4f} {now_c - native_c:+9.4f} "
                        f"{(inner if label == 'L-R' else ''):>8s}"
                    )
        emit()
        emit(f"  clause 2 on the {tier} tier: {len(missed)} side(s) missed")
        for scheme, dpr, scene, side, native, now, delta in missed:
            emit(
                f"    MISSED {scheme:6s} {dpr} {scene:44s} {side:7s} native {native:.4f} "
                f"after {now:.4f} ({delta:+.4f})"
            )

        # The same verdict on the BEFORE column, so a miss that this gate created is legible apart
        # from one it inherited. A clause is a bound on the bed, not on the change, and both
        # readings are needed to say which of the two the wave is looking at.
        emit()
        emit(f"  what moved across the clause on the {tier} tier")
        newly_missed, newly_met, held = [], [], 0
        for profile, dpr, scheme in PROFILES:
            before = load(args.directory, profile, tier, "before")
            after = load(args.directory, profile, tier, "after")
            for scene in sorted(after):
                if scene.split("__")[0] not in SOLID_BACKGROUNDS or "tint" in scene:
                    continue
                row, was = after[scene], before.get(scene)
                if row.get("rimWeb") is None or was is None or was.get("rimWeb") is None:
                    continue
                for index, side in enumerate(SIDES):
                    native = row["rimNative"][index]
                    then_ok = abs(was["rimWeb"][index] - native) <= RIM_CLAUSE
                    now_ok = abs(row["rimWeb"][index] - native) <= RIM_CLAUSE
                    if then_ok and not now_ok:
                        newly_missed.append(
                            (scheme, dpr, scene, side, native, was["rimWeb"][index],
                             row["rimWeb"][index])
                        )
                    elif now_ok and not then_ok:
                        newly_met.append(
                            (scheme, dpr, scene, side, native, was["rimWeb"][index],
                             row["rimWeb"][index])
                        )
                    else:
                        held += 1
        emit(f"    newly MET {len(newly_met)}, newly MISSED {len(newly_missed)}, unchanged {held}")
        for label, rows in (("newly MET", newly_met), ("newly MISSED", newly_missed)):
            for scheme, dpr, scene, side, native, then, now in rows:
                emit(
                    f"    {label:12s} {scheme:6s} {dpr} {scene:44s} {side:7s} native {native:.4f} "
                    f"before {then:.4f} → after {now:.4f}"
                )

    # W21's two open cells, called by name on the GPU tier.
    emit()
    emit("=== W21 clause 4's two open cells, on the dark bed, GPU tier ===")
    for profile, dpr, scheme in PROFILES:
        if scheme != "dark":
            continue
        before = load(args.directory, profile, "webgpu", "before")
        after = load(args.directory, profile, "webgpu", "after")
        for scene in W21_OPEN:
            row, was = after.get(scene), before.get(scene)
            if row is None or row.get("rimWeb") is None:
                emit(f"  {scene:44s} {dpr:3s} not readable on this profile")
                continue
            lr_before = (
                was["rimWeb"][2] - was["rimWeb"][3]
                if was is not None and was.get("rimWeb") is not None
                else float("nan")
            )
            lr_after = row["rimWeb"][2] - row["rimWeb"][3]
            left_delta = row["rimWeb"][2] - row["rimNative"][2]
            emit(
                f"  {scene:44s} {dpr:3s} L−R before {lr_before:+.4f} → after {lr_after:+.4f}; "
                f"left |Δ| against the reference {abs(left_delta):.4f} "
                f"({'met' if abs(left_delta) <= RIM_CLAUSE else 'MISSED'})"
            )

    if args.out is not None:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
