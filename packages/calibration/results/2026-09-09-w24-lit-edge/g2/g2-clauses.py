"""W24 G2 — the parent's clauses 1 and 3, read off the two beds with numbers.

Clause 2 is the impulse instrument's and is run by `run-impulse.sh`; clauses 4-7 are the matrix's,
the goldens' and the tier's and are read by `delta-e.py`, `stops.py`, `byte-identity.py` and the
golden attribution. What is here is the pair that needs the angular reader.

**Clause 1, as W24 Decision Log 2 (b) re-declared it.** On every untinted SOLID cell of both beds at
both scales:

  * the ratio of the brightest 22.5 deg bin to the dimmest within 20 % of the reference's, on every
    cell where the reference's ratio EXCEEDS 2 — the cells where there is an angular profile to
    match at all; and
  * the worst bin error no more than HALF the landed bed's, on every untinted solid row.

The absolute bin bound the charter carried (0.005 dark / 0.03 light) is not this term's: the
residual it leaves is W23's amplitude, which on the light bed is 0.05-0.10 of a bin. Both halves are
printed per row either way, so the bound that was replaced is legible beside the one that replaced
it.

A bin is skipped where the reader itself declares it unreadable — truncated, clipped, or with its
peak outside the declared contour — on either side, which is the instrument declaring its own loss
rather than reporting a number it did not measure.

**Clause 3, as W24 Decision Log 2 (f) answered it.** The dark structured thin capsules run `k` = 0,
so no transmission constant can reach them; what is checked here is that they did not move — their
bodies, before and after, on both scales in both schemes.

    g2-clauses.py <canonical-reads dir> [--out <file>]
"""

import argparse
import json
import math
import os

SOLID = ("dark-solid", "mid-dark-solid", "light-solid")
RATIO_GATE = 2.0
RATIO_TOLERANCE = 0.20
STRUCTURED_THIN = (
    "checkerboard__capsule-button__rest",
    "photo__capsule-button__rest",
)
PROFILES = (
    ("apple-macos-26.5-1x-light-standard", "1x", "light"),
    ("apple-macos-26.5-2x-light-standard", "2x", "light"),
    ("apple-macos-26.5-1x-dark-standard", "1x", "dark"),
    ("apple-macos-26.5-2x-dark-standard", "2x", "dark"),
    ("apple-macos-26.5-1x-light-increased-contrast", "1x", "light-ic"),
    ("apple-macos-26.5-1x-light-reduced-transparency", "1x", "light-rt"),
)


def ok(value):
    return value is not None and not (isinstance(value, float) and math.isnan(value))


def load(directory, profile, tier, when, suffix):
    path = os.path.join(directory, f"{profile}-{tier}-{when}{suffix}.json")
    if not os.path.exists(path):
        return {}
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def readable(side, index):
    """A bin the instrument itself vouches for, on one side of the comparison."""
    for field in ("truncatedFraction", "clipFraction", "outsideFraction"):
        values = side.get(field)
        if isinstance(values, list) and index < len(values):
            value = values[index]
            if ok(value) and value > 0.05:
                return False
    bins = side.get("bins")
    return isinstance(bins, list) and index < len(bins) and ok(bins[index])


def worst_bin_error(row, web_key):
    native = row.get("native") or {}
    web = row.get(web_key) or {}
    if not native or not web:
        return None, 0
    worst = 0.0
    counted = 0
    for index in range(len(native.get("bins") or [])):
        if not readable(native, index) or not readable(web, index):
            continue
        worst = max(worst, abs((web["bins"][index]) - (native["bins"][index])))
        counted += 1
    return (worst if counted else None), counted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reads")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W24 G2 — clauses 1 and 3, read on the angular instrument and on the eroded body")
    emit("=" * 118)
    emit("before = the landed 0.12.0 bed (the W23 bed); after = this gate's dry run.")
    emit("Clause 1 is W24 Decision Log 2 (b)'s: the ratio within 20 % where the reference's")
    emit("exceeds 2, and the worst bin error no more than half the landed bed's.")

    emit()
    emit("=== CLAUSE 1 (a) — the brightest/dimmest bin ratio, GPU tier, untinted solid rows ===")
    emit(
        f"  {'profile':46s} {'scene':40s} {'ref':>8s} {'before':>8s} {'after':>8s} "
        f"{'after/ref':>10s} {'verdict':>9s}"
    )
    ratio_rows = 0
    ratio_met = 0
    for profile, _dpr, _scheme in PROFILES:
        after = load(args.reads, profile, "webgpu", "after", "-angular")
        before = load(args.reads, profile, "webgpu", "before", "-angular")
        for scene in sorted(after):
            row = after[scene]
            old = before.get(scene)
            if old is None or row.get("tint") is not None:
                continue
            if row.get("background") not in SOLID:
                continue
            native = (row.get("native") or {}).get("ratio")
            new = (row.get("web") or {}).get("ratio")
            was = (old.get("web") or {}).get("ratio")
            if not ok(native) or not ok(new) or native <= RATIO_GATE:
                continue
            ratio_rows += 1
            share = new / native
            met = abs(share - 1.0) <= RATIO_TOLERANCE
            ratio_met += 1 if met else 0
            emit(
                f"  {profile:46s} {scene:40s} {native:8.2f} "
                f"{(was if ok(was) else float('nan')):8.2f} {new:8.2f} {share:10.2f} "
                f"{('met' if met else 'MISSED'):>9s}"
            )
    emit(f"  rows where the reference's ratio exceeds {RATIO_GATE:g}: {ratio_rows}; met {ratio_met}")

    emit()
    emit("=== CLAUSE 1 (b) — the worst bin error, GPU tier, untinted solid rows ===")
    emit("  bound: no more than HALF the landed bed's, per row.")
    emit(
        f"  {'profile':46s} {'scene':40s} {'bins':>5s} {'before':>9s} {'after':>9s} "
        f"{'share':>7s} {'verdict':>9s}"
    )
    err_rows = 0
    err_met = 0
    for profile, _dpr, _scheme in PROFILES:
        after = load(args.reads, profile, "webgpu", "after", "-angular")
        before = load(args.reads, profile, "webgpu", "before", "-angular")
        for scene in sorted(after):
            row = after[scene]
            old = before.get(scene)
            if old is None or row.get("tint") is not None:
                continue
            if row.get("background") not in SOLID:
                continue
            new, counted = worst_bin_error(row, "web")
            was, _ = worst_bin_error(old, "web")
            if not ok(new) or not ok(was) or was <= 0:
                continue
            err_rows += 1
            share = new / was
            met = share <= 0.5
            err_met += 1 if met else 0
            emit(
                f"  {profile:46s} {scene:40s} {counted:5d} {was:9.4f} {new:9.4f} {share:7.2f} "
                f"{('met' if met else 'MISSED'):>9s}"
            )
    emit(f"  untinted solid rows read: {err_rows}; at or under half the landed bed's: {err_met}")

    emit()
    emit("=== CLAUSE 1 — the same two, on the CSS tier, as context (X5) ===")
    emit("  This tier draws one border alpha the whole way round and cannot carry an angular")
    emit("  profile in any form; what moves here is the band's derived interior light.")
    emit(
        f"  {'profile':46s} {'scene':40s} {'ref':>8s} {'before':>8s} {'after':>8s}"
    )
    for profile, _dpr, _scheme in PROFILES:
        after = load(args.reads, profile, "css", "after", "-angular")
        before = load(args.reads, profile, "css", "before", "-angular")
        for scene in sorted(after):
            row = after[scene]
            old = before.get(scene)
            if old is None or row.get("tint") is not None:
                continue
            if row.get("background") not in SOLID:
                continue
            native = (row.get("native") or {}).get("ratio")
            new = (row.get("web") or {}).get("ratio")
            was = (old.get("web") or {}).get("ratio")
            if not ok(native) or not ok(new):
                continue
            emit(
                f"  {profile:46s} {scene:40s} {native:8.2f} "
                f"{(was if ok(was) else float('nan')):8.2f} {new:8.2f}"
            )

    emit()
    emit("=== CLAUSE 3 — the dark structured thin capsules did not move ===")
    emit("  Their `k` is 0.0000 at both scales in both schemes (W24 G1 §4, read off the running")
    emit("  system's own published group state), so no transmission constant reaches them; what")
    emit("  is read here is that nothing else did either.")
    emit(
        f"  {'profile':46s} {'scene':40s} {'tier':6s} {'native':>9s} {'before':>9s} "
        f"{'after':>9s} {'Δ':>9s}"
    )
    worst = 0.0
    for profile, _dpr, _scheme in PROFILES:
        for tier in ("webgpu", "css"):
            after = load(args.reads, profile, tier, "after", "")
            before = load(args.reads, profile, tier, "before", "")
            for scene in STRUCTURED_THIN:
                row, old = after.get(scene), before.get(scene)
                if row is None or old is None:
                    continue
                a, b, n = row.get("bodyWeb"), old.get("bodyWeb"), row.get("bodyNative")
                if not ok(a) or not ok(b):
                    continue
                worst = max(worst, abs(a - b))
                emit(
                    f"  {profile:46s} {scene:40s} {tier:6s} "
                    f"{(n if ok(n) else float('nan')):9.5f} {b:9.5f} {a:9.5f} {a - b:+9.5f}"
                )
    emit(f"  worst |Δ body| on the cells clause 3 names: {worst:.5f}")

    if args.out:
        open(args.out, "w").write("\n".join(lines) + "\n")


main()
