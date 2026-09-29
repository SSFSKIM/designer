"""W42 G0 rehearsal (charter clause 3): the shipped WebGPU body, the grounding law LT, and the
tone curves the rehearsal composes it with, as float64 forward models on the canonical canvas.

Nothing here reads a native pixel. Inputs are the committed backdrops, `scenes.json`'s geometry
and `resolved.json` (this directory's `resolve.ts`, every number the worktree's material code).

THE SHIPPED BODY (`Shipped`) is grounding memo B's float64 replica
(`~/vitrea-w42/grounding/kernel/code-map/{kernel_sim,tone_ed,verify}.py`, hashed in
`2026-09-29-w42-grounding/scratch-sha256.txt`), which reproduced 11 web cores at rms 0.27-0.38
codes. Three things changed, none of them in its arithmetic:
  - the pyramid is applied level by level (L_n = 0.5 (A_y L A_x' + B_y L B_x')), which is the
    same linear operator memo B composed as 2^n separable terms, at a cost one cell can afford;
  - the body and chain are SAMPLED at the refracted position the optics pass samples them at
    (`wgsl/optics.ts` "The lens (W12 G2)": the displacement D(u) along the field normal
    blended toward the inscribed oval), so the model is a model of the whole body and not of
    its lens-free core only;
  - every shape of the canonical non-holdout bed (rrect-lg and the toolbar's three capsules
    as three surfaces) and every endpoint's own tone abscissa (source when active, the
    surface's silhouette when receded).
It does NOT model the rim, the specular highlight, the inner shadow, the author tint or the
outer shadow. The swap (`swap.py`) never needs them: it adds the DIFFERENCE between two bodies
to the shipped capture, so everything the capture carries beyond the body is kept.

LT (`lt_argument`) is grounding memo E's literal-tree family (`~/vitrea-w42/grounding/refit/
lt.py`, the charter's reference forward model), evaluated over the whole canvas and on all
three channels instead of on memo C's luma deep masks: the capture S on the shape's box plus
the declared margin with memo C's 0.8-device-px floor before the knee (1.6 on rrect-lg), the
narrow term G(kappa 5 o(d)) S by the 'var' reading (the declared opacity scales the radius,
interpolated over five blur levels as memo E did), the wide term G(kappa 8) S, clamp-to-edge
when active and normalised when receded, the knee on encoded luma at lambda and the Normal
fill at w = 0.5. Its luma is M; its chroma is W's, because memo A reads the body's chroma as
taking the heavy argument only. A(x) = M_L(x) + (W(x) - L(W(x))).

THE TONES:
  - `landed_T(ep, comp, scale, A)`: candidate 1 in the three endpoints whose landed T is the
    shipped solve, "the shipped tone solve's uniform response, evaluated at M per pixel rather
    than at the group argument" (charter, T): each pixel is toned as the shipped material tones
    a uniform backdrop of colour A(x), abscissa included; a constant backdrop therefore reads
    exactly the shipped body.
  - `e3_extended(A, W)`: candidate 1 in light receded, E3's F on encoded luma (W41's seven
    ordinates on 40-150, the shader's own continuation below 40) extended above 150 by the
    light-inactive native uniform readings memo C tabled (160 -> 202, 242.4 -> 235.3,
    255 -> 240) STANDING IN for family A's ordinates, which do not exist until G1; chroma is
    g(L(W)) v(W) as the charter writes it.
  - `native_T(ep, span, L)`: candidate 2's T, memo C's native uniform table with its span
    corrections (`~/vitrea-w42/grounding/probe/reader.py`), the same table memo E inverted.
    It is luma only; candidate 2 keeps candidate 1's chroma and replaces its luma.
"""
from __future__ import annotations

import functools
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
FIX = ROOT / 'apps/reference-apple/fixtures'
SPEC = json.loads((ROOT / 'apps/reference-apple/scenes.json').read_text())
RES = json.loads((HERE / 'resolved.json').read_text())['endpoints']
W709 = np.array([0.2126, 0.7152, 0.0722])
CANVAS = (320, 200)


def dec(c):
    c = np.clip(np.asarray(c, dtype=np.float64), 0, 1)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def enc(c):
    c = np.clip(np.asarray(c, dtype=np.float64), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, dtype=np.float64) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def endpoint_of(scheme: str, pose: str) -> str:
    return f"{scheme}-{'receded' if pose == 'inactive' else 'active'}"


def pose_of(scene: str) -> str:
    return 'inactive' if scene.split('__')[2].startswith('inactive') else 'rest'


@functools.lru_cache(maxsize=None)
def backdrop(bg: str, scale: int) -> np.ndarray:
    """Encoded sRGB in [0, 1], (H, W, 3)."""
    with Image.open(FIX / 'backgrounds' / f'{bg}@{scale}x.png') as im:
        return np.asarray(im.convert('RGB'), dtype=np.float64) / 255.0


# ---------------------------------------------------------------- geometry

def surfaces(component: str):
    """The scene's surfaces in CSS px: (resolved key, cx, cy, w, h, r). Groups are their items."""
    c = SPEC['components'][component]
    cx, cy = CANVAS[0] / 2, CANVAS[1] / 2
    if c['kind'] == 'capsule':
        w, h = c['size']
        return [('capsule', cx, cy, w, h, min(w, h) / 2)]
    if c['kind'] == 'rrect':
        w, h = c['size']
        off = c.get('offset', [0, 0])
        return [(component, cx + off[0], cy + off[1], w, h, c['radius'])]
    if c['kind'] == 'group':
        items, sp = c['items'], c['spacing']
        total = sum(i['size'][0] for i in items) + sp * (len(items) - 1)
        x0, out = cx - total / 2, []
        for i in items:
            w, h = i['size']
            out.append(('toolbar-member', x0 + w / 2, cy, w, h, min(w, h) / 2))
            x0 += w + sp
        return out
    raise ValueError(f'{component}: kind {c["kind"]} is not rehearsed')


def rrect_sdf(xs, ys, cx, cy, w, h, r):
    qx = np.abs(xs - cx) - (w / 2 - r)
    qy = np.abs(ys - cy) - (h / 2 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


class Field:
    """Per device pixel: the SDF (CSS px, negative inside), the owning surface, its normal,
    and the position relative to that surface's centre (the lens's oval)."""

    def __init__(self, component: str, scale: int):
        W, H = CANVAS[0] * scale, CANVAS[1] * scale
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
        px, py = (xs + 0.5) / scale, (ys + 0.5) / scale
        self.surfaces = surfaces(component)
        ds = np.stack([rrect_sdf(px, py, cx, cy, w, h, r) for _, cx, cy, w, h, r in self.surfaces])
        self.owner = np.argmin(ds, axis=0)
        self.d = np.take_along_axis(ds, self.owner[None], 0)[0]
        eps = 1e-3
        gx = np.stack([rrect_sdf(px + eps, py, *s[1:]) - rrect_sdf(px - eps, py, *s[1:])
                       for s in self.surfaces]) / (2 * eps)
        gy = np.stack([rrect_sdf(px, py + eps, *s[1:]) - rrect_sdf(px, py - eps, *s[1:])
                       for s in self.surfaces]) / (2 * eps)
        gx = np.take_along_axis(gx, self.owner[None], 0)[0]
        gy = np.take_along_axis(gy, self.owner[None], 0)[0]
        n = np.maximum(np.hypot(gx, gy), 1e-9)
        self.nx, self.ny = gx / n, gy / n
        cxs = np.array([s[1] for s in self.surfaces])[self.owner]
        cys = np.array([s[2] for s in self.surfaces])[self.owner]
        self.relx, self.rely = px - cxs, py - cys
        self.halfw = np.array([s[3] / 2 for s in self.surfaces])[self.owner]
        self.halfh = np.array([s[4] / 2 for s in self.surfaces])[self.owner]
        self.span = np.array([min(s[3], s[4]) for s in self.surfaces])[self.owner]
        self.scale, self.W, self.H = scale, W, H
        # Pixel coverage of the contour, the swap's weight (a one-device-pixel ramp).
        self.cov = np.clip(-self.d * scale + 0.5, 0.0, 1.0)

    def displacement(self, ep: str) -> tuple[np.ndarray, np.ndarray]:
        """The optics pass's refraction offset in CSS px (thickness 8, refraction 'true')."""
        L = RES[ep]['lensLaw']
        fold = RES[ep]['fold']
        thick = 8.0
        span = self.span
        thick_scale = thick / L['thicknessReference']
        height = np.minimum(L['heightPerSpan'] * span, L['heightMax'])
        amount = np.minimum(L['amountPerSpan'] * span, L['amountMax'])
        unclamped = thick + (height * thick_scale - thick) * fold
        depth = np.clip(unclamped, 0, span * 0.5)
        ratio = np.where(unclamped > 1e-6, depth / np.maximum(unclamped, 1e-9), 0.0)
        magnitude = L['refractionGain'] * (thick + (amount * thick_scale - thick) * fold) * ratio
        extent = np.maximum(L['extentGain'] * depth, 1e-4)
        lens_t = np.maximum(1 - np.maximum(-self.d, 0) / extent, 0)
        disp = magnitude * lens_t ** L['profileExponent'] * 1.0
        oval_t = np.clip((span - L['ovalizationSpanMin']) /
                         max(L['ovalizationSpanMax'] - L['ovalizationSpanMin'], 1e-6), 0, 1)
        omega = L['ovalization'] * oval_t * oval_t * (3 - 2 * oval_t)
        hw, hh = np.maximum(self.halfw, 1e-4), np.maximum(self.halfh, 1e-4)
        unit = np.maximum(np.hypot(self.relx / hw, self.rely / hh), 1e-6)
        ogx = self.relx / (hw * hw) * (np.minimum(hw, hh) / unit)
        ogy = self.rely / (hh * hh) * (np.minimum(hw, hh) / unit)
        bx = (1 - omega) * self.nx + omega * ogx
        by = (1 - omega) * self.ny + omega * ogy
        bl = np.hypot(bx, by)
        dx = np.where(bl > 1e-6, bx / np.maximum(bl, 1e-12), self.nx)
        dy = np.where(bl > 1e-6, by / np.maximum(bl, 1e-12), self.ny)
        inside = self.d < 0
        return np.where(inside, -dx * disp, 0.0), np.where(inside, -dy * disp, 0.0)


@functools.lru_cache(maxsize=None)
def field(component: str, scale: int) -> Field:
    return Field(component, scale)


# ---------------------------------------------------------------- the WebGPU chain

def _bilinear_row(u, n):
    w = np.zeros(n)
    t = u * n - 0.5
    i0 = math.floor(t)
    f = t - i0
    w[min(max(i0, 0), n - 1)] += 1 - f
    w[min(max(i0 + 1, 0), n - 1)] += f
    return w


def _down(ns, nd, offsets, weights):
    M = np.zeros((nd, ns))
    for j in range(nd):
        uv = (j + 0.5) / nd
        for o, wt in zip(offsets, weights):
            M[j] += wt * _bilinear_row(uv + o / ns, ns)
    return M


def _blur9(n, sigma):
    M = np.zeros((n, n))
    ts = np.arange(-4, 5)
    w = np.exp(-(ts ** 2) / (2 * max(sigma, 1e-4) ** 2))
    w /= w.sum()
    for j in range(n):
        for t, wt in zip(ts, w):
            M[j, min(max(j + t, 0), n - 1)] += wt
    return M


@functools.lru_cache(maxsize=None)
def _chain_ops(W, H):
    levels = [(W, H)]
    while len(levels) < 12:
        w, h = levels[-1]
        nw, nh = max(1, w >> 1), max(1, h >> 1)
        if min(nw, nh) < 8:
            break
        levels.append((nw, nh))
    ops = []
    for n in range(1, len(levels)):
        (ws, hs), (wd, hd) = levels[n - 1], levels[n]
        ops.append((_down(ws, wd, (-2, 0, 2), (0.25, 0.5, 0.25)), _down(hs, hd, (-2, 0, 2), (0.25, 0.5, 0.25)),
                    _down(ws, wd, (-1, 1), (0.5, 0.5)), _down(hs, hd, (-1, 1), (0.5, 0.5))))
    return levels, ops


def _sep(My, L, Mx):
    """My @ L[..., c] @ Mx.T for every channel, as two matrix products."""
    return np.einsum('lk,ikc->ilc', Mx, np.einsum('ij,jkc->ikc', My, L, optimize=True), optimize=True)


@functools.lru_cache(maxsize=8)
def chain(bg: str, scale: int):
    """Every chain level of the LINEAR backdrop, (h, w, 3) each (fs_downsample, rgba16float)."""
    lin = dec(backdrop(bg, scale))
    H, W, _ = lin.shape
    levels, ops = _chain_ops(W, H)
    out = [lin]
    for Ax, Ay, Bx, By in ops:
        L = out[-1]
        out.append(0.5 * (_sep(Ay, L, Ax) + _sep(By, L, Bx)))
    return out


def blurred_level(bg, scale, level, sigma):
    L = chain(bg, scale)[level]
    if sigma is None:
        return L
    hl, wl, _ = L.shape
    return _sep(_blur9(hl, sigma), L, _blur9(wl, sigma))


def sample(tex, u, v):
    """Bilinear, clamp-to-edge, at normalised (u, v): the sampler every body tap uses."""
    hl, wl, _ = tex.shape
    coords = [v * hl - 0.5, u * wl - 0.5]
    return np.stack([ndimage.map_coordinates(tex[..., c], coords, order=1, mode='nearest')
                     for c in range(3)], -1)


def sample_image(img, fx, fy, scale):
    """Bilinear sample of a device-px image at CSS offsets (fx, fy) from each pixel centre."""
    H, W = img.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
    coords = [ys + fy * scale, xs + fx * scale]
    if img.ndim == 2:
        return ndimage.map_coordinates(img, coords, order=1, mode='nearest')
    return np.stack([ndimage.map_coordinates(img[..., c], coords, order=1, mode='nearest')
                     for c in range(img.shape[2])], -1)


# ---------------------------------------------------------------- statistics the solve reads

def source_stat(img):
    e = img.reshape(-1, 3).mean(axis=0)
    lin = dec(img.reshape(-1, 3)).mean(axis=0)
    return dict(level=float(dec(e) @ W709), linLum=float(lin @ W709))


def silhouette_stat(img, scale, surface):
    _, cx, cy, w, h, r = surface
    H, W, _ = img.shape
    ys, xs = np.mgrid[0:H, 0:W]
    m = rrect_sdf(xs + 0.5, ys + 0.5, cx * scale, cy * scale, w * scale, h * scale, r * scale) <= 0
    encl = (img[m] @ W709).mean()
    lin = dec(img[m]).mean(axis=0)
    return dict(level=float(dec(encl)), linLum=float(lin @ W709))


@functools.lru_cache(maxsize=None)
def edge_density(bg, scale):
    """The analysis pass's edge density (memo B's tone_ed.edge_density, vectorised)."""
    lum = dec(backdrop(bg, scale)) @ W709
    H, W = lum.shape
    levels, ops = _chain_ops(W, H)
    L = lum
    for Ax, Ay, Bx, By in ops[:1 if scale == 1 else 2]:
        L = 0.5 * (Ay @ L @ Ax.T + By @ L @ Bx.T)
    hl, wl = L.shape
    g = np.arange(64) / 63.0
    rows = lambda vs: np.stack([_bilinear_row(v, hl) for v in vs])
    cols = lambda us: np.stack([_bilinear_row(u, wl) for u in us])
    s = lambda us, vs: rows(vs) @ L @ cols(us).T  # s[v, u]
    dx = s(g + 1 / wl, g) - s(g - 1 / wl, g)
    dy = s(g, g + 1 / hl) - s(g, g - 1 / hl)
    return float((np.hypot(dx, dy) * 0.5).sum() / 4096)


# ---------------------------------------------------------------- the tone solve, vectorised

def _tone_response(x, sizeK, e):
    f = sizeK * sizeK * (3 - 2 * sizeK)
    ys = [a + (b - a) * f for a, b in zip(e['thin'], e['thick'])]
    xs = e['anchorX']
    xc = np.clip(x, xs[0], xs[3])
    h = [max(xs[i + 1] - xs[i], 1e-4) for i in range(3)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(3)]
    m1 = 2 * d[0] * d[1] / (d[0] + d[1]) if d[0] * d[1] > 0 else 0.0
    m2 = 2 * d[1] * d[2] / (d[1] + d[2]) if d[1] * d[2] > 0 else 0.0
    seg = np.where(xc > xs[2], 2, np.where(xc > xs[1], 1, 0))
    s0 = np.choose(seg, [d[0], m1, m2])
    s1 = np.choose(seg, [m1, m2, d[2]])
    hh = np.choose(seg, h)
    x0 = np.choose(seg, xs[:3])
    y0 = np.choose(seg, ys[:3])
    y1 = np.choose(seg, ys[1:])
    t = (xc - x0) / hh
    return (y0 * (1 + 2 * t) * (1 - t) ** 2 + s0 * hh * t * (1 - t) ** 2
            + y1 * t * t * (3 - 2 * t) + s1 * hh * t * t * (t - 1))


def solve(e, sizeK, level, lin):
    """optics.ts's tone adapt, W9 solve and W36 black branch, over arrays (memo B's `solve`)."""
    level = np.asarray(level, dtype=np.float64)
    lin = np.asarray(lin, dtype=np.float64)
    tintA, occ = e['tintAlpha'], e['sizeOcclusionGain']
    neutral = e['tint'][0]
    sized = tintA + occ * sizeK * (1 - tintA)
    strength = e['backdropToneMax']
    high = max(e['backdropToneHigh'], e['backdropToneLow'] + 1e-4)
    toneX = level + e['backdropToneSizeBias'] * sizeK
    tt = np.clip((toneX - e['backdropToneLow']) / max(high - e['backdropToneLow'], 1e-6), 0, 1)
    toneAdapt = strength * (1 - tt * tt * (3 - 2 * tt))
    solvedN = np.full_like(level, neutral)
    solvedA = np.full_like(level, sized)
    rs = min(max(e['responseStrength'], 0), 1)
    active = (strength > 0) & (e['responseStrength'] > 0) & (sized > 1e-3) & (toneAdapt < 0.995)
    x = enc(level)
    anchor = max(e['anchorX'][0], 1e-4)
    authority = smoothstep(anchor * 0.5, anchor, x) * rs
    bw = np.zeros_like(level)
    if e['black'][0] > 0:
        bw = np.where(x < 0.003, min(max(e['black'][0], 0), 1) * (1 - smoothstep(0.0, 0.003, x)), 0.0)
        authority = authority + (rs - authority) * bw
    R = _tone_response(x, sizeK, e)
    f = sizeK * sizeK * (3 - 2 * sizeK)
    R = R + ((e['black'][1] + (e['black'][2] - e['black'][1]) * f) - R) * bw
    run = active & (authority > 0)
    pre = (R - toneAdapt * lin) / np.maximum(1 - toneAdapt, 1e-9)
    nominal = (1 - sized) * lin + sized * neutral
    shift = (pre - nominal) / sized * authority * strength
    N = np.where(run, np.clip(neutral + shift, 0, 1), solvedN)
    achieved = (1 - sized) * lin + sized * N
    raise_ = run & (pre > achieved + 1e-4) & (N > lin + 1e-3)
    target = np.clip((pre - lin) / np.where(np.abs(N - lin) > 1e-12, N - lin, 1e-12), sized, 1)
    A = np.where(raise_, sized + (target - sized) * authority * strength, solvedA)
    return dict(a=A + toneAdapt * (1 - A), N=N, toneAdapt=toneAdapt, solvedA=A)


def compose(e, bt, s, tone_target):
    """colour = mix(backdrop, adapted, a), chroma retention, gamut at held luma (optics.ts)."""
    tA = np.asarray(s['toneAdapt'])[..., None]
    a = np.asarray(s['a'])[..., None]
    sa = np.asarray(s['solvedA'])[..., None]
    N = np.asarray(s['N'])[..., None]
    adapted = np.where((tA > 0) & (a > 0),
                       (N * ((1 - tA) * sa) + tone_target * tA) / np.maximum(a, 1e-12), N)
    col = (1 - a) * bt + a * adapted
    ret = e['bodyChromaRetention']
    if ret <= 0:
        return col
    Y = col @ W709
    Yb = bt @ W709
    ok = (Y > 1e-6) & (Y <= 1.0) & (Yb > 1e-6)
    toward = bt * (Y / np.maximum(Yb, 1e-9))[..., None]
    rest = col + (toward - col) * ret
    Yr = rest @ W709
    rest = rest * (Y / np.maximum(Yr, 1e-9))[..., None]
    d = rest - Y[..., None]
    t = np.ones_like(Y)
    for i in range(3):
        di = d[..., i]
        t = np.where(di > 1e-7, np.minimum(t, (1 - Y) / np.where(di > 1e-7, di, 1)), t)
        t = np.where(di < -1e-7, np.minimum(t, -Y / np.where(di < -1e-7, di, -1)), t)
    rest = Y[..., None] + (rest - Y[..., None]) * np.clip(t, 0, 1)[..., None]
    return np.where(ok[..., None], rest, col)


# ---------------------------------------------------------------- the shipped body

def shipped_argument(ep, scale, bg, component, lensed=True):
    """bt: the per-pixel blurred backdrop the optics pass composites (LINEAR), at the refracted
    position when `lensed`, plus the per-pixel scatter share it was mixed at."""
    e = RES[ep]
    sc = e['perScale'][f'{scale}x']
    fl = field(component, scale)
    W, H = fl.W, fl.H
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
    fx, fy = fl.displacement(ep) if lensed else (np.zeros((H, W)), np.zeros((H, W)))
    u = (xs + 0.5) / W + fx / CANVAS[0]
    v = (ys + 0.5) / H + fy / CANVAS[1]
    u, v = np.clip(u, 0, 1), np.clip(v, 0, 1)
    bp = sc['bodyPlan']
    body = sample(blurred_level(bg, scale, bp['level'], bp['residualSigmaTexels']), u, v)
    bt = np.zeros((H, W, 3))
    k = np.zeros((H, W))
    ed = edge_density(bg, scale)
    gain, ref = e['scaleCond']
    for i, surf in enumerate(fl.surfaces):
        c = sc['components'][surf[0]]
        m = fl.owner == i
        if sc['heavyPlan'] is not None:
            hp = sc['heavyPlan']
            deep = sample(blurred_level(bg, scale, hp['level'], hp['residualSigmaTexels']), u, v)
        else:
            lod = c['scatterLod']
            l0 = int(math.floor(lod))
            f = lod - l0
            deep = sample(blurred_level(bg, scale, l0, None), u, v)
            if f > 1e-9:
                deep = (1 - f) * deep + f * sample(blurred_level(bg, scale, l0 + 1, None), u, v)
        depth = -fl.d
        rampT = np.maximum(1 - depth / sc['reachCss'], 0)
        sharp = np.clip(c['sDeep'] + max(c['rampStart'] - c['sDeep'], 0) * rampT, 0, 1)
        ki = np.clip(np.clip(1 - sharp, 0, 1) + gain * (ed - ref), 0, 1)
        bt[m] = ((1 - ki)[..., None] * body + ki[..., None] * deep)[m]
        k[m] = ki[m]
    return bt, k


def shipped_body(ep, scale, bg, component, lensed=True):
    """The shipped body, LINEAR RGB (H, W, 3): the group-level solve over the per-pixel bt."""
    e = RES[ep]
    sc = e['perScale'][f'{scale}x']
    fl = field(component, scale)
    bt, _ = shipped_argument(ep, scale, bg, component, lensed)
    img = backdrop(bg, scale)
    out = np.zeros_like(bt)
    for i, surf in enumerate(fl.surfaces):
        c = sc['components'][surf[0]]
        st = silhouette_stat(img, scale, surf) if e['abscissa'] != 'source(default)' else source_stat(img)
        s = solve(e, c['sizeK'], st['level'], st['linLum'])
        m = fl.owner == i
        tone_colour = np.full(3, st['linLum'])  # the group's mean colour enters only via toneAdapt
        out[m] = compose(e, bt[m], {k_: np.full(m.sum(), float(v)) for k_, v in s.items()},
                         tone_colour)
    return out


# ---------------------------------------------------------------- candidate 1: landed T per pixel

def black_join(ep, scale, component):
    """Where the landed uniform response, after its dip, climbs back to its value at black, per
    surface kind (encoded input in [0, 1]), with that value. Below it the per-pixel response is
    not monotone: W36's black branch is a GROUP construction that blends toward the black ordinate
    below encoded input 0.003 and rejoins a solve whose own value there is lower. Used only by the
    rehearsal's monotone device."""
    e = RES[ep]
    out = {}
    for key in {s[0] for s in field(component, scale).surfaces}:
        sizeK = e['perScale'][f'{scale}x']['components'][key]['sizeK']
        x = np.linspace(0, 64 / 255, 16385)
        c = dec(x)
        lvl = c if e['abscissa'] == 'source(default)' else c
        st = solve(e, sizeK, lvl, c)
        y = compose(e, np.repeat(c[:, None], 3, 1), st, np.repeat(c[:, None], 3, 1))[:, 0]
        low = int(np.argmin(y))
        above = np.nonzero(y[low:] >= y[0])[0]
        out[key] = (float(x[low + above[0]]) if len(above) else float(x[-1]), float(y[0]),
                    float(x[low]), float(y[low]))
    return out


def landed_T(ep, scale, component, A, mono_black=False):
    """The shipped solve's uniform response at A(x), per pixel (A encoded in [0, 1]); LINEAR out.

    `mono_black` is a REHEARSAL DEVICE, not a declaration (the parent's item (e)): below the
    input where the response first climbs back to its value at black, the black value is held
    flat, which makes the per-pixel response monotone."""
    e = RES[ep]
    sc = e['perScale'][f'{scale}x']
    fl = field(component, scale)
    c = dec(A)
    lin = c @ W709
    level = dec(A @ W709) if e['abscissa'] != 'source(default)' else lin
    out = np.zeros_like(c)
    joins = black_join(ep, scale, component) if mono_black else {}
    for i, surf in enumerate(fl.surfaces):
        m = fl.owner == i
        s = solve(e, sc['components'][surf[0]]['sizeK'], level[m], lin[m])
        out[m] = compose(e, c[m], s, c[m])
        if mono_black:
            xj, y0 = joins[surf[0]][:2]
            low = m & ((A @ W709) < xj)
            out[low] = y0
    return out


# ---------------------------------------------------------------- candidate 1, light receded: E3

E3_KNOTS = np.array([40, 56, 72, 88, 104, 128, 150], float)
E3_NEUTRAL = np.array([150, 157, 164, 171, 178, 188, 197], float)
E3_GAINS = np.array([0.929205829365914, 0.9597570955316058, 0.9383102545096953])
# Family A's ordinates above 150 do not exist before G1; memo C's light-inactive native uniform
# readings stand in for them (probe/reader.py T_TAB: (160, 202), (242.4, 235.3), (255, 240)).
F_EXT_KNOTS = np.array([160.0, 242.4, 255.0])
F_EXT_VALUES = np.array([202.0, 235.3, 240.0])


def e3_F(L):
    """E3's neutral on encoded luma (codes): the shader's seven knots, first segment continued
    below 40; above 150 the stand-in extension, linear between knots and flat past 255."""
    L = np.asarray(L, dtype=np.float64)
    i = np.clip(np.searchsorted(E3_KNOTS, L, side='right') - 1, 0, 5)
    t = (L - E3_KNOTS[i]) / (E3_KNOTS[i + 1] - E3_KNOTS[i])
    lo = E3_NEUTRAL[i] + t * (E3_NEUTRAL[i + 1] - E3_NEUTRAL[i])
    kx = np.concatenate([[150.0], F_EXT_KNOTS])
    ky = np.concatenate([[197.0], F_EXT_VALUES])
    hi = np.interp(L, kx, ky)
    return np.clip(np.where(L > 150, hi, lo), 0, 255)


def e3_gain(L):
    L = np.asarray(L, dtype=np.float64)
    lo = E3_GAINS[0] + np.clip((L - 63) / 30, 0, 1) * (E3_GAINS[1] - E3_GAINS[0])
    hi = E3_GAINS[1] + np.clip((L - 93) / 25, 0, 1) * (E3_GAINS[2] - E3_GAINS[1])
    return np.where(L > 93, hi, lo)


def e3_shader(A255):
    """The SHIPPED-at-seal E3 (W41), on encoded codes: F unextended, g at the argument's luma."""
    L = A255 @ W709
    i = np.clip(np.searchsorted(E3_KNOTS, L, side='right') - 1, 0, 5)
    t = (L - E3_KNOTS[i]) / (E3_KNOTS[i + 1] - E3_KNOTS[i])
    f = np.clip(E3_NEUTRAL[i] + t * (E3_NEUTRAL[i + 1] - E3_NEUTRAL[i]), 0, 255)
    chroma = A255 - L[..., None]
    return np.clip(f[..., None] + e3_gain(L)[..., None] * chroma, 0, 255)


def e3_extended(M_L255, W255):
    """Candidate 1, light receded: y = F(L(M)) 1 + g(L(W)) v(W), codes."""
    LW = W255 @ W709
    return np.clip(e3_F(M_L255)[..., None] + e3_gain(LW)[..., None] * (W255 - LW[..., None]), 0, 255)


# ---------------------------------------------------------------- candidate 2: native T (memo C)

T_TAB = {
    'light-active': [(0, 132), (28.1, 146.1), (32, 148), (40, 152), (56, 160), (64, 164), (72, 168), (88, 176), (96, 179), (104, 183), (128, 195), (150, 205), (160, 210), (242.4, 247.4), (255, 253)],
    'light-receded': [(0, 133), (28.1, 145.1), (32, 147), (40, 150), (56, 157), (64, 161), (69, 163), (72, 164), (88, 171), (96, 175), (104, 178), (128, 188), (150, 197), (160, 202), (242.4, 235.3), (255, 240)],
    'dark-active': [(0, 32), (28.1, 58.2), (32, 62), (40, 69), (56, 83), (64, 89), (72, 96), (88, 108), (96, 113), (104, 119), (128, 134), (150, 146), (160, 151), (255, 184)],
    'dark-receded': [(0, 20), (28.1, 48.2), (32, 52), (40, 60), (56, 74), (64, 81), (72, 87), (88, 100), (96, 106), (104, 111), (128, 127), (140, 135), (150, 140), (160, 146), (242.4, 177.4), (255, 180)],
}
T_SPAN = {
    'light-active': {32: [(0, -1), (28.1, -1), (69, -1.5), (242.4, -2), (255, -2)], 96: [(0, 2), (28.1, 2), (69, 2.5), (128, 3), (242.4, 1), (255, 1)],
                     128: [(0, 4), (28.1, 4), (69, 5), (242.4, 2), (255, 2)], 160: [(0, 5), (28.1, 5), (69, 6.5), (128, 6), (242.4, 3), (255, 3)]},
    'dark-active': {32: [(0, 0), (28.1, 0), (69, -1.4), (242.4, 0.7), (255, 0.7)],
                    96: [(0, -1.1), (28.1, -1.1), (69, -5.4), (128, -13), (255, -50)],
                    128: [(0, -3.1), (28.1, -3.1), (69, -7.4), (128, -15), (242.4, -53), (255, -54)],
                    160: [(0, -5), (28.1, -5), (69, -9.4), (128, -16), (242.4, -55.4), (255, -57)]},
    'dark-receded': {96: [(0, -0.1), (28.1, -0.1), (69, -3.75), (128, -13), (242.4, -51), (255, -53)],
                     128: [(0, -0.1), (28.1, -0.1), (69, -4.25), (140, -20.7), (242.4, -58.3), (255, -60)],
                     160: [(0, -0.1), (28.1, -0.1), (69, -4.75), (140, -20.7), (242.4, -58.3), (255, -60)]},
}
# Memo C's trust: dark tops clamp at spans >= 96, where the table above 128 / 140 is not a reading.
T_TRUST = {'dark-active': {96: 128, 128: 128, 160: 128}, 'dark-receded': {96: 128, 128: 140, 160: 140}}


def t_span(span):
    return min((32, 44, 96, 128, 160), key=lambda v: abs(v - span))


def native_T(ep, span, L255):
    xs, ys = np.array(T_TAB[ep], float).T
    sp = t_span(span)
    if ep in T_SPAN and sp in T_SPAN[ep]:
        cx, cy = np.array(T_SPAN[ep][sp], float).T
        ys = ys + np.interp(xs, cx, cy)
    return np.interp(L255, xs, ys)


# ---------------------------------------------------------------- LT (memo E), whole canvas

KAPPA = {'light-active': 1.983, 'light-receded': 2.035, 'dark-active': 2.094, 'dark-receded': 2.074}
LAMBDA, WN, RB, RF = 0.9, 0.5, 5.0, 8.0


def _gf(X, sig, mode):
    m = 'nearest' if mode == 'clamp' else 'constant'
    return ndimage.gaussian_filter(X, sig, mode=m, truncate=4) if sig >= 1e-3 else X


def lt_argument(ep, scale, bg, component, kappa=None, lam=LAMBDA, w=WN, chroma='W', knee='luma',
                kappa_n=None, kappa_w=None, support='box', floor=True):
    """LT's argument over the canvas, ENCODED codes (H, W, 3): A = M_L + (W - L(W)).

    Returns (A, M_L, W) so the E3 candidate can take g at W's luma. Pixels outside every
    surface's footprint are the backdrop (they are never swapped).

    `chroma='M'` is the rehearsal's diagnostic rival to memo A's reading: the chroma of the
    per-channel composite (the knee taken per channel, U6's rival) instead of W's, with the luma
    still LT's on-luma M. The charter declares candidate 1's light receded chroma on W; the
    other endpoints' 'solve at M per pixel' leaves the chroma kernel open (U6, family E).

    Round 2 (the parent's items (a) and (d)), each a rival the charter already declares:
    `knee='channel'` is the per-channel knee (U6): N and M per channel, A = M_rgb, its luma
    L(M_rgb). `kappa_n` / `kappa_w` separate the two radii's scales (LT-2k). `support` is W's
    footprint: 'box' (the declared box plus margin), 'canvas' (the whole capture, the
    footprint's null), or 'shape' (W normalised over the rounded shape plus the margin, the
    'W on the rounded shape' rival). `floor=False` drops memo C's 0.8-dev capture floor."""
    kappa = KAPPA[ep] if kappa is None else kappa
    kn = kappa if kappa_n is None else kappa_n
    kw = kappa if kappa_w is None else kappa_w
    B = backdrop(bg, scale) * 255.0
    H, Wd, _ = B.shape
    fl = field(component, scale)
    active = not ep.endswith('receded')
    mode = 'clamp' if active else 'norm'
    sg = 1.0 if ep.startswith('light') else -1.0
    A_out = B.copy()
    ML_out = B @ W709
    W_out = B.copy()
    ys, xs = np.mgrid[0:H, 0:Wd].astype(np.float64)
    for i, (key, cx, cy, sw, sh, r) in enumerate(fl.surfaces):
        span = min(sw, sh)
        t = min(max((span - 64) / 96, 0), 1)
        f = 4 if key == 'rrect-lg' else 2
        marg = (0.35 * span if span > 64 else 16.0) if active else 1.0 / scale
        m = int(round(marg * scale)) if support != 'canvas' else 10 ** 6
        x0 = max(0, int(math.floor((cx - sw / 2) * scale)) - m)
        y0 = max(0, int(math.floor((cy - sh / 2) * scale)) - m)
        x1 = min(Wd, int(math.ceil((cx + sw / 2) * scale)) + m)
        y1 = min(H, int(math.ceil((cy + sh / 2) * scale)) + m)
        crop = B[y0:y1, x0:x1]
        S = np.stack([ndimage.gaussian_filter(crop[..., c], 0.4 * f, mode='nearest', truncate=4)
                      for c in range(3)], -1) if floor else crop.copy()
        cy_, cx_ = ys[y0:y1, x0:x1], xs[y0:y1, x0:x1]
        dpt = rrect_sdf((cx_ + 0.5) / scale, (cy_ + 0.5) / scale, cx, cy, sw, sh, r)
        if active:
            o = np.interp(dpt, [-span / 2, -1.0, 0.0], [0.8 * t, 0.4 * t, 0.5])
        else:
            o = np.full_like(dpt, 0.4 + 0.4 * t)
        u = float(scale)  # one pt in device px
        ones = np.ones(S.shape[:2])

        def G(X, sig):
            if mode == 'clamp':
                return np.stack([_gf(X[..., c], sig, 'clamp') for c in range(3)], -1)
            nrm = _gf(ones, sig, 'norm')
            return np.stack([_gf(X[..., c], sig, 'norm') for c in range(3)], -1) / nrm[..., None]

        if support == 'shape':
            # W normalised over the rounded shape plus the margin (the rival's support).
            ms = (dpt <= marg).astype(float)
            sw_ = kw * RF * u
            num = np.stack([_gf(S[..., c] * ms, sw_, 'norm') for c in range(3)], -1)
            Wt = num / np.maximum(_gf(ms, sw_, 'norm'), 1e-9)[..., None]
        else:
            Wt = G(S, kw * RF * u)
        lo, hi = float(o.min()), float(o.max())
        if hi - lo < 1e-6:
            C = G(S, kn * RB * lo * u)
        else:
            lv = np.linspace(lo, hi, 5)
            stack = np.stack([G(S, kn * RB * v * u) for v in lv])
            idx = np.clip(np.searchsorted(lv, o) - 1, 0, 3)
            fr = ((o - lv[idx]) / (lv[idx + 1] - lv[idx]))[..., None]
            a = np.take_along_axis(stack, idx[None, ..., None], 0)[0]
            b = np.take_along_axis(stack, (idx + 1)[None, ..., None], 0)[0]
            C = a + fr * (b - a)
        CL, WL = C @ W709, Wt @ W709
        NL = CL + sg * lam * np.maximum(0, sg * (WL - CL))
        ML = (1 - w) * NL + w * WL
        if knee == 'channel':
            Nc = C + sg * lam * np.maximum(0, sg * (Wt - C))
            A = (1 - w) * Nc + w * Wt
            ML = A @ W709
        elif chroma == 'M':
            Nc = C + sg * lam * np.maximum(0, sg * (Wt - C))
            Mc = (1 - w) * Nc + w * Wt
            A = ML[..., None] + (Mc - (Mc @ W709)[..., None])
        else:
            A = ML[..., None] + (Wt - WL[..., None])
        own = (fl.owner[y0:y1, x0:x1] == i)
        sl = (slice(y0, y1), slice(x0, x1))
        A_out[sl] = np.where(own[..., None], A, A_out[sl])
        ML_out[sl] = np.where(own, ML, ML_out[sl])
        W_out[sl] = np.where(own[..., None], Wt, W_out[sl])
    return A_out, ML_out, W_out
