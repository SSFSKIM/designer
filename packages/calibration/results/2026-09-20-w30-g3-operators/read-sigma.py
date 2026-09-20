#!/usr/bin/env python3
"""W30 G3 — what the instrument reads back off VITREA's own shadow, per span.

    python3 read-sigma.py [<matrix.json> ...] [--any-document] [--renderer webgpu]

The sigma law is written into a uniform in CSS px; `metrics/shadow.ts` fits a
blurred edge to what was drawn and returns `falloffSigmaPxWeb`. The two are only
the same number if the reader is unbiased on vitrea's own shadow, and nothing
had checked that: the shipped material draws ONE sigma at every span, so a
reading of `falloffSigmaWeb` per span at the shipped documents is a direct
measurement of the reader's own bias, span by span, with the law held constant.

That is why this file exists before the first candidate is built. It prints, per
bed per span, the native sigma, the web sigma and their ratio, and the same for
the falloff amplitude — the pair claims §5.156 §2 says trades along a valley in
the thin regime and is separately identified in the thick one.

The scene's casting span comes from `scenes.json` (the declared component's
shorter side), the same source W30 G0's cut uses, so the two tables are keyed
the same way.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent
SCENES = ROOT / "apps/reference-apple/scenes.json"
CAPTURE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")
TIER = {"texture": "webgpu", "dom": "css"}


def spans() -> dict[str, float]:
    spec = json.loads(SCENES.read_text())
    out: dict[str, float] = {}
    for name, component in spec["components"].items():
        size = component.get("size")
        if isinstance(size, list) and len(size) == 2:
            out[name] = float(min(size))
    return out


def bed_of(profile: str) -> str:
    return profile.replace("apple-macos-27.0-", "").replace("-glass0.5", "").replace(
        "-standard", "").replace("1x-", "1x ").replace("2x-", "2x ")


def at(block: dict, name: str) -> float | None:
    entry = (block or {}).get(name)
    return entry["value"] if isinstance(entry, dict) else None


def median(values: list[float]) -> float | None:
    return sorted(values)[len(values) // 2] if values else None


def main(argv: list[str]) -> int:
    honour = "--any-document" not in argv
    renderer = "webgpu"
    if "--renderer" in argv:
        renderer = argv[argv.index("--renderer") + 1]
    paths = [Path(a) for a in argv if not a.startswith("--") and a.endswith(".json")]
    if not paths:
        paths = [PACKAGE / "results/matrix.json"]
    hashes = {f"packages/calibration/profiles/{p.name}":
              hashlib.sha256(p.read_bytes()).hexdigest()[:12]
              for p in sorted((PACKAGE / "profiles").glob("*.json"))}
    component_span = spans()

    rows = []
    for path in paths:
        for cell in json.loads(path.read_text())["cells"]:
            profile = cell["key"]["profileKey"]
            if not profile.startswith("apple-macos-27.0-"):
                continue
            if TIER.get(cell["tier"], cell["tier"]) != renderer:
                continue
            if honour:
                clause = CAPTURE.search(cell["key"]["web"]["capturePath"])
                if clause is None or hashes.get(clause.group(1)) != clause.group(2):
                    continue
            scene = cell["key"]["sceneId"]
            parts = scene.split("__")
            if len(parts) < 2:
                continue
            span = component_span.get(parts[1])
            shadow = cell.get("shadow") or {}
            native = at(shadow, "falloffSigmaNative")
            web = at(shadow, "falloffSigmaWeb")
            rows.append({
                "profile": profile,
                "bed": bed_of(profile),
                "scene": scene,
                "set": cell.get("fixtureSet"),
                "state": cell.get("state"),
                "span": span,
                "scale": 2 if "-2x-" in profile else 1,
                "sigmaNative": None if native is None else native / (2 if "-2x-" in profile else 1),
                "sigmaWeb": None if web is None else web / (2 if "-2x-" in profile else 1),
                "amplitudeNative": at(shadow, "falloffAmplitudeNative"),
                "amplitudeWeb": at(shadow, "falloffAmplitudeWeb"),
                "departureNative": at(shadow, "meanDepartureNative"),
                "departureWeb": at(shadow, "meanDepartureWeb"),
            })

    print(f"W30 G3 — the reader's own sigma on vitrea's shadow, {renderer} tier")
    print("=" * 108)
    print(f"  {len(rows)} macOS 27 rows on this tier; "
          "active, non-holdout, sigma_css <= span, both sides resolved")
    print()
    keep = [r for r in rows
            if r["set"] != "holdout" and r["state"] != "inactive"
            and r["sigmaNative"] is not None and r["sigmaWeb"] is not None
            and r["span"] is not None and r["sigmaNative"] <= r["span"]
            and r["sigmaWeb"] <= r["span"]]
    beds = sorted({r["bed"] for r in keep})
    span_list = sorted({r["span"] for r in keep})
    print(f"  {'bed':<34}{'span':>6}{'n':>4}{'sigma N':>10}{'sigma W':>10}{'W/N':>8}"
          f"{'amp N':>9}{'amp W':>9}{'W/N':>8}")
    for bed in beds:
        for span in span_list:
            sel = [r for r in keep if r["bed"] == bed and r["span"] == span]
            if not sel:
                continue
            native = median([r["sigmaNative"] for r in sel])
            web = median([r["sigmaWeb"] for r in sel])
            an = median([r["amplitudeNative"] for r in sel if r["amplitudeNative"] is not None])
            aw = median([r["amplitudeWeb"] for r in sel if r["amplitudeWeb"] is not None])
            print(f"  {bed:<34}{span:>6.0f}{len(sel):>4}{native:>10.4f}{web:>10.4f}"
                  f"{web / native:>8.3f}"
                  + (f"{an:>9.4f}{aw:>9.4f}{aw / an:>8.3f}" if an and aw else f"{'—':>26}"))
    print()
    pooled = [r for r in keep]
    if pooled:
        print("  pooled over every bed, per span — the reader's bias on ONE drawn sigma")
        for span in span_list:
            sel = [r for r in pooled if r["span"] == span]
            if not sel:
                continue
            web = median([r["sigmaWeb"] for r in sel])
            print(f"    span {span:>5.0f}   n {len(sel):>3}   median sigma_web {web:>8.4f}")
    print()
    # The table is the evidence; `--json` writes the per-row readings beside it
    # for a reader that wants them and is not committed.
    if "--json" in argv:
        (HERE / "read-sigma.json").write_text(json.dumps(
            {"source": [str(p) for p in paths], "renderer": renderer, "rows": rows}, indent=1)
            + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
