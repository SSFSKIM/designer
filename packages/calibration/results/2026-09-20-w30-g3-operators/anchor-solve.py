#!/usr/bin/env python3
"""W30 G3 — the six anchors and the lift, solved from one round's departure.

    VITREA_G3_SCRATCH=/tmp/w30g3 python3 anchor-solve.py <label> [<label> ...] \
        [--constants round-A.json]

The objective is the shadow axis's `meanDeparture` — the mean of
`backdrop - rendered` over the whole exterior of the declared region, in linear
light — which is the quantity W29 G3b fitted the anchors against and the
quantity B3's stop is read on. The amplitude is reported beside it and is not
what is minimised: it is one parameter of a two-parameter fit to ring means and
it collapses in the thin regime (claims §5.156 §2), while the departure is an
exact integral over a fixed population and is defined on every cell.

**Why one round is enough to solve, and what the second round is for.** At a
fixed geometry the departure is very nearly linear in the composited alpha, so a
round at a known anchor gives the geometry factor per regime and the anchor the
native departure wants follows in closed form:

    anchor_wanted = anchor_rendered * (departure_native / departure_web)

The round after it is a check on the linearity rather than a second search, and
where the check disagrees the pair of rounds is a secant and the disagreement is
what it is read through.

**Which cells identify which anchor.** The occlusion law blends a thin regime
keyed on the BACKDROP's luminance with a thick regime keyed on the casting SPAN,
through the smoothstep of `sizeThickness` — so at span 44 the composite is 97.6 %
thin and at span 96 and above it is entirely thick (`outerShadowOcclusionAt`).
The grouping below is that law's own: the thin regimes are read on spans at and
below 44 and split by backdrop class, the thick anchors on their own spans. A
cell over `dark-solid` or `impulse` is in the dark regime, where the anchor is
0 and the reference removes at most one or two of 255 codes — it is reported and
never solved, because a ratio of two numbers that are both zero is not one.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent
SCENES = ROOT / "apps/reference-apple/scenes.json"
SCRATCH = Path(os.environ.get("VITREA_G3_SCRATCH", "/tmp/g3scratch"))

sys.path.insert(0, str(HERE.parent / "2026-09-19-w29-g3-refit"))
from fit import cells as fit_cells  # noqa: E402

# The backdrop classes the thin regime keys on, by the encoded means
# `fit.py`'s own table records and the thresholds `OUTER_SHADOW_THIN_L` uses.
DARK_BACKDROPS = {"impulse", "dark-solid"}
BRIGHT_BACKDROPS = {"light-solid"}


def spans() -> dict[str, float]:
    spec = json.loads(SCENES.read_text())
    return {name: float(min(c["size"])) for name, c in spec["components"].items()
            if isinstance(c.get("size"), list) and len(c["size"]) == 2}


def at(block: dict, name: str) -> float | None:
    entry = (block or {}).get(name)
    return entry["value"] if isinstance(entry, dict) else None


def regime(span: float | None, backdrop: str) -> str | None:
    if span is None:
        return None
    if span <= 44:
        if backdrop in DARK_BACKDROPS:
            return "thinDark"
        if backdrop in BRIGHT_BACKDROPS:
            return "thinBright"
        return "thinMid"
    if span <= 96:
        return "thick96"
    if span <= 128:
        return "thick128"
    if span < 160:
        return "span130"
    return "thick160"


ANCHOR = {
    "thinDark": "thinOcclusionDark",
    "thinMid": "thinOcclusionMid",
    "thinBright": "thinOcclusionBright",
    "thick96": "thickOcclusionAt96",
    "thick128": "thickOcclusionAt128",
    "thick160": "thickOcclusionAt160",
}
ORDER = ["thinDark", "thinMid", "thinBright", "thick96", "thick128", "span130", "thick160"]


def scheme_of(profile: str) -> str:
    return "dark" if "-dark-" in profile else "light"


def bed_of(profile: str) -> str:
    return profile.replace("apple-macos-27.0-", "").replace("-glass0.5", "")


def main(argv: list[str]) -> int:
    constants = None
    if "--constants" in argv:
        constants = json.loads(Path(argv[argv.index("--constants") + 1]).read_text())
    labels = [a for a in argv if not a.startswith("--")
              and not a.endswith(".json")]
    component_span = spans()

    rows: list[dict] = []
    for label in labels:
        run = SCRATCH / "fit-log" / label
        for matrix in sorted(run.glob("*.json")):
            for cell in fit_cells(matrix):
                shadow = cell.get("shadow")
                if shadow is None:
                    continue
                scene = cell["key"]["sceneId"]
                parts = scene.split("__")
                span = component_span.get(parts[1]) if len(parts) > 1 else None
                native, web = at(shadow, "meanDepartureNative"), at(shadow, "meanDepartureWeb")
                if native is None or web is None:
                    continue
                rows.append({
                    "label": label,
                    "profile": cell["key"]["profileKey"],
                    "bed": bed_of(cell["key"]["profileKey"]),
                    "scheme": scheme_of(cell["key"]["profileKey"]),
                    "scene": scene,
                    "set": cell.get("fixtureSet"),
                    "state": cell.get("state") or "rest",
                    "backdrop": parts[0],
                    "span": span,
                    "regime": regime(span, parts[0]),
                    "departureNative": native,
                    "departureWeb": web,
                    "sigmaNative": at(shadow, "falloffSigmaNative"),
                    "sigmaWeb": at(shadow, "falloffSigmaWeb"),
                    "offsetNative": at(shadow, "offsetYNative"),
                    "offsetWeb": at(shadow, "offsetYWeb"),
                    "amplitudeNative": at(shadow, "falloffAmplitudeNative"),
                    "amplitudeWeb": at(shadow, "falloffAmplitudeWeb"),
                })

    print("W30 G3 — the anchors solved from the departure, "
          f"labels {', '.join(labels)}")
    print("=" * 112)
    print(f"  {len(rows)} rows carry the shadow axis (holdout dropped in fit.py's cells())")
    print()

    # The two standard schemes are what the anchors live in; the accessibility
    # profiles' six anchors are overwritten by the reduced-transparency fold, so
    # they are reported and never solved here.
    FOLDED = ("reduced-transparency", "increased-contrast")
    for scheme in ("light", "dark"):
        print(f"{scheme} document — active cells, the beds it is fitted on")
        print("-" * 112)
        print(f"  {'regime':<12}{'n':>4}{'dep N':>11}{'dep W':>11}{'N/W':>9}"
              f"{'anchor now':>12}{'anchor wanted':>15}{'amp N':>9}{'amp W':>9}")
        for name in ORDER:
            sel = [r for r in rows
                   if r["scheme"] == scheme and r["regime"] == name and r["state"] != "inactive"
                   and not any(f in r["profile"] for f in FOLDED)]
            if not sel:
                continue
            native = sum(r["departureNative"] for r in sel) / len(sel)
            web = sum(r["departureWeb"] for r in sel) / len(sel)
            leaf = ANCHOR.get(name)
            now = (constants or {}).get(scheme, {}).get(leaf) if leaf else None
            wanted = (now * native / web) if (now is not None and web) else None
            amps_n = [r["amplitudeNative"] for r in sel if r["amplitudeNative"] is not None]
            amps_w = [r["amplitudeWeb"] for r in sel if r["amplitudeWeb"] is not None]
            print(f"  {name:<12}{len(sel):>4}{native:>11.5f}{web:>11.5f}"
                  f"{(native / web if web else float('nan')):>9.3f}"
                  f"{('—' if now is None else f'{now:.4f}'):>12}"
                  f"{('—' if wanted is None else f'{wanted:.4f}'):>15}"
                  f"{(sum(amps_n) / len(amps_n) if amps_n else float('nan')):>9.4f}"
                  f"{(sum(amps_w) / len(amps_w) if amps_w else float('nan')):>9.4f}")
        print()

        print(f"  the same per bed, so a 1x/2x split in one regime is visible")
        print(f"  {'bed':<30}{'regime':<12}{'n':>4}{'dep N':>11}{'dep W':>11}{'N/W':>9}")
        for bed in sorted({r["bed"] for r in rows if r["scheme"] == scheme
                           and not any(f in r["profile"] for f in FOLDED)}):
            for name in ORDER:
                sel = [r for r in rows if r["bed"] == bed and r["regime"] == name
                       and r["state"] != "inactive"]
                if not sel:
                    continue
                native = sum(r["departureNative"] for r in sel) / len(sel)
                web = sum(r["departureWeb"] for r in sel) / len(sel)
                print(f"  {bed:<30}{name:<12}{len(sel):>4}{native:>11.5f}{web:>11.5f}"
                      f"{(native / web if web else float('nan')):>9.3f}")
        print()

    print("The reduced-transparency fold — six anchors overwritten by "
          "`reducedTransparencyOcclusion`, outside this fit (X3)")
    print("-" * 112)
    print(f"  {'bed':<46}{'regime':<12}{'n':>4}{'dep N':>11}{'dep W':>11}{'N/W':>9}")
    for bed in sorted({r["bed"] for r in rows if any(f in r["profile"] for f in FOLDED)}):
        for name in ORDER:
            sel = [r for r in rows if r["bed"] == bed and r["regime"] == name
                   and r["state"] != "inactive"]
            if not sel:
                continue
            native = sum(r["departureNative"] for r in sel) / len(sel)
            web = sum(r["departureWeb"] for r in sel) / len(sel)
            print(f"  {bed:<46}{name:<12}{len(sel):>4}{native:>11.5f}{web:>11.5f}"
                  f"{(native / web if web else float('nan')):>9.3f}")
    print()

    print("Inactive cells — the receded documents, which inherit the block leaf for leaf")
    print("-" * 112)
    print(f"  {'scheme':<10}{'regime':<12}{'n':>4}{'dep N':>11}{'dep W':>11}{'N/W':>9}")
    for scheme in ("light", "dark"):
        for name in ORDER:
            sel = [r for r in rows if r["scheme"] == scheme and r["regime"] == name
                   and r["state"] == "inactive"]
            if not sel:
                continue
            native = sum(r["departureNative"] for r in sel) / len(sel)
            web = sum(r["departureWeb"] for r in sel) / len(sel)
            print(f"  {scheme:<10}{name:<12}{len(sel):>4}{native:>11.5f}{web:>11.5f}"
                  f"{(native / web if web else float('nan')):>9.3f}")
    print()

    everything = [abs(r["departureWeb"] - r["departureNative"]) for r in rows]
    print(f"  mean |Δ departure| over all {len(rows)} rows of this round: "
          f"{sum(everything) / len(everything):.5f}")
    print()

    print("The sigma the instrument reads back, per bed per span — the law is a "
          "closed form and this is not it")
    print("-" * 112)
    print("  The OFFSET is beside it deliberately. `offsetPx` is one constant on macOS 27's")
    print("  documents (7.95) and the native offset is span-graded like the sigma was — so at a")
    print("  thin caster vitrea's exterior is dominated by a silhouette displaced twice as far")
    print("  as Apple's, and a blurred-edge model fits a wide sigma to that band whatever sigma")
    print("  was drawn. The read W/N at spans 32 and 44 is that, not the blur.")
    print()
    print(f"  {'bed':<30}{'span':>6}{'n':>4}{'sigma N':>10}{'sigma W':>10}{'W/N':>8}"
          f"{'offset N':>11}{'offset W':>11}")
    for bed in sorted({r["bed"] for r in rows}):
        for span in sorted({r["span"] for r in rows if r["span"] is not None}):
            sel = [r for r in rows if r["bed"] == bed and r["span"] == span
                   and r["state"] != "inactive"
                   and r["sigmaNative"] is not None and r["sigmaWeb"] is not None]
            # The bed name has the `apple-macos-27.0-` prefix stripped, so the
            # scale is its first token rather than an infix.
            scale = 2 if bed.startswith("2x") else 1
            sel = [r for r in sel if r["sigmaNative"] / scale <= span
                   and r["sigmaWeb"] / scale <= span]
            if not sel:
                continue
            native = sorted(r["sigmaNative"] / scale for r in sel)[len(sel) // 2]
            web = sorted(r["sigmaWeb"] / scale for r in sel)[len(sel) // 2]
            offsets = [(r["offsetNative"], r["offsetWeb"]) for r in sel
                       if r.get("offsetNative") is not None and r.get("offsetWeb") is not None]
            offset_n = (sorted(o[0] for o in offsets)[len(offsets) // 2] / scale
                        if offsets else float("nan"))
            offset_w = (sorted(o[1] for o in offsets)[len(offsets) // 2] / scale
                        if offsets else float("nan"))
            print(f"  {bed:<30}{span:>6.0f}{len(sel):>4}{native:>10.4f}{web:>10.4f}"
                  f"{web / native:>8.3f}{offset_n:>11.2f}{offset_w:>11.2f}")
    print()

    # No JSON beside the table. These rows are a fit round's scratch matrices
    # read once; the committed evidence is this table, and a second copy of half
    # a megabyte of intermediate readings is weight rather than evidence.
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    raise SystemExit(main(sys.argv[1:]))
