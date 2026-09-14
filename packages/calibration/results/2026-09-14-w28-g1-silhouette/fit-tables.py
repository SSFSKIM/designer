"""G1d's equal-cell body objective and 9x control refusal, with W28 admission locks."""
from pathlib import Path
from statistics import mean
import json
import math
import sys

HERE = Path(__file__).resolve().parent
load = lambda path: json.loads(path.read_text())
partition = load(HERE / "partition.json")
bed = load(HERE.parent / "2026-09-11-w27c-g1b/checking-bed.json")
base_id = lambda scene: "__".join(scene.split("__")[:2])
denied = {base_id(scene) for scene in next(g for g in bed["groups"] if g["id"] == "D")["scenes"]}
denied.add("checkerboard__rrect-ml")
holdout = set(partition["holdout"])
baseline = {f'{r["profile"]}/{r["scene"]}': r for r in
            load(HERE.parent / "2026-09-14-w27c-g1d/frozen-checking-matrix.json")["rows"]}


def admit(rows):
    for row in rows:
        cell = f'{row["profile"]}/{row["scene"]}'
        if base_id(row["scene"]) in denied:
            raise ValueError(f"{cell}: checking set cannot enter any sweep row")
        if cell in holdout:
            raise ValueError(f"{cell}: W28 holdout cannot enter any sweep row")


def score(scheme):
    expected = {r["cell"]: r for r in partition["rows"]
                if r["scheme"] == scheme and r["a11yMode"] == "standard"}
    table = {}
    for path in sorted((HERE / "sweep-matrices").glob(f"{scheme}-*.json")):
        doc = load(path)
        if doc["renderer"] != "webgpu":
            continue
        admit(doc["rows"])
        rows = {f'{r["profile"]}/{r["scene"]}': r for r in doc["rows"]}
        if len(rows) != len(doc["rows"]) or rows.keys() != expected.keys():
            raise ValueError(f"{path.name}: incomplete or duplicate population")
        if any(not math.isfinite(r["body"]["deltaE"]) for r in rows.values()):
            raise ValueError(f"{path.name}: non-finite metric")
        fit = [row for cell, row in rows.items() if expected[cell]["role"] == "fit"]
        controls = []
        for cell, row in rows.items():
            if expected[cell]["role"] != "control":
                continue
            old = baseline[cell]
            if row["nativeSha256"] != old["nativeSha256"]:
                raise ValueError(f"{cell}: control native bytes differ from G1d")
            controls.append({"cell": cell, "bodyDeltaE": row["body"]["deltaE"],
                             "baselineBodyDeltaE": old["body"]["deltaE"],
                             "ratio": row["body"]["deltaE"] / max(old["body"]["deltaE"], 1e-9)})
        worst = max(controls, key=lambda r: r["ratio"])
        table[path.stem] = {
            "patchSha256": doc["patchSha256"],
            "inactiveSha256": doc["inactiveSha256"],
            "fitMeanBodyDeltaE": mean(row["body"]["deltaE"] for row in fit),
            "controlMeanBodyDeltaE": mean(row["bodyDeltaE"] for row in controls),
            "worstControl": worst,
            "refused": worst["ratio"] > partition["controlCap"],
            "rows": [{"cell": cell, "role": expected[cell]["role"],
                      "bodyDeltaE": row["body"]["deltaE"],
                      "webY": row["body"]["webY"], "nativeY": row["body"]["nativeY"],
                      "fullCanvasDeltaE": row["deltaE"]["mean"]}
                     for cell, row in sorted(rows.items())],
        }
    candidates = [name for name, row in table.items()
                  if not row["refused"] and "baseline-source" not in name]
    selected = min(candidates, key=lambda name: (table[name]["fitMeanBodyDeltaE"],
                   "four" in name, name), default=None)
    result = {"gate": "W28 G1 / claims §5.145", "scheme": scheme,
              "objective": partition["metric"], "controlCap": partition["controlCap"],
              "selected": selected, "admissible": candidates, "rungs": table}
    (HERE / f"fit-{scheme}.json").write_text(json.dumps(result, indent=2) + "\n")
    if selected is None:
        raise ValueError(f"{scheme}: every rung refused; stop, do not widen the family")
    print(scheme, selected, table[selected]["fitMeanBodyDeltaE"], table[selected]["worstControl"])


if __name__ == "__main__":
    for scheme in sys.argv[1:] or ["light", "dark"]:
        score(scheme)
