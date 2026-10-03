#!/usr/bin/env python3.12
"""W45 G1 step 7: the holdout's tables, read once on the completed light stage (charter clause 7;
claims §5.206 §16). W43 G3 (ii)'s `stage/holdout.py`, ported to W45's cuts: of the ruled rows only
the TABLES state a holdout population (active, calibration, validation AND holdout, no probe, no
recorded), so the holdout's table reading is the 0.5 tables per tier on the holdout cells, with the
conditioning predicate on the shape rows, beside the level error and ssimMean per cell; and each
cell beside c05's reading of it (W43 G3 (ii)'s `holdout-reading.json`, the published c05 rows).
Recorded, never re-read.

    python3.12 -B holdout.py --dark DARK_MATRIX      writes holdout-reading.json and .txt here
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
CUTS = CAL / "results" / "2026-10-03-w45-g0-operator" / "cuts"
sys.path.insert(0, str(CUTS))
import bed as B  # noqa: E402
import cuts as C  # noqa: E402

STAGE = Path.home() / "vitrea-w45" / "g1-stage-light" / "matrix.json"
W43 = CAL / "results" / "2026-10-02-w43-g3-refit" / "stage" / "holdout-reading.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dark", type=Path, required=True)
    args = ap.parse_args()
    bed = B.load([str(STAGE), str(args.dark)], "sealed", with_holdout=True)
    c05 = json.loads(W43.read_text())["readings"]
    tables = C.owner_tables()
    out, lines = {}, ["W45 G1 step 7: the holdout's one reading (the 0.5 tables per tier, holdout cells), "
                      "beside c05's (W43 G3 (ii))", ""]
    for profile in B.PROFILES:
        twin = tables["profiles"][B.counterpart_05(profile)]
        members = [sid for sid in B.SCENES.declared(profile)
                   if B.SCENES.role[sid] == "holdout" and not B.SCENES.inactive(sid)]
        for renderer, tier in B.TIERS.items():
            by_scene = {r["key"]["sceneId"]: r for r in bed.rows if r["key"]["profileKey"] == profile
                        and r["key"]["web"]["renderer"] == renderer and r["fixtureSet"] == "holdout"}
            no_row = sorted(sid for sid in members if sid not in by_scene)
            rows = [by_scene[sid] for sid in members if sid in by_scene]
            misses, cells = [], []
            for axis, metric, comparison, threshold in twin[tier]:
                applicable = ([r for r in rows if r.get("shape") is not None and C.well_conditioned(r)]
                              if axis == "shape" else rows)
                for r in applicable:
                    measured = B.value(r, axis, metric)
                    ok = measured is not None and (measured >= threshold if comparison == "≥"
                                                   else measured <= threshold)
                    if not ok:
                        misses.append(dict(scene=r["key"]["sceneId"], metric=metric, measured=measured,
                                           bound=f"{comparison} {threshold}"))
            for r in rows:
                n, w = B.value(r, "material", "interiorMeanNative"), B.value(r, "material", "interiorMeanWeb")
                cells.append(dict(scene=r["key"]["sceneId"], levelError=None if None in (n, w) else w - n,
                                  ssimMean=B.value(r, "perceptual", "ssimMean")))
            verdict = ("UNMEASURED" if not rows else "MISS" if misses else
                       f"PASS, {len(no_row)} UNMEASURED (no row)" if no_row else "PASS")
            key = f"{profile} {renderer}"
            before = {(m["scene"], m["metric"]) for m in c05.get(key, {}).get("misses", [])}
            new = [m for m in misses if (m["scene"], m["metric"]) not in before]
            closed = sorted(before - {(m["scene"], m["metric"]) for m in misses})
            out[key] = dict(table=twin["names"][tier], cells=len(rows), noRow=no_row, misses=misses, verdict=verdict,
                            c05Verdict=c05.get(key, {}).get("verdict"), newMisses=new, closedMisses=closed,
                            perCell=cells)
            lines.append(f"{profile.replace('apple-macos-27.0-', '')} {renderer}: {twin['names'][tier]}, "
                         f"{len(rows)} holdout cells, {len(misses)} misses -> {verdict} (c05: "
                         f"{c05.get(key, {}).get('verdict')}); new {len(new)}, closed {len(closed)}")
            for m in misses:
                lines.append(f"  {'NEW ' if m in new else '    '}{m['scene']:<48} {m['metric']:<20} {m['measured']} vs {m['bound']}")
            for s, metric in closed:
                lines.append(f"  closed {s} {metric}")
            errors = [abs(c["levelError"]) for c in cells if c["levelError"] is not None]
            if errors:
                lines.append(f"  level |web - native| max {max(errors):.4f}, mean {sum(errors) / len(errors):.4f}")
    result = dict(what="W45 G1 step 7: the holdout's one reading", bed=bed.described(),
                  ownerTest=dict(sha256=tables["sha256"]), c05Reading=str(W43.relative_to(CAL)), readings=out)
    (HERE / "holdout-reading.json").write_text(json.dumps(result, indent=1) + "\n")
    (HERE / "holdout-reading.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
