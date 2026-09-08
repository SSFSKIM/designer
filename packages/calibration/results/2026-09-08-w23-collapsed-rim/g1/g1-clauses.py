"""W23 G1 — the parent's clauses 1, 2, 3 and 4, each read with numbers, on both canonical beds.

The instrument for 1-3 is the wave's own (X1): the contour read, per side, in linear luminance per
CSS px, `rimLocal` for the fit and `rim` against the eroded body beside it. Clause 4 is re-checked
on W21's DECLARED-GEOMETRY band read instead, because it is W22's clause on W22's instrument and
this wave does not restate other waves' verdicts in its own units (W23 Decision Log 1 (b)).

The clauses, verbatim from the charter's Parent-Level Acceptance:

  1. *Glass on black is visible.* On every collapsed cell of the bed, vitrea's contour rim within
     0.005 of the reference's on every side, and its body within 0.002.
  2. *The rim's law on the solids.* On every untinted texture-tier cell over a solid backdrop at
     both scales in both schemes, the contour rim within 0.03 of the reference's per side; where the
     reference's contour row clips to 1.000 vitrea's does too; `L-R` within 0.003.
  3. *The law holds off the solids.* On the structured calibration cells within 0.05 per side, and
     the validation cells no worse than the calibration cells' mean miss.
  4. *The band read closes.* Under W22's per-side band read, the eighteen sides on the three light
     cells within 0.03 of the reference; no side that met W22 clause 2 leaves it.

    g1-clauses.py <canonical-reads dir> [--out <file>]
"""

import argparse
import json
import math
import os

SIDES = ("top", "bottom", "left", "right")
SOLID = ("dark-solid", "mid-dark-solid", "light-solid")
PROFILES = (
    ("apple-macos-26.5-1x-light-standard", "1x", "light"),
    ("apple-macos-26.5-2x-light-standard", "2x", "light"),
    ("apple-macos-26.5-1x-dark-standard", "1x", "dark"),
    ("apple-macos-26.5-2x-dark-standard", "2x", "dark"),
)
# The cells the charter names as collapsed, from the pixels rather than from the size law: G0's
# definition is "the landed GPU capture's contour rim is exactly 0 on every side" and these are the
# canonical bed's members of that set. W21's probe `dark-solid__rrect-sm` is on the probe grid and
# not on this bed, so it is named in the findings and not read here.
COLLAPSED = ("dark-solid__capsule-button__rest", "impulse__capsule-button__rest")
# The three light cells W22 deferred under the name "the collapsed rim in light" (W22 Decision Log
# 4 (d)) — the eighteen sides clause 4 is written on.
W22_DEFERRED = (
    "dark-solid__rrect-md__rest",
    "impulse__rrect-md__rest",
    "mid-dark-solid__capsule-button__rest",
)
CLAUSE1_RIM, CLAUSE1_BODY = 0.005, 0.002
CLAUSE2_RIM, CLAUSE2_LR = 0.03, 0.003
CLAUSE3_RIM = 0.05
CLAUSE4_BAND = 0.03


def load(directory, profile, tier, when, suffix=""):
    path = os.path.join(directory, f"{profile}-{tier}-{when}{suffix}.json")
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def ok(value):
    return value is not None and not (isinstance(value, float) and math.isnan(value))


def sides(row, field):
    values = row.get(field)
    if not isinstance(values, list):
        return []
    return [(SIDES[i], v) for i, v in enumerate(values) if ok(v)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W23 G1 — the parent's clauses 1-4, read with numbers")
    emit("=" * 118)
    emit("before = the canonical bed at the 0.11.0 landing; after = this gate's dry run.")
    emit("Clauses 1-3 on the contour read (X1); clause 4 on W21's declared-geometry band read.")

    verdicts = {}

    # ---- clause 1 -----------------------------------------------------------------
    emit()
    emit("=== clause 1 — glass on black is visible (rim 0.005, body 0.002), GPU tier ===")
    emit(
        f"  {'cell':44s} {'scheme':6s} {'dpr':3s} {'side':7s} {'native':>9s} {'before':>9s} "
        f"{'after':>9s} {'d after':>9s} {'verdict':>8s}"
    )
    worst1 = 0.0
    misses1 = []
    for profile, dpr, scheme in PROFILES:
        before = load(args.directory, profile, "webgpu", "before")
        after = load(args.directory, profile, "webgpu", "after")
        for scene in COLLAPSED:
            row = after.get(scene)
            was = before.get(scene)
            if row is None or row.get("rimWeb") is None:
                continue
            for index, side in enumerate(SIDES):
                n = row["rimNative"][index]
                now = row["rimWeb"][index]
                if not ok(n) or not ok(now):
                    continue
                had = was["rimWeb"][index] if was and ok(was["rimWeb"][index]) else float("nan")
                d = now - n
                worst1 = max(worst1, abs(d))
                verdict = "ok" if abs(d) <= CLAUSE1_RIM else "MISS"
                if verdict == "MISS":
                    misses1.append((scene, scheme, dpr, side, d))
                emit(
                    f"  {scene:44s} {scheme:6s} {dpr:3s} {side:7s} {n:9.4f} {had:9.4f} "
                    f"{now:9.4f} {d:+9.4f} {verdict:>8s}"
                )
            bn, bw = row.get("bodyNative"), row.get("bodyWeb")
            if ok(bn) and ok(bw):
                d = bw - bn
                verdict = "ok" if abs(d) <= CLAUSE1_BODY else "MISS"
                emit(
                    f"  {scene:44s} {scheme:6s} {dpr:3s} {'body':7s} {bn:9.4f} "
                    f"{float('nan'):9.4f} {bw:9.4f} {d:+9.4f} {verdict:>8s}"
                )
                if verdict == "MISS":
                    misses1.append((scene, scheme, dpr, "body", d))
    emit(f"  worst |rim - native| over every collapsed side: {worst1:.4f} against 0.005")
    verdicts["clause 1"] = (not misses1, f"worst rim side {worst1:.4f} / 0.005", misses1)

    # ---- clauses 2 and 3 ----------------------------------------------------------
    for label, backgrounds, bound, key in (
        ("clause 2 — the rim's law on the solids", SOLID, CLAUSE2_RIM, "clause 2"),
        ("clause 3 — the law holds off the solids", None, CLAUSE3_RIM, "clause 3"),
    ):
        emit()
        emit(f"=== {label} (bound {bound}), GPU tier ===")
        emit(
            f"  {'cell':44s} {'scheme':6s} {'dpr':3s} {'side':7s} {'native':>9s} {'before':>9s} "
            f"{'after':>9s} {'d after':>9s} {'clip':>5s} {'verdict':>8s}"
        )
        misses = []
        worst = 0.0
        by_set = {"calibration": [], "validation": []}
        for profile, dpr, scheme in PROFILES:
            before = load(args.directory, profile, "webgpu", "before")
            after = load(args.directory, profile, "webgpu", "after")
            for scene in sorted(after):
                row = after[scene]
                if row.get("tint") is not None or row.get("rimWeb") is None:
                    continue
                if row.get("set") not in ("calibration", "validation"):
                    continue
                background = row["background"]
                if backgrounds is None:
                    if background in SOLID or scene in COLLAPSED:
                        continue
                else:
                    if background not in backgrounds or scene in COLLAPSED:
                        continue
                was = before.get(scene)
                for index, side in enumerate(SIDES):
                    n = row["rimLocalNative"][index]
                    now = row["rimLocalWeb"][index]
                    clip = row["clipNative"][index]
                    if not ok(n) or not ok(now):
                        continue
                    if ok(clip) and clip > 0.5:
                        # A clipped reference row cannot report how much brighter it wanted to be;
                        # the clause's own words make it a clip check and not an amplitude one.
                        clipped_web = row["clipWeb"][index]
                        emit(
                            f"  {scene:44s} {scheme:6s} {dpr:3s} {side:7s} {n:9.4f} "
                            f"{float('nan'):9.4f} {now:9.4f} {float('nan'):9.4f} "
                            f"{clipped_web:5.2f} {'clip':>8s}"
                        )
                        continue
                    had = was["rimLocalWeb"][index] if was and ok(was["rimLocalWeb"][index]) else float("nan")
                    d = now - n
                    worst = max(worst, abs(d))
                    by_set.setdefault(row["set"], []).append(abs(d))
                    verdict = "ok" if abs(d) <= bound else "MISS"
                    if verdict == "MISS":
                        misses.append((scene, scheme, dpr, side, d))
                    emit(
                        f"  {scene:44s} {scheme:6s} {dpr:3s} {side:7s} {n:9.4f} {had:9.4f} "
                        f"{now:9.4f} {d:+9.4f} {0.0:5.2f} {verdict:>8s}"
                    )
                if backgrounds is not None:
                    lr = None
                    if ok(row["rimLocalWeb"][2]) and ok(row["rimLocalWeb"][3]):
                        lr = row["rimLocalWeb"][2] - row["rimLocalWeb"][3]
                    if lr is not None:
                        verdict = "ok" if abs(lr) <= CLAUSE2_LR else "MISS"
                        emit(
                            f"  {scene:44s} {scheme:6s} {dpr:3s} {'L-R':7s} {float('nan'):9.4f} "
                            f"{float('nan'):9.4f} {lr:9.4f} {lr:+9.4f} {0.0:5.2f} {verdict:>8s}"
                        )
                        if verdict == "MISS":
                            misses.append((scene, scheme, dpr, "L-R", lr))
        cal = by_set.get("calibration") or []
        val = by_set.get("validation") or []
        if cal and val:
            cm, vm = sum(cal) / len(cal), sum(val) / len(val)
            emit(
                f"  calibration mean |d| {cm:.4f} over {len(cal)} sides; validation mean |d| "
                f"{vm:.4f} over {len(val)} — the validation rows must be no worse"
            )
            if key == "clause 3" and vm > cm:
                misses.append(("validation mean", "-", "-", "mean", vm - cm))
        emit(f"  worst |after - native|: {worst:.4f} against {bound}")
        verdicts[key] = (not misses, f"worst {worst:.4f} / {bound}", misses)

    # ---- clause 4 -----------------------------------------------------------------
    emit()
    emit("=== clause 4 — the band read closes on W22's own instrument (bound 0.03), GPU tier ===")
    emit(
        f"  {'cell':44s} {'scheme':6s} {'dpr':3s} {'side':7s} {'native':>9s} {'before':>9s} "
        f"{'after':>9s} {'d after':>9s} {'d before':>9s} {'verdict':>8s}"
    )
    misses4 = []
    left4 = []
    for profile, dpr, scheme in PROFILES:
        try:
            before = load(args.directory, profile, "webgpu", "before", "-band")
            after = load(args.directory, profile, "webgpu", "after", "-band")
        except FileNotFoundError:
            emit(f"  {profile}: no band read on disk")
            continue
        for scene in sorted(after):
            row = after[scene]
            was = before.get(scene)
            if was is None:
                continue
            # The band reader's `rimNative` / `rimWeb` are the declared box's per-side rim-band
            # PEAKS in absolute linear luminance, which is the quantity W22 clause 2 is stated on.
            peaks_n = row.get("rimNative")
            peaks_w = row.get("rimWeb")
            peaks_b = was.get("rimWeb")
            if not isinstance(peaks_n, list) or not isinstance(peaks_w, list):
                continue
            for index, side in enumerate(SIDES):
                n, now = peaks_n[index], peaks_w[index]
                had = peaks_b[index] if isinstance(peaks_b, list) else float("nan")
                if not ok(n) or not ok(now):
                    continue
                d, d0 = now - n, (had - n) if ok(had) else float("nan")
                interesting = scene in W22_DEFERRED
                verdict = "ok" if abs(d) <= CLAUSE4_BAND else "MISS"
                if ok(d0) and abs(d0) <= CLAUSE4_BAND and abs(d) > CLAUSE4_BAND:
                    left4.append((scene, scheme, dpr, side, d0, d))
                    verdict = "LEFT"
                if interesting or verdict != "ok":
                    emit(
                        f"  {scene:44s} {scheme:6s} {dpr:3s} {side:7s} {n:9.4f} {had:9.4f} "
                        f"{now:9.4f} {d:+9.4f} {d0:+9.4f} {verdict:>8s}"
                    )
                if interesting and verdict == "MISS":
                    misses4.append((scene, scheme, dpr, side, d))
    emit(f"  sides that met W22 clause 2 and no longer do: {len(left4)}")
    verdicts["clause 4"] = (not misses4 and not left4,
                            f"{len(misses4)} deferred sides open, {len(left4)} sides left the bound",
                            misses4 + [(a, b, c, d, f) for a, b, c, d, _e, f in left4])

    emit()
    emit("=== the verdicts ===")
    for key in ("clause 1", "clause 2", "clause 3", "clause 4"):
        met, summary, misses = verdicts[key]
        emit(f"  {key}: {'MET' if met else 'MISSED'} — {summary}")
        for miss in misses[:12]:
            emit(f"      {miss}")

    if args.out:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")


main()
