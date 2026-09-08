"""W22 G1 — stops S2 and S3 in spirit, and the four W21 instrument floors re-read.

Three readings the wave's stops name and no other table carries:

  * **S2, the tinted cells** — no tinted cell's body moved by more than 0.002. The fitted constant
    is a rim term and the tint layer sits over it, so a tinted body that moved would say the fit
    reached something it should not have.
  * **S3 in spirit, the collapsed capsules** — the cells whose material has taken its backdrop's
    tone draw no lit edge at all (`present` scales the whole band), so they must not move either.
    W21's own S3 is written on the dark bed; it is read here on both.
  * **The four W21 instrument floors on the 2x dark nested pane** — `texture` silhouetteIoU, `dom`
    silhouetteIoU, `dom` contourDistanceMean and `dom` contourDistanceP95 on
    `checkerboard__glass-over-glass__rest`. They sit on a HOLDOUT cell, so G0 could not touch them
    and this gate is the first that can (X5). `adopted-thresholds.test.ts` enforces them; this
    prints the numbers beside the pinned floors so the margin is legible whichever way the gate goes.

    stops.py --reads <canonical-reads dir> --matrix <dry-run matrix.json> [--out <file>]
"""

import argparse
import json
import os

BODY_STOP = 0.002
PROFILES = (
    ("apple-macos-26.5-1x-light-standard", "1x", "light"),
    ("apple-macos-26.5-2x-light-standard", "2x", "light"),
    ("apple-macos-26.5-1x-dark-standard", "1x", "dark"),
    ("apple-macos-26.5-2x-dark-standard", "2x", "dark"),
)
# The four rows W21 pinned as floors on the 2x dark nested pane, with the floors themselves as
# `adopted-thresholds.test.ts` records them. `direction` is which way is worse.
W21_FLOORS = (
    ("texture", "shape", "silhouetteIoU", 0.9257, "at least"),
    ("dom", "shape", "silhouetteIoU", 0.9038, "at least"),
    ("dom", "shape", "contourDistanceMean", 1.8602, "at most"),
    ("dom", "shape", "contourDistanceP95", 13.1, "at most"),
)
FLOOR_CELL = ("checkerboard__glass-over-glass__rest", "apple-macos-26.5-2x-dark-standard")


def load(directory, profile, tier, when):
    path = os.path.join(directory, f"{profile}-{tier}-{when}.json")
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def value(cell, axis, field):
    node = cell.get(axis)
    if not isinstance(node, dict):
        return None
    entry = node.get(field)
    if isinstance(entry, dict):
        return entry.get("value")
    return entry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", required=True)
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W22 G1 — stops S2 and S3, and the four W21 instrument floors")
    emit("=" * 108)

    for label, want_tint in (("S2 — the tinted cells", True), ("S3 — the collapsed cells", False)):
        emit()
        emit(f"=== {label}: body before → after, the stop at {BODY_STOP} ===")
        emit(
            f"  {'cell':44s} {'scheme':6s} {'dpr':3s} {'tier':7s} {'native':>8s} {'before':>8s} "
            f"{'after':>8s} {'moved':>9s} {'stop':>6s}"
        )
        fired = 0
        for tier in ("webgpu", "css"):
            for profile, dpr, scheme in PROFILES:
                before = load(args.reads, profile, tier, "before")
                after = load(args.reads, profile, tier, "after")
                for scene in sorted(after):
                    row, was = after[scene], before.get(scene)
                    if row.get("bodyWeb") is None or was is None or was.get("bodyWeb") is None:
                        continue
                    tinted = row.get("tint") is not None
                    if tinted != want_tint:
                        continue
                    if not want_tint:
                        # "Collapsed" is a reading, not a label: the body sits within a code step
                        # of its own backdrop on the reference side.
                        if abs(row["bodyNative"] - row["backdropLinearMean"]) > 0.008:
                            continue
                    moved = row["bodyWeb"] - was["bodyWeb"]
                    hit = abs(moved) > BODY_STOP
                    fired += 1 if hit else 0
                    emit(
                        f"  {scene:44s} {scheme:6s} {dpr:3s} {tier:7s} {row['bodyNative']:8.4f} "
                        f"{was['bodyWeb']:8.4f} {row['bodyWeb']:8.4f} {moved:+9.4f} "
                        f"{'FIRES' if hit else 'ok':>6s}"
                    )
        emit(f"  → {fired} cell(s) past the stop.")

    emit()
    emit("=== the four W21 instrument floors on the 2x dark nested pane, re-read ===")
    scene, profile = FLOOR_CELL
    matrix = json.load(open(args.matrix))
    emit(f"  {'tier':8s} {'row':24s} {'measured':>10s} {'floor':>10s} {'direction':>10s} {'':>8s}")
    for tier, axis, field, floor, direction in W21_FLOORS:
        found = None
        for cell in matrix["cells"]:
            if (
                cell["key"]["profileKey"] == profile
                and cell["key"]["sceneId"] == scene
                and cell["tier"] == tier
            ):
                if found is None or cell["capturedAt"] > found["capturedAt"]:
                    found = cell
        measured = None if found is None else value(found, axis, field)
        if measured is None:
            emit(f"  {tier:8s} {field:24s} {'absent':>10s} {floor:10.4f} {direction:>10s}")
            continue
        ok = measured >= floor if direction == "at least" else measured <= floor
        emit(
            f"  {tier:8s} {field:24s} {measured:10.5f} {floor:10.4f} {direction:>10s} "
            f"{'held' if ok else 'BROKEN':>8s}"
        )

    if args.out is not None:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
