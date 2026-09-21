#!/usr/bin/env python3
"""W31 G1 — the exterior-width instrument: two candidate statistics for the
shadow's exterior, computed over the current generation from committed fields
only.

    python3 exterior-instrument.py > exterior-instrument.txt
    python3 exterior-instrument.py --with-holdout \
      --against "0.19.0 (c9a §5.154)=results/superseded/f42ddec1cf5a.json,results/superseded/272d1b0c3e10.json" \
      --against "W30 G3 (c9a §5.159)=results/superseded/d731b3838994.json,results/superseded/ce1af58886ff.json" \
      > exterior-instrument-with-holdout.txt

**Nothing is fitted, adopted or captured here.** Every number is read off
`results/matrix.json` — the working file, by name — and off the superseded
generations named on the command line, both of which are committed evidence
(X2, X5 of the W30 charter; W31 acceptance clause 4). No profile document, no
material constant, no golden and no row moves.

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

DIRECTIONS = ["all", "above", "below", "left", "right"]

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

    def weighted(field: str) -> tuple[float | None, int]:
        usable = [b for b in SHAPE_BANDS if b in per_band and field in per_band[b]]
        if not usable:
            return None, 0
        total = sum(BAND_WIDTH_CSS_PX[b] for b in usable)
        return sum(BAND_WIDTH_CSS_PX[b] * abs(per_band[b][field]) for b in usable) / total, len(usable)

    T, bands_used = weighted("deltaSlopeA")
    L, _ = weighted("deltaInterceptC")
    support = value(row["shadow"], "backdropSupport")
    if support is not None and support < MIN_BACKDROP_SUPPORT:
        return {"bands": per_band, "T": None, "L": None, "bandsUsed": 0,
                "unsupported": support}
    return {"bands": per_band, "T": T, "L": L, "bandsUsed": bands_used,
            "unsupported": None}


def agreement_radius(row: dict, bar: float) -> int | None:
    """The innermost band edge from which every band outward is within `bar`."""
    shape = shape_error(row)["bands"]
    for index, band in enumerate(SHAPE_BANDS):
        tail = [b for b in SHAPE_BANDS[index:] if b in shape and "deltaSlopeA" in shape[b]]
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

    print("W31 G1 — the exterior-width instrument: two candidates over the current generation")
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
        shape = shape_error(row)
        row["T"], row["L"], row["bandsUsed"] = shape["T"], shape["L"], shape["bandsUsed"]
        row["backdropUnsupported"] = shape["unsupported"]
        row["bands"] = shape["bands"]

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
    print(f"  {'bed':<36}{'tier':<8}{'span':>5}{'n':>4}{'native σ':>11}{'law σ':>9}"
          f"{'law err':>10}{'B1':>6}{'rendered σ':>12}{'(i)':>9}{'σ_web − σ_nat':>15}")
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

    for bed in bed_order(with_sigma):
        for tier in ("webgpu", "css"):
            for span in B1_SPANS + [130]:
                picked = [r for r in with_sigma
                          if r["bed"] == bed and r["tier"] == tier and r["span"] == span
                          and r["state"] != "inactive"]
                if not picked:
                    continue
                native = upper_middle([r["sigmaNativeCss"] for r in picked])
                rendered = upper_middle([r["sigmaWebCss"] for r in picked])
                law = law_sigma(picked[0]["scheme"], span)
                law_error = (law - native) / native
                verdict = "PASS" if abs(law_error) <= B1_TOLERANCE else "FAIL"
                print(f"  {bed:<36}{tier:<8}{span:>5}{len(picked):>4}{native:>11.3f}{law:>9.3f}"
                      f"{law_error * 100:>9.2f}%{verdict:>6}{rendered:>12.3f}"
                      f"{upper_middle([r['sigmaRelativeError'] for r in picked]):>9.3f}"
                      f"{rendered - native:>15.3f}")
    print()
    signed = [r for r in with_sigma
              if r["span"] is not None and r["span"] >= 96 and r["state"] != "inactive"]
    wider = sum(1 for r in signed if r["sigmaWebCss"] > r["sigmaNativeCss"])
    print(f"  Sign, at the thick spans: the rendered σ is WIDER than the native on {wider} of "
          f"{len(signed)} rows that resolve both.")
    print()

    span_table(rows, "§3. Candidate (ii): `T`, the width-weighted transmission error over 3–48 CSS px",
               lambda r: r["T"], 32, 5, active)
    span_table(rows, "§3b. `L` beside it: the same weighted mean over the LIFT `c`, linear luminance",
               lambda r: r["L"], 32, 5, active)

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
        "statistic": "upper middle order statistic, sorted[n // 2]",
        "rows": [
            {k: v for k, v in row.items() if k not in ("shadow", "bands")}
            for row in rows
        ],
    }
    (out_dir / f"exterior-instrument{suffix}.json").write_text(json.dumps(payload, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
