#!/usr/bin/env python3
"""W27c G1c: the CSS tier's derivation of the fitted endpoint, for the record only.

Contract X1: every measured claim is on the WebGPU tier and the CSS tier derives.
Nothing here gates anything, no threshold is applied and no floor is proposed —
this exists because the wave's contract says a derived residual is written down
rather than discovered later, and because the accessibility fold this child moved
is one of the terms `tier-coherence.test.ts` pins across the two tiers.

    python3 css-derivation.py /tmp/w27c-g1c-frozen/checking-css.json \
                              /tmp/w27c-g1c-frozen/checking.json
"""
import json
import os
import sys
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    css = json.load(open(sys.argv[1] if len(sys.argv) > 1
                         else "/tmp/w27c-g1c-frozen/checking-css.json"))
    gpu = json.load(open(sys.argv[2] if len(sys.argv) > 2
                         else "/tmp/w27c-g1c-frozen/checking.json"))
    assert css["renderer"] == "css" and gpu["renderer"] == "webgpu"
    assert css["patchSha256"] == gpu["patchSha256"], "the two tiers read different endpoints"

    by_gpu = {(r["profile"], r["scene"]): r for r in gpu["rows"]}
    out = {
        "gate": "W27c G1c / claims §5.141",
        "kind": "record only — X1: the CSS tier derives and gates nothing",
        "patchSha256": css["patchSha256"],
        "machineAccessibility": css["machineAccessibility"],
        "perProfile": {},
        "widestTierGap": None,
    }
    widest = None
    for profile in sorted({r["profile"] for r in css["rows"]}):
        rows = [r for r in css["rows"] if r["profile"] == profile]
        pairs = [(r, by_gpu[(r["profile"], r["scene"])]) for r in rows
                 if (r["profile"], r["scene"]) in by_gpu]
        for c, g in pairs:
            gap = abs(c["body"]["webY"] - g["body"]["webY"])
            if widest is None or gap > widest["bodyYGap"]:
                widest = {"cell": f"{c['profile']}/{c['scene']}", "bodyYGap": gap,
                          "cssBodyY": c["body"]["webY"], "webgpuBodyY": g["body"]["webY"],
                          "nativeBodyY": c["body"]["nativeY"]}
        out["perProfile"][profile] = {
            "cells": len(rows),
            "cssMeanFullCanvasDeltaE": mean(r["deltaE"]["mean"] for r in rows),
            "cssMeanBodyDeltaE": mean(r["body"]["deltaE"] for r in rows),
            "webgpuMeanFullCanvasDeltaE": mean(g["deltaE"]["mean"] for _, g in pairs),
            "webgpuMeanBodyDeltaE": mean(g["body"]["deltaE"] for _, g in pairs),
            "meanAbsTierGapInBodyY": mean(
                abs(c["body"]["webY"] - g["body"]["webY"]) for c, g in pairs),
        }
    out["widestTierGap"] = widest
    with open(os.path.join(HERE, "css-derivation.json"), "w") as handle:
        json.dump(out, handle, indent=1)
        handle.write("\n")

    print(f"{'profile':46} {'n':>3} {'css fc':>9} {'gpu fc':>9} {'css body':>9} "
          f"{'gpu body':>9} {'tier ΔY':>8}")
    for profile, v in out["perProfile"].items():
        print(f"{profile.replace('apple-macos-26.5-',''):46} {v['cells']:3} "
              f"{v['cssMeanFullCanvasDeltaE']:9.5f} {v['webgpuMeanFullCanvasDeltaE']:9.5f} "
              f"{v['cssMeanBodyDeltaE']:9.5f} {v['webgpuMeanBodyDeltaE']:9.5f} "
              f"{v['meanAbsTierGapInBodyY']:8.5f}")
    print(f"\nwidest tier gap in body Y: {widest['cell']} "
          f"css {widest['cssBodyY']:.5f} against webgpu {widest['webgpuBodyY']:.5f} "
          f"(native {widest['nativeBodyY']:.5f})")


sys.exit(main())
