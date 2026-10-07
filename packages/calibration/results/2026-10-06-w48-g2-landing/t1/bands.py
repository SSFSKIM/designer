#!/usr/bin/env python3.12
"""W48 G2: the text stratum's two bands on the published DARK 0.25 generation `b2d074d2df24`, as the
fixture the owner test pins beside W46's `d0219cd684bf` one (claims §5.214; charter clause 10, X59 part (i)).
W46 G2's `t1/bands.py` (`results/2026-10-05-w46-g2-landing/t1/bands.py`), copied; only the generation, the
output and the labels change, and every entry is held to the band reading G1's exposure cut and this
landing's cut carry for the same capture (`--check`).

G1 committed no standalone fixture: its exposure cut (`2026-10-06-w48-g1-refit/cuts/
cut-025-w48-dl9-exposure.json.gz`, `T1.readings`) carries the eight T cells' bands, read off its stage's
captures, which the canonical tree now holds byte for byte (`../tree/witness-copy.json`). This reads them
again off the canonical tree through the same pinned readers and asserts equality with both cuts.

W46 G2's text follows.

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

GENERATION = "b2d074d2df24"
CUTS = (RESULTS / "2026-10-06-w48-g1-refit" / "cuts" / "cut-025-w48-dl9-exposure.json.gz",
        RESULTS / "2026-10-06-w48-g2-landing" / "cuts" / "cut-025-dark-w48-landing.json")
OUT = HERE / f"t-bands-{GENERATION}.json"


def check(entries) -> None:
    """Every entry equals the band readings both cuts carry for the same capture (by its PNG's SHA-256)."""
    import gzip
    for path in CUTS:
        opener = gzip.open if path.suffix == ".gz" else open
        with opener(path, "rt") as f:
            readings = {r["cell"]: r for r in json.load(f)["T1"]["readings"]}
        for e in entries:
            got = readings.get(f"{e['profile']} {e['renderer']} {e['scene']}")
            if got is None or got["webSha256"] != e["webSha256"]:
                raise SystemExit(f"{path.name}: {e['scene']} has no reading of this capture")
            for b in T1.BANDS:
                for side in ("native", "web"):
                    if got[side][b] != e["bands"][b][side]:
                        raise SystemExit(f"{path.name}: {e['profile']} {e['scene']} {b} {side}: "
                                         f"{got[side][b]} against {e['bands'][b][side]}")
        print(f"{len(entries)} entries equal to {path.name}")


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
        what="W48 G2: T1-fine and T1-low of every T cell of the dark 0.25 profiles at b2d074d2df24, WebGPU, read "
             "off the canonical capture tree through W44 G1's cuts/readings.py; equal to G1's exposure cut and "
             "the landing cut on every entry (claims §5.214)",
        generation=GENERATION,
        readers={n: hashlib.sha256((W.W44_G1 / "cuts" / n).read_bytes()).hexdigest() for n in ("readings.py", "t1.py")},
        definition=dict(fine="SD of L - G(L, sigma 4 device px), linear luminance, native silhouette eroded 4 CSS px",
                        low="SD of G(L, sigma 4 device px) over the same support",
                        sigmaDevicePx=R.FINE_SIGMA_DEVICE, erodeCssPx=R.ERODE_CSS),
        entries=entries)
    check(entries)
    with OUT.open("x") as f:
        f.write(json.dumps(body, indent=1) + "\n")
    print(f"{len(entries)} T cells -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
