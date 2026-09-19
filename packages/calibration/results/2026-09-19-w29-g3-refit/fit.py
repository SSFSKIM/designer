#!/usr/bin/env python3
"""W29 G3 — the refit's measuring loop: one candidate document, one render, one table.

Not a sweep. `scripts/sweep.ts` turns SCALAR axes through a grid, and the laws
this child refits are mostly rows of a curve — `backdropToneResponseThin` and
`…Thick` are three or four ordinates each, and a grid over them is a product no
machine time buys. So the loop here is the one the evidence supports instead:
render a candidate, read the residual the law is stated in (the body's own
level, the rim's peak and width, the interior's spread), move the candidate by
that residual, render again. Every step is a measurement and the whole path is
in `fit-log/`.

    python3 fit.py render <label> <profile> <renderer> <document> [--set S] [--scene a,b]
    python3 fit.py table  <label> [--metric interiorMean]
    python3 fit.py doc    <out.json> <base.json> <overrides.json>

`render` refuses the same three things `read.sh` does — another capture process,
an accessibility toggle that is not 0, a slider that is not the bed's 0.5 — and
writes into `$VITREA_G3_SCRATCH`, never beside the canonical matrix.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
SCRATCH = Path(os.environ.get("VITREA_G3_SCRATCH", "/tmp/g3scratch"))

BACKDROP_ENCODED_MEAN = {
    # The bed's own backdrops at their encoded mean, as claims §5.151 §5 prints
    # them. They are a property of the rasters, and G1 Part B proved the rasters
    # are byte-identical across the two operating systems — 896 comparisons, zero
    # disagreements — so this table is as true of the 27 bed as of the 26.5 one.
    "impulse": 0.004,
    "dark-solid": 0.110,
    "mid-chroma-solid": 0.255,
    "mid-dark-solid": 0.271,
    "photo": 0.425,
    "checkerboard-64": 0.472,
    "checkerboard": 0.500,
    "checkerboard-32": 0.500,
    "checkerboard-4": 0.500,
    "checkerboard-8": 0.500,
    "checkerboard-lc16": 0.700,
    "hc-text": 0.740,
    "hc-text-7": 0.750,
    "hc-text-28": 0.765,
    "light-solid": 0.950,
}


def machine_ready() -> None:
    out = subprocess.run(
        ["pgrep", "-f", "compare.ts|sweep.ts|capture-web|VitreaReference|playwright"],
        capture_output=True,
    )
    if out.returncode == 0:
        raise SystemExit("fit: another capture process is running (X7)")
    reads = {}
    for name, domain, key in (
        ("reduceTransparency", "com.apple.universalaccess", "reduceTransparency"),
        ("increaseContrast", "com.apple.universalaccess", "increaseContrast"),
        ("NSGlassTintAmount", "-g", "NSGlassTintAmount"),
    ):
        argv = ["defaults", "read", domain, key]
        got = subprocess.run(argv, capture_output=True, text=True)
        reads[name] = got.stdout.strip() if got.returncode == 0 else "absent"
    print(f"machine: {reads}", file=sys.stderr)
    if reads["reduceTransparency"] != "0" or reads["increaseContrast"] != "0":
        raise SystemExit(f"fit: accessibility toggles must read 0, got {reads}")
    if reads["NSGlassTintAmount"] != "0.5":
        raise SystemExit(f"fit: the bed is at slider 0.5, machine reads {reads}")


def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def make_doc(out: Path, base: Path, overrides: dict) -> Path:
    """A candidate document: a committed profile's sections with a patch merged over."""
    source = json.loads(base.read_text())
    doc = {
        "$comment": [
            "W29 G3 SCRATCH — a fit candidate, not evidence. The sealed documents are",
            "packages/calibration/profiles/apple-macos-27.0-*.json.",
        ],
        "profileKey": source.get("profileKey"),
        "colorSpace": source.get("colorSpace", "srgb"),
        "patch": deep_merge(source.get("patch", {}), overrides.get("patch", {})),
    }
    mapping = deep_merge(source.get("cssTierMapping", {}), overrides.get("cssTierMapping", {}))
    if mapping:
        doc["cssTierMapping"] = mapping
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n")
    return out


def render(label: str, profile: str, renderer: str, document: Path, argv: list[str]) -> Path:
    machine_ready()
    run = SCRATCH / "fit-log" / label
    run.mkdir(parents=True, exist_ok=True)
    matrix = run / f"{profile}.{renderer}.json"
    if matrix.exists():
        matrix.unlink()
    command = [
        "npx", "tsx", "cli/compare.ts",
        "--profile", profile,
        "--material-profile", str(document),
        "--renderer", renderer,
        "--out-matrix", str(matrix),
        "--write-partial",
        *argv,
    ]
    env = {**os.environ, "VITREA_WEB_CAPTURES": str(run / "web-captures")}
    log = (run / f"{profile}.{renderer}.log").open("w")
    # `compare` exits 1 when a cell could not be measured and `--write-partial`
    # is what lets the rest of the run stand. A fit loop reads the cells that
    # measured and the log names the ones that did not, so the exit code is
    # checked against the matrix having been written rather than against zero.
    subprocess.run(command, cwd=PACKAGE, env=env, stdout=log, stderr=subprocess.STDOUT)
    if not matrix.exists():
        raise SystemExit(f"fit: {matrix} was not written; see {run}")
    return matrix


def readings(matrix: Path) -> list[dict]:
    cells = json.loads(matrix.read_text())["cells"]
    rows = []
    for cell in cells:
        material = cell.get("material") or {}
        at = lambda k: material[k]["value"] if isinstance(material.get(k), dict) else None
        scene = cell["key"]["sceneId"]
        rows.append(
            {
                "profile": cell["key"]["profileKey"],
                "renderer": cell["key"]["web"]["renderer"],
                "scene": scene,
                "set": cell.get("fixtureSet"),
                "state": cell.get("state"),
                "backdrop": scene.split("__")[0],
                "x": BACKDROP_ENCODED_MEAN.get(scene.split("__")[0]),
                "component": scene.split("__")[1] if "__" in scene else None,
                "interiorMeanNative": at("interiorMeanNative"),
                "interiorMeanWeb": at("interiorMeanWeb"),
                "interiorStdDevNative": at("interiorStdDevNative"),
                "interiorStdDevWeb": at("interiorStdDevWeb"),
                "rimPeakNative": at("rimPeakLuminanceNative"),
                "rimPeakWeb": at("rimPeakLuminanceWeb"),
                "rimFwhmNative": at("rimFwhmNative"),
                "rimFwhmWeb": at("rimFwhmWeb"),
                "slopeNative": at("luminanceSlopeNative"),
                "slopeWeb": at("luminanceSlopeWeb"),
                "tintDeltaLNative": at("tintDeltaLNative"),
                "tintDeltaLWeb": at("tintDeltaLWeb"),
                "ssim": ((cell.get("perceptual") or {}).get("ssimMean") or {}).get("value"),
                "deMean": ((cell.get("perceptual") or {}).get("oklabDeltaEMean") or {}).get("value"),
                "deP95": ((cell.get("perceptual") or {}).get("oklabDeltaEP95") or {}).get("value"),
            }
        )
    return rows


def table(label: str, metric: str = "interiorMean") -> None:
    run = SCRATCH / "fit-log" / label
    rows: list[dict] = []
    for matrix in sorted(run.glob("*.json")):
        rows += readings(matrix)
    rows = [r for r in rows if r.get(f"{metric}Native") is not None]
    rows.sort(key=lambda r: (r["profile"], r["state"] or "", r["x"] or 0, r["scene"]))
    print(f"{'profile':<50}{'state':<9}{'scene':<44}{'x':>7}{'N':>9}{'W':>9}{'W-N':>9}")
    for r in rows:
        native, web = r[f"{metric}Native"], r[f"{metric}Web"]
        print(
            f"{r['profile']:<50}{(r['state'] or ''):<9}{r['scene']:<44}"
            f"{(r['x'] if r['x'] is not None else float('nan')):>7.3f}"
            f"{native:>9.4f}{web:>9.4f}{web - native:>9.4f}"
        )
    if rows:
        worst = max(rows, key=lambda r: abs(r[f"{metric}Web"] - r[f"{metric}Native"]))
        mean = sum(abs(r[f"{metric}Web"] - r[f"{metric}Native"]) for r in rows) / len(rows)
        print(f"\nmean |Δ| {mean:.5f} over {len(rows)} cells; worst {worst['scene']} "
              f"{worst[f'{metric}Web'] - worst[f'{metric}Native']:+.5f}")


def main() -> int:
    verb = sys.argv[1]
    if verb == "doc":
        out, base, overrides = (Path(a) for a in sys.argv[2:5])
        print(make_doc(out, base, json.loads(overrides.read_text())))
    elif verb == "render":
        label, profile, renderer, document = sys.argv[2:6]
        print(render(label, profile, renderer, Path(document), sys.argv[6:]))
    elif verb == "table":
        table(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "interiorMean")
    elif verb == "merge":
        # Every matrix a label's renders wrote, as one file the referee can read.
        # The cells keep their own keys, so a merge can never fuse two rows.
        out = Path(sys.argv[2])
        cells: list[dict] = []
        for source in sys.argv[3:]:
            for matrix in sorted((SCRATCH / "fit-log" / source).glob("*.json")):
                cells += json.loads(matrix.read_text())["cells"]
        out.write_text(json.dumps({"schemaVersion": 5, "cells": cells}))
        print(f"{out} ({len(cells)} cells)")
    else:
        raise SystemExit(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
