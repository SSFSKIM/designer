"""W45 G0: the classifying web census before every browser launch (§5.201 §21's ruling).

Reads W43 G3 (ii)'s `stage/census.py` by path, appends the observation to `census.jsonl` beside
this file with the label of the launch it gates, and exits 1 when the census refuses — so a shell
caller gates the launch on this command's own exit code.

    python3.12 -B census-gate.py <label>
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
_spec = importlib.util.spec_from_file_location(
    "w43_census", CAL / "results/2026-10-02-w43-g3-refit/stage/census.py")
census = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(census)


def main() -> int:
    label = sys.argv[1] if len(sys.argv) > 1 else "unlabelled"
    observation = census.observe()
    entry = dict(label=label, at=observation["recordedAt"], passes=observation["passes"],
                 refusals=observation["refusals"], refuse=observation["refuse"],
                 annotate=[dict(pid=a["pid"], why=a["why"]) for a in observation["annotate"]])
    with (HERE / "census.jsonl").open("a") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    print(f"census {label}: {'passes' if observation['passes'] else 'REFUSES'} "
          f"({len(observation['annotate'])} annotated, refusals {observation['refusals']})")
    return 0 if observation["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
