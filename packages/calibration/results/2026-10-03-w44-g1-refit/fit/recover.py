#!/usr/bin/env python3.12
"""W44 G1 step 2, a correction beside the record (the review of G1 steps 0-2, P2): the move
objectives of the four move-1 points that had one UNMEASURED objective member.

On four renders (m1b-s14, m1c-0.25-3, m1c-0.25-4, m1c-0.5-6) the driver wrote the capture of
`checkerboard-lc16__rrect-md__rest` and then failed the cell on its shape axis ("a 0.00px contour
sampled 512 times at σ=3 carries no curvature"), so the row is absent and the recorded objective
of each point is a median over 26 of move 1's 27 F u C u P cells. The declared objective is over
the move's cells, so those four values are not the declared statistic. The interior statistic
does not depend on the contour: T1's web reading is the luminance SD of the WEB capture over the
NATIVE silhouette (`cli/measure.ts`), which G0's port (`port/interior.py`) reproduces to 2.3e-10.

This reads each missing cell's web reading off its scratch capture through the port (the capture's
cell JSON must name the candidate's declaration), proves the same port reproduces the driver's
recorded `interiorStdDevWeb` on every cell those four renders DID record (to 1e-6), recomputes the
four objectives over all 27 members, and re-runs part 2's move-1 decision with them. The recorded
summaries and `path/move1.json` stay as they were; this writes `path/recovered.json` and
`path/move1-recovered.json` beside them.

    python3.12 -B recover.py
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE / "cuts"))
sys.path.insert(0, str(HERE))
import bed as B  # noqa: E402
import t1  # noqa: E402
import fit  # noqa: E402

sys.path.insert(0, str(B.G0 / "port"))
import interior as P  # noqa: E402

PROFILE = fit.PROFILE[2]
FIXTURES = B.ROOT / "apps/reference-apple/fixtures"
MOVE = "move1"
TOLERANCE = 1e-6


def web_sd(label: str, sid: str, scope_dir: Path) -> float:
    folder = scope_dir / "web-captures" / PROFILE / sid
    meta = json.loads((folder / "cell__webgpu.json").read_text())
    want = str((HERE / "candidates" / label / "candidate.json").relative_to(B.ROOT))
    if f"candidateDocument={want}" not in meta["capturePath"]:
        raise SystemExit(f"{label} {sid}: the capture names {meta['capturePath'][-200:]}, not {want}")
    native = P.read(FIXTURES / PROFILE / f"{sid}.png")
    background = P.read(FIXTURES / "backgrounds" / f"{B.SCENES.by_id[sid]['background']}@2x.png")
    mask = P.native_interior(native, background, B.SCENES.component(sid), B.SCENES.canvas, 2)
    return P.level(P.read(folder / f"{sid}__webgpu.png"), mask)["stdDev"]


def main() -> int:
    members = [s for s in fit.scenes_for(MOVE) if t1.stratum(s) in t1.SELECTION_STRATA]
    c05 = {r["key"]["sceneId"]: r for r in B.load_published("6d18c059eb42").rows
           if r["key"]["profileKey"] == PROFILE and r["key"]["web"]["renderer"] == "webgpu"}
    out, proof = {}, []
    for f in sorted((HERE / "candidates").glob("*/summary.json")):
        s = json.loads(f.read_text())
        if s["move"] != MOVE:
            continue
        missing = [m for m in members if m not in s["cells"]]
        if not missing:
            continue
        label = s["label"]
        scope_dir = fit.SCRATCH / label / MOVE
        rows = {r["key"]["sceneId"]: r for r in json.loads((scope_dir / "matrix.json").read_bytes())["cells"]}
        for sid, row in rows.items():          # the port against the driver on this render's rows
            got = web_sd(label, sid, scope_dir)
            proof.append(dict(label=label, scene=sid, port=got, driver=B.value(row, "material", "interiorStdDevWeb"),
                              diff=abs(got - B.value(row, "material", "interiorStdDevWeb"))))
        logs = {sid: abs(math.log(c["k"] / c["n"])) for sid, c in s["cells"].items() if sid in members}
        recovered = {}
        for sid in missing:
            k = web_sd(label, sid, scope_dir)
            n = B.value(c05[sid], "material", "interiorStdDevNative")
            recovered[sid] = dict(native=n, web=k, ratio=k / n)
            logs[sid] = abs(math.log(k / n))
        out[label] = dict(missing=missing, recovered=recovered, members=len(logs),
                          recordedObjective=s["moves"][MOVE]["objective"],
                          declaredObjective=statistics.median(logs.values()))
    worst = max(p["diff"] for p in proof)
    if worst > TOLERANCE:
        raise SystemExit(f"recover: the port misses the driver by {worst} on a recorded row")
    # Part 2's move-1 decision again, with the four objectives over all 27 members.
    record = json.loads((HERE / "path" / f"{MOVE}.json").read_text())
    rows = [dict(r, objective=out[r["label"]]["declaredObjective"]) if r["label"] in out else r
            for fam in record["families"].values() for r in fam]
    best = min(rows, key=lambda r: r["objective"])
    ties = [r for r in rows if r["objective"] - best["objective"] <= best["tie"]]
    landed = min(ties, key=lambda r: (r["leaves"], r["objective"]))
    again = dict(record, landed=landed["label"],
                 families={fam: [dict(r, objective=out[r["label"]]["declaredObjective"]) if r["label"] in out else r
                                 for r in rows_] for fam, rows_ in record["families"].items()},
                 correction="the four points with an UNMEASURED member read over all 27 (recover.py)")
    (HERE / "path" / f"{MOVE}-recovered.json").write_text(json.dumps(again, indent=1) + "\n")
    result = dict(what="W44 G1 step 2: the four move-1 objectives with an UNMEASURED member, recovered through G0's port",
                  portProof=dict(rows=len(proof), worstAbsDiff=worst, tolerance=TOLERANCE),
                  points=out, landedBefore=record["landed"], landedAfter=landed["label"],
                  decisionUnchanged=landed["label"] == record["landed"])
    (HERE / "path" / "recovered.json").write_text(json.dumps(result, indent=1) + "\n")
    for label, v in out.items():
        print(f"{label}: recorded {v['recordedObjective']:.4f} over 26, declared {v['declaredObjective']:.4f} over "
              f"{v['members']}; recovered {', '.join(f'{s} web {r['web']:.4f} (x{r['ratio']:.2f})' for s, r in v['recovered'].items())}")
    print(f"port against the driver on {len(proof)} recorded rows: worst {worst:.2e}")
    print(f"move 1 lands {landed['label']} (recorded {record['landed']}): "
          f"{'unchanged' if result['decisionUnchanged'] else 'CHANGED'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
