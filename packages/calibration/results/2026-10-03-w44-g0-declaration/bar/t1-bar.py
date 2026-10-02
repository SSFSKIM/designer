#!/usr/bin/env python3.12
"""W44 G0 (b): T1's bar per cell, from the seven G1a runs (charter clause 4; Design "T1", Bar).

    python3.12 -B t1-bar.py [--archive ROOT]     writes t1-bar.json beside it

The archive is W43 G1a's archive of record (`w43-archive-g1a`, asset sha256 f60c784a..., inventory
56489f87...), read from the on-disk copy `~/vitrea-w43/archive-copy-g1a/<asset>/extracted/archive`
after W43's own `verify_tree` (every inventory file present and intact, every frame stored under
its own digest, nothing else). For every T1 cell (both light 0.25 profiles, every structured scene,
every set), and every structured cell of the dark 0.25 profiles (read, not gated), it takes the cell record's seven `bed-*` runs, resolves each to its stored frame, and
reads T1's native statistic on that frame through the proven port (`../port/interior.py`): the
native silhouette of THAT frame, bounded to the declared region, and its linear-luminance SD.

  bar  = 0.5 code + 0.5 x (the largest pairwise separation of the seven runs' values)
  code = the linear step of one encoded sRGB code at the cell's native interior mean (the
         plurality fixture's, `interior.code_step`)

W39's rule on this statistic. A cell whose bar exceeds one code is READ, not gated, and named
(clause 4's stop). Native frames only: nothing here renders or reads a web capture.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE / "port"))
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402
import interior as P  # noqa: E402
import prove  # noqa: E402

ASSET = "f60c784a00c585646394e99812c4dd77ef55f6643b246b2d03fc45156ea28352"
INVENTORY = "56489f87dc6ed07904cc0a57fa26178b19d4becbf656a393dbdf1774bccf6926"
DEFAULT = Path.home() / "vitrea-w43" / "archive-copy-g1a" / ASSET / "extracted" / "archive"
TOOL = B.RESULTS / "2026-10-01-w43-g0-declaration/bed/sitting/w43_archive.py"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", type=Path, default=DEFAULT)
    args = ap.parse_args()
    root = args.archive
    spec = importlib.util.spec_from_file_location("w43_archive", TOOL)
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    tree = A.verify_tree(root)
    if tree["inventorySha256"] != INVENTORY:
        raise SystemExit(f"archive inventory {tree['inventorySha256']}, not w43-archive-g1a's {INVENTORY}")
    records = {}
    for path in root.glob("*/*.cell.json.gz"):
        record = json.loads(gzip.decompress(path.read_bytes()))
        records[record["cell"]] = record
    cells, over = [], []
    for profile, sid in prove.t1_cells():
        record = records.get(f"{profile}/{sid}")
        if record is None:
            raise SystemExit(f"{profile}/{sid}: no record in the archive")
        runs = sorted((r for r in record["runs"] if r["pass"].startswith("bed-")), key=lambda r: r["run"])
        if len(runs) != 7:
            raise SystemExit(f"{profile}/{sid}: {len(runs)} bed runs, not seven")
        values, frames = [], []
        for run in runs:
            raw = (root / "frames" / f"{run['frame']}.png").read_bytes()
            if hashlib.sha256(raw).hexdigest() != run["frame"]:
                raise SystemExit(f"{profile}/{sid}: frame {run['frame']} is not its name")
            values.append(prove.native_reading(profile, sid, raw)["stdDev"])
            frames.append(run["frame"])
        plurality = prove.native_reading(profile, sid)
        fixture = P.read(prove.FIXTURES / profile / f"{sid}.png")
        identical = sum(bool((P.decode((root / "frames" / f"{f}.png").read_bytes()) == fixture).all())
                        for f in frames)
        code = P.code_step(plurality["mean"])
        spread = max(abs(a - b) for a, b in itertools.combinations(values, 2))
        bar = 0.5 * code + 0.5 * spread
        cell = dict(profile=profile, scene=sid, set=B.SCENES.role[sid], gated=profile in prove.LIGHT,
                    runs=len(runs),
                    distinctFrames=len(set(frames)), runsPixelIdenticalToFixture=identical,
                    nativeMean=plurality["mean"], nativeStdDev=plurality["stdDev"], code=code,
                    runValues=values, largestPairwiseSeparation=spread, bar=bar, barCodes=bar / code,
                    status="read, not gated (bar above one code)" if bar > code else "gated")
        if bar > code and profile in prove.LIGHT:
            over.append(f"{profile}/{sid}")
        cells.append(cell)
    codes = [c["barCodes"] for c in cells]
    out = dict(
        schema="w44-t1-bar-1",
        what="W44 G0 (b), clause 4: T1's native run-to-run bar per cell from the seven G1a runs, "
             "0.5 code + half the largest pairwise separation, through the proven port",
        archive=dict(asset=ASSET, inventorySha256=tree["inventorySha256"], entries=tree["entries"],
                     root=str(root)),
        tools={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
               for p in (Path(__file__), EVIDENCE / "port/interior.py", EVIDENCE / "port/prove.py")},
        rule="bar = 0.5 * code + 0.5 * max_{i<j} |sd_i - sd_j| over the seven bed runs; code = "
             "interior.code_step(native interior mean of the plurality fixture)",
        cells=len(cells), barCodesRange=[min(codes), max(codes)],
        barLinearRange=[min(c["bar"] for c in cells), max(c["bar"] for c in cells)],
        maxSeparation=max(c["largestPairwiseSeparation"] for c in cells),
        cellsWithMoreThanOneFrame=[f"{c['profile']}/{c['scene']}" for c in cells if c["distinctFrames"] > 1],
        cellsWithRunsNotIdenticalToFixture=[f"{c['profile']}/{c['scene']}" for c in cells
                                            if c["runsPixelIdenticalToFixture"] != c["runs"]],
        readNotGated=over, table=cells)
    (HERE / "t1-bar.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{len(cells)} T1 cells; bar {min(codes):.3f}-{max(codes):.3f} code "
          f"({out['barLinearRange'][0]:.5f}-{out['barLinearRange'][1]:.5f} linear); max separation "
          f"{out['maxSeparation']:.3g}; {len(out['cellsWithMoreThanOneFrame'])} cells with more than one "
          f"frame; {len(out['cellsWithRunsNotIdenticalToFixture'])} with a run unlike the fixture; "
          f"{len(over)} read, not gated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
