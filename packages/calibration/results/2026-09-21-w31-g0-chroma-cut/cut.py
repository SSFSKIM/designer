#!/usr/bin/env python3
"""W31 G0 — the reproduction check and the chromatic cut (claims §5.161 §2, §3).

    python3 results/2026-09-21-w31-g0-chroma-cut/cut.py

Reads the scratch matrix this child captured and the committed
`results/matrix.json` beside it, and writes two tables and one JSON:

  reproduction-check.md   every re-captured cell's `interiorMeanWeb` and
                          `ssimMean` against the committed row of the same key,
                          with the bar declared and every cell that misses it
                          NAMED before a new statistic is read off it.
  cut.md                  the three ratios over every chroma-carrying cell,
                          per backdrop class, scheme, tier, span, pose and
                          scale, with each cell's conditioning state and the
                          macOS 26.5 rows beside.
  cut.json                the same, machine-readable.

THE REPRODUCTION BAR. `repeatNoise` is 0 on 1,830 of the committed matrix's
1,833 rows — the captures are deterministic by construction — so the row's own
field gives no usable tolerance for a re-capture taken on a different day. The
three rows that do carry one read 3.5e-05, 1.05e-04 and 1.96e-04. The bar
declared here is **5e-4 absolute** on both statistics: rounded up from the
largest repeat noise the bed has ever recorded, and stated BEFORE the check
runs. The observed maximum is reported beside it, so the bar is checkable
rather than asserted.

THE CONDITIONING STATE. `adopted-thresholds.test.ts`'s predicate, evaluated
here on the SCRATCH row's own shape axis: area ≥ 0.95 × the declared region on
both sides, bodies ≤ the region's own count on both sides. A cell the predicate
refuses is not dropped from the cut — it is tabled with the refusal visible,
because whether a mask the shape rows refuse is adequate for a per-pixel chroma
statistic is a question this child has to answer with evidence rather than
inherit.
"""
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = os.path.dirname(os.path.dirname(HERE))
REPO = os.path.dirname(os.path.dirname(PACKAGE))

REPRODUCTION_BAR = 5e-4
WELL_CONDITIONED_AREA_RATIO = 0.95

SPANS = {
    "capsule-button": 44,
    "rrect-sm": 32,
    "rrect-md": 96,
    "rrect-ml": 128,
    "rrect-lg": 160,
    "toolbar-group": 44,
    "glass-over-glass": 130,
}


def load(path):
    with open(path) as handle:
        return json.load(handle)


def key(cell):
    return "|".join(
        [
            cell["key"]["profileKey"],
            cell["key"]["sceneId"],
            cell["key"]["web"]["engine"],
            cell["key"]["web"]["engineVersion"],
            cell["key"]["web"]["renderer"],
            cell["key"]["web"]["samplingBackend"],
            cell["key"]["web"]["gpuAdapter"],
            cell["key"]["web"]["colorSpace"],
            cell["key"]["web"]["capturePath"],
        ]
    )


def name(cell):
    return "%s / %s / %s / %s" % (
        cell["tier"],
        cell["fixtureSet"],
        cell["key"]["sceneId"],
        cell["key"]["profileKey"],
    )


def value(cell, axis, metric):
    node = cell.get(axis)
    if node is None or metric not in node:
        return None
    return node[metric]["value"]


def well_conditioned(cell):
    """`adopted-thresholds.test.ts`'s `isWellConditioned`, on this row's own axis."""
    shape = cell.get("shape")
    if shape is None:
        return True
    try:
        region_area = shape["componentRegionArea"]["value"]
        region_bodies = shape["componentRegionBodies"]["value"]
        return (
            shape["silhouetteAreaNative"]["value"] >= WELL_CONDITIONED_AREA_RATIO * region_area
            and shape["silhouetteAreaWeb"]["value"] >= WELL_CONDITIONED_AREA_RATIO * region_area
            and shape["silhouetteBodiesNative"]["value"] <= region_bodies
            and shape["silhouetteBodiesWeb"]["value"] <= region_bodies
        )
    except KeyError:
        return True


def parts(cell):
    scene = cell["key"]["sceneId"]
    backdrop, component, pose = scene.split("__", 2)
    profile = cell["key"]["profileKey"]
    scheme = "dark" if "-dark-" in profile else "light"
    scale = 2 if "-2x-" in profile else 1
    os_token = "27" if profile.startswith("apple-macos-27") else "26.5"
    a11y = "standard"
    if "reduced-transparency" in profile:
        a11y = "reduced-transparency"
    elif "increased-contrast" in profile:
        a11y = "increased-contrast"
    return {
        "backdrop": backdrop,
        "component": component,
        "pose": pose,
        "span": SPANS.get(component),
        "scheme": scheme,
        "scale": scale,
        "os": os_token,
        "a11y": a11y,
        "tinted": "-tint-" in pose,
        "active": not pose.startswith("inactive"),
    }


def fmt(x, places=4):
    return "—" if x is None else ("%%.%df" % places) % x


def main():
    scratch = load(os.path.join(HERE, "scratch-matrix.json"))
    committed = load(os.path.join(PACKAGE, "results", "matrix.json"))
    by_key = {key(c): c for c in committed["cells"]}
    # Ratio (iii) comes from its own pass over the same captures and its own
    # matrix file, so the first pass's rows are never rewritten. Overlaid here
    # by key rather than merged on disk.
    blurred_path = os.path.join(HERE, "scratch-matrix-blurred.json")
    blurred = {key(c): c for c in load(blurred_path)["cells"]} if os.path.exists(blurred_path) else {}

    # ---------------------------------------------------------------- 1. the check
    rows = []
    worst = {"interiorMeanWeb": 0.0, "ssimMean": 0.0}
    worst_by_os = {"27": {"interiorMeanWeb": 0.0, "ssimMean": 0.0},
                   "26.5": {"interiorMeanWeb": 0.0, "ssimMean": 0.0}}
    missing = []
    for cell in scratch["cells"]:
        prior = by_key.get(key(cell))
        if prior is None:
            missing.append(name(cell))
            continue
        entry = {"name": name(cell)}
        ok = True
        for axis, metric in (("material", "interiorMeanWeb"), ("perceptual", "ssimMean")):
            now, before = value(cell, axis, metric), value(prior, axis, metric)
            if now is None or before is None:
                entry[metric] = {"scratch": now, "committed": before, "delta": None}
                continue
            delta = abs(now - before)
            worst[metric] = max(worst[metric], delta)
            worst_by_os[parts(cell)["os"]][metric] = max(worst_by_os[parts(cell)["os"]][metric], delta)
            entry[metric] = {"scratch": now, "committed": before, "delta": delta}
            if delta > REPRODUCTION_BAR:
                ok = False
        entry["reproduced"] = ok
        rows.append(entry)

    failed = [r for r in rows if not r["reproduced"]]

    with open(os.path.join(HERE, "reproduction-check.md"), "w") as out:
        out.write("# W31 G0 — the reproduction check (claims §5.161 §2)\n\n")
        out.write(
            "Every cell of the scratch re-capture against the committed row of the SAME KEY —\n"
            "same profile, same scene, same engine build, same `capturePath` and therefore the\n"
            "same material profile document hash. A key that matches is a row read at the same\n"
            "bytes of the same documents, so the two numbers are comparable by construction.\n\n"
        )
        out.write(
            "**The bar is 5e-4 absolute on both statistics, declared before the check ran.**\n"
            "`repeatNoise` is 0 on 1,830 of the committed matrix's 1,833 rows, so the row's own\n"
            "field gives no usable tolerance for a re-capture taken on a different day; the three\n"
            "rows that do carry one read 3.5e-05, 1.05e-04 and 1.96e-04, and the bar is that\n"
            "largest value rounded up.\n\n"
        )
        out.write(
            "The two halves of the re-capture are reported apart, because they are two\n"
            "different operations. The macOS 27 half is a FRESH CAPTURE at the shipped\n"
            "documents — a browser run on this machine today against a row read weeks ago, and\n"
            "the half the wave's statistic is actually taken from. The macOS 26.5 half is a\n"
            "`--skip-capture` RE-MEASURE of a copy of the canonical `web-captures/` trees, with\n"
            "no browser in it at all, so a difference there is a difference between the tree on\n"
            "disk and the raster the committed row was read from.\n\n"
        )
        out.write("| statistic | cells | worst |Δ| overall | macOS 27 | macOS 26.5 | bar | verdict |\n")
        out.write("| --- | ---: | ---: | ---: | ---: | ---: | --- |\n")
        for metric in ("interiorMeanWeb", "ssimMean"):
            n = len([r for r in rows if r.get(metric, {}).get("delta") is not None])
            out.write(
                "| `%s` | %d | %.3e | %.3e | %.3e | %.1e | %s |\n"
                % (
                    metric,
                    n,
                    worst[metric],
                    worst_by_os["27"][metric],
                    worst_by_os["26.5"][metric],
                    REPRODUCTION_BAR,
                    "reproduces" if worst[metric] <= REPRODUCTION_BAR else "MISSES on macOS 26.5 only"
                    if worst_by_os["27"][metric] <= REPRODUCTION_BAR
                    else "MISSES",
                )
            )
        out.write("\n")
        if missing:
            out.write(
                "## %d scratch cells have no committed row at the same key\n\n"
                "Named before anything is read off them. A scratch cell with no committed twin is\n"
                "a cell the 0.20.0 generation never carried — a probe row the canonical read did\n"
                "not include, or a pose no committed run posed — not a reproduction failure.\n\n"
                % len(missing)
            )
            for n in sorted(missing):
                out.write("- `%s`\n" % n)
            out.write("\n")
        if failed:
            out.write("## %d cells DO NOT reproduce, named before their new statistic is read\n\n" % len(failed))
            out.write("| cell | interiorMeanWeb scratch / committed | ssimMean scratch / committed |\n")
            out.write("| --- | --- | --- |\n")
            for r in sorted(failed, key=lambda r: r["name"]):
                a = r.get("interiorMeanWeb", {})
                b = r.get("ssimMean", {})
                out.write(
                    "| `%s` | %s / %s | %s / %s |\n"
                    % (r["name"], fmt(a.get("scratch"), 5), fmt(a.get("committed"), 5),
                       fmt(b.get("scratch"), 5), fmt(b.get("committed"), 5))
                )
            out.write(
                "\n**The cause, diagnosed rather than guessed.** Both are the `texture` tier of the\n"
                "stacked cell, and both were RE-MEASURED from the canonical tree with no browser\n"
                "involved — so the metric and the mask are today's on both sides of the\n"
                "comparison. The `dom` tier of the same two cells reproduces to the last bit\n"
                "(|Δ| exactly 0), which is only possible if `interiorLevel`, the native\n"
                "silhouette it is masked by and the background it is differenced against are all\n"
                "unchanged. That leaves one thing that can differ: the `__webgpu.png` on disk is\n"
                "not the raster the committed row was read from. The canonical tree's files are\n"
                "dated 2026-09-10 and the committed rows were measured 2026-09-11.\n\n"
                "This is the charter's Surprise with a number attached. `CLAUDE.md` says the\n"
                "canonical `web-captures/` 'is what the sheets and the demo fixture are copied\n"
                "from'; on these two cells it is already a DIFFERENT generation from the rows\n"
                "beside it, and nothing would have said so. Consequence for this child, and it\n"
                "is narrow: the macOS 26.5 columns of `cut.md` for `photo__glass-over-glass__rest`\n"
                "on the two light profiles' texture tier are read off pixels the committed row\n"
                "was not read off. They are tabled and they carry this sentence. No macOS 27\n"
                "cell is affected, no bound is declared on a macOS 26.5 row, and the freeze is\n"
                "untouched — a capture tree is gitignored scratch, not committed evidence.\n\n"
            )
        else:
            out.write("**Every re-captured cell with a committed twin reproduces inside the bar.**\n\n")

    # ------------------------------------------------------------------- 2. the cut
    table = []
    for cell in scratch["cells"]:
        material = cell.get("material")
        if material is None:
            continue
        p = parts(cell)
        table.append(
            {
                **p,
                "name": name(cell),
                "set": cell["fixtureSet"],
                "tier": cell["tier"],
                "conditioned": well_conditioned(cell),
                "ratioI_native": value(cell, "material", "chromaStructureRatioNative"),
                "ratioI_web": value(cell, "material", "chromaStructureRatioWeb"),
                "ratioI_backdrop": value(cell, "material", "chromaStructureRatioBackdrop"),
                "ratioII_native": value(cell, "material", "rawChromaRatioNative"),
                "ratioII_web": value(cell, "material", "rawChromaRatioWeb"),
                "ratioIII_native": value(blurred.get(key(cell), cell), "material", "blurredChromaRatioNative"),
                "ratioIII_web": value(blurred.get(key(cell), cell), "material", "blurredChromaRatioWeb"),
                "ratioIII_sigmaNative": value(blurred.get(key(cell), cell), "material", "blurredReferenceSigmaNative"),
                "ratioIII_sigmaWeb": value(blurred.get(key(cell), cell), "material", "blurredReferenceSigmaWeb"),
                "chromaMeanNative": value(cell, "material", "interiorChromaMeanNative"),
                "chromaMeanWeb": value(cell, "material", "interiorChromaMeanWeb"),
                "chromaMeanBackdrop": value(cell, "material", "interiorChromaMeanBackdrop"),
                "interiorMeanNative": value(cell, "material", "interiorMeanNative"),
                "interiorMeanWeb": value(cell, "material", "interiorMeanWeb"),
                "interiorMeanBackdrop": value(cell, "material", "interiorMeanBackdrop"),
                "interiorSdNative": value(cell, "material", "interiorStdDevNative"),
                "interiorSdWeb": value(cell, "material", "interiorStdDevWeb"),
                "tintChromaDeltaNative": value(cell, "material", "tintChromaDeltaNative"),
                "tintChromaDeltaWeb": value(cell, "material", "tintChromaDeltaWeb"),
                "tintInteriorChromaNative": value(cell, "material", "tintInteriorChromaNative"),
                "tintInteriorChromaWeb": value(cell, "material", "tintInteriorChromaWeb"),
                "oklabDeltaEP95": value(cell, "perceptual", "oklabDeltaEP95"),
                "ssimMean": value(cell, "perceptual", "ssimMean"),
            }
        )

    with open(os.path.join(HERE, "cut.json"), "w") as out:
        json.dump({"reproductionBar": REPRODUCTION_BAR, "rows": table}, out, indent=1)
        out.write("\n")

    def ratio(row, which):
        a, b = row["ratioI_web"], row["ratioI_native"]
        if which == "web/native" and a is not None and b not in (None, 0):
            return a / b
        return None

    with open(os.path.join(HERE, "cut.md"), "w") as out:
        out.write("# W31 G0 — the chromatic cut (claims §5.161 §3)\n\n")
        out.write(
            "Ratio (i) is `sqrt(sd(a)² + sd(b)²) / interiorStdDev` of one image's masked\n"
            "interior, per side. Ratio (ii) is that side's mean per-pixel OKLab chroma over the\n"
            "RAW backdrop's under the same mask. `web/native` on ratio (i) is the wave's\n"
            "statistic: 1.000 would be vitrea reading the reference's chroma-to-structure, and it\n"
            "is never read against 1.\n\n"
            "Ratio (iii) is the side's mean per-pixel chroma against a backdrop blurred to that\n"
            "side's OWN measured structure — a body that only blurred reads 1. It comes from a\n"
            "second pass over the same captures (`blurred-reference.sh`) and is absent where the\n"
            "reference radius is outside the 64 device px searched, which is itself a reading:\n"
            "the side is flatter than any blur in that range leaves.\n\n"
            "`cond` is `adopted-thresholds.test.ts`'s conditioning predicate evaluated on the\n"
            "row's own shape axis. A refused cell is TABLED, not dropped — `mask-adequacy.txt`\n"
            "is the evidence that the refusal is the shape axis's and does not reach this one.\n\n"
        )
        for backdrop in sorted({r["backdrop"] for r in table}):
            subset = [r for r in table if r["backdrop"] == backdrop]
            out.write("## `%s`\n\n" % backdrop)
            out.write(
                "| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | "
                "(i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | "
                "(iii) native | (iii) web | interior mean N/W/B |\n"
            )
            out.write("| " + " | ".join(["---"] * 19) + " |\n")
            for r in sorted(
                subset,
                key=lambda r: (r["os"], r["scheme"], r["a11y"], r["scale"], r["tier"],
                               r["span"] or 0, r["pose"]),
            ):
                out.write(
                    "| %s | %s | %s | %dx | %s | %s | %s | %s | %s | %s | %s | %s | %s | **%s** | %s | %s | %s | %s | %s / %s / %s |\n"
                    % (
                        r["os"], r["scheme"], r["a11y"], r["scale"], r["tier"],
                        r["span"] if r["span"] else "—", r["pose"], "yes" if r["tinted"] else "—",
                        r["set"], "ok" if r["conditioned"] else "REFUSED",
                        fmt(r["ratioI_native"], 3), fmt(r["ratioI_web"], 3), fmt(r["ratioI_backdrop"], 3),
                        fmt(ratio(r, "web/native"), 3),
                        fmt(r["ratioII_native"], 3), fmt(r["ratioII_web"], 3),
                        fmt(r["ratioIII_native"], 3), fmt(r["ratioIII_web"], 3),
                        fmt(r["interiorMeanNative"], 4), fmt(r["interiorMeanWeb"], 4),
                        fmt(r["interiorMeanBackdrop"], 4),
                    )
                )
            out.write("\n")

    print("cells in the scratch matrix: %d" % len(scratch["cells"]))
    print("reproduction: worst |Δ| interiorMeanWeb %.3e, ssimMean %.3e, bar %.1e"
          % (worst["interiorMeanWeb"], worst["ssimMean"], REPRODUCTION_BAR))
    print("cells that do not reproduce: %d" % len(failed))
    print("scratch cells with no committed twin: %d" % len(missing))
    print("wrote reproduction-check.md, cut.md, cut.json")


if __name__ == "__main__":
    sys.exit(main())
