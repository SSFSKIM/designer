#!/usr/bin/env python3.12
"""W45 G1 step 2: the move objective per rung, from the stage records `search.py` wrote (claims
§5.206). Reads only; writes `path/rungs.txt` and `path/rungs.json`.

For each lineage (c05, joint), each stage and each component, every point in the order the sweep
asked for it, with the component's objective on its own scope (`search.scope_objective`: the
recorded value, or the recovered one for a point whose render lost a member; never a partial
median), the label that measures it where a content twin does, and what it moves beyond the
component's starting point. The stage's decision follows each stage.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "2026-10-03-w45-g0-operator" / "fit"))
import fit  # noqa: E402
import search  # noqa: E402


def moved(ov: dict, base: dict) -> str:
    out = []
    for slot, leaves in sorted(ov.items()):
        for leaf, v in sorted(leaves.items()):
            if base.get(slot, {}).get(leaf) != v:
                out.append(f"{'receded ' if slot == 'receded.light' else ''}{leaf}={v:g}")
    return ", ".join(out) or "(the starting point)"


def main() -> int:
    lines, out = [], {}
    runs = [("", HERE / "path")]
    if (HERE / "path" / "factorial" / "c05" / "stage2.json").exists():
        # The continuation the parent ruled on 2026-10-04 (factorial.py): its records beside the
        # coordinate run's, under path/factorial/, appended after them.
        runs.append(("continuation ", HERE / "path" / "factorial"))
    for prefix, root in runs:
        for start in fit.STARTS:
            for stage in ("stage1", "stage2"):
                rec = json.loads((root / start / f"{stage}.json").read_text())
                lines.append(f"== {prefix}{start} {stage}: base {rec['base']}")
                comps = []
                for comp in rec["components"]:
                    lines.append(f"  -- component {comp['family']} on {comp['scope']} ({len(comp['points'])} points), "
                                 f"best {comp['best']}")
                    rows = []
                    for label in comp["points"]:
                        ov = search.base_overrides(label)
                        obj = search.scope_objective(label, comp["scope"])
                        by = fit.measured_label(label)
                        rows.append(dict(label=label, objective=obj, measuredBy=by, moves=moved(ov, comp["from"])))
                        lines.append(f"    {label:<58} {obj:.4f}{'  (measured by ' + by + ')' if by != label else ''}"
                                     f"  [{moved(ov, comp['from'])}]")
                    comps.append(dict(family=comp["family"], scope=comp["scope"], best=comp["best"], rows=rows))
                landed = next(p for p in rec["points"] if p["label"] == rec["landed"])
                lines.append(f"  => landed {rec['landed']} at {landed['objective']:.4f} ({rec['within']}); {rec['how']}")
                out[f"{prefix}{start}/{stage}"] = dict(base=rec["base"], components=comps, landed=rec["landed"],
                                               objective=landed["objective"], within=rec["within"], how=rec["how"])
    (HERE / "path" / "rungs.txt").write_text("\n".join(lines) + "\n")
    (HERE / "path" / "rungs.json").write_text(json.dumps(out, indent=1) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
