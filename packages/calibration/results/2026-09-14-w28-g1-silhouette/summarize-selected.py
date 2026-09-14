"""Record CSS derivation and the accessibility rows without selecting on either."""
from pathlib import Path
from statistics import mean
import json

here = Path(__file__).resolve().parent
load = lambda name: json.loads((here / name).read_text())
coherence = []
for scheme in ["light", "dark"]:
    selected = load(f"fit-{scheme}.json")["selected"]
    gpu = {r["cell"]: r for r in load(f"sweep-matrices/{selected}.json")["rows"]}
    css = {r["cell"]: r for r in load(f"sweep-matrices/css-{scheme}-selected.json")["rows"]}
    assert gpu.keys() == css.keys()
    for cell, row in css.items():
        coherence.append({"cell": cell, "profile": row["profile"],
                          "cssY": row["body"]["webY"], "gpuY": gpu[cell]["body"]["webY"],
                          "absoluteYGap": abs(row["body"]["webY"] - gpu[cell]["body"]["webY"]),
                          "cssBodyDeltaE": row["body"]["deltaE"],
                          "gpuBodyDeltaE": gpu[cell]["body"]["deltaE"]})
profiles = {profile: mean(r["absoluteYGap"] for r in coherence if r["profile"] == profile)
            for profile in sorted({r["profile"] for r in coherence})}
(here / "css-coherence.json").write_text(json.dumps({
    "role": "Record only; no CSS fit, gate or holdout read", "rows": coherence,
    "meanAbsoluteBodyYGapByProfile": profiles,
    "worst": max(coherence, key=lambda row: row["absoluteYGap"]),
}, indent=2) + "\n")
base = {r["profile"] + "/" + r["scene"]: r for r in json.loads(
    (here.parent / "2026-09-14-w27c-g1d/frozen-checking-matrix.json").read_text())["rows"]}
accessibility = []
for label in ["a11y-ic-selected", "a11y-rt-selected"]:
    for row in load(f"sweep-matrices/{label}.json")["rows"]:
        old = base[row["cell"]]
        accessibility.append({"cell": row["cell"], "body": row["body"],
                              "baselineBody": old["body"],
                              "bodyMetricsIdentical": row["body"] == old["body"]})
(here / "accessibility-check.json").write_text(json.dumps({
    "levelsRetained": {"reduceTransparency": 0.88, "increaseContrast": 0.98},
    "rows": accessibility,
}, indent=2) + "\n")
print("CSS body-Y gaps", profiles)
print("Worst", max(coherence, key=lambda row: row["absoluteYGap"]))
print("Accessibility body metrics identical", sum(r["bodyMetricsIdentical"] for r in accessibility), "/", len(accessibility))
