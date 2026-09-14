"""Check that cache/bounds review fixes preserve measured canonical inputs."""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
rows = []
for label, tier in [("review-fix-gpu-photo", "webgpu"), ("review-fix-gpu-worst", "webgpu"),
                    ("review-fix-css-photo", "css")]:
    fresh = json.loads((here / f"{label}.json").read_text())
    original = {r["id"]: r for r in json.loads((here / f"mechanism-{tier}-final.json").read_text())["rows"]}
    for row in fresh["rows"]:
        actual = [x for group in row["groups"] for x in group["state"].get("backdropToneAbscissae", [])
                  if x["kind"] == "silhouette"]
        prior = [x for group in original[row["id"]]["groups"]
                 for x in group["state"].get("backdropToneAbscissae", []) if x["kind"] == "silhouette"]
        assert actual == prior, (row["id"], actual, prior)
        pixels_equal = Path(row["capture"]).read_bytes() == Path(original[row["id"]]["capture"]).read_bytes()
        rows.append({"id": row["id"], "tier": tier, "readoutsIdentical": True,
                     "captureBytesIdentical": pixels_equal})
canonical = json.loads((here / "mechanism-webgpu-final.json").read_text())["rows"]
checked = 0
for row in canonical:
    if "interaction" in row["flags"]:
        continue
    width, height = [extent / row["scale"] for extent in row["pixelSize"]]
    for surface in row["surfaces"]:
        bounds = surface["bounds"]
        assert 0 <= bounds["x"] <= bounds["x"] + bounds["width"] <= width
        assert 0 <= bounds["y"] <= bounds["y"] + bounds["height"] <= height
        checked += 1
(here / "review-fix-input-identity.json").write_text(json.dumps({
    "cells": len(rows), "allUnpressedSurfaceBoundsInsideViewport": checked, "rows": rows,
}, indent=2) + "\n")
print("Post-fix input identity:", len(rows), "/", len(rows))
evidence = json.loads((here / "gpu-evidence.json").read_text())
for row in evidence["benchmark"]["differences"]:
    print("overhead", row["geometry"], row["dpr"], row["medianPairedOverheadMs"], row["p95PairedOverheadMs"])
for row in evidence["diagnostics"]:
    print("mip", row["background"], row["dpr"], row["analysisLevel"], row["deltas"])
