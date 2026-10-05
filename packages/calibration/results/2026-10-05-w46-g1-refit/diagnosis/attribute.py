#!/usr/bin/env python3.12
"""W46 G1 step 0 (charter Decision Log 8 item 1): the per-pixel attribution of the level change that
G0's ladder (i) read on `impulse__capsule-button__inactive` when the receded `tintAlpha` leaves 0.89
(+0.0331 at 0.8, +0.0702 at 0.7 at 1x; §5.208 §7), which G0's level check named `unexplained`.

Inputs: the six renders `render.sh` made (control = the shipped rung, i-r-0.8, i-r-0.7; both dark 0.25
profiles; WebGPU; candidate mode from G0's committed candidates), the native fixture, the background
fixture, the measurement's own mask (`mask.ts`: the NATIVE silhouette every `interiorMean*` row is read
over), and the shader's arithmetic evaluated by G0's `level/arith.ts` (the runtime's exported functions)
at the abscissa the renderer itself reported for the surface (`backdropToneAbscissae`: the silhouette
reduction the receded document selects).

The model is the composite the optics pass writes for a neutral backdrop (`wgsl/optics.ts`, the W9
solve and the composite after it): per pixel

    L_px = (1 − α′)·b_px + α′·Ñ

with `b_px` the pixel's own scattered backdrop, `α′` the sized alpha after the one-sided opacity lift,
`Ñ` the solved neutral's luma. `α′` and `Ñ` are per surface (one abscissa for the capsule); every
stand-down the charter names lives in them: the black branch (its weight, zero above encoded 0.003), the
authority fade, the clamp of the neutral at 0, the collapse (`toneAdapt`). The term `(1 − α′)·b_px` is
the transmission and carries none of them. So the change between two rungs splits per pixel into

    ΔL_px = Δ(α′Ñ)            the solve term: uniform over the surface, the stand-downs' only path
          + Δ(1 − α′)·b_px    the transmission of the pixel's own backdrop

`b_px` is recovered from the shipped rung's render (`(L − α′Ñ)/(1 − α′)`), and the two moved rungs
are then PREDICTED per pixel and compared with their renders: if the residual is at quantisation, the
arithmetic accounts for the change pixel by pixel.

    python3.12 -B attribute.py           # writes attribution.json and attribution.txt beside this file
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parents[1]
G0 = CAL / "results/2026-10-05-w46-g0-declaration"
SCRATCH = Path.home() / "vitrea-w46/g1-scratch/diagnosis"
SCENE = "impulse__capsule-button__inactive"
RUNGS = ("control", "i-r-0.8", "i-r-0.7")
SPAN = 44                                   # capsule-button, 120 × 44 CSS px


def decode(v):
    v = np.asarray(v, dtype=np.float64)
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def encode(x):
    x = np.asarray(x, dtype=np.float64)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.clip(x, 0, None) ** (1 / 2.4) - 0.055)


def luminance(path: Path) -> np.ndarray:
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    return decode(rgb) @ np.array([0.2126, 0.7152, 0.0722])


def arith(rung: str, cell: dict) -> dict:
    folder = G0 / "ladders/candidates" / rung
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "in.json"
        path.write_text(json.dumps(dict(endpoints=dict(active=str(folder / "active.dark.json"),
                                                       receded=str(folder / "receded.dark.json")),
                                        cells=[cell])))
        got = subprocess.run(["pnpm", "exec", "tsx", str(G0 / "level/arith.ts"), str(path)], cwd=CAL,
                             capture_output=True, text=True, check=True)
    return json.loads(got.stdout)[0]


def read_scale(scale: int) -> dict:
    profile = f"apple-macos-27.0-{scale}x-dark-standard-glass0.25"
    mask_doc = json.loads((SCRATCH / "masks" / f"{scale}x.json").read_text())
    h, w = mask_doc["height"], mask_doc["width"]
    mask = np.array(mask_doc["nativeSilhouette"], dtype=bool).reshape(h, w)
    region = np.array(mask_doc["region"], dtype=bool).reshape(h, w)
    background = luminance(ROOT / f"apps/reference-apple/fixtures/backgrounds/impulse@{scale}x.png")
    native = luminance(ROOT / f"apps/reference-apple/fixtures/{profile}/{SCENE}.png")
    out = dict(profile=profile, maskPixels=int(mask.sum()), regionPixels=int(region.sum()),
               backgroundUnderMask=dict(mean=float(background[mask].mean()), min=float(background[mask].min())),
               nativeUnderMask=float(native[mask].mean()), rungs={})
    renders, solve = {}, {}
    for rung in RUNGS:
        capture = SCRATCH / rung / f"{scale}x/web-captures" / profile / SCENE
        report = json.loads((capture / "report__webgpu.json").read_text())
        abscissa = report["page"]["groups"][0]["state"]["backdropToneAbscissae"][0]
        row = next(c for c in json.loads((SCRATCH / rung / f"{scale}x/matrix.json").read_text())["cells"]
                   if c["key"]["sceneId"] == SCENE)
        tint = report["page"]["recededMaterialProfile"]["optics"]["regular"]["tintAlpha"]
        cell = dict(id=f"{scale}x/{rung}", pose="inactive", span=SPAN, dpr=scale,
                    encoded=abscissa["encodedLuminance"], linear=abscissa["linearLuminance"])
        p = arith(rung, cell)
        L = luminance(capture / f"{SCENE}__webgpu.png")
        renders[rung], solve[rung] = L, p
        a = p["sizedAlpha"] + p["alphaLift"]
        out["rungs"][rung] = dict(
            recededTintAlpha=tint, abscissa=dict(kind=abscissa["kind"], encoded=abscissa["encodedLuminance"],
                                                 linear=abscissa["linearLuminance"],
                                                 samples=abscissa["sampleCount"]),
            interiorMeanWebRow=row["material"]["interiorMeanWeb"]["value"],
            interiorMeanNativeRow=row["material"]["interiorMeanNative"]["value"],
            interiorMeanWebFromMask=float(L[mask].mean()),
            arithmetic=dict(sizeK=p["sizeK"], sizedAlpha=p["sizedAlpha"], alphaLift=p["alphaLift"],
                            drawnAlpha=a, blackWeight=p["blackWeight"], authority=p["authority"],
                            toneAdapt=p["toneAdapt"], collapsed=p["collapsed"], clamped=p["clamped"],
                            response=p["response"], neutral=p["neutral"], solvedNeutral=p["solved"],
                            solveTerm=a * p["solved"], transmission=1 - a,
                            groupMeanComposite=p["achieved"]))
    # b_px from the shipped rung; predict the moved rungs pixel by pixel.
    c = solve["control"]
    a0 = c["sizedAlpha"] + c["alphaLift"]
    b = (renders["control"] - a0 * c["solved"]) / (1 - a0)
    alpha = np.asarray(Image.open(SCRATCH / "control" / f"{scale}x/web-captures" / profile / SCENE /
                                  f"{SCENE}__webgpu__alpha.png"))[..., 3]
    # The model is the opaque body's: the drawn interior is where the material's own alpha (the
    # capture over a transparent page) is 1; the antialiased contour composites a coverage the
    # model does not carry, and the region's margin is not drawn at all.
    interior = alpha == 255
    out["interiorPixels"] = int(interior.sum())
    out["maskInsideInterior"] = bool((mask <= interior).all())
    body = interior & ~mask & (background == 0)
    out["recoveredBackdrop"] = dict(underMask=float(b[mask].mean()), bodyAwayFromDots=float(np.median(b[body])),
                                    interiorMean=float(b[interior].mean()))
    for rung in RUNGS[1:]:
        p = solve[rung]
        a = p["sizedAlpha"] + p["alphaLift"]
        predicted = (1 - a) * b + a * p["solved"]
        resid_code = (encode(predicted) - encode(renders[rung])) * 255
        d_solve = a * p["solved"] - a0 * c["solved"]
        d_trans = (a0 - a) * b
        measured = renders[rung] - renders["control"]
        out["rungs"][rung]["perPixel"] = dict(
            residualCodesOverMask=dict(maxAbs=float(np.abs(resid_code[mask]).max()),
                                       meanAbs=float(np.abs(resid_code[mask]).mean())),
            residualCodesOverInterior=dict(maxAbs=float(np.abs(resid_code[interior]).max()),
                                           p99Abs=float(np.percentile(np.abs(resid_code[interior]), 99)),
                                           meanAbs=float(np.abs(resid_code[interior]).mean())),
            overMask=dict(measuredDelta=float(measured[mask].mean()), solveTerm=float(d_solve),
                          transmissionTerm=float(d_trans[mask].mean()),
                          predictedDelta=float(d_solve + d_trans[mask].mean())),
            overBodyAwayFromDots=dict(measuredDelta=float(np.median(measured[body])), solveTerm=float(d_solve),
                                      transmissionTerm=float(np.median(d_trans[body]))),
            rowDelta=out["rungs"][rung]["interiorMeanWebRow"] - out["rungs"]["control"]["interiorMeanWebRow"])
    return out


def main() -> int:
    result = {f"{s}x": read_scale(s) for s in (1, 2)}
    (HERE / "attribution.json").write_text(json.dumps(result, indent=1) + "\n")
    lines = []
    for scale, r in result.items():
        lines.append(f"{scale} {r['profile']}: L1 mask (native silhouette) {r['maskPixels']} px of a "
                     f"{r['regionPixels']} px region, inside the {r['interiorPixels']} px drawn interior: "
                     f"{r['maskInsideInterior']}; backdrop under it mean {r['backgroundUnderMask']['mean']:.4f} "
                     f"(min {r['backgroundUnderMask']['min']:.4f}); native under it {r['nativeUnderMask']:.4f}")
        for rung, x in r["rungs"].items():
            m = x["arithmetic"]
            lines.append(f"  {rung:8} a′ {x['recededTintAlpha']}: row {x['interiorMeanWebRow']:.6f} = mask "
                         f"{x['interiorMeanWebFromMask']:.6f}; abscissa {x['abscissa']['kind']} enc "
                         f"{x['abscissa']['encoded']:.6f} lin {x['abscissa']['linear']:.6f}; blackWeight "
                         f"{m['blackWeight']:.3f} authority {m['authority']:.4f} toneAdapt {m['toneAdapt']:.4f} "
                         f"clamped {m['clamped']} lift {m['alphaLift']:.4f}; α′ {m['drawnAlpha']:.4f} Ñ "
                         f"{m['solvedNeutral']:.5f} solve term {m['solveTerm']:.5f}")
            if "perPixel" in x:
                pp = x["perPixel"]
                lines.append(f"           over the mask: measured {pp['overMask']['measuredDelta']:+.5f} (row "
                             f"{pp['rowDelta']:+.5f}) = solve {pp['overMask']['solveTerm']:+.5f} + transmission "
                             f"{pp['overMask']['transmissionTerm']:+.5f} (predicted "
                             f"{pp['overMask']['predictedDelta']:+.5f}); body away from the dots: measured "
                             f"{pp['overBodyAwayFromDots']['measuredDelta']:+.5f}, solve "
                             f"{pp['overBodyAwayFromDots']['solveTerm']:+.5f}; per-pixel residual over the mask "
                             f"max {pp['residualCodesOverMask']['maxAbs']:.2f} codes, over the drawn interior p99 "
                             f"{pp['residualCodesOverInterior']['p99Abs']:.2f} max "
                             f"{pp['residualCodesOverInterior']['maxAbs']:.2f}")
        lines.append(f"  recovered scattered backdrop: under the mask {r['recoveredBackdrop']['underMask']:.4f}, "
                     f"body away from the dots {r['recoveredBackdrop']['bodyAwayFromDots']:.5f}, drawn interior mean "
                     f"{r['recoveredBackdrop']['interiorMean']:.5f} (the solve's abscissa reads "
                     f"{r['rungs']['control']['abscissa']['linear']:.5f})")
    text = "\n".join(lines) + "\n"
    (HERE / "attribution.txt").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
