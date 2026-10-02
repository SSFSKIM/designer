#!/usr/bin/env python3.12
"""W43 G3 (i), clause 10 step 1: the 0.25 adopted rows, implemented before any candidate is judged.

Decision Log 5 as RULED by the user on 2026-10-02 ("Adopt all eleven recommendations"; Decision
Log 7 items 10 and 11), re-instantiated over the four ``-glass0.25`` standard profiles:

  tables  the 0.5 standard tables' values per tier (W29 Decision Log 4 (a)'s form): each 0.25
          profile carries its 0.5 twin's TEXTURE / DOM table, read OUT OF
          ``test/adopted-thresholds.test.ts`` (the 27 tables are aliases of the 26.5 ones there,
          and the alias is followed, never transcribed by hand). Gated bed as the owner test's:
          active pose, calibration and validation (holdout never read here), no probe, no
          recorded; perceptual rows on every cell, shape rows on cells with a shape axis that
          pass the conditioning predicate. No floor (Decision Log 5 (d)): a miss is a miss, and
          a row without the metric is listed with the misses (status UNMEASURED) and reads MISS.
  M1      the body's chroma-to-structure ratio R = web / native on the untinted photo cells,
          calibration and validation, both poses, WebGPU: median per scheme and pose in
          [0.8, 1.2], every cell in [0.6, 1.4].
  M2      directional (W42 Decision Log 5a's form): interiorStdDevWeb against the REFERENCE, the
          pre-fit render's reading on the same cell; a cell misses at |w - r| / r > 2 %; a miss
          is NAMED when it moves toward Apple's interiorStdDevNative and not past it by more
          than 2 % of Apple's value, a FAILURE otherwise (away, past by more, or any move where
          Apple sits on the reference).
  C1      the shadow's exterior shape per bed x span (W32): T = band-width-weighted mean of
          |slopeA web - native| over the span's admitted bands, active WebGPU standard
          non-holdout non-recorded cells carrying the whole admitted set and backdrop support
          >= 0.1; the upper middle per (scale, scheme, span) <= 0.0042.
  X1      the native-black exterior stays black (W33): on black backdrops, 2 device px outside
          the declared rect (integer and analytic masks), where native is black, the web
          maximum channel is 0 on every pixel. Read from the bed's own capture tree.
  L1      fixed-native-silhouette level (W36): |interiorMeanWeb - interiorMeanNative| <= 0.055
          on the WebGPU calibration/validation cells, and its growth against the pre-fit
          render's error <= 0.005. The two clauses are evaluated apart: a cell whose own means
          are missing is UNMEASURED on both, one whose pre-fit row carries no web mean is
          UNMEASURED on the growth clause (``growthUnmeasured``), and each is named and
          counted against the verdict, never a pass.
  E2      per cell in absolute codes (W42 Decision Log 5e's form) over E2's own bins and
          population rule (W38 ``e2.py``): per bin the mean |web - native| per channel; per
          cell the mean over its measured bins and channels; a cell FAILS iff that mean exceeds
          the pre-fit render's; every bin worse than the pre-fit's by more than 1 code on a
          channel is listed as a named miss (recorded, never a gate). No measured bin:
          UNMEASURED, never a pass.
  S1      as R2 (Decision Log 7 item 11): over ``s1/r2-population.json``'s interiorMean cells
          (183 WebGPU, 125 CSS), vitrea's change V = 0.25 row - 0.5 row (current generation,
          X41-frozen) has Apple's sign on every cell, and the median of V / dA pooled over the
          four profiles per tier is in [0.8, 1.2]; per-profile medians reported, not gated.
          Read in G3, adopted only by the user's ruling at the landing (Decision Log 5 (c)).

The tiers: each row is GATED on the tier it was adopted on (tables on both, by their own
tables; S1 on both; M1, M2, C1, X1, L1 and E2 on WebGPU) and READ, descriptively and marked so,
on the other where the rows or captures carry the reading.

The populations are DECLARED, never read off the bed. Each cut draws its members from the four
profiles' ``scenes.json`` lists under its own scene-level rule (``bed.py`` refuses a row whose
split role or state disagrees with ``scenes.json``, so the rule selects exactly the rows a rule
on the rows would), then looks each member's row up. The render drivers write with
``--write-partial``, so a bed can lack a cell or a whole (profile, tier) pair; a member with no
row is UNMEASURED and listed as ``noRow``, apart from a row that carries no reading (L1's four
dark inactive dark-solid means, E2's cells with no measured bin). No verdict is PASS while a
member is UNMEASURED: a miss still reads MISS; otherwise "PASS, N UNMEASURED", with how many had
no row (or, for L1, only the growth clause unread) in parentheses; "UNMEASURED" when nothing was
evaluated. A row reading the rule itself conditions on (C1's admitted bands and support, E2's
sampling backend) still excludes a present row; a member with no row cannot show it, so it
counts. S1's members are ``r2-population.json``'s fixed cells.

Admission is ``bed.py``'s: a ``prefit`` bed (the shipped 0.5 documents on the 0.25 cells, the
cross-position stamp) or a ``candidate`` bed (one declared candidate document). Every output
names which, and a candidate output opens ``# CANDIDATE``. The reference for L1, M2 and E2 is
always a ``prefit`` bed.

    python3.12 -B cuts.py --bed M.json [--bed M2.json] --kind prefit|candidate
        [--candidate-document PATH[=SHA12]] --captures ROOT
        --prefit P.json [--prefit P2.json] --prefit-captures ROOT --out OUT.json [--text OUT.txt]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bed as B  # noqa: E402

TEST = B.CAL / "test" / "adopted-thresholds.test.ts"
E2_DIR = B.RESULTS / "2026-09-25-w38-g0-rim-axis-cut"
R2_POPULATION = B.RESULTS / "2026-10-02-w43-g2-reading" / "s1" / "r2-population.json"
FIXTURES = B.ROOT / "apps" / "reference-apple" / "fixtures"

# ---------------------------------------------------------------------------------------------
# The declared bounds (Decision Log 5 as ruled; each the 0.5 row's own constant)
# ---------------------------------------------------------------------------------------------
M1_MEDIAN = (0.8, 1.2)
M1_CELL = (0.6, 1.4)
M2_TOLERANCE = 0.02
C1_TOLERANCE = 0.0042
C1_SPANS = (96, 128, 160)
C1_ADMITTED = {96: ["3-6", "6-12", "12-24", "24-48"], 128: ["3-6", "6-12", "12-24"],
               160: ["3-6", "6-12"]}
C1_BAND_WIDTH = {"3-6": 3, "6-12": 6, "12-24": 12, "24-48": 24}
C1_MIN_SUPPORT = 0.1
X1_BLACK = ["checkerboard", "checkerboard-4", "checkerboard-8", "checkerboard-32",
            "checkerboard-64", "impulse", "hc-text", "hc-text-7", "hc-text-28"]
L1_ABSOLUTE = 0.055
L1_GROWTH = 0.005
E2_NAMED_CODES = 1.0
E2_MIN_PIXELS = 4
S1_RATIO = (0.8, 1.2)
WELL_CONDITIONED_AREA_RATIO = 0.95
GATED_TIER = {"tables": ("webgpu", "css"), "M1": ("webgpu",), "M2": ("webgpu",),
              "C1": ("webgpu",), "X1": ("webgpu",), "L1": ("webgpu",), "E2": ("webgpu",),
              "S1": ("webgpu", "css")}


def upper_middle(values):
    s = sorted(values)
    return s[len(s) // 2] if s else math.nan


# ---------------------------------------------------------------------------------------------
# Declared populations
# ---------------------------------------------------------------------------------------------
def declared(rule) -> list[tuple[str, str]]:
    """A cut's members as scenes.json declares them: (profile, scene) over the four profiles'
    non-holdout lists where the cut's scene-level `rule` holds. Drawn without the bed."""
    return [(p, sid) for p in B.PROFILES for sid in B.SCENES.declared(p)
            if B.SCENES.role[sid] in B.NON_HOLDOUT and rule(sid)]


def selected(bed: B.Bed, renderer: str, members) -> tuple[list, list]:
    """(the bed's rows of `members` on `renderer`, in the bed's order; the members with no row)."""
    wanted = set(members)
    rows = [r for r in bed.rows if r["key"]["web"]["renderer"] == renderer
            and (r["key"]["profileKey"], r["key"]["sceneId"]) in wanted]
    have = {(r["key"]["profileKey"], r["key"]["sceneId"]) for r in rows}
    return rows, [k for k in members if k not in have]


def labels(keys) -> list[str]:
    return [f"{p}/{s}" for p, s in keys]


def qualified(verdict: str, unmeasured: int, **kinds: int) -> str:
    """`verdict` qualified by its `unmeasured` members, the kinds that are not a missing reading
    counted in parentheses: "PASS, 5 UNMEASURED (1 no row)"."""
    if not unmeasured:
        return verdict
    notes = ", ".join(f"{n} {kind.replace('_', ' ')}" for kind, n in kinds.items() if n)
    return f"{verdict}, {unmeasured} UNMEASURED" + (f" ({notes})" if notes else "")


# ---------------------------------------------------------------------------------------------
# The tables, read out of the owner test
# ---------------------------------------------------------------------------------------------
ROW = re.compile(r'\[\s*"(shape|perceptual)",\s*(?:/\*[^*]*\*/\s*)?"(\w+)",\s*(?:/\*[^*]*\*/\s*)?'
                 r'"(≥|≤)",\s*([0-9.]+)\s*\]')


def owner_tables() -> dict:
    """{0.5 profile: {"texture": rows, "dom": rows, "names": {...}}} from the test's source,
    each 27 table followed through its alias to the literal it equals."""
    source = TEST.read_text()
    alias = dict(re.findall(r"^const (\w+_27_\w*) = (\w+);$", source, re.M))
    literals = {}
    for name, body in re.findall(r"^const (\w+): readonly GateRow\[\] = \[(.*?)^\];", source,
                                 re.M | re.S):
        literals[name] = [(a, m, c, float(t)) for a, m, c, t in ROW.findall(body)]
    block = re.search(r"^const DECLARED_27_PROFILES: .*?^\];", source, re.M | re.S).group(0)
    out = {}
    for profile, texture, dom in re.findall(
            r'profileKey: "([^"]+)",.*?names: \{\s*texture: "(\w+)",\s*dom: "(\w+)"', block, re.S):
        out[profile] = {"names": {"texture": texture, "dom": dom},
                        "aliasOf": {"texture": alias[texture], "dom": alias[dom]},
                        "texture": literals[alias[texture]], "dom": literals[alias[dom]]}
    return dict(sha256=hashlib.sha256(source.encode()).hexdigest(), profiles=out)


def well_conditioned(row) -> bool:
    shape = row.get("shape")
    if shape is None:
        return True
    at = lambda m: shape[m]["value"]  # noqa: E731
    region = at("componentRegionArea")
    bodies = at("componentRegionBodies")
    return (at("silhouetteAreaNative") >= WELL_CONDITIONED_AREA_RATIO * region
            and at("silhouetteAreaWeb") >= WELL_CONDITIONED_AREA_RATIO * region
            and at("silhouetteBodiesNative") <= bodies and at("silhouetteBodiesWeb") <= bodies)


def gated_member(sid) -> bool:
    """The owner test's gated bed: active pose, calibration and validation (no probe, no
    recorded)."""
    return B.SCENES.role[sid] in ("calibration", "validation") and not B.SCENES.inactive(sid)


def cut_tables(bed: B.Bed, tables: dict) -> dict:
    out = {}
    for profile in B.PROFILES:
        twin = tables["profiles"][B.counterpart_05(profile)]
        members = [k for k in declared(gated_member) if k[0] == profile]
        for renderer, tier in B.TIERS.items():
            rows, no_row = selected(bed, renderer, members)
            excluded = sorted(r["key"]["sceneId"] for r in rows
                              if r.get("shape") is not None and not well_conditioned(r))
            no_shape = sorted(r["key"]["sceneId"] for r in rows if r.get("shape") is None)
            misses, checked = [], 0
            for axis, metric, comparison, threshold in twin[tier]:
                applicable = ([r for r in rows if r.get("shape") is not None and well_conditioned(r)]
                              if axis == "shape" else rows)
                for r in applicable:
                    measured = B.value(r, axis, metric)
                    checked += 1
                    ok = measured is not None and (measured >= threshold if comparison == "≥"
                                                   else measured <= threshold)
                    if not ok:
                        misses.append(dict(scene=r["key"]["sceneId"], set=r["fixtureSet"],
                                           metric=metric, measured=measured,
                                           bound=f"{comparison} {threshold}",
                                           status="UNMEASURED" if measured is None else "MISS"))
            out[f"{profile} {renderer}"] = dict(
                table=twin["names"][tier], aliasOf=twin["aliasOf"][tier], cells=len(rows),
                predicateExcludes=excluded, noShapeAxis=no_shape, checks=checked,
                misses=misses, noRow=[sid for _, sid in no_row],
                verdict=("UNMEASURED" if not rows else "MISS" if misses else
                         qualified("PASS", len(no_row), no_row=len(no_row))))
    return out


# ---------------------------------------------------------------------------------------------
# M1 / M2
# ---------------------------------------------------------------------------------------------
def chroma_member(sid) -> bool:
    """The untinted photo cells, calibration and validation, both poses."""
    return (B.SCENES.role[sid] in ("calibration", "validation") and sid.startswith("photo__")
            and "-tint-" not in sid)


def chroma_bed(bed: B.Bed, renderer: str) -> tuple[dict, list]:
    rows, no_row = selected(bed, renderer, declared(chroma_member))
    return {(r["key"]["profileKey"], r["key"]["sceneId"]): r for r in rows}, no_row


def structure_verdict(r: float, w: float, n: float) -> str:
    """W42 Decision Log 5a, `structureVerdict` in adopted-thresholds.test.ts, transcribed."""
    if not abs((w - r) / r) > M2_TOLERANCE:
        return "within"
    toward = (w - r) * (n - r) > 0
    beyond = (w - n) * (n - r) > 0
    return "named" if toward and (not beyond or abs(w - n) / n <= M2_TOLERANCE) else "failure"


def cut_m1_m2(bed: B.Bed, prefit: B.Bed, renderer: str) -> dict:
    cells, missing = [], []
    reference, _ = chroma_bed(prefit, renderer)
    here, no_row = chroma_bed(bed, renderer)
    no_row = labels(no_row)
    for key, r in sorted(here.items()):
        profile, sid = key
        web, native = (B.value(r, "material", "chromaStructureRatioWeb"),
                       B.value(r, "material", "chromaStructureRatioNative"))
        w, n = B.value(r, "material", "interiorStdDevWeb"), B.value(r, "material", "interiorStdDevNative")
        ref = B.value(reference.get(key), "material", "interiorStdDevWeb")
        if None in (web, native, w, n, ref):
            missing.append(f"{profile}/{sid}")
            continue
        delta = (w - ref) / ref
        cells.append(dict(profile=profile, scene=sid, set=r["fixtureSet"],
                          scheme=B.scheme_of(profile), scale=B.scale_of(profile),
                          pose="inactive" if B.SCENES.inactive(sid) else "active",
                          R=web / native, interiorStdDevWeb=w, interiorStdDevNative=n,
                          interiorStdDevWebReference=ref, structureDeltaFraction=delta,
                          m2=structure_verdict(ref, w, n)))
    beds = {}
    for scheme in ("light", "dark"):
        for pose in ("active", "inactive"):
            group = [c for c in cells if c["scheme"] == scheme and c["pose"] == pose]
            if group:
                values = [c["R"] for c in group]
                beds[f"{scheme}|{pose}"] = dict(cells=len(group), median=statistics.median(values),
                                                min=min(values), max=max(values),
                                                medianInWindow=M1_MEDIAN[0] <= statistics.median(values) <= M1_MEDIAN[1])
    cell_misses = [dict(cell=f"{c['profile']}/{c['scene']}", R=c["R"]) for c in cells
                   if not M1_CELL[0] <= c["R"] <= M1_CELL[1]]
    m2 = [dict(cell=f"{c['profile']}/{c['scene']}", reference=c["interiorStdDevWebReference"],
               web=c["interiorStdDevWeb"], native=c["interiorStdDevNative"],
               delta=c["structureDeltaFraction"], verdict=c["m2"])
          for c in cells if c["m2"] != "within"]
    m1_pass = (all(b["medianInWindow"] for b in beds.values()) and not cell_misses)
    unmeasured = len(missing) + len(no_row)
    m1_verdict = ("UNMEASURED" if not cells else "MISS" if not m1_pass else
                  qualified("PASS", unmeasured, no_row=len(no_row)))
    return dict(
        M1=dict(beds=beds, cellMisses=cell_misses, unmeasured=missing, noRow=no_row,
                verdict=m1_verdict),
        M2=dict(misses=m2, named=[m for m in m2 if m["verdict"] == "named"],
                failures=[m for m in m2 if m["verdict"] == "failure"], unmeasured=missing,
                noRow=no_row,
                worstAbsDelta=max((abs(c["structureDeltaFraction"]) for c in cells), default=None),
                verdict=("UNMEASURED" if not cells else
                         "FAIL" if any(m["verdict"] == "failure" for m in m2) else
                         qualified("NAMED MISSES" if m2 else "PASS", unmeasured,
                                   no_row=len(no_row)))),
        cells=cells)


# ---------------------------------------------------------------------------------------------
# C1
# ---------------------------------------------------------------------------------------------
def c1_reading(row) -> dict | None:
    profile, sid = row["key"]["profileKey"], row["key"]["sceneId"]
    if row["fixtureSet"] == "holdout" or row["fixtureSet"] == "recorded" or \
            B.SCENES.role[sid] == "recorded" or row.get("state") == "inactive":
        return None
    shadow = row.get("shadow")
    if shadow is None:
        return None
    span = B.SCENES.span(sid)
    if span not in C1_SPANS:
        return None
    scale = B.scale_of(profile)
    axis = lambda f: shadow[f]["value"] if isinstance(shadow.get(f), dict) else None  # noqa: E731
    clearance = min(axis(f) if axis(f) is not None else math.nan for f in
                    ("clearanceAbove", "clearanceBelow", "clearanceLeft", "clearanceRight")) / scale
    admitted = [b for b in C1_BAND_WIDTH if int(b.split("-")[1]) <= clearance]

    def slope(side, band):
        return next((e.get("slopeALinear") for e in shadow.get(side) or []
                     if e["direction"] == "all" and e["ringLabel"] == band), None)
    support = axis("backdropSupport")
    if support is not None and support < C1_MIN_SUPPORT:
        return None
    usable = [b for b in admitted if slope("affineNative", b) is not None
              and slope("affineWeb", b) is not None]
    if not usable or usable != C1_ADMITTED[span]:
        return None
    total = sum(C1_BAND_WIDTH[b] for b in usable)
    T = sum(C1_BAND_WIDTH[b] * abs(slope("affineWeb", b) - slope("affineNative", b))
            for b in usable) / total
    return dict(bed=f"{scale}x {B.scheme_of(profile)}", span=span, T=T, bands="/".join(usable))


def c1_member(sid) -> bool:
    """Active, non-holdout, non-recorded, at a gated span; the admitted-band and support
    predicate is a row reading and excludes only a present row."""
    return (B.SCENES.role[sid] in ("calibration", "validation", "probe")
            and not B.SCENES.inactive(sid) and B.SCENES.span(sid) in C1_SPANS)


def cut_c1(bed: B.Bed, renderer: str, others: dict) -> dict:
    """`others`: label -> {(profile-with-0.25-token, scene): T} for side-by-side reading."""
    rows, no_row = selected(bed, renderer, declared(c1_member))
    readings = {}
    for r in rows:
        got = c1_reading(r)
        if got is not None:
            readings[(r["key"]["profileKey"], r["key"]["sceneId"])] = got
    out = {}
    for b in ("1x light", "2x light", "1x dark", "2x dark"):
        for span in C1_SPANS:
            cell = {k: v for k, v in readings.items() if v["bed"] == b and v["span"] == span}
            values = [v["T"] for v in cell.values()]
            absent = labels((p, s) for p, s in no_row if B.SCENES.span(s) == span
                           and f"{B.scale_of(p)}x {B.scheme_of(p)}" == b)
            entry = dict(cells=len(values), statistic=upper_middle(values) if values else None,
                         min=min(values, default=None), max=max(values, default=None),
                         noRow=absent,
                         verdict=("UNMEASURED" if not values else
                                  qualified("PASS", len(absent), no_row=len(absent))
                                  if upper_middle(values) <= C1_TOLERANCE else "MISS"))
            for label, other in others.items():
                ov = [other[k] for k in cell if k in other]
                entry[label] = dict(cells=len(ov), statistic=upper_middle(ov) if ov else None,
                                    maxAbsCellChange=max((abs(cell[k]["T"] - other[k]) for k in cell
                                                          if k in other), default=None))
            out[f"{b} span {span}"] = entry
    return dict(perBedSpan=out, cells={f"{p}/{s}": v for (p, s), v in sorted(readings.items())},
                noRow=labels(no_row),
                verdict=("MISS" if any(e["verdict"] == "MISS" for e in out.values()) else
                         "UNMEASURED" if any(e["verdict"] == "UNMEASURED" for e in out.values())
                         else qualified("PASS", len(no_row), no_row=len(no_row))))


def c1_map(rows, renderer, to_025=False) -> dict:
    out = {}
    for r in rows:
        if r["key"]["web"]["renderer"] != renderer:
            continue
        got = c1_reading(r)
        if got is not None:
            profile = r["key"]["profileKey"]
            if to_025:
                profile = profile.replace("-glass0.5", "-glass0.25")
            out[(profile, r["key"]["sceneId"])] = got["T"]
    return out


# ---------------------------------------------------------------------------------------------
# Captures
# ---------------------------------------------------------------------------------------------
def rgb(raw: bytes) -> np.ndarray:
    return np.asarray(Image.open(io.BytesIO(raw)).convert("RGB"))


def capture(root: Path, row, renderer: str) -> tuple[np.ndarray, str]:
    """The web PNG this row was measured off: its metadata must name the row's capturePath."""
    profile, sid = row["key"]["profileKey"], row["key"]["sceneId"]
    folder = (root / profile / sid).resolve()
    if root.resolve() not in folder.parents:
        raise SystemExit(f"{profile}/{sid}: escapes {root}")
    meta = json.loads((folder / f"cell__{renderer}.json").read_text())
    if meta.get("capturePath") != row["key"]["web"]["capturePath"]:
        raise SystemExit(f"{profile}/{sid} {renderer}: capture metadata under {root} names another "
                         "generation than the row")
    raw = (folder / f"{sid}__{renderer}.png").read_bytes()
    return rgb(raw), hashlib.sha256(raw).hexdigest()


def native(profile: str, sid: str, kind: str = "png") -> np.ndarray:
    if B.SCENES.role[sid] not in ("calibration", "validation", "probe"):
        raise PermissionError(f"{profile}/{sid}: canonical {B.SCENES.role[sid]} is not read here")
    if kind == "png":
        return rgb((FIXTURES / profile / f"{sid}.png").read_bytes())
    scene = B.SCENES.by_id[sid]
    return rgb((FIXTURES / "backgrounds" / f"{scene['background']}@{B.scale_of(profile)}x.png").read_bytes())


# ---------------------------------------------------------------------------------------------
# X1
# ---------------------------------------------------------------------------------------------
def x1_member(sid) -> bool:
    """Single shapes on a black backdrop, at rest or receded, calibration/validation/probe."""
    scene = B.SCENES.by_id[sid]
    return (B.SCENES.role[sid] in ("calibration", "validation", "probe")
            and scene["state"] in ("rest", "inactive") and scene["background"] in X1_BLACK
            and B.SCENES.component(sid)["kind"] in ("rrect", "capsule"))


def cut_x1(bed: B.Bed, root: Path, renderer: str) -> dict:
    cells = []
    rows, no_row = selected(bed, renderer, declared(x1_member))
    for r in rows:
        profile, sid = r["key"]["profileKey"], r["key"]["sceneId"]
        scene = B.SCENES.by_id[sid]
        comp = B.SCENES.component(sid)
        w, digest = capture(root, r, renderer)
        n, bg = native(profile, sid), native(profile, sid, "background")
        scale = B.scale_of(profile)
        width, height = comp["size"]
        dx, dy = comp.get("offset", [0, 0])
        x0 = ((320 - width) / 2 + dx) * scale
        y0 = ((200 - height) / 2 + dy) * scale
        x1, y1 = x0 + width * scale, y0 + height * scale
        y, x = np.indices(n.shape[:2])
        black, nat, maximum = np.all(bg == 0, 2), np.all(n == 0, 2), w.max(2)
        masks = dict(
            integer=np.maximum.reduce([x0 - x, x - (x1 - 1), y0 - y, y - (y1 - 1)]) >= 2 * scale,
            analytic=np.hypot(np.maximum.reduce([x0 - (x + .5), x + .5 - x1, np.zeros_like(x)]),
                              np.maximum.reduce([y0 - (y + .5), y + .5 - y1, np.zeros_like(y)])) >= 2 * scale)
        row = dict(cell=f"{profile}/{sid}", role=B.SCENES.role[sid], span=min(width, height),
                   pose=scene["state"], background=scene["background"], webSha256=digest)
        for name, mask in masks.items():
            eligible = mask & black & nat
            pixels = int(eligible.sum())
            row[name] = dict(pixels=pixels, aboveZero=int(np.sum(eligible & (maximum > 0))),
                             aboveOne=int(np.sum(eligible & (maximum > 1))))
        cells.append(row)
    failing = [c for c in cells if any(c[m]["aboveZero"] or c[m]["aboveOne"] or not c[m]["pixels"]
                                       for m in ("integer", "analytic"))]
    return dict(cells=len(cells),
                totals={m: {k: sum(c[m][k] for c in cells) for k in ("pixels", "aboveZero", "aboveOne")}
                        for m in ("integer", "analytic")},
                failing=failing, noRow=labels(no_row),
                verdict=("UNMEASURED" if not cells else "MISS" if failing else
                         qualified("PASS", len(no_row), no_row=len(no_row))),
                perCell=cells)


# ---------------------------------------------------------------------------------------------
# L1
# ---------------------------------------------------------------------------------------------
def cut_l1(bed: B.Bed, prefit: B.Bed, renderer: str) -> dict:
    members = declared(lambda sid: B.SCENES.role[sid] in ("calibration", "validation"))
    rows, no_row = selected(bed, renderer, members)
    reference = prefit.by_key(renderer)
    cells = []
    for r in rows:
        key = (r["key"]["profileKey"], r["key"]["sceneId"])
        old = reference.get(key)
        n, w = B.value(r, "material", "interiorMeanNative"), B.value(r, "material", "interiorMeanWeb")
        bn, bw = B.value(old, "material", "interiorMeanNative"), B.value(old, "material", "interiorMeanWeb")
        if old is None:
            raise SystemExit(f"L1: {key} has no pre-fit row")
        if n != bn:
            raise SystemExit(f"L1: {key} native mean {n} differs from the pre-fit row's {bn}")
        error = None if n is None or w is None else abs(w - n)
        before = None if bn is None or bw is None else abs(bw - bn)
        growth = None if error is None or before is None else error - before
        clauses = [c for c, v in (("absolute", error), ("growth", growth)) if v is None]
        cell = dict(cell=f"{key[0]}/{key[1]}", native=n, web=w, prefitError=before,
                    error=error, growth=growth, status="UNMEASURED" if clauses else "MEASURED")
        if clauses:
            cell["unmeasuredClauses"] = clauses
        cells.append(cell)
    cells.sort(key=lambda c: c["cell"])
    absolute = [c for c in cells if c["error"] is not None and c["error"] > L1_ABSOLUTE]
    growth = [c for c in cells if c["growth"] is not None and c["growth"] > L1_GROWTH]
    # Both clauses unread (the cell's own means), then the growth clause alone (the pre-fit
    # row's web mean): each is counted against the verdict, never read as a pass.
    unmeasured = [c["cell"] for c in cells if c["error"] is None]
    growth_only = [c["cell"] for c in cells if c["error"] is not None and c["growth"] is None]
    count = len(unmeasured) + len(growth_only) + len(no_row)
    return dict(population=len(members), measured=len(cells) - len(unmeasured) - len(growth_only),
                unmeasured=unmeasured, growthUnmeasured=growth_only, noRow=labels(no_row),
                absoluteMisses=absolute, growthMisses=growth,
                maxError=max((c["error"] for c in cells if c["error"] is not None), default=None),
                maxGrowth=max((c["growth"] for c in cells if c["growth"] is not None), default=None),
                verdict=("MISS" if absolute or growth else
                         "UNMEASURED" if len(unmeasured) == len(cells) else
                         qualified("PASS", count, growth_clause_only=len(growth_only),
                                   no_row=len(no_row))), cells=cells)


# ---------------------------------------------------------------------------------------------
# E2, absolute
# ---------------------------------------------------------------------------------------------
def e2_module():
    sys.path.insert(0, str(E2_DIR))
    import e2  # noqa: E402
    return e2


def e2_member(sid) -> bool:
    """W38 `e2.population`'s scene rule: calibration, validation and probe roles, the rest
    state, capsule / rrect / the three-capsule group."""
    return (B.SCENES.role[sid] in ("calibration", "validation", "probe")
            and B.SCENES.by_id[sid]["state"] == "rest"
            and B.SCENES.component(sid)["kind"] in ("capsule", "rrect", "group"))


def e2_population(bed: B.Bed, renderer: str) -> tuple[dict, list]:
    """W38 `e2.population`'s rule on the 0.25 rows: `e2_member`, and WebGPU on a gpu-texture
    backend (a row reading, so it excludes a present row only). Returns the rows and the
    members with no row."""
    rows, no_row = selected(bed, renderer, declared(e2_member))
    out = {}
    for r in rows:
        sid = r["key"]["sceneId"]
        if renderer == "webgpu" and r["key"]["web"]["samplingBackend"] != "gpu-texture":
            continue
        comp = B.SCENES.component(sid)
        if comp["kind"] == "group" and (len(comp["items"]) != 3 or any(
                i["kind"] != "capsule" or i["size"] != [44, 44] for i in comp["items"])):
            raise SystemExit("E2: grouped scene geometry changed; declare an estimator first")
        out[(r["key"]["profileKey"], sid)] = r
    return out, no_row


def cut_e2(bed: B.Bed, root: Path, prefit: B.Bed, prefit_root: Path, renderer: str) -> dict:
    e2 = e2_module()
    (here, no_row), (there, _) = e2_population(bed, renderer), e2_population(prefit, renderer)
    cells, named = [], []
    for key in sorted(here):
        profile, sid = key
        if key not in there:
            raise SystemExit(f"E2: {key} has no pre-fit row")
        scale = B.scale_of(profile)
        n = native(profile, sid).astype(float)
        w, _ = capture(root, here[key], renderer)
        p, _ = capture(prefit_root, there[key], renderer)
        w, p = w.astype(float), p.astype(float)
        comp = B.SCENES.component(sid)
        shape = n.shape[:2]
        _, parts = (e2.group_geometry(shape, comp, scale) if comp["kind"] == "group"
                    else e2.single_geometry(shape, comp, scale))
        res_c, res_p, bins = [], [], 0
        worst = None
        for info, mask in parts:
            if info["pixels"] < E2_MIN_PIXELS:
                continue
            bins += 1
            rc = np.abs(w[mask] - n[mask]).mean(axis=0)
            rp = np.abs(p[mask] - n[mask]).mean(axis=0)
            res_c.append(rc)
            res_p.append(rp)
            delta = rc - rp
            if delta.max() > E2_NAMED_CODES:
                named.append(dict(cell=f"{profile}/{sid}",
                                  **{k: info[k] for k in ("side", "member", "shell", "angleBin") if k in info},
                                  pixels=info["pixels"], prefitRGB=rp.tolist(),
                                  candidateRGB=rc.tolist(), deltaRGB=delta.tolist()))
            if worst is None or delta.max() > worst:
                worst = float(delta.max())
        if not bins:
            cells.append(dict(cell=f"{profile}/{sid}", status="UNMEASURED", bins=0))
            continue
        mean_c, mean_p = float(np.mean(res_c)), float(np.mean(res_p))
        cells.append(dict(cell=f"{profile}/{sid}", status="measured", bins=bins,
                          meanAbsCodes=mean_c, prefitMeanAbsCodes=mean_p, change=mean_c - mean_p,
                          worstBinDelta=worst, verdict="FAIL" if mean_c > mean_p else "within"))
    failing = [c for c in cells if c.get("verdict") == "FAIL"]
    unmeasured = [c["cell"] for c in cells if c["status"] == "UNMEASURED"]
    changes = [c["change"] for c in cells if "change" in c]
    return dict(cells=len(cells), measured=len(changes), unmeasured=unmeasured,
                noRow=labels(no_row), failing=failing, namedMissBins=named,
                namedMissCells=sorted({b["cell"] for b in named}),
                meanChange=float(np.mean(changes)) if changes else None,
                verdict=("MISS" if failing else "UNMEASURED" if not changes else
                         qualified("PASS", len(unmeasured) + len(no_row), no_row=len(no_row))),
                perCell=cells)


# ---------------------------------------------------------------------------------------------
# S1 as R2
# ---------------------------------------------------------------------------------------------
def cut_s1(bed: B.Bed, current: dict) -> dict:
    population = json.loads(R2_POPULATION.read_text())
    out = {}
    for renderer in B.TIERS:
        entries = [e for e in population["cells"] if e["reading"] == "interiorMean"
                   and e["tier"] == renderer]
        rows = bed.by_key(renderer)
        cells, unmeasured, worst_check = [], [], 0.0
        no_row = [f"{e['profileKey']}/{e['sceneId']}" for e in entries
                  if (e["profileKey"], e["sceneId"]) not in rows]
        for e in entries:
            key = (e["profileKey"], e["sceneId"])
            row = rows.get(key)
            old = current.get((B.counterpart_05(e["profileKey"]), renderer, e["sceneId"]))
            w25, w05 = B.value(row, "material", "interiorMeanWeb"), B.value(old, "material", "interiorMeanWeb")
            n25, n05 = (B.value(row, "material", "interiorMeanNative"),
                        B.value(old, "material", "interiorMeanNative"))
            if None in (w25, w05, n25, n05):
                unmeasured.append(f"{key[0]}/{key[1]}")
                continue
            worst_check = max(worst_check, abs((n25 - n05) - e["dA"]))
            V = w25 - w05
            cells.append(dict(cell=f"{key[0]}/{key[1]}", profile=key[0], dA=e["dA"], e05=e["e"], V=V,
                              ratio=V / e["dA"], sign=(V * e["dA"] > 0),
                              error025=w25 - n25))
        ratios = [c["ratio"] for c in cells]
        wrong = [c for c in cells if not c["sign"]]
        pooled = upper_middle(ratios) if ratios else None
        per_profile = {p: dict(cells=len([c for c in cells if c["profile"] == p]),
                               median=upper_middle([c["ratio"] for c in cells if c["profile"] == p]))
                       for p in B.PROFILES}
        out[renderer] = dict(
            population=len(entries), measured=len(cells), unmeasured=unmeasured, noRow=no_row,
            appleChangeFromRowsMaxDeviation=worst_check,
            wrongSign=[dict(cell=c["cell"], V=c["V"], dA=c["dA"]) for c in wrong],
            pooledMedianRatio=pooled, perProfileMedian=per_profile,
            verdict=("UNMEASURED" if unmeasured or not cells else
                     "PASS" if not wrong and S1_RATIO[0] <= pooled <= S1_RATIO[1] else "MISS"),
            cells=cells)
    return out


# ---------------------------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bed", action="append", required=True)
    ap.add_argument("--kind", choices=("prefit", "candidate"), required=True)
    ap.add_argument("--candidate-document")
    ap.add_argument("--captures", type=Path, required=True)
    ap.add_argument("--prefit", action="append", required=True)
    ap.add_argument("--prefit-captures", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--text", type=Path)
    ap.add_argument("--skip-captures", action="store_true",
                    help="row-derived cuts only (X1 and E2 UNMEASURED); a scratch look, never a verdict")
    args = ap.parse_args(argv)

    bed = B.load(args.bed, args.kind, args.candidate_document)
    prefit = B.load(args.prefit, "prefit")
    tables = owner_tables()
    current = B.current_05_rows()
    current_rows = list(current.values())
    result = dict(
        what="W43 G3 (i): the 0.25 adopted rows as RULED 2026-10-02 (Decision Log 5 (a)-(e); "
             "Decision Log 7 items 10-11), read on one bed",
        cutsSource={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (HERE / "cuts.py", HERE / "bed.py")},
        bed=bed.described(), reference=dict(label=prefit.label, **prefit.described()),
        ownerTest=dict(path=str(TEST.relative_to(B.ROOT)), sha256=tables["sha256"]),
        scenesSha256=hashlib.sha256(B.SCENES.raw).hexdigest(),
        withHoldout=False, gatedTier=GATED_TIER,
    )
    result["tables"] = cut_tables(bed, tables)
    m = {r: cut_m1_m2(bed, prefit, r) for r in B.TIERS}
    result["M1"] = {r: m[r]["M1"] for r in B.TIERS}
    result["M2"] = {r: m[r]["M2"] for r in B.TIERS}
    result["M1M2cells"] = {r: m[r]["cells"] for r in B.TIERS}
    result["C1"] = {r: cut_c1(bed, r, {"prefit": c1_map(prefit.rows, r),
                                       "shipped05": c1_map(current_rows, r, to_025=True)})
                    for r in B.TIERS}
    result["L1"] = {r: cut_l1(bed, prefit, r) for r in B.TIERS}
    if args.skip_captures:
        result["X1"] = result["E2"] = "UNMEASURED: --skip-captures"
    else:
        result["X1"] = {r: cut_x1(bed, args.captures, r) for r in B.TIERS}
        result["E2"] = {r: cut_e2(bed, args.captures, prefit, args.prefit_captures, r) for r in B.TIERS}
    result["S1"] = cut_s1(bed, current)
    result["summary"] = summary(result)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as f:
        json.dump(result, f, indent=1, allow_nan=True)
        f.write("\n")
    text = report(result)
    if args.text:
        with args.text.open("x") as f:
            f.write(text)
    print(text)
    return 0


def summary(result) -> dict:
    out = {}
    for profile_tier, t in result["tables"].items():
        out[f"tables {profile_tier}"] = t["verdict"]
    for cut in ("M1", "M2", "C1", "L1", "X1", "E2", "S1"):
        block = result[cut]
        if isinstance(block, str):
            out[cut] = block
            continue
        for renderer, entry in block.items():
            gate = "GATED" if renderer in GATED_TIER[cut] else "descriptive"
            out[f"{cut} {renderer} ({gate})"] = entry["verdict"]
    return out


def fmt(value, spec=".4f") -> str:
    return "—" if value is None else format(value, spec)


NO_ROW_LISTED = 12


def no_row_lines(cells, indent: str, what: str = "") -> list[str]:
    """The members with no row, the first NO_ROW_LISTED of them by name (the JSON has all)."""
    lines = [f"{indent}UNMEASURED{what}, no row {c}" for c in cells[:NO_ROW_LISTED]]
    if len(cells) > NO_ROW_LISTED:
        lines.append(f"{indent}... and {len(cells) - NO_ROW_LISTED} more with no row")
    return lines


def report(result) -> str:
    lines = []
    if result["bed"]["kind"] == "candidate":
        lines.append(f"# CANDIDATE: {result['bed']['candidateDocument']['path']} "
                     f"sha256:{result['bed']['candidateDocument']['sha256'][:12]} "
                     "(a declared scratch document; not a shipped cut)")
    else:
        lines.append("# PREFIT: the shipped 0.5 documents on the 0.25 cells, "
                     "crossPosition=shipped-glass0.5-against-glass0.25 (scratch; the unmoved endpoint)")
    lines.append(f"# owner test {result['ownerTest']['path']} sha256:{result['ownerTest']['sha256'][:12]}; "
                 "holdout not read")
    lines.append("")
    lines.append("verdicts")
    for k, v in result["summary"].items():
        lines.append(f"  {k:<64} {v}")
    lines.append("")
    lines.append("tables (the 0.5 tables per tier; misses listed)")
    for pt, t in result["tables"].items():
        lines.append(f"  {pt}: {t['table']} (= {t['aliasOf']}), {t['cells']} cells, "
                     f"{len(t['predicateExcludes'])} predicate-excluded, {len(t['misses'])} misses")
        for miss in t["misses"]:
            lines.append(f"    {miss['set']:<11} {miss['scene']:<48} {miss['metric']:<20} "
                         f"{miss['measured'] if miss['measured'] is None else round(miss['measured'], 5)} "
                         f"vs {miss['bound']}")
        lines += no_row_lines(t["noRow"], "    ")
    for r in ("webgpu", "css"):
        g = "GATED" if r in GATED_TIER["M1"] else "descriptive"
        lines.append(f"\nM1 {r} ({g})")
        for b, e in result["M1"][r]["beds"].items():
            lines.append(f"  {b:<16} n={e['cells']:<3} median R {fmt(e['median'])}  min {fmt(e['min'])}  max {fmt(e['max'])}")
        for miss in result["M1"][r]["cellMisses"]:
            lines.append(f"  cell miss {miss['cell']} R {miss['R']:.4f}")
        m2 = result["M2"][r]
        lines.append(f"M2 {r} ({g}): {len(m2['misses'])} misses, {len(m2['named'])} named, "
                     f"{len(m2['failures'])} failures, worst |Δsd| "
                     f"{(m2['worstAbsDelta'] or 0) * 100:.3f}%")
        for miss in m2["misses"]:
            lines.append(f"  {miss['verdict']:<8} {miss['cell']:<84} r {miss['reference']:.5f} "
                         f"w {miss['web']:.5f} n {miss['native']:.5f} ({miss['delta'] * 100:+.2f}%)")
        lines += no_row_lines(m2["noRow"], "  ", " (M1, M2)")
    for r in ("webgpu", "css"):
        g = "GATED" if r in GATED_TIER["C1"] else "descriptive"
        lines.append(f"\nC1 {r} ({g}): upper middle per bed x span, bound {C1_TOLERANCE}")
        for k, e in result["C1"][r]["perBedSpan"].items():
            stat = "—" if e["statistic"] is None else f"{e['statistic']:.5f}"
            pre = e.get("prefit", {}).get("statistic")
            s05 = e.get("shipped05", {}).get("statistic")
            lines.append(f"  {k:<22} n={e['cells']:<3} {stat:<9} {e['verdict']:<10} prefit "
                         f"{'—' if pre is None else f'{pre:.5f}'}  shipped0.5 {'—' if s05 is None else f'{s05:.5f}'}")
            lines += no_row_lines(e["noRow"], "    ")
    for r in ("webgpu", "css"):
        g = "GATED" if r in GATED_TIER["L1"] else "descriptive"
        l1 = result["L1"][r]
        lines.append(f"\nL1 {r} ({g}): {l1['population']} cells, {l1['measured']} measured, max error "
                     f"{fmt(l1['maxError'])}, max growth {fmt(l1['maxGrowth'], '+.4f')}; "
                     f"{len(l1['absoluteMisses'])} absolute, {len(l1['growthMisses'])} growth misses")
        for c in l1["absoluteMisses"]:
            lines.append(f"  absolute {c['cell']:<84} {c['error']:.4f} (prefit {c['prefitError']:.4f})")
        for c in l1["growthMisses"]:
            lines.append(f"  growth   {c['cell']:<84} {c['growth']:+.4f} (error {c['error']:.4f})")
        for c in l1["unmeasured"]:
            lines.append(f"  UNMEASURED {c}")
        for c in l1["growthUnmeasured"]:
            lines.append(f"  UNMEASURED growth {c} (the pre-fit row carries no web mean)")
        lines += no_row_lines(l1["noRow"], "  ")
    if not isinstance(result["X1"], str):
        for r in ("webgpu", "css"):
            x = result["X1"][r]
            g = "GATED" if r in GATED_TIER["X1"] else "descriptive"
            lines.append(f"\nX1 {r} ({g}): {x['cells']} cells, totals {x['totals']}, "
                         f"{len(x['failing'])} failing")
            for c in x["failing"][:40]:
                lines.append(f"  {c['cell']:<84} integer {c['integer']} analytic {c['analytic']}")
            lines += no_row_lines(x["noRow"], "  ")
        for r in ("webgpu", "css"):
            e = result["E2"][r]
            g = "GATED" if r in GATED_TIER["E2"] else "descriptive"
            lines.append(f"\nE2 {r} ({g}): {e['cells']} cells, {e['measured']} measured, "
                         f"{len(e['failing'])} failing, mean change {fmt(e['meanChange'], '+.4f')} codes, "
                         f"{len(e['namedMissBins'])} named-miss bins on {len(e['namedMissCells'])} cells")
            for c in e["failing"][:60]:
                lines.append(f"  FAIL {c['cell']:<84} {c['prefitMeanAbsCodes']:.3f} -> "
                             f"{c['meanAbsCodes']:.3f} codes")
            lines += no_row_lines(e["noRow"], "  ")
    for r in ("webgpu", "css"):
        s = result["S1"][r]
        lines.append(f"\nS1/R2 {r} (GATED, adopted only at the landing by ruling): "
                     f"{s['measured']}/{s['population']} cells, pooled median ratio "
                     f"{fmt(s['pooledMedianRatio'])}, {len(s['wrongSign'])} wrong sign; "
                     f"dA from rows max deviation {s['appleChangeFromRowsMaxDeviation']:.2e}")
        for p, e in s["perProfileMedian"].items():
            lines.append(f"  {p:<50} n={e['cells']:<4} median {fmt(e['median'] if e['cells'] else None)}")
        lines += no_row_lines(s["noRow"], "  ")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
