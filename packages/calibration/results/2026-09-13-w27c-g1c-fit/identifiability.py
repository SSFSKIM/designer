#!/usr/bin/env python3
"""W27c G1c: what the bed can and cannot identify about the thin response.

Native-only, from `native-response.json`: nothing here is compared with a vitrea
capture and nothing is spent. It tabulates the reference's own thin-row response
per scheme — the settled interior level against the backdrop's ENCODED-space
mean, at `sizeThickness` 0 or as near as the bed gets — and then states the two
things about the bed that decide whether T1's one free ordinate can carry it: where
the ANCHORS are, and where the UNIFORM backdrops are.

The response's abscissa is not a free grid. `backdropToneAnchorX` is three
measured uniform-patch means and the interpolation between them is monotone
Fritsch-Carlson, so the curve above the middle knot is fixed by two numbers.
Whether that is enough is a question about the spacing of the evidence, and the
spacing is what this prints.

    python3 identifiability.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ANCHORS = [0.1104, 0.2706, 0.9505]
UNIFORM_SD = 1e-6


def main():
    native = json.load(open(os.path.join(HERE, "native-response.json")))
    rows = [r for r in native["rows"] if r["scale"] == 1 and r["a11y"] == "standard"]

    out = {
        "gate": "W27c G1c / claims §5.141",
        "kind": "native-only — the bed's own geometry on the response's abscissa; nothing spent",
        "anchors": {
            "backdropToneAnchorX": ANCHORS,
            "$comment": "the three declared uniform patches' encoded-space means: dark-solid "
                        "28/255, mid-dark-solid 69/255 exactly, light-solid's raster mean",
        },
        "schemes": {},
    }
    for scheme in ("light", "dark"):
        thin = sorted(
            (r for r in rows if r["scheme"] == scheme and r["sizeThickness"] < 0.1),
            key=lambda r: r["encodedBackdropMean"],
        )
        out["schemes"][scheme] = {
            "thinRow": [
                {"scene": r["scene"], "span": r["span"],
                 "encodedBackdropMean": r["encodedBackdropMean"],
                 "sizeThickness": r["sizeThickness"],
                 "nativeBodyY": r["nativeBodyY"],
                 "backdrop": "uniform" if r["nativeBodySd"] <= UNIFORM_SD else "structured",
                 "backdropSd": r["nativeBodySd"]}
                for r in thin
            ],
        }

    uniform = sorted({
        (r["background"], round(r["encodedBackdropMean"], 4))
        for r in rows if r["nativeBodySd"] <= UNIFORM_SD
    }, key=lambda p: p[1])
    structured = sorted({
        (r["background"], round(r["encodedBackdropMean"], 4))
        for r in rows if r["nativeBodySd"] > UNIFORM_SD
    }, key=lambda p: p[1])
    gaps = [
        {"between": [uniform[i][0], uniform[i + 1][0]],
         "from": uniform[i][1], "to": uniform[i + 1][1],
         "width": round(uniform[i + 1][1] - uniform[i][1], 4)}
        for i in range(len(uniform) - 1)
    ]
    out["bedGeometry"] = {
        "uniformBackdrops": [{"background": b, "encodedMean": x} for b, x in uniform],
        "structuredBackdrops": [{"background": b, "encodedMean": x} for b, x in structured],
        "uniformGaps": gaps,
        "widestUniformGap": max(gaps, key=lambda g: g["width"]) if gaps else None,
        "brightestStructured": structured[-1] if structured else None,
        "theConfound":
            "there is no UNIFORM backdrop between the middle anchor and the far one, and no "
            "STRUCTURED backdrop above the brightest structured mean. A reference level that is "
            "low at the brightest structured backdrop and high at the far uniform one is "
            "therefore explained equally by the abscissa (the response steps near white) and by "
            "the structure (the recede goes transparent over a uniform bright field and not over "
            "a broken one). The bed separates neither, and a fit that assumes one is a fit to an "
            "assumption.",
    }
    with open(os.path.join(HERE, "identifiability.json"), "w") as handle:
        json.dump(out, handle, indent=1)
        handle.write("\n")

    for scheme in ("light", "dark"):
        print(f"\n{scheme} scheme, thin row (sizeThickness < 0.1), 1x standard")
        print(f"  {'backdrop mean':>13}  {'kind':10} {'span':>4}  {'native Y':>9}  scene")
        for r in out["schemes"][scheme]["thinRow"]:
            print(f"  {r['encodedBackdropMean']:13.4f}  {r['backdrop']:10} {r['span']:4}  "
                  f"{r['nativeBodyY']:9.5f}  {r['scene']}")
    g = out["bedGeometry"]
    print("\nuniform backdrops:    " + ", ".join(f"{b['background']} {b['encodedMean']}"
                                                 for b in g["uniformBackdrops"]))
    print("structured backdrops: " + ", ".join(f"{b['background']} {b['encodedMean']}"
                                               for b in g["structuredBackdrops"]))
    print(f"widest uniform gap:   {g['widestUniformGap']['from']} → {g['widestUniformGap']['to']} "
          f"({g['widestUniformGap']['width']} of the axis, between "
          f"{' and '.join(g['widestUniformGap']['between'])})")
    print(f"brightest structured: {g['brightestStructured'][0]} at {g['brightestStructured'][1]}")


sys.exit(main())
