"""W43 G2 (b): the native delta's law tables, read off the rows (descriptive; the verdicts are verdicts.py's).

Reads ``slider-delta.json`` and ``slider-recede-delta.json`` beside itself. Every change is
subject − reference = Apple at 0.25 − Apple at 0.5. Levels are given twice: in linear luminance, and
as the encoded sRGB code difference of the two levels (255 · (enc(L₀.₂₅) − enc(L₀.₅))), which is the
unit the eye sheets and W39's bars are in. Every rrect-lg cell is its own stratum (memo F's capture
scale step), printed apart.

    python3.12 -B law-tables.py   # writes law-tables.txt beside itself
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
STRUCTURED = re.compile(r"^(checkerboard|hc-text|photo|impulse)")
SPAN = {  # the declared short side, CSS px (scenes.json components)
    "capsule-button": 44, "rrect-sm": 32, "rrect-48": 48, "rrect-64": 64, "rrect-80": 80, "rrect-md": 96,
    "rrect-md-clear20": 96, "rrect-ml": 128, "rrect-lg": 160, "toolbar-group": 44, "glass-over-glass": 0,
}


def enc(linear: float) -> float:
    linear = min(max(linear, 0.0), 1.0)
    return 12.92 * linear if linear <= 0.0031308 else 1.055 * linear ** (1 / 2.4) - 0.055


def codes(pair) -> float | None:
    if not pair or None in pair:
        return None
    return 255.0 * (enc(pair[1]) - enc(pair[0]))


def q(values, p):
    if not values:
        return math.nan
    s = sorted(values)
    return s[min(len(s) - 1, int(p * len(s)))]


def med(values):
    return q(values, 0.5)


def scheme(row):
    return "light" if "-light-" in row["profileKey"] else "dark"


def scale(row):
    return "2x" if "-2x-" in row["profileKey"] else "1x"


def stat_line(label, values, width=34):
    if not values:
        return f"  {label:<{width}} —"
    up = sum(v > 0 for v in values)
    down = sum(v < 0 for v in values)
    return (f"  {label:<{width}} n {len(values):>3}  p10 {q(values, 0.1):+8.3f}  median {med(values):+8.3f}  "
            f"p90 {q(values, 0.9):+8.3f}  up/down {up}/{down}")


def main() -> None:
    rows = json.loads((HERE / "slider-delta.json").read_text())["rows"]
    recede = json.loads((HERE / "slider-recede-delta.json").read_text())["rows"]
    held = [r for r in rows if r["component"] != "rrect-lg"]
    lg = [r for r in rows if r["component"] == "rrect-lg"]
    out: list[str] = []
    say = out.append
    say("# The native delta, 0.25 against 0.5, read off the rows (W43 G2 (b); claims §5.200)")
    say("")
    say(f"{len(rows)} pair rows ({len(lg)} rrect-lg, held apart), {len(recede)} recede rows.")
    say("Every change is Apple at 0.25 minus Apple at 0.5. 'codes' is the encoded sRGB difference of the")
    say("two levels; 'lin' is linear luminance.")
    say("")

    # 1. the body level by backdrop, per scheme and pose
    say("## 1. The body level (bodyLevel, the declared box eroded 6 CSS px), codes, by backdrop")
    for sch in ("light", "dark"):
        for pose in ("active", "inactive"):
            subset = [r for r in held if scheme(r) == sch and r["pose"] == pose]
            say(f"### {sch}, {pose} ({len(subset)} cells, rrect-lg apart)")
            by = defaultdict(list)
            means = {}
            for r in subset:
                c = codes(r["readings"].get("bodyLevel"))
                if c is not None:
                    by[r["background"]].append(c)
                    means[r["background"]] = r["backdropEncodedMean"]
            for background, values in sorted(by.items(), key=lambda kv: means[kv[0]]):
                say(stat_line(f"{background} (enc mean {means[background]:.3f})", values))
            allv = [c for v in by.values() for c in v]
            say(stat_line("ALL", allv))
            lgv = [codes(r["readings"].get("bodyLevel")) for r in lg if scheme(r) == sch and r["pose"] == pose]
            say(stat_line("rrect-lg stratum", [v for v in lgv if v is not None]))
            say("")

    # 2. the body level by span, per scheme and pose (memo F: the dark cap moves at s >= 80)
    say("## 2. The body level by component span, codes (memo F: the dark MaxLuma cap moves at s >= 80)")
    for sch in ("light", "dark"):
        for pose in ("active", "inactive"):
            say(f"### {sch}, {pose}")
            by = defaultdict(list)
            for r in rows:
                if scheme(r) != sch or r["pose"] != pose:
                    continue
                c = codes(r["readings"].get("bodyLevel"))
                if c is not None:
                    by[(SPAN.get(r["component"], -1), r["component"])].append(c)
            for (span, component), values in sorted(by.items()):
                say(stat_line(f"{component} (s {span})", values))
            say("")

    # 3. tone response: the affine transfer within the cell
    say("## 3. Tone response by backdrop: the affine transfer of rendered against backdrop luminance")
    for sch in ("light", "dark"):
        for pose in ("active", "inactive"):
            say(f"### {sch}, {pose}")
            by = defaultdict(list)
            for r in held:
                if scheme(r) != sch or r["pose"] != pose:
                    continue
                s_ = r["readings"].get("transferSlope")
                o_ = r["readings"].get("transferOffset")
                if s_ and o_:
                    by[r["background"]].append((s_[0], s_[1], o_[1] - o_[0]))
            for background, items in sorted(by.items()):
                say(f"  {background:<20} n {len(items):>3}  slope {med([a for a, _, _ in items]):.3f} -> "
                    f"{med([b for _, b, _ in items]):.3f}  median offset change {med([c for _, _, c in items]):+.4f} lin")
            say("")

    # 4. scatter
    say("## 4. Scatter: the interior's spatial spread (interiorStdDev, lin), structured against solid")
    for sch in ("light", "dark"):
        for pose in ("active", "inactive"):
            say(f"### {sch}, {pose}")
            by = defaultdict(list)
            for r in held:
                if scheme(r) != sch or r["pose"] != pose:
                    continue
                pair = r["readings"].get("interiorStdDev")
                if pair:
                    by[r["background"]].append((pair[0], pair[1]))
            for background, items in sorted(by.items()):
                kind = "structured" if STRUCTURED.match(background) else "solid"
                ratio = [b / a for a, b in items if a > 1e-6]
                say(f"  {background:<20} {kind:<10} n {len(items):>3}  stdDev {med([a for a, _ in items]):.4f} -> "
                    f"{med([b for _, b in items]):.4f}  median ratio {med(ratio):.3f}")
            say("")

    # 5. chroma of the body, untinted cells
    say("## 5. The body's chroma (tintChroma, OKLab chroma of the interior), untinted cells")
    for sch in ("light", "dark"):
        for pose in ("active", "inactive"):
            say(f"### {sch}, {pose}")
            by = defaultdict(list)
            for r in held:
                if scheme(r) != sch or r["pose"] != pose or "-tint-" in r["sceneId"]:
                    continue
                pair = r["readings"].get("tintChroma")
                if pair:
                    by[r["background"]].append((pair[0], pair[1]))
            for background, items in sorted(by.items()):
                ratio = [b / a for a, b in items if a > 0.005]
                say(f"  {background:<20} n {len(items):>3}  chroma {med([a for a, _ in items]):.4f} -> "
                    f"{med([b for _, b in items]):.4f}  median ratio (where >= 0.005) {med(ratio):.3f}")
            say("")

    # 6. rim and highlight, uniform backdrops: the edge's own change
    say("## 6. Rim and highlight on uniform backdrops (both readers subtract the body), lin")
    for sch in ("light", "dark"):
        for pose in ("active", "inactive"):
            subset = [r for r in held if scheme(r) == sch and r["pose"] == pose and not STRUCTURED.match(r["background"])]
            rim = [r["readings"]["rimContourMeanSide"] for r in subset if r["readings"].get("rimContourMeanSide")]
            peak, floor = [], []
            for r in subset:
                bins = r["readings"].get("highlightBins")
                if not bins:
                    continue
                a = [v for v in bins[0] if v is not None]
                b = [v for v in bins[1] if v is not None]
                if a and b:
                    peak.append((max(a), max(b)))
                    floor.append((min(a), min(b)))
            say(f"### {sch}, {pose} ({len(subset)} uniform-backdrop cells)")
            if rim:
                say(f"  rim excess per side (W23)      {med([p[0] for p in rim]):+.4f} -> {med([p[1] for p in rim]):+.4f}"
                    f"   median change {med([p[1] - p[0] for p in rim]):+.4f}")
            if peak:
                say(f"  highlight brightest bin (W24)  {med([p[0] for p in peak]):+.4f} -> {med([p[1] for p in peak]):+.4f}"
                    f"   median change {med([p[1] - p[0] for p in peak]):+.4f}")
                say(f"  highlight dimmest bin          {med([p[0] for p in floor]):+.4f} -> {med([p[1] for p in floor]):+.4f}"
                    f"   median change {med([p[1] - p[0] for p in floor]):+.4f}")
            say("")

    # 7. the exterior: where the two captures differ outside the declared contour
    say("## 7. The exterior: cells whose bands are byte-identical, and the largest code difference")
    for name, subset_all in (("held-in", held), ("rrect-lg", lg)):
        for sch in ("light", "dark"):
            for pose in ("active", "inactive"):
                subset = [r for r in subset_all if scheme(r) == sch and r["pose"] == pose]
                if not subset:
                    continue
                parts = []
                for band in ("near-exterior", "exterior", "far"):
                    items = [b for r in subset for b in r["radial"] if b["band"] == band]
                    identical = sum(1 for b in items if b["differing"] == 0)
                    worst = max((b["maxAbsCode"] for b in items), default=0)
                    mean_lum = med([b["meanSignedLuminance"] for b in items])
                    parts.append(f"{band} {identical}/{len(items)} identical, max {worst:.0f}, med signed {mean_lum:+.5f}")
                say(f"  {name:<8} {sch:<5} {pose:<8}  " + "; ".join(parts))
    say("")
    say("Shadow readings (shadowField), held-in cells, reference -> subject medians:")
    for sch in ("light", "dark"):
        for pose in ("active", "inactive"):
            subset = [r for r in held if scheme(r) == sch and r["pose"] == pose]
            md = [r["readings"]["shadowMeanDeparture"] for r in subset if r["readings"].get("shadowMeanDeparture")]
            sp = [r["readings"]["shadowStrengthPeak"] for r in subset if r["readings"].get("shadowStrengthPeak")]
            sg = [r["readings"]["shadowFalloffSigmaPx"] for r in subset if r["readings"].get("shadowFalloffSigmaPx")]
            line = f"  {sch:<5} {pose:<8}"
            if md:
                line += f"  mean departure {med([a for a, _ in md]):+.5f} -> {med([b for _, b in md]):+.5f} (n {len(md)})"
            if sp:
                line += f"  strength peak {med([a for a, _ in sp]):.4f} -> {med([b for _, b in sp]):.4f} (n {len(sp)})"
            if sg:
                line += f"  falloff sigma {med([a for a, _ in sg]):.2f} -> {med([b for _, b in sg]):.2f} px (n {len(sg)})"
            say(line)
    say("")

    # 8. tint shade
    say("## 8. Tint shade, tinted cells: the tint's lightness (tintDeltaL) and chroma, by tint")
    for sch in ("light", "dark"):
        for pose in ("active", "inactive"):
            by = defaultdict(list)
            for r in held:
                if scheme(r) != sch or r["pose"] != pose or "-tint-" not in r["sceneId"]:
                    continue
                tint = r["sceneId"].split("-tint-")[1]
                dl = r["readings"].get("tintDeltaL")
                ch = r["readings"].get("tintChroma")
                if dl and ch:
                    by[tint].append((dl[0], dl[1], ch[0], ch[1]))
            for tint, items in sorted(by.items()):
                say(f"  {sch:<5} {pose:<8} {tint:<7} n {len(items):>2}  dL {med([a for a, *_ in items]):+.4f} -> "
                    f"{med([b for _, b, *_ in items]):+.4f}  chroma {med([c for *_, c, _ in items]):.4f} -> "
                    f"{med([d for *_, d in items]):.4f}")
    say("")

    # 9. the recede
    say("## 9. The recede: (inactive − active) at each position, and their difference")
    for sch in ("light", "dark"):
        for sc in ("1x", "2x"):
            subset = [r for r in recede if (("-light-" in r["profileKey"]) == (sch == "light")) and f"-{sc}-" in r["profileKey"]
                      and r["activeSceneId"].split("__")[1] != "rrect-lg"]
            for name in ("bodyLevel", "rimContourMean", "highlightPeak", "interiorStdDev", "tintChroma"):
                items = [(r["recedeReference"][name], r["recedeSubject"][name], r["deltaOfRecede"][name])
                         for r in subset if name in r["deltaOfRecede"]]
                if not items:
                    continue
                say(f"  {sch:<5} {sc}  {name:<16} n {len(items):>3}  recede at 0.5 {med([a for a, _, _ in items]):+.4f}"
                    f"  at 0.25 {med([b for _, b, _ in items]):+.4f}  median difference {med([c for _, _, c in items]):+.4f}")
    say("")
    (HERE / "law-tables.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
