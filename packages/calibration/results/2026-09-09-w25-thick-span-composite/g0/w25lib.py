"""W25 G0 — the shared reader library: geometry, masks, and the three width readers.

WHAT THIS READS. Reference fixtures `apps/reference-apple/fixtures/<profile>/<scene>.png` and the
probe grids under `packages/calibration/results/…/`; the canonical web captures
`packages/calibration/web-captures/<profile>/<scene>/<scene>__<tier>.png`; and the backdrop rasters
`apps/reference-apple/fixtures/backgrounds/<bg>@{1,2}x.png`. Nothing is written here.

UNITS. Every image is decoded sRGB → linear light and reduced to Rec.709 luma (dimensionless,
0..1), the same transfer W21's, W22's and W24's readers use. Geometry is declared in CSS px and
converted to DEVICE px by multiplying by the scale; every sigma this file returns is in DEVICE px
of the image it was read from, and the CSS-px value is always sigma/scale. Levels are linear luma;
an "8-bit code" is the difference expressed through the sRGB OETF at the level in question, so a
code is a display step, not a linear one.

THE THREE READERS, and what each needs from the backdrop.

  A. `psf_fit` — the dot's point-spread function. Needs an `impulse` backdrop (4 CSS px white
     squares, 64 CSS px apart). Fits the box convolved with a SUM OF TWO Gaussians plus an offset
     to the transmitted profile. W24 G1's `psf.py` bounded the pair at sharp sigma <= 4*scale and
     heavy sigma >= 4*scale, which is a ceiling this wave has to go past; the generalisation here
     keeps the bounds' PURPOSE (both amplitudes non-negative, the components ordered, so the fit
     cannot spend a large positive and a large negative Gaussian of the same width on any profile)
     while removing the numeric ceiling: the heavy component is parameterised as sharp + delta with
     delta >= 0, and the only ceiling left is `sharp_max_dev`, stated per call and reported.

  B. `edge_spread` — the edge-spread function on one resolvable backdrop step. A Python restatement
     of `packages/calibration/src/metrics/material.ts:102` `blurEdgeSpread` and `:216`
     `singleEdgeRegion`: locate the step in the BACKDROP (the known input), window it by its
     neighbours, fit `low + (high-low)*Phi((x-c)/sigma)` with the two plateaux solved in closed form,
     and report the residual RMS AS A FRACTION OF THE PROFILE'S OWN STEP HEIGHT — the committed
     definition, under which "large means sigma is not identifiable" (`src/report.ts:391-397`).
     The one change: `sigma_ceiling` is a parameter instead of `max(length/2, 4*guess)`.

  C. `sigma_match` — the whole-region sigma match. `read-stack.py:118-141`'s `blurSigmaMatchPx`
     with the grid extended past its 16.00 ceiling: the backdrop raster blurred at sigma, then
     affinely rescaled (one gain and one offset solved in closed form), scored against the region's
     own pixels. The statistic is about the SHAPE the material passed, not its level. Reported with
     its RMS and with a flag saying whether the minimum is interior to the grid.
"""

import json
import math
import os

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.optimize import least_squares
from scipy.special import erf

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "..", ".."))
FIXTURES = os.path.join(REPO, "apps", "reference-apple", "fixtures")
BACKGROUNDS = os.path.join(FIXTURES, "backgrounds")
# The canonical web captures are gitignored and live beside the canonical `results/matrix.json` in
# the MAIN checkout, not in a worktree (CLAUDE.md: "the canonical `web-captures/` beside it is
# gitignored — it lives on the capture machine"). So the root is the main checkout's, and it is
# read-only here: this wave's G0 writes nothing under it.
MAIN_CHECKOUT = os.environ.get("VITREA_MAIN_CHECKOUT", "/Users/new/Developer/GitHub/designer")
CAPTURES = os.environ.get(
    "VITREA_WEB_CAPTURES",
    os.path.join(MAIN_CHECKOUT, "packages", "calibration", "web-captures"),
)
SCENES = os.path.join(REPO, "apps", "reference-apple", "scenes.json")
CANVAS = {"width": 320.0, "height": 200.0}


# --------------------------------------------------------------------------- decode

def linearise(a):
    """sRGB EOTF, on 0..255 input."""
    a = np.asarray(a, dtype=np.float64) / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def encode(v):
    """The inverse: linear light -> 0..1 display signal (for expressing a delta in 8-bit codes)."""
    v = np.clip(np.asarray(v, dtype=np.float64), 0.0, 1.0)
    return np.where(v <= 0.0031308, v * 12.92, 1.055 * v ** (1 / 2.4) - 0.055)


def codes(a, b):
    """The difference a-b expressed in 8-bit display codes at that level."""
    return float((encode(a) - encode(b)) * 255.0)


def luma_of(path):
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    c = linearise(rgb)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


# --------------------------------------------------------------------------- geometry

def load_components(scenes_path=SCENES):
    return json.load(open(scenes_path))["components"]


def place(size, offset=(0.0, 0.0), canvas=CANVAS):
    """`packages/calibration/src/component-region.ts`'s rule, restated (see read-stack.py)."""
    w, h = float(size[0]), float(size[1])
    left = round((canvas["width"] - w) / 2) + float(offset[0])
    top = round((canvas["height"] - h) / 2) + float(offset[1])
    return {"left": left, "top": top, "width": w, "height": h}


def rrect_mask(box, radius, scale, shape, erode=0.0, kind="rrect"):
    """A rounded rect (or capsule) inset by `erode` CSS px, as a boolean mask in device px."""
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    x = (xx + 0.5) / scale - (box["left"] + box["width"] / 2.0)
    y = (yy + 0.5) / scale - (box["top"] + box["height"] / 2.0)
    hw = box["width"] / 2.0 - erode
    hh = box["height"] / 2.0 - erode
    r = max((box["height"] / 2.0 if kind == "capsule" else radius) - erode, 0.0)
    r = min(r, hw, hh)
    dx = np.maximum(np.abs(x) - (hw - r), 0.0)
    dy = np.maximum(np.abs(y) - (hh - r), 0.0)
    return (np.abs(x) <= hw) & (np.abs(y) <= hh) & (np.hypot(dx, dy) <= r + 1e-9)


def signed_distance(box, radius, scale, shape, kind="rrect"):
    """Signed distance to the shape's contour in CSS px; negative inside."""
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    x = (xx + 0.5) / scale - (box["left"] + box["width"] / 2.0)
    y = (yy + 0.5) / scale - (box["top"] + box["height"] / 2.0)
    hw, hh = box["width"] / 2.0, box["height"] / 2.0
    r = box["height"] / 2.0 if kind == "capsule" else radius
    r = min(r, hw, hh)
    qx = np.abs(x) - (hw - r)
    qy = np.abs(y) - (hh - r)
    outside = np.hypot(np.maximum(qx, 0.0), np.maximum(qy, 0.0))
    inside = np.minimum(np.maximum(qx, qy), 0.0)
    return outside + inside - r


class Cell:
    """One component's geometry on the canvas, with the masks the readers take.

    `spans` are quoted in CSS px; `short` is what `instances.ts:204` feeds the size law.
    """

    def __init__(self, name, components=None, canvas=CANVAS):
        comps = components or load_components()
        spec = comps[name]
        self.name = name
        self.kind = spec["kind"]
        self.canvas = canvas
        if self.kind == "stack":
            self.base = (place(spec["base"]["size"], spec["base"].get("offset", (0, 0)), canvas),
                         float(spec["base"].get("radius", 0)), spec["base"]["kind"])
            self.over = (place(spec["over"]["size"], spec["over"].get("offset", (0, 0)), canvas),
                         float(spec["over"].get("radius", 0)), spec["over"]["kind"])
            self.short = min(spec["base"]["size"])
            self.long = max(spec["base"]["size"])
            self.radius = float(spec["base"]["radius"])
        elif self.kind == "group":
            items = spec["items"]
            spacing = float(spec["spacing"])
            total = sum(i["size"][0] for i in items) + spacing * (len(items) - 1)
            height = max(i["size"][1] for i in items)
            left0 = round((canvas["width"] - total) / 2)
            top0 = round((canvas["height"] - height) / 2)
            self.members = []
            x = left0
            for it in items:
                w, h = float(it["size"][0]), float(it["size"][1])
                self.members.append(({"left": x, "top": top0 + (height - h) / 2.0,
                                      "width": w, "height": h},
                                     h / 2.0, it["kind"]))
                x += w + spacing
            self.short = min(items[0]["size"])
            self.long = max(items[0]["size"])
            self.radius = float(items[0]["size"][1]) / 2.0
        else:
            self.box = place(spec["size"], (0, 0), canvas)
            self.radius = float(spec.get("radius", 0.0))
            self.short = float(min(spec["size"]))
            self.long = float(max(spec["size"]))
        self.spec = spec

    def area(self):
        if self.kind == "stack":
            return self.base[0]["width"] * self.base[0]["height"]
        if self.kind == "group":
            return self.members[0][0]["width"] * self.members[0][0]["height"]
        return self.box["width"] * self.box["height"]

    def body_mask(self, scale, shape, erode=6.0):
        """The body the levels and the sigma-match are read over.

        For the stack this is the W22 geometry verbatim (`read-stack.py`): the base's box eroded
        `erode` CSS px with the OVERLAY's box DILATED by the same amount cut out of it. For the
        toolbar group it is the union of the three members eroded the same way.
        """
        if self.kind == "stack":
            b, br, bk = self.base
            o, orad, ok = self.over
            return (rrect_mask(b, br, scale, shape, erode, bk)
                    & ~rrect_mask(o, orad, scale, shape, -erode, ok))
        if self.kind == "group":
            m = np.zeros(shape, dtype=bool)
            for box, rad, kind in self.members:
                m |= rrect_mask(box, rad, scale, shape, erode, kind)
            return m
        return rrect_mask(self.box, self.radius, scale, shape, erode, self.kind)

    def sides(self):
        """The straight sides available to the along-side reader, per sub-box.

        Each entry is (label, box, radius, kind, side) where `side` is one of top/bottom/left/right.
        The along-side reader walks only the straight part of a side (outside the corner arcs).
        """
        out = []
        if self.kind == "stack":
            boxes = [("base", *self.base)]
        elif self.kind == "group":
            boxes = [(f"m{i}", *m) for i, m in enumerate(self.members)]
        else:
            boxes = [("", self.box, self.radius, self.kind)]
        for label, box, rad, kind in boxes:
            for side in ("top", "bottom", "left", "right"):
                out.append((label, box, rad, kind, side))
        return out


# --------------------------------------------------------------------------- reader A: the PSF

def profile_along(lum, cx, cy, axis, half_dev, band_dev):
    """W24 `read-impulse.py`'s profile, verbatim in behaviour: `band_dev` lines averaged."""
    h, w = lum.shape
    offs = np.arange(int(math.floor(-half_dev)), int(math.ceil(half_dev)) + 1)
    b = max(int(round(band_dev)), 1)
    b0 = -(b // 2)
    vals = []
    for o in offs:
        acc = []
        for k in range(b0, b0 + b):
            if axis == "x":
                xi, yi = int(round(cx - 0.5)) + int(o), int(round(cy - 0.5)) + k
            else:
                xi, yi = int(round(cx - 0.5)) + k, int(round(cy - 0.5)) + int(o)
            if 0 <= yi < h and 0 <= xi < w:
                acc.append(lum[yi, xi])
        vals.append(np.mean(acc) if acc else np.nan)
    return offs.astype(float), np.array(vals, dtype=float)


def box_gauss(x, w, sigma):
    s = max(abs(sigma), 1e-6)
    return 0.5 * (erf((x + w / 2) / (s * np.sqrt(2))) - erf((x - w / 2) / (s * np.sqrt(2))))


def psf_fit(offs, vals, box_dev, scale, sharp_min_dev=0.05, sharp_max_dev=None,
            body_from_dev=None):
    """Reader A. Fit box (x) (sharp + heavy Gaussian) + offset to one transmitted dot profile.

    `offs`/`vals` are a profile in DEVICE px around the dot's centre. `box_dev` is the dot's own
    width in device px (4 CSS px * scale). Returns sigmas in DEVICE px.

    THE BOUNDS, and why each is here (the generalisation of `psf.py`'s):
      - both amplitudes >= 0, so the fit cannot spend a large positive and a large negative
        Gaussian of the same width on the profile (the failure W24 G1 recorded and bounded away);
      - the heavy component is sharp + delta, delta >= 0, which ORDERS the pair instead of putting
        a numeric wall between them, so a sharp sigma above W24's 4*scale is representable;
      - the only ceiling left is `sharp_max_dev` (default: a quarter of the profile's half-window,
        the widest a dot 64 CSS px from its neighbour can carry) and it is REPORTED with the fit,
        so a value sitting on it is read as a bound and not as a measurement.
    """
    half = float(np.max(np.abs(offs)))
    if sharp_max_dev is None:
        sharp_max_dev = half
    body_from = body_from_dev if body_from_dev is not None else 0.8 * half
    body = float(np.nanmean(vals[np.abs(offs) >= body_from]))
    y = vals - body
    ok = np.isfinite(y)
    offs, y = offs[ok], y[ok]
    peak = float(np.nanmax(y)) if y.size else float("nan")

    def residual(q):
        a1, s1, a2, d, c = q
        return a1 * box_gauss(offs, box_dev, s1) + a2 * box_gauss(offs, box_dev, s1 + d) + c - y

    seed = [max(peak, 1e-5), min(2.0 * scale, sharp_max_dev), max(peak, 1e-5) * 0.05,
            6.0 * scale, 0.0]
    lo = [0.0, sharp_min_dev, 0.0, 0.0, -0.01]
    hi = [np.inf, sharp_max_dev, np.inf, 60.0 * scale, 0.01]
    seed = [min(max(s, l), h) for s, l, h in zip(seed, lo, hi)]
    r = least_squares(residual, seed, bounds=(lo, hi))
    a1, s1, a2, d, c = r.x
    rms = float(np.sqrt((r.fun ** 2).mean()))
    return {
        "body": body, "peak": peak,
        "sharpA": float(a1), "sharpSigmaDev": float(s1),
        "heavyA": float(a2), "heavySigmaDev": float(s1 + d),
        "heavyShare": float(a2 / max(a1 + a2, 1e-12)),
        "offset": float(c), "rms": rms,
        # The residual in the unit the other two readers report in: a fraction of the signal.
        "rmsRel": rms / peak if peak and np.isfinite(peak) and peak > 0 else float("inf"),
        "sharpCeilingDev": float(sharp_max_dev),
        "atCeiling": bool(s1 > sharp_max_dev * 0.999),
        "sigmaEquivDev": kernel_sigma_equiv(a1, s1, a2, s1 + d),
    }


def kernel_sigma_equiv(a1, s1, a2, s2, span_dev=400.0):
    """The fitted two-Gaussian kernel's single-Gaussian equivalent, by HALF-WIDTH AT HALF MAXIMUM.

    Readers B and C each fit ONE width, so comparing them with reader A needs one number from its
    pair. The amplitude-weighted RMS width is the obvious choice and is the wrong one: a heavy
    component at 1 % amplitude and sixty times the width dominates a variance average and reports a
    width nothing in the image has. The HWHM is what the eye and the other two readers see — the
    width of the kernel's core — so the pair is reduced to the sigma of the Gaussian with the same
    HWHM, sigma = w / sqrt(2 ln 2).
    """
    a1, a2 = max(float(a1), 0.0), max(float(a2), 0.0)
    s1, s2 = max(abs(float(s1)), 1e-6), max(abs(float(s2)), 1e-6)
    if a1 + a2 <= 0:
        return float("nan")

    def k(x):
        return a1 * np.exp(-0.5 * (x / s1) ** 2) + a2 * np.exp(-0.5 * (x / s2) ** 2)

    peak = k(0.0)
    xs = np.linspace(0.0, span_dev, 20001)
    v = k(xs)
    below = np.nonzero(v <= peak / 2.0)[0]
    if below.size == 0:
        return float("nan")
    j = below[0]
    if j == 0:
        return 0.0
    x0, x1 = xs[j - 1], xs[j]
    y0, y1 = v[j - 1], v[j]
    w = x0 + (y0 - peak / 2.0) / (y0 - y1) * (x1 - x0)
    return float(w / math.sqrt(2.0 * math.log(2.0)))


def find_dots(bg):
    """The impulse background's dot centres, in device px, by labelling its own lit pixels."""
    from scipy import ndimage
    lab, n = ndimage.label(bg > 0.5)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        out.append((xs.mean() + 0.5, ys.mean() + 0.5))
    out.sort(key=lambda p: (round(p[1]), round(p[0])))
    return out


HALF_LADDER = (30.0, 24.0, 20.0, 16.0, 14.0, 12.0)


def read_psf_cell(lum, bg, cell, scale, erode=6.0, half_css=30.0, sharp_max_dev=None,
                  min_half_css=12.0):
    """Reader A over every dot the eroded shape covers, both axes. Sigmas in DEVICE px.

    THE WINDOW IS CHOSEN PER DOT AND PER AXIS, and this is the part W24's `psf.py` left implicit.
    That reader took a fixed half-window of 20 CSS px and a body band at 14 CSS px and out, with no
    check that either stayed inside the surface — on `capsule-button`, whose eroded half-height is
    16 CSS px against a dot sitting 4 CSS px below the shape's centre, the vertical window leaves
    the surface and the "body" it subtracts is the backdrop. Here the widest half-window from
    `HALF_LADDER` whose whole band lies inside the eroded shape is used, the profile's body is
    taken from its outer fifth, and a dot with no window of at least `min_half_css` on an axis is
    skipped rather than read against the rim.

    The dots are 64 CSS px apart, so 30 CSS px is the widest window that never takes in a
    neighbour, and it is the ceiling of the ladder for that reason.
    """
    mask = cell.body_mask(scale, lum.shape, erode)
    rows = []
    for (dx, dy) in find_dots(bg):
        xi, yi = int(round(dx - 0.5)), int(round(dy - 0.5))
        if not (0 <= yi < mask.shape[0] and 0 <= xi < mask.shape[1] and mask[yi, xi]):
            continue
        for axis in ("x", "y"):
            chosen = None
            for half in HALF_LADDER:
                if half > half_css or half < min_half_css:
                    continue
                offs, vals = profile_along(lum, dx, dy, axis, half * scale, 1 * scale)
                inside = in_profile_mask(mask, dx, dy, axis, offs, 1 * scale)
                if inside.all() and np.isfinite(vals).all():
                    chosen = (half, offs, vals)
                    break
            if chosen is None:
                continue
            half, offs, vals = chosen
            f = psf_fit(offs, vals, 4.0 * scale, scale, sharp_max_dev=sharp_max_dev)
            f["pos"] = (dx / scale, dy / scale)
            f["axis"] = axis
            f["halfCss"] = half
            rows.append(f)
    return rows


def in_profile_mask(mask, cx, cy, axis, offs, band_dev):
    """Whether every sample of the profile band lies inside `mask` (W24 `read-impulse.py`'s rule)."""
    h, w = mask.shape
    b = max(int(round(band_dev)), 1)
    b0 = -(b // 2)
    ok = []
    for o in offs:
        good = True
        for k in range(b0, b0 + b):
            if axis == "x":
                xi, yi = int(round(cx - 0.5)) + int(o), int(round(cy - 0.5)) + k
            else:
                xi, yi = int(round(cx - 0.5)) + k, int(round(cy - 0.5)) + int(o)
            good = good and 0 <= yi < h and 0 <= xi < w and bool(mask[yi, xi])
        ok.append(good)
    return np.array(ok)


# --------------------------------------------------------------------------- reader B: the ESF

def normal_cdf(z):
    return 0.5 * (1.0 + erf(z / np.sqrt(2.0)))


def _linear_fit(model, target):
    mm = float(np.dot(model, model))
    m1 = float(model.sum())
    n = float(len(model))
    det = mm * n - m1 * m1
    if abs(det) < 1e-18:
        return None
    mt = float(np.dot(model, target))
    t1 = float(target.sum())
    slope = (mt * n - m1 * t1) / det
    offset = (mm * t1 - m1 * mt) / det
    return slope, offset


def _golden(f, a, b, iters=80):
    gr = (math.sqrt(5.0) - 1.0) / 2.0
    c, d = b - gr * (b - a), a + gr * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(iters):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = f(d)
    return (a + b) / 2.0


def edge_spread(esf, sigma_ceiling):
    """Reader B on one already-extracted profile. `esf` in linear luma, positions in device px.

    Returns sigma in DEVICE px and `residualRms` normalised by the profile's own step height —
    `material.ts:127-149`'s definition exactly, so the number is comparable with the matrix's
    `blurSigmaNative` / `blurFitResidual*` fields and with `report.ts:391-397`'s reading of them.
    """
    length = len(esf)
    tail = max(1, int(length * 0.1))
    step_height = abs(float(esf[-tail:].mean()) - float(esf[:tail].mean()))
    if step_height < 1e-4:
        return {"sigmaDev": float("nan"), "residual": float("inf"), "stepHeight": step_height,
                "length": length, "ceilingDev": sigma_ceiling, "atCeiling": False,
                "reason": "no step: the profile rises by less than 1e-4 end to end"}
    i = np.arange(length, dtype=float)
    deriv = np.zeros(length)
    deriv[1:-1] = (esf[2:] - esf[:-2]) / 2.0
    wsum = float(deriv.sum())
    centre_guess = float((deriv * i).sum() / wsum) if wsum != 0 else (length - 1) / 2.0
    second = float((deriv * (i - centre_guess) ** 2).sum())
    sigma_guess = math.sqrt(abs(second / wsum)) if wsum != 0 else length / 8.0

    def objective(centre, sigma):
        model = normal_cdf((i - centre) / max(sigma, 1e-6))
        fit = _linear_fit(model, esf)
        if fit is None:
            return float("inf")
        slope, offset = fit
        pred = offset + slope * model
        return float(np.sqrt(((pred - esf) ** 2).mean()) / step_height)

    centre = min(max(centre_guess, 0.0), length - 1.0)
    sigma = min(max(sigma_guess, 0.05), sigma_ceiling)
    for _ in range(3):
        s = sigma
        centre = _golden(lambda v: objective(v, s), 0.0, length - 1.0)
        c = centre
        sigma = _golden(lambda v: objective(c, v), 0.05, sigma_ceiling)
    return {"sigmaDev": float(sigma), "residual": objective(centre, sigma),
            "stepHeight": step_height, "length": length, "ceilingDev": sigma_ceiling,
            "atCeiling": bool(sigma > sigma_ceiling * 0.999), "centreDev": float(centre),
            "reason": ""}


def step_windows(bg, mask, axis, band_half=2, min_gap_dev=8):
    """Every single-step window the BACKDROP offers inside `mask`, `singleEdgeRegion`'s rule.

    Yields (start, end, band_centre): a window straddling exactly one backdrop transition, bounded
    by its neighbours, with the whole window and band inside `mask`. The edge is found in the
    backdrop — the known input — never in the rendered image.
    """
    h, w = bg.shape
    ys, xs = np.nonzero(mask)
    if ys.size == 0:
        return []
    if axis == "x":
        lo, hi = int(xs.min()), int(xs.max())
        rows = range(int(ys.min()) + band_half, int(ys.max()) - band_half + 1)
    else:
        lo, hi = int(ys.min()), int(ys.max())
        rows = range(int(xs.min()) + band_half, int(xs.max()) - band_half + 1)
    out = []
    for centre in rows:
        if axis == "x":
            sl = bg[centre - band_half:centre + band_half + 1, lo:hi + 1].mean(axis=0)
            inside = mask[centre, lo:hi + 1]
        else:
            sl = bg[lo:hi + 1, centre - band_half:centre + band_half + 1].mean(axis=1)
            inside = mask[lo:hi + 1, centre]
        if sl.size < 8:
            continue
        span = float(np.max(np.abs(sl - sl[0])))
        thr = max(0.05, span * 0.4)
        edges = [k for k in range(1, len(sl)) if abs(sl[k] - sl[k - 1]) >= thr]
        if not edges:
            continue
        for j, e in enumerate(edges):
            before = edges[j - 1] if j > 0 else 0
            after = edges[j + 1] - 1 if j + 1 < len(edges) else len(sl) - 1
            half = max(3, min(e - before, after - e))
            s, t = max(0, e - half), min(len(sl) - 1, e + half)
            if t - s < min_gap_dev:
                continue
            if not inside[s:t + 1].all():
                continue
            out.append((lo + s, lo + t, centre, half))
    return out


def read_edge_spread(lum, bg, mask, scale, sigma_ceiling_dev, axis="x", band_half=2,
                     min_gap_dev=8):
    """Reader B over every single-step window the backdrop offers under the shape.

    Returns the per-window rows and the median sigma / median residual. Reporting the MEDIAN over
    windows rather than the matrix's single centre window is the only other change from the
    committed metric: the checkerboard offers dozens of steps under a thick surface and one of them
    is a sample, not a measurement.
    """
    rows = []
    for (s, t, centre, half) in step_windows(bg, mask, axis, band_half, min_gap_dev):
        def cut(a, b):
            if axis == "x":
                return np.asarray(lum[centre - band_half:centre + band_half + 1,
                                      a:b + 1].mean(axis=0), dtype=float)
            return np.asarray(lum[a:b + 1,
                                  centre - band_half:centre + band_half + 1].mean(axis=1),
                              dtype=float)

        r = edge_spread(cut(s, t), sigma_ceiling_dev)
        # One re-window. The neighbours bound the window at half a backdrop cell, and on a step
        # much narrower than that the far ends of the window are already turning back towards the
        # NEXT step, which biases a single-erf fit low. Re-cutting to +/-(4 sigma + 2) once the
        # first fit has a width removes that bias where the width allows it, and changes nothing
        # where 4 sigma already exceeds the neighbour bound — which is the case this reader cannot
        # answer and reports as a residual.
        if np.isfinite(r["sigmaDev"]):
            want = int(math.ceil(4.0 * r["sigmaDev"] + 2.0))
            if want < half:
                mid = (s + t) // 2
                s2, t2 = max(s, mid - want), min(t, mid + want)
                if t2 - s2 >= min_gap_dev:
                    r2 = edge_spread(cut(s2, t2), sigma_ceiling_dev)
                    if np.isfinite(r2["sigmaDev"]):
                        r = r2
                        r["reWindowedDev"] = want
        r["halfWindowDev"] = half
        rows.append(r)
    good = [r for r in rows if np.isfinite(r["sigmaDev"])]
    if not good:
        return {"n": 0, "sigmaDev": float("nan"), "residual": float("inf"), "rows": rows}
    return {
        "n": len(good),
        "sigmaDev": float(np.median([r["sigmaDev"] for r in good])),
        "sigmaIqr": float(np.subtract(*np.percentile([r["sigmaDev"] for r in good], [75, 25]))),
        "residual": float(np.median([r["residual"] for r in good])),
        "atCeiling": float(np.mean([r["atCeiling"] for r in good])),
        "halfWindowDev": float(np.median([r["halfWindowDev"] for r in good])),
        "rows": rows,
    }


# --------------------------------------------------------------------------- reader C: the match

def default_grid(top=64.0):
    """`read-stack.py`'s grid with the ceiling raised: 0..4 by 0.1, 4..16 by 0.25, then 16..top."""
    return np.concatenate([np.arange(0.0, 4.0, 0.1), np.arange(4.0, 16.0, 0.25),
                           np.arange(16.0, top + 1e-9, 0.5)])


_BLUR_CACHE = {}
_BLUR_CACHE_KEY = [None]


def blurred_reference(reference, sigma, ref_key=None):
    """`reference` blurred at `sigma`, memoised per reference identity.

    Reader C sweeps ~145 sigmas, and on a given (backdrop, scale) every cell and every source —
    the reference fixture, the WebGPU capture, the CSS capture — is matched against the SAME
    blurred stack. Blurring it once per sigma instead of once per cell per source is the whole
    difference between a read that takes an hour and one that takes minutes; the cache holds one
    backdrop at a time, so it costs one image stack of memory and nothing else.
    """
    if ref_key is None:
        return reference if sigma == 0 else gaussian_filter(reference, sigma, mode="nearest")
    if _BLUR_CACHE_KEY[0] != ref_key:
        _BLUR_CACHE.clear()
        _BLUR_CACHE_KEY[0] = ref_key
    hit = _BLUR_CACHE.get(sigma)
    if hit is None:
        hit = reference if sigma == 0 else gaussian_filter(reference, sigma, mode="nearest")
        _BLUR_CACHE[sigma] = hit
    return hit


def sigma_match(target, reference, mask, sigmas=None, top=64.0, gain_max=5.0,
                sd_floor=3.0e-4, ref_key=None):
    """Reader C. `read-stack.py:118-141` with the grid a parameter and two identifiability guards.

    THE GUARDS, and why the reading is wrong without them. The closed-form gain is
    cov(ref, target)/var(ref), so once the blurred reference is nearly flat the denominator goes to
    zero, the gain runs away, and the affine rescaling can fit the target's own quantisation dither
    at an arbitrary sigma. Measured on the synthetic (see `validate.txt`): a 16 CSS px checkerboard
    at 1x under a true sigma of 8 device px is matched at 15.50 with a gain of 495, and under a
    true sigma of 16 at 0.00 with a gain of 0 — two confident numbers that mean nothing.

      - `gain_max` — a material attenuates the structure it passes; it does not amplify it. Any
        sigma whose closed-form gain leaves (0, gain_max] is refused, not scored.
      - `sd_floor` — a region whose own standard deviation is below one 8-bit code at the bottom of
        the range (3e-4 linear) has no structure to match a width against, and the answer is that
        the width is not identifiable from this cell, which is a reading in its own right.

    A run where every sigma is refused returns `sigmaDev` NaN with the reason stated, and a run
    whose minimum sits on the grid's last point returns `atCeiling` True — a lower bound.
    """
    if sigmas is None:
        sigmas = default_grid(top)
    t = target[mask]
    sd = float(np.std(t)) if t.size else 0.0
    if t.size == 0 or sd < sd_floor:
        return {"sigmaDev": float("nan"), "rms": float("nan"), "atCeiling": False,
                "sd": sd, "rmsRel": float("nan"), "gain": float("nan"), "curve": [],
                "reason": f"the region's sd {sd:.2e} is below one 8-bit code (3e-4 linear): "
                          f"there is no structure to match a width against"}
    best = (float("inf"), float("nan"), float("nan"), float("nan"))
    curve = []
    refused = 0
    for sigma in sigmas:
        blurred = blurred_reference(reference, sigma, ref_key)
        r = blurred[mask]
        var = float(np.var(r))
        if var <= 1e-12:
            refused += 1
            continue
        gain = float(np.cov(r, t, bias=True)[0, 1]) / var
        if not (0.0 < gain <= gain_max):
            refused += 1
            continue
        offset = float(np.mean(t) - gain * np.mean(r))
        rms = float(np.sqrt(np.mean((gain * r + offset - t) ** 2)))
        curve.append((float(sigma), rms))
        if rms < best[0]:
            best = (rms, float(sigma), gain, offset)
    rms, sigma, gain, offset = best
    if not np.isfinite(sigma):
        return {"sigmaDev": float("nan"), "rms": float("nan"), "atCeiling": False, "sd": sd,
                "rmsRel": float("nan"), "gain": float("nan"), "curve": [],
                "reason": f"every sigma on the grid was refused by the gain guard "
                          f"(0 < gain <= {gain_max:g}); the backdrop's structure does not survive "
                          f"this material at any width the grid carries"}
    return {"sigmaDev": sigma, "rms": rms, "gain": gain, "offset": offset,
            "atCeiling": bool(sigma >= float(sigmas[-1]) - 1e-9),
            "sd": sd, "refused": refused,
            # The residual in the unit readers A and B report in: a fraction of the region's own
            # structure. A match whose residual approaches the region's sd has explained nothing.
            "rmsRel": rms / max(sd, 1e-12),
            "curve": curve, "reason": ""}


# --------------------------------------------------------------------------- paths

def native_path(profile, scene, root=FIXTURES):
    return os.path.join(root, profile, f"{scene}.png")


def web_path(profile, scene, tier, root=CAPTURES):
    return os.path.join(root, profile, scene, f"{scene}__{tier}.png")


def bg_path(name, scale):
    p = os.path.join(BACKGROUNDS, f"{name}@{int(scale)}x.png")
    return p if os.path.exists(p) else os.path.join(BACKGROUNDS, f"{name}@1x.png")


def background_for(name, scale, shape):
    """The backdrop raster at the image's own scale, NEAREST-resampled if only 1x exists.

    W22's `read-stack.py` always loaded the 1x raster and NEAREST-resampled it at 2x; where a 2x
    raster is committed this uses it, which is the same image for the synthetic backgrounds and the
    correct one for `photo`.
    """
    p = bg_path(name, scale)
    img = Image.open(p).convert("RGB")
    if (img.height, img.width) != tuple(shape):
        img = img.resize((shape[1], shape[0]), Image.NEAREST)
    c = linearise(np.asarray(img, dtype=np.float64))
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


RESULTS = os.path.join(REPO, "packages", "calibration", "results")

# The two probe grids, read-only. Both are W9's declared grid (claims 5.30) — the same backgrounds,
# components, tints and scene ids — captured once under the LIGHT scheme (W9) and once under the
# DARK one (W21), by wave-local scripts through `VITREA_SCENES`, so the canonical bed was never
# touched. They are the only fixtures on disk that carry `rrect-sm`, `-md`, `-ml` and `-lg` over the
# SAME backdrop, which is what a span axis needs, and the only ones carrying a coarse checkerboard
# (32 and 64 CSS px cells) — the backdrop pitch reader B and reader C's bounds scale with.
# W9's fixture directory has no `backgrounds/` of its own; W21's does, and W21's scene file states
# that every background there is W9's verbatim, so the same rasters serve both.
PROBE_BG = os.path.join(RESULTS, "2026-09-06-w21-dark-scheme", "probe", "backgrounds")
PROBES = {
    "w9-1x-light": (os.path.join(RESULTS, "2026-09-02-w9-probe",
                                 "apple-macos-26.5-1x-light-standard"), 1.0, "light",
                    os.path.join(REPO, "apps", "reference-apple", "scenes-w9-probe.json")),
    "w21-1x-dark": (os.path.join(RESULTS, "2026-09-06-w21-dark-scheme", "probe",
                                 "apple-macos-26.5-1x-dark-standard"), 1.0, "dark",
                    os.path.join(REPO, "apps", "reference-apple", "scenes-w21-probe.json")),
}


def probe_background(name, scale, shape):
    """A probe grid's backdrop raster, at the reading's own scale (both grids are 1x)."""
    p = os.path.join(PROBE_BG, f"{name}@{int(scale)}x.png")
    if not os.path.exists(p):
        p = os.path.join(PROBE_BG, f"{name}@1x.png")
    img = Image.open(p).convert("RGB")
    if (img.height, img.width) != tuple(shape):
        img = img.resize((shape[1], shape[0]), Image.NEAREST)
    c = linearise(np.asarray(img, dtype=np.float64))
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def backdrop_pitch_css(name):
    """The backdrop's own step pitch in CSS px, which is what readers B and C's bounds scale with.

    `None` where the backdrop has no single pitch (`photo`, `impulse`) or none at all (the solids).
    """
    if name == "checkerboard":
        return 16.0
    if name.startswith("checkerboard-lc"):
        return 16.0
    if name.startswith("checkerboard-"):
        return float(name.rsplit("-", 1)[1])
    if name == "hc-text":
        return 14.0
    if name.startswith("hc-text-"):
        return float(name.rsplit("-", 1)[1])
    return None


PROFILES = {
    "1x-light": ("apple-macos-26.5-1x-light-standard", 1.0, "light"),
    "2x-light": ("apple-macos-26.5-2x-light-standard", 2.0, "light"),
    "1x-dark": ("apple-macos-26.5-1x-dark-standard", 1.0, "dark"),
    "2x-dark": ("apple-macos-26.5-2x-dark-standard", 2.0, "dark"),
    "1x-rt": ("apple-macos-26.5-1x-light-reduced-transparency", 1.0, "light"),
    "1x-ic": ("apple-macos-26.5-1x-light-increased-contrast", 1.0, "light"),
}
