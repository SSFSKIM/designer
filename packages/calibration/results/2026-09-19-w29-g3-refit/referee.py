#!/usr/bin/env python3
"""W29 G3 — the declared bounds, evaluated over a candidate 27 matrix.

    python3 referee.py <matrix.json> [--cells]

The authoritative gate is `test/adopted-thresholds.test.ts` run over the
canonical matrix; this is the referee a FIT needs, which is a different job. A
vitest case stops at its first failing cell, and a fit loop has to see every
miss at once and watch the worst cell move. So this evaluates the same rows over
a scratch matrix and prints the whole distribution.

**It holds no copy of a threshold.** The numbers are parsed out of
`adopted-thresholds.test.ts` itself — the one place in the repository they live
(that file's own opening paragraph) — so a referee that disagreed with the gate
about what was declared is not expressible. It parses two things: the
`GateRow[]` table constants, and the `DECLARED_27_PROFILES` entries that say
which table each 27 profile and tier is gated by.

The conditioning predicate is the gate's own, restated here for the shape rows
only, because a shape row over an unresolvable silhouette is not a fidelity
reading in either file.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE.parent.parent / "test" / "adopted-thresholds.test.ts"
WELL_CONDITIONED_AREA_RATIO = 0.95

ROW = re.compile(
    r'\[\s*"(?P<axis>shape|perceptual)"\s*,\s*(?:/\*[^*]*\*/\s*)?"(?P<metric>\w+)"\s*,'
    r'\s*(?:/\*[^*]*\*/\s*)?"(?P<cmp>[≥≤])"\s*,\s*(?P<value>[-\d.]+)\s*\]'
)
TABLE = re.compile(
    r"const (?P<name>[A-Z_0-9]+): readonly GateRow\[\] = \[(?P<body>.*?)\n\];", re.S
)
ALIAS = re.compile(r"^const (?P<name>[A-Z_0-9]+) = (?P<of>[A-Z_0-9]+);$", re.M)
ENTRY = re.compile(
    r'profileKey: "(?P<key>apple-macos-27\.0-[^"]+)".*?'
    r'names:\s*\{\s*texture:\s*"(?P<texture>\w+)",\s*dom:\s*"(?P<dom>\w+)",?\s*\}',
    re.S,
)


def declared() -> tuple[dict[str, list[tuple]], dict[str, dict[str, str]]]:
    source = GATE.read_text()
    tables = {
        m.group("name"): [
            (r.group("axis"), r.group("metric"), r.group("cmp"), float(r.group("value")))
            for r in ROW.finditer(m.group("body"))
        ]
        for m in TABLE.finditer(source)
    }
    # The 27 tables are aliases of their 26.5 twins (Decision Log 4 (a)), so an
    # alias resolves to the rows it names rather than to a table of its own.
    for m in ALIAS.finditer(source):
        if m.group("of") in tables:
            tables[m.group("name")] = tables[m.group("of")]
    block = source[source.index("const DECLARED_27_PROFILES") :]
    block = block[: block.index("\n];")]
    profiles = {
        m.group("key"): {"texture": m.group("texture"), "dom": m.group("dom")}
        for m in ENTRY.finditer(block)
    }
    if not profiles:
        raise SystemExit("referee: parsed no 27 profile out of the gate file")
    return tables, profiles


def value(cell: dict, axis: str, metric: str) -> float | None:
    entry = (cell.get(axis) or {}).get(metric)
    return entry["value"] if isinstance(entry, dict) else None


def well_conditioned(cell: dict) -> bool:
    if "shape" not in cell or cell["shape"] is None:
        return True
    at = lambda m: value(cell, "shape", m)
    floor = WELL_CONDITIONED_AREA_RATIO * at("componentRegionArea")
    return (
        at("silhouetteAreaNative") >= floor
        and at("silhouetteAreaWeb") >= floor
        and at("silhouetteBodiesNative") <= at("componentRegionBodies")
        and at("silhouetteBodiesWeb") <= at("componentRegionBodies")
    )


def main() -> int:
    matrix_path = Path(sys.argv[1])
    show_cells = "--cells" in sys.argv
    matrix = json.loads(matrix_path.read_text())
    tables, profiles = declared()

    cells = [c for c in matrix["cells"] if c["key"]["profileKey"].startswith("apple-macos-27.0-")]
    cells = [c for c in cells if c.get("fixtureSet") != "probe" and c.get("state") != "inactive"]
    if not cells:
        raise SystemExit(f"referee: {matrix_path} carries no active 27 row")

    missed_total = 0
    for key in sorted(profiles):
        for tier, renderer in (("texture", "webgpu"), ("dom", "css")):
            table = tables[profiles[key][tier]]
            mine = [
                c
                for c in cells
                if c["key"]["profileKey"] == key and c["key"]["web"]["renderer"] == renderer
            ]
            if not mine:
                continue
            print(f"\n{key} / {tier} ({len(mine)} cells, table {profiles[key][tier]})")
            for axis, metric, cmp, bound in table:
                pool = [c for c in mine if axis != "shape" or ("shape" in c and c["shape"])]
                if axis == "shape":
                    pool = [c for c in pool if well_conditioned(c)]
                readings = [(value(c, axis, metric), c) for c in pool]
                readings = [(v, c) for v, c in readings if v is not None]
                if not readings:
                    print(f"  {metric:<22} {cmp} {bound:<8} — no cell carries it")
                    continue
                values = [v for v, _ in readings]
                worst = min(values) if cmp == "≥" else max(values)
                misses = [
                    (v, c) for v, c in readings if (v < bound if cmp == "≥" else v > bound)
                ]
                missed_total += len(misses)
                flag = "MISS" if misses else "ok  "
                print(
                    f"  {metric:<22} {cmp} {bound:<8} worst {worst:.5f}"
                    f"  n={len(readings)}  {flag} {len(misses)}"
                )
                if show_cells and misses:
                    for v, c in sorted(misses, key=lambda p: -abs(p[0] - bound)):
                        print(
                            f"      {c['fixtureSet']:<11} {c['key']['sceneId']:<44} {v:.5f}"
                        )
    print(f"\ntotal missed cell-rows: {missed_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
