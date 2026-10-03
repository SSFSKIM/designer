#!/usr/bin/env python3.12
"""W45 G0 (b): objectives with an UNMEASURED member, recovered beside the record — W44 G1's
`recover.py` (the review of W44 G1 steps 0-2, P2) ported for W45's scopes (X58). W44's committed
copy is untouched. Writes G1's `fit/path/recovered.json`; the summaries stay as recorded.

    python3.12 -B recover.py

A render can write a cell's capture and then fail the cell on an axis T1 does not read (W44 G1 met
"a 0.00px contour sampled 512 times at sigma=3 carries no curvature"), so the row is absent and a
scope objective recorded over it is a median over fewer than the scope's F u C u P cells — not the
declared statistic. T1's web reading is the luminance SD of the WEB capture over the NATIVE
silhouette (`cli/measure.ts`), which W44 G0's port (`port/interior.py`, shared by path and pinned)
reproduces to 2.3e-10. For every point whose summary lacks a member of a scope it rendered, this
reads the missing cell's web SD off the point's scratch capture through the port (the capture's
cell JSON must name the point's declaration), proves the port reproduces the driver's recorded
`interiorStdDevWeb` on every row that render DID record (to 1e-6), and records the scope objective
over all its members. `search.decide` ranks such a point on that value or not at all.
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
PROFILE = fit.PROFILE[2]
FIXTURES = W.ROOT / "apps/reference-apple/fixtures"
TOLERANCE = 1e-6


def port():
    W.require_shared()
    return W.load_module("w45_port_interior", W.PORT / "interior.py")


def capture_dir(label: str, sid: str) -> Path | None:
    """The scratch scope directory of `label` whose captures hold `sid`, or None (never rendered)."""
    root = W.refuse_w44_path(fit.SCRATCH / label, "the scratch render")
    for d in sorted(root.iterdir()) if root.exists() else []:
        if d.name != "x48" and (d / "web-captures" / PROFILE / sid / "cell__webgpu.json").exists():
            return d
    return None


def web_sd(P, B, label: str, sid: str, scope_dir: Path) -> float:
    folder = scope_dir / "web-captures" / PROFILE / sid
    meta = json.loads((folder / "cell__webgpu.json").read_text())
    want = str((fit.G1 / "candidates" / label / "candidate.json").relative_to(W.ROOT))
    if f"candidateDocument={want}" not in meta["capturePath"]:
        raise W.Refusal(f"{label} {sid}: the capture names {meta['capturePath'][-200:]}, not {want}")
    native = P.read(FIXTURES / PROFILE / f"{sid}.png")
    background = P.read(FIXTURES / "backgrounds" / f"{B.SCENES.by_id[sid]['background']}@2x.png")
    mask = P.native_interior(native, background, B.SCENES.component(sid), B.SCENES.canvas, 2)
    return P.level(P.read(folder / f"{sid}__webgpu.png"), mask)["stdDev"]


def main() -> int:
    B, t1 = fit.cuts()
    P = port()
    c05 = {r["key"]["sceneId"]: r for r in B.load_published(W.C05["light"]).rows
           if r["key"]["profileKey"] == PROFILE and r["key"]["web"]["renderer"] == "webgpu"}
    out, proof = {}, []
    for f in sorted((fit.G1 / "candidates").glob("*/summary.json")):
        s = json.loads(f.read_text())
        label = s["label"]
        proved = False
        # Every scope the search reads, family scopes and stages (a stage's union spans the label's
        # scope directories); a scope is recovered only where each missing member WAS rendered.
        for scope in fit.ALL_SCOPES:
            if s["stages"].get(scope, {}).get("objective") is None:
                continue
            members = [m for m in fit.scenes_for(scope) if t1.stratum(m) in t1.SELECTION_STRATA]
            missing = [m for m in members if m not in s["cells"]]
            where = {sid: capture_dir(label, sid) for sid in missing}
            if not missing or any(d is None for d in where.values()):
                continue
            if not proved:
                for scope_dir in sorted({d for d in (fit.SCRATCH / label).iterdir() if d.name != "x48"
                                         and (d / "matrix.json").exists()}):
                    rows = json.loads((scope_dir / "matrix.json").read_bytes())["cells"]
                    for row in rows:
                        sid = row["key"]["sceneId"]
                        got = web_sd(P, B, label, sid, scope_dir)
                        driver = B.value(row, "material", "interiorStdDevWeb")
                        proof.append(dict(label=label, scope=scope_dir.name, scene=sid, port=got, driver=driver,
                                          diff=abs(got - driver)))
                proved = True
            logs = {sid: abs(math.log(c["k"] / c["n"])) for sid, c in s["cells"].items() if sid in members}
            recovered = {}
            for sid in missing:
                k = web_sd(P, B, label, sid, where[sid])
                n = B.value(c05[sid], "material", "interiorStdDevNative")
                recovered[sid] = dict(native=n, web=k, ratio=k / n)
                logs[sid] = abs(math.log(k / n))
            out.setdefault(label, {})[scope] = dict(
                missing=missing, recovered=recovered, members=len(logs),
                recordedObjective=s["stages"][scope]["objective"], declaredObjective=statistics.median(logs.values()))
    worst = max((p["diff"] for p in proof), default=0.0)
    if worst > TOLERANCE:
        raise W.Refusal(f"recover: the port misses the driver by {worst} on a recorded row")
    result = dict(what="W45 G1: scope objectives with an UNMEASURED member, recovered through W44 G0's port",
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
