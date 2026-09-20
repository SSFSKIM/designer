#!/usr/bin/env python3
"""W30 G3b — the undrawn band, predicted from the falloff's own overflow.

`outer_shadow_falloff` evaluates `0.5 * (1 + tanh(K * (x + C * x**3)))` where
`x = -signedDistance / sigma`. A backend that lowers `tanh` through `exp(2t)`
overflows f32 at `2t > 88.7228`, so the function returns NaN for every
`x > X_NAN` below, and the NaN reaches the composite's alpha.

For a capsule of half-height H centred on row `c`, the pixels whose SHADOW READ
lands in that region are the rows `|s - c| <= H + spread - X_NAN * sigma`,
shifted DOWN by `offsetPx` because the read is taken one offset above the pixel
being shaded. This script prints that band for every configuration claims
§5.159 §6's bisect table captured, and the table is reproduced to the row.

    python3 bisect.py
"""

K = 0.7978845608028654
C = 0.044715
F32_EXP_MAX = 88.7228  # `exp` overflows f32 past this; `tanh` needs `exp(2t)`.


def t_of(x: float) -> float:
    return K * (x + C * x * x * x)


def x_nan() -> float:
    """The smallest x at which f32's `exp(2t)` overflows."""
    lo, hi = 0.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 2 * t_of(mid) < F32_EXP_MAX:
            lo = mid
        else:
            hi = mid
    return lo


X_NAN = x_nan()


def sigma_at(span: float, sigma_px: float, slope: float, ref: float, thin: float) -> float:
    """The renderer's `outerShadowSigmaPx`, and its own 1e-4 floor."""
    return max(sigma_px + max(thin, slope * (span - ref)), 1e-4)


def band(sigma: float, spread: float, offset: float, centre: float, half: float):
    """The drawn canvas rows the NaN covers, or None."""
    limit = half + spread - X_NAN * sigma
    if limit < 0:
        return None
    return (centre - limit + offset, centre + limit + offset)


# `checkerboard__capsule-button__rest` at 1x: a 120x44 capsule, rows 78..121.
CENTRE, HALF = 99.5, 22.0
SPREAD, OFFSET = 3.1, 7.95
LAW = dict(slope=0.1314, ref=96.0, thin=-6.8328)
INERT = dict(slope=0.0, ref=0.0, thin=0.0)

CASES = [
    ("the fitted law", 8.96, LAW, SPREAD, OFFSET, "104…111"),
    ("the fitted law, offsetPx 0", 8.96, LAW, SPREAD, 0.0, "96…103"),
    ("the fitted law, spreadPx 0", 8.96, LAW, 0.0, OFFSET, "107…108"),
    ("sigmaPx 8, the law live", 8.0, LAW, SPREAD, OFFSET, "95…121"),
    ("sigmaPx 4, the law live", 4.0, LAW, SPREAD, OFFSET, "83…121"),
    ("0.19.0: sigmaPx 11, law inert", 11.0, INERT, SPREAD, OFFSET, "none"),
    ("sigmaPx 8, law inert", 8.0, INERT, SPREAD, OFFSET, "none"),
    ("sigmaPx 2.13, law inert", 2.13, INERT, SPREAD, OFFSET, "104…111"),
]

if __name__ == "__main__":
    print(f"tanh's argument overflows f32 at t = {F32_EXP_MAX / 2:.4f}, which is x = {X_NAN:.4f}")
    print()
    print(f"{'document':34s} {'σ(44)':>8s} {'predicted band':>18s}   measured")
    for label, sigma_px, law, spread, offset, measured in CASES:
        sigma = sigma_at(44.0, sigma_px, law["slope"], law["ref"], law["thin"])
        rows = band(sigma, spread, offset, CENTRE, HALF)
        shown = "none" if rows is None else f"{rows[0]:.2f}…{rows[1]:.2f}"
        print(f"{label:34s} {sigma:8.4f} {shown:>18s}   {measured}")
    print()
    print("The surface itself is rows 78…121, so a band running past 121 is clipped by it.")
    print()
    print("The 'strip bottom sits 24 CSS px above the field rect's bottom' of §5.159 §6")
    print("is 11.05·σ − 0.5, not a constant:")
    for sigma in (2.1272, 1.1672, 8.96, 15.55):
        print(f"  σ {sigma:7.4f} → {11.05 * sigma - 0.5:6.2f} CSS px")
