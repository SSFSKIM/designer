"""W12 G1 (second half) helpers: geometry, the landed lens law, masked body fits, row profiles.

Everything in CSS px unless a name says device px; captures are read as linear luminance (Rec.709 of
sRGB-decoded channels), the same rule the runtime samples a backdrop with.
"""
import sys
sys.path.insert(0, '/Users/new/.claude/jobs/5c70e47f/tmp')
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
from w11lib import (ROOT, FIX, PROBE, WEB, CANVAS, COMP, SPAN, PITCH, load_rgb, luma_lin, luma_enc,
                    native_path, probe_path, web_path, plate_path, checker_plate)

PROF = {1: 'apple-macos-26.5-1x-light-standard', 2: 'apple-macos-26.5-2x-light-standard'}

# ---- the landed size law and lens (material.ts) -------------------------------------------------
THICKNESS = 8.0          # the surface's authored thickness (platform-web host default)
LENS_SIZE_GAIN_MAX = 2.6
LENS_REFRACTION_GAIN = 1.6
SIZE_SPAN_MIN, SIZE_SPAN_MAX = 32.0, 96.0


def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def size_thickness(span):
    return smoothstep(SIZE_SPAN_MIN, SIZE_SPAN_MAX, span)


def lens_depth(comp):
    """lensDepthPx = min(thickness × (1 + (gainMax − 1)·sizeThickness(span)), span/2), CSS px."""
    span = SPAN[comp]
    return min(THICKNESS * (1 + (LENS_SIZE_GAIN_MAX - 1) * size_thickness(span)), span / 2)


def lens_displacement(u, L, S=None):
    """D(u) = S · (1 − u/L)² for 0 ≤ u ≤ L, else 0; S defaults to L × lensRefractionGain."""
    if S is None:
        S = L * LENS_REFRACTION_GAIN
    depth = np.clip(u / L, 0, 1)
    return S * (1 - depth) ** 2


# ---- geometry ---------------------------------------------------------------------------------
def sdf_rrect(W, H, cx, cy, w, h, r):
    """Signed distance (negative inside) and outward unit normal, on pixel centres; device px."""
    ys, xs = np.mgrid[0:H, 0:W]
    px = np.abs(xs + 0.5 - cx) - (w / 2 - r)
    py = np.abs(ys + 0.5 - cy) - (h / 2 - r)
    d = np.sqrt(np.maximum(px, 0) ** 2 + np.maximum(py, 0) ** 2) + np.minimum(np.maximum(px, py), 0) - r
    gy, gx = np.gradient(d)
    nrm = np.sqrt(gx * gx + gy * gy) + 1e-9
    return d, gx / nrm, gy / nrm


def geometry(comp, scale):
    """(u in CSS px, nx, ny, xs, ys) for a centred component at the given scale."""
    W, H = CANVAS[0] * scale, CANVAS[1] * scale
    w, h, r = COMP[comp]
    d, nx, ny = sdf_rrect(W, H, 160 * scale, 100 * scale, w * scale, h * scale, r * scale)
    ys, xs = np.mgrid[0:H, 0:W]
    return -d / scale, nx, ny, xs, ys


def plate_luma(backdrop, scale):
    return luma_lin(load_rgb(plate_path(backdrop, scale)))


def capture(side, scene, scale, renderer='webgpu'):
    """Linear luminance of a native fixture ('native'), a vitrea capture ('webgpu'/'css'), or a probe cell ('probe')."""
    if side == 'native':
        return luma_lin(load_rgb(native_path(PROF[scale], scene)))
    if side == 'probe':
        assert scale == 1
        return luma_lin(load_rgb(probe_path(scene)))
    return luma_lin(load_rgb(web_path(PROF[scale], scene, side)))


# ---- the radial prediction ----------------------------------------------------------------------
def radial_prediction(P_blur, comp, scale, L, S, a, t, mask=None):
    """Y = a + t · B(q − D(u)·n̂) with B the blurred plate; returns the full canvas (zeros where u ≤ 0)."""
    u, nx, ny, xs, ys = geometry(comp, scale)
    inside = u > 0
    D = lens_displacement(u, L, S) * scale
    sx = xs - nx * D
    sy = ys - ny * D
    out = np.zeros_like(P_blur)
    m = inside if mask is None else (inside & mask)
    out[m] = a + t * map_coordinates(P_blur, [sy[m], sx[m]], order=1, mode='nearest')
    return out


# ---- masked fits ---------------------------------------------------------------------------------
def lstsq_at(y, x):
    X = np.stack([np.ones_like(x), x], 1)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    rms = float(np.sqrt(np.mean(res ** 2)))
    ss = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - float(np.sum(res ** 2)) / ss if ss > 0 else float('nan')
    return float(coef[0]), float(coef[1]), rms, r2


def fit_single(Y, P, mask, sigmas_css, scale):
    """Best single-Gaussian (σ CSS px, a, t, rms, r²) over the mask, and the whole curve."""
    y = Y[mask]
    best, curve = None, []
    for s in sigmas_css:
        B = gaussian_filter(P, s * scale, mode='nearest') if s > 0 else P
        a, t, rms, r2 = lstsq_at(y, B[mask])
        curve.append((s, a, t, rms, r2))
        if best is None or rms < best[3]:
            best = (s, a, t, rms, r2)
    return best, curve


def fit_two(Y, P, mask, scale, sb=1.25, sh=10.0, ks=np.linspace(0, 1, 41)):
    """vitrea's form (1 − k)·G_sb + k·G_sh, k free; returns (k, a, t, rms, r²)."""
    y = Y[mask]
    Gb = gaussian_filter(P, sb * scale, mode='nearest')
    Gh = gaussian_filter(P, sh * scale, mode='nearest')
    best = None
    for k in ks:
        a, t, rms, r2 = lstsq_at(y, ((1 - k) * Gb + k * Gh)[mask])
        if best is None or rms < best[3]:
            best = (float(k), a, t, rms, r2)
    return best


def interior_mask(comp, scale, inset=None):
    """Pixels deeper than `inset` (CSS px) inside the component; inset defaults to min(radius, h/4)."""
    w, h, r = COMP[comp]
    m = min(r, h / 4) if inset is None else inset
    u, *_ = geometry(comp, scale)
    return u > m


def to_png(arr_lin, path, zoom=1):
    """Linear luminance → sRGB 8-bit grey PNG, nearest-neighbour zoom."""
    from w11lib import lin_to_srgb
    im = Image.fromarray((lin_to_srgb(np.clip(arr_lin, 0, 1)) * 255 + 0.5).astype(np.uint8), 'L')
    if zoom != 1:
        im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    im.save(path)


def side_by_side(panels, path, zoom, gap=4):
    ims = [Image.fromarray(p, 'L' if p.ndim == 2 else 'RGB') for p in panels]
    ims = [im.resize((im.width * zoom, im.height * zoom), Image.NEAREST) for im in ims]
    W = sum(im.width for im in ims) + gap * (len(ims) - 1)
    H = max(im.height for im in ims)
    out = Image.new('RGB', (W, H), (255, 0, 255))
    x = 0
    for im in ims:
        out.paste(im.convert('RGB'), (x, 0))
        x += im.width + gap
    out.save(path)
