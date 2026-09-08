"""W24 G1 (b) — the dark thin structured cells: the body, and the structure the material passes.

Clause 3 asks whether a transmitting collapse reaches the cells W21 and W22 carried as "the
appearance switch" and W23 G0 measured at −16 / −19 codes. Two readings side by side, both under
the declared shape eroded 6 CSS px (W21's instrument):

- **body** — the mean linear luma, native against web, and the difference in 8-bit codes at that
  level, which is the number the wave quotes;
- **passthrough** — W21 G0's read (`results/2026-09-06-w21-dark-scheme/g0/passthrough.txt`): the
  body's own standard deviation against the BACKDROP's standard deviation over the same region,
  `pass = sd / bgSd`. That is the fraction of the structure on offer that the material let through,
  and it is the quantity a transmitting collapse moves directly. A material that collapses onto one
  colour reads `pass` 0 however close its body level is.

The two together separate the level from the structure, which is the whole of the wave's second
term: `checkerboard` and `photo` under a thin dark capsule can be right in body and still be flat.

Usage: read-structure.py <captures-dir> <profile>/<scene>/<component>/<scale> ...
"""

import sys

import numpy as np

import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("read_impulse", os.path.join(_here,
                                                                           "read-impulse.py"))
ri = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ri)

REF = "/Users/new/Developer/GitHub/designer"


def codes(linear):
    """The 8-bit code a linear luma lands on, so a body difference can be quoted the way the wave
    quotes it."""
    v = 12.92 * linear if linear <= 0.0031308 else 1.055 * (linear ** (1 / 2.4)) - 0.055
    return v * 255.0


def read(path, component, scale, erode=6.0):
    lum = ri.luma_of(path)
    kind, w, h, radius = ri.COMPONENTS[component]
    mask = ri.shape_mask(kind, w, h, radius, scale, lum.shape, erode)
    return float(lum[mask].mean()), float(lum[mask].std()), mask


def main(argv):
    root = argv[0]
    print(f"{'profile':36}{'scene':32}{'src':8}{'body':>9}{'sd':>9}{'bgSd':>9}{'pass':>8}"
          f"{'code':>8}")
    for spec in argv[1:]:
        profile, scene, component, scale_s = spec.split("/")
        scale = float(scale_s)
        bg = scene.split("__")[0]
        bg_path = f"{REF}/apps/reference-apple/fixtures/backgrounds/{bg}@{int(scale)}x.png"
        _, _, mask = read(bg_path, component, scale)
        bg_lum = ri.luma_of(bg_path)
        bg_sd = float(bg_lum[mask].std())
        for tag, path in (
            ("native", f"{REF}/apps/reference-apple/fixtures/{profile}/{scene}.png"),
            ("web", f"{root}/{profile}/{scene}/{scene}__webgpu.png"),
        ):
            body, sd, _ = read(path, component, scale)
            print(f"{profile:36}{scene:32}{tag:8}{body:9.4f}{sd:9.4f}{bg_sd:9.4f}"
                  f"{(sd / bg_sd if bg_sd > 1e-6 else np.nan):8.4f}{codes(body):8.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
