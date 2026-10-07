#!/usr/bin/env python3.12
"""W48 G1: the two light 0.25 CSS 2x cells X60 by render read as DIFFERS, re-captured twice in scratch
strict-mode stages (~/vitrea-w48/g1-stage-x60-light-recheck-{1,2}) on the same light documents, read against
the published ebc3d9105a4a rows and canonical captures: is the difference the dark freeze, or the capture's
own non-determinism (the stage rows carry `deterministic: false` and a non-zero `repeatNoise`)?

    python3.12 -B recheck.py      writes recheck.json beside this file
"""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[3]
CANON = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
P = "apple-macos-27.0-2x-light-standard-glass0.25"
SCENES = ("impulse__rrect-ml__rest", "mid-chroma-solid__rrect-lg__rest")
pub = {r["key"]["sceneId"]: r for r in json.loads((CAL / "results/generations/ebc3d9105a4a.json").read_text())["cells"]
       if r["key"]["profileKey"] == P and r["key"]["web"]["renderer"] == "css"}


def png(root, s):
    f = sorted((root / P / s).glob("*css*.png")) if (root / P / s).exists() else []
    return {x.name: hashlib.sha256(x.read_bytes()).hexdigest() for x in f}


def strip(r):
    r = json.loads(json.dumps(r)); r.pop("capturedAt", None); return r


out = {}
stages = {"x60 stage": Path.home() / "vitrea-w48/g1-stage-x60-light"} | {
    f"recheck {i}": Path.home() / f"vitrea-w48/g1-stage-x60-light-recheck-{i}" for i in (1, 2)}
for s in SCENES:
    out[s] = {"published": dict(deterministic=pub[s]["key"]["web"]["deterministic"],
                                repeatNoise=pub[s]["key"]["web"]["repeatNoise"], png=png(CANON, s))}
    for name, root in stages.items():
        row = next(r for r in json.loads((root / "matrix.json").read_text())["cells"]
                   if r["key"]["sceneId"] == s and r["key"]["profileKey"] == P and r["key"]["web"]["renderer"] == "css")
        out[s][name] = dict(deterministic=row["key"]["web"]["deterministic"], repeatNoise=row["key"]["web"]["repeatNoise"],
                            rowEqualButCapturedAt=strip(row) == strip(pub[s]), png=png(root / "web-captures", s))
        out[s][name]["pngEqualToPublished"] = out[s][name]["png"] == out[s]["published"]["png"]
(HERE / "recheck.json").write_text(json.dumps(out, indent=1) + "\n")
for s, v in out.items():
    for k, x in v.items():
        if k != "published":
            print(s, k, "det", x["deterministic"], "noise", x["repeatNoise"], "row==", x["rowEqualButCapturedAt"], "png==", x["pngEqualToPublished"])
