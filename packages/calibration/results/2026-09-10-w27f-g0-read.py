"""W27f G0: read frozen, scratch-only captures. No fitting and no renderer changes.

Run with numpy and Pillow installed:
  python this-file.py --scratch /tmp/w27f-g0/final --out /tmp/w27f-g0/final/reading.json
The W23 contour instrument is imported, not reimplemented. Its raw two-row mean
and local excess are recorded separately; neither is an OKLab lightness.

Two provenance rules this reader holds itself to:

* The measured region is the DECLARATION, obtained from `resolveScene` over
  `apps/reference-apple/scenes.json` through `scripts/declared-geometry.ts` — the
  same placement the calibration page lays its hosts out with. A capture's own
  reported bounds are then checked against it. Reading the region off the report
  would move the measurement window with any placement fault and report no fault.
* An arm's route and hint are not taken from the directory it was written to.
  These captures predate the report's `requestedBackdropMode` /
  `requestedBackdropLevel` fields, so their requested axes were configured
  externally (the capture driver's environment) and are CHECKED here against what
  each report did record: `configuredSource`, the resolved `samplingBackend`, and
  the resolved `backdropTone`. Nothing is written back into a frozen report.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "packages/calibration"
PROFILE = "apple-macos-26.5-1x-light-standard"
GEOMETRY = PACKAGE / "scripts/declared-geometry.ts"
W23 = ROOT / "packages/calibration/results/2026-09-08-w23-collapsed-rim/g0/read-contour.py"
spec = importlib.util.spec_from_file_location("w23", W23)
w23 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w23)

# What each web arm was asked for: the sampling route for its raster-backed
# groups, and whether it authored the scene's measured backdrop level. The stack
# overlay is `dom` in every arm and is never handed the raw-raster hint — it sees
# rendered glass — so it is excluded from the route and hint expectations below.
ARMS = {
    "sampledToday": ("texture", False),
    "sampled-hint": ("texture", True),
    "unsampled": ("dom", True),
    "unsampled-nohint": ("dom", False),
    "css": ("dom", True),
    "css-today": ("texture", False),
}
OVERLAY = "component-over"
TOLERANCE = 1e-12


def declared_geometry():
    """The declared placement of every scene, from the shared TypeScript resolver."""
    out = subprocess.run(["npx", "tsx", "scripts/declared-geometry.ts"], cwd=PACKAGE,
                         check=True, capture_output=True, text=True)
    return json.loads(out.stdout)


def check_declared_bounds(where, declared, reported, exact):
    """A report's measured surfaces against the declaration. Returns the size excess.

    Identity, radius and ORIGIN must agree exactly on every capture: a surface
    that landed somewhere else is not the shape this read is measuring, whatever
    the pixels look like. The measured EXTENT is a separate matter — the CSS tier
    lays a border on the host, and the calibration page sizes hosts content-box,
    so its border box is wider than the declaration by that border on each side.
    That excess is a property of the tier, not of a cell, so it is returned to be
    named once rather than tolerated per capture; `exact` refuses it outright for
    a tier that has no such layout.
    """
    if len(declared) != len(reported):
        raise ValueError(f"{where}: {len(reported)} surfaces where the matrix declares {len(declared)}")
    excess = set()
    for want, got in zip(declared, reported):
        for key in ("nodeId", "groupId", "plane", "family", "radius"):
            if want[key] != got.get(key):
                raise ValueError(f"{where}: {key} measured {got.get(key)}, declared {want[key]}")
        box, declared_box = got.get("bounds"), want["bounds"]
        if box is None or box["x"] != declared_box["x"] or box["y"] != declared_box["y"]:
            raise ValueError(f"{where}: measured origin {box}, declared {declared_box}")
        excess.add((box["width"] - declared_box["width"], box["height"] - declared_box["height"]))
    if len(excess) != 1:
        raise ValueError(f"{where}: surfaces disagree about the measured size excess {sorted(excess)}")
    only = excess.pop()
    if exact and only != (0, 0):
        raise ValueError(f"{where}: measured extent exceeds the declaration by {only}")
    return list(only)


def hint_signature(tone, level):
    """Does this resolved tone carry the authored hint rather than an analysis?

    A hint is achromatic and `root.ts` sets its linear mean equal to its level, so
    a hinted group reports three equal channels at exactly the level asked for. A
    sampled group carries an independent linear mean and, over any structured
    raster, three unequal channels. The stack overlay always derives its own tone
    from the glass already rendered beneath it, so it inherits whatever the base
    carried — three unequal channels where the base sampled, three equal ones
    where the base was hinted. Its LEVEL is what separates it either way: it is
    the level of rendered glass, never the raw raster's.
    """
    if tone is None or level is None:
        return False
    r, g, b = tone["rgb"]
    return (abs(r - g) <= TOLERANCE and abs(g - b) <= TOLERANCE
            and abs(tone["linearLuminance"] - tone["level"]) <= TOLERANCE
            and abs(tone["level"] - level) <= TOLERANCE)


def check_requested_axes(name, tier, page, level, structured):
    """The arm's label against the report's own recorded state. Returns the record."""
    mode, hinted = ARMS[name]
    undiscriminable = []
    for group in page["groups"]:
        overlay = group["id"] == OVERLAY
        want_mode = "dom" if overlay else mode
        want_backend = "gpu-texture" if tier == "webgpu" and want_mode == "texture" else "css-backdrop"
        where = f"{name}/{page['sceneId']}/{group['id']}"
        if group["configuredSource"] != want_mode:
            raise ValueError(f"{where}: configuredSource {group['configuredSource']}, expected {want_mode}")
        if group["state"]["samplingBackend"] != want_backend:
            raise ValueError(f"{where}: samplingBackend {group['state']['samplingBackend']}, "
                             f"expected {want_backend}")
        signature = hint_signature(group["backdropTone"], level)
        if hinted and not overlay:
            if not signature:
                raise ValueError(f"{where}: no authored hint in the resolved tone {group['backdropTone']}")
        elif signature:
            # Over a uniform backdrop a sampled tone and the hint taken from it
            # are the same three numbers, so the record cannot separate them.
            # Named rather than raised, and refused where the raster has structure.
            if structured:
                raise ValueError(f"{where}: resolved tone carries the hint but this arm authored none")
            undiscriminable.append(group["id"])
    record = {
        "provenance": "Externally configured by this gate's capture driver environment "
                      "(VITREA_BACKDROP_MODE / VITREA_BACKDROP_LEVELS) and checked here against the "
                      "report's own configuredSource, samplingBackend and backdropTone. These captures "
                      "predate the report's requestedBackdropMode/requestedBackdropLevel fields.",
        "expectedBackdropMode": mode,
        "expectedAuthoredLevel": level if hinted else None,
        "reportedBackdropMode": page.get("requestedBackdropMode"),
        "reportedAuthoredLevel": page.get("requestedBackdropLevel"),
        "hintUndiscriminableGroups": undiscriminable,
    }
    # A capture taken after those fields landed states its own axes; then the
    # externally configured expectation is checked against the record itself.
    if "requestedBackdropMode" in page:
        if page["requestedBackdropMode"] != mode:
            raise ValueError(f"{name}: report requests {page['requestedBackdropMode']}, expected {mode}")
        if page.get("requestedBackdropLevel") != (level if hinted else None):
            raise ValueError(f"{name}: report authors {page.get('requestedBackdropLevel')}, "
                             f"expected {level if hinted else None}")
        record["provenance"] = ("Stated by the capture's own report (requestedBackdropMode / "
                                "requestedBackdropLevel) and checked against the resolved group state.")
    return record


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image(path):
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=float)
    linear = w23.linearise(rgb)
    lms = linear @ np.array([[.4122214708, .5363325363, .0514459929],
                            [.2119034982, .6806995451, .1073969566],
                            [.0883024619, .2817188376, .6299787005]]).T
    lab = np.cbrt(lms) @ np.array([[.2104542553, .7936177850, -.0040720468],
                                  [1.9779984951, -2.4285922050, .4505937099],
                                  [.0259040371, .7827717662, -.8086757660]]).T
    return rgb, linear @ np.array([.2126, .7152, .0722]), lab


def distance(surface, shape):
    """Declared rounded-box SDF, matching component-region.ts at pixel centres."""
    b, r = surface["bounds"], surface["radius"]
    y, x = np.mgrid[:shape[0], :shape[1]]
    qx = np.abs(x + .5 - b["x"] - b["width"] / 2) - b["width"] / 2 + r
    qy = np.abs(y + .5 - b["y"] - b["height"] / 2) - b["height"] / 2 + r
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def finite_mean(values):
    values = np.asarray(values)
    return float(values[np.isfinite(values)].mean()) if np.isfinite(values).any() else None


def read_region(data, native, surfaces, distances, selected):
    rgb, lum, lab = data
    union = np.minimum.reduce(distances)
    footprint = np.zeros(lum.shape, bool)
    interior = np.zeros(lum.shape, bool)
    contour = []
    for i in selected:
        visible = np.ones(lum.shape, bool)
        # Later stack layers cover the base. Siblings on the same plane do not.
        for j in range(i + 1, len(surfaces)):
            if surfaces[j]["plane"] != surfaces[i]["plane"]:
                visible &= distances[j] > 0
        footprint |= (distances[i] <= 0) & visible
        interior |= (distances[i] <= -6) & visible
        s = surfaces[i]
        b = s["bounds"]
        # contour_read centres its box on canvas/2; translating that declared
        # centre lets the unchanged W23 instrument read each composite member.
        canvas = {"width": 2*b["x"] + b["width"], "height": 2*b["y"] + b["height"]}
        _, sides = w23.contour_read(lum, rgb, canvas,
            (b["width"], b["height"], s["radius"]), 1, 6, 2, 1.6)
        contour.append({"surface": s["nodeId"], "sides": sides})
    levels = lab[..., 0][interior]
    rows = [v for c in contour for side in c["sides"].values() for v in side["rows"]]
    excess = [side["rimLocal"] for c in contour for side in c["sides"].values()]
    return {
        "footprintPixels": int(footprint.sum()), "interiorPixels": int(interior.sum()),
        "interiorOklabLMean": float(levels.mean()), "interiorOklabLStddev": float(levels.std()),
        "interiorOklabMean": lab[interior].mean(axis=0).tolist(),
        "interiorLinearRgbMean": w23.linearise(rgb)[interior].mean(axis=0).tolist(),
        "interiorLinearLuminanceMean": float(lum[interior].mean()),
        "footprintLinearLuminanceMean": float(lum[footprint].mean()),
        "deltaEAgainstNative": float(np.linalg.norm(lab-native[2], axis=-1)[footprint].mean()),
        "rimBandLinearMean": finite_mean(rows), "rimLocalExcessMean": finite_mean(excess),
        "contour": contour,
    }


def clean(value):
    if isinstance(value, float) and not np.isfinite(value): return None
    if isinstance(value, dict): return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list): return [clean(v) for v in value]
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    levels = json.loads((args.scratch / "levels.json").read_text())
    matrix = json.loads((ROOT / "apps/reference-apple/scenes.json").read_text())
    scene_specs = {s["id"]: s for s in matrix["scenes"]}
    geometry = declared_geometry()
    css_excess = set()
    rows = []
    for scene in sorted(levels):
        baseline_dir = args.scratch / "sampled" / PROFILE / scene
        baseline_report = json.loads((baseline_dir / "report__webgpu.json").read_text())
        declared = geometry["scenes"][scene]
        surfaces = declared["surfaces"]
        check_declared_bounds(f"sampledToday/{scene}", surfaces,
                              baseline_report["page"]["surfaces"], exact=True)
        native_path = ROOT / "apps/reference-apple/fixtures" / PROFILE / (scene + ".png")
        native = image(native_path)
        background = ROOT / "apps/reference-apple/fixtures/backgrounds" / (declared["backgroundId"] + "@1x.png")
        bg = image(background)
        # Structure in the raster, measured rather than inferred from the id: it
        # is what decides whether a sampled tone and the hint drawn from it are
        # separable in the record at all.
        structured = float(bg[1].std()) > 0
        distances = [distance(s, bg[1].shape) for s in surfaces]
        union = np.minimum.reduce(distances)
        decidable_exterior = (union > 0) & (bg[1] >= .05)
        paths = {"native": native_path, "sampledToday": baseline_dir / (scene + "__webgpu.png")}
        for name, tier in [("sampled-hint", "webgpu"), ("unsampled", "webgpu"),
                           ("unsampled-nohint", "webgpu"), ("css", "css"), ("css-today", "css")]:
            paths[name] = args.scratch / name / PROFILE / scene / (scene + "__" + tier + ".png")
        row = {"scene": scene, "hintedBackdropLevel": levels[scene], "surfaces": surfaces,
               "backgroundSha256": digest(background), "readings": {}}
        for name, path in paths.items():
            data = image(path)
            result = read_region(data, native, surfaces, distances, range(len(surfaces)))
            result["outerShadowExteriorPixels"] = int((decidable_exterior &
                ((bg[1]-data[1]) / np.maximum(bg[1], .00001) > .01)).sum())
            result["decidableExteriorPixels"] = int(decidable_exterior.sum())
            result["sha256"] = digest(path)
            result["perSurface"] = {s["nodeId"]: read_region(data, native, surfaces, distances, [i])
                                    for i, s in enumerate(surfaces)}
            if name != "native":
                tier = "css" if name in ("css", "css-today") else "webgpu"
                report = json.loads((path.parent / ("report__"+tier+".json")).read_text())
                result["measuredBoundsExcess"] = check_declared_bounds(
                    f"{name}/{scene}", surfaces, report["page"]["surfaces"], exact=tier == "webgpu")
                if tier == "css":
                    css_excess.add(tuple(result["measuredBoundsExcess"]))
                if report["page"]["background"]["id"] != declared["backgroundId"]:
                    raise ValueError(f"{name}/{scene}: composited the wrong background raster")
                result["requestedAxes"] = check_requested_axes(
                    name, tier, report["page"], levels[scene], structured)
                # Measured, and kept per arm rather than once: the route decides
                # the ladder, so the DOM arms resolve `approximate` where the
                # texture arms resolve `true`.
                result["surfaceRefraction"] = {s["nodeId"]: s["refraction"]
                                               for s in report["page"]["surfaces"]}
                result["groups"] = report["page"]["groups"]
                result["capturedAt"] = report["capturedAt"]
                result["adapter"] = report["page"]["adapter"]
                result["diagnostics"] = report["page"]["diagnostics"]
                if report["problems"] or report["page"]["problems"]: raise ValueError(report["problems"])
                if any(g["state"]["activeRenderer"] != tier for g in result["groups"]):
                    raise ValueError("Wrong resolved tier")
                cell = json.loads((path.parent / ("cell__"+tier+".json")).read_text())
                result["deterministic"] = cell["deterministic"]
                result["repeatNoise"] = cell["repeatNoise"]
                if not cell["deterministic"] or cell["repeatNoise"] != 0:
                    raise ValueError("Non-deterministic capture")
                if tier == "webgpu" and result["adapter"].get("isFallback") is not False:
                    raise ValueError("Capture requires a measured hardware adapter")
            tint = matrix["tints"].get(scene_specs[scene].get("tint"))
            result["apparentPaintShade"] = None
            if tint is not None and tint.get("alpha", 1) == 1:
                # At full author opacity, projection onto the declared linear
                # seed identifies the observed shade; half tint mixes the body
                # and is intentionally not interpreted as an isolated shade.
                seed = w23.linearise(np.asarray(tint["srgb"], dtype=float))
                mean_rgb = np.asarray(result["interiorLinearRgbMean"])
                shade = float(np.dot(mean_rgb, seed) / np.dot(seed, seed))
                result["apparentPaintShade"] = shade
                result["paintOffSeedRgbNorm"] = float(np.linalg.norm(mean_rgb - shade * seed))
            row["readings"][name] = result
        rows.append(row)
    if len(css_excess) != 1:
        raise ValueError(f"The CSS arms do not share one measured size excess: {sorted(css_excess)}")
    out = {"date": "2026-09-10", "gate": "W27f G0", "profile": PROFILE,
           "baseCommit": "80a745b",
           "captureRoot": str(args.scratch.resolve()),
           "sceneManifestSha256": digest(ROOT / "apps/reference-apple/scenes.json"),
           "nativeManifestSha256": digest(ROOT / "apps/reference-apple/fixtures/manifest.json"),
           "materialProfileSha256": digest(ROOT / "packages/calibration/profiles" / (PROFILE + ".json")),
           "contourInstrumentSha256": digest(W23),
           "declaredGeometrySource": geometry["source"],
           "declaredGeometryScriptSha256": digest(GEOMETRY),
           "cssTierMeasuredSizeExcessCssPx": list(sorted(css_excess)[0]),
           "method": {
               "geometry": "Every measured region is the DECLARATION, resolved by scripts/declared-geometry.ts "
                           "over apps/reference-apple/scenes.json, and every report's measured surface identity, "
                           "radius and ORIGIN are checked to agree with it. No region is read off the capture "
                           "being measured. The measured EXTENT agrees exactly on every GPU-tier capture; every "
                           "CSS-tier capture measures cssTierMeasuredSizeExcessCssPx larger, because that tier "
                           "lays a border on the host and the calibration page sizes hosts content-box. The "
                           "declared region is measured either way, so the CSS rows read the declaration and not "
                           "the outermost CSS px that tier covered.",
               "requestedAxes": "Each arm's route and authored level are checked against the report's recorded "
                                "configuredSource, samplingBackend and backdropTone; the overlay is dom in every "
                                "arm and never carries the raw-raster hint. Where the raster is uniform a sampled "
                                "tone and the hint taken from it are the same numbers, and the arm is named as "
                                "undiscriminable from the record rather than asserted.",
               "footprint": "Declared circular rounded-box SDF at pixel centres, visible union; base excludes overlay.",
               "interior": "Declared footprint eroded 6 CSS px; mean and population standard deviation of per-pixel OKLab L.",
               "deltaE": "Mean Euclidean OKLab distance over declared visible footprint (not full canvas).",
               "rim": "Unchanged W23 contour_read: first 2 CSS px, corner factor 1.6; raw linear row mean and local excess. Empty straight spans are null.",
               "shadow": "Scene-wide count outside ALL declared shapes with background linear luminance >=0.05 and relative occlusion >0.01. Black pixels undecidable. Stack overlay shadow cannot be separated from base without an intervention.",
               "hints": "Actual baseline sampled backdropTone.level, same on hinted texture and DOM base groups. Hints are achromatic and set linear mean equal to level; sampledToday preserves that separate information loss. Stack overlays retain their real stacked-tone derivation, never the raw-raster hint.",
               "stack": "Both requested holdout cells, once per frozen configuration; overlay remains css-backdrop even in sampled-labelled scenes. No true texture sample of already-rendered glass exists here.",
           }, "rows": rows}
    args.out.write_text(json.dumps(clean(out), indent=2, allow_nan=False) + "\n")
    for r in rows:
        a,b = r["readings"]["sampled-hint"],r["readings"]["unsampled"]
        print(r["scene"],f'{a["deltaEAgainstNative"]:.5f}',f'{b["deltaEAgainstNative"]:.5f}',
              f'{b["interiorOklabLMean"]-a["interiorOklabLMean"]:+.5f}')


if __name__ == "__main__": main()
