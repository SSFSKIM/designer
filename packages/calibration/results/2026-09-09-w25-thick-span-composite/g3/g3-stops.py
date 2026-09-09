"""W25 G3 — the stops this wave adds to W24 G2's list, read with numbers.

`stops.py` beside this file carries S1, S2, S7 and S11's straight-span half unchanged. This one
reads the three the parent's dispatch adds and the half of S11 it widens:

  * **S11's angular family** — W24's per-bin rim reads, before and after, on every untinted solid
    row of both canonical beds. The along-side field grades the rim's amplitude by POSITION; W24's
    exponent grades it by the normal's DIRECTION. A bin's mean folds both, so the bins are where a
    position term that had accidentally re-aimed the light would show. The bound is the family's
    own: 0.005 on any bin, which is S11's number read on the other reader.
  * **S12 — any THIN cell moved by more than 0.001 ΔE** (X5). Thin is span at or below 44, which is
    the capsule and `rrect-sm` and the toolbar group's members; `sizeThickness` is 0 at 32 and
    0.0923 at 44, so 44 is the thin end's whole exposure and the only thin span that can move at
    all.
  * **S13 — a golden moved outside a thick surface's body or rim.** Read out of
    `goldens-attribution.txt`, which is the per-pixel measurement the hashes cannot carry: the
    largest delta OUTSIDE a contour band, over every scene.
  * **S14 — a probe row worse by more than 0.002 ΔE at the fitted constants than at the inert
    ones.** Read off the probe set's own matrices at the two materials, which is where this wave's
    constants were fitted and therefore where a fit that had bought its own rows at the expense of
    the rest would show.

    g3-stops.py --reads <canonical-reads dir> --before <matrix.json> --after <matrix.json>
                --probe-inert <probe matrix> --probe-landed <probe matrix>
                --goldens <goldens-attribution.txt> [--out <file>]
"""

import argparse
import json
import math
import os
import re

BIN_STOP = 0.005
THIN_DELTA_E_STOP = 0.001
THIN_SPAN = 44.0
PROBE_STOP = 0.002
TIERS = {"texture": "webgpu", "dom": "css"}
SOLID_BACKGROUNDS = ("dark-solid", "mid-dark-solid", "light-solid")
PROFILES = (
    "apple-macos-26.5-1x-light-standard",
    "apple-macos-26.5-2x-light-standard",
    "apple-macos-26.5-1x-light-increased-contrast",
    "apple-macos-26.5-1x-light-reduced-transparency",
    "apple-macos-26.5-1x-dark-standard",
    "apple-macos-26.5-2x-dark-standard",
)
SCENES = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "..", "..", "..", "..",
                                      "apps", "reference-apple", "scenes.json"))


def identity(cell):
    return (cell["key"]["profileKey"], cell["key"]["sceneId"], cell["tier"],
            cell["key"]["web"]["renderer"])


def delta_e(cell):
    entry = (cell.get("perceptual") or {}).get("oklabDeltaEMean")
    if isinstance(entry, dict):
        entry = entry.get("value")
    return entry if isinstance(entry, (int, float)) and not math.isnan(entry) else None


def spans():
    scenes = json.load(open(SCENES))
    comps = scenes["components"]
    out = {}
    for scene in scenes["scenes"]:
        spec = comps[scene["component"]]
        if spec["kind"] == "stack":
            out[scene["id"]] = float(min(spec["base"]["size"]))
        elif spec["kind"] == "group":
            out[scene["id"]] = float(min(spec["items"][0]["size"]))
        else:
            out[scene["id"]] = float(min(spec["size"]))
    return out


def angular(directory, profile, tier, when):
    path = os.path.join(directory, f"{profile}-{tier}-{when}-angular.json")
    if not os.path.exists(path):
        return {}
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--probe-inert", required=True)
    ap.add_argument("--probe-landed", required=True)
    ap.add_argument("--goldens", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W25 G3 — S11's angular family, S12, S13 and S14, read with numbers")
    emit("=" * 112)

    # ------------------------------------------------------------------ S11, the angular half
    emit()
    emit("=== S11 (angular) — W24's per-bin rim reads on every untinted solid row (bound 0.005) ===")
    emit(f"  {'profile':46s} {'scene':40s} {'tier':6s} {'bin':5s} {'before':>9s} {'after':>9s} "
         f"{'Δ':>9s}")
    worst_bin = 0.0
    fired = 0
    rows_read = 0
    for profile in PROFILES:
        for tier in ("webgpu", "css"):
            was, now = angular(args.reads, profile, tier, "before"), angular(args.reads, profile,
                                                                            tier, "after")
            for scene in sorted(now):
                row, old = now[scene], was.get(scene)
                if old is None or row.get("tint") is not None:
                    continue
                if row.get("background") not in SOLID_BACKGROUNDS:
                    continue
                # A row whose web side the reader could not read at all — a capture the profile
                # does not declare, or a contour it refused — has no bins to compare and is not a
                # reading either way.
                if not isinstance(row.get("web"), dict) or not isinstance(old.get("web"), dict):
                    continue
                a, b = row["web"].get("bins"), old["web"].get("bins")
                if not isinstance(a, list) or not isinstance(b, list):
                    continue
                rows_read += 1
                for index in range(min(len(a), len(b))):
                    if a[index] is None or b[index] is None:
                        continue
                    d = a[index] - b[index]
                    worst_bin = max(worst_bin, abs(d))
                    if abs(d) > BIN_STOP:
                        fired += 1
                        emit(f"  {profile:46s} {scene:40s} {tier:6s} {index:5d} {b[index]:9.5f} "
                             f"{a[index]:9.5f} {d:+9.5f}")
    emit(f"  {rows_read} rows read; worst |Δ bin| {worst_bin:.5f} against {BIN_STOP}; "
         f"bins firing: {fired}")

    # A bin that MOVED is not a bin that got worse, and on this wave's mechanism the two are
    # different questions: the field grades the rim's amplitude by POSITION, and on a rounded
    # rectangle a bin of the normal's direction is a position, so the bins move by construction.
    # What decides whether the movement is the mechanism working is the bin's ERROR against the
    # reference, which is read here beside it, per row and per compass bin.
    emit()
    emit("  the same bins as ERROR against the reference, |web − native|, before -> after:")
    emit(f"  {'profile':46s} {'scene':40s} {'tier':6s} {'mean|e| before':>14s} "
         f"{'after':>10s} {'worst before':>13s} {'after':>10s}")
    improved = 0
    worsened = 0
    for profile in PROFILES:
        for tier in ("webgpu", "css"):
            was, now = angular(args.reads, profile, tier, "before"), angular(args.reads, profile,
                                                                            tier, "after")
            for scene in sorted(now):
                row, old = now[scene], was.get(scene)
                if old is None or row.get("tint") is not None:
                    continue
                if row.get("background") not in SOLID_BACKGROUNDS:
                    continue
                if not isinstance(row.get("web"), dict) or not isinstance(old.get("web"), dict):
                    continue
                ref = row.get("native", {}).get("bins")
                a, b = row["web"].get("bins"), old["web"].get("bins")
                if not (isinstance(ref, list) and isinstance(a, list) and isinstance(b, list)):
                    continue
                ea = [abs(a[i] - ref[i]) for i in range(min(len(a), len(ref)))
                      if a[i] is not None and ref[i] is not None]
                eb = [abs(b[i] - ref[i]) for i in range(min(len(b), len(ref)))
                      if b[i] is not None and ref[i] is not None]
                if not ea or not eb:
                    continue
                ma, mb = sum(ea) / len(ea), sum(eb) / len(eb)
                if ma < mb:
                    improved += 1
                elif ma > mb:
                    worsened += 1
                emit(f"  {profile:46s} {scene:40s} {tier:6s} {mb:14.5f} {ma:10.5f} "
                     f"{max(eb):13.5f} {max(ea):10.5f}")
    emit(f"  rows whose mean bin error IMPROVED: {improved}; worsened: {worsened}")

    # ------------------------------------------------------------------ S12, the thin cells
    span = spans()
    before = {identity(c): c for c in json.load(open(args.before))["cells"]}
    after = {identity(c): c for c in json.load(open(args.after))["cells"]}
    emit()
    emit(f"=== S12 — every THIN cell (span <= {THIN_SPAN:g}) against the 0.13.0 bed "
         f"(bound {THIN_DELTA_E_STOP}) ===")
    worst_thin = -1.0
    worst_key = None
    thin_cells = 0
    thin_fired = []
    for ident, cell in sorted(after.items()):
        if span.get(ident[1], 0.0) > THIN_SPAN:
            continue
        base = before.get(ident)
        if base is None:
            continue
        a, b = delta_e(cell), delta_e(base)
        if a is None or b is None:
            continue
        thin_cells += 1
        d = a - b
        if d > worst_thin:
            worst_thin, worst_key = d, ident
        if d > THIN_DELTA_E_STOP:
            thin_fired.append((ident, d))
            emit(f"  {ident[0]:46s} {ident[1]:40s} {TIERS[ident[2]]:6s} {d:+10.6f} FIRES")
    emit(f"  {thin_cells} thin cells; worst rise {worst_thin:+.6f} on "
         f"{worst_key[0] if worst_key else '—'} / {worst_key[1] if worst_key else '—'} / "
         f"{TIERS[worst_key[2]] if worst_key else '—'}; cells firing: {len(thin_fired)}")

    # ------------------------------------------------------------------ S13, the goldens
    emit()
    emit("=== S13 — a golden moved outside a thick surface's body or rim ===")
    emit("  read out of goldens-attribution.txt: the largest delta OUTSIDE a contour band.")
    worst_outside = None
    for line in open(args.goldens):
        match = re.match(r"^(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", line.strip())
        if not match:
            continue
        scene, scene_span, in_band, outside, moved_in, moved_out = match.groups()
        emit(f"  {scene:26s} span {scene_span:>4s} inBand {in_band:>4s} outside {outside:>4s} "
             f"movedIn {moved_in:>6s} movedOut {moved_out:>4s}")
        worst_outside = max(worst_outside or 0, int(outside))
    emit(f"  largest movement outside any contour band, over every scene: {worst_outside}")

    # ------------------------------------------------------------------ S14, the probe rows
    inert = {identity(c): c for c in json.load(open(args.probe_inert))["cells"]}
    landed = {identity(c): c for c in json.load(open(args.probe_landed))["cells"]}
    emit()
    emit(f"=== S14 — every PROBE row, inert -> fitted (bound {PROBE_STOP}) ===")
    worst_probe = -1.0
    worst_probe_key = None
    probe_fired = []
    n = 0
    for ident, cell in sorted(landed.items()):
        base = inert.get(ident)
        if base is None:
            continue
        a, b = delta_e(cell), delta_e(base)
        if a is None or b is None:
            continue
        n += 1
        d = a - b
        if d > worst_probe:
            worst_probe, worst_probe_key = d, ident
        if d > PROBE_STOP:
            probe_fired.append((ident, d))
            emit(f"  {ident[0]:46s} {ident[1]:40s} {TIERS[ident[2]]:6s} {d:+10.6f} FIRES")
    emit(f"  {n} probe cells; worst rise {worst_probe:+.6f} on "
         f"{worst_probe_key[0] if worst_probe_key else '—'} / "
         f"{worst_probe_key[1] if worst_probe_key else '—'}; cells firing: {len(probe_fired)}")

    emit()
    emit("summary")
    emit(f"  S11 (angular)  worst |Δ bin| {worst_bin:.5f} / {BIN_STOP}      "
         f"{'FIRES' if fired else 'clear'}")
    emit(f"  S12            worst rise {worst_thin:+.6f} / {THIN_DELTA_E_STOP}   "
         f"{'FIRES' if thin_fired else 'clear'}")
    emit(f"  S13            worst outside a band {worst_outside}            "
         f"{'FIRES' if (worst_outside or 0) > 0 else 'clear'}")
    emit(f"  S14            worst rise {worst_probe:+.6f} / {PROBE_STOP}   "
         f"{'FIRES' if probe_fired else 'clear'}")

    if args.out:
        with open(args.out, "w") as handle:
            handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
