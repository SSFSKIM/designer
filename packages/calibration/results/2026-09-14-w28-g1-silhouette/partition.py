"""Declare fit membership from manifest metadata; this script opens no pixels."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
load = lambda path: json.loads(path.read_text())
manifest = load(REPO / "apps/reference-apple/fixtures/manifest.json")
spec = load(REPO / "apps/reference-apple/scenes.json")
checking = load(HERE.parent / "2026-09-11-w27c-g1b/checking-bed.json")
denied = set(next(group for group in checking["groups"] if group["id"] == "D")["scenes"])
denied.add("checkerboard__rrect-ml__inactive")
holdout = {row["cell"] for row in load(HERE / "declaration.json")["holdout"]["rows"]}
baseline = load(HERE.parent / "2026-09-14-w27c-g1d/frozen-checking-matrix.json")
base = {f'{row["profile"]}/{row["scene"]}': row for row in baseline["rows"]}
fit_shapes = {
    "dark-solid": ["rrect-sm", "rrect-lg"],
    "mid-dark-solid": ["rrect-sm", "rrect-md", "rrect-lg"],
    "mid-light-solid": ["capsule-button", "rrect-sm", "rrect-ml", "rrect-lg"],
    "light-solid": ["capsule-button", "rrect-sm", "rrect-lg"],
    "checkerboard": ["capsule-button", "rrect-sm", "rrect-md"],
    "photo": ["capsule-button", "rrect-sm", "rrect-md", "rrect-ml"],
    "impulse": ["capsule-button", "rrect-md", "rrect-ml", "rrect-lg"],
}
fit_scenes = {f"{background}__{shape}__inactive"
              for background, shapes in fit_shapes.items() for shape in shapes}
control_scenes = {f"{background}__{shape}__inactive"
                  for background, shapes in {
                      "checkerboard-8": ["rrect-md", "rrect-lg"],
                      "checkerboard-32": ["rrect-lg"],
                      "checkerboard-64": ["rrect-md", "rrect-lg"],
                      "dark-solid": ["capsule-button"],
                  }.items() for shape in shapes}
rows = []
for profile in manifest["profiles"]:
    key = profile["profileKey"]
    if not key.startswith("apple-macos-26.5-"):
        continue
    for fixture in profile["fixtures"]:
        scene = fixture["sceneId"]
        cell = f"{key}/{scene}"
        if scene in denied or cell in holdout:
            continue
        if profile["a11yMode"] == "standard":
            role = "fit" if scene in fit_scenes else "control" if scene in control_scenes else None
        else:
            role = "accessibility-check" if scene in {
                "checkerboard__rrect-md__inactive", "photo__rrect-md__inactive"
            } else None
        if role is None:
            continue
        if role == "control" and cell not in base:
            raise ValueError(f"Control has no G1d baseline: {cell}")
        rows.append({"cell": cell, "profile": key, "scene": scene,
                     "scheme": profile["colorScheme"], "scale": profile["display"]["actualBackingScale"],
                     "a11yMode": profile["a11yMode"], "role": role,
                     "manifestRole": fixture["fixtureSet"],
                     "nativeFile": fixture["file"],
                     "nativeLineage": "G1d exact target bytes" if cell in base else "committed recovered fixture",
                     "baselineBodyDeltaE": base.get(cell, {}).get("body", {}).get("deltaE")})
rows.sort(key=lambda row: row["cell"])
result = {
    "gate": "W28 G1 / claims §5.145",
    "declaredBeforeFit": True,
    "metric": "Equal-cell mean body OKLab ΔE on fit rows, WebGPU; CSS is record-only (X1)",
    "controlCap": 9,
    "controlBaseline": "../2026-09-14-w27c-g1d/frozen-checking-matrix.json",
    "admission": "admission.ts refuses D and W28 holdout before any native PNG or browser page",
    "supplyingRoleNote": "The dispatch explicitly includes recovered thin impulse capsules and photo squares, whose inherited manifest roles include validation. They are supplying fit rows in this wave; no manifest role is rewritten.",
    "holdout": sorted(holdout),
    "rows": rows,
}
(HERE / "partition.json").write_text(json.dumps(result, indent=2) + "\n")
from collections import Counter
print(Counter((row["scheme"], row["a11yMode"], row["role"]) for row in rows))
