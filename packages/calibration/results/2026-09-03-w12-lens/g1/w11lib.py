"""W11 structure analysis helpers: load captures, synthesize plates, fit (level, transmission, blur sigma)."""
import numpy as np, json, os
from PIL import Image
from scipy.ndimage import gaussian_filter, uniform_filter

ROOT = '/Users/new/Developer/GitHub/designer'
FIX = ROOT + '/apps/reference-apple/fixtures'
PROBE = ROOT + '/packages/calibration/results/2026-09-02-w9-probe/apple-macos-26.5-1x-light-standard'
WEB = ROOT + '/packages/calibration/web-captures'
CANVAS = (320, 200)
COMP = {  # w, h, radius (pt); centred on the canvas
    'rrect-sm': (64, 32, 8), 'capsule-button': (120, 44, 22), 'rrect-md': (160, 96, 20),
    'rrect-ml': (224, 128, 27), 'rrect-lg': (280, 160, 34),
}
SPAN = {'rrect-sm': 32, 'capsule-button': 44, 'rrect-md': 96, 'rrect-ml': 128, 'rrect-lg': 160}
PITCH = {'checkerboard-4': 4, 'checkerboard-8': 8, 'checkerboard': 16, 'checkerboard-32': 32, 'checkerboard-64': 64}


def load_rgb(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float64) / 255.0


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(l):
    l = np.clip(l, 0, 1)
    return np.where(l <= 0.0031308, l * 12.92, 1.055 * l ** (1 / 2.4) - 0.055)


def luma_lin(rgb):
    l = srgb_to_lin(rgb)
    return 0.2126 * l[..., 0] + 0.7152 * l[..., 1] + 0.0722 * l[..., 2]


def luma_enc(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def native_path(profile, scene):
    return f'{FIX}/{profile}/{scene}.png'


def probe_path(scene):
    return f'{PROBE}/{scene}.png'


def web_path(profile, scene, renderer):
    return f'{WEB}/{profile}/{scene}/{scene}__{renderer}.png'


def plate_path(backdrop, scale):
    return f'{FIX}/backgrounds/{backdrop}@{scale}x.png'


def checker_plate(cell_pt, scale, a=0.0, b=1.0):
    """Bottom-left anchored checkerboard (AppKit flipped y). Returns linear luminance (a where even cells)."""
    W, H = CANVAS[0] * scale, CANVAS[1] * scale
    c = cell_pt * scale
    ys = np.arange(H); xs = np.arange(W)
    iy = np.floor((H - 1 - ys) / c).astype(int)
    ix = np.floor(xs / c).astype(int)
    par = (ix[None, :] + iy[:, None]) % 2
    return np.where(par == 0, a, b).astype(np.float64)


def interior_box(comp, scale, inset_pt=None):
    w, h, r = COMP[comp]
    m = r if inset_pt is None else max(r, inset_pt)
    cx, cy = CANVAS[0] / 2, CANVAS[1] / 2
    x0, x1 = int(round((cx - w / 2 + m) * scale)), int(round((cx + w / 2 - m) * scale))
    y0, y1 = int(round((cy - h / 2 + m) * scale)), int(round((cy + h / 2 - m) * scale))
    return x0, x1, y0, y1


def crop(img, box):
    x0, x1, y0, y1 = box
    return img[y0:y1, x0:x1]


def fit_blur(Y, plate, box, sigmas, kernel='gauss'):
    """Least squares Y ≈ a + t * K_sigma(plate) over the box, for each sigma; returns best (sigma, a, t, rms, r2) and the curve."""
    y = crop(Y, box).ravel()
    best = None; curve = []
    for s in sigmas:
        if kernel == 'gauss':
            B = gaussian_filter(plate, s, mode='nearest') if s > 0 else plate
        elif kernel == 'box':
            B = uniform_filter(plate, int(round(s)), mode='nearest') if s >= 2 else plate
        x = crop(B, box).ravel()
        X = np.stack([np.ones_like(x), x], 1)
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        res = y - X @ coef
        rms = float(np.sqrt(np.mean(res ** 2)))
        r2 = 1 - np.sum(res ** 2) / np.sum((y - y.mean()) ** 2)
        curve.append((s, coef[0], coef[1], rms, r2))
        if best is None or rms < best[3]:
            best = (s, float(coef[0]), float(coef[1]), rms, float(r2))
    return best, curve


def ssim_map(a_enc, b_enc, sigma=1.5, K1=0.01, K2=0.03, L=255.0):
    """Replica of packages/calibration/src/metrics/perceptual.ts: 11x11 Gaussian sigma 1.5, 'valid' windows, encoded luma in 0..255."""
    a = a_enc * 255.0; b = b_enc * 255.0
    C1 = (K1 * L) ** 2; C2 = (K2 * L) ** 2
    r = 5
    x = np.arange(-r, r + 1); g = np.exp(-x ** 2 / (2 * sigma ** 2)); g /= g.sum()

    def conv(im):
        from scipy.ndimage import convolve1d
        t = convolve1d(im, g, axis=0, mode='constant')
        t = convolve1d(t, g, axis=1, mode='constant')
        return t[r:-r, r:-r]
    mu_a = conv(a); mu_b = conv(b)
    saa = conv(a * a) - mu_a ** 2; sbb = conv(b * b) - mu_b ** 2; sab = conv(a * b) - mu_a * mu_b
    return ((2 * mu_a * mu_b + C1) * (2 * sab + C2)) / ((mu_a ** 2 + mu_b ** 2 + C1) * (saa + sbb + C2))


def ssim_mean(a_rgb, b_rgb):
    m = ssim_map(luma_enc(a_rgb), luma_enc(b_rgb))
    return float(m.mean()), float(m.min())
