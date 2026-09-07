"""W21 G1 — the parent's clauses 3 and 4, and stop S3, on the canonical dark bed.

Read from `read-canonical.sh`'s output, which is the declared-geometry instrument (contract X2)
applied to the canonical bed's native fixtures against vitrea before and after. The clauses:

  * **3 — the body.** On every untinted dark texture-tier cell at both scales, the body under the
    declared box eroded 6 CSS px within **0.010** of the reference's, with the collapsed cells held
    within 0.002 of where they are (that last is stop S3). Reported THIN and THICK apart, because
    W21 Decision Log 2 (e) rules that the thick rows meet it by construction and the thin rows carry
    the deferred appearance term; the parent rules on the thin remainder.
  * **4 — the rim.** On every untinted dark cell over a SOLID backdrop, each side's rim-band peak
    within **0.03** of the reference's, and the reference's flatness (max side minus min side)
    reproduced within 0.03.

Thickness here is the size law's, not a guess: `sizeThickness` saturates at span 96, so `rrect-md`
(96), `rrect-lg` (160) and `glass-over-glass` are thick and `capsule-button` (44) is thin. The
`recorded` pressed cell and the composite `glass-over-glass` are reported where the reader can read
them and named where it cannot.

    g1-clauses.py <canonical-reads dir>
"""

import json
import os
import sys

SOLID_BACKGROUNDS = ("dark-solid", "mid-dark-solid", "light-solid", "impulse")
THIN_COMPONENTS = ("capsule-button",)
BODY_CLAUSE = 0.010
COLLAPSE_STOP = 0.002
RIM_CLAUSE = 0.03
SIDES = ("top", "bottom", "left", "right")


def load(directory, profile, tier, when):
    path = os.path.join(directory, f"{profile}-{tier}-{when}.json")
    return {row["scene"]: row for row in json.load(open(path))["rows"]}


def main():
    directory = sys.argv[1]
    profiles = ("apple-macos-26.5-1x-dark-standard", "apple-macos-26.5-2x-dark-standard")

    for tier in ("webgpu", "css"):
        print(f"\n=== clause 3 — the body under the declared geometry, {tier} tier ===")
        print(f"  {'cell':46s} {'dpr':3s} {'set':11s} {'thick':6s} {'native':>8s} {'before':>8s} "
              f"{'after':>8s} {'|Δ| after':>10s} {'clause 3':>9s}")
        summary = {}
        for profile in profiles:
            dpr = "1x" if "1x" in profile else "2x"
            before = load(directory, profile, tier, "before")
            after = load(directory, profile, tier, "after")
            for scene in sorted(after):
                row, was = after[scene], before.get(scene)
                if row.get("tint") is not None or "bodyWeb" not in row:
                    continue
                thick = row["component"] not in THIN_COMPONENTS
                error = abs(row["bodyWeb"] - row["bodyNative"])
                verdict = "met" if error <= BODY_CLAUSE else "MISSED"
                summary.setdefault((dpr, thick), []).append(error)
                print(f"  {scene:46s} {dpr:3s} {row['set']:11s} {str(thick):6s} "
                      f"{row['bodyNative']:8.4f} "
                      f"{(was['bodyWeb'] if was and 'bodyWeb' in was else float('nan')):8.4f} "
                      f"{row['bodyWeb']:8.4f} {error:10.4f} {verdict:>9s}")
        print(f"  {'mean |Δbody| by scale and thickness':50s}")
        for (dpr, thick), errors in sorted(summary.items()):
            print(f"    {dpr}  {'thick' if thick else 'thin ':5s}  n={len(errors):2d}  "
                  f"mean {sum(errors) / len(errors):.4f}  worst {max(errors):.4f}")

        print(f"\n=== stop S3 — the collapsed capsules, moved by more than {COLLAPSE_STOP} in body, "
              f"{tier} tier ===")
        for profile in profiles:
            dpr = "1x" if "1x" in profile else "2x"
            before = load(directory, profile, tier, "before")
            after = load(directory, profile, tier, "after")
            for scene in sorted(after):
                background = scene.split("__")[0]
                if background not in ("dark-solid", "impulse") or "tint" in scene:
                    continue
                if after[scene]["component"] not in THIN_COMPONENTS:
                    continue
                row, was = after[scene], before.get(scene)
                if was is None or "bodyWeb" not in row or "bodyWeb" not in was:
                    continue
                moved = row["bodyWeb"] - was["bodyWeb"]
                print(f"  {'FIRES' if abs(moved) > COLLAPSE_STOP else '     '} {scene:46s} {dpr:3s} "
                      f"native {row['bodyNative']:7.4f}  before {was['bodyWeb']:7.4f} → after "
                      f"{row['bodyWeb']:7.4f} ({moved:+.4f})")

        print(f"\n=== clause 4 — the rim per side over a solid backdrop, {tier} tier ===")
        print(f"  {'cell':46s} {'dpr':3s} {'side':7s} {'native':>8s} {'before':>8s} {'after':>8s} "
              f"{'Δ after':>9s} {'clause 4':>9s}")
        for profile in profiles:
            dpr = "1x" if "1x" in profile else "2x"
            before = load(directory, profile, tier, "before")
            after = load(directory, profile, tier, "after")
            for scene in sorted(after):
                if scene.split("__")[0] not in SOLID_BACKGROUNDS or "tint" in scene:
                    continue
                row, was = after[scene], before.get(scene)
                if "rimWeb" not in row:
                    continue
                for index, side in enumerate(SIDES):
                    native = row["rimNative"][index]
                    now = row["rimWeb"][index]
                    then = was["rimWeb"][index] if was and "rimWeb" in was else float("nan")
                    delta = now - native
                    print(f"  {scene:46s} {dpr:3s} {side:7s} {native:8.4f} {then:8.4f} {now:8.4f} "
                          f"{delta:+9.4f} {'met' if abs(delta) <= RIM_CLAUSE else 'MISSED':>9s}")
                flat_native = max(row["rimNative"]) - min(row["rimNative"])
                flat_web = max(row["rimWeb"]) - min(row["rimWeb"])
                print(f"  {scene:46s} {dpr:3s} {'FLAT':7s} {flat_native:8.4f} "
                      f"{'':8s} {flat_web:8.4f} {flat_web - flat_native:+9.4f} "
                      f"{'met' if abs(flat_web - flat_native) <= RIM_CLAUSE else 'MISSED':>9s}")


if __name__ == "__main__":
    main()
