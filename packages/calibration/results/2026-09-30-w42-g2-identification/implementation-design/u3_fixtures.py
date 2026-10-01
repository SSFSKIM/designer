"""W42 G2 step 3, U3: the stage fixture `renderer-webgpu/test/w42-body-law-stage.test.ts` reads.

The GPU stage (`body-law-pass.ts`) runs a SCHEDULE: which widths are stored, at which decimation, on
which grid, padded by how much, and read back at which coordinate. `u2_mirror.py` measured the
realisation with its own schedule, each width padded by its own amount. The runtime's schedule shares
one decimated grid per q, padded by the largest padding any of its widths needs, and claims that is the
same arithmetic. This fixture is what that claim is held to: for a handful of cells chosen to exercise
every branch of the schedule, the mirror's graph in f64 (`u2_mirror.py`'s `stored_blur` and
`interp_levels`, formats off) and the exact per-pixel Gaussian (`narrow_error.py`'s `exact_at`) at
sample pixels. The test runs the runtime's schedule in f64 over the same backdrop and compares.

The backdrop is not a bed backdrop: it is an integer formula both languages evaluate exactly (a
checkerboard of pitch 8 with a deterministic high-frequency texture), so the fixture carries a
formula rather than 100 000 pixels.

  cells (all on the instrument's 320 x 200 canvas):
    rrect-md        1x  light active    pt     cubic levels, all direct; W at q = 2
    rrect-lg        1x  dark  active    texel  six levels on one shared q = 2 grid; W at q = 4
    capsule-button  2x  light receded   pt     normalised mode; one level direct, W at q = 2 zero-padded
    rrect-80        2x  dark  active    pt     cubic levels direct, the contour level (10.5) on q = 2 with W
    capsule-button  1x  light active    pt     t = 0: the floored capture and the contour level, linear

    python3.12 -B u3_fixtures.py      # writes fixtures/stage.json beside this file
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import u2_mirror as M  # noqa: E402  (puts the instrument and the rehearsal on the path)

N = M.N
G = M.G
M.FMT['f64'] = np.float64
OUT = os.path.join(HERE, 'fixtures', 'stage.json')
UNIT = {0: lambda scale, f: 1.0, 1: lambda scale, f: float(scale), 2: lambda scale, f: float(f)}
CELLS = (
    ('rrect-md', 1, 'light', 'active', 1),
    ('rrect-lg', 1, 'dark', 'active', 2),
    ('capsule-button', 2, 'light', 'receded', 1),
    ('rrect-80', 2, 'dark', 'active', 1),
    ('capsule-button', 1, 'light', 'active', 1),
)
PER_STRATUM = 40
# The realisation since the perf wave (§17, `BODY_LAW_REALISATION.decimateActiveNarrowFromDevicePx`):
# the active pose's narrow levels are decimated from 6 device px; W and the receded level keep the
# oracle's 12.
ACTIVE_NARROW_FROM = 6.0


def backdrop(H, W):
    """The integer backdrop both languages build: codes 0..255, (H, W, 3)."""
    y, x = np.mgrid[0:H, 0:W].astype(np.int64)
    out = np.empty((H, W, 3), np.int64)
    checker = ((x >> 3) + (y >> 3)) & 1
    for c in range(3):
        v = (x * 37 + y * 101 + c * 59 + ((x * y) % 29) * 13) % 41
        out[..., c] = np.clip(np.where(checker == 1, 200, 40) + v - 20 + c * 7, 0, 255)
    return out


def read(X, mode):
    """u2_mirror.read without its f32 rounding: the formats are off here."""
    if mode == 'clamp':
        return X[..., :3]
    return X[..., :3] / np.maximum(X[..., 3:4], 1e-12)


def cell(comp, scale, scheme, pose, unit, rng):
    receded = pose == 'receded'
    k = (M.K_REC if receded else M.K)[scheme]
    lam = (M.LAM_REC if receded else M.LAM)[scheme]
    h = 1 if scheme == 'light' else -1
    s = G.span(comp)
    t = G.size_t(s)
    f = G.backdrop_texel_dev(comp)
    u = UNIT[unit](scale, f)
    d = G.sdf(comp, scale)
    H, Wd = d.shape
    B8 = backdrop(H, Wd).astype(np.float64)
    y0, y1, x0, x1 = N.window(comp, scale, not receded, d)
    dw = d[y0:y1, x0:x1]
    mode = 'norm' if receded else 'clamp'
    X = np.concatenate([B8[y0:y1, x0:x1] / 255, np.ones((y1 - y0, x1 - x0, 1))], -1)
    h1 = M.gauss1(X, 0.4 * f, 1, 'clamp')
    S = M.gauss1(h1, 0.4 * f, 0, 'clamp')
    S[..., 3] = 1.0

    depth = -dw
    inside = dw < 0
    strata = [inside, (dw >= 0) & (dw <= 2.0)] if receded else [
        inside & (depth < 20), inside & (depth >= 20) & (depth < 20 + 16.8 * t),
        inside & (depth >= 20 + 16.8 * t), (dw >= 0) & (dw <= 2.0)]
    picks = [N.sample(rng, m, PER_STRATUM) for m in strata if m.any()]
    py = np.concatenate([p[0] for p in picks])
    px = np.concatenate([p[1] for p in picks])
    sig = k * 5.0 * M.opacity(dw[py, px], s, receded) * u
    levels, how = M.levels_for(s, u, k, receded)
    sw = k * 8.0 * u

    narrow_from = M.DECIMATE_FROM if receded else ACTIVE_NARROW_FROM
    stack = np.array([read(M.stored_blur(S, v, mode, 'f64', narrow_from), mode)[py, px] for v in levels])
    Cm = M.interp_levels(stack, levels, sig, how)
    Wm = read(M.stored_blur(S, sw, mode, 'f64'), mode)[py, px]
    ex = 'clamp' if mode == 'clamp' else 'norm'
    Cx = np.array([[N.exact_at(S[..., c], a, b, sg, ex) for c in range(3)] for a, b, sg in zip(py, px, sig)])
    Wx = np.array([[N.exact_at(S[..., c], a, b, sw, ex) for c in range(3)] for a, b in zip(py, px)])
    A, LW, _ = M.composite(Cm, Wm, 0, h, lam)

    cx, cy, w, hh, r = G.shape_frame(comp)
    return dict(
        comp=comp, scale=scale, scheme=scheme, pose=pose, unit=unit, k=k, lam=lam, hinge=h,
        canvas=[Wd, H], centre=[cx, cy], size=[w, hh], radius=r,
        window=dict(x0=int(x0), y0=int(y0), x1=int(x1), y1=int(y1)),
        levels=[float(v) for v in levels], interpolation=how, wide=float(sw), mode=mode,
        samples=dict(
            y=py.tolist(), x=px.tolist(), depth=(-dw[py, px]).tolist(), sigma=sig.tolist(),
            mirrorC=Cm.tolist(), mirrorW=Wm.tolist(), exactC=Cx.tolist(), exactW=Wx.tolist(),
            argument=A.tolist(), wideLuma=LW.tolist(),
        ),
    )


def main():
    rng = np.random.default_rng(20261001)
    cells = [cell(*spec, rng) for spec in CELLS]
    doc = dict(
        source='implementation-design/u3_fixtures.py',
        backdrop='codes = clip((checker ? 200 : 40) + ((37x + 101y + 59c + ((xy) mod 29) 13) mod 41) - 20 + 7c,'
                 ' 0, 255), checker = ((x >> 3) + (y >> 3)) & 1',
        normal=M.WN, cells=cells,
    )
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as fh:
        json.dump(doc, fh, separators=(',', ':'))
        fh.write('\n')
    for c in cells:
        s = c['samples']
        dc = np.abs(np.array(s['mirrorC']) - np.array(s['exactC'])).max() * 255
        dw = np.abs(np.array(s['mirrorW']) - np.array(s['exactW'])).max() * 255
        print(f"{c['comp']:16s} {c['scale']}x {c['scheme']:5s} {c['pose']:8s} unit {c['unit']} "
              f"levels {len(c['levels'])} {c['interpolation']:6s} window {c['window']} "
              f"mirror-exact C {dc:.3f} W {dw:.3f} codes")


if __name__ == '__main__':
    main()
