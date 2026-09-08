"""W23 G3 — the stops S1, S2 and S7, and the floors re-read.

Three of the wave's eight stops are readings no clause table carries, and they are here:

  * **S1 — no untinted row worse than the W22 bed by more than 0.001 ΔE mean or 0.005 `ssimMean`.**
    Read per cell off the two matrices, split by tier, because the parent's clause 5 is stated on
    the GPU tier and the CSS tier's captures move for their own reason this wave (X5).
  * **S2 — no tinted cell's body moved by more than 0.002.** The law is a rim term and the author's
    colour sits over it, so a tinted body that moved would say the change reached something it
    should not have. Read on the contour instrument's own body (W21's eroded box).
  * **S7 — no collapsed cell's body moved by more than 0.002.** The collapse's body is the
    backdrop's tone and this wave gives it a rim, not a level; a body that moved would mean the rim
    leaked into the interior.

and the eleven floors `adopted-thresholds.test.ts` pins are re-read beside them, with the margin
legible either way, because a floor whose cell recovers goes inert and is removed with its reason.

    stops.py --reads <canonical-reads dir> --before <matrix.json> --after <matrix.json>
             [--out <file>]
"""

import argparse
import json
import math
import os

BODY_STOP = 0.002
DELTA_E_STOP = 0.001
SSIM_STOP = 0.005
TIERS = {"texture": "webgpu", "dom": "css"}
PROFILES = (
    ("apple-macos-26.5-1x-light-standard", "1x", "light"),
    ("apple-macos-26.5-2x-light-standard", "2x", "light"),
    ("apple-macos-26.5-1x-light-increased-contrast", "1x", "light-ic"),
    ("apple-macos-26.5-1x-light-reduced-transparency", "1x", "light-rt"),
    ("apple-macos-26.5-1x-dark-standard", "1x", "dark"),
    ("apple-macos-26.5-2x-dark-standard", "2x", "dark"),
)
COLLAPSED = ("dark-solid__capsule-button__rest", "impulse__capsule-button__rest")


def load_reads(directory, profile, tier, when):
    path = os.path.join(directory, f"{profile}-{tier}-{when}.json")
    if not os.path.exists(path):
        return {}
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def identity(cell):
    return (
        cell["key"]["profileKey"],
        cell["key"]["sceneId"],
        cell["tier"],
        cell["key"]["web"]["renderer"],
    )


def metric(cell, axis, field):
    node = cell.get(axis)
    if not isinstance(node, dict):
        return None
    entry = node.get(field)
    if isinstance(entry, dict):
        return entry.get("value")
    return entry


def ok(value):
    return value is not None and not (isinstance(value, float) and math.isnan(value))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lines = []

    def emit(text=""):
        lines.append(text)
        print(text)

    emit("W23 G3 — the stops S1, S2 and S7, read with numbers")
    emit("=" * 112)

    before = {identity(c): c for c in json.load(open(args.before))["cells"]}
    after = {identity(c): c for c in json.load(open(args.after))["cells"]}

    emit()
    emit("=== S1 — every row's ΔE mean and ssimMean against the W22 bed ===")
    emit(f"  bound: ΔE mean +{DELTA_E_STOP}, ssimMean −{SSIM_STOP}, on UNTINTED rows")
    emit(
        f"  {'profile':46s} {'scene':44s} {'tier':7s} {'ΔdE':>10s} {'Δssim':>10s} {'verdict':>8s}"
    )
    fired1 = []
    worst_de = 0.0
    worst_ssim = 0.0
    for ident, cell in sorted(after.items()):
        base = before.get(ident)
        if base is None:
            continue
        if "tint" in ident[1]:
            continue
        de_a, de_b = metric(cell, "perceptual", "oklabDeltaEMean"), metric(base, "perceptual", "oklabDeltaEMean")
        ss_a, ss_b = metric(cell, "perceptual", "ssimMean"), metric(base, "perceptual", "ssimMean")
        d_de = (de_a - de_b) if ok(de_a) and ok(de_b) else None
        d_ss = (ss_a - ss_b) if ok(ss_a) and ok(ss_b) else None
        bad = (d_de is not None and d_de > DELTA_E_STOP) or (d_ss is not None and d_ss < -SSIM_STOP)
        if d_de is not None:
            worst_de = max(worst_de, d_de)
        if d_ss is not None:
            worst_ssim = min(worst_ssim, d_ss)
        if bad:
            fired1.append((ident, d_de, d_ss))
            emit(
                f"  {ident[0]:46s} {ident[1]:44s} {TIERS[ident[2]]:7s} "
                f"{(d_de if d_de is not None else float('nan')):+10.5f} "
                f"{(d_ss if d_ss is not None else float('nan')):+10.5f} {'FIRES':>8s}"
            )
    emit(f"  worst ΔE mean rise {worst_de:+.5f} (bound +{DELTA_E_STOP}); worst ssimMean fall "
         f"{worst_ssim:+.5f} (bound −{SSIM_STOP}); rows firing: {len(fired1)}")

    for label, stop_key, selector in (
        ("S2 — the tinted cells' bodies", "S2", lambda scene, row: row.get("tint") is not None),
        ("S7 — the collapsed cells' bodies", "S7", lambda scene, row: scene in COLLAPSED),
    ):
        emit()
        emit(f"=== {label} (bound {BODY_STOP}) ===")
        emit(
            f"  {'profile':46s} {'scene':44s} {'tier':6s} {'before':>9s} {'after':>9s} "
            f"{'Δ':>9s} {'verdict':>8s}"
        )
        fired = []
        worst = 0.0
        for profile, _dpr, _scheme in PROFILES:
            for tier in ("webgpu", "css"):
                was = load_reads(args.reads, profile, tier, "before")
                now = load_reads(args.reads, profile, tier, "after")
                for scene in sorted(now):
                    row = now[scene]
                    old = was.get(scene)
                    if old is None or not selector(scene, row):
                        continue
                    a, b = row.get("bodyWeb"), old.get("bodyWeb")
                    if not ok(a) or not ok(b):
                        continue
                    d = a - b
                    worst = max(worst, abs(d))
                    verdict = "ok" if abs(d) <= BODY_STOP else "FIRES"
                    if verdict == "FIRES":
                        fired.append((profile, scene, tier, d))
                        emit(
                            f"  {profile:46s} {scene:44s} {tier:6s} {b:9.5f} {a:9.5f} "
                            f"{d:+9.5f} {verdict:>8s}"
                        )
        emit(f"  worst |Δ body|: {worst:.5f} against {BODY_STOP}; rows firing: {len(fired)}")

    if args.out:
        open(args.out, "w").write("\n".join(lines) + "\n")


main()
