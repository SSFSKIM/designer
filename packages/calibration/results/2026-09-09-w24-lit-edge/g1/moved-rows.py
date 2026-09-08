"""W24 G1 (c) — what the two moved cells do on the bed's own metrics, rung against the landed bed.

Clause 4 is graded on the matrix, not on the dot: no untinted row worse by 0.001 ΔE or 0.005
`ssimMean`, and the calibration mean not up by more than 0.0001. This reads the same rows out of a
scratch ladder matrix and out of the committed one and prints them side by side, so the fit's cost
on the bed is a table rather than a hope. Only the GPU tier's rows are read; a scene appearing at
several profile-document hashes is reduced to its newest row per key, which is the harness's own
rule for a matrix that appends.

Usage: moved-rows.py <landed-matrix.json> <rung-matrix.json> <profileKey> [scene ...]
"""

import json
import sys

METRICS = ("oklabDeltaEMean", "oklabDeltaEP95", "oklabDeltaEMax", "ssimMean", "ssimMin",
           "interiorMeanNative", "interiorMeanWeb", "interiorMeanBackdrop")


def rows(path, profile):
    out = {}
    for cell in json.load(open(path))["cells"]:
        key = cell["key"]
        if key["profileKey"] != profile or key["web"]["renderer"] != "webgpu":
            continue
        material = cell.get("material") or {}
        values = {}
        for group in (material, cell.get("perceptual") or {}, cell.get("shape") or {}):
            for name in METRICS:
                if name in group and name not in values:
                    entry = group[name]
                    values[name] = entry.get("value") if isinstance(entry, dict) else entry
        out[key["sceneId"]] = values
    return out


def main(argv):
    landed = rows(argv[0], argv[2])
    rung = rows(argv[1], argv[2])
    scenes = argv[3:] or sorted(set(landed) & set(rung))
    print(f"{'scene':44}{'metric':22}{'landed':>12}{'rung':>12}{'Δ':>12}")
    for scene in scenes:
        a, b = landed.get(scene, {}), rung.get(scene, {})
        for name in METRICS:
            x, y = a.get(name), b.get(name)
            if x is None or y is None:
                continue
            print(f"{scene:44}{name:22}{x:12.5f}{y:12.5f}{y - x:12.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
