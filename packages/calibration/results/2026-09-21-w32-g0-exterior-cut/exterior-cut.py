#!/usr/bin/env python3
"""W32 G0 — the direction-resolved exterior cut, read inside each cell's own
clearance (claims §5.166; W32 acceptance clause 1).

    python3 exterior-cut.py > exterior-cut.txt
    python3 exterior-cut.py --with-holdout > exterior-cut-with-holdout.txt

## What this file is

**A copy of W31 G1's `exterior-instrument.py`**
(`results/2026-09-21-w31-g1-exterior-instrument/exterior-instrument.py`,
claims §5.162), taken verbatim into this gate's own evidence directory and
extended here, because nothing under `results/` is edited after commit. The
statistics' definitions, the exclusions, the holdout drop, the noise bar, the
`--against` lever and the two candidates are that file's and are not restated.

**What changed, and why each change is here.**

  1. **The admitted-band rule** (W32 clause 1, folded from the charter's
     adversarial review). A band is read on a cell only where the band's OUTER
     edge in CSS px lies inside that cell's own clearance in the direction being
     read — `clearance{Above,Below,Left,Right}` divided by the row's scale, and
     for `all` the minimum of the four. W31 G1's `weighted()` renormalised `T`
     per cell over whatever bands it happened to find usable (its line ~400),
     which pooled a span-160 cell whose `24-48` band survives only in the
     capture's four corners with a span-96 cell whose `24-48` band is whole.
     Here the set is fixed per span BEFORE pooling, bands-used is printed beside
     every figure, and an order statistic is taken only over the cells that
     carry the span's full admitted set; the cells that carry a shorter set are
     counted and reported apart rather than silently averaged in.
  2. **Direction resolution.** `T`, `Δa` and `Δc` are computed for every one of
     `all`, `above`, `below`, `left` and `right` on every row, each inside that
     direction's own clearance. W31 G1 resolved direction only on the two cells
     of its §4; this gate resolves it bed-wide, because the offset is identified
     one-sidedly (`above` reads exactly 0 at span 44) and a shift and a widening
     are only separable per direction.
  3. **The extents and the offsets**, per direction and both sides, with the
     count of rows where a side is absent, per span — the frame having eaten the
     measurement rather than a reading (`ShadowFieldReport`'s own rule).
  4. **The window-restricted departure**, over the bands 3–48 CSS px, computed
     from the per-band `sampleCount`, `backdropMeanLinear` and
     `renderedLevelLinear` the affine entries already carry, beside the
     whole-exterior `meanDeparture` B3 is stated over. W32 clause 3 restricts
     the anchor solve to this window because the `0-3` band holds the body's own
     over-fill (§5.62) and is of the opposite sign.
  5. **The inactive pose as its own population**, tabled rather than only
     summarised, because W32 clause 4 solves the receded documents' anchors on
     it.

Everything else — including the per-band per-direction arithmetic of §4, which
this gate's own vitest case pins against W31 G1's committed printout — is
unchanged, and §4's numbers are expected to reproduce byte for byte.

**Nothing here is fitted, adopted or captured** (W32 X2, X5).

**Nothing is fitted, adopted or captured here.** Every number is read off
`results/matrix.json` — the working file, by name — and off the superseded
generations named on the command line, both of which are committed evidence
(X2, X5 of the W30 charter; W31 acceptance clause 4). No profile document, no
material constant, no golden and no row moves.

## The admitted-band rule, stated once

A band is ADMITTED on a cell in a direction when

    band outer edge (CSS px)  ≤  that direction's clearance (device px) / scale

and for the pooled direction `all` when it is admitted in all four. The
clearance is the distance from the declared contour to the canvas edge on that
side and is on every row (`ShadowFieldReport.clearance*`, W32 X7): a band whose
outer edge is past it is not a reading of the shadow at that distance but a
reading of the corners the frame left. The axis says the same thing in its own
words at `truncatedSides` — *"rings past a truncated side's clearance are
averaged over an incomplete annulus, which pulls `falloffSigmaPx` toward the
window. Measured on this bed at roughly 8% low for a σ ≈ 17 px shadow read
through a 20 px margin"* — and that comment is about σ; this rule is the same
qualification applied to the transmission profile, where it can be enforced per
band instead of caveated per cell.

The rule is geometric, so the admitted set is a property of the component and
the scale rather than of the scene, and every cell at a span carries the same
one. `bands-used` is printed beside every figure anyway, because a cell can
still fail to IDENTIFY an admitted band (a flat backdrop, or fewer than the
axis's 32 samples), and a figure whose band set differs from its span's is not
the same statistic.

## Why two candidates and not one

W30 claimed three rows through the shadow and the read **refuted** them
(Decision Log 5 (d), claims §5.159 §7): the σ law's lever moved — the CSS group
clip at span 160 went 33.05 → 45.79 CSS px — and the rows moved by 0.0002 where
they needed 0.016, because SSIM over a whole cell is dominated by the interior
and the backdrop. The biggest movers of that whole read were `falloffSigmaWeb`,
by up to 30 CSS px, on an axis no gated bound is stated over. W30's Deferred
item 1 is therefore "a metric that reads the exterior's width", and its item 9
is a second thing the eye found and no metric reads: below a span-160 panel the
×8 difference carries visible level CONTOURS rather than a featureless haze
(§5.160 §6). Those are two different quantities — a width and a shape — so this
gate computes one candidate for each and lets the bed say which is worth a
clause.

**Candidate (i), the fitted σ's relative error.** Per cell,
`|falloffSigmaWeb − falloffSigmaNative| / falloffSigmaNative`, with both sides
divided by the row's own scale so they are in CSS px — §5.154 §4's correction
verbatim, the same arithmetic `shadow-cut.py` applies. It is the quantity W30's
verdict names as the biggest mover, read web-against-native on the same cell
instead of against the document's leaf.

**Candidate (ii), the departure profile's shape.** The shadow axis already
carries, per cell, an affine map of the backdrop `y = a·bg + c` fitted per band
and per direction in linear light (W14 X7, `ShadowAffineSample`): `a` is the
transmission the exterior applies to the backdrop at that distance and `c` is
the light it adds. The sequence of `a` with distance **is** the falloff's shape,
measured without assuming the profile is a blurred edge at all, and it lives
strictly outside the declared contour, so nothing about the interior can dilute
it. The one-number summary is defined at `T` below.

## The exclusions, and whose rule they are

Candidate (i) drops a cell whose fitted σ exceeds the casting span **on either
side** — W30 G0's rule (`σ_css > span`, claims §5.156 §2): a fitted blur wider
than the surface casting it has no edge left in the measuring window, so the
number is a reading of the backdrop and not of the material. G0 applied it to
the native side; a web side can run away the same way and for the same reason,
so it is applied to both here and every exclusion is named.

Candidate (ii) drops a band the axis itself left unidentifiable — a flat
backdrop makes `a` and `c` collinear, and a band the frame ran out of has too
few pixels. Those absences are the axis's own (`ShadowAffineAbsence`), never
zeroed, and a cell with no identified band in the shape window carries no `T`.

It also drops a cell whose `backdropSupport` is below the axis's own
`DEFAULT_MIN_BACKDROP_SUPPORT` of 0.1 — the fraction of the exterior whose
backdrop clears the level at which a shadow is recoverable at all. The affine
pair is reported on those cells by design (a lift is measured cleanly over
black, which is exactly where a ratio has no denominator), but a TRANSMISSION
error over a backdrop with no light to remove is arithmetic on no information:
`impulse` (support 0.004) and `dark-solid` (0) both read `T` exactly 0.000000 on
every band, which is the backdrop's floor and not a fidelity reading. The
constant is the axis's, not this gate's, and the cells it removes are counted
and named by class.

**Beside, 2026-09-21 (review closure; claims §5.162 §9, finding B-2). The two
sentences above overstate what this rule does, and the correction is measured in
`support-rule-check.py` / `.txt` beside this file — nothing this reader prints
moves.** The 48 `dark-solid` rows identify NO affine band in 3–48 CSS px at all,
so they carry no `T` with the rule or without it: the rule's real reach is the
**32 `impulse` rows**, not eighty. And those 32 do not all read zero — **14 of
them carry a non-zero `T`, from 0.000295 to 0.004287**, the largest being
`impulse__rrect-md__rest` on the 1x light CSS tier, whose Δa reads −0.005190,
−0.012409 and 0.000000 over the `6-12`, `12-24` and `24-48` bands. So "left in,
they would have made the bed look better" is wrong in count for all eighty and
wrong in direction for the fourteen. The rule is nevertheless KEPT, and for the
reason it was taken rather than for the one written down: it is the shadow
axis's own condition on reporting a normalised figure, and admitting all 32
moves **no upper middle order statistic on the WebGPU tier**, the bed C1 is read
on. It moves twelve per-span COUNTS and two CSS-tier span-44 medians (1x light
0.00518 → 0.00512, 2x dark 0.00356 → 0.00290), neither of them a figure the
ledger or the declaration prints.

**Beside, 2026-09-21 (same finding): a code inconsistency, recorded and not
changed.** `shape_error()` applies this gate to `L` as well as to `T`, while the
justification above is that a LIFT is measured cleanly over black — which is
exactly where a transmission has no denominator. `L` is recorded and not bounded
(claims §5.162 §3), so the closure records the withheld `L` on every reached row
in `support-rule-check.txt` §2 rather than changing what this reader reports;
the withheld values are 0.000000–0.000004 on all 32. A later wave that wants `L`
over an unlit backdrop takes it from there, or moves the gate deliberately.

The `0-3` band is excluded from `T` by the axis's own caveat: it holds the
body's own edge, and vitrea's GPU capsule over-fills its declared contour by
3.5–4 CSS px where Apple's does by ≤ 1 (claims §5.62). Bands from `3-6` outward
are the shadow alone. `0-3` is tabled beside `T` rather than dropped from the
record, and `0-6` is never used because it overlaps `0-3` and `3-6` and is in
the axis only so published figures can be read without re-binning.

## The holdout, dropped by construction

`cells()` below is the one function every table here takes its rows from and it
drops every row whose `fixtureSet` is `holdout` before returning, printing the
count and the scenes it refused — `fit.py`'s `cells()` idiom (claims §5.156 §4),
which exists so that a reader cannot put a holdout number in front of the person
choosing constants by accident. `--with-holdout` is the deliberate exception and
has to be typed.

This gate types it, once, for the run committed as
`exterior-instrument-with-holdout.txt`, and the charter authorises exactly that:
G1's brief asks for "the seven missed rows' readings under each" statistic and
all seven are holdout rows. It costs the holdout rule nothing, because the rule
(Decision Log 1 (b) of W31, ruled) is about **reading the holdout at a
configuration** — capturing it and fitting after it — and no capture is taken
here, no constant is fitted here, and the rows read were already read at W30
G3b's canonical read of this very generation. A committed row re-read is not a
new read of the bed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent

MATRIX = PACKAGE / "results/matrix.json"
PROFILES = PACKAGE / "profiles"
SCENES = ROOT / "apps/reference-apple/scenes.json"
NOISE_BAR = PACKAGE / "results/2026-09-19-w29-g3b-shadow-recede/noise-bar.json"

CAPTURE = re.compile(r"materialProfile=(\S+) sha256:([0-9a-f]{12})")
GENERATION = "apple-macos-27.0-"
TIER = {"texture": "webgpu", "dom": "css"}
HOLDOUT = "holdout"

SPANS = [32, 44, 96, 128, 130, 160, 220]

# The affine bands, in CSS px outside the declared contour, in the axis's own
# order. `0-6` is deliberately absent: it overlaps the first two and exists in
# the axis only so §5.60 and §5.62's published lifts can be read unbinned.
BANDS = ["0-3", "3-6", "6-12", "12-24", "24-48"]

# The window `T` is taken over, and the width of each band in CSS px. `0-3` is
# out for the axis's own reason (the body's own edge lives in it); the widths
# are the weights, which makes `T` the distance-average of the transmission
# error over 3–48 CSS px rather than a mean over four bands of unequal reach.
SHAPE_BANDS = ["3-6", "6-12", "12-24", "24-48"]
BAND_WIDTH_CSS_PX = {"0-3": 3, "3-6": 3, "6-12": 6, "12-24": 12, "24-48": 24}

# The band's outer edge in CSS px — what the clearance is compared against.
# `SHADOW_AFFINE_BANDS_CSS_PX` in `src/metrics/shadow.ts` is the source; the
# labels are that list's own and the numbers are read out of the labels here
# rather than re-tabulated, so a band that moved there would not be silently
# mis-admitted here.
BAND_OUTER_CSS_PX = {band: int(band.split("-")[1]) for band in BANDS}

DIRECTIONS = ["all", "above", "below", "left", "right"]
# `SHADOW_DIRECTIONS` in `src/metrics/shadow.ts`, in its order: the four sectors
# without the pooled one.
SHADOW_SIDES = ["above", "below", "left", "right"]

# Which clearance field bounds which direction. `all` takes the minimum of the
# four, because the pooled band mixes pixels from all four sectors and is whole
# only where every sector's is.
CLEARANCE_FIELD = {
    "above": "clearanceAbove",
    "below": "clearanceBelow",
    "left": "clearanceLeft",
    "right": "clearanceRight",
}

# `metrics/shadow.ts`'s `DEFAULT_MIN_BACKDROP_SUPPORT`: the fraction of the
# exterior whose backdrop must clear the axis's floor before a normalised figure
# is reported at all. Candidate (ii) is a transmission, so it takes the same
# condition rather than inventing one.
MIN_BACKDROP_SUPPORT = 0.1

# The two cells the eye read at §5.160 §6, at the scale and the tier the sheets
# were made at: the span-44 caster the eye called the wave's clean win, and the
# span-160 panel under which it saw level contours rather than a haze.
EYE_CELLS = [
    ("photo__capsule-button__rest", "right — the difference is confined to the body"),
    ("photo__rrect-lg__rest", "wrong — visible level contours below the panel"),
]

# The seven rows `MISSED_27_ROWS` holds, derived from that list's own shape
# rather than from a sentence: tier key as the matrix writes it, profile, scene,
# metric, the recorded measurement and the bound. Every one is a holdout row,
# which is why this block only prints under `--with-holdout`.
MISSED_27_ROWS = [
    ("dom", "apple-macos-27.0-1x-light-standard-glass0.5",
     "checkerboard__glass-over-glass__rest", "ssimMean", 0.89531, "≥ 0.9"),
    ("dom", "apple-macos-27.0-1x-light-standard-glass0.5",
     "checkerboard__rrect-lg__rest", "ssimMean", 0.88423, "≥ 0.9"),
    ("dom", "apple-macos-27.0-1x-dark-standard-glass0.5",
     "photo__rrect-lg__rest", "oklabDeltaEP95", 0.20095, "≤ 0.18"),
    ("dom", "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
     "photo__rrect-lg__rest", "ssimOutside", 0.82695, "≥ 0.83"),
    ("dom", "apple-macos-27.0-2x-dark-standard-glass0.5",
     "photo__rrect-lg__rest", "oklabDeltaEP95", 0.19474, "≤ 0.19"),
    ("texture", "apple-macos-27.0-1x-dark-standard-glass0.5",
     "photo__rrect-lg__rest", "oklabDeltaEP95", 0.21531, "≤ 0.17"),
    ("texture", "apple-macos-27.0-2x-dark-standard-glass0.5",
     "photo__rrect-lg__rest", "oklabDeltaEP95", 0.21341, "≤ 0.17"),
]

B1_TOLERANCE = 0.05
B1_SPANS = [96, 128, 160]


# ---------------------------------------------------------------------------
# Reading the bed
# ---------------------------------------------------------------------------

def spans_of(components: dict) -> dict[str, int]:
    """The casting span: the declared component's SHORTER side.

    `shadow-cut.py`'s function verbatim, and for its reason — the span is read
    from `scenes.json` rather than tabulated, so a scene declaration that moves
    moves the table with it.
    """
    out = {}
    for name, spec in components.items():
        kind = spec["kind"]
        if kind in ("capsule", "rrect"):
            out[name] = min(spec["size"])
        elif kind == "stack":
            out[name] = min(spec["base"]["size"])
        elif kind == "group":
            out[name] = min(min(item["size"]) for item in spec["items"])
    return out


def shipped_hashes() -> dict[str, str]:
    """`departure-stat.py`'s `atAShippedDocument`, by the same rule."""
    return {
        f"packages/calibration/profiles/{p.name}":
            hashlib.sha256(p.read_bytes()).hexdigest()[:12]
        for p in sorted(PROFILES.glob("*.json"))
    }


def value(axis: dict, name: str):
    """A `MetricValue`'s number, or None where the field is absent."""
    field = axis.get(name)
    return field["value"] if isinstance(field, dict) and "value" in field else None


def cells(matrix: Path, with_holdout: bool = False) -> list[dict]:
    """Every cell of one matrix — MINUS the holdout rows.

    THE TABLES NEVER READ A HOLDOUT ROW UNLESS THE FLAG IS TYPED.

    `fit.py`'s `cells()` (claims §5.156 §4): the drop lives in the one function
    every reader in this file takes its rows from, rather than in each table's
    own filter, and the count and the scenes are printed rather than silently
    swallowed.
    """
    everything = json.loads(matrix.read_text())["cells"]
    if with_holdout:
        print(f"# --with-holdout: every row of {matrix.name} is read, the holdout included.")
        return everything
    dropped = [c for c in everything if c.get("fixtureSet") == HOLDOUT]
    if dropped:
        print(f"# {len(dropped)} holdout row(s) in {matrix.name} and NOT read:")
        for profile, scene in sorted(
            {(c["key"]["profileKey"], c["key"]["sceneId"]) for c in dropped}
        ):
            print(f"#   {profile} {scene}")
    return [c for c in everything if c.get("fixtureSet") != HOLDOUT]


def readings(matrix: Path, span_of: dict[str, int], at_documents: str,
             with_holdout: bool = False) -> list[dict]:
    """The macOS 27 generation's shadow rows, one record per cell.

    `at_documents` is `shipped` for the working file — the `capturePath` names a
    profile document and a twelve-hex content hash and the row counts only if
    that hash is the hash of the file on disk — and `any` for a superseded file,
    whose documents are by definition no longer the shipped ones. The observed
    document hashes are printed either way, so the generation a table was read
    at is in the output rather than in a memory.
    """
    hashes = shipped_hashes()
    out = []
    for cell in cells(matrix, with_holdout):
        profile_key = cell["key"]["profileKey"]
        if not profile_key.startswith(GENERATION):
            continue
        clause = CAPTURE.search(cell["key"]["web"]["capturePath"])
        if clause is None:
            continue
        if at_documents == "shipped" and hashes.get(clause.group(1)) != clause.group(2):
            continue
        shadow = cell.get("shadow")
        if shadow is None:
            continue
        scene = cell["key"]["sceneId"]
        parts = scene.split("__")
        component = parts[1] if len(parts) > 1 else ""
        rest = profile_key.removeprefix(GENERATION).removesuffix("-glass0.5")
        scale, _, tail = rest.partition("-")
        out.append({
            "profile": profile_key,
            "scene": scene,
            "backdrop": parts[0],
            "component": component,
            "span": span_of.get(component),
            "scale": int(scale.removesuffix("x")),
            "bed": f"{scale} {tail.replace('-standard', '')}",
            "scheme": "dark" if "-dark-" in profile_key else "light",
            "tier": TIER.get(cell["tier"], cell["tier"]),
            "set": cell.get("fixtureSet"),
            "state": cell.get("state"),
            "document": f"{clause.group(1)} sha256:{clause.group(2)}",
            "shadow": shadow,
        })
    return out


# ---------------------------------------------------------------------------
# The two statistics
# ---------------------------------------------------------------------------

def sigma_error(row: dict) -> tuple[float | None, float | None, float | None, str | None]:
    """Candidate (i): `|σ_web − σ_native| / σ_native`, both sides in CSS px.

    Returns `(σ_native_css, σ_web_css, relative error, exclusion)`. The
    exclusion is W30 G0's `σ_css > span` rule applied to BOTH sides; a cell
    excluded carries its two σ for the record and no error.
    """
    shadow, scale, span = row["shadow"], row["scale"], row["span"]
    native = value(shadow, "falloffSigmaNative")
    web = value(shadow, "falloffSigmaWeb")
    if native is None or web is None or span is None or native == 0:
        return None, None, None, None
    native_css, web_css = native / scale, web / scale
    if native_css > span or web_css > span:
        return native_css, web_css, None, "σ_css > span"
    return native_css, web_css, abs(web_css - native_css) / native_css, None


def clearance_css(row: dict, direction: str) -> float:
    """That direction's clearance, in CSS px — the row's own, divided by scale.

    `clearance*` is written in device px (`ShadowAxisReport`), and the bands are
    in CSS px, which is §5.154 §4's correction applied to a second field of the
    same axis. `all` takes the minimum of the four sides, because the pooled
    band's pixels come from all four.
    """
    shadow = row["shadow"]
    if direction == "all":
        return min(value(shadow, field) for field in CLEARANCE_FIELD.values()) / row["scale"]
    return value(shadow, CLEARANCE_FIELD[direction]) / row["scale"]


def admitted_bands(row: dict, direction: str = "all") -> list[str]:
    """The shape bands whose outer edge lies inside that direction's clearance.

    The rule, and the whole of it. A band from the `3-6` outward is admitted
    when its outer edge in CSS px is no greater than the clearance in the
    direction being read; `0-3` is never in the shape window for the axis's own
    reason (the body's edge lives in it) and is tabled beside.
    """
    limit = clearance_css(row, direction)
    return [band for band in SHAPE_BANDS if BAND_OUTER_CSS_PX[band] <= limit]


def affine(shadow: dict, side: str, direction: str = "all") -> dict[str, dict]:
    return {
        band["ringLabel"]: band
        for band in shadow.get(f"affine{side}", [])
        if band["direction"] == direction
    }


def shape_error(row: dict, direction: str = "all") -> dict:
    """Candidate (ii): the departure profile's shape, per band and summarised.

    `T` — the one-number summary, and the quantity a clause is declared on:

        T = Σ_b w_b · |a_web,b − a_native,b|  /  Σ_b w_b

    over the bands `3-6`, `6-12`, `12-24` and `24-48`, with `w_b` the band's
    width in CSS px. `a` is the transmission the exterior applies to its
    backdrop at that distance, in linear luminance, so `T` is the mean vertical
    gap between vitrea's falloff curve and Apple's over 3–48 CSS px outside the
    declared contour — a single number in the same unit as the curves.

    Why this form. A width statistic presumes the profile is a blurred edge and
    reports one parameter of it; the eye's residual at §5.160 §6 is a difference
    in the profile's SHAPE at one span, which a width cannot express. Weighting
    by band width rather than by band count makes `T` the discrete integral of
    the transmission error over distance, so a near band and a far band
    contribute what they cover; weighting by pixel count instead would hand the
    statistic to the outer bands' area, which is the same dilution that made
    whole-cell SSIM blind. `T` reduces to the departure statistic B3 already
    reads when the two profiles differ by a constant, and separates from it
    exactly when they differ in shape.

    `L` is the same weighted mean over `|c_web − c_native|` — the lift, the part
    a transmission cannot express — reported beside `T` and never summed into
    it: a shadow that removes less light and a shadow that adds some are
    different findings (W14 X7).

    `R`, the agreement radius, is the innermost band edge in CSS px from which
    every band outward agrees within the cell's own native-pair bar. Absent
    means the profiles never agree inside 48 CSS px.
    """
    native = affine(row["shadow"], "Native", direction)
    web = affine(row["shadow"], "Web", direction)
    per_band = {}
    for band in BANDS:
        n, w = native.get(band), web.get(band)
        if n is None or w is None:
            continue
        entry = {
            "levelNative": n["renderedLevelLinear"],
            "levelWeb": w["renderedLevelLinear"],
            "backdropStdDev": n["backdropStdDevLinear"],
        }
        if n.get("slopeALinear") is not None and w.get("slopeALinear") is not None:
            entry["slopeANative"] = n["slopeALinear"]
            entry["slopeAWeb"] = w["slopeALinear"]
            entry["deltaSlopeA"] = w["slopeALinear"] - n["slopeALinear"]
        if n.get("interceptCLinear") is not None and w.get("interceptCLinear") is not None:
            entry["interceptCNative"] = n["interceptCLinear"]
            entry["interceptCWeb"] = w["interceptCLinear"]
            entry["deltaInterceptC"] = w["interceptCLinear"] - n["interceptCLinear"]
        per_band[band] = entry

    admitted = admitted_bands(row, direction)

    def weighted(field: str) -> tuple[float | None, tuple[str, ...]]:
        usable = [b for b in admitted if b in per_band and field in per_band[b]]
        if not usable:
            return None, ()
        total = sum(BAND_WIDTH_CSS_PX[b] for b in usable)
        return (sum(BAND_WIDTH_CSS_PX[b] * abs(per_band[b][field]) for b in usable) / total,
                tuple(usable))

    T, bands_used = weighted("deltaSlopeA")
    L, lift_bands = weighted("deltaInterceptC")
    support = value(row["shadow"], "backdropSupport")
    if support is not None and support < MIN_BACKDROP_SUPPORT:
        return {"bands": per_band, "T": None, "L": None, "bandsUsed": (),
                "liftBands": (), "admitted": tuple(admitted), "unsupported": support}
    return {"bands": per_band, "T": T, "L": L, "bandsUsed": bands_used,
            "liftBands": lift_bands, "admitted": tuple(admitted), "unsupported": None}


def legacy_T(row: dict, direction: str = "all") -> float | None:
    """W31 G1's `T`, kept verbatim so the change the rule makes is measurable.

    Its `weighted()` renormalised over every band the cell IDENTIFIED in 3–48
    CSS px, with no reference to the clearance (§5.162 §1; the reader's line
    ~400). This gate does not withdraw that number — it is committed evidence —
    it prints it beside the admitted-band one so a reader can see at which spans
    the two are the same statistic and at which they are not.
    """
    native = affine(row["shadow"], "Native", direction)
    web = affine(row["shadow"], "Web", direction)
    support = value(row["shadow"], "backdropSupport")
    if support is not None and support < MIN_BACKDROP_SUPPORT:
        return None
    usable = [b for b in SHAPE_BANDS
              if b in native and b in web
              and native[b].get("slopeALinear") is not None
              and web[b].get("slopeALinear") is not None]
    if not usable:
        return None
    total = sum(BAND_WIDTH_CSS_PX[b] for b in usable)
    return sum(BAND_WIDTH_CSS_PX[b] * abs(web[b]["slopeALinear"] - native[b]["slopeALinear"])
               for b in usable) / total


def window_departure(row: dict) -> dict:
    """The departure restricted to the admitted bands of direction `all`.

    `meanDeparture{Native,Web}` on a row is `mean(backdrop − rendered)` over the
    WHOLE exterior — every exterior pixel, with no backdrop floor and no window
    (`shadowField`). B3 is stated over it and stays stated over it. W32 clause 3
    solves the six occlusion anchors from a departure restricted to 3–48 CSS px
    instead, because the `0-3` band holds the body's own over-fill — vitrea's
    GPU capsule spills 3.5–4 CSS px past its declared contour against Apple's
    ≤ 1 (§5.62) — which at span 160 reads `Δa` +0.090 to +0.157, an order of
    magnitude above the shadow bands and of the opposite sign.

    The restricted quantity is computable from a committed row and needs no
    render: each affine band entry carries `sampleCount`, `backdropMeanLinear`
    and `renderedLevelLinear` on both sides over the SAME pixels (the bands are
    cut from the scene's own distance field, so the two sides' counts agree),
    and the sample-count-weighted mean of `backdropMean − renderedLevel` over
    the admitted bands is the same functional as `meanDeparture` over the
    window's pixels. It is exact rather than an approximation: a mean of means
    weighted by their counts is the mean of the union.

    The bands are the direction-`all` entries, which are the four sectors
    pooled, so the restricted departure is over the same pixels as `T`.
    """
    admitted = admitted_bands(row, "all")
    native = affine(row["shadow"], "Native", "all")
    web = affine(row["shadow"], "Web", "all")
    used, n_total, native_sum, web_sum = [], 0, 0.0, 0.0
    for band in admitted:
        n, w = native.get(band), web.get(band)
        if n is None or w is None:
            continue
        count = n["sampleCount"]
        used.append(band)
        n_total += count
        native_sum += count * (n["backdropMeanLinear"] - n["renderedLevelLinear"])
        web_sum += count * (w["backdropMeanLinear"] - w["renderedLevelLinear"])
    if n_total == 0:
        return {"native": None, "web": None, "difference": None, "bands": (), "samples": 0}
    return {"native": native_sum / n_total, "web": web_sum / n_total,
            "difference": (web_sum - native_sum) / n_total,
            "bands": tuple(used), "samples": n_total}


def reach_fields(row: dict) -> dict:
    """The per-direction extents and the two offsets, both sides, web − native.

    Absent means the walk reached the canvas edge and the axis withheld the
    number rather than reporting the size of the window (`ShadowFieldReport`).
    The absence is the reading this gate counts: a span at which the web side
    carries no extent is a span at which the bed cannot see vitrea's reach at
    all, whatever its `T` says.
    """
    shadow = row["shadow"]
    out = {}
    for direction in SHADOW_SIDES:
        field = f"extent{direction.capitalize()}"
        native, web = value(shadow, field + "Native"), value(shadow, field + "Web")
        out[direction] = {
            "native": None if native is None else native / row["scale"],
            "web": None if web is None else web / row["scale"],
            "delta": None if native is None or web is None else (web - native) / row["scale"],
        }
    for axis_name in ("offsetX", "offsetY"):
        native, web = value(shadow, axis_name + "Native"), value(shadow, axis_name + "Web")
        out[axis_name] = {
            "native": None if native is None else native / row["scale"],
            "web": None if web is None else web / row["scale"],
            "delta": None if native is None or web is None else (web - native) / row["scale"],
        }
    return out


def agreement_radius(row: dict, bar: float) -> int | None:
    """The innermost band edge from which every band outward is within `bar`.

    Read over the ADMITTED bands only, which is this gate's change: a radius
    declared from a band the frame ate is a statement about the corners of the
    capture. Where the admitted set stops short of 48 CSS px the radius, if
    found, is a radius inside the clearance and says so in `bands-used`.
    """
    shape = shape_error(row)["bands"]
    admitted = admitted_bands(row, "all")
    for index, band in enumerate(admitted):
        tail = [b for b in admitted[index:] if b in shape and "deltaSlopeA" in shape[b]]
        if not tail:
            continue
        if all(abs(shape[b]["deltaSlopeA"]) <= bar for b in tail):
            return int(band.split("-")[0])
    return None


# ---------------------------------------------------------------------------
# The native pair's noise bar
# ---------------------------------------------------------------------------

def noise_bars() -> tuple[dict, dict]:
    """W29 G3b's `noise-bar.json`: what "within noise" means on a native pair.

    The bar is the MAX over the 21 unordered pairs of a cell's seven raw macOS
    27 runs, per metric — "beyond anything this bed did against itself". Two of
    its rows are this gate's, and they are the same functions of a pair of
    captures that the two statistics here are:

      - `shadowFalloffSigmaDeltaPx`, the bar on candidate (i)'s two σ;
      - `shadowAffineSlopeDeltaMax`, the WORST band-and-direction difference in
        `a` between two runs — an upper bound on what a width-weighted mean of
        the same differences could be, which is the bar `T` is read against.

    Where a cell's own pairwise max is zero — seven byte-identical runs — the
    bar is the bed's smallest non-zero max for that metric, so a cell that
    happened to be perfectly stable is not given an infinitely sharp instrument.
    That is the bar's own rule, not this gate's.
    """
    document = json.loads(NOISE_BAR.read_text())
    floors = document["bedMinimumNonZeroBar"]
    per_cell = {}
    for cell in document["cells"]:
        pairwise = cell["pairwise"]
        per_cell[(cell["profileKey"], cell["sceneId"])] = {
            metric: pairwise[metric]["max"] for metric in pairwise
        }
    return per_cell, floors


def bar_for(bars: dict, floors: dict, row: dict, metric: str) -> float:
    reading = bars.get((row["profile"], row["scene"]), {}).get(metric)
    if reading is None or reading == 0:
        return floors[metric]
    return reading


# ---------------------------------------------------------------------------
# Printing
# ---------------------------------------------------------------------------

def upper_middle(values: list[float]) -> float:
    """`law-tables.txt`'s convention and W30 G0's statistic: `sorted[n // 2]`."""
    return sorted(values)[len(values) // 2]


def summarise(values: list[float], width: int, places: int) -> str:
    if not values:
        return f"{'—':>{width}}"
    body = (f"{upper_middle(values):.{places}f} [{min(values):.{places}f}–"
            f"{max(values):.{places}f}] ({len(values)})")
    return body.rjust(width)


def bed_order(rows: list[dict]) -> list[str]:
    return sorted({r["bed"] for r in rows}, key=lambda b: (b.split()[1], b.split()[0]))


def set_class(row: dict) -> str:
    if row["set"] == "probe":
        return "probe"
    if row["set"] == HOLDOUT:
        return "holdout"
    return "cal+val"


def ratio_of(values: list[float]) -> str:
    """An order statistic of a ratio, or `—` where the denominator was zero.

    Printed rather than `nan`, because on the INACTIVE pose the native side's
    in-window departure is exactly zero on a large part of the bed — Apple's
    receded window removes no light at all from 3 CSS px outward on those cells
    — and a ratio there is not a small number but an absent one. The count of
    cells whose native window departure is exactly zero is printed beside it.
    """
    return f"{upper_middle(values):.2f}" if values else "—"


def full_set(row: dict, direction: str = "all") -> bool:
    """Does this row carry its span's WHOLE admitted set in that direction?

    The pooling rule of W32 clause 1: an order statistic is taken over cells
    carrying the same admitted band set, so a cell that identified only two of
    the three bands its clearance admits is not averaged in with cells that
    identified all three. It is counted and reported apart instead.
    """
    return row["bandsUsedDir"][direction] == row["admittedDir"][direction]


def band_set_label(bands) -> str:
    return "/".join(bands) if bands else "—"


def span_table(rows: list[dict], title: str, pick, width: int, places: int,
               keep=lambda r: True) -> None:
    print(title)
    print("-" * 160)
    for tier in ("webgpu", "css"):
        selected = [r for r in rows if r["tier"] == tier and keep(r)]
        if not selected:
            continue
        print(f"  tier {tier}")
        print(f"    {'bed':<36}{'set':<10}" + "".join(f"{('span ' + str(s)):>{width}}" for s in SPANS))
        for bed in bed_order(selected):
            for klass in ("cal+val", "probe", "holdout"):
                line = f"    {bed:<36}{klass:<10}"
                printed = False
                for span in SPANS:
                    values = [
                        v for r in selected
                        if r["bed"] == bed and r["span"] == span and set_class(r) == klass
                        for v in [pick(r)] if v is not None
                    ]
                    if values:
                        printed = True
                    line += summarise(values, width, places)
                if printed:
                    print(line)
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", default=str(MATRIX),
                        help="the matrix to read; defaults to the committed working file")
    parser.add_argument("--at-documents", choices=("shipped", "any"), default="shipped",
                        help="'shipped' keeps only rows whose capturePath hash is a document on "
                             "disk today; 'any' is for a superseded generation, whose documents "
                             "are by definition not the shipped ones")
    parser.add_argument("--against", action="append", default=[],
                        help="a superseded generation to compare against, as LABEL=path[,path]; "
                             "the paths are named BY NAME under results/superseded/; repeatable")
    parser.add_argument("--with-holdout", action="store_true",
                        help="the deliberate exception: read the holdout rows too")
    parser.add_argument("--out", default=str(HERE), help="where the JSON is written")
    args = parser.parse_args()

    matrix = Path(args.matrix)
    out_dir = Path(args.out)
    scenes = json.loads(SCENES.read_text())
    span_of = spans_of(scenes["components"])
    bars, floors = noise_bars()

    print("W32 G0 — the direction-resolved exterior cut, read inside each cell's own clearance")
    print("=" * 160)
    print()
    print(f"Matrix:  {matrix}")
    print(f"Spans:   the declared component's shorter side, from {SCENES.relative_to(ROOT)}")
    print("         " + "  ".join(f"{k}={v}" for k, v in sorted(span_of.items(), key=lambda kv: kv[1])))
    print("Cells:   the macOS 27 generation, at the documents on disk" if args.at_documents == "shipped"
          else "Cells:   the macOS 27 generation, at whatever documents the rows name")
    print("Nothing here is fitted, adopted or captured. Every figure is a cut of committed evidence.")
    print()

    rows = readings(matrix, span_of, args.at_documents, args.with_holdout)
    print()

    for row in rows:
        native, web, error, excluded = sigma_error(row)
        row["sigmaNativeCss"], row["sigmaWebCss"] = native, web
        row["sigmaRelativeError"], row["sigmaExcluded"] = error, excluded
        row["clearanceCss"] = {d: clearance_css(row, d) for d in DIRECTIONS}
        row["Tdir"], row["Ldir"] = {}, {}
        row["bandsUsedDir"], row["admittedDir"], row["perBand"] = {}, {}, {}
        for direction in DIRECTIONS:
            shape = shape_error(row, direction)
            row["Tdir"][direction] = shape["T"]
            row["Ldir"][direction] = shape["L"]
            row["bandsUsedDir"][direction] = shape["bandsUsed"]
            row["admittedDir"][direction] = shape["admitted"]
            row["perBand"][direction] = {
                band: {"deltaA": entry.get("deltaSlopeA"),
                       "deltaC": entry.get("deltaInterceptC")}
                for band, entry in shape["bands"].items()
            }
            if direction == "all":
                row["T"], row["L"] = shape["T"], shape["L"]
                row["bandsUsed"] = shape["bandsUsed"]
                row["admitted"] = shape["admitted"]
                row["backdropUnsupported"] = shape["unsupported"]
                row["bands"] = shape["bands"]
        row["reach"] = reach_fields(row)
        row["departure"] = {
            "native": value(row["shadow"], "meanDepartureNative"),
            "web": value(row["shadow"], "meanDepartureWeb"),
            "window": window_departure(row),
        }
        native_d, web_d = row["departure"]["native"], row["departure"]["web"]
        row["departure"]["ratio"] = (
            None if not native_d else web_d / native_d)
        window = row["departure"]["window"]
        row["departure"]["windowRatio"] = (
            None if not window["native"] else window["web"] / window["native"])

    documents = sorted({r["document"] for r in rows})
    print("§0. The bed")
    print("-" * 160)
    print(f"  {len(rows)} macOS 27 rows carry a shadow axis. Documents they name:")
    for document in documents:
        count = sum(1 for r in rows if r["document"] == document)
        print(f"    {count:>4}  {document}")
    with_sigma = [r for r in rows if r["sigmaRelativeError"] is not None]
    excluded = [r for r in rows if r["sigmaExcluded"] is not None]
    no_pair = [r for r in rows if r["sigmaNativeCss"] is None or r["sigmaWebCss"] is None]
    with_t = [r for r in rows if r["T"] is not None]
    print(f"  candidate (i)  reads {len(with_sigma)} rows: {len(no_pair)} carry no σ on one or both "
          f"sides (the axis's own absence — no backdrop light to remove, or fewer than three rings "
          f"past the edge ring), {len(excluded)} are excluded by W30 G0's rule.")
    unsupported = [r for r in rows if r["backdropUnsupported"] is not None]
    print(f"  candidate (ii) reads {len(with_t)} rows: "
          f"{len(rows) - len(with_t) - len(unsupported)} identify no affine band in 3–48 CSS px "
          f"(a solid backdrop makes `a` and `c` collinear), and {len(unsupported)} have a backdrop "
          f"with no light to remove.")
    by_backdrop = {}
    for row in unsupported:
        by_backdrop.setdefault(row["backdrop"], []).append(row["backdropUnsupported"])
    for backdrop, supports in sorted(by_backdrop.items()):
        print(f"    {len(supports):>4} rows over `{backdrop}`, backdropSupport "
              f"{min(supports):.3f}–{max(supports):.3f}, below the axis's own "
              f"{MIN_BACKDROP_SUPPORT}")
    print()
    print("  The cells candidate (i) excludes, every one named:")
    for row in sorted(excluded, key=lambda r: -max(r["sigmaNativeCss"], r["sigmaWebCss"])):
        print(f"    σ native {row['sigmaNativeCss']:8.2f}  web {row['sigmaWebCss']:8.2f}  "
              f"span {row['span']:>3}  {row['bed']:<36}{row['tier']:<8}{row['scene']:<50}{row['set']}")
    print()

    print("§0b. The admitted-band rule, per span and per direction")
    print("-" * 160)
    print("  A band is admitted where its OUTER edge in CSS px is inside that direction's own")
    print("  clearance (the row's `clearance*` in device px, divided by the row's scale); `all`")
    print("  takes the minimum of the four. The rule is geometric, so the set is a property of the")
    print("  component and the scale — every cell at a span carries the same one, which is what")
    print("  makes an order statistic over a span comparable at all (W32 clause 1).")
    print()
    print(f"  {'span':>5}  {'component':<18}{'scale':>6}{'clearance CSS px (a/b/l/r)':>32}   "
          f"{'admitted (all)':<24}{'above':<24}{'below':<24}{'left':<24}{'right':<24}{'rows':>6}")
    seen: dict[tuple, dict] = {}
    for row in rows:
        key = (row["span"], row["component"], row["scale"])
        entry = seen.setdefault(key, {"n": 0, "row": row})
        entry["n"] += 1
    for key in sorted(seen, key=lambda k: (k[0] or 0, k[1], k[2])):
        span, component, scale = key
        row = seen[key]["row"]
        shadow = row["shadow"]
        clearances = "/".join(
            f"{value(shadow, CLEARANCE_FIELD[d]) / scale:.2f}" for d in SHADOW_SIDES)
        line = (f"  {span if span is not None else '—':>5}  {component:<18}{scale:>6}"
                f"{clearances:>32}   {band_set_label(row['admittedDir']['all']):<24}")
        for direction in SHADOW_SIDES:
            line += f"{band_set_label(row['admittedDir'][direction]):<24}"
        print(line + f"{seen[key]['n']:>6}")
    print()
    print("  What the bed says, and where it departs from what the charter expected:")
    for span in SPANS:
        picked = [r for r in rows if r["span"] == span]
        if not picked:
            continue
        sets = sorted({band_set_label(r["admittedDir"]["all"]) for r in picked})
        short = [r for r in picked if not full_set(r)]
        print(f"    span {span:>3}: admitted (all) {', '.join(sets):<24} "
              f"{len(picked)} rows, {len(short)} of which identify fewer bands than the set admits")
    print()

    active = lambda r: r["state"] != "inactive"
    print("§1 to §3b read the ACTIVE pose only, which is the pose W30 G0's own σ cut is read on")
    print("(claims §5.156 §2). The inactive pose is a receded document's difference over the active")
    print("one and is reported apart, at §7.")
    print()
    span_table(rows, "§1. Candidate (i): the fitted σ's relative error, `median [min–max] (n)`",
               lambda r: r["sigmaRelativeError"], 30, 3, active)

    print("§2. Candidate (i) beside B1's per-bed windows, on the same cells")
    print("-" * 160)
    print("  B1 (adopted, W30 G4, claims §5.160) asserts the σ law's closed form is within ±5 % of")
    print("  the bed's median NATIVE σ at spans 96, 128 and 160. Candidate (i) asserts the RENDERED")
    print("  σ is within some tolerance of the same native σ on the same cell. The two sides of B1")
    print("  are the document's blur leaf and a fit of Apple's render; candidate (i)'s two sides are")
    print("  fits of both renders by one instrument. Where they disagree, the law is not what is")
    print("  wrong — what is wrong is that the law's σ is not the whole of what vitrea draws.")
    print()
    print("  `B1 window` is that bed's own ±5 % window around its median native σ — the interval")
    print("  B1 requires the LAW's σ to sit in. `law` and `rendered` are marked IN or OUT of it,")
    print("  which is the comparison the charter asks for: one window, two things held up to it.")
    print()
    print(f"  {'bed':<36}{'tier':<8}{'span':>5}{'n':>4}{'native σ':>11}"
          f"{'B1 window':>20}{'law σ':>9}{'law err':>9}{'':>5}"
          f"{'rendered σ':>12}{'(i)':>8}{'':>5}{'σ_web − σ_nat':>15}")
    documents_by_scheme = {}
    for scheme, name in (("light", "apple-macos-27.0-1x-light-standard-glass0.5.json"),
                         ("dark", "apple-macos-27.0-1x-dark-standard-glass0.5.json")):
        documents_by_scheme[scheme] = json.loads((PROFILES / name).read_text())["patch"]["outerShadow"]

    def law_sigma(scheme: str, span: int) -> float:
        leaves = documents_by_scheme[scheme]
        return leaves["sigmaPx"] + max(
            leaves["sigmaThinOffsetPx"],
            leaves["sigmaSlopePerSpan"] * (span - leaves["sigmaSpanRefPx"]),
        )

    print("  Extended beyond §5.162 §2's eight rows, for the record and at W32 clause 1's ask:")
    print("  every bed and every span the bed carries, spans 32 and 44 included, where the law's")
    print("  σ is the thin regime's floor and the instrument's isotropic ring mean is mostly")
    print("  reading the displacement (§5.162 §2). B1 is stated at 96, 128 and 160 only; the rows")
    print("  at 32, 44 and 130 are printed and are not B1's.")
    print()
    for bed in bed_order(with_sigma):
        for tier in ("webgpu", "css"):
            for span in SPANS:
                picked = [r for r in with_sigma
                          if r["bed"] == bed and r["tier"] == tier and r["span"] == span
                          and r["state"] != "inactive"]
                if not picked:
                    continue
                native = upper_middle([r["sigmaNativeCss"] for r in picked])
                rendered = upper_middle([r["sigmaWebCss"] for r in picked])
                law = law_sigma(picked[0]["scheme"], span)
                law_error = (law - native) / native
                low, high = native * (1 - B1_TOLERANCE), native * (1 + B1_TOLERANCE)
                inside = lambda v: " IN " if low <= v <= high else "OUT"
                window = f"[{low:.3f}, {high:.3f}]"
                print(f"  {bed:<36}{tier:<8}{span:>5}{len(picked):>4}{native:>11.3f}"
                      f"{window:>20}{law:>9.3f}{law_error * 100:>8.2f}%{inside(law):>5}"
                      f"{rendered:>12.3f}"
                      f"{upper_middle([r['sigmaRelativeError'] for r in picked]):>8.3f}"
                      f"{inside(rendered):>5}"
                      f"{rendered - native:>15.3f}"
                      f"{('  B1' if span in B1_SPANS else '    '):>6}")
    print()
    signed = [r for r in with_sigma
              if r["span"] is not None and r["span"] >= 96 and r["state"] != "inactive"]
    wider = sum(1 for r in signed if r["sigmaWebCss"] > r["sigmaNativeCss"])
    print(f"  Sign, at the thick spans: the rendered σ is WIDER than the native on {wider} of "
          f"{len(signed)} rows that resolve both.")
    print()

    print("§3 and §3b are read over the ADMITTED bands and over the cells carrying their span's")
    print("whole admitted set, which is W32 clause 1's pooling rule. §5.162's own `T` renormalised")
    print("per cell over whatever bands it found usable, so at spans 128 and 160 it summed bands")
    print("the frame had eaten; §3c prints the two side by side.")
    print()
    span_table(rows, "§3. Candidate (ii): `T`, the width-weighted transmission error over the admitted bands",
               lambda r: r["T"], 32, 5, lambda r: active(r) and full_set(r))
    span_table(rows, "§3b. `L` beside it: the same weighted mean over the LIFT `c`, linear luminance",
               lambda r: r["L"], 32, 5, lambda r: active(r) and full_set(r))

    print("§3c. What the admitted-band rule changes, against W31 G1's own renormalisation")
    print("-" * 160)
    print("  Left: `T` as §5.162 read it — every band the cell identified in 3–48 CSS px, the")
    print("  weights renormalised per cell. Right: `T` over the admitted bands only, on the cells")
    print("  carrying the span's whole set. A span whose clearance holds all four bands reads the")
    print("  same number twice; a span whose clearance does not is where the two part company.")
    print()
    print(f"  {'bed':<38}{'span':>5}{'admitted':>24}{'n (W31)':>9}{'T (W31 rule)':>14}"
          f"{'n (admitted)':>14}{'T (admitted)':>14}{'Δ':>12}")
    for bed in bed_order(rows):
        for span in SPANS:
            picked = [r for r in rows if r["bed"] == bed and r["span"] == span
                      and r["tier"] == "webgpu" and active(r) and r["set"] != HOLDOUT]
            old = [legacy_T(r) for r in picked]
            old = [v for v in old if v is not None]
            new = [r["T"] for r in picked if full_set(r) and r["T"] is not None]
            if not old and not new:
                continue
            admitted = band_set_label(picked[0]["admittedDir"]["all"]) if picked else "—"
            left = f"{upper_middle(old):.5f}" if old else "—"
            right = f"{upper_middle(new):.5f}" if new else "—"
            delta = (f"{upper_middle(new) - upper_middle(old):+.5f}" if old and new else "—")
            print(f"  {bed:<38}{span:>5}{admitted:>24}{len(old):>9}{left:>14}"
                  f"{len(new):>14}{right:>14}{delta:>12}")
    print()

    print("§4. Candidate (ii) per band and per direction, on the cells the eye read (§5.160 §6)")
    print("-" * 160)
    print("  The sheets were native | vitrea WebGPU | difference ×8 at 2x, two cells per scheme.")
    print("  `below` is the direction the material's own `offsetPx` displaces the shadow into.")
    print()
    for scene, verdict in EYE_CELLS:
        for bed in ("2x light", "2x dark"):
            picked = [r for r in rows
                      if r["scene"] == scene and r["bed"] == bed and r["tier"] == "webgpu"]
            if not picked:
                print(f"  {scene} on {bed}: not read here (holdout, without the flag)")
                continue
            row = picked[0]
            slope_bar = bar_for(bars, floors, row, "shadowAffineSlopeDeltaMax")
            radius = agreement_radius(row, slope_bar)
            print(f"  {scene} — {bed}, span {row['span']}, {row['set']} — the eye: {verdict}")
            first = ("—" if row["sigmaRelativeError"] is None
                     else f"{row['sigmaRelativeError']:.3f}")
            print(f"    candidate (i) {first}   candidate (ii) T {row['T']:.5f}   "
                  f"L {row['L']:.5f}   native-pair bar on `a` {slope_bar:.6f}   "
                  f"agreement radius {radius if radius is not None else 'none inside 48 CSS px'}")
            header = f"    {'band':<8}" + "".join(f"{d:>13}" for d in DIRECTIONS)
            print(header)
            for field, label in (("deltaSlopeA", "Δa (web−nat)"), ("deltaInterceptC", "Δc (web−nat)")):
                for band in BANDS:
                    line = f"    {band:<8}"
                    printed = False
                    for direction in DIRECTIONS:
                        entry = shape_error(row, direction)["bands"].get(band, {})
                        reading = entry.get(field)
                        if reading is None:
                            line += f"{'—':>13}"
                        else:
                            printed = True
                            line += f"{reading:>13.5f}"
                    if printed:
                        print(f"{line}   {label}")
            print()
    print()

    if args.with_holdout:
        print("§5. The seven rows `MISSED_27_ROWS` holds, under both statistics")
        print("-" * 160)
        print("  Every one is a holdout row, which is why this block needs the flag. The readings")
        print("  sit beside the SSIM or ΔE the row is missed on, so a later wave can see which")
        print("  statistic reads the width that whole-cell SSIM could not.")
        print()
        index = {(r["tier"], r["profile"], r["scene"]): r for r in rows}
        print(f"  {'tier':<8}{'scene':<38}{'bed':<36}{'metric':<16}{'measured':>10}{'bound':>9}"
              f"{'span':>5}{'σ nat':>8}{'σ web':>8}{'(i)':>9}{'(ii) T':>10}{'(ii) L':>10}")
        for tier, profile, scene, metric, measured, bound in MISSED_27_ROWS:
            row = index.get((TIER[tier], profile, scene))
            if row is None:
                print(f"  {tier:<8}{scene:<38}{profile:<56}{metric:<16}"
                      f"{'not in the bed read here'}")
                continue
            error = row["sigmaRelativeError"]
            print(f"  {tier:<8}{scene:<38}{row['bed']:<36}{metric:<16}{measured:>10.5f}{bound:>9}"
                  f"{row['span']:>5}{row['sigmaNativeCss']:>8.2f}{row['sigmaWebCss']:>8.2f}"
                  f"{error:>9.3f}{row['T']:>10.5f}{row['L']:>10.5f}")
        print()
        print("  The same seven, direction-resolved and with their reach — what the shadow could")
        print("  reach on each. `T_dir` is over the admitted bands; an extent printed `—` is one")
        print("  the frame ate, and at span 160 that is every side on both sides of the cell.")
        print()
        print(f"  {'tier':<8}{'scene':<38}{'bed':<36}{'admitted':>12}"
              + "".join(f"{d:>10}" for d in DIRECTIONS)
              + "".join(f"{('Δ' + d):>9}" for d in SHADOW_SIDES) + f"{'ΔoffY':>9}")
        for tier, profile, scene, metric, measured, bound in MISSED_27_ROWS:
            row = index.get((TIER[tier], profile, scene))
            if row is None:
                continue
            line = (f"  {tier:<8}{scene:<38}{row['bed']:<36}"
                    f"{band_set_label(row['admittedDir']['all']):>12}")
            for direction in DIRECTIONS:
                reading = row["Tdir"][direction]
                line += f"{'—':>10}" if reading is None else f"{reading:>10.5f}"
            for field in SHADOW_SIDES + ["offsetY"]:
                delta = row["reach"][field]["delta"]
                line += f"{'—':>9}" if delta is None else f"{delta:>9.2f}"
            print(line)
        print()
    else:
        print("§5. The seven rows `MISSED_27_ROWS` holds — NOT READ")
        print("-" * 160)
        print(f"  All {len(MISSED_27_ROWS)} are holdout rows and this reader drops the holdout by")
        print("  construction. Re-run with `--with-holdout` for the reported check.")
        print()

    print("§6. The native pair's noise bar, on both statistics")
    print("-" * 160)
    print(f"  Source: {NOISE_BAR.relative_to(PACKAGE)} — the max over 21 pairs of a cell's seven")
    print("  raw macOS 27 runs, which is what `within noise` means on this bed.")
    print()
    for metric, label, places in (("shadowFalloffSigmaDeltaPx", "candidate (i)'s σ, device px", 6),
                                  ("shadowAffineSlopeDeltaMax", "candidate (ii)'s `a`, worst band", 6),
                                  ("shadowAffineInterceptDeltaMax", "the lift `c`, worst band", 8)):
        readings_for = sorted(
            per_cell[metric] for per_cell in bars.values() if metric in per_cell
        )
        p95 = readings_for[int(0.95 * len(readings_for))]
        non_zero = sum(1 for v in readings_for if v > 0)
        print(f"  {label:<36} n {len(readings_for):>4}  non-zero {non_zero:>4}  "
              f"p95 {p95:.{places}f}  max {readings_for[-1]:.{places}f}  "
              f"bed floor {floors[metric]:.3e}")
    print()
    for span in SPANS:
        values = [r["T"] for r in rows
                  if r["span"] == span and r["tier"] == "webgpu" and r["state"] != "inactive"
                  and r["set"] != HOLDOUT and r["T"] is not None]
        if not values:
            continue
        bar_values = [bar_for(bars, floors, r, "shadowAffineSlopeDeltaMax") for r in rows
                      if r["span"] == span and r["tier"] == "webgpu" and r["state"] != "inactive"
                      and r["set"] != HOLDOUT and r["T"] is not None]
        print(f"  span {span:>3}: T median {upper_middle(values):.5f} over {len(values)} active "
              f"non-holdout WebGPU rows, against a median per-cell bar of "
              f"{upper_middle(bar_values):.6f} — {upper_middle(values) / upper_middle(bar_values):.0f}×")
    print()

    print("§7. The bed a clause would be read on: ACTIVE pose, WebGPU tier, non-holdout")
    print("-" * 160)
    print("  The shadow is the WebGPU tier's to fit — the CSS tier derives one `box-shadow` blur")
    print("  radius per surface from the same profile — so the clause is read there and the CSS")
    print("  tier is recorded beside it (the tier rule, Decision Log 23 of 2026-09-05). The")
    print("  inactive pose is a different document's difference and is reported, never pooled in.")
    print()
    print(f"  {'bed':<36}{'pose':<10}" + "".join(f"{('span ' + str(s)):>30}" for s in SPANS))
    for bed in bed_order(rows):
        for pose, keep in (("active", lambda r: r["state"] != "inactive"),
                           ("inactive", lambda r: r["state"] == "inactive")):
            line = f"  {bed:<36}{pose:<10}"
            printed = False
            for span in SPANS:
                values = [r["T"] for r in rows
                          if r["bed"] == bed and r["span"] == span and r["tier"] == "webgpu"
                          and r["set"] != HOLDOUT and r["T"] is not None and keep(r)]
                if values:
                    printed = True
                line += summarise(values, 30, 5)
            if printed:
                print(line)
    print()

    if args.against:
        print("§8. The lever: this generation against the superseded ones, named on the command line")
        print("-" * 160)
        print("  A cell's key carries the document's content hash, so a superseded generation's rows")
        print("  are joined to this one on (tier, profileKey, sceneId) rather than on the key. Each")
        print("  block below is one earlier generation, read from `results/superseded/` BY NAME —")
        print("  `index.json` there maps a document hash to the file holding its rows.")
        print()
        for spec in args.against:
            label, _, names = spec.partition("=")
            older: dict[tuple, dict] = {}
            for name in names.split(","):
                path = Path(name)
                if not path.is_absolute():
                    path = PACKAGE / name
                print(f"  {label}: reading {path.relative_to(PACKAGE)}")
                for row in readings(path, span_of, "any", args.with_holdout):
                    row["sigmaRelativeError"] = sigma_error(row)[2]
                    row["T"] = shape_error(row)["T"]
                    older[(row["tier"], row["profile"], row["scene"])] = row
            shared = [r for r in rows if (r["tier"], r["profile"], r["scene"]) in older]
            print(f"  {label}: {len(shared)} cells shared with this generation.")
            print()
            print(f"  {'span':>5}{'set':>14}{'tier':>9}{'n (i)':>7}{'(i) before':>12}{'(i) after':>11}"
                  f"{'n (ii)':>8}{'(ii) before':>13}{'(ii) after':>12}")
            for span in SPANS:
                for klass in ("cal+val", "probe", "holdout"):
                    for tier in ("webgpu", "css"):
                        before_i, after_i, before_t, after_t = [], [], [], []
                        for row in shared:
                            if (row["span"] != span or set_class(row) != klass
                                    or row["tier"] != tier or row["state"] == "inactive"):
                                continue
                            was = older[(row["tier"], row["profile"], row["scene"])]
                            if (was["sigmaRelativeError"] is not None
                                    and row["sigmaRelativeError"] is not None):
                                before_i.append(was["sigmaRelativeError"])
                                after_i.append(row["sigmaRelativeError"])
                            if was["T"] is not None and row["T"] is not None:
                                before_t.append(was["T"])
                                after_t.append(row["T"])
                        if not before_i and not before_t:
                            continue
                        line = f"  {span:>5}{klass:>14}{tier:>9}{len(before_i):>7}"
                        line += (f"{upper_middle(before_i):>12.4f}{upper_middle(after_i):>11.4f}"
                                 if before_i else f"{'—':>12}{'—':>11}")
                        line += f"{len(before_t):>8}"
                        line += (f"{upper_middle(before_t):>13.5f}{upper_middle(after_t):>12.5f}"
                                 if before_t else f"{'—':>13}{'—':>12}")
                        print(line)
            print()

    def direction_block(pose: str, keep) -> None:
        print(f"  pose {pose}")
        print(f"    {'bed':<38}{'span':>5}{'direction':>10}{'admitted':>24}"
              f"{'n':>5}{'T_dir':>11}{'min':>11}{'max':>11}   bands-used")
        for bed in bed_order(rows):
            for span in SPANS:
                for direction in DIRECTIONS:
                    picked = [r for r in rows
                              if r["bed"] == bed and r["span"] == span and r["tier"] == "webgpu"
                              and r["set"] != HOLDOUT and keep(r)
                              and r["Tdir"][direction] is not None
                              and full_set(r, direction)]
                    if not picked:
                        continue
                    values = [r["Tdir"][direction] for r in picked]
                    used = sorted({band_set_label(r["bandsUsedDir"][direction]) for r in picked})
                    print(f"    {bed:<38}{span:>5}{direction:>10}"
                          f"{band_set_label(picked[0]['admittedDir'][direction]):>24}"
                          f"{len(values):>5}{upper_middle(values):>11.5f}"
                          f"{min(values):>11.5f}{max(values):>11.5f}   {', '.join(used)}")
        print()

    print("§9. The direction-resolved cut: `T_dir` per bed, per span, per direction")
    print("-" * 160)
    print("  WebGPU tier, non-holdout, over the admitted bands, on the cells carrying the")
    print("  direction's whole admitted set. `below` is the direction `offsetPx` displaces the")
    print("  shadow into and `above` is the direction it displaces it out of: a SHIFT moves the")
    print("  two in opposite directions where a WIDENING moves them together, which is what makes")
    print("  the direction resolution the thing that identifies the offset (W32 Design).")
    print()
    direction_block("active", lambda r: r["state"] != "inactive")
    direction_block("inactive", lambda r: r["state"] == "inactive")

    print("§9b. The per-band `Δa` median per direction — the profile the summary is a mean of")
    print("-" * 160)
    print("  WebGPU tier, active, non-holdout. A band outside the span's clearance is printed as")
    print("  `(x)` around its figure rather than omitted, so the reading the frame ate is visible")
    print("  and is not in any statistic. `0-3` is the body's own edge and is never in `T`.")
    print()
    for bed in bed_order(rows):
        for span in SPANS:
            here = [r for r in rows if r["bed"] == bed and r["span"] == span
                    and r["tier"] == "webgpu" and r["set"] != HOLDOUT
                    and r["state"] != "inactive"]
            if not here:
                continue
            print(f"  {bed}, span {span} — {len(here)} cells, admitted "
                  f"{band_set_label(here[0]['admittedDir']['all'])}")
            print(f"    {'band':<8}" + "".join(f"{d:>16}" for d in DIRECTIONS))
            for field, label in (("deltaA", "Δa (web−nat)"), ("deltaC", "Δc (web−nat)")):
                for band in BANDS:
                    line = f"    {band:<8}"
                    printed = False
                    for direction in DIRECTIONS:
                        values = [r["perBand"][direction][band][field] for r in here
                                  if band in r["perBand"][direction]
                                  and r["perBand"][direction][band][field] is not None]
                        if not values:
                            line += f"{'—':>16}"
                            continue
                        printed = True
                        inside_clearance = band in here[0]["admittedDir"][direction]
                        figure = f"{upper_middle(values):.5f}"
                        line += (f"{figure:>16}" if inside_clearance
                                 else f"{'(' + figure + ')':>16}")
                    if printed:
                        print(line + f"   {label}")
            print()
    print()

    print("§10. The reach: per-direction extents and the two offsets, web − native, in CSS px")
    print("-" * 160)
    print("  An extent is ABSENT where the walk reached the canvas edge, which the axis withholds")
    print("  rather than reporting the size of the window. The absence is the reading: a span at")
    print("  which the web side carries no extent is a span at which the bed cannot see vitrea's")
    print("  own reach at all. WebGPU tier, active, non-holdout.")
    print()
    print(f"  {'span':>5}{'field':>10}{'n both':>8}{'nat absent':>12}{'web absent':>12}"
          f"{'native':>11}{'web':>11}{'web − native':>14}")
    for span in SPANS:
        here = [r for r in rows if r["span"] == span and r["tier"] == "webgpu"
                and r["set"] != HOLDOUT and r["state"] != "inactive"]
        if not here:
            continue
        for field in SHADOW_SIDES + ["offsetX", "offsetY"]:
            both = [r for r in here if r["reach"][field]["delta"] is not None]
            native_absent = sum(1 for r in here if r["reach"][field]["native"] is None)
            web_absent = sum(1 for r in here if r["reach"][field]["web"] is None)
            natives = [r["reach"][field]["native"] for r in here
                       if r["reach"][field]["native"] is not None]
            webs = [r["reach"][field]["web"] for r in here if r["reach"][field]["web"] is not None]
            line = (f"  {span:>5}{field:>10}{len(both):>8}"
                    f"{f'{native_absent}/{len(here)}':>12}{f'{web_absent}/{len(here)}':>12}")
            line += f"{upper_middle(natives):>11.2f}" if natives else f"{'—':>11}"
            line += f"{upper_middle(webs):>11.2f}" if webs else f"{'—':>11}"
            line += (f"{upper_middle([r['reach'][field]['delta'] for r in both]):>14.2f}"
                     if both else f"{'—':>14}")
            print(line)
        print()
    print()

    print("§11. The departure: the whole exterior, and the same quantity restricted to 3–48 CSS px")
    print("-" * 160)
    print("  `meanDeparture` is `mean(backdrop − rendered)` over every exterior pixel and is what")
    print("  B3 is stated over. The window-restricted figure is the same functional over the")
    print("  admitted bands only, recovered exactly from each band's `sampleCount`,")
    print("  `backdropMeanLinear` and `renderedLevelLinear` — a count-weighted mean of means is")
    print("  the mean of the union. W32 clause 3 solves the six anchors on the restricted one")
    print("  because `0-3` holds the body's own over-fill and is of the opposite sign; the")
    print("  difference between the two solves is what G1 measures at its first round.")
    print()
    for tier in ("webgpu", "css"):
        print(f"  tier {tier}, active, non-holdout")
        print(f"    {'bed':<38}{'span':>5}{'n':>4}{'whole nat':>11}{'whole web':>11}{'ratio':>8}"
              f"{'|Δ| whole':>11}{'win nat':>11}{'win web':>11}{'win ratio':>11}{'|Δ| window':>12}"
              f"{'nat 0':>9}   bands")
        for bed in bed_order(rows):
            for span in SPANS:
                here = [r for r in rows if r["bed"] == bed and r["span"] == span
                        and r["tier"] == tier and r["set"] != HOLDOUT
                        and r["state"] != "inactive"
                        and r["departure"]["window"]["native"] is not None]
                if not here:
                    continue
                whole_n = [r["departure"]["native"] for r in here]
                whole_w = [r["departure"]["web"] for r in here]
                ratios = [r["departure"]["ratio"] for r in here if r["departure"]["ratio"]]
                whole_d = [abs(r["departure"]["web"] - r["departure"]["native"]) for r in here]
                win_n = [r["departure"]["window"]["native"] for r in here]
                win_w = [r["departure"]["window"]["web"] for r in here]
                win_r = [r["departure"]["windowRatio"] for r in here
                         if r["departure"]["windowRatio"]]
                win_d = [abs(r["departure"]["window"]["difference"]) for r in here]
                bands = sorted({band_set_label(r["departure"]["window"]["bands"]) for r in here})
                zero_native = sum(1 for v in win_n if v == 0)
                print(f"    {bed:<38}{span:>5}{len(here):>4}{upper_middle(whole_n):>11.5f}"
                      f"{upper_middle(whole_w):>11.5f}"
                      f"{ratio_of(ratios):>8}"
                      f"{upper_middle(whole_d):>11.5f}"
                      f"{upper_middle(win_n):>11.6f}{upper_middle(win_w):>11.6f}"
                      f"{ratio_of(win_r):>11}"
                      f"{upper_middle(win_d):>12.5f}"
                      f"{(f'  {zero_native}/{len(here)}' if zero_native else ''):>9}"
                      f"   {', '.join(bands)}")
        print()
    print()

    print("§12. The inactive pose as its own population — never pooled with the active")
    print("-" * 160)
    print("  A receded document is a DIFFERENCE over its own scheme's active document, so an")
    print("  inactive row is a reading of a different material and an average across the two poses")
    print("  is an average of two materials. W32 clause 4 solves the receded documents' anchors")
    print("  here, on the fixtures the bed already holds.")
    print()
    span_table(rows, "  §12a. `T` over the admitted bands, inactive pose",
               lambda r: r["T"], 32, 5,
               lambda r: r["state"] == "inactive" and full_set(r))
    print("  §12b. The inactive departure, whole exterior and window-restricted")
    print(f"    {'bed':<38}{'span':>5}{'tier':>8}{'n':>4}{'whole nat':>11}{'whole web':>11}"
          f"{'ratio':>8}{'win nat':>11}{'win web':>11}{'win ratio':>11}{'nat 0':>10}")
    for bed in bed_order(rows):
        for span in SPANS:
            for tier in ("webgpu", "css"):
                here = [r for r in rows if r["bed"] == bed and r["span"] == span
                        and r["tier"] == tier and r["set"] != HOLDOUT
                        and r["state"] == "inactive"
                        and r["departure"]["window"]["native"] is not None]
                if not here:
                    continue
                ratios = [r["departure"]["ratio"] for r in here if r["departure"]["ratio"]]
                win_r = [r["departure"]["windowRatio"] for r in here
                         if r["departure"]["windowRatio"]]
                win_native = [r["departure"]["window"]["native"] for r in here]
                zero_native = sum(1 for v in win_native if v == 0)
                print(f"    {bed:<38}{span:>5}{tier:>8}{len(here):>4}"
                      f"{upper_middle([r['departure']['native'] for r in here]):>11.5f}"
                      f"{upper_middle([r['departure']['web'] for r in here]):>11.5f}"
                      f"{ratio_of(ratios):>8}"
                      f"{upper_middle(win_native):>11.6f}"
                      f"{upper_middle([r['departure']['window']['web'] for r in here]):>11.6f}"
                      f"{ratio_of(win_r):>11}"
                      f"{f'  {zero_native}/{len(here)}':>10}")
    print()

    print("  §12c. What the native side of the inactive pose actually carries")
    print("  " + "-" * 158)
    print("    `nat flat` counts the inactive rows whose NATIVE render equals its backdrop, to the")
    print("    axis's six written decimals, in EVERY admitted band — a receded window that removes")
    print("    no light at all from 3 CSS px outward. Where the affine pair is identified on those")
    print("    rows it reads `a` = 1.000000 and `c` = 0. `0-3 nat` is the native departure in the")
    print("    body's own edge band beside it — which is where the recede's whole exterior lives —")
    print("    and `σ nat` is how many of those rows resolve a native falloff σ at all (the axis")
    print("    withholds it below three qualifying rings). Read on the WebGPU tier; the native")
    print("    side is the same capture on both tiers.")
    print()
    print(f"    {'bed':<38}{'span':>5}{'n':>4}{'nat flat':>10}{'web flat':>10}"
          f"{'0-3 nat':>11}{'0-3 web':>11}{'σ nat':>8}{'σ web':>8}")
    for bed in bed_order(rows):
        for span in SPANS:
            here = [r for r in rows if r["bed"] == bed and r["span"] == span
                    and r["tier"] == "webgpu" and r["state"] == "inactive"
                    and r["set"] != HOLDOUT and r["bands"]]
            if not here:
                continue
            def flat(row: dict, side: str) -> bool:
                """Does every ADMITTED band on this side remove no light at all?

                Read on the LEVEL rather than on the slope, because the slope is
                absent wherever the band's backdrop is flat (the axis's own
                `flat-backdrop`) and a solid backdrop is exactly where a receded
                window's shadow would be easiest to see. `renderedLevelLinear ==
                backdropMeanLinear` at the axis's six written decimals is the
                band having removed nothing; where the pair IS identified on
                these rows it reads `a` = 1.000000 with `c` = 0.
                """
                entries = affine(row["shadow"], side, "all")
                got = [entries[b] for b in admitted_bands(row, "all") if b in entries]
                return bool(got) and all(
                    e["renderedLevelLinear"] == e["backdropMeanLinear"] for e in got)

            def edge(side: str) -> list[float]:
                out = []
                for row in here:
                    entry = affine(row["shadow"], side, "all").get("0-3")
                    if entry is not None:
                        out.append(entry["backdropMeanLinear"] - entry["renderedLevelLinear"])
                return out

            def count(predicate) -> str:
                return f"{sum(1 for r in here if predicate(r))}/{len(here)}"

            native_edge, web_edge = edge("Native"), edge("Web")
            print(f"    {bed:<38}{span:>5}{len(here):>4}"
                  f"{count(lambda r: flat(r, 'Native')):>10}"
                  f"{count(lambda r: flat(r, 'Web')):>10}"
                  f"{(upper_middle(native_edge) if native_edge else float('nan')):>11.5f}"
                  f"{(upper_middle(web_edge) if web_edge else float('nan')):>11.5f}"
                  f"{count(lambda r: r['sigmaNativeCss'] is not None):>8}"
                  f"{count(lambda r: r['sigmaWebCss'] is not None):>8}")
    print()

    suffix = "-with-holdout" if args.with_holdout else ""
    payload = {
        "source": str(matrix),
        "atDocuments": args.at_documents,
        "documents": documents,
        "withHoldout": args.with_holdout,
        "candidateI": {
            "quantity": "abs(falloffSigmaWeb - falloffSigmaNative) / falloffSigmaNative, "
                        "both sides divided by the row's scale (CSS px)",
            "exclusionRule": "sigma_css > span on EITHER side (W30 G0, claims §5.156 §2)",
        },
        "candidateII": {
            "quantity": "T = sum_b width_b * abs(slopeAWeb_b - slopeANative_b) / sum_b width_b "
                        "over the bands 3-6, 6-12, 12-24, 24-48 CSS px, direction `all`, "
                        "linear luminance",
            "beside": "L, the same weighted mean over abs(interceptCWeb - interceptCNative)",
            "excluded": "the 0-3 band (the body's own edge) and 0-6 (an overlap of the first two)",
        },
        "admittedBandRule": {
            "rule": "a shape band is admitted in a direction where its outer edge in CSS px is "
                    "<= that direction's clearance (device px) / scale; `all` takes the minimum "
                    "of the four sides",
            "pooling": "an order statistic is taken only over cells whose identified band set "
                       "equals their span's admitted set; the rest are counted apart",
            "source": "ShadowFieldReport.clearance* (src/metrics/shadow.ts), on every row",
        },
        "windowDeparture": {
            "quantity": "sample-count-weighted mean of (backdropMeanLinear - renderedLevelLinear) "
                        "over the admitted bands of direction `all`, per side",
            "beside": "meanDeparture{Native,Web}, the same functional over the whole exterior, "
                      "which is what B3 is stated over",
        },
        "statistic": "upper middle order statistic, sorted[n // 2]",
        "rows": [
            {k: v for k, v in row.items() if k not in ("shadow", "bands")}
            for row in rows
        ],
    }
    (out_dir / f"exterior-cut{suffix}.json").write_text(json.dumps(payload, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
