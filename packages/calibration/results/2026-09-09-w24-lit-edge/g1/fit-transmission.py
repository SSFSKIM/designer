"""W24 G1 (c) — the fit: the constant the probe rung solves for, per scale.

On a fully collapsed surface (k = 1, which is every `impulse__capsule-button` cell —
`solve-state.txt`) the shader's composite reduces to `colour = (1 − c)·toneColour + c·backdrop`,
so the dot's excess over the body is exactly `c · E` where `E` is the excess vitrea's own blurred
backdrop carries at that pixel. `E` is a property of the material's scatter law and not of `c`, so
ONE rendered rung at a known `c` fixes it:

    E  = peak(rung) / c_rung          c* = c_rung · peak(native) / peak(rung)

The same arithmetic is printed for the integral, because the peak and the integral cannot both be
matched while the transmitted WIDTH differs (the kernel finding, `g1-findings.md` §5) and the
parent should see both candidates and what each costs.

Usage: fit-transmission.py <c_rung> <native.png> <rung.png> <component> <scale> [<label>]
"""

import importlib.util
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("read_impulse", os.path.join(_here,
                                                                           "read-impulse.py"))
ri = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ri)

R = "/Users/new/Developer/GitHub/designer"


def centre(path, bg, component, scale):
    cell = ri.read_cell(path, bg, component, scale)
    for dot in cell["dots"]:
        if dot["centre"]:
            return dot["x"], cell["body"]
    raise SystemExit(f"no centre dot under the shape in {path}")


def main(argv):
    c_rung = float(argv[0])
    native_path, rung_path, component, scale_s = argv[1], argv[2], argv[3], argv[4]
    label = argv[5] if len(argv) > 5 else ""
    scale = float(scale_s)
    bg = ri.luma_of(f"{R}/apps/reference-apple/fixtures/backgrounds/impulse@{int(scale)}x.png")
    n, n_body = centre(native_path, bg, component, scale)
    r, r_body = centre(rung_path, bg, component, scale)
    e_peak = r["peak"] / c_rung
    e_int = r["integral"] / c_rung
    print(f"{label:34}{scale:.0f}x  c_rung {c_rung:.4f}")
    print(f"  native   peak {n['peak']:9.5f}  fwhm {n['fwhm']:6.2f}  integral {n['integral']:8.4f}"
          f"  body {n_body:.5f}")
    print(f"  rung     peak {r['peak']:9.5f}  fwhm {r['fwhm']:6.2f}  integral {r['integral']:8.4f}"
          f"  body {r_body:.5f}")
    print(f"  vitrea's own blurred backdrop excess E: peak {e_peak:.5f}  integral {e_int:.4f}")
    print(f"  c* on the PEAK      {c_rung * n['peak'] / r['peak']:.5f}")
    print(f"  c* on the INTEGRAL  {c_rung * n['integral'] / r['integral']:.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
