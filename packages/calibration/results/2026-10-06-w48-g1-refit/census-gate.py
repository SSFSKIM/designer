"""W48 G1: the classifying web census and the browser pin before every G1 browser launch.

G0's `census-gate.py` (W48's copy of W47's: the census of §5.201 §21 and the Playwright/Chromium pin)
is imported by path and run unchanged; only its log moves, so that G1's launches append to
`census.jsonl` beside this file and G0's committed census log is never written again (W46 G1's form).

    python3.12 -B census-gate.py <label>
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parent / "2026-10-06-w48-g0-declaration"
spec = importlib.util.spec_from_file_location("w48_g0_census_gate", G0 / "census-gate.py")
GATE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GATE)


def main() -> int:
    label = sys.argv[1] if len(sys.argv) > 1 else "unlabelled"
    observation = GATE.W.census().observe()
    pinned = GATE.pin()
    passes = observation["passes"] and pinned["ok"]
    refusals = observation["refusals"] + ([] if pinned["ok"] else ["browserNotPinned"])
    entry = dict(label=label, at=observation["recordedAt"], passes=passes, refusals=refusals,
                 refuse=observation["refuse"], pin=pinned,
                 annotate=[dict(pid=a["pid"], why=a["why"]) for a in observation["annotate"]])
    with (HERE / "census.jsonl").open("a") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    print(f"census {label}: {'passes' if passes else 'REFUSES'} "
          f"({len(observation['annotate'])} annotated, refusals {refusals}"
          + ("" if pinned["ok"] else f"; pin: {'; '.join(pinned['why'])}") + ")")
    return 0 if passes else 1


if __name__ == "__main__":
    sys.exit(main())
