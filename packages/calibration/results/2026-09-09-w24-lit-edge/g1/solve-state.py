"""W24 G1 (b) — the collapse's and the solve's state on the cells the wave reads, off the running
system's own publication.

The calibration page publishes each group's RESOLVED state into `report__webgpu.json`
(`page.groups[].backdropTone` — the level the host measured, its linear luminance and its colour —
beside `page.surfaces[].bounds` and the material profile patch the run was given). That is the
honesty core: it is what the group actually resolved, not what the scene asked for. This script
reads those published numbers and evaluates the shader's own arithmetic on them, so the state is
attributed to a published value per group rather than inferred from a picture.

What it prints per cell:

- `sizeK` — the size law's thickness factor at the surface's span (smoothstep over
  `sizeSpanMin`..`sizeSpanMax`, fold 1 at rest under no preference);
- `toneX`, `k` — the collapse's argument and its strength `backdropToneMax · (1 − smoothstep(low,
  high, toneX))`;
- `alpha` — `tintAlpha + sizeOcclusionGain · sizeK · (1 − tintAlpha)`, the pre-solve occlusion;
- `auth`, `solve` — the W9 response solve's authority and whether it runs at all. Its gate is
  `strength > 0 ∧ alpha > 1e-3 ∧ k < 0.995 ∧ authority > 0`. The shader's struct comment still says
  the strength is "0 on dark profiles"; the dark profile document records 1 (W21 G1 put the
  response law on the dark scheme at strength 1, claims §5.90), and this read takes the published
  patch, which is the number that ran.

The point of the table is one question: on the cells where the transmission is gone, is the alpha
solve implicated? Where `k` is 1 the answer is arithmetic — the solve does not run.

Usage: solve-state.py <captures-dir> <profile>/<scene> ...
"""

import json
import sys

CANVAS = (320.0, 200.0)


def srgb_encode(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def smoothstep(a, b, x):
    t = min(max((x - a) / max(b - a, 1e-6), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


# The renderer's own defaults for the keys this read needs, copied from
# `packages/renderer-webgpu/src/material.ts`; the profile patch the report publishes overrides each
# of them, and the dark profile document leaves `backdropToneSizeBias` and `tintAlpha`'s neighbours
# to these.
DEFAULTS = {
    "sizeSpanMin": 32.0,
    "sizeSpanMax": 96.0,
    "backdropToneMax": 1.0,
    "backdropToneLow": 0.02,
    "backdropToneHigh": 0.055,
    "backdropToneSizeBias": 0.05,
    "sizeOcclusionGain": 0.05,
    "backdropToneResponseStrength": 1.0,
    "backdropToneAnchorX": [0.1104, 0.2706, 0.9505],
}


def state_of(report_path):
    page = json.load(open(report_path))["page"]
    patch = page.get("materialProfile") or {}
    p = {k: patch.get(k, v) for k, v in DEFAULTS.items()}
    tint_alpha = (((patch.get("optics") or {}).get("regular") or {}).get("tintAlpha")) or 0.46
    out = []
    for surface in page["surfaces"]:
        group = next(g for g in page["groups"] if g["id"] == surface["groupId"])
        tone = group.get("backdropTone")
        b = surface["bounds"]
        span = min(float(b["width"]), float(b["height"]))
        size_k = smoothstep(p["sizeSpanMin"], p["sizeSpanMax"], span)
        if tone is None:
            out.append((surface["nodeId"], span, size_k, None))
            continue
        level = float(tone["level"])
        linear = float(tone.get("linearLuminance", level))
        tone_x = level + p["backdropToneSizeBias"] * size_k
        k = p["backdropToneMax"] * (
            1.0 - smoothstep(p["backdropToneLow"], p["backdropToneHigh"], tone_x)
        )
        alpha = tint_alpha + p["sizeOcclusionGain"] * size_k * (1.0 - tint_alpha)
        encoded = srgb_encode(min(max(level, 0.0), 1.0))
        anchor = max(p["backdropToneAnchorX"][0], 1e-4)
        authority = smoothstep(anchor * 0.5, anchor, encoded) * min(
            max(p["backdropToneResponseStrength"], 0.0), 1.0
        )
        runs = p["backdropToneResponseStrength"] > 0 and alpha > 1e-3 and k < 0.995 \
            and authority > 0
        out.append((surface["nodeId"], span, size_k, {
            "level": level, "linear": linear, "toneX": tone_x, "k": k, "alpha": alpha,
            "encoded": encoded, "authority": authority, "solve": runs,
            "rgb": tone.get("rgb"),
        }))
    return out


def main(argv):
    root = argv[0]
    print(f"{'profile':40}{'scene':34}{'node':8}{'span':>6}{'sizeK':>8}{'level':>9}{'toneX':>8}"
          f"{'k':>8}{'alpha':>8}{'auth':>7}{'solve':>7}")
    for spec in argv[1:]:
        profile, scene = spec.split("/", 1)
        path = f"{root}/{profile}/{scene}/report__webgpu.json"
        for node, span, size_k, s in state_of(path):
            if s is None:
                print(f"{profile:40}{scene:34}{node:8}{span:6.0f}{size_k:8.4f}"
                      f"{'  (no backdrop tone measured — the axis is stood down)':>46}")
                continue
            print(f"{profile:40}{scene:34}{node:8}{span:6.0f}{size_k:8.4f}{s['level']:9.5f}"
                  f"{s['toneX']:8.4f}{s['k']:8.4f}{s['alpha']:8.4f}{s['authority']:7.3f}"
                  f"{('yes' if s['solve'] else 'no'):>7}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
