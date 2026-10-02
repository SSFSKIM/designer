#!/usr/bin/env python3.12
"""W44 G0 (f), review closure: L3's between-rung evidence, recomputed beside `results.json`.

`results.json` was written by `read.py` at the SHA-256 its `tools` field records, whose L3
adjacency sorted the (share, width) pairs lexicographically, so two of its steps moved both leaves
and two share-neighbour steps were missing (the independent review of (f)-(g), P2). The decision
quantities it records (flat per base, non-flat range, struck, the 1x inert proof) never used that
adjacency and stand. `read.py` now steps within each one-leaf ladder; this writes the corrected L3
comparisons beside the recorded file, which stays as it is (part 2 pins it).

    python3.12 -B l3-adjacency.py      writes l3-adjacency.json (refuses to overwrite)
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ladder as Lm  # noqa: E402
import read as R  # noqa: E402

OUT = HERE / "l3-adjacency.json"


def main() -> int:
    if OUT.exists():
        raise SystemExit("l3-adjacency.json exists; a recorded reading is never overwritten")
    lad = next(l for l in R.PROTOCOL["ladders"] if l["id"] == "L3")
    bars = R.t1.load_bars()
    P2 = R.PROTOCOL["profiles"][0]
    acting = [sid for sid in R.FINE if R.matches(lad["actsOn"], P2, sid)]
    out = {}
    for base, values in lad["readAt"].items():
        labels = [R.PROTOCOL["bases"][base]["label"]] + [
            r["label"] for r in Lm.rungs() if r["ladder"] == "L3" and r["base"] == base]
        members = [R.Rung(next(r for r in Lm.unique_rungs() if r["label"] == l)) for l in labels]
        values_all = [R._base_value(lad, base)] + list(values)
        out[base] = R.adjacency(lad, values_all, members, acting, bars, P2)
    recorded = json.loads((HERE / "results.json").read_bytes())
    body = dict(schema="w44-l3-adjacency-1",
                supersedes="results.json ladders.L3.bases.*.adjacent (a lexicographic sort of the pairs)",
                resultsSha256=hashlib.sha256((HERE / "results.json").read_bytes()).hexdigest(),
                recordedReadPy=recorded["tools"]["read.py"],
                readPy=hashlib.sha256((HERE / "read.py").read_bytes()).hexdigest(),
                adjacent=out)
    OUT.write_text(json.dumps(body, indent=1) + "\n")
    for base, steps in out.items():
        for st in steps:
            moved = [s for s, c in st["cells"].items() if not c["withinBar"]]
            print(f"{base} {st['leaf']:<24} {str(st['between']):<22} moves beyond the bar on {len(moved)} "
                  f"of {len(st['cells'])} acting cells; pixel-identical on "
                  f"{sum(c['pixelIdentical'] for c in st['cells'].values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
