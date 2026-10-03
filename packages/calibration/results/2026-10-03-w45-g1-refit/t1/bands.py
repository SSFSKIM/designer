#!/usr/bin/env python3.12
"""W45 G1: the candidate's T-band fixture, read off the light stage's captures (charter G2's
five-part order, part (i) at the gate and part (ii) at the exposure; claims §5.206).

The owner test's T1 block reads a T cell (`hc-text-7`) on two bands the rows do not carry, T1-fine
and T1-low, from one fixture keyed by capture path (`results/2026-10-03-w44-g2-landing/t1/
t-bands.json`, the reference generation's, which stays as it is). Clause (b) looks up BOTH the
candidate's and the reference's T cells through a fixture, so the candidate's bands are read into
a NEW fixture beside the reference's, keyed by its generation and capture path, through the same
readers (W44 G1's `cuts/readings.py` and `t1.py`, shared by path and pinned), exactly as W44 G2's
`bands.py` read the reference.

    python3.12 -B bands.py gate     --stage MATRIX --captures TREE --generation SHA12
    python3.12 -B bands.py exposure --stage MATRIX --captures TREE --generation SHA12

`gate` reads the T cells of the gate partition (no referee, no holdout) and writes
`t-bands-<generation>.gate.json`; `exposure` reads every T cell the stage then holds (the exposed
ones added) and writes `t-bands-<generation>.json`, whose gate entries must equal the gate file's
byte for byte in value. Neither ever overwrites a file. Before a pixel is read, each capture's cell
JSON must name its row's `capturePath` (the sealed documents), and every row must be drawn with the
sealed light documents the generation names.
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
G1 = HERE.parent
CAL = G1.parents[1]
sys.path.insert(0, str(CAL / "results" / "2026-10-03-w45-g0-operator" / "fit"))
import bindings as W  # noqa: E402

B, t1 = W.load_cuts()
if str(W.READINGS_PATH.parent) not in sys.path:
    sys.path.append(str(W.READINGS_PATH.parent))
import readings as R  # noqa: E402  (W44 G1's, pinned by bindings.SHARED)

if Path(R.__file__).resolve() != W.READINGS_PATH.resolve():
    raise SystemExit(f"readings imported from {R.__file__}, not W44 G1's pinned {W.READINGS_PATH}")

PROFILES = W.LIGHT_025


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(stage: Path, captures: Path, generation: str, partitions: tuple[str, ...]) -> list[dict]:
    plan = W.referee_plan()
    held = plan.referee_cells(plan.load_manifest())
    rows = json.loads(stage.read_bytes())["cells"]
    entries = []
    for r in rows:
        profile, sid, tier = r["key"]["profileKey"], r["key"]["sceneId"], r["key"]["web"]["renderer"]
        if profile not in PROFILES or tier != "webgpu" or B.SCENES.by_id[sid]["background"] not in t1.STRATA["T"]:
            continue
        part = t1.partition(profile, sid, held)
        if part not in partitions:
            continue
        cp = r["key"]["web"]["capturePath"]
        if f"sha256:{generation}" not in cp:
            raise SystemExit(f"{profile} {sid}: the row is not drawn with the generation's active document {generation}")
        folder = captures / profile / sid
        meta = json.loads((folder / f"cell__{tier}.json").read_text())
        if meta.get("capturePath") != cp:
            raise SystemExit(f"{profile} {sid}: the capture names another generation than the row")
        png = folder / f"{sid}__{tier}.png"
        native = W.ROOT / "apps/reference-apple/fixtures" / profile / f"{sid}.png"
        rgb = lambda p: np.asarray(Image.open(p).convert("RGB"))  # noqa: E731
        got = R.read(profile, sid, rgb(native), rgb(png))
        entries.append(dict(profile=profile, renderer=tier, scene=sid, set=r["fixtureSet"], partition=part,
                            capturePath=cp, webSha256=sha(png),
                            bands={b: dict(native=got["native"][b], web=got["web"][b]) for b in t1.BANDS},
                            erodedPixels=got["pixels"]["eroded"]))
    entries.sort(key=lambda e: (e["profile"], e["scene"]))
    return entries


def body(generation: str, entries: list[dict], what: str) -> dict:
    return dict(
        what=what, generation=generation,
        readers={n: sha(p) for n, p in (("readings.py", W.READINGS_PATH), ("t1.py", W.T1_PATH))},
        definition=dict(fine="SD of L - G(L, sigma 4 device px), linear luminance, native silhouette eroded 4 CSS px",
                        low="SD of G(L, sigma 4 device px) over the same support",
                        sigmaDevicePx=R.FINE_SIGMA_DEVICE, erodeCssPx=R.ERODE_CSS),
        reference="results/2026-10-03-w44-g2-landing/t1/t-bands.json (generation 6d18c059eb42), unchanged",
        entries=entries)


def write(path: Path, data: dict) -> None:
    with path.open("x") as f:
        f.write(json.dumps(data, indent=1) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("gate", "exposure"))
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--captures", type=Path, required=True)
    ap.add_argument("--generation", required=True)
    args = ap.parse_args()
    W.refuse_w44_path(args.stage, "the stage")
    gate_file = HERE / f"t-bands-{args.generation}.gate.json"
    if args.mode == "gate":
        entries = read(args.stage, args.captures, args.generation, ("gate",))
        write(gate_file, body(args.generation, entries,
                              "W45 G1 (gate): T1-fine and T1-low of the candidate's T cells in the gate partition, "
                              "light 0.25, WebGPU, read off the stage's captures (claims §5.206; G2 part (i))"))
        print(f"{len(entries)} gate T cells -> {gate_file}")
        return 0
    gate = json.loads(gate_file.read_text())
    entries = read(args.stage, args.captures, args.generation, ("gate", "referee", "holdout"))
    by = {(e["profile"], e["scene"]): e for e in entries}
    for e in gate["entries"]:
        if by.get((e["profile"], e["scene"])) != e:
            raise SystemExit(f"{e['profile']} {e['scene']}: the stage's reading is not the gate fixture's")
    out = HERE / f"t-bands-{args.generation}.json"
    write(out, body(args.generation, entries,
                    "W45 G1 (exposure): T1-fine and T1-low of every T cell of the candidate, light 0.25, WebGPU, "
                    "read off the stage's captures; the gate entries are the gate fixture's, the exposed ones "
                    "added (claims §5.206; G2 parts (i) and (ii))"))
    print(f"{len(entries)} T cells ({len(entries) - len(gate['entries'])} exposed) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
