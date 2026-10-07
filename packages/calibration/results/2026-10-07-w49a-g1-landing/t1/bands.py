#!/usr/bin/env python3.12
"""X59 (i): W49a's eight dark T-cell bands, keyed by BOTH documents and each capture path.

Read the completed stage, not the canonical tree awaiting its landing copy. Each capture must
name its row exactly; each computed band must equal the regenerated landing cut's reading.
The W46 and W48 fixtures stay unchanged and are required separately by derive.py.

  python3.12 -B bands.py --stage STAGE
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
sys.path.insert(0, str(HERE))
import w49_inputs as I

C = I.cuts()
B, T1 = C.B, C.T1
sys.path.insert(0, str(B.W44_G1 / "cuts"))
import readings as R

OUT = HERE / f"t-bands-{I.GENERATION}.json"
CUT = HERE.parent / "cuts/cut-025-dark-w49a-landing.json"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=Path, required=True)
    args = ap.parse_args()
    if OUT.exists():
        raise SystemExit(f"{OUT} exists; a fixture's bytes never move")
    readings = {r["cell"]: r for r in json.loads(CUT.read_text())["T1"]["readings"]}
    entries = []
    for row in I.stage_rows(args.stage):
        profile, tier, sid = I.row_key(row)
        if tier != "webgpu" or B.SCENES.by_id[sid]["background"] not in T1.STRATA["T"]:
            continue
        folder = args.stage / "web-captures" / profile / sid
        meta = json.loads((folder / f"cell__{tier}.json").read_text())
        path = row["key"]["web"]["capturePath"]
        if meta.get("capturePath") != path:
            raise ValueError(f"{profile} {sid}: capture does not name row")
        png = folder / f"{sid}__{tier}.png"
        native = B.ROOT / "apps/reference-apple/fixtures" / profile / f"{sid}.png"
        got = R.read(profile, sid, np.asarray(Image.open(native).convert("RGB")),
                     np.asarray(Image.open(png).convert("RGB")))
        sha = hashlib.sha256(png.read_bytes()).hexdigest()
        cut = readings[f"{profile} {tier} {sid}"]
        if cut["webSha256"] != sha:
            raise ValueError(f"{sid}: landing cut names another PNG")
        for band in T1.BANDS:
            for side in ("native", "web"):
                if got[side][band] != cut[side][band]:
                    raise ValueError(f"{sid}: {band} {side} disagrees with landing cut")
        entries.append(dict(profile=profile, renderer=tier, scene=sid, set=row["fixtureSet"],
                            capturePath=path, webSha256=sha,
                            bands={b: {s: got[s][b] for s in ("native", "web")} for b in T1.BANDS},
                            erodedPixels=got["pixels"]["eroded"]))
    if len(entries) != 8:
        raise ValueError(f"expected eight dark T cells, found {len(entries)}")
    entries.sort(key=lambda e: (e["profile"], e["scene"]))
    body = dict(what="W49a X59 (i): dark T-cell bands from the sealed stage, equal to its landing cut",
                generation=I.GENERATION, active=I.PAIR[0], receded=I.PAIR[1],
                readers={n: hashlib.sha256((B.W44_G1 / "cuts" / n).read_bytes()).hexdigest()
                         for n in ("readings.py", "t1.py")},
                definition=dict(fine="SD of L - G(L, sigma 4 device px), native silhouette eroded 4 CSS px",
                                low="SD of G(L, sigma 4 device px) on the same support; linear luminance",
                                sigmaDevicePx=R.FINE_SIGMA_DEVICE, erodeCssPx=R.ERODE_CSS), entries=entries)
    with OUT.open("x") as f:
        f.write(json.dumps(body, indent=1) + "\n")
    print(f"{len(entries)} T cells, equal to landing cut -> {OUT}")


if __name__ == "__main__":
    main()
