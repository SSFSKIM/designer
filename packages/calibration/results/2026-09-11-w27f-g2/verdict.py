"""W27f G2: the declared bound against the read, and nothing else.

`declaration.md` fixed the bound before any capture of this gate ran. This file
evaluates it. It decides nothing it was not told to decide: the envelope's
endpoints and the pinned magnitudes below are transcribed from claims §5.131 §6,
the read comes from the runner's own `reading.json`, and the verdict is the
comparison. It fits nothing and it writes no canonical file.

    python verdict.py --scratch /tmp/w27f-g2 --out verdict.json

The exit status is 0 whether the bound holds or misses — a miss is a reading,
not a crash — and `verdict.json`'s `landing` field carries the answer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Claims §5.131 §6, transcribed. `s0` is the old textured-base composite, which
# cannot be re-measured at this head because the material that produced it is
# gone from the runtime; `s1` and `uh` are what this gate re-reads. Every value
# was verified against the committed G1 evidence JSONs before the declaration
# was written, not copied from the ledger's prose.
RECORD = {
    ("light", "checkerboard"): {
        "native": {"lum": 0.904655, "rim": 0.111642},
        "s0": {"de": 0.007735, "lum": 0.890113, "rim": 0.042743},
        "s1": {"de": 0.005438, "lum": 0.895571, "rim": 0.111347},
        "uh": {"de": 0.004662, "lum": 0.896252, "rim": 0.109977},
    },
    ("light", "photo"): {
        "native": {"lum": 0.893533, "rim": 0.084228},
        "s0": {"de": 0.019478, "lum": 0.873339, "rim": 0.047788},
        "s1": {"de": 0.018619, "lum": 0.880533, "rim": 0.114151},
        "uh": {"de": 0.009126, "lum": 0.886175, "rim": 0.109090},
    },
    ("dark", "checkerboard"): {
        "native": {"lum": 0.020698, "rim": 0.031990},
        "s0": {"de": 0.013765, "lum": 0.023909, "rim": 0.035140},
        "s1": {"de": 0.016702, "lum": 0.024857, "rim": 0.037864},
        "uh": {"de": 0.013059, "lum": 0.023673, "rim": 0.036194},
    },
    # No native fixture in apple-macos-26.5-1x-dark-standard. Declared unbounded
    # (declaration.md §1); its readings are reported and nothing is adopted.
    ("dark", "photo"): {
        "native": None,
        "s0": {"de": None, "lum": 0.021413, "rim": 0.032367},
        "s1": {"de": None, "lum": 0.021612, "rim": 0.033665},
        "uh": {"de": None, "lum": 0.021984, "rim": 0.033604},
    },
}

ARM_OF = {"s1": "sampled", "uh": "unsampled-hint", "u0": "unsampled-nohint"}
METRICS = ("de", "lum", "rim")
PRECISION = 6


def error(kind, value, native):
    """A reading's distance to native.

    ΔE is already a distance and carries no native ordinate of its own — the
    native overlay's ΔE against itself is zero by construction. Level and rim
    are absolute readings, so their distance is taken here.
    """
    if value is None:
        return None
    if kind == "de":
        return value
    if native is None:
        return None
    return abs(value - native)


def recorded_errors(cell, which):
    record = RECORD[cell]
    native = record["native"] or {}
    return {kind: error(kind, record[which][kind], native.get(kind)) for kind in METRICS}


def envelope(cell):
    """[min, max] of the two textured-base composites' distance to native, per metric.

    S0 and S1 are kept apart: this returns both endpoints and which configuration
    supplied each, so the bound can never be read as an average of the two.
    """
    s0, s1 = recorded_errors(cell, "s0"), recorded_errors(cell, "s1")
    out = {}
    for kind in METRICS:
        a, b = s0[kind], s1[kind]
        if a is None or b is None:
            out[kind] = None
            continue
        low, high = (a, b) if a <= b else (b, a)
        out[kind] = {"min": round(low, PRECISION), "max": round(high, PRECISION),
                     "upperFrom": "s0" if a >= b else "s1"}
    return out


def read_cell(reading, scene, arm):
    for row in reading["rows"]:
        if row["scene"] != scene:
            continue
        over = ((row.get("stackOverlay") or {}).get("readings", {}).get(arm) or {}).get("over")
        if over is None:
            return None
        return {"de": over.get("deltaEAgainstNative"),
                "lum": over.get("interiorLinearLuminanceMean"),
                "rim": over.get("rimLocalExcessMean")}
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scratch", type=Path, default=Path("/tmp/w27f-g2"))
    parser.add_argument("--out", type=Path, default=HERE / "verdict.json")
    args = parser.parse_args()

    holdout = json.loads((args.scratch / "holdout" / "reading.json").read_text())
    cells, stops = [], []

    for (scheme, stack), record in RECORD.items():
        scene = f"{stack}__glass-over-glass__rest"
        reading = holdout["schemes"][scheme]
        native = record["native"]
        env = envelope((scheme, stack))
        entry = {"scheme": scheme, "stack": stack, "scene": scene,
                 "nativeFixture": native is not None, "envelope": env, "arms": {}}

        for which in ("s1", "uh", "u0"):
            got = read_cell(reading, scene, ARM_OF[which])
            if got is None:
                stops.append(f"{scheme}/{stack}: the {ARM_OF[which]} arm produced no overlay reading")
                continue
            arm = {"read": {k: (None if got[k] is None else round(got[k], PRECISION))
                            for k in METRICS}}
            if which in ("s1", "uh"):
                arm["recorded"] = {k: round(record[which][k], PRECISION)
                                   if record[which][k] is not None else None for k in METRICS}
                arm["reproducesRecord"] = all(
                    arm["read"][k] == arm["recorded"][k] for k in METRICS
                    if arm["recorded"][k] is not None)
            if native is not None:
                errors, pins, envelope_ok = {}, {}, {}
                for kind in METRICS:
                    got_error = error(kind, got[kind], native.get(kind))
                    errors[kind] = None if got_error is None else round(got_error, PRECISION)
                    if which == "u0":
                        continue  # declared outside the bound (declaration.md §2)
                    pinned = recorded_errors((scheme, stack), which)[kind]
                    pins[kind] = {"pin": round(pinned, PRECISION),
                                  "holds": errors[kind] is not None
                                           and errors[kind] <= round(pinned, PRECISION)}
                    if not pins[kind]["holds"]:
                        stops.append(f"S2 {scheme}/{stack}/{which}/{kind}: read "
                                     f"{errors[kind]} exceeds the pin {round(pinned, PRECISION)}")
                    if which == "uh":
                        cap = env[kind]["max"]
                        envelope_ok[kind] = {"bound": cap, "from": env[kind]["upperFrom"],
                                             "holds": errors[kind] is not None
                                                      and errors[kind] <= cap}
                        if not envelope_ok[kind]["holds"]:
                            stops.append(f"S1 {scheme}/{stack}/{kind}: read {errors[kind]} "
                                         f"outside the envelope's upper endpoint {cap}")
                arm["errorToNative"] = errors
                if pins:
                    arm["clauseB"] = pins
                if envelope_ok:
                    arm["clauseA"] = envelope_ok
            entry["arms"][which] = arm
        cells.append(entry)

    verdict = {
        "gate": "W27f G2",
        "declaration": "packages/calibration/results/2026-09-11-w27f-g2/declaration.md",
        "source": "claims §5.131 §6 for every recorded value; the read is the runner's reading.json",
        "scratch": str(args.scratch),
        "cells": cells,
        "stops": stops,
        "landing": "the bound holds" if not stops else "the bound is missed; adopt nothing",
    }
    args.out.write_text(f"{json.dumps(verdict, indent=1)}\n")

    for cell in cells:
        head = f"{cell['scheme']:5s} {cell['stack']:12s}"
        if not cell["nativeFixture"]:
            print(f"{head}  no native fixture — unbounded, nothing adopted")
            continue
        for which in ("s1", "uh"):
            arm = cell["arms"].get(which)
            if arm is None:
                continue
            bits = []
            for kind in METRICS:
                e = arm["errorToNative"][kind]
                pin = arm["clauseB"][kind]
                mark = "ok" if pin["holds"] else "MISS"
                got = "   none  " if e is None else f"{e:.6f}"
                bits.append(f"{kind}={got} (pin {pin['pin']:.6f} {mark})")
            same = "reproduces" if arm.get("reproducesRecord") else "MOVED"
            print(f"{head} {which:3s} {same:10s} " + "  ".join(bits))
    print(f"\n{verdict['landing']}")
    for stop in stops:
        print(f"  {stop}")


if __name__ == "__main__":
    main()
