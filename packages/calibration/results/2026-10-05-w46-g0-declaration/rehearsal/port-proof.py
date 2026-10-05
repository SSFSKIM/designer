#!/usr/bin/env python3.12
"""W46 G0 (a): the cuts port, held to W45's landing cut on every DARK entry it shares (the brief's "tested
on d0219cd684bf"). W45 G2's `cut-025-w45-landing.json` read the dark 0.25 rows at the published
`d0219cd684bf` bytes; W46's cut of that generation against itself (`d0219-cuts.json.gz`) must equal it on
every dark entry outside W46's six referee scenes, which W46 withholds and W45 did not (so every
population that held them differs by exactly them: T1's partition label, X1's, E2's and C1's members).
The light entries are not compared: W45's light reference was c05, W46's is ebc3d9105a4a.

    python3.12 -B port-proof.py
"""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bindings as W  # noqa: E402

LANDING = W.RESULTS / "2026-10-03-w45-g2-landing/cuts/cut-025-w45-landing.json"
REFEREES = set(json.loads((HERE.parent / "referees/referees.json").read_text())["scenes"])


def dark(x) -> bool:
    s = x.get("cell") if isinstance(x, dict) else x
    return isinstance(s, str) and "-dark-standard" in s


def held(x) -> bool:
    s = x.get("cell") if isinstance(x, dict) else x
    return any(r in s for r in REFEREES)


def main() -> int:
    a = json.loads(LANDING.read_text())
    b = json.loads(gzip.open(HERE / "d0219-cuts.json.gz").read())
    compared, differ = 0, []
    for cut in ("L1", "X1", "C1", "E2", "M1", "M2"):
        for tier in ("webgpu", "css"):
            for k, av in a[cut][tier].items():
                bv = b[cut][tier].get(k)
                if isinstance(av, list):
                    ad = [x for x in av if dark(x) and not held(x)]
                    bd = [x for x in bv if dark(x)]
                    compared += len(ad)
                    if json.dumps(ad, sort_keys=True) != json.dumps(bd, sort_keys=True):
                        differ.append(f"{cut} {tier} {k}")
                elif isinstance(av, dict):
                    for kk, v in av.items():
                        if "-dark-standard" in kk and not held(kk):
                            compared += 1
                            if json.dumps(v, sort_keys=True) != json.dumps(bv.get(kk), sort_keys=True):
                                differ.append(f"{cut} {tier} {k} {kk}")
    ka = {(c["profile"], c["tier"], c["scene"]): c for c in a["T1"]["cells"]}
    t1 = 0
    for c in b["T1"]["cells"]:
        k = (c["profile"], c["tier"], c["scene"])
        if c["scheme"] != "dark":
            continue
        for f in ("native", "reference", "candidate", "fidelity", "change", "bar", "code", "stratum", "pose", "spanClass"):
            t1 += 1
            if ka[k].get(f) != c.get(f):
                differ.append(f"T1 {k} {f}")
        if c["scene"] in REFEREES:
            if (ka[k]["partition"], c["partition"]) != ("gate", "referee"):
                differ.append(f"T1 {k} partition {ka[k]['partition']} -> {c['partition']}")
        elif ka[k]["partition"] != c["partition"]:
            differ.append(f"T1 {k} partition")
    # Rows-derived per-bed-span C1 statistics pool the referee cells; they are excluded by construction above.
    print(f"port proof: {compared} dark row-cut entries and {t1} dark T1 fields compared with W45's landing cut; "
          f"{len(differ)} differ" + ("" if not differ else ": " + "; ".join(differ[:10])))
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
