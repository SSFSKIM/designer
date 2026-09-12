#!/usr/bin/env python3
"""W27e G2's 1x both-pose reading, walked out of the raw dumps.

Claims §5.138; declared in `declaration.md` beside this file before anything here
was read. It answers the four questions that declaration names — the surface
operator per pose, the label operator per pose, the author tint, and the third
window state — and it resolves claims §5.137 §6's four outcomes.

This is a SECOND implementation on purpose. `scripts/vibrancy.ts --corpus probe-1x`
writes `table.json` and `table.md` beside this file from the same 150 dumps; this
walks the JSON itself with no shared code, so the numbers §5.138 publishes are
two independent passes agreeing rather than one pass quoted twice. Where the two
disagree the reading is void — `verify.matches` below records the comparison.

Nothing here decodes a pixel, calls the capture harness or writes anything under a
dump tree. Writes `reading.json` beside itself.
"""
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "reading.json")

CORPUS = os.path.join(RESULTS, "2026-09-12-w27e-probe-1x")
ARMS = ("active", "policy-only", "recede")
SCHEMES = ("light", "dark")
# The 2x corpus of §5.136, read only to place this one against it, and the 1x key
# corpus of §5.133, read for the same reason. Neither is re-published here.
PROBE_2X = os.path.join(RESULTS, "2026-09-11-w27e-probe")
G0_TREES = (
    os.path.join(RESULTS, "2026-09-03-w12-lens", "layer-dumps"),
    os.path.join(RESULTS, "2026-09-03-w12-lens", "layer-dumps-ramp"),
    os.path.join(RESULTS, "2026-09-03-w12-lens", "layer-dumps-adapt"),
    os.path.join(RESULTS, "2026-09-05-w18-union-contour", "probe", "layer-dumps"),
    os.path.join(RESULTS, "2026-09-05-w20-capsule-corner", "g0", "layer-dumps"),
)

DRAWING = "CGDrawingLayer"
HIGHLIGHT = "CASDFKeyFillHighlightEffect"
GRADIENT = "CASDFGradientEffect"


def walk(layer, path="0"):
    yield path, layer
    for i, child in enumerate(layer.get("sublayers") or []):
        yield from walk(child, "%s.%d" % (path, i))


def role_of(layer):
    effect = ((layer.get("properties") or {}).get("effect") or {}).get("class")
    if effect == HIGHLIGHT:
        return "surface-highlight"
    if effect == GRADIENT:
        return "author-tint"
    if DRAWING in layer.get("class", ""):
        return "content-label"
    return "unclassified"


def occurrences(doc):
    """Every `vibrantColorMatrix` in a dump, with the layer it sits on."""
    out = []
    for path, layer in walk(doc["view"]["layer"]):
        for f in layer.get("filters") or []:
            if f.get("description") != "vibrantColorMatrix":
                continue
            inputs = f.get("inputs") or {}
            out.append({
                "layerPath": path,
                "layerClass": layer.get("class"),
                "layerOpacity": layer.get("opacity"),
                "role": role_of(layer),
                "matrix": (inputs.get("inputColorMatrix") or {}).get("float32"),
                "inputBackdropAware": inputs.get("inputBackdropAware"),
                "inputClamp": inputs.get("inputClamp"),
                "inputClampPreserveHue": inputs.get("inputClampPreserveHue"),
            })
    return out


def surfaces(doc):
    """Every `CABackdropLayer` carrying `glassBackground` in a tree."""
    found = []
    for _, layer in walk(doc["view"]["layer"]):
        if layer.get("class") != "CABackdropLayer":
            continue
        for f in layer.get("filters") or []:
            if f.get("description") == "glassBackground":
                found.append((layer, f))
    return found


def glass(doc):
    """The one glass surface a tree holds, and its own adapted state.

    Every scene in this corpus declares one control, so a tree holding other than
    one glass surface is a scene the reading does not understand and is refused
    rather than resolved by picking one (declaration §5, stop S5). The G0 corpus
    holds one scene that is two surfaces; it is excluded from the cross-check by
    name rather than resolved here.
    """
    found = surfaces(doc)
    if len(found) != 1:
        raise SystemExit("%s: %d glass surfaces, not one" % (doc["scene"], len(found)))
    layer, f = found[0]
    inputs = f.get("inputs") or {}
    fill = inputs.get("inputFaceColorMatrixFillColor")
    props = layer.get("properties") or {}
    return {
        "tracksLuma": props.get("tracksLuma"),
        "marginWidth": props.get("marginWidth"),
        "scale": props.get("scale"),
        "faceColorMatrixBlack": inputs.get("inputFaceColorMatrixBlack"),
        "faceColorMatrixWhite": inputs.get("inputFaceColorMatrixWhite"),
        # The body's own adapted state, in one bit: Apple flips the face fill from
        # white to black when the glass adapts, which §5.133 §4 found co-varies
        # with the vibrancy operator on the two cells it had. Here it is the axis.
        "faceFillIsDark": bool(fill and (fill.get("cgColorComponents") or [1])[0] == 0),
        "shadowFillIsNil": inputs.get("inputShadowColorMatrixFillColor") is None,
    }


def load(directory):
    """Every dump in a directory, with the repo-relative path the reader names it by.

    The path travels with the document because the cross-check below joins this
    pass to `table.json` on it: the two passes number their operators in their own
    first-seen order, so nothing may be compared by id, and a dump path plus a
    layer path is the only key both sides agree on without sharing code.
    """
    out = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".json") or name == "scenes.json":
            continue
        full = os.path.join(directory, name)
        rel = "packages/calibration/results/%s" % os.path.relpath(full, RESULTS)
        with open(full, "r", encoding="utf8") as fh:
            out.append((rel, json.load(fh)))
    return out


def cells(dumps, arm=None, skipped=None):
    """One record per dump: the pose, the three operators, the body's state.

    `skipped` collects the scenes a single-surface reading cannot describe, which
    is how the G0 corpus's one stacked scene stays named rather than resolved. The
    probe corpora declare one control per scene, so passing no collector there
    turns a second surface into a stop.
    """
    rows = []
    for path, doc in dumps:
        if skipped is not None and len(surfaces(doc)) != 1:
            skipped.append(doc["scene"])
            continue
        occ = occurrences(doc)
        by_role = defaultdict(list)
        for o in occ:
            by_role[o["role"]].append(o)
        if by_role["unclassified"]:
            raise SystemExit("%s: an occurrence on no known layer family" % doc["scene"])
        if len(by_role["surface-highlight"]) != 1:
            raise SystemExit("%s: %d highlight occurrences, not one"
                             % (doc["scene"], len(by_role["surface-highlight"])))
        labels = [l for _, l in walk(doc["view"]["layer"]) if DRAWING in l.get("class", "")]
        highlight = by_role["surface-highlight"][0]
        label = by_role["content-label"][0] if by_role["content-label"] else None
        spans = [min(l["frame"]["width"], l["frame"]["height"])
                 for _, l in walk(doc["view"]["layer"])
                 if l.get("class") == "CASDFElementLayer"
                 and l["frame"]["width"] > 0 and l["frame"]["height"] > 0]
        rows.append({
            "arm": arm,
            "path": path,
            "scene": doc["scene"],
            "background": doc["background"],
            "span": min(spans) if spans else None,
            "colorScheme": doc["colorScheme"],
            "scale": doc["backingScaleFactor"],
            "a11y": doc["a11y"],
            "settleSeconds": doc["settleSeconds"],
            "os": doc["os"],
            "isKeyWindow": doc["isKeyWindow"],
            "appIsActive": doc.get("appIsActive", "not recorded"),
            "activationPolicy": doc.get("activationPolicy", "not recorded"),
            "declaredLabelSrgb": (doc.get("label") or {}).get("srgb") if doc.get("label") else None,
            "declaresLabel": doc.get("label") is not None,
            "labelLayers": len(labels),
            "labelLayersWithOperator": sum(
                1 for l in labels
                if any(f.get("description") == "vibrantColorMatrix" for f in (l.get("filters") or []))),
            "highlight": highlight,
            "label": label,
            "tints": by_role["author-tint"],
            "glass": glass(doc),
        })
    return rows


def key_of(matrix):
    return json.dumps(matrix)


def catalogue(rows):
    """Distinct matrices, numbered in first-seen order, with what carries them."""
    seen = {}
    for row in rows:
        for o in [row["highlight"]] + ([row["label"]] if row["label"] else []) + row["tints"]:
            k = key_of(o["matrix"])
            if k not in seen:
                seen[k] = {"id": len(seen), "matrix": o["matrix"], "roles": set(), "count": 0}
            seen[k]["roles"].add(o["role"])
            seen[k]["count"] += 1
    return {k: v for k, v in seen.items()}


def within_tolerance(cat, tolerance=1e-6):
    """Which exact-byte classes are one operator at the reader's own tolerance."""
    values = sorted(cat.values(), key=lambda v: v["id"])
    merged, pairs = [], []
    for v in values:
        for m in merged:
            gap = max(abs(a - b) for a, b in zip(m[0]["matrix"], v["matrix"]))
            if gap <= tolerance:
                m.append(v)
                pairs.append({"ids": [m[0]["id"], v["id"]], "maxCoefficientGap": gap})
                break
        else:
            merged.append([v])
    return {"tolerance": tolerance, "byteClasses": len(values), "operators": len(merged),
            "merged": pairs}


def verify(rows, group_of, high_ids_by_matrix):
    """This pass against `scripts/vibrancy.ts`'s, quantity by quantity.

    The module header promises that a disagreement voids the reading, so the
    comparison has to exist and has to be able to fail. It joins on the pair
    (dump path, layer path) — the only key two implementations that number their
    own operators can share — and compares the matrix itself rather than either
    side's operator id. `matches` is the whole verdict; `differences` names every
    quantity that moved, so a failure says which one rather than only that one did.
    """
    table_path = os.path.join(HERE, "table.json")
    if not os.path.exists(table_path):
        return {"matches": None, "reason": "table.json has not been written yet",
                "table": table_path}
    with open(table_path, "r", encoding="utf8") as fh:
        table = json.load(fh)

    def reader_group(row):
        # The arm is the directory the reader read the dump out of, which is the
        # same rule `armOf` applies on the TypeScript side.
        return "%s/%s/%s" % (row["dump"].split("/")[4], row["colorScheme"],
                             "key" if row["isKeyWindow"] else "non-key")

    mine, theirs = {}, {}
    for r in rows:
        for occ in [r["highlight"]] + ([r["label"]] if r["label"] else []) + r["tints"]:
            mine[(r["path"], occ["layerPath"])] = {
                "role": occ["role"], "matrix": occ["matrix"],
                "layerOpacity": occ["layerOpacity"], "group": group_of(r),
                "scene": r["scene"], "marginWidth": r["glass"]["marginWidth"],
                "faceFillIsDark": r["glass"]["faceFillIsDark"],
            }
    for row in table["rows"]:
        theirs[(row["dump"], row["layerPath"])] = {
            "role": row["role"], "matrix": row["matrix"],
            "layerOpacity": row["layerOpacity"], "group": reader_group(row),
            "scene": row["scene"], "marginWidth": row["surface"]["marginWidth"],
            "faceFillIsDark": row["body"]["faceFillIsDark"],
        }

    differences = []
    if sorted(mine) != sorted(theirs):
        only_mine = sorted(set(mine) - set(theirs))[:5]
        only_theirs = sorted(set(theirs) - set(mine))[:5]
        differences.append({"quantity": "occurrence keys",
                            "onlyInThisPass": only_mine, "onlyInReader": only_theirs})
    for key in sorted(set(mine) & set(theirs)):
        a, b = mine[key], theirs[key]
        for field in ("role", "matrix", "layerOpacity", "group", "scene", "marginWidth",
                      "faceFillIsDark"):
            if a[field] != b[field]:
                differences.append({"quantity": field, "key": list(key),
                                    "thisPass": a[field], "reader": b[field]})

    # The aggregates §5.138 quotes, recomputed from the reader's own rows and its
    # own per-group summary, so a divergence in how either side GROUPS shows up
    # even when every occurrence matches.
    def from_reader():
        out = {}
        for g in table["summary"]["groups"]:
            name = "%s/%s/%s" % (g["arm"], g["colorScheme"],
                                 "key" if g["isKeyWindow"] else "non-key")
            out[name] = {
                "dumps": g["dumps"],
                "highlightOccurrences": g["surfaceHighlight"]["occurrences"],
                "labelOccurrences": g["contentLabel"]["occurrences"],
                "tintOccurrences": g["authorTint"]["occurrences"],
                "highlightLayerOpacities": sorted(g["surfaceHighlight"]["layerOpacities"]),
                "highGainScenes": sorted(
                    s for o in g["surfaceHighlight"]["operators"]
                    if json.dumps(next(r["matrix"] for r in table["rows"]
                                       if r["operatorId"] == o["operatorId"])) in high_ids_by_matrix
                    for s in o["scenes"]),
            }
        return out

    def from_mine():
        out = {}
        for g in sorted({group_of(r) for r in rows}):
            ours = [r for r in rows if group_of(r) == g]
            out[g] = {
                "dumps": len(ours),
                "highlightOccurrences": len(ours),
                "labelOccurrences": sum(1 for r in ours if r["label"]),
                "tintOccurrences": sum(len(r["tints"]) for r in ours),
                "highlightLayerOpacities": sorted({r["highlight"]["layerOpacity"] for r in ours}),
                "highGainScenes": sorted(
                    r["scene"] for r in ours
                    if key_of(r["highlight"]["matrix"]) in high_ids_by_matrix),
            }
        return out

    a, b = from_mine(), from_reader()
    if sorted(a) != sorted(b):
        differences.append({"quantity": "group names",
                            "thisPass": sorted(a), "reader": sorted(b)})
    for g in sorted(set(a) & set(b)):
        for field in sorted(a[g]):
            if a[g][field] != b[g][field]:
                differences.append({"quantity": "%s / %s" % (g, field),
                                    "thisPass": a[g][field], "reader": b[g][field]})

    return {
        "matches": not differences,
        "table": "table.json",
        "occurrencesCompared": len(set(mine) & set(theirs)),
        "groupsCompared": len(set(a) & set(b)),
        "fieldsPerOccurrence": ["role", "matrix", "layerOpacity", "group", "scene",
                                "marginWidth", "faceFillIsDark"],
        "differences": differences,
    }


def main():
    arms = {arm: {s: cells(load(os.path.join(CORPUS, arm, s)), arm) for s in SCHEMES}
            for arm in ARMS}
    rows = [r for arm in ARMS for s in SCHEMES for r in arms[arm][s]]

    # --- stops, before anything is concluded -------------------------------
    stops = {
        "S1_dumpsPerArmScheme": {"%s/%s" % (a, s): len(arms[a][s]) for a in ARMS for s in SCHEMES},
        "S2_scales": sorted({r["scale"] for r in rows}),
        "S2_a11y": sorted({r["a11y"] for r in rows}),
        "S2_settleSeconds": sorted({r["settleSeconds"] for r in rows}),
        "S2_os": sorted({r["os"] for r in rows}),
        "S4_highlightOpacityInKeyPose": sorted(
            {r["highlight"]["layerOpacity"] for r in rows if r["isKeyWindow"]}),
    }

    cat = catalogue(rows)
    ids = {k: v["id"] for k, v in cat.items()}
    for r in rows:
        r["highlightOperator"] = ids[key_of(r["highlight"]["matrix"])]
        r["labelOperator"] = ids[key_of(r["label"]["matrix"])] if r["label"] else None
        r["tintOperators"] = sorted({ids[key_of(t["matrix"])] for t in r["tints"]})

    def group(r):
        return "%s/%s/%s" % (r["arm"], r["colorScheme"], "key" if r["isKeyWindow"] else "non-key")

    groups = sorted({group(r) for r in rows})
    per_group = {}
    for g in groups:
        mine = [r for r in rows if group(r) == g]
        per_group[g] = {
            "dumps": len(mine),
            "appIsActive": sorted({str(r["appIsActive"]) for r in mine}),
            "activationPolicy": sorted({str(r["activationPolicy"]) for r in mine}),
            "highlightLayerOpacity": sorted({r["highlight"]["layerOpacity"] for r in mine}),
            "backdropMarginWidth": sorted({r["glass"]["marginWidth"] for r in mine}),
            "highlightOperators": dict(Counter(r["highlightOperator"] for r in mine)),
            "highlightOperatorByScene": {
                str(op): sorted(r["scene"] for r in mine if r["highlightOperator"] == op)
                for op in sorted({r["highlightOperator"] for r in mine})},
            "labelOperators": dict(Counter(r["labelOperator"] for r in mine if r["label"])),
            "labelLayerOpacity": sorted({r["label"]["layerOpacity"] for r in mine if r["label"]}),
            "labelLayersCommitted": sum(r["labelLayers"] for r in mine),
            "labelLayersWithOperator": sum(r["labelLayersWithOperator"] for r in mine),
            "tintOperators": dict(Counter(op for r in mine for op in r["tintOperators"])),
            "tintLayerOpacity": sorted({t["layerOpacity"] for r in mine for t in r["tints"]}),
        }

    # --- the law: the operator is a function of the body's own adapted state ---
    def covariation(rs, high_ids):
        bad = [r for r in rs if (r["highlightOperator"] in high_ids) != r["glass"]["faceFillIsDark"]]
        badshadow = [r for r in rs
                     if (r["highlightOperator"] in high_ids) != r["glass"]["shadowFillIsNil"]]
        return {"rows": len(rs), "faceFillViolations": len(bad),
                "shadowFillViolations": len(badshadow)}

    # The high-gain operator is the one whose fifth column is 0.15 — read from the
    # matrix rather than from a count, so it is named the same way in every corpus.
    high = {v["id"] for v in cat.values()
            if v["matrix"][4] == 0.15 or abs(v["matrix"][4] - 0.15) < 1e-6}
    law = covariation(rows, high)

    label_law = {"labelled": 0, "violations": []}
    for r in rows:
        if not r["label"]:
            continue
        label_law["labelled"] += 1
        lightening = abs(r["label"]["matrix"][4] - 1.0) < 1e-6
        if lightening != r["glass"]["faceFillIsDark"]:
            label_law["violations"].append("%s %s" % (group(r), r["scene"]))

    # --- where the groups disagree, which is what bounds any selector law -----
    #
    # Per scene AND per scheme: the two schemes are expected to differ and pooling
    # them would report every scene as split. What is read here is whether the SAME
    # cell, in the same scheme, carries the same operator through all the window
    # states the corpus reaches — because a cell that does not is a bound on how
    # tightly any selector law can be stated, whatever the law is.
    scenes = sorted({(r["colorScheme"], r["scene"]) for r in rows})
    unanimous, split = [], {}
    for scheme, s in scenes:
        mine = [r for r in rows if r["scene"] == s and r["colorScheme"] == scheme]
        if len({r["highlightOperator"] for r in mine}) == 1:
            unanimous.append("%s %s" % (scheme, s))
        else:
            split["%s %s" % (scheme, s)] = {group(r): r["highlightOperator"] for r in mine}

    # --- the one law the whole corpus is scored against ----------------------
    #
    # Stated over the dump's own fields — the background's name and the declared
    # span — rather than over a decoded luminance, so this pass needs no fixture:
    # the tone each background carries is in `table.json` beside this file, and
    # what matters here is which cells the law puts on which side.
    #
    # Every surface sits at its SCHEME's base state — the default operator in
    # light, the high-gain one in dark — and adapts to the other when the backdrop
    # is far enough the other way. In light that is the two darkest backgrounds
    # (`dark-solid` at linear 0.011711, `impulse` at 0.003284) and only while the
    # span is small; in dark it is the brightest (`light-solid` at 0.890969), at
    # every span the corpus holds. This is a DESCRIPTION of these 150 rows, not a
    # fitted selector: §5.138 declares none and Decision Log 15 (c) is the user's.
    def predicted_high_gain(row):
        if row["colorScheme"] == "light":
            return row["background"] in ("dark-solid", "impulse") and row["span"] <= 64
        return row["background"] != "light-solid"

    deviants = [{"group": group(r), "scene": r["scene"], "background": r["background"],
                 "span": r["span"], "observedHighGain": r["highlightOperator"] in high,
                 "predictedHighGain": predicted_high_gain(r)}
                for r in rows if (r["highlightOperator"] in high) != predicted_high_gain(r)]
    law_check = {
        "rows": len(rows),
        "agreeing": len(rows) - len(deviants),
        "deviants": deviants,
        "spansByBackgroundLight": sorted({
            "%s@%s" % (r["background"], r["span"]) for r in rows if r["colorScheme"] == "light"}),
    }

    # --- the brackets the corpus draws ---------------------------------------
    def bracket(scheme):
        mine = [r for r in rows if r["colorScheme"] == scheme]
        hi = [r for r in mine if r["highlightOperator"] in high]
        lo = [r for r in mine if r["highlightOperator"] not in high]
        return {
            "highGain": len(hi), "default": len(lo),
            "tracksLumaOnHighGain": sorted({r["glass"]["tracksLuma"] for r in hi}),
            "tracksLumaOnDefault": sorted({r["glass"]["tracksLuma"] for r in lo}),
        }

    # --- across the scales ----------------------------------------------------
    two_x = cells(load(os.path.join(PROBE_2X, "light")), "2x") \
        + cells(load(os.path.join(PROBE_2X, "dark")), "2x")
    for r in two_x:
        r["highlightOperator"] = key_of(r["highlight"]["matrix"])
    recede = {(r["colorScheme"], r["scene"]): key_of(r["highlight"]["matrix"])
              for r in rows if r["arm"] == "recede"}
    differ = sorted("%s %s" % (r["colorScheme"], r["scene"]) for r in two_x
                    if recede[(r["colorScheme"], r["scene"])] != r["highlightOperator"])
    # The label half of the same comparison, which §5.138 §4 publishes as 5 of 24
    # and this pass previously took on trust from the reader rather than deriving.
    recede_labels = {(r["colorScheme"], r["scene"]): key_of(r["label"]["matrix"])
                     for r in rows if r["arm"] == "recede" and r["label"]}
    labels_2x = [r for r in two_x if r["label"]]
    labels_differ = sorted("%s %s" % (r["colorScheme"], r["scene"]) for r in labels_2x
                           if recede_labels.get((r["colorScheme"], r["scene"]))
                           != key_of(r["label"]["matrix"]))
    # `tracksLuma` by declared span at each scale, COMPUTED rather than asserted:
    # if the flag were computed on device pixels the 2x tally would move, and the
    # claim that it does not is load-bearing for §5.138 §4's refutation.
    def tracks_luma_by_span(rs):
        out = defaultdict(set)
        for r in rs:
            out[str(r["span"])].add(r["glass"]["tracksLuma"])
        return {span: sorted(v) for span, v in sorted(out.items(), key=lambda kv: float(kv[0]))}

    across = {
        "dumps2x": len(two_x),
        "2xHighlightLayerOpacity": sorted({r["highlight"]["layerOpacity"] for r in two_x}),
        "2xMarginWidth": sorted({r["glass"]["marginWidth"] for r in two_x}),
        "2xIsKeyWindow": sorted({r["isKeyWindow"] for r in two_x}),
        "2xFaceFillIsDarkByScheme": {
            s: sorted({r["glass"]["faceFillIsDark"] for r in two_x if r["colorScheme"] == s})
            for s in SCHEMES},
        "tracksLumaByDeclaredSpan": {
            "1x": tracks_luma_by_span(rows),
            "2x": tracks_luma_by_span(two_x),
        },
        "tracksLumaBySpanIsUnchangedAcrossScales":
            tracks_luma_by_span(rows) == tracks_luma_by_span(two_x),
        "scenesDifferingFrom1xRecede": differ,
        "labels2x": len(labels_2x),
        "labelScenesDifferingFrom1xRecede": labels_differ,
    }

    # G0's corpus, for the same body law and for the one scene id that moved.
    g0_skipped = []
    g0 = [r for tree in G0_TREES for r in cells(load(tree), "g0", g0_skipped)]
    g0_ids = {}
    for r in g0:
        g0_ids.setdefault(key_of(r["highlight"]["matrix"]), len(g0_ids))
    g0_high = {k for k in g0_ids if abs(json.loads(k)[4] - 0.15) < 1e-6}
    g0_law = {"rows": len(g0), "scenesExcludedAsTwoSurfaces": sorted(set(g0_skipped)),
              "faceFillViolations": sum(
                  1 for r in g0
                  if (key_of(r["highlight"]["matrix"]) in g0_high) != r["glass"]["faceFillIsDark"])}
    # G0's 57 dumps are light, 1x, key, so only this corpus's LIGHT groups are
    # comparable with them; putting a dark group beside a light reading would
    # report the scheme as a disagreement.
    shared = sorted({r["scene"] for r in g0} & {r["scene"] for r in rows})
    light_rows = [r for r in rows if r["colorScheme"] == "light"]
    g0_compare = {}
    for s in shared:
        g0_m = sorted({key_of(r["highlight"]["matrix"]) for r in g0 if r["scene"] == s})
        g0_compare[s] = {
            "g0Matrices": len(g0_m),
            "agreesWith": sorted({group(r) for r in light_rows
                                  if r["scene"] == s and key_of(r["highlight"]["matrix"]) in g0_m}),
            "differsFrom": sorted({group(r) for r in light_rows
                                   if r["scene"] == s and key_of(r["highlight"]["matrix"]) not in g0_m}),
        }

    checked = verify(rows, group, {k for k, v in cat.items() if v["id"] in high})

    result = {
        "declaredIn": "W27 coverage wave, W27e G2; claims §5.138; Decision Log 15 (c);"
                      " the four-outcome reading of claims §5.137 §6",
        "corpus": CORPUS.split("results/")[-1],
        # The two-implementation check the module header promises. `matches` false
        # voids the reading; `matches` null means `table.json` is not written yet,
        # which is the state on a first run into a clean directory.
        "verify": checked,
        "stops": stops,
        "operators": [{"id": v["id"], "count": v["count"], "roles": sorted(v["roles"]),
                       "matrix": v["matrix"]}
                      for v in sorted(cat.values(), key=lambda v: v["id"])],
        # This pass groups matrices on exact equality; `scripts/vibrancy.ts` groups
        # them within 1e-6 on every coefficient. The two counts differ by the pairs
        # below, which are the same operator written twice by float32 — recorded
        # rather than smoothed away, because "nine byte-classes, eight operators"
        # is the honest statement and a reader comparing the two tables needs it.
        "matricesWithinReaderTolerance": within_tolerance(cat),
        "highGainOperatorIds": sorted(high),
        "groups": per_group,
        "bodyLaw": {
            "thisCorpus": law,
            "g0Corpus": g0_law,
            "label": {"labelled": label_law["labelled"],
                      "violations": label_law["violations"]},
        },
        "sceneAgreement": {"unanimousAcrossAllGroups": len(unanimous),
                           "split": split},
        "lawCheck": law_check,
        "brackets": {s: bracket(s) for s in SCHEMES},
        "acrossScales": across,
        "againstG0": g0_compare,
        "labelHot": sorted(
            "%s %s layers=%d withOperator=%d srgb=%s"
            % (group(r), r["scene"], r["labelLayers"], r["labelLayersWithOperator"],
               r["declaredLabelSrgb"])
            for r in rows if r["scene"].endswith("label-hot")),
        "labelFlags": sorted({"%s/%s/%s" % (r["label"]["inputBackdropAware"],
                                            r["label"]["inputClamp"],
                                            r["label"]["inputClampPreserveHue"])
                              for r in rows if r["label"]}),
        "highlightFlags": sorted({"%s/%s/%s" % (r["highlight"]["inputBackdropAware"],
                                                r["highlight"]["inputClamp"],
                                                r["highlight"]["inputClampPreserveHue"])
                                  for r in rows}),
        "tintFlags": sorted({"%s/%s/%s" % (t["inputBackdropAware"], t["inputClamp"],
                                           t["inputClampPreserveHue"])
                             for r in rows for t in r["tints"]}),
    }

    with open(OUT, "w", encoding="utf8") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("%d dumps, %d matrix byte-classes; body law %d/%d, label law %d/%d; %d of %d"
          " scene-and-scheme cells carry one operator through every window state"
          % (len(rows), len(cat), law["rows"] - law["faceFillViolations"], law["rows"],
             label_law["labelled"] - len(label_law["violations"]), label_law["labelled"],
             len(unanimous), len(scenes)))
    print("verify against table.json: matches=%s over %s occurrences and %s groups%s"
          % (checked["matches"], checked.get("occurrencesCompared"),
             checked.get("groupsCompared"),
             "" if checked["matches"] is not False
             else " — %d differences, the reading is VOID" % len(checked["differences"])))
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
