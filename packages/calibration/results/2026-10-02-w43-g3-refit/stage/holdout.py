#!/usr/bin/env python3.12
"""W43 G3 (ii): the holdout's one reading, after the gate (charter clause 10 step 6).

Read once per tier into the same stages, last. Of the ruled rows only the TABLES state a holdout
population (the owner test's gated bed: active, calibration, validation AND holdout, no probe, no
recorded); M1, M2, C1, X1, L1, E2 and S1 are declared over non-holdout cells. So the holdout's
reading is the 0.5 tables per tier on the holdout cells, with the conditioning predicate on the
shape rows, beside two descriptive readings per cell (the level error |web - native| interiorMean
and the whole-cell ssimMean). Whatever it reads is recorded and never re-read; a miss goes to the
user (clause 10 step 6).

    python3.12 -B holdout.py      # writes holdout-reading.json and .txt beside this file
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cuts"))
import bed as B  # noqa: E402
import cuts as C  # noqa: E402

STAGES = [Path.home() / "vitrea-w43" / f"g3-stage-{s}" / "matrix.json" for s in ("light", "dark")]


def main() -> int:
    bed = B.load([str(p) for p in STAGES], "sealed", with_holdout=True)
    tables = C.owner_tables()
    out, lines = {}, ["W43 G3 (ii): the holdout's one reading (the 0.5 tables per tier, holdout cells)", ""]
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
                cells.append(dict(scene=r["key"]["sceneId"],
                                  levelError=None if None in (n, w) else w - n,
                                  ssimMean=B.value(r, "perceptual", "ssimMean")))
            verdict = ("UNMEASURED" if not rows else "MISS" if misses else
                       f"PASS, {len(no_row)} UNMEASURED (no row)" if no_row else "PASS")
            out[f"{profile} {renderer}"] = dict(table=twin["names"][tier], cells=len(rows), noRow=no_row,
                                                misses=misses, verdict=verdict, perCell=cells)
            lines.append(f"{profile.replace('apple-macos-27.0-', '')} {renderer}: {twin['names'][tier]}, "
                         f"{len(rows)} holdout cells, {len(misses)} misses -> {verdict}")
            for m in misses:
                lines.append(f"  {m['scene']:<48} {m['metric']:<20} {m['measured']} vs {m['bound']}")
            errors = [abs(c["levelError"]) for c in cells if c["levelError"] is not None]
            if errors:
                lines.append(f"  level |web - native| max {max(errors):.4f}, mean {sum(errors) / len(errors):.4f}")
    result = dict(what="W43 G3 (ii): the holdout's one reading", bed=bed.described(),
                  ownerTest=dict(sha256=tables["sha256"]), readings=out)
    (HERE / "holdout-reading.json").write_text(json.dumps(result, indent=1) + "\n")
    (HERE / "holdout-reading.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
