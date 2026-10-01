"""W43 G2 (1): W29's own second states, as pairs against their published 0.5 fixtures.

Every one of the 103 standard 0.5 cells that carried two states over W29's seven runs
(``raw-states.json``) gives one pair: a raw run in the minority state against the published fixture
(the plurality). The pair's true slider change is zero and its difference is the 0.5 side's own
run-to-run noise, the thing the declared bar is built from, so the declared bar must hold on every
one of these pairs on every metric that is a symmetric function of the pair. It is the rehearsal's
positive control, and its radial bands say where W29's two states differ (G2 (a), gap 2).

    python3.12 -B w29-state-pairs.py   # writes rehearsal/w29-state-pairs.json
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
W29_RUNS = Path.home() / "vitrea-w29-27-run"


def main() -> None:
    states = json.loads((HERE / "raw-states.json").read_text())["reference"]
    pairs = []
    for key, cell in sorted(states.items()):
        if len(cell["states"]) < 2:
            continue
        profile, scene = key.split("/")
        minority = next(run for run, sha in sorted(cell["runs"].items()) if sha != cell["fixtureSha256"])
        pairs.append(
            {
                "label": f"w29-state:{cell['pass']}/{minority}/{scene}",
                "subjectImage": str(W29_RUNS / cell["pass"] / minority / profile / f"{scene}.png"),
                "profileKey": profile,
                "sceneId": scene,
            }
        )
    (HERE / "rehearsal").mkdir(exist_ok=True)
    (HERE / "rehearsal" / "w29-state-pairs.json").write_text(json.dumps(pairs, indent=1) + "\n")
    print(f"{len(pairs)} W29 minority-state pairs")


if __name__ == "__main__":
    main()
