#!/usr/bin/env python3.12
"""W44 G0 (b): prove the port reproduces the driver on the plurality fixture, every T1 cell (clause 4).

For every T1 cell (the light 0.25 profiles at both scales, every structured scene in every set),
and every structured cell of the dark 0.25 profiles, which T1 reads and does not gate, the port (`interior.py`) reads the published plurality fixture and the shared background raster,
builds the native silhouette, and reports its interior mean and SD. Each must equal what the
driver recorded on the published rows (`generations/6d18c059eb42.json`, light; `d0219cd684bf.json`,
dark) to 1e-6 absolute, on
BOTH tiers' rows (the native side of a cell is one measurement, written into each tier's row). It
reads native pixels only: no web render is compared, so no configuration is exposed to the
holdout's native frames by this proof.

    python3.12 -B prove.py              writes proof.json beside it; exit 1 if any cell misses 1e-6
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402
import interior as P  # noqa: E402

TOLERANCE = 1e-6
FIXTURES = B.ROOT / "apps/reference-apple/fixtures"
T1_BACKDROPS = ("checkerboard", "checkerboard-lc16", "checkerboard-4", "checkerboard-8", "checkerboard-32",
                "checkerboard-64", "hc-text", "hc-text-7", "hc-text-28", "impulse", "photo")
LIGHT = ("apple-macos-27.0-1x-light-standard-glass0.25", "apple-macos-27.0-2x-light-standard-glass0.25")
DARK = ("apple-macos-27.0-1x-dark-standard-glass0.25", "apple-macos-27.0-2x-dark-standard-glass0.25")


def t1_cells(profiles=LIGHT + DARK):
    for profile in profiles:
        for sid in B.SCENES.declared(profile):
            if B.SCENES.by_id[sid]["background"] in T1_BACKDROPS:
                yield profile, sid


def native_reading(profile: str, sid: str, raw: bytes | None = None) -> dict:
    scene = B.SCENES.by_id[sid]
    scale = B.scale_of(profile)
    native = P.decode(raw if raw is not None else (FIXTURES / profile / f"{sid}.png").read_bytes())
    background = P.read(FIXTURES / "backgrounds" / f"{scene['background']}@{scale}x.png")
    mask = P.native_interior(native, background, B.SCENES.component(sid), B.SCENES.canvas, scale)
    return P.level(native, mask)


def main() -> int:
    rows = B.load_published("6d18c059eb42").rows + B.load_published("d0219cd684bf").rows
    recorded = {}
    for r in rows:
        recorded.setdefault((r["key"]["profileKey"], r["key"]["sceneId"]), {})[r["key"]["web"]["renderer"]] = r
    cells, worst, misses = [], 0.0, []
    for profile, sid in t1_cells():
        got = native_reading(profile, sid)
        entry = dict(profile=profile, scene=sid, set=B.SCENES.role[sid],
                     gated=profile in LIGHT, portMean=got["mean"],
                     portStdDev=got["stdDev"], pixels=got["count"],
                     fixtureSha256=hashlib.sha256((FIXTURES / profile / f"{sid}.png").read_bytes()).hexdigest())
        for tier, row in sorted(recorded[(profile, sid)].items()):
            sd, mean = B.value(row, "material", "interiorStdDevNative"), B.value(row, "material", "interiorMeanNative")
            d_sd, d_mean = abs(got["stdDev"] - sd), abs(got["mean"] - mean)
            entry[tier] = dict(driverStdDev=sd, driverMean=mean, absDiffStdDev=d_sd, absDiffMean=d_mean)
            worst = max(worst, d_sd, d_mean)
            if d_sd > TOLERANCE or d_mean > TOLERANCE:
                misses.append(f"{profile}/{sid} {tier}: sd {d_sd:.3g} mean {d_mean:.3g}")
        cells.append(entry)
    out = dict(
        schema="w44-port-proof-1",
        what="W44 G0 (b), clause 4: the Python port of the driver's interior statistic against the "
             "recorded interiorStdDevNative / interiorMeanNative, plurality fixture, every T1 cell",
        tolerance=TOLERANCE, cells=len(cells), rowsCompared=sum(1 for c in cells for t in ("css", "webgpu") if t in c),
        worstAbsDiff=worst, misses=misses,
        generations=["packages/calibration/results/generations/6d18c059eb42.json",
                     "packages/calibration/results/generations/d0219cd684bf.json"],
        gatedCells=sum(1 for c in cells if c["gated"]),
        port={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE / "interior.py", HERE / "prove.py")},
        table=cells)
    (HERE / "proof.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{len(cells)} T1 cells, {out['rowsCompared']} rows; worst |port - driver| {worst:.3g}; "
          f"{len(misses)} beyond {TOLERANCE}")
    for m in misses[:20]:
        print("  MISS", m)
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
