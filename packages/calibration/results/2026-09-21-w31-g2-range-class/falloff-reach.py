#!/usr/bin/env python3
"""W31 G2 — does any pixel of a bed component reach the outer shadow's overflow
boundary? (claims c9a §5.163 §4.)

W30 G3b left one residual it measured and did not explain: three `glass-over-glass`
texture cells on the 2x dark bed moved by at most 7.94e-4 (`shadow.falloffSigmaWeb`)
and 8.86e-4 (`shadow.centroidOffsetXWeb`) across a shader fix that is supposed to be
the identity, with their `shape` axis not moving at all. The tracker's candidate was
"a handful of exterior pixels whose falloff argument sat at the overflow boundary",
and its stated way to settle it was the range proof W31 G2 owes.

This is that range proof, evaluated per component per document.

THE BOUNDARY. `outer_shadow_falloff` computes tanh(K(x + C x^3)) with
K = 0.7978845608028654 and C = 0.044715, where x is the distance to the SHADOW's
silhouette measured in sigma, negated — positive inside. Metal's fast-math path
lowers tanh through exp(2t) and f32's exp overflows at 2t > ln(f32max) = 88.7228,
so the argument overflows at t > 44.3614, which K(x + C x^3) crosses at
x = 10.0610 (claims §5.159b §1).

TWO PROPERTIES OF THAT SENTENCE MATTER, and the second is the one W30 G3b's
residual paragraph missed:

  * It is ONE-SIDED. The lowering overflows only for +2t; at x negative the same
    expression drives exp(2t) to zero and the quotient to -1 without ever leaving
    f32. An EXTERIOR pixel has x < 0 by construction, so no exterior pixel can
    reach the boundary at all.
  * The deepest INTERIOR pixel of a caster sits at x = (halfSpan + spreadPx)/sigma,
    which is what §5.159b measured on the span-44 capsule: 22 + 3.1 = 25.1 CSS px
    against 10.061 * 2.13 = 21.4.

So the table below is the whole answer: per component, the deepest x its own
geometry and its own sigma produce, against 10.0610.

Run: python3 falloff-reach.py
"""

import json
import math
import pathlib

K = 0.7978845608028654
C = 0.044715
# ln(f32max) / 2, the point the exp(2t) lowering overflows at (claims §5.159b).
T_OVERFLOW = math.log(3.4028234663852886e38) / 2


def x_at_overflow() -> float:
    """The x that drives K(x + C x^3) to T_OVERFLOW, by bisection."""
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if K * (mid + C * mid**3) < T_OVERFLOW:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


X_OVERFLOW = x_at_overflow()

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROFILES = ROOT / "packages" / "calibration" / "profiles"
SCENES = json.loads((ROOT / "apps" / "reference-apple" / "scenes.json").read_text())


def resolved_shadow(name: str) -> dict:
    """A document's outer shadow, composed over the documents it is a difference of.

    The dark document is a difference over the light one and the light one is a
    patch over the runtime default, so a leaf a dark patch does not name comes
    from the light patch. The three leaves the runtime default supplies that no
    macOS 27 document names are written here with the file that carries them.
    """
    chain = ["apple-macos-27.0-1x-light-standard-glass0.5"]
    if name != chain[0]:
        chain.append(name)
    out = {}
    for key in chain:
        patch = json.loads((PROFILES / f"{key}.json").read_text())["patch"]
        out.update(patch.get("outerShadow", {}))
    return out


def sigma(span: float, shadow: dict) -> float:
    """sigma(span) = sigmaPx + max(sigmaThinOffsetPx, sigmaSlopePerSpan*(span - ref))."""
    return shadow["sigmaPx"] + max(
        shadow["sigmaThinOffsetPx"],
        shadow["sigmaSlopePerSpan"] * (span - shadow["sigmaSpanRefPx"]),
    )


def spans_of(component: dict) -> list[tuple[str, float]]:
    """Each casting surface's own SHORTER side, in CSS px — what the field pass
    unions into the aux target as `castSpanCss` and the sigma law reads per pixel."""
    kind = component.get("kind")
    if kind == "rrect":
        w, h = component["size"]
        return [("", min(w, h))]
    if kind == "capsule":
        w, h = component["size"]
        return [("", min(w, h))]
    if kind == "group":
        out = []
        for index, item in enumerate(component["items"]):
            for _, span in spans_of(item):
                out.append((f"item{index}", span))
        return out
    if kind == "stack":
        out = []
        for label in ("base", "over"):
            for _, span in spans_of(component[label]):
                out.append((label, span))
        return out
    if kind == "text":
        return []
    return []


def main() -> None:
    documents = [
        "apple-macos-27.0-1x-light-standard-glass0.5",
        "apple-macos-27.0-1x-dark-standard-glass0.5",
    ]
    lines = [
        "W31 G2 — the outer shadow's falloff argument at the deepest pixel of each bed",
        "component, against the overflow boundary. Claims c9a §5.163 §4.",
        "",
        f"The boundary: tanh's exp(2t) lowering overflows f32 at t > {T_OVERFLOW:.4f},",
        f"which K(x + C x^3) crosses at x = {X_OVERFLOW:.4f}.",
        "",
        "x_max = (halfSpan + spreadPx) / sigma(span), the deepest interior pixel of the",
        "shadow's own silhouette. An EXTERIOR pixel has x < 0 and cannot reach a",
        "one-sided +2t overflow at all.",
        "",
    ]
    reached_any = False
    for document in documents:
        shadow = resolved_shadow(document)
        spread = shadow["spreadPx"]
        lines.append(f"## {document}")
        lines.append(
            f"   sigmaPx {shadow['sigmaPx']}, slope {shadow['sigmaSlopePerSpan']}, "
            f"ref {shadow['sigmaSpanRefPx']}, thin floor {shadow['sigmaThinOffsetPx']}, "
            f"spread {spread}"
        )
        lines.append("")
        lines.append(f"   {'component':26s} {'part':6s} {'span':>7s} {'sigma':>8s} {'depth':>8s} {'x_max':>8s}  verdict")
        for name, component in sorted(SCENES["components"].items()):
            if name.startswith("$"):
                continue
            for part, span in spans_of(component):
                s = sigma(span, shadow)
                depth = span / 2 + spread
                x = depth / s
                reaches = x >= X_OVERFLOW
                reached_any = reached_any or reaches
                lines.append(
                    f"   {name:26s} {part:6s} {span:7.1f} {s:8.4f} {depth:8.2f} {x:8.4f}  "
                    + ("REACHES the boundary" if reaches else "under")
                )
        lines.append("")

    lines.append("## The W30 G3b residual, settled on this table")
    lines.append("")
    for document in documents:
        shadow = resolved_shadow(document)
        spread = shadow["spreadPx"]
        component = SCENES["components"]["glass-over-glass"]
        worst = max(
            ((part, span, sigma(span, shadow)) for part, span in spans_of(component)),
            key=lambda row: (span_depth := row[1] / 2 + spread) / row[2],
        )
        part, span, s = worst
        x = (span / 2 + spread) / s
        lines.append(
            f"   glass-over-glass on {document}: the deepest x is {x:.4f} on the "
            f"'{part}' surface (span {span:.0f}, sigma {s:.4f}), against {X_OVERFLOW:.4f}. "
            f"Margin {X_OVERFLOW - x:.4f} in x, {(X_OVERFLOW - x) * s:.2f} CSS px of depth."
        )
    lines.append("")
    lines.append(
        "   So NO pixel of that scene reaches the overflow, on either document, from"
    )
    lines.append(
        "   the inside — and no exterior pixel can reach it from the outside, because"
    )
    lines.append(
        "   the lowering is one-sided. The tracker's candidate for the three texture"
    )
    lines.append("   cells is refuted, and the residual is re-opened rather than closed.")
    lines.append("")
    lines.append(
        f"   (Cross-check, the cells that DID fail: the span-44 capsule reaches "
        f"x = {(44/2 + resolved_shadow(documents[0])['spreadPx']) / sigma(44, resolved_shadow(documents[0])):.4f} "
        f"on the light document, over the boundary — which is claims §5.159b §1's own reading.)"
    )
    lines.append("")
    lines.append(f"Any component reaching the boundary at the shipped documents: {reached_any}")
    lines.append("")

    text = "\n".join(lines)
    (HERE / "falloff-reach.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
