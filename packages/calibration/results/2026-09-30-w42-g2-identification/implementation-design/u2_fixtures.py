"""W42 G2 step 3, U2: the oracle fixtures `renderer-webgpu/test/w42-body-law.test.ts` reads
(`implementation-design.md` §6, tests 2 and 3).

Every expected value comes from the instrument (`instrument/forward.py`, `geometry.py`) or from the
rehearsal (`gate/rehearsal/body.py`, `swap.py`) at the hashed declaration's bytes, or from the pre-read
addendum's reference (`native_t.py`); none is written by hand. Nothing here reads a native pixel.

  plan.json       forward.py's footprint (Cell.crop('box')), texel, floor and widths, and the exact
                  sigma_n at a set of depths, for every canonical and bed single shape at dpr 1 and 2,
                  both poses and all three units; plus the realisation's level set (narrow_error.py's
                  `levels_for`, four interior levels) beside it
  composite.json  forward.py's `_hinge` + Normal fill for the per-channel and on-luma knees, and
                  body.py's chroma-from-W form, on random encoded pairs, both hinges, four lambdas
  landed.json     body.py's `solve` + `compose` (the rehearsal's `landed_T`) per endpoint and sizeK on
                  a colour grid, with the endpoint's resolved inputs
  tones.json      the F extension (an independent numpy form of the declared interpolation) and
                  candidate 2's table (native_t.py's grid on the stand-in ordinates) with its chroma

    python3.12 -B u2_fixtures.py      # writes fixtures/*.json beside this file
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
G0 = os.path.abspath(os.path.join(HERE, '..', '..', '2026-09-29-w42-g0-declaration'))
sys.path.insert(0, os.path.join(G0, 'instrument'))
sys.path.insert(0, os.path.join(G0, 'gate', 'rehearsal'))
sys.path.insert(0, HERE)
import geometry as G  # noqa: E402
import forward as F  # noqa: E402
import body as BODY  # noqa: E402
import native_t as NT  # noqa: E402

OUT = os.path.join(HERE, 'fixtures')
G.load_scenes(os.path.join(G0, 'bed', 'scenes-w42-body.json'))
UNITS = {0: 'dev', 1: 'pt', 2: 'texel'}
K = (1.9, 2.3)
DEPTHS = (-200.0, -80.0, -48.0, -30.0, -20.0, -10.0, -4.0, -1.0, -0.5, 0.0, 0.5, 3.0)


def levels_for(s, scale_u, kn, receded):
    """The realisation's stored narrow widths (implementation-design.md §2.2), device px."""
    t = G.size_t(s)
    sc = kn * F.RN * scale_u
    if receded:
        return [sc * (0.4 + 0.4 * t)]
    if t == 0:
        return [0.0, sc * 0.5]
    lv = list(np.linspace(sc * 0.4 * t, sc * 0.8 * t, 4))
    if sc * 0.5 > sc * 0.8 * t + 1e-9:
        lv.append(sc * 0.5)
    return lv


def plan_fixture():
    rows = []
    shapes = [k for k, v in G.COMPONENTS.items()
              if isinstance(v, dict) and v.get('kind') in ('capsule', 'rrect')]
    for comp in sorted(shapes):
        cx, cy, w, h, r = G.shape_frame(comp)
        for scale in (1, 2):
            for pose in ('rest', 'inactive'):
                cell = F.Cell(comp, {'kind': 'solid', 'srgb': [128, 128, 128]}, comp, scale, 'light', pose)
                y0, y1, x0, x1 = cell.crop('box')
                by0, by1, bx0, bx1 = (int(v) for v in cell.box_px)
                for unit, name in UNITS.items():
                    u = cell.unit_dev(name)
                    fam = F.Family('LT', units=name)
                    p = {'k_n': K[0], 'k_w': K[1]}
                    sig = [float(F.sigma_n_pt(cell, fam, p, np.array([dd]))[0] * u) for dd in DEPTHS]
                    rows.append(dict(
                        component=comp, centre=[cx, cy], size=[w, h], scale=scale,
                        receded=pose == 'inactive', unit=unit,
                        box=dict(x0=bx0, y0=by0, x1=bx1, y1=by1),
                        footprint=dict(x0=int(x0), y0=int(y0), x1=int(x1), y1=int(y1)),
                        canvas=dict(x0=0, y0=0, x1=int(G.CANVAS[0] * scale), y1=int(G.CANVAS[1] * scale)),
                        texel=int(cell.f), floor=0.4 * cell.f, span=cell.span, t=cell.t,
                        wide=K[1] * F.RW * u, depths=list(DEPTHS), narrowAtDepth=sig,
                        edge='clamp' if cell.active else 'normalised',
                        levels=levels_for(cell.span, u, K[0], pose == 'inactive')))
    return dict(k=list(K), rows=rows)


def composite_fixture():
    rng = np.random.default_rng(20260930)
    rows = []
    for _ in range(64):
        C = rng.uniform(0, 1, 3)
        W = rng.uniform(0, 1, 3)
        if rng.uniform() < 0.25:        # near-isoluminant pairs, where the on-luma decision is fine
            W = C + rng.normal(0, 0.02, 3)
            W = np.clip(W, 0, 1)
        for lam in (-0.3, 0.7, 0.9, 1.4):
            for w in (0.5, 0.25):
                for sg in (1, -1):
                    out = {}
                    for name, knee in (('channel', 'channel'), ('luma', 'luma')):
                        N = F._hinge(C[None], W[None], sg, lam, knee)[0]
                        out[name] = list((1 - w) * N + w * W)
                    CL, WL = C @ G.W709, W @ G.W709
                    NL = CL + sg * lam * max(0.0, sg * (WL - CL))
                    ML = (1 - w) * NL + w * WL
                    out['chromaW'] = list(ML + (W - WL))
                    rows.append(dict(C=list(C), W=list(W), lam=lam, w=w, hinge=sg, M=out,
                                     wideLuma=float(WL)))
    return dict(rows=rows)


def landed_fixture():
    rng = np.random.default_rng(20260931)
    greys = [0.0, 0.0005, 0.001, 0.002, 0.003, 0.004, 0.01, 0.03, 0.05, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0]
    colours = [[g, g, g] for g in greys] + [list(rng.uniform(0, 1, 3)) for _ in range(40)]
    A = np.array(colours)
    out = {}
    for ep, e in BODY.RES.items():
        entry = dict(
            params={k: e[k] for k in ('tint', 'tintAlpha', 'sizeOcclusionGain', 'backdropToneLow',
                                       'backdropToneHigh', 'backdropToneSizeBias', 'backdropToneMax',
                                       'anchorX', 'thin', 'thick', 'responseStrength', 'black',
                                       'bodyChromaRetention', 'abscissa', 'sizeToneLevelFar')},
            cases=[])
        for sizeK in (0.0, 0.0923, 0.35, 1.0):
            c = BODY.dec(A)
            lin = c @ BODY.W709
            level = BODY.dec(A @ BODY.W709) if e['abscissa'] != 'source(default)' else lin
            s = BODY.solve(e, sizeK, level, lin)
            y = BODY.compose(e, c, s, c)
            entry['cases'].append(dict(sizeK=sizeK, A=A.tolist(), linear=y.tolist()))
        out[ep] = entry
    return out


def e3_ext(codes, gain_level, gains, neutral, high, strength):
    """E3's F, continued and clipped (material.ts bodyE3Encoded), moved above 150 toward the table
    through (150, n6), (160, h0) ... (255, h6); g at gain_level on A - L(A)."""
    L = float(np.dot(codes, G.W709))
    knots = np.array([40, 56, 72, 88, 104, 128, 150], float)
    i = int(np.clip(np.searchsorted(knots[1:6], L, side='right'), 0, 5))
    t = (L - knots[i]) / (knots[i + 1] - knots[i])
    f = float(np.clip(neutral[i] + t * (neutral[i + 1] - neutral[i]), 0, 255))
    if strength > 0 and L > 150:
        table = float(np.interp(L, [150, 160, 176, 192, 208, 224, 240, 255], [neutral[6], *high]))
        f = f + strength * (table - f)
    if codes[0] == codes[1] == codes[2]:
        return [f, f, f]
    g = BODY.e3_gain(np.array([gain_level]))[0] if gains is None else float(
        np.where(gain_level > 93, gains[1] + np.clip((gain_level - 93) / 25, 0, 1) * (gains[2] - gains[1]),
                 gains[0] + np.clip((gain_level - 63) / 30, 0, 1) * (gains[1] - gains[0])))
    return [float(np.clip(f + g * (v - L), 0, 255)) for v in codes]


def tones_fixture():
    rng = np.random.default_rng(20260932)
    e3 = []
    neutral = [150, 157, 164, 171, 178, 188, 197]
    for _ in range(80):
        codes = list(rng.uniform(0, 255, 3)) if rng.uniform() > 0.2 else [float(rng.uniform(0, 255))] * 3
        gl = float(rng.uniform(0, 255))
        high = sorted(rng.uniform(190, 255, 7).tolist())
        gains = rng.uniform(0.5, 1.5, 3).tolist()
        for strength in (0.0, 0.4, 1.0):
            e3.append(dict(codes=codes, gainLevel=gl, gains=gains, neutral=neutral, high=high,
                           strength=strength, out=e3_ext(np.array(codes), gl, gains, neutral, high, strength)))
    table = []
    for ep, scheme, geo in (('light-inactive', 'light', 'light-receded'), ('dark-rest', 'dark', 'dark-active')):
        nt = NT.NativeT(NT.stand_in(ep, scheme), scheme)
        tab = nt.table()
        gains = [0.95, 0.949, 0.933] if scheme == 'light' else [1.203, 1.165, 1.070]
        scale = 1.07
        cases = []
        for _ in range(60):
            codes = list(rng.uniform(0, 255, 3)) if rng.uniform() > 0.2 else [float(rng.uniform(0, 255))] * 3
            span = float(rng.choice([32, 44, 64, 72, 80, 88, 96, 112, 128, 150, 160, 200]))
            L = float(np.dot(codes, G.W709))
            f = float(np.clip(NT.grid_eval(tab, np.array([L]), span)[0], 0, 255))
            if codes[0] == codes[1] == codes[2]:
                y = [f, f, f]
            else:
                g = scale * float(np.where(L > 93, gains[1] + np.clip((L - 93) / 25, 0, 1) * (gains[2] - gains[1]),
                                           gains[0] + np.clip((L - 63) / 30, 0, 1) * (gains[1] - gains[0])))
                y = [float(np.clip(f + g * (v - L), 0, 255)) for v in codes]
            cases.append(dict(codes=codes, span=span, out=y))
        table.append(dict(endpoint=geo, levels=list(NT.GRID_LEVELS), spans=list(NT.GRID_SPANS),
                          codes=tab.tolist(), gains=gains, scale=scale, cases=cases))
    return dict(e3=e3, table=table)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (('plan', plan_fixture), ('composite', composite_fixture), ('landed', landed_fixture),
                     ('tones', tones_fixture)):
        data = fn()
        with open(os.path.join(OUT, f'{name}.json'), 'w') as fh:
            json.dump(data, fh, separators=(',', ':'))
            fh.write('\n')
        print(name, os.path.getsize(os.path.join(OUT, f'{name}.json')), 'bytes')


if __name__ == '__main__':
    main()
