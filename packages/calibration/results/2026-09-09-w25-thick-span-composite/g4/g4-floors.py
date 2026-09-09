"""W25 G4 — the regression floors, re-read on the LANDED bed beside the 0.13.0 one.

W25 G3's script on the canonical rebuild. `REGRESSION_FLOORS` in `test/adopted-thresholds.test.ts` is the
list of cells the frozen bed cannot meet, each pinned at what the bed measured with a floor one
`FLOOR_EPSILON` beyond it. A floor comes off by FIX and is re-pinned only by the user (the fidelity
discipline), so this reads every one and says which way it moved; it never writes the file.

The fourteen floors are all `checkerboard` rows on thick surfaces or on the nested pane, which is
the family a thick-span change reaches. None moved at G3b's dry run; this is the same reading taken
on the bed that ships, and a breach here stops the landing rather than being pinned.

    g4-floors.py <before matrix.json> <after matrix.json> > g4-floors.txt
"""

import json
import os
import re
import sys

TEST = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "test", "adopted-thresholds.test.ts"))
TIERS = {"texture": "webgpu", "dom": "css"}


def floors():
    """The `REGRESSION_FLOORS` table, parsed out of the test that owns it."""
    source = open(TEST).read()
    start = source.index("const REGRESSION_FLOORS")
    end = source.index("\n};", start)
    body = source[start:end]
    out = {}
    for match in re.finditer(
        r'"([^"]+?)\s*::\s*([A-Za-z0-9]+)"\s*:\s*\{\s*measured:\s*([-0-9.]+),\s*'
        r'floor:\s*([-0-9.]+)\s*\}', body
    ):
        out[(match.group(1), match.group(2))] = (float(match.group(3)), float(match.group(4)))
    return out


def value(cell, metric):
    for axis in ("perceptual", "shape", "material", "shadow", "coherence"):
        node = cell.get(axis)
        if isinstance(node, dict) and metric in node:
            entry = node[metric]
            return entry.get("value") if isinstance(entry, dict) else entry
    return None


def index(path):
    out = {}
    for cell in json.load(open(path))["cells"]:
        key = (cell["tier"], cell["fixtureSet"], cell["key"]["sceneId"], cell["key"]["profileKey"])
        out[" / ".join(key)] = cell
    return out


def main():
    before, after = index(sys.argv[1]), index(sys.argv[2])
    table = floors()
    print("W25 G4 — the regression floors, 0.13.0 bed -> the landed bed")
    print("=" * 116)
    print(f"{'cell':82s} {'metric':22s} {'floor':>9s} {'before':>9s} {'after':>9s} {'verdict':>9s}")
    breached = 0
    read = 0
    for (cell, metric), (measured, floor) in sorted(table.items()):
        b, a = before.get(cell), after.get(cell)
        if a is None:
            print(f"{cell:82s} {metric:22s} {floor:9.5f} {'—':>9s} {'—':>9s} {'absent':>9s}")
            continue
        vb = value(b, metric) if b is not None else None
        va = value(a, metric)
        if va is None:
            print(f"{cell:82s} {metric:22s} {floor:9.5f} {'—':>9s} {'—':>9s} {'no read':>9s}")
            continue
        read += 1
        # `contourDistance*` are `≤` metrics and their floors are pinned ABOVE the measurement;
        # every other floor in this table is a lower bound pinned below it.
        upper = metric.startswith("contourDistance")
        ok = va <= floor if upper else va >= floor
        if not ok:
            breached += 1
        print(f"{cell:82s} {metric:22s} {floor:9.5f} "
              f"{(vb if vb is not None else float('nan')):9.5f} {va:9.5f} "
              f"{'ok' if ok else 'BREACHED':>9s}  "
              f"{'<=' if upper else '>='} pinned at {measured:.5f}")
    print()
    print(f"{read} floors read, {breached} breached")


if __name__ == "__main__":
    main()
