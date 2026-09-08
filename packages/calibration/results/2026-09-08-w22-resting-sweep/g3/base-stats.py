"""The base pane's two tone statistics, measured off vitrea's own capture.

The derived tone `backdrop-stack.ts` hands the overlay claims to be the base pane's output in W9's
two spaces. The capture carries the truth: read the base pane's body region and take BOTH means —
the linear mean, and the encoded-space mean decoded once — the way `backdrop-tone.ts` takes them.
"""
import importlib.util
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = "/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-ac98f964c1299c688"
G0 = os.path.join(HERE, "packages/calibration/results/2026-09-08-w22-resting-sweep/g0")
spec = importlib.util.spec_from_file_location("rs", os.path.join(G0, "read-stack.py"))
rs = importlib.util.module_from_spec(spec)
sys.modules["rs"] = rs
spec.loader.exec_module(rs)


def decode(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


scenes = json.load(open(os.path.join(HERE, "apps/reference-apple/scenes.json")))
canvas = scenes["canvas"]
comp = scenes["components"]["glass-over-glass"]
base_box = rs.place(comp["base"], canvas)
over_box = rs.place(comp["over"], canvas)

CAP = "/Users/new/.claude/jobs/5c70e47f/tmp/w22/g3/stacked"
print(f"{'profile':38s} {'tier':7s} {'linearMean':>11s} {'encodedMean':>12s} {'gap':>9s}")
for profile in ("apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard",
                "apple-macos-26.5-1x-dark-standard", "apple-macos-26.5-2x-dark-standard"):
    for tier in ("webgpu", "css"):
        sid = "checkerboard__glass-over-glass__rest"
        png = os.path.join(CAP, profile, sid, f"{sid}__{tier}.png")
        if not os.path.exists(png):
            continue
        rgb = np.asarray(Image.open(png).convert("RGB"), dtype=np.float64) / 255.0
        lin = decode(rgb)
        lum_lin = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
        scale = rgb.shape[1] / canvas["width"]
        body = rs.rect_mask(base_box, scale, lum_lin.shape, 6.0)
        body &= ~rs.rect_mask(over_box, scale, lum_lin.shape, -6.0)
        linear_mean = float(lum_lin[body].mean())
        enc = rgb[body]
        enc_mean = enc.mean(axis=0)
        d = decode(enc_mean)
        encoded_mean = float(0.2126 * d[0] + 0.7152 * d[1] + 0.0722 * d[2])
        print(f"{profile:38s} {tier:7s} {linear_mean:11.4f} {encoded_mean:12.4f} "
              f"{encoded_mean - linear_mean:+9.4f}")
