#!/usr/bin/env python3.12
"""W44 G2: the text stratum's two bands on the published light 0.25 generation, as a fixture the
owner test reads (claims §5.204; charter Decision Log 7 item 3).

A T cell (`hc-text-7`) reads its fidelity on T1-fine and its regression on T1-low (Decision Log 7),
and both bands are image statistics the matrix rows do not carry: the SD of the residual
L - G(L, sigma 4 device px), and of the low-pass G(L, 4), in linear luminance over the native
silhouette eroded 4 CSS px. `adopted-thresholds.test.ts` reads rows only, so this script reads
them once, through W44 G1's `cuts/readings.py` (the readers part 2's amendment pins), off the
CANONICAL capture tree for every T cell of the two light 0.25 profiles on the WebGPU tier, every
set, and writes `t-bands.json`: each entry names its row's `capturePath` and its PNG's SHA-256, so
the test can hold the fixture to the rows it reads and, where the tree is on disk, to the bytes.

    python3.12 -B bands.py [--captures TREE]      (refuses to overwrite t-bands.json)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
G1_CUTS = CAL / "results" / "2026-10-03-w44-g1-refit" / "cuts"
sys.path.insert(0, str(G1_CUTS))
import bed as B  # noqa: E402
import readings as R  # noqa: E402
import t1  # noqa: E402

CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
GENERATION = "6d18c059eb42"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", type=Path, default=CANONICAL)
    args = ap.parse_args()
    out = HERE / "t-bands.json"
    if out.exists():
        raise SystemExit(f"{out} exists; a fixture's bytes never move")
    rows = B.load_published(GENERATION).rows
    entries = []
    for r in rows:
        profile, sid, tier = r["key"]["profileKey"], r["key"]["sceneId"], r["key"]["web"]["renderer"]
        if profile not in t1.GATED_PROFILES or tier != "webgpu":
            continue
        if B.SCENES.by_id[sid]["background"] not in t1.STRATA["T"]:
            continue
        folder = args.captures / profile / sid
        meta = json.loads((folder / f"cell__{tier}.json").read_text())
        if meta.get("capturePath") != r["key"]["web"]["capturePath"]:
            raise SystemExit(f"{profile} {sid}: the capture names another generation than the row")
        png = folder / f"{sid}__{tier}.png"
        native = B.ROOT / "apps/reference-apple/fixtures" / profile / f"{sid}.png"
        import numpy as np
        from PIL import Image
        rgb = lambda p: np.asarray(Image.open(p).convert("RGB"))  # noqa: E731
        got = R.read(profile, sid, rgb(native), rgb(png))
        entries.append(dict(profile=profile, renderer=tier, scene=sid, set=r["fixtureSet"],
                            capturePath=r["key"]["web"]["capturePath"],
                            webSha256=hashlib.sha256(png.read_bytes()).hexdigest(),
                            bands={b: dict(native=got["native"][b], web=got["web"][b]) for b in t1.BANDS},
                            erodedPixels=got["pixels"]["eroded"]))
    entries.sort(key=lambda e: (e["profile"], e["scene"]))
    body = dict(
        what="W44 G2: T1-fine and T1-low of every T cell of the light 0.25 profiles, WebGPU, read off the "
             "canonical capture tree through W44 G1's cuts/readings.py (claims §5.204)",
        generation=GENERATION,
        readers={n: hashlib.sha256((G1_CUTS / n).read_bytes()).hexdigest() for n in ("readings.py", "t1.py")},
        definition=dict(fine="SD of L - G(L, sigma 4 device px), linear luminance, native silhouette eroded 4 CSS px",
                        low="SD of G(L, sigma 4 device px) over the same support",
                        sigmaDevicePx=R.FINE_SIGMA_DEVICE, erodeCssPx=R.ERODE_CSS),
        entries=entries)
    with out.open("x") as f:
        f.write(json.dumps(body, indent=1) + "\n")
    print(f"{len(entries)} T cells -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
