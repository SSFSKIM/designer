#!/usr/bin/env python3.12
"""W46 G0 (a): objectives with an UNMEASURED member, recovered beside the record — W45 G0's
`recover.py` (`results/2026-10-03-w45-g0-operator/fit/recover.py`) ported for W46's two scales and
stages (clause 1). W45's committed copy is untouched. Writes G1's `fit/path/recovered.json`; the
summaries stay as recorded.

    python3.12 -B recover.py

**What W46 changes.** Both dark profiles: a member is `<scale>x <scene>`, read off that scale's scope
directory (`<scope>-<scale>x`) through W44 G0's port at that scale; the native SD is the published
`d0219cd684bf` row's (the reference the cut reads).

W45's text, unchanged: a render can write a cell's capture and then fail the cell on an axis T1 does
not read, so the row is absent and a scope objective recorded over it is a median over fewer cells
than the scope's F u C u P — not the declared statistic. T1's web reading is the luminance SD of the
WEB capture over the NATIVE silhouette, which the port reproduces. For every point whose summary
lacks a member of a scope it rendered, this reads the missing cell's web SD off the point's scratch
capture through the port (the capture's cell JSON must name the point's declaration), proves the port
reproduces the driver's recorded `interiorStdDevWeb` on every row that render DID record (to 1e-6),
and records the scope objective over all its members. `search.decide` ranks such a point on that
value or not at all.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit  # noqa: E402

W = fit.W
FIXTURES = W.ROOT / "apps/reference-apple/fixtures"
TOLERANCE = 1e-6


def port():
    W.require_shared()
    return W.load_module("w46_port_interior", W.PORT / "interior.py")


def capture_dir(label: str, scale: int, sid: str) -> Path | None:
    root = W.refuse_other_wave_path(fit.SCRATCH / label, "the scratch render")
    for d in sorted(root.iterdir()) if root.exists() else []:
        if d.name.endswith(f"-{scale}x") and (d / "web-captures" / fit.PROFILE[scale] / sid / "cell__webgpu.json").exists():
            return d
    return None


def web_sd(P, B, label: str, scale: int, sid: str, scope_dir: Path) -> float:
    profile = fit.PROFILE[scale]
    folder = scope_dir / "web-captures" / profile / sid
    meta = json.loads((folder / "cell__webgpu.json").read_text())
    want = str((fit.G1 / "candidates" / label / "candidate.json").relative_to(W.ROOT))
    if f"candidateDocument={want}" not in meta["capturePath"]:
        raise W.Refusal(f"{label} {sid}: the capture names {meta['capturePath'][-200:]}, not {want}")
    native = P.read(FIXTURES / profile / f"{sid}.png")
    background = P.read(FIXTURES / "backgrounds" / f"{B.SCENES.by_id[sid]['background']}@{scale}x.png")
    mask = P.native_interior(native, background, B.SCENES.component(sid), B.SCENES.canvas, scale)
    return P.level(P.read(folder / f"{sid}__webgpu.png"), mask)["stdDev"]


def main() -> int:
    B, t1, _ = fit.cuts()
    P = port()
    ref = {(r["key"]["profileKey"], r["key"]["sceneId"]): r for r in B.load_published(W.REFERENCE["dark"]).rows
           if r["key"]["web"]["renderer"] == "webgpu"}
    out, proof = {}, []
    for f in sorted((fit.G1 / "candidates").glob("*/summary.json")):
        s = json.loads(f.read_text())
        label = s["label"]
        proved = False
        for scope in fit.ALL_SCOPES:
            if s["stages"].get(scope, {}).get("objective") is None:
                continue
            members = fit.selection_members(scope)
            missing = [m for m in members if m not in s["cells"]]
            where = {m: capture_dir(label, int(m.split("x ")[0]), m.split("x ", 1)[1]) for m in missing}
            if not missing or any(d is None for d in where.values()):
                continue
            if not proved:
                for scope_dir in sorted(d for d in (fit.SCRATCH / label).iterdir() if (d / "matrix.json").exists()):
                    scale = int(scope_dir.name.rsplit("-", 1)[1].rstrip("x"))
                    for row in json.loads((scope_dir / "matrix.json").read_bytes())["cells"]:
                        sid = row["key"]["sceneId"]
                        got = web_sd(P, B, label, scale, sid, scope_dir)
                        driver = B.value(row, "material", "interiorStdDevWeb")
                        proof.append(dict(label=label, scope=scope_dir.name, scene=sid, port=got, driver=driver,
                                          diff=abs(got - driver)))
                proved = True
            logs = {k: abs(math.log(c["k"] / c["n"])) for k, c in s["cells"].items() if k in members}
            recovered = {}
            for m in missing:
                scale, sid = int(m.split("x ")[0]), m.split("x ", 1)[1]
                k = web_sd(P, B, label, scale, sid, where[m])
                n = B.value(ref[(fit.PROFILE[scale], sid)], "material", "interiorStdDevNative")
                recovered[m] = dict(native=n, web=k, ratio=k / n)
                logs[m] = abs(math.log(k / n))
            out.setdefault(label, {})[scope] = dict(
                missing=missing, recovered=recovered, members=len(logs),
                recordedObjective=s["stages"][scope]["objective"], declaredObjective=statistics.median(logs.values()))
    worst = max((p["diff"] for p in proof), default=0.0)
    if worst > TOLERANCE:
        raise W.Refusal(f"recover: the port misses the driver by {worst} on a recorded row")
    result = dict(what="W46 G1: scope objectives with an UNMEASURED member, recovered through W44 G0's port",
                  portProof=dict(rows=len(proof), worstAbsDiff=worst, tolerance=TOLERANCE), points=out)
    (fit.G1 / "path").mkdir(parents=True, exist_ok=True)
    (fit.G1 / "path" / "recovered.json").write_text(json.dumps(result, indent=1) + "\n")
    for label, scopes in out.items():
        for scope, v in scopes.items():
            print(f"{label} {scope}: recorded {v['recordedObjective']} over {v['members'] - len(v['missing'])}, "
                  f"declared {v['declaredObjective']:.4f} over {v['members']}")
    print(f"port against the driver on {len(proof)} recorded rows: worst {worst:.2e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
