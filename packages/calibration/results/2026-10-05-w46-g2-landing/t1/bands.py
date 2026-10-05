#!/usr/bin/env python3.12
"""W46 G2: the text stratum's two bands on the published DARK 0.25 generation `d0219cd684bf`, as the
fixture the owner test reads (claims §5.210; charter Decision Logs 3 and 10; W44 G2's `t1/bands.py`,
`results/2026-10-03-w44-g2-landing/t1/bands.py`, ported for the dark profiles).

A T cell (`hc-text-7`) reads its fidelity on T1-fine and its regression on T1-low: the SD of the
residual L - G(L, sigma 4 device px), and of the low-pass G(L, 4), in linear luminance over the native
silhouette eroded 4 CSS px. The matrix rows do not carry them, so this reads them once, through W44 G1's
pinned `cuts/readings.py`, off the CANONICAL capture tree, for every T cell of the two dark 0.25
profiles on the WebGPU tier in every set, and writes `t-bands-d0219cd684bf.json`. Each entry names its
row's `capturePath` and its PNG's SHA-256.

    python3.12 -B bands.py [--captures TREE]      (refuses to overwrite the fixture)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
sys.path.insert(0, str(RESULTS / "2026-10-05-w46-g0-declaration"))
import bindings as W  # noqa: E402

B, T1, _ = W.load_cuts()
sys.path.insert(0, str(W.W44_G1 / "cuts"))
import readings as R  # noqa: E402

GENERATION = "d0219cd684bf"
OUT = HERE / f"t-bands-{GENERATION}.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", type=Path, default=W.CANONICAL_CAPTURES)
    args = ap.parse_args()
    if OUT.exists():
        raise SystemExit(f"{OUT} exists; a fixture's bytes never move")
    rgb = lambda p: np.asarray(Image.open(p).convert("RGB"))  # noqa: E731
    entries = []
    for r in B.load_published(GENERATION).rows:
        profile, sid, tier = r["key"]["profileKey"], r["key"]["sceneId"], r["key"]["web"]["renderer"]
        if profile not in W.DARK_025 or tier != "webgpu" or B.SCENES.by_id[sid]["background"] not in T1.STRATA["T"]:
            continue
        folder = args.captures / profile / sid
        meta = json.loads((folder / f"cell__{tier}.json").read_text())
        if meta.get("capturePath") != r["key"]["web"]["capturePath"]:
            raise SystemExit(f"{profile} {sid}: the capture names another generation than the row")
        png = folder / f"{sid}__{tier}.png"
        native = W.ROOT / "apps/reference-apple/fixtures" / profile / f"{sid}.png"
        got = R.read(profile, sid, rgb(native), rgb(png))
        entries.append(dict(profile=profile, renderer=tier, scene=sid, set=r["fixtureSet"],
                            capturePath=r["key"]["web"]["capturePath"],
                            webSha256=hashlib.sha256(png.read_bytes()).hexdigest(),
                            bands={b: dict(native=got["native"][b], web=got["web"][b]) for b in T1.BANDS},
                            erodedPixels=got["pixels"]["eroded"]))
    entries.sort(key=lambda e: (e["profile"], e["scene"]))
    body = dict(
        what="W46 G2: T1-fine and T1-low of every T cell of the dark 0.25 profiles, WebGPU, read off the "
             "canonical capture tree through W44 G1's cuts/readings.py (claims §5.210)",
        generation=GENERATION,
        readers={n: hashlib.sha256((W.W44_G1 / "cuts" / n).read_bytes()).hexdigest() for n in ("readings.py", "t1.py")},
        definition=dict(fine="SD of L - G(L, sigma 4 device px), linear luminance, native silhouette eroded 4 CSS px",
                        low="SD of G(L, sigma 4 device px) over the same support",
                        sigmaDevicePx=R.FINE_SIGMA_DEVICE, erodeCssPx=R.ERODE_CSS),
        entries=entries)
    with OUT.open("x") as f:
        f.write(json.dumps(body, indent=1) + "\n")
    print(f"{len(entries)} T cells -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
