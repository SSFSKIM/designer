"""Every inactive scene the canonical matrix admits, read from the declaration.

The list is generated rather than written down, for X10's reason one axis over: an
id typed into a script is a split decision made in code, and `scenes.json` is the
only place a split is allowed to be decided. `holdout` and `recorded` are excluded
here — holdout because a holdout is one native reading per frozen configuration and
W28 spent exactly six of them at G2 (claims §5.146 §3), `recorded` because it is the
pressed pose, which this wave measured nothing about.

    python3 inactive-scenes.py --csv     # for `compare --scene`
    python3 inactive-scenes.py           # one per line, with the set it came from
"""
import json
import pathlib
import sys

ADMITTED = ("calibration", "validation", "probe")

root = pathlib.Path(__file__).resolve().parents[4]
spec = json.loads((root / "apps/reference-apple/scenes.json").read_text())
split = spec["split"]


def set_of(scene_id):
    for name in ("calibration", "validation", "holdout", "recorded", "probe"):
        if scene_id in split.get(name, []):
            return name
    raise SystemExit(f"{scene_id}: in no declared split")


rows = [
    (scene["id"], set_of(scene["id"]))
    for scene in spec["scenes"]
    if scene.get("state") == "inactive"
]
admitted = [(i, s) for i, s in rows if s in ADMITTED]

if "--csv" in sys.argv:
    print(",".join(i for i, _ in admitted))
else:
    for scene_id, name in rows:
        print(f"{'+' if name in ADMITTED else '-'} {name:12} {scene_id}")
    print(f"\n{len(admitted)} admitted of {len(rows)} inactive scenes", file=sys.stderr)
