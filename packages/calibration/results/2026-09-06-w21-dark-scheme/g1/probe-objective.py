"""W21 G1 — the probe-grid body objective, before and after, on one definition.

The profile document's `measurement` block has to state an objective and an improvement on it, and
the wave's objective is the body under the declared geometry. This is that number, computed the
same way for every candidate so the document's before/after is one quantity: the mean absolute
difference between vitrea's body and the reference's over the probe's calibration and validation
cells, split thin / thick / switch the way claims §5.89 §6 splits it, and quoted with the tinted
capsules and the collapsed cell called out because the law reaches neither.

    probe-objective.py <label>=<read.json> ...
"""

import json
import sys

THIN = "rrect-sm"
SWITCH = "light-solid__rrect-sm__rest"

print(f"{'candidate':28s} {'all':>8s} {'n':>4s} {'thin':>8s} {'n':>4s} {'thick':>8s} {'n':>4s} "
      f"{'switch':>8s} {'tinted':>8s} {'n':>4s}")
for entry in sys.argv[1:]:
    label, path = entry.split("=", 1)
    rows = [row for row in json.load(open(path))["rows"] if "bodyWeb" in row]
    groups = {"all": [], "thin": [], "thick": [], "switch": [], "tinted": []}
    for row in rows:
        error = abs(row["bodyWeb"] - row["bodyNative"])
        if row.get("tint") is not None:
            groups["tinted"].append(error)
            continue
        if row["scene"] == SWITCH:
            groups["switch"].append(error)
            continue
        groups["all"].append(error)
        groups["thin" if row["component"] == THIN else "thick"].append(error)
    mean = lambda values: sum(values) / len(values) if values else float("nan")
    print(f"{label:28s} {mean(groups['all']):8.4f} {len(groups['all']):4d} "
          f"{mean(groups['thin']):8.4f} {len(groups['thin']):4d} "
          f"{mean(groups['thick']):8.4f} {len(groups['thick']):4d} "
          f"{mean(groups['switch']):8.4f} {mean(groups['tinted']):8.4f} "
          f"{len(groups['tinted']):4d}")
