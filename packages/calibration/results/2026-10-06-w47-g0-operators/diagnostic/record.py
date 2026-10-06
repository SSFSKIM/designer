#!/usr/bin/env python3.12
"""W47 G0 (f): the depth-split diagnostic's record in the form part 1 pins (`declare.py`'s
`check_diagnostic`: `chosenForm` and `cells` [{cell, scale, R: {body, deep}}]), projected from the
committed reading (`reading.json`, written by `read.py`) and checked against it. Nothing is re-read
or re-rendered here: the record is a projection, and the criterion is recomputed from its R values.

    python3.12 -B record.py        (writes record.json; refuses to overwrite)
"""
from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
READING = HERE / "reading.json"
OUT = HERE / "record.json"
FORMS = ("body", "deep")


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"{OUT.name} exists; committed evidence is not overwritten")
    raw = READING.read_bytes()
    reading = json.loads(raw)
    cells = [dict(cell=r["scene"], scale=r["scale"], profile=r["profile"], spanCss=r["spanCss"],
                  E=r["E"], fine=r["fine"], R=r["R"],
                  weights={m: dict(pixels=v["pixels"], body=v["bodyWeightMean"], deep=v["deepWeightMean"])
                           for m, v in r["masks"].items()})
             for r in reading["rows"]]
    mean = {f: statistics.mean(c["R"][f] for c in cells) for f in FORMS}
    chosen = [f for f in FORMS if all(c["R"][f] >= 0.5 for c in cells)
              and mean[f] > mean[FORMS[1 - FORMS.index(f)]]]
    choice = chosen[0] if len(chosen) == 1 else "parent"
    if choice != reading["verdict"].lower():
        raise SystemExit(f"the criterion reads {choice}, the reading says {reading['verdict']}")
    body = dict(what="W47 G0 (f): the depth-split diagnostic's record (charter Design \"The ladders\", "
                     "the last item; Decision Log 3 as amended), projected from reading.json",
                reading=dict(path=READING.name, sha256=hashlib.sha256(raw).hexdigest()),
                criterion=reading["criterion"], definition=reading["definition"],
                chosenForm=choice, pooledMeanR=mean, cells=cells)
    with OUT.open("x") as f:
        f.write(json.dumps(body, indent=1) + "\n")
    print(f"{choice}: pooled R {mean}; {len(cells)} cells -> {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
